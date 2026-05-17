---
target_persona: "Hackathon judges + Devpost readers who are saturated with dark-mode bento-glass SaaS landings; specifically the senior judge who reads pitch decks like a federal auditor reads a 10-K and wants evidence per claim, not vibes."
primary_surface: both
success_metric: "Judge dwell time on landing ≥45s (vs typical 12s skim) because the typewritten dossier aesthetic forces serial reading instead of bento-grid eye-bouncing."
bias_reasoning: |
  Everyone in 2026 ships OKLCH-dark-glass-bento-Three.js. The Glasshat v0.3 prototype already does this beautifully — which means it disappears into the crowd. Contrarian move: render Glasshat as what it actually IS — a forensic audit document. Print-magazine + typewriter + courtroom-stenography aesthetic. Cream paper, black ink, marginal red corrections, rubber stamps, footnotes, page numbers. The product is "audit the judge" — so make the UI look like an audit report. Form follows function literally.
key_tradeoffs: |
  SACRIFICE: instant "ooh shiny" reaction. Dark-mode bento gets a 2-second dopamine hit that this won't. Mobile experience is mediocre (print aesthetic assumes desktop / paper proportions). Some judges scrolling at 3am may bounce on text density. No flashy animations to GIF for Twitter. The 3D constellation becomes a 2D scatterplot — less spectacular at first glance, but more legible.
  GAIN: memorability (it's the ONLY hackathon submission that looks like a Berkshire Hathaway annual report), implicit credibility (typewritten = "this person did the work"), thematic coherence (audit aesthetic for an audit product), defensible originality on the Qdrant Originality axis.
why_pick_this: "If 47 other Devpost submissions are dark-mode-bento-glass and 1 is a typewritten audit report, the judge remembers the audit report."
---

# Landing hero ASCII sketch (10 lines)

```
┌──────────────────────────────────────────────────────────────────────┐
│  G L A S S H A T   ░░░░░░░░░░░░░░░░░░░░░░░░░  FILE No. 2026-001    │
│  AUDIT OF AN AI JURY     ⌐⌐⌐ CLASSIFIED · UNREDACTED ⌐⌐⌐           │
│ ──────────────────────────────────────────────────────────────────── │
│  Re: The judge is on trial.                          [STAMP: EXHIBIT]│
│                                                                      │
│  ¶1  Glasshat ingests a deck, a repo, and a rubric. Six AI hats     │
│  ─── score. A panel of three Phoenix evaluators audits the panel.   │
│  ¶2  When a hat over-scores, ¹ the Qdrant vector space pulls it    │
│  ─── back. The correction happens in front of you.                  │
│  ¹ see footnote, p.2:  "Yellow A1: 9.0 → 7̶.̶6̶ ← struck through live" │
└──────────────────────────────────────────────────────────────────────┘
```

# Demo wow scene ASCII sketch (10 lines)

```
═══════════════════════════════════════════════════════════════════════
  STENOGRAPHIC RECORD · GLASSHAT v0.4 · run #qd-2026-06-01-001
═══════════════════════════════════════════════════════════════════════
  01:23:04  YELLOW HAT:  A1 Problem Clarity ........ 9.0  /10
  01:23:08  [PHX-EVAL #1]: ▓ over_confident detected (LLM judge)
  01:23:08  [PHX-EVAL #2]: ▓ over_confident detected (Python)
  01:23:09  [BLACK HAT]:   ▓ counter-claim filed
  01:23:11  [MCP CALL]:    get-experiment-by-id ... mean Δ = −1.2
  01:23:13  [QDRANT]:      recommend() ... 3 anchors: 7.2, 7.5, 7.8
  01:23:15  YELLOW HAT:    A1 ........... 9̶.̶0̶ ⟶ 7.6 /10   [CORRECTED]
  01:23:16  ── COURT REPORTER: let the record reflect the correction ──
═══════════════════════════════════════════════════════════════════════
```
