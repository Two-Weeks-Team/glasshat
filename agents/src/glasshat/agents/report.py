"""ReportAssembler — final score in the rubric's native scale + RunRecord.

Each criterion score is normalized to a 0-1 fraction (``score/scale``), combined
per the rubric's aggregation (weighted sum vs simple/tie-break average), then
projected onto the display scale's upper bound (100 for ``0-100``, 5 for ``1-5``,
etc.). Distinct rubrics over the same hat scores yield legitimately different
finals — the dual-rubric variance feature.
"""

from __future__ import annotations

from collections.abc import Iterable

from glasshat.agents.types import AuditCorrection, CriterionScore, RunRecord
from glasshat.rubric.models import SynthesizedRubric
from glasshat.shared.enums import Aggregation, RunMode


def _scale_top(final_scale: str) -> float:
    """Upper bound of the display scale ('0-100' -> 100, '1-5' -> 5)."""
    return float(final_scale.strip().split("-")[-1])


def final_score(rubric: SynthesizedRubric, scores: Iterable[CriterionScore]) -> float:
    """Compute the final score on the rubric's ``final_scale``."""
    by_id = {s.criterion_id: s.score for s in scores}
    fractions = {c.id: (by_id.get(c.id, 0.0) / c.scale) for c in rubric.criteria}  # 0-1, 1.0 = top
    if rubric.scoring_rule.aggregation == Aggregation.WEIGHTED_SUM:
        agg = sum((c.weight or 0.0) * fractions[c.id] for c in rubric.criteria)
    else:  # simple_average / tie_break_ordered
        agg = sum(fractions.values()) / len(fractions)
    return round(agg * _scale_top(rubric.scoring_rule.final_scale), 2)


def assemble(
    run_id: str,
    rubric: SynthesizedRubric,
    scores: list[CriterionScore],
    corrections: Iterable[AuditCorrection],
    *,
    mode: RunMode,
    created_at: str,
    pre_audit_scores: list[CriterionScore] | None = None,
) -> RunRecord:
    """Assemble the immutable run record.

    ``pre_audit_scores`` is the same scoring pass but with ``corrections=[]``;
    when supplied, its projected final score is preserved in
    :attr:`RunRecord.pre_audit_final_score` so the rank-flip board can show
    "without Glasshat audit" vs "with Glasshat audit" side by side.
    """
    audited_final = final_score(rubric, scores)
    pre_audit_final = (
        final_score(rubric, pre_audit_scores) if pre_audit_scores is not None else audited_final
    )
    return RunRecord(
        run_id=run_id,
        rubric=rubric,
        scores=scores,
        final_score=audited_final,
        pre_audit_final_score=pre_audit_final,
        audit_corrections=list(corrections),
        mode=mode,
        created_at=created_at,
    )
