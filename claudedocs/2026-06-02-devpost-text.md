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
  six-hat panel, and scoring; **`text-embedding-005`** for evidence retrieval.
- **Google ADK** orchestration; every agent and every hat is its own span.
- **Arize AX** observability over OpenInference/OTLP. A **Phoenix-MCP calibration
  consultant + Phoenix-Dataset write-back loop** is implemented and E2E-verified
  offline; the credential-free live image runs the deterministic spike-D prior, and
  the MCP path activates by config flag when a Phoenix endpoint is set — so the
  audit *can* improve over time without overclaiming the live URL.
- **In-code hybrid retrieval** (Vertex embeddings + cosine + BM25 + RRF) — **no
  vector database**. A GitHub-REST **metadata-only** code grader (no clone) folds
  repo evidence into retrieval.
- TypeScript/Next.js PWA front end with a real-time SSE trace, 3D constellation,
  and rank-flip board. Python monorepo (uv workspace), 243 Python + 73 web tests,
  97.8% coverage, CI with a Gemini/Google-only dependency gate.

## How it maps to the judging criteria
- **Technological Implementation (primary / tie-break #1):** a real
  self-correction *algorithm* grounded in held-out calibration data — not prompt
  theatre. Deployed live on Vertex + ADK + Arize with a measured ±2.0-bounded
  correction, reproducible run-to-run, 97.8% test coverage.
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
- Live, reproducible, Apache-2.0, with a self-correction that's real math.
- Next: activate the live Phoenix-MCP consultant by default and accumulate
  per-rubric calibration so the audit sharpens with every evaluation.

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
- Live model is **`gemini-3.1-flash-lite`** (Gemini 2.5 is not used).
- The deployed image ships **no** general-purpose LLM SDKs (Gemini/Google only,
  CI-enforced).
- The "Qdrant" rubric preset is an **external rule set Glasshat judges against**,
  not a software dependency — Glasshat uses no Qdrant.
