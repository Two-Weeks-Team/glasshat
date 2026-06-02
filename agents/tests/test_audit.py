import asyncio

from glasshat.agents.audit import (
    AnchorConsultant,
    CalibrationAnchor,
    Consultant,
    ConsultResult,
    DatasetExample,
    FallbackConsultant,
    NullDatasetWriter,
    TableConsultant,
    WeightAware,
    apply_correction,
    bucket_of,
    make_dataset_examples,
    run_audit,
)
from glasshat.agents.types import AuditCorrection, HatAssessment
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


# --- Improvement A: learning-loop primitives --------------------------------


class _CountingConsultant:
    """Phoenix-MCP stand-in that returns a configured ``ConsultResult`` and
    counts how many times it was called — used to assert primary-vs-backup
    ordering in :class:`FallbackConsultant`."""

    def __init__(self, result: ConsultResult | None) -> None:
        self.calls = 0
        self._result = result

    async def consult(self, hat: Hat, criterion_id: str, bucket: str) -> ConsultResult | None:
        self.calls += 1
        return self._result


def test_fallback_consultant_satisfies_protocol() -> None:
    fb = FallbackConsultant(primary=TableConsultant({}), backup=TableConsultant({}))
    assert isinstance(fb, Consultant)


def test_fallback_consultant_uses_primary_when_warm() -> None:
    warm = ConsultResult(mean_delta=1.2, n=12, p25=6.0, p75=8.5)
    primary = _CountingConsultant(warm)
    backup = _CountingConsultant(ConsultResult(0.31, 99, 0.0, 10.0))
    fb = FallbackConsultant(primary=primary, backup=backup)
    out = asyncio.run(fb.consult(Hat.YELLOW, "tech-implementation", "low"))
    assert out is warm
    assert primary.calls == 1
    assert backup.calls == 0  # warm primary → backup is never consulted


def test_fallback_consultant_falls_back_on_cold_start() -> None:
    primary = _CountingConsultant(None)  # cold Phoenix dataset
    backup_result = ConsultResult(mean_delta=1.45, n=7, p25=0.0, p75=10.0)
    backup = _CountingConsultant(backup_result)
    fb = FallbackConsultant(primary=primary, backup=backup)
    out = asyncio.run(fb.consult(Hat.YELLOW, "tech-implementation", "low"))
    assert out is backup_result
    assert primary.calls == 1
    assert backup.calls == 1


def test_fallback_consultant_falls_back_on_too_few_samples() -> None:
    primary = _CountingConsultant(ConsultResult(mean_delta=1.0, n=2, p25=0.0, p75=10.0))
    backup = _CountingConsultant(ConsultResult(mean_delta=1.45, n=7, p25=0.0, p75=10.0))
    fb = FallbackConsultant(primary=primary, backup=backup)
    out = asyncio.run(fb.consult(Hat.YELLOW, "tech-implementation", "low"))
    assert out is not None and out.n == 7
    assert backup.calls == 1


def test_fallback_consultant_swallows_primary_exception() -> None:
    class _Boom:
        async def consult(self, *_args: object) -> ConsultResult | None:
            raise RuntimeError("phoenix outage")

    backup_result = ConsultResult(mean_delta=1.45, n=9, p25=0.0, p75=10.0)
    fb = FallbackConsultant(primary=_Boom(), backup=_CountingConsultant(backup_result))
    out = asyncio.run(fb.consult(Hat.YELLOW, "tech-implementation", "low"))
    assert out is backup_result


def test_make_dataset_examples_signs_deltas_and_recovers_bucket() -> None:
    over = AuditCorrection(
        hat=Hat.YELLOW,
        criterion_id="tech-implementation",
        original=9.0,
        corrected=7.84,
        mean_delta=1.45,
        n=7,
        reason="YELLOW over/under-confident on 'tech-implementation' "
        "(evidence=low, mean_delta=+1.45, n=7)",
    )
    under = AuditCorrection(
        hat=Hat.GREEN,
        criterion_id="quality-of-idea",
        original=4.0,
        corrected=4.8,
        mean_delta=-1.0,
        n=12,
        reason="GREEN over/under-confident on 'quality-of-idea' "
        "(evidence=high, mean_delta=-1.00, n=12)",
    )
    rows = make_dataset_examples([over, under], run_id="run-xyz", created_at="2026-05-27T00:00:00Z")
    assert len(rows) == 2
    over_row = rows[0]
    assert isinstance(over_row, DatasetExample)
    assert over_row.bucket == "low"
    assert over_row.delta == 1.16  # 9.0 - 7.84
    assert over_row.run_id == "run-xyz"
    under_row = rows[1]
    assert under_row.bucket == "high"
    assert under_row.delta == -0.8  # under-confident → upward correction → negative delta


