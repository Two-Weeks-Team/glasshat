# P18 — The Designer · Proposal

## 6-Tuple (Preview Card)

```json
{
  "id": "P18",
  "advocate": "The Designer",
  "framing": "Glasshat is a short film about a moment of self-correction. The product is the story of an AI judge catching itself being wrong — and the vector space that lets the audience see it happen. The narrative IS the product surface.",
  "target_persona": "Hackathon judges + technical-leadership audience watching demo videos under 3 minutes; they decide on emotional resonance + visual proof in the first 30 seconds, then validate technically afterwards.",
  "primary_surface": "Scroll-driven cinematic landing (Act I-III storytelling) + 6-stage demo film (auto-play, scrub-able like a short film, not a UI). Product proper sits behind the curtain; the story is the front door.",
  "opus_4_7_capability": "Multi-modal scene composition — Opus 4.7 orchestrates SVG character design, scroll-act pacing, and emotional beat sequencing in a single coherent narrative that maps 1:1 onto the 5-step audit-the-auditor loop (detection → consultation → anchoring → correction → reveal).",
  "mvp_scope": "Two static HTML files (landing + demo film), zero external dependencies, ≤90KB total, all SVG inline. Demo is auto-play with chapter scrubber. 4-day-build-able because there is no backend; the wow moment is dramatized, not executed.",
  "one_liner_pitch": "An AI judge audits itself — and we filmed it. Glasshat as a 3-min short, with Six Hats as characters and Qdrant's constellation as the silent third act.",
  "spec_alignment_notes": "all fields populated per docs/wow-moment-design.md §1 verbal anchor + §13.5 narration anchors; chose film-as-product framing because P18 bias is visual storytelling and other advocates own dashboard / UI / cli surfaces — non-overlap secured by treating narrative-as-interface as the differentiating primary_surface."
}
```

---

## ASCII Scene Storyboard

```
═══════════════════════════════════════════════════════════════════
  LANDING.HTML  ·  6 SCROLL-ACTS
═══════════════════════════════════════════════════════════════════

  ┌─────────────────────────────────────────────────────────────┐
  │  HERO SCENE  ·  "The moment the judge audits itself"         │
  │                                                              │
  │      ·  ·  *  ·       *  ·       ·  ·       *               │
  │   *  ·        ___        ·       ·    *                     │
  │           .-'`   `'-.            ╱╲ qdrant                  │
  │   YELLOW  |  (◉‿◉)  |          *  ╲  503 anchors            │
  │   ┌──┐    `─-─────-─'             ╲*                        │
  │   │!!│  ⟿⟿⟿⟿  PHOENIX EYE  ⟸⟸⟸  *                        │
  │   └──┘                                                       │
  │   ▔▔▔ stage ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔                │
  │  silhouette audience                                         │
  │                                                              │
  │        ✦ A film about fairness · 3 min ✦                    │
  │     [▶ Watch the 3-min film]  [Meet the cast]                │
  └─────────────────────────────────────────────────────────────┘
                          ↓ scroll
  ┌─────────────────────────────────────────────────────────────┐
  │  ACT I — THE CAST  ·  Six hats as characters                 │
  │                                                              │
  │  ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐                              │
  │  │白│ │紅│ │黃│ │黑│ │綠│ │藍│                              │
  │  │ω │ │ψ │ │^ │ │o │ │∪ │ │— │                             │
  │  └──┘ └──┘ └──┘ └──┘ └──┘ └──┘                              │
  │  Facts Gut  LEAD Skep Wild Cond                              │
  │       (Yellow has the lead role)                             │
  └─────────────────────────────────────────────────────────────┘
                          ↓
  ┌─────────────────────────────────────────────────────────────┐
  │  ACT II — THE TURN  ·  "9 out of 10"... silence              │
  │  ┌──────────────┐                                            │
  │  │ A1 CLARITY   │  4 steps:                                  │
  │  │  ❤ 9.0 ────  │  1. Detection (triple-redundant)           │
  │  │  ✕═══════    │  2. Phoenix MCP consultation               │
  │  │  ✓ 7.6       │  3. Qdrant anchor retrieval                │
  │  │ ◉◉◉ anchors  │  4. Score correction on screen             │
  │  └──────────────┘                                            │
  └─────────────────────────────────────────────────────────────┘
                          ↓
  ┌─────────────────────────────────────────────────────────────┐
  │  ACT III — THE PROOF  ·  Dual-rubric variance                │
  │  ┌─────────────┐  ┌─────────────┐                           │
  │  │  Qdrant     │  │  Rapid/Arize│                           │
  │  │   87        │  │    73       │                           │
  │  │ orig·func·  │  │ tech·innov· │                           │
  │  │ ux·vector   │  │ impact·pres │                           │
  │  └─────────────┘  └─────────────┘                           │
  │     "Correct rubric-aware variance, not bias."               │
  └─────────────────────────────────────────────────────────────┘
                          ↓
  ┌─────────────────────────────────────────────────────────────┐
  │  FINALE  ·  503-anchor constellation                         │
  │     ·  *  ·  *    ★(winner)    ·  *  ·  *                   │
  │   "Same engine. Different rubric. Different score."          │
  └─────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════
  DEMO.HTML  ·  6 CINEMATIC STAGES (auto-play, scrub-able)
