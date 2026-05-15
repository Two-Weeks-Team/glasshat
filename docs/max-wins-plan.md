# Glasshat — Max-Wins Plan (Qdrant VSD + Rapid Agent / Arize track)

> **Status**: Strategic baseline locked 2026-05-14 by the user.
> Supersedes the implicit "build everything, submit twice" model in `PLAN.md`. `PLAN.md` remains the engineering inventory; this file is the **winning thesis** + **decision record**.
>
> **Product was named `Panelyst` (repo: `Two-Weeks-Team/panelyst`). User-approved rename to `Glasshat` on 2026-05-14 (panel recommendation §6).** All forward references use Glasshat. Repo/domain/.env migration is a downstream task tracked in §9.

---

## §0 — One paragraph

**Glasshat** ingests a PDF pitch deck + a GitHub repo URL, runs a six-perspective AI panel over both, scores against a fixed 100-point BMAD rubric with every sub-score grounded in vector-retrieved evidence and anchored to comparable past evaluations — and **on screen, in front of you, the panel catches itself being biased and self-corrects**. Built on Gemini 3 (Vertex) + Google Cloud Agent Builder + Arize Phoenix MCP (runtime self-introspection, not just trace emission) + Qdrant (six load-bearing collections) + Cloud Run + Firestore + Next.js (3D evaluation graph in react-three-fiber, 2D radar silent fallback). One codebase. Two hackathon submissions. Two demo narrations. **Qdrant VSD is primary** (binding deadline, visual remarkability is non-retrofittable). **Rapid Agent / Arize track is repackaging** (the planned architecture already does the harder thing — Phoenix MCP runtime consultation — that most submissions will skip).

---

## §1 — Dimension 1: Rules re-verification (live, 2026-05-14)

### 1.1 Qdrant VSD "Think Outside the Bot" 2026

| Item | Verified value | Source / change from 2026-05-13 capture |
|---|---|---|
| Deadline | **2026-06-01 23:59 PT** (= 2026-06-02 ~16:00 KST) | `try.qdrant.tech/hackathon-vsd` |
| Build period start | Not explicitly stated (page says "Now through June 1, 2026"). Glasshat first commit 2026-05-13 is comfortably in-period. | unchanged |
| **Submission channel** | `https://forms.gle/YDQ2TDUi8MqS9Vx28` **(URL changed)** — replaces the earlier `forms.hl.qdrant.tech` reference. Terms still cite `try.qdrant.tech/hackathon-vsd` (the landing page). | **changed** — note for submission day |
| Judging criteria | **Functionality · Originality · User Experience** (formal list) | unchanged |
| Prizes | 1st **$5,000** · 2nd **$3,000** · 3rd **$2,000** + "several Best-in-Category prizes from our sponsors" (**2026 sponsor list NOT yet published**; 2025 had Crew, Twelve Labs, Neo4j, Mistral, Cognee, Superlinked, Linkup). Monitor for 2026 sponsor announcement; re-check weekly. | partial — 2026 sponsors TBD |
| Submission requirements | (a) Public OR private GitHub repo, (b) README.md (project description + install/run instructions + 3rd-party deps), (c) demo video ≤3 min on Loom/YouTube/Dropbox/similar, (d) basic code comments | unchanged |
| Hard rule — no chatbots | "Submissions that are only chatbots are not allowed. The focus is on creativity and new interactions with vector search systems that go beyond simple Q&A chatbots." | unchanged |
| Hard rule — no previous projects | "All code must be created during the hackathon period (no previous projects allowed!)" | unchanged — Glasshat first commit 2026-05-13 ✓ |
| **New rule** — no sharing | **"Sharing work with other teams is not allowed."** | **new from prior capture** |
| Eligibility | 18+, global (subject to local laws); Qdrant employees/directors/officers + immediate family/household excluded; **teams 1–4** | unchanged |
| Qdrant DB required | "Qdrant Vector Database is required for submissions" — material part | unchanged |

**Compliance status for Glasshat**: ✓ first commit in-period · ✓ non-chatbot by construction · ✓ Qdrant load-bearing (6 collections) · ✓ team will be ≤4 · ✓ no work-sharing with other teams.

### 1.2 Rapid Agent Hackathon (Arize track) — **official rules now posted at `/rules`**

| Item | Verified value | Source / change |
|---|---|---|
| Contest period | **2026-05-05 12:00 PT → 2026-06-11 14:00 PT** (= 2026-06-12 ~06:00 KST). Glasshat first commit 2026-05-13 is in-period ✓ | `rapid-agent.devpost.com/rules` |
| Judging period | 2026-06-22 → 2026-07-06 | unchanged |
| Mission (verbatim) | "Building Agents for Real-World Challenges is your opportunity to **move beyond the chatbot** and into the world of agents that accomplish tasks for you." Stack: **Gemini 3 + Google Cloud Agent Builder + Partner Entity MCP server**. | confirmed Gemini **3** specifically |
| Judging — Stage 1 (pass/fail) | Must include all submission requirements + "reasonably addresses the challenge and reasonably applies both the required data provided by Partner and Google Cloud products." Real partner-MCP-data integration is gated. | new specificity |
| Judging — Stage 2 (4 equal-weight axes) | (1) **Technological Implementation** — quality of GCP + partner interaction, (2) **Design** — UX thought-through, (3) **Potential Impact** — target community impact, (4) **Quality of the Idea** — creative/unique. | unchanged |
| **Tie-breaker order** | **In the order listed → Tech Implementation breaks first**, then Design, then Impact, then Idea. Final tie → judge vote. | **explicit — key strategic input** |
| Prize structure | 6 tracks (Arize, Elastic, Dynatrace, Fivetran, GitLab, MongoDB): 1st **$5K** + social-media-promo opportunity · 2nd **$3K** · 3rd **$2K**. **One prize max per submission.** $60K total. | unchanged |
| Eligibility (geo) | Excluded: Afghanistan, Antarctica, China, Djibouti, Iraq, Somalia, Venezuela, W. Sahara, Italy, Brazil, Quebec, Cuba, Iran, Syria, N. Korea, Sudan, Belarus, Russia, Vietnam, Crimea, Donetsk, Luhansk. **South Korea: OK ✓.** Plus OFAC SDN / US Denied Persons exclusions. | confirmed |
| Eligibility (age/employment) | Legal age of majority (20+ in Taiwan). Google + Partner Entity employees/contractors/officers + immediate family/household ineligible. Government-employee conflict-of-interest excluded. | confirmed |
| Team rules | Max **4 individuals**; one Representative authorized. Individuals may submit multiple **substantially different** submissions; multiple teams permitted with unique submissions. | confirmed |
| **"All code in period" rule** | **"Projects must be newly created by the entrant during the Contest Period. The Project must be Your original creation not a modification or extension of Your or anyone else's existing work."** Same posture as Qdrant. fairthon concept lineage stays as documented in README; no code reuse. | **confirmed — explicit** |
| **Competitive restriction** | **"The use of other services that directly compete with Google Cloud (for cloud platform capabilities) or with the Partner whose track you've selected is not permitted."** Arize ≠ Qdrant (observability vs vector DB are different categories) — Glasshat must explicitly frame this in README. | **new — risk item §10.1** |
| Repo requirements | Public + OSI-approved license **detectable in the About sidebar**. License must permit commercial use. **Apache-2.0 already at panelyst repo root and About sidebar ✓.** | unchanged |
| Hosted URL | Required, judged. Platform = web / Android / iOS. No explicit no-login or uptime clause, but pass/fail Stage 1 implies judges must be able to run it. | confirmed |
| Demo video | **≤3 min** (over → only first 3 min judged) · **YouTube or Vimeo only** (NOT Loom / Dropbox / etc., unlike Qdrant) · English or English subtitles · written entry portions in English · footage of project functioning on submitted platform · no third-party ads/logos/trademarks · perpetual royalty-free license to Google/Partners/affiliates for use of video. | **confirmed — YouTube/Vimeo is a tighter constraint than Qdrant** |
| Arize track specifics (devpost/details/arize-resources) | Required: (a) OpenInference instrumentation, (b) traces sent to Phoenix, (c) Phoenix MCP server configured for **runtime introspection** (not just emission), (d) **LLM-as-judge evals on traces** (or code evals). Bonus: **"agents that use their own observability data to improve over time"** → self-improvement loop. Runtime: **Cloud Run / Google ADK / Gemini CLI / Agent Runtime / Gemini Enterprise SDK** (Visual Agent Builder alone insufficient — code ownership mandatory). Starter kit: `github.com/Arize-ai/gemini-hackathon`. Phoenix Cloud free tier: `app.phoenix.arize.com`. | **new specificity — Phoenix MCP runtime consultation is the moat** |