def test_make_dataset_examples_defaults_unknown_bucket_to_mid() -> None:
    legacy = AuditCorrection(
        hat=Hat.YELLOW,
        criterion_id="design",
        original=9.0,
        corrected=7.0,
        mean_delta=2.5,
        n=4,
        reason="hand-written, no evidence marker",
    )
    rows = make_dataset_examples([legacy], run_id="r", created_at="t")
    assert rows[0].bucket == "mid"


def test_null_dataset_writer_returns_zero() -> None:
    out = asyncio.run(NullDatasetWriter().write([]))
    assert out == 0


# --- Improvement (c): weight-aware anchor retrieval -------------------------

_CELL = (Hat.YELLOW, "tech-implementation", "low")


def _anchor(weights: tuple[float, ...], mean_delta: float) -> CalibrationAnchor:
    return CalibrationAnchor(
        weights_vector=weights,
        rubric_schema_hash="h",
        deltas={_CELL: ConsultResult(mean_delta=mean_delta, n=9, p25=0.0, p75=10.0)},
    )


def test_anchor_consultant_satisfies_protocols() -> None:
    ac = AnchorConsultant([], backup=TableConsultant({}))
    assert isinstance(ac, Consultant)
    assert isinstance(ac, WeightAware)


def test_anchor_selection_changes_consult_result_with_weights() -> None:
    """The mechanism: binding a different rubric weighting selects a different
    nearest anchor, so the returned calibration changes. (Fixture anchors carry
    distinct deltas to exercise selection — the shipped seed does not fabricate
    cross-schema differences.)"""
    # Anchor A is weighted toward the first criterion, B toward the second; they
    # carry deliberately different deltas so the selected one is observable.
    anchor_a = _anchor((0.7, 0.1, 0.1, 0.1), mean_delta=1.45)
    anchor_b = _anchor((0.1, 0.7, 0.1, 0.1), mean_delta=0.31)
    consultant = AnchorConsultant([anchor_a, anchor_b], backup=TableConsultant({}), top_k=1)

    near_a = consultant.for_weights([0.65, 0.15, 0.1, 0.1])
    near_b = consultant.for_weights([0.15, 0.65, 0.1, 0.1])
    res_a = asyncio.run(near_a.consult(*_CELL))
    res_b = asyncio.run(near_b.consult(*_CELL))

    assert res_a is not None and res_b is not None
    assert res_a.mean_delta == 1.45  # picked anchor A
    assert res_b.mean_delta == 0.31  # picked anchor B
    assert res_a.mean_delta != res_b.mean_delta  # weights changed the result


def test_anchor_empty_corpus_falls_back_to_table() -> None:
    backup = TableConsultant({_CELL: ConsultResult(mean_delta=0.8, n=10, p25=0.0, p75=10.0)})
    consultant = AnchorConsultant([], backup=backup).for_weights([0.25, 0.25, 0.25, 0.25])
    res = asyncio.run(consultant.consult(*_CELL))
    assert res is not None and res.mean_delta == 0.8  # came from the table backup


def test_anchor_unbound_falls_back_to_table() -> None:
    # Never bound with for_weights → cannot rank anchors → uses the backup.
    backup = TableConsultant({_CELL: ConsultResult(mean_delta=0.8, n=10, p25=0.0, p75=10.0)})
    consultant = AnchorConsultant([_anchor((0.7, 0.1, 0.1, 0.1), 1.45)], backup=backup)
    res = asyncio.run(consultant.consult(*_CELL))
    assert res is not None and res.mean_delta == 0.8  # backup, anchors not consulted


def test_anchor_uncovered_cell_falls_back_to_table() -> None:
    backup = TableConsultant(
        {(Hat.GREEN, "design", "high"): ConsultResult(mean_delta=0.5, n=8, p25=0.0, p75=10.0)}
    )
    consultant = AnchorConsultant([_anchor((0.7, 0.1, 0.1, 0.1), 1.45)], backup=backup).for_weights(
        [0.7, 0.1, 0.1, 0.1]
    )
    # Anchor only covers _CELL; a different cell defers to the table.
    res = asyncio.run(consultant.consult(Hat.GREEN, "design", "high"))
    assert res is not None and res.mean_delta == 0.5
