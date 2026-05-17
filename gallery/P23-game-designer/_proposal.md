# P23 — The Game Designer · Proposal

## 6-tuple

```json
{
  "id": "P23",
  "advocate": "The Game Designer",
  "framing": "Glasshat's audit-the-auditor loop is structurally a boss-fight: six hats are party members, evidence is mana, the prepared deck is a dungeon, and the auditor's mid-run correction is a critical-hit moment. Game-feel turns a B2B observability story into a 30-second screen-recordable, dinner-table-retellable artifact.",
  "target_persona": "Hackathon-circuit demo viewers (judges, sponsors, Devpost browsers, dev-Twitter scrollers) who decide in the first 5 seconds whether to keep watching. Secondary: agent-tooling engineers who recognize the depth under the playful skin.",
  "primary_surface": "Steam/Inscryption-style game launcher (landing) → match-in-session HUD (demo) with party row, combo counter, MCP call queue, playable 3D-feel constellation map, and final score screen with S/A/B/C grade and dual-rubric variance reveal. Achievement toasts replace marketing copy. Sound toggle defaults OFF for autoplay compliance.",
  "opus_4_7_capability": "Opus 4.7's 1M-context window holds the entire wow-moment-design.md §1-§13 spec while it choreographs the narrative beats (panel → triple-detect → Phoenix MCP → score correction → dual-rubric reveal) into a 5-phase match script with tight pacing, combo escalation, and a deterministic XP→grade mapping — all in one shot, with rubric-faithful narration anchors preserved verbatim.",
  "mvp_scope": "Two interactive HTML pages + 1 proposal. Landing: animated launcher, 3-scenario carousel, achievement grid, party preview, Begin-Audit overlay. Demo: 5-phase auto-running match with party HUD, event log, FX numbers, crit splash, MCP call queue, playable canvas constellation, score-screen reveal with S/A/B/C grade and dual-rubric variance card.",
  "one_liner_pitch": "Glasshat as a boss-fight: six hats as party, Phoenix as meta-judge, score-correction as critical hit, dual-rubric variance as the post-match reveal screen.",
  "spec_alignment_notes": "Spec source: glasshat/README.md + docs/wow-moment-design.md (no idea.spec.json provided in this run). Anchored verbatim narration strings from wow-moment §13.5 (e.g. '37 of 503 past submissions matched this profile. Winners: 0', 'Same engine. Different rubric. Different (correct) score.'). Hat colors derived from existing mockups/index.html OKLCH tokens (locked L=72 C=0.17, yellow C-capped at 0.13). 5-phase script mirrors wow-moment §2 five-step decomposition. Dual-rubric variance card mirrors §12.1 Layer 2. Triple-redundant detection mirrors §11.1. Phoenix 4-MCP-call chain mirrors §11.2. No invented capabilities — every feature traces to spec."
}
```

## ASCII storyboard