**Compliance status for Glasshat**: ✓ all-code-in-period (first commit 2026-05-13) · ✓ team ≤4 · ✓ Apache-2.0 in About ✓ · ✓ Cloud Run runtime · ✓ Korea eligible · ✓ Gemini 3 verified (`docs/gcp-setup.md`) · ⚠ must use YouTube/Vimeo specifically for Rapid Agent demo (Qdrant accepts more channels) · ⚠ must explicitly frame Qdrant ≠ Arize in README (competitive-restriction defense).

---

## §2 — Dimension 2: Judging criteria × feature scoring matrix

### 2.1 Qdrant VSD (3 axes, equal weight)

| Glasshat feature | Functionality | Originality | UX | Material vector use? | Net contribution |
|---|---|---|---|---|---|
| Six-Hat panel evaluation | High — full pipeline runs | Medium — Six Hats is 1985 framework, known | Low if hidden, Medium if foregrounded as conflict | Medium — Hats query Qdrant collections | Foundational; high if framed as conflict, mid if presented as feature list |
| **Audit-the-auditor moment** (Black flags Yellow, Phoenix detects drift, score self-corrects with retrieved evidence highlighted) | **Very high** — proves end-to-end works | **Very high** — no other 2025 entry did meta-audit | **Very high** — theatrical, comprehensible | **Very high** — vectors are the protagonist (past_evals + evidence retrieval) | **★ Wins on all 3 axes simultaneously. Build to ship-quality.** |
| 3D evaluation graph (R3F) | Medium — visual surface only | **Very high** — pattern-matches 2025 winners (Vector Vintage, CosmicTwin, Quant Memory Palace all R3F) | **Very high** — rotating reveals cluster info 2D cannot | **High** — spatial layout from past_evals embeddings | **★ Wins on Originality + UX. Material vector use proof.** |
| BMAD 17-item rubric | High — proves rigor | Low — rubric is generic | Low if all 17 are paraded; medium if 3-5 foregrounded | Low — rubric is config, not vector | Functional credibility; never the headline |
| `past_evals` Qdrant collection with 50-150 seeded projects + "ranks similar to X" anchor comparison | High — anchor comparison is real | Medium — vector retrieval of comparables is a known pattern, but rarely shown in agent demos | High — closes the demo memorably | **Very high — direct vector-search demonstration** | **★ Material vector use; serves the demo close.** |
| `pitch_chunks` + `repo_chunks` evidence grounding | High — each sub-score has receipts | Medium | High — drill-down to passage is satisfying | **Very high** | **★ Vector search as protagonist of sub-score justification** |
| Live monitoring dashboard (Phoenix gauges + Arize meta-eval) | High | High if shown as the *audit happening*; Medium if shown as graphs | High if integrated into wow moment; Medium if a separate tab | Medium — Phoenix traces, not Qdrant per se | **★ Becomes the wow when fused with audit-the-auditor; standalone it's a dashboard** |
| Vector-search browse page (find-similar-past-projects) | Medium | Medium | Medium — but **competes with wow for demo attention** | High | Build for compliance ("non-chatbot UX exists") + Arize submission; **cut from Qdrant demo** |
| Signed-report cryptographic audit trail | Medium — "defensible evaluation" thesis support | Low | Low — signatures are invisible in a demo | None | Build minimally, mention 5 sec, never demo |
| Korean i18n + SSE Korean | Low — adds engineering risk | Zero | Zero for English judges | None | **Cut from v1 entirely** |
| Code Grader static heuristics (15-20 checks) | High — completes the pipeline | Low | Low — invisible | Medium — fact rows + sampled-code chunks | Functional necessity; not demoable |
| Web-search RAG (Vertex Grounding) | Medium | Low | Low — invisible | Low — `web_evidence` collection | Functional; not demoable |

**Strategic conclusion (Qdrant)**: The audit-the-auditor moment + 3D graph + anchor comparison together pull all three judging axes. Six Hats is the *mechanism* (kept), but the *foreground* of the demo is the audit moment, not the hat enumeration. Vector search must be visibly material — past_evals retrieval at the audit moment + spatial 3D layout from embeddings are the proofs.

### 2.2 Rapid Agent / Arize track (4 axes, equal weight, **tie-break in order**)

| Glasshat feature | Tech Implementation | Design | Potential Impact | Quality of Idea | Arize-specific bonus (self-improvement loop) |
|---|---|---|---|---|---|
| **Phoenix MCP runtime consultation** (Blue planner queries Phoenix mid-run, changes retrieval strategy, score-before/score-after delta shown) | **Very high — this is the tie-breaker winner** | High — visible decision moment | High — defensible AI evaluation has broad applicability | **Very high** — most submissions will instrument traces but not consult them | **★ This IS the self-improvement loop. Direct bonus-point earner.** |
| Gemini 3 + Agent Builder orchestration (Blue planner registers 6 hat sub-agents as Agent Builder agents) | **Very high** — full required stack | Medium | Medium | High | Foundational |
| OpenInference instrumentation (every hat/tool/retrieval/score span) | **Very high** — required for pass/fail Stage 1 | Low — invisible | Medium | Medium | Required minimum |
| LLM-as-judge evals on traces (Phoenix evals for groundedness, inter-Hat consistency, hallucination flags) | **Very high** | Medium | Medium | High | **★ Direct judging dimension** |
| Audit-the-auditor moment (same engine, Phoenix-framed narration) | High | **Very high — Design axis** | **Very high — Potential Impact axis: "this could underwrite every accelerator / grant body's evaluation"** | **Very high** | Reinforces the loop visually |
| 3D evaluation graph | Medium — engineering depth proves design polish | **Very high — Design axis** | Medium | High — uncommon in agent demos | Tangential |
| 6 Hats as Agent Builder sub-agents (separate registration + tool budgets) | **Very high — proves multi-agent orchestration** | Medium | High | Medium | Medium |
| Cloud Run hosting + Firestore audit trail | High — runtime requirement met | Low | Medium | Low | Required |
| Two human gates (plan approval + score override) | Medium — proves "keep user in control" | High — explicit consent moments | Medium | Medium | Reinforces "agents that work *with* you" mission framing |
| Korean i18n | Low | Low | Low — English-speaking judges | Low | None |
| Code Grader Cloud Run Job | High — proves multi-component orchestration | Low | Medium | Medium | Low |
| Vector-search browse page | Medium | Medium | Medium | Medium | Low (Phoenix has its own UI) |
| Signed-report audit trail | Medium — "defensibility" is part of Idea Quality | Low | High — defensibility is the impact thesis | Medium | Low |

**Strategic conclusion (Arize)**: Tie-break order makes **Tech Implementation the highest-leverage axis**. The Phoenix MCP runtime consultation moment is the single feature that maxes this axis *and* earns the Arize-specific bonus. Design axis is satisfied by the 3D graph + the human gates. Impact axis is satisfied by the "underwrite every accelerator's evaluation" framing. Idea Quality is satisfied by the meta-evaluation novelty.

### 2.3 Cross-hackathon coverage (one feature, two payoffs)

| Feature | Qdrant payoff | Arize payoff | Build once, demo twice? |
|---|---|---|---|
| Audit-the-auditor moment | Wow / Originality + UX | Tech Impl + Design + Idea + bonus | **✓ Same code, different narration** |
| Phoenix MCP runtime consultation | Helps audit moment land (provides the drift data) | The literal moat | **✓** |
| 3D graph | Wins on Originality + UX | Design axis support | **✓** |
| Qdrant 6 collections + past_evals | Material vector use proof | Provides corpus for self-improvement loop | **✓** |
| Six Hats as separate agents | Mechanism foreground | Multi-agent orchestration proof | **✓ (compress to 2-3 visible in Qdrant demo; show all 6 in Arize demo)** |
| Anchor comparison ("ranks similar to X") | Memorable close | Demonstrates retrieval-grounded reasoning | **✓** |

**80%+ overlap** in build effort. The 20% delta is *narration*, *which surfaces to foreground*, and the *Phoenix UI side-by-side* in the Arize demo. This validates the "one engine, two demos" thesis.

---

## §3 — Dimension 3: Past-winner pattern reverse engineering

### 3.1 Qdrant 2025 "Thinking Outside the Bot" — actual winner taxonomy

