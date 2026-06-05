#!/usr/bin/env python
"""Run the glasshat A2A server (AgentCard at /.well-known/agent-card.json + RPC).

OWNER-RUN, overlay-only (needs a2a-sdk + ADK a2a + uvicorn). The agent is exposed
over the A2A protocol so other agents can discover and call glasshat:

    uv run --with-requirements deploy/requirements-cloud.txt python deploy/a2a_server.py

Env: A2A_HOST (default 0.0.0.0), A2A_PORT (default 8080).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# uv-managed CPython doesn't process editable .pth — put the src layouts on the path.
_REPO = Path(__file__).resolve().parents[1]
for _pkg in (
    "packages/shared",
    "packages/rubric",
    "agents",
    "services/ingest",
    "services/code-grader",
    "services/pipeline-orchestrator",
):
    _src = str(_REPO / _pkg / "src")
    if _src not in sys.path:
        sys.path.insert(0, _src)


def main() -> int:
    import uvicorn
    from glasshat.pipeline.a2a import build_a2a_app

    host = os.environ.get("A2A_HOST", "0.0.0.0")
    port = int(os.environ.get("A2A_PORT", "8080"))
    print(f"glasshat A2A server on {host}:{port} — card at /.well-known/agent-card.json")
    uvicorn.run(build_a2a_app(host=host, port=port), host=host, port=port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
