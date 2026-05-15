# Glasshat — Interactive Demo Prototype Spec

> **Live URL**: https://two-weeks-team.github.io/glasshat/prototype.html
> **Source**: `mockups/index.html` (single self-contained file, 2,268 lines, 89 KB)
> **Status**: prototype **v0.3** locked 2026-05-15. Approval-gated artifact — sign-off enables Phase 1 D code start.
>
> **v0.3 changelog** (2026-05-15): 10-persona expert panel review (UX Researcher, Senior Designer, Performance Eng, Hackathon Judge, VC Investor, Motion Designer, A11y Expert, Demo Director, Backend Eng, Skeptic) found 98 improvement points. ~30 P0/P1 applied: Three.js lazy load (PERF-1), 3D constellation as Tier 1 hero (JUD-1/DES-1), category-anchored hero copy (VC-1), Plain English caption toggle (UX-3), role-based CTAs (UX-2), Qdrant Live persistent badge (JUD-2), Why -1.4 expand panel with real anchors (JUD-3), `(correct)` → `rubric-faithful` (SK-1), Rubric Sanity Layer (SK-2), all trace names match OpenInference/Phoenix MCP/Qdrant API exactly (BE-1/2/10), math reconciles `9.0 - 0.8×1.75 = 7.6` (BE-3), full A11y (`prefers-reduced-motion`, `forced-colors`, `:focus-visible`, skip link, `aria-live`/`aria-label`/`aria-pressed`, semantic `<h2>` + landmarks), micro-beats fill 1:00-1:30 dead air (DEM-1), climax cinematic isolation (DEM-2), closing callback `It audits the judge.` (DEM-3), reveal stack pills + multi-CTA (DEM-7), OKLCH locked hat colors L=72 C=0.17 (DES-4), 6-step type scale + spacing 2-tier (DES-3/6), selective glass (DES-7), spring/out/emphasized easing semantics (DES-9/MO-3), debounced resize (PERF-2), scrubber transform-only (PERF-7), scrubber as ARIA slider with arrow keys, `EU AI Act Art. 12` compliance vocab (VC-6), "Why now" line (VC-9), unit economics in cost ticker (UX-9), scene markers + non-flicker scrubber seek (UX-7).

---

## Why this prototype exists

Per user's 2026-05-15 directive: **before we burn engineering time on ADK / GCP / Vertex / Phoenix wiring, prove the wow + interaction model in a click-through artifact**. Decisions resolved by the prototype:

- Does the wow moment land in <30 seconds for a non-team viewer?
- Is the dual-rubric variance display comprehensible without explanation?
- Does the Judge × Participant viewport split feel like one product or two?
- Does the 3D graph add value or distract?
- Is the 2026 visual language cohesive?

Approval here unlocks ~$X engineering investment and Phase 1 ~10d sequence ([[glasshat-rubric-and-mode]] §6). Reject here = cheaper to redesign.

---

## What's in the prototype

### Self-contained delivery
- **Single HTML file** (`mockups/index.html`) — no build step, no backend, no API keys
- **Three.js via CDN** for the 3D constellation (only external dep)
- **Google Fonts CDN** for variable Inter + JetBrains Mono + Space Grotesk
- **Zero data fetches** — all state hardcoded; safe to share/embed/airgap

### Two viewports on one engine
- **Judge mode** (Qdrant primary demo) — batch evaluation Kanban + Top-K hit rate badge + 503 anchor 3D constellation
- **Participant mode** (Rapid Agent primary demo) — single submission + Phoenix MCP iterate-loop + score animation
- Toggle in header switches both at runtime; same engine UI, different scenario script

### Auto-play scenario player
- 3-minute time-coded sequence per viewport (180s, scrubbable)
- Mouse-cursor simulation in auto mode (visible cursor moves to dropzone, clicks)
- All wow beats land at exact times matching `docs/max-wins-plan.md` §5.1 (Qdrant) and §5.2 (Rapid Agent)
- Scrub anywhere on the timeline to jump