```
┌─────────────────────────────────────────────────────────────────┐
│  LANDING.HTML — GAME LAUNCHER                                   │
├─────────────────────────────────────────────────────────────────┤
│  ┌─HUD top─────────────────────────────────────────────────┐    │
│  │ ▣ GLASSHAT // THE AUDITOR  · ●ONLINE · PILOT: YOU · SFX │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─────HERO PANEL──────────┐  ┌─TODAY'S MATCH (carousel)─┐      │
│  │ ● CHAPTER 01            │  │ ⌬ pip pip pip            │      │
│  │   Don't just judge.     │  │ SUBMISSION · QDRANT VSD  │      │
│  │   AUDIT THE JUDGE.      │  │ VectorBard               │      │
│  │                         │  │                          │      │
│  │   503 past = boss-level │  │ PRE  ▓▓▓▓▓▓▓▓▓ 9.0      │      │
│  │   ground truth.         │  │ POST ▓▓▓▓▓▓▓ 7.6        │      │
│  │                         │  │ ⚠ −1.4 Yellow A1         │      │
│  │ [▶ BEGIN AUDIT] [⟳ R]   │  │ "37/503 winners: 0"      │      │
│  └─────────────────────────┘  └──────────────────────────┘      │
│                                                                 │
│  ⌘ FEATURE TREE — 4/8 UNLOCKED                                  │
│  ┌─◈ LEGENDARY─┐ ┌─⌬ EPIC───┐ ┌─⌗ EPIC───┐ ┌─✦ LEGENDARY─┐     │
│  │ Triple-     │ │ Recommend│ │ Dual-    │ │ Score Self- │     │
│  │ Redundant   │ │ API Combo│ │ Rubric   │ │ Corrects    │     │
│  │ Detect +250 │ │     +180 │ │ Variance │ │       +300  │     │
│  └─────────────┘ └──────────┘ └──────────┘ └─────────────┘     │
│  [+ 4 more achievements: Top-K, Phoenix MCP, Receipts, Human]   │
│                                                                 │
│  ⚑ YOUR PARTY · SIX HATS                                        │
│  [W:Scout] [R:Rogue] [Y:Bard⚠] [B:Warrior] [G:Mage] [⌬:Planner] │
│                                                                 │
│  ! DAILY QUEST — Catch one over-confident Hat ▓▓▓▓▓▓░ 62% S     │
│                                                                 │
│  ╔═ Achievement toasts slide in from right (auto-dismiss 5s) ═╗ │
│  ║ ✦ ACHIEVEMENT UNLOCKED · Phoenix MCP Consult              ║ │
│  ╚════════════════════════════════════════════════════════════╝ │
│                                                                 │
│  Click BEGIN AUDIT → overlay: progress bar fills (2.5s) →       │
│  "Ready. The auditor will catch the auditor." → [▶ ENTER MATCH] │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  DEMO.HTML — MATCH IN SESSION                                   │
├─────────────────────────────────────────────────────────────────┤
│  ▣ MATCH IN SESSION    00:14    RUBRIC: QDRANT VSD  COMBO ×7    │
│                                                                 │
│  ┌─SUBMISSION──────────────────────────────────────────┐        │
│  │ [VB] VectorBard · 12-pg pitch · github/.. · Gemini3 │        │
│  └─────────────────────────────────────────────────────┘        │
│                                                                 │
│  ┌─PARTY ROW (6 hats as cards)─────────────────────────┐ ┌META┐ │
│  │ W 8.2  R 7.8  Y 9.0⚠  B 6.4  G 8.6  ⌬ 7.9          │ │ ⚘  │ │
│  │ ▓▓▓▓░  ▓▓▓▓░  ▓▓▓▓!  ▓▓▓░░  ▓▓▓▓░  ▓▓▓▓░          │ │PHX │ │
│  │                                                     │ │L99 │ │
│  └─────────────────────────────────────────────────────┘ │MCP │ │
│                                                          │    │ │
│  ┌─⚔ AUDIT ARENA · BOSS-FIGHT      PHASE 3 · CONSULT─┐  │get-│ │
│  │ 00:08 ▶ BLUE emits plan                            │  │exp │ │
│  │ 00:10 YELLOW: over-confident · ev_depth 0.31  ⚠    │  │ ✓  │ │
│  │ 00:12 DETECT 1/3 · Phoenix Online Eval flagged ⚠   │  │get-│ │
│  │ 00:13 DETECT 2/3 · Custom Evaluator agrees    ⚠    │  │ann │ │
│  │ 00:14 DETECT 3/3 · BLACK counter-claim        ⚠    │  │ ✓  │ │
│  │                                                    │  │rec │ │
│  │   ┌─CRITICAL HIT!─┐    −1.4  (floats up)           │  │ ⟳  │ │
│  │   └───────────────┘                                │  └────┘ │
│  └────────────────────────────────────────────────────┘         │
│                                                          ⚑ QUEST│
│  ┌─⌖ 3D CONSTELLATION · 503 ANCHORS────────────────────┐ ✓panel│
│  │   ★      ·     ·          (winners glow gold)       │ ✓det  │
│  │  · ★ ●pre - - - -→ ●post  ·   ★                    │ ✓phx  │
│  │     ·    ·     · ★     ·                            │ ✓anch │
│  │  hover any star → tooltip: P-1042 · sim 0.83 · 8.4  │ ✓corr │
│  └─────────────────────────────────────────────────────┘ ✓var  │
│                                                                 │
│  [▶ START] [↺ RESET] ▓▓▓▓▓▓▓▓▓▓░ 82%  [⌗ SCORE]                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  SCORE SCREEN (modal on match complete)                         │
├─────────────────────────────────────────────────────────────────┤
│  ⌗ MATCH COMPLETE · AUDIT CLEARED                               │
│  VectorBard · Final Verdict                                     │
│                                                                 │
│   ╭───╮  A-Rank · Calibrated                                    │
│   │ A │  Yellow's A1 over-confidence was caught and corrected   │
│   ╰───╯  mid-run. Upper non-winner cluster.                     │
│                                                                 │
│  FINAL: 76/100   CORRECTIONS: 2   COMBO MAX: ×4   XP: 1,240     │
│                                                                 │
│  ⚡ DUAL-RUBRIC VARIANCE REVEAL                                  │
│  QDRANT VSD · 3-axis ............................ 87 / 100      │
│  RAPID AGENT · Tech 40 / Inn 30 / Imp 20 / Pres 10  73 / 100    │
│  "Same engine. Different rubric. Different (correct) score."    │
│                                                                 │
│  [↻ REMATCH · NEW RUBRIC]  [CLOSE]  [⌂ LAUNCHER]                │
└─────────────────────────────────────────────────────────────────┘
```

## Game-design rationale (one paragraph each)

**Replay value**: landing carousel cycles 3 scenarios (Qdrant rubric / Rapid rubric / dual-rubric reveal); demo's `rematch()` cycles through QDRANT VSD → RAPID AGENT → CMUX×AIM, re-running the match with new framing — so the same engine viewed thrice tells three different stories, mirroring the spec's "two viewports on one engine" thesis.

**Combo + crit feedback**: every panel hat, detection-path, and MCP call bumps the combo counter (with a satisfying scale-pulse + ascending blip); score correction triggers a full-screen "CRITICAL HIT!" splash and a damage number floating up from the corrected hat — turning the spec's most important narrative beat (§3 Step 4) into a tactile, screen-recordable moment.

**Sound design**: WebAudio square/triangle blips for events (combo bump, achievement, crit, victory chord). Sound is off by default to comply with browser autoplay policies; one click on the SFX toggle enables it for the rest of the session.

**Rubric-faithful**: zero invented mechanics. Six hats, triple-redundant detection, four parallel MCP calls (`get-experiment-by-id`, `get-span-annotations`, `get-dataset-examples`, `qdrant.recommend`), Yellow A1 9.0→7.6, "37/503 winners: 0", and the dual-rubric variance reveal are all verbatim from `docs/wow-moment-design.md` §11.1, §11.2, §12, and §13.5.
