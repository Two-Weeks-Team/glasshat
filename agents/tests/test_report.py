import pytest
from glasshat.agents.report import assemble, final_score
from glasshat.agents.types import AuditCorrection, CriterionScore
from glasshat.rubric.models import SynthesizedRubric
from glasshat.rubric.presets import load_preset
from glasshat.shared.enums import Hat, RunMode


def _scores(rubric: SynthesizedRubric, value: float) -> list[CriterionScore]:
    return [CriterionScore(criterion_id=c.id, score=value) for c in rubric.criteria]


def test_weighted_sum_all_top_is_100() -> None:
    r = load_preset("rapid-agent")  # 25/25/25/25, scale 5, final 0-100
    assert final_score(r, _scores(r, 5.0)) == 100.0


def test_weighted_sum_all_mid() -> None:
    r = load_preset("rapid-agent")
    assert final_score(r, _scores(r, 3.0)) == 60.0  # 3/5 = 0.6 -> 60


def test_simple_average_qdrant_0_100() -> None:
    r = load_preset("qdrant")  # 3 axes, simple average, final 0-100, scale 5
    scores = [
        CriterionScore(criterion_id="functionality", score=4.0),
        CriterionScore(criterion_id="originality", score=5.0),
        CriterionScore(criterion_id="user-experience", score=4.0),
    ]
    assert final_score(r, scores) == pytest.approx(86.67, abs=0.1)  # 4.33/5 -> ~87


def test_native_scale_cmux_is_1_to_5() -> None:
    r = load_preset("cmux-aim")  # final_scale 1-5
    assert final_score(r, _scores(r, 3.0)) == 3.0


def test_assemble_builds_run_record() -> None:
    r = load_preset("rapid-agent")
    corr = AuditCorrection(
        hat=Hat.YELLOW,
        criterion_id="tech-implementation",
        original=9.0,
        corrected=7.6,
        mean_delta=1.74,
        n=14,
    )
    rr = assemble(
        "run-1", r, _scores(r, 5.0), [corr], mode=RunMode.JUDGE, created_at="2026-05-21T00:00:00Z"
    )
    assert rr.run_id == "run-1"
    assert rr.final_score == 100.0
    assert len(rr.audit_corrections) == 1
    assert rr.mode == RunMode.JUDGE
