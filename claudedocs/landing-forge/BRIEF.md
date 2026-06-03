# Glasshat landing — shared ground truth (WOW scene mockups)

EVERY mockup reads THIS file. Diverge on *form* (the scene-arrival technique + the depicted
moment), never on *facts*.

## ⭐ THE ONE THING (north-star — overrides everything)
> You're watching an AI judge score a project — and then, unprompted, **the judge catches its
> own over-confidence and pulls the score back to where the evidence actually supports**, live,
> with the math shown. The visitor witnesses the correction *happen to* the number, not a UI to
> operate. The feeling: "it audits the judge — including itself."

The moment is a **SCENE** (a vivid depicted instant of self-correction), not a text card. The
page behaves like the audit itself — the over-scored value surfaces, then **recedes to the
calibrated value on its own** when the situation calls it up. The visitor is a **recipient**.

## What Glasshat actually is (facts — do not invent beyond these)
- Rubric-aware AI **evaluation** that "**audits the judge**": it mirrors an evaluator's official
  rules into a per-evaluation rubric, scores with a **six-hat panel** (White / Red / Yellow /
  Black / Green / Blue — de Bono hats), grounds every sub-score in **retrieved evidence**, then
  **self-corrects its own over-confidence** live. It is an evaluation pipeline + a transparent
  fairness monitor — **not a chatbot**.
- **The flagship moment:** an over-confident, low-evidence assessment (typically the YELLOW
  "optimism" hat) is pulled back toward calibrated past evaluations. The correction is real math:
  `clip(score − 0.8·mean_delta, p25, p75)` with a **±2.0 cap**. The calibration prior is recovered
  from **held-out spike-D anchors** (an evidence-bucketed over-confidence delta — strongest where
  evidence is thin).
- **Rank-flip:** on a whole cohort, the audit doesn't just nudge a number — it can change **who
  wins** (a better-evidenced project rises once calibration is applied).
- **3D evaluation constellation:** criteria plotted by score · weight · evidence depth; corrected
  nodes slide from their over-confident origin to the calibrated position.
- **Stack:** **Gemini 3.1 Flash-Lite** on **Vertex AI** (global endpoint) + **text-embedding-005**;
  **Google ADK** orchestration (every agent + hat = its own span); **Arize AX** observability +
  **Phoenix-MCP** calibration loop (wired). **No vector database** — in-code hybrid retrieval
  (Vertex embeddings + cosine + BM25 + RRF). Two viewports on one engine: **/judge** (batch rank +
  rank-flip) and **/participate** (single submission + live self-correct).
- **Emotional truth:** every hackathon / grant / promotion runs on judgment nobody audits. AI
  judges make it worse — confident, fast, unaccountable. Glasshat is the missing audit layer.

## ⛔ HONESTY — do not reintroduce fabricated numbers (a judge greps this)
- **NEVER** claim "503 held-out anchors" or "4,493 submissions" drove the calibration. The runtime
  prior is the evidence-bucketed **spike-D** delta. Say "a calibration prior recovered from held-out
  spike-D anchors" — nothing about 503/4,493.
- Live model is **gemini-3.1-flash-lite** (Gemini 2.5 is NOT used). No Qdrant (the "Qdrant" preset
  is *judged content*, not a dependency).
- The Phoenix-MCP learning loop is **wired + E2E-verified**; the credential-free live image runs the
  deterministic spike-D prior. Don't claim a live MCP call the deploy isn't making.
- Illustrative scores/ranks in the scene must be labeled illustrative; no invented precision/% claims.

## Hard rules (every mockup MUST obey)
1. **Bring a SCENE before the eyes** — a vivid, full-bleed depicted moment of self-correction
   (CSS/SVG/canvas), materializing as the centerpiece. Not a quote/feature card.
2. **Immediate visual WOW** — striking on first glance; full-bleed/cinematic; make someone stop.
3. **NO chatbot / message-bubble / chat-feed / terminal-or-console-as-UI / search-box.** No
   "search / explore / ask" affordances. (A *depicted* score panel/graph inside the scene is fine.)
4. **Unbidden arising** — the correction materializes autonomously (timer / scroll-as-passage /
   IntersectionObserver), **never** via hover/cursor/click. The audit happens *to* the viewer.
5. **Self-contained** — one HTML file: inline CSS + vanilla JS only. No build, no CDN, no framework.
   A web font via <link> is OK; prefer system/`Space Grotesk`-like display + an italic serif accent.
6. **Honest copy** — real links: live web **https://glasshat-web-o366v7tl2q-uc.a.run.app**
   (`/judge` · `/participate`), live API health
   **https://glasshat-api-o366v7tl2q-uc.a.run.app/health** → `{"status":"ok"}`, **Apache-2.0**.
   No marketing superlatives; honor the HONESTY section above.
7. **Accessible** — keyboard-reachable; `prefers-reduced-motion` renders the scene fully
   **resolved & static** (the corrected number already at rest, no churn/strobe); contrast ≥ 4.5:1
   for text; decorative canvas/SVG `aria-hidden`; stage `aria-label`; `aria-live` for the surfaced
   corrected score. (This must survive a Lighthouse a11y ≥ 90 pass when ported.)

## Brand palette (OKLCH — keep coherent across all mockups)
- bg `oklch(0.15 0.021 265)` · surface `oklch(0.205 0.024 265)` · ink `oklch(0.97 0.01 265)` ·
  muted `oklch(0.72 0.02 265)`
- accent (violet) `oklch(0.72 0.17 290)` · accent-2 (cyan) `oklch(0.82 0.13 205)` · accent-3
  (magenta) `oklch(0.78 0.16 330)` · good (green) `oklch(0.78 0.15 150)` · warn (amber)
  `oklch(0.82 0.15 85)`
- For SOLID fills under white text use a darker accent `oklch(0.55 0.17 290)` (AA contrast).
- The signature gesture: **amber (over-confident) → violet (calibrated)** as the score is pulled back.

## What to deliver
A standalone HTML mockup whose centerpiece is the self-correction SCENE materializing by the
assigned technique. One bold coherent idea over a hero+features+footer template. The correction
must be *felt*.
