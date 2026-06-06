"""Live ADK runtime adapter (Arize Stage-1 gate).

Wires the real orchestrator: OpenInference auto-instrumentation + the ADK
instrumentor send traces to Phoenix; the audit step consults Phoenix over an
MCP **stdio** session (``npx @arizeai/phoenix-mcp``, the spike-C wiring) and
writes each correction back via the same MCP session (``add-dataset-examples``,
spike-G), closing the "agent improves over time" loop the Arize track gives
explicit bonus consideration to. Every symbol is importable without
``google-adk``/``phoenix`` installed — the heavy SDKs are imported lazily inside
the functions, so this module is CI-safe while the actual calls are exercised
by ``@integration`` tests / live deployment.
"""

from __future__ import annotations

import asyncio
import statistics
from typing import Any

from glasshat.agents.audit import ConsultResult, DatasetExample
from glasshat.agents.types import EvaluationInput, RunRecord
from glasshat.shared.config import Settings, get_settings
from glasshat.shared.enums import Hat

# Pin the MCP server (never `@latest`) so a runtime `npx` fetch can't pull an
# unreviewed release into the deployed image — supply-chain hardening.
_PHOENIX_MCP_PACKAGE = "@arizeai/phoenix-mcp@4.0.13"
# A hung `npx`/stdio session must not hang the whole evaluation; cap every MCP
# round-trip. FallbackConsultant catches exceptions (incl. TimeoutError).
_MCP_CALL_TIMEOUT = 30.0


def _mcp_server_params(base_url: str, api_key: str) -> Any:
    """Stdio params for ``npx @arizeai/phoenix-mcp`` — pinned, key via env not argv.

    The API key is passed through the subprocess environment (``PHOENIX_API_KEY``,
    which phoenix-mcp reads), never as ``--apiKey <secret>`` in argv: argv is
    world-readable via ``/proc/<pid>/cmdline``, so an argv secret leaks to any
    local process. ``os.environ`` is inherited so ``npx`` keeps its ``PATH``.
    """
    import os

    from mcp import StdioServerParameters

    env = {**os.environ, "PHOENIX_API_KEY": api_key} if api_key else None
    return StdioServerParameters(
        command="npx",
        args=["-y", _PHOENIX_MCP_PACKAGE, "--baseUrl", base_url],
        env=env,
    )


def instrument_adk(project_name: str = "glasshat") -> None:  # pragma: no cover - requires SDKs
    """Register OpenInference + the Google ADK instrumentor against Phoenix.

    Legacy helper (registers its own Phoenix provider). The genuine Tier B path
    instead reuses the one provider the configured tracer already registered — see
    :func:`maybe_instrument_adk` — so the agent span tree and the ``glasshat.*``
    manual spans land on a single provider (no split / dropped traces)."""
    from openinference.instrumentation.google_adk import GoogleADKInstrumentor
    from phoenix.otel import register

    tracer_provider = register(project_name=project_name, auto_instrument=True)
    GoogleADKInstrumentor().instrument(tracer_provider=tracer_provider)


# Process-wide guard: the Google ADK instrumentor must attach to the tracer
# provider exactly once (a second instrument() would double-count / drop spans).
_ADK_INSTRUMENTED = {"done": False}


def instrument_adk_on_provider(tracer_provider: Any) -> None:  # pragma: no cover - requires SDKs
    """Attach the Google ADK instrumentor to an ALREADY-registered tracer provider.

    Idempotent: a second call is a no-op, so across the process the provider is
    registered once (by the tracer) and instrumented once (here)."""
    if _ADK_INSTRUMENTED["done"]:
        return
    from openinference.instrumentation.google_adk import GoogleADKInstrumentor

    GoogleADKInstrumentor().instrument(tracer_provider=tracer_provider)
    _ADK_INSTRUMENTED["done"] = True


def maybe_instrument_adk(tracer: Any) -> bool:
    """Wire the ADK instrumentor onto the configured tracer's single provider.

    Real ``ArizeTracer`` / ``PhoenixTracer`` expose ``tracer_provider`` (registered
    once in their ``__init__``); the ADK agent spans attach to it so the nested
    tree shows up in the SAME Arize/Phoenix project as the manual spans. A
    ``NoOpTracer`` (tests / CI / no SDK) has no provider, so this is a safe no-op —
    the parity path never needs the instrumentor, only the live trace tree does.

    Returns ``True`` when instrumentation was wired."""
    provider = getattr(tracer, "tracer_provider", None)
    if provider is None:
        return False
    instrument_adk_on_provider(provider)
    return True


