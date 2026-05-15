# Glasshat

> **The panel that audits itself.**

**Glasshat** ingests a PDF pitch deck and a GitHub repo, runs a six-perspective AI panel against a 100-point evaluation rubric, and — on screen, in front of you — **catches its own biases mid-evaluation and corrects them in real time, in 3D**. It is an *artifact-ingesting evaluation pipeline + a live transparent fairness monitor*, **not a chatbot**.

> 📺 **Demo videos** *(uploaded at submission)* — one for each hackathon, same engine, different narration.
>
> - **Qdrant VSD demo** — the panel audits itself; vector-anchored score correction; 3D evaluation graph
> - **Rapid Agent / Arize demo** — agent consults Phoenix MCP mid-run, detects past drift, changes retrieval strategy live

**Status (2026-05-15)**: scaffold + architecture + GCP/Gemini verification + 7-spike technical validation **complete**. Renamed from `Panelyst` → `Glasshat` on 2026-05-14 (panel recommendation, see `docs/max-wins-plan.md` §6.1). Phase 1 implementation cleared to begin.

---

## The one-paragraph pitch

Glasshat takes a pitch deck and a codebase, runs a six-perspective agent panel (Six Thinking Hats — White facts / Red intuition / Yellow value / Black risk / Green creative / Blue synthesis), and scores against a fixed 17-item / 100-point BMAD rubric. **Every sub-score is grounded in vector-retrieved evidence** (Qdrant, hybrid dense + sparse) **and anchored to comparable past evaluations** drawn from a calibrated corpus. The novelty: a **triple-redundant audit loop** (Phoenix Online Eval LLM-as-judge + Phoenix Custom Evaluator + Black-hat counter-claim) that detects when a hat's score is inconsistent with its evidence depth; the Blue planner then **consults Arize Phoenix's MCP server at runtime** to retrieve past-drift statistics and a Qdrant **Recommendation API** call returns anti-pattern anchors. The score visibly self-corrects on screen; the 3D evaluation graph reshapes. **One engine, two demo narrations** for the Qdrant VSD and Rapid Agent / Arize hackathons respectively.

---

## About this submission (hackathon compliance disclosure)

**All code in this repository was authored during the hackathon period** (first commit 2026-05-13). The product is submitted to:

- **Qdrant "Think Outside the Bot" Hackathon** (Vector Space Day SF 2026) — submission deadline **2026-06-01 23:59 PT**, winners 2026-06-11. Submission via Google Form `https://forms.gle/YDQ2TDUi8MqS9Vx28`. **Qdrant Vector DB is load-bearing here**: six collections (`pitch_chunks`, `repo_chunks`, `techniques`, `bmad_criteria`, `past_evals`, `web_evidence`) are queried by every scoring decision via hybrid dense+sparse search with RRF fusion, Recommendation API, group-by aggregations, and Scalar Quantization. **No chatbots**: Glasshat's UI is two drop zones → plan card → live monitor → scored report → 3D graph → vector-search browse page.

- **Google Cloud Rapid Agent Hackathon** (Arize track, `rapid-agent.devpost.com`) — submission deadline **2026-06-11 14:00 PT**. **Powered by Gemini 3 + Google Cloud Agent Builder + Google ADK on Cloud Run**, integrating Arize Phoenix's MCP server at runtime for the **self-improvement loop**: the Blue planner queries Phoenix mid-evaluation, detects calibration drift, and changes its retrieval strategy live. Apache-2.0 license detectable in the GitHub About sidebar.

### Concept lineage disclosure

Glasshat's *methodology* — the Six Thinking Hats perspective decomposition, the BMAD 17-item / 100-point rubric, the 75 evaluation-technique taxonomy, the 3D evaluation graph — derives from **fairthon.com** (same team). That methodology is design/spec, not code. **No fairthon (or any prior project's) source code is reused here; every line in this repo is fresh, authored during the hackathon period.**

### Calibration corpus disclosure

Glasshat's `past_evals` Qdrant collection and Phoenix calibration experiment (`glasshat-calibration-v1`) are seeded from **524 public submissions to the Gemini 3 Hackathon** (Dec 2025 – Feb 2026, concluded, `gemini3.devpost.com` — public project gallery). The sample is stratified: all 24+ named winners (1 Grand Prize, 1 Second, 1 Third, 10 Honorable Mentions, plus ribbon-winners) + 500 random non-winners. Each project's public Devpost description, public GitHub repo metadata, and judged outcome (winner / non-winner) is used as **evaluation calibration data only**. No code or content from those submissions is reused in Glasshat.

### Stack distinction (per Rapid Agent competitive-restriction clause)

Arize and Qdrant occupy **orthogonal categories**: Arize Phoenix is the LLM-application observability and meta-evaluation layer (traces, span annotations, evaluator orchestration); Qdrant is the vector database for product memory (precedents, evidence chunks, techniques, rubric definitions, web evidence). They do not compete on capabilities; they co-operate on roles.

---

## What it does (the loop)

