"""ADK runtime: the evaluation pipeline as a genuine Google ADK agent graph.

``AGENT_RUNTIME=adk`` runs the SAME stage functions as the python runtime, but
wired as a real ADK graph::

    SequentialAgent[
        input_guard, ingest, synthesize, plan,
        hats_enter, ParallelAgent[ one agent per hat ], hats_gather,
        LoopAgent[ audit ],            # single convergent pass today
        score, persist,
    ]

executed by the ADK ``Runner``. With the OpenInference Google ADK instrumentor
registered (live deployment), this emits a nested span TREE to Arize AX — the
Sequential → Parallel[6 hats] → Loop[audit] shape — instead of the python path's
flat manual spans. Every leaf calls the identical pure stage function over the
shared :class:`~glasshat.pipeline.engine.RunContext`, so the ``RunRecord`` and the
ordered SSE stream are byte-identical to the python path (the parity test is the
gate). ``google-adk`` is imported lazily, so importing this module never requires
the SDK; the agent classes are built only when a run actually uses ``adk``.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from glasshat.agents.hats import run_hat
from glasshat.agents.types import EvaluationInput, RunRecord
from glasshat.pipeline.engine import (
    Deps,
    EventSink,
    RunContext,
    make_emit,
    stage_audit,
    stage_ingest,
    stage_input_guard,
    stage_persist,
    stage_plan,
    stage_score,
    stage_synthesize,
)
from glasshat.pipeline.events import Stage
from glasshat.shared.enums import Hat
from glasshat.shared.ids import new_uuid

# ADK agents (pydantic, not picklable) cannot carry the live RunContext as a
# field, and the ADK session store would deep-copy it. Instead each run registers
# its context under its unique ADK session id; the leaf agents look it up by
# ``ctx.session.id`` (verified to hold object references in-process).
_RUN_REGISTRY: dict[str, RunContext] = {}

# The six hats, in canonical order. The ParallelAgent runs one leaf per hat; the
# gather step re-orders by ``pln.hats_enabled`` so the assembled assessment list
# matches ``run_panel`` exactly.
_HATS: tuple[Hat, ...] = (Hat.WHITE, Hat.RED, Hat.YELLOW, Hat.BLACK, Hat.GREEN, Hat.BLUE)


async def _adk_hats_enter(ctx: RunContext) -> None:
    """Emit the single HATS_RUNNING event (the ParallelAgent provides the span tree)."""
    assert ctx.pln is not None
    ctx.emit(Stage.HATS_RUNNING, hats=[h.value for h in ctx.pln.hats_enabled])


async def _adk_hats_gather(ctx: RunContext) -> None:
    """Concatenate the per-hat batches in ``hats_enabled`` order — identical to the
    list ``run_panel`` returns in the python runtime."""
    assert ctx.pln is not None
    ctx.assessments = [a for h in ctx.pln.hats_enabled for a in ctx.hat_batches.get(h.value, [])]


async def _adk_run_one_hat(ctx: RunContext, hat_value: str) -> None:
    """Run one hat over every in-scope criterion (skipping disabled hats), storing
    its batch for the gather step. Deterministic mock embeddings make the on-demand
    per-hat embedding identical to ``run_panel``'s shared-vector path."""
    assert ctx.pln is not None and ctx.rubric is not None
    hat = Hat(hat_value)
    if hat in ctx.pln.hats_enabled:
        ctx.hat_batches[hat.value] = await run_hat(
            hat,
            ctx.rubric,
            ctx.inp,
            ctx.deps.llm,
            ctx.deps.retrieval,
            ctx.deps.tracer,
            scoring_mode=ctx.deps.scoring_mode,
        )


# name -> stage coroutine. The deterministic stages reuse the engine's stage
# functions verbatim; only the hats are split (enter / per-hat / gather) so they
# can fan out across a ParallelAgent.
_STAGE_DISPATCH: dict[str, Callable[[RunContext], Awaitable[None]]] = {
    "input_guard": stage_input_guard,
    "ingest": stage_ingest,
    "synthesize": stage_synthesize,
    "plan": stage_plan,
    "hats_enter": _adk_hats_enter,
    "hats_gather": _adk_hats_gather,
    "audit": stage_audit,
    "score": stage_score,
    "persist": stage_persist,
}


def _build_pipeline_agent() -> Any:
    """Construct the root ADK SequentialAgent. Defined here (lazy) so the google-adk
    import only happens on the ``adk`` path."""
    from google.adk.agents import BaseAgent, LoopAgent, ParallelAgent, SequentialAgent

    class _StageLeaf(BaseAgent):  # type: ignore[misc]
        """A deterministic stage: looks up its run context and awaits the stage fn."""

        stage_name: str = ""

        async def _run_async_impl(self, adk_ctx: Any) -> Any:
            ctx = _RUN_REGISTRY[adk_ctx.session.id]
            await _STAGE_DISPATCH[self.stage_name](ctx)
            return
            yield  # pragma: no cover - marks this an async generator (ADK contract)

    class _HatLeaf(BaseAgent):  # type: ignore[misc]
        """One hat of the panel, run concurrently inside the ParallelAgent."""

        hat_value: str = ""

        async def _run_async_impl(self, adk_ctx: Any) -> Any:
            ctx = _RUN_REGISTRY[adk_ctx.session.id]
            await _adk_run_one_hat(ctx, self.hat_value)
            return
            yield  # pragma: no cover - marks this an async generator (ADK contract)

    def leaf(name: str) -> Any:
        return _StageLeaf(name=name, stage_name=name)

    panel = ParallelAgent(
        name="six_hat_panel",
        sub_agents=[_HatLeaf(name=f"hat_{h.value}", hat_value=h.value) for h in _HATS],
    )
    audit_loop = LoopAgent(name="audit_loop", max_iterations=1, sub_agents=[leaf("audit")])
    return SequentialAgent(
        name="glasshat_pipeline",
        sub_agents=[
            leaf("input_guard"),
            leaf("ingest"),
            leaf("synthesize"),
            leaf("plan"),
            leaf("hats_enter"),
            panel,
            leaf("hats_gather"),
            audit_loop,
            leaf("score"),
            leaf("persist"),
        ],
    )


async def run_evaluation_adk(
    inp: EvaluationInput, deps: Deps, *, on_event: EventSink | None = None
) -> RunRecord:
    """Run the pipeline through the ADK agent graph and return the RunRecord.

    Mirrors :func:`~glasshat.pipeline.engine.run_evaluation` exactly: same QUEUED
    event, same stage order, same per-stage events — only the orchestration is an
    ADK ``Runner`` driving the agent tree. A stage that raises propagates out of
    ``run_async`` (and halts the sequence), so failure paths match the python path.
    """
    from google.adk.runners import InMemoryRunner
    from google.genai import types as gtypes

    ctx = RunContext(inp=inp, deps=deps, emit=make_emit(on_event), run_id=new_uuid())
    ctx.emit(Stage.QUEUED, run_id=ctx.run_id)

    root = _build_pipeline_agent()
    session_id = f"glasshat-{ctx.run_id}"
    _RUN_REGISTRY[session_id] = ctx
    try:
        runner = InMemoryRunner(agent=root, app_name="glasshat")
        await runner.session_service.create_session(
            app_name="glasshat", user_id="glasshat", session_id=session_id
        )
        message = gtypes.Content(role="user", parts=[gtypes.Part(text="evaluate")])
        async for _event in runner.run_async(
            user_id="glasshat", session_id=session_id, new_message=message
        ):
            pass
    finally:
        _RUN_REGISTRY.pop(session_id, None)

    assert ctx.record is not None
    return ctx.record
