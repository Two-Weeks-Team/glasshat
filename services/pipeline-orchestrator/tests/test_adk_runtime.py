import asyncio
import json
import sys
import types
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import pytest
from glasshat.agents.audit import Consultant, DatasetWriter
from glasshat.pipeline.adk_runtime import (
    PhoenixMcpConsultant,
    PhoenixMcpDatasetWriter,
    _mcp_server_params,
    _parse_deltas,
    _parse_examples,
    build_phoenix_mcp_toolset,
    instrument_adk,
    run_via_adk,
)
from glasshat.shared.enums import Hat


def test_runtime_api_is_importable_without_adk() -> None:
    # Module import + symbol presence must NOT require google-adk/phoenix (lazy).
    assert callable(instrument_adk)
    assert callable(run_via_adk)
    assert callable(build_phoenix_mcp_toolset)


def test_phoenix_mcp_consultant_satisfies_consultant_protocol() -> None:
    consultant = PhoenixMcpConsultant(base_url="http://localhost:6006")
    assert isinstance(consultant, Consultant)


def test_phoenix_mcp_dataset_writer_satisfies_writer_protocol() -> None:
    writer = PhoenixMcpDatasetWriter(base_url="http://localhost:6006")
    assert isinstance(writer, DatasetWriter)


@pytest.mark.integration
def test_instrument_adk_smoke() -> None:
    pytest.importorskip("google.adk")
    pytest.importorskip("phoenix")
    instrument_adk("glasshat-test")


# --- Q1: executable-body coverage for the live Phoenix-MCP path ---------------
# The stdio call chain runs against a *fake* `mcp` injected into sys.modules so
# the bodies (parsing, fetch-once caching, tool name/args) are exercised without
# the real (optional) SDK or a live npx subprocess.


class _Item:
    def __init__(self, text: str | None) -> None:
        self.text = text


class _ToolResult:
    def __init__(self, items: list[_Item]) -> None:
        self.content = items


def _result(examples: list[dict[str, Any]]) -> _ToolResult:
    return _ToolResult([_Item(json.dumps({"examples": examples}))])


@contextmanager
def _fake_mcp(
    tool_result: Any, recorder: list[tuple[str, dict[str, Any]]]
) -> Iterator[dict[str, Any]]:
    captured: dict[str, Any] = {}

    class StdioServerParameters:
        def __init__(
            self, command: str, args: list[str], env: dict[str, str] | None = None
        ) -> None:
            self.command, self.args, self.env = command, args, env

    class ClientSession:
        def __init__(self, read: Any, write: Any) -> None:
            pass

        async def __aenter__(self) -> "ClientSession":
            return self

        async def __aexit__(self, *exc: Any) -> bool:
            return False

        async def initialize(self) -> None:
            pass

        async def call_tool(self, name: str, args: dict[str, Any]) -> Any:
            recorder.append((name, args))
            return tool_result

    class _StdioCtx:
        def __init__(self, params: Any) -> None:
            captured["params"] = params

        async def __aenter__(self) -> tuple[Any, Any]:
            return (None, None)

        async def __aexit__(self, *exc: Any) -> bool:
            return False

    mcp_mod = types.ModuleType("mcp")
    mcp_mod.StdioServerParameters = StdioServerParameters  # type: ignore[attr-defined]
    mcp_mod.ClientSession = ClientSession  # type: ignore[attr-defined]
    client_mod = types.ModuleType("mcp.client")
    stdio_mod = types.ModuleType("mcp.client.stdio")
    stdio_mod.stdio_client = lambda params: _StdioCtx(params)  # type: ignore[attr-defined]
    keys = ("mcp", "mcp.client", "mcp.client.stdio")
    saved = {k: sys.modules.get(k) for k in keys}
    sys.modules.update({"mcp": mcp_mod, "mcp.client": client_mod, "mcp.client.stdio": stdio_mod})
    try:
        yield captured
    finally:
        for k in keys:
            if saved[k] is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = saved[k]


