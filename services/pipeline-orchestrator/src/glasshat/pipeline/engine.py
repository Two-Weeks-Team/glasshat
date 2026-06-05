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
    is_genuinely_weight_aware,
    make_dataset_examples,
    run_audit,
)
from glasshat.agents.blue_planner import plan
from glasshat.agents.bmad_scorer import score
from glasshat.agents.hats import run_panel
from glasshat.agents.injection_guard import (
    HeuristicInjectionGuard,
    InjectionGuard,
    get_injection_guard,
)
from glasshat.agents.report import assemble
from glasshat.agents.rubric_synthesizer import synthesize
from glasshat.agents.types import (
    AuditCorrection,
    Chunk,
    CriterionScore,
    EvaluationInput,
    HatAssessment,
    PlanObject,
    RunRecord,
)
from glasshat.ingest import embed_chunks, ingest_deck
from glasshat.pipeline.events import PipelineEvent, Stage
from glasshat.rubric.models import SynthesizedRubric
from glasshat.rubric.presets import list_presets, load_preset
from glasshat.shared.blobstore import get_blobstore
from glasshat.shared.config import AgentRuntime, ScoringMode, Settings, get_settings
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
    injection_guard: InjectionGuard = field(default_factory=HeuristicInjectionGuard)
    # ``legacy`` (default) keeps the live demo's hat-scoring byte-identical;
    # ``structured`` switches the panel to typed JSON scoring under a system
    # instruction that quarantines the untrusted submission (Tier A).
    scoring_mode: ScoringMode = "legacy"
    # ``python`` (default) runs the stages as a plain async sequence; ``adk`` runs
    # the SAME stages as a Google ADK agent graph for a nested Arize span tree
    # (Tier B). Both paths produce an identical RunRecord + SSE stream (parity test).
    agent_runtime: AgentRuntime = "python"


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
    tracer = get_tracer(settings)
    if settings.agent_runtime == "adk":
        # Attach the ADK instrumentor to the tracer's single (already-registered)
        # provider so the nested agent span tree lands in the same Arize/Phoenix
        # project as the manual spans. No-op for the NoOp tracer (tests/CI).
        from glasshat.pipeline.adk_runtime import maybe_instrument_adk

        maybe_instrument_adk(tracer)
    return Deps(
        llm=get_llm_client(settings),
        retrieval=HybridIndex(),
        docstore=get_docstore(settings),
        blobstore=get_blobstore(settings),
        tracer=tracer,
        consultant=_select_consultant(settings),
        dataset_writer=_select_dataset_writer(settings),
        repo_grader=_select_repo_grader(settings),
        injection_guard=get_injection_guard(settings),
        scoring_mode=settings.scoring_mode,
        agent_runtime=settings.agent_runtime,
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


@dataclass
class RunContext:
    """Mutable per-run state threaded through the pipeline stages.

    Both the ``python`` runtime (``run_evaluation``) and the ``adk`` runtime
    (:mod:`glasshat.pipeline.adk_agents`) drive the *same* stage functions over
    this context, so the two paths cannot drift: identical inputs produce an
    identical ``RunRecord`` and event stream (asserted by the ADK parity test).
    """

    inp: EvaluationInput
    deps: Deps
    emit: Callable[..., None]
    run_id: str
    rubric: SynthesizedRubric | None = None
    pln: PlanObject | None = None
    # per-hat assessment batches keyed by hat value (the ADK ParallelAgent writes
    # these concurrently; the gather step concatenates them in hats_enabled order).
    hat_batches: dict[str, list[HatAssessment]] = field(default_factory=dict)
    assessments: list[HatAssessment] = field(default_factory=list)
    weight_aware: bool = False
    corrections: list[AuditCorrection] = field(default_factory=list)
    dataset_examples_used: int = 0
    created_at: str = ""
    scores: list[CriterionScore] = field(default_factory=list)
    pre_audit_scores: list[CriterionScore] = field(default_factory=list)
    record: RunRecord | None = None
    dataset_examples_added: int = 0


async def stage_input_guard(ctx: RunContext) -> None:
    """Screen the untrusted submission for prompt-injection / score-steering before
    it reaches the panel. This does not block the run — the structural defense
    (typed scoring + quarantined <submission> in structured mode) is what stops a
    planted score — but the verdict is recorded as a glasshat.* span attribute so
    an attempt is observable in Arize AX."""
    deps, inp = ctx.deps, ctx.inp
    with deps.tracer.span("input_guard", **{"glasshat.agent": "InjectionGuard"}) as guard_span:
        # classify is sync; the default heuristic is instant CPU, but the optional
        # phoenix backend does blocking network I/O — offload so neither stalls the
        # event loop.
        verdict = await asyncio.to_thread(deps.injection_guard.classify, inp.deck_text or "")
        guard_span.set_attr("glasshat.injection_flag", verdict.flagged)
        guard_span.set_attr("glasshat.injection_guard_backend", verdict.backend)
        if verdict.flagged:
            logger.warning(
                "run %s: submission flagged by injection guard (%s); matched %d pattern(s)",
                ctx.run_id,
                verdict.backend,
                len(verdict.matched),
            )


async def stage_ingest(ctx: RunContext) -> None:
    deps, inp = ctx.deps, ctx.inp
    ctx.emit(Stage.INGESTING)
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
                "repo grading failed for run %s; falling back to deck-only",
                ctx.run_id,
                exc_info=True,
            )
            repo_chunks = []
        if repo_chunks:
            index_chunks.extend(repo_chunks)
            ctx.emit(Stage.INGESTING, repo_chunks=len(repo_chunks))
    if index_chunks:
        embedded = await embed_chunks(index_chunks, deps.llm)
        deps.retrieval.index(
            Document(id=c.id, text=c.text, vector=c.vector, payload={"source": c.source})
            for c in embedded
        )


