# Arize gemini-hackathon Starter Kit — capture

> Source: https://github.com/Arize-ai/gemini-hackathon · Fetched 2026-05-21 · WebFetch extraction of README

# Gemini Hackathon Starter Kit: Complete Setup Guide

## Repository Purpose
Arize's official starter application for the Gemini hackathon, combining a Google ADK agent with OpenInference instrumentation and Phoenix Cloud tracing for observable AI development.

## Directory Structure
```
gemini-hackathon/
├── .gemini/              # Phoenix MCP + docs config
├── agent/
│   ├── main.py           # One-shot CLI with tracing
│   ├── instrumentation.py # Phoenix OTEL setup
│   └── shopping_demo/    # ADK agent, prompts, tools
├── .env.example          # Environment template
├── Makefile              # Build automation
├── pyproject.toml        # Python dependencies
└── README.md
```

## Instrumentation & Tracing
**Phoenix Integration**: Uses `phoenix.otel.register(..., auto_instrument=True)` for automatic span capture of LLM and tool calls.

`instrumentation.py` initializes Phoenix tracing before agent execution, capturing:
- LLM invocations (Gemini API calls)
- Tool executions (search/click operations)
- Full request-response chains

**Environment Variables**:
- `PHOENIX_API_KEY`: Cloud authentication
- `PHOENIX_COLLECTOR_ENDPOINT`: Hostname with `/s/...` path
- `PHOENIX_PROJECT_NAME`: Defaults to `gemini-hackathon`
- `GOOGLE_API_KEY`: Gemini authentication (or Vertex via `gcloud auth`)

## Running the Agent
**Quickstart**:
```bash
make run MESSAGE='Find a floral dress in size M'
```
**ADK CLI alternative**:
```bash
make run-adk
```
Both automatically load `.env` and initialize Phoenix tracing.

## Phoenix MCP Server (Gemini CLI)
`.gemini/settings.json` configures the Phoenix MCP server inside Gemini CLI, enabling queries against your Phoenix workspace (traces, sessions, experiments, prompts).

**Setup**:
1. Configure `@arizeai/phoenix-mcp@latest` with `--baseUrl` (your Phoenix hostname) and `--apiKey`
2. Export `PHOENIX_API_KEY` in the shell
3. Example: _"Show me the last 3 traces in my gemini-hackathon project"_

## Key Dependencies
- **Language**: Python 3.10–3.12
- **Package Manager**: `uv`
- **Primary Libraries**: Google ADK, OpenInference, Phoenix SDK
- Dependencies in `pyproject.toml`, lock file `uv.lock`

## Credits & License
Agent structure adapted from **Google ADK Samples** — personalized-shopping sample. **License: Apache-2.0**
