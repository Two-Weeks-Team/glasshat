import asyncio

from glasshat.agents.audit import (
    ConsultResult,
    TableConsultant,
    apply_correction,
    bucket_of,
    run_audit,
)
from glasshat.agents.types import HatAssessment
from glasshat.shared.enums import Hat


def _yellow_low() -> HatAssessment:
    return HatAssessment(
        hat=Hat.YELLOW, criterion_id="tech-implementation", score=9.0, evidence_depth=0.3
    )


def test_bucket_of() -> None:
    assert bucket_of(0.3) == "low"
    assert bucket_of(0.5) == "mid"
    assert bucket_of(0.9) == "high"


def test_apply_correction_yellow_low_evidence_to_about_7_6() -> None:
    consult = ConsultResult(mean_delta=1.74, n=14, p25=6.0, p75=8.5)
    corr = apply_correction(_yellow_low(), consult)
    assert corr is not None
    assert corr.original == 9.0
    assert 7.5 <= corr.corrected <= 7.7  # 9.0 - 0.8*1.74 = 7.61


def test_apply_correction_is_bidirectional() -> None:
    """A negative mean_delta (an under-confident axis) is corrected *upward*."""
    under = HatAssessment(
        hat=Hat.GREEN, criterion_id="quality-of-idea", score=4.0, evidence_depth=0.8
    )
    corr = apply_correction(under, ConsultResult(mean_delta=-1.0, n=12, p25=0.0, p75=10.0))
    assert corr is not None
    assert corr.corrected == 4.8  # 4.0 - 0.8*(-1.0) = 4.8, raised, not lowered
    assert corr.corrected > corr.original


def test_no_correction_when_calibrated() -> None:
    assert apply_correction(_yellow_low(), ConsultResult(0.1, 20, 5.0, 9.0)) is None


def test_no_correction_when_too_few_samples() -> None:
    assert apply_correction(_yellow_low(), ConsultResult(1.74, 2, 6.0, 8.5)) is None


def test_absolute_cap_two_points() -> None:
    corr = apply_correction(_yellow_low(), ConsultResult(mean_delta=5.0, n=10, p25=0.0, p75=10.0))
    assert corr is not None
    assert corr.corrected == 7.0  # capped at original - 2.0


def test_table_consultant_lookup() -> None:
    t = TableConsultant(
        {(Hat.YELLOW, "tech-implementation", "low"): ConsultResult(1.74, 14, 6.0, 8.5)}
    )
    assert asyncio.run(t.consult(Hat.YELLOW, "tech-implementation", "low")).mean_delta == 1.74
    assert asyncio.run(t.consult(Hat.WHITE, "x", "low")) is None


def test_run_audit_corrects_only_flagged() -> None:
    assessments = [
        _yellow_low(),
        HatAssessment(
            hat=Hat.BLACK, criterion_id="tech-implementation", score=5.0, evidence_depth=0.3
        ),
    ]
    table = {(Hat.YELLOW, "tech-implementation", "low"): ConsultResult(1.74, 14, 6.0, 8.5)}
    corrections = asyncio.run(run_audit(assessments, TableConsultant(table)))
    assert len(corrections) == 1
    assert corrections[0].hat == Hat.YELLOW
