# P13 — The Data Nerd

## 6-tuple

```json
{
  "id": "P13",
  "advocate": "The Data Nerd",
  "framing": "Glasshat is not a feel-good auditor — it is a calibration experiment. Every claim of 'less biased' must reduce to a measurable delta (ECE, Spearman, bias-flip rate, anchor cosine) on the 503-project Gemini 3 corpus with confidence intervals.",
  "target_persona": "Evaluation-rigor reviewers (Arize ML leadership, Qdrant DevRel, academic LLM-judge researchers) who will distrust any number that lacks a CI, a methodology footnote, or a reproducibility hash.",
  "primary_surface": "Distill.pub-style scrollytelling research note. KPI strip + headline calibration chart + funnel of 503 → 17 audit triggers → 12 score corrections + cohort tables + bias-delta histogram + ECE reliability diagram + Spearman scatter + ROC + posterior shift. Dashboard density throughout, no marketing chrome.",
  "opus_4_7_capability": "Opus 4.7's 1M context lets the Blue planner hold the full 503-row anchor table + 17-item rubric + per-hat trace in working memory, so the audit-loop can compute calibration deltas (Δscore, ECE, Spearman) against the full corpus in one pass instead of retrieval-and-summarize hops.",
  "mvp_scope": "Day 4 demo = ONE chart that decides the room: reliability diagram (predicted-vs-actual win probability) for vanilla LLM-judge vs Glasshat-audited, on the 503 corpus, with 95% bootstrap CI bands. Everything else (ROC, posterior, anchor cosine) renders on the demo page but the hero is the calibration delta.",
  "one_liner_pitch": "An evaluation paper masquerading as a product page: every Glasshat claim is a chart, every chart has a CI, every CI is reproducible from the 503 corpus.",
  "spec_alignment_notes": "all fields populated, followed spec verbatim — analytics-first persona maps cleanly onto Glasshat's measurable thesis (calibration delta vs vanilla LLM-judge); did not invade Designer (visual hero) or Storyteller (narrative arc) territory."
}
```

## ASCII wireframe — landing.html

```
+============================================================+
|  GLASSHAT · technical report v0.3 · 2026-05-17 · 503 N    |
|  [methodology] [dataset] [metrics] [limits] [repro]        |
+============================================================+
|                                                            |
|  GLASSHAT REDUCES LLM-JUDGE CALIBRATION ERROR BY 38%       |
|  Measured on the 503-project Gemini 3 corpus, vs a         |
|  vanilla Gemini-3.1-Pro judge baseline. 95% bootstrap CI.  |
|                                                            |
|  [KPI strip — 4 cards, each with point estimate + CI]      |
|  ECE 0.18→0.11   Spearman .42→.71   Bias-flip 23%→8%      |
|                                                            |
+============================================================+
|  FIG 1 · HEADLINE — Reliability diagram                    |
|  (predicted win-prob vs empirical win-prob, 10 bins)       |
|                                                            |
|   1.0 ┤                                       perfect──┐   |
|       │                              ●─── glasshat ╱   |   |
|   0.5 ┤                  ●─────●            ╱           |   |
|       │     ●───●─── vanilla judge      ╱               |   |
|   0.0 ┤────●                       ╱                    |   |
|       └─────────────────────────────────────            |   |
|         0.0   0.2   0.4   0.6   0.8   1.0  predicted    |   |
|   shaded = 95% bootstrap CI, n=503, 1000 resamples       |
+============================================================+
|  §1 METHODOLOGY                                            |
|  Pipeline · split · baselines · evaluator panel · ECE def  |
|                                                            |
|  §2 DATASET — 503 Gemini 3 corpus                          |
|  [stratification table: 13 winners / 490 non-winners]      |
|  [built-with frequency bar chart, top 15]                  |
|                                                            |
|  §3 METRICS                                                |
|  3.1 Precision@K (table, K=1,5,10,25,50)                   |
|  3.2 Spearman ρ (scatter: judge score vs Devpost rank)     |
|  3.3 ECE reliability diagram (full version, 15 bins)       |
|  3.4 Bias-flip histogram (delta per audit trigger)         |
|                                                            |
|  §4 LIMITATIONS                                            |
|  - corpus is gallery-truncated (503 of ~700)               |
|  - winner label is binary, not ordinal                     |
|  - no inter-annotator agreement available                  |
|                                                            |
|  §5 REPRODUCIBILITY                                        |
|  seed=42 · rubric_schema_hash=sha256:a3f1… · model         |
|  versions pinned · scripts/seed-past-evals.py              |
+============================================================+
```

## ASCII wireframe — demo.html

```
+============================================================+
|  GLASSHAT · LIVE AUDIT · submission #418 (Globot)          |
|  t=00:00  step 1/5  ●○○○○                                  |
+============================================================+
|  [left panel: scrubber + step legend]                      |
|  [right panel: changes per step]                           |
|                                                            |
|  STEP 1 · ANCHOR RETRIEVAL                                 |
|    histogram of cosine(query, past_evals)                  |
|    n=503 bars, vertical line at p25/p50/p75                |
|    top-12 anchors selected (shaded region)                 |
|                                                            |
|  STEP 2 · PANEL SCORE (6 hats)                             |
|    box-plot per hat, raw sub-scores                        |
|    Black hat outlier flagged (z=2.3)                       |
|                                                            |
|  STEP 3 · BIAS DETECTION → ROC                             |
|    Phoenix LLM-judge + Custom + Black counter              |
|    ROC AUC = 0.84 [0.79, 0.88]                             |
|    operating point shown                                   |
|                                                            |
|  STEP 4 · SCORE CORRECTION → POSTERIOR                     |
|    prior (panel raw) vs posterior (anchor-shrunk)          |
|    two overlapping density curves, Δμ = -2.4               |
|                                                            |
|  STEP 5 · 3D CONSTELLATION                                 |
|    scatter (PCA-2D projection) + density contours          |
|    submission point + 12 anchors + 491 background          |
|                                                            |
|  [bottom: trace table — every number reproducible]         |
+============================================================+
```
