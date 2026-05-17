# P05 — The Design-Forward · Proposal

> **Tier 3 · Preview Advocate** · bias: UX first · award-target: Awwwards SOTD
> Project: **Glasshat** — *"doesn't just judge projects. It audits the judge."*

---

## 6-tuple

```json
{
  "id": "P05",
  "advocate": "The Design-Forward",
  "framing": "Glasshat's strongest competitive asset is not the agent topology — it's the audit moment as cinema. Re-frame the landing + demo as a high-fidelity cultural artifact (Linear/Vercel/Resend tier) so judges feel the fairness thesis before reading a word of spec.",
  "target_persona": "Hackathon judge scanning 200+ submissions in one sitting — design-literate, time-poor, decides go/no-go in 5 seconds. Secondary: founder-VC scrolling Twitter, lured by a screenshot.",
  "primary_surface": "First frame = pitch. Editorial display type ('audits the judge.' as italic serif on dark) over a live Three.js 503-anchor constellation. Custom cursor + kinetic word-reveal + breathing glow CTA. Every element animates on hover/scroll — micro-states everywhere.",
  "opus_4_7_capability": "Opus 4.7's million-token context lets it hold the entire RubricSynthesizer spec + wow-moment §6 corpus + four narration anchors simultaneously, so the demo's choreography (camera dolly + transcript captions + audit timeline + Phoenix MCP HUD) stays factually grounded across 22-second cinematic timeline without drift.",
  "mvp_scope": "Two files (landing.html + demo.html). Landing: hero w/ Three.js constellation + 5s wow panel + feature trio + corpus proof + CTA. Demo: 22-second auto-play of the audit moment with cinematic camera choreography, climax typography fade-in, dual-rubric reveal. Self-contained, Three.js via CDN.",
  "one_liner_pitch": "An audit moment shot like a film: editorial typography, breathing constellation, custom cursor, choreographed score self-correction in 22 seconds — proof that fairness is a design surface.",
  "spec_alignment_notes": "Anchors used verbatim from wow-moment-design.md §13.5 ('audits the judge.', '37 of 503', '72% similar to winner cluster', 'And the auditor is the vector space.', 'Same engine. Different rubric. Different (correct) score.'). 503 anchor count from §6.2. Yellow A1 9.0→7.6 + evidence_depth 0.31 + mean_delta −1.2 + 14 spans + 800ms MCP budget all from §11.2. Triple-redundant detection (Phoenix Online Eval + Custom Evaluator + Black-hat counter-claim) from §11.1 referenced in feature 01. Dual-rubric variance from §12.1 Layer 2. RubricSynthesizer credited in feature 03 per §12.4. No invented numbers."
}
```

---

## ASCII sketches

### landing.html — first-fold composition

```
┌──────────────────────────────────────────────────────────────────────┐
│ ● Glasshat        the audit | engine | corpus | demo    [Open →]     │  nav (sticky, blurred)
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ⚪ VECTOR SPACE DAY SF · RAPID AGENT · ARIZE · 2026                  │  eyebrow (pulse dot)
│                                                                      │
│  Glasshat                                                            │
│  doesn't just                                       ╱ kinetic ╲      │
│  judge.                                            │  word-by-  │    │
│  It audits the judge.  ← italic gradient serif    │   word     │    │
│                                                    │  reveal    │    │
│                                                     ╲          ╱     │
│  An artifact-ingesting evaluation pipeline…                          │  sub
│                                                                      │
│  [ Watch the 3-min demo ]   [ See the audit moment ]                 │  CTAs
│                                                  ┌──QDRANT · VSD──┐  │
│                                                  └──ARIZE PHOENIX──┘  │ rail (right)
│                                                                      │
│  ╔════════════════════════════════════════════════════════════════╗ │
│  ║       · · · · ·  · · ·  ·         ● ←current      ·     · · ·  ║ │  Three.js
│  ║  · · ·  ·  ·  ·    · · · · ·    halo+lines       ·  · ·  ·     ║ │  constellation
│  ║       ✦ ✦ ✦  winner cluster        ·  ·  ·  · ·    ·           ║ │  (mouse parallax)
│  ║   503 ANCHOR PROJECTS · CLUSTERED BY OUTCOME TIER · LIVE        ║ │
│  ╚════════════════════════════════════════════════════════════════╝ │
└──────────────────────────────────────────────────────────────────────┘
                              ↓ scroll
[ THE 5-SECOND WOW ] → audit panel (left, live trace) | reveal stack (right)
[ FEATURE TRIO ]     → 01 triple-redundant audit | 02 503 anchors | 03 dual-rubric
[ SOCIAL PROOF ]     → italic display quote · 503/6/4/2 stats
[ CTA ]              → "Same engine. Different rubric. Different (correct) score."
```

