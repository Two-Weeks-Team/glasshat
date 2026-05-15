# Glasshat — Spike Tests

> Purpose: validate that the chosen tech stack (Google ADK + Arize Phoenix + Qdrant + Gemini 3) actually behaves as documented BEFORE sinking weeks into the full Phase 1 build. See `../docs/wow-moment-design.md` §7 + §12.
>
> Each spike is a small, focused script with a clear PASS/FAIL outcome. Total budget: ~14h.

## Prerequisites

- Python 3.12, uv installed (`uv --version`)
- Node 24, npm/npx (for Phoenix MCP via `@arizeai/phoenix-mcp@latest`)
- `.env` filled (per `../docs/gcp-setup.md`); GOOGLE_APPLICATION_CREDENTIALS pointing at SA key
- No Docker required (Phoenix runs in-process; Qdrant in-memory)
- No external cloud signup required (Arize AX features substituted with OSS Phoenix equivalents)

## Setup (one-time)

```bash
# from this directory
uv sync                     # installs all dependencies into .venv
uv run python -c "import phoenix; print(phoenix.__version__)"  # sanity check
```

## Spike index

| # | Spike | What it validates | External deps | Status |
|---|---|---|---|---|
| A | `01_spike_a_phoenix_mcp_smoke.py` | Phoenix MCP server (npx) responds to `get-spans` / `list-projects` with structured data | Phoenix in-process · Node | TBD |
| B | `02_spike_b_adk_loop.py` | ADK `LoopAgent` runs sub-agents with state sharing + `escalate` termination + max_iter cap | none | TBD |
| C | `03_spike_c_adk_mcptoolset.py` | ADK `LlmAgent` with `MCPToolset(StdioServerParameters(npx@phoenix-mcp))` discovers tools + invokes them | Phoenix in-process · Node · Vertex AI | TBD |
| D | `04_spike_d_calibration_toy.py` | Synthetic dataset → calibration policy improves held-out MAE ≥15% | none | TBD |
| E | `05_spike_e_sse_animation/` | Python FastAPI streams 6 SSE events @ 800ms gaps → Next.js consumer animates smoothly | none | TBD |
| F | `06_spike_f_phoenix_online_evals.py` | `phoenix.evals.run_evals` runs LLM-as-judge on spans → annotations attached, MCP-queryable | Phoenix in-process · Vertex AI | TBD |
| G | `07_spike_g_phoenix_annotations.py` | Write annotation via SDK → read via MCP get-span-annotations round-trip <2s | Phoenix in-process · Node | TBD |

## How to run

```bash
# Individual spikes
uv run python 01_spike_a_phoenix_mcp_smoke.py
uv run python 02_spike_b_adk_loop.py
# ... etc

# Result summary (after all run)
uv run python summarize_spike_results.py    # writes spike-results.json
```

Each spike script prints a clear `[PASS]` or `[FAIL: <reason>]` line at the end and exits with corresponding code.

## Output

Each spike writes a JSON result file to `results/<spike-name>.json`. The summary script aggregates and produces `../docs/spike-results.md` (decision document).

## Notes

- These are **spikes, not production code**. Brevity > completeness. Error handling minimal.
- Phoenix in-process mode (`px.launch_app()`) starts a local server on port 6006 — same port as PHOENIX_PORT in `.env`.
- Qdrant uses `QdrantClient(":memory:")` for fast in-process tests.
- Vertex AI calls use the existing SA key in GOOGLE_APPLICATION_CREDENTIALS.
- The 524 Gemini 3 corpus is NOT seeded in spike phase — that's Phase 1.12.
