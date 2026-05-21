from glasshat.agents.blue_planner import plan
from glasshat.agents.types import EvaluationInput
from glasshat.rubric.presets import load_preset
from glasshat.shared.enums import Hat


def test_plan_enables_six_hats_and_all_criteria() -> None:
    r = load_preset("rapid-agent")
    p = plan(r, EvaluationInput(rubric_source={"preset_id": "rapid-agent"}))
    assert set(p.hats_enabled) == set(Hat)
    assert set(p.criteria_in_scope) == {c.id for c in r.criteria}


def test_plan_weights_and_budget() -> None:
    r = load_preset("rapid-agent")
    p = plan(r, EvaluationInput(rubric_source={"preset_id": "rapid-agent"}))
    assert p.weights["tech-implementation"] == 0.25
    assert p.retrieval_budget["past_evals"] == 3


def test_plan_simple_average_weights_default_zero() -> None:
    r = load_preset("cmux-aim")  # weights are null
    p = plan(r, EvaluationInput(rubric_source={"preset_id": "cmux-aim"}))
    assert all(w == 0.0 for w in p.weights.values())
