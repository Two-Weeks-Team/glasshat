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
