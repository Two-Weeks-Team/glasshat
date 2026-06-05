# Glasshat — Rapid Agent (Arize track) Compliance

> **Authoritative, judge-facing.** This document is the shipped-state contract for the
> Google Cloud Rapid Agent Hackathon — **Arize track**. Where any other doc (e.g.
> `docs/architecture.md`, `docs/max-wins-plan.md`) disagrees, **this file and `README.md`
> win**; those are historical/planning docs and are banner-marked as such.
> Companion: [`docs/evidence-matrix.md`](./evidence-matrix.md) (claim → command → result).

> **⬆️ Updated 2026-06-05 — this doc UNDERSTATES the shipped state.** Since the rows below
> were written, glasshat went further: the evaluation pipeline is now a genuine **ADK 2.0
> `Workflow` agent DEPLOYED on the Gemini Enterprise Agent Platform (Agent Engine)** — live
> resource `…/reasoningEngines/7480191458771730432`, serving `stream_query` — with the
> **full nested trace tree** in Arize AX (per-hat `AsyncGenerateContent`/`AsyncEmbedContent`
> spans, verified via `client.spans.list(project="glasshat")`) **plus Arize AX Datasets +
> Experiments + a code Evaluator** (`glasshat-golden`, `glasshat-hit-at-13-gemini`,
> `glasshat-prompt-injection`; live **hit@13 0.6154**). Where rows below say "ADK on Cloud
> Run" or "one span per agent", read **README.md "🛰️ Also deployed…"** +
> [`../claudedocs/arize-evidence/`](../claudedocs/arize-evidence/) as the current truth.

Live system: **Gemini `gemini-3.1-flash-lite` (Vertex AI) on Cloud Run + a genuine ADK 2.0
Workflow agent on the Gemini Enterprise Agent Platform (Agent Engine) + Arize AX
observability (full nested trace + datasets/experiments/evals) + Phoenix MCP server**,
project `panelyst-hackathon`, us-central1.

- Web: https://glasshat-web-o366v7tl2q-uc.a.run.app (`/judge` · `/participate`)
- API: https://glasshat-api-o366v7tl2q-uc.a.run.app (`/health` · `/api/evaluate`)

---

## 1. Compliance matrix

