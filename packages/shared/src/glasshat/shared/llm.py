"""LLM adapter: deterministic ``mock`` backend + real Vertex Gemini backend.

The ``mock`` backend is a complete, deterministic implementation (hash-seeded) —
not a stub — used for tests/CI with no credentials. The Vertex backend lazily
imports ``google.genai`` so importing this module never requires the SDK.
Selection is by ``Settings.llm_backend``. AI policy: Gemini/Google only.
"""

from __future__ import annotations

import asyncio
import json
import random
from collections.abc import Awaitable, Callable, Sequence
from typing import Any

import numpy as np
from glasshat.shared.config import Settings, get_settings
from glasshat.shared.ids import sha256_hex
from glasshat.shared.protocols import LlmClient

_TIER_DEFAULT = "flash"

# Vertex resilience: bound each call and retry transient failures (rate limits /
# 5xx / timeouts) with exponential backoff + jitter. Non-transient errors (4xx
# auth/validation) are not retried.
_RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})
_MAX_RETRIES = 3
_BASE_DELAY_S = 0.5
_CALL_TIMEOUT_S = 60.0


def _retryable_status(exc: BaseException) -> bool:
    """A transient HTTP-ish failure worth retrying (rate limit / 5xx)."""
    for attr in ("code", "status_code", "status"):
        value = getattr(exc, attr, None)
        if isinstance(value, int) and value in _RETRYABLE_STATUS:
            return True
    return False


def _is_retryable(exc: BaseException) -> bool:
    return isinstance(exc, asyncio.TimeoutError | TimeoutError) or _retryable_status(exc)


async def _with_retry[T](op: Callable[[], Awaitable[T]], *, timeout: float = _CALL_TIMEOUT_S) -> T:
    """Run ``op`` with a per-attempt timeout and bounded retry on transient errors."""
    for attempt in range(_MAX_RETRIES + 1):
        try:
            return await asyncio.wait_for(op(), timeout=timeout)
        except Exception as exc:  # noqa: BLE001 — classify, then re-raise or retry
            if attempt >= _MAX_RETRIES or not _is_retryable(exc):
                raise
            delay = _BASE_DELAY_S * (2**attempt) + random.uniform(0.0, _BASE_DELAY_S)
            await asyncio.sleep(delay)
    raise AssertionError("unreachable")  # pragma: no cover


class MockLlmClient:
    """Deterministic, credential-free LLM client for tests/CI (architecture §5)."""

    def __init__(self, embedding_dim: int = 768) -> None:
        self._dim = embedding_dim

    async def generate(
        self,
        prompt: str,
        *,
        tier: str = _TIER_DEFAULT,
        response_schema: Any = None,
        system_instruction: str | None = None,
        **kwargs: Any,
    ) -> str:
        if response_schema is not None:
            # Structured mode: emit schema-valid JSON deterministically. The score
            # is derived from the (system_instruction + prompt) hash — NOT from any
            # `SCORE:` text inside the prompt — so a planted `SCORE: 10` in an
            # untrusted deck cannot steer the mock's output (parity with the real
            # Vertex path, where the system instruction quarantines the submission).
            basis = f"{tier}:{system_instruction or ''}:{prompt}"
            seed = int(sha256_hex(basis)[:6], 16)
            score = round((seed % 1001) / 100.0, 2)
            return json.dumps(
                {"score": score, "rationale": f"[mock:{tier}] {sha256_hex(basis)[:24]}"}
            )
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

    async def generate(
        self,
        prompt: str,
        *,
        tier: str = _TIER_DEFAULT,
        response_schema: Any = None,
        system_instruction: str | None = None,
        **kwargs: Any,
    ) -> str:
        model = self._models().get(tier, self._settings.gemini_flash)
        location = self._locations().get(tier, self._settings.gemini_flash_location)

        async def _op() -> str:
            call_kwargs: dict[str, Any] = {"model": model, "contents": prompt}
            if response_schema is not None or system_instruction is not None:
                # Lazy import keeps google.genai out of the import path for the
                # mock/CI runtime. ``structured`` scoring asks Gemini for typed
                # JSON under a system instruction that quarantines the submission.
                # Only attach a config when one is needed, so the legacy call stays
                # byte-identical.
                from google.genai import types as genai_types

                call_kwargs["config"] = genai_types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type=(
                        "application/json" if response_schema is not None else None
                    ),
                    response_schema=response_schema,
                )
            resp = await self._client_for(location).aio.models.generate_content(**call_kwargs)
            return str(resp.text or "")

        return await _with_retry(_op)

    async def embed(self, texts: Sequence[str]) -> list[list[float]]:
        # text-embedding-005 is a regional model → use the configured region, not global.
        client = self._client_for(self._settings.google_cloud_region)

        async def _op() -> list[list[float]]:
            resp = await client.aio.models.embed_content(
                model="text-embedding-005", contents=list(texts)
            )
            return [list(e.values) for e in resp.embeddings]

        return await _with_retry(_op)


def get_llm_client(settings: Settings | None = None) -> LlmClient:
    """Return the configured LLM client (``mock`` default, ``vertex`` when set)."""
    settings = settings or get_settings()
    if settings.llm_backend == "vertex":
        return VertexLlmClient(settings)
    return MockLlmClient()