### Manual mode
- Curtain landing offers `Manual · Judge mode`
- Click anywhere advances time +5s (so viewer can study a beat as long as they want)
- Pause/play in header toggles autoplay

### Visible production-relevant components
- 6-Hat panel with **Live Bias Meter** dial (sangguen 6.8) — turns red when Yellow over-confident
- **Score Receipts UI** (sangguen 6.11) — dual-rubric panel showing the same submission scored under TWO synthesized rubrics
- **3D Evaluation Constellation** — 503 anchors color-coded by tier (gold=winner, grey=non), current submission as glowing magenta point that migrates after audit correction
- **Winner Gravity callout** (sangguen 6.10) — floating tooltip on the moving node
- **Phoenix Monitor live trace** — append-only log of MCP calls, evaluator firings, calibration deltas
- **Anti-Pattern Radar narration** (sangguen 6.9) — caption appears at audit moment
- **Dual-Rubric Variance banner** — appears at 2:30, captioned per spec
- **Top-K hit rate badge** — appears at 2:42 in Judge mode
- **Cost ticker** — animates throughout, demonstrates production-discipline tone
- **Final reveal overlay** — caption: *"Same engine. Different rubric. Different (correct) score."*

---

## What's NOT in the prototype (intentional)

| Production thing | Why not in prototype | Where it goes |
|---|---|---|
| Real Vertex Gemini calls | Prototype is offline-safe | Phase 1 D (LLM adapter) |
| Real Qdrant queries | Same | Phase 1 B (Qdrant + 6 collections) |
| Real Phoenix MCP | Trace is scripted text | Phase 1.4 |
| Real PDF / repo ingestion | Prototype assumes input | Phase 1 C |
| Real RubricSynthesizer Gemini call | Rubric output is hardcoded as if synthesized | Phase 1.5 (full spec: `docs/rubric-synthesis-spec.md`) |
| Authentication / RLS | Single-user offline | Phase 1.mode-UI (full spec: `docs/hybrid-mode-spec.md`) |
| Editing / file upload | Prototype shows ingestion as scripted action | Production: drag-drop with real GCS upload |

---

## 2026 design trends — the choices we made

