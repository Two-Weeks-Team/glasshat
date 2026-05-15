# Hybrid Mode — Specification (Judge × Participant)

> **Status**: Locked 2026-05-15 by user. Implements [[glasshat-rubric-and-mode]] decision §14. Full design before code (Phase 1.mode-UI implementation target, ~2.3d).
>
> **Pattern reference**: `Two-Weeks-Team/seoul-26th-april-hack-judges` (CMUX×AIM judge workbench). **Design pattern only — zero code reuse**, per fairthon-lineage discipline.

---

## §1 — Why two modes on one engine

Glasshat's evaluation engine (RubricSynthesizer + Six Hats + AuditLoop + BMADScorer) is *viewer-agnostic*. The same scored report can be consumed by:

- A **judge** evaluating N submissions in batch, ranking them, locking official scores under their portal's authority.
- A **participant** evaluating their own single submission, iterating on weak axes before submitting.

Both viewers need the same engine output, but with **different UI affordances, different RLS scopes, and different demo narrations**. Building two products would split focus; building one product with a viewport switch leverages the engine twice.

**Strategic payoff**:

| Hackathon | Primary viewport | Why |
|---|---|---|
| Qdrant VSD | Judge mode | Batch evaluation of 503 corpus = vector search at scale; Top-K hit rate = ground-truth verification; Recommendation API + group-by visible |
| Rapid Agent / Arize | Participant mode | Mid-iteration Phoenix MCP consultation = literal "agent that improves over time" (Arize bonus dimension); Tech tie-break maxed by RubricSynthesizer + iterate-loop |

