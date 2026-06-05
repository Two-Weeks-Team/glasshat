"""ADK runtime: the evaluation pipeline as a genuine Google ADK 2.0 Workflow graph.

``AGENT_RUNTIME=adk`` runs the SAME stage functions as the python runtime, but
wired as a real **ADK 2.0 Workflow** (graph-based "Workflow Runtime", GA
2026-05-19). The composition agents ``SequentialAgent`` / ``ParallelAgent`` /
``LoopAgent`` are deprecated in ADK 2.0; this module uses the canonical
``Workflow(edges=…)`` graph where each stage is a ``FunctionNode`` and the six
hats are an unconditional parallel fan-out joined by a ``JoinNode``::

    START → input_guard → ingest → synthesize → plan → hats_enter
          → ( hat_white ‖ hat_red ‖ hat_yellow ‖ hat_black ‖ hat_green ‖ hat_blue )
          → JoinNode → hats_gather → audit → score → persist

driven by the ADK ``Runner`` (``InMemoryRunner(node=workflow)``). With the
OpenInference Google-ADK instrumentor registered (live deployment), the graph
emits a nested span TREE to Arize AX — the sequential spine with a parallel
fan-out/join subtree — instead of the python path's flat manual spans. Every node
calls the identical pure stage function over the shared
:class:`~glasshat.pipeline.engine.RunContext`, so the ``RunRecord`` and the ordered
SSE stream are byte-identical to the python path (the parity test is the gate).
``google-adk`` is imported lazily, so importing this module never requires the
SDK; the graph is built only when a run actually uses ``adk``.

The single-pass audit (Tier B's ``LoopAgent(max_iterations=1)``) is a single audit
node here — byte-identical to the python path's one convergent pass. A future
multi-iteration audit would become a loop edge back into the audit node.
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

# ADK nodes (pydantic) and the ADK session store cannot carry the live, unpicklable
# RunContext. Instead each run registers its context under its unique run key; the
# node callables close over that key (a plain str) and look the context up here.
_RUN_REGISTRY: dict[str, RunContext] = {}

# One hat node per enum member, derived directly from the enum (no separate
# hardcoded list to drift out of sync). Fan-out order here is only the span-tree
# layout; the gather step re-orders by ``pln.hats_enabled`` so the assembled
# assessment list matches ``run_panel`` exactly.
_HATS: tuple[Hat, ...] = tuple(Hat)


async def _adk_hats_enter(ctx: RunContext) -> None:
    """Emit the single HATS_RUNNING event (the parallel fan-out provides the span tree)."""
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
# can fan out across the parallel group.
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

# The sequential spine, in order. ``hats_enter`` fans out to the six hat nodes;
# the JoinNode then resumes the spine at ``hats_gather``.
_SPINE_BEFORE_HATS = ("input_guard", "ingest", "synthesize", "plan", "hats_enter")
_SPINE_AFTER_HATS = ("hats_gather", "audit", "score", "persist")


def _build_workflow(run_key: str) -> Any:
    """Construct the root ADK 2.0 ``Workflow`` for one run. Defined here (lazy) so the
    google-adk import only happens on the ``adk`` path.

    Each node is a ``FunctionNode`` with ``parameter_binding="state"`` whose callable
    closes over ``run_key`` and runs the matching stage over the registered
    ``RunContext``. The callable takes a bare ``ctx`` parameter (no annotation) so
    ADK's state binding never tries to resolve a ``Context`` type hint under this
    module's ``from __future__ import annotations``."""
    from google.adk import Workflow
    from google.adk.workflow import FunctionNode, JoinNode

    def stage_node(stage_name: str) -> Any:
        async def _run(ctx: Any) -> None:  # noqa: ARG001 — ADK binds ctx; we use run_key
            await _STAGE_DISPATCH[stage_name](_RUN_REGISTRY[run_key])

        return FunctionNode(func=_run, name=stage_name, parameter_binding="state")

    def hat_node(hat: Hat) -> Any:
        async def _run(ctx: Any) -> None:  # noqa: ARG001 — ADK binds ctx; we use run_key
            await _adk_run_one_hat(_RUN_REGISTRY[run_key], hat.value)

        return FunctionNode(func=_run, name=f"hat_{hat.value}", parameter_binding="state")

    hats = tuple(hat_node(h) for h in _HATS)
    return Workflow(
        name="glasshat_pipeline",
        edges=[
            # START → sequential spine → fan-out to the six hats (the tuple = an
            # unconditional parallel group).
            ("START", *(stage_node(s) for s in _SPINE_BEFORE_HATS), hats),
            # Join the six hats, then resume the sequential spine.
            (hats, JoinNode(name="six_hat_join"), *(stage_node(s) for s in _SPINE_AFTER_HATS)),
        ],
    )


async def run_evaluation_adk(
    inp: EvaluationInput, deps: Deps, *, on_event: EventSink | None = None
) -> RunRecord:
    """Run the pipeline through the ADK 2.0 Workflow graph and return the RunRecord.

    Mirrors :func:`~glasshat.pipeline.engine.run_evaluation` exactly: same QUEUED
    event, same stage order, same per-stage events — only the orchestration is an
    ADK ``Runner`` driving the Workflow graph. A node that raises propagates out of
    ``run_async`` (and halts the graph), so failure paths match the python path.
    """
    from google.adk.runners import InMemoryRunner
    from google.genai import types as gtypes

    ctx = RunContext(inp=inp, deps=deps, emit=make_emit(on_event), run_id=new_uuid())
    ctx.emit(Stage.QUEUED, run_id=ctx.run_id)

    session_id = f"glasshat-{ctx.run_id}"
    _RUN_REGISTRY[session_id] = ctx
    try:
        root = _build_workflow(session_id)
        runner = InMemoryRunner(node=root, app_name="glasshat")
        await runner.session_service.create_session(
            app_name="glasshat", user_id="glasshat", session_id=session_id
        )
        # The seed message is ignored by the state-bound nodes (which read the
        # RunContext from the registry); ADK requires a message to start a run.
        message = gtypes.Content(role="user", parts=[gtypes.Part(text="evaluate")])
        async for _event in runner.run_async(
            user_id="glasshat", session_id=session_id, new_message=message
        ):
            pass
    finally:
        _RUN_REGISTRY.pop(session_id, None)

    assert ctx.record is not None
    return ctx.record
