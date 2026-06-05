# Glasshat — Evidence Matrix

> **⬆️ 2026-06-05 — newer genuine evidence not in the 2026-05-23 rows below:** a live ADK
> 2.0 Workflow agent on **Agent Engine** (`reasoningEngines/7480191458771730432`), the **full
> nested Arize AX trace** (per-hat Gemini spans via `client.spans.list(project="glasshat")`),
> and AX **Dataset `glasshat-golden` + Experiment `glasshat-hit-at-13-gemini`** (hit@13 0.6154)
> + code evaluator `glasshat-prompt-injection`. Machine-readable: [`../claudedocs/arize-evidence/ax-live-capture.json`](../claudedocs/arize-evidence/ax-live-capture.json); narrative: README "🛰️ Also deployed…".
>
> Every load-bearing claim, with the **exact command or URL** a judge can run and the
> **observed result**. Companion to [`docs/rapid-agent-compliance.md`](./rapid-agent-compliance.md)
> and `README.md`. Results below were observed on **2026-05-23** (commit on branch
> `docs/rapid-agent-compliance-evidence`).

Repo: **https://github.com/Two-Weeks-Team/glasshat** · License: **Apache-2.0** (root `LICENSE`).

---

## A. Reproducible locally (no credentials — `mock`/`memory` backends)

| Claim | Command | Observed result (2026-05-23) |
|---|---|---|
| Python engine + API test suite passes | `uv run pytest` | **323 passed, 3 deselected** (3 = `@integration`, need live creds) |
| Coverage gate (CI) holds | `uv run pytest --cov=glasshat --cov-fail-under=90` | passes (coverage ≈ 97.8%, `uv run --cov`) |
| Lint clean | `uv run ruff check .` | no errors |
| Format clean | `uv run ruff format --check .` | no changes needed |
| Types clean (strict) | `uv run mypy packages agents services apps/api` | passes |
| Web unit tests pass | `cd apps/web && pnpm test` | **Test Files 21 passed, Tests 74 passed** |
| Web lint clean | `cd apps/web && pnpm lint` | no errors |
| Web types clean | `cd apps/web && pnpm typecheck` | `tsc --noEmit` passes |
| Web builds | `cd apps/web && pnpm build` | static prerender of `/`, `/judge`, `/participate` |
| API runs + serves a deterministic eval | `uv run uvicorn glasshat.api:create_app --factory --port 8088` then `curl -s localhost:8088/health` and `POST /api/evaluate` | health 200; `RunRecord` returned (deterministic mock LLM) |
| Full stack via Docker | `docker compose -f infra/docker-compose.yml up --build` | web :3000, api :8088 |

## B. Real-integration (require live creds; proven by scripts/tests)

| Claim | Command / file | What it proves |
|---|---|---|
| Real ADK → **Phoenix MCP** stdio round trip | `uv run python scripts/real_e2e.py` | ADK agent calls `npx @arizeai/phoenix-mcp@latest` over stdio, then the full pipeline self-corrects → report |
| Phoenix **Cloud** MCP variant | `uv run python scripts/real_phoenix_cloud_e2e.py` | same path against Phoenix Cloud |
| Real **Arize AX** tracing (per-agent spans) | `uv run python scripts/real_arize_ax_e2e.py` | OpenInference → `otlp.arize.com`; one span per agent + per hat |
| Consultant satisfies the audit protocol | `uv run pytest services/pipeline-orchestrator/tests/test_adk_runtime.py` | `PhoenixMcpConsultant` is a valid `Consultant`; `build_phoenix_mcp_toolset` is callable |
| Real Gemini eval on the live model | live API (below) | `RunRecord` on `gemini-3.1-flash-lite` with `audit_corrections` |

## C. Live deployment (Cloud Run, project `panelyst-hackathon`)

