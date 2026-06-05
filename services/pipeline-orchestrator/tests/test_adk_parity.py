"""ADK ⇄ python runtime parity (Tier B gate).

The ``adk`` runtime must be behaviourally indistinguishable from the ``python``
runtime: same ``RunRecord`` (modulo the per-run ``run_id`` / ``created_at``), the
same ordered SSE stream, and the same failure behaviour. If these hold, the only
difference is the span topology (a nested ADK tree vs flat manual spans), which is
exactly the Tier B goal. google-adk is a dev dependency, so this runs in CI.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import pytest
from glasshat.agents.audit import TableConsultant
from glasshat.agents.types import EvaluationInput
from glasshat.pipeline.engine import Deps, default_calibration_table, run_evaluation
from glasshat.pipeline.events import PipelineEvent, Stage
from glasshat.rubric.presets import list_presets
from glasshat.shared.blobstore import LocalFsBlobStore
from glasshat.shared.docstore import MemoryDocStore
from glasshat.shared.enums import RunMode
from glasshat.shared.llm import MockLlmClient
from glasshat.shared.retrieval import HybridIndex
from glasshat.shared.tracing import NoOpTracer

pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")

# Per-run identifiers that legitimately differ between any two runs (the python
# and adk runs each mint their own), so they are excluded from the parity compare.
_VOLATILE_RECORD_FIELDS = ("run_id", "created_at")
_VOLATILE_EVENT_KEYS = frozenset({"run_id", "rubric_id"})


def _deps(tmp_path: Path, *, agent_runtime: str, llm: Any = None) -> Deps:
    return Deps(
        llm=llm or MockLlmClient(embedding_dim=8),
        retrieval=HybridIndex(),
        docstore=MemoryDocStore(),
        blobstore=LocalFsBlobStore(str(tmp_path)),
        tracer=NoOpTracer(),
        consultant=TableConsultant(default_calibration_table()),
        agent_runtime=agent_runtime,  # type: ignore[arg-type]
    )


def _strip_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in payload.items() if k not in _VOLATILE_EVENT_KEYS}


def _run(
    deps: Deps, inp: EvaluationInput
) -> tuple[dict[str, Any], list[tuple[str, dict[str, Any]]]]:
    events: list[PipelineEvent] = []
    record = asyncio.run(run_evaluation(inp, deps, on_event=events.append))
    dumped = record.model_dump(mode="json")
    for f in _VOLATILE_RECORD_FIELDS:
        dumped.pop(f, None)
    # rubric_id is a fresh UUID per load_preset call (a per-run id), so normalize it
    # out of the nested rubric and the PLANNING event payload.
    if isinstance(dumped.get("rubric"), dict):
        dumped["rubric"].pop("rubric_id", None)
    seq = [(e.stage.value, _strip_payload(e.payload)) for e in events]
    return dumped, seq


@pytest.mark.parametrize("preset_id", list_presets())
def test_adk_matches_python_record_and_events(tmp_path: Path, preset_id: str) -> None:
    inp = EvaluationInput(
        rubric_source={"preset_id": preset_id},
        deck_text="We built a retrieval-augmented multi-agent evaluator in Python.",
        mode=RunMode.JUDGE,
    )
    rec_py, ev_py = _run(_deps(tmp_path / "py", agent_runtime="python"), inp)
    rec_adk, ev_adk = _run(_deps(tmp_path / "adk", agent_runtime="adk"), inp)

    assert rec_adk == rec_py, f"RunRecord diverged for preset {preset_id}"
    assert ev_adk == ev_py, f"SSE event stream diverged for preset {preset_id}"


def test_adk_emits_the_full_audit_event_sequence(tmp_path: Path) -> None:
    # Sanity: the parity above is non-trivial — the run actually emits the audit
    # wow-beats (corrections fire from the seeded table), not just queued/complete.
    inp = EvaluationInput(
        rubric_source={"preset_id": "rapid-agent"}, deck_text="x y z", mode=RunMode.JUDGE
    )
    _rec, seq = _run(_deps(tmp_path, agent_runtime="adk"), inp)
    stages = [s for s, _ in seq]
    assert stages[0] == Stage.QUEUED.value
    assert stages[-1] == Stage.COMPLETE.value
    for required in (
        Stage.HATS_RUNNING.value,
        Stage.AUDIT_STARTED.value,
        Stage.SCORE_CORRECTED.value,
        Stage.DATASET_WRITE.value,
    ):
        assert required in stages, f"adk run missing {required}"


class _RaisingEmbedLlm(MockLlmClient):
    """Raises in embed, so the failure lands in the (sequential) ingest stage —
    where both runtimes raise the identical single exception (the parallel hats
    would otherwise wrap a hat failure in an ExceptionGroup)."""

    async def embed(self, texts: Any) -> list[list[float]]:
        raise RuntimeError("ingest boom")


def test_adk_failure_path_matches_python(tmp_path: Path) -> None:
    inp = EvaluationInput(
        rubric_source={"preset_id": "rapid-agent"}, deck_text="x", mode=RunMode.JUDGE
    )

    def run_collecting(agent_runtime: str) -> list[tuple[str, dict[str, Any]]]:
        events: list[PipelineEvent] = []
        deps = _deps(tmp_path / agent_runtime, agent_runtime=agent_runtime, llm=_RaisingEmbedLlm(8))
        with pytest.raises(RuntimeError, match="ingest boom"):
            asyncio.run(run_evaluation(inp, deps, on_event=events.append))
        return [(e.stage.value, _strip_payload(e.payload)) for e in events]

    # Both runtimes raise the same error AND emit the identical events-before-failure
    # (queued → ingesting, then the ingest stage raises and halts the run).
    py = run_collecting("python")
    adk = run_collecting("adk")
    assert adk == py
    assert [s for s, _ in adk] == [Stage.QUEUED.value, Stage.INGESTING.value]
