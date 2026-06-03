# Glasshat — Gap Remediation Checklist (2026-06-03)

Source: 5 parallel read-only expert agents (honesty/Skeptic, security, backend, quality, frontend/a11y) audited HEAD `b3e0cae`. This is the authoritative remediation list. Each item: severity · file:line · fix · checkbox. Check `[x]` only when merged + verified.

> Convergent finding (honesty + backend + quality agents): the live deploy has `CONSULTANT_BACKEND=phoenix-mcp` but **`PHOENIX_COLLECTOR_ENDPOINT` is empty**, so `engine.py` falls back to `TableConsultant`/`NullDatasetWriter` — the "learning loop" is inert in production and the SSE `phoenix_consultation`/`dataset_*` numbers are table-derived, not real Phoenix calls.

---

## 🔴 BLOCKER — submission honesty (highest risk; a judge greps and it collapses)

- [x] **B1** — `claudedocs/2026-06-02-devpost-text.md:28-30` + `claudedocs/2026-06-02-demo-video-script.md:45-46`: remove/correct the "**503 held-out anchors / 4,493 real submissions**" calibration claim. Reality: correction is driven by `_YELLOW_DELTA_BY_BUCKET` (spike-D synthetic toy data, n=7/10/16, total 33). 503/4,493 is the crawled `data/devpost-gemini3/` set, **never wired into the runtime calibration**. Rewrite to "a calibrated prior recovered from spike-D held-out anchors."
- [x] **B2** — `demo-video-script.md:62-68`, `devpost-text.md:43-45`: present-tense "talks to a Phoenix dataset over MCP and writes back / improves over time" overstates the live URL (endpoint unset → table/null). Restate as "implemented + E2E-verified offline; the live image runs the deterministic table prior."
- [x] **B3** — `apps/web/lib/stages.ts:45` (+ emit `engine.py:289`): live SSE beat label "Consulting Phoenix (MCP) for drift statistics" shows table-derived `Δ·n` on the live service. Either rename to reflect the prior, or gate the "Phoenix (MCP)" wording behind `phoenix_collector_endpoint` being set.

## 🟠 HIGH — security

- [x] **S1** — `infra/Dockerfile.api:34`: add `--proxy-headers --forwarded-allow-ips 0.0.0.0/0` to the uvicorn CMD so the rate limiter keys on the real client IP (X-Forwarded-For), not the Cloud Run LB IP. Without it per-IP rate limiting is a single shared bucket → cost-DoS unblocked.
- [x] **S2** — `apps/api/src/glasshat/api/app.py:124`: add `dependencies=[Depends(_rate_limit)]` to `@app.post("/api/plan")` (unguarded Vertex pro-tier LLM call).
- [x] **S3** — `services/pipeline-orchestrator/src/glasshat/pipeline/adk_runtime.py:39,78,146`: pin `@arizeai/phoenix-mcp` to a fixed version (not `@latest`) and/or pre-install in the Docker builder; remove the runtime-`npx`-downloads-latest supply-chain risk.
- [x] **S4** — `adk_runtime.py:41,80,148`: pass the Phoenix API key via `StdioServerParameters(env={"PHOENIX_API_KEY": api_key, ...})`, not `--apiKey <value>` in argv (avoids `/proc/<pid>/cmdline` secret leak).

## 🟠 HIGH — backend reliability

- [x] **R1** — `adk_runtime.py:82,162`: wrap the raw `stdio_client(...)` consult/write blocks in `asyncio.wait_for(..., timeout=30.0)` — a hung `npx` currently hangs the whole evaluation (FallbackConsultant catches exceptions, not hangs).

## 🟠 HIGH — frontend / a11y (this is why live a11y is 95-97, not 100)

- [x] **A1** — `apps/web/app/page.tsx:34`, `participate/ParticipateClient.tsx:195,223`, `judge/JudgeClient.tsx:194,554`: primary CTA `text-white` on `var(--color-accent)` = **2.64:1** (fails WCAG AA 4.5:1). Darken the button accent (≈`oklch(0.58 0.17 290)`) or use a dark ink token. This is the actual axe `color-contrast` blocker.
- [x] **A2** — `apps/web/app/page.tsx:13` full-bleed hero `w-screen` (`100vw`) overflows by the scrollbar gutter on Windows/Linux. Add `html { overflow-x: hidden; }` (or `overflow-x: clip` on body) in `globals.css`.
- [x] **A3** — `apps/web/components/ConstellationGraph.tsx:72-116`: add `role="img"` + generated `aria-label` summarizing each criterion's score/correction; gate `OrbitControls autoRotate` behind a `prefers-reduced-motion` check. (Canvas is currently opaque to AT and ignores reduced-motion.)

