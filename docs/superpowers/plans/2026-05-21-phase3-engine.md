# Phase 3 — Evaluation engine (ingest + agents + pipeline)

> REQUIRED SUB-SKILL: superpowers:executing-plans (inline). Derives from `2026-05-21-glasshat-roadmap.md`. Split into **P3a** (`feat/arize-ingest-agents`) + **P3b** (`feat/arize-pipeline`) to avoid a mega-PR.

**Goal:** Implement the full evaluation pipeline against the P1/P2 abstractions so it runs **end-to-end on `mock` LLM + `memory` store with no credentials and no `google-adk`** (CI-green), producing a persisted `RunRecord` that includes the audit **self-correct score delta**. The real ADK runtime (`LoopAgent`/`ParallelAgent`/`MCPToolset`) and Phoenix-MCP consultation are lazy, integration-gated adapters.

**Architecture:** New `glasshat.*` workspace packages. Engine stages are plain async Python consuming `LlmClient`/`Retrieval`/`DocStore`/`Tracer` — the ADK graph is an adapter that wraps the same stage functions for the live runtime. Calibration math from spike D: `new = clip(predicted − 0.8·mean_delta, p25, p75)`, ±2.0 cap.

**Packages (workspace members):** `agents/` → `glasshat.agents`; `services/ingest` → `glasshat.ingest`; `services/code-grader` → `glasshat.code_grader`; `services/pipeline-orchestrator` → `glasshat.pipeline`.

---

## P3a — branch `feat/arize-ingest-agents`

### Task 0: workspace expansion + 3 package skeletons
- root `pyproject.toml`: `[tool.uv.workspace] members = ["packages/*", "services/*", "agents"]`; pytest `pythonpath` + mypy `mypy_path` += `agents/src`, `services/ingest/src`, `services/code-grader/src`, `services/pipeline-orchestrator/src`. CI `testpaths` add the new tests dirs.
- `agents/pyproject.toml` (`glasshat-agents`, deps glasshat-shared+glasshat-rubric), `services/ingest/pyproject.toml`, `services/code-grader/pyproject.toml` — all hatchling src-layout namespace. `src/glasshat/<x>/__init__.py`. Smoke test each import. `uv sync`; commit.

### Task 1: `glasshat.agents.types` (engine contracts — SDD)
Pydantic models: `Chunk(id,text,source,vector?)`, `RepoFacts(url,languages,loc,has_tests,has_ci,readme_excerpt,heuristics:dict)`, `EvaluationInput(rubric_source, deck_text, repo_url, mode)`, `PlanObject(hats_enabled:list[Hat], criteria_in_scope:list[str], retrieval_budget:dict, weights:dict[str,float], code_grader_depth:str)`, `HatAssessment(hat, criterion_id, score:float, evidence_refs:list[str], rationale, evidence_depth:float)`, `AuditCorrection(hat, criterion_id, original:float, corrected:float, mean_delta:float, n:int, reason)`, `CriterionScore(criterion_id, score:float, evidence_refs, audit:AuditCorrection|None)`, `RunRecord(run_id, rubric:SynthesizedRubric, scores:list[CriterionScore], final_score:float, audit_corrections:list[AuditCorrection], mode, created_at)`. TDD: construct + validate ranges.

### Task 2: `glasshat.agents.rubric_synthesizer`
`async synthesize(inp, llm, *, validator=validate_rubric) -> SynthesizedRubric`: Path A (preset_id → `load_preset`), Path D (custom_yaml → `validate_custom_yaml`), Paths B/C (llm.generate(prompt) → parse YAML → `SynthesizedRubric` + soft-validate). TDD: preset path returns rapid-agent 25/25/25/25; custom path; mock-LLM URL path returns a valid rubric (mock returns a canned valid YAML keyed by prompt? — use a `parse` injection so the test feeds llm output). Use `agents/rubric_synthesizer/prompt.md` (spec §5 text) loaded at module import.

### Task 3: `glasshat.agents.blue_planner`
`plan(rubric, inp) -> PlanObject`: enable all 6 hats; criteria_in_scope = rubric criterion ids; weights from rubric; retrieval_budget defaults; code_grader_depth from input. TDD deterministic.

### Task 4: `glasshat.agents.hats`
`async run_hat(hat, rubric, ctx, llm, retrieval, tracer) -> list[HatAssessment]` (one per in-scope criterion; score derived from llm.generate parsed deterministically in mock; evidence via retrieval.search). `async run_panel(plan, ...) -> list[HatAssessment]` (gather across hats). TDD with mock llm + HybridIndex: panel returns assessments for every (hat, criterion); spans opened on tracer.

