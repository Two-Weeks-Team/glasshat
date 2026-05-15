# RubricSynthesizer — Specification

> **Status**: Locked 2026-05-15 by user. Implements [[glasshat-rubric-and-mode]] decision §13. Full design before code (Phase 1.5 implementation target).
>
> **Position in pipeline**: between IngestAgent and BluePlannerAgent. Output is `rubric.synthesized.yaml` consumed by every downstream agent (Six Hats, BMADScorer, AuditLoop, Anchor retrieval).

---

## §1 — Why this exists

The original Glasshat plan hard-coded BMAD's 17 items × 100 points as the universal scoring shape. That works when the evaluator is BMAD itself, but every real hackathon and grant body publishes its own rubric:

| Domain | Actual rubric (verified 2026-05) |
|---|---|
| Qdrant VSD 2026 | Functionality · Originality · UX (3 axes, equal weight) |
| Rapid Agent / Arize | Tech 40 · Innovation 30 · Impact 20 · Presentation 10 (4 axes, **Tech tie-break #1**) |
| CMUX × AIM Hackathon (Seoul 2026-04) | Track 1: 5 criteria @ 1-5 scale · Track 2: 6 criteria · Track 3: 6 criteria — simple average per portal |
| Gemini 3 Hackathon (Dec 2025-Feb 2026, concluded) | Tech 40 · Innovation 30 · Impact 20 · Presentation 10 |

Forcing BMAD on all of these produces score-domain mismatch — a judge sees "17/100" when their own portal expects "3.4/5 averaged across 5 axes" and the score is structurally non-comparable. The Glasshat thesis demands evaluation that mirrors the actual evaluator.

**Solution**: a `RubricSynthesizer` agent that *parses the official rules* and emits a per-evaluation rubric whose criteria, weights, scales, and tie-break ordering match the source-of-truth rules. BMAD becomes a *vocabulary super-set* — every synthesized criterion is defined as a mapping over 1+ BMAD primitives, preserving fairthon lineage and enabling inter-rubric comparison.

---

## §2 — Inputs

```yaml
EvaluationContext:
  artifact:
    deck_pdf_uri: gs://glasshat-uploads/<run_id>/deck.pdf
    repo_url: https://github.com/<owner>/<name>
  rubric_source:
    # Exactly one of these four:
    preset_id: qdrant | rapid-agent | cmux-aim | gemini3       # Path A — fastest, version-pinned
    rules_url: https://rapid-agent.devpost.com/rules           # Path B — auto-detect via fetch + parse
    rules_pdf_uri: gs://glasshat-uploads/<run_id>/rules.pdf    # Path C — uploaded official rules document
    custom_yaml: <inline>                                      # Path D — user-edited YAML, no synthesis needed
  metadata:
    submitted_to_track: optional[string]                       # e.g. "Track 2: Business & Applications" for multi-track events
    judge_persona: optional[string]                            # e.g. "VC investor" / "academic reviewer" — biases descriptor language
```

The synthesizer dispatches based on `rubric_source` first non-null in the order: preset_id → custom_yaml → rules_url → rules_pdf_uri.

---

## §3 — Output schema (`synthesized.schema.json` excerpt)

```yaml
SynthesizedRubric:
  schema_version: "1.0"                                         # bump if breaking schema change
  rubric_id: <uuid>                                             # unique per synthesis
  rubric_schema_hash: <sha256-of-canonicalized-rubric>          # used for past_evals anchor matching
  source:
    type: preset | url | pdf | custom
    identifier: qdrant | <url> | <gs-uri> | "user-supplied"
    fetched_at: 2026-05-15T07:30:00Z
    source_text_excerpt: "..." # first 1000 chars of source for traceability
  scoring_rule:
    aggregation: weighted_sum | simple_average | tie_break_ordered
    final_scale: 0-100 | 1-5 | 1-7                              # display scale shown to user
  criteria:
    - id: tech-implementation
      label: "Technical Implementation"
      weight: 0.40                                              # null if simple_average
      scale: 1-5                                                # per-criterion native scale
      bmad_mapping: [B1, B2, C1, C2, C3, C4]                    # which BMAD vocabulary primitives this absorbs
      descriptor_levels:                                        # per-score human-readable rubric
        1: "Surface — basic wrapper, no novel engineering"
        2: "Functional — working integration, some custom logic"
        3: "Solid — non-trivial engineering, edge cases handled"
        4: "Impressive — complex architecture, custom protocols"
        5: "Exceptional — publication-worthy depth"
      evidence_required: true                                   # Phase 1 always true; Phase 2 may relax for soft criteria
      source_clause: "Stage 2 axis #1, weight 40%, tie-break first"
      source_excerpt: "Technological Implementation. Quality of the…"  # verbatim quote from rules
    # ... more criteria
  tie_breakers:
    - { order: 1, criterion_id: tech-implementation }
    - { order: 2, criterion_id: design }
    - { order: 3, criterion_id: potential-impact }
    - { order: 4, criterion_id: quality-of-idea }
  threshold_gates:                                              # pass/fail items separate from scoring
    - id: stage-1-required-data
      condition: "Must use Phoenix MCP server at runtime"
      check: manual                                             # or: automated via pipeline assertion
  weights_vector:                                               # canonical numeric vector for cosine-similarity anchor retrieval
    [0.40, 0.30, 0.20, 0.10]                                   # ordered by criterion_id alphabetical for canonical-form
  confidence: 0.92                                              # synthesizer's self-reported confidence, 0-1
  warnings:
    - "Rule mentions 'displayed weight' but says calculation uses simple average — synthesized weights are display-only"
```

The full JSON Schema lives at `packages/rubric/synthesized.schema.json` and is validated at Plan-time via typia (TS) and pydantic (Python).

---

## §4 — The four input paths

### Path A — Preset (recommended for known evaluators)

`packages/rubric/presets/{qdrant,rapid-agent,cmux-aim,gemini3}.yaml`. Hand-curated, version-pinned to `verified_at` date in YAML frontmatter. CI step (`scripts/check-preset-freshness.sh`) re-fetches each preset's source URL weekly and diffs against the response hash; if the rule page changed, opens a tracking issue.

Example skeleton:

```yaml
# packages/rubric/presets/qdrant.yaml
preset_id: qdrant
verified_at: 2026-05-14
source_url: https://try.qdrant.tech/hackathon-vsd
source_excerpt: |
  Functionality · Originality · User Experience.
  1st $5,000 / 2nd $3,000 / 3rd $2,000.
  Submissions that are only chatbots are not allowed.
synthesized:
  schema_version: "1.0"
  rubric_id: <static-uuid-for-preset>
  scoring_rule:
    aggregation: simple_average
    final_scale: 0-100
  criteria:
    - id: functionality
      label: "Functionality"
      weight: 0.333
      scale: 1-5
      bmad_mapping: [C1, C2, C3, C4, C5, B3, B4]
      descriptor_levels:
        1: "Pipeline doesn't run end-to-end"
        2: "Runs but breaks on edge cases"
        3: "Solid end-to-end on golden path"
        4: "Handles edge cases + retries gracefully"
        5: "Production-grade observability + recovery"
      evidence_required: true
      source_clause: "Judging criterion 1 of 3"
    - id: originality
      label: "Originality"
      weight: 0.333
      scale: 1-5
      bmad_mapping: [A1, A3, B1]
      descriptor_levels:
        1: "Recognizable wrapper pattern"
        2: "Familiar pattern with one twist"
        3: "Non-obvious vector use"
        4: "Pattern not seen in 2025 winners"
        5: "Defines a new pattern"
      evidence_required: true
      source_clause: "Judging criterion 2 of 3 — emphasized in landing page hero"
    - id: user-experience
      label: "User Experience"
      weight: 0.333
      scale: 1-5
      bmad_mapping: [D1, D2, D3, D4, A4]
      descriptor_levels:
        1: "Confusing first run, no feedback"
        2: "Works with friction, sparse docs"
        3: "Smooth happy path, helpful errors"
        4: "Thoughtful pacing, demo-able in 60s"
        5: "Memorable beat, dinner-table-retellable"
      evidence_required: true
      source_clause: "Judging criterion 3 of 3"
  threshold_gates:
    - id: non-chatbot
      condition: "Submission must not be a chatbot (no chat-only UX)"
      check: manual
    - id: qdrant-load-bearing
      condition: "Qdrant Vector DB must be material to the pipeline"
      check: automated  # CI assertion: qdrant_search_tool called in ≥1 hat agent
  weights_vector: [0.333, 0.333, 0.333]
  confidence: 1.0  # presets are 1.0 by definition
```

### Path B — Auto-detect from URL

`RubricSynthesizer` agent invoked. Steps:

1. `fetch_url(rules_url)` via `httpx` (15s timeout, 1 RPS).
2. Pass response body (HTML/Markdown) to Gemini 3.1 Pro `thinking_level=high` with the synthesizer prompt (§5).
3. Validate output against `synthesized.schema.json` via typia. If invalid, retry once with strict-mode prompt; if still invalid, fall back to Path D (custom YAML required from user).
4. Cache `(url, last-modified-header) → SynthesizedRubric` in Firestore for 7 days.

### Path C — Auto-detect from PDF

Same as Path B, but Step 1 = Gemini 3 multimodal PDF parse → markdown text → into prompt.

### Path D — Custom YAML

User-supplied YAML conforming to `synthesized.schema.json`. No synthesis; only validation. Useful for organizations with proprietary rubrics.

---

## §5 — Synthesizer prompt (Gemini 3.1 Pro, `thinking_level=high`)

Stored at `agents/rubric_synthesizer/prompt.md`. Full text below (this *is* the spec — the agent is its prompt).

```
You are Glasshat's RubricSynthesizer. Given the official rules text for a
hackathon, grant program, accelerator review, or evaluation board, produce a
SynthesizedRubric YAML object that exactly matches `packages/rubric/synthesized.schema.json`.

Constraints:

1. Every `criterion` you emit MUST cite the source_clause + source_excerpt
   verbatim from the rules text. If you cannot find the verbatim source for
   a weight or descriptor, emit a warning instead of fabricating.

2. Map each criterion to BMAD vocabulary primitives via `bmad_mapping`.
   The BMAD vocabulary is:
     A1 problem clarity · A2 target users · A3 differentiation · A4 market impact
     B1 stack fit · B2 system design · B3 scalability · B4 feasibility
     C1 implementation completeness · C2 code quality · C3 testing · C4 docs
     C5 reproducibility
     D1 demo clarity · D2 storytelling · D3 visual polish · D4 timing
   A criterion can map to multiple primitives; this is the "vocabulary
   super-set" relationship that lets Glasshat compare scores across rubrics.

3. `weights_vector` MUST be in alphabetical-by-criterion-id canonical order
   so cosine similarity is comparable across rubrics.

4. If the source mentions a tie-break order, populate `tie_breakers` exactly
   in the order stated. Tie-break is a structural property; do not infer it
   from weight magnitude.

5. `descriptor_levels` for each criterion MUST cover ALL points on the
   declared scale (e.g., 1, 2, 3, 4, 5 for a 1-5 scale; not just "low/mid/high").
   If the source only provides 3 levels, interpolate the missing 2 with
   `[interpolated]` prefix and add a warning.

6. `threshold_gates` capture pass/fail rules separate from scoring (e.g.,
   "must use Qdrant", "must have public repo", "must include 3-min video").
   Mark `check: manual` unless the rule is structurally automatable.

7. Set `confidence` honestly:
   - 0.95-1.0 = source is unambiguous, all axes have explicit weight + descriptors
   - 0.80-0.94 = some inference required (e.g., descriptors inferred from axis names)
   - 0.50-0.79 = significant inference (e.g., source only lists axes, no scale or weights)
   - <0.50 = refuse and emit warning "Source insufficient for synthesis; user must provide custom YAML"

8. `final_scale` is what the user-facing report displays:
   - If source uses 100-pt or weighted-sum, set 0-100.
   - If source uses N-point scale with simple average, set the native scale.
   - If unclear, default to 0-100 and add warning.

OUTPUT: Pure YAML matching the schema. No commentary, no markdown fence.
```

---

## §6 — ADK agent wiring (Phase 1.5)

```python
# services/rubric_synthesizer/agent.py
from google.adk.agents import LlmAgent
from google.adk.tools.fetch_tool import FetchUrlTool   # built-in
from google.adk.tools.pdf_parse_tool import PdfParseTool # custom wrapper around Gemini multimodal
from glasshat.shared.llm import get_vertex_llm
from glasshat.shared.types import SynthesizedRubric  # typia/pydantic

rubric_synthesizer = LlmAgent(
    name="RubricSynthesizer",
    model=get_vertex_llm(tier="pro", thinking_level="high"),
    instruction=open("agents/rubric_synthesizer/prompt.md").read(),
    tools=[FetchUrlTool(timeout=15, rps=1), PdfParseTool()],
    output_key="rubric_synthesized",
    output_schema=SynthesizedRubric,  # strict typia validation
    before_model_callback=cost_tracking_callback,
    after_model_callback=schema_validation_callback,  # rejects + retries on invalid YAML
)
```

Invocation flow:

```python
# services/pipeline_orchestrator/root_agent.py (excerpt)
async def _run_async_impl(self, ctx):
    yield from ingest_agent.run_async(ctx)
    if ctx.session.state["rubric_source"]["preset_id"]:
        # Path A: load preset directly, skip synthesizer
        ctx.session.state["rubric_synthesized"] = load_preset(
            ctx.session.state["rubric_source"]["preset_id"]
        )
    elif ctx.session.state["rubric_source"]["custom_yaml"]:
        # Path D: validate user YAML, skip synthesizer
        ctx.session.state["rubric_synthesized"] = validate_custom_yaml(
            ctx.session.state["rubric_source"]["custom_yaml"]
        )
    else:
        # Paths B/C: invoke synthesizer
        yield from rubric_synthesizer.run_async(ctx)
    yield from blue_planner.run_async(ctx)
    # ... rest of pipeline
```

---

## §7 — Validation + fallback strategy

### Validation pipeline

1. **Schema validation** (typia/pydantic): every `synthesized` payload must conform to `synthesized.schema.json`.
2. **Source-clause traceability check**: for each criterion, regex-confirm `source_excerpt` appears verbatim in the source text. Mismatch → reject + retry with stricter prompt.
3. **Weights consistency**: if `aggregation: weighted_sum`, `sum(weights) == 1.0 ± 0.01`. If `simple_average`, all weights equal or all null. Mismatch → reject.
4. **Descriptor coverage**: each criterion's `descriptor_levels` covers every integer in `scale`. Missing levels → reject.
5. **BMAD mapping coverage**: every criterion has ≥1 `bmad_mapping` primitive. Empty → reject.

### Fallback ladder

| Failure | Action |
|---|---|
| Schema invalid after 1 retry | Mark `confidence: 0.0`, emit `"synthesis_failed"` warning, escalate to user with raw source text + offer Path D (custom YAML) |
| URL fetch timeout / non-200 | Try once with 30s timeout. Then escalate to user: "Provide rules.pdf upload or custom YAML." |
| PDF parse fails (corrupted, encrypted) | Same escalation; offer URL or YAML path. |
| Source language not English | Attempt synthesis (Gemini 3 multilingual capable). If `confidence < 0.7`, recommend translating + manual review before submission. |

---

## §8 — Past_evals anchor retrieval (downstream consumer)

When AuditLoop's `PhoenixConsultantAgent` retrieves anchor projects from Qdrant `past_evals`, it now uses `weights_vector` cosine similarity:

```python
# services/audit/anchor_retrieval.py (excerpt)
def select_anchors(synthesized_rubric, hat, criterion, evidence_depth_bucket, top_k=3):
    current_weights = synthesized_rubric.weights_vector
    return qdrant.search(
        collection="past_evals",
        query_vector=current_weights,
        query_filter={
            "must": [
                {"key": "hat", "match": {"value": hat}},
                {"key": "criterion_bmad_mapping", "match": {"any": criterion.bmad_mapping}},
                {"key": "evidence_depth_bucket", "match": {"value": evidence_depth_bucket}},
            ]
        },
        # weights_vector stored as named vector "rubric_weights" on each past_eval point
        using="rubric_weights",
        limit=top_k,
        with_payload=True,
    )
```

This means **Glasshat's own seed corpus (503 Gemini 3 projects) is anchored under Gemini 3's weight schema (Tech 0.40 / Inn 0.30 / Imp 0.20 / Pres 0.10), but at runtime evaluating a Qdrant submission (weights `[0.333, 0.333, 0.333]`) Glasshat retrieves the past_evals whose stored weights are *most similar to the current rubric*** — usually the same project re-anchored under different weight assumptions. No per-rubric re-evaluation is needed; the weight vector is the bridge.

---

## §9 — Demo viewport behavior

### Judge mode (Qdrant primary demo)

- Operator selects `preset: qdrant` (or pastes the rules URL).
- All 503 corpus submissions are evaluated against the synthesized rubric in batch.
- Results sorted by Glasshat's predicted score; top-13 highlighted.
- Compare to actual 13 winners → Top-K hit rate metric (target ≥9/13 = 69%).

### Participant mode (Rapid Agent primary demo)

- Participant uploads deck + repo + selects `preset: rapid-agent`.
- Synthesizer outputs the 4-axis Tech/Inn/Imp/Pres rubric with Tech tie-break.
- After Six Hats run, the per-criterion score reveals the **lowest-scoring axis with highest weight × leverage** ("Tech is 4/5 but weighs 40% — improving to 5/5 = +1 final pt").
- Phoenix MCP mid-loop consultation suggests specific README/repo improvements.
- Participant edits → re-runs → score updates live.

### Dual-rubric demo close (both demos)

The same deck+repo is silently scored under TWO rubrics in parallel:

```
   ┌──────────────────────────┬──────────────────────────┐
   │  Qdrant rubric           │  Rapid-Agent rubric      │
   │  Functionality:    4/5   │  Tech Implementation: 5/5│
   │  Originality:      5/5   │  Design:              4/5│
   │  UX:               4/5   │  Impact:              3/5│
   │                          │  Quality of Idea:     5/5│
   │  Final: 4.33/5 = 87/100  │  Final: weighted = 73/100│
   └──────────────────────────┴──────────────────────────┘
   Δ = 14 points. Caption: "Correct rubric-aware variance, not bias."
```

8-second scene; appears at `2:30-2:38` in both demo timelines.

---

## §10 — Source-clause traceability UI

Every synthesized criterion's `source_clause` + `source_excerpt` is shown in the Plan-card UI (gate 1) so the user can verify "is this rubric faithful to the official rules?" before approving the run. Example UI:

```
PLAN PREVIEW (gate 1 — approve to proceed)

Synthesized rubric:                             Source: rapid-agent.devpost.com/rules
                                                Confidence: 0.94 ▓▓▓▓▓▓▓▓▓░

▸ Tech Implementation     weight 40%   tie-break #1
   Source: "Stage 2 axis #1, weight 40%, tie-break first"
   Excerpt: "Technological Implementation. Quality of the GCP + partner interaction…"

▸ Design                  weight 30%
   Source: "Stage 2 axis #2, weight 30%"
   Excerpt: "Design. UX thought-through…"

▸ Potential Impact        weight 20%
   ...

▸ Quality of Idea         weight 10%
   ...

[ Approve & run ]   [ Edit YAML ]   [ Reject & re-synthesize ]
```

This is what makes Glasshat's audit trail defensible — every score traces to a criterion, every criterion traces to a verbatim source clause in the official rules.

---

## §11 — Open questions / future work (V2+)

| Item | Notes |
|---|---|
| Multi-track auto-detect | CMUX×AIM-style multi-track events: synthesizer should ask "which track?" and load that track's sub-rubric only |
| Rubric versioning over hackathon period | If rules amended mid-period, old runs stay anchored to v1 schema_hash; new runs use v2 |
| Per-judge subjective weights | Some grant programs give individual judges latitude on weights; future Path E could load per-judge override |
| Rubric diff visualization | Side-by-side view: "this rubric vs. last hackathon's rubric — what changed" |
| Synthesizer self-improvement | Phoenix Online Eval on RubricSynthesizer's own outputs; if descriptor levels consistently rated low-quality, refine prompt |

---

*Last updated: 2026-05-15 KST. Authoritative on RubricSynthesizer design. Phase 1.5 implementation derives from this spec.*
