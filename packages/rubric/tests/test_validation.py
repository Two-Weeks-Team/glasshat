from collections.abc import Callable

import pytest
import yaml
from glasshat.rubric.models import SynthesizedRubric
from glasshat.rubric.presets import PRESETS_DIR
from glasshat.rubric.validation import (
    RubricWarning,
    validate_custom_yaml,
    validate_rubric,
)
from glasshat.shared.errors import RubricValidationError

MakeRubric = Callable[..., SynthesizedRubric]


def test_source_clause_traceability_warns_when_excerpt_absent(make_rubric: MakeRubric) -> None:
    r = make_rubric(source_excerpts={"tech-implementation": "THIS IS NOT IN THE SOURCE"})
    warns = validate_rubric(r, source_text="the official rules text mentions nothing relevant")
    assert any("traceab" in w.message.lower() for w in warns)
    assert all(isinstance(w, RubricWarning) for w in warns)


def test_clean_rubric_no_warnings_without_source_text(make_rubric: MakeRubric) -> None:
    assert validate_rubric(make_rubric(), source_text=None) == []


def test_traceability_passes_when_all_excerpts_present(make_rubric: MakeRubric) -> None:
    r = make_rubric()
    source = " | ".join(c.source_excerpt for c in r.criteria)
    assert validate_rubric(r, source_text=source) == []


def test_validate_custom_yaml_roundtrip() -> None:
    body = yaml.safe_load((PRESETS_DIR / "qdrant.yaml").read_text())["synthesized"]
    r = validate_custom_yaml(body)
    assert r.scoring_rule.aggregation == "simple_average"


def test_validate_custom_yaml_rejects_garbage() -> None:
    with pytest.raises(RubricValidationError):
        validate_custom_yaml({"not": "a rubric"})


def test_low_confidence_warning(make_rubric: MakeRubric) -> None:
    r = make_rubric()
    r.confidence = 0.3
    warns = validate_rubric(r, source_text=None)
    assert any(w.code == "low_confidence" for w in warns)
