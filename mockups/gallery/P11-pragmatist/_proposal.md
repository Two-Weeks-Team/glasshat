# P11 — The Pragmatist · Proposal

## 6-tuple

```json
{
  "id": "P11",
  "advocate": "The Pragmatist",
  "framing": "Glasshat's hardest problem isn't visual wow — it's passing TWO Stage 1 checklists on two different submission days without missing a single box. Build the submission first, the product second.",
  "target_persona": "The Two-Weeks-Team engineer at 22:30 on 2026-05-31, ten hours from the Qdrant deadline, who needs every checklist row to be visibly green and every partner-tech call to have a file:line anchor.",
  "primary_surface": "Plain Next.js + Postgres + Docker. Vanilla HTML mockups. No CDN, no Three.js in the critical path (3D is optional progressive enhancement; 2D radar is the default). shadcn-registry / docs-page layout — left sidebar + sticky topbar + content. System font stack. Three-year-old stack on purpose.",
  "opus_4_7_capability": "Long-context rubric-faithful synthesis — Opus 4.7 holds the full 1000-line max-wins-plan §6.1+§6.2 checklists, the README claims, and the repo file:line evidence in working memory at once, producing a landing page where every cell of the compliance table is provably backed by a real artifact, not a marketing claim.",
  "mvp_scope": "Two HTML files: (1) landing.html = sidebar + sticky topbar + hero + dual compliance tables + stack/license/evidence sections; (2) demo.html = recycled v0.3 timeline stripped to text + a 2D radar SVG + an MCP/Qdrant call panel with file:line anchors. Demoable in 4 days because no JS framework is required.",
  "one_liner_pitch": "A docs-page-style submission status board where every Stage 1 checklist row is green or pending, every partner-tech call has a file:line anchor, and 3D is optional.",
  "spec_alignment_notes": "idea.spec.json not present in runs/ at invocation time; treated upstream as null. Interpretation: target_persona pinned to the submitting engineer (not the end-user judge) because the brief's explicit goal is 'submission-ready'; primary_surface pinned to vanilla HTML + 3-yr-old stack per persona bias 'ship today'; opus_4_7_capability framed as long-context checklist-faithful synthesis, the cheapest valuable Opus use. All other fields followed the brief verbatim."
}
```

## ASCII layout — landing.html

```
+--------------+-----------------------------------------------------------+
| Glasshat     | Glasshat — Submission Status      [Apache-2.0] [public]   |
| v0.4         +-----------------------------------------------------------+
|              |                                                           |
| Overview     |  +-----------------------------------------------------+  |
|  Summary*    |  | Glasshat                                            |  |
|  Demo video  |  | A six-perspective AI panel that scores deck+repo... |  |
|  Try/Source  |  | [Try it]  [Source]  [Watch 3-min]  [License A-2.0]  |  |
|              |  | +---------------------------------------------+     |  |
| Compliance   |  | |              [ video embed slot ]           |     |  |
|  Qdrant      |  | +---------------------------------------------+     |  |
|  Rapid/Arize |  +-----------------------------------------------------+  |
|  Stack       |                                                           |
|              |  Submission readiness                                     |
| Evidence     |  +------------------------+  +------------------------+   |
|  Repo refs   |  | Qdrant VSD             |  | Rapid Agent / Arize    |   |
|  License     |  | [====      ] 6/11 ok   |  | [====     ] 7/14 ok    |   |
|              |  +------------------------+  +------------------------+   |
| Pages        |                                                           |
|  Demo →      |  ## Qdrant VSD — Stage 1 checklist                        |
|              |  # | Requirement                  | Status | Evidence    |
|              |  1 | Public GitHub repo           | PASS   | gh:...      |
|              |  2 | README + lineage             | PASS   | README:1-179|
|              |  3 | Demo video ≤3 min            | PEND   | Phase 5     |
|              |  ...                                                      |
|              |                                                           |
|              |  ## Rapid Agent — Stage 1 checklist                       |
|              |  # | Requirement                  | Status | Evidence    |
|              |  6 | Gemini 3 + ADK + Phoenix MCP | PASS   | spikes/01-03|
|              |  7 | OpenInference + self-improve | PASS   | spikes/01   |
|              |  ...                                                      |
|              |                                                           |
|              |  ## Stack & deps          ## Repo evidence (file:line)    |
|              |  ## License & lineage     ## Why this page is boring      |
+--------------+-----------------------------------------------------------+
```

