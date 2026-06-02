import pytest
from glasshat.agents.audit import Consultant, DatasetWriter
from glasshat.pipeline.adk_runtime import (
    PhoenixMcpConsultant,
    PhoenixMcpDatasetWriter,
    build_phoenix_mcp_toolset,
    instrument_adk,
    run_via_adk,
)


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
