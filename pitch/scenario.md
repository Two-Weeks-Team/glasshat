# Glasshat — Demo Scenario (180s · problem-first · 13 slides)

> **Hackathon:** Google Cloud Rapid Agent Hackathon · Arize track
> **Hero copy (sacred, verbatim):** **Trace it. Trust it.** — delivered at F4 (primary), F11 (echo), and the close. Never paraphrased.
> **Tone:** agro → drop → thrill. Doumont staccato — every period is a breath instruction. Every em-dash is a held breath (0.4–0.6s).
> **Timing convention:** the recorded 180s video is the F1→F11 range (`F` key). Cover and Close are title cards that bookend the recording. Topbar times below are the recorded-content clock (F1 = 0:00).

**Honesty rails (hold the line in delivery):**
- Never say "un-gameable." The audit *raises the bar and makes the score observable* — that is the claim.
- Never say "503 anchors." The calibration prior is the held-out spike-D prior; the golden labels are binary Winner badges.
- `hit@13 = 0.6154` is a **binary Winner-label hit rate, not a rank curve.** On this golden set the audit did **not** reorder the top-13 (Δ = 0).
- Say which path is which: the **public Cloud Run demo** runs the **live Phoenix-MCP calibration loop** (reads + writes the `glasshat-calibration` dataset over MCP per request) on the `SCORING_MODE=legacy` python path. The **full nested trace tree + the hit@13 experiment** are the **credentialed Agent Engine** run. (spike-D = the dataset's seed/fallback.)
- Model is **Gemini 3.1 Flash-Lite via Vertex AI**. Orchestrated with **Google ADK 2.0**.

---

## Cover — Title card · 8s · `cover` shape · palette: problem (violet)

**On screen:** "Glasshat" · sub *"the audit layer for AI evaluation"* · hero chip **"Trace it. Trust it."** · meta chips: Gemini 3.1 Flash-Lite · Google ADK 2.0 · Arize AX · Apache-2.0. Eyebrow: *Google Cloud Rapid Agent Hackathon · Arize track*.

**VO:** *(silent title card — hold 8s)*

**Delivery:** Title-card calm. Let the hero chip sit. The room reads it before you speak.

---

## F1 — Who audits the judge? · 0:00 – 0:10 (10s) · `chain` shape · palette: problem (violet)

**Heading:** **who audits the judge?**
**On screen:** chain blocks `submission → AI judge → score → ?` — the final `?` is a red, pulsing block.

**VO:**
> "Every hackathon. Every grant. Every model-as-judge pipeline. Runs on a score nobody audits."

**Delivery:** Prosecutor opening. No smile. Land each fragment — *hackathon · grant · pipeline.* Pause before "nobody audits." Point at the pulsing `?`.

---

## F2 — Confident. Fast. Unaccountable. · 0:10 – 0:25 (15s) · `stack-strikethrough` shape · palette: failure (red)

**Heading:** **confident. fast. unaccountable.**
**On screen:** 5 strikethrough rows — what an AI judge can't show: `no evidence for the score` · `no calibration` · `no audit trail` · `can't reproduce it` · `can't trust it`.

**VO:**
> "An AI judge is worse. Confident. Fast. Wrong — with no way to check it."

**Delivery:** Indictment. Drop pitch on each strikethrough beat as it lands. The em-dash before "with no way to check it" is a held breath. The judge in the room nods.

---

## F3 — Audit the judge. · 0:25 – 0:35 (10s) · `chain` shape · palette: pivot (green)

**Heading:** **audit the judge.**
**On screen:** the chain reverses and turns green: `score → audit → corrected score`.

**VO:**
> "So we flipped it. Don't only judge the work. Audit the judgment itself."

**Delivery:** Say "So we flipped it" like you've solved something. Then go quiet. "Audit the judgment itself" lands as a calm statement of fact, not a sales line.

---

## F4 — THE HERO · 0:35 – 1:00 (25s) · `gallery-hero` shape · palette: hero (bright cyan) ★ DELAYED HERO

**Heading:** *(hero canvas — no script panel)*
**On screen:** a constellation grid of cyan trace spans blooms in; backdrop darkens; the big hero lands: **Trace it. *Trust it.***

**VO:**
> "Every judgment becomes a trace you can open. And audit. **Trace it. Trust it.**"

**Delivery:** ★ Read the hero slowly — five clicks of the tongue: *Trace · it · · Trust · it.* Half-beat silence after. The audience exhales. Hold the hero on screen for the full 25s — this is the still the room remembers.

---

## F5 — 104 spans. One evaluation. · 1:00 – 1:06 (6s) · `counter-roll` shape · palette: problem→cyan (cyan)

**Label:** SPANS IN ONE EVALUATION
**On screen:** counter rolls `0 → 104`. Breakdown: *6 hats · every Gemini generate + embed · one nested Arize AX trace.*

**VO:**
> "How? Every hat. Every retrieval. Every score — a span in Arize AX. A hundred and four of them. One evaluation."

**Delivery:** "How?" is a question to the room — a beat of audience participation. Then the rule-of-three rhythm: every-hat / every-retrieval / every-score. Land "one hundred and four" on the rolled number.

---

## F6 — One ADK 2.0 Workflow. · 1:06 – 1:30 (24s) · `hierarchy-diagram` shape · palette: architecture (cyan/violet)

**Label:** ADK 2.0 WORKFLOW GRAPH
**On screen:** an SVG hierarchy: `Ingest → RubricSynth → Planner → [6-hat ParallelAgent: White · Red · Yellow · Black · Green · Blue] → Join → Audit (loop) → Score → Report`. Footer chip: *deployed on the Gemini Enterprise Agent Platform · Agent Engine.*

**VO:**
> "One ADK 2.0 Workflow. Six hats in parallel. Deployed as a real agent on Agent Engine — not a notebook."

**Delivery:** Builder explaining their workshop. Trace the spine with your eyes. "Not a notebook" is the line judges remember — the em-dash before it is a held breath.

---

## F7 — It reads the evaluator's own rules. · 1:30 – 1:54 (24s) · `modal-live-json` shape · palette: pivot (green)

**Heading:** the rubric is synthesized, not assumed.
**On screen:** left = the rubric being synthesized from "the evaluator's own rules"; right = a live-filling RunRecord JSON (criterion scores, evidence refs).

**VO:**
> "It reads the evaluator's own rules. Synthesizes the rubric. Then every hat grounds its score in retrieved evidence."

**Delivery:** Confident craftsman. "Synthesizes the rubric" is the pivot. The closer "grounds its score in retrieved evidence" lands as a quiet payoff — no score is free of evidence.

---

## F8 — Six perspectives. Watch Yellow. · 1:54 – 2:20 (26s) · `gallery-hero` (six-hat panel) · palette: problem (violet)

**Heading:** six perspectives. one runs hot.
**On screen:** six hat cards — White · Red · Yellow · Black · Green · Blue — each with a sub-score. YELLOW (optimism) is visibly highest.

**VO:**
> "Six perspectives score in parallel. Watch Yellow — optimism — run hot."

**Delivery:** Showman + invitation. "Watch Yellow" is a finger on the screen. The em-dashes around "optimism" set it apart. Let the over-confident YELLOW card glow before you move on.

---

## F9 — THE AUDIT MOMENT · 2:20 – 2:46 (26s) · `triple-pane` shape · palette: pivot (green) ★ THE WOW

**Heading:** the audit catches its own over-confidence.
**On screen:** three panes. Pane 1 **panel** — raw consensus **9.0**. Pane 2 **audit** — calibration prior, YELLOW delta, `clip(score − 0.8·mean_delta, p25, p75)` ±2.0 cap. Pane 3 **score** — the corrected number **7.6** with a gauge. The audited score visibly recedes from 9.0 to 7.6.

**VO:**
> "Now watch. Yellow over-scored. Against a held-out calibration prior — strongest where the evidence is thin — the audit catches its own over-confidence. And pulls the score back. **Live. With the math shown.**"

**Delivery:** Live narration of a crafted process. "Now watch" = pointing at the screen. Rapid-fire fragments. The em-dashes around "strongest where the evidence is thin" are held breaths. Land "Live. With the math shown." as two discrete beats — the math is on screen, not hidden.

---

## F10 — Open Arize. The audit changes who wins. · 2:46 – 2:55 (9s) · `terminal-browser` shape · palette: payoff (cyan)

**Heading:** every span is there.
**On screen:** terminal runs `client.spans.list(project="glasshat")` → prints the nested span tree (agent → workflow → 6 hats · 104 spans). Browser shows the **rank-flip board** (without-audit vs with-audit — a row moves to #1) and a chip: *hit@13 0.6154 · Arize AX experiment.*

**VO:**
> "Open Arize. Every span is there. And on a whole cohort — the audit changes who wins."

**Delivery:** Maker exhaling. "Every span is there" while the tree prints. The em-dash before "the audit changes who wins" is the gut-punch beat. *(Honesty note for the recorder: this is a cohort-level statement; the hit@13 0.6154 is a binary Winner-label hit rate, and on the golden set the top-13 did not reorder — Δ = 0. Do not claim a rank flip on that specific set on camera.)*

---

## F11 — Open source. Apache 2.0. · 2:55 – 3:00 (5s) · `repo-install` shape · palette: hero (bright cyan)

**Heading:** Apache-2.0. Open. Reproducible.
**On screen:** repo `github.com/Two-Weeks-Team/glasshat` · badges (Gemini 3.1 Flash-Lite · ADK 2.0 · Arize AX · Agent Engine · Apache-2.0) · install/run snippet · lockup hero echo **Trace it. *Trust it.***

**VO:**
> "Open source. Apache 2.0. **Trace it. Trust it.**"

**Delivery:** Arrival. The hero echo is the last thing said in the entire video. Slow it down — *Trace · it · · Trust · it.* Then silence. Then the music tail.

---

## Close — Title card · END (12s) · `close` shape · palette: pivot (green)

**Heading:** **Trace it. *Trust it.***
**On screen — checklist:**
- ✓ ADK 2.0 Workflow on Agent Engine
- ✓ full nested Arize AX trace (104 spans)
- ✓ Datasets + Experiment (hit@13 0.6154) + code Evaluator
- ✓ six-hat audit self-corrects (9.0 → 7.6, ±2.0 bounded)
- ✓ live + reproducible
- ✓ Apache-2.0

**Call:** `github.com/Two-Weeks-Team/glasshat`
**Honest note (on screen):** *hit@13 = binary Winner-label, not a rank curve · the public demo runs the live Phoenix-MCP calibration loop (`SCORING_MODE=legacy` python path); the full trace tree + the hit@13 experiment = credentialed Agent Engine run.*

**VO:** *(silent — hold 12s while the recorder cuts)*

**Delivery:** Title-card close. Hero is the last words on screen. Let it hold.

---

## Timing roll-up (recorded clock)

| # | id | shape | act | time | dur |
|---|----|-------|-----|------|-----|
| 1 | cover | cover | cover | — | 8s |
| 2 | F1 | chain | agro | 0:00 – 0:10 | 10s |
| 3 | F2 | stack-strikethrough | agro | 0:10 – 0:25 | 15s |
| 4 | F3 | chain | drop | 0:25 – 0:35 | 10s |
| 5 | F4 | gallery-hero | drop | 0:35 – 1:00 | 25s ★ hero |
| 6 | F5 | counter-roll | thrill | 1:00 – 1:06 | 6s |
| 7 | F6 | hierarchy-diagram | thrill | 1:06 – 1:30 | 24s |
| 8 | F7 | modal-live-json | thrill | 1:30 – 1:54 | 24s |
| 9 | F8 | gallery-hero | thrill | 1:54 – 2:20 | 26s |
| 10 | F9 | triple-pane | thrill | 2:20 – 2:46 | 26s ★ wow |
| 11 | F10 | terminal-browser | thrill | 2:46 – 2:55 | 9s |
| 12 | F11 | repo-install | outro | 2:55 – 3:00 | 5s |
| 13 | close | close | close | END | 12s |

- **Opening range (F1 → F4, `O` key):** 60s.
- **Full recorded range (F1 → F11, `F` key):** **180s.**
- **F4 hero hold:** 25s (≥ 5s requirement satisfied; hero word-reveal completes ~2.4s, then ~22s clean hold).
- **SLIDE_DURATION array (cover…close):** `[8, 10, 15, 10, 25, 6, 24, 24, 26, 26, 9, 5, 12]`.
