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
    """Real Vertex Gemini client (generation + embeddings). Lazy-imports google.genai."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._client: Any = None

    def _models(self) -> dict[str, str]:
        return {
            "pro": self._settings.gemini_pro,
            "flash": self._settings.gemini_flash,
            "flash_lite": self._settings.gemini_flash_lite,
        }

    def _get_client(self) -> Any:  # pragma: no cover - requires GCP credentials
        if self._client is None:
            from google import genai

            self._client = genai.Client(
                vertexai=True,
                project=self._settings.google_cloud_project,
                location=self._settings.google_cloud_region,
            )
        return self._client

    async def generate(  # pragma: no cover - requires GCP credentials
        self, prompt: str, *, tier: str = _TIER_DEFAULT, **kwargs: Any
    ) -> str:
        model = self._models().get(tier, self._settings.gemini_flash)
        resp = await self._get_client().aio.models.generate_content(model=model, contents=prompt)
        return str(resp.text or "")

    async def embed(  # pragma: no cover - requires GCP credentials
        self, texts: Sequence[str]
    ) -> list[list[float]]:
        resp = await self._get_client().aio.models.embed_content(
            model="text-embedding-005", contents=list(texts)
        )
        return [list(e.values) for e in resp.embeddings]


def get_llm_client(settings: Settings | None = None) -> LlmClient:
    """Return the configured LLM client (``mock`` default, ``vertex`` when set)."""
    settings = settings or get_settings()
    if settings.llm_backend == "vertex":
        return VertexLlmClient(settings)
    return MockLlmClient()
