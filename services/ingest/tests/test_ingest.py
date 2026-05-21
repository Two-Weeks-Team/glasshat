import asyncio

import pytest
from glasshat.agents.types import Chunk
from glasshat.ingest import chunk_text, embed_chunks, ingest_deck
from glasshat.shared.llm import MockLlmClient


def test_chunk_text_windows() -> None:
    chunks = chunk_text("a" * 2000, max_chars=800)
    assert len(chunks) == 3  # 800 + 800 + 400
    assert all(isinstance(c, Chunk) and c.source == "deck" for c in chunks)
    assert all(len(c.text) <= 800 for c in chunks)
    assert len({c.id for c in chunks}) == 3  # unique ids


def test_chunk_text_empty() -> None:
    assert chunk_text("   ") == []


def test_ingest_deck_text_path() -> None:
    chunks = asyncio.run(ingest_deck(text="We built a multi-agent system. It is novel."))
    assert len(chunks) >= 1
    assert chunks[0].source == "deck"


def test_ingest_deck_requires_a_source() -> None:
    with pytest.raises(ValueError):
        asyncio.run(ingest_deck())


def test_embed_chunks_sets_vectors() -> None:
    chunks = chunk_text("hello world foo bar baz", max_chars=8)
    embedded = asyncio.run(embed_chunks(chunks, MockLlmClient(embedding_dim=8)))
    assert all(c.vector is not None and len(c.vector) == 8 for c in embedded)
