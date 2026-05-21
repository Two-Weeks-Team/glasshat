# Arize Track Resources — capture

> Source: https://rapid-agent.devpost.com/details/arize-resources · Fetched 2026-05-21 · WebFetch extraction

# Arize Track Resources - Google Cloud Rapid Agent Hackathon

## Deadline
**June 11, 2026 @ 2:00pm PDT**

## Track Requirements
The Arize track mandates "a code-owned agent runtime — Gemini CLI, Gemini Enterprise Agent Platform SDK, Google ADK, Agent Runtime, or Cloud Run." Visual Agent Builder alone is insufficient. Direct code instrumentation is required.

## Evaluation Criteria
Submissions are assessed on: technical implementation, meaningful use of tracing and MCP, quality of the agent's self-improvement loop, and overall impact.

## Required Technologies & Setup Steps
1. **Instrumentation**: Use OpenInference auto-instrumentors
2. **Tracing**: Send traces to Phoenix Cloud or self-hosted Phoenix
3. **MCP Integration**: Configure Phoenix MCP server for runtime introspection
4. **Evaluations**: Run LLM-as-a-Judge or code evals on traces
5. **Enhancement**: Agents improving over time earn bonus consideration

## Key Resources & URLs

| Resource | URL |
|----------|-----|
| Phoenix Cloud (free tier) | https://app.phoenix.arize.com |
| Phoenix GitHub (open-source) | https://github.com/Arize-ai/phoenix |
| Phoenix Documentation | https://arize.com/docs/phoenix |
| Phoenix MCP Server Guide | https://arize.com/docs/phoenix/integrations/phoenix-mcp-server |
| OpenInference GitHub | https://github.com/Arize-ai/openinference |
| Gemini Hackathon Example | https://github.com/Arize-ai/gemini-hackathon |
| Agent Platform Tracing Guide | https://docs.arize.com/arize/llm-tracing/tracing-integrations-auto/vertex-ai-gemini |
| LLM-as-a-Judge Evals | https://arize.com/docs/phoenix/evaluation/llm-evals |
| Hackathon Discord | https://discord.gg/7Dqk5ebCD4 |

## Instrumentor Packages
- `openinference-instrumentation-google-adk` (Google ADK agents)
- `openinference-instrumentation-vertexai` (Gemini Enterprise Agent Platform SDK)
- `openinference-instrumentation-google-genai` (unified google-genai SDK)

## Technical Contact
**Richard Young** — ryoung@arize.com (technical questions during hackathon)

## Participants
**8,702** registered participants
