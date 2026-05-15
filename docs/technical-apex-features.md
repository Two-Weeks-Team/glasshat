# Technical Apex Features — Decision Matrix

> **Status**: Locked 2026-05-14. Maps every advanced capability from Qdrant / Phoenix-Arize / Gemini 3 / Google ADK to an APPLY / CUT / STRETCH decision for Glasshat. Each row records the judging-axis payoff and implementation complexity, so the build sequence is deterministic. Companion files: `docs/max-wins-plan.md` (strategy + scripts), `docs/wow-moment-design.md` (audit-the-auditor design).

---

## §0 — Decision legend

| Code | Meaning |
|---|---|
| **APPLY** | Must be in v1. Earns judging points on ≥1 axis with reasonable build cost. |
| **STRETCH** | Build if Phase 1/2 schedule permits; do not block on this. Has a clean cut path. |
| **CUT** | Explicitly out of v1. Documented to prevent scope creep. |

| Judging axis abbreviations |
|---|
| Q-F = Qdrant Functionality, Q-O = Qdrant Originality, Q-UX = Qdrant User Experience |
| R-T = Rapid Agent Tech Implementation, R-D = Design, R-I = Potential Impact, R-Q = Quality of Idea |
| R-Arize = Arize-track-specific bonus ("self-improvement loop" + "meaningful use of tracing and MCP") |

---

## §1 — Qdrant advanced features

| # | Feature | Decision | Judging payoff | Complexity | Implementation outline / risk |
|---|---|---|---|---|---|
| 1.1 | **Dense + sparse hybrid search via Query API (v1.10+) with RRF fusion** | APPLY | Q-F · Q-O (sophistication) · R-T | Medium | Each `pitch_chunks` and `repo_chunks` point holds dense (Vertex embedding) + sparse (BM25-style). All hat agents that query these two collections use `prefetch` with both vectors → `FusionQuery(fusion=Fusion.RRF)`. Bigger gain: significantly better retrieval on text-heavy chunks. Risk: dual embedding pipeline doubles ingest cost by ~30%; mitigated by single combined call. |
| 1.2 | **Weighted RRF (v1.17+)** | APPLY | Q-F · Q-O | Low | Use `{"rrf": {"weights": [3.0, 1.0]}}` on `pitch_chunks` queries where dense semantic match is more important than sparse keyword match. Tune weights once on the 524 calibration corpus. |
| 1.3 | **Recommendation API with positive+negative examples (`average_vector` strategy)** | APPLY | Q-O (★ the wow moment uses this) · R-T | Medium | At the AUDIT moment, instead of plain `past_evals` similarity search, use `recommend(positive=[bias_pattern_anchors], negative=[anti_pattern_anchors], strategy="average_vector")` to retrieve projects that scored similarly *and* had the same evidence-depth profile. This is the "find similar over-confident Yellow A1 patterns, but only from runs where Black hat was accurate" query. Sharper than plain similarity → richer anchor explanation → judge sees vectors doing real reasoning, not just nearest-neighbor lookup. |
| 1.4 | **Discovery API (target + context for guided exploration)** | STRETCH | Q-O · Q-UX | Medium | The 3D evaluation graph's "explore neighbors" interaction uses `discover` with target=current_project and context pairs of (winner_example, non_winner_example). Lets the user navigate the spatial graph with semantic constraints. Visual polish if time permits; cut cleanly if 3D animation budget tight. |
| 1.5 | **Group-by / aggregations in queries** | APPLY | Q-F · R-T | Low | Anchor comparison panel uses `query_groups` to fetch top-3 per `outcome_tier` (winner / honorable / non-winner) in a single API call. 1 round-trip vs 3. Demo close shows "ranks similar to X (winner), weaker than Y (winner), stronger than Z (non-winner)" cleanly. |
| 1.6 | **Payload filtering with high-cardinality fields (`outcome_tier`, `hat`, `criterion`, `evidence_depth_bucket`)** | APPLY | Q-F · R-T | Low | Indexed payload fields with `range` and `match` filters on every retrieval. Standard practice; codify it as a discipline, not a bolt-on. Verify all 6 collections have appropriate payload indexes. |
| 1.7 | **Scalar / Product Quantization (memory + cost reduction)** | APPLY | Q-F · R-T (production-readiness signal) | Low-Medium | `past_evals` collection (largest, ~3000+ points after 524-project seed) uses Scalar Quantization (int8) with `rescore=True` for accuracy. Halves memory footprint, judge-visible "this is built for scale" signal. Other smaller collections (techniques, bmad_criteria) skip quantization. |
| 1.8 | **Multi-vector points (e.g., one point with dense + sparse + ColBERT)** | STRETCH | Q-O (depth) | Medium-High | ColBERT-style late interaction for re-ranking the top-100 candidates → top-10 final. Improvement on retrieval quality. Cut if Vertex AI doesn't offer a clean ColBERT model out of the box; the gain is real but the engineering bloat is real. |
| 1.9 | **DBSF (Distribution-Based Score Fusion, v1.11+)** | CUT | (negligible vs RRF for our use case) | Low | RRF is well-understood and sufficient. DBSF requires careful score distribution tuning; gains are marginal for 6 collections of moderate size. |
| 1.10 | **Cross-collection lookup (`lookup_from`)** | STRETCH | Q-F · R-T | Low | Use case: in Recommendation queries on `past_evals`, look up the actual vector of an anchor project's `pitch_chunks` to refine the retrieval. Niche; only build if a specific scenario in the AUDIT pipeline benefits clearly. |
| 1.11 | **Snapshots / HA / cluster sharding** | CUT | (operational concern, not judging concern) | High | Hackathon submission doesn't need HA. Single-node Qdrant Cloud cluster is sufficient. |

