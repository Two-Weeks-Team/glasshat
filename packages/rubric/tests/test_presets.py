from glasshat.rubric.canonical import compute_weights_vector
from glasshat.rubric.presets import list_presets, load_preset


def test_four_presets() -> None:
    assert set(list_presets()) == {"qdrant", "rapid-agent", "cmux-aim", "gemini3"}


def test_all_presets_load_and_validate() -> None:
    for pid in list_presets():
        r = load_preset(pid)
        assert r.criteria  # constructs a valid SynthesizedRubric or raises
        assert r.rubric_schema_hash  # loader populates the hash
        assert r.source.identifier == pid


def test_rapid_agent_is_equal_25_not_40_30_20_10() -> None:
    """Locked decision 2026-05-21: official rule is 4 axes x equal 25%."""
    r = load_preset("rapid-agent")
    weights = {c.id: c.weight for c in r.criteria}
    assert weights == {
        "tech-implementation": 0.25,
        "design": 0.25,
        "potential-impact": 0.25,
        "quality-of-idea": 0.25,
    }
    assert compute_weights_vector(r) == [0.25, 0.25, 0.25, 0.25]


def test_rapid_agent_tie_break_order() -> None:
    """Tie-break by listed order: Tech -> Design -> Impact -> Idea."""
    r = load_preset("rapid-agent")
    order = [tb.criterion_id for tb in sorted(r.tie_breakers, key=lambda t: t.order)]
    assert order == [
        "tech-implementation",
        "design",
        "potential-impact",
        "quality-of-idea",
    ]


def test_qdrant_is_three_axis_simple_average() -> None:
    r = load_preset("qdrant")
    assert r.scoring_rule.aggregation == "simple_average"
    assert {c.id for c in r.criteria} == {"functionality", "originality", "user-experience"}


def test_load_unknown_preset_raises() -> None:
    import pytest

    with pytest.raises(KeyError):
        load_preset("does-not-exist")
