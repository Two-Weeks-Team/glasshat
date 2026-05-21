"""Pipeline orchestrator — wires the engine stages end-to-end.

``run_evaluation`` runs ingest -> synthesize -> plan -> 6-hat panel -> audit ->
score -> report -> persist, emitting SSE events (including the self-correct score
delta) along the way. It depends only on the P1/P2 abstractions, so it runs fully
on ``mock`` LLM + ``memory`` store with no credentials. The ADK runtime adapter
and the Phoenix-MCP consultant (``adk_runtime``) wrap these same stages for the
live deployment.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from glasshat.agents.audit import Consultant, ConsultResult, TableConsultant, run_audit
from glasshat.agents.blue_planner import plan
from glasshat.agents.bmad_scorer import score
from glasshat.agents.hats import run_panel
from glasshat.agents.report import assemble
from glasshat.agents.rubric_synthesizer import synthesize
from glasshat.agents.types import EvaluationInput, RunRecord
from glasshat.ingest import embed_chunks, ingest_deck
from glasshat.pipeline.events import PipelineEvent, Stage
from glasshat.rubric.presets import list_presets, load_preset
from glasshat.shared.blobstore import get_blobstore
from glasshat.shared.config import Settings, get_settings
from glasshat.shared.docstore import get_docstore
from glasshat.shared.enums import Hat
from glasshat.shared.ids import new_uuid
from glasshat.shared.llm import get_llm_client
from glasshat.shared.protocols import BlobStore, DocStore, LlmClient, Retrieval, Tracer
from glasshat.shared.retrieval import Document, HybridIndex
from glasshat.shared.tracing import get_tracer

EventSink = Callable[[PipelineEvent], None]


@dataclass
class Deps:
    """The injectable dependencies for one evaluation run."""

    llm: LlmClient
    retrieval: Retrieval
    docstore: DocStore
    blobstore: BlobStore
    tracer: Tracer
    consultant: Consultant


def default_calibration_table() -> dict[tuple[Hat, str, str], ConsultResult]:
    """Seed YELLOW (optimism-bias) calibration for every preset criterion + bucket."""
    table: dict[tuple[Hat, str, str], ConsultResult] = {}
    for preset_id in list_presets():
        for criterion in load_preset(preset_id).criteria:
            for bucket in ("low", "mid", "high"):
                table[(Hat.YELLOW, criterion.id, bucket)] = ConsultResult(1.0, 14, 0.0, 10.0)
    return table


def default_deps(settings: Settings | None = None) -> Deps:
    """Build the config-selected dependencies (mock/memory/local-fs/noop by default)."""
    settings = settings or get_settings()
    return Deps(
        llm=get_llm_client(settings),
        retrieval=HybridIndex(),
        docstore=get_docstore(settings),
        blobstore=get_blobstore(settings),
        tracer=get_tracer(settings),
        consultant=TableConsultant(default_calibration_table()),
    )


def _now() -> str:
    return datetime.now(UTC).isoformat()


async def run_evaluation(
    inp: EvaluationInput, deps: Deps, *, on_event: EventSink | None = None
) -> RunRecord:
    """Run the full evaluation pipeline and persist the immutable RunRecord."""

    def emit(stage: Stage, **payload: Any) -> None:
        if on_event is not None:
            on_event(PipelineEvent(stage=stage, payload=payload))

    run_id = new_uuid()
    emit(Stage.QUEUED, run_id=run_id)

    emit(Stage.INGESTING)
    if inp.deck_text:
        chunks = await embed_chunks(await ingest_deck(text=inp.deck_text, llm=deps.llm), deps.llm)
        deps.retrieval.index(
            Document(id=c.id, text=c.text, vector=c.vector, payload={"source": c.source})
            for c in chunks
        )

    rubric = await synthesize(inp, deps.llm)
    emit(Stage.PLANNING, rubric_id=rubric.rubric_id)
    pln = plan(rubric, inp)

    emit(Stage.HATS_RUNNING, hats=[h.value for h in pln.hats_enabled])
    assessments = await run_panel(pln, rubric, inp, deps.llm, deps.retrieval, deps.tracer)

    emit(Stage.AUDITING)
    emit(Stage.AUDIT_STARTED)
    corrections = await run_audit(assessments, deps.consultant)
    for c in corrections:
        emit(Stage.INCONSISTENCY_FLAGGED, hat=c.hat.value, criterion=c.criterion_id)
        emit(Stage.PHOENIX_CONSULTATION, mean_delta=c.mean_delta, n=c.n)
        emit(Stage.ANCHOR_RETRIEVAL, n=c.n)
        emit(
            Stage.SCORE_CORRECTED,
            **{
                "hat": c.hat.value,
                "criterion": c.criterion_id,
                "from": c.original,
                "to": c.corrected,
            },
        )

    emit(Stage.SCORING)
    scores = score(rubric, assessments, corrections)
    record = assemble(run_id, rubric, scores, corrections, mode=inp.mode, created_at=_now())

    deps.docstore.put("runs", run_id, record.model_dump(mode="json"))
    emit(Stage.GRAPH_RESHAPE, criteria=len(scores))
    emit(Stage.COMPLETE, final_score=record.final_score)
    return record
