from collections.abc import Callable, Mapping, Sequence

import pytest
from glasshat.rubric.models import (
    Criterion,
    RubricSource,
    ScoringRule,
    SynthesizedRubric,
)
from glasshat.shared.enums import Aggregation, SourceKind

MakeRubric = Callable[..., SynthesizedRubric]


@pytest.fixture
def make_rubric() -> MakeRubric:
    """Build a valid SynthesizedRubric for tests.

    Args (all keyword):
      weights: mapping criterion_id -> weight (defaults to equal weights over `order`)
      order: explicit criterion id ordering (defaults to the 4 rapid-agent axes)
      aggregation: "weighted_sum" | "simple_average"
      source_excerpts: mapping criterion_id -> source_excerpt override
      scale: per-criterion integer scale (default 5)
    """

    def _make(
        *,
        weights: Mapping[str, float] | None = None,
        order: Sequence[str] | None = None,
        aggregation: str = "weighted_sum",
        source_excerpts: Mapping[str, str] | None = None,
        scale: int = 5,
    ) -> SynthesizedRubric:
        if weights is not None:
            ids = list(order) if order is not None else list(weights.keys())
            wmap = dict(weights)
        else:
            ids = (
                list(order)
                if order is not None
                else [
                    "tech-implementation",
                    "design",
                    "potential-impact",
                    "quality-of-idea",
                ]
            )
            wmap = {i: round(1.0 / len(ids), 6) for i in ids}

        excerpts: Mapping[str, str] = source_excerpts or {}
        crits = [
            Criterion(
                id=cid,
                label=cid.replace("-", " ").title(),
                weight=wmap[cid],
                scale=scale,
                bmad_mapping=["C1"],
                descriptor_levels={i: f"level {i}" for i in range(1, scale + 1)},
                source_clause=f"clause for {cid}",
                source_excerpt=excerpts.get(cid, f"excerpt for {cid}"),
            )
            for cid in ids
        ]
        return SynthesizedRubric(
            source=RubricSource(type=SourceKind.PRESET, identifier="test"),
            scoring_rule=ScoringRule(aggregation=Aggregation(aggregation), final_scale="0-100"),
            criteria=crits,
        )

    return _make
