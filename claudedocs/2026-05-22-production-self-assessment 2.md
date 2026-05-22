# Glasshat — Production-Grade Self-Assessment (2026-05-22)

> Scope: bring Glasshat to submission-ready, production-grade. Assessment surfaces
> PASS/FAIL + evidence for three axes: (a) visual wow, (b) orchestration role
> effectiveness + AX span separation, (c) input→output flow with live real-Gemini
> RunRecord. FAIL gaps are closed in per-phase PRs this session.
>
> **Baseline gates (clean tree, `main`, before changes):** Python — ruff ✅ /
> ruff-format ✅ / mypy ✅ (34 files) / pytest **152 passed, 97.73 % cov** (≥90
> gate). Web — eslint ✅ / tsc ✅ / vitest **40 passed** / next build ✅ (4 routes).
> Live — `/health` 200, `/ /judge /participate` 200.

## Round 1 — initial assessment (as found)

| # | Axis | Verdict | Evidence | Gap → action |
|---|------|---------|----------|--------------|
| a | Visual wow (Lighthouse ≥90 all pages) | **PASS** (documented), re-verify pending | `claudedocs/2026-05-22-design-elevation-verification.md`: landing 90/95/96 desktop · 95/95/96 mobile; `/judge`,`/participate` 100/96/96. Live routes 200. | Re-measure Lighthouse on live after redeploy → confirm. |
| b1 | Orchestration — **role effectiveness** of all 6 agents | **PASS** | Code-verified, see "Role evidence" below. All 6 are real implementations (no stubs). | — |
| b2 | Orchestration — **AX span separation** per agent | **FAIL** | `engine.py:run_evaluation` opens explicit `glasshat.*` spans **only** for the 6-hat stage (`hats.py:run_hat` → `tracer.span("hat_assess", glasshat.hat=…, glasshat.criterion=…)`). The other 5 agents (synthesize/plan/audit/score/report) emit SSE events but **no per-agent tracer span** → cannot be isolated by role in Arize AX. | **PR-B**: wrap each engine stage in `tracer.span("stage_<name>", glasshat.agent=…)`. |
| c1 | I→O flow — code path (plan gate→SSE→result→3D→gate2) | **PASS** | `app.py`: `/api/plan` (gate 1) · `/api/evaluate/stream` (SSE, 12 stages incl. audit wow-beats) · `/api/runs/{id}` · `/api/runs/{id}/override` (gate 2). `events.py` Stage enum drives the 3D `graph_reshape`. All real. | — |
| c2 | I→O flow — **live real-Gemini RunRecord on gemini-3.1** | **FAIL** | Current live API runs `gemini-2.5-flash` (forbidden by this session's mandate). `deploy.sh:62` force-pins `gemini-2.5-*`; `llm.py:_get_client` uses `location=google_cloud_region` (us-central1) for **all** calls, ignoring per-tier `*_location="global"` config → 3.x models 404 on the regional endpoint (the documented reason 2.5 was pinned). | **PR-A**: location-aware Vertex client + `deploy.sh` → `gemini-3.1-flash-lite`; redeploy; produce live RunRecord on 3.1. |

### Role evidence (b1) — each agent is a real, distinct implementation

| Agent | File | Role & evidence it is real (not a stub) |
|-------|------|------------------------------------------|
| **RubricSynthesizer** | `agents/.../rubric_synthesizer.py` | Official rules → `SynthesizedRubric`. Path A (preset) + Path D (custom YAML) deterministic & validated; Path B (URL) fetches page then LLM(`tier=pro`) synthesizes YAML, parsed + `model_validate`d, raises `SynthesisError` on bad output. |
| **BluePlanner** | `agents/.../blue_planner.py` | Emits the inspectable `PlanObject` shown at human gate 1: enables 6 hats, scopes every criterion, carries weights + retrieval budget. Deterministic by design (a plan, not a guess). |
| **6-Hat panel** | `agents/.../hats.py` | 6 **distinct personas** (`HAT_PERSONAS`: facts/intuition/optimism/critique/alternatives/synthesis). Each hat × criterion: embed query → hybrid retrieval → LLM(`tier=flash`) with persona prompt → `SCORE: <n>` extraction (real-Gemini) or stable hash (mock). Opens `hat_assess` span w/ `glasshat.hat`+`glasshat.criterion`. |
| **Audit** | `agents/.../audit.py` | Calibration self-correction (spike-D): `new = clip(score − 0.8·mean_delta, p25, p75)` with ±2.0 cap, only fires when `n≥3` and `|mean_delta|≥0.5`. `TableConsultant` (deterministic) **and** `PhoenixMcpConsultant` (live Phoenix calibration over MCP stdio — `adk_runtime.py`) implement the same `Consultant` protocol. |
| **BMADScorer** | `agents/.../bmad_scorer.py` | Substitutes audited (corrected) scores for originals, averages hats per criterion → internal 0-10 → rescales to native `1..scale`; attaches the most impactful audit correction for the report's trail. |
| **ReportAssembler** | `agents/.../report.py` | Weighted-sum vs simple/tie-break aggregation on 0-1 fractions → projects onto display scale (100/5/…) → immutable `RunRecord`. Distinct rubrics over the same hat scores yield legitimately different finals. |

### Shipped-code hygiene grep (named mock/memory excluded)

`grep -rniE "mock|stub|placeholder|todo|fixme" packages services agents apps` (excl. tests) →
**23 matches, all legitimate**: named `mock`/`memory` backend docstrings (explicitly out of scope —
deterministic, not stubs), HTML `<input placeholder="…">` attributes (real UI), and the `"TodoZap"`
judge **demo-seed** label. **Zero unfinished-code markers.** ✅

## Gaps to close this session (per-phase PRs)

1. **PR-A — model migration (closes c2 + model constraint).** Location-aware
   `VertexLlmClient` (per-tier `*_location`, global for 3.x, regional for
   embeddings) + `deploy.sh` → `gemini-3.1-flash-lite` (GA). Redeploy; capture
   live RunRecord on 3.1.
2. **PR-B — orchestration AX span separation (closes b2).** Per-agent
   `glasshat.agent` spans around all 6 stages in `run_evaluation`.
3. **Redeploy + re-verify** (a) Lighthouse on live, (c) `/health`+3 routes 200,
   live RunRecord model = `gemini-3.1-flash-lite`.

_Round 2 (final verdicts after gap closure) is appended at the bottom of this file._
