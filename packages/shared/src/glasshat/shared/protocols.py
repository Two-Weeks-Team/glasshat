"""Abstraction interfaces (the "config flip" boundaries from architecture §5).

Each external system is consumed through one of these ``Protocol`` types; the
concrete implementation is chosen by a backend selector in
:mod:`glasshat.shared.config`. Implementations land in Phase 2
(``glasshat.shared.llm``, ``glasshat.shared.retrieval``, etc.). These are
``@runtime_checkable`` so structural conformance can be asserted in tests.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from contextlib import AbstractContextManager
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class LlmClient(Protocol):
    """Generation + embedding over a Gemini/Vertex (or deterministic ``mock``) backend."""

    async def generate(self, prompt: str, *, tier: str = "flash", **kwargs: Any) -> str: ...

    async def embed(self, texts: Sequence[str]) -> list[list[float]]: ...


@runtime_checkable
class Retrieval(Protocol):
    """In-code hybrid retrieval (dense cosine + BM25 + RRF). No external vector DB."""

    def search(self, query: str, *, top_k: int = 5, **kwargs: Any) -> list[Any]: ...

    def index(self, docs: Iterable[Any]) -> None: ...


@runtime_checkable
class DocStore(Protocol):
    """Document persistence (memory / sqlite / firestore)."""

    def get(self, collection: str, doc_id: str) -> Mapping[str, Any] | None: ...

    def put(self, collection: str, doc_id: str, doc: Mapping[str, Any]) -> None: ...

    def query(self, collection: str, **filters: Any) -> list[Mapping[str, Any]]: ...


@runtime_checkable
class BlobStore(Protocol):
    """Binary blob persistence (local-fs / gcs). Returns a stable reference key/URI."""

    def put_blob(self, key: str, data: bytes) -> str: ...

    def get_blob(self, key: str) -> bytes: ...


@runtime_checkable
class Tracer(Protocol):
    """OpenInference/Phoenix span emission with ``glasshat.*`` custom attributes."""

    def span(self, name: str, **attrs: Any) -> AbstractContextManager[Any]: ...

    def set_attr(self, key: str, value: Any) -> None: ...
