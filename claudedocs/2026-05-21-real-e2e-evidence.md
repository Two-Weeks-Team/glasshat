# Real-input e2e evidence (goal item 4) — 2026-05-21

Run: `scripts/real_e2e.py` against **real Vertex Gemini** (ADC, project `panelyst-hackathon`,
`us-central1`) + **locally self-hosted Phoenix** (in-process; Docker daemon was down, so the
`arize-phoenix` server was used — functionally identical to the Phoenix Docker container) +
**real Phoenix MCP** over stdio driven by a **real Google ADK agent**.

## What was real (no mocks)

| Component | Evidence |
|---|---|
| Self-hosted Phoenix | in-process server; **80 spans captured** (OpenInference auto-instrument) |
| Google ADK + GoogleADKInstrumentor | real `LlmAgent` + `InMemoryRunner` ran, instrumented |
| Phoenix MCP (MCPToolset stdio, `npx @arizeai/phoenix-mcp`) | **27 tools discovered**; ADK→MCP `list-projects` tool call made |
| Vertex Gemini (generation) | 6-hat panel scored on `gemini-2.5-flash` |
| Vertex embeddings | `text-embedding-005`, 768-dim |
| In-code hybrid retrieval | dense cosine + BM25 + RRF over the embedded deck |
| RubricSynthesizer | `rapid-agent` preset → 25/25/25/25 + ordered tie-break |
| Audit self-correct | YELLOW 8.0→7.04, 6.0→5.04, 10.0→9.0, 8.0→7.04 (spike-D calibration policy) |
| Report | final_score **54.04** (rapid-agent weighted) |
| SSE | 25 events incl. `score_corrected`, ending `complete` |

## Run record (real Gemini)

```
run_id=ccbe2bce-efef-448a-bb85-22a8275edd39  final_score=54.04
  tech-implementation: 3.336  [self-corrected]
  design: 1.8027  [self-corrected]
  potential-impact: 2.3333  [self-corrected]
  quality-of-idea: 3.336  [self-corrected]
audit self-corrections (yellow):
  tech-implementation: 8.0 -> 7.04
  design: 6.0 -> 5.04
  potential-impact: 10.0 -> 9.0
  quality-of-idea: 8.0 -> 7.04
Phoenix spans captured: 80
```

## Honest scope

- Real: Vertex Gemini generation + embeddings, in-code hybrid retrieval, Phoenix trace send
  (80 spans), Phoenix MCP stdio call via a real ADK agent, the full
  RubricSynthesizer→6-hat→audit→score→report pipeline, the self-correct score change, SSE.
- The **self-correct delta** is computed by the in-code calibration table (the deterministic
  implementation of the spike-D policy `clip(score − 0.8·mean_delta, p25, p75)`). Driving the
  correction from Phoenix-MCP-queried deltas (vs. the in-code table) would require seeding a
  Phoenix calibration dataset — a refinement, not a gap in the demonstrated chain.
- Models: `gemini-2.5` family on `us-central1` (the `gemini-3-*-preview` ids in `.env.example`
  require the `global` endpoint and were not exercised here).

Reproduce:
```
GOOGLE_CLOUD_PROJECT=panelyst-hackathon GOOGLE_GENAI_USE_VERTEXAI=true \
GOOGLE_CLOUD_REGION=us-central1 GLASSHAT_GEMINI_FLASH=gemini-2.5-flash \
PYTHONPATH=packages/shared/src:packages/rubric/src:agents/src:services/ingest/src:services/code-grader/src:services/pipeline-orchestrator/src:apps/api/src \
uv run python scripts/real_e2e.py
```
(requires the optional SDKs: `uv pip install google-genai google-adk arize-phoenix arize-phoenix-otel openinference-instrumentation-google-adk openinference-instrumentation-google-genai mcp`)
