import asyncio
import os

import numpy as np
import pytest
from glasshat.shared.config import Settings
from glasshat.shared.llm import MockLlmClient, VertexLlmClient, get_llm_client
from glasshat.shared.protocols import LlmClient


def test_mock_is_llmclient() -> None:
    assert isinstance(MockLlmClient(), LlmClient)


def test_mock_generate_is_deterministic_and_nonempty() -> None:
    c = MockLlmClient()
    a = asyncio.run(c.generate("prompt x"))
    b = asyncio.run(c.generate("prompt x"))
    d = asyncio.run(c.generate("prompt y"))
    assert a == b
    assert a != d
    assert a


def test_mock_generate_varies_by_tier() -> None:
    c = MockLlmClient()
    assert asyncio.run(c.generate("p", tier="pro")) != asyncio.run(c.generate("p", tier="flash"))


def test_mock_embed_deterministic_with_dim() -> None:
    c = MockLlmClient(embedding_dim=16)
    v1 = asyncio.run(c.embed(["hello"]))
    v2 = asyncio.run(c.embed(["hello"]))
    assert len(v1) == 1 and len(v1[0]) == 16
    assert v1 == v2


def test_mock_embed_unit_norm_and_distinct() -> None:
    c = MockLlmClient(embedding_dim=32)
    [vh, vw] = asyncio.run(c.embed(["hello", "world"]))
    assert abs(float(np.linalg.norm(vh)) - 1.0) < 1e-6
    assert vh != vw


def test_get_llm_client_returns_mock_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LLM_BACKEND", raising=False)
    c = get_llm_client(Settings(_env_file=None))  # type: ignore[call-arg]
    assert isinstance(c, MockLlmClient)


def test_get_llm_client_returns_vertex_when_configured() -> None:
    s = Settings(_env_file=None, llm_backend="vertex")  # type: ignore[call-arg]
    assert isinstance(get_llm_client(s), VertexLlmClient)  # lazy: no creds needed to construct


@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("GOOGLE_CLOUD_PROJECT"), reason="no GCP project configured")
def test_vertex_generate_smoke() -> None:
    out = asyncio.run(VertexLlmClient(Settings()).generate("Reply with OK", tier="flash_lite"))
    assert out
