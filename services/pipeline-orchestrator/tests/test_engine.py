import asyncio
from pathlib import Path
from typing import Any

from glasshat.agents.audit import ConsultResult, TableConsultant
from glasshat.agents.types import EvaluationInput, RunRecord
from glasshat.pipeline.engine import Deps, default_deps, run_evaluation
from glasshat.pipeline.events import PipelineEvent, Stage
from glasshat.rubric.presets import load_preset
from glasshat.shared.blobstore import LocalFsBlobStore
from glasshat.shared.docstore import MemoryDocStore
from glasshat.shared.enums import Hat, RunMode
from glasshat.shared.llm import MockLlmClient
from glasshat.shared.retrieval import HybridIndex
from glasshat.shared.tracing import NoOpTracer


class _OverconfidentYellowLlm(MockLlmClient):
    async def generate(self, prompt: str, *, tier: str = "flash", **kw: Any) -> str:
        if "YELLOW" in prompt:
            return "SCORE: 9.0\nRATIONALE: extremely optimistic"
        return await super().generate(prompt, tier=tier, **kw)


def _deps(tmp_path: Path) -> Deps:
    r = load_preset("rapid-agent")
    table = {
        (Hat.YELLOW, c.id, b): ConsultResult(1.74, 14, 6.0, 8.5)
        for c in r.criteria
        for b in ("low", "mid", "high")
    }
    return Deps(
        llm=_OverconfidentYellowLlm(embedding_dim=8),
        retrieval=HybridIndex(),
        docstore=MemoryDocStore(),
        blobstore=LocalFsBlobStore(str(tmp_path)),
        tracer=NoOpTracer(),
        consultant=TableConsultant(table),
    )


def test_run_evaluation_end_to_end_with_self_correction(tmp_path: Path) -> None:
    inp = EvaluationInput(
        rubric_source={"preset_id": "rapid-agent"},
        deck_text="we built a novel multi-agent system in python with tests and a clean design",
        mode=RunMode.JUDGE,
    )
    deps = _deps(tmp_path)
    events: list[PipelineEvent] = []
    rec = asyncio.run(run_evaluation(inp, deps, on_event=events.append))

    assert isinstance(rec, RunRecord)
    assert rec.run_id and rec.final_score > 0
    # self-correct delta present and pulled the over-confident YELLOW down
    assert len(rec.audit_corrections) >= 1
    assert all(c.original >= c.corrected for c in rec.audit_corrections)
    assert any(c.original > c.corrected for c in rec.audit_corrections)
    yellow = next(c for c in rec.audit_corrections if c.hat == Hat.YELLOW)
    assert 7.5 <= yellow.corrected <= 7.7  # 9.0 -> ~7.6

    # persisted
    assert deps.docstore.get("runs", rec.run_id) is not None

    # SSE event sequence
    stages = [e.stage for e in events]
    assert Stage.SCORE_CORRECTED in stages
    assert stages[-1] == Stage.COMPLETE
    assert stages.index(Stage.HATS_RUNNING) < stages.index(Stage.SCORING)


def test_default_deps_runs_without_credentials() -> None:
    inp = EvaluationInput(
        rubric_source={"preset_id": "rapid-agent"}, deck_text="alpha beta gamma delta epsilon"
    )
    rec = asyncio.run(run_evaluation(inp, default_deps()))
    assert rec.run_id and rec.scores


def test_persisted_record_shape(tmp_path: Path) -> None:
    inp = EvaluationInput(
        rubric_source={"preset_id": "qdrant"}, deck_text="functionality originality user experience"
    )
    deps = _deps(tmp_path)
    rec = asyncio.run(run_evaluation(inp, deps))
    stored = deps.docstore.get("runs", rec.run_id)
    assert stored is not None
    assert stored["final_score"] == rec.final_score
    assert stored["mode"] == rec.mode
