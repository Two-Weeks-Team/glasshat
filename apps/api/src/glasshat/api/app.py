"""FastAPI application exposing the evaluation engine + the two human gates.

The app holds one set of pipeline ``Deps`` (config-selected; ``mock``/``memory``
by default), so a run persisted by ``/api/evaluate`` is readable by
``/api/runs/{id}``. Endpoints: health, plan preview (gate 1), synchronous
evaluate, SSE stream, run fetch, and score override (gate 2).
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections import deque
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from glasshat.agents.blue_planner import plan
from glasshat.agents.rubric_synthesizer import synthesize
from glasshat.agents.types import EvaluationInput, PlanObject, RunRecord
from glasshat.pipeline.engine import Deps, default_deps, run_evaluation
from glasshat.pipeline.events import PipelineEvent, sse_line
from glasshat.rubric.presets import list_presets, load_preset
from glasshat.shared.config import Settings, get_settings
from pydantic import BaseModel

logger = logging.getLogger(__name__)


def _client_ip(request: Request) -> str:
    """The real client IP for rate-limit keying, resistant to X-Forwarded-For spoofing.

    Cloud Run's front end appends the true client IP to ``X-Forwarded-For`` and
    then its own proxy IP, so the trustworthy client is the **second-to-last**
    entry; everything to the left is attacker-supplied and must be ignored
    (otherwise a caller rotates a fake leftmost IP and bypasses the limiter).
    This reads the raw header directly — no uvicorn ``--proxy-headers`` whose
    default trusts the *leftmost*, spoofable entry. Falls back to the direct peer
    when the header is absent/short (local/dev).
    """
    parts = [p.strip() for p in request.headers.get("x-forwarded-for", "").split(",") if p.strip()]
    if len(parts) >= 2:
        return parts[-2]
    if parts:
        return parts[-1]
    return request.client.host if request.client else "unknown"


class _SlidingWindowRateLimiter:
    """Per-key sliding-window limiter (in-memory, per process/instance).

    Guards the expensive evaluate endpoints against cost-DoS. Per-instance state
    is sufficient alongside Cloud Run's bounded concurrency; ``per_minute <= 0``
    disables it.
    """

    def __init__(self, per_minute: int) -> None:
        self._per_minute = per_minute
        self._hits: dict[str, deque[float]] = {}

    def allow(self, key: str, now: float) -> bool:
        if self._per_minute <= 0:
            return True
        window = self._hits.setdefault(key, deque())
        cutoff = now - 60.0
        while window and window[0] < cutoff:
            window.popleft()
        if len(window) >= self._per_minute:
            return False
        window.append(now)
        return True


class OverrideRequest(BaseModel):
    """A human score override (gate 2)."""

    criterion_id: str
    score: float
    reason: str = ""


class PresetInfo(BaseModel):
    """A rubric preset summary for the picker (gate-0 rubric selection)."""

    id: str
    label: str
    criteria_count: int
    final_scale: str
    source_type: str


def _preset_label(preset_id: str) -> str:
    """Human display label, e.g. ``"rapid-agent"`` -> ``"Rapid Agent"``."""
    return " ".join(part.capitalize() for part in preset_id.replace("_", "-").split("-"))


def create_app(deps: Deps | None = None, settings: Settings | None = None) -> FastAPI:
    """Build the FastAPI app. Pass ``deps`` (e.g. mock) in tests; defaults otherwise."""
    settings = settings or get_settings()
    app = FastAPI(title="Glasshat API", version="0.1.0")
    origins = [o.strip() for o in settings.cors_allow_origins.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["*"],
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )
    app.state.deps = deps or default_deps()

    limiter = _SlidingWindowRateLimiter(settings.rate_limit_per_minute)

    async def _rate_limit(request: Request) -> None:
        # async so it runs on the event loop, not FastAPI's thread pool: the
        # limiter's deque ops are not thread-safe, and a sync dependency would let
        # two same-key requests race (IndexError → 500). No I/O here, so the
        # single-threaded loop makes it atomic without a lock.
        if not limiter.allow(_client_ip(request), time.monotonic()):
            raise HTTPException(status_code=429, detail="rate limit exceeded; retry shortly")

    def _deps() -> Deps:
        result: Deps = app.state.deps
        return result

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/presets")
    def presets() -> list[PresetInfo]:
        out: list[PresetInfo] = []
        for preset_id in list_presets():
            rubric = load_preset(preset_id)
            out.append(
                PresetInfo(
                    id=preset_id,
                    label=_preset_label(preset_id),
                    criteria_count=len(rubric.criteria),
                    final_scale=rubric.scoring_rule.final_scale,
                    source_type=str(rubric.source.type.value),
                )
            )
        return out

    @app.post("/api/plan", dependencies=[Depends(_rate_limit)])
    async def plan_preview(inp: EvaluationInput) -> PlanObject:
        rubric = await synthesize(inp, _deps().llm)
        return plan(rubric, inp)

    @app.post("/api/evaluate", dependencies=[Depends(_rate_limit)])
    async def evaluate(inp: EvaluationInput) -> RunRecord:
        return await run_evaluation(inp, _deps())

    @app.post("/api/evaluate/stream", dependencies=[Depends(_rate_limit)])
    async def evaluate_stream(inp: EvaluationInput) -> StreamingResponse:
        queue: asyncio.Queue[PipelineEvent | None] = asyncio.Queue()
        failed = {"error": False}

        async def _run() -> None:
            try:
                await run_evaluation(inp, _deps(), on_event=queue.put_nowait)
            except Exception:  # noqa: BLE001 — surface a graceful SSE error, never crash the stream
                logger.exception("evaluation stream failed")
                failed["error"] = True
            finally:
                queue.put_nowait(None)

        async def _gen() -> Any:
            task = asyncio.create_task(_run())
            while True:
                event = await queue.get()
                if event is None:
                    break
                yield sse_line(event)
            await task
            if failed["error"]:
                # Generic message — never leak internal error text to the client.
                yield 'event: error\ndata: {"message": "evaluation failed"}\n\n'

        return StreamingResponse(_gen(), media_type="text/event-stream")

    @app.get("/api/runs/{run_id}")
    def get_run(run_id: str) -> dict[str, Any]:
        record = _deps().docstore.get("runs", run_id)
        if record is None:
            raise HTTPException(status_code=404, detail="run not found")
        return dict(record)

    @app.post("/api/runs/{run_id}/override", dependencies=[Depends(_rate_limit)])
    def override(run_id: str, body: OverrideRequest) -> dict[str, Any]:
        record = _deps().docstore.get("runs", run_id)
        if record is None:
            raise HTTPException(status_code=404, detail="run not found")
        updated = dict(record)
        overrides = list(updated.get("overrides", []))
        overrides.append(body.model_dump())
        updated["overrides"] = overrides
        _deps().docstore.put("runs", run_id, updated)
        return updated

    return app
