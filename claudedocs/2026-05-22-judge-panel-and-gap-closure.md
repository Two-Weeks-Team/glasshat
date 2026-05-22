# Glasshat — Pre-Submission Judge Panel + Gap Closure (2026-05-22)

Four **independent third-party judges** (separate sub-agents, adversarial, no sycophancy)
reviewed the live submission. Each produced a score + concrete gap list. This doc records
their verdicts and how each gap was closed (per-phase PRs).

## Panel scores (initial)

| Judge | Score | One-line |
|---|---|---|
| Technical / architecture / observability | **78** | Real 6-agent orchestration + per-agent AX spans + real hybrid retrieval + correct Gemini-3 global-endpoint handling; held back by stale architecture-of-record and a self-correction loop whose data-driven variant isn't the deployed one. |
| Design / UX (visual wow) | **74** | Genuine OKLCH design system + strong landing hero motif, but the two app screens' idle first-paint is an empty admin form — the wow is gated behind a click + API round-trip. |
| Product / story / 5-min comprehension | **72** | Sharp "audit the judge" positioning, works live; but README stale (Phoenix vs AX, old 2.5 run, PRs to #25) and no live-demo runbook. |
| Adversarial skeptic / credibility | **72** | Core claims survive scrutiny; biggest landmine = `docs/architecture.md` self-declaring authority while describing a Qdrant/LangGraph/Firebase/17-item system that never shipped. |

## Convergent findings → gap closures

### PR-C — Documentation truth-pass (docs/template/scripts; no redeploy)
Closes the credibility landmines all four judges flagged:
- **`docs/architecture.md`**: removed the "if code diverges, this doc wins / code is the bug" line; added a **SUPERSEDED** banner with a this-doc-says → shipped-reality table (Qdrant→in-code, LangGraph→ADK, Firebase→no-auth, 17-items→4-criteria, Phoenix→AX, model→gemini-3.1-flash-lite).
- **`README.md`**: Phoenix→**Arize AX** in the lead; added **live model line** (`gemini-3.1-flash-lite`, global endpoint); added a **"Try the live demo (≈60s)"** runbook; honest self-correction framing (deployed = calibrated prior via `TableConsultant`; live-trace variant = `PhoenixMcpConsultant`); PRs **#7–#30** incl. #27/#28; replaced stale run `58f6892c`/64.6 with live `2b2e29c2`/56.93 on 3.1; fresh Lighthouse (92/93/95); labelled the no-cred curl as mock/deterministic.
- **`HANDOFF.md`, `PLAN.md`, `docs/team-onboarding.md`**: SUPERSEDED banners (Qdrant dual-track dropped → single-track Arize, no vector DB) pointing to README + handoff v3.
- **`scripts/real_*_e2e.py`**: replaced forbidden `gemini-2.5-*` with `gemini-3.1-flash-lite` + `GOOGLE_CLOUD_LOCATION=global` (ADK global endpoint).
- **`.env.example`**: added `arize` to `MONITOR_BACKEND`, added `ARIZE_SPACE_ID`, removed the "Gemini 2.5" comment.
- **Hygiene**: removed tracked macOS sync-dups `.coverage 2` / `.coverage 3`; broadened `.gitignore`.
- Dated note on `claudedocs/2026-05-21-real-e2e-evidence.md` (2.5-era snapshot).

### PR-D — Visual-wow elevation (web; redeploy) — see below for status
- `/judge` and `/participate` first paint: ship a pre-evaluated / sample-seeded state so the
  ranked rows, score bars, and self-correction badges are visible before any API round-trip.
- `ScoreBar`: ease the width transition + show the over-confident origin as a faded ghost the
  fill recedes from (make the live "pull-back" visible — it currently snaps).
- Skeleton/shimmer for preset + API-status loading states; hero-sized score/rank numerals.

### PR-E — Technical-kick honesty + depth (backend; redeploy) — see below for status
- Make the default calibration table credible (varied per cell incl. a negative `mean_delta`
  so an **upward** correction is demonstrable) + a test for the upward case.
- Emit a tracer attribute (`glasshat.score_parse_failed`) when a real-LLM hat response lacks a
  parseable `SCORE:` (currently falls back to a hash silently).
- README already reframed so the deployed self-correction is not overstated as live-trace-driven.

## Deferred to handoff next-step (bigger lifts, not blockers)
- Wire `repo_url` → `code-grader` → retrieval into the default pipeline (README implies repo
  evidence flows into scoring; today only `deck_text` is indexed).
- Wire `PhoenixMcpConsultant` into the live API path (vs. exercised only by e2e scripts).
- Wire `weight_aware_anchor` (cross-rubric anchor retrieval) into the audit step.
- Display-font + larger typographic moment on the app screens (design "bigger lift").
