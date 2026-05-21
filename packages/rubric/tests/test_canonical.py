from collections.abc import Callable

from glasshat.rubric.canonical import (
    canonicalize,
    compute_schema_hash,
    compute_weights_vector,
)
from glasshat.rubric.models import SynthesizedRubric

MakeRubric = Callable[..., SynthesizedRubric]


def test_weights_vector_is_alpha_by_criterion_id(make_rubric: MakeRubric) -> None:
    r = make_rubric(
        weights={
            "tech-implementation": 0.4,
            "design": 0.1,
            "potential-impact": 0.2,
            "quality-of-idea": 0.3,
        }
    )
    # alpha order: design, potential-impact, quality-of-idea, tech-implementation
    assert compute_weights_vector(r) == [0.1, 0.2, 0.3, 0.4]


def test_schema_hash_is_order_independent(make_rubric: MakeRubric) -> None:
    r1 = make_rubric(weights={"a": 0.5, "b": 0.5}, order=["a", "b"])
    r2 = make_rubric(weights={"a": 0.5, "b": 0.5}, order=["b", "a"])
    assert compute_schema_hash(r1) == compute_schema_hash(r2)


def test_schema_hash_changes_with_weights(make_rubric: MakeRubric) -> None:
    a = make_rubric(weights={"a": 0.5, "b": 0.5})
    b = make_rubric(weights={"a": 0.6, "b": 0.4})
    assert compute_schema_hash(a) != compute_schema_hash(b)


def test_schema_hash_is_64_hex(make_rubric: MakeRubric) -> None:
    h = compute_schema_hash(make_rubric())
    assert len(h) == 64 and all(c in "0123456789abcdef" for c in h)


def test_canonicalize_excludes_volatile_fields(make_rubric: MakeRubric) -> None:
    r = make_rubric()
    canon = canonicalize(r)
    assert "rubric_id" not in canon
    assert "confidence" not in canon
    # two rubrics differing only by rubric_id hash identically
    assert compute_schema_hash(make_rubric()) == compute_schema_hash(make_rubric())