1. **Ingest** — PDF deck → Cloud Storage → parsed by Gemini multimodal → chunked. Repo URL → shallow clone → static heuristics + sampled code. Deck chunks and code chunks are embedded into Qdrant with **dense + sparse vectors** (hybrid retrieval, RRF fusion).
2. **Plan** — a **Blue orchestrator agent** (Google ADK on Cloud Run, registered with Agent Builder; Gemini 3.1 Pro with `thinking_level=high`) emits an inspectable evaluation plan: which of the six hats run, which of the 17 BMAD items, which techniques apply, retrieval budgets, rubric weights. The thinking-token trace is visible in the UI. **The user approves/edits the plan (human gate 1).**
3. **Run the panel** — six perspective sub-agents (ADK `ParallelAgent`) on Gemini 3 via Vertex AI: White (Gemini 3 Flash + Vertex Grounding with Google Search), Red, Yellow, Green, Black (Gemini 3.1 Pro, must cite precedent — enforced via ADK callback / Plugin), Blue synthesis. Each emits structured findings (claims + evidence refs + sub-scores via `responseSchema`), allowed to disagree.
4. **Audit (the wow moment)** — ADK `LoopAgent` with `max_iterations=2`:
   - **Detection** (triple-redundant): (1) Phoenix Online Eval LLM-as-judge auto-fires on every score span; (2) Phoenix Custom Python Evaluator runs in parallel as deterministic backup; (3) Black hat's counter-claim from session state.
   - **Consultation**: PhoenixConsultantAgent makes 4 parallel MCP calls — `get-experiment-by-id` (drift stats) + `get-span-annotations` (proof chain) + `get-dataset-examples` (anchor profiles) + Qdrant `recommend(positive, negative, strategy="average_vector")` (anti-pattern retrieval).
   - **Calibration**: ScoreCalibrationAgent applies `new_score = clip(predicted − 0.8 × mean_delta, anchor_p25, anchor_p75)` with ±2.0 cap. Signals exit via `escalate=True` on convergence.
5. **Score** — Blue synthesizes panel + audit findings and maps to the 17 BMAD items / 100 points via rubric-aware RAG over `bmad_criteria` + `techniques` + `past_evals` (group-by per outcome tier) + grounded evidence chunks. Every scored item carries ≥1 evidence ref.
6. **Report** — an immutable, signed run record (input hashes, repo SHA, rubric version, technique set, model versions, web-search snapshot, per-criterion score + evidence + precedent IDs, human overrides). Surfaces: scored report, 2D radar + 3D evaluation graph with 524-project anchor constellation, vector-search page, KO/EN i18n. **The user can override any final score with a reason (human gate 2)** — recorded as a Phoenix Annotation with `annotator_kind="HUMAN"` that feeds future-run calibration. Closes the loop.
7. **Observe** — every agent call, tool call, retrieval, and score is auto-traced into Phoenix via OpenInference auto-instrumentation; meta-eval metrics (inter-hat consistency, drift vs. precedent set, groundedness, rubric coverage) surface on the live monitoring dashboard.

## Why this is "an agent that does a task," not a chatbot

Glasshat takes inputs that aren't prompts (a PDF + a repo URL), **plans** (an inspectable plan object), **uses tools** (PDF parser, code grader, web-search grounding, Qdrant hybrid + Recommendation API, Phoenix MCP runtime introspection), **executes a multi-stage workflow autonomously** (Six hats in parallel + audit loop + scoring + grounding), **keeps the user in control** (plan approval + score override gates), and **produces an artifact** (signed evidence-grounded scored report + 3D graph + live trace + audit trail). There is no chat box anywhere in the product.

---

## Stack

| Layer | Choice | Notes |
|---|---|---|
| Intelligence | **Gemini 3 on Vertex AI** — 3.1 Pro (Blue, Black) · 3 Flash (White, Red, Yellow) · 3.1 Flash-Lite (code-grader; corpus seed via Batch) | `thinking_level` per agent tier · context caching (90% saved on rubric + hat prompts) · `responseSchema` strict |
| Agent runtime | **Google ADK on Cloud Run** | LoopAgent + ParallelAgent + Custom BaseAgent + MCPToolset (Stdio) + before/after model+tool callbacks + session state. Spike-validated 2026-05-15. |
| Agent registration | Google Cloud Agent Builder | Blue planner registered for partner-track compliance. |
| Partner MCP integration | **Arize Phoenix** (Cloud free tier / self-hosted fallback) | Phoenix MCP server (27 tools) via `npx @arizeai/phoenix-mcp@latest` over stdio. OpenInference auto-instrumentation. Online Evals + Custom Evaluators + Annotations API + Datasets + Experiments. |
| Vector DB | **Qdrant** | 6 collections, hybrid dense+sparse with RRF fusion (weighted), Recommendation API, group-by aggregations, Scalar Quantization on `past_evals`. |
| Document of record | **Firestore Native** | Run records, technique registry, users, audit trail. |
| Compute | **Cloud Run** + Cloud Run Jobs | `pipeline-orchestrator` service · `code-grader-job` |
| Ingest pipeline | **Cloud Storage** + **Eventarc** | |
| Web search | **Vertex AI Grounding with Google Search** | Citation snapshot visible in UI. |
| Auth | **Firebase Authentication** | Google sign-in. |
| Frontend | **Next.js on Cloud Run** | Report view · 3D graph (`react-three-fiber`) · live monitoring dashboard · vector-search page · KO/EN i18n · SSE-streamed progress with 800ms-paced audit beats. |

