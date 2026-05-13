# Panelyst

> An **agentic fair-evaluation panel.** Give it a pitch deck (PDF) and a codebase (repo URL); it runs a **six-perspective AI panel**, scores the project against a fixed **100-point rubric** with **every score grounded in retrieved evidence** and **anchored to comparable past projects** — all under a **live, transparent fairness monitor**. It is an *evaluation pipeline*, **not a chatbot**.

**Status: scaffold only (2026-05-13).** Architecture and plan below; implementation begins next.

---

## Hackathon context (read this first)

This repository is built for, and **submitted to, two hackathons** with the same codebase (only the demo video / framing differs per event):

1. **Qdrant "Think Outside the Bot" Hackathon** (Vector Space Day San Francisco) — submission deadline **2026-06-01 23:59 PT**, winners 2026-06-11. Submission via the Google Form `https://forms.hl.qdrant.tech/hackathon-vsd`. Qdrant Vector DB is a mandatory, material part of the project; **no chatbots**; **all code in this repository was authored during the hackathon period (no previous projects).**
2. **Google Cloud Rapid Agent Hackathon** (`rapid-agent.devpost.com`) — submission deadline ~2026-06-11/12. An agent powered by **Gemini + Google Cloud Agent Builder** that integrates a **partner-entity MCP server** (here: **Arize**, the evaluation-observability layer that powers the transparent real-time fairness monitor); hosted project URL + this public OSS repo with a LICENSE detectable in the About section + a ~3-min demo video.

**Concept lineage disclosure:** Panelyst's *methodology* — the Six Thinking Hats perspective decomposition, the BMAD 17-item / 100-point rubric, the 75 evaluation-technique taxonomy, the 3D evaluation graph — derives from **fairthon.com** (same team). That methodology is design/spec, not code. **No fairthon (or any prior project's) source code is reused here; everything in this repo is fresh, authored during the hackathon period.**

---

## What it does (the loop)

