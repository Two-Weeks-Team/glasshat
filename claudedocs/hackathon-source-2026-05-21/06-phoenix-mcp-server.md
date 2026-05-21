# Phoenix MCP Server Guide — capture

> Source: https://arize.com/docs/phoenix/integrations/phoenix-mcp-server · Fetched 2026-05-21 · WebFetch extraction

# Phoenix MCP Server Guide

## Overview
The Phoenix MCP Server (`@arizeai/phoenix-mcp`) connects AI assistants to Phoenix instances for managing operational and analytical workflows.

## Exposed Capabilities
- **Projects, Traces, and Spans**: explore recent traces, inspect spans, analyze annotations
- **Sessions**: review conversation flows and session annotations
- **Annotation Configs**: inspect available labeling and scoring configs
- **Prompts Management**: create, list, update, iterate on prompts
- **Datasets**: explore datasets and synthesize new examples
- **Experiments**: pull experiment results and visualize with LLM help

> The doc does not enumerate exact tool names (e.g. `get-experiment-by-id`, `get-span-annotations`, `add-dataset-examples`, `list-prompts`) — confirm against the phoenix-mcp repo when wiring.

## Installation & Runtime
- **Package**: `@arizeai/phoenix-mcp@latest`
- **Transport**: npx command (stdio-based)
- **Command**:
```
npx -y @arizeai/phoenix-mcp@latest --baseUrl <url> --apiKey <key>
```

## Required Configuration
1. **`--baseUrl`**: Phoenix endpoint (e.g. `https://app.phoenix.arize.com` for Phoenix Cloud, or self-hosted URL)
2. **`--apiKey`**: Phoenix API key

## Client Connection Methods
### Claude Code CLI
```bash
claude mcp add phoenix -- npx -y @arizeai/phoenix-mcp@latest \
  --baseUrl https://my-phoenix.com \
  --apiKey your-api-key
```
### Claude Desktop / Cursor (MCP config JSON)
```json
{
  "mcpServers": {
    "phoenix": {
      "command": "npx",
      "args": ["-y", "@arizeai/phoenix-mcp@latest",
               "--baseUrl", "https://my-phoenix.com",
               "--apiKey", "your-api-key"]
    }
  }
}
```
> For ADK: wire via `MCPToolset` + `StdioServerParameters` with the same npx command (see local spike 03_spike_c_adk_mcptoolset.py).

## Example Queries
- "Show me the latest traces in my default Phoenix project"
- "What prompts do I have in Phoenix?"
- "Create a new prompt in Phoenix that classifies user intent"

## Notes
Open-source on GitHub; no explicit version requirements stated.