async def stage_synthesize(ctx: RunContext) -> None:
    deps = ctx.deps
    with deps.tracer.span("agent_synthesize", **{"glasshat.agent": "RubricSynthesizer"}):
        ctx.rubric = await synthesize(ctx.inp, deps.llm)
    ctx.emit(Stage.PLANNING, rubric_id=ctx.rubric.rubric_id)


async def stage_plan(ctx: RunContext) -> None:
    assert ctx.rubric is not None
    with ctx.deps.tracer.span("agent_plan", **{"glasshat.agent": "BluePlanner"}):
        ctx.pln = plan(ctx.rubric, ctx.inp)


async def stage_hats(ctx: RunContext) -> None:
    """Run the full six-hat panel (python runtime). The ADK runtime replaces this
    with a ParallelAgent of one agent per hat + a gather, producing identical
    assessments; both emit the single HATS_RUNNING event below."""
    deps = ctx.deps
    assert ctx.pln is not None and ctx.rubric is not None
    ctx.emit(Stage.HATS_RUNNING, hats=[h.value for h in ctx.pln.hats_enabled])
    with deps.tracer.span(
        "agent_hats",
        **{"glasshat.agent": "SixHatPanel", "glasshat.hats": len(ctx.pln.hats_enabled)},
    ):
        ctx.assessments = await run_panel(
            ctx.pln,
            ctx.rubric,
            ctx.inp,
            deps.llm,
            deps.retrieval,
            deps.tracer,
            scoring_mode=deps.scoring_mode,
        )


async def stage_audit(ctx: RunContext) -> None:
    deps = ctx.deps
    assert ctx.rubric is not None
    ctx.emit(Stage.AUDITING)
    ctx.emit(Stage.AUDIT_STARTED)
    # Bind the rubric's weighting for weight-aware consultants (AnchorConsultant)
    # so the audit consults the past evals whose rubric weighting is nearest this
    # run's. Non-weight-aware consultants (table, Phoenix-MCP) are used unchanged.
    consultant = deps.consultant
    # A FallbackConsultant is WeightAware by protocol even when both children are
    # flat-prior — so gate the anchor-retrieval claims on *genuine* weight-awareness
    # (a real AnchorConsultant in the chain), not the bare protocol check.
    weight_aware = is_genuinely_weight_aware(consultant)
    if weight_aware and isinstance(consultant, WeightAware):  # narrows for .for_weights below
        consultant = consultant.for_weights(ctx.rubric.weights_vector)
        ctx.emit(Stage.ANCHOR_RETRIEVAL, weights_vector=list(ctx.rubric.weights_vector))
    ctx.weight_aware = weight_aware
    with deps.tracer.span("agent_audit", **{"glasshat.agent": "Audit"}):
        ctx.corrections = await run_audit(ctx.assessments, consultant)
    # Calibration sample size that actually informed this run — the "how many
    # past evals did we learn from?" telemetry the demo renders as a count-up.
    ctx.dataset_examples_used = max((c.n for c in ctx.corrections), default=0)
    ctx.emit(Stage.DATASET_LOOKUP, n_examples=ctx.dataset_examples_used)
    for c in ctx.corrections:
        ctx.emit(Stage.INCONSISTENCY_FLAGGED, hat=c.hat.value, criterion=c.criterion_id)
        ctx.emit(Stage.PHOENIX_CONSULTATION, mean_delta=c.mean_delta, n=c.n)
        # Only a weight-aware consultant (AnchorConsultant) genuinely retrieves a
        # per-anchor calibration; the table / Phoenix-MCP backends apply a flat
        # prior, so claiming anchor retrieval there would be theatre. Gate it.
        if weight_aware:
            ctx.emit(Stage.ANCHOR_RETRIEVAL, n=c.n)
        ctx.emit(
            Stage.SCORE_CORRECTED,
            **{
                "hat": c.hat.value,
                "criterion": c.criterion_id,
                "from": c.original,
                "to": c.corrected,
            },
        )


