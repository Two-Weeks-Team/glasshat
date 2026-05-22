"""LLM adapter: deterministic ``mock`` backend + real Vertex Gemini backend.

The ``mock`` backend is a complete, deterministic implementation (hash-seeded) —
not a stub — used for tests/CI with no credentials. The Vertex backend lazily
imports ``google.genai`` so importing this module never requires the SDK.
Selection is by ``Settings.llm_backend``. AI policy: Gemini/Google only.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np
from glasshat.shared.config import Settings, get_settings
from glasshat.shared.ids import sha256_hex
from glasshat.shared.protocols import LlmClient

_TIER_DEFAULT = "flash"


class MockLlmClient:
    """Deterministic, credential-free LLM client for tests/CI (architecture §5)."""

    def __init__(self, embedding_dim: int = 768) -> None:
        self._dim = embedding_dim

    async def generate(self, prompt: str, *, tier: str = _TIER_DEFAULT, **kwargs: Any) -> str:
        return f"[mock:{tier}] {sha256_hex(f'{tier}:{prompt}')[:32]}"

    async def embed(self, texts: Sequence[str]) -> list[list[float]]:
        out: list[list[float]] = []
        for text in texts:
            seed = int(sha256_hex(text)[:8], 16)
            vec = np.random.default_rng(seed).standard_normal(self._dim)
            norm = float(np.linalg.norm(vec))
            out.append((vec / norm).tolist())
        return out


class VertexLlmClient:
    """Real Vertex Gemini client (generation + embeddings). Lazy-imports google.genai.

    Location-aware: Gemini 3.x models are served on the Vertex **global** endpoint
    (a regional endpoint returns 404), while the embedding model
    ``text-embedding-005`` is regional. Each tier carries its own location
    (``Settings.gemini_*_location``, default ``global``); a ``google.genai.Client``
    is built and cached **per location** so generation hits ``global`` and
    embeddings stay on ``google_cloud_region``.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._clients: dict[str, Any] = {}

    def _models(self) -> dict[str, str]:
        return {
            "pro": self._settings.gemini_pro,
            "flash": self._settings.gemini_flash,
            "flash_lite": self._settings.gemini_flash_lite,
        }

    def _locations(self) -> dict[str, str]:
        return {
            "pro": self._settings.gemini_pro_location,
            "flash": self._settings.gemini_flash_location,
            "flash_lite": self._settings.gemini_flash_lite_location,
        }

    def _client_for(self, location: str) -> Any:
        client = self._clients.get(location)
        if client is None:  # pragma: no cover - requires google-genai + GCP credentials
            from google import genai

            client = genai.Client(
                vertexai=True,
                project=self._settings.google_cloud_project,
                location=location,
            )
            self._clients[location] = client
        return client

    async def generate(self, prompt: str, *, tier: str = _TIER_DEFAULT, **kwargs: Any) -> str:
        model = self._models().get(tier, self._settings.gemini_flash)
        location = self._locations().get(tier, self._settings.gemini_flash_location)
        resp = await self._client_for(location).aio.models.generate_content(
            model=model, contents=prompt
        )
        return str(resp.text or "")

    async def embed(self, texts: Sequence[str]) -> list[list[float]]:
        # text-embedding-005 is a regional model → use the configured region, not global.
        client = self._client_for(self._settings.google_cloud_region)
        resp = await client.aio.models.embed_content(
            model="text-embedding-005", contents=list(texts)
        )
        return [list(e.values) for e in resp.embeddings]


def get_llm_client(settings: Settings | None = None) -> LlmClient:
    """Return the configured LLM client (``mock`` default, ``vertex`` when set)."""
    settings = settings or get_settings()
    if settings.llm_backend == "vertex":
        return VertexLlmClient(settings)
    return MockLlmClient()
