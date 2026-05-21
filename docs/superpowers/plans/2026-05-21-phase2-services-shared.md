# Phase 2 — Shared services layer (`glasshat.shared.{llm,retrieval,tracing,docstore,blobstore}`)

> REQUIRED SUB-SKILL: superpowers:executing-plans (inline). Derives from `2026-05-21-glasshat-roadmap.md`. Branch: `feat/arize-services-shared`.

**Goal:** Implement the shared runtime layer behind the P1 abstraction Protocols — the in-code hybrid retrieval that replaces Qdrant, the Vertex/mock LLM adapter, the Phoenix/NoOp tracer, and the docstore/blobstore backends — with full TDD. `mock`/`memory`/`local-fs`/`noop` backends + the pure retrieval math are unit-tested with zero credentials; real Vertex/Phoenix/Firestore/GCS implementations are lazy-imported and exercised only by integration tests that **skip** without credentials.

**Architecture:** All modules live in `packages/shared/src/glasshat/shared/` (matches the spec's `glasshat.shared.llm` import path and the goal's scaffold-fill list, which has no `services/shared`). Heavy SDKs are optional extras + lazy imports; `numpy` + `rank-bm25` are core deps (the hybrid retrieval is the product, not a mock). Backend selection is by `glasshat.shared.config.Settings`.

**Tech Stack:** numpy, rank-bm25 (core); google-genai/google-adk, arize-phoenix(+otel)/openinference-instrumentation-google-adk, google-cloud-firestore, google-cloud-storage (optional, lazy). pytest markers: `integration` (deselected by default).

---

## SDD — contracts first (all implement P1 `glasshat.shared.protocols`)

```python
# retrieval
@dataclass
class Document: id: str; text: str; vector: list[float] | None = None; payload: dict[str, Any] = {}
@dataclass
class SearchHit: doc: Document; score: float; dense_rank: int | None; sparse_rank: int | None
class HybridIndex(Retrieval):
    def index(self, docs: Iterable[Document]) -> None
    def search(self, query: str, *, top_k=5, query_vector: list[float] | None = None,
               dense_weight: float = 1.0, sparse_weight: float = 1.0, **kw) -> list[SearchHit]
    def weight_aware_anchor(self, weights_vector: list[float], *, top_k=3) -> list[SearchHit]
def cosine_similarity(a, b) -> float
def rrf_fuse(rankings: list[list[str]], *, k: int = 60) -> dict[str, float]

# llm
class MockLlmClient(LlmClient):    # deterministic, complete (NOT a stub): hash-seeded
    async def generate(self, prompt, *, tier="flash", **kw) -> str
    async def embed(self, texts) -> list[list[float]]   # dim from settings (default 768)
class VertexLlmClient(LlmClient):  # lazy import google.genai; real Gemini + Vertex embeddings
def get_llm_client(settings=None) -> LlmClient   # mock | vertex

# tracing
class NoOpTracer(Tracer): ...
class PhoenixTracer(Tracer):       # lazy import phoenix.otel; glasshat.* span attrs
def get_tracer(settings=None) -> Tracer   # phoenix-* -> PhoenixTracer else NoOp

# docstore
class MemoryDocStore(DocStore): ...
class SqliteDocStore(DocStore):    # stdlib sqlite3, one table (collection, doc_id, body json)
class FirestoreDocStore(DocStore): # lazy google.cloud.firestore
def get_docstore(settings=None) -> DocStore   # memory | sqlite | firestore

# blobstore
class LocalFsBlobStore(BlobStore): ...
class GcsBlobStore(BlobStore):     # lazy google.cloud.storage
def get_blobstore(settings=None) -> BlobStore   # local-fs | gcs
```

---

## Task 1: deps + pytest `integration` marker + mypy overrides
**Files:** `packages/shared/pyproject.toml` (add `numpy`, `rank-bm25`; `[project.optional-dependencies]` vertex/phoenix/firestore/gcs), root `pyproject.toml` (`[tool.pytest.ini_options] markers`, `addopts = "-q -m 'not integration'"`; `[[tool.mypy.overrides]]` ignore_missing_imports for `rank_bm25`, `google.genai.*`, `phoenix.*`, `openinference.*`, `google.cloud.*`).
- [ ] `uv sync`; `uv run python -c "import numpy, rank_bm25"`; commit `chore(p2): retrieval deps + integration marker + mypy overrides`.

## Task 2: `retrieval` — cosine + RRF (pure math, TDD)
- [ ] RED `test_retrieval.py::test_cosine_similarity` (orthogonal=0, identical=1, known vectors). GREEN `cosine_similarity` (numpy).
- [ ] RED `test_rrf_fuse` (known rankings → known fused order; item in two lists ranks above singletons). GREEN `rrf_fuse`.
- [ ] Commit `feat(p2): retrieval cosine + RRF fusion`.

