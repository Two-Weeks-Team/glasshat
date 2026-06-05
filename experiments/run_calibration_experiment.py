"""CLI: run the offline hit@k calibration experiment.

Scores every golden entry on the configured backend (mock by default) and writes
``experiments/calibration_result.json`` — the before/after hit@k the /judge page
renders, with its provenance caveat. Runs without prod. With ``LLM_BACKEND=vertex``
set in the environment this produces the live figure (user-gated).
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

# uv-managed CPython does not process the editable .pth files, so put the src
# layouts on the path explicitly (same dirs as the pytest `pythonpath`).
_REPO = Path(__file__).resolve().parents[1]
for _pkg in (
    "packages/shared",
    "packages/rubric",
    "agents",
    "services/ingest",
    "services/code-grader",
    "services/pipeline-orchestrator",
    "apps/api",
):
    sys.path.insert(0, str(_REPO / _pkg / "src"))

from glasshat.pipeline.calibration import load_golden, run_calibration  # noqa: E402

_HERE = Path(__file__).resolve().parent
_GOLDEN = _HERE / "golden_rapid_agent.json"
_OUT = _HERE / "calibration_result.json"
# The /judge page imports this copy at build time (single generated source).
_WEB_OUT = _REPO / "apps" / "web" / "lib" / "calibration-result.json"


def main() -> None:
    golden = load_golden(_GOLDEN)
    backend = "vertex" if os.environ.get("LLM_BACKEND") == "vertex" else "mock"
    result = asyncio.run(run_calibration(golden, backend=backend))
    payload = result.model_dump_json(indent=2) + "\n"
    _OUT.write_text(payload, encoding="utf-8")
    _WEB_OUT.write_text(payload, encoding="utf-8")
    print(payload)


if __name__ == "__main__":
    main()
