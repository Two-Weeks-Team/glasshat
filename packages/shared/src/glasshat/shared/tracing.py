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

        # Keep the registered provider so the ADK instrumentor (Tier B) can attach
        # to THIS single provider instead of registering a second one.
        self.tracer_provider = register(
            project_name=settings.phoenix_project_name, auto_instrument=True
        )
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


class ArizeTracer:  # pragma: no cover - requires the arize-otel extra + creds
    """OpenInference -> Arize AX tracer (otlp.arize.com, api_key + space_id)."""

    def __init__(self, settings: Settings | None = None) -> None:
        settings = settings or get_settings()
        from arize.otel import register

        # Register the Arize AX provider ONCE as the global provider, and keep it so
        # the ADK instrumentor (Tier B) attaches the nested agent spans to this same
        # provider rather than registering a second one (which would split traces).
        self.tracer_provider = register(
            space_id=settings.arize_space_id,
            api_key=settings.phoenix_api_key,
            project_name=settings.phoenix_project_name,
            set_global_tracer_provider=True,
        )
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


def get_tracer(settings: Settings | None = None) -> NoOpTracer | PhoenixTracer | ArizeTracer:
    """Return the configured tracer; NoOp when the backend's SDK is unavailable."""
    settings = settings or get_settings()
    if settings.monitor_backend == "arize":
        try:
            import arize.otel  # noqa: F401
        except ImportError:
            return NoOpTracer()
        return ArizeTracer(settings)  # pragma: no cover - arize extra installed
    if settings.monitor_backend.startswith("phoenix"):
        try:
            import phoenix.otel  # noqa: F401
        except ImportError:
            return NoOpTracer()
        return PhoenixTracer(settings)  # pragma: no cover - phoenix extra installed
    return NoOpTracer()