async def stage_score(ctx: RunContext) -> None:
    deps = ctx.deps
    assert ctx.rubric is not None
    ctx.created_at = _now()
    ctx.emit(Stage.SCORING)
    with deps.tracer.span("agent_score", **{"glasshat.agent": "BMADScorer"}):
        ctx.scores = score(ctx.rubric, ctx.assessments, ctx.corrections)
        # Pre-audit scores power the /judge rank-flip board: same hats, same
        # rubric, but no calibration applied — so judges can see *what would
        # have ranked* without Glasshat's self-correction.
        ctx.pre_audit_scores = score(ctx.rubric, ctx.assessments, [])
    with deps.tracer.span("agent_report", **{"glasshat.agent": "ReportAssembler"}):
        ctx.record = assemble(
            ctx.run_id,
            ctx.rubric,
            ctx.scores,
            ctx.corrections,
            pre_audit_scores=ctx.pre_audit_scores,
            mode=ctx.inp.mode,
            created_at=ctx.created_at,
        )


async def stage_persist(ctx: RunContext) -> None:
    deps = ctx.deps
    assert ctx.record is not None
    # Close the learning loop: write one example per correction to the dataset
    # so the next run's consultant has a richer prior. The writer is best-effort
    # — a Phoenix outage must not fail an evaluation. Counts feed the
    # /participate "calibration confidence (n)" chart.
    dataset_examples_added = 0
    if ctx.corrections:
        examples = make_dataset_examples(
            ctx.corrections, run_id=ctx.run_id, created_at=ctx.created_at
        )
        with deps.tracer.span("agent_dataset_writer", **{"glasshat.agent": "DatasetWriter"}):
            try:
                dataset_examples_added = await deps.dataset_writer.write(examples)
            except Exception:  # noqa: BLE001 — writer is best-effort, never block the run
                # Observable, not silent: a write failure means the learning loop
                # did not persist this run (e.g. Phoenix unreachable / mcp absent),
                # which must be visible in the deploy logs rather than masked as 0.
                logger.warning(
                    "dataset write failed for run %s; learning loop did not persist this run",
                    ctx.run_id,
                    exc_info=True,
                )
                dataset_examples_added = 0
    ctx.dataset_examples_added = dataset_examples_added
    ctx.emit(Stage.DATASET_WRITE, n_added=dataset_examples_added)

    ctx.record = ctx.record.model_copy(
        update={
            "dataset_examples_used": ctx.dataset_examples_used,
            "dataset_examples_added": dataset_examples_added,
        }
    )
    deps.docstore.put("runs", ctx.run_id, ctx.record.model_dump(mode="json"))
    ctx.emit(Stage.GRAPH_RESHAPE, criteria=len(ctx.scores))
    ctx.emit(Stage.COMPLETE, final_score=ctx.record.final_score)


# The pipeline as an ordered list of stage functions over a shared RunContext.
# The ``python`` runtime awaits them in sequence; the ``adk`` runtime wraps the
# same callables in ADK agents (hats fanned out to a ParallelAgent).
PIPELINE_STAGES: tuple[Callable[[RunContext], Any], ...] = (
    stage_input_guard,
    stage_ingest,
    stage_synthesize,
    stage_plan,
    stage_hats,
    stage_audit,
    stage_score,
    stage_persist,
)


def make_emit(on_event: EventSink | None) -> Callable[..., None]:
    """Build the event sink closure used by every stage."""

    def emit(stage: Stage, **payload: Any) -> None:
        if on_event is not None:
            on_event(PipelineEvent(stage=stage, payload=payload))

    return emit


async def run_evaluation(
    inp: EvaluationInput, deps: Deps, *, on_event: EventSink | None = None
) -> RunRecord:
    """Run the full evaluation pipeline and persist the immutable RunRecord.

    Dispatches on ``deps.agent_runtime``: ``python`` (default) runs the stages as a
    plain async sequence; ``adk`` runs the same stages as a Google ADK agent graph
    (identical result + events, asserted by the parity test)."""
    if deps.agent_runtime == "adk":
        from glasshat.pipeline.adk_agents import run_evaluation_adk

        return await run_evaluation_adk(inp, deps, on_event=on_event)

    ctx = RunContext(inp=inp, deps=deps, emit=make_emit(on_event), run_id=new_uuid())
    ctx.emit(Stage.QUEUED, run_id=ctx.run_id)
    for stage in PIPELINE_STAGES:
        await stage(ctx)
    assert ctx.record is not None
    return ctx.record
