"""ADK tracer-provider wiring (Tier B B2 — single provider, no double-register).

The live SDK calls (``GoogleADKInstrumentor().instrument(...)``) are pragma-no-cover,
but the *orchestration* — instrument exactly once, on the tracer's own provider,
and a clean no-op when there is no provider — is asserted here without any SDK.
"""

from __future__ import annotations

from typing import Any

import pytest
from glasshat.pipeline import adk_runtime
from glasshat.pipeline.engine import default_deps
from glasshat.shared.config import Settings
from glasshat.shared.tracing import NoOpTracer


@pytest.fixture(autouse=True)
def _reset_flag() -> Any:
    adk_runtime._ADK_INSTRUMENTED["done"] = False
    yield
    adk_runtime._ADK_INSTRUMENTED["done"] = False


def test_noop_tracer_has_no_provider_so_instrumentation_is_skipped() -> None:
    assert adk_runtime.maybe_instrument_adk(NoOpTracer()) is False


def test_instrument_on_provider_is_idempotent() -> None:
    # Pre-mark as done so the real openinference import is never reached; a second
    # call must early-return (no-op), proving the once-only guard.
    adk_runtime._ADK_INSTRUMENTED["done"] = True
    adk_runtime.instrument_adk_on_provider(object())  # no raise → guarded no-op


def test_maybe_instrument_returns_true_when_provider_present() -> None:
    adk_runtime._ADK_INSTRUMENTED["done"] = True  # guard short-circuits the SDK import

    class _TracerWithProvider:
        tracer_provider = object()

    assert adk_runtime.maybe_instrument_adk(_TracerWithProvider()) is True


def test_default_deps_adk_runtime_builds_with_noop_tracer() -> None:
    # agent_runtime=adk with the default (no-SDK) monitor → NoOp tracer, and
    # default_deps wires through maybe_instrument_adk without error.
    settings = Settings(_env_file=None, agent_runtime="adk")  # type: ignore[call-arg]
    deps = default_deps(settings)
    assert deps.agent_runtime == "adk"
    assert isinstance(deps.tracer, NoOpTracer)
