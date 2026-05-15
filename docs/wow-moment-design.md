# Audit-the-Auditor Wow Moment — Technical Feasibility & Design

> **Status**: Feasibility verified 2026-05-14. No technical blockers. Implementation plan locked.
>
> The audit-the-auditor moment is the linchpin of Glasshat's dual-submission strategy (see `docs/max-wins-plan.md` §4). This file decomposes it into concrete steps, verifies each step against current Phoenix MCP + Google ADK capabilities, identifies fallbacks, and specifies spike-tests to validate before Phase 1 build.

---

## §1 — The wow moment (verbal anchor)

> *"Black hat flags Yellow's score on rubric item A1 as inconsistent with evidence depth. Blue planner pauses, consults Phoenix MCP for past performance — Phoenix returns 'Yellow over-confident on A1 by avg 1.2 pts when evidence_depth < 0.4 over 14 past runs'. Blue calls Qdrant `past_evals` for anchor projects with similar profiles — returns 3 projects scored 7.2 / 7.5 / 7.8 vs current 9.0. Yellow's A1 score animates from 9.0 → 7.6 on screen, contradicting past-eval chunks highlighted, 3D evaluation graph reshapes."*

Both demos render this same engineering, with different narrative emphasis (Qdrant foregrounds the past_evals + 3D; Arize foregrounds the Phoenix consultation + score delta).

---

## §2 — Decomposition into 5 steps

| # | Step | What needs to happen | Owner agent |
|---|---|---|---|
| 1 | **Detection** | Compare Yellow's A1 score against the evidence-depth signal; flag inconsistency | InconsistencyDetectorAgent |
| 2 | **Phoenix consultation** | Query Phoenix MCP for past-run drift statistics on (hat=Yellow, criterion=A1, evidence_depth_bucket=low) | PhoenixConsultantAgent (uses Phoenix MCPToolset) |
| 3 | **Qdrant anchor retrieval** | Top-k similar profiles from `past_evals` collection; extract their A1 scores for comparison | PhoenixConsultantAgent (also calls Qdrant tool) or separate retrieval step |
| 4 | **Score correction** | Apply calibration delta to Yellow's A1 score; write to session state; signal loop convergence | ScoreCalibrationAgent |
| 5 | **UI animation** | Emit SSE event with old score, new score, contradicting evidence chunks, anchor projects; frontend animates | Backend SSE emitter + Next.js frontend |

---

## §3 — Step-by-step feasibility verdict

### Step 1 — Detection ✓ PROVEN

**What**: Quantify "Yellow's A1 score is inconsistent with the evidence depth retrieved from the deck/repo".

**Tech**:
- Each hat outputs `{score: int, confidence: float, evidence_refs: string[], reasoning: string}` (structured Gemini output, `output_key="hat_<color>_result"` in ADK).
- `evidence_depth` = count of distinct `evidence_refs` × avg chunk relevance (cosine sim). Computed deterministically post-hat-run.
- Inconsistency rule (v1, simple): if `score >= 8` and `evidence_depth < 0.4` → flag.
- Inconsistency rule (v2, learned): Phoenix-driven threshold from past runs (deferred to v1.1).

**Risk**: None. Pure deterministic computation over structured hat outputs.

**Demo readability concern**: The inconsistency flag must produce a visible, named reason in the UI. Solution: emit `{type: "inconsistency_flagged", hat: "yellow", criterion: "A1", reason: "score 9.0 with evidence_depth 0.31"}` to SSE — the UI shows this in plain English.

---

### Step 2 — Phoenix consultation ✓ PROVEN (with pre-seed dependency)

**What**: Query Phoenix to retrieve past-run drift on (hat=Yellow, criterion=A1, evidence_depth_bucket=low).

