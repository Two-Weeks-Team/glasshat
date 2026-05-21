"""Live ADK runtime adapter (Arize Stage-1 gate).

Wires the real orchestrator: OpenInference auto-instrumentation + the ADK
instrumentor send traces to Phoenix; the audit step consults Phoenix over an
MCP **stdio** session (``npx @arizeai/phoenix-mcp``, the spike-C wiring). Every
symbol is importable without ``google-adk``/``phoenix`` installed — the heavy
SDKs are imported lazily inside the functions, so this module is CI-safe while
the actual calls are exercised by ``@integration`` tests / live deployment.
"""

from __future__ import annotations

import statistics
from typing import Any

from glasshat.agents.audit import ConsultResult
from glasshat.agents.types import EvaluationInput, RunRecord
from glasshat.shared.config import Settings, get_settings
from glasshat.shared.enums import Hat


def instrument_adk(project_name: str = "glasshat") -> None:  # pragma: no cover - requires SDKs
    """Register OpenInference + the Google ADK instrumentor against Phoenix."""
    from openinference.instrumentation.google_adk import GoogleADKInstrumentor
    from phoenix.otel import register

    tracer_provider = register(project_name=project_name, auto_instrument=True)
    GoogleADKInstrumentor().instrument(tracer_provider=tracer_provider)


def build_phoenix_mcp_toolset(base_url: str, api_key: str = "") -> Any:  # pragma: no cover
    """Build the ADK Phoenix MCP toolset over stdio (spike-C validated pattern)."""
    from google.adk.tools.mcp_tool import MCPToolset, StdioConnectionParams
    from mcp import StdioServerParameters

    args = ["-y", "@arizeai/phoenix-mcp@latest", "--baseUrl", base_url]
    if api_key:
        args += ["--apiKey", api_key]
    return MCPToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(command="npx", args=args),
            timeout=30.0,
        )
    )


def _percentile(values: list[float], pct: float) -> float:
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, round(pct * (len(ordered) - 1))))
    return ordered[idx]


class PhoenixMcpConsultant:
    """Consultant that derives calibration stats from Phoenix over MCP stdio.

    Implements :class:`~glasshat.agents.audit.Consultant`: for a (hat, criterion,
    bucket) cell it calls the Phoenix MCP ``get-dataset-examples`` tool, parses the
    per-anchor score deltas, and returns mean/percentiles. The MCP round-trip over
    stdio is the auditable self-improvement call chain.
    """

    def __init__(
        self, base_url: str, api_key: str = "", dataset: str = "glasshat-calibration"
    ) -> None:
        self._base_url = base_url
        self._api_key = api_key
        self._dataset = dataset

    async def consult(  # pragma: no cover - requires phoenix-mcp over stdio
        self, hat: Hat, criterion_id: str, bucket: str
    ) -> ConsultResult | None:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        args = ["-y", "@arizeai/phoenix-mcp@latest", "--baseUrl", self._base_url]
        if self._api_key:
            args += ["--apiKey", self._api_key]
        params = StdioServerParameters(command="npx", args=args)
        async with stdio_client(params) as (read, write), ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "get-dataset-examples",
                {
                    "dataset": self._dataset,
                    "filter": f"hat={hat.value} AND criterion={criterion_id} AND bucket={bucket}",
                },
            )
        deltas = _parse_deltas(result)
        if len(deltas) < 3:
            return None
        return ConsultResult(
            mean_delta=statistics.mean(deltas),
            n=len(deltas),
            p25=_percentile(deltas, 0.25),
            p75=_percentile(deltas, 0.75),
        )


def _parse_deltas(mcp_result: Any) -> list[float]:  # pragma: no cover - shape depends on phoenix
    deltas: list[float] = []
    for item in getattr(mcp_result, "content", []) or []:
        text = getattr(item, "text", None)
        if text is None:
            continue
        import json

        try:
            payload = json.loads(text)
        except (ValueError, TypeError):
            continue
        for example in payload if isinstance(payload, list) else payload.get("examples", []):
            delta = example.get("delta") if isinstance(example, dict) else None
            if isinstance(delta, int | float):
                deltas.append(float(delta))
    return deltas


async def run_via_adk(  # pragma: no cover - requires the full live stack
    inp: EvaluationInput, settings: Settings | None = None
) -> RunRecord:
    """Run an evaluation through the instrumented ADK runtime + live Phoenix MCP."""
    from glasshat.pipeline.engine import Deps, run_evaluation
    from glasshat.shared.blobstore import get_blobstore
    from glasshat.shared.docstore import get_docstore
    from glasshat.shared.llm import get_llm_client
    from glasshat.shared.retrieval import HybridIndex
    from glasshat.shared.tracing import PhoenixTracer

    settings = settings or get_settings()
    instrument_adk(settings.phoenix_project_name)
    deps = Deps(
        llm=get_llm_client(settings),
        retrieval=HybridIndex(),
        docstore=get_docstore(settings),
        blobstore=get_blobstore(settings),
        tracer=PhoenixTracer(settings),
        consultant=PhoenixMcpConsultant(
            base_url=settings.phoenix_collector_endpoint, api_key=settings.phoenix_api_key
        ),
    )
    return await run_evaluation(inp, deps)