def test_parse_examples_reads_writer_shape_and_skips_garbage() -> None:
    result = _ToolResult(
        [
            _Item(None),  # no text → skipped
            _Item("{not json"),  # bad JSON → skipped
            _Item(
                json.dumps(
                    {
                        "examples": [
                            {
                                "input": {"hat": "yellow", "criterion": "t", "bucket": "low"},
                                "output": {"delta": 1.5},
                            },
                            "not-a-dict",  # skipped
                            {
                                "input": {"hat": "yellow", "criterion": "t"},
                                "output": {"delta": 9.0},
                            },  # missing bucket → skipped
                            {
                                "hat": "green",
                                "criterion": "q",
                                "bucket": "high",
                                "delta": -2.0,
                            },  # flat fallback
                        ]
                    }
                )
            ),
        ]
    )
    pairs = _parse_examples(result)
    assert (("yellow", "t", "low"), 1.5) in pairs
    assert (("green", "q", "high"), -2.0) in pairs
    assert len(pairs) == 2  # the missing-bucket + non-dict rows were dropped
    assert sorted(_parse_deltas(result)) == [-2.0, 1.5]


def test_mcp_server_params_pins_version_and_passes_key_via_env() -> None:
    with _fake_mcp(_result([]), []):
        params = _mcp_server_params("http://phoenix:6006", "ak-secret")
        assert "@arizeai/phoenix-mcp@4.0.13" in params.args
        assert "--apiKey" not in params.args  # never in argv (no /proc cmdline leak)
        assert params.env is not None and params.env["PHOENIX_API_KEY"] == "ak-secret"
        # No key → inherit env (None), still pinned package.
        params2 = _mcp_server_params("http://phoenix:6006", "")
        assert params2.env is None
        assert "@arizeai/phoenix-mcp@4.0.13" in params2.args


def test_consultant_fetches_dataset_once_and_filters_locally() -> None:
    examples = [
        {"input": {"hat": "yellow", "criterion": "tech", "bucket": "low"}, "output": {"delta": d}}
        for d in (1.0, 1.5, 2.0)
    ] + [
        {
            "input": {"hat": "yellow", "criterion": "tech", "bucket": "high"},
            "output": {"delta": 0.3},
        },
    ]
    recorder: list[tuple[str, dict[str, Any]]] = []
    consultant = PhoenixMcpConsultant(
        base_url="http://phoenix:6006", dataset="glasshat-calibration"
    )
    with _fake_mcp(_result(examples), recorder):
        hit = asyncio.run(consultant.consult(Hat.YELLOW, "tech", "low"))
        miss = asyncio.run(consultant.consult(Hat.YELLOW, "tech", "high"))  # only 1 sample (<3)
        again = asyncio.run(consultant.consult(Hat.YELLOW, "tech", "low"))
    assert hit is not None and hit.n == 3 and abs(hit.mean_delta - 1.5) < 1e-9
    assert miss is None  # fewer than 3 samples → no correction
    assert again is not None and again.n == 3
    # Fetched ONCE despite three consults (the cache), and asked the right tool.
    fetches = [c for c in recorder if c[0] == "get-dataset-examples"]
    assert len(fetches) == 1
    assert fetches[0][1] == {"dataset": "glasshat-calibration"}


def test_writer_calls_add_dataset_examples_with_rows() -> None:
    from glasshat.agents.audit import DatasetExample

    recorder: list[tuple[str, dict[str, Any]]] = []
    writer = PhoenixMcpDatasetWriter(base_url="http://phoenix:6006", dataset="glasshat-calibration")
    ex = DatasetExample(
        hat=Hat.YELLOW, criterion_id="tech", bucket="low", delta=1.2, run_id="r1", created_at="t0"
    )
    with _fake_mcp(_result([]), recorder):
        n = asyncio.run(writer.write([ex]))
        empty = asyncio.run(writer.write([]))  # short-circuit, no MCP call
    assert n == 1 and empty == 0
    writes = [c for c in recorder if c[0] == "add-dataset-examples"]
    assert len(writes) == 1
    payload = writes[0][1]
    assert payload["dataset"] == "glasshat-calibration"
    row = payload["examples"][0]
    assert row["input"] == {"hat": "yellow", "criterion": "tech", "bucket": "low"}
    assert row["output"] == {"delta": 1.2}
    assert row["metadata"] == {"run_id": "r1", "created_at": "t0"}
