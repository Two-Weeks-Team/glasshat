# services/ingest (`glasshat.ingest`)

Deck ingestion: deterministic text chunking + (optional) Vertex Gemini multimodal
PDF parsing, then Vertex embeddings attached to each chunk. The chunks feed the
**in-code hybrid retrieval** index (dense cosine + BM25 + RRF) — there is **no
Qdrant**. Runs credential-free on the deterministic `mock` LLM backend.
Implemented and tested (`agents`/`services` test suites, CI-green).
