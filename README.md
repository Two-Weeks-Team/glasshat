# Glasshat

> **Glasshat doesn't just judge projects. It audits the judge.**

Glasshat ingests a pitch deck + a GitHub repo + **the evaluator's official rules**, synthesizes a per-evaluation rubric that mirrors those rules, runs a six-perspective AI panel that grounds every sub-score in retrieved evidence, and then — live, on screen — **catches its own over-confidence and self-corrects the score**, with the 3D evaluation graph reshaping as it happens. It is an *artifact-ingesting evaluation pipeline + a transparent fairness monitor*, **not a chatbot**.

**Track**: Google Cloud Rapid Agent Hackathon — **Arize track**. Built on **Gemini (Vertex AI) + Google ADK** with **Arize Phoenix** observability and the **Phoenix MCP server** consulted at runtime for the self-improvement loop.

**Live deployment** (Cloud Run, `panelyst-hackathon`, us-central1, min-instances=0):
- Web: **https://glasshat-web-o366v7tl2q-uc.a.run.app** (`/judge` · `/participate`)
- API: **https://glasshat-api-o366v7tl2q-uc.a.run.app** (`/health` · `/api/evaluate`)

**Two viewports, one engine**: `/judge` (batch rank + lock official scores) and `/participate` (single submission + iterate on the weakest axis). Closing line: *"Same engine. Different viewer. Different fairness."*

---

## How it works

```
deck.pdf + repo URL + rubric source
        │
   ingest (chunk + Vertex embeddings)        ── glasshat.ingest / glasshat.code_grader
        │
   RubricSynthesizer  (official rules → SynthesizedRubric)   ── glasshat.agents.rubric_synthesizer
        │
   BluePlanner → 6-hat panel (White/Red/Yellow/Black/Green/Blue)   ── glasshat.agents.hats
        │     each hat retrieves evidence via in-code hybrid search
        │     (dense cosine + BM25 + RRF), every step a Phoenix span
        │
   AuditLoop  (calibration self-correct: clip(score − 0.8·mean_delta, p25, p75))  ── glasshat.agents.audit
        │     consults Phoenix over MCP (stdio) for per-cell drift stats
        │
   BMADScorer → ReportAssembler  (final score in the rubric's native scale)
        │
   RunRecord  →  Firestore / SQLite / memory      ── glasshat.shared.docstore
```

- **Rubric-aware, not one-size-fits-all.** Each criterion maps onto a shared **BMAD vocabulary** so scores are comparable across rubrics. The official Rapid Agent rule is **4 criteria × equal 25%** (Technological Implementation, Design, Potential Impact, Quality of the Idea) with **tie-break by listed order**.
- **Dual-rubric variance (feature).** The same submission scored under two synthesized rubrics yields legitimately different finals — *correct rubric-aware variance, not bias*.
- **Self-correction is real math** (validated in `spikes/`), not theatre: an over-confident, low-evidence assessment is pulled back toward calibrated past evaluations.
- **No vector database.** Retrieval is **in-code** (Vertex embeddings + cosine + `rank-bm25` + RRF) over a Firestore-persisted + in-memory index — no Qdrant.

## Architecture (monorepo)

| Path | Package | Role |
|---|---|---|
| `packages/shared` | `glasshat.shared` | config, ids, enums, errors, abstraction Protocols, **llm** (mock/Vertex), **retrieval** (hybrid), **tracing** (NoOp/Phoenix), **docstore**, **blobstore** |
| `packages/rubric` | `glasshat.rubric` | `SynthesizedRubric` model + JSON Schema, BMAD vocabulary, presets, validation |
| `agents/` | `glasshat.agents` | engine stages (synthesizer, planner, hats, audit, scorer, report) |
| `services/ingest` | `glasshat.ingest` | deck chunking/embed + Vertex multimodal PDF |
| `services/code-grader` | `glasshat.code_grader` | static repo heuristics |
| `services/pipeline-orchestrator` | `glasshat.pipeline` | `run_evaluation` end-to-end + SSE + ADK/Phoenix-MCP runtime |
| `apps/api` | `glasshat.api` | FastAPI: evaluate / plan gate / SSE stream / runs / override gate |
| `apps/web` | `glasshat-web` | Next.js 16: landing + `/judge` (batch rank · tie-break · gate-2 override · lock) + `/participate` (plan gate · live SSE monitor · evidence · audit callouts · 3D self-correction) |
| `infra/` | — | Dockerfiles, compose, Cloud Run deploy |