## The rubric (BMAD, 17 items / 100 points)

- **A. Problem Definition & Vision (25)** — A1 clarity (8) · A2 target users (5) · A3 differentiation (7) · A4 market impact (5)
- **B. Technical Design & Architecture (25)** — B1 stack fit (7) · B2 system design (6) · B3 scalability (6) · B4 feasibility (6)
- **C. Implementation & Code Quality (30)** — C1–C5
- **D. Documentation & Presentation (20)** — D1–D4

The rubric is a versioned external config (`packages/rubric/`), not LLM-improvised. The **75 evaluation techniques** live in a registry designed for all 75; the MVP populates a high-signal subset.

---

## Repo layout

```
glasshat/
├── apps/
│   ├── web/                       # Next.js — report view, 3D graph, monitoring dashboard, vector-search
│   └── api/                       # thin BFF if needed
├── services/
│   ├── ingest/                    # Cloud Run svc: PDF parse → chunk → Qdrant (hybrid)
│   ├── code-grader/               # Cloud Run job: clone repo → heuristics → sample → Qdrant
│   └── pipeline-orchestrator/     # ADK CustomAgent → BluePlanner → HatsPanel → AuditLoop → BMADScorer → Report
├── agents/                        # 6 hat agent definitions + audit-loop sub-agents
├── packages/
│   ├── rubric/                    # BMAD 17-item config + 75-technique registry
│   └── shared/                    # llm.py (Vertex adapter), qdrant.py (hybrid+recommend), phoenix.py
├── infra/                         # GCP IaC, Cloud Run configs, Eventarc
├── scripts/                       # seed-past-evals (Gemini 3 corpus 524 stratified), dev helpers
├── spikes/                        # 7 technical-validation spike scripts (all PASS as of 2026-05-15)
├── docs/
│   ├── architecture.md            # topology + agent graph + sequence diagrams
│   ├── max-wins-plan.md           # dual-submission winning thesis + decision log
│   ├── wow-moment-design.md       # audit-the-auditor 5-step feasibility design
│   ├── technical-apex-features.md # 33 APPLY + 9 STRETCH + 5 CUT advanced-feature decisions
│   ├── spike-results.md           # 7-spike validation results
│   └── gcp-setup.md               # verified GCP bootstrap + Gemini 3 panel
├── PLAN.md                        # engineering inventory (mirrored from umbrella tracker)
├── HANDOFF.md                     # session handoff
└── LICENSE                        # Apache-2.0
```

---

## Setup

### Prerequisites

- Python 3.12 (we use [uv](https://docs.astral.sh/uv/) for package management)
- Node 24 + npm/npx (Phoenix MCP runs via `@arizeai/phoenix-mcp` over stdio)
- A Google Cloud project with Vertex AI enabled, a service account JSON key (see `docs/gcp-setup.md` for the verified bootstrap recipe)
- Optionally: Docker (for production-style Phoenix self-hosting; not required for dev — Phoenix runs in-process via `px.launch_app()`)

### Running the spikes (recommended first step)

```bash
cd spikes/
uv sync
uv run python 01_spike_a_phoenix_mcp_smoke.py
uv run python 02_spike_b_adk_loop.py
# ... 03 through 07
```

All 7 spikes should print `[PASS]`. See `docs/spike-results.md` for what each validates.

### Running Glasshat (Phase 1 onward)

```bash
cp .env.example .env
# fill in GOOGLE_CLOUD_PROJECT, GOOGLE_APPLICATION_CREDENTIALS, etc.
# (see docs/gcp-setup.md for the verified configuration)

# Phase 1 commands will appear here once the orchestrator is built.
```

---

## Plan & status

- Engineering inventory: [`PLAN.md`](PLAN.md)
- Dual-submission winning thesis: [`docs/max-wins-plan.md`](docs/max-wins-plan.md)
- Audit-the-auditor wow moment design: [`docs/wow-moment-design.md`](docs/wow-moment-design.md)
- Advanced-feature decision matrix: [`docs/technical-apex-features.md`](docs/technical-apex-features.md)
- Spike validation results: [`docs/spike-results.md`](docs/spike-results.md)
- GCP bootstrap: [`docs/gcp-setup.md`](docs/gcp-setup.md)
- Architecture diagrams: [`docs/architecture.md`](docs/architecture.md)
- Session handoff: [`HANDOFF.md`](HANDOFF.md)

The product was scaffolded 2026-05-13 (compliant with both hackathons' "all code in period" rules) under the working name `Panelyst`; renamed to `Glasshat` on 2026-05-14 after a five-expert positioning-strategy panel (Porter, Christensen, Godin, Doumont, Drucker) recommended a more memorable, theatrical name aligned with the transparent-audit thesis. Git history is preserved; the prior `Two-Weeks-Team/WhyC` "While YC hires, we ship" project (different product, archived) is unrelated.

---

## License

[Apache License 2.0](LICENSE).
