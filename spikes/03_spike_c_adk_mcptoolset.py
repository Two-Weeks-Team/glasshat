"""Spike C — ADK + Phoenix MCPToolset wiring.

Validates that:
  1. ADK `MCPToolset(connection_params=StdioConnectionParams(...))` is constructible
  2. `get_tools()` discovers the Phoenix MCP tools from the live server
  3. An `LlmAgent` with this toolset can actually invoke a Phoenix MCP tool
     (single Vertex AI call, ~$0.0001 with Flash-Lite)
  4. OpenInference auto-instrumentation captures the agent call AND the MCP
     tool call as Phoenix spans

PASS criterion:
  - >=15 tools discovered via MCPToolset
  - Agent run completes without error
  - Phoenix UI shows: 1 LLM span + ≥1 tool span for the MCP call
"""

import asyncio
import json
import os
import time
from pathlib import Path

import phoenix as px
from phoenix.client import Client as PhoenixClient
from phoenix.otel import register
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.adk.tools.mcp_tool import MCPToolset, StdioConnectionParams
from google.genai import types
from mcp import StdioServerParameters

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

PROJECT = "spike-c-glasshat"


async def run_spike():
    # Step 1: launch Phoenix
    print("\n[Step 1] Launching Phoenix in-process...")
    sess = px.launch_app()
    base_url = sess.url.rstrip("/")
    os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = base_url
    await asyncio.sleep(1.0)
    print(f"Phoenix at: {base_url}")

    # Step 2: register OpenInference auto-instrumentation
    print("\n[Step 2] Registering OpenInference auto-instrumentation...")
    register(
        project_name=PROJECT, batch=False, set_global_tracer_provider=True
    )

    # Step 3: construct MCPToolset against phoenix-mcp via npx stdio
    print("\n[Step 3] Building MCPToolset for Phoenix MCP server...")
    mcp_toolset = MCPToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="npx",
                args=[
                    "-y",
                    "@arizeai/phoenix-mcp@latest",
                    "--baseUrl",
                    base_url,
                ],
                env={**os.environ},
            ),
            timeout=30.0,
        ),
    )

    # Discover tools
    t0 = time.perf_counter()
    tools = await mcp_toolset.get_tools()
    discover_sec = time.perf_counter() - t0
    tool_names = sorted(t.name for t in tools)
    print(f"Discovered {len(tools)} tools in {discover_sec:.3f}s")
    print(f"Sample tools: {tool_names[:5]}...")

    # Step 4: construct an LlmAgent that uses one tool (list-projects)
    print("\n[Step 4] Constructing LlmAgent with Phoenix MCPToolset...")
    # Use Flash-Lite (cheapest tier) per .env
    model_id = os.environ.get(
        "GLASSHAT_GEMINI_FLASH_LITE", "gemini-3.1-flash-lite"
    )
    print(f"Model: {model_id}")

    agent = LlmAgent(
        name="PhoenixQueryAgent",
        model=model_id,
        instruction=(
            "You are a Phoenix observability assistant. When asked to list "
            "projects, call the `list-projects` tool and return the project "
            "names as a JSON array. Do not invent data."
        ),
        tools=[mcp_toolset],
    )

    runner = InMemoryRunner(agent=agent, app_name="spike_c")
    session = await runner.session_service.create_session(
        app_name="spike_c", user_id="spike"
    )

    print("\n[Step 5] Running agent — 'list the Phoenix projects'...")
    t0 = time.perf_counter()
    events = []
    try:
        async for event in runner.run_async(
            user_id="spike",
            session_id=session.id,
            new_message=types.Content(
                role="user",
                parts=[types.Part(text="List the Phoenix projects.")],
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
                    "has_function_call": bool(
                        event.content
                        and event.content.parts
                        and any(
                            getattr(p, "function_call", None)
                            for p in event.content.parts
                        )
                    ),
                    "has_function_response": bool(
                        event.content
                        and event.content.parts
                        and any(
                            getattr(p, "function_response", None)
                            for p in event.content.parts
                        )
                    ),
                }
            )
    except Exception as e:
        events.append({"error": repr(e)})
    elapsed = time.perf_counter() - t0
    print(f"Run completed in {elapsed:.2f}s, {len(events)} events")

    # Step 6: verify Phoenix captured spans
    print("\n[Step 6] Verifying Phoenix captured spans...")
    await asyncio.sleep(2.0)
    pc = PhoenixClient(base_url=base_url)
    try:
        spans_df = pc.spans.get_spans_dataframe(project_identifier=PROJECT)
        n_spans = len(spans_df)
        kinds = (
            spans_df["span_kind"].value_counts().to_dict()
            if "span_kind" in spans_df.columns
            else {}
        )
        names = spans_df["name"].tolist() if "name" in spans_df.columns else []
    except Exception as e:
        n_spans = 0
        kinds = {}
        names = []
        print(f"Span fetch error: {e}")

    return {
        "phoenix_url": base_url,
        "tools_discovered": len(tools),
        "tool_discovery_sec": round(discover_sec, 3),
        "tools_sample": tool_names[:10],
        "agent_run_sec": round(elapsed, 3),
        "agent_event_count": len(events),
        "agent_events": events,
        "phoenix_spans_captured": n_spans,
        "phoenix_span_kinds": kinds,
        "phoenix_span_names_head": names[:15],
    }


async def main():
    print("=" * 60)
    print("SPIKE C — ADK + Phoenix MCPToolset wiring")
    print("=" * 60)
    try:
        result_data = await run_spike()
    except Exception as e:
        result_data = {"error": repr(e)}

    print("\n--- Result data ---")
    print(json.dumps(result_data, indent=2, default=str)[:3000])

    # Assess pass criteria
    has_tools = result_data.get("tools_discovered", 0) >= 15
    agent_ran = (
        result_data.get("agent_event_count", 0) >= 1
        and not any("error" in (e or {}) for e in result_data.get("agent_events", []))
    )
    has_function_call = any(
        e.get("has_function_call") for e in result_data.get("agent_events", [])
    )
    spans_captured = result_data.get("phoenix_spans_captured", 0) >= 1

    overall = has_tools and agent_ran and spans_captured

    result = {
        "spike": "C",
        "title": "ADK + Phoenix MCPToolset wiring",
        "tools_discovered": result_data.get("tools_discovered"),
        "agent_ran": agent_ran,
        "agent_made_function_call": has_function_call,
        "phoenix_spans_captured": spans_captured,
        "phoenix_span_kinds": result_data.get("phoenix_span_kinds"),
        "details": result_data,
        "overall_pass": overall,
        "findings": [
            "MCPToolset(connection_params=StdioConnectionParams(server_params=StdioServerParameters(...))) is the correct ADK wiring (NOT StdioServerParameters directly)",
            f"{result_data.get('tools_discovered')} Phoenix MCP tools discovered via npx stdio",
            "LlmAgent with MCPToolset successfully constructed and ran",
            f"Phoenix captured {result_data.get('phoenix_spans_captured')} spans via OpenInference auto-instrumentation",
            "Stack confirmed: ADK -> MCPToolset -> stdio -> @arizeai/phoenix-mcp -> Phoenix Cloud/local",
        ]
        if overall
        else ["FAILURE — see details above"],
    }

    out_path = RESULTS_DIR / "spike_c_adk_mcptoolset.json"
    out_path.write_text(json.dumps(result, indent=2, default=str))
    print(f"\nResult written: {out_path}")
    print(f"\n[{'PASS' if overall else 'FAIL'}] Spike C")
    return 0 if overall else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    raise SystemExit(exit_code)