def build_phoenix_mcp_toolset(base_url: str, api_key: str = "") -> Any:  # pragma: no cover
    """Build the ADK Phoenix MCP toolset over stdio (spike-C validated pattern)."""
    from google.adk.tools.mcp_tool import MCPToolset, StdioConnectionParams

    return MCPToolset(
        connection_params=StdioConnectionParams(
            server_params=_mcp_server_params(base_url, api_key),
            timeout=_MCP_CALL_TIMEOUT,
        )
    )


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
        # Fetch the whole calibration dataset ONCE per run and filter locally.
        # Spawning npx per (hat, criterion, bucket) cell would cost ~1.8s × N cells
        # (24+ on a full run), blowing past _MCP_CALL_TIMEOUT. ``None`` until the
        # first consult loads + groups it; reused for every subsequent cell.
        self._grouped: dict[tuple[str, str, str], list[float]] | None = None

    async def _load(self) -> dict[tuple[str, str, str], list[float]]:
        if self._grouped is not None:
            return self._grouped
        from mcp import ClientSession
        from mcp.client.stdio import stdio_client

        params = _mcp_server_params(self._base_url, self._api_key)

        async def _call() -> Any:
            async with stdio_client(params) as (read, write), ClientSession(read, write) as session:
                await session.initialize()
                return await session.call_tool(
                    "get-dataset-examples", {"dataset_name": self._dataset}
                )

        # Bound the single round-trip: a hung npx/stdio session must not hang the run.
        result = await asyncio.wait_for(_call(), timeout=_MCP_CALL_TIMEOUT)
        grouped: dict[tuple[str, str, str], list[float]] = {}
        for key, delta in _parse_examples(result):
            grouped.setdefault(key, []).append(delta)
        self._grouped = grouped
        return grouped

    async def consult(self, hat: Hat, criterion_id: str, bucket: str) -> ConsultResult | None:
        grouped = await self._load()
        deltas = grouped.get((hat.value, criterion_id, bucket), [])
        if len(deltas) < 3:
            return None
        return ConsultResult(
            mean_delta=statistics.mean(deltas),
            n=len(deltas),
            # p25/p75 are the SCORE clip bounds for apply_correction
            # (clip(raw_score, p25, p75)) — NOT delta percentiles. Match the
            # table/anchor convention (ConsultResult(mean_delta, n, 0.0, 10.0)) so
            # the live MCP correction equals the deterministic prior instead of
            # being crushed onto the ±2 cap.
            p25=0.0,
            p75=10.0,
        )


def _parse_examples(
    mcp_result: Any,
) -> list[tuple[tuple[str, str, str], float]]:
    """Yield ``((hat, criterion, bucket), delta)`` for each example in an MCP result.

    Reads the shape the writer emits — ``input.{hat,criterion,bucket}`` +
    ``output.delta`` — tolerating a flat ``{hat,criterion,bucket,delta}`` fallback.
    phoenix-mcp's ``get-dataset-examples`` wraps the rows as
    ``{"data": {"examples": [...]}}``, so unwrap ``data`` before reading ``examples``.
    """
    import json

    out: list[tuple[tuple[str, str, str], float]] = []
    for item in getattr(mcp_result, "content", []) or []:
        text = getattr(item, "text", None)
        if text is None:
            continue
        try:
            payload = json.loads(text)
        except (ValueError, TypeError):
            continue
        if isinstance(payload, dict) and isinstance(payload.get("data"), dict):
            payload = payload["data"]  # phoenix-mcp wraps rows under "data"
        examples = payload if isinstance(payload, list) else payload.get("examples", [])
        for ex in examples:
            if not isinstance(ex, dict):
                continue
            inp = ex.get("input", ex)
            outp = ex.get("output", ex)
            hat, crit, bucket = inp.get("hat"), inp.get("criterion"), inp.get("bucket")
            delta = outp.get("delta") if isinstance(outp, dict) else None
            if isinstance(delta, int | float) and hat and crit and bucket:
                out.append(((str(hat), str(crit), str(bucket)), float(delta)))
    return out


