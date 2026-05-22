# Design Elevation — Verification (G3 / D1–D4, 2026-05-22)

Plan: `docs/superpowers/plans/2026-05-22-design-elevation.md`. Goal: elevate the three pages to a
level that objectively boasts **visual WOW + technical kick**, with measurable evidence.

## What shipped (one PR per phase, no squash)

| PR | Phase | Scope |
|----|-------|-------|
| #20 | D1 — design system | Animated OKLCH **mesh-gradient** atmosphere, tri-color accent, `elevate`/`hover-lift`/scroll-reveal utilities, on-brand `:focus-visible`, full `prefers-reduced-motion`; `Reveal` primitive; `StatCard` hover-lift. |
| #21 | D2 — landing WOW | `HeroGraphic` (SVG motif that *shows* the self-correction, looping, CSS-only); two-column hero with gradient headline; **bento** feature grid; staggered reveals; live preset showcase. `Reveal` → CSS-only load-in (never stuck hidden). |
| #22 | D3 — surface polish | `CountUp` animated final score; `/participate` results in reveals; `elevate` across `/participate` + `/judge` surfaces. |
| (this) | D4 — audit | Lighthouse on all pages (mobile + desktop), responsive screenshots, redeploy, docs. |

## Lighthouse (production build, `next start`, npx lighthouse 12)

All categories **≥ 90** on every page:

| Page | Device | Performance | Accessibility | Best-Practices |
|------|--------|------------|---------------|----------------|
| `/` landing | desktop | **90** | 95 | 96 |
| `/` landing | mobile  | **95** | 95 | 96 |
| `/judge` | desktop | **100** | 96 | 96 |
| `/participate` | desktop | **100** | 96 | 96 |

(Heavy 3D — `react-three-fiber` — is dynamically imported only when participant results render, so it
never weighs down initial load. All motion is CSS-only with no images.)

## Visual evidence

- `assets/design-landing.png` — desktop landing (hero motif, bento grid, viewports, presets).
- `assets/design-mobile.png` — mobile landing (responsive single-column at 390px).
- `assets/design-participate.png` — `/participate` results: live pipeline + wow-beat ticker, CountUp
  final score, per-criterion scores + audit callouts, 3D self-correction graph, weakest-axis, rubric.

## Accessibility + motion

- Semantic landmarks/headings; `:focus-visible` ring; `HeroGraphic` has an `aria-label`.
- Every animation (mesh drift, hero motif, reveal, count-up, pulse) is disabled or frozen-final under
  `prefers-reduced-motion: reduce`; content is never hidden behind JS (CSS `both` fill-mode).

Verified each PR: `pnpm lint && pnpm typecheck && pnpm test && pnpm build` green; CI (lint·web·docker) green.
