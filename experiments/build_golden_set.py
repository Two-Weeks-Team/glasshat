"""CLI: build ``experiments/golden_rapid_agent.json`` from the Devpost crawl.

Deterministic (no randomness): all 13 Winner-badged submissions + the first 37
non-winners by software_id. Binary ``placed`` labels only — there is no rank in
the source. Re-run after the crawl changes; the output is committed.
"""

from __future__ import annotations

import json
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

from glasshat.pipeline.calibration import build_golden_from_devpost  # noqa: E402

_ROOT = Path(__file__).resolve().parents[1]
_DATA = _ROOT / "data" / "devpost-gemini3"
_OUT = Path(__file__).resolve().parent / "golden_rapid_agent.json"


def main() -> None:
    golden = build_golden_from_devpost(_DATA / "winners.json", _DATA / "submissions.json")
    _OUT.write_text(json.dumps([e.model_dump() for e in golden], indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(golden)} golden entries ({sum(e.placed for e in golden)} winners) to {_OUT}")


if __name__ == "__main__":
    main()
