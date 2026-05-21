"""Audit loop — calibration-driven self-correction (the wow moment).

A consultant supplies per-cell calibration stats (mean over/under-confidence vs
held-out anchors). Over-confident assessments are pulled back by the spike-D
formula ``new = clip(score - 0.8·mean_delta, p25, p75)`` with a ±2.0 absolute
cap. The default :class:`TableConsultant` is deterministic (in-code table); the
real Phoenix-MCP consultant (P3b) implements the same protocol over live trace
data. Source: ``docs/spike-results.md`` §4, ``docs/architecture.md`` §1.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from glasshat.agents.types import AuditCorrection, HatAssessment
from glasshat.shared.enums import Hat

_GAIN = 0.8
_THRESHOLD = 0.5
_MIN_N = 3
_MAX_ABS = 2.0


@dataclass(frozen=True)
class ConsultResult:
    """Calibration stats for one (hat, criterion, evidence-bucket) cell."""

    mean_delta: float
    n: int
    p25: float
    p75: float


@runtime_checkable
class Consultant(Protocol):
    """Supplies calibration stats for a given cell (table or Phoenix-MCP backed)."""

    async def consult(self, hat: Hat, criterion_id: str, bucket: str) -> ConsultResult | None: ...


class TableConsultant:
    """Deterministic consultant backed by an in-code calibration table."""

    def __init__(self, table: dict[tuple[Hat, str, str], ConsultResult]) -> None:
        self._table = table

    async def consult(self, hat: Hat, criterion_id: str, bucket: str) -> ConsultResult | None:
        return self._table.get((hat, criterion_id, bucket))


def bucket_of(evidence_depth: float) -> str:
    """Bucket evidence depth into low/mid/high (spike-D thresholds)."""
    if evidence_depth < 0.4:
        return "low"
    if evidence_depth < 0.7:
        return "mid"
    return "high"


def apply_correction(
    assessment: HatAssessment, consult: ConsultResult | None
) -> AuditCorrection | None:
    """Apply the calibration formula; return a correction only if it changes the score."""
    if consult is None or consult.n < _MIN_N or abs(consult.mean_delta) < _THRESHOLD:
        return None
    raw = assessment.score - _GAIN * consult.mean_delta
    clipped = max(consult.p25, min(consult.p75, raw))
    capped = max(assessment.score - _MAX_ABS, min(assessment.score + _MAX_ABS, clipped))
    corrected = round(capped, 2)
    if abs(corrected - assessment.score) < 1e-9:
        return None
    return AuditCorrection(
        hat=assessment.hat,
        criterion_id=assessment.criterion_id,
        original=assessment.score,
        corrected=corrected,
        mean_delta=consult.mean_delta,
        n=consult.n,
        reason=(
            f"{assessment.hat.value} over/under-confident on "
            f"'{assessment.criterion_id}' (evidence={bucket_of(assessment.evidence_depth)}, "
            f"mean_delta={consult.mean_delta:+.2f}, n={consult.n})"
        ),
    )


async def run_audit(
    assessments: Iterable[HatAssessment], consultant: Consultant
) -> list[AuditCorrection]:
    """Consult calibration for each assessment and collect the applied corrections."""
    corrections: list[AuditCorrection] = []
    for assessment in assessments:
        consult = await consultant.consult(
            assessment.hat, assessment.criterion_id, bucket_of(assessment.evidence_depth)
        )
        correction = apply_correction(assessment, consult)
        if correction is not None:
            corrections.append(correction)
    return corrections
