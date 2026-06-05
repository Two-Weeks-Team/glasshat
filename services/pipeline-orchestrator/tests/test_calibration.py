"""Offline calibration harness (Tier C) — CI smoke + metric correctness."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from glasshat.agents.audit import TableConsultant
from glasshat.pipeline.calibration import (
    GoldenEntry,
    build_golden_from_devpost,
    hit_at_k,
    load_golden,
    run_calibration,
)
from glasshat.pipeline.engine import Deps, default_calibration_table
from glasshat.shared.blobstore import LocalFsBlobStore
from glasshat.shared.docstore import MemoryDocStore
from glasshat.shared.llm import MockLlmClient
from glasshat.shared.retrieval import HybridIndex
from glasshat.shared.tracing import NoOpTracer

_REPO = Path(__file__).resolve().parents[3]
_DATA = _REPO / "data" / "devpost-gemini3"
_EXPERIMENTS = _REPO / "experiments"
_WEB_RESULT = _REPO / "apps" / "web" / "lib" / "calibration-result.json"


def _mock_deps(tmp_path: Path) -> Deps:
    return Deps(
        llm=MockLlmClient(embedding_dim=8),
        retrieval=HybridIndex(),
        docstore=MemoryDocStore(),
        blobstore=LocalFsBlobStore(str(tmp_path)),
        tracer=NoOpTracer(),
        consultant=TableConsultant(default_calibration_table()),
    )


def test_hit_at_k_ranks_by_score() -> None:
    # Top-2 by score are (9.0, winner) and (8.0, non) → 1 winner of 2 = 0.5.
    scored = [(9.0, True), (8.0, False), (1.0, True), (0.5, False)]
    assert hit_at_k(scored, 2) == 0.5
    assert hit_at_k(scored, 4) == 0.5  # 2 winners of 4
    assert hit_at_k([], 13) == 0.0
    assert hit_at_k(scored, 0) == 0.0


def test_golden_entry_deck_text() -> None:
    e = GoldenEntry(software_id="1", title="Globot", tagline="does things", placed=True)
    assert e.deck_text() == "Globot. does things"


def test_build_golden_is_deterministic_with_13_winners() -> None:
    a = build_golden_from_devpost(
        _DATA / "winners.json", _DATA / "submissions.json", n_non_winners=5
    )
    b = build_golden_from_devpost(
        _DATA / "winners.json", _DATA / "submissions.json", n_non_winners=5
    )
    assert [e.software_id for e in a] == [e.software_id for e in b]  # no randomness
    assert sum(e.placed for e in a) == 13
    assert len(a) == 18  # 13 winners + 5 non-winners


def test_run_calibration_smoke(tmp_path: Path) -> None:
    # CI smoke: the harness runs end-to-end offline on a tiny set and returns a
    # well-formed, deterministic result with the honesty caveat.
    golden = build_golden_from_devpost(
        _DATA / "winners.json", _DATA / "submissions.json", n_non_winners=4
    )[:6]
    result = asyncio.run(run_calibration(golden, deps_factory=lambda: _mock_deps(tmp_path), k=3))
    assert result.backend == "mock"
    assert result.n == 6 and result.k == 3
    assert 0.0 <= result.hit_at_k_pre_audit <= 1.0
    assert 0.0 <= result.hit_at_k_post_audit <= 1.0
    assert result.delta == round(result.hit_at_k_post_audit - result.hit_at_k_pre_audit, 4)
    assert "not a rank curve" in result.caveat

    # Determinism: same golden + same mock backend → identical metric.
    again = asyncio.run(run_calibration(golden, deps_factory=lambda: _mock_deps(tmp_path), k=3))
    assert again.model_dump() == result.model_dump()


def test_committed_golden_and_result_are_consistent() -> None:
    # The committed artifacts the /judge page renders must be internally consistent.
    golden = load_golden(_EXPERIMENTS / "golden_rapid_agent.json")
    assert sum(e.placed for e in golden) == 13
    result = json.loads((_EXPERIMENTS / "calibration_result.json").read_text())
    assert result["k"] == 13
    assert result["n"] == len(golden)
    assert result["n_winners"] == 13
    assert result["backend"] == "mock"
    assert result["delta"] == round(result["hit_at_k_post_audit"] - result["hit_at_k_pre_audit"], 4)


def test_web_copy_matches_experiments_result() -> None:
    # The /judge page renders the web copy; it must never drift from the canonical
    # experiments result (both are emitted by run_calibration_experiment.py).
    assert _WEB_RESULT.read_text(encoding="utf-8") == (
        _EXPERIMENTS / "calibration_result.json"
    ).read_text(encoding="utf-8")
