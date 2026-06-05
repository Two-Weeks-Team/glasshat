# Glasshat — Devpost Submission Text (copy-paste ready)

> **Scope:** this is the *text only*, written so the teammate can paste each block
> straight into the Devpost form. **Submitting the form, uploading the video, and
> filling media fields are out of scope for this document** (teammate's job).
> Verify the live URLs are warm before submitting.

---

## Project name
**Glasshat — the audit layer for AI evaluation**

## Tagline (≤ 200 chars)
Glasshat doesn't just judge projects — it audits the judge. A rubric-aware, six-perspective evaluator that catches its own over-confidence and self-corrects the score, live, on Gemini + Arize.

## Inspiration
Every hackathon, grant review, and promotion committee runs on judgment that no
one audits. AI judges make it worse: confident, fast, and unaccountable. We asked
the uncomfortable question — *who audits the judge?* — and built the missing layer:
an evaluator that measures and corrects its **own** bias in the open.

## What it does
Glasshat ingests three things — a pitch deck, a GitHub repo, and **the evaluator's
own official rules** — and:
1. **Synthesizes a rubric** that mirrors those rules (no one-size-fits-all scoring).
2. Runs a **six-hat panel** (White/Red/Yellow/Black/Green/Blue), each perspective
   retrieving evidence and scoring every criterion.
3. **Audits itself.** Using a calibration prior recovered from **held-out spike-D
   anchors** — an evidence-bucketed YELLOW over-confidence delta (strongest where
   evidence is thin), the measured prior the runtime actually applies — it detects
   per-cell over-confidence and applies a transparent correction —
   `clip(score − 0.8·mean_delta, p25, p75)` with a ±2.0 cap — live on screen, with
   the 3D evaluation graph reshaping as it happens.
4. Shows **the audit changing who wins**: a rank-flip board puts the
   better-evidenced project on top once calibration is applied.

It is an artifact-ingesting evaluation pipeline **and** a transparent fairness
monitor — **not a chatbot**.

## How we built it
- **Gemini 3.1 Flash-Lite on Vertex AI** (global endpoint) for synthesis, the
  six-hat panel, and scoring; **`text-embedding-005`** for evidence retrieval. The
  Agent-Engine deployment runs the GA `gemini-enterprise` backend
  (`gemini-3.5-flash` / `gemini-3.1-pro`).
- **Google ADK 2.0** — the whole pipeline is a real **`Workflow` graph**
  (ingest → synth → plan → 6-hat parallel fan-out → join → audit → score),
  **deployed as a genuine agent on the Gemini Enterprise Agent Platform (Agent
  Engine)** — live resource `reasoningEngines/7480191458771730432`, serving
  `stream_query`. The credential-free Cloud Run demo runs the parity-identical
  python path (byte-identical RunRecord+SSE).
- **Arize AX** observability over OpenInference/OTLP. The deployed agent emits a
  **full nested trace tree** (agent → Workflow → each of the six hats' Gemini
  generate + embed calls — 104 spans in a two-query capture, verified via
  `client.spans.list(project="glasshat")`), using an isolated tracer-provider so
  Agent Engine doesn't drop the global one. We also ran a real **Arize AX
  Experiment** over a `glasshat-golden` Dataset with a `glasshat-prompt-injection`
  code Evaluator: **hit@13 = 0.6154** on real Gemini (8 of 13 historical winners
  ranked into the top-13) vs 0.3846 mock / 0.26 chance — a binary Winner-label
  hit@13, not a rank curve.
- A **Phoenix-MCP calibration consultant + Phoenix-Dataset write-back loop** is
  implemented and E2E-verified; the credential-free live image runs the
  deterministic spike-D prior, and the MCP path activates by config flag when a
  Phoenix endpoint is set — so we state exactly which path is live rather than
  overclaim.
- **In-code hybrid retrieval** (Vertex embeddings + cosine + BM25 + RRF) — **no
  vector database**. A GitHub-REST **metadata-only** code grader (no clone) folds
  repo evidence into retrieval.
- TypeScript/Next.js PWA front end with a real-time SSE trace, 3D constellation,
  and rank-flip board. Python monorepo (uv workspace), **323 Python + 74 web
  tests**, CI with a Gemini/Google-only dependency gate (the deployed image ships
  no general-purpose LLM SDKs).

## How it maps to the judging criteria
- **Technological Implementation (primary / tie-break #1):** a real
  self-correction *algorithm* grounded in held-out calibration data — not prompt
  theatre. The evaluation brain is a genuine **ADK 2.0 Workflow agent deployed on
  the Gemini Enterprise Agent Platform (Agent Engine)**, traced end-to-end in
  **Arize AX** (full nested tree) and measured with an **Arize AX Experiment**
  (hit@13 0.6154). Measured ±2.0-bounded correction, reproducible run-to-run.
- **Design:** the correction is the interface — over-confidence visibly recedes,
  the graph reshapes, and a rank-flip board makes "the audit changes who wins"
  legible in one glance.
- **Potential Impact:** any evaluation that must be *defended* — hackathons,
  grants, hiring, model-as-judge pipelines — needs an audit layer. Glasshat is
  rubric-agnostic, so it generalizes across rule sets.
- **Quality of the Idea:** "audit the judge" is a genuinely different framing from
  "be a better judge" — it treats evaluator bias as a measurable, correctable
  quantity.

## Challenges we ran into
- **Honest MCP claims.** The Phoenix-MCP learning loop is deployed and wired, but
  the credential-free demo image runs on the deterministic spike-D prior; we made
  the UI and docs state exactly which path is live rather than overclaim.
- **Calibration without fabrication.** With only one measured corpus, we shipped
  the weight-aware anchor *mechanism* honestly (it fills with genuinely per-rubric
  deltas as the live dataset grows) instead of faking cross-rubric differences.
- **Cold-start on camera.** Vertex cold start is real; we warm the service and use
  fixed sample inputs for a reliable live demo.

## Accomplishments / What's next
- Live, reproducible, Apache-2.0, with a self-correction that's real math —
  **genuinely deployed on Agent Engine, traced in Arize AX, and measured (hit@13)**.
- Next: flip the live demo to the hardened `structured` scoring mode + judge auth,
  activate the live Phoenix-MCP consultant by default, and accumulate per-rubric
  calibration so the audit sharpens with every evaluation.

## Built with
`google-cloud` · `vertex-ai` · `gemini` · `google-adk` · `arize` · `arize-ax` ·
`phoenix` · `mcp` · `python` · `fastapi` · `typescript` · `next.js` · `react` ·
`tailwindcss` · `three.js` · `uv` · `docker` · `cloud-run`

## Links
- **Live web:** https://glasshat-web-o366v7tl2q-uc.a.run.app  (`/judge` · `/participate`)
- **Live API health:** https://glasshat-api-o366v7tl2q-uc.a.run.app/health → `{"status":"ok"}`
- **License:** Apache-2.0
- **Demo video:** _(teammate inserts link)_
- **Repo:** _(teammate inserts public repo link)_

## Honest disclosures (keep — they raise credibility)
- Live model is **`gemini-3.1-flash-lite`** (Gemini 2.5 is not used); the
  Agent-Engine deploy runs GA `gemini-3.5-flash` / `gemini-3.1-pro`.
- **hit@13 0.6154 is a binary Winner-label metric, not a rising rank curve**; on
  this golden set the audit did not reorder the top-13 (Δ=0). We never claim the
  judge is "un-gameable".
- The public Cloud Run demo runs `SCORING_MODE=legacy` (the hardened
  `structured` mode + judge-auth are opt-in); the Agent-Engine agent is the genuine
  ADK runtime (Cloud Run runs the parity-identical python path).
- The deployed image ships **no** general-purpose LLM SDKs (Gemini/Google only,
  CI-enforced).
- The "Qdrant" rubric preset is an **external rule set Glasshat judges against**,
  not a software dependency — Glasshat uses no Qdrant.
