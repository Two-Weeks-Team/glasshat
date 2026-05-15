# Glasshat — Session Handoff

> New session: `cd ~/Documents/GitHub/panelyst` then `/handon` (this file is at repo root). For Claude's persistent memory of this project see `/Users/kimsejun/.claude/projects/-Users-kimsejun-Documents-GitHub-hackathon-submissions/memory/` (start at `MEMORY.md`).

Last updated: 2026-05-14 KST.

---

## §0 — Two-line summary

**Glasshat** = an agentic fair-evaluation panel: ingest a pitch deck (PDF) + a codebase → six-perspective AI panel → 100-pt BMAD-style rubric score with **evidence-grounded, precedent-anchored** scores → 3D evaluation graph + a **live transparent fairness monitor**. **Not a chatbot.** Single project, dual-submitted to the **Qdrant "Think Outside the Bot" hackathon** (deadline **2026-06-01 23:59 PT** — Qdrant DB mandatory, no chatbots, all code in-period; submission via Google Form `forms.hl.qdrant.tech/hackathon-vsd`) AND the **Google Cloud Rapid Agent hackathon** (~2026-06-11/12 — Gemini + Google Cloud Agent Builder + an **Arize** partner-MCP integration that powers the real-time fairness monitor). Same codebase for both — only the demo video / framing differs.

## §1 — Repo & lineage

- Repo: `Two-Weeks-Team/panelyst` (public, Apache-2.0). Local clone: `~/Documents/GitHub/panelyst/`. First commit 2026-05-13 — inside the Qdrant hackathon period → compliant with the "all code created during the hackathon period (no previous projects)" rule.
- This repo occupies what the umbrella tracker calls the "WhyC fairthon-port" slot. The **prior `Two-Weeks-Team/WhyC` ("While YC hires, we ship") project is archived on GitHub.** Different product, not used here.
- Concept lineage: methodology (Six Thinking Hats, BMAD 17-item rubric, 75 techniques, 3D graph) derives from **fairthon.com** (same team). Disclosed in README. **No fairthon code reused.** fairthon source (reference only, not copied): `~/Documents/GitHub/fairthon/`.

## §2 — What's done · what's next

### Done (2026-05-13 → 2026-05-14)
- [x] Repo scaffold (README + monorepo dir skeleton + `.gitignore` + LICENSE Apache-2.0).
- [x] Full plan committed: [`PLAN.md`](PLAN.md) (mirrored from the umbrella tracker, built from a 6-expert-team analysis).
- [x] Authoritative architecture doc: [`docs/architecture.md`](docs/architecture.md) (topology, agent graph mermaid, sequence mermaid, phase-by-phase deployment, abstractions, the two human gates).
- [x] **GCP project bootstrap** ([`docs/gcp-setup.md`](docs/gcp-setup.md)) — `panelyst-hackathon` project (916178791322) on `app.2weeks@gmail.com`, billing linked to 크레딧계정 (`01B677-A6E5C9-B265AF`), 13 APIs enabled, service account `panelyst-dev` with 8 roles, SA key at `~/.config/gcloud/panelyst-dev-sa-key.json` (mode 600, outside the repo).
- [x] **Vertex AI Gemini panel verified live** ([`docs/gcp-setup.md`](docs/gcp-setup.md)) — `gemini-3.1-pro-preview` / `gemini-3-flash-preview` / `gemini-3.1-flash-lite` on **global** endpoint; 2.5 fallbacks on us-central1. All 6 models confirmed working with the SA key.
- [x] `.env` populated locally (gitignored); `.env.example` updated to the verified configuration with all phase 1–5 env vars; abstraction switches documented.

### Not started (in priority order)
- [ ] **Phase 1 — local E2E** (per [[user-local-first-then-cloud]] decision): docker-compose for Qdrant local + Phoenix in-process + Python services + Next.js frontend, all calling Vertex Gemini directly via the SA key.
  - [ ] LLM adapter (Vertex global/regional routing + 3-tier model selection + fallback + token budgets) — `services/pipeline-orchestrator/`
  - [ ] Qdrant 6 collection schemas + hybrid (dense+sparse) embedding strategy — see memory `qdrant-collection-design`
  - [ ] Phoenix tracer integration (OTel spans for every hat call / tool call / retrieval / score) + meta-eval metrics
  - [ ] PDF ingest path (Gemini multimodal via Flash-Lite, chunk → Qdrant `pitch_chunks`)
  - [ ] Code Grader (clone + static heuristics + sample → Qdrant `repo_chunks`; ~15-20 BMAD-relevant checks)
  - [ ] BMAD 17-item rubric YAML (`packages/rubric/`) + 75-technique registry (≥20 populated) + 6 Hat system prompts (`agents/`)
  - [ ] Pipeline orchestrator (LangGraph DAG: BLUE planner → 5 hats parallel → BLUE synthesis → BMAD scorer with rubric-aware RAG → evidence grounding → immutable run record to SQLite)
  - [ ] Next.js frontend (two drop zones + plan card + monitor dashboard + report + 2D radar + vector-search page + i18n KO/EN + SSE)
  - [ ] Seed `past_evals` from ~50–150 public Devpost projects (a few hours batch on the credits)
