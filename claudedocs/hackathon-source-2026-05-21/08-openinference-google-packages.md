# OpenInference Google Instrumentation Packages — capture

> Source: https://github.com/Arize-ai/openinference · Fetched 2026-05-21 · WebFetch extraction

# OpenInference Google Instrumentation Packages

## 1. google-genai
- **Pip**: `openinference-instrumentation-google-genai`
- **Instruments**: Google GenAI (Gemini API + Vertex)
- **Usage**: `GoogleGenAIInstrumentor().instrument()`

## 2. vertexai
- **Pip**: `openinference-instrumentation-vertexai`
- **Instruments**: VertexAI
- **Usage**: `VertexAIInstrumentor().instrument()`

## 3. google-adk
- **Pip**: `openinference-instrumentation-google-adk`
- **Instruments**: Google ADK
- **Usage**: `GoogleADKInstrumentor().instrument()`

## Semantic Conventions (referenced)
- LLM spans: `llm.input.messages`, `llm.output_messages`
- Tool spans: `tool.name`
- Retrieval spans: `retrieval.documents`

> Exact code snippets / full semantic-convention mappings for the Google packages are in the individual package directories in the repo — consult before final wiring.
