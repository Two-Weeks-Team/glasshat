# Phoenix LLM-as-a-Judge Evals — capture

> Source: https://arize.com/docs/phoenix/evaluation/llm-evals · Fetched 2026-05-21 · WebFetch extraction (partial — API method names not surfaced)

# Phoenix LLM-as-a-Judge Evaluations

## Core Architecture
Phoenix supports "LLM-as-a-judge evaluators, where a second model scores the output against a rubric." Uses **tool calling** for structured outputs rather than text parsing: Phoenix generates tools from evaluator output configs.

## Two Evaluation Approaches
1. **Client-Side Evals (SDK)**: Python and TypeScript SDKs for running evaluations against Phoenix traces, datasets, or any data source.
2. **Server-Side Evals (UI)**: configure evaluators in the Phoenix UI and attach to datasets.

## Key Capabilities
- **Model Agnostic** via adapters for OpenAI, LiteLLM, LangChain, AI SDK.
  > ⚠️ COMPLIANCE: for this hackathon the judge model MUST be Google/Gemini (e.g. via LiteLLM → Gemini, or a Gemini model class), NOT OpenAI/Anthropic.
- **Pre-built metrics** for RAG and tool-calling agents.
- **Automatic tracing** via OpenTelemetry.
- **Built-in Explanations**: all Phoenix LLM evaluations return explanations by default.

## Infrastructure
Handles rate-limit handling, error management, dynamic concurrency automatically via executors.

## Transparency
All evaluator runs are auto-traced via OpenTelemetry to a dedicated Phoenix project (inputs, prompts, reasoning, scores, timing).

> The extraction did NOT surface specific Python API names (`run_evals`, `llm_classify`), built-in template names (hallucination, QA-correctness, relevance, groundedness, toxicity), custom evaluator code, or Gemini model-class names. Local design (`docs/technical-apex-features.md` §2.3–2.9) already references these; confirm against full docs index when implementing.
