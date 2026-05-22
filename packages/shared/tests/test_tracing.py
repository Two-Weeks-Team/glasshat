import pytest
from glasshat.shared.config import Settings
from glasshat.shared.protocols import Tracer
from glasshat.shared.tracing import NoOpTracer, get_tracer


def test_noop_is_tracer() -> None:
    assert isinstance(NoOpTracer(), Tracer)


def test_noop_span_and_set_attr_do_not_raise() -> None:
    t = NoOpTracer()
    with t.span("evaluate", **{"glasshat.hat": "blue"}) as span:
        span.set_attr("glasshat.criterion", "tech-implementation")
    t.set_attr("glasshat.predicted_score", 4)


def test_get_tracer_falls_back_to_noop_without_phoenix() -> None:
    # CI does not install the phoenix extra, so even monitor_backend=phoenix-local -> NoOp
    t = get_tracer(Settings(_env_file=None))  # type: ignore[call-arg]
    assert isinstance(t, NoOpTracer)


def test_get_tracer_arize_falls_back_to_noop_without_arize_otel() -> None:
    # CI does not install the arize extra, so monitor_backend=arize -> NoOp
    t = get_tracer(Settings(_env_file=None, monitor_backend="arize"))  # type: ignore[call-arg]
    assert isinstance(t, NoOpTracer)


@pytest.mark.integration
def test_phoenix_tracer_span_emits() -> None:
    pytest.importorskip("phoenix")
    from glasshat.shared.tracing import PhoenixTracer

    t = PhoenixTracer(Settings())
    with t.span("evaluate", **{"glasshat.hat": "blue"}) as span:
        span.set_attr("glasshat.criterion", "tech-implementation")
