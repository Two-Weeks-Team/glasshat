import asyncio
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from glasshat.agents.audit import (
    AnchorConsultant,
    ConsultResult,
    DatasetExample,
    NullDatasetWriter,
    TableConsultant,
)
from glasshat.agents.types import EvaluationInput, RunRecord
from glasshat.pipeline.engine import (
    Deps,
    default_calibration_anchors,
    default_calibration_table,
    default_deps,
    run_evaluation,
)
from glasshat.pipeline.events import PipelineEvent, Stage
from glasshat.rubric.presets import list_presets, load_preset
from glasshat.shared.blobstore import LocalFsBlobStore
from glasshat.shared.docstore import MemoryDocStore
from glasshat.shared.enums import Hat, RunMode
from glasshat.shared.llm import MockLlmClient
from glasshat.shared.retrieval import HybridIndex
from glasshat.shared.tracing import NoOpTracer


class _RecordingTracer:
    """Tracer that records (span_name, attrs) so tests can assert per-agent spans."""

    def __init__(self) -> None:
        self.spans: list[tuple[str, dict[str, Any]]] = []

    @contextmanager
    def span(self, name: str, **attrs: Any) -> Iterator[SimpleNamespace]:
        self.spans.append((name, dict(attrs)))
        yield SimpleNamespace(set_attr=lambda *a, **k: None)

    def set_attr(self, key: str, value: Any) -> None:
        return None


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


def test_each_orchestration_agent_opens_a_distinct_glasshat_span(tmp_path: Path) -> None:
    """Every one of the 6 orchestration agents must emit its own glasshat.agent
    span so Arize AX can isolate each role (not just the 6-hat panel)."""
    tracer = _RecordingTracer()
    r = load_preset("rapid-agent")
    table = {
        (Hat.YELLOW, c.id, b): ConsultResult(1.74, 14, 6.0, 8.5)
        for c in r.criteria
        for b in ("low", "mid", "high")
    }
    deps = Deps(
        llm=MockLlmClient(embedding_dim=8),
        retrieval=HybridIndex(),
        docstore=MemoryDocStore(),
        blobstore=LocalFsBlobStore(str(tmp_path)),
        tracer=tracer,
        consultant=TableConsultant(table),
    )
    inp = EvaluationInput(
        rubric_source={"preset_id": "rapid-agent"}, deck_text="we built X with tests and design"
    )
    asyncio.run(run_evaluation(inp, deps))

    agents = {attrs["glasshat.agent"] for _, attrs in tracer.spans if "glasshat.agent" in attrs}
    assert {
        "RubricSynthesizer",
        "BluePlanner",
        "SixHatPanel",
        "Audit",
        "BMADScorer",
        "ReportAssembler",
    } <= agents
    # the 6-hat panel still emits its per-(hat, criterion) spans underneath
    assert any(name == "hat_assess" for name, _ in tracer.spans)


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


# --- Improvement A: learning-loop wiring ------------------------------------


class _RecordingDatasetWriter:
    """Captures the rows passed to ``add-dataset-examples`` for assertions."""

    def __init__(self) -> None:
        self.rows: list[DatasetExample] = []

    async def write(self, examples: list[DatasetExample]) -> int:
        self.rows.extend(examples)
        return len(examples)


class _RaisingDatasetWriter:
    async def write(self, examples: list[DatasetExample]) -> int:
        raise RuntimeError("phoenix outage")


def test_pre_audit_score_is_strictly_greater_when_yellow_gets_pulled_down(
    tmp_path: Path,
) -> None:
    """The rank-flip board needs both scores on the same RunRecord — and the
    pre-audit score must be strictly higher than the audited score whenever
    YELLOW's over-confidence gets corrected downward."""
    inp = EvaluationInput(
        rubric_source={"preset_id": "rapid-agent"},
        deck_text="we built a novel multi-agent system in python with tests and a clean design",
        mode=RunMode.JUDGE,
    )
    rec = asyncio.run(run_evaluation(inp, _deps(tmp_path)))
    assert len(rec.audit_corrections) >= 1
    assert rec.pre_audit_final_score > rec.final_score
    # And the SAME pipeline with no over-confident YELLOW should leave pre==post.


