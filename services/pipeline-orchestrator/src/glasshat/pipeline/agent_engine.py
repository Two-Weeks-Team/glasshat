"""Glasshat as a deployed ADK agent on the Gemini Enterprise Agent Platform.

This module is the evaluation *brain* that runs ON Agent Runtime (Agent Engine).
A query carries an ``EvaluationInput`` (JSON); the agent runs the SAME ADK 2.0
Workflow pipeline (``run_evaluation_adk``) and returns the ``RunRecord``. Because
the run goes through the real ADK Workflow graph with the OpenInference Google-ADK
instrumentor attached, the nested span TREE (sequential spine + parallel hat
fan-out + audit) lands in Arize AX.

Arize tracing landmine fix (documented by Arize for Agent Engine): the instrumentor
must be registered against an **isolated** tracer provider
(``set_global_tracer_provider=False``) because Agent Engine shuts down a *global*
provider during init → dropped traces. :func:`setup_arize_tracing` does exactly
that and is **guarded** on ``ARIZE_SPACE_ID`` / ``ARIZE_API_KEY`` so importing this
module locally / in CI is a credential-free no-op. All heavy SDKs (google.adk,
arize, vertexai) are imported lazily, so this module is safe to ship in the lean
image (it is only exercised by the deployed agent).
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from glasshat.agents.types import RunRecord

_ARIZE_PROJECT_DEFAULT = "glasshat"

# Tri-state import guard: None = not attempted, True/False = result. Keeps
# setup_arize_tracing idempotent (a second instrument() would double-count spans).
_TRACING_ENABLED: bool | None = None


def setup_arize_tracing(*, force: bool = False) -> bool:
    """Register the OpenInference Google-ADK instrumentor against an ISOLATED Arize
    AX tracer provider, so the deployed agent's nested Workflow span tree lands in
    AX without Agent Engine dropping it.

    Returns ``True`` when tracing was enabled, ``False`` when ARIZE creds are absent
    (a no-op — local/CI import stays credential-free). Idempotent. ``force`` re-runs
    the guard (used by tests)."""
    global _TRACING_ENABLED
    if _TRACING_ENABLED is not None and not force:
        return _TRACING_ENABLED
    space_id = os.environ.get("ARIZE_SPACE_ID")
    api_key = os.environ.get("ARIZE_API_KEY")
    if not (space_id and api_key):
        _TRACING_ENABLED = False
        return False
    # Imported here (not at module top) so the lean image never pulls arize unless
    # the deployed agent actually enables tracing.
    from arize.otel import register
    from openinference.instrumentation.google_adk import GoogleADKInstrumentor

    tracer_provider = register(
        space_id=space_id,
        api_key=api_key,
        project_name=os.environ.get("ARIZE_PROJECT_NAME", _ARIZE_PROJECT_DEFAULT),
        # Agent Engine shuts down a GLOBAL provider during init → dropped traces.
        set_global_tracer_provider=False,
    )
    GoogleADKInstrumentor().instrument(tracer_provider=tracer_provider)
    _TRACING_ENABLED = True
    return True


async def evaluate_message(text: str) -> RunRecord:
    """Parse an ``EvaluationInput`` JSON message and run the full ADK 2.0 Workflow
    pipeline, returning the ``RunRecord``.

    This is the deployed agent's core and is fully testable on the deterministic
    ``mock`` backend (no credentials). ``default_deps()`` reads the env-configured
    backends, so on Agent Engine it uses the real Gemini backend + Arize tracer."""
    from glasshat.agents.types import EvaluationInput
    from glasshat.pipeline.adk_agents import run_evaluation_adk
    from glasshat.pipeline.engine import default_deps

    inp = EvaluationInput.model_validate_json(text)
    return await run_evaluation_adk(inp, default_deps())


def build_root_agent() -> Any:
    """Build the deployed ADK agent: a thin ``BaseAgent`` that runs the Workflow
    pipeline for each query and returns the ``RunRecord`` JSON as the model turn.
    ``google.adk`` is imported lazily."""
    from google.adk.agents import BaseAgent
    from google.adk.events import Event
    from google.genai import types as gtypes

    class GlasshatEvalAgent(BaseAgent):  # type: ignore[misc]
        """Runs the glasshat evaluation Workflow for each query message."""

        async def _run_async_impl(self, ctx: Any) -> Any:
            content = getattr(ctx, "user_content", None)
            parts = content.parts if content is not None else []
            text = "".join(p.text for p in parts if getattr(p, "text", None))
            record = await evaluate_message(text)
            # invocation_id is REQUIRED by the Agent Engine managed Session service
            # (a bare Event → 400 INVALID_ARGUMENT on append). Carry it from the ctx.
            yield Event(
                invocation_id=getattr(ctx, "invocation_id", ""),
                author=self.name,
                content=gtypes.Content(
                    role="model", parts=[gtypes.Part(text=record.model_dump_json())]
                ),
            )

    return GlasshatEvalAgent(name="glasshat_eval")