### Color: OKLCH-native palette
- Background: `oklch(13% 0.018 250)` — deep, warm-cool navy (not pure black; less harsh on judges' eyes)
- Primary: `oklch(75% 0.16 215)` — Glasshat cyan, perceptually saturated
- Accent: `oklch(78% 0.20 350)` — magenta, used for the score-correction beat
- Gold: `oklch(82% 0.16 88)` — winner anchors + Top-K badge
- Why OKLCH: 2026's perceptually-uniform color space; gradients between hues stay visually consistent (no muddy purples between blue→red); supported in all modern browsers including Safari Tech Preview

### Typography: variable + display contrast
- Display: **Space Grotesk** — modern geometric sans, used for headings + brand
- Body: **Inter** (variable) — feature-set `cv11, ss01, ss03` for tabular numerics
- Mono: **JetBrains Mono** — used in trace, hat scores, badges
- Why these: each one is a 2024-2026 hot pick with clear metrics support and multiple weights in the same file (variable), meaning the prototype downloads less while supporting the wow's typographic motion

### Layout: bento grid (CSS Grid + grid-template-areas)
- 4 cards: Hats panel (left tall) · 3D graph (center) · Phoenix monitor (right tall) · Score Receipts (bottom wide)
- Why: Bento layouts dominated 2024-2026 SaaS dashboards (Linear, Vercel, Resend, OpenAI); they let the eye process N parallel domains without scrolling
- Responsive: single column on mobile, 2-column on tablet

### Glass surfaces: subtle, not heavy
- `backdrop-filter: blur(20px) saturate(140%)` on cards
- 1px border at 10-20% white-on-dark
- Elevated shadow + 1px inner highlight
- Why subtle (vs 2020-2022 heavy frosted glass): 2026 trend is "*just enough*" — the depth signal is real but doesn't fight the content

### Motion: spring easings + meaningful animations
- All transitions use `cubic-bezier(0.34, 1.56, 0.64, 1)` for spring overshoot
- Score change animation: easeOutCubic counter from old → new value
- 3D camera: continuous slow rotation
- Cursor: 1.2s easeOut between waypoints (feels "human", not robotic)
- Reveal: fade + spring scale
- Why: Material 3 Expressive (2025) and Apple visionOS 2 (2026) normalized spring physics; static interactions feel dated

### Depth: stacked surface elevation
- Card hover: border lights up + `translateY(-1px)`
- Active (current) card: glow ring (`box-shadow: 0 0 24px var(--primary-soft)`)
- 3D graph: real perspective + camera depth
- Why: spatial UI (hint of visionOS / Apple Spatial) without committing to AR/VR — communicates "production polish"

### Interaction language
- Pressed buttons (viewport toggle): inset shadow + filled background
- Hover lift on cards (1px translate + brightness)
- Cursor click ripple (visible in auto mode only — confirms automation isn't a static gif)
- Captions fade-swap (200ms) instead of cut
- Why: judges process *micro-interactions* as signal of engineering taste; missing them = "unfinished"

---

## Demo timing — what happens when (Judge mode example)

Per `docs/max-wins-plan.md` §5.1 + sangguen narration locks:

| Time | Beat | What viewer sees |
|---|---|---|
| 0:00 | Hook | Caption: *"Glasshat doesn't just judge projects. It audits the judge."* |
| 0:05 | Lead-in | Caption: instructions for upload |
| 0:10 | Cursor moves | Auto-cursor moves to dropzone, clicks |
| 0:12 | Kanban appears | Overlay: 7-column Kanban with cards streaming |
| 0:15 | First batch | 50 cards distributed across columns |
| 0:20 | Mid batch | 150 cards, cost: $0.024 |
| 0:25 | More cards | 300 cards, cost: $0.080 |
| 0:30 | Plan + Hats | Kanban hides, RubricSynthesizer plan visible, 6 Hats activate (parallel) |
| 0:34 | Scoring | 6 Hat scores fill in (partial values) |
| 0:42 | Full scores | 6 Hat scores at full values, cost ticks |
| 0:50 | Yellow bias | Yellow Hat A1=9.0 with bias meter pegged red, caption explains |
| 1:00 | Detection | Phoenix Online Eval card appears, trace logs fire |
| 1:05 | Triple-redundant | Trace shows Custom Eval + Black Hat counter-claim |
| 1:15 | Phoenix MCP | Trace shows MCP calls cascading |
| 1:20 | Anchors | Trace shows Qdrant Recommendation API + 3 anchor projects |
| 1:24 | Correction | Trace shows ScoreCalibrationAgent applying delta |
| 1:27 | Yellow updates | Score animates 9.0 → 7.6, Hat row turns green |
| 1:45 | 3D fly | Current node migrates toward winner cluster |
| 1:55 | Gravity callout | Floating tooltip: "72% similar to winner cluster, but pulled toward..." |
| 2:10 | Anti-Pattern | Caption: "37 of 503 past submissions matched. Winners: 0." |
| 2:30 | Dual-Rubric | Variance banner appears: Δ = 14, "correct rubric-aware variance" |
| 2:38 | Variance hold | Caption emphasizes the variance message |
| 2:42 | Top-K | Gold badge appears: "9/13 winners in predicted top-13" |
| 2:50 | Close | Caption: *"And the auditor is the vector space."* |
| 2:55 | Reveal | Full-screen overlay: *"Same engine. Different rubric. Different (correct) score."* |

Participant mode timing matches but with different scenario: single submit, mid-loop Phoenix consultation, score 73 → 79 animation, Phoenix annotation write-back visible.

---

## Approval criteria (sign-off here unlocks Phase 1 D start)

Reviewer should verify:

- [ ] **Auto-play Judge mode** runs end-to-end without freezing or blank screens
- [ ] **Auto-play Participant mode** runs end-to-end (toggle viewport in header or click "Auto-play · Participant")
- [ ] **Wow moment** (audit + score self-correction at ~1:27) is comprehensible without prior knowledge
- [ ] **Dual-rubric variance** scene at 2:30 communicates "same submission, two rubrics" without explanation
- [ ] **3D constellation** rotates smoothly; current submission node visible and migrates after correction
- [ ] **Phoenix Monitor trace** logs are believable (real OpenInference span names, not Lorem)
- [ ] **Visual cohesion** — colors, typography, motion feel like 2026 (not 2018, not 2030)
- [ ] **Manual mode** — clicking advances; user can take their time on each beat
- [ ] **Mobile** — try on iPhone Safari; layout collapses gracefully (1 column, header stacks)

If all checked: ✅ **approve Phase 1 D start** (`services/shared/llm.py`).

If any failed: ❌ open GitHub issue with screenshot + describe what failed; iterate prototype before code.

---

## Production wiring map (when approved)

For each prototype mock, this is where the real implementation lands:

| Prototype mock | Real implementation | Owner |
|---|---|---|
| `appendTrace()` calls | OpenInference auto-instrument + custom span attributes | Backend |
| `correctYellow()` animation | Real ScoreCalibrationAgent + SSE stream + same animation code | Backend + Frontend |
| `fillRubricScores()` data | Real Six Hats output → BMADScorer → response | Backend + Frontend |
| `kanbanBatch()` random distribution | Real Cloud Run Jobs queue state | Backend |
| 3D anchor positions | Real Qdrant `past_evals` weights_vector → UMAP/PCA projection | Backend + Frontend |
| Cost ticker hardcoded | Real `before_model` callback summing token cost | Backend |
| Captions hardcoded text | Pre-recorded narration matching demo storyboard | QA/Demo |
| Phoenix Eval card content | Real Phoenix Online Eval annotation via MCP `get-span-annotations` | Backend |
| Variance banner Δ=14 | Real BMADScorer run twice (cheap re-score) under both rubrics | Backend |
| Top-K hit rate badge | Real `scripts/check_top_k_hit_rate.py` against 503 corpus | Data |
| Dual-rubric block scores | Real RubricSynthesizer outputs (preset Qdrant + Rapid Agent) | Backend |

---

## Iteration plan (if approved with changes)

If reviewer says "approve, but tweak X":

| Tweak class | Action |
|---|---|
| Color/typography | Edit CSS custom properties in `:root`; live-reload |
| New scenario beat | Add `{ t: <sec>, fn: () => {...} }` to `buildScenario()` |
| Wow moment timing | Adjust `t` values; scenario re-runs scrubbed |
| Add new component | Add to `<main>` bento grid + render function |
| Different sample submission | Edit `CFG.hats[].baseScore` + `submission-name` |
| Branding | Update `.brand-mark`, font-family vars |

Each tweak is <1h. The prototype is intentionally small (1,767 lines) for fast iteration.

---

## Decisions still deferred

These are NOT decided by the prototype; await user/team input:

- **Logo asset**: prototype uses CSS-rendered "G" badge. Real logo TBD.
- **Demo voice/audio**: prototype is silent. If we add voice-over for YouTube, who records, in what tone?
- **Korean i18n in production frontend**: max-wins-plan §12 says cut from v1. Confirm with team.
- **Phoenix Cloud account branding**: do we use the public Phoenix UI or our own dashboard? Affects Demo recording.
- **Dataset for live demo**: 503 corpus is calibration; what gets *evaluated* in the actual recorded demo? An impressive Gemini 3 winner? A fictional submission engineered to trigger the audit?

---

*Last updated: 2026-05-15 KST. Authoritative on prototype design + approval criteria. Update when prototype iterates.*
