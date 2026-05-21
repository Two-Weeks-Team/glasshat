"""Tracing abstraction: NoOp (default/CI) + Phoenix/OpenInference (real).

The Arize Stage-1 gate requires OpenInference auto-instrumentation sending
traces to Phoenix. :class:`PhoenixTracer` lazily imports ``phoenix.otel`` and
registers with ``auto_instrument=True``; it carries ``glasshat.*`` custom span
attributes. When the phoenix extra is not installed (e.g. CI), :func:`get_tracer`
degrades to :class:`NoOpTracer` so tracing never breaks the run.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from glasshat.shared.config import Settings, get_settings


class _NoOpSpan:
    def set_attr(self, key: str, value: Any) -> None:
        return None


class NoOpTracer:
    """A tracer that records nothing (used in tests/CI and when Phoenix is absent)."""

    @contextmanager
    def span(self, name: str, **attrs: Any) -> Iterator[_NoOpSpan]:
        yield _NoOpSpan()

    def set_attr(self, key: str, value: Any) -> None:
        return None


class _OtelSpan:  # pragma: no cover - requires phoenix/opentelemetry
    def __init__(self, span: Any) -> None:
        self._span = span

    def set_attr(self, key: str, value: Any) -> None:
        self._span.set_attribute(key, value)


class PhoenixTracer:  # pragma: no cover - requires the phoenix extra + collector
    """OpenInference -> Phoenix tracer with ``glasshat.*`` span attributes."""

    def __init__(self, settings: Settings | None = None) -> None:
        settings = settings or get_settings()
        from phoenix.otel import register

        register(project_name=settings.phoenix_project_name, auto_instrument=True)
        from opentelemetry import trace

        self._tracer = trace.get_tracer("glasshat")

    @contextmanager
    def span(self, name: str, **attrs: Any) -> Iterator[_OtelSpan]:
        with self._tracer.start_as_current_span(name) as sp:
            for key, value in attrs.items():
                sp.set_attribute(key, value)
            yield _OtelSpan(sp)

    def set_attr(self, key: str, value: Any) -> None:
        from opentelemetry import trace

        trace.get_current_span().set_attribute(key, value)


def get_tracer(settings: Settings | None = None) -> NoOpTracer | PhoenixTracer:
    """Return the configured tracer; NoOp when Phoenix is unavailable."""
    settings = settings or get_settings()
    if settings.monitor_backend.startswith("phoenix"):
        try:
            import phoenix.otel  # noqa: F401
        except ImportError:
            return NoOpTracer()
        return PhoenixTracer(settings)  # pragma: no cover - phoenix extra installed
    return NoOpTracer()