### Task 5: `glasshat.agents.audit` (triple detection + calibration self-correct)
`detect_inconsistencies(assessments, calibration_table) -> list[flagged]` (path: calibration mean_delta per (hat,criterion,evidence_bucket); flag if |mean_delta|>threshold). `Consultant` protocol (`consult(hat,criterion,bucket)->ConsultResult{mean_delta,n,p25,p75}`); `TableConsultant` (deterministic from in-code table) + lazy `PhoenixMcpConsultant` (MCPToolset stdio, pragma no cover). `apply_correction(assessment, consult) -> AuditCorrection` using spike-D formula. `async run_audit(assessments, consultant) -> list[AuditCorrection]`. TDD: engineered over-confident Yellow A1 (9.0, low evidence) → corrected ≈7.6; calibrated hat → no correction; ±2.0 cap; p25/p75 clip.

### Task 6: `glasshat.agents.bmad_scorer`
`score(rubric, assessments, corrections) -> list[CriterionScore]`: per criterion, aggregate hat assessments (mean of corrected scores), attach evidence + audit. TDD: corrected scores feed through; criterion with audit shows corrected value.

### Task 7: `glasshat.agents.report`
`assemble(run_id, rubric, scores, corrections, mode) -> RunRecord`: compute final per `scoring_rule` — weighted_sum (Σ weightᵢ·scoreᵢ scaled to final_scale), simple_average (mean), tie_break_ordered; map per-criterion scale→final_scale. TDD: rapid-agent 25/25/25/25 weighted final; qdrant simple_average; tie-break ordering exposed.

### Task 8: `glasshat.ingest`
`chunk_text(text, *, max_tokens=...) -> list[Chunk]` (deterministic splitter); `async ingest_deck(text=None, pdf_bytes=None, llm=None) -> list[Chunk]` (text path pure; pdf path lazy Gemini multimodal, pragma no cover); `embed_chunks(chunks, llm) -> chunks(with vectors)`. TDD text+embed paths with mock llm.

### Task 9: `glasshat.code_grader`
`grade_repo(path) -> RepoFacts`: real static heuristics over a directory (detect languages by extension, count LOC, presence of tests/ + .github/workflows, README excerpt). `async clone_and_grade(url) -> RepoFacts` (lazy `git clone --depth 1`, pragma no cover). TDD: build a tmp repo dir fixture → asserts languages/has_tests/has_ci.

### Task 10: P3a gate + PR
Full gate green (coverage ≥85% on new code; integration/lazy paths pragma'd). Push, PR, CI green, merge (merge commit).

---

## P3b — branch `feat/arize-pipeline`

### Task 11: `glasshat.pipeline.events` (SSE event model)
`PipelineEvent(stage, payload, ts)`; the 6 wow-beat events (audit_started, inconsistency_flagged, phoenix_consultation, anchor_retrieval, score_corrected, graph_reshape). TDD serialize to SSE `data:` lines.

### Task 12: `glasshat.pipeline.engine` (orchestrator — end-to-end)
`Deps(llm, retrieval, docstore, blobstore, tracer, consultant)` + `default_deps(settings)` (mock/memory/noop/table). `async def run_evaluation(inp, deps, *, on_event=None) -> RunRecord`: ingest → synthesize → plan → panel → audit → score → report → docstore.put("runs", run_id, record); emits events incl. the **self-correct delta**. TDD: full run on mock+memory yields RunRecord with ≥1 AuditCorrection and a persisted doc; event sequence emitted in order. This is the **end-to-end-on-mock** exit evidence.

### Task 13: `glasshat.pipeline.adk_runtime` (lazy ADK adapter, integration)
Wrap the stage fns in ADK `CustomAgent`/`LoopAgent`/`ParallelAgent` + `MCPToolset(StdioConnectionParams(... npx @arizeai/phoenix-mcp ...))` (spike C pattern) + `GoogleADKInstrumentor`. All pragma no cover + `@integration` smoke (skip without google-adk + creds).

### Task 14: P3b gate + PR; both merged → engine phase complete.

## Notes
- "mock"/"memory"/"noop"/"table" are real deterministic backends (architecture §5), not stubs. Zero `TODO`/`placeholder`/`not implemented` strings.
- Coverage gate stays ≥90% globally where unit-reachable; ADK/Vertex/Phoenix-MCP/PDF/git lazy bodies are `# pragma: no cover` (integration-only) — documented.
