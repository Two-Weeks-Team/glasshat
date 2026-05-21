"""BluePlanner — emits the inspectable plan object shown at human gate 1.

Deterministic: enables all six hats, scopes every rubric criterion, and carries
the rubric's weights + a default retrieval budget (architecture §6).
"""

from __future__ import annotations

from glasshat.agents.types import EvaluationInput, PlanObject
from glasshat.rubric.models import SynthesizedRubric
from glasshat.shared.enums import Hat

_DEFAULT_RETRIEVAL_BUDGET = {"pitch_chunks": 5, "repo_chunks": 5, "past_evals": 3}


def plan(rubric: SynthesizedRubric, inp: EvaluationInput) -> PlanObject:
    """Build the plan object for an evaluation."""
    return PlanObject(
        hats_enabled=list(Hat),
        criteria_in_scope=[c.id for c in rubric.criteria],
        retrieval_budget=dict(_DEFAULT_RETRIEVAL_BUDGET),
        weights={c.id: (c.weight or 0.0) for c in rubric.criteria},
        code_grader_depth="lint",
    )