| Claim | URL / command | Observed |
|---|---|---|
| Web up (3 routes) | https://glasshat-web-o366v7tl2q-uc.a.run.app , `/judge` , `/participate` | HTTP 200 |
| API health | `curl -fsS https://glasshat-api-o366v7tl2q-uc.a.run.app/health` | 200 |
| Live real-Gemini eval | `curl -s -X POST https://glasshat-api-o366v7tl2q-uc.a.run.app/api/evaluate -H 'content-type: application/json' -d '{"rubric_source":{"preset_id":"rapid-agent"},"deck_text":"we built …","mode":"judge"}'` | `RunRecord` w/ per-criterion scores + `audit_corrections` on `gemini-3.1-flash-lite` (e.g. run `2b2e29c2`, final 56.93, 4 self-corrections) |
| Lighthouse ≥ 90 (live, fresh) | `npx lighthouse <url> --chrome-flags=--user-data-dir=/tmp/lh-iso` | landing **91–92/95/96**, `/judge` **93/96/96**, `/participate` **92–95/96/96** (Perf/A11y/BP) |
| Arize AX registration | Cloud Run logs after deploy | registers to `otlp.arize.com` (project `glasshat`), no export errors |

## D. Code-path anchors (open these files)

| Capability | File:symbol |
|---|---|
| Gemini on Vertex (location-aware, `global` for 3.x) | `packages/shared/src/glasshat/shared/llm.py` → `VertexLlmClient` |
| Arize AX tracer | `packages/shared/src/glasshat/shared/tracing.py` → `ArizeTracer` (l.68) |
| Per-agent spans | `services/pipeline-orchestrator/src/glasshat/pipeline/engine.py:115-149` |
| Calibration prior (deployed audit) | `…/pipeline/engine.py:61` → `_YELLOW_DELTA_BY_BUCKET`; `agents/src/glasshat/agents/audit.py` |
| ADK runtime + Phoenix MCP toolset/consultant | `…/pipeline/adk_runtime.py` → `instrument_adk`, `build_phoenix_mcp_toolset`, `PhoenixMcpConsultant`, `run_via_adk` |
| Phoenix MCP tool call | `…/pipeline/adk_runtime.py:82` → `get-dataset-examples` |
| FastAPI surface | `apps/api/src/glasshat/api/app.py` → `/health` (l.64), `/api/evaluate` (l.89), `/api/evaluate/stream` SSE (l.93) |
| Cloud Run deploy | `infra/deploy.sh` (`gcloud run deploy glasshat-api / glasshat-web`) |
| CI | `.github/workflows/ci.yml` |

## E. Lineage / originality

| Claim | Command | Observed |
|---|---|---|
| First commit inside Contest Period (May 5 – Jun 11, 2026) | `git log --reverse --format='%h %ad %s' --date=short \| head -1` | `dda8dc1 2026-05-13 Initial commit` |
| OSI license present from the start | `git log --diff-filter=A --format='%ad %h' --date=short -- LICENSE \| tail -1` | `2026-05-13 dda8dc1` (Apache-2.0 in the initial commit) |
| No fairthon source reused | `grep -rli fairthon --include='*.py' . \| grep -v '/.venv/'` | **no matches** (fairthon appears only in docs/handoffs as concept lineage) |
| Public repo | `git remote get-url origin` | `https://github.com/Two-Weeks-Team/glasshat` |

## F. "Not the shipped state" — terms a judge might worry about

| Term | Reality | Where it legitimately appears |
|---|---|---|
| **Qdrant** | **Not used.** In-code hybrid retrieval (Vertex embeddings + cosine + `rank-bm25` + RRF). | Banner-marked historical/planning docs only (`docs/architecture.md`, `docs/max-wins-plan.md`, …) |
| **LangGraph** | **Not used.** Google ADK runtime. | Historical docs only |
| **Visual Agent Builder** | **Not used** (track says it's insufficient — see compliance §2). ADK + Cloud Run instead. | Historical docs only |
| **Firebase Auth** | **Not used.** Open demo endpoints. | Historical docs only |
| **Gemini 2.5** | **Not the live model.** Live = `gemini-3.1-flash-lite`. | Explicitly-historical notes only |
| **Dual submission** | **Single Arize-track submission.** | Historical `docs/max-wins-plan.md` (now banner-marked) |

Verify no shipped-state contamination in the two authoritative docs + README:
```bash
grep -niE 'qdrant|langgraph|firebase|gemini[ -]?2\.5|dual.?submit' \
  README.md docs/rapid-agent-compliance.md docs/evidence-matrix.md
# → only the explicit "not used / historical" rows above
```
