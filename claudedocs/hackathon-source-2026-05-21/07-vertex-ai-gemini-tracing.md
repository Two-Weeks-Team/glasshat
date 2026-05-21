# Vertex AI / Gemini Auto-Instrumentation — capture

> Source: https://arize.com/docs/ax/llm-tracing/tracing-integrations-auto/vertex-ai-gemini (redirected from docs.arize.com/arize/...) · Fetched 2026-05-21 · WebFetch extraction
> NOTE: example below uses `arize.otel.register` (Arize hosted). For **Phoenix Cloud**, swap to `phoenix.otel.register(...)` with PHOENIX_* env vars. The instrumentor class is identical.

# Vertex AI / Gemini Auto-Instrumentation Guide

## Installation
```bash
pip install arize-otel openinference-instrumentation-google-genai google-genai
```
The `google-genai` package includes `google-auth`, so Application Default Credentials (ADC) work automatically.

## Environment Variables
```bash
gcloud auth application-default login
export ARIZE_SPACE_ID="<your-space-id>"
export ARIZE_API_KEY="<your-api-key>"
export ARIZE_PROJECT_NAME="vertexai-tracing-example"
export GOOGLE_CLOUD_PROJECT="<your-gcp-project-id>"
export GOOGLE_CLOUD_LOCATION="us-central1"  # optional; defaults to us-central1
```

## Python Setup (`instrumentation.py`)
```python
import os
from arize.otel import register
from openinference.instrumentation.google_genai import GoogleGenAIInstrumentor

tracer_provider = register(
    space_id=os.environ["ARIZE_SPACE_ID"],
    api_key=os.environ["ARIZE_API_KEY"],
    project_name=os.environ["ARIZE_PROJECT_NAME"],
)

GoogleGenAIInstrumentor().instrument(tracer_provider=tracer_provider)
```

## Key Implementation Details
- **Instrumentation must load first**: "Importing instrumentation first ensures tracing is set up before `google.genai` is imported."
- **Instrumentor class**: `GoogleGenAIInstrumentor` handles BOTH the Gemini API and Vertex AI.
- **Vertex-specific**: init the client with `vertexai=True`:
```python
from instrumentation import tracer_provider
from google import genai

client = genai.Client(vertexai=True)
```
Project and location come from env vars or explicit params.

## Spans Captured
Captures "every Vertex call — chat completions, tool calls, and token usage" with a `GenerateContent` LLM span containing the prompt, response, and token usage.

## Critical Caveats
- **Auth**: Vertex uses IAM-based auth only ("Vertex AI accepts only IAM-based auth, not API keys").
- **Legacy SDK**: deprecated `vertexai` SDK (in `google-cloud-aiplatform`) "will be removed June 24, 2026" → use the new `google-genai` SDK.
- **Instrumentor timing**: if it runs after importing `google.genai`, Vertex spans won't appear.
