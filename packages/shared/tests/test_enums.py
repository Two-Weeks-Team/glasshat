from glasshat.shared.enums import Aggregation, Hat, RunMode, SourceKind
from glasshat.shared.errors import (
    GlasshatError,
    LlmError,
    RetrievalError,
    RubricValidationError,
    SynthesisError,
)


def test_six_hats() -> None:
    assert {h.value for h in Hat} == {"blue", "white", "red", "yellow", "black", "green"}


def test_aggregation_values() -> None:
    assert Aggregation.WEIGHTED_SUM.value == "weighted_sum"
    assert Aggregation.SIMPLE_AVERAGE.value == "simple_average"
    assert Aggregation.TIE_BREAK_ORDERED.value == "tie_break_ordered"


def test_source_kind() -> None:
    assert {s.value for s in SourceKind} == {"preset", "url", "pdf", "custom"}


def test_run_mode() -> None:
    assert {m.value for m in RunMode} == {"judge", "participant"}


def test_str_enum_is_str() -> None:
    assert Hat.BLUE == "blue"


def test_error_hierarchy() -> None:
    for exc in (RubricValidationError, SynthesisError, RetrievalError, LlmError):
        assert issubclass(exc, GlasshatError)
