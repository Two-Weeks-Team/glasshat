# P25 · The AI-Native — Proposal

## 6-tuple

```json
{
  "id": "P25",
  "advocate": "The AI-Native",
  "framing": "Judges who evaluate AI products ARE LLM-ops engineers. Show them the agent runtime they already trust (Phoenix Cloud trace tree, OpenInference span attributes, MCP tool chain) and the audit-the-auditor moment lands as observable telemetry — not a sales pitch.",
  "target_persona": "LLM-ops / agent engineer judge who lives in Phoenix + Langfuse + Vercel AI dashboards; reads span trees faster than prose; trusts a product when its instrumentation is legible.",
  "primary_surface": "Phoenix Cloud trace UI replica (3-pane: span tree · waterfall+topology+JSON+hat streams · attribute inspector). Calibration query console (typed @-mention command surface, NOT a chatbot) is secondary on landing. Structured forms appear nowhere.",
  "opus_4_7_capability": "Long-context structured reasoning over an entire agent trace tree — Opus 4.7 simultaneously authors realistic OpenInference span attributes, ADK topology with correct LoopAgent/ParallelAgent semantics, four parallel MCP tool calls with believable args/returns, and a deterministic clip() calibration policy — all numerically consistent across landing.html and demo.html (yellow.A1: 9.0 → 7.6, mean_delta -1.2, anchors p25=7.4 / p75=7.9).",
  "mvp_scope": "4-day demo: (1) Phoenix trace replica with the actual 47-span tree of one Glasshat run wired to clickable detail pane; (2) live-streaming generative UI panel that mock-emits scores then self-corrects; (3) calibration query console that streams a structured verdict JSON (not prose) on Run.",
  "one_liner_pitch": "Glasshat as instrumented agent runtime — judges open a familiar Phoenix trace and watch the panel catch its own bias with four MCP calls and a clip() policy, live.",
  "spec_alignment_notes": "framing=spec verbatim (artifact-ingesting eval pipeline + live fairness monitor, not chatbot — Qdrant rule honored: command palette is typed-intent-against-run, not assistant). target_persona narrowed from spec's broad 'judge' to LLM-ops engineer specifically because Rapid Agent + Arize judges are observability natives. primary_surface chose Phoenix UI replica because spec § says 'judges who use Phoenix recognize home'. opus_4_7_capability picked long-context structured-reasoning because the trace tree + span attrs + MCP chain + JSON mutation must stay numerically self-consistent across 2 files (cross-file consistency is the load-bearing trick)."
}
```

## ASCII wireframes

### landing.html

```
+---------------------------------------------------------------------------+
| ◈ Glasshat / agent   Docs Traces Rubrics      ● live  v0.3  [⌘K Run]      |
+---------------------------------------------------------------------------+
|                                                                           |
|  v0.3 · ADK · Phoenix MCP                  +---------------------------+  |
|                                            | ● ● ●  audit_loop iter 1  |  |
|  The agent that                            +---------------------------+  |
|  audits the judge.                         | ⚪ White ███████░░  8.2   |  |
|                                            | 🔴 Red    █████░░░░  6.4   |  |
|  An autonomous evaluation pipeline. ...    | 🟡 Yellow ██████░░░  9̶.̶0̶→7.6|  |
|                                            | ⚫ Black  ██████░░░  7.1   |  |
|  [▶ Run on submission] [⌘K palette]        | 🟢 Green  ████████░  7.9   |  |
|                                            | 🔵 Blue   ████████░  7.8   |  |
|  gemini-3.1-pro · google-adk · phoenix     | tokens: [blue.synth]      |  |
|  mcp · qdrant hybrid+rrf                   |  → mcp.call(get-exp...)▌  |  |
|                                            +---------------------------+  |
+---------------------------------------------------------------------------+
| (scroll-driven 5-step explainer)         | STICKY PHOENIX TRACE PANEL  |  |
| 01 synthesize   rubric becomes data      | ▾ GlasshatRoot     14.20s   |  |
| 02 panel        6 hats parallel + tools  |   ▾ HatsPanel      4.92s    |  |
| 03 detect       triple-redundant         |     yellow.A1  [FLAG] 2.04s |  |
| 04 consult      4 MCP calls in parallel  |   ▾ AuditLoop      5.81s    |  |
| 05 correct      score self-corrects 9→7.6|     phoenix.online_eval ⚠   |  |
|                                          |     mcp ✕ 4 calls           |  |
|                                          | [span detail: OpenInference]|  |
|                                          |   glasshat.evidence.depth=  |  |
|                                          |     0.31 (< threshold 0.40) |  |
+---------------------------------------------------------------------------+
| CALIBRATION QUERY CONSOLE (not a chatbot — typed intents)                 |
| +---------------------------+  +---------------------------------------+ |
| | @audit why was yellow.A1  |  | model · gemini-3.1-pro · thinking high| |
| |   corrected 9.0 → 7.6?    |  | event inconsistency_flagged           | |
| |   show @anchors @phx.delta|  | event phoenix_consultation            | |
| | scope: run/7af9c2…  [Run↵]|  | event score_corrected                 | |
| +---------------------------+  | { "score": {"before":9.0,"after":7.6}}| |
| try: @anchors  @variance  @trace  @override                              | |
+---------------------------------------------------------------------------+
```

