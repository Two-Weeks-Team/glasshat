# Web Rebuild — Verification (2026-05-22)

## Why this work happened

The deployed site read as empty and non-functional ("페이지의 상태도 너무 허전하고 제대로 된 기능이
아무것도 없습니다"). Investigation confirmed: the **engine/API was rich and live**, but the
**frontend was a ~227-line shell** — a static `/judge` placeholder (a bullet list of features that
didn't exist) and a single hardcoded `/participate` button. The landing was a header + two cards.

It was rebuilt across four per-phase PRs (SDD + TDD, no squash):

| PR | Branch | Scope |
|----|--------|-------|
| #15 | `feat/web-foundation` | Typed API contract, dark design system, reusable components, `GET /api/presets` |
| #16 | `feat/participate-rebuild` | `/participate`: form → plan gate → live SSE run → results → 3D reshape |
| #17 | `feat/judge-rebuild` | `/judge`: batch eval → ranking + ordered tie-break → Top-K → gate-2 override → lock |
| #18 | `feat/landing-deploy-verify` | Landing rebuild, real-Vertex deploy enablement, this verification |

## Root-cause fix: the live client never reached the API

`infra/Dockerfile.web` ran `pnpm build` **without** `NEXT_PUBLIC_API_BASE`. Next.js inlines
`NEXT_PUBLIC_*` into the **client bundle at build time**; the deploy then set it only as a
**runtime** env var, which a static build ignores. So on the live site every client API call went
to the web service's own origin (`/api/...` → 404). The one participate button could never have
worked in production — consistent with the "nothing works" report.

**Fix (PR #18):** `Dockerfile.web` takes `ARG NEXT_PUBLIC_API_BASE` and exports it before
`pnpm build`; `deploy.sh` now deploys the API first, then builds the web image with the live API
URL baked in.

## Local end-to-end verification (real browser, Playwright)

Stack: API on `127.0.0.1:8088` (`LLM_BACKEND=mock`, `DOCSTORE_BACKEND=memory`,
`OTEL_SDK_DISABLED=true`), web served by `next start` with `NEXT_PUBLIC_API_BASE=http://127.0.0.1:8088`.
(Production build, not `next dev` — the dev HMR websocket fails under headless Playwright and
reload-loops React state; that is a dev-server artifact, not an app bug.)

| Page | Verified | Evidence |
|------|----------|----------|
| `/` landing | Hero, "how it works" pipeline, feature cards, two-viewport section, **live preset chips (4)**, "API live" | `assets/landing.png` |
| `/judge` | Cohort runs via real `/api/evaluate`; ranking table (4 ranked), per-criterion bars + weights, self-correction badges, winner/lock/override controls | `assets/judge-ranked.png` |
| `/participate` | Real `/api/plan` gate (6 hats, 4×25%, retrieval budget); live `StageTimeline` + full self-correction ticker (Phoenix MCP → anchors → score corrected); final 50.5, per-criterion scores + evidence + audit callouts; 3D graph with amber corrected nodes; weakest-axis iterate; synthesized rubric | `assets/participate-results.png` |

The dropdown populated with all four presets and the footer showed **API live** — confirming the
client↔API contract works once the API base is correct (the very thing the build-time fix ensures
in production).

## Test + build gates (every PR)

- Backend: `uv run ruff check .` ✓ · `uv run mypy …` ✓ (34 files) · `uv run pytest` ✓ (157 tests)
- Web: `pnpm lint` ✓ · `pnpm typecheck` ✓ · `pnpm test` ✓ (35 tests) · `pnpm build` ✓
- CI (GitHub Actions): `lint·typecheck·test`, `web`, `docker build (api+web)` — all green per PR.
- No `mock|stub|placeholder|TODO|not implemented` in shipped web code.

## Real-Vertex + Phoenix deploy enablement (PR #18)

- `glasshat-shared` extras (`vertex`, `phoenix`) surfaced as root extras; `uv.lock` re-locked.
- `Dockerfile.api` takes `ARG UV_EXTRAS` (empty by default → fast mock build for CI; deploy passes
  `--extra vertex --extra phoenix`). Verified `uv sync --frozen --no-dev --extra vertex --extra phoenix`
  resolves and installs.
- `infra/deploy.sh` gained a real (default) / `--mock` mode. Real mode sets `LLM_BACKEND=vertex`,
  `MONITOR_BACKEND=phoenix-cloud`, `GOOGLE_GENAI_USE_VERTEXAI=true`, and injects `PHOENIX_API_KEY`
  from **Secret Manager** (`phoenix-api-key:latest`) — no committed `.env`.

### Remaining (needs the user) before the real-Vertex redeploy
1. `PHOENIX_API_KEY` placed in Secret Manager:
   `printf '%s' "<key>" | gcloud secrets create phoenix-api-key --data-file=- --project=panelyst-hackathon`
2. Cloud Run runtime SA granted `roles/aiplatform.user` + `roles/secretmanager.secretAccessor`.
3. `bash infra/deploy.sh --confirm` (real) — then curl `/health` 200 and re-screenshot the live site.

A `--mock` redeploy needs none of the above and already serves the full rebuilt UI (with the
build-time API-base fix), so the live site stops being "empty" immediately.

## Real verification + live real-Vertex deploy (2026-05-22, follow-up)

### G1 — Real Arize Phoenix e2e (self-hosted)
`scripts/real_phoenix_cloud_e2e.py` targets Phoenix **Cloud**; `scripts/real_e2e.py` targets a
self-hosted Phoenix. Ran the latter against real Vertex on `panelyst-hackathon`:
- Self-hosted Arize Phoenix (OSS) up, project `glasshat-e2e`.
- Real ADK → Phoenix **MCP** (stdio): 27 tools, `list-projects` tool called.
- Real **Vertex Gemini** (`gemini-2.5-flash`): RunRecord `f9ab2489`, final **54.39**, all 4 criteria
  self-corrected (yellow hat, mean_delta 1.2); 25 SSE stages incl. the full self-correction beats.
- **29 Phoenix spans captured.**

**Key-type finding:** the provided `ak-…` key is an **Arize AX** key (authenticates at
`otlp.arize.com`, 400-not-401), **not** a Phoenix-Cloud key, so it cannot push to
`app.phoenix.arize.com` (401). To stream traces to the user's hosted account we need either a
Phoenix-Cloud key (from `app.phoenix.arize.com/settings/api-keys`, no `ak-` prefix) or the Arize AX
**Space ID** (for the `otlp.arize.com` endpoint). Secret `phoenix-api-key` is created in Secret
Manager and the Cloud Run SA has `secretmanager.secretAccessor` + `aiplatform.user`.

### G2 — Live real-Vertex deploy
`bash infra/deploy.sh --confirm --no-phoenix` (real Vertex Gemini; tracing NoOp pending the correct
Phoenix credential) → deployed to `panelyst-hackathon`/us-central1, min-instances=0.
- API revision `glasshat-api-00002-cbv`; `GET /health` → `{"status":"ok"}`.
- Live `POST /api/evaluate` (**real Gemini**): `run_id 38de48ed`, final **58.27**, all 4 criteria
  self-corrected, 4 audit corrections (~77s cold: cold start + 6 sequential real hat calls).
- `/`, `/judge`, `/participate` → HTTP **200**; live landing screenshot `assets/live-landing.png`
  shows the full rebuilt UI in production.

Live URLs: Web https://glasshat-web-o366v7tl2q-uc.a.run.app · API https://glasshat-api-o366v7tl2q-uc.a.run.app

## Resolution — Arize AX observability is live (PR #24, redeploy)

The `ak-…` key was confirmed to be an **Arize AX** key (`app.arize.com`); the user provided the
Space ID (`U3BhY2U6NDUxMzY6V012Yg==`, "app.2weeks Space"). Added a first-class `arize` monitor
backend (`ArizeTracer` → `arize.otel.register` → `otlp.arize.com`), wired `deploy.sh` real mode to
it, and **redeployed**:

- `scripts/real_arize_ax_e2e.py` (local): probe span flushed with **zero export errors**, real Vertex
  pipeline `run 42951b51` final 59.04 (4 self-corrections), all spans flushed to AX project `glasshat`.
- **Live service**: registers to `otlp.arize.com` (project `glasshat`, all auth headers set, no export
  errors in Cloud Run logs); live real-Gemini eval `run 58f6892c` final 64.6. Every pipeline stage is
  now a span in the AX space.

Deps were also upgraded to latest majors (PR #25): web eslint 10 / TS 6 / vitest 4 / jsdom 29 /
three 0.184; Python `uv lock --upgrade`. Held (upstream caps): `@vitejs/plugin-react`@5 (6 needs
vite 8; vitest 4 ships vite 7) and `starlette`@0.52 (FastAPI caps `<1.0`).