def test_pre_audit_score_equals_audited_when_no_corrections(tmp_path: Path) -> None:
    # Empty calibration table → no consultant signal → no corrections produced.
    deps = Deps(
        llm=MockLlmClient(embedding_dim=8),
        retrieval=HybridIndex(),
        docstore=MemoryDocStore(),
        blobstore=LocalFsBlobStore(str(tmp_path)),
        tracer=NoOpTracer(),
        consultant=TableConsultant({}),
    )
    inp = EvaluationInput(
        rubric_source={"preset_id": "rapid-agent"},
        deck_text="we built X with tests and design",
    )
    rec = asyncio.run(run_evaluation(inp, deps))
    assert rec.audit_corrections == []
    assert rec.pre_audit_final_score == rec.final_score
    assert rec.dataset_examples_used == 0
    assert rec.dataset_examples_added == 0


def test_dataset_writer_receives_one_row_per_correction(tmp_path: Path) -> None:
    writer = _RecordingDatasetWriter()
    deps = _deps(tmp_path)
    deps.dataset_writer = writer
    inp = EvaluationInput(
        rubric_source={"preset_id": "rapid-agent"},
        deck_text="we built a novel multi-agent system in python with tests and a clean design",
        mode=RunMode.JUDGE,
    )
    rec = asyncio.run(run_evaluation(inp, deps))
    assert len(writer.rows) == len(rec.audit_corrections) >= 1
    assert rec.dataset_examples_added == len(writer.rows)
    # The "n past evals informed this run" telemetry equals the max ConsultResult.n.
    assert rec.dataset_examples_used == max(c.n for c in rec.audit_corrections)
    # Each row's bucket is one of the spike-D evidence buckets, not None.
    assert {row.bucket for row in writer.rows} <= {"low", "mid", "high"}


def test_dataset_write_failure_does_not_fail_the_run(tmp_path: Path) -> None:
    """A Phoenix outage must never poison the evaluation. The run completes,
    the RunRecord persists, but `dataset_examples_added` is zero."""
    deps = _deps(tmp_path)
    deps.dataset_writer = _RaisingDatasetWriter()
    inp = EvaluationInput(
        rubric_source={"preset_id": "rapid-agent"},
        deck_text="we built a novel multi-agent system in python with tests and a clean design",
        mode=RunMode.JUDGE,
    )
    rec = asyncio.run(run_evaluation(inp, deps))
    assert rec.audit_corrections  # still ran the audit
    assert rec.dataset_examples_added == 0


def test_sse_emits_dataset_lookup_and_write_events(tmp_path: Path) -> None:
    deps = _deps(tmp_path)
    deps.dataset_writer = _RecordingDatasetWriter()
    inp = EvaluationInput(
        rubric_source={"preset_id": "rapid-agent"},
        deck_text="we built a novel multi-agent system in python with tests and a clean design",
        mode=RunMode.JUDGE,
    )
    events: list[PipelineEvent] = []
    asyncio.run(run_evaluation(inp, deps, on_event=events.append))
    stages = [e.stage for e in events]
    assert Stage.DATASET_LOOKUP in stages
    assert Stage.DATASET_WRITE in stages
    # DATASET_WRITE must fire *after* SCORE_CORRECTED (writes follow corrections).
    assert stages.index(Stage.SCORE_CORRECTED) < stages.index(Stage.DATASET_WRITE)


def test_default_deps_keeps_null_writer_for_credential_free_runs() -> None:
    deps = default_deps()
    assert isinstance(deps.dataset_writer, NullDatasetWriter)


# --- Improvement (a): repo_url -> code grader -> retrieval -------------------


class _RepoCorroboratingLlm(MockLlmClient):
    """A hat that rewards corroborating repo evidence: it emits a higher SCORE
    whenever a ``repo:*`` evidence ref appears in the prompt, so the presence of
    ``repo_url`` measurably changes the score — exactly the deferred-(a) wiring
    the Skeptic flagged (before this, ``repo_url`` was accepted but ignored and
    evidence was ``deck-0`` only)."""

    async def generate(self, prompt: str, *, tier: str = "flash", **kw: Any) -> str:
        if "repo:" in prompt:
            return "SCORE: 8.0\nRATIONALE: the repository corroborates the deck claim"
        return "SCORE: 5.0\nRATIONALE: deck only, no repository evidence"


