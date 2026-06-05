"""FastAPI application exposing the evaluation engine + the two human gates.

The app holds one set of pipeline ``Deps`` (config-selected; ``mock``/``memory``
by default), so a run persisted by ``/api/evaluate`` is readable by
``/api/runs/{id}``. Endpoints: health, plan preview (gate 1), synchronous
evaluate, SSE stream, run fetch, and score override (gate 2).
"""

from __future__ import annotations

import asyncio
import logging
import secrets
import time
from collections import deque
from collections.abc import Mapping
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
from glasshat.shared.enums import RunMode
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


class ParticipantScore(BaseModel):
    """One criterion's score as shown to a participant (no audit internals)."""

    criterion_id: str
    score: float


class ParticipantRunView(BaseModel):
    """The redacted run view a participant may read (M6).

    Deliberately omits the full ``rubric`` (criterion weights / descriptors /
    source clauses) and the per-correction calibration internals (``mean_delta`` /
    ``n``) — leaking those would hand an entrant the exact knobs to game. The
    self-correction *story* survives (pre vs post score, how many corrections),
    just not the magnitudes. Judges (bearer-authed) get the full record.
    """

    run_id: str
    final_score: float
    pre_audit_final_score: float = 0.0
    scores: list[ParticipantScore]
    corrections_count: int = 0
    mode: str = RunMode.PARTICIPANT.value
    created_at: str = ""


def _participant_view(record: Mapping[str, Any]) -> dict[str, Any]:
    """Project a stored run record down to the participant-safe fields."""
    scores = [
        {"criterion_id": s["criterion_id"], "score": s["score"]} for s in record.get("scores", [])
    ]
    return ParticipantRunView(
        run_id=str(record.get("run_id", "")),
        final_score=float(record.get("final_score", 0.0)),
        pre_audit_final_score=float(record.get("pre_audit_final_score", 0.0)),
        scores=[ParticipantScore(**s) for s in scores],
        corrections_count=len(record.get("audit_corrections", [])),
        mode=str(record.get("mode", RunMode.PARTICIPANT.value)),
        created_at=str(record.get("created_at", "")),
    ).model_dump()


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
    judge_token = settings.judge_api_token
    _judge_open_warned = {"done": False}

    def _is_judge(request: Request) -> bool:
        """Whether the caller may take judge-only actions (override, JUDGE-mode
        runs, un-redacted run views). When ``JUDGE_API_TOKEN`` is unset the judge
        surface is OPEN (local/CI/demo) but warns once; when set it requires a
        constant-time ``Authorization: Bearer <token>`` match."""
        if not judge_token:
            if not _judge_open_warned["done"]:
                logger.warning(
                    "JUDGE_API_TOKEN unset — judge endpoints (override, judge-mode runs, "
                    "un-redacted run views) are OPEN. Set it in any exposed deployment."
                )
                _judge_open_warned["done"] = True
            return True
        provided = request.headers.get("authorization", "")
        return secrets.compare_digest(provided, f"Bearer {judge_token}")

    def _require_judge(request: Request) -> None:
        if not _is_judge(request):
            raise HTTPException(status_code=401, detail="judge authorization required")

    def _enforce_mode(inp: EvaluationInput, request: Request) -> None:
        # M5 server-enforcement: a JUDGE-mode run (which unlocks rules_url /
        # custom_yaml rubrics) is honored only for an authorized judge; an
        # unauthenticated caller cannot escalate by setting mode=judge. (A
        # participant payload with a non-preset source is already rejected at
        # validation, returning 422.)
        if inp.mode is RunMode.JUDGE and not _is_judge(request):
            raise HTTPException(status_code=403, detail="judge mode requires authorization")

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
    async def plan_preview(inp: EvaluationInput, request: Request) -> PlanObject:
        _enforce_mode(inp, request)
        rubric = await synthesize(inp, _deps().llm)
        return plan(rubric, inp)

    @app.post("/api/evaluate", dependencies=[Depends(_rate_limit)])
    async def evaluate(inp: EvaluationInput, request: Request) -> RunRecord:
        _enforce_mode(inp, request)
        return await run_evaluation(inp, _deps())

    @app.post("/api/evaluate/stream", dependencies=[Depends(_rate_limit)])
    async def evaluate_stream(inp: EvaluationInput, request: Request) -> StreamingResponse:
        _enforce_mode(inp, request)
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
    def get_run(run_id: str, request: Request) -> dict[str, Any]:
        record = _deps().docstore.get("runs", run_id)
        if record is None:
            raise HTTPException(status_code=404, detail="run not found")
        # M6: judges (bearer-authed, or open in demo) see the full record;
        # everyone else gets the redacted participant view.
        if _is_judge(request):
            return dict(record)
        return _participant_view(record)

    @app.post(
        "/api/runs/{run_id}/override",
        dependencies=[Depends(_rate_limit), Depends(_require_judge)],
    )
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