def _parse_deltas(mcp_result: Any) -> list[float]:
    """Flat list of deltas (ungrouped) — retained for callers that only need values."""
    return [delta for _, delta in _parse_examples(mcp_result)]


class PhoenixMcpDatasetWriter:
    """Append audit corrections to a Phoenix Dataset via MCP ``add-dataset-examples``.

    Implements :class:`~glasshat.agents.audit.DatasetWriter`. Each call opens a
    fresh stdio session — the live deployment runs at a small scale where the
    npx spin-up cost (~1.8s per spike-A) is acceptable as a fire-and-forget
    write after the run completes. Failures are silently swallowed by the
    engine's wrapper so a Phoenix outage cannot fail an evaluation.
    """

    def __init__(
        self, base_url: str, api_key: str = "", dataset: str = "glasshat-calibration"
    ) -> None:
        self._base_url = base_url
        self._api_key = api_key
        self._dataset = dataset

    async def write(self, examples: list[DatasetExample]) -> int:
        if not examples:
            return 0
        from mcp import ClientSession
        from mcp.client.stdio import stdio_client

        params = _mcp_server_params(self._base_url, self._api_key)
        rows = [
            {
                "input": {
                    "hat": ex.hat.value,
                    "criterion": ex.criterion_id,
                    "bucket": ex.bucket,
                },
                "output": {"delta": ex.delta},
                "metadata": {"run_id": ex.run_id, "created_at": ex.created_at},
            }
            for ex in examples
        ]

        async def _call() -> None:
            async with stdio_client(params) as (read, write), ClientSession(read, write) as session:
                await session.initialize()
                await session.call_tool(
                    "add-dataset-examples",
                    {"dataset_name": self._dataset, "examples": rows},
                )

        # Bound the round-trip: a hung npx/stdio session must not hang the run.
        await asyncio.wait_for(_call(), timeout=_MCP_CALL_TIMEOUT)
        return len(rows)


async def run_via_adk(  # pragma: no cover - requires the full live stack
    inp: EvaluationInput, settings: Settings | None = None
) -> RunRecord:
    """Run an evaluation through the instrumented ADK runtime + live Phoenix MCP.

    Wires both halves of the learning loop: ``PhoenixMcpConsultant`` reads the
    accumulated calibration dataset (with a deterministic ``TableConsultant``
    fallback for cold start), and ``PhoenixMcpDatasetWriter`` appends this
    run's audit corrections back to that dataset.
    """
    from glasshat.agents.audit import FallbackConsultant
    from glasshat.pipeline.engine import Deps, default_calibration_table, run_evaluation
    from glasshat.shared.blobstore import get_blobstore
    from glasshat.shared.docstore import get_docstore
    from glasshat.shared.llm import get_llm_client
    from glasshat.shared.retrieval import HybridIndex
    from glasshat.shared.tracing import PhoenixTracer

    settings = settings or get_settings()
    from glasshat.agents.audit import TableConsultant

    # Register the Phoenix provider ONCE (in the tracer) and attach the ADK
    # instrumentor to THAT provider — no separate instrument_adk() register, so the
    # agent span tree and the manual glasshat.* spans share a single provider.
    tracer = PhoenixTracer(settings)
    maybe_instrument_adk(tracer)

    live_consultant = PhoenixMcpConsultant(
        base_url=settings.phoenix_collector_endpoint,
        api_key=settings.phoenix_api_key,
        dataset=settings.phoenix_calibration_dataset,
    )
    cold_start = TableConsultant(default_calibration_table())
    deps = Deps(
        llm=get_llm_client(settings),
        retrieval=HybridIndex(),
        docstore=get_docstore(settings),
        blobstore=get_blobstore(settings),
        tracer=tracer,
        consultant=FallbackConsultant(primary=live_consultant, backup=cold_start),
        dataset_writer=PhoenixMcpDatasetWriter(
            base_url=settings.phoenix_collector_endpoint,
            api_key=settings.phoenix_api_key,
            dataset=settings.phoenix_calibration_dataset,
        ),
        agent_runtime="adk",  # genuinely run the ADK graph (matches the function name)
    )
    return await run_evaluation(inp, deps)