| # | Requirement | Implementation in Glasshat | Code path | Verify | Status |
|---|---|---|---|---|---|
| 1 | **Gemini on Vertex AI** (Google Cloud AI tool, required) | Location-aware Vertex client; live tier `gemini-3.1-flash-lite` on the Vertex **`global`** endpoint (Gemini 3.x is global-only); `gemini-3.1-pro` for URL→rubric synthesis; `text-embedding-005` (regional) for retrieval | `packages/shared/src/glasshat/shared/llm.py` → `VertexLlmClient` (`_client_for(location)`, lines 41–92); models in `infra/deploy.sh:99`, `.env.example:17–24` | `curl -s -X POST <API>/api/evaluate -d '{"rubric_source":{"preset_id":"rapid-agent"},"deck_text":"…","mode":"judge"}'` → real-Gemini `RunRecord` | ✅ Live |
| 2 | **Code-owned agent runtime** (rules name "Agent Builder"; the **Arize track** requires a code-owned runtime — *Gemini CLI / Agent Platform SDK / **Google ADK** / Agent Runtime / **Cloud Run***, and states **"Visual Agent Builder alone is insufficient. Direct code instrumentation is required."**) | **Google ADK** orchestrator, OpenInference-instrumented, deployed on **Cloud Run**. No visual Agent Builder app — that path is *explicitly disallowed* for this track. See §2. | `services/pipeline-orchestrator/src/glasshat/pipeline/adk_runtime.py` (`instrument_adk`, `run_via_adk`); engine `…/pipeline/engine.py`; deploy `infra/deploy.sh` | §2 below + `claudedocs/hackathon-source-2026-05-21/03-arize-resources.md` (the rule, quoted) | ✅ Resolved |
| 3 | **Arize partner integration** (OpenInference tracing → Arize/Phoenix) | OpenInference auto-instrumentation → **Arize AX** at `otlp.arize.com`; **one span per agent** (`RubricSynthesizer · BluePlanner · SixHatPanel · Audit · BMADScorer · ReportAssembler`) + per-hat `hat_assess`, all carrying `glasshat.*` attributes | `packages/shared/src/glasshat/shared/tracing.py` → `ArizeTracer` (registers via `arize.otel`, line 68); span sites `…/pipeline/engine.py:115–149` | `uv run python scripts/real_arize_ax_e2e.py`; live run `2b2e29c2` (final 56.93, 4 self-corrections) | ✅ Live |
| 4 | **Partner MCP server** (Phoenix MCP — required by the track) | ADK **`MCPToolset` over stdio** → `npx @arizeai/phoenix-mcp@latest`. The audit's calibration consultant calls the Phoenix MCP **`get-dataset-examples`** tool, parses per-anchor score deltas, and feeds them into the self-correction. See §3. | `…/pipeline/adk_runtime.py` → `build_phoenix_mcp_toolset` (l.31), `PhoenixMcpConsultant.consult` (l.53–96, tool `get-dataset-examples` l.82) | `uv run python scripts/real_e2e.py` (real ADK → Phoenix MCP stdio → pipeline) | ✅ Wired — exercised by e2e (see §3 on deployed vs. live-trace path) |
| 5 | **Cloud Run deployment** (Google Cloud hosting) | API + web both on Cloud Run, project `panelyst-hackathon`, us-central1, `min-instances=0`; API URL baked into the web bundle at build time | `infra/deploy.sh`, `infra/cloudbuild-api.yaml`, `infra/cloudbuild-web.yaml`, `infra/Dockerfile.api`, `infra/Dockerfile.web` | `curl -fsS https://glasshat-api-o366v7tl2q-uc.a.run.app/health` → 200; web `/`,`/judge`,`/participate` → 200 | ✅ Live |
| 6 | **CI / tests / Lighthouse / live API** (engineering quality evidence) | GitHub Actions: `ruff` + `ruff format` + `mypy --strict` + `pytest` (coverage gate ≥ 90%); web `eslint` + `tsc` + `vitest` + `next build`; Docker build (api + web) | `.github/workflows/ci.yml` | `uv run pytest` → **323 passed**; `cd apps/web && pnpm test` → **74 passed**; Lighthouse ≥ 90 all pages | ✅ Green |

Status legend: **✅ Live** = running in the deployed Cloud Run service; **✅ Wired** = real
integration, code path + e2e proven, with the deployment caveat stated in §3;
**✅ Green / Resolved** = verified by CI / documented interpretation.

---

## 2. Agent Builder ambiguity — resolved

**The question.** The general hackathon framing says: *"Build a functional agent—powered by
Gemini and **Google Cloud Agent Builder**—that integrates a Partner Entity's MCP server."*
Glasshat does **not** use the visual Agent Builder console. Is that a gap?

**The answer: No — and using it would have been wrong for this track.** The **Arize track
resources page** (captured verbatim at
`claudedocs/hackathon-source-2026-05-21/03-arize-resources.md`) narrows the requirement:

> *"The Arize track mandates 'a code-owned agent runtime — Gemini CLI, Gemini Enterprise
> Agent Platform SDK, **Google ADK**, Agent Runtime, or **Cloud Run**.' **Visual Agent
> Builder alone is insufficient. Direct code instrumentation is required.**"*

"Agent Builder" is the umbrella for Google's agent stack (Vertex AI Agent Builder spans the
visual console **and** the code-first ADK + Agent Runtime + Cloud Run options). For the Arize
track, the **code-owned runtime is mandatory** precisely because the track is judged on
**direct code instrumentation** (OpenInference) and **meaningful MCP use** — neither of which
the visual builder alone can demonstrate.

**What Glasshat ships, mapped to the rule:**

