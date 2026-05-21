# Glasshat (Panelyst) — Arize-Track Build Roadmap (Reconciled Spec-of-Record)

> **Authority order**: this roadmap reconciles `docs/*` (2026-05-15 baseline) with the **2026-05-21 locked decisions** in `claudedocs/2026-05-21-session-handoff.md` §2. Where they conflict, locked decisions + this roadmap win. This is the SDD source-of-truth for the build; per-phase plans derive from it.
>
> **Created**: 2026-05-21. Drives the `/goal` build condition (handoff §3).

---

## 0. What changed vs. `docs/architecture.md` (locked-decision reconciliation)

| Topic | `docs/*` baseline (2026-05-15) | **Locked decision (authoritative)** |
|---|---|---|
| Vector store | Qdrant (6 collections, Recommendation API, weighted RRF lib, quantization) | **Qdrant removed.** Vertex `text-embedding` + **in-code hybrid retrieval** (dense cosine + `rank-bm25` sparse + RRF fusion) over a **Firestore-persisted + in-memory** index. Module: `glasshat.shared.retrieval` (NOT `qdrant.py`). The 6 "collections" become Firestore collections + in-memory indices. |
| Orchestrator | "Phase 1 LangGraph local → Phase 3 Agent Builder" | **Google ADK** end-to-end (`google-adk`). No LangGraph. |
| Tracks | Dual: Qdrant VSD (primary) + Rapid Agent/Arize (secondary) | **Arize track only.** Qdrant VSD not pursued. **Dual-rubric variance kept as a product feature** (same submission, two synthesized rubrics, legitimate score delta). |
| AI provider | Gemini (already) | **Gemini/Google only.** Vertex Gemini for all generation; Phoenix LLM-as-judge model = Gemini; embeddings = Vertex; sparse = statistical BM25 (`rank-bm25`, not neural). **No OpenAI/Anthropic in production.** |
| Scoring weights | `rapid-agent` shown as Tech 40 / Inn 30 / Imp 20 / Pres 10 in `rubric-synthesis-spec.md` §1 | **Official rule = 4 criteria × equal 25%**: ① Technological Implementation ② Design ③ Potential Impact ④ Quality of the Idea. **Tie-break = listed order** (Tech→Design→Impact→Idea), then judge vote. The `rapid-agent` preset MUST encode `25/25/25/25` + ordered tie-break. The "40/30/20/10" in the spec doc is wrong and is corrected here. |
| README/docs | Dual-claim ("two viewports for Qdrant + Rapid Agent", "Qdrant primary") | **Arize-only re-narration.** Stack wording = ADK. dual-rubric variance retained as a feature, not a track. |

**Arize Stage-1 hard gates** (must all be live in the demo): OpenInference auto-instrument (`phoenix.otel.register(auto_instrument=True)` + `GoogleADKInstrumentor`) → Phoenix trace send (Cloud free tier or self-host) → Phoenix MCP runtime introspection (ADK `MCPToolset` + stdio `npx @arizeai/phoenix-mcp`) → LLM-as-judge evals on traces → self-improvement loop (Blue planner queries Phoenix MCP mid-eval → score self-corrects).

---

## 1. Stack & monorepo layout (locked for this build)

Polyglot monorepo, **Python-first engine + TypeScript frontend**:

- **Python 3.12**, managed by **`uv` workspace** (root `pyproject.toml` with `[tool.uv.workspace]`). Members: `packages/shared`, `packages/rubric`, `services/ingest`, `services/pipeline-orchestrator`, `services/code-grader`, `agents/*`, `apps/api`.
- **Namespace package** `glasshat.*` (PEP 420 implicit namespace). `packages/shared` → `glasshat.shared`; `packages/rubric` → `glasshat.rubric`; `services/*` → `glasshat.<service>`.
- **TypeScript** `apps/web` = Next.js 16 (App Router), managed by **`pnpm`** (standalone; not in the uv workspace). Consumes the rubric JSON Schema as its cross-language contract.
- **Lint/format/type (Python)**: `ruff` (lint+format) + `mypy --strict` (or `pyright`). **Test**: `pytest` + `pytest-cov`. **Frontend**: `eslint` + `tsc --noEmit` + `vitest`/`playwright`.
- **Cross-language contract**: `packages/rubric/synthesized.schema.json` (JSON Schema 2020-12). Python validates via pydantic (model is the source; schema is generated/checked against it in CI). TS consumes the emitted schema.
- **Config flip via env** (architecture §5, retained): `LLM_BACKEND` (`vertex`|`mock`), `MONITOR_BACKEND` (`phoenix-local`|`phoenix-cloud`), `DOCSTORE_BACKEND` (`memory`|`sqlite`|`firestore`), `BLOB_BACKEND` (`local-fs`|`gcs`), `AGENT_RUNTIME` (`adk-local`|`adk-cloud-run`). `mock` backends make CI/TDD run with zero external calls.

---

## 2. Phases → PRs (each phase = one feature branch → PR → main, squash forbidden)

Per-phase PR boundary is a goal requirement. Each phase ships working, CI-green, tested software. SDD (schema/contract first) + TDD (red→green→refactor; test committed before impl) inside every phase.