**Cross-cutting Qdrant discipline (all APPLY-tier features depend on this)**:
- Every collection has a **payload schema YAML** committed at `packages/shared/qdrant-schemas/<collection>.yaml`
- Every payload field intended for filtering is **indexed** at collection creation
- All retrieval functions in `services/shared/qdrant.py` go through a single `query_with_audit()` wrapper that emits an OpenInference span with `retrieval.documents.0.document.content`, `retrieval.query`, and Qdrant API params — making vector retrieval visible in Phoenix traces

---

## §2 — Arize Phoenix advanced features

| # | Feature | Decision | Judging payoff | Complexity | Implementation outline |
|---|---|---|---|---|---|
| 2.1 | **OpenInference auto-instrumentation via `phoenix.otel.register(..., auto_instrument=True)`** | APPLY | R-T · R-Arize (★ required for Stage 1 pass/fail) | Low | Single line at app startup. Auto-captures all Gemini calls, all LLM tool calls, and ADK agent invocations as spans with standard semantic conventions (`llm.input.messages`, `llm.output`, `tool.name`, `retrieval.documents`). Free-of-charge depth signal. |
| 2.2 | **OpenInference semantic conventions for custom spans** | APPLY | R-T (clarity signal) · R-Arize | Low | Custom spans emitted from our orchestrator (e.g., "audit_loop.iteration", "calibration_applied") use OpenInference attribute names where applicable. Makes Phoenix UI auto-render rich detail panels rather than opaque attribute lists. Spec: `openinference.semconv` constants for all custom attribute keys. |
| 2.3 | **Phoenix Online Evals — Task that runs an LLM-as-judge on Yellow's span the moment it's emitted** | APPLY | R-T · R-Arize (★★ this is the Arize moat) · R-Q | Medium-High | Create a Phoenix Task: scope=span, filter=`span.kind=="llm" AND attributes.glasshat.hat=="yellow" AND attributes.glasshat.criterion=="A1"`, evaluator = LLM-as-judge prompt that compares the predicted score to evidence_depth and returns `{label: "calibrated" \| "over_confident" \| "under_confident", score: float, explanation: str}`. Result auto-attaches to span as `eval.calibration.label/score/explanation`. AuditLoop's InconsistencyDetector queries `get-span-annotations` via Phoenix MCP. Sampling rate: 100% during demo, 10-30% in production. |
| 2.4 | **Phoenix Custom Evaluators in Python (for offline batch over the 524 corpus)** | APPLY | R-T · R-Arize (★ proves "agent improves over time") | Medium | Python evaluator registered with `arize-phoenix-evals`. Runs over the 524 calibration corpus to compute per-(hat, criterion, evidence_depth_bucket) drift statistics. Results upserted to a Phoenix Dataset that backs the `glasshat-calibration-v1` Experiment. |
| 2.5 | **Phoenix Datasets API (with `add-dataset-examples` via MCP)** | APPLY | R-Arize | Low | Calibration ground truth lives in a Phoenix Dataset (one row per (project_id, hat, criterion) tuple with predicted_score + ground_truth_label). PhoenixConsultantAgent can MCP-query this dataset during audit. Versioned: v1, v2, v3 as the corpus grows. |
| 2.6 | **Phoenix Experiments + `get-experiment-by-id` MCP call (already in wow-moment-design §6)** | APPLY | R-Arize (★ self-improvement loop evidence) | Medium | Pre-computed calibration aggregates stored as a Phoenix Experiment. AuditLoop's PhoenixConsultantAgent queries this at runtime. Returns mean_delta + sample_size + confidence interval. Sub-200ms latency. |
| 2.7 | **Phoenix Annotations API for the two human gates (plan approval + score override)** | APPLY | R-D (UX) · R-Arize | Low | Every user override at gate 2 emits a Phoenix Annotation on the corresponding score span: `annotation.human_override.score`, `annotation.human_override.reason`. Future runs' calibration experiment incorporates these annotations as ground truth. Closes the loop: human feedback → Phoenix → next-run calibration. |
| 2.8 | **Phoenix Prompt Playground / Prompt versioning** | STRETCH | R-T (rigor signal) | Low-Medium | The 6 hat prompts + BMAD scorer prompt + audit detector prompt are versioned in Phoenix (`upsert-prompt`, `get-prompt-version-by-tag`). Demo can show prompt-version pinning. Cut cleanly if time tight: prompts live in `agents/<color>/prompt.md` only. |
| 2.9 | **Phoenix LLM-as-judge built-in templates (groundedness, hallucination, QA-correctness)** | APPLY | R-T · R-Arize | Low | Built-in groundedness evaluator runs on every hat span — checks "does the hat's claim trace to a retrieved chunk?" Built-in hallucination evaluator runs on Black hat output (where hallucinations are most damaging). Results visible in Phoenix UI side-by-side with traces. |
| 2.10 | **Phoenix Online Eval — Agent trajectory evaluator** | STRETCH | R-T · R-D | Medium | Trajectory-scope evaluator scores the entire audit-loop sequence as a unit ("did the agent converge in ≤2 iterations? did the correction reduce score variance?"). Cool for a demo close, but its value vs cost is moderate; cut cleanly if needed. |
| 2.11 | **Phoenix self-hosting (Docker Compose, in Cloud Run)** | APPLY (as fallback) | (resilience, not judging) | Medium | `MONITOR_BACKEND=phoenix-local` interface abstraction (already in `.env`). Used in case Phoenix Cloud free tier rate-limits or has outage on judging day. Same MCP server works against either. |

