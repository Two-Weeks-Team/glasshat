"""Glasshat ingestion: deck text/PDF -> chunks -> embeddings.

The text path is deterministic and credential-free; PDF parsing uses Vertex
Gemini multimodal (lazy, credential-gated). Embeddings come from the injected
LLM client (mock or Vertex).
"""

from __future__ import annotations

from collections.abc import Sequence

from glasshat.agents.types import Chunk
from glasshat.shared.protocols import LlmClient


def chunk_text(text: str, *, max_chars: int = 800, source: str = "deck") -> list[Chunk]:
    """Split text into deterministic fixed-width character windows."""
    text = text.strip()
    if not text:
        return []
    chunks: list[Chunk] = []
    for start in range(0, len(text), max_chars):
        chunks.append(
            Chunk(id=f"{source}-{len(chunks)}", text=text[start : start + max_chars], source=source)
        )
    return chunks


async def ingest_deck(
    text: str | None = None,
    pdf_bytes: bytes | None = None,
    llm: LlmClient | None = None,
    *,
    source: str = "deck",
    max_chars: int = 800,
) -> list[Chunk]:
    """Ingest a deck from raw text (preferred) or PDF bytes (Vertex multimodal)."""
    if text is not None:
        return chunk_text(text, max_chars=max_chars, source=source)
    if pdf_bytes is not None:  # pragma: no cover - requires Vertex multimodal
        parsed = await _parse_pdf(pdf_bytes)
        return chunk_text(parsed, max_chars=max_chars, source=source)
    raise ValueError("ingest_deck requires either text or pdf_bytes")


async def embed_chunks(chunks: Sequence[Chunk], llm: LlmClient) -> list[Chunk]:
    """Attach embedding vectors to chunks (in place of a vector store)."""
    if not chunks:
        return []
    vectors = await llm.embed([c.text for c in chunks])
    return [c.model_copy(update={"vector": vec}) for c, vec in zip(chunks, vectors, strict=True)]


async def _parse_pdf(pdf_bytes: bytes) -> str:  # pragma: no cover - requires Vertex multimodal
    from glasshat.shared.config import get_settings
    from google import genai
    from google.genai import types

    settings = get_settings()
    client = genai.Client(
        vertexai=True,
        project=settings.google_cloud_project,
        location=settings.gemini_pro_location,
    )
    resp = await client.aio.models.generate_content(
        model=settings.gemini_pro,
        contents=[
            types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
            "Extract all text from this deck as plain markdown.",
        ],
    )
    return str(resp.text or "")