def _repo_chunks() -> list[Any]:
    from glasshat.agents.types import Chunk

    return [
        Chunk(
            id="repo:readme",
            text="Repository README excerpt: a multi-agent evaluator.",
            source="repo",
        ),
        Chunk(
            id="repo:languages",
            text="Repository languages by byte share: Python (90000 bytes).",
            source="repo",
        ),
        Chunk(
            id="repo:facts",
            text="Repository facts: tests present=True; CI configured=True.",
            source="repo",
        ),
    ]


class _FakeRepoGrader:
    """Returns fixed repo chunks with no network — stands in for the live
    GitHubApiRepoGrader so the wiring is exercised hermetically."""

    def __init__(self, chunks: list[Any]) -> None:
        self._chunks = chunks
        self.calls = 0

    async def chunks_for(self, url: str) -> list[Any]:
        self.calls += 1
        return list(self._chunks)


def _repo_sensitive_deps(tmp_path: Path) -> Deps:
    # Empty table → no audit corrections, so the persisted score reflects the
    # raw hat verdict (isolating the repo-evidence effect from the audit).
    return Deps(
        llm=_RepoCorroboratingLlm(embedding_dim=8),
        retrieval=HybridIndex(),
        docstore=MemoryDocStore(),
        blobstore=LocalFsBlobStore(str(tmp_path)),
        tracer=NoOpTracer(),
        consultant=TableConsultant({}),
    )


def _tech_score(rec: RunRecord) -> float:
    return next(s.score for s in rec.scores if s.criterion_id == "tech-implementation")


def _tech_refs(rec: RunRecord) -> list[str]:
    return next(s.evidence_refs for s in rec.scores if s.criterion_id == "tech-implementation")


def test_repo_url_changes_tech_score_and_surfaces_repo_provenance(tmp_path: Path) -> None:
    deck = "we built a multi-agent system"
    # (1) deck-only baseline
    rec_a = asyncio.run(
        run_evaluation(
            EvaluationInput(rubric_source={"preset_id": "rapid-agent"}, deck_text=deck),
            _repo_sensitive_deps(tmp_path),
        )
    )
    # (2) SAME deck + a repo_url whose grader injects repo chunks
    deps_b = _repo_sensitive_deps(tmp_path)
    grader = _FakeRepoGrader(_repo_chunks())
    deps_b.repo_grader = grader
    rec_b = asyncio.run(
        run_evaluation(
            EvaluationInput(
                rubric_source={"preset_id": "rapid-agent"},
                deck_text=deck,
                repo_url="https://github.com/acme/widget",
            ),
            deps_b,
        )
    )

    assert grader.calls == 1
    # The tech-criterion score is strictly different *because* repo evidence
    # reached the hat — the whole point of wiring repo_url.
    assert _tech_score(rec_a) != _tech_score(rec_b)
    # Provenance surfaced: the audited tech criterion now cites repo evidence;
    # the deck-only baseline cites none.
    assert any(r.startswith("repo:") for r in _tech_refs(rec_b))
    assert not any(r.startswith("repo:") for r in _tech_refs(rec_a))


def test_repo_url_with_default_null_grader_stays_deck_only(tmp_path: Path) -> None:
    # repo_url present but the default NullRepoGrader yields nothing → no repo
    # evidence, no error, fully deck-only.
    rec = asyncio.run(
        run_evaluation(
            EvaluationInput(
                rubric_source={"preset_id": "rapid-agent"},
                deck_text="we built x",
                repo_url="https://github.com/acme/widget",
            ),
            _repo_sensitive_deps(tmp_path),
        )
    )
    for s in rec.scores:
        assert not any(r.startswith("repo:") for r in s.evidence_refs)


def test_repo_grader_failure_falls_back_to_deck_only(tmp_path: Path, caplog: Any) -> None:
    class _BoomGrader:
        async def chunks_for(self, url: str) -> list[Any]:
            raise RuntimeError("github down")

    deps = _repo_sensitive_deps(tmp_path)
    deps.repo_grader = _BoomGrader()
    with caplog.at_level("WARNING"):
        rec = asyncio.run(
            run_evaluation(
                EvaluationInput(
                    rubric_source={"preset_id": "rapid-agent"},
                    deck_text="we built a multi-agent system",
                    repo_url="https://github.com/acme/widget",
                ),
                deps,
            )
        )
    # The run completed despite the grader blowing up, and stayed deck-only.
    assert rec.final_score > 0
    for s in rec.scores:
        assert not any(r.startswith("repo:") for r in s.evidence_refs)
    # Best-effort, but not silent: the degraded run is logged for observability.
    assert any("repo grading failed" in m for m in caplog.messages)