**Phoenix discipline (cross-cutting)**:
- All custom span attributes prefixed `glasshat.*` (e.g., `glasshat.hat`, `glasshat.criterion`, `glasshat.evidence_depth`)
- All eval results follow naming convention `eval.<name>.label/score/explanation`
- Phoenix project name = `glasshat-{env}` (`glasshat-prod` for the live submission; `glasshat-corpus-seed` for the 524-project run)

---

## §3 — Gemini 3 best practices

| # | Feature | Decision | Judging payoff | Complexity | Implementation outline |
|---|---|---|---|---|---|
| 3.1 | **`thinking_level` parameter** | APPLY | R-T · R-D (★ Blue planner reasoning visible) | Low | Blue planner uses `thinking_level: "high"` for plan generation and synthesis — emits thinking tokens that we surface in the demo as the "planner's reasoning trace". 6 hat agents use `thinking_level: "medium"` (balance cost + quality). Code-grader heuristics use `thinking_level: "minimal"` (fast, structured output). Per-call cost impact is non-trivial; budget tracked. |
| 3.2 | **Thinking tokens visible in the demo (Blue planner)** | APPLY | R-D · Q-UX | Low | When Blue planner runs, the Next.js UI streams its `thinking` channel into a collapsible "show reasoning" panel. Visual proof of thought. Avoids the "black box" impression. |
| 3.3 | **Context caching (Vertex AI explicit cache)** | APPLY | R-T (★ production discipline signal) | Medium | BMAD rubric (~17 items × ~120 words = ~3K tokens) + each hat's full system prompt + the 75-technique catalog (~6K tokens) = ~10-15K tokens of repeated context per run. Above the 4,096-token Gemini 3 minimum for caching. Create one explicit cache per environment (`glasshat-prompts-v1`), TTL 60 min, refresh on each demo session. **90% token-cost discount** on cached portions. For 524-project corpus seeding, this brings the build cost from ~$50 toward ~$20. |
| 3.4 | **Function calling with `responseSchema` (structured output) on every hat call** | APPLY | R-T | Low | Every hat agent declares a strict JSON schema for its output `{score, confidence, evidence_refs[], reasoning}`. Parsing 100% reliable. Phoenix span captures the structured output cleanly. Audit detector reads structured fields directly, no regex. |
| 3.5 | **Multi-modal (PDF + image) single-call ingestion** | STRETCH | R-T · Q-F | Medium | Currently planned as a separate `ingest-svc` that parses PDF → text → chunks. Alternative: hat agents themselves accept the raw PDF inline (Gemini 3 supports up to 10MB docs) and reference figures by index. Saves a service hop. Risk: longer hat-call latency. Cut if benchmark shows >1.5s slowdown per hat. |
| 3.6 | **Batch prediction API for 524-project corpus seed** | APPLY | (cost, not judging) | Low-Medium | Vertex Batch Prediction submits 524 × 6 hats = ~3,144 requests as a single batch job → ~50% cost reduction + ~70% latency reduction vs sequential. Single-day corpus seed feasible. |
| 3.7 | **Code execution tool (Gemini-native sandboxed Python)** | STRETCH | Q-O · R-Q (★ judges remember this) | Medium | Some Code Grader heuristics (e.g., cyclomatic complexity on sampled functions, dependency-tree linting) can be implemented as Gemini's native code-execution tool inside the Black hat agent rather than as our own Cloud Run Job. "The agent runs Python on the user's repo, live" — memorable. Cut if Vertex code-exec doesn't permit external imports or network. |
| 3.8 | **Grounding with Google Search (Vertex AI Grounding)** | APPLY | R-T · Q-F (web_evidence collection backing) | Low | White hat agent uses Vertex Grounding for A3 (differentiation) and B1 (stack fit) — returns search results that are snapshotted into the `web_evidence` Qdrant collection AND emitted as Phoenix spans with `retrieval.documents` attributes. URLs visible in the report's evidence drill-down. |
| 3.9 | **Citation snapshot — the retrieved URLs visible on screen** | APPLY | Q-UX (★ demo polish) · R-D | Low | When White hat cites a URL in its claim, the report UI shows the favicon + title + source-snapshot timestamp. Compliant with Vertex Grounding's snapshot requirement. Trust-signal. |
| 3.10 | **`responseMimeType: "application/json"` strict enforcement on all hat outputs** | APPLY | R-T | Low | Combined with `responseSchema`, guarantees parseable output. Required for the structured output discipline (3.4). |
| 3.11 | **Long-context "stuff everything in one prompt"** | CUT | (not always better; risks attention dilution) | n/a | Gemini 3 has long context, but our retrieval-augmented approach is more selective and shows vectors doing work. "Stuffing" is the lazy path. |

