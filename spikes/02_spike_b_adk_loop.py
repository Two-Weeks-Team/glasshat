"""Spike B — Google ADK LoopAgent + escalation + state sharing.

Validates:
  1. LoopAgent runs sub_agents iteratively
  2. State persists across iterations via ctx.session.state
  3. exit_loop tool (tool_context.actions.escalate=True) terminates the loop
  4. max_iterations cap prevents runaway loops
  5. (negative) without escalate, hits max_iterations safety net

PASS criterion:
  - Loop terminates via escalate before max_iter when calibration converges
  - State carries the corrected score across iterations
  - With unconvergeable rule, hits max_iter cap

No external services required. Uses ADK's InMemoryRunner.
"""

import asyncio
import json
import os
import time
from pathlib import Path

from google.adk.agents import LoopAgent, BaseAgent
from google.adk.runners import InMemoryRunner
from google.adk.events import Event
from google.adk.agents.invocation_context import InvocationContext
from google.adk.tools import ToolContext
from google.adk.tools.function_tool import FunctionTool
from google.genai import types
from typing import AsyncGenerator


RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)


# --- Mock sub-agents (do NOT call LLM, deterministic for spike) ----------

class MockInconsistencyDetector(BaseAgent):
    """Reads state.current_score; if score > evidence_threshold, flags audit."""

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        from google.adk.events import EventActions
        state = ctx.session.state
        current = state.get("current_score", 9.0)
        evidence = state.get("evidence_depth", 0.31)
        threshold = 0.4
        inconsistent = current >= 8.0 and evidence < threshold
        iter_count = state.get("iteration_count", 0) + 1
        # Live-mutate session state (works within run) AND emit state_delta
        # (persists past run via session service)
        state["inconsistency_flagged"] = inconsistent
        state["iteration_count"] = iter_count
        yield Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            actions=EventActions(
                state_delta={
                    "inconsistency_flagged": inconsistent,
                    "iteration_count": iter_count,
                }
            ),
            content=types.Content(
                role="model",
                parts=[
                    types.Part(
                        text=f"iter={iter_count} "
                        f"score={current} ev_depth={evidence} "
                        f"flagged={inconsistent}"
                    )
                ],
            ),
        )


class MockCalibrator(BaseAgent):
    """If flagged, reduces score by 0.8 * 1.4 (toward calibrated value).
    Calls exit_loop when score within target band."""

    def __init__(self, name: str, unconvergeable: bool = False):
        super().__init__(name=name)
        # Use object.__setattr__ to bypass pydantic ModelMetaclass field validation
        # for instance-level attribute on BaseAgent (pydantic v2)
        object.__setattr__(self, "_unconvergeable", unconvergeable)

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        state = ctx.session.state
        from google.adk.events import EventActions

        if not state.get("inconsistency_flagged"):
            state["exit_reason"] = "no_inconsistency"
            yield Event(
                invocation_id=ctx.invocation_id,
                author=self.name,
                actions=EventActions(escalate=True),
                content=types.Content(
                    role="model",
                    parts=[types.Part(text="EXIT_LOOP — converged")],
                ),
            )
            return

        # apply correction
        current = state.get("current_score", 9.0)
        if not self._unconvergeable:
            new_score = max(current - 1.4 * 0.8, 7.0)
        else:
            new_score = 9.0
        state["current_score"] = new_score

        yield Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            actions=EventActions(state_delta={"current_score": new_score}),
            content=types.Content(
                role="model",
                parts=[
                    types.Part(text=f"corrected score to {new_score}")
                ],
            ),
        )


# --- Test cases -----------------------------------------------------------

async def run_test(unconvergeable: bool, max_iter: int = 2) -> dict:
    detector = MockInconsistencyDetector(name="InconsistencyDetector")
    calibrator = MockCalibrator(name="Calibrator", unconvergeable=unconvergeable)

    loop_agent = LoopAgent(
        name="AuditLoop",
        sub_agents=[detector, calibrator],
        max_iterations=max_iter,
    )

    runner = InMemoryRunner(agent=loop_agent, app_name="spike_b")
    session = await runner.session_service.create_session(
        app_name="spike_b",
        user_id="spike",
        state={
            "current_score": 9.0,
            "evidence_depth": 0.31,
            "iteration_count": 0,
        },
    )

    events = []
    t0 = time.perf_counter()
    async for event in runner.run_async(
        user_id="spike",
        session_id=session.id,
        new_message=types.Content(
            role="user", parts=[types.Part(text="start audit")]
        ),
    ):
        events.append(
            {
                "author": event.author,
                "text": (
                    event.content.parts[0].text
                    if event.content and event.content.parts
                    else None
                ),
                "escalate": bool(event.actions and event.actions.escalate),
            }
        )
    dt = time.perf_counter() - t0

    # Fetch final session state
    final_session = await runner.session_service.get_session(
        app_name="spike_b", user_id="spike", session_id=session.id
    )
    final_state = dict(final_session.state) if final_session else {}

    return {
        "unconvergeable": unconvergeable,
        "max_iter": max_iter,
        "elapsed_sec": round(dt, 3),
        "event_count": len(events),
        "final_state": final_state,
        "events_tail": events[-6:],
    }


async def main():
    print("=" * 60)
    print("SPIKE B — ADK LoopAgent + escalation")
    print("=" * 60)

    # Case 1: convergeable — should exit early via escalate (≤2 iter)
    print("\n[Case 1] Convergeable — should exit via escalate")
    r1 = await run_test(unconvergeable=False, max_iter=5)
    print(json.dumps(r1, indent=2, default=str))

    # Case 2: unconvergeable — should hit max_iter=2 cap
    print("\n[Case 2] Unconvergeable — should hit max_iter=2 cap")
    r2 = await run_test(unconvergeable=True, max_iter=2)
    print(json.dumps(r2, indent=2, default=str))

    # Assess pass/fail using events (state_delta now also persists post-run)
    c1_pass = (
        r1["final_state"].get("iteration_count", 99) <= 3
        and any(e.get("escalate") for e in r1["events_tail"])
        and r1["final_state"].get("current_score", 9.0) < 9.0
    )
    c2_pass = (
        r2["final_state"].get("iteration_count", 0) == 2
        and r2["final_state"].get("current_score", 0) == 9.0
        and not any(e.get("escalate") for e in r2["events_tail"])
    )

    overall = c1_pass and c2_pass
    result = {
        "spike": "B",
        "title": "ADK LoopAgent + escalation",
        "case_1_convergeable": {"pass": c1_pass, "details": r1},
        "case_2_unconvergeable_capped": {"pass": c2_pass, "details": r2},
        "overall_pass": overall,
        "findings": [
            "LoopAgent runs sub_agents in order, repeating until escalate or max_iter",
            "ctx.session.state is shared across iterations",
            "EventActions(escalate=True) cleanly terminates the loop",
            "max_iterations safely caps unconvergeable cases",
        ]
        if overall
        else ["FAILURE — see case_X details above"],
    }

    out_path = RESULTS_DIR / "spike_b_adk_loop.json"
    out_path.write_text(json.dumps(result, indent=2, default=str))
    print(f"\nResult written: {out_path}")
    print(f"\n[{'PASS' if overall else 'FAIL'}] Spike B")
    return 0 if overall else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    raise SystemExit(exit_code)