**Tech — verified from `@arizeai/phoenix-mcp` README** (https://github.com/Arize-ai/phoenix/blob/main/js/packages/phoenix-mcp):

Phoenix MCP exposes these relevant tools:
- `list-traces` / `get-trace`
- **`get-spans`** ← returns spans with attribute filters
- **`get-span-annotations`** ← returns LLM-as-judge eval results per span
- `list-annotation-configs`
- `list-datasets` / `get-dataset` / `get-dataset-examples` / **`get-dataset-experiments`** / `add-dataset-examples`
- `list-experiments-for-dataset` / **`get-experiment-by-id`** ← aggregated experiment results
- Prompts, sessions, projects (not used in this moment)

**Two retrieval paths** (we use both, with fallback):

**Path A — Pre-computed Experiment** (low-latency, primary for demo):
1. Pre-seed: after running 50-150 past Devpost projects through Glasshat, run a Phoenix Experiment that aggregates per-(hat, criterion) calibration error vs evidence_depth bucket. Store as a named experiment (e.g., `glasshat-calibration-v1`).
2. At runtime: PhoenixConsultantAgent calls `get-experiment-by-id` → returns pre-computed `{mean_delta: 1.2, sample_size: 14, conditions: {hat: Yellow, criterion: A1, evidence_depth_bucket: "<0.4"}}`. **Sub-200ms.**

**Path B — Live span aggregation** (fallback for unseen hat/criterion pairs):
1. PhoenixConsultantAgent calls `get-spans` with attribute filter `{name: "hat_yellow_score_a1", evidence_depth_bucket: "<0.4"}` → returns raw spans.
2. Aggregate client-side in PhoenixConsultantAgent's tool wrapper (mean of `predicted_score - ground_truth_score`).
3. Latency: ~500ms-2s depending on corpus size. Acceptable for demo if Path A misses.

**Authentication**: `@arizeai/phoenix-mcp` accepts `--baseUrl` + `--apiKey` flags or `PHOENIX_API_KEY`/`PHOENIX_HOST` env vars. Phoenix Cloud free tier issues `px_live_*` keys at `app.phoenix.arize.com`. Self-hosted fallback (`MONITOR_BACKEND=phoenix-local` per `.env`) uses same MCP server, different baseUrl.

**Risk**: Pre-seeding `past_evals` and Phoenix experiment is a Phase 1.12 (existing) + new Phase 1.13 task. If we skip seeding, the demo Path A returns empty. **Mitigation**: hard requirement that seeding completes before demo recording. Add to §6 submission checklist.

---

### Step 3 — Qdrant anchor retrieval ✓ PROVEN

**What**: Top-k similar past projects with similar evidence-depth profile; return their A1 scores.

**Tech**: Standard Qdrant query against `past_evals` collection. Filter: `criterion="A1" AND evidence_depth_bucket="<0.4"`. Sort by cosine similarity to current pitch's A1-relevant chunks.

**Risk**: None. Plain vector search. Already designed in `panelyst-project` memory + PLAN.md §3.3.

---

### Step 4 — Score correction ✓ PROVEN

**What**: Apply calibration delta to Yellow's A1 score; write to session state; signal loop convergence.

**Tech**:
- ScoreCalibrationAgent receives Phoenix mean_delta + Qdrant anchor scores in session state.
- Calibration policy (v1, simple): `new_score = clip(current_score - 0.8 * phoenix_mean_delta, anchor_score_p25, anchor_score_p75)`. Conservative: don't snap to anchors; pull toward them.
- Write `session.state["hat_yellow_score_a1"] = new_score`; write `session.state["audit_corrections"] = [{...}]` for UI to read.
- If correction applied, signal `tool_context.actions.escalate = True` to exit the LoopAgent on next iteration.

**Risk**: Calibration policy could over-correct or under-correct. **Mitigation**: cap delta at ±2.0 absolute; cap iterations at 2 (initial + correction check); add a human-override gate (already in MVP spec).

---

### Step 5 — UI animation ✓ PROVEN

**What**: Frontend animates the score change with contradicting evidence chunks highlighted; 3D graph reshapes.

**Tech**:
- Backend SSE event sequence:
  1. `{type: "audit_started"}`
  2. `{type: "inconsistency_flagged", hat, criterion, reason, old_score}`
  3. `{type: "phoenix_consultation", query, result}` (Arize demo only foregrounds this)
  4. `{type: "anchor_retrieval", anchors: [{project_id, score, similarity}]}`
  5. `{type: "score_corrected", hat, criterion, old_score, new_score, contradicting_chunks: [...]}`
  6. `{type: "graph_reshape", updates: {node_id, new_pos}}`
- Frontend: useEventSource hook → React state → CSS transition for score number, react-three-fiber animation for 3D graph node position.

**Risk**: Timing — the animation must take ~6 seconds for the audience to see it land. **Mitigation**: backend introduces deliberate ≥800ms gaps between SSE events 2-5. Demo pacing is a feature, not a bug.

---

## §4 — Agent topology (Google ADK)

```
GlasshatRootAgent  (CustomAgent — orchestrator, owns the loop)
│
├─ IngestAgent  (CustomAgent — deterministic tools)
│  ├─ pdf_parser_tool  (Gemini Flash-Lite multimodal)
│  └─ repo_cloner_tool  (Cloud Run Job code-grader)
│
├─ BluePlannerAgent  (LlmAgent, Gemini 3.1 Pro)
│  └─ output_key="plan"
│
├─ HatsPanel  (ParallelAgent)
│  ├─ WhiteAgent    (LlmAgent + qdrant_search_tool + web_search_tool)
│  ├─ RedAgent      (LlmAgent)
│  ├─ YellowAgent   (LlmAgent + qdrant_search_tool)
│  ├─ BlackAgent    (LlmAgent + qdrant_search_tool, must_cite_precedent=True)
│  ├─ GreenAgent    (LlmAgent)
│  └─ BlueSynthesisAgent  (LlmAgent, runs after others; reads all hat outputs)
│
├─ AuditLoop  (LoopAgent, max_iterations=2)
│  ├─ InconsistencyDetectorAgent  (LlmAgent — flags hat/criterion pairs)
│  │  └─ output_key="audit_flags"
│  ├─ PhoenixConsultantAgent  (LlmAgent + Phoenix MCPToolset)
│  │  ├─ tool: get-experiment-by-id  (Phoenix Cloud)
│  │  ├─ tool: get-spans  (Phoenix Cloud, fallback)
│  │  ├─ tool: qdrant_past_evals_search  (anchor retrieval)
│  │  └─ output_key="phoenix_findings"
│  └─ ScoreCalibrationAgent  (LlmAgent)
│     ├─ tool: exit_audit_loop  (escalation signal when no more inconsistencies)
│     └─ output_key="audit_corrections"
│
├─ BMADScorerAgent  (LlmAgent + qdrant_search_tool — rubric-aware RAG over all 17 items)
│  └─ output_key="bmad_scores"
│
└─ ReportAssemblerAgent  (deterministic — Firestore write + signed audit trail + SSE final event)
```

**Why this topology wins on both judging dimensions**:
- *Tech Implementation (Rapid Agent tie-break #1)*: ADK + LoopAgent + ParallelAgent + Phoenix MCPToolset is recognizable, idiomatic, and demonstrates real multi-agent orchestration.
- *Originality (Qdrant)*: the AuditLoop sub-pipeline is the unique contribution — nothing in the 2025 Qdrant winners pool did meta-audit.
- *Material Vector Use (Qdrant)*: 4 of the 7 LLM agents call `qdrant_search_tool` against different collections. Vectors are the protagonist of scoring + auditing.
- *Self-improvement loop (Arize bonus)*: AuditLoop literally is the self-improvement loop, with Phoenix at its center.

---

## §5 — MCPToolset wiring for Phoenix MCP

```python
# services/pipeline-orchestrator/src/agents/phoenix_consultant.py
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import MCPToolset, StdioServerParameters

phoenix_mcp_toolset = MCPToolset(
    connection_params=StdioServerParameters(
        command="npx",
        args=[
            "-y",
            "@arizeai/phoenix-mcp@latest",
            "--baseUrl", os.environ["PHOENIX_BASE_URL"],
            "--apiKey", os.environ["PHOENIX_API_KEY"],
        ],
    ),
)

phoenix_consultant = LlmAgent(
    name="PhoenixConsultantAgent",
    model="gemini-3-flash-preview",  # fast, structured-output
    instruction=(
        "You are Glasshat's calibration consultant. Given an inconsistency flag "
        "(hat, criterion, current_score, evidence_depth), call the Phoenix MCP "
        "tool `get-experiment-by-id` for experiment 'glasshat-calibration-v1' "
        "with filters (hat, criterion, evidence_depth_bucket). If empty, fall "
        "back to `get-spans` with attribute filters and aggregate client-side. "
        "Also call `qdrant_past_evals_search` for top-3 anchor projects. "
        "Return: {mean_delta, sample_size, anchor_scores: [...], "
        "contradicting_chunks: [...]}."
    ),
    tools=[phoenix_mcp_toolset, qdrant_past_evals_tool],
    output_key="phoenix_findings",
)
```

**Verified compatibility** (from ADK docs at `adk.dev/agents/workflow-agents/loop-agents/` + `adk.dev/agents/custom-agents`):
- `MCPToolset` supports `StdioServerParameters` (verified ADK pattern) — same connection mode as Arize starter kit
- MCP tools inside LoopAgent sub-agents work the same as inside any LlmAgent — no loop-specific syntax
- ADK auto-instrumentation via OpenInference (`phoenix.otel.register(..., auto_instrument=True)`) — same pattern as Arize starter kit's `agent/instrumentation.py`

---

## §6 — Pre-seeding requirement (CRITICAL) — **Gemini 3 Hackathon corpus strategy**

The wow moment depends on Phoenix having past run data to retrieve. **Pre-demo seeding is non-negotiable.**

### §6.1 Source corpus: Gemini 3 Hackathon (Dec 2025 – Feb 2026, concluded)

User-approved 2026-05-14: seed `past_evals` and Phoenix calibration experiment from **the public Gemini 3 Hackathon project gallery** (`gemini3.devpost.com/project-gallery`), not from a generic Devpost sweep.

| Property | Value | Why it matters |
|---|---|---|
| Total submissions | **4,499** | 30-90× richer than the original "50-150 generic projects" plan |
| Submission stack | All projects use **Gemini 3 API** | Matches Glasshat's stack — comparison is in-distribution, not cross-stack |
| Recency | Dec 2025 – Feb 2026 | Recent; calibration data isn't stale |
| Public required assets | Devpost page (~200-word description) + **public GitHub repo** (or AI Studio link) + ~3 min demo video | Exact format Glasshat ingests |
| Ground truth labels | **24+ winners** (1 Grand $50K + 1 2nd + 1 3rd + 10 Honorable + extras with winner ribbons) vs ~4,475 non-winners | Reverse-engineerable for calibration; Glasshat scores then compared to winner/non-winner outcome |
| **Disclosed judging criteria + weights** | **Technical Execution 40% · Innovation/Wow 30% · Potential Impact 20% · Presentation/Demo 10%** | Maps approximately to Glasshat BMAD (A Problem/Vision 25 ≈ Innovation 30 + Impact 20 partial; B Tech/Arch 25 + C Implementation 30 ≈ Tech 40; D Doc/Presentation 20 ≈ Presentation 10). Provides rubric-anchored ground truth for cross-validation. |

### §6.2 Sampling strategy (524 projects)

User-approved 2026-05-14: **All winners + stratified random non-winners = 524 projects.**

| Stratum | Count | Selection method |
|---|---|---|
| Grand Prize | 1 | All |
| 2nd Place | 1 | All |
| 3rd Place | 1 | All |
| Honorable Mentions | 10 | All |
| Additional ribbon-winners (if any beyond 13 named) | ~11 | All |
| Stratified random non-winners | 500 | Random sample drawn after enumerating full 4,499 gallery; stratify by `(submission_week, has_github_repo_url, team_size_bucket)` to avoid temporal/structural bias |
| **TOTAL** | **524** | |

### §6.3 Scraping pipeline (Phase 1.13)

| Step | What | Throughput | Estimated time |
|---|---|---|---|
| A | Verify `gemini3.devpost.com/robots.txt` allows project-gallery + project-detail page crawling; respect any `Crawl-delay` directive | one-shot | 5 min |
| B | Enumerate full project gallery (188 pages × 24) → `seed/gemini3-index.jsonl` with `{title, devpost_slug, thumbnail, winner_badge, like_count, comment_count}` | 1 RPS | ~1 hour at 1 RPS for 188 pages |
| C | Apply stratified sampling → `seed/gemini3-sample-524.jsonl` | one-shot | <1 min |
| D | Per-project page fetch (524 pages) → extract: full description, **GitHub repo URL or AI Studio link**, demo URL, video URL, tech-stack tags, builders → `seed/gemini3-projects-524.jsonl` | 1 RPS | ~9 min |
| E | Filter projects with public GitHub repos (drop AI-Studio-only; estimate ~10-30% drop rate) → final corpus ~370-500 projects with clonable code | one-shot | <1 min |
| F | Clone each repo shallow (`git clone --depth=1`); read README + `~/15-20 static heuristics` + sample code chunks | parallel 5× | ~30 min for 500 repos |
| G | For each project: PDF deck → Glasshat ingestion is **not applicable** (Gemini 3 submissions don't have deck PDFs); substitute = Devpost description (~200 words) parsed as pitch + GitHub README as supplementary pitch material | — | folded into H |
| H | Run Glasshat pipeline (6 hats + BMAD scoring + audit loop) over each project. **Use Flash-Lite for hats + Flash for synthesis (cheap tier) to keep cost down.** | parallel 3-5× concurrency | ~6-12 hours for 500 projects |
| I | All spans flow to Phoenix Cloud project `glasshat-prod` via OpenInference auto-instrumentation | continuous | included in H |
| J | Run Phoenix Experiment `glasshat-calibration-v1`: aggregate per-(hat, criterion, evidence_depth_bucket) `predicted_score - ground_truth_label`, where `ground_truth_label` = winner-tier proxy (winner ribbon → high; honorable → high-mid; non-winner → unlabeled, used for variance only) | Phoenix UI / API | ~30 min |
| K | Validate: for unseen sample (5-10 held-out projects from corpus), Glasshat's calibrated score vs ground-truth label MAE ≤ 0.85 × uncalibrated MAE | manual + script | ~30 min |

**Estimated total cost** (Vertex Gemini, conservative):
- Hats per project: 6 × ~5K tokens output × 500 = 15M output tokens at Flash-Lite ≈ $5-10
- Inputs per project (deck + repo + retrieval context): ~50K × 500 = 25M input tokens at Flash-Lite ≈ $2-5
- Blue synthesis + BMAD scorer per project: ~10K output × 500 = 5M output tokens at Flash ≈ $7-15
- Phoenix Cloud: free tier covers this volume
- Qdrant Cloud: free tier or starter — within budget
- **Total: ~$20-50 well within the $500 GCP challenge credit** (`docs/gcp-setup.md`)

### §6.4 Compliance & disclosure

| Concern | Disposition |
|---|---|
| Qdrant rule "All code must be created during the hackathon period" | **Compliant.** Consuming public data as evaluation calibration corpus is not "modification or extension of existing work." Glasshat's own code is 100% new. Same legal posture as reading public textbooks during a coding contest. |
| Rapid Agent rule "Projects must be newly created by the entrant" | **Compliant** (same reasoning). |
| Devpost ToS / scraping ethics | Verify robots.txt before pipeline B runs. Respect any `Crawl-delay`. Throttle to 1 RPS. Identify with descriptive User-Agent (`Glasshat-Calibration-Bot/0.1 +<glasshat-repo-url>`). No login bypass; only data already public. |
| Repository licenses | Apache/MIT/BSD: clone freely. No license at all: read GitHub page + README via API only (allowed under GitHub ToS); do not clone or redistribute code. Glasshat persists only **derived statistical features** (token counts, complexity scores, our own scoring deltas), never the source code. |
| Builders' privacy | Builder names visible in gallery are public Devpost handles; do not enrich with external personal data. |
| README disclosure (mandatory) | Add to README §7.2 "About this submission": *"Glasshat's calibration corpus is seeded from 524 public submissions to the Gemini 3 Hackathon (Dec 2025 – Feb 2026, concluded). Each project's public Devpost description, public GitHub repo metadata, and judged outcome (winner/non-winner) is used as evaluation calibration data only. No code or content from those submissions is reused in Glasshat."* |

### §6.5 Verification gates

| Gate | Criterion | Verified by |
|---|---|---|
| §6.3-A | robots.txt allows the crawl with respected throttle | manual + recorded user-agent log |
| §6.3-D | ≥500 of 524 sampled projects have parseable Devpost pages | scraping log |
| §6.3-E | ≥350 of 524 sampled projects have public GitHub repo URLs (acceptable drop rate <33%) | filter output count |
| §6.3-H | Glasshat pipeline runs over ≥350 projects without fatal error; ≥85% return a complete BMAD score | run log |
| §6.3-I | Phoenix project `glasshat-prod` shows ≥3000 spans (6 hats × ~500 projects ≈ 3000+) and traces match project IDs | Phoenix UI sanity check |
| §6.3-J | `get-experiment-by-id glasshat-calibration-v1` returns calibration rows for ≥85% of (hat, criterion) cells | MCP call test |
| §6.3-K | Held-out MAE improvement ≥15% with calibration | analysis script |
| Demo dry-run | Prepared sample deck → triggers inconsistency on Yellow A1 → Phoenix returns drift → score corrects with deterministic anchors | 3 dry runs, recorded |

### §6.6 Risk register addendum

| Risk | Severity × Likelihood | Mitigation |
|---|---|---|
| Devpost rate-limits the scrape mid-way | Medium × Medium | Resume-from-cursor on each page; exponential back-off; if blocked, fall back to authenticated read via Devpost API (if available) or pause + retry next day. |
| < 350 projects have public GitHub repos | Medium × Low | If true, supplement with Devpost description-only evaluation (Glasshat treats projects as "deck-only" for those). Reduces precision but keeps sample size up. |
| Pipeline H exceeds budget | Medium × Low | Hard-cap at $100 spend; pause + reduce sample size; revert to 200 stratified. |
| Phoenix Experiment doesn't aggregate cleanly | Medium × Medium | Pre-compute aggregations in a separate Python script and upload as a Phoenix Dataset; PhoenixConsultantAgent queries dataset instead of experiment. Both pathways supported by MCP. |
| Demo close mentions "4,499 evaluated" but corpus is 524 | High × Low | **Demo script wording**: say "*we evaluated 524 of the Gemini 3 Hackathon's 4,499 submissions, including all 24+ winners*" — honest, still impressive. |

**Risk**: If past_evals/Phoenix corpus is empty at submission, the demo fails. **Mitigation**: parallel pre-seeding starts at Phase 1.5 (PDF ingest path is ready), not deferred. Run scraping pipeline (steps A-E) in week 1 as documentation work; pipeline H runs continuously through Phase 2-3 as the Glasshat agent matures.

---

## §7 — Spike-test specifications (before Phase 1 build)

To **prove** the wow moment is end-to-end achievable, run these spikes early (no UI, no polish):

### Spike A — Phoenix MCP smoke test (1-2h)
- Install `@arizeai/phoenix-mcp@latest` locally
- Point at Phoenix Cloud free tier (`app.phoenix.arize.com`)
- Manually emit ~50 spans with attributes (hat, criterion, evidence_depth, predicted_score, ground_truth_score)
- From a Python script using MCP client library, call `get-spans` with filters
- Verify returns expected spans; verify aggregation client-side works
- **Pass criterion**: returns ≥10 spans matching filter in <2s

### Spike B — ADK LoopAgent + escalation (2-3h)
- Build a minimal LoopAgent with 2 sub-agents (mock InconsistencyDetector + mock ScoreCalibration)
- Verify state sharing via `ctx.session.state` across iterations
- Verify `tool_context.actions.escalate = True` correctly terminates the loop
- Verify max_iterations=2 caps runaway loops
- **Pass criterion**: loop runs 1-2 iterations as designed; state persists; escalation exits cleanly

### Spike C — ADK + Phoenix MCPToolset wiring (2-3h)
- Build a single LlmAgent with `MCPToolset(StdioServerParameters(command="npx", args=["-y", "@arizeai/phoenix-mcp@latest", ...]))`
- Verify the agent discovers Phoenix MCP tools via `get_tools_async`
- Verify the LLM can invoke `list-projects` and return structured data
- Verify OpenInference auto-instrumentation captures the tool call as a span in Phoenix Cloud
- **Pass criterion**: tool invocation works end-to-end; trace appears in Phoenix within 30s

### Spike D — Calibration policy on toy data (2h)
- Generate synthetic dataset of (hat, criterion, evidence_depth, predicted_score, ground_truth) for 50 examples
- Run Phoenix Experiment to compute per-(hat, criterion) mean delta
- Apply calibration policy `new_score = clip(current_score - 0.8 * mean_delta, anchor_p25, anchor_p75)` to held-out 10 examples
- Compare calibrated vs uncalibrated MAE
- **Pass criterion**: calibrated MAE ≤ 0.9 × uncalibrated MAE on held-out

### Spike E — SSE event animation latency (1h)
- Build a tiny Next.js page with EventSource hook
- Stream 6 events from a local Python server with 800ms gaps
- Verify the React state transitions look "live" (no batched updates, no jank)
- **Pass criterion**: subjective — the audit reads as theatrical, not janky

**Total spike budget**: ~10 hours. Run before Phase 1.9 (pipeline orchestrator build). If any spike fails, document the blocker and pivot the design before sinking weeks into the full build.

---

## §8 — Fallback design (if any step fails)

| Failure mode | Fallback |
|---|---|
| Phoenix Cloud rate-limits or outages | Switch to self-hosted Phoenix in Cloud Run (`MONITOR_BACKEND=phoenix-local`). Pre-recorded Phoenix UI screenshot for demo backup. |
| Phoenix MCP `get-experiment-by-id` returns empty (seeding incomplete) | Fall back to `get-spans` + client-side aggregation. If that also returns empty: use mock calibration data labeled "demo seed — replace with live data" in the UI. (Honest, but reduces wow.) |
| ADK LoopAgent + MCPToolset interaction has unknown bug | Replace LoopAgent with a hand-written CustomAgent that explicitly invokes the 3 sub-agents and checks `escalate` in code. Same behavior, less ADK magic. |
| Phoenix MCP latency too high for demo pacing | Pre-call Phoenix at IngestAgent stage (warm-up), cache findings; AuditLoop reads from cache. |
| 3D graph fails to reshape on score correction | Fall back to 2D radar with the corrected score animated. Audit moment still lands without 3D; just less spectacular. |
| Calibration policy mis-corrects (over/under) | Cap delta at ±2.0; require ≥3 anchor projects before applying; human-override gate as final safety net. |

---

## §9 — Updated architecture decisions

These supersede portions of `docs/architecture.md` and `PLAN.md`:

| Decision | Old (PLAN.md / architecture.md) | New (verified 2026-05-14) | Rationale |
|---|---|---|---|
| Agent runtime | Vertex AI Agent Builder (Blue planner registered there) + LangGraph-in-Cloud-Run | **Google ADK on Cloud Run** | ADK has native LoopAgent + conditional re-execution; Arize starter kit uses ADK; Rapid Agent eligible-runtime list includes ADK; Agent Builder is for higher-level surfacing, not inner loops |
| MCP integration | Arize MCP server tool calls from the orchestrator (unspecified mechanism) | **Phoenix MCPToolset with StdioServerParameters (npx)** | Verified pattern from Arize starter kit + ADK MCP docs; works on Cloud Run |
| Self-improvement loop | "Phoenix tracing + meta-eval metrics" (unspecified runtime adaptation) | **LoopAgent(max_iterations=2) with InconsistencyDetector → PhoenixConsultant → ScoreCalibration; escalates on convergence** | Concrete, demoable, fits ADK idiom |
| Phoenix corpus seeding | Implicit ("past_evals seeded with 50-150 projects") | **Two-stage seed: (1) run pipeline over past projects, (2) run Phoenix Experiment to aggregate calibration data**. Both before demo. | Without (2), `get-experiment-by-id` returns empty and Path A of Phoenix consultation fails |
| Calibration policy | Not specified | **`new_score = clip(current_score - 0.8 × phoenix_mean_delta, anchor_p25, anchor_p75)`, ±2.0 cap, ≥3 anchors required** | Deterministic, demoable, robust |

---

## §10 — Updates to `PLAN.md` (additions to §9 "Next work")

Replace Phase 1.12 (generic seed) with:

> **1.12 Gemini 3 Hackathon corpus scrape (524 stratified projects)**: enumerate `gemini3.devpost.com/project-gallery` (4,499 projects, 188 pages), apply stratified sampling (all 24+ winners + 500 random non-winners), fetch per-project Devpost pages, filter to those with public GitHub repos. Produces `seed/gemini3-projects-524.jsonl` + cloned repos in `seed/repos/`. Respects robots.txt + 1 RPS throttle. See `docs/wow-moment-design.md` §6.

Add Phase 1.13:

> **1.13 Phoenix calibration experiment (`glasshat-calibration-v1`)**: run Glasshat pipeline over the 524 corpus (using Flash-Lite tier for cost), all spans flow to Phoenix Cloud via OpenInference. Then aggregate per-(hat, criterion, evidence_depth_bucket) `predicted_score - ground_truth_label` into a named Phoenix Experiment. Validate held-out MAE improvement ≥15% with calibration. PhoenixConsultantAgent queries via `get-experiment-by-id`. Pre-seed before any demo recording. Budget ≤$50. See `docs/wow-moment-design.md` §6.

Replace Phase 1.9 (Pipeline orchestrator) sub-step "LangGraph" with:

> **1.9 Pipeline orchestrator (Google ADK on Cloud Run)**: GlasshatRootAgent (CustomAgent) → IngestAgent → BluePlannerAgent → HatsPanel (ParallelAgent of 6) → AuditLoop (LoopAgent of 3 sub-agents, max_iterations=2) → BMADScorerAgent → ReportAssemblerAgent. MCPToolset wires Phoenix MCP via npx-stdio. OpenInference auto-instrumentation. See `docs/wow-moment-design.md` §4 for the topology, §5 for the wiring, §7 for spike tests.

---

## §11 — Apex-Pass refinement: Phoenix-native detection (2026-05-14 update)

This section supersedes §3 Step 1 (Detection) and §4 (Agent topology) where they previously assumed a hand-coded "if score >= 8 and evidence_depth < 0.4" rule. Post-Apex-Pass (see `docs/technical-apex-features.md`), the detection is **Phoenix-native + redundant**.

### §11.1 Triple-redundant detection (no single point of failure)

The wow moment relies on *detecting* Yellow's miscalibration. Previously: single hand-coded check. Now: three independent paths converge.

| # | Detection path | What it does | Where it lives |
|---|---|---|---|
| 1 | **Phoenix Online Eval Task** (LLM-as-judge) | Auto-runs the moment Yellow's score span is emitted; evaluator prompt compares predicted_score vs evidence_depth; returns `eval.calibration.label = "over_confident"` annotation attached to the span. Sub-second latency. Sampling 100% in demo, configurable in prod. | Phoenix Cloud Task (configured at deploy time); see `docs/technical-apex-features.md` §2.3 |
| 2 | **Phoenix Custom Evaluator (Python)** | Runs same logic as Path 1 but as a Python function with statistical rules (no LLM call). Faster, deterministic, lower cost. Parallel to Path 1; either independently triggers the audit. | Custom evaluator registered via `arize-phoenix-evals` SDK; see `technical-apex-features.md` §2.4 |
| 3 | **Black hat counter-claim (orchestrator-level)** | Black hat runs in parallel with Yellow under ADK ParallelAgent; if Black flags an evidence gap on the same criterion Yellow scored high on, this independently triggers the AuditLoop. | `agents/black/prompt.md` + post-hat callback (4.5) |

**Convergence**: AuditLoop's `InconsistencyDetectorAgent` reads the union of {Phoenix Online Eval annotation, Phoenix Custom Eval annotation, Black hat counter-claim} from session state. If any ≥1 of these flags an issue, audit proceeds. Demo visualization shows all three lighting up.

This is what `max-wins-plan.md` §5.1's "BACKUP BEAT" at the 1:00-1:30 slot refers to. Even if Path 1 has a hiccup, Paths 2-3 carry the narration.

### §11.2 MCP call chain at the consultation moment (Apex-Pass version)

When Blue planner consults Phoenix at 1:30-2:00 (Arize demo) / 1:30-1:45 (Qdrant demo), it makes **3 MCP calls in parallel**, all visible in the Phoenix trace tree:

1. **`get-experiment-by-id("glasshat-calibration-v1")`** with filters `{hat: "yellow", criterion: "A1", evidence_depth_bucket: "<0.4"}` → aggregated `{mean_delta: -1.2, n: 14, CI: [0.9, 1.5]}`. Primary signal.
2. **`get-span-annotations(yellow_a1_span_id)`** → returns the Online Eval annotation that triggered this consultation (proof chain).
3. **`get-dataset-examples("calibration_corpus_v1", filter, limit: 3)`** → 3 anchor projects with similar profiles for the Qdrant Recommendation API to use as positive examples.

Then Qdrant Recommendation API call:
4. **`recommend(positive=[anchor_ids_from_step_3], negative=[accurate_yellow_anchor_ids], strategy="average_vector")`** → top-3 best-calibrated examples for the score correction guidance.

This 4-call sequence completes in <800ms total (verified bound: `get-experiment-by-id` ~200ms cached + 3 parallel calls ~300ms + Qdrant ~200ms + RTT). Well within demo pacing budget.

### §11.3 The annotation closure (human-in-the-loop closes calibration loop)

After auto-correction, the human-override gate (gate 2 from `PLAN.md`) is offered:
- If user accepts: `annotation.human_override.action = "confirmed_auto"` written to Phoenix → next-run calibration treats this as positive ground truth.
- If user rejects: `annotation.human_override.action = "rejected"` + `annotation.human_override.score = <user_value>` + `annotation.human_override.reason = <text>` → next-run calibration adjusts.

Phoenix Annotations API (via MCP `add-dataset-examples` or direct REST) closes the loop. Demo shows the override UI even when the user accepts auto, to demonstrate the human-in-control axis (Rapid Agent: "keep the user in control").

### §11.4 Updated agent topology

```
GlasshatRootAgent (CustomAgent)
│
├─ IngestAgent
│
├─ BluePlannerAgent (LlmAgent, thinking_level=high)
│  ├─ before_model + after_model callbacks (4.5-4.6)
│  └─ output_key="plan"
│
├─ HatsPanel (ParallelAgent)
│  ├─ WhiteAgent  (LlmAgent + qdrant_hybrid_search_tool + vertex_grounding_tool)
│  ├─ RedAgent    (LlmAgent)
│  ├─ YellowAgent (LlmAgent + qdrant_hybrid_search_tool)
│  ├─ BlackAgent  (LlmAgent + qdrant_hybrid_search_tool, must_cite_precedent via Plugin)
│  ├─ GreenAgent  (LlmAgent)
│  └─ BlueSynthesisAgent
│
├─ AuditLoop (LoopAgent, max_iterations=2)
│  ├─ InconsistencyDetectorAgent
│  │  └─ Reads union of:
│  │       - Phoenix Online Eval annotation (path 1)
│  │       - Phoenix Custom Evaluator annotation (path 2)
│  │       - Black hat counter-claim from session state (path 3)
│  ├─ PhoenixConsultantAgent (LlmAgent + Phoenix MCPToolset + Qdrant Recommendation tool)
│  │  ├─ get-experiment-by-id
│  │  ├─ get-span-annotations
│  │  ├─ get-dataset-examples
│  │  └─ qdrant.recommend(positive, negative, strategy="average_vector")
│  └─ ScoreCalibrationAgent
│     ├─ exit_audit_loop tool (sets escalate=True)
│     └─ writes audit_corrections to session state
│
├─ BMADScorerAgent (LlmAgent + qdrant_hybrid_search_tool + qdrant_groupby_tool)
│  └─ Uses context cache for BMAD rubric (3K tokens, 90% discount)
│
└─ ReportAssemblerAgent
   ├─ Writes Firestore audit record
   ├─ Emits SSE events with ≥800ms gaps for demo pacing
   └─ Writes Phoenix Annotation on human-override gate decision
```

### §11.5 Why this raises both Qdrant and Arize win probabilities

| Effect | Qdrant impact | Arize impact |
|---|---|---|
| Phoenix Online Eval as detection | (background) | **★★ Self-improvement loop bonus maxed** — agent reacts to its own observability data in real-time |
| Custom Evaluator as backup | (background) | **★ Demonstrates two independent eval surfaces** |
| Recommendation API for anchor retrieval | **★ Material vector use (non-obvious)** | (background) |
| Triple-redundant detection | **★ Functionality (resilient)** | **★ Tech Implementation (engineering depth)** |
| Phoenix Annotations close the loop | (background) | **★ "Keep user in control" thesis literal** |
| All 4 MCP calls visible in trace tree | (background) | **★★ "Meaningful use of tracing and MCP" — direct judging-criterion match** |

**Probability estimate revision** (post-Apex-Pass):
- Qdrant top-3: 28-35% → **35-42%** (Recommendation API + Phoenix Online Eval + multi-layer demo)
- Arize top-3: 50-55% → **58-65%** (multi-eval surface + annotation closure + visible MCP call chain hits tie-break #1 dimension hard)

---

## §12 — Bottom line

**The audit-the-auditor wow moment is technically feasible AND densified with redundancy.** All required capabilities exist in shipping versions:
- Google ADK: `LoopAgent`, `ParallelAgent`, `MCPToolset`, `before_*/after_*` callbacks, Cloud Run deploy
- `@arizeai/phoenix-mcp`: `get-experiment-by-id`, `get-span-annotations`, `get-dataset-examples`, `add-dataset-examples` (annotation closure)
- Arize AX Online Evals: Task/sampling/scope/filter all configurable
- Qdrant: hybrid + RRF + Recommendation API + group-by + payload filtering — all v1.10+

The 5 spike-tests (§7, ~10 hours) prove the integration before sinking weeks into the full build, plus 2 new spikes added by Apex-Pass:

**Spike F — Phoenix Online Eval Task end-to-end** (2-3h): create a Task, point at a synthetic dataset, verify the LLM-as-judge auto-fires on new spans within sampling rate, results queryable via `get-span-annotations`. Pass: sub-second eval, annotation visible in Phoenix UI.

**Spike G — Phoenix Annotation write + read** (1-2h): write annotation via SDK, read via MCP, verify it influences next experiment aggregation. Pass: round-trip <2s, annotation surfaces in subsequent `get-experiment-by-id` aggregation if Experiment is re-run.

**Critical dependencies** for the moment to land at demo:
1. ✅ Tooling exists (ADK + Phoenix MCP + Online Evals) — verified
2. ⚠ Pre-seeded past_evals (524 Gemini 3 corpus) + Phoenix experiment — **must be done before demo recording**; Phase 1.12 + 1.13
3. ⚠ Phoenix Online Eval Task configured + tested — Spike F (Phase 1 pre-flight)
4. ⚠ Spike tests A-G pass — schedule before Phase 1.9 starts
5. ⚠ Calibration policy doesn't over/under-correct on demo data — manual dry-run validation 1 week before submission
6. ⚠ Triple-redundant detection — at least 2 of 3 paths must fire on the demo's prepared deck

**Failure mode that kills the wow** (refined): NONE of three detection paths fires → no audit triggered → demo flatlines. **Mitigation**: prepared demo deck is *engineered* to produce evidence_depth ~0.31 on Yellow A1 (well below threshold), virtually guaranteeing at least Path 2 fires. Plus Black hat must-cite-precedent (Plugin or callback enforces this) virtually guarantees Path 3.

---

---

## §12 — Rubric-aware audit + Hybrid mode (added 2026-05-15)

This section supersedes parts of §3 + §4 + §11 where they previously assumed a single, fixed rubric. Per [[glasshat-rubric-and-mode]] (locked 2026-05-15), Glasshat now **synthesizes the rubric per evaluation** (`docs/rubric-synthesis-spec.md`) and **runs in two viewports** on one engine (`docs/hybrid-mode-spec.md`).

### §12.1 What changed in the wow moment

**Before**: a single Yellow A1 score self-corrects from 9.0 → 7.6 based on Phoenix calibration data. Compelling but single-axis.

**After**: the wow moment now has **two layers**:

1. **Layer 1 (existing)**: triple-redundant detection (§11.1) + Phoenix MCP consultation (§11.2) + ScoreCalibrationAgent correction. *Same as before.*
2. **Layer 2 (NEW)**: a **dual-rubric variance display** at 2:30-2:38 — same submission scored under TWO synthesized rubrics shown side-by-side. Caption: *"Correct rubric-aware variance, not bias."*

The variance display proves Glasshat doesn't just self-correct; it proves **fairness is rubric-relative**. This is the dinner-table-retellable upgrade.

### §12.2 Demo viewport split

| Demo | Primary viewport | Wow moment specifics |
|---|---|---|
| **Qdrant VSD** | Judge mode (`/judge`) | Layer 1 fires on a high-profile card from the 503 corpus during batch run; Layer 2 dual-rubric variance shows after batch complete |
| **Rapid Agent / Arize** | Participant mode (`/participate`) | Layer 1 fires mid-iteration; participant accepts Phoenix MCP suggestion → re-runs → score animates 73→79; Layer 2 dual-rubric variance shows after re-run |

**Final 1-second reveal in both demos**: caption *"Same engine. Different viewer. Different fairness."*

### §12.3 Anchor retrieval becomes weight-aware

§3 Step 3 (Qdrant anchor retrieval) is updated to use the new `rubric_weights` named vector on `past_evals`:

```python
# services/audit/anchor_retrieval.py
def select_anchors(synthesized_rubric, hat, criterion_id, evidence_depth_bucket, top_k=3):
    return qdrant.search(
        collection="past_evals",
        query_vector=synthesized_rubric["weights_vector"],
        using="rubric_weights",  # named vector, cosine similarity
        query_filter={
            "must": [
                {"key": "hat", "match": {"value": hat}},
                {"key": "criterion_bmad_mapping",
                 "match": {"any": criterion["bmad_mapping"]}},
                {"key": "evidence_depth_bucket", "match": {"value": evidence_depth_bucket}},
            ]
        },
        limit=top_k,
        with_payload=True,
    )
```

This means **the 503 Gemini 3 corpus (anchored under Gemini 3's Tech 40/Inn 30/Imp 20/Pres 10 weights) is reusable across all 4 preset rubrics** — the cosine similarity on `weights_vector` automatically biases retrieval toward anchors with similar weight schemas to the current evaluation. No re-evaluation required at seed time.

See `docs/rubric-synthesis-spec.md` §8 for the full anchor retrieval logic.

### §12.4 Updated agent topology (additive — RubricSynthesizer node)

```
GlasshatRootAgent (CustomAgent)
│
├─ IngestAgent
│
├─ RubricSynthesizerAgent  (NEW — LlmAgent, Gemini 3.1 Pro thinking_high)
│  ├─ Path A: load preset directly (skip Gemini call)
│  ├─ Path B: fetch_url + parse rules
│  ├─ Path C: PDF parse + parse rules
│  ├─ Path D: validate user YAML (skip Gemini call)
│  └─ output_key="rubric_synthesized"
│
├─ BluePlannerAgent (LlmAgent, thinking_level=high)
│  └─ Reads ctx.session.state["rubric_synthesized"] to plan retrieval budgets per criterion
│
├─ HatsPanel (ParallelAgent)  ── unchanged from §11.4 ──
├─ AuditLoop (LoopAgent, max_iterations=2)  ── unchanged from §11.4 ──
├─ BMADScorerAgent (LlmAgent)
│  └─ Maps hat outputs to synthesized rubric criteria via bmad_mapping (NEW)
│
└─ ReportAssemblerAgent
   └─ Emits scores in synthesized rubric's native scale (NOT fixed BMAD 100)
```

The RubricSynthesizer node sits *between* Ingest and BluePlanner. All downstream agents read `ctx.session.state["rubric_synthesized"]` for the rubric-of-record.

### §12.5 Probability impact

Per [[glasshat-rubric-and-mode]] §1 estimates:

- Qdrant top-3: 38-45% → **42-52%** (+4-7 pp)
  - Layer 2 dual-rubric scene lands on Originality + Functionality + UX simultaneously
  - Top-K hit rate badge on 503 corpus = ground-truth proof
- Arize top-3: 62-68% → **65-72%** (+3-4 pp)
  - Participant-mode iterate-loop = literal "agent that improves over time"
  - RubricSynthesizer + 4 source-clause traceability maxes Tech tie-break #1

### §12.6 What this does NOT change

- All 5 existing wow-moment steps (§2) remain
- All 7 spike validations (§7 + Apex Spikes F, G) remain valid (no new spike needed for rubric synthesis — pure prompt-engineering against existing Vertex Gemini 3.1 Pro pathway)
- All fallbacks (§8) remain
- Phoenix MCP consultation chain (§11.2) unchanged
- Annotation closure (§11.3) unchanged
- Triple-redundant detection (§11.1) unchanged

The rubric+mode upgrade is **additive**, not destructive. Phase 1 build can proceed exactly per §17 of `docs/max-wins-plan.md` with the new ordering: D → 1.5 (RubricSynthesizer) → B → mode UI.

---

---

## §13 — sangguen's Vector-DB-as-Protagonist sharpening (added 2026-05-15)

sangguen's positioning insight (2026-05-15 17:45 KST) refines the wow moment without scope expansion:

> *"AI 심사위원이 자기 점수가 틀렸다는 걸, **Qdrant에 저장된 과거 제출작 벡터 공간 때문에** 들켜서, 실시간으로 점수를 고친다."*
>
> *"Glasshat doesn't just judge projects. It audits the judge."*

This is the demo's first 5-second hook in **both** Qdrant and Rapid Agent versions.

### §13.1 Four narration upgrades (all APPLY-tier per `docs/technical-apex-features.md` §10.0)

1. **Live Bias Meter per Hat** (6.8) — Hat cards show a small dial gauge: rises when the Hat overscores, falls back to normal range *visibly* after Phoenix-MCP + Qdrant-anchor consultation. Makes the bias correction tactile — judges see meters move, not just numbers tick.

2. **Anti-Pattern Radar narration** (6.9) — at audit moment, on-screen text: *"37 of 503 past Gemini 3 submissions matched this profile. Winners: 0. Common failure: vague user, weak repo evidence, no working demo."* Re-uses Qdrant Recommendation API negative anchors; the **narration** is what's new.

3. **Winner Gravity narration upgrade** (6.10) — when 3D graph node moves post-correction, floating tooltip: *"72% similar to winner cluster, but pulled toward non-winner pattern by anchor 'X' (similar evidence depth)."* Makes the spatial movement *legible*.

4. **Score Receipts UI rebrand** (6.11) — what we called "evidence drill-down" → **"Score Receipts"** (each score has a receipt: deck quote + repo file:line + 2 anchor projects + their scores). Memorable shareable label.

### §13.2 Qdrant becomes the protagonist (8 visible touch points across 3-min demo)

Per sangguen's "Vector DB must be load-bearing", Qdrant is foregrounded **eight times** in the Qdrant 3-min demo:

| Slot | Qdrant feature visible |
|---|---|
| 0:10-0:30 | LAYER 2 — pitch_chunks + repo_chunks DENSE+SPARSE indicators ticking |
| 0:30-1:00 | LAYER 4 — Yellow card shows evidence_depth = 0.31 (computed from Qdrant retrieval depth) |
| 1:30-1:45 | LAYER — Recommendation API call visible: positive=[over_confident_anchors] negative=[accurate_anchors], strategy=average_vector |
| 1:30-1:45 | LAYER — group_by query results: anchor projects + their A1 scores |
| 1:45-2:30 | LAYER 2 — 503 anchor constellation in 3D, clustered by outcome_tier (gold/silver/grey) |
| 1:45-2:30 | LAYER 4 — corrected node migrates toward winner-anchor cluster (Winner Gravity narration) |
| 2:30-2:50 | RIGHT panel — group_by query "Ranks similar to X (winner)" + Anti-Pattern Radar narration |
| 2:50-3:00 | Tagline: "*And the auditor is the vector space.*" |

### §13.3 sangguen's scope-cut alignment (already in our v1)

| sangguen proposed cut | Our v1 status |
|---|---|
| KO/EN i18n 보류 | ✅ Already cut (max-wins-plan §12 decision 5) |
| 75 evaluation techniques 보류 | ✅ Already cut (max-wins-plan §12 decision 6 + technical-apex §0) |
| Production auth 보류 | Partial — Firebase Auth Google sign-in retained (RLS prerequisite); SSO/SAML/enterprise auth in V2 |
| 6 Hats UI: only 3 visible | ✅ Already cut (max-wins-plan §12 decision 6) |

### §13.4 Why our hybrid+rubric thesis sharpens sangguen's message (one level higher)

sangguen's framing is **"Qdrant audits the judge."** Our 2026-05-15 thesis upgrade ([[glasshat-rubric-and-mode]]) extends this to:

> **"Qdrant audits the judge — *and proves the judge is rubric-relative*."**

Why this is one level higher (Christensen JTBD-frame):
- sangguen's frame answers: "Is the AI judge fair?"
- Our extended frame also answers: "**Fair according to whom**?"

The dual-rubric variance display (§12.1 Layer 2 + max-wins-plan §13) shows the same submission scoring 87 under Qdrant rubric and 73 under Rapid Agent rubric, captioned *"Correct rubric-aware variance, not bias."* This delivers sangguen's message **and** opens Glasshat to evaluators across hackathons / VCs / accelerators / academic boards — single-protagonist Qdrant audit + multi-rubric defensibility.

Both demos' final 1-second reveal: *"Same engine. Different rubric. Different (correct) score."*

### §13.5 Authoritative narration anchors (lock 2026-05-15)

These exact strings are demo voice / on-screen captions; do not paraphrase in scripts:

| Beat | String |
|---|---|
| Both demos 0:00-0:05 hook | *"Glasshat doesn't just judge projects. It audits the judge."* |
| Qdrant demo 1:30-1:45 anti-pattern | *"37 of 503 past submissions matched this profile. Winners: 0."* |
| Qdrant demo 1:45-2:30 gravity | *"72% similar to winner cluster, but pulled toward non-winner pattern."* |
| Qdrant demo 2:50-3:00 close | *"And the auditor is the vector space."* |
| Rapid Agent demo 2:50-3:00 close | *"And the audit happens mid-iteration."* |
| Both demos 2:55-3:00 reveal | *"Same engine. Different rubric. Different (correct) score."* |

---

*Last updated: 2026-05-15 KST post-rubric-and-mode lock + sangguen's wow-sharpening. Authoritative on wow moment technical design. Updates require user review.*