**Final 1-second reveal** (both demos' close):

> "Both viewports run the same engine. Fairness is who's looking."

This is the dinner-table-retellable closure for the hybrid thesis: Glasshat doesn't just evaluate; it proves that evaluation is observer-relative.

---

## §2 — Topology

```
                     ┌────────────────────────────────────────────┐
                     │          GLASSHAT EVALUATION ENGINE         │
                     │   RubricSynthesizer → BluePlanner → Hats → │
                     │   AuditLoop → BMADScorer → Report           │
                     └─────────────┬───────────────┬───────────────┘
                                   │               │
                       same engine output (Phoenix-traced, Firestore-persisted)
                                   │               │
              ┌────────────────────┘               └────────────────────┐
              ▼                                                          ▼
   ┌──────────────────────┐                              ┌──────────────────────┐
   │   /judge viewport     │                              │  /participate         │
   │                      │                              │  viewport             │
   │  • Batch upload      │                              │  • Single submission  │
   │    (CSV/zip)         │                              │  • Iterate loop       │
   │  • Rank table        │                              │  • Phoenix uplift     │
   │  • Top-K hit rate    │                              │    suggestions        │
   │  • Human-locked      │                              │  • Pre-submit gate    │
   │    official scores   │                              │                      │
   └──────────────────────┘                              └──────────────────────┘
              │                                                          │
              │     (Firestore RLS + ADK SessionService scope)           │
              ▼                                                          ▼
   judge_runs/{run_id}                                  participant_runs/{user_id}/{run_id}
   judge_locked_scores/{run_id}/{submission_id}         participant_iterations/{run_id}
```

**Single source of truth**: the evaluation engine. Both viewports read the same `runs/{id}` Firestore documents and the same Phoenix project (`glasshat-prod`). The viewport split is presentation + RLS, not engine logic.

---

## §3 — Judge mode (`/judge`)

### Persona
- Hackathon operations team
- Incubator/accelerator review committee
- VC firm associate doing first-pass dealflow scoring
- Internal R&D evaluation board

### Flow

1. **Login** as a judge (Firebase Auth Google sign-in, claim `glasshat.role: judge` set via custom claim).
2. **Create batch run**: select rubric (preset / URL / YAML upload), upload CSV manifest or zip of N submissions:
   - CSV columns: `submission_id, deck_pdf_url, repo_url, [optional: track_id, team_size, …]`
   - zip layout: `{submission_id}/deck.pdf` + `{submission_id}/repo_url.txt`
3. **Background batch processing**: each submission runs through the engine. Cloud Run Jobs scale parallel; batch size capped at concurrency limit (default 5, configurable per Cloud Run quota).
4. **Live progress dashboard**: 7-column Kanban inspired by seoul-26th-april — *queued → ingesting → planning → hats running → auditing → scoring → complete*. Each card streams its current state via SSE (engine is already SSE-emitting from existing wow-moment design).
5. **Rank table** (post-batch):
   ```
   ┌──────┬──────────────────────────┬───────┬─────────────────────────────────┐
   │ Rank │ Submission               │ Score │ Top criterion / weak criterion  │
   ├──────┼──────────────────────────┼───────┼─────────────────────────────────┤
   │  1   │ Globot                   │ 91/100│ Originality 5/5 / Design 4/5   │
   │  2   │ Aegis Multi-Agent Crisis │ 89/100│ Tech 5/5 / Presentation 3/5    │
   │  3   │ ...                      │ ...   │ ...                              │
   └──────┴──────────────────────────┴───────┴─────────────────────────────────┘
   [ Lock official scores ]   [ Export CSV ]   [ Compare with: 2 winners (manual) ]
   ```
6. **Top-K hit rate badge**: if the dataset has known winners (e.g., 503 corpus has 13 named winners), the rank table shows `9/13 winners in predicted top-13 (69%)`. Demo viewport feature.
7. **Human gate (lock)**: judge locks official scores. Locked scores are immutable + signed; subsequent runs cannot modify them. This is the seoul-26th-april "AI proposes, human disposes" pattern.

### Demo (Qdrant version, 3 min)

The Qdrant demo's core scene becomes the **Judge mode batch run on the 503 corpus**. The narration foregrounds:

- 0:00-0:30 Hook + drag a 503-row CSV onto `/judge` page
- 0:30-1:30 Live Kanban shows ~30 cards/sec moving through stages; cost meter ticks; total elapsed shown
- 1:30-2:00 Audit moment fires on a high-profile card (engineered to trigger; e.g., one of the synthetic `/demo` items); 3D graph appears with 503 anchor constellation
- 2:00-2:30 Rank table appears; **Top-K hit rate: 9/13 winners** flashes
- 2:30-2:50 Recommendation API close: "ranks similar to Vector Vintage (winner)" anchor comparison
- 2:50-3:00 Tagline + reveal teaser: "Same engine has another viewport — see Rapid Agent demo"

### RLS scope
- Judge sees only the `judge_runs/{run_id}` they created or were granted access to (via `judge_share_grants/{run_id}/{judge_uid}`)
- Participants in the dataset cannot see judge runs (different namespace)

### Security
- Batch zip is uploaded to `gs://glasshat-judge-uploads/` with 7-day TTL
- Each submission's `repo_url` is cloned in a Cloud Run Job with **read-only filesystem + no network egress** — clones only the URL provided, runs static heuristics + sampled-code grading, never executes user code
- Phoenix project: `glasshat-judge-{run_id}` (per-run namespace prevents cross-judge trace leakage)

---

## §4 — Participant mode (`/participate`)

### Persona
- Hackathon participant preparing a submission
- Startup founder preparing a VC deck
- Academic preparing a research-program proposal

### Flow

1. **Login** as participant (Firebase Auth Google sign-in, default role `glasshat.role: participant`).
2. **Single submission upload**: deck.pdf + repo URL + select target rubric (preset or URL).
3. **Engine runs** (same as judge mode, single submission only).
4. **Score breakdown view**:
   ```
   YOUR SUBMISSION: Glasshat                                  Rubric: Rapid Agent / Arize
   ┌────────────────────────────────────────────────────────────────┐
   │  Tech Implementation  ████████░  4/5   weight 40%   8 leverage  │  ◀ tie-break #1
   │  Design               █████░░░░  3/5   weight 30%   3 leverage  │
   │  Potential Impact     ██████░░░  3/5   weight 20%   2 leverage  │
   │  Quality of Idea      █████████  5/5   weight 10%   0 leverage  │
   │  ─────                                                          │
   │  Final: 73/100                                                  │
   └────────────────────────────────────────────────────────────────┘

   ▸ Strongest: Quality of Idea — meta-evaluation thesis is novel
   ▸ Weakest with highest leverage: Tech Implementation
       Phoenix MCP suggestion (mid-loop):
         "README lacks 'multi-stage container' section. Adding to README
          before C2 evaluation typically yields +0.5 on Tech axis on
          comparable past submissions. Estimated final score lift: +2 pts."
       [ Show diff suggestion ]   [ Apply + re-run ]
   ```
5. **Iterate loop**: participant edits README/code → click `Apply + re-run` → score updates live (delta animation). Phoenix MCP consultation re-fires if the change crossed any criterion threshold.
6. **Pre-submit gate**: Glasshat verifies threshold gates (e.g., "Apache-2.0 in About sidebar", "video URL ≤3 min on YouTube/Vimeo", "Qdrant load-bearing in code"). Refuses to declare "ready" until all gates pass.

### Demo (Rapid Agent version, 3 min)

The Rapid Agent demo's core scene becomes a **Participant mode iterate loop** on a synthetic-but-realistic submission. Foregrounds:

- 0:00-0:30 Hook + participant uploads "MyAgent" deck + repo to `/participate`
- 0:30-1:00 Engine runs; participant sees Tech 3/5 result with Phoenix MCP highlighted
- 1:00-1:30 Phoenix MCP consultation visible (split screen: Glasshat left, Phoenix Cloud trace tree right) — the consultation suggests adding a section to README
- 1:30-2:00 Participant clicks `Apply + re-run` → ADK LoopAgent re-executes affected sub-pipeline → score animates from 73 → 79
- 2:00-2:30 Loop closes with Phoenix Annotation written; trace tree shows the complete self-improvement chain; before/after delta panel
- 2:30-2:50 Compliance proof: License badge + Cloud Run service URL + Phoenix MCP call chain visible
- 2:50-3:00 Tagline + reveal teaser: "Same engine has another viewport — see Qdrant demo"

### RLS scope
- Participant sees only their own `participant_runs/{user_id}/{run_id}` documents
- Phoenix project: `glasshat-participant-{user_id}` (per-user namespace; participants don't see each other's traces)

### Security
- Participant repo URL cloned in Cloud Run Job with same constraints as judge mode (read-only FS, no egress)
- Iterate-loop's `Apply + re-run` only re-runs the affected sub-pipeline (RubricSynthesizer cached, only re-evaluates the criteria affected by changed inputs); cost-bounded

---

## §5 — Final 1-second reveal (both demos)

After the primary demo's close, a 1-second cut shows the *other* viewport with the same submission's score:

- **Qdrant demo close**: The 503 rank table fades to participant view of one of the rows ("This was a participant view too — see how Globot's team would have used it: …").
- **Rapid Agent demo close**: The participant iterate-loop fades to a judge view of the same submission ranked among 22 others ("This is what a judge sees once you submit. Same engine. Different viewer.")

Caption: **"Same engine. Different viewer. Different fairness."**

This is the rhetorical closure: Glasshat doesn't just evaluate; it makes evaluation accountable to the viewer.

---

## §6 — Firestore data model

```
glasshat-firestore/
├── runs/{run_id}                          # ENGINE-OWNED, both modes write here
│   {
│     status: "complete",
│     rubric_synthesized: <SynthesizedRubric>,
│     scores: { criterion_id: { score, evidence_refs, ... } },
│     audit_corrections: [...],
│     phoenix_project: "glasshat-...",
│     created_at: ts, finished_at: ts,
│     creator_uid: <user_id>,
│     mode: "judge" | "participant",
│   }
│
├── judge_runs/{run_id}                    # MODE-SPECIFIC: judge metadata
│   {
│     judge_uid: <user_id>,
│     dataset_manifest: { source: "csv" | "zip", ... },
│     submissions: [ submission_id, ... ],
│     rank_table: [ { submission_id, score, rank } ],
│     locked: false,
│     locked_at: null,
│     locked_signature: null,
│     top_k_hit_rate: { k: 13, hits: 9, ground_truth_source: "gemini3-winners.json" },
│   }
│
├── judge_locked_scores/{run_id}/{submission_id}   # IMMUTABLE post-lock
│   {
│     official_score: 87,
│     official_rank: 3,
│     judge_signature: <hash>,
│     locked_at: ts,
│     # Cannot be modified after creation. Append-only audit log via DB trigger.
│   }
│
├── participant_runs/{user_id}/{run_id}     # MODE-SPECIFIC: participant ownership
│   {
│     submission: { deck_pdf_url, repo_url },
│     iterations: [ { iteration_id, score, delta, phoenix_suggestion } ],
│     ready_for_submission: false,
│     threshold_gates_status: { gate_id: pass | fail | unchecked },
│   }
│
├── judge_share_grants/{run_id}/{judge_uid}  # RLS: who can see this judge run
└── audit_events/                             # Append-only via DB trigger; no UPDATE/DELETE
```

**RLS rules** (Firestore security rules excerpt):

```
match /runs/{run_id} {
  allow read: if request.auth.uid == resource.data.creator_uid
              || (resource.data.mode == "judge"
                  && exists(/databases/$(database)/documents/judge_share_grants/$(run_id)/$(request.auth.uid)));
  allow write: if request.auth.uid == resource.data.creator_uid && resource.data.locked == false;
}

match /judge_runs/{run_id} {
  allow read: if request.auth.token.glasshat_role == "judge"
              && (request.auth.uid == resource.data.judge_uid
                  || exists(/databases/$(database)/documents/judge_share_grants/$(run_id)/$(request.auth.uid)));
  allow write: if request.auth.uid == resource.data.judge_uid;
}

match /judge_locked_scores/{run_id}/{submission_id} {
  allow read: if request.auth.token.glasshat_role == "judge";
  allow create: if request.auth.token.glasshat_role == "judge"
                 && request.auth.uid == get(/databases/$(database)/documents/judge_runs/$(run_id)).data.judge_uid;
  allow update, delete: if false;  // immutable
}

match /participant_runs/{user_id}/{run_id} {
  allow read, write: if request.auth.uid == user_id;
}
```

---

## §7 — Next.js app structure

```
apps/web/
├── app/
│   ├── layout.tsx                         # Shared shell + auth provider
│   ├── page.tsx                            # Landing — "Choose your viewport"
│   │                                       Big buttons: [I'm a Judge] [I'm a Participant]
│   │
│   ├── judge/
│   │   ├── layout.tsx                     # Judge-role guard (redirect if not judge claim)
│   │   ├── page.tsx                       # Dashboard: list of own + shared judge runs
│   │   ├── new/
│   │   │   └── page.tsx                   # New batch run wizard
│   │   ├── runs/[runId]/
│   │   │   ├── page.tsx                   # Live Kanban + rank table
│   │   │   ├── lock/
│   │   │   │   └── page.tsx               # Lock confirmation flow
│   │   │   └── compare/
│   │   │       └── page.tsx               # Top-K hit rate viewer (if ground truth supplied)
│   │
│   ├── participate/
│   │   ├── layout.tsx                     # Participant guard (default for any logged-in user)
│   │   ├── page.tsx                       # Dashboard: own runs
│   │   ├── new/
│   │   │   └── page.tsx                   # Single submission upload
│   │   ├── runs/[runId]/
│   │   │   ├── page.tsx                   # Score breakdown + iterate UI
│   │   │   └── compare/
│   │   │       └── page.tsx               # Compare iterations (delta visualization)
│   │
│   └── api/
│       ├── runs/                          # Engine invocation endpoints
│       └── webhooks/phoenix/              # Phoenix annotation write-back
│
├── components/
│   ├── shared/                            # KanbanCard, ScoreBar, AuditDrawer (used by both modes)
│   ├── judge/                              # RankTable, BatchUploader, LockGate, TopKBadge
│   └── participate/                        # IterateBar, PhoenixSuggestionCard, ThresholdGateChecklist
│
└── lib/
    ├── firebase.ts                         # Auth + Firestore client
    ├── sse.ts                              # SSE consumer (shared)
    └── rls.ts                              # Client-side role checks
```

---

## §8 — Implementation sequence (Phase 1.mode-UI, ~2.3d)

| Step | What | Time | Owner |
|---|---|---|---|
| 1 | Next.js app scaffold + auth + landing page | 0.3d | Frontend |
| 2 | Shared components (KanbanCard, ScoreBar, AuditDrawer, SSE hook) | 0.5d | Frontend |
| 3 | Judge mode: batch upload + Kanban + rank table | 0.6d | Frontend + Backend |
| 4 | Judge mode: lock flow + Top-K hit rate compute | 0.3d | Frontend + Backend |
| 5 | Participant mode: single upload + score breakdown + iterate UI | 0.4d | Frontend + Backend |
| 6 | Firestore security rules + RLS verification tests | 0.2d | Backend |
| **Total** | | **2.3d** | |

---

## §9 — Open questions (deferred to V2 unless user calls them up)

| Item | Default disposition |
|---|---|
| Multi-judge consensus on the same dataset (3 judges score, system computes inter-rater agreement) | V2 — Glasshat v1 is single-judge per run |
| Participant-to-judge "request review" flow | V2 |
| Anonymized batch judging (judge sees scores without team identity) | V2 — useful for VC bias mitigation |
| Public leaderboard for judge runs (with judge's permission) | V2 |
| Self-improvement of the engine itself: judge override patterns feed RubricSynthesizer fine-tuning corpus | V2 — interesting research direction |

---

*Last updated: 2026-05-15 KST. Authoritative on Hybrid mode (Judge × Participant) design. Phase 1.mode-UI implementation derives from this spec.*
