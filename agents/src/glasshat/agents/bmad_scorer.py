"""BMADScorer — aggregate hat assessments into per-criterion native scores.

For each rubric criterion: take all hats' assessments, substitute any audited
(corrected) score for the original, average to an internal 0-10 score, then
rescale to the criterion's native scale (``1..scale``). The most impactful audit
correction for the criterion is attached for the report's audit trail.
"""

from __future__ import annotations

from collections.abc import Iterable

from glasshat.agents.types import AuditCorrection, CriterionScore, HatAssessment
from glasshat.rubric.models import SynthesizedRubric


def _rescale(internal: float, scale: int) -> float:
    """Map an internal 0-10 score onto the criterion's native ``1..scale``."""
    return round(1.0 + (internal / 10.0) * (scale - 1), 4)


def score(
    rubric: SynthesizedRubric,
    assessments: Iterable[HatAssessment],
    corrections: Iterable[AuditCorrection],
) -> list[CriterionScore]:
    """Produce one :class:`CriterionScore` per rubric criterion."""
    by_criterion: dict[str, list[HatAssessment]] = {}
    for a in assessments:
        by_criterion.setdefault(a.criterion_id, []).append(a)

    corr_by_cell: dict[tuple[str, str], AuditCorrection] = {}
    corr_by_criterion: dict[str, list[AuditCorrection]] = {}
    for c in corrections:
        corr_by_cell[(c.hat, c.criterion_id)] = c
        corr_by_criterion.setdefault(c.criterion_id, []).append(c)

    results: list[CriterionScore] = []
    for criterion in rubric.criteria:
        items = by_criterion.get(criterion.id, [])
        if items:
            effective = [
                corr_by_cell[(a.hat, a.criterion_id)].corrected
                if (a.hat, a.criterion_id) in corr_by_cell
                else a.score
                for a in items
            ]
            internal = sum(effective) / len(effective)
        else:
            internal = 5.0
        evidence: list[str] = []
        for a in items:
            for ref in a.evidence_refs:
                if ref not in evidence:
                    evidence.append(ref)
        crit_corrections = corr_by_criterion.get(criterion.id, [])
        audit = (
            max(crit_corrections, key=lambda c: abs(c.original - c.corrected))
            if crit_corrections
            else None
        )
        results.append(
            CriterionScore(
                criterion_id=criterion.id,
                score=_rescale(internal, criterion.scale),
                evidence_refs=evidence,
                audit=audit,
            )
        )
    return results
