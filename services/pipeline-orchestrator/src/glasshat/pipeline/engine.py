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
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from glasshat.agents.audit import (
    Consultant,
    ConsultResult,
    DatasetWriter,
    NullDatasetWriter,
    TableConsultant,
    make_dataset_examples,
    run_audit,
)
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
    dataset_writer: DatasetWriter = field(default_factory=NullDatasetWriter)


# YELLOW (optimism) over-confidence prior, grounded in spike-D held-out anchors
# (docs/spike-results.md §4: recovered mean_delta 1.453 @ low-evidence, 0.306 @
# high-evidence). The bias is strongest when evidence is thin, so the prior is
# evidence-bucket-varied rather than a flat constant — the audit pulls YELLOW back
# hardest exactly where it has the least to stand on. The correction formula itself
# is bidirectional (a negative mean_delta raises an under-confident score — see
# test_audit.test_apply_correction_is_bidirectional); the deployed prior encodes the
# over-confidence bias that spike-D actually measured.
_YELLOW_DELTA_BY_BUCKET: dict[str, tuple[float, int]] = {
    "low": (1.45, 7),
    "mid": (0.80, 10),
    "high": (0.31, 16),
}


def default_calibration_table() -> dict[tuple[Hat, str, str], ConsultResult]:
    """Seed the spike-D YELLOW optimism-bias prior for every preset criterion + bucket."""
    table: dict[tuple[Hat, str, str], ConsultResult] = {}
    for preset_id in list_presets():
        for criterion in load_preset(preset_id).criteria:
            for bucket, (mean_delta, n) in _YELLOW_DELTA_BY_BUCKET.items():
                table[(Hat.YELLOW, criterion.id, bucket)] = ConsultResult(mean_delta, n, 0.0, 10.0)
    return table


def default_deps(settings: Settings | None = None) -> Deps:
    """Build the config-selected dependencies (mock/memory/local-fs/noop by default).

    Honors ``consultant_backend`` / ``dataset_writer_backend`` so the deployed
    Cloud Run service reads + writes the live Phoenix calibration dataset
    while local/CI/mock runs stay on the deterministic spike-D table prior.
    Phoenix-MCP backends fall back to ``table``/``null`` when no Phoenix
    endpoint is configured, so a partial env file can never silently disable
    the audit.
    """
    settings = settings or get_settings()
    return Deps(
        llm=get_llm_client(settings),
        retrieval=HybridIndex(),
        docstore=get_docstore(settings),
        blobstore=get_blobstore(settings),
        tracer=get_tracer(settings),
        consultant=_select_consultant(settings),
        dataset_writer=_select_dataset_writer(settings),
    )


def _select_consultant(settings: Settings) -> Consultant:
    table = TableConsultant(default_calibration_table())
    if settings.consultant_backend == "phoenix-mcp" and settings.phoenix_collector_endpoint:
        from glasshat.agents.audit import FallbackConsultant
        from glasshat.pipeline.adk_runtime import PhoenixMcpConsultant

        return FallbackConsultant(
            primary=PhoenixMcpConsultant(
                base_url=settings.phoenix_collector_endpoint,
                api_key=settings.phoenix_api_key,
                dataset=settings.phoenix_calibration_dataset,
            ),
            backup=table,
        )
    return table


def _select_dataset_writer(settings: Settings) -> DatasetWriter:
    if settings.dataset_writer_backend == "phoenix-mcp" and settings.phoenix_collector_endpoint:
        from glasshat.pipeline.adk_runtime import PhoenixMcpDatasetWriter

        return PhoenixMcpDatasetWriter(
            base_url=settings.phoenix_collector_endpoint,
            api_key=settings.phoenix_api_key,
            dataset=settings.phoenix_calibration_dataset,
        )
    return NullDatasetWriter()


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

    with deps.tracer.span("agent_synthesize", **{"glasshat.agent": "RubricSynthesizer"}):
        rubric = await synthesize(inp, deps.llm)
    emit(Stage.PLANNING, rubric_id=rubric.rubric_id)
    with deps.tracer.span("agent_plan", **{"glasshat.agent": "BluePlanner"}):
        pln = plan(rubric, inp)

    emit(Stage.HATS_RUNNING, hats=[h.value for h in pln.hats_enabled])
    with deps.tracer.span(
        "agent_hats",
        **{"glasshat.agent": "SixHatPanel", "glasshat.hats": len(pln.hats_enabled)},
    ):
        assessments = await run_panel(pln, rubric, inp, deps.llm, deps.retrieval, deps.tracer)

    emit(Stage.AUDITING)
    emit(Stage.AUDIT_STARTED)
    with deps.tracer.span("agent_audit", **{"glasshat.agent": "Audit"}):
        corrections = await run_audit(assessments, deps.consultant)
    # Calibration sample size that actually informed this run — the "how many
    # past evals did we learn from?" telemetry the demo renders as a count-up.
    dataset_examples_used = max((c.n for c in corrections), default=0)
    emit(Stage.DATASET_LOOKUP, n_examples=dataset_examples_used)
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

    created_at = _now()
    emit(Stage.SCORING)
    with deps.tracer.span("agent_score", **{"glasshat.agent": "BMADScorer"}):
        scores = score(rubric, assessments, corrections)
        # Pre-audit scores power the /judge rank-flip board: same hats, same
        # rubric, but no calibration applied — so judges can see *what would
        # have ranked* without Glasshat's self-correction.
        pre_audit_scores = score(rubric, assessments, [])
    with deps.tracer.span("agent_report", **{"glasshat.agent": "ReportAssembler"}):
        record = assemble(
            run_id,
            rubric,
            scores,
            corrections,
            pre_audit_scores=pre_audit_scores,
            mode=inp.mode,
            created_at=created_at,
        )

    # Close the learning loop: write one example per correction to the dataset
    # so the next run's consultant has a richer prior. The writer is best-effort
    # — a Phoenix outage must not fail an evaluation. Counts feed the
    # /participate "calibration confidence (n)" chart.
    dataset_examples_added = 0
    if corrections:
        examples = make_dataset_examples(corrections, run_id=run_id, created_at=created_at)
        with deps.tracer.span("agent_dataset_writer", **{"glasshat.agent": "DatasetWriter"}):
            try:
                dataset_examples_added = await deps.dataset_writer.write(examples)
            except Exception:  # noqa: BLE001 — writer is best-effort, never block the run
                dataset_examples_added = 0
    emit(Stage.DATASET_WRITE, n_added=dataset_examples_added)

    record = record.model_copy(
        update={
            "dataset_examples_used": dataset_examples_used,
            "dataset_examples_added": dataset_examples_added,
        }
    )
    deps.docstore.put("runs", run_id, record.model_dump(mode="json"))
    emit(Stage.GRAPH_RESHAPE, criteria=len(scores))
    emit(Stage.COMPLETE, final_score=record.final_score)
    return record