**Gemini discipline**:
- `thinking_level` per agent tier: Blue=high, Hats=medium, Code-grader/Detector=minimal
- `responseSchema` strictly defined for every structured-output call
- Context cache created once at deploy, referenced by all hat calls
- All Vertex AI calls go through `services/shared/llm.py` adapter (already planned 1.2) which: (a) routes global vs regional endpoint, (b) adds thinking_level, (c) attaches context cache, (d) emits OpenInference span, (e) handles 3-tier fallback per `docs/gcp-setup.md`

---

## §4 — Google ADK best practices

| # | Feature | Decision | Judging payoff | Complexity | Implementation outline |
|---|---|---|---|---|---|
| 4.1 | **`LoopAgent` for AuditLoop (max_iterations=2)** | APPLY | R-T (★ already in wow-moment-design §4) | Low | Built-in idiom. The audit-the-auditor moment depends on this. |
| 4.2 | **`ParallelAgent` for HatsPanel (6 hats run concurrently)** | APPLY | R-T · Q-F (latency) | Low | Sequential 6 hats × ~6s = ~36s. Parallel ~6s. Demo pacing benefits hugely. |
| 4.3 | **Custom `BaseAgent` for `GlasshatRootAgent` (overall orchestrator)** | APPLY | R-T | Medium | Inherits `BaseAgent`, overrides `_run_async_impl`. Controls: Ingest → BluePlanner → HatsPanel → AuditLoop → BMADScorer → ReportAssembler with conditional dispatch. |
| 4.4 | **`MCPToolset` (StdioServerParameters) for Phoenix MCP** | APPLY | R-Arize (★ required for the partner integration) | Low | Already specified in wow-moment-design §5. |
| 4.5 | **`before_tool` / `after_tool` callbacks for instrumentation** | APPLY | R-T (★ rigor signal) | Low | Every tool call (Qdrant query, Vertex search, MCP call) is wrapped by a callback that: emits an OpenInference span with consistent attributes, increments a cost-tracking counter in session state, and logs to Firestore for audit. Discipline > ad-hoc instrumentation. |
| 4.6 | **`before_model` / `after_model` callbacks** | APPLY | R-T · R-Arize | Low | Captures every LLM call's prompt, tokens used, model name, thinking_tokens count. Cost dashboard for the demo. Phoenix automatically captures this via OpenInference, but the callback adds Glasshat-specific attributes (hat name, criterion, audit_iteration). |
| 4.7 | **`before_agent` / `after_agent` callbacks** | STRETCH | R-T | Low | Top-level agent timing. Useful for the demo's "total run time" badge. Cut if redundant with Phoenix root span timing. |
| 4.8 | **ADK session state with persistent backend (Firestore)** | APPLY | R-T · R-D (audit trail) | Medium | Session state persisted to Firestore as a checkpoint document per `run/{id}`. Two human gates (plan approve, score override) write to this state. Enables resume + reproducibility. |
| 4.9 | **Streaming responses (ADK native streaming → SSE)** | APPLY | Q-UX · R-D | Medium | Frontend SSE consumer reads ADK's native event stream rather than a parallel reimplementation. One source of truth for live progress. |
| 4.10 | **ADK Eval framework** | CUT | (overlaps with Phoenix evals; pick one) | n/a | We use Phoenix as the single eval surface (for both judging dimensions and discipline). ADK Eval added without integration would just be duplication. |
| 4.11 | **A2A (Agent-to-Agent) protocol** | CUT | (immature, marginal payoff) | High | Newer Google standard. Documentation thin in May 2026. The 6 hat agents communicate via shared session state, which is cleaner and judge-comprehensible. Re-evaluate post-v1. |
| 4.12 | **ADK Plugins (vs callbacks for safety/permission)** | STRETCH | R-T (modularity signal) | Medium | Docs recommend Plugins over Callbacks for guardrails. For Glasshat: the "must-cite-precedent" rule on Black hat could be a Plugin that intercepts Black's output and rejects if no `evidence_ref` is present, forcing re-generation. Cleaner than callback logic. Cut cleanly if Plugins API documentation is thin. |
| 4.13 | **ADK on Cloud Run deployment template (`gcloud run deploy`)** | APPLY | R-T (Stage 1 pass/fail) | Low | Standard ADK Cloud Run deploy. Containerized; uvicorn or ADK-native server. |