═══════════════════════════════════════════════════════════════════

  STAGE 1 · 00:00 ────────────────────────────────────────────────
   "The judge audits itself." — title card, fade in over starfield

  STAGE 2 · 00:30 ────────────────────────────────────────────────
   ┌─────────────────────────────────────────────────────────┐
   │                                                          │
   │    YELLOW (entering, confident strut)                    │
   │       (^‿^)         ╔═══════════════════╗               │
   │      ┌───┐    ───▶  ║ A1 Clarity        ║               │
   │      │ Y │          ║ 9.0 out of 10     ║               │
   │      └───┘          ╚═══════════════════╝               │
   │   confidence-aura     (speech bubble pops)               │
   │                                                          │
   │   [evidence pile sits ignored at depth=0.31]             │
   └─────────────────────────────────────────────────────────┘

  STAGE 3 · 01:00 ────────────────────────────────────────────────
   ┌─────────────────────────────────────────────────────────┐
   │   ⚠ ONLINE          ╱─────────╲                         │
   │   ⚠ CUSTOM   ⟶⟶⟶  │  PHOENIX  │  ← lid lifts            │
   │   ⚠ BLACK          ╲   (◉)    ╱     iris focuses        │
   │                     ╰─────────╯     glow expands        │
   │                                                          │
   │           "Yellow over-confident by 1.2 pts."            │
   └─────────────────────────────────────────────────────────┘

  STAGE 4 · 01:30 ────────────────────────────────────────────────
   ┌─────────────────────────────────────────────────────────┐
   │              QDRANT · 503 PAST SUBMISSIONS               │
   │       ·  ·  *   *  ·  *  ·  *   ·  *  *                 │
   │              ┌─────┐                                     │
   │      ┌─────┐ │ 7.5 │ ┌─────┐                            │
   │      │ 7.2 │─────────│ 7.8 │     stars pop in,          │
   │      └─────┘         └─────┘     lines draw between     │
   │              recommend(+,−)                              │
   │                                                          │
   │       "37 of 503 matched. Winners: 0."                   │
   └─────────────────────────────────────────────────────────┘

  STAGE 5 · 02:00 ────────────────────────────────────────────────
   ┌─────────────────────────────────────────────────────────┐
   │                                  ┌──────┐                │
   │   YELLOW (humbled, smaller)      │ 9̶.̶0̶  │  ← strike     │
   │      ( ◕︵◕ )                     └──────┘                │
   │       ┌─┐    ‧° (sweat)          ┌──────┐  ↑ rises      │
   │       │y│  ↓ shrink              │ 7.6  │   CALIBRATED  │
   │       └─┘                        └──────┘                │
   │                                                          │
   │   3D graph node ⟿ migrates to winner cluster             │
   └─────────────────────────────────────────────────────────┘

  STAGE 6 · 02:30 ────────────────────────────────────────────────
   ┌─────────────────────────────────────────────────────────┐
   │                  *   ·   *   ·   *                       │
   │              ·                       ·                   │
   │                    ╱─────────╲                           │
   │                   │  (◉)      │     ← Phoenix watching   │
   │                    ╲─────────╱                           │
   │              ·     winner ★      ·                       │
   │                                                          │
   │            Same engine.                                  │
   │            Different rubric.                             │
   │            Different (correct) score.                    │
   └─────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════
  CHAPTER SCRUBBER (bottom rail, cinema-style)
═══════════════════════════════════════════════════════════════════

  ▶  [■■■][■■■][   ][   ][   ][   ]   01:00 / 03:00
     Open  Yel  Phx  Qdr  Cal  Final
```

---

## File manifest

| File | Purpose | Size budget |
|---|---|---|
| `landing.html` | Scroll-story landing — Hero scene → Cast → The Turn → Proof → Finale | ≤55 KB |
| `demo.html`    | 6-stage demo film — auto-play, chapter scrubber, cinematic transitions | ≤70 KB |
| `_proposal.md` | This file | ≤10 KB |
| **TOTAL**      | All three artifacts                                                   | **≤90 KB** combined |

---

## Design rationale (one paragraph each)

**Why a film, not a UI.** Other advocates ship dashboards, CLIs, IDE-style monitors. The Designer bias says: judges decide on feeling in the first 30 seconds. A scrolling story with characters (Six Hats as Pixar-style avatars), a protagonist arc (Yellow's overconfidence → humbling), and a final-frame closing shot lets the *emotional truth* land first; the technical truth then feels inevitable.

**Why Yellow is the lead.** Per `wow-moment-design.md` §1 the verbal anchor is *Yellow over-confident on A1 by 1.2 pts*. Yellow is the natural protagonist because optimism is the most relatable bias — every judge has been Yellow. The audience sees themselves in Yellow, then feels relief when Phoenix + Qdrant correct him.

**Why Phoenix is an eye.** Phoenix MCP is observability — literally the act of seeing. A blinking eye that opens, focuses an iris, and stays watching is the cleanest visual metaphor for *meta-evaluation*. The phoenix-feather eyelashes nod to the Arize Phoenix brand without using their logo.

**Why Qdrant is a constellation.** 503 past submissions = 503 stars. Three anchors lighting up with connecting lines = the Recommendation API call made tactile. The constellation metaphor scales: backdrop dust = full corpus, foreground bright stars = retrieved anchors, gold star = winner cluster. One visual, three layers of meaning.

**Why the final frame is just the eye.** Movie endings are quiet. After the action of correction, the closing shot is the eye still open, still watching, with the winner-star pulsing below. The captions *"Same engine. Different rubric. Different (correct) score."* land in silence — Doumont-style cognitive minimum, maximum recall.