## Task 3: `retrieval` — HybridIndex + weight-aware anchor (TDD)
- [ ] RED `test_hybrid_search_combines_dense_and_sparse` (index 4 docs with vectors + text; a doc strong on BOTH dense+sparse ranks #1; dense-only and sparse-only docs both appear). RED `test_weight_aware_anchor` (docs carry payload["weights_vector"]; nearest-by-cosine-on-weights returned first). RED `test_search_empty_index_returns_empty`.
- [ ] GREEN `HybridIndex` (BM25Okapi over whitespace-tokenized texts; dense cosine over stacked vectors; per-modality rank lists → `rrf_fuse` → top_k `SearchHit`s). `weight_aware_anchor` (cosine over payload weights vectors).
- [ ] Commit `feat(p2): glasshat.shared.retrieval — in-code hybrid (dense+bm25+RRF) + weight anchor`.

## Task 4: `llm` — MockLlmClient + factory (TDD); VertexLlmClient (lazy, integration)
- [ ] RED `test_mock_generate_deterministic` (same prompt → same output; different → different). RED `test_mock_embed_deterministic_dim` (len==dim; same text same vector; normalized ~1.0). RED `test_get_llm_client_returns_mock_by_default`.
- [ ] GREEN `MockLlmClient` (hash-seeded numpy RNG for embeddings; generate returns deterministic tagged string). `get_llm_client` factory. `VertexLlmClient` with lazy `import google.genai` in `__init__`/methods (real generate via `genai.Client(vertexai=True)`, embed via Vertex embedding model).
- [ ] RED/integration `test_vertex_llm_smoke` marked `@pytest.mark.integration` + `skipif` no `GOOGLE_CLOUD_PROJECT`.
- [ ] Commit `feat(p2): glasshat.shared.llm — mock + Vertex Gemini adapter + factory`.

## Task 5: `tracing` — NoOpTracer + factory (TDD); PhoenixTracer (lazy, integration)
- [ ] RED `test_noop_tracer_span_contextmanager` (span() usable as `with`, set_attr no-op, no raise). RED `test_get_tracer_noop_for_mock_settings`.
- [ ] GREEN `NoOpTracer`, `PhoenixTracer` (lazy `phoenix.otel.register`), `get_tracer`. Integration test marked for Phoenix register.
- [ ] Commit `feat(p2): glasshat.shared.tracing — NoOp + Phoenix tracer + factory`.

## Task 6: `docstore` — Memory + Sqlite (TDD); Firestore (lazy, integration)
- [ ] RED `test_memory_docstore_put_get_query`, `test_sqlite_docstore_roundtrip` (tmp_path db; put/get/query equality filter; persists across instances), `test_get_docstore_memory_default`.
- [ ] GREEN `MemoryDocStore`, `SqliteDocStore` (sqlite3, JSON body), `FirestoreDocStore` (lazy), `get_docstore`.
- [ ] Commit `feat(p2): glasshat.shared.docstore — memory + sqlite + firestore + factory`.

## Task 7: `blobstore` — LocalFs (TDD); Gcs (lazy, integration)
- [ ] RED `test_localfs_put_get_blob` (tmp_path; put returns uri; get returns bytes; round-trip), `test_get_blobstore_localfs_default`.
- [ ] GREEN `LocalFsBlobStore`, `GcsBlobStore` (lazy), `get_blobstore`.
- [ ] Commit `feat(p2): glasshat.shared.blobstore — local-fs + gcs + factory`.

## Task 8: full gate + PR
- [ ] `uv run ruff check . && uv run ruff format --check packages && uv run mypy packages && uv run pytest --cov=glasshat --cov-report=term-missing --cov-fail-under=90` all green (coverage measured on non-integration; lazy real-backend bodies may be excluded via `# pragma: no cover` on the `import` lines guarded by credential checks, or covered by integration job — keep ≥90% on unit-reachable code).
- [ ] Push, open PR, CI green, merge with **merge commit** (no squash).

## Notes
- "mock"/"noop" backends are **real, complete, deterministic** implementations (architecture §5), not stubs/placeholders. No `TODO`/`placeholder`/`not implemented` strings anywhere. The final-verification grep (goal §2) targets the real e2e path; these documented backends are a legitimate config feature.
- Coverage: lazy real-SDK code paths (Vertex/Phoenix/Firestore/GCS) are only reachable with credentials. Mark those branches `# pragma: no cover` (justified: integration-only) so the ≥90% gate reflects unit-reachable logic; integration tests exercise them when creds exist.
