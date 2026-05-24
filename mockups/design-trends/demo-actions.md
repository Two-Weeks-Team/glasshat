# Glasshat Design-Trend Gallery — Demo Actions

Participant-facing only (no judge/evaluator mode). Every trend conveys the same core
truth dynamically: **the user sees the evaluation happen, sees the evidence behind each
score, and watches the panel catch and correct its own over-confidence before the score
is final.** Each mockup is a single self-contained HTML file (inline CSS/JS, no network).

Open the gallery: `mockups/design-trends/index.html`. Live model named throughout:
`gemini-3.1-flash-lite` (Vertex AI) · Arize AX tracing · Phoenix MCP calibration path.

## Persona → Trend → one on-screen demo action

| # | pf persona | Design trend | File | Demo action (what the user does / sees) |
|---|---|---|---|---|
| 01 | the-design-forward | Aurora Glassmorphism | `01-aurora-glassmorphism.html` | Paste pitch → **Evaluate transparently**: pipeline animates node-by-node, each hat opens a frosted glass evidence drawer with retrieved source spans; at Audit, YELLOW visibly self-corrects 9.0 → 7.8, then the final score ring + rubric breakdown resolve. |
| 02 | the-ai-native | Generative AI-Native Canvas | `02-ai-native-canvas.html` | Click **Evaluate live**: the six hats stream token-by-token; click **Open evidence** on any card to see the exact retrieved sentence; the Audit card pulls Yellow 9.0 → 7.8 in place before the gauge settles. |
| 03 | the-game-designer | Gamified Evaluation Quest | `03-gamified-quest.html` | Click **Start Evaluation**: YELLOW posts an over-confident 9.0, then the BLUE referee's **Fairness Power-Up** corrects it to 7.8 to match the evidence found; open any hat's evidence badge to verify. |
| 04 | the-mobile-first | Mobile Live Bottom-Sheet | `04-mobile-bottomsheet.html` | Tap **Evaluate**: the pipeline streams in a draggable bottom sheet; Self-audit recalibrates YELLOW 9.0 → 7.8; tap any hat chip to open the exact retrieved deck quote behind its sub-score. |
| 05 | the-designer | Editorial Kinetic Typography | `05-editorial-kinetic-type.html` | Press **Run evaluation**: stages animate; Yellow's score kinetically counts DOWN 9.0 → 7.8 with a struck-through "recalibrated" flag; open any score to surface the quoted pitch lines that grounded it. |
| 06 | the-data-nerd | Live Telemetry Cockpit | `06-telemetry-cockpit.html` | Press **run live evaluation**: a trace-span waterfall fires; the CalibrationAudit span draws a Δ−1.2 marker and pulls YELLOW 9.0 → 7.8 before the score commits; click **view evidence** to slide open retrieved quotes. |
| 07 | the-dreamer | Spatial 3D Constellation | `07-spatial-constellation.html` | Watch the pipeline reveal each criterion node; the over-confident YELLOW node visibly drifts outward as it self-corrects 9.0 → 7.8 during Self-Audit; click a node to open its grounded, cited evidence. |
| 08 | the-privacy-hawk | Transparent Trust Ledger | `08-trust-ledger.html` | Click **Run evaluation**: ledger entries append live; the Audit flags YELLOW and self-corrects it (9.0 → 7.8) as a "SELF-CORRECTED" entry before the score is sealed against a chained root hash; open any entry's evidence to read the source line + hash. |
| 09 | the-educator | Guided Step-Reveal Explainer | `09-guided-explainer.html` | Click **Evaluate my pitch**: the pipeline steps forward with plain-language captions; the Self-Audit explains the fairness moment, then corrects Yellow 9.0 → 7.8; each hat has a "Why this score? · open evidence" panel. |
| 10 | the-speed-obsessed | Instant Optimistic Minimal | `10-instant-minimal.html` | Click **Evaluate**: skeleton → result resolves fast; the Audit step flips YELLOW's number 9.0 → 7.8 inline before the final locks in; click any hat to open the retrieved evidence behind its sub-score. |
| 11 | the-contrarian | Neo-Brutalist | `11-neo-brutalist.html` | Hit **EVALUATE ME**: a monospace terminal log runs the pipeline bluntly; it FLAGS the over-confident YELLOW hat and self-corrects 9.0 → 7.8 (9.0 struck) before the weighted final; evidence is openable inline. |
| 12 | the-indie-hacker | Bold Conversion Landing | `12-bold-conversion-landing.html` | Click the hero CTA **Run live evaluation**: an inline 6-stage pipeline animates; **See the evidence** opens the pitch lines + rubric criterion behind a score; the Audit pulls Yellow 9.0 → 7.8 before the grounded final on the 0–10 scale. |
| 13 | the-researcher | Provenance & Citations | `13-provenance-citations.html` | Click an inline citation **[n]** next to a score: its grounding passage highlights in the References panel; the Auditor visibly corrects Yellow 9.0 → 7.8 as a rigorous calibration note appears, before the final score is reported. |

## The shared "transparent evaluation" beat (in every trend)

1. **Live pipeline** — Input → RubricSynthesizer → BluePlanner → SixHatPanel → Audit → Final score animates on screen.
2. **Evidence on demand** — each sub-score opens to the exact retrieved passage from the user's own pitch that grounded it.
3. **Self-correction** — the Audit catches an over-confident hat (YELLOW 9.0 → 7.8) and visibly pulls it back *before* finalizing.
4. **Transparent final** — the score lands on the rubric's native scale with a per-criterion breakdown the user can read.