**ADK discipline**:
- Every agent has a `before_*` + `after_*` callback pair where it matters (instrumentation hygiene)
- Custom agents inherit `BaseAgent` and emit structured `Event` objects throughout `_run_async_impl`
- Session state schema versioned and documented in `services/pipeline-orchestrator/SCHEMA.md`

---

## §5 — Cross-cutting decisions

| # | Decision | Owner | Why |
|---|---|---|---|
| 5.1 | OpenInference semantic conventions everywhere | Phoenix auto-instrumentation + custom callback layer | Rich Phoenix UI, free judging signal |
| 5.2 | All retrieval (Qdrant + Vertex Grounding) emits `retrieval.documents.{n}.document.content` span attributes | Custom span wrapper in `services/shared/qdrant.py` + Vertex adapter | Vector retrieval visible in traces; satisfies Qdrant "material vector use" + Arize observability |
| 5.3 | All scores emit `glasshat.score.{hat}.{criterion}` span attribute | BMAD scorer | Phoenix Online Eval (2.3) targets these via filter |
| 5.4 | All human overrides emit Phoenix Annotations | Frontend → backend annotation endpoint | Closes calibration loop |
| 5.5 | Cost tracking dashboard (token counts × model rates) in demo UI | After-model callback (4.6) | "Production-ready cost discipline" badge |
| 5.6 | All MCP calls wrapped to emit span + Glasshat-prefixed attributes | MCP toolset wrapper | Phoenix MCP calls visible in Phoenix itself — meta-loop visible |
| 5.7 | Schema versioning on every persistent surface (Qdrant collections, Phoenix datasets, Firestore docs) | All shared modules | Demonstrates engineering rigor |

