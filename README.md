# Glasshat

### Trace it. Trust it.

> **Glasshat doesn't just judge projects — it audits the judge.**

**Why now:** AI writes the submissions now. Vibe-coding has multiplied hackathon, grant, and review entries — [most developers use AI coding tools daily and a large share of new code is AI-generated](https://daily.dev/blog/vibe-coding-how-ai-changing-developers-code/) — but the judging didn't change. Organizers will tell you [judging is "the biggest pain point"](https://dorahacks.io/blog/guides/hackathon-judging-plan), and the tooling still lacks **variance detection and audit trails**. Glasshat is exactly that missing layer.

Glasshat ingests a pitch deck + a GitHub repo + **the evaluator's official rules**, synthesizes a per-evaluation rubric that mirrors those rules, runs a six-perspective AI panel that grounds every sub-score in retrieved evidence, and then — live, on screen — **catches its own over-confidence and self-corrects the score**, with the 3D evaluation graph reshaping as it happens. It is an *artifact-ingesting evaluation pipeline + a transparent fairness monitor*, **not a chatbot**.

Every agent, every one of the six hats, and the self-correction itself opens its own **trace span in Arize AX** — so the score isn't a black box you take on faith. You open the trace of how it was judged and audited, and check it. **Trace it. Trust it.**

**Track**: Google Cloud Rapid Agent Hackathon — **Arize track**. Built on **Gemini (Vertex AI) + Google ADK** with **Arize AX** observability (OpenInference/OTLP → `otlp.arize.com`), and the **Phoenix MCP server** available for the live-trace-driven calibration consultant. **Live model: `gemini-3.1-flash-lite`** (Vertex, served on the `global` endpoint).

**Live deployment** (Cloud Run, `panelyst-hackathon`, us-central1, min-instances=0):
- Web: **https://glasshat-web-o366v7tl2q-uc.a.run.app** (`/judge` · `/participate`)
- API: **https://glasshat-api-o366v7tl2q-uc.a.run.app** (`/health` · `/api/evaluate`)

### See it in ≈60 seconds (no install)

1. Open **https://glasshat-web-o366v7tl2q-uc.a.run.app/participate**.
2. Pick the **Rapid Agent** rubric preset, paste any pitch text, submit.
3. **Approve the plan** at gate 1 (the inspectable plan card: 6 hats, criteria, weights).
4. Watch the **live SSE monitor** stream the pipeline (`ingesting → planning → hats_running → auditing`), then the **audit self-correct** beat: an over-confident hat (e.g. YELLOW pulled back ≈`0.8 × mean_delta` at low evidence — `9.0 → 7.84`) is corrected and the **3D constellation reshapes** to the calibrated position.
5. `/judge` shows the batch view: rank by rubric, ordered tie-break, gate-2 override, lock — plus the **rank-flip board** ("the audit changes who wins").

Or hit the API directly (real Gemini 3.1 RunRecord):
```bash
curl -s -X POST https://glasshat-api-o366v7tl2q-uc.a.run.app/api/evaluate \
  -H 'content-type: application/json' \
  -d '{"rubric_source":{"preset_id":"rapid-agent"},"deck_text":"we built ...","mode":"judge"}'
# → RunRecord: per-criterion scores + audit_corrections (the live self-correction)
```

**Two viewports, one engine**: `/judge` (batch rank + lock official scores) and `/participate` (single submission + iterate on the weakest axis). *"Same engine. Different viewer. Different fairness."*

---

### ✅ Rapid Agent · Arize track — compliance at a glance

> Already saw the demo above? Here's the proof behind it. Full detail +
> run-it-yourself commands: **[`docs/rapid-agent-compliance.md`](docs/rapid-agent-compliance.md)** ·
> **[`docs/evidence-matrix.md`](docs/evidence-matrix.md)**.

| Requirement | Implementation | Code path | Verify | Status |
|---|---|---|---|---|
| **Gemini / Vertex AI** | live `gemini-3.1-flash-lite` on the Vertex `global` endpoint (+ `gemini-3.1-pro` for rubric synthesis) | `packages/shared/src/glasshat/shared/llm.py` (`VertexLlmClient`) | `POST <API>/api/evaluate` → real-Gemini `RunRecord` | ✅ Live |
| **Agent runtime** (code-owned ADK) | a real **ADK 2.0 graph-`Workflow`** (ingest→synth→plan→6-hat parallel fan-out→join→audit→score) **deployed on the Gemini Enterprise Agent Platform (Agent Engine)**. The Cloud Run demo runs the **parity-identical python path** (`AGENT_RUNTIME=python`, byte-identical RunRecord+SSE — the gated default); the genuine ADK Workflow runs on Agent Engine. | `…/pipeline/adk_agents.py` (Workflow), `…/pipeline/agent_engine.py`, `deploy/agent_engine_deploy.py` | live resource `…/reasoningEngines/7480191458771730432` (`stream_query` → `RunRecord`) | ✅ Live (Agent Engine) |
| **Arize partner integration** | OpenInference/OTLP → **Arize AX** (`otlp.arize.com`): **full nested trace tree** (agent→Workflow→6 hats' Gemini calls, 104 spans verified) **+ Datasets + Experiments + Evaluator Hub**; live **hit@13 = 0.6154** | `…/pipeline/agent_engine.py` (`setup_arize_tracing`), `…/pipeline/arize_experiment.py` | `client.spans.list(project="glasshat")` → 104 spans; AX experiment `glasshat-hit-at-13-gemini` | ✅ Live |
| **Phoenix MCP server** | ADK `MCPToolset` over stdio → `npx @arizeai/phoenix-mcp@latest`; audit consultant calls the MCP `get-dataset-examples` tool + writes corrections back (learning loop) | `…/pipeline/adk_runtime.py` (`build_phoenix_mcp_toolset`, `PhoenixMcpConsultant`, `PhoenixMcpDatasetWriter`) | `uv run python scripts/real_e2e.py` | ✅ **Live** — the deployed audit reads the `glasshat-calibration` dataset and writes each correction back over MCP **per request**, against a Cloud-SQL-backed Phoenix on Cloud Run (`PHOENIX_COLLECTOR_ENDPOINT` set; seed via `scripts/seed_phoenix_calibration.py`) ([§3](docs/rapid-agent-compliance.md#3-arize-partner-mcp-path-agent--mcp--traceeval--report)) |
| **Cloud Run** | API + web, project `panelyst-hackathon`, us-central1, min-instances=0 | `infra/deploy.sh`, `infra/cloudbuild-*.yaml`, `infra/Dockerfile.*` | `curl -fsS <API>/health` → 200 | ✅ Live |
| **CI / tests / live API** | GH Actions: ruff + mypy + pytest (cov ≥ 90) · web lint/tsc/vitest/build · docker · supply-chain leak gate | `.github/workflows/ci.yml` | `uv run pytest` → 323 passed; web 74 passed | ✅ Green |

---

### 🛰️ Also deployed as a genuine ADK 2.0 *Workflow* agent on the Gemini Enterprise Agent Platform

Beyond the Cloud Run front door, the **evaluation brain itself is deployed as a real
ADK 2.0 graph-`Workflow` agent on the Gemini Enterprise Agent Platform (Agent Engine/
Runtime)** and serves live queries — with the **full nested trace tree** landing in
**Arize AX**. (Vertex AI was renamed → Gemini Enterprise Agent Platform at Cloud Next 2026; the SDK still imports as `vertexai`.)

- **Live Agent Engine resource** — `…/reasoningEngines/7480191458771730432` (managed Sessions + Memory Bank + `AGENT_IDENTITY`). A `stream_query` returns a real `RunRecord` with a live `final_score`. Code: `services/pipeline-orchestrator/src/glasshat/pipeline/agent_engine.py`, `deploy/agent_engine_deploy.py`.
- **Full nested AX trace tree** — verified via `client.spans.list(project="glasshat")`: **104 spans** across two live queries — `agent_run [glasshat_eval] → invocation → 48× AsyncGenerateContent + 50× AsyncEmbedContent` (the six hats' Gemini generate + embedding calls). The Agent-Engine trace-drop landmine is fixed with an **isolated provider** (`register(set_global_tracer_provider=False)`) + the OpenInference **ADK + google-genai** instrumentors.
- **Live calibration figure — Arize AX Experiment** — **hit@13 = 0.6154** on real Gemini (8 of 13 historical winners ranked into the top-13), vs **0.3846** mock and **0.26** chance. Binary Winner-badge label → this is **hit@13, not a rank curve**; for this golden set the audit did not reorder the top-13 (Δ = 0). Code: `services/pipeline-orchestrator/src/glasshat/pipeline/arize_experiment.py`.
- **Arize AX Datasets + Experiments + Evaluator Hub** — a `glasshat-golden` dataset, a `glasshat-hit-at-13-gemini` experiment, and a `glasshat-prompt-injection` code evaluator, all genuine.

Every number is captured in [`claudedocs/arize-evidence/ax-live-capture.json`](claudedocs/arize-evidence/ax-live-capture.json) (re-runnable). **Provenance:** the nested trace is emitted by the **deployed resource** `7480…` (its `invocation` + per-hat Gemini spans); the **hit@13 0.6154** comes from the **experiment harness** (`run_arize_experiment.py`, real Gemini over the golden set) pushed to the same AX space — the same pipeline, a different invocation, not a query of the deployed agent.

Reproduce (owner GCP/Arize creds):
```bash
# deploy the ADK 2.0 Workflow agent to Agent Engine
GOOGLE_CLOUD_PROJECT=panelyst-hackathon GOOGLE_CLOUD_QUOTA_PROJECT=panelyst-hackathon \
  uv run --with-requirements deploy/requirements-cloud.txt \
  python deploy/agent_engine_deploy.py --project=panelyst-hackathon --staging-bucket gs://glasshat-agent-staging
# run the hit@13 Arize AX experiment on real Gemini
ARIZE_SPACE_ID=… ARIZE_API_KEY=… LLM_BACKEND=gemini-enterprise \
  uv run --with-requirements deploy/requirements-cloud.txt python experiments/run_arize_experiment.py
```

> Honest scope: the Cloud Run demo above runs `gemini-3.1-flash-lite`; the Agent-Engine
> deployment runs the GA `gemini-enterprise` backend (`gemini-3.5-flash`/`gemini-3.1-pro`).
> Both share one byte-identical pipeline (parity-gated). No "un-gameable" claim; the
> calibration number is binary-label hit@13, not a rising rank curve.
>
> Security scope (honest): the **public Cloud Run demo runs `SCORING_MODE=legacy`** — the
> historical free-text `SCORE:` extraction, which a planted `SCORE: 10` can steer — and
> its judge-only endpoints (`/override`, un-redacted views) are **open** (`JUDGE_API_TOKEN`
> unset). The hardened path ships and is opt-in: `SCORING_MODE=structured` (typed JSON that
> quarantines the submission) + `JUDGE_API_TOKEN` + the always-on injection guard. Flipping
> them on the live instance is a user-gated prod redeploy.

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
        │     (dense cosine + BM25 + RRF); every agent + hat is its own Arize AX span
        │
   AuditLoop  (calibration self-correct: clip(score − 0.8·mean_delta, p25, p75))  ── glasshat.agents.audit
        │     Consultant protocol: deployed path = PhoenixMcpConsultant — reads per-cell
        │     drift from the live glasshat-calibration dataset + writes each correction
        │     back, over Phoenix MCP/stdio per request (Cloud-SQL-backed Phoenix on Cloud
        │     Run); TableConsultant (spike-D held-out prior) is the fallback when no
        │     PHOENIX_COLLECTOR_ENDPOINT is set
        │
   BMADScorer → ReportAssembler  (final score in the rubric's native scale)
        │
   RunRecord  →  Firestore / SQLite / memory      ── glasshat.shared.docstore
```

- **Rubric-aware, not one-size-fits-all.** Each criterion maps onto a shared **BMAD vocabulary** so scores are comparable across rubrics. The official Rapid Agent rule is **4 criteria × equal 25%** (Technological Implementation, Design, Potential Impact, Quality of the Idea) with **tie-break by listed order**.
- **Dual-rubric variance (feature).** The same submission scored under two synthesized rubrics yields legitimately different finals — *correct rubric-aware variance, not bias*.
- **Self-correction is real math** (validated in `spikes/`), not theatre: an over-confident, low-evidence assessment is pulled back toward calibrated past evaluations.
- **No vector database.** Retrieval is **in-code** (Vertex embeddings + cosine + `rank-bm25` + RRF) over an **in-memory** index, rebuilt per run; the resulting `RunRecord` — not the index — persists to the docstore (the **live deploy uses in-memory**, so run history is not durable across cold restarts; Firestore / SQLite are opt-in). No Qdrant.

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

**Config-flip backends** (env): `LLM_BACKEND` (`mock`|`vertex`|`gemini-enterprise`), `MONITOR_BACKEND` (`phoenix-local`|`phoenix-cloud`|`arize`), `CONSULTANT_BACKEND` (`table`|`phoenix-mcp`|`anchor`), `DOCSTORE_BACKEND` (`memory`|`sqlite`|`firestore`), `BLOB_BACKEND` (`local-fs`|`gcs`), `AGENT_RUNTIME` (`python`|`adk`). The `mock`/`memory`/`local-fs`/`noop` backends are complete, deterministic implementations — the whole engine runs and is tested with **zero credentials**.

## Reproduce

**Python engine + API (no credentials — `mock`/`memory` backends, deterministic):**
```bash
uv sync
uv run pytest                       # full suite, mock/memory backends
uv run uvicorn glasshat.api:create_app --factory --port 8088
curl -s localhost:8088/health
curl -s -X POST localhost:8088/api/evaluate \
  -H 'content-type: application/json' \
  -d '{"rubric_source":{"preset_id":"rapid-agent"},"deck_text":"we built ...","mode":"participant"}'
# Scores here are deterministic (mock LLM). For real Gemini, set LLM_BACKEND=vertex
# + the GLASSHAT_GEMINI_* / GOOGLE_CLOUD_* env (see .env.example), or use the live demo above.
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

Engine, API, and web are built and **CI-green** (SDD + TDD; one PR per phase — merged PRs **#7 onward**, see the repo PR list). The web was rebuilt from a thin shell into two fully functional viewports (PRs #15–#18), then elevated visually (PRs #20–#23: mesh-gradient design system, animated hero motif, bento grid, count-up, scroll reveals). A build-time fix ensures the deployed client actually reaches the API (`NEXT_PUBLIC_API_BASE` is baked at web build, not runtime). Observability is wired to **Arize AX** (PR #24); the live model was migrated to **`gemini-3.1-flash-lite`** with a location-aware Vertex client that routes Gemini 3.x to the `global` endpoint (PR #27), and every orchestration agent now emits its own `glasshat.agent` AX span (PR #28). See `claudedocs/2026-05-22-production-self-assessment.md`. Verified:

- **Lighthouse ≥ 90** on all pages — fresh live (post-deploy): landing **92/95/96**, `/judge` **93/96/96**, `/participate` **95/96/96** (Performance / Accessibility / Best-Practices). Motion respects `prefers-reduced-motion`.
- **Live Arize AX observability**: the deployed service registers to `otlp.arize.com` (project `glasshat`) and emits a span **per agent** (`RubricSynthesizer · BluePlanner · SixHatPanel · Audit · BMADScorer · ReportAssembler`) plus per-hat `hat_assess` spans on every evaluation — verified via live registration logs (no export errors) and a live real-Gemini eval on `gemini-3.1-flash-lite` (e.g. run `2b2e29c2`, final 56.93, 4 audit self-corrections). e2e: `scripts/real_arize_ax_e2e.py`.

- **Mock stack** (no credentials): full `run_evaluation` end-to-end, self-correct, SSE, 397 tests (323 py + 74 web), Docker images build in CI.
- **Real e2e** (`scripts/real_e2e.py`): real Vertex Gemini + Vertex embeddings + in-code hybrid retrieval + self-hosted Phoenix + real Phoenix MCP (stdio, `list-projects` via a Google ADK agent) → RubricSynthesizer→6-hat→audit **self-correct** → report. Evidence: `claudedocs/2026-05-21-real-e2e-evidence.md` _(headline numbers there were captured pre-#27 on gemini-2.5; the live path is now gemini-3.1-flash-lite)_.
- **Live Cloud Run**: both viewports return HTTP 200; `/api/evaluate` returns a self-corrected `RunRecord` on real `gemini-3.1-flash-lite`.
- **3D self-correction**: `/participate` runs the pipeline and reshapes the constellation from real output — `claudedocs/assets/glasshat-3d-self-correction.png`.

See `docs/superpowers/plans/` for the per-phase build plans.

## Lineage and no-code-reuse

Glasshat is a **new project created during the Contest Period** (May 5 – Jun 11, 2026), as the
rules require ("newly created … not a modification or extension of … existing work"). Detail +
audit commands in [`docs/rapid-agent-compliance.md` §5](docs/rapid-agent-compliance.md#5-lineage-and-no-code-reuse).

- **First commit `dda8dc1` = 2026-05-13** — inside the period. The repo began as an empty
  scaffold ("Initial commit"); it was first named **Panelyst** and renamed to **Glasshat** in
  PR #1 — a rename inside this same fresh repo, not an import of prior code.
- **Public + open source**: https://github.com/Two-Weeks-Team/glasshat, **Apache-2.0**
  ([`LICENSE`](LICENSE)) — present since the first commit, visible at the repo root.
- **fairthon is concept lineage only.** It seeded the *idea* of fairness-aware evaluation;
  **no fairthon source code is reused** (`grep -rli fairthon --include='*.py' .` → no matches).
  The engine — rubric synthesizer, 6-hat panel, audit self-correction, ADK + Phoenix-MCP
  runtime, in-code hybrid retrieval — was authored from scratch in this repo (see the
  key-files list in compliance §5).

## License

Apache-2.0 — see [`LICENSE`](LICENSE).
