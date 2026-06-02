"""Pipeline orchestrator — wires the engine stages end-to-end.

``run_evaluation`` runs ingest -> synthesize -> plan -> 6-hat panel -> audit ->
score -> report -> persist, emitting SSE events (including the self-correct score
delta) along the way. It depends only on the P1/P2 abstractions, so it runs fully
on ``mock`` LLM + ``memory`` store with no credentials. The ADK runtime adapter
and the Phoenix-MCP consultant (``adk_runtime``) wrap these same stages for the
live deployment.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Protocol, runtime_checkable

from glasshat.agents.audit import (
    AnchorConsultant,
    CalibrationAnchor,
    Consultant,
    ConsultResult,
    DatasetWriter,
    NullDatasetWriter,
    TableConsultant,
    WeightAware,
    make_dataset_examples,
    run_audit,
)
from glasshat.agents.blue_planner import plan
from glasshat.agents.bmad_scorer import score
from glasshat.agents.hats import run_panel
from glasshat.agents.report import assemble
from glasshat.agents.rubric_synthesizer import synthesize
from glasshat.agents.types import Chunk, EvaluationInput, RunRecord
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

logger = logging.getLogger(__name__)


@runtime_checkable
class RepoGrader(Protocol):
    """Turn a ``repo_url`` into retrievable repo chunks (metadata-only).

    The deployed implementation talks only to the fixed ``api.github.com`` host
    (see :class:`glasshat.code_grader.GitHubApiRepoGrader`); the default
    :class:`NullRepoGrader` returns nothing so credential-free / offline runs
    are deck-only.
    """

    async def chunks_for(self, url: str) -> list[Chunk]: ...


class NullRepoGrader:
    """No-op grader (default): never touches the network, always deck-only."""

    async def chunks_for(self, url: str) -> list[Chunk]:
        return []


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
    repo_grader: RepoGrader = field(default_factory=NullRepoGrader)


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


def default_calibration_anchors() -> list[CalibrationAnchor]:
    """Honest weight-aware seed: one anchor per preset, each carrying the *real*
    spike-D prior for its own criteria (no fabricated cross-schema differences).

    The anchors differ by ``weights_vector`` (so :class:`AnchorConsultant` can
    pick the nearest schema), but all carry the same measured prior today — the
    live Phoenix dataset accumulates genuinely per-schema deltas over time. Until
    then this behaves like the table prior, just selected by rubric weighting.
    """
    anchors: list[CalibrationAnchor] = []
    for preset_id in list_presets():
        preset = load_preset(preset_id)
        deltas: dict[tuple[Hat, str, str], ConsultResult] = {}
        for criterion in preset.criteria:
            for bucket, (mean_delta, n) in _YELLOW_DELTA_BY_BUCKET.items():
                deltas[(Hat.YELLOW, criterion.id, bucket)] = ConsultResult(mean_delta, n, 0.0, 10.0)
        anchors.append(
            CalibrationAnchor(
                weights_vector=tuple(preset.weights_vector),
                rubric_schema_hash=preset.rubric_schema_hash,
                deltas=deltas,
            )
        )
    return anchors


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
        repo_grader=_select_repo_grader(settings),
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
    if settings.consultant_backend == "anchor":
        # Weight-aware anchor retrieval (spec §8) with the table prior as the
        # cold-start / uncovered-cell fallback. The engine binds the rubric's
        # weights_vector at the audit step (see WeightAware).
        return AnchorConsultant(default_calibration_anchors(), backup=table)
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


def _select_repo_grader(settings: Settings) -> RepoGrader:
    if settings.repo_grader_backend == "github-api":
        from glasshat.code_grader import GitHubApiRepoGrader

        return GitHubApiRepoGrader(token=settings.github_token)
    return NullRepoGrader()


# Bound the whole repo-grading pre-step (network + parse). The grader's own httpx
# timeout guards each request; this guards the aggregate so a slow/hung repo can
# never delay the evaluation past a few seconds — on breach we run deck-only.
_REPO_GRADE_TIMEOUT_S = 20.0


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
    # Deck and repo evidence are indexed together in a SINGLE index() call:
    # HybridIndex.index() replaces its corpus each call, so two calls would drop
    # the deck. Repo grading is bounded and best-effort — any failure (bad URL,
    # network, timeout) degrades to a deck-only run rather than failing.
    index_chunks: list[Chunk] = []
    if inp.deck_text:
        index_chunks.extend(await ingest_deck(text=inp.deck_text, llm=deps.llm))
    if inp.repo_url:
        try:
            repo_chunks = await asyncio.wait_for(
                deps.repo_grader.chunks_for(inp.repo_url), timeout=_REPO_GRADE_TIMEOUT_S
            )
        except Exception:  # noqa: BLE001 — repo grading is best-effort; never fail the run
            # Best-effort, but not silent: a timeout / network / GitHub error is
            # logged (with the run_id for correlation) so a degraded deck-only
            # run is observable rather than mysterious.
            logger.warning(
                "repo grading failed for run %s; falling back to deck-only", run_id, exc_info=True
            )
            repo_chunks = []
        if repo_chunks:
            index_chunks.extend(repo_chunks)
            emit(Stage.INGESTING, repo_chunks=len(repo_chunks))
    if index_chunks:
        embedded = await embed_chunks(index_chunks, deps.llm)
        deps.retrieval.index(
            Document(id=c.id, text=c.text, vector=c.vector, payload={"source": c.source})
            for c in embedded
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
    # Bind the rubric's weighting for weight-aware consultants (AnchorConsultant)
    # so the audit consults the past evals whose rubric weighting is nearest this
    # run's. Non-weight-aware consultants (table, Phoenix-MCP) are used unchanged.
    consultant = deps.consultant
    if isinstance(consultant, WeightAware):
        consultant = consultant.for_weights(rubric.weights_vector)
        emit(Stage.ANCHOR_RETRIEVAL, weights_vector=list(rubric.weights_vector))
    with deps.tracer.span("agent_audit", **{"glasshat.agent": "Audit"}):
        corrections = await run_audit(assessments, consultant)
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
