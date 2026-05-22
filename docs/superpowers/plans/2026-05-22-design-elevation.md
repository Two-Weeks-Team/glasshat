# Glasshat Design Elevation — Plan (G3)

**Goal:** Elevate landing + `/judge` + `/participate` from "clean and functional" to a level that
objectively boasts **visual WOW + technical kick** — iteratively (improve → check → verify → plan),
per-phase PRs, CI green, with measurable evidence.

## Principles (from 2026 trend + dev-tool-landing research)

1. **Dark mode is the canvas** (have it) — push contrast and depth, not flatness.
2. **Atmospheric / mesh gradients** — painterly, layered, mood-setting (not neon). Already have radial
   glows; upgrade to a layered mesh + subtle animated drift in the hero.
3. **Bold typography as the hero** — oversized, high-contrast headline; gradient clip on the key phrase
   (have a start); tighten the type scale and rhythm.
4. **Bento-grid** modular sections — 67% of top SaaS use it; restructure the feature/explainer area
   into a balanced bento that mixes copy, a live stat, and a product visual.
5. **Micro-interactions** — hover lifts, smooth focus rings, animated counters, the stage timeline and
   3D graph as living elements. "Feels alive" without being noisy.
6. **Show the product** — for an under-the-hood engine, the *differentiator visual* is the engine itself:
   the live self-correction monitor + the 3D constellation. Surface a tasteful hero preview of it.
7. **Accessibility is non-negotiable** — WCAG 2.2 AA contrast, visible focus, reduced-motion support,
   semantic landmarks. (Also gates the Lighthouse A11y score.)

References: Vercel (animated gradient hero, whitespace, bento blocks), Linear (precision + motion),
Evil Martians "100 devtool landing pages" (clarity + show value), Figma 2026 trends.

## Measurable targets (the "objective" bar)

- **Lighthouse (production build, mobile + desktop)**: Performance ≥ 90, Accessibility ≥ 90,
  Best-Practices ≥ 90 on `/`, `/judge`, `/participate`.
- **Responsive**: clean at 390px (mobile) and 1440px (desktop) — screenshots as evidence.
- **Motion**: respects `prefers-reduced-motion`; no layout shift (CLS ~0).
- **No regressions**: `pnpm lint/typecheck/test/build` green; CI green; no placeholders.

## Phased PRs (iterate)

- **D1 — Design system depth**: tokens (mesh-gradient utilities, elevation, motion vars, reduced-motion),
  typography scale, a reusable `Reveal`/hover-lift primitive + tests. Apply to shared components.
- **D2 — Landing WOW**: animated mesh hero + bold type + bento feature grid + a hero product preview
  (mini constellation / live-monitor motif) + micro-interactions. Lighthouse evidence.
- **D3 — /participate + /judge polish**: elevate the run/results surfaces — animated stage timeline,
  count-up final score, refined tables/cards, motion on result reveal. Lighthouse evidence.
- **D4 — Audit + verify**: full Lighthouse pass on all three pages (mobile+desktop), responsive
  screenshots, reduced-motion check, redeploy, update README + verification doc.

## Verification each PR

`pnpm lint && pnpm typecheck && pnpm test && pnpm build` green → Lighthouse (Chrome) on the production
build → screenshots → CI green → merge (no squash). Iterate until every target is met on every page.
