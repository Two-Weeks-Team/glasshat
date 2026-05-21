from collections.abc import Mapping, Sequence
from contextlib import contextmanager
from typing import Any

from glasshat.shared.protocols import BlobStore, DocStore, LlmClient, Retrieval, Tracer


def test_llmclient_protocol_structural() -> None:
    class Fake:
        async def generate(self, prompt: str, *, tier: str = "flash", **kw: Any) -> str:
            return "x"

        async def embed(self, texts: Sequence[str]) -> list[list[float]]:
            return [[0.0]]

    assert isinstance(Fake(), LlmClient)


def test_retrieval_protocol_structural() -> None:
    class FakeR:
        def search(self, query: str, *, top_k: int = 5, **kw: Any) -> list[Any]:
            return []

        def index(self, docs: Any) -> None:
            return None

    assert isinstance(FakeR(), Retrieval)


def test_docstore_and_blobstore_protocols() -> None:
    class FakeDoc:
        def get(self, c: str, i: str) -> Mapping[str, Any] | None:
            return None

        def put(self, c: str, i: str, d: Mapping[str, Any]) -> None:
            return None

        def query(self, c: str, **f: Any) -> list[Mapping[str, Any]]:
            return []

    class FakeBlob:
        def put_blob(self, key: str, data: bytes) -> str:
            return key

        def get_blob(self, key: str) -> bytes:
            return b""

    assert isinstance(FakeDoc(), DocStore)
    assert isinstance(FakeBlob(), BlobStore)


def test_tracer_protocol() -> None:
    class FakeTracer:
        @contextmanager
        def span(self, name: str, **attrs: Any) -> Any:
            yield None

        def set_attr(self, key: str, value: Any) -> None:
            return None

    assert isinstance(FakeTracer(), Tracer)


def test_non_conforming_object_is_not_instance() -> None:
    assert not isinstance(object(), LlmClient)
