"""The ``SynthesizedRubric`` contract and its components.

This pydantic model is the cross-language source of truth; the JSON Schema in
``packages/rubric/synthesized.schema.json`` is generated from it (see
:mod:`glasshat.rubric.schema`). Structure follows
``docs/rubric-synthesis-spec.md`` §3.
"""

from __future__ import annotations

from glasshat.rubric.bmad import is_valid_primitive
from glasshat.shared.enums import Aggregation, SourceKind
from glasshat.shared.ids import new_uuid
from pydantic import BaseModel, Field, field_validator, model_validator


class Criterion(BaseModel):
    """One scored axis of a rubric, mapped onto BMAD primitives."""

    id: str
    label: str
    weight: float | None = None
    scale: int = Field(ge=2)
    bmad_mapping: list[str] = Field(min_length=1)
    descriptor_levels: dict[int, str]
    evidence_required: bool = True
    source_clause: str = ""
    source_excerpt: str = ""

    @field_validator("bmad_mapping")
    @classmethod
    def _bmad_codes_valid(cls, v: list[str]) -> list[str]:
        bad = [c for c in v if not is_valid_primitive(c)]
        if bad:
            raise ValueError(f"unknown BMAD primitive(s): {bad}")
        return v

    @model_validator(mode="after")
    def _descriptors_cover_scale(self) -> Criterion:
        # Numeric scales (1..N, N<=10) must have a descriptor for every level.
        if self.scale <= 10:
            expected = set(range(1, self.scale + 1))
            if set(self.descriptor_levels) != expected:
                raise ValueError(
                    f"descriptor_levels must cover {sorted(expected)}, "
                    f"got {sorted(self.descriptor_levels)}"
                )
        return self


class TieBreaker(BaseModel):
    """One step in the ordered tie-break chain (lower ``order`` breaks first)."""

    order: int = Field(ge=1)
    criterion_id: str


class ThresholdGate(BaseModel):
    """A pass/fail rule separate from scoring (e.g. 'must have public repo')."""

    id: str
    condition: str
    check: str = "manual"  # "manual" | "automated"

    @field_validator("check")
    @classmethod
    def _check_kind(cls, v: str) -> str:
        if v not in ("manual", "automated"):
            raise ValueError("check must be 'manual' or 'automated'")
        return v


class RubricSource(BaseModel):
    """Provenance of the synthesized rubric."""

    type: SourceKind
    identifier: str
    fetched_at: str | None = None
    source_text_excerpt: str = ""


class ScoringRule(BaseModel):
    """How per-criterion scores aggregate, and the display scale."""

    aggregation: Aggregation
    final_scale: str = "0-100"


class SynthesizedRubric(BaseModel):
    """A per-evaluation rubric whose axes mirror the source-of-truth rules."""

    schema_version: str = "1.0"
    rubric_id: str = Field(default_factory=new_uuid)
    rubric_schema_hash: str = ""
    source: RubricSource
    scoring_rule: ScoringRule
    criteria: list[Criterion] = Field(min_length=1)
    tie_breakers: list[TieBreaker] = Field(default_factory=list)
    threshold_gates: list[ThresholdGate] = Field(default_factory=list)
    weights_vector: list[float] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    warnings: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _consistency(self) -> SynthesizedRubric:
        agg = self.scoring_rule.aggregation
        weights = [c.weight for c in self.criteria]

        if agg == Aggregation.WEIGHTED_SUM:
            if any(w is None for w in weights):
                raise ValueError("weighted_sum requires a weight on every criterion")
            total = sum(w for w in weights if w is not None)
            if abs(total - 1.0) > 0.01:
                raise ValueError(f"weighted_sum weights must total 1.0 (got {total:.4f})")
        elif agg == Aggregation.SIMPLE_AVERAGE:
            non_null = [round(w, 6) for w in weights if w is not None]
            if non_null and len(set(non_null)) > 1:
                raise ValueError("simple_average requires equal (or null) weights")

        crit_ids = {c.id for c in self.criteria}
        for tb in self.tie_breakers:
            if tb.criterion_id not in crit_ids:
                raise ValueError(f"tie_breaker references unknown criterion '{tb.criterion_id}'")
        orders = [tb.order for tb in self.tie_breakers]
        if len(orders) != len(set(orders)):
            raise ValueError("tie_breaker orders must be unique")
        return self
