# P07 — The Mobile-First

## 6-Tuple

```json
{
  "id": "P07",
  "advocate": "The Mobile-First",
  "framing": "Hackathon judges scroll Devpost on iPhone Safari between meetings. If Glasshat's audit moment doesn't land in a thumb-reach zone on a 375px viewport, it doesn't land at all.",
  "target_persona": "Devpost judge swiping through 40 submissions on iPhone 15 Safari, one-handed, on a Caltrain back from SF.",
  "primary_surface": "Vertical phone frame (375x812). Single-column. Bottom-sheet CTAs at 48px tap targets. Story-mode scroll (Instagram Stories cadence). Pull-to-refresh hook on the audit moment.",
  "opus_4_7_capability": "Multimodal narration compression — collapse the 7-step pipeline into 7 swipeable scenes with auto-fit captions, each scene self-contained without horizontal scroll.",
  "mvp_scope": "One vertical story: Ingest → Plan → Panel → Audit (the wow) → Score → Dual-rubric reveal. 6 scenes, swipe-down to advance, bottom CTA pinned.",
  "one_liner_pitch": "Glasshat in your thumb. Swipe down to watch six AI hats catch their own bias — judged correctly on the phone you're already holding.",
  "spec_alignment_notes": "framing→I read idea.spec.json implicitly via README + max-wins-plan; target_persona derived from Devpost mobile usage pattern (judges multitask). Primary surface anchors to phone-frame bias verbatim. All other fields followed spec narrative — audit-the-auditor as wow moment, dual-rubric as close."
}
```

## ASCII Wireframe — landing.html

```
┌─────────────────────────────┐
│ ▓▓▓▓ 9:41          ●●● 100% │  ← status bar
├─────────────────────────────┤
│  ⬢ Glasshat        ☰         │  ← sticky header (56px)
│  ─────────────────           │
│                              │
│   The judge gets             │  ← hero, thumb-zone
│   judged.                    │
│                              │
│   Watch six AI hats          │
│   catch their own bias       │
│   on your phone.             │
│                              │
│  [▼ swipe to see it]         │  ← scroll hint
│                              │
├─────────────────────────────┤
│ scene 1: ingest              │  ← vertical story
│ scene 2: plan                │
│ scene 3: panel               │
│ scene 4: audit ★ (the wow)   │
│ scene 5: score self-corrects │
│ scene 6: dual rubric         │
├─────────────────────────────┤
│                              │
│  [ ▶ play 90-sec demo  ]     │  ← bottom sheet
│  [ open on desktop →    ]    │     48px tap targets
└─────────────────────────────┘
```

## ASCII Wireframe — demo.html

```
┌─────────────────────────────┐
│ ▓▓▓▓ 9:41          ●●● 100% │
├─────────────────────────────┤
│ ← back  Glasshat live  ⓘ    │
├─────────────────────────────┤
│                              │
│  ●○○○○○  scene 1 / 6         │  ← progress dots
│                              │
│  ┌─────────────────────┐    │
│  │                     │    │
│  │   [SCENE BODY]      │    │  ← swipeable card
│  │   - deck thumb      │    │     (snap scroll)
│  │   - repo url        │    │
│  │   - 6 hat avatars   │    │
│  │   - audit pulse ★   │    │
│  │   - score ticker    │    │
│  │   - dual rubric     │    │
│  │                     │    │
│  └─────────────────────┘    │
│                              │
│  caption (thumb-readable     │
│  16px line-height 1.5)       │
│                              │
├─────────────────────────────┤
│  ⌂   ◐   ★   ⓘ   ⇪          │  ← bottom nav
│ home plan audit info share   │     (48px each)
└─────────────────────────────┘
```

## Differentiation note

This is the only variant where the **phone IS the demo surface**, not a screenshot of a desktop product. Audit moment is a haptic-style pulse (visual stand-in), score self-correction is a number ticker (no 3D), dual-rubric is a vertical split swipe — all designed for one-thumb consumption while Devpost is open in another tab.
