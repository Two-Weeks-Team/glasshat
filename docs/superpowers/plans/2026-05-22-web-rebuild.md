# Glasshat Web Rebuild — Spec of Record

> **For agentic workers:** SDD + TDD, one PR per phase (feature branch → PR → main, **no squash**).
> Methodology and constraints are locked from the prior `/goal`.

**Goal:** Replace the thin web shell (static `/judge` placeholder + one hardcoded `/participate` button) with two genuinely functional viewports that exercise the full engine the API already serves.

**Why now:** The backend is rich and live (`/api/plan`, `/api/evaluate`, `/api/evaluate/stream`, `/api/runs/{id}`, `/api/runs/{id}/override`), but the frontend surfaces almost none of it. The live page reads as empty. This rebuild closes that gap.

**Tech stack:** Next.js 16 App Router, React 19, Tailwind v4 (OKLCH), `@react-three/fiber`, Vitest + Testing Library. Backend FastAPI (already built); one small additive endpoint (`/api/presets`).

---

## Contract (verified against running API, 2026-05-22)

### `PlanObject` (`POST /api/plan`)
```
hats_enabled: Hat[]            # "blue"|"white"|"red"|"yellow"|"black"|"green"
criteria_in_scope: string[]
retrieval_budget: { pitch_chunks:int, repo_chunks:int, past_evals:int }
weights: Record<criterion_id, number>   # sums to 1.0
code_grader_depth: string      # "lint" | ...
```

### `SynthesizedRubric` (embedded in `RunRecord.rubric`)
```
schema_version, rubric_id, rubric_schema_hash
source: { type, identifier, fetched_at, source_text_excerpt }
scoring_rule: { aggregation, final_scale }   # e.g. "weighted_sum", "0-100"
criteria: Criterion[]
tie_breakers: { order:int, criterion_id:string }[]
```
`Criterion`: `{ id, label, weight, scale, bmad_mapping:string[], descriptor_levels:Record<"1".."5",string>, evidence_required:bool, source_clause, source_excerpt }`

### `RunRecord` (`POST /api/evaluate`, `GET /api/runs/{id}`)
```
run_id, rubric:SynthesizedRubric, final_score:number,
scores: CriterionScore[], audit_corrections: AuditCorrection[],
mode: "judge"|"participant", created_at:string
```
`CriterionScore`: `{ criterion_id, score, evidence_refs:string[], audit:AuditCorrection|null }`
`AuditCorrection`: `{ hat, criterion_id, original, corrected, mean_delta, n, reason }`

### SSE stages (`POST /api/evaluate/stream`, `event:`/`data:`)
`queued{run_id}` → `ingesting{}` → `planning{rubric_id}` → `hats_running{hats[]}` →
`auditing{}` → `audit_started{}` → per-correction: `inconsistency_flagged{hat,criterion}`,
`phoenix_consultation{mean_delta,n}`, `anchor_retrieval{n}`, `score_corrected{hat,criterion,from,to}` →
`scoring{}` → `graph_reshape{criteria}` → `complete{final_score}`.
`complete` carries only `final_score`; fetch `GET /api/runs/{run_id}` for the full record.

### New: `GET /api/presets`
Returns `PresetInfo[]`: `{ id, label, criteria_count, final_scale, source_type }` —
derived from `glasshat.rubric.presets.list_presets()` + `load_preset()`.

---

## Phases (one PR each)

### PR #15 — Foundation + `/api/presets`
- **Backend (TDD):** `GET /api/presets` in `apps/api/.../app.py`; test in `apps/api/tests/`.
- **Frontend:** rewrite `lib/api.ts` with full types + `getPlan`, `listPresets`, `override`;
  `lib/stages.ts` (typed stage metadata). Design system: dark `globals.css`, `layout.tsx`
  (global nav + footer). Reusable components: `Badge`, `StatCard`, `StageTimeline`,
  `RubricTable`, `EvidenceList`, `AuditCallout`. Vitest tests for pure/presentational units.
- **Files:** `apps/api/.../app.py`, `apps/web/lib/{api,stages}.ts`, `apps/web/app/{globals.css,layout.tsx}`,
  `apps/web/components/{Badge,StatCard,StageTimeline,RubricTable,EvidenceList,AuditCallout}.tsx` (+ `.test.tsx`).

### PR #16 — `/participate` full rebuild
- Input form (deck textarea, repo URL, preset `<select>` from `/api/presets`, mode).
- Plan gate: `POST /api/plan` → render plan + rubric (`RubricTable`) → "Approve & run".
- Live run: `streamEvaluate` → `StageTimeline` lights up; wow-beats drive a self-correction
  callout. On `complete` → `getRun` → results.
- Results: final score (native scale), per-criterion `ScoreBar` (weight %, evidence, audit),
  `ConstellationGraph` reshaped from real scores (corrected nodes move), weakest-axis hint.
- Extract SSE→state reducer to `lib/participate-state.ts` for unit tests.

### PR #17 — `/judge` full rebuild
- Seeded sample submissions + add-your-own deck texts.
- Batch evaluate (N× `/api/evaluate`), per-submission live status, ranking table
  (rank, label, final, per-criterion mini-bars), Top-K vs known winners.
- Lock official score → `POST /api/runs/{id}/override`; locked rows immutable.
- Extract ranking/Top-K logic to `lib/ranking.ts` for unit tests.

### PR #18 — Landing + real-Vertex deploy + verify
- Landing: hero, pipeline viz, live API status, preset showcase.
- `Dockerfile.api`: install `vertex`+`phoenix` extras. `deploy.sh`: real-Vertex env +
  Secret Manager wiring for `PHOENIX_API_KEY` (no committed `.env`).
- Redeploy after CI green (needs user-provided `PHOENIX_API_KEY`). Verification doc + README update.

## Verification gate (every PR)
```
uv run pytest                                   # backend, mock/memory
cd apps/web && pnpm lint && pnpm typecheck && pnpm test && pnpm build
```
All green before merge. No `mock|stub|placeholder|TODO|not implemented` in shipped code.
