"""Audit loop — calibration-driven self-correction (the wow moment).

A consultant supplies per-cell calibration stats (mean over/under-confidence vs
held-out anchors). Over-confident assessments are pulled back by the spike-D
formula ``new = clip(score - 0.8·mean_delta, p25, p75)`` with a ±2.0 absolute
cap. The default :class:`TableConsultant` is deterministic (in-code table); the
real Phoenix-MCP consultant (P3b) implements the same protocol over live trace
data, and the :class:`DatasetWriter` protocol closes the learning loop by
recording each correction back to the Phoenix Dataset that the next run will
consult — so the agent measurably improves over time. Sources:
``docs/spike-results.md`` §4 (calibration math) and §7 (annotation round trip),
``docs/architecture.md`` §1.
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


class FallbackConsultant:
    """Try a primary consultant first; on missing/empty cells defer to a backup.

    Wraps the live Phoenix-MCP consultant for cold-start safety: when the
    Phoenix dataset has fewer than the minimum samples (or the MCP call times
    out / raises), the deployed deterministic prior keeps the audit working.
    """

    def __init__(self, primary: Consultant, backup: Consultant) -> None:
        self._primary = primary
        self._backup = backup

    async def consult(self, hat: Hat, criterion_id: str, bucket: str) -> ConsultResult | None:
        try:
            result = await self._primary.consult(hat, criterion_id, bucket)
        except Exception:  # noqa: BLE001 — Phoenix MCP can fail many ways; we always fall back
            result = None
        if result is not None and result.n >= _MIN_N:
            return result
        return await self._backup.consult(hat, criterion_id, bucket)


@dataclass(frozen=True)
class DatasetExample:
    """One row written back to the Phoenix calibration dataset after a run.

    Future runs read these via :class:`~glasshat.shared.protocols.Consultant`
    implementations and use them to compute per-cell mean_delta / percentiles —
    closing the "agent improves over time" loop the Arize track explicitly
    weights.
    """

    hat: Hat
    criterion_id: str
    bucket: str
    delta: float
    run_id: str
    created_at: str


@runtime_checkable
class DatasetWriter(Protocol):
    """Persist audit corrections so future runs can learn from them."""

    async def write(self, examples: list[DatasetExample]) -> int: ...


class NullDatasetWriter:
    """No-op writer (default; used by tests, mock backend, and cold runs)."""

    async def write(self, examples: list[DatasetExample]) -> int:
        return 0


def make_dataset_examples(
    corrections: Iterable[AuditCorrection], *, run_id: str, created_at: str
) -> list[DatasetExample]:
    """Project applied corrections into rows the Phoenix calibration dataset accepts.

    ``delta = original − corrected``: positive = the hat was over-confident and
    we pulled it down; negative = under-confident and we pulled it up. The next
    run's :class:`Consultant` averages these deltas per cell to derive the
    spike-D mean / p25 / p75 used by :func:`apply_correction`.
    """
    return [
        DatasetExample(
            hat=c.hat,
            criterion_id=c.criterion_id,
            bucket=bucket,
            delta=round(c.original - c.corrected, 6),
            run_id=run_id,
            created_at=created_at,
        )
        for c in corrections
        for bucket in (_bucket_for_correction(c),)
    ]


def _bucket_for_correction(c: AuditCorrection) -> str:
    """Recover the evidence bucket from a correction's stored ``reason`` line.

    ``apply_correction`` writes ``evidence=<bucket>`` into the reason; we keep
    the dataset bucket consistent with the bucket the consultant was queried
    against. Falls back to ``mid`` for legacy / hand-written rows.
    """
    marker = "evidence="
    idx = c.reason.find(marker)
    if idx == -1:
        return "mid"
    rest = c.reason[idx + len(marker) :]
    end = rest.find(",")
    bucket = (rest if end == -1 else rest[:end]).strip()
    return bucket if bucket in {"low", "mid", "high"} else "mid"


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
