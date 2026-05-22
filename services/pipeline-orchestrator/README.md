# services/pipeline-orchestrator (`glasshat.pipeline`)

Wires the engine stages end-to-end: `run_evaluation` runs ingest → synthesize →
plan → 6-hat panel → audit self-correct → score → report, emitting SSE events and
a per-agent `glasshat.agent` Arize AX span at each stage. Depends only on the
P1/P2 abstractions, so it runs fully on the deterministic `mock` LLM + `memory`
store with **no credentials**. The ADK runtime adapter (`adk_runtime.py`) and the
Phoenix-MCP calibration consultant wrap the same stages for the live deployment.
Implemented and tested, CI-green.