---

## §6 — Summary tables

### §6.1 APPLY list (must be in v1)

**Qdrant (8)**: 1.1 hybrid+RRF · 1.2 weighted RRF · 1.3 Recommendation API ★ · 1.5 Group-by · 1.6 payload filtering · 1.7 Scalar Quantization

**Phoenix (9)**: 2.1 OpenInference auto-instrument · 2.2 semantic conventions · 2.3 Online Evals ★★ · 2.4 Custom evaluators · 2.5 Datasets · 2.6 Experiments + MCP ★ · 2.7 Annotations · 2.9 built-in templates · 2.11 self-host fallback

**Gemini (8)**: 3.1 thinking_level · 3.2 thinking tokens visible · 3.3 context caching · 3.4 responseSchema · 3.6 batch prediction · 3.8 grounding · 3.9 citation snapshot · 3.10 strict JSON mime

**ADK (8)**: 4.1 LoopAgent · 4.2 ParallelAgent · 4.3 Custom BaseAgent · 4.4 MCPToolset · 4.5 before/after tool · 4.6 before/after model · 4.8 session state Firestore · 4.9 native streaming + 4.13 Cloud Run deploy

**Total APPLY = 33 advanced features** distributed across the stack.

### §6.2 STRETCH list (build if Phase 1/2 schedule permits)

- 1.4 Discovery API (3D graph guided exploration)
- 1.8 Multi-vector points (ColBERT re-rank)
- 1.10 Cross-collection lookup
- 2.8 Prompt versioning
- 2.10 Agent trajectory evaluator
- 3.5 Multi-modal single-call ingestion
- 3.7 Code execution tool (the "agent runs Python live" feature)
- 4.7 before/after agent callbacks
- 4.12 ADK Plugins for guardrails

### §6.3 CUT list (explicitly out of v1)

- 1.9 DBSF (RRF sufficient)
- 1.11 Snapshots/HA/sharding (operational, not judging)
- 3.11 Long-context stuffing (anti-pattern for retrieval-augmented design)
- 4.10 ADK Eval framework (overlaps Phoenix evals)
- 4.11 A2A protocol (immature, marginal payoff)

---

## §7 — Judging-axis coverage map

For each judging axis, which APPLY-tier features score on it. Multiple features per axis → robust scoring.

### Qdrant axes

| Axis | APPLY features that score |
|---|---|
| **Functionality** | 1.1 hybrid · 1.2 weighted RRF · 1.5 group-by · 1.6 payload filter · 1.7 quantization · 3.8 grounding · 2.6 experiments · 4.1-4.4 agent topology · 4.8 session state |
| **Originality** | **1.3 Recommendation API ★** · **2.3 Online Evals ★★** · **2.6 Experiments + MCP ★** · 1.7 quantization · 3.7 code-exec (stretch) · the **524 Gemini 3 corpus narrative** (covered in §3.4 max-wins-plan) |
| **User Experience** | **3.2 thinking tokens visible ★** · **3.9 citation snapshot ★** · 4.9 streaming · 2.7 annotations (human gates) · 3D graph (covered in `max-wins-plan` §2.1) |

### Rapid Agent / Arize axes