| Phase | Branch | Scope | Exit criteria (PR merge gate) |
|---|---|---|---|
| **P1** | `feat/arize-packages` | **Foundation** (root `uv` workspace `pyproject.toml` + `ruff`/`mypy`/`pytest` config + `.github/workflows/ci.yml` lint+typecheck+test+coverage + updated `.env.example` [Qdrant removed, ADK, Gemini-only] + `.gitignore` for `var/`) **+ packages**: `packages/shared` (`glasshat.shared`: config, env, ids/hashing, errors, base enums, abstraction Protocols) + `packages/rubric` (`glasshat.rubric`: `SynthesizedRubric` pydantic model, `synthesized.schema.json`, BMAD vocabulary, 4 presets incl. **corrected** `rapid-agent` 25/25/25/25, preset loader, custom-YAML validator, §7 validation pipeline, canonicalization → `rubric_schema_hash` + `weights_vector`). Foundation + packages are one cohesive PR (can't build/test packages without the workspace). | `uv sync` works; `uv run pytest` 0 failures; CI workflow present + green; `ruff`+`mypy --strict` clean; coverage ≥90% on `packages/*`; schema↔model consistency test green; `rapid-agent` preset asserts 25/25/25/25 + tie-break order. |
| **P2** | `feat/arize-services-shared` | `services/shared` (lives under `packages/shared` or `services/shared`): `glasshat.shared.llm` (Vertex Gemini adapter + `mock` backend + OpenInference span), `glasshat.shared.retrieval` (Vertex embeddings + dense cosine + `rank-bm25` + RRF + weight-aware anchor; in-memory + Firestore-backed), `glasshat.shared.tracing` (Phoenix register + `glasshat.*` span attrs), `glasshat.shared.docstore`/`blobstore` (memory/sqlite/local-fs + firestore/gcs). | TDD all green with `mock`/`memory` backends; RRF + weight-aware anchor unit-tested against known vectors; coverage ≥90%; real-Vertex path behind a marked integration test (skipped without ADC). |
| **P3** | `feat/arize-ingest-agents` | `services/ingest` (PDF→Gemini multimodal parse→chunk→embed; repo clone→static heuristics→chunk) + `agents/*` (RubricSynthesizer, BluePlanner, 6 hats, AuditLoop, BMADScorer, ReportAssembler) + `services/pipeline-orchestrator` (ADK root agent wiring the sequence; Phoenix MCP `MCPToolset` self-improvement; SSE-emitting). 503-corpus seed from `data/devpost-gemini3`. | TDD green with `mock` LLM; pipeline runs end-to-end on `mock` producing a `runs/{id}` record with self-correct delta; Phoenix MCP wiring unit-tested (stdio mock); coverage ≥85%; real-Gemini integration test marked. |
| **P4** | `feat/arize-apps` | `apps/api` (FastAPI: `/evaluate`, plan-approve gate, score-override gate, SSE stream, Phoenix webhook) + `apps/web` (Next.js: landing, `/judge` + `/participate` viewports, shared components, 3D self-correction graph PCA/UMAP via r3f, SSE consumer, Firebase auth). | API contract tests green; web build (`pnpm build`) + `tsc` + `vitest` green; Playwright e2e on `mock` engine green; SSE delta + 3D reshape driven by real pipeline output (screenshot). |
| **P5** | `feat/arize-infra-deploy` | `infra` (multi-stage Dockerfile(s), `docker-compose`, Cloud Run config) + finalize CI (build+deploy) + **live deploy** to Cloud Run (`panelyst-hackathon`, `us-central1`, min=0) + README Arize-only re-narration + reproduce guide. | Cloud Run URL `curl` 200 on `/judge` + `/participate`; full **real-input e2e** (Vertex Gemini + Vertex embeddings + in-code hybrid + Phoenix trace + Phoenix MCP) passes with logs surfaced; README rewritten; all phase PRs merged. |

**Final completion (goal §7)**: full e2e re-run passes + all phase PRs merged + CI green + deploy 200, surfaced together with evidence.

---

## 3. SDD + TDD discipline (every phase)

1. **SDD**: before code, fix the contract — pydantic model / JSON Schema / FastAPI OpenAPI / TS types — derived from `docs/*`. The contract is committed and reviewed first.
2. **TDD**: per unit, write the failing test (red) → run to confirm it fails → minimal impl (green) → run to confirm pass → refactor → commit. **Test commit precedes (or accompanies, test-first in the same commit ordering) the implementation**; `squash 금지` preserves this ordering as evidence.
3. **Verification gate per PR**: `ruff` clean, `mypy --strict` clean, `pytest` 0 failures, coverage threshold met, CI green. No merge without these.
4. **No mock/stub in product code paths** (the `mock` LLM/`memory` store *backends* are legitimate config-selected implementations per architecture §5, not stubs — they are real, complete, deterministic implementations used for tests/CI).

---

## 4. Credential / live-dependency reality (honest blockers)

- **GCP ADC**: handoff §6 says present on this machine (`~/.config/gcloud/application_default_credentials.json`). Real Vertex calls (P2/P3 integration tests, P5 e2e) depend on it + the `panelyst-hackathon` project + billing.
- **Phoenix Cloud**: needs `PHOENIX_API_KEY` / collector endpoint (handoff §6 — may need user setup on this machine). Self-host Phoenix (in-process) is the fallback for local; Cloud for the demo.
- **Cloud Run deploy** (P5): needs `gcloud` auth + billing; deploy is performed by this build (not the production-8080 server — different project, explicitly allowed).
- Everything through **P1, P2-unit, P3-unit, P4-build** runs with **zero external calls** (`mock`/`memory` backends) and is fully verifiable in-session. Live integration (P2/P3 integration tests, P5 e2e+deploy) is attempted and, if a credential/billing gate blocks it, surfaced to the user rather than faked.

---

*Per-phase detailed TDD plans live alongside this file as `2026-05-21-phaseN-*.md`.*
