"""Golden per-criterion score regression (A7).

Pins the deterministic mock-backed panel output for EVERY preset in BOTH scoring
modes. The ``legacy`` column is the contract that the Tier A security work did not
move the live demo's numbers (it must reproduce today's scores byte-for-byte);
the ``structured`` column pins the new typed-JSON path so future changes to it are
also caught. Regenerate intentionally with ``GLASSHAT_WRITE_GOLDEN=1``.
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from glasshat.agents.blue_planner import plan
from glasshat.agents.bmad_scorer import score
from glasshat.agents.hats import run_panel
from glasshat.agents.types import EvaluationInput
from glasshat.rubric.presets import list_presets, load_preset
from glasshat.shared.config import ScoringMode
from glasshat.shared.llm import MockLlmClient
from glasshat.shared.retrieval import Document, HybridIndex
from glasshat.shared.tracing import NoOpTracer

GOLDEN = Path(__file__).parent / "golden_scores.json"
DECK = (
    "We built a custom multi-agent evaluation system in Python with hybrid "
    "retrieval, a clean design, a smooth live demo, and a clear go-to-market plan."
)


def _index() -> HybridIndex:
    idx = HybridIndex()
    idx.index(
        [
            Document(id="c1", text="custom multi-agent architecture in python with retrieval"),
            Document(id="c2", text="clean design, smooth live demo, clear value proposition"),
            Document(id="c3", text="market analysis and go-to-market plan with early traction"),
        ]
    )
    return idx


def _criterion_scores(preset_id: str, mode: ScoringMode) -> dict[str, float]:
    rubric = load_preset(preset_id)
    inp = EvaluationInput(rubric_source={"preset_id": preset_id}, deck_text=DECK)
    pln = plan(rubric, inp)
    assessments = asyncio.run(
        run_panel(
            pln,
            rubric,
            inp,
            MockLlmClient(embedding_dim=8),
            _index(),
            NoOpTracer(),
            scoring_mode=mode,
        )
    )
    return {cs.criterion_id: cs.score for cs in score(rubric, assessments, [])}


def _compute_all() -> dict[str, dict[str, dict[str, float]]]:
    return {
        preset_id: {mode: _criterion_scores(preset_id, mode) for mode in ("legacy", "structured")}
        for preset_id in list_presets()
    }


def _canonical(obj: object) -> str:
    return json.dumps(obj, indent=2, sort_keys=True) + "\n"


def test_scoring_matches_pinned_golden() -> None:
    computed = _compute_all()
    if os.environ.get("GLASSHAT_WRITE_GOLDEN"):
        GOLDEN.write_text(_canonical(computed))
    expected = json.loads(GOLDEN.read_text())
    # Canonical-JSON string compare so float formatting is identical on both sides.
    assert _canonical(computed) == _canonical(expected)


def test_scoring_is_deterministic_across_runs() -> None:
    assert _compute_all() == _compute_all()


def test_legacy_and_structured_are_independent_paths() -> None:
    # The two modes are genuinely different code paths (not an alias): at least one
    # preset's per-criterion scores must differ between legacy and structured.
    allv = _compute_all()
    assert any(v["legacy"] != v["structured"] for v in allv.values())