| Place | Project | Builder | What it does (one sentence) | Stack | Pattern flag |
|---|---|---|---|---|---|
| 🥇 1st ($5K + $1K Neo4j) | **Vector Vintage** | Benedict Counsell | 3D explorable terrain for vintage e-commerce; mountains = categories, hills = subcategories, height = result count; LLM "Q-Bert" guides curated tours | Mistral embeddings + Qdrant similarity + Neo4j graph curation + UMAP + **React Three Fiber** | **Visual immersion + 3D + LLM tour guide + non-obvious vector use** |
| 🥈 2nd ($3K) | **RoboBank** | Sanya Kapoor | Robot trajectory memory: banks sensor-action vector sequences, labels by safety, retrieves safest neighbor for next-move fallback | Qdrant (trajectory memory, safe/unsafe labels), 2D simulator | **Sharp single domain + safety-critical + visible UI** |
| 🥉 3rd ($2K) | **Spatio-Temporal NPCs** | cortexandcode | Video-game NPCs with persistent memory via embeddings (locations, events, interactions) — organic personality | GPT-OSS-120B + Qdrant + CLIP + Whisper + PiperTTS + MiniLM | **Entertainment + multimodal + memorable framing** |
| CrewAI prize | ReMap | TatankAm Explorers | Route-aware event discovery: route+time → semantic + geospatial search on map | Qdrant + CrewAI + OpenStreetMap | Map-based discovery |
| Mistral prize ($3K) | **CosmicTwin** | Inferno | Personality quiz → "home planet" → cosmic twinmates via vector similarity, per-planet chat | Qdrant + Mistral + **React Three Fiber** | **Playful + 3D + social hook** |
| Superlinked prize ($1K) | Bachata Vibes | Erick Rea | AI choreographer matching music features → labeled dance clip vectors | Superlinked + Qdrant Cloud | Sharp domain (dance), unusual modality |
| TwelveLabs prize ($1K) | Qlassroom | YHHA | Multimodal classroom assistant indexing speech/video/slides/images | TwelveLabs + Qdrant | Multimodal |
| Honorable | Quant Memory Palace | The Mondays | 3D knowledge cluster navigation + real-time search preview | Qdrant + R3F implied | **3D + memory metaphor** |
| Honorable | OmniVault | Lone Qdrantic Agent | Privacy-first local index of files + browsing + multimodal search | Qdrant + Redis + CLIP + Ollama + Chrome ext | Local-first |
| Honorable | Drawland | Drawland | Kid-friendly drawing/storytelling with vector retrieval | Qdrant | Sharp audience |

### 3.2 Extracted patterns (what reliably wins Qdrant)