### demo.html — cinematic three-column stage

```
┌──── 00:11.430 / 03:00 · AUDIT · CORRECTING ─────────────────────────┐
│ ● Glasshat · The audit       ⊙ JUDGE MODE · QDRANT VSD       timer │
├─────────┬────────────────────────────────────────────────┬──────────┤
│ HATS    │  EVALUATION GRAPH    ┌─tick─tick─┐    FOCUS    │  AUDIT   │
│ ┌─────┐ │                                                │  LOOP    │
│ │White│ │       · · ✦ · ·    ●←current sub               │ ┌──────┐ │
│ │ 7.4 │ │      ·  ·  · ·  · ·   (amber, halo)            │ │● flag│ │
│ └─────┘ │                                                │ │● phx │ │
│ ╔═════╗ │             ╱ anchor lines ╲                  │ │● annot│ │
│ ║Yel.║ │       ·   ╱       ●          ╲ ·              │ │● rec  │ │
│ ║flag║ │          ✦         ●           ✦  ←3 anchors   │ │● calb│ │
│ ║9.0→║ │   · · ·       ●          · ·                   │ │● conv │ │
│ ║7.6 ║ │                                                │ └──────┘ │
│ ╚═════╝ │            ╔════════════════════╗              │          │
│ ┌─────┐ │            ║ audits the judge. ║ ←climax serif│ ╔══════╗ │
│ │Black│ │            ╚════════════════════╝   gradient  │ ║87→73 ║ │
│ │ 6.8 │ │   QDRANT recommend · 3 anchors  PHOENIX get-* │ ║rubric║ │
│ └─────┘ │   ▸ "and the auditor IS the vector space."    │ ║reveal║ │
│  ...    │       ↑ transcript chip                       │ ╚══════╝ │
├─────────┴────────────────────────────────────────────────┴──────────┤
│  [↺] [❚❚]  PANEL ──────●────────────────────── REVEAL    ESC · SPACE│
└─────────────────────────────────────────────────────────────────────┘
```

### 22-second choreography

```
0s ─── 2s ─── 4s ─── 5.5s ─── 7s ─── 9s ─── 11s ─── 12.5s ─── 15s ─── 18s ─── 22s
│      │     │       │       │      │      │        │         │       │
panel  Yel.  Phx     Phx     Qdr.   anchor calib   migrate  CLIMAX   reveal
idle   flag  exp-id  spans   rec    pull   9→7.6   3D node  serif    dual
gentle red   mean    proof   3      lines  amber   toward   "audits  87/73
drift  ring  =-1.2   chain   anchors+stars card    winners  the      panel
                                                            judge."  fades

camera:  (.5,.4,9) ──dolly─→ (1.0,.4,8) ── push─→ (1.2,.6,6.8) ─pull back→ (0,.2,8.5)
audio:   silent (visual rhythm only — 800ms gaps as Doumont clarity)
```

---

## Design rationale (why this differs from P-other-advocates)

| Axis | Our move | Other advocates would do |
|---|---|---|
| **Type system** | Display serif italic ("New York"-stack) for headlines + mono for ops trace + sans for body. Three voices, one composition. | Single sans-serif "modern" voice — safer but indistinguishable. |
| **Color** | OKLCH-only palette w/ amber as signal, violet/cyan/emerald as supporting hues, true blacks only via low L*. | RGB primaries, harder gradients. |
| **Motion** | Choreographed (not decorative): camera dolly aligned to audit beats; climax serif fades on convergence; node migration animates between hat flag and winner cluster. | Random fades, no causal link between motion and narrative. |
| **3D** | Three.js as the stage (503 anchors live, weight-aware clustering by tier), not a hero decoration. | CSS 3D as ornament, lacks load-bearing read. |
| **Polish** | Custom cursor, mouse parallax, scroll-triggered word reveal, breathing CTA halo, blurred glass nav, cinema corner ticks, sticky scrubber. | One or two of these, not all. |

---

## File inventory

| File | Path | Size budget | Status |
|---|---|---|---|
| Landing | `mockups/gallery/P05-design-forward/landing.html` | ≤55KB · ≤1500 lines | ~18KB · 425 lines |
| Demo    | `mockups/gallery/P05-design-forward/demo.html`    | ≤70KB · ≤2000 lines | ~22KB · 540 lines |
| Proposal | `mockups/gallery/P05-design-forward/_proposal.md` | — | this file |
| **Total** | | ≤90KB combined | well under budget |

Self-contained except Three.js via `unpkg.com/three@0.160.0` CDN (spec-allowed). No external fonts (system stack), no images (inline SVG), inline `<style>` only.

---

*Authored 2026-05 · The Design-Forward · Opus 4.7 medium · Awwwards SOTD target*
