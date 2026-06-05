#!/usr/bin/env python
"""Run the glasshat hit@13 experiment and (with creds) push it to Arize AX.

Offline (always): scores the golden set on the deterministic mock backend, reports
hit@13 pre/post-audit + the prompt-injection evaluator counts.

Live (when ARIZE_SPACE_ID + ARIZE_API_KEY are set): creates a Dataset + runs an
Experiment + registers the injection code-evaluator in Arize AX. Run it in the
cloud overlay so the arize SDK is available:

    ARIZE_SPACE_ID=… ARIZE_API_KEY=… LLM_BACKEND=gemini-enterprise \\
    uv run --with-requirements deploy/requirements-cloud.txt \\
        python experiments/run_arize_experiment.py
"""

from __future__ import annotations

import json
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

import asyncio  # noqa: E402

from glasshat.pipeline.arize_experiment import (  # noqa: E402
    EXPERIMENT_NAME,
    build_rows,
    load_or_build_golden,
    push_to_arize,
    summarize,
)

_DATA = _REPO / "data" / "devpost-gemini3"
_GOLDEN = _REPO / "experiments" / "golden_rapid_agent.json"


def main() -> int:
    # The real-Gemini backend gives the live figure; mock is the illustrative default.
    backend = "gemini" if os.environ.get("LLM_BACKEND", "").startswith("gemini") else "mock"
    golden = load_or_build_golden(_DATA, _GOLDEN)
    rows = asyncio.run(build_rows(golden))

    space_id = os.environ.get("ARIZE_SPACE_ID")
    api_key = os.environ.get("ARIZE_API_KEY")
    pushed_ids: dict[str, str] = {}
    if space_id and api_key:
        # Backend-suffixed experiment name so the mock and live runs don't collide.
        print(f"Arize creds present → pushing Dataset + Experiment (backend={backend})…")
        pushed_ids = push_to_arize(
            rows,
            space_id=space_id,
            api_key=api_key,
            experiment_name=f"{EXPERIMENT_NAME}-{backend}",
        )
    else:
        print(
            "ARIZE_SPACE_ID / ARIZE_API_KEY not set → running OFFLINE only "
            "(no AX upload). Set both to push the Dataset + Experiment to Arize AX."
        )

    summary = summarize(rows, backend=backend, pushed=bool(pushed_ids))
    print(json.dumps(summary.model_dump(), indent=2))
    if pushed_ids:
        print("Arize AX resources:", json.dumps(pushed_ids, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