| Axis | APPLY features that score |
|---|---|
| **Tech Implementation (tie-break #1)** | 1.1 hybrid · 1.5 group-by · 1.7 quantization · **2.1-2.9 Phoenix stack ★★** · **3.1 thinking_level ★** · 3.3 context caching · 3.4 responseSchema · 3.6 batch · **4.1-4.6 ADK stack ★** · 4.8 session state · 4.13 Cloud Run |
| **Design** | 3.2 thinking visible · 3.9 citation snapshot · 4.9 streaming · 2.7 annotations · 3D graph |
| **Potential Impact** | 524-corpus calibration (proves it works on real data) · human gates (responsible AI) · multi-modal support |
| **Quality of Idea** | **1.3 Recommendation API as anti-pattern retrieval ★** · **2.3-2.6 Phoenix self-improvement loop ★★** · **3.7 code execution (stretch) ★** · meta-evaluation thesis as a whole |
| **R-Arize bonus (self-improvement loop)** | **2.3 Online Evals ★★** · **2.4 Custom evaluators** · **2.6 Experiments + MCP ★** · **2.7 Annotations (human feedback closes the loop)** |

Every axis has **≥4 APPLY features** scoring on it. Stage 1 pass/fail is hard-gated by 2.1 (OpenInference), 4.4 (Phoenix MCP), 4.13 (Cloud Run), 3.4 (Gemini), 4.1+4.2+4.3 (multi-agent orchestration).

---

## §8 — Updated PLAN.md additions

To `PLAN.md` §9 "Next work" (and `panelyst/PLAN.md` Phase 1 sequence) — add these sub-phases informed by this matrix:

| Sub-phase | New requirement |
|---|---|
| 1.2 LLM adapter | Add thinking_level (3.1) routing, context cache (3.3) attach, batch (3.6) submit mode, structured output (3.4 + 3.10) enforcement |
| 1.3 Qdrant docker-compose + 6 collections | Each collection's schema YAML pre-specifies hybrid (dense+sparse) vectors (1.1), payload index list (1.6), quantization config (1.7), group-by support (1.5) |
| 1.4 Phoenix integration | Auto-instrument (2.1) + semantic conventions (2.2) + Online Eval Task creation script (2.3) + Custom evaluator skeleton (2.4) + Dataset+Experiment scaffolding (2.5, 2.6) + Annotations endpoint (2.7) + self-host docker-compose (2.11) |
| 1.9 Pipeline orchestrator | Custom BaseAgent (4.3) + ParallelAgent (4.2) + LoopAgent (4.1) + MCPToolset (4.4) + all four callback types (4.5-4.7) + session state Firestore (4.8) + native streaming (4.9) |
| 1.10 Next.js frontend | Streaming consumer (4.9 backed) + thinking-trace panel (3.2) + citation snapshot UI (3.9) + cost dashboard (5.5) + human gate annotations submit (2.7) |
| 1.12 Corpus scrape | (unchanged from wow-moment-design §6) |
| 1.13 Calibration experiment | Phoenix Online Eval Task created + Custom evaluator runs over 524 corpus + Experiment computed + held-out validation (wow-moment-design §6.5 K) |

---

## §9 — What this changes vs the prior plan

Before this Apex Pass, `PLAN.md` + `docs/max-wins-plan.md` + `docs/wow-moment-design.md` named **~15 features**. After this Apex Pass: **33 APPLY-tier features + 9 STRETCH + 5 explicit CUTs = 47 explicit feature-level decisions**.

The Wow/Kick distribution is also denser (covered in next deliverable — `docs/max-wins-plan.md` §5 rewrite). The audit-the-auditor moment becomes:
- Phoenix-native (Online Eval Task runs on Yellow's span)
- Recommendation-API-driven (anti-pattern retrieval, not plain similarity)
- Thinking-token-visible (Blue planner reasons in public)
- Cost-tracked (badge in corner shows token spend)
- Annotation-closed (override emits Phoenix annotation that feeds future calibration)

That is technical apex.

---

*Last updated: 2026-05-14 KST. Authoritative on advanced feature decisions for Glasshat v1. Companion: `docs/max-wins-plan.md` (strategy), `docs/wow-moment-design.md` (audit moment), `PLAN.md` (engineering inventory).*