1. **Visual / immersive surface** (8 of 10 above have a memorable visual; 3D + R3F appears in 1st, Mistral-prize, and an honorable mention — that's not coincidence)
2. **Non-obvious vector use** — none of the winners are "search docs." They're: navigate a *terrain*, remember robot *trajectories*, match music to *dance moves*, find *cosmic twins*, give NPCs *persistent memory*. Vector is the verb, not the noun.
3. **Memorable proper-noun naming** — every winner has a complete pitch in the name: *Vector Vintage* (place + era), *RoboBank* (collision noun), *CosmicTwin* (mystery+scale), *Drawland* (domain). "Panelyst" was a category. **"Glasshat" fits the pattern** (collision noun, suggests both mechanism and virtue).
4. **Single sharp use case** — every winner does *one thing* surprisingly well. No "platform for everything."
5. **Demo-able in 1-2 minutes** — 2025 required ≤1 min videos. 2026 allows ≤3 min, which means *don't fill it* — use the space for one wow moment with breathing room.
6. **Partner tech stacked** — Vector Vintage uses 4 stacks (Mistral + Qdrant + Neo4j + R3F). Best-in-Category prizes reward partner-stack usage. **Implication for Glasshat**: if 2026 best-in-category sponsors include any AI eval / observability / R3F / 3D-related sponsor, Glasshat earns an extra angle.

### 3.3 Glasshat's pattern fit (after rename + audit-moment + 3D commit)

| Pattern | Glasshat fit | Action |
|---|---|---|
| Visual/immersive | ✓ if 3D graph + audit-the-auditor visual lands | Lock 3D graph as must-build; visual style spec for audit moment |
| Non-obvious vector use | ✓ — "vectors anchor scores to past evaluations and contradict claims on demand" is non-obvious | Foreground this in demo + README |
| Memorable name | ✓ Glasshat | Migration §9 |
| Single sharp use case | ✓ — "evaluate a deck + repo, audit-the-auditor visible" | Trim feature list to support this (§5 cut list) |
| Demo-able with breathing room | ✓ — script in §5 leaves silence around the wow | Lock script + rehearse |
| Partner tech stacked | Depends on 2026 sponsor list. Current stack: Mistral-equivalents are Gemini, Neo4j-equivalent is Qdrant graph metadata, R3F ✓, observability via Arize Phoenix | Re-check Qdrant sponsor list weekly |

### 3.4 The Gemini 3 Hackathon as Glasshat's calibration corpus (added 2026-05-14)

Independent of the 2025 Qdrant winner pattern, a richer dataset for Glasshat's `past_evals` collection + Phoenix calibration experiment is the **concluded Gemini 3 Hackathon** (`gemini3.devpost.com`, Dec 2025 – Feb 2026, $100K prize pool, 4,499 submissions, 35,580 participants).

**Why this corpus is uniquely strong**:
- Every submission used **Gemini 3 API** — matches Glasshat's own stack (in-distribution comparison)
- Required public assets: Devpost page (~200-word description) + **public GitHub repo** (or AI Studio link) + ~3-min demo video — exact format Glasshat ingests
- **Disclosed judging weights**: Technical Execution 40% · Innovation/Wow 30% · Potential Impact 20% · Presentation 10% — maps approximately to BMAD (A 25 + B 25 ≈ Innovation+Impact 50%; C 30 ≈ Tech 40%; D 20 ≈ Presentation 10%) → provides cross-validation ground truth
- 24+ judged winners + ~4,475 non-winners → labels for calibration

**User-approved sampling 2026-05-14**: **All 24+ winners + 500 stratified random non-winners = 524 projects**. Phoenix calibration experiment derived from this corpus (see `docs/wow-moment-design.md` §6 for the full pipeline + cost ~$20-50 within $500 GCP credit).

**Demo-narrative usage** (user-approved 2026-05-14):
- **Qdrant demo**: 1-line caption at 2:30-2:50 — *"Glasshat evaluated 524 of the Gemini 3 Hackathon's 4,499 submissions — including all 24+ winners — to calibrate its own bias before scoring yours."* This converts the meta-evaluation thesis from an abstract claim into a concrete number with provenance.
- **Arize demo**: NOT mentioned as a meta-narrative. The same corpus surfaces only as the Phoenix experiment dataset that drives the runtime consultation. Keeps Arize demo focused on technical implementation rather than meta-storytelling.

**Compliance**: Both hackathon rules' "newly created… not a modification or extension of existing work" clauses are satisfied — consuming public data as evaluation calibration corpus is not code reuse. README discloses corpus origin and use-as-calibration-only stance.

### 3.5 Rapid Agent / Arize-track patterns (limited data — Rapid Agent is new in 2026)

- Closest analog: 2025 **ADK Hackathon** (10,400 participants, 477 projects, 1,500 agents). Headline winners: **SalesShortcut** (multi-agent SDR system) and **TradeSage AI** (multi-agent hypothesis evaluation). Pattern: **multi-agent + real-world job + complete pipeline**.
- Implication: judges reward **complete agent pipelines that accomplish a task**, not chatbots-with-tools. Glasshat fits: ingest → plan → 6 hats execute → score → audit → report. Visible orchestration matters.
- Arize-specific: starter kit `github.com/Arize-ai/gemini-hackathon` is the reference. Examine it for instrumentation patterns + "self-improvement" demo idioms during Phase 1.

---

## §4 — Dimension 4: Wow factor

### 4.1 The single dinner-table-retellable moment (both demos)

> **"I watched an AI panel catch itself being biased, look up its own past mistakes, and fix the score in front of me — in 3D."**

This is the sentence a judge can retell at dinner 24 hours after the demo. Every other decision in this plan defends this sentence.

### 4.2 Qdrant version (visual + theatrical emphasis)

**The moment, sec-by-sec build:**
1. Black hat issues a verdict: "claim X in the pitch is unsupported"
2. Yellow hat issues a verdict: "this is excellent — strong market"
3. Blue planner detects a **score inconsistency**: Yellow rated A1 too high relative to evidence depth
4. Blue queries Phoenix MCP for past similar runs → sees Yellow has historically been over-optimistic on A1 by ~1.2 pts when evidence-depth was low
5. Blue queries Qdrant `past_evals` collection → retrieves 3 past projects with similar evidence-depth scores → those past projects scored A1 lower
6. The Yellow A1 score **visibly self-corrects on screen** (animated decrement), the contradicting past-eval chunks highlighted in side panel
7. The 3D evaluation graph **reshapes in real-time** to reflect the corrected score; the node moves toward the corrected cluster

**Why it wins Qdrant**:
- **Functionality**: full pipeline ran end-to-end, returned a defensible score
- **Originality**: no 2025 entry did meta-audit; this is a fresh use of vectors (past_evals as the bias-correction signal)
- **UX**: theatrical, comprehensible, one moment with breathing room — judge tells the story in 1 sentence
- **Material vector use**: Qdrant `past_evals` retrieval is the protagonist of the correction

### 4.3 Arize version (technical + Phoenix-foregrounded emphasis)

**The same engineering, different framing:**
1. Blue planner starts evaluating
2. Mid-run, Blue **pauses** with a visible message: *"Consulting Phoenix for past performance on rubric item A1"*
3. Phoenix MCP returns: *"You've been over-confident on A1 by 1.2 pts when evidence-depth < threshold; in this run evidence-depth = X"*
4. Blue changes its retrieval strategy: switches Qdrant collection from `pitch_chunks` (shallow) to `repo_chunks` + raises top-k from 5 → 12
5. Phoenix UI shown side-by-side: trace tree grows, span for "Phoenix consultation" highlighted, downstream spans show the new retrieval
6. Final score appears with **delta**: "Without Phoenix consultation: 78/100. With consultation: 71/100. The agent corrected itself."

**Why it wins Arize**:
- **Tech Implementation (tie-break #1)**: real Phoenix MCP runtime consultation, not just trace emission — meets the "code-owned runtime introspecting at runtime" bar that most submissions will not clear
- **Design**: the pause + side-by-side Phoenix UI is a deliberate Design choice — the agent shows its meta-reasoning
- **Potential Impact**: every grant body / accelerator / hackathon judge / investor running evaluations at scale can use this
- **Quality of Idea**: meta-evaluation that improves itself is a fresh agent pattern
- **Arize self-improvement bonus**: the score-before vs score-after delta IS the loop made visible

### 4.4 Why one moment, not many

Doumont: "A 3-minute demo cannot show seven surfaces. It can show two, maybe three. Pick now."

Pick: (1) audit moment (~45s), (2) 3D graph rotation (~30s for Qdrant; Phoenix UI for Arize), (3) anchor comparison close (~15s). The rest is setup + transitions.

---

## §5 — Dimension 5: 3-minute demo scripts (sec-by-sec)

### 5.1 Qdrant version — densified with WOW/KICK at every slot (rev 2026-05-14 post-Apex-Pass)

> Every slot below explicitly names ≥1 **WOW** (memorable beat) or **KICK** (technical-depth moment). Single-failure points have **BACKUP** beats. Visuals are **layered** (multiple things on screen simultaneously, Vector-Vintage style).

```
0:00–0:10  HOOK [★ WOW #0 — emotional setup]
           Black screen, white text fade in: "Who audits the AI evaluator?"
           Hold 3 sec. Brief synth chord, fades.
           LAYER: tiny "Glasshat" wordmark appears bottom-right at 0:08.

0:10–0:30  ARTIFACT IN MOTION + COST DASHBOARD [★ KICK #1 — production polish]
           Drop deck.pdf onto dropzone (top-left). Paste GitHub URL (centre).
           Click Run.
           LAYER 1: Cost tracker badge appears top-right ticking up
                    ($0.000 / 0 tokens → $0.012 / 8K tokens by 0:30)
           LAYER 2: Vector indexing animations in BOTH pitch_chunks AND
                    repo_chunks — DENSE indicator + SPARSE indicator both
                    ticking (Qdrant hybrid retrieval visible, RRF fusion)
           LAYER 3: Blue planner box opens centre with "thinking..."
                    indicator (Gemini 3 thinking_level=high)
           No narration; screen tells story.

0:30–1:00  PANEL + BLUE PLANNER REASONING [★ KICK #2 — thinking tokens visible]
           LAYER 1: Blue planner's thinking trace streams into a "show
                    reasoning" panel (Gemini 3 thinking tokens, surface
                    3-line live summary)
           LAYER 2: 6 hat cards begin scoring in PARALLEL (ADK ParallelAgent
                    visible). Each card shows: live token count, retrieved
                    chunks count, score accumulating.
           LAYER 3: WHITE hat retrieves 2 URLs via Vertex Grounding; URLs
                    appear in side panel with favicon + title + timestamp
                    (citation snapshot)
           LAYER 4: YELLOW says A1=9.0 with 1 evidence_ref (visible:
                    low evidence_depth = 0.31)
           Cost badge: "$0.024 / 15K tokens"

1:00–1:30  ★★ WOW #1 PART A — PHOENIX ONLINE EVAL FIRES (audit detection)
           Yellow's score span emits → Phoenix Online Eval Task auto-fires.
           VISIBLE: Yellow card shimmers; annotation badge appears:
                    "Phoenix eval: over_confident (calibration_score: 0.31)"
           BACKUP BEAT: in parallel, Black hat (running concurrently) issues
                    counter-claim: "Evidence depth 0.31 does not support
                    score 9.0." Two flags appear simultaneously — Phoenix
                    annotation + Black hat critique. Even if one channel
                    looks subtle on the judge's screen, the other narrates.
           No score change yet — this is the DETECTION beat.

1:30–1:45  ★★ WOW #1 PART B — PHOENIX MCP CONSULTATION + RECOMMENDATION API
           Blue planner pauses, spinner with "consulting Phoenix MCP..."
           SPLIT INSET (briefly): Phoenix Cloud UI shows MCP trace tree
                    growing with `get-experiment-by-id` call landing.
           Phoenix returns: "Yellow over-confident on A1 by avg 1.2 pts
                    when evidence_depth < 0.4 (n=14 past runs, CI ±0.3)"
           Qdrant Recommendation API call visible in retrieval panel:
                    recommend(positive=[over_confident_yellow_anchors],
                              negative=[accurate_yellow_anchors],
                              strategy="average_vector")
           → returns 3 anchor projects with correctly-scored A1
                    (visible: project IDs + their A1 = 7.2 / 7.5 / 7.8)
           Yellow A1 score animates 9.0 → 7.6 with smooth transition.
           Contradicting evidence chunks highlight on right panel
                    (vector-retrieved from pitch + repo).
           Cost badge: "$0.032 / 21K tokens · 6.8K cached (90% saved)"

1:45–2:30  ★ WOW #2 — 3D EVALUATION GRAPH WITH ANCHOR CONSTELLATION
           Camera pulls back from score cards into 3D scene (r3f).
           LAYER 1: 17 BMAD criteria as spatial nodes; edges = evidence
                    retrievals; node size = score weight; color = confidence.
           LAYER 2: 524 anchor projects appear as small dots in the space,
                    clustered by outcome_tier:
                      • gold cluster  = 24+ winners
                      • silver cluster = honorable mentions
                      • grey cloud    = non-winner baseline
           LAYER 3: User rotates the graph slowly. Two clusters revealed
                    only from this angle:
                      (1) B-axis (Tech) — dense edge fan-in (strong)
                      (2) A-axis (Problem) — weakened post-audit (sparse)
           LAYER 4: The corrected Yellow A1 node visibly migrates toward
                    the winner-anchor cluster as the rotation continues.
           [BACKUP if 3D fails on demo machine: 2D radar with corrected
            score animated — same narrative beat, less spectacular]

2:30–2:50  ANCHOR COMPARISON + META-CORPUS CLOSE [★ KICK #3 — provenance]
           Right panel: group_by query results in one call:
                    "Ranks similar to [Project X] (winner, 82/100)
                     Weaker than [Project Y] (winner, 88/100) on evidence depth
                     Stronger than [Project Z] (non-winner, 64/100)"
           1-line caption (THE META-NARRATIVE):
                    "Glasshat evaluated 524 of the Gemini 3 Hackathon's
                     4,499 submissions — including all 24+ winners — to
                     calibrate its own bias before scoring yours."
           1-sec mention: "Every score has a receipt — signed audit trail."
           Cost badge final: "$0.041 / 26K tokens · 7.1K cached"

2:50–3:00  TAGLINE
           Logo + tagline: "Glasshat. The panel that audits itself."
           Small text: "Apache-2.0 · Public repo · One agent. Six perspectives.
                        Live audit. github.com/Two-Weeks-Team/glasshat"
```

**Wow/Kick distribution audit** (post-rev):
| Slot | WOW | KICK | Backup if fails |
|---|---|---|---|
| 0:00-0:10 | ★ #0 hook | — | (low risk) |
| 0:10-0:30 | — | ★ #1 cost+hybrid | (recoverable; not load-bearing) |
| 0:30-1:00 | — | ★ #2 thinking tokens + parallel hats + citation | (multiple layers; resilient) |
| 1:00-1:30 | ★★ #1A detection | — | ★ Backup beat: Black hat critique parallel |
| 1:30-1:45 | ★★ #1B correction | — | (depends on MCP + Qdrant; high stakes) |
| 1:45-2:30 | ★ #2 3D | — | ★ Backup: 2D radar fallback |
| 2:30-2:50 | — | ★ #3 anchor + meta-corpus | (low risk) |
| 2:50-3:00 | (close) | — | (low risk) |

7 wow/kick beats, ≤45-second longest gap between beats, every high-risk beat has a backup.

**Production notes**:
- No live mic-narration; on-screen captions + ambient sound bed only.
- All on-screen text English. UTF-8 fonts that render numerals + special chars cleanly.
- Cost dashboard ticks throughout — establishes production-discipline tone.
- Rehearse to 3:00 ±5 sec. Cut order (if long): 2:30-2:50 first (compress anchor close to 15 sec), then 1:45-2:30 (compress 3D rotation by 10 sec), never cut 1:00-1:45 (the wow).

### 5.2 Arize / Rapid Agent version — densified with WOW/KICK at every slot (rev 2026-05-14 post-Apex-Pass)

> Same engine as Qdrant version. Foreground: Phoenix-side technical depth (Tech Implementation = tie-break #1). NO meta-corpus narrative (user decision).

```
0:00–0:15  HOOK [★ WOW #0]
           Black screen, white text: "Most agents claim self-improvement."
           3-sec pause.
           "Watch ours mid-correction."
           LAYER: tiny stack badges row at bottom, fading in:
                  Gemini 3 · Agent Builder · Google ADK · Phoenix MCP ·
                  Qdrant · Cloud Run · Apache-2.0

0:15–0:45  STACK + INGESTION + PHOENIX UI LIVE [★ KICK #1 — full stack visible]
           Drop deck + paste GitHub URL. Click Run.
           LAYER 1: Cost dashboard top-right tick (Token cost + cached %)
           LAYER 2: Phoenix Cloud trace tree streaming live in split inset
                    (LEFT half: Glasshat orchestrator; RIGHT half: Phoenix UI)
           LAYER 3: 6 hat sub-agents spawn via ADK ParallelAgent
                    (6 cards visible with per-card metadata):
                      • Blue:   Gemini 3.1 Pro · thinking_level=high
                      • White:  Gemini 3 Flash · thinking_level=medium
                      • Red:    Gemini 3 Flash · thinking_level=medium
                      • Yellow: Gemini 3 Flash · thinking_level=medium
                      • Black:  Gemini 3.1 Pro · thinking_level=high
                                  (heavy hat — must cite precedent)
                      • Green:  Gemini 3 Flash-Lite · thinking_level=minimal

0:45–1:00  BLUE PLANNER REASONING + RECOMMENDATION API ARM [★ KICK #2]
           Blue planner thinking trace expands into a sidebar panel
                    (Gemini 3.1 Pro thinking tokens streaming)
           Blue's plan object renders as structured JSON
                    (responseSchema enforced):
                    {hats_running: 6, criteria_addressed: 17,
                     retrieval_budget: {pitch_chunks: 5, repo_chunks: 5,
                                        past_evals: 3},
                     thinking_level: dynamic}
           In Phoenix UI: spans for the plan call appear with FULL
                    OpenInference attributes visible (llm.input.messages,
                    llm.output.token_count, llm.invocation_parameters)
           Hats start running parallel.

1:00–1:30  ★★ WOW #1 PART A — PHOENIX ONLINE EVAL FIRES (Phoenix-native detection)
           Yellow hat emits score 9.0 for A1 with evidence_depth 0.31.
           Phoenix Online Eval Task auto-fires (sampling 100%, scope=span,
                    filter=glasshat.hat==yellow AND glasshat.criterion==A1).
           VISIBLE in Phoenix UI: span gets "evaluating..." badge, then
                    after ~800ms returns:
                    eval.calibration.label = "over_confident"
                    eval.calibration.score = 0.31
                    eval.calibration.explanation = "evidence_depth 0.31
                              inconsistent with score 9.0 (threshold 0.6)"
           AuditLoop's InconsistencyDetector queries
                    get-span-annotations(yellow_a1_span) via Phoenix MCP
                    → receives the annotation → triggers consultation.
           BACKUP BEAT: in parallel, Phoenix Custom Evaluator running as
                    a separate Task catches the same pattern using a
                    Python rule (statistical, not LLM). Two independent
                    detection paths.

1:30–2:00  ★★ WOW #1 PART B — PHOENIX MCP CONSULTATION + STRATEGY CHANGE
           Blue planner pauses with visible "consulting Phoenix MCP" message.
           In Phoenix trace tree (still live, RIGHT panel): MCP call chain
                    appears as 3 sibling spans:
                    > get-experiment-by-id(glasshat-calibration-v1)
                      → mean_delta: -1.2pts, n=14, CI ±0.3
                    > get-span-annotations(yellow_a1_span)
                      → label: over_confident, score: 0.31
                    > get-dataset-examples(calibration_corpus_v1, limit=3,
                                           filter: hat=yellow AND
                                                   evidence_depth_bucket=low)
                      → 3 anchor projects
           Blue's strategy change visible (animated text):
                    "Adjustment:
                      pitch_chunks → repo_chunks (deeper)
                      top_k:        5 → 12
                      thinking_level: medium → high"
           Qdrant Recommendation API also fires:
                    recommend(positive=[over_confident_yellow_anchors],
                              negative=[accurate_yellow_anchors],
                              strategy="average_vector")
           Yellow A1 score animates with explicit delta caption:
                    "Pre-Phoenix:  9.0
                     Post-Phoenix: 7.6
                     Δ = -1.4 (calibration applied)"

2:00–2:30  SELF-IMPROVEMENT LOOP COMPLETES + ANNOTATIONS WRITE [★ KICK #3]
           Evaluation continues with adjusted strategy.
           Phoenix groundedness eval re-runs on the corrected Yellow span:
                    eval.groundedness.label = "grounded" (now passes)
           Inter-hat consistency gauge in Phoenix dashboard updates green.
           ADK LoopAgent next iteration: InconsistencyDetector confirms
                    consistency, signals exit_loop via
                    tool_context.actions.escalate = True.
           Human-override gate UI offers user the chance to override
                    auto-correction — user accepts. Phoenix Annotation
                    written:
                    annotation.human_override.action = "confirmed_auto"
                    annotation.human_override.score = 7.6
                    annotation.human_override.reason = ""
           Trace tree in Phoenix shows the COMPLETE self-improvement loop:
                    > yellow.score → eval.calibration → mcp.consult
                    → blue.adjust → yellow.score(rev) → eval.calibration(pass)
                    → annotation.human_override

2:30–2:50  SCORE DELTA + COST + ARCHITECTURE [★ KICK #4]
           Two-score side-by-side panel:
             ┌──────────────────────────────────┐
             │ Without Phoenix consultation: 78 │
             │ With Phoenix consultation:    71 │
             │ Delta:                        -7 │
             │ The agent corrected itself.      │
             └──────────────────────────────────┘
           Cost dashboard final:
             $0.043 / 27K tokens · 7.2K cached (90% saved)
             Total runtime: 67 seconds.
           Architecture card slides in (10 stack badges):
             Gemini 3.1 Pro · Gemini 3 Flash · Gemini 3.1 Flash-Lite ·
             Agent Builder · Google ADK · Phoenix MCP · Phoenix Online Evals ·
             Qdrant Cloud · Cloud Run · Firestore

2:50–3:00  TAGLINE + COMPLIANCE PROOF
           Logo + tagline: "Glasshat. An agent that reads its own mistakes."
           1-frame flash at 2:55: GitHub repo About sidebar with
                                  Apache-2.0 license badge visible
                                  (Rapid Agent Stage 1 pass/fail proof).
           Repo URL displayed: github.com/Two-Weeks-Team/glasshat
```

**Wow/Kick distribution audit** (post-rev):
| Slot | WOW | KICK | Backup |
|---|---|---|---|
| 0:00-0:15 | ★ #0 hook | — | (low risk) |
| 0:15-0:45 | — | ★ #1 stack visible + Phoenix UI live | (resilient) |
| 0:45-1:00 | — | ★ #2 reasoning + structured plan | (resilient) |
| 1:00-1:30 | ★★ #1A Phoenix Online Eval | — | ★ Backup: Python Custom Evaluator |
| 1:30-2:00 | ★★ #1B MCP consult + strategy change | — | (high stakes) |
| 2:00-2:30 | — | ★ #3 loop closure + annotations | (resilient) |
| 2:30-2:50 | — | ★ #4 delta + cost + architecture | (low risk) |
| 2:50-3:00 | (close) | LICENSE badge frame | (low risk) |

8 wow/kick beats, every high-risk beat has a backup.

**Production notes** (Arize-specific):
- **YouTube upload mandatory** (Vimeo backup); Devpost form accepts both.
- English captions burned in (not auto-generated; pre-written + timed to ±0.5s).
- Phoenix UI must be **live during recording**, not screenshot — Phoenix Cloud project public-read enabled so judges can verify (optional but high-trust).
- Apache-2.0 in About sidebar visible at 2:55 (Stage 1 pass/fail compliance proof).
- Rehearse to 3:00 ±5 sec. Cut order: 2:30-2:50 → 2:00-2:30 → 0:15-0:45; never cut 1:00-2:00 (the wow).

**Production notes**:
- **YouTube upload mandatory** (Vimeo backup); demo posted at submission.
- English captions burned in (not auto-generated — pre-written, accurate, timed to ±0.5s).
- Phoenix UI must be **live**, not screenshot — Phoenix Cloud free tier project, public-read enabled so judges can verify (optional but high-trust).
- Show the GitHub repo About sidebar with Apache-2.0 license badge for 1 frame at 2:50 (Stage 1 pass/fail compliance proof).
- Rehearse to 3:00 ±5 seconds. Same cut priority as Qdrant version.

### 5.3 Demo timing risks + mitigations

| Risk | Mitigation |
|---|---|
| Live network failure during demo | Pre-record demo on a local cached path; deploy live version + screencast version both. Submit screencast to YouTube (live = backup). |
| Cloud Run cold-start on judge re-run | Pre-warm via cron; offer a "Try a sample" button with pre-cached run for judges who hit cold-start. |
| Phoenix Cloud rate-limit / outage at judging time | Local Phoenix in Cloud Run as failover (interface abstraction `MONITOR_BACKEND=phoenix-local` already planned in PLAN.md). |
| Demo crosses 3:00 mark | Hard cut at 3:00 in the recorded YouTube version (Rapid Agent rule: only first 3 min judged). Qdrant lets it slide but don't risk it. |
| Voice-over English clarity for non-native team | No voice-over. All text on-screen, English. Removes the risk entirely. |

---

## §6 — Dimension 6: Submission asset checklists (gate at submission day)

### 6.1 Qdrant VSD submission checklist (~2026-06-01)

| # | Item | Verification command / location | Status |
|---|---|---|---|
| 1 | Public OR private GitHub repo with all source code | `gh repo view Two-Weeks-Team/glasshat` (post-rename) | Pending §9 migration |
| 2 | README.md with: project description, install/run instructions, 3rd-party dependencies, fairthon-lineage disclosure, "all code authored in hackathon period" statement, architecture diagram | `cat README.md` | TBD |
| 3 | Demo video ≤3 minutes uploaded to YouTube (primary) + Loom (backup) | Public URL | TBD |
| 4 | Code with basic comments | `grep -r "//.*$\\|#.*$" --include="*.{ts,py}" ...` (qualitative check) | Pending Phase 1 |
| 5 | Qdrant DB load-bearing (6 collections, retrieval in scoring pipeline) | `pnpm run smoke:qdrant` | Pending Phase 1 |
| 6 | Non-chatbot UX confirmed (drop zones + plan card + monitor + report + 3D + vector-search page, no chat box) | Manual UI walkthrough | Pending Phase 1 |
| 7 | Team ≤4 members, all eligible | Team roster | TBD §9 |
| 8 | Submitted via Google Form `https://forms.gle/YDQ2TDUi8MqS9Vx28` (NOT Devpost) | Submission receipt | Day-of |
| 9 | Hosted URL accessible (no-login optional but recommended for judge ease) | `curl -I <url>` | Pending Phase 2 |
| 10 | Glasshat first commit timestamp in-period (2026-05-13 onwards) — git log proof preserved (no squash, no force-push to main) | `git log --reverse \| head -3` | ✓ first commit 2026-05-13 (pre-rename, but git history continuous) |
| 11 | 2026 Best-in-Category sponsor list checked weekly; secondary submission narrative ready if a sponsor matches Glasshat stack | Manual web check | Recurring |

### 6.2 Rapid Agent / Arize track submission checklist (~2026-06-11 14:00 PT)

| # | Item | Verification | Status |
|---|---|---|---|
| 1 | URL to hosted project (web platform) | `curl -I <url>` returns 200 | Pending Phase 2-3 |
| 2 | Public OSS repo with Apache-2.0 license **detectable in About sidebar** (not just LICENSE file) | GitHub repo About panel visual check | ✓ already configured for panelyst; verify post-rename |
| 3 | Demo video ≤3 minutes on **YouTube or Vimeo only** | Public YouTube URL | TBD |
| 4 | English or English subtitles in video; English in all written submission portions | Manual review | TBD |
| 5 | Devpost submission form complete (Arize track selected, team roster, project description) | Devpost submission preview | Day-of |
| 6 | **Stage 1 pass/fail proofs**: (a) Gemini 3 used, (b) Agent Builder used (Blue planner + hat sub-agents registered), (c) Arize Phoenix MCP server used at runtime, (d) Google Cloud product used (Cloud Run + Firestore + Eventarc), (e) "reasonably applies both required data from Partner and Google Cloud" — i.e., agent must visibly use Phoenix data + GCP infra to do the job | Reviewer walkthrough | Pending Phase 3 |
| 7 | **Arize track specifics**: (a) OpenInference instrumentation in code, (b) traces sent to Phoenix Cloud, (c) Phoenix MCP server configured for runtime introspection, (d) LLM-as-judge evals on traces, (e) self-improvement loop demonstrated in demo | Code grep + Phoenix UI verification | Pending Phase 3-4 |
| 8 | Runtime is **Cloud Run** (eligible category — not Visual Agent Builder alone) | Cloud Run service URL | Pending Phase 2 |
| 9 | Team ≤4 members, all eligible (Korea OK, no excluded territories) | Roster | TBD §9 |
| 10 | First commit + every commit in 2026-05-05 → 2026-06-11 PT window (origin commit history) | `git log --since="2026-05-05" --until="2026-06-11 14:00 PT"` | ✓ ongoing |
| 11 | "Project newly created by entrant during Contest Period" warranty defensible — README discloses fairthon as *concept* lineage, no code reused | README inspection | Pending §7 README rewrite |
| 12 | **Competitive-restriction defense**: README explicitly frames Qdrant ≠ Arize (vector DB vs observability — orthogonal categories) | README inspection | Pending §7 |
| 13 | No third-party advertising, slogans, logos, trademarks in video; original work warranty | Manual review | TBD |
| 14 | Video uploaded to YouTube unlisted (or public) → URL on submission form | YouTube upload | Day-of |

### 6.3 Shared/recurring tasks

| # | Item | Notes |
|---|---|---|
| S1 | Repo rename `panelyst → glasshat` (or new repo) + history preservation | §9 migration |
| S2 | All in-repo references updated (.env, README, PLAN.md, code, docs) | §9 |
| S3 | README rewrite for both narratives — Qdrant-framed top, Rapid-Agent-framed lower section, fairthon-lineage section, competitive-restriction defense paragraph | §7 |
| S4 | 50-150 public Devpost past-projects ingested into `past_evals` for anchor-comparison feature | Phase 1.12 |
| S5 | Demo storyboards locked, recorded, edited, ≤3:00 each, uploaded to YouTube | Phase 5+ |

---

## §7 — Dimension 7: README narrative architecture (per hackathon)

### 7.1 README top-of-fold (single README, two-narrative structure)

```markdown
# Glasshat

> The panel that audits itself.

**Glasshat** ingests a pitch deck and a GitHub repo, runs a six-perspective
AI panel scoring each artifact against a 100-point rubric — and shows you
the panel catching its own biases, in real time, in 3D.

**One demo, two ways to watch it:**

📺 **[Qdrant VSD demo (3 min)](youtube-link-1)** — _the panel audits
itself; vector-anchored score correction; 3D evaluation graph._

📺 **[Rapid Agent / Arize demo (3 min)](youtube-link-2)** — _agent
consults Phoenix MCP mid-run, detects past drift, changes retrieval
strategy live._

---

## What you drop in, what you get out

[ deck + repo ] → [ 6-perspective panel ] → [ 100-pt scored report
                                              + 3D evaluation graph
                                              + signed audit trail ]
                       ↑
                       └─ audits itself for bias/drift via Phoenix MCP +
                          Qdrant past_evals retrieval (live)
```

### 7.2 Required disclosure block (both hackathons read this)

```markdown
## About this submission

**All code in this repository was authored during the hackathon period**
(first commit 2026-05-13). The product is submitted to:

- **Qdrant "Think Outside the Bot" VSD 2026** (deadline 2026-06-01) —
  Qdrant is load-bearing: 6 collections (pitch_chunks, repo_chunks,
  techniques, bmad_criteria, past_evals, web_evidence) are queried by
  every scoring decision. Glasshat is not a chatbot — it is an
  artifact-ingesting evaluation pipeline.
- **Google Cloud Rapid Agent Hackathon** (Arize track, deadline
  2026-06-11) — Glasshat is a Gemini 3 + Agent Builder agent that
  integrates Arize Phoenix's MCP server at runtime to introspect its
  own evaluation traces and adapt its strategy. The integration is
  load-bearing: removing Phoenix breaks the self-improvement loop and
  the meta-evaluation that makes scores defensible.

**Concept lineage**: Glasshat re-implements the conceptual approach of
[fairthon.com] (Six Thinking Hats + BMAD rubric + 75 evaluation
techniques + 3D graph) on a GCP-native, agentic stack with a new
contribution: a transparent real-time fairness monitor. No code from
fairthon was reused; every line was authored fresh for this hackathon
period.

**Stack distinction (per Rapid Agent competitive-restriction clause)**:
Arize and Qdrant occupy orthogonal categories — Arize Phoenix is the
LLM-application observability and meta-evaluation layer; Qdrant is the
vector database for product memory (precedents, evidence, techniques,
rubric definitions). They do not compete on capabilities; they
co-operate on roles.
```

### 7.3 Architecture diagram inline (same as `docs/architecture.md`, embedded)

### 7.4 Setup + run instructions (Qdrant judge runs locally; Rapid Agent judge uses hosted URL)

### 7.5 License (Apache-2.0, in About sidebar — already configured for `panelyst`, migrate post-rename)

---

## §8 — `PLAN.md` §8 open items — closed

Original open items 1-9 from `PLAN.md` §8, each with the decision locked today:

| # | Open item (verbatim from PLAN.md) | Decision 2026-05-14 | Source |
|---|---|---|---|
| 1 | Confirm the Qdrant VSD hackathon START date + the exact "no previous projects" wording | **Period is open; exact start date not published. "All code must be created during the hackathon period (no previous projects allowed!)" — Glasshat first commit 2026-05-13 is comfortably in-period.** | §1.1 |
| 2 | Confirm Rapid Agent Official Rules once posted | **Posted. Period 2026-05-05 12:00 PT → 2026-06-11 14:00 PT. "Projects must be newly created by the entrant during the Contest Period. The Project must be Your original creation not a modification or extension of Your or anyone else's existing work." Tie-break: Tech Implementation > Design > Impact > Idea. Excluded countries: Korea NOT in list ✓.** | §1.2 |
| 3 | Repo name / slug — keep `panelyst` or new name? Apache-2.0 confirmed | **Rename to `glasshat`** (panel recommendation §6.1, user-approved 2026-05-14). Apache-2.0 ✓. Migration plan §9. | User decision 2026-05-14 |
| 4 | What happens to existing `~/Documents/GitHub/WhyC/` "While YC hires" code | **N/A** — already archived; `panelyst` (now → `glasshat`) is a separate fresh repo. | unchanged |
| 5 | fairthon historical-evaluation export (anonymized) to seed `past_evals` — available? | **Decision: do NOT use fairthon's history** (avoids "modification or extension of existing work" risk for both hackathons). Seed `past_evals` exclusively with 50-150 public Devpost past projects, run fresh through Glasshat's own pipeline. | Risk-mitigation decision |
| 6 | Arize plan/access (Arize AX / Phoenix; MCP server availability) + Rapid Agent partner onboarding | **Phoenix Cloud free tier at `app.phoenix.arize.com`. Phoenix MCP server = `@arizeai/phoenix-mcp` (npx-installable). Starter kit `github.com/Arize-ai/gemini-hackathon`. Self-host fallback for outage scenarios (interface abstraction `MONITOR_BACKEND=phoenix-local` already in `.env`).** | §1.2 |
| 7 | Team-of-record on each Devpost (≤4 for Qdrant) | **TBD — single user as of 2026-05-14. If team grows, max 4 for both hackathons. Decision deferred to user.** | Pending §10 |
| 8 | Frontend hosting (Cloud Run vs Firebase Hosting + Cloud Run backend); Qdrant Cloud vs self-hosted | **Frontend: Cloud Run (single hosting layer simplifies "code-owned runtime" Arize requirement). Qdrant: Cloud (zero-ops MVP), with local docker-compose for dev (interface abstraction `QDRANT_URL` already in `.env`).** | Resource-allocation decision |
| 9 | 3D graph must-demo vs nice-to-have (2D radar fallback locked) | **3D graph reclassified from stretch to MUST-BUILD** (panel §6.3, user-approved 2026-05-14, "ignore dates" — build to ship quality). 2D radar fallback remains in code, silent. No calendar-based go/no-go gate. | User decision 2026-05-14 |

---

## §9 — Rename migration plan (panelyst → glasshat)

User-approved on 2026-05-14. No timeline pressure (per user "ignore dates"). Sequenced for minimal disruption.

### 9.1 What needs to change

| Layer | Current | Target |
|---|---|---|
| GitHub repo | `Two-Weeks-Team/panelyst` | `Two-Weeks-Team/glasshat` (rename, preserve history + redirects) |
| Working directory | `~/Documents/GitHub/panelyst/` | Option A: rename folder. Option B: keep folder, repo remote points to glasshat. Decision: **rename folder** (clean state for new sessions) — but only after all in-flight work committed. |
| `package.json` / `pyproject.toml` name fields | `panelyst` | `glasshat` |
| `.env` and `.env.example` keys | `PANELYST_*` if any (check) | `GLASSHAT_*` |
| GCP project | `panelyst-hackathon` | **KEEP** (rename is org-confusing for billing/IAM, no judging value). Add `glasshat` as a label on resources. |
| Service account | `panelyst-dev@…` | **KEEP** (same reason) |
| Qdrant collections | `pitch_chunks` etc. | **KEEP** (collection names are functional, not branded) |
| README all references | "Panelyst" | "Glasshat" |
| PLAN.md / HANDOFF.md / docs/* | "Panelyst" | "Glasshat" (with note: "previously Panelyst pre-rename") |
| `claudedocs/` historical files | "Panelyst" | **DO NOT EDIT** (history snapshots) |
| Memory entries `~/.claude/projects/-Users-...-hackathon-submissions/memory/panelyst-project.md` etc. | references to Panelyst | Update memory body + index to reflect Glasshat as current name |
| Cloud Run service name | TBD (not deployed yet) | `glasshat-*` |
| Devpost project draft | TBD | `Glasshat` |
| Demo video script + on-screen text | TBD | "Glasshat" throughout |

### 9.2 Sequence (no dates; user "ignore dates")

1. **Lock decision in PLAN.md addendum** (point to this file)
2. Create rename branch `chore/rename-glasshat` (don't touch main yet — handoff continuity)
3. Update `package.json`, `pyproject.toml`, code identifiers, .env vars
4. Update `README.md` (full rewrite per §7 narrative)
5. Update `PLAN.md`, `docs/architecture.md`, `docs/gcp-setup.md` with new name (history files in `claudedocs/` untouched)
6. Update memory entries (`panelyst-project.md` body — rename mention, keep slug or rename slug to `glasshat-project`)
7. Open PR (or direct-to-main since pre-Phase 1)
8. `gh repo rename glasshat` (preserves history + URL redirects for ~30 days)
9. `mv ~/Documents/GitHub/panelyst ~/Documents/GitHub/glasshat`; update remote URL
10. Update GCP labels (optional, low priority)
11. Reflect rename in next `/handoff` doc

### 9.3 Backward-compatibility window

- GitHub repo redirects auto-active for ~30 days post-rename. After that, dead links break. Update README badges, hackathon submission links, demo overlay carefully.

---

## §10 — Risk register (top 10) with concrete mitigations

| # | Risk | Severity × Likelihood | Mitigation |
|---|---|---|---|
| 10.1 | **Rapid Agent competitive-restriction clause flagged** ("services that compete with the Partner") — judge questions whether Qdrant competes with Arize | High × Low | README §7.2 explicitly distinguishes Arize-Phoenix-as-observability from Qdrant-as-vector-DB; demo narration avoids "Phoenix vector search" framing. If asked, defense: Arize Phoenix's vector capability is for trace clustering, not a product offering competing with Qdrant in the vector DB category. |
| 10.2 | **Dual-submission split focus** — Arize-specific features bleed into Qdrant-primary build period | High × High | Lock: zero Arize-only code before Qdrant submission. Arize repackaging is narration + Phoenix UI side-by-side recording + README expansion, not new features. Decision tested at each plan-change request. |
| 10.3 | **3D graph under-delivers visually** | High × Medium | Build with 2D radar parity (every data point also computable in 2D). 3D adds **cluster-reveal-on-rotation** as the discriminator. If clusters don't reveal: rework camera angles before cutting the feature. No date gate (user instruction); kill only if visually proven inferior to 2D after 3 design iterations. |
| 10.4 | **Audit-the-auditor moment doesn't land in 3-min demo** | Critical × Medium | User-test on 5 non-team viewers before final video record. Acceptance: ≥4 of 5 can retell "the AI caught itself and fixed the score" within 30 seconds of viewing. If <4: rebuild visual emphasis (on-screen caption at correction beat; slow pacing of the moment by 5-8 seconds; brighter highlight on retrieved contradicting evidence). |
| 10.5 | **Cloud Run cold-start mid-demo** | High × Medium | Pre-warm before record. Local cached demo as YouTube upload. Live hosted URL is for judge re-runs; pre-warm cron + "Try a sample" button with pre-cached payload for judges hitting cold-start. |
| 10.6 | **Phoenix Cloud outage or rate-limit at judging** | High × Low | Self-hosted Phoenix in Cloud Run as failover (`MONITOR_BACKEND=phoenix-local` switch already in `.env`). Demo video uses Phoenix Cloud screenshot if live fails. |
| 10.7 | **Gemini 3 Pro preview API breaking change** | Medium × Medium | LLM adapter (planned Phase 1.2) auto-falls back to `gemini-2.5-pro` (`docs/gcp-setup.md` documented). Test the fallback weekly. |
| 10.8 | **Stage 1 pass/fail rejection on Rapid Agent** — judge can't verify Gemini + Agent Builder + Phoenix MCP + GCP integration in their walkthrough | Critical × Low | Hosted URL with a public "Demo run" button that runs a canned pipeline + exposes Phoenix UI link + Cloud Run service URLs + GitHub repo About sidebar. Walkthrough doc in README §7 with screenshots of each integration point. |
| 10.9 | **Naming collision** — "Glasshat" trademarked or already taken on Devpost / GitHub | Medium × Low | Check before rename PR: `gh repo view Two-Weeks-Team/glasshat`, USPTO TESS search, devpost search. If conflict: fall back to alternates (`Hatwatch`, `Tribunal`, `Witness`) noted in panel §6. |
| 10.10 | **2026 Qdrant Best-in-Category sponsors mismatch Glasshat stack** | Low × Medium | Monitor weekly. If a sponsor matches (e.g., Mistral, Neo4j, R3F-related), prepare a secondary narrative angle in README; if no match, no harm done. |

---

## §11 — Honest probability estimates + leverage shifts

From the 5-expert panel (Discussion + Synthesis), with current trajectory before/after this plan's recommendations are adopted:

| Hackathon | P(top-3) — current trajectory | P(top-3) — after this plan | Top 3 leverage shifts (in order of impact) |
|---|---|---|---|
| **Qdrant VSD 2026** | ~13% (median) | **~28-35%** | (1) Rename to Glasshat + headline sentence ("the panel that audits itself") locked; (2) 3D graph reclassified to must-build; (3) Demo script §5.1 rehearsed to 3:00 ±5s with audit moment functional |
| **Rapid Agent / Arize** | ~33% (median) | **~50-55%** | (1) Phoenix MCP runtime consultation built as a *visible decision change* (not just trace emission); (2) Score-before/after delta shown in demo as the loop made tangible; (3) Stage 1 pass/fail proofs (§6.2 items 6-7) verifiable in <2 minutes by a judge |

**Combined expected value** (1st-place equivalent, conservative): pre-plan ≈ $1.7K. Post-plan ≈ $4.2K, with material probability of placing in both contests rather than zero. (Honesty note: top-3 ≠ 1st-place; this is order-of-magnitude reasoning, not a financial forecast.)

The **single most important investment** for raising P(both) further is the audit-the-auditor moment's quality — its functional reliability, its 30-second comprehensibility, and its theatrical timing. Every other feature should be cut before this is cut.

---

## §12 — Decisions locked today (2026-05-14)

User-approved + panel-recommended:

1. ✅ **Qdrant VSD = primary submission target**. Rapid Agent / Arize track = repackaging of the same engine.
2. ✅ **Rename**: Panelyst → **Glasshat**. Migration sequenced in §9 (no date pressure).
3. ✅ **3D evaluation graph = must-build**, no calendar gate.
4. ✅ **Audit-the-auditor moment = the wow factor for both demos**.
5. ✅ **Cut from build entirely**: Korean i18n for v1, fairthon historical-evaluation seeding.
6. ✅ **Cut from demo (build retained)**: signed-report cryptographic UI (5-sec mention only), vector-search browse page for Qdrant demo (kept for Arize), 17-item BMAD parade (3-5 visible in demo).
7. ✅ **Phoenix MCP runtime consultation** (not just trace emission) = the Arize moat feature; build as a visible mid-run decision change.
8. ✅ Hosting: **Cloud Run for frontend + backend** (single runtime simplifies Arize "code-owned runtime" compliance); **Qdrant Cloud** for prod, local docker-compose for dev (interface abstraction unchanged).
9. ✅ No fairthon code or historical eval reuse; `past_evals` seeded only from 50-150 public Devpost past projects run fresh through Glasshat's own pipeline.
10. ✅ Both hackathon demo videos: on-screen captions in English, no live voice-over.
11. ✅ **Past_evals + Phoenix calibration corpus = Gemini 3 Hackathon stratified 524 projects** (24+ winners + 500 random non-winners, drawn from `gemini3.devpost.com`'s 4,499 corpus). Disclosed in README as calibration-only data. See `docs/wow-moment-design.md` §6.
12. ✅ **Meta-corpus narrative usage**: Qdrant demo includes 1-line "evaluated 524 of 4,499" caption at 2:30-2:50; Arize demo does NOT include meta-narrative (Phoenix experiment framing only).

### Deferred / not-yet-decided (pending user input or external event)

- §8.7: **Team composition** (≤4 for both) — single user as of today; if team grows, must commit before either submission.
- §10.10: **2026 Qdrant Best-in-Category sponsor list** — monitor weekly; trigger secondary narrative angle if a relevant sponsor appears.
- §10.9: **Glasshat name conflict check** (Devpost / GitHub / USPTO TESS) — verify before rename PR is merged.
- Hosted URL no-login / signup flow — decide during Phase 2 (Firebase Auth Google sign-in default; consider "Try a sample" button bypass for judges).

---

## §13 — What `PLAN.md` no longer represents accurately

The following sections of `PLAN.md` predate this Max-Wins Plan and are partially superseded:

- §3.1 "Agentic system" — accurate as architecture, but the demo emphasis is now the audit-the-auditor moment, not the Six Hats parade.
- §4 fairthon feature inventory → coverage — Korean i18n now **out of v1** (was MVP). Web-search RAG (Vertex Grounding) downgraded to optional Phase 2 if time permits (cut from demo path entirely).
- §6 MVP — 3D graph reclassified from "stretch-within-MVP" to **MUST-BUILD** (no calendar gate, build to ship quality).
- §8 open items — **closed** in this file's §8 table.
- §9 next work — sequence remains valid; cuts and double-downs apply per this file's §2 matrix and §12 decision log.

A short addendum will be appended to `PLAN.md` pointing to this file as the authoritative max-wins thesis. `docs/architecture.md` remains the authoritative architecture diagram.

---

*Last updated: 2026-05-14 KST. Authoritative on dual-submission strategy + decision log + risk register. Living document — update as 2026 Qdrant sponsor list publishes, team composition firms, and Phase 1+ executes.*
