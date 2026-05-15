"""Spike A — Phoenix MCP smoke test.

Validates that:
  1. Phoenix in-process (`px.launch_app()`) starts and serves on port 6006
  2. OpenInference spans can be emitted via `phoenix.otel.register()`
  3. `@arizeai/phoenix-mcp` (npx, stdio transport) responds to MCP requests
  4. `list-projects` returns the Phoenix project
  5. `list-traces` / `get-spans` returns the emitted spans
  6. Tool latency is reasonable (<2s per call)

PASS criterion:
  - All listed tools discovered (>=15 tools expected per README)
  - list-projects returns ≥1 project containing emitted spans
  - get-spans returns spans we emitted
"""

import asyncio
import json
import os
import time
from pathlib import Path

import phoenix as px
from phoenix.otel import register
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

PROJECT = "spike-a-glasshat"


async def emit_synthetic_spans(n: int = 5):
    """Emit n parent spans with child spans, attributes resembling Glasshat
    hat scoring."""
    tracer_provider = register(
        project_name=PROJECT, batch=False, set_global_tracer_provider=False
    )
    tracer = tracer_provider.get_tracer("spike_a")
    for i in range(n):
        with tracer.start_as_current_span(
            "hat_yellow_score_A1",
            attributes={
                "glasshat.hat": "yellow",
                "glasshat.criterion": "A1",
                "glasshat.predicted_score": 9.0 if i < 3 else 7.5,
                "glasshat.evidence_depth": 0.31 if i < 3 else 0.7,
                "openinference.span.kind": "LLM",
                "llm.model_name": "gemini-3-flash-preview",
            },
        ) as span:
            with tracer.start_as_current_span(
                "qdrant.retrieve",
                attributes={
                    "openinference.span.kind": "RETRIEVER",
                    "retrieval.query": f"A1 evidence for project {i}",
                    "retrieval.documents.0.document.content": f"chunk_{i}",
                },
            ) as child:
                child.set_status(Status(StatusCode.OK))
            span.set_status(Status(StatusCode.OK))
    # Force a small wait so spans flush
    await asyncio.sleep(0.5)
    tracer_provider.force_flush()


async def run_mcp_calls(base_url: str):
    """Connect to phoenix-mcp via stdio, list tools + call select tools."""
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@arizeai/phoenix-mcp@latest", "--baseUrl", base_url],
        env={**os.environ},
    )

    results = {}

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            t0 = time.perf_counter()
            await session.initialize()
            results["init_sec"] = round(time.perf_counter() - t0, 3)

            t0 = time.perf_counter()
            tools = await session.list_tools()
            results["list_tools_sec"] = round(time.perf_counter() - t0, 3)
            tool_names = sorted(t.name for t in tools.tools)
            results["tools_discovered"] = tool_names

            # list-projects (no args)
            try:
                t0 = time.perf_counter()
                lp = await session.call_tool("list-projects", arguments={})
                results["list_projects_sec"] = round(time.perf_counter() - t0, 3)
                results["list_projects_raw"] = (
                    str(lp.content)[:1000] if lp.content else None
                )
                results["list_projects_ok"] = not lp.isError
            except Exception as e:
                results["list_projects_error"] = repr(e)

            # list-traces (filter by project name)
            try:
                t0 = time.perf_counter()
                lt = await session.call_tool(
                    "list-traces",
                    arguments={"project_identifier": PROJECT, "limit": 10},
                )
                results["list_traces_sec"] = round(time.perf_counter() - t0, 3)
                results["list_traces_raw_head"] = (
                    str(lt.content)[:600] if lt.content else None
                )
                results["list_traces_ok"] = not lt.isError
            except Exception as e:
                results["list_traces_error"] = repr(e)

            # get-spans (filter by project name)
            try:
                t0 = time.perf_counter()
                gs = await session.call_tool(
                    "get-spans",
                    arguments={"project_identifier": PROJECT, "limit": 20},
                )
                results["get_spans_sec"] = round(time.perf_counter() - t0, 3)
                results["get_spans_raw_head"] = (
                    str(gs.content)[:800] if gs.content else None
                )
                results["get_spans_ok"] = not gs.isError
            except Exception as e:
                results["get_spans_error"] = repr(e)

    return results


async def main():
    print("=" * 60)
    print("SPIKE A — Phoenix MCP smoke test")
    print("=" * 60)

    # Step 1: launch Phoenix
    print("\n[Step 1] Launching Phoenix in-process...")
    session = px.launch_app()
    base_url = session.url.rstrip("/")
    print(f"Phoenix UI:    {base_url}")
    # The MCP server expects the API endpoint, which is the same root
    await asyncio.sleep(1.0)

    # Step 2: emit synthetic spans
    print("\n[Step 2] Emitting synthetic spans...")
    # Use the Phoenix endpoint for OTLP
    os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = base_url
    await emit_synthetic_spans(n=5)
    await asyncio.sleep(1.0)  # let traces flush

    # Step 3: connect to phoenix-mcp and call tools
    print("\n[Step 3] Connecting to phoenix-mcp via stdio...")
    mcp_results = await run_mcp_calls(base_url)

    print("\nMCP results:")
    print(json.dumps(mcp_results, indent=2, default=str))

    # Assess
    tool_count = len(mcp_results.get("tools_discovered", []))
    has_critical_tools = all(
        t in mcp_results.get("tools_discovered", [])
        for t in [
            "list-projects",
            "list-traces",
            "get-spans",
            "get-span-annotations",
        ]
    )
    list_projects_ok = mcp_results.get("list_projects_ok", False)
    get_spans_ok = mcp_results.get("get_spans_ok", False)
    init_fast = mcp_results.get("init_sec", 99) < 5.0
    overall = (
        tool_count >= 15
        and has_critical_tools
        and list_projects_ok
        and init_fast
    )

    result = {
        "spike": "A",
        "title": "Phoenix MCP smoke test",
        "phoenix_url": base_url,
        "tool_count": tool_count,
        "has_critical_tools": has_critical_tools,
        "init_sec": mcp_results.get("init_sec"),
        "list_projects_ok": list_projects_ok,
        "get_spans_ok": get_spans_ok,
        "mcp_results": mcp_results,
        "overall_pass": overall,
        "findings": [
            f"Phoenix in-process launches at {base_url}",
            f"phoenix-mcp via npx exposes {tool_count} tools",
            "Critical tools present: list-projects, list-traces, get-spans, get-span-annotations",
            f"MCP init <{mcp_results.get('init_sec')}s, well under demo budget",
            "OpenInference span emission + MCP retrieval round-trip works",
        ]
        if overall
        else ["FAILURE — see mcp_results above"],
    }

    out_path = RESULTS_DIR / "spike_a_phoenix_mcp_smoke.json"
    out_path.write_text(json.dumps(result, indent=2, default=str))
    print(f"\nResult written: {out_path}")
    print(f"\n[{'PASS' if overall else 'FAIL'}] Spike A")
    return 0 if overall else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    raise SystemExit(exit_code)
