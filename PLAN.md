<!-- Mirrored from Two-Weeks-Team/hackathon-submissions:projects/rapid-agent-hackathon/planning/whyc-fairthon-port-plan.md . The umbrella copy is the source of truth for planning; this is the in-repo copy. Repo name is 'panelyst' (the prior 'WhyC' name belonged to the now-archived 'While YC hires' project). -->

# WhyC — Plan (fairthon-port: GCP + Agent Builder + Arize + Qdrant) — dual-submit: Rapid Agent + Qdrant VSD

Recorded at KST: `2026-05-13`. Decisions locked by the user this session (see § "Decisions" below).

> Planning record — not a submission claim, not an official source capture. Official facts stay in `../sources/` (Rapid Agent) and the Qdrant VSD page (`https://try.qdrant.tech/hackathon-vsd`). Built from a 6-expert-team analysis (3 teams × 5 = leader + 3 specialists + 1 critic; reports archived in this session's transcript).

---

## Decisions (user, 2026-05-13)

1. **WhyC is rebuilt new** = a GCP-native re-implementation of **fairthon.com**'s fair multi-perspective evaluation system, using **the full feature set** for "optimal evaluation," and adding **transparent, fair, real-time monitoring** of the evaluation process as a new headline capability. (Supersedes the prior "While YC hires, we ship" product that occupied the `WhyC` repo.)
2. **Stack**: **Gemini on Vertex AI** + **Google Cloud Agent Builder** (Rapid Agent mandate) + **Arize** as the partner-MCP integration (Rapid Agent partner track) — Arize is the *evaluation-observability / real-time monitoring* layer, which is exactly the "transparent & fair monitoring" the user wants → load-bearing, not a checkbox. **Qdrant** is used additionally as the vector layer (Rapid Agent rules allow non-partner tech; Qdrant VSD *requires* Qdrant) — confirm no rule forbids it (it doesn't).
3. **Single project / single repo**, submitted **identically to both** Rapid Agent (`rapid-agent.devpost.com`, ~2026-06-11/12) and the Qdrant "Think Outside the Bot" VSD hackathon (~2026-06-01/02). Only the **demo video + the "necessity / purpose" framing** is re-cut per hackathon; the codebase, the architecture, the README core are the same.
4. **Time constraints are set aside** at the user's direction — proceed without timeline gating. (But the calendar still matters for ordering: **Qdrant June 1** is the earliest hard deadline — build for it first.)
5. (Related, same session) **SocialSeed.ing** → **Track 3 (Refactor for Marketplace & Gemini Enterprise)** confirmed — see `../../google-for-startups-ai-agents-challenge/planning/socialseed-agent-ideation.md`.

✅ **Qdrant compliance — resolved (web-verified 2026-05-13):** the Qdrant VSD build period is **already open**, so a **fresh repo started now** with all WhyC code authored from now → June 1 is in-period and compliant with *"all code created during the hackathon period (no previous projects)."* The *concept* lineage from fairthon (Six Hats, BMAD, 75 techniques, 3D graph) is non-code spec and is **disclosed in the README**. *"No chatbots"* is satisfied by construction (WhyC is an artifact-ingesting evaluation pipeline + a monitoring dashboard + a search/filter vector-browse page — no chat box anywhere). One caveat: do NOT branch the fresh repo off the old `Two-Weeks-Team/WhyC` ('While YC hires') or off fairthon, and don't copy their source — re-implement from scratch against the spec. Qdrant submission goes via the **Google Form `https://forms.hl.qdrant.tech/hackathon-vsd`**, not Devpost; the **earliest deadline of the three is Qdrant's June 1** → build Qdrant-first, freeze, then finalize Rapid Agent (~June 11/12).

---

## 1. Source-grounded constraints

| Area | Fact | Source |
|---|---|---|
| **Rapid Agent** mission | "Build a functional agent powered by **Gemini and Google Cloud Agent Builder** that integrates a **Partner Entity MCP server** to solve a real challenge." Move beyond chat; agent plans, uses tools, executes, keeps the user in control; demonstrate meaningful integration with ≥1 partner via MCP. | `../sources/devpost-extracted.json`, `../sources/challenge_overview.html` |
| Rapid Agent — submission | Hosted project URL · **public OSS repo with a LICENSE file detectable in the GitHub About section** · ~3-min demo video · selected challenge · Devpost form. | `../sources/devpost-extracted.json` |
| Rapid Agent — schedule | Submissions **May 5 – June 11, 2026 PDT** (≈ June 12 06:00 KST); judging Jun 22–Jul 6; winners Jul 13. **Official Rules not yet posted as of capture — re-check.** | `../sources/devpost-extracted.json` |
| Rapid Agent — prizes | $60k total; **partner tracks: Elastic, Arize, Dynatrace, Fivetran, GitLab, MongoDB** — per-partner 1st $5k / 2nd $3k / 3rd $2k. (**Arize** is our track.) Qdrant is **not** a partner. | `../sources/devpost-extracted.json` |
| Rapid Agent — judging | Technological Implementation · Design · Potential Impact · Quality of the Idea. | `../sources/devpost-extracted.json` |
| **Qdrant VSD** | "Think Outside the Bot" Virtual Hackathon, in the lead-up to **Vector Space Day San Francisco** (VSD = June 11, 2026). Theme: "Push the boundaries of vector search… no chatbots allowed!" **Build/registration period is ALREADY OPEN** (as of 2026-05-13). **Submission deadline: 2026-06-01 11:59 PM PT** (≈ 2026-06-02 ~15:59 KST). **Winners announced: 2026-06-11** at VSD SF + online. Eligibility: 18+, global (subject to local laws), Qdrant employees/families excluded. **Teams of 1–4.** Submission = a **GitHub repo (public OR private)** + **README.md** + a **demo video max 3 min** (Loom/YouTube/Dropbox/etc.) + code with basic comments. **"Qdrant Vector Database is required for submissions"** as a material part. **"All code must be created during the hackathon period (no previous projects allowed!)"** — and since the period is open now, WhyC code authored from now on is in-period and compliant. **"submissions that are only chatbots are not allowed. The focus is on creativity and new interactions with vector search systems that go beyond simple Q&A chatbots."** Judging: **functionality, originality, user experience.** Prizes: 1st **$5,000** / 2nd **$3,000** / 3rd **$2,000** + multiple "Best-in-Category" sponsor bonuses. **Submission platform: a Google Form — `https://forms.hl.qdrant.tech/hackathon-vsd`** (NOT Devpost). | `https://try.qdrant.tech/hackathon-vsd` (web-verified 2026-05-13) |
| **fairthon.com** (the capability being re-built) | AI-based **fair multi-perspective project evaluation**. Inputs: a **PDF pitch deck + a GitHub repo URL**. Pipeline: **Six Thinking Hats** = 6 parallel AI agents (White/facts·data, Red/intuition·emotion, Yellow/optimism·value, Black/critical·risk, Green/creative·alternatives, Blue/process·synthesis). **BMAD framework** scoring: 17 items, 100 pts, 4 categories — A. Problem & Vision (25: A1 clarity 8, A2 target users 5, A3 differentiation 7, A4 market impact 5), B. Tech Design & Architecture (25: B1 stack fit 7, B2 system design 6, B3 scalability 6, B4 feasibility 6), C. Implementation & Code Quality (30, C1–C5), D. Documentation & Presentation (20, D1–D4). **75 evaluation techniques.** A **Code Grader** (clones & analyzes the repo → B/C items), README analysis, **web-search RAG** (A3/B1/C3). Outputs: a scored report + a **3D evaluation graph** + **i18n** (incl. Korean SSE streaming). Orchestration: LangGraph, 6 LLM models. Current prod stack: FastAPI + MongoDB (Motor/GridFS) + Next.js (Vercel) + Supabase Auth. Positioning: "AI-based Due Diligence documentation — a defensible audit trail for decision-makers" (B2B/B2G; hackathon white-label is the cash cow). Planned-but-unbuilt: judge-invitation system. | `~/Documents/GitHub/fairthon/` (README, `docs/ai-evaluation-system.md`, `docs/bmad-framework-overview.md`, `docs/strategic-pivot-plan.md`, `docs/api-specification.md`) |

---

## 2. The concept (one paragraph)

**WhyC takes a pitch deck and a codebase, runs a six-perspective agent panel over them, scores them against a fixed 100-point rubric with every score grounded in retrieved evidence and anchored to comparable past projects — and does it all under a live, transparent monitoring surface that shows the evaluation happening, watches the evaluator for bias/inconsistency, and emits a signed audit trail.** It's an **agent that does a task** (ingest → plan → run tools → score → report), not a chatbot. Built on **Gemini + Google Cloud Agent Builder**; **Arize** is the real-time monitoring/observability layer over the agent's own work (the "is the evaluation fair?" answer); **Qdrant** is the memory layer (precedent retrieval, evidence grounding, derivative/duplicate detection, theme clustering, rubric-aware retrieval-augmented scoring). The novelty vs. fairthon: agentic re-platforming (Six Hats as autonomous Gemini agents under an Agent-Builder orchestrator using real tools), Qdrant-backed *scoring consistency* and *evidence receipts*, and the **transparent real-time fairness monitor** — fairthon scores in a vacuum and silently; WhyC scores against a corpus and shows its work, with the evaluator itself observed.

Why this fits **Arize** as the partner track: Arize is LLM-application observability + evaluation. WhyC's product *is* evaluation; the partner integration is "the evaluator is itself continuously observed and evaluated — every Hat call, retrieval, and score is traced into Arize; meta-eval metrics (inter-Hat consistency, drift vs. precedent, hallucination flags on the evaluator's own claims, calibration) run in Arize and surface on the monitoring dashboard." That's the rare case where the partner integration is the headline feature, not a bolt-on.

---

## 3. Architecture

### 3.1 Agentic system (Gemini + Agent Builder)

- **Inputs that aren't prompts**: a PDF deck + a repo URL. **Output that isn't a chat reply**: a signed scored report + a 3D evaluation graph + a live monitoring trace. → not a chatbot, by construction.
- **Blue = orchestrator/planner agent** (Agent Builder app): given the deck + repo metadata, emits an inspectable **plan object** (which Hats run, which BMAD items, which of the 75 techniques apply *to this submission*, web-search budget, code-grader depth, rubric weights). **Human gate 1: approve/edit the plan & weights.**
- **6 perspective sub-agents** (White / Red / Yellow / Black / Green / Blue-synthesis) — distinct Agent-Builder agents, each with its own instruction, its own retrieval scope, a structured output schema (`claims[] + evidence_refs[] + sub_scores{}`), and *allowed to disagree*. White is RAG-heavy (web search + Qdrant). Black is forced to cite a Qdrant precedent or a CVE. Green may be ungrounded but is flagged speculative. Blue runs last, reconciles disagreements, maps findings → the 17 BMAD items → 100 pts.
- **Deterministic tools (not agents)**: PDF parser; **repo ingester / Code Grader** (clone → static heuristics: tests present, CI status, license, secrets scan, dependency parse, structure score, README quality → B/C signals + sampled code chunks); **web-search RAG** (Vertex AI Grounding w/ Google Search); **Qdrant retrieval** (precedents, techniques, evidence chunks); **Arize tracer/eval** (every agent step + retrieval + score → Arize span; meta-eval metrics); 3D-graph renderer; report assembler.
- **Human gate 2: override any final item score with a reason** → recorded in the audit trail alongside the agent's original.
- The rubric is a **versioned external config**, not LLM-improvised. Every scored item must carry ≥1 `evidence_ref` or the report assembler rejects it.

### 3.2 Arize — the transparent, fair, real-time monitoring layer (partner integration)

- Every Hat agent call, every tool call, every retrieval, every score → an **Arize trace span** (OpenTelemetry → Arize, or Arize MCP server tool calls from the orchestrator).
- **Meta-evaluation metrics computed/displayed via Arize**: inter-Hat consistency on shared sub-scores; this evaluation's deviation vs. the precedent set (Qdrant) per criterion (the "calibration / fairness" signal); hallucination/groundedness check on the evaluator's own claims (does each claim trace to a real passage?); rubric-coverage completeness; per-Hat token/latency/cost.
- **The monitoring dashboard** (new vs. fairthon): a live view of the run — which Hat is active, what it's retrieving, in-flight sub-scores, the Arize fairness/consistency gauges, the audit trail building up, and a "why this score" drill-down. This *is* the "transparent and fair" deliverable; it's also a strong UX/originality artifact for the Qdrant judges and "Design" for the Rapid Agent judges.

### 3.3 Qdrant — load-bearing vector layer

- **Collections**: `pitch_chunks` (deck chunks, dense+sparse hybrid), `repo_chunks` (function-/doc-level code chunks), `techniques` (the 75-technique texts; designed for all 75, MVP populates ~20), `bmad_criteria` (17 criterion definitions), `past_evals` (one vector per (project, criterion) pair — structured summary + score + rationale), `web_evidence` (web-search result chunks per run).
- **The scoring function takes Qdrant retrievals as arguments**: criterion *Cn* is scored from `bmad_criteria[Cn]` + top-relevant `techniques` for *Cn* + top-k `past_evals` precedents for *Cn* + grounded evidence chunks → structured Gemini output. Delete Qdrant → scores become ungrounded opinions with no precedent anchor, no receipts, no consistency check.
- **Headline vector-native features (non-chatbot)**: ① **precedent retrieval** — "scoring consistency anchor": each criterion's score shown next to how comparable past projects scored and why ("on B3 you scored 4/6; Project-X scored 4/6 — 'single-region, no caching'; you're closest to Project-X"). ② **evidence grounding** — "show me the receipt": every sub-score links to the exact deck/code passage(s). ③ **rubric-aware retrieval-augmented scoring** (the plumbing for ① and ②). Secondary: **derivative/duplicate detection** across a cohort (catches shared codebases / re-submissions across multi-track hackathons — a nice honest wink). Add-on: **theme clustering** of a cohort → the 3D graph populated with real neighbors.
- **Bootstrap `past_evals`**: run the WhyC pipeline over 50–150 public Devpost past projects (decks + repos public) during the build; optionally seed with fairthon's exported historical evaluations (anonymized) if available. Every new run grows the corpus.

### 3.4 GCP service map

| Concern | Service |
|---|---|
| File upload | Cloud Storage (`whyc-uploads`, `whyc-reports`; signed URLs; `noindex`; TTL on reports) |
| Ingest trigger | Eventarc (GCS object-finalize → Cloud Run) |
| Agent pipeline (Blue planner + 6 Hats) | Cloud Run service `pipeline-orchestrator`; top-level agent registered in **Vertex AI Agent Builder**; Gemini Flash (cheap Hats) + Gemini Pro (Blue/synthesis + scoring) on **Vertex AI**; ADK agents where it tightens Agent Builder integration |
| Code Grader | Cloud Run Job `code-grader-job` (shallow clone, static heuristics, sampled code → Gemini scoring; facts → Firestore; code chunks → Qdrant) |
| Web-search RAG | Vertex AI Grounding with Google Search; results snapshotted into the run record + `web_evidence` |
| Datastore | **Firestore (Native)** — evaluation docs, run records, technique registry, users (serverless; doc shape matches the report; Qdrant owns similarity, Firestore owns the document of record) |
| Vector search | **Qdrant Cloud** (zero-ops MVP; self-host on Cloud Run/GKE later if budget) |
| Observability / fairness monitor | **Arize** (OTel/Arize SDK or Arize MCP server); the monitoring dashboard reads Arize + Firestore |
| Auth | Firebase Authentication (Google sign-in) |
| Frontend | Next.js on Cloud Run (or Firebase Hosting + Cloud Run backend) — report view, 3D graph (react-three-fiber), the live monitoring dashboard, SSE stream, i18n (next-intl) KO/EN |
| Streaming | SSE via Cloud Run (heartbeats; buffering off) |
| Secrets | Secret Manager (GitHub token, Qdrant key, Arize key, partner-MCP creds) |
| Report PDF | Cloud Run Job (headless render) — stretch; MVP = client print-to-PDF |

### 3.5 Textual architecture diagram

```
   USER ─ deck.pdf + repo URL ─► [Next.js: 2 drop zones · plan card · live monitor · 3D report]
     ▲  ① approve plan/weights      │ (Firebase Auth)
     │                              ▼
     │   GCS whyc-uploads ──(finalize)──► Eventarc ──► Cloud Run: ingest-svc
     │     └ PDF→text/figures (Gemini multimodal); chunk → Qdrant: pitch_chunks
     │                                                │
     │                                       Cloud Run Job: code-grader-job
     │                                         clone repo · static heuristics · CI status · sample code
     │                                         → facts→Firestore; code chunks→Qdrant: repo_chunks
     │                                                ▼
     │   ┌──────────────────────────────────────────────────────────────────────────────────┐
     │   │  Cloud Run: pipeline-orchestrator  ── top agent registered in AGENT BUILDER ──     │
     │   │                                                                                    │
     │   │   BLUE (planner) ──► plan object ──[① human approve]──► dispatches:                 │
     │   │     ├ WHITE (facts)  ─ Vertex Grounding (Google Search) ─┐                          │
     │   │     ├ RED (intuition)                                     │                         │
     │   │     ├ YELLOW (value)               all Hats query  ───────┼──► QDRANT               │
     │   │     ├ BLACK (risk)   ── must cite precedent / CVE         │   • techniques (rubric) │
     │   │     ├ GREEN (creative, may be ungrounded → flagged)       │   • past_evals (precedent)│
     │   │     └ BLUE (synthesis) ◄─ 5 Hats + precedent + evidence ──┘   • pitch/repo chunks    │
     │   │                                                                                     │
     │   │   BMAD scorer: 17 items × structured Gemini output, each prompt = bmad_criteria[Cn]  │
     │   │     + relevant techniques + precedent set + grounded evidence  (rubric-aware RAG)    │
     │   │   Evidence grounding: per sub-score → hybrid search pitch/repo chunks → attach passages│
     │   │                                                                                     │
     │   │   ░░ every Hat call · tool call · retrieval · score  →  ARIZE span ░░                │
     │   │   ░░ Arize meta-eval: inter-Hat consistency · drift-vs-precedent · groundedness ░░   │
     │   └──────────────────────────────┬──────────────────────────────────────────────────────┘
     │                                  ▼
     │   Firestore: run/{id}  (immutable audit record: input hashes, repo SHA, rubric v, technique set,
     │                          model versions, web snapshot, per-criterion score + evidence + precedent IDs,
     │                          ② human overrides + reasons)
     │                                  │
     │            ┌─────────────────────┼─────────────────────────────────┐
     │            ▼                     ▼                                 ▼
     │   live MONITOR dashboard   3D evaluation graph         report + evidence drill-down (KO/EN)
     └────────────┘  (reads Arize fairness gauges + Firestore run state, streaming)
```

---

## 4. fairthon feature inventory → WhyC coverage

| fairthon feature | WhyC implementation | MVP / deferred |
|---|---|---|
| PDF pitch-deck ingest | GCS → Eventarc → ingest-svc; Gemini multimodal parse; chunk → Qdrant `pitch_chunks` | MVP |
| GitHub repo ingest + clone + Code Grader (B/C items) | `code-grader-job`: shallow clone, ~15–20 static heuristics, sampled code → Gemini scoring; code chunks → Qdrant `repo_chunks` | MVP (subset of deep checks) |
| Six Thinking Hats (6 parallel agents) | 6 Agent-Builder agents; Blue orchestrator/synthesis; White RAG-heavy | MVP — all 6 wired; Red/Green "lite" first pass, full depth for the final submission |
| BMAD 17-item / 100-pt scoring | structured Gemini calls per category, rubric-aware RAG; scores → Firestore | MVP — full 17-item structure |
| 75 evaluation techniques | technique registry (designed for 75) + embedded in Qdrant `techniques`; agent retrieves the relevant ones per submission | partial MVP (registry + ~20 active); full 75 = content work |
| Web-search RAG (A3/B1/C3) | Vertex AI Grounding w/ Google Search; snapshot → run record + `web_evidence` | MVP |
| 3D evaluation graph | react-three-fiber, axes = BMAD category scores, neighbors plotted from `past_evals`; 2D radar fallback locked | MVP (2D guaranteed, 3D stretch-within-MVP) |
| i18n + Korean SSE streaming | SSE via Cloud Run; Gemini generates report in locale (KO/EN MVP) | MVP |
| Multi-model (6 in fairthon) | Vertex: Gemini Flash + Gemini Pro (2 tiers); pluggable interface; Gemini-first per Rapid Agent rules | partial MVP (2 Gemini tiers + pluggable) |
| Report export | Firestore doc → HTML; client print-to-PDF; server-side PDF job stretch | MVP (HTML + client PDF) |
| Auth (Supabase) | Firebase Authentication | MVP |
| Datastore (MongoDB) | Firestore (Native) | MVP |
| LangGraph orchestration | re-expressed via Agent Builder / ADK (don't carry LangGraph code — fresh build); or LangGraph-in-Cloud-Run as a transitional internal | MVP — Agent Builder is the runtime |
| "Due-diligence audit trail" positioning | the immutable Firestore run record + Qdrant evidence grounding = a defensible, comparable, signed audit trail | MVP — core, not optional |
| Judge-invitation system (Phase 2, unbuilt in fairthon) | out of scope; cohort features (duplicate detection, theme clustering) partly serve the same need | deferred |
| **NEW: transparent real-time fairness monitoring** | Arize tracing + meta-eval + the live monitor dashboard (see §3.2) | MVP — the headline new capability |

---

## 5. Dual submission — one project, two framings

- **One repo, one codebase, one architecture.** Submitted to **both** Rapid Agent and Qdrant VSD.
- **Re-cut per hackathon: the demo video + the "necessity / purpose" framing only.**
  - *Qdrant VSD video*: lead with the **vector-native** story — precedent retrieval as the scoring-consistency anchor, evidence grounding, derivative/duplicate detection across a cohort, theme clustering — and the **monitoring dashboard** as the originality/UX punch. Emphasize "no chatbot — an artifact-ingesting evaluation pipeline." Disclose the fairthon concept lineage + "all code authored during the hackathon period" in the README. (No partner-MCP framing needed; having Arize/Agent-Builder doesn't hurt.)
  - *Rapid Agent video*: lead with the **agentic** story — Gemini + Agent Builder orchestrator, six perspective sub-agents that plan / use tools / execute / keep the user in control (the two human gates), the **Arize MCP partner integration** as the transparent-monitoring layer (the agent that's observed and evaluated). Emphasize Potential Impact (every hackathon / accelerator / grant body needs defensible evaluation at scale) and Quality of the Idea. Hosted URL + LICENSE-in-About (Apache-2.0).
- **README**: a "Submitted to" section noting both hackathons + the concept lineage from fairthon.com + "all code in this repo authored during the hackathon period; no fairthon code reused."

---

## 6. MVP (the smallest genuinely-WhyC, runnable, demoable build)

Inputs: one PDF deck + one public GitHub (or GitLab) repo URL via the Next.js UI.
1. Upload → GCS → Eventarc → ingest-svc: PDF → text (Gemini multimodal) → chunk → Qdrant `pitch_chunks`.
2. `code-grader-job`: shallow clone, ~15–20 static heuristics, README quality, sample ≤40 code chunks → Qdrant `repo_chunks`; facts → Firestore.
3. Agent-Builder pipeline: Blue planner emits plan → **human approve** → 6 Hats (3 full + Blue synthesis MVP; Red/Green lite, all 6 wired) each call the tool bus (Qdrant precedent/grounding, Web-Search, Code-Grader facts) → **BMAD: all 17 items**, rubric-aware RAG path → evidence grounding pass → **human override gate** → immutable run record to Firestore.
4. **Arize**: every agent/tool/retrieval/score → trace; meta-eval metrics (consistency, drift-vs-precedent, groundedness) computed.
5. Outputs: SSE-streamed progress; the **live monitoring dashboard** (active Hat, retrievals, in-flight scores, Arize fairness gauges, audit trail building); the **scored report** (17-item BMAD table, 100-pt total, A/B/C/D breakdown, per-criterion precedent panel + evidence passages, override trail); **2D radar (guaranteed) + 3D cohort point-cloud (stretch)**; a first-class **vector-search page** ("find similar past projects" / "show evidence for this score" — search + filter chips, never a chat box); KO + EN.
6. Seed `past_evals` with ~50–150 public Devpost projects run through the pipeline.
7. Submission assets: README (lineage + "code authored in hackathon period" + setup + ADK/Agent-Builder + Arize + Qdrant explanation + architecture diagram inline), Apache-2.0 LICENSE at repo root, hosted URL (Cloud Run / Firebase + a "Try a sample" button with a packaged anonymized deck + small public repo), two ≤3-min videos (per §5).
- **Out of MVP**: full 75 techniques (registry + ~20), deep Code-Grader checks, 6-model support (2 Gemini tiers + pluggable), server-side PDF, judge-invite system, Cloud SQL, private-repo auth.

---

## 7. Risks & mitigations

| Risk | Mitigation |
|---|---|
| Qdrant "no previous projects / all code in the period" vs. "single project to both" | Repo's first commit postdates the Qdrant start date (confirm the date); all substantive commits in-window; README discloses fairthon as *concept* lineage, states no fairthon code reused; git history is the evidence — keep it clean, don't backdate/squash. Risk is "a judge subjectively dislikes the lineage" → mitigated by genuine in-window substance + load-bearing Qdrant + the new monitoring capability that fairthon doesn't have. |
| "It's a chatbot" (Qdrant disqualifier) | No chat box anywhere. UI = upload → plan card → run → report + 3D graph + monitoring dashboard + a search/filter vector-browse page. Language: "agentic evaluation pipeline," "multi-perspective analyzer." |
| Arize integration reads as a checkbox | It's the *transparent fairness monitoring* the product is about — Arize traces the evaluator and runs meta-eval; the monitoring dashboard is a headline UX surface; remove Arize → lose the "is the evaluation fair?" answer. |
| "Just fairthon on GCP — where's the new idea?" | (a) agentic re-platform: Six Hats as autonomous Gemini agents under an Agent-Builder orchestrator using real tools, not a LangGraph DAG; (b) Qdrant memory: precedent-anchored scoring + evidence receipts vs. fairthon's vacuum scoring; (c) the transparent real-time fairness monitor. Lead with all three. |
| Rapid Agent Official Rules not yet posted | Don't commit irreversibly; re-validate when posted (esp. any "new code" clause, the precise "Partner Entity MCP" definition, eligibility, hosted-URL public/no-login). |
| `past_evals` empty on day one | Seed from 50–150 public Devpost projects (a few hours of batch on the $100/$500 credit); optionally fairthon's exported history; corpus compounds with each run; degrades gracefully to "no comparable precedents yet" (an honest UX state). |
| GCP service sprawl | MVP critical path = 3 Cloud Run units (web, pipeline-orchestrator, code-grader-job) + GCS + Eventarc + Firestore + Vertex Gemini + Qdrant Cloud + Arize + Secret Manager + Firebase Auth. Pub/Sub optional. All serverless. |
| Eligibility (age/territory; VSD-SF in-person/US-residency for prizes?) | Confirm for every team member before committing; keep the submitting team ≤4 (Qdrant cap). |

---

## 8. Open items / confirmations needed

1. **Confirm the Qdrant VSD hackathon START date** + the exact "no previous projects" wording (gates when the repo's first commit must land).
2. **Confirm Rapid Agent Official Rules** once posted (new-code clause? "Partner Entity MCP" exact meaning? eligibility/territory? hosted-URL public-no-login?).
3. **Repo name / slug** — keep `WhyC` (now meaning the fairthon-port), or a new name? GCP project name? Billing owner? Apache-2.0 confirmed.
4. **What happens to the existing `~/Documents/GitHub/WhyC/` "While YC hires" code** — retire / archive / repurpose? (It's superseded as "WhyC.")
5. **fairthon historical-evaluation export** (anonymized) to seed `past_evals` — available?
6. **Arize plan/access** (Arize AX / Phoenix; MCP server availability) + does the Rapid Agent partner program require a specific Arize onboarding?
7. **Team-of-record** on each Devpost (≤4 for Qdrant; "team" vs "contributor").
8. **Frontend hosting** (Cloud Run vs Firebase Hosting + Cloud Run backend); **Qdrant Cloud vs self-hosted** — pick.
9. **3D graph** must-demo vs nice-to-have (2D radar fallback is locked).

---

## 9. Next work

1. Confirm the § 8 items (esp. Qdrant start date, Rapid Agent rules, repo name, Arize access).
2. Create the repo (fresh; first commit dated for Qdrant compliance), Apache-2.0, README skeleton w/ lineage + "code authored in hackathon period", `.env.example`, `HANDOFF.md`.
3. Stand up the GCP project + Vertex AI + Agent Builder + Cloud Run + Firestore + Eventarc + Secret Manager + Firebase Auth; redeem the $500 challenge credits; provision Qdrant Cloud + Arize.
4. Build the ingest path (GCS → Eventarc → ingest-svc → Gemini parse → Qdrant), the `code-grader-job`, the Firestore run-record schema.
5. Build the Agent-Builder pipeline: Blue planner + plan card + human gate 1; the 6 Hat agents (3 full + synthesis MVP); the rubric-aware RAG scorer over `bmad_criteria` + `techniques` + `past_evals` + grounded chunks; the evidence-grounding pass; human gate 2.
6. Wire **Arize** tracing on every agent/tool/retrieval/score + the meta-eval metrics; build the **live monitoring dashboard**.
7. Build the report view (17-item BMAD table, precedent panels, evidence drill-down, override trail), the 2D radar + 3D graph, the vector-search page, i18n (KO/EN), SSE streaming.
8. Seed `past_evals` (50–150 public Devpost projects).
9. Hosted URL + "Try a sample" button + LICENSE-in-About; record the two ≤3-min videos (Qdrant-framed and Rapid-Agent-framed); README + architecture diagram; Devpost forms for both.
10. Submit to Qdrant VSD (~Jun 1/2) first, freeze; then finalize the Rapid Agent submission (~Jun 11/12).