1. **Ingest** — a PDF pitch deck (→ Cloud Storage → parsed by Gemini multimodal → chunked) and a repo URL (→ shallow clone → static heuristics + sampled code). Deck chunks and code chunks are embedded into **Qdrant**.
2. **Plan** — a **Blue orchestrator agent** (on Google Cloud Agent Builder) emits an inspectable evaluation plan: which of the six hats run, which of the 17 BMAD items, which of the 75 techniques apply *to this submission*, the web-search budget, the code-grader depth, the rubric weights. **The user approves/edits the plan (human gate 1).**
3. **Run the panel** — six perspective sub-agents (White facts·data / Red intuition / Yellow value / Black risk / Green alternatives / Blue synthesis) on **Gemini via Vertex AI**, each with its own retrieval scope, each emitting structured findings (claims + evidence refs + sub-scores), allowed to disagree. White is web-search-grounded (Vertex AI Grounding with Google Search). Black must cite a Qdrant precedent or a CVE. The **Code Grader** feeds hard metrics (tests present, CI status, license, secrets scan, structure, README quality).
4. **Score** — Blue synthesizes the panel's findings and maps them to the 17 BMAD items / 100 points. Each criterion is scored via **rubric-aware retrieval-augmented scoring**: the prompt is assembled from the criterion definition + the relevant techniques + the top-k comparable past evaluations (Qdrant `past_evals`) + the grounded evidence chunks. Every scored item must carry ≥1 evidence ref.
5. **Ground** — for every sub-score, hybrid-search the deck/code chunks and attach the exact justifying passages.
6. **Report** — an immutable, signed run record (input hashes, repo SHA, rubric version, technique set, model versions, web-search snapshot, per-criterion score + evidence + precedent IDs, plus any human overrides). Surfaces: the **scored report** (17-item BMAD table, 100-pt total, A/B/C/D breakdown, per-criterion precedent panel + evidence drill-down), a **2D radar + 3D evaluation graph** (with comparable past projects plotted as neighbors), a first-class **vector-search page** ("find similar past projects" / "show evidence for this score" — search + filter, never a chat box), and **i18n** (Korean + English, SSE-streamed). **The user can override any final score with a reason (human gate 2)** — recorded alongside the agent's original.
7. **Monitor (the headline new capability)** — every agent call, tool call, retrieval, and score is traced into **Arize**; Arize-computed meta-evaluation metrics (inter-hat consistency, deviation vs. the precedent set per criterion = the "fairness/calibration" signal, groundedness of the evaluator's own claims, rubric coverage, per-hat latency/cost) surface on a **live monitoring dashboard** that shows the evaluation happening and watches the evaluator itself. *fairthon scores in a vacuum and silently; Panelyst scores against a corpus and shows its work.*

## Why this is "an agent that does a task," not a chatbot

It takes inputs that aren't prompts (a PDF, a repo), it **plans** (an inspectable plan object), it **uses tools** (PDF parser, repo/Code-Grader, web-search, Qdrant retrieval, Arize tracer), it **executes a multi-stage workflow autonomously**, it **keeps the user in control** (two designed human checkpoints — approve the plan, override scores), and it **produces an artifact** (a signed, evidence-grounded scored report + a 3D graph + a live trace). There is no chat box anywhere in the product.

## Stack

| Layer | Choice |
|---|---|
| Intelligence | **Gemini on Vertex AI** (Flash for the cheap hats, Pro for synthesis + scoring) — *not* AI Studio (not credit-eligible for Rapid Agent) |
| Agent orchestration | **Google Cloud Agent Builder** (+ ADK where it tightens integration) |
| Partner integration / monitoring | **Arize** — evaluation-observability over the agent's own work; powers the transparent real-time fairness monitor |
| Vector memory (REQUIRED for Qdrant hackathon, load-bearing here) | **Qdrant** — collections: `pitch_chunks`, `repo_chunks`, `techniques`, `bmad_criteria`, `past_evals`, `web_evidence`; hybrid dense+sparse on the chunk collections |
| Document of record | **Firestore (Native)** — evaluation docs, run records, technique registry, users |
| Compute | **Cloud Run** (web, `pipeline-orchestrator`) + **Cloud Run Jobs** (`code-grader`, report render) |
| Ingest pipeline | **Cloud Storage** + **Eventarc** |
| Web search | **Vertex AI Grounding with Google Search** |
| Auth | **Firebase Authentication** |
| Frontend | **Next.js** (report view, 3D graph via react-three-fiber, the live monitoring dashboard, the vector-search page; i18n KO/EN; SSE) |

## The rubric (BMAD, 17 items / 100 points)

- **A. Problem Definition & Vision (25)** — A1 clarity (8), A2 target users (5), A3 differentiation (7), A4 market impact (5)
- **B. Technical Design & Architecture (25)** — B1 stack fit (7), B2 system design (6), B3 scalability (6), B4 feasibility (6)
- **C. Implementation & Code Quality (30)** — C1–C5
- **D. Documentation & Presentation (20)** — D1–D4

The rubric is a versioned external config (`packages/rubric/`), not LLM-improvised; the **75 evaluation techniques** live in a registry designed for all 75 (the MVP populates a high-signal subset).

## Repo layout

```
panelyst/
├── apps/
│   ├── web/                       # Next.js — report view, 3D graph, live monitoring dashboard, vector-search page, i18n
│   └── api/                       # thin BFF if needed
├── services/
│   ├── ingest/                    # Cloud Run svc: PDF parse → chunk → Qdrant
│   ├── code-grader/               # Cloud Run job: clone repo → static heuristics → sample code → Qdrant
│   └── pipeline-orchestrator/     # Agent Builder app: Blue planner + 6 hat agents + BMAD scorer + Arize tracing
├── agents/                        # the six Thinking-Hat agent definitions + the orchestrator
├── packages/
│   ├── rubric/                    # BMAD 17-item config + 75-technique registry
│   └── shared/                    # shared types/schemas
├── infra/                         # GCP IaC, Cloud Run configs, Eventarc
├── scripts/                       # seed-past-evals (from public Devpost projects), dev helpers
├── docs/                          # architecture diagram, ADRs
├── PLAN.md                        # the full plan (mirrored from the umbrella tracker)
├── HANDOFF.md                     # session handoff
└── LICENSE                        # Apache-2.0
```

## Plan & status

Full plan: [`PLAN.md`](PLAN.md). Tracking: [`Two-Weeks-Team/hackathon-submissions`](https://github.com/Two-Weeks-Team/hackathon-submissions) → `projects/rapid-agent-hackathon/planning/whyc-fairthon-port-plan.md`. (This repo was scaffolded 2026-05-13; it occupies what the tracker calls the "WhyC fairthon-port" slot — the prior `Two-Weeks-Team/WhyC` "While YC hires, we ship" project has been archived.)

## License

[Apache License 2.0](LICENSE).