**Config-flip backends** (env): `LLM_BACKEND` (`mock`\|`vertex`), `MONITOR_BACKEND` (`phoenix-local`\|`phoenix-cloud`), `DOCSTORE_BACKEND` (`memory`\|`sqlite`\|`firestore`), `BLOB_BACKEND` (`local-fs`\|`gcs`), `AGENT_RUNTIME` (`adk-local`\|`adk-cloud-run`). The `mock`/`memory`/`local-fs`/`noop` backends are complete, deterministic implementations — the whole engine runs and is tested with **zero credentials**.

## Reproduce

**Python engine + API (no credentials):**
```bash
uv sync
uv run pytest                       # full suite, mock/memory backends
uv run uvicorn glasshat.api:create_app --factory --port 8088
curl -s localhost:8088/health
curl -s -X POST localhost:8088/api/evaluate \
  -H 'content-type: application/json' \
  -d '{"rubric_source":{"preset_id":"rapid-agent"},"deck_text":"we built ...","mode":"participant"}'
```

**Web (no credentials):**
```bash
cd apps/web && pnpm install && pnpm dev   # http://localhost:3000
```

**Full stack (Docker):**
```bash
docker compose -f infra/docker-compose.yml up --build   # web :3000, api :8088
```

**Live (Cloud Run, project=`panelyst-hackathon`, us-central1, min-instances=0):**
```bash
# Real Vertex Gemini + Arize AX tracing (default). One-time: put the Arize AX API key
# (the `ak-…` key) in Secret Manager, and grant the Cloud Run SA aiplatform.user + secretAccessor:
#   printf '%s' "<ARIZE_API_KEY>" | gcloud secrets create phoenix-api-key --data-file=- --project=panelyst-hackathon
ARIZE_SPACE_ID=<your-AX-space-id> bash infra/deploy.sh --confirm

# Real Vertex Gemini, tracing off (no observability creds needed):
bash infra/deploy.sh --confirm --no-phoenix

# Deterministic mock/memory demo — no credentials at all:
bash infra/deploy.sh --confirm --mock
```
The script ignores your active gcloud project and always targets `panelyst-hackathon` explicitly.
It deploys the API first, then bakes the live API URL into the web client bundle at build time
(`NEXT_PUBLIC_API_BASE` is build-time, not runtime). Observability backends: `arize` (Arize AX,
`otlp.arize.com`), `phoenix-cloud`/`phoenix-local` (Arize Phoenix), or NoOp.

## Status

Engine, API, and web are built and **CI-green** (SDD + TDD; one PR per phase — see merged PRs #7–#25). The web was rebuilt from a thin shell into two fully functional viewports (PRs #15–#18), then elevated visually (PRs #20–#23: mesh-gradient design system, animated hero motif, bento grid, count-up, scroll reveals). A build-time fix ensures the deployed client actually reaches the API (`NEXT_PUBLIC_API_BASE` is baked at web build, not set at runtime). Observability is wired to **Arize AX** (PR #24) and deps are at latest majors (PR #25). See `claudedocs/2026-05-22-web-rebuild-verification.md` and `claudedocs/2026-05-22-design-elevation-verification.md`. Verified:

- **Lighthouse ≥ 90** on all pages: landing 90/95/96 (desktop), 95/95/96 (mobile); `/judge` & `/participate` 100/96/96 (desktop) — Performance / Accessibility / Best-Practices. Motion respects `prefers-reduced-motion`.
- **Live Arize AX observability**: the deployed service registers to `otlp.arize.com` (project `glasshat`) and exports a span per pipeline stage on every evaluation — verified via the live registration logs (no export errors) and a live real-Gemini eval (run `58f6892c`, final 64.6). e2e: `scripts/real_arize_ax_e2e.py`.

- **Mock stack** (no credentials): full `run_evaluation` end-to-end, self-correct, SSE, 150+ tests, Docker images build in CI.
- **Real e2e** (`scripts/real_e2e.py`): real Vertex Gemini + Vertex embeddings + in-code hybrid retrieval + self-hosted Phoenix (80 spans) + real Phoenix MCP (stdio, 27 tools, `list-projects` call via a Google ADK agent) → RubricSynthesizer→6-hat→audit **self-correct** → final 54.04. Evidence: `claudedocs/2026-05-21-real-e2e-evidence.md`.
- **Live Cloud Run**: both viewports return HTTP 200; `/api/evaluate` returns a self-corrected `RunRecord`.
- **3D self-correction**: `/participate` runs the pipeline and reshapes the constellation from real output — `claudedocs/assets/glasshat-3d-self-correction.png`.

See `docs/superpowers/plans/` for the per-phase build plans.

## License

Apache-2.0 — see [`LICENSE`](LICENSE).