def test_default_deps_uses_null_repo_grader() -> None:
    from glasshat.pipeline.engine import NullRepoGrader

    deps = default_deps()
    assert isinstance(deps.repo_grader, NullRepoGrader)


# --- Improvement (c): weight-aware anchor consultant wiring ------------------


def test_anchor_backend_binds_rubric_weights_and_emits_anchor_retrieval(
    tmp_path: Path,
) -> None:
    deps = Deps(
        llm=_OverconfidentYellowLlm(embedding_dim=8),
        retrieval=HybridIndex(),
        docstore=MemoryDocStore(),
        blobstore=LocalFsBlobStore(str(tmp_path)),
        tracer=NoOpTracer(),
        # Same wiring _select_consultant builds for CONSULTANT_BACKEND=anchor.
        consultant=AnchorConsultant(
            default_calibration_anchors(), backup=TableConsultant(default_calibration_table())
        ),
    )
    inp = EvaluationInput(
        rubric_source={"preset_id": "rapid-agent"},
        deck_text="we built a novel multi-agent system in python with tests",
        mode=RunMode.JUDGE,
    )
    events: list[PipelineEvent] = []
    rec = asyncio.run(run_evaluation(inp, deps, on_event=events.append))

    # The audit consulted via the weight-aware path → ANCHOR_RETRIEVAL fired with
    # the bound rubric weighting (honest: only emitted when actually weight-aware).
    anchor_events = [
        e for e in events if e.stage == Stage.ANCHOR_RETRIEVAL and "weights_vector" in e.payload
    ]
    assert anchor_events, "expected an ANCHOR_RETRIEVAL event carrying weights_vector"
    assert anchor_events[0].payload["weights_vector"] == [0.25, 0.25, 0.25, 0.25]
    # The rapid-agent anchor covers YELLOW cells with the spike-D prior, so the
    # over-confident YELLOW still gets pulled down (same as the table path).
    assert any(c.hat == Hat.YELLOW and c.original > c.corrected for c in rec.audit_corrections)


def test_default_calibration_anchors_are_per_preset_and_carry_real_prior() -> None:
    anchors = default_calibration_anchors()
    # One anchor per preset, each keyed by that preset's own weighting.
    assert len(anchors) == len(list_presets())
    # Honest seed: every YELLOW low-evidence delta is the measured spike-D prior
    # (1.45) — no fabricated cross-schema differentiation.
    for anchor in anchors:
        low_deltas = {
            res.mean_delta
            for (hat, _crit, bucket), res in anchor.deltas.items()
            if hat == Hat.YELLOW and bucket == "low"
        }
        assert low_deltas <= {1.45}


# --- F: end-to-end reproducibility ------------------------------------------


def test_evaluation_is_reproducible_run_id_aside(tmp_path: Path) -> None:
    """Two runs of the SAME deterministic deps on the SAME input must yield the
    SAME final_score, scores and corrections — only the run_id differs. Guards the
    'self-correction is real math, not theatre' claim against accidental
    nondeterminism (run with `uv run pytest -k reproducib`)."""
    inp = EvaluationInput(
        rubric_source={"preset_id": "rapid-agent"},
        deck_text="we built a novel multi-agent system in python with tests and a clean design",
        mode=RunMode.JUDGE,
    )
    rec_a = asyncio.run(run_evaluation(inp, _deps(tmp_path)))
    rec_b = asyncio.run(run_evaluation(inp, _deps(tmp_path)))

    assert rec_a.run_id != rec_b.run_id  # uuids differ
    assert rec_a.final_score == rec_b.final_score
    assert rec_a.pre_audit_final_score == rec_b.pre_audit_final_score
    assert [(s.criterion_id, s.score) for s in rec_a.scores] == [
        (s.criterion_id, s.score) for s in rec_b.scores
    ]
    assert [(c.hat, c.criterion_id, c.corrected) for c in rec_a.audit_corrections] == [
        (c.hat, c.criterion_id, c.corrected) for c in rec_b.audit_corrections
    ]