### demo.html (Phoenix Cloud replica)

```
+---------------------------------------------------------------------------+
| 🦅 Phoenix · glasshat-prod   projects/glasshat-prod/traces/7af9c2…  ●live |
+---------------------------------------------------------------------------+
| [Spans 47] [Datasets 3] [Experiments 1] [Prompts] [Evaluators 2] [Anno 3] |
+----------------+----------------------------------+-----------------------+
| FILTER ⌕ ...   | TOPOLOGY                         | YellowAgent.score·A1  |
| SPAN TREE      | ┌──────┐  ┌─Parallel[6]─┐ ┌Loop┐ | [attrs][I/O][events]  |
| ▾ Root  14.20s | │Root  │→ │  W R Y K G B│→│aud │ | openinference         |
|   Ingest 740ms | └──────┘  └─────────────┘ └────┘ |  span.id   ...ylw_a1  |
|   Rubric 1.81s |               ↓ flag ↘             |  llm.model_name      |
|   Blue   820ms |                  MCPToolset       |    gemini-3-flash    |
| ▾ HatsPanel    +----------------------------------+  token.count 2041/318 |
|   white  2.10s | WATERFALL  (47 spans · 14.20s)   | glasshat              |
|  [Y]ellow 2.04s|  Root      ████████████████████  |  hat: yellow          |
|   black  2.81s |  Ingest    █░                    |  criterion: A1        |
| ▾ AuditLoop    |  Rubric    ░██                   |  score.predicted: 9.0 |
|   Inconsist.   |  HatsPanel ░░░░██████            |  evidence.depth: 0.31 |
|   ▾ Phx Cons.  |  yellow    ░░░░░░██[flag]        | annotations · 3       |
|     mcp×3      |  AuditLoop ░░░░░░░░░░██████████  |  [over_confident]     |
|     qdrant.rec |  mcp×4     ░░░░░░░░░░░▏▏▏▏       |  [evidence_low]       |
|   Calibrate    |                                  |  [missing_metric]     |
|   BMAD  1.92s  | HAT REASONING STREAMS (gen tok)  | mcp tool calls        |
|   Report 180ms |  ⚪W: evidence found n=4 d=0.74  |  get-experiment-by-id |
|                |  🟡Y: TAM=$2.1B...BUT depth=0.31▌|   210ms · 200         |
|                |  ⚫K: counter-claim missing met. |  get-span-annotations |
|                |                                  |  get-dataset-examples |
|                | SCORE · LIVE MUTATION  ●applying |  qdrant.recommend     |
|                | {"score": 9̶.̶0̶ → 7.6,            |   190ms · 3 hits      |
|                |  detection:[...],                |                       |
|                |  consultation:{mean_delta:-1.2}, |                       |
|                |  anchors:[g3-0214,g3-0177,...]} |                       |
+----------------+----------------------------------+-----------------------+
```

## Why this lands

1. **Familiarity is rapport** — Arize judges open the demo and see their own product's UI. Trust is zero-cost.
2. **Non-chatbot per Qdrant rule** — the only typed surface is a structured query console that emits JSON, not prose. The MCP tool chain is the protagonist.
3. **Numerically consistent** — yellow 9.0→7.6, mean_delta −1.2, anchors 7.4/7.6/7.9, 4 MCP calls in 800ms — match across both files and the README's wow-moment spec verbatim.
4. **Generative UI, not generative chat** — score bars stream, JSON mutates with strike-through patches, hat reasoning tokens type out with carets. The "stream" is structured state changing, not assistant turns.