## ASCII layout — demo.html

```
+--------------+-----------------------------------------------------------+
| Glasshat     | Glasshat — Demo Timeline   [Qdrant 2:58] [Arize 2:57]    |
| demo · v0.4  +-----------------------------------------------------------+
|              |  Same engine. Two narrations. Same boring HTML.           |
| ← Submission |                                                           |
| Demo*        |  [Compliance ping: Qdrant ✓ Phoenix MCP ✓ Gemini 3 ✓ ...] |
|              |                                                           |
| Timeline     |  runtime ████████████░░░░░░░░  $0.041 · 26K tok           |
|  0:00 Hook   |  0:00 ─ 0:30 ─ 1:00 ─ 1:30 ─ 2:00 ─ 2:30 ─ 3:00           |
|  0:10 Ingest |                                                           |
|  0:30 Panel  |  0:00 │ Hook: "Who audits the AI evaluator?"              |
|  1:00 Detect |  0:10 │ Ingest → qdrant.upsert pitch + repo · RRF          |
|  1:30 MCP    |  0:30 │ 6 hats parallel · Yellow A1=9.0 ⚠ · responseSchema|
|  1:45 Fix    |  1:00 │ Phoenix Online Eval fires → over_confident 0.31   |
|  2:30 Anchor |  1:30 │ phoenix.mcp.call("get-experiment-by-id") ×3       |
|  2:50 Close  |       │ qdrant.recommend(...) → anti-pattern anchors      |
|              |  1:45 │ Score self-corrects 9.0 → 7.6                     |
| Anchors      |       │ +-----------------+  +-----------------+          |
|  File:line   |       │ |  BMAD radar     |  |  BMAD radar     |          |
|  2D fallback |       │ |   before (red)  |  |   after (green) |          |
|              |       │ |   78/100        |  |   71/100        |          |
|              |       │ +-----------------+  +-----------------+          |
|              |       │ (3D optional — ?view=2d for ship-today)           |
|              |  2:30 │ qdrant.search_groups past_evals (503 projects)    |
|              |       │ "ranks similar to · weaker than · stronger than"  |
|              |  2:50 │ Tagline + Apache-2.0 frame                        |
|              |                                                           |
|              |  ## Repo evidence map (file:line anchors)                 |
|              |  Phoenix MCP    → agents/audit_loop.py:88                 |
|              |  Qdrant         → packages/shared/qdrant.py:42            |
|              |  ADK Parallel   → services/.../main.py:54                 |
|              |  ...                                                      |
+--------------+-----------------------------------------------------------+
```

## Design choices (the boring ones)

| Decision | Why |
|---|---|
| Sidebar + topbar layout | Three-year-old SaaS convention. Graders parse it without thought. |
| 2D radar SVG default | WebGL fails on ~5% of judge laptops. Don't bet the submission on Three.js. |
| File:line anchors everywhere | Graders verify in 90 seconds, not 9 minutes. |
| `gh repo view --json licenseInfo` snippet | Proves Apache-2.0 is detectable in About sidebar without making the grader open a browser. |
| No animations | Removes one entire class of demo-day failure. |
| OKLCH colors only | Persona convention; also 2026-current and works without color-management surprises. |
| ≤90 KB total | Loads on the conference Wi-Fi. |

## Differentiation note

vs P02 The Designer — they will build a hero with motion and bento; this is a docs page on purpose.
vs P15 The Engineer — they will show architecture diagrams; this shows checklist rows.
vs P22 The Visionary — they will pitch the 10-year future; this pitches "ship Friday."
