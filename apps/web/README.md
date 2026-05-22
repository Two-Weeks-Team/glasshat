# apps/web (`glasshat-web`)

Next.js 16 frontend:

- **Landing** — mesh-gradient design system, animated self-correction hero motif, bento grid.
- **`/judge`** — batch cohort eval → rank with ordered tie-break → Top-K → gate-2
  override → lock. First paint shows a real cached sample cohort; "Run cohort live"
  re-evaluates.
- **`/participate`** — plan gate (human gate 1) → live SSE monitor → per-criterion
  scores + evidence + audit callouts → 3D self-correction constellation → iterate on
  the weakest axis.

Lighthouse ≥ 90 on all pages; motion respects `prefers-reduced-motion`. Implemented
and tested (vitest), CI-green. Dev: `pnpm install && pnpm dev`.
