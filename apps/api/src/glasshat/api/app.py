"""FastAPI application exposing the evaluation engine + the two human gates.

The app holds one set of pipeline ``Deps`` (config-selected; ``mock``/``memory``
by default), so a run persisted by ``/api/evaluate`` is readable by
``/api/runs/{id}``. Endpoints: health, plan preview (gate 1), synchronous
evaluate, SSE stream, run fetch, and score override (gate 2).
"""

from __future__ import annotations

import asyncio
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from glasshat.agents.blue_planner import plan
from glasshat.agents.rubric_synthesizer import synthesize
from glasshat.agents.types import EvaluationInput, PlanObject, RunRecord
from glasshat.pipeline.engine import Deps, default_deps, run_evaluation
from glasshat.pipeline.events import PipelineEvent, sse_line
from glasshat.rubric.presets import list_presets, load_preset
from pydantic import BaseModel


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


def create_app(deps: Deps | None = None) -> FastAPI:
    """Build the FastAPI app. Pass ``deps`` (e.g. mock) in tests; defaults otherwise."""
    app = FastAPI(title="Glasshat API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.state.deps = deps or default_deps()

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

    @app.post("/api/plan")
    async def plan_preview(inp: EvaluationInput) -> PlanObject:
        rubric = await synthesize(inp, _deps().llm)
        return plan(rubric, inp)

    @app.post("/api/evaluate")
    async def evaluate(inp: EvaluationInput) -> RunRecord:
        return await run_evaluation(inp, _deps())

    @app.post("/api/evaluate/stream")
    async def evaluate_stream(inp: EvaluationInput) -> StreamingResponse:
        queue: asyncio.Queue[PipelineEvent | None] = asyncio.Queue()

        async def _run() -> None:
            try:
                await run_evaluation(inp, _deps(), on_event=queue.put_nowait)
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

        return StreamingResponse(_gen(), media_type="text/event-stream")

    @app.get("/api/runs/{run_id}")
    def get_run(run_id: str) -> dict[str, Any]:
        record = _deps().docstore.get("runs", run_id)
        if record is None:
            raise HTTPException(status_code=404, detail="run not found")
        return dict(record)

    @app.post("/api/runs/{run_id}/override")
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