| Track-accepted runtime | Glasshat |
|---|---|
| **Google ADK** | Orchestrator wired with the Google ADK runtime + `MCPToolset`, OpenInference-instrumented — `services/pipeline-orchestrator/src/glasshat/pipeline/adk_runtime.py` (`instrument_adk`, `build_phoenix_mcp_toolset`, `run_via_adk`) |
| **Cloud Run** | API + web deployed to Cloud Run — `infra/deploy.sh` (`gcloud run deploy glasshat-api / glasshat-web`) |
| Direct code instrumentation | `GoogleADKInstrumentor().instrument(...)` + OpenInference → Arize AX — `adk_runtime.py:22–28`, `packages/shared/src/glasshat/shared/tracing.py` |

**Conclusion:** Glasshat satisfies "Agent Builder" via the track's own enumerated, code-owned
options (ADK + Cloud Run). The visual Agent Builder is deliberately **not** used because the
Arize track declares it insufficient on its own. This is a documented rules interpretation
backed by the official track page, not an omission. No thin visual-builder wrapper is added,
as it would add an un-instrumented, un-judged surface contrary to the track's intent.

---

## 3. Arize partner MCP path (agent → MCP → trace/eval → report)

```
EvaluationInput (deck_text + rubric_source [+ repo_url])
   │
   ▼  Google ADK runtime, OpenInference auto-instrumented
   │     instrument_adk()  ──► GoogleADKInstrumentor + OTLP → Arize AX (otlp.arize.com)
   │     adk_runtime.py:22-28 · tracing.py ArizeTracer (l.68)
   │
   ▼  6 agents, each its own Arize AX span (glasshat.agent=…)
   │     RubricSynthesizer → BluePlanner → SixHatPanel(+per-hat hat_assess)
   │     engine.py:115-149
   │
   ▼  AuditLoop — self-correction needs calibration stats per (hat, criterion, evidence-bucket)
   │     ┌─ DEPLOYED path: TableConsultant — spike-D held-out calibrated prior
   │     │     (_YELLOW_DELTA_BY_BUCKET, engine.py:61) → deterministic, no network
   │     └─ LIVE-TRACE path: PhoenixMcpConsultant.consult(hat,criterion,bucket)
   │           ADK MCPToolset over stdio → `npx @arizeai/phoenix-mcp@latest`
   │           → Phoenix MCP tool `get-dataset-examples` (adk_runtime.py:82)
   │           → parse per-anchor deltas → mean/p25/p75
   │     clip(score − 0.8·mean_delta, p25, p75)   ← the on-screen self-correct
   │
   ▼  BMADScorer → ReportAssembler → RunRecord (audit_corrections[])
   │
   ▼  Glasshat report / dashboard
         /participate live SSE monitor + 3D constellation reshape;
         /judge batch rank + lock. RunRecord persisted (Firestore/SQLite/memory).
```

**Honest deployment note (no overclaim).** Two consultants implement the same
`glasshat.agents.audit.Consultant` protocol:

- The **deployed Cloud Run audit** uses **`TableConsultant`** — a calibrated prior recovered
  from the spike-D held-out anchors (`docs/spike-results.md §4`), so the live demo
  self-corrects deterministically with **zero external dependency**.
- The **`PhoenixMcpConsultant`** is the **live-trace variant**: it performs the real
  partner-MCP round trip (ADK → Phoenix MCP over stdio → `get-dataset-examples`) and is
  **exercised end-to-end** by `scripts/real_e2e.py` and `scripts/real_phoenix_cloud_e2e.py`.
  Wiring it into the live API hot path is a tracked follow-up (see the session handoff "deferred"
  list); it is **not** silently claimed to run on every production request.

This separation is the partner-MCP proof: the MCP integration is real code, validated by
a real stdio round trip (spike-C pattern, `adk_runtime.py:31-44`), and the calibration math
it returns is the same math the deployed audit applies.