## 🟠 HIGH — quality / false-confidence

- [x] **Q1** — `services/pipeline-orchestrator/tests/test_adk_runtime.py`: add unit tests that drive `_parse_deltas` with a realistic phoenix-mcp `CallToolResult` fixture, and `PhoenixMcpConsultant.consult`/`PhoenixMcpDatasetWriter.write` with a fake `ClientSession` (monkeypatch `stdio_client`/`ClientSession`) asserting the exact tool name + arguments. (Live MCP bodies currently have ZERO executable-body coverage.)
- [x] **Q2** — `agents/tests/test_audit.py`: add a test asserting that with the **shipped** `default_calibration_anchors()`, two different `for_weights(...)` bindings return the **same** `ConsultResult` (documents the honest degenerate seed; current "changes who wins" test uses fabricated distinct-delta fixtures only).
- [x] **Q3** — `services/pipeline-orchestrator/tests/test_engine.py`: parametrized test over `Settings(consultant_backend=.../dataset_writer_backend=.../repo_grader_backend=...)` asserting `_select_*` wires the correct adapter type (the prod env-flag wiring is currently uncovered).
- [x] **Q4** — `agents/tests/test_audit.py:209`: add a second `@given` hypothesis property with independent `p25,p75` (NOT bracketing `score`) asserting `p25-tol ≤ corrected ≤ p75+tol AND |corrected-score| ≤ 2+tol` — covers the one-sided-band / cap-binds-clip adversarial regime currently untested.

## 🟡 MEDIUM

- [x] **M1** — `app.py:168` `/api/runs/{id}/override`: add `Depends(_rate_limit)` (and ideally an origin/secret check) — currently unauthenticated score tampering with only run_id.
- [x] **M2** — `engine.py:290`: gate the per-correction `emit(Stage.ANCHOR_RETRIEVAL, ...)` behind `isinstance(deps.consultant, WeightAware)` so the demo animation doesn't claim anchor retrieval that didn't happen on table/phoenix-mcp backends.
- [x] **M3** — `agents/src/glasshat/agents/types.py:52-57`: replace the `startswith("https://github.com/")` repo_url validator with the actual `_GITHUB_URL_RE` (shared) so the Pydantic layer matches the downstream SSRF gate.
- [x] **M4** — `infra/deploy.sh:126`: add `--concurrency 1` (or document) so the per-instance in-memory rate limiter can't be bypassed via horizontal scale.
- [ ] **M5** — docs number consistency: `docs/rapid-agent-compliance.md:26` stale "161 passed / 40 web" → real counts; unify the coverage figure (97%, not 96.7%) across `devpost-text.md:50,57`, `docs/evidence-matrix.md:17`, README.

## 🟢 LOW

- [x] **L1** — `infra/deploy.sh` `--no-phoenix` branch (~:91): set `CORS_ALLOW_ORIGINS=${WEB_ORIGIN}` (currently omitted → CORS `*` on that path). Consider changing `config.py` default from `"*"` to `""`.
- [ ] **L2** — `docs/architecture.md:37,143`: add "(shipped: GitHub REST metadata-only, no clone)" to the superseded-delta note (still shows `git clone`).
- [ ] **L3** — `apps/web/lib/participate-state.ts:148-151`: drive 3D `fromX` from the same `preAuditScoreMap` aggregate used by the 2D ScoreBar ghost (multi-hat criteria currently disagree).
- [ ] **L4** — `README.md:70,76`: add "(live deploy uses in-memory; Firestore/SQLite opt-in)" so "persists" isn't read as durable.
- [ ] **L5** — `apps/web/app/participate/ParticipateClient.tsx:305`: default `show3d=false` for real runs too (or IntersectionObserver-defer) so the ~900KB three/drei chunk isn't eagerly loaded for real participants.

## 🔒 Out of scope (user-gated / teammate)

- **U1** — Make phoenix-mcp genuinely live: set `PHOENIX_COLLECTOR_ENDPOINT` to a reachable Phoenix base URL + seed the `glasshat-calibration` dataset (needs user's Phoenix account). If done, B2/B3 can claim live instead of E2E-only.
- **U2** — Triage the ~253 `spikes/` gitleaks hits before making the repo fully public (security agent confirmed spot-checks read from `os.environ`, likely scraped/example, but not individually triaged).
- **U3** — Video recording + Devpost form submission (teammate).