- [ ] Phase 2 — Cloud Run + Cloud Storage + Firestore + Eventarc.
- [ ] Phase 3 — wrap orchestrator as Google Cloud Agent Builder app (Rapid Agent mandate).
- [ ] Phase 4 — switch `QDRANT_URL` to Qdrant Cloud.
- [ ] Phase 5 — switch `MONITOR_BACKEND` to Arize hosted (Rapid Agent partner integration finalized).
- [ ] Submission assets (×2: Qdrant + Rapid Agent): hosted URL + LICENSE-in-About + ~3-min videos (different framing per hackathon) + README + architecture diagram + Devpost form (Rapid Agent) + Google Form (Qdrant).

## §3 — Verified configuration (snapshot — see docs/gcp-setup.md for full)

| Item | Value |
|---|---|
| GCP project | `panelyst-hackathon` (`916178791322`) |
| Billing | `01B677-A6E5C9-B265AF` (크레딧계정, app.2weeks@gmail.com) |
| Service account | `panelyst-dev@panelyst-hackathon.iam.gserviceaccount.com` |
| SA key | `~/.config/gcloud/panelyst-dev-sa-key.json` (mode 600) |
| Default region | `us-central1` (Gemini 2.5 + Cloud Run + Firestore) |
| **Gemini 3 family endpoint** | **`global`** (regional returns 404) |
| Pro model | `gemini-3.1-pro-preview` @ global (preview; eval-JSON p50 ≈ 9.3s) |
| Flash model | `gemini-3-flash-preview` @ global (preview; p50 ≈ 4.0s) |
| Flash-Lite model | `gemini-3.1-flash-lite` @ global (**GA**; p50 ≈ 1.3s — fastest) |
| Pro/Flash/Lite fallbacks | `gemini-2.5-pro` / `gemini-2.5-flash` / `gemini-2.5-flash-lite` @ us-central1 |

Gotchas (also in docs/gcp-setup.md): `gemini-3-pro-preview` returns 404 — the real 3-Pro slot is `gemini-3.1-pro-preview`. Gemini 2.5 Pro is a thinking model — needs ≥2000 output tokens or hits MAX_TOKENS. Don't rely on ADC; use the SA key.

## §4 — Persistent memory

Claude's memory of this project across sessions: [`/Users/kimsejun/.claude/projects/-Users-kimsejun-Documents-GitHub-hackathon-submissions/memory/MEMORY.md`](file:///Users/kimsejun/.claude/projects/-Users-kimsejun-Documents-GitHub-hackathon-submissions/memory/MEMORY.md). Key entries: `panelyst-project`, `gcp-panelyst-hackathon`, `gemini-model-panel-verified`, `qdrant-vsd-hackathon`, `rapid-agent-hackathon`, `fairthon-lineage`, `qdrant-collection-design`, `user-local-first-then-cloud`, `user-proper-gcp-setup`, `user-decision-via-askuserquestion`, `production-safety-rules`.

## §5 — Resume prompt (copy-paste)

> Working dir: `~/Documents/GitHub/panelyst/` (loaded via `/handon`). GCP setup + Gemini 3 panel verified — see docs/gcp-setup.md. Phase 1 (local E2E) not started. Read PLAN.md + docs/architecture.md + the memory index. Hard rules: non-chatbot; all code authored in the hackathon period (no fairthon code reuse — fairthon is concept lineage, disclosed in README); Qdrant load-bearing; Gemini via Vertex with SA key (not AI Studio, not ADC); Arize is the Rapid Agent partner integration. Build Qdrant-first (deadline 2026-06-01). Next concrete step: pick one of {LLM adapter, Qdrant collections + docker-compose, ingest path, Code Grader, BMAD rubric config, Next.js frontend scaffold, past_evals seed corpus}.