**Evidence to look at:**
- Code: `services/pipeline-orchestrator/src/glasshat/pipeline/adk_runtime.py`
- e2e scripts: `scripts/real_e2e.py`, `scripts/real_phoenix_cloud_e2e.py`, `scripts/real_arize_ax_e2e.py`
- Tests: `services/pipeline-orchestrator/tests/test_adk_runtime.py` (consultant satisfies the protocol; toolset builder callable)
- Real-run evidence: `claudedocs/2026-05-21-real-e2e-evidence.md` (headline numbers captured pre-#27 on the older model; the live path is now `gemini-3.1-flash-lite`)

---

## 4. Gemini model — one canonical answer

**Live model = `gemini-3.1-flash-lite`** (Vertex AI, `global` endpoint). `gemini-3.1-pro`
backs the pro tier (URL→rubric synthesis only). **Gemini 2.5 is not used and is forbidden by
project policy.**

| Surface | Token | Note |
|---|---|---|
| `README.md` | `gemini-3.1-flash-lite` | live model, stated up front |
| `.env.example:19,23` | `gemini-3.1-pro`, `gemini-3.1-flash-lite` | (`GLASSHAT_GEMINI_FLASH` template default is `gemini-3.5-flash`; the live deploy overrides FLASH → `gemini-3.1-flash-lite` in `deploy.sh:99`) |
| `infra/deploy.sh:99` | `gemini-3.1-flash-lite` (flash + flash_lite), `gemini-3.1-pro` (pro) | the values actually deployed |
| `scripts/real_*_e2e.py` | `gemini-3.1-flash-lite` | real-eval scripts |

Any "Gemini 2.5" string that remains in the repo is **explicitly historical** (e.g.
`README.md` Status note: *"headline numbers captured pre-#27 on gemini-2.5; the live path is
now gemini-3.1-flash-lite"*, and the banner-marked planning docs). No current judge-facing
doc claims 2.5 as the shipped model.

---

## 5. Lineage and no-code-reuse

| Rule (official) | Glasshat evidence |
|---|---|
| *"Projects must be newly created by the entrant during the Contest Period."* (Contest Period: **May 5 – Jun 11, 2026**) | **First commit `dda8dc1` = 2026-05-13** — inside the period. Verify: `git log --reverse --format='%h %ad %s' --date=short \| head -1` |
| *"original creation, not a modification or extension of … existing work"* | Built from an empty scaffold (`dda8dc1` "Initial commit"). The project was first named **Panelyst**, renamed to **Glasshat** in PR #1 (`5ac5ba7`) — a rename within this same fresh repo, **not** an import of prior code. |
| Public, open-source repo with a visible OSI license | Public GitHub repo (org `Two-Weeks-Team`); **Apache-2.0** in [`LICENSE`](../LICENSE) at the repo root, linked from `README.md`. Verify: `head -3 LICENSE` |
| No reuse of prior personal projects (incl. **fairthon**) | **fairthon is concept lineage only** — it seeded the *idea* of fairness-aware evaluation. **No fairthon source code is reused.** Glasshat's engine (rubric synthesizer, 6-hat panel, audit self-correction, ADK + Phoenix-MCP runtime, in-code hybrid retrieval) was authored from scratch in this repo. |

**Key implementation files authored in Glasshat (origin of record):**
- `packages/shared/src/glasshat/shared/llm.py` — location-aware Vertex client
- `packages/shared/src/glasshat/shared/tracing.py` — NoOp / Phoenix / Arize AX tracers
- `packages/shared/src/glasshat/shared/retrieval.py` — in-code hybrid retrieval (cosine + BM25 + RRF)
- `agents/src/glasshat/agents/{rubric_synthesizer,blue_planner,hats,audit,bmad_scorer,report}.py`
- `services/pipeline-orchestrator/src/glasshat/pipeline/{engine.py,adk_runtime.py}` — orchestration + ADK/Phoenix-MCP runtime
- `apps/api/src/glasshat/api/app.py` — FastAPI (`/api/evaluate`, SSE stream, gates)
- `apps/web/**` — Next.js `/judge` + `/participate`

**To audit the claim directly:**
```bash
git log --reverse --format='%h %ad %s' --date=short | head -5   # first commit in-period
git log --diff-filter=A --format='%ad %h' --date=short -- LICENSE | tail -1   # license added
grep -rli fairthon --include='*.py' . | grep -v '/\.venv/' || echo "no fairthon code"
```
