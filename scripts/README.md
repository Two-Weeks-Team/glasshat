# scripts — dev / e2e helpers

- `real_e2e.py` — real Vertex `gemini-3.1-flash-lite` + Vertex embeddings + in-code
  hybrid retrieval + self-hosted Phoenix + real Phoenix MCP (stdio) via a Google
  ADK agent → full RubricSynthesizer→6-hat→audit→report run.
- `real_arize_ax_e2e.py` — same, exporting traces to **Arize AX** (`otlp.arize.com`).
- `real_phoenix_cloud_e2e.py` — same, exporting to Phoenix Cloud.
- `gen_rubric_schema.py` — regenerate the SynthesizedRubric JSON Schema.

All run against the live stack with credentials from the environment (never
hard-coded). No Qdrant.
