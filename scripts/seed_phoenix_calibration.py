#!/usr/bin/env python3
"""Seed the ``glasshat-calibration`` Phoenix dataset with the spike-D YELLOW
optimism over-confidence prior, so the live ``PhoenixMcpConsultant`` (read over
MCP ``get-dataset-examples``) reproduces the deterministic table prior.

Each example is ``input={hat,criterion,bucket}`` + ``output={delta}`` — exactly
the shape ``PhoenixMcpConsultant._parse_examples`` reads. For every preset
criterion and evidence bucket we emit ``n`` examples at the measured mean_delta
(low 1.45/n7, mid 0.80/n10, high 0.31/n16), so the consultant's mean == the table
prior's mean and ``n`` matches.

Run:
  PHOENIX_URL=https://glasshat-phoenix-...run.app \
    uv run --extra phoenix python scripts/seed_phoenix_calibration.py
"""

from __future__ import annotations

import os

# spike-D held-out YELLOW prior (mirror of engine._YELLOW_DELTA_BY_BUCKET).
_YELLOW_DELTA_BY_BUCKET: dict[str, tuple[float, int]] = {
    "low": (1.45, 7),
    "mid": (0.80, 10),
    "high": (0.31, 16),
}
_DATASET = "glasshat-calibration"


def main() -> None:
    import pathlib
    import sys

    # uv's editable install of the PEP420 glasshat namespace isn't always picked up
    # under `--extra phoenix`; add every workspace src dir so the namespace merges.
    _root = pathlib.Path(__file__).resolve().parents[1]
    for _p in (
        "packages/rubric/src",
        "packages/shared/src",
        "agents/src",
        "services/code-grader/src",
        "services/ingest/src",
        "services/pipeline-orchestrator/src",
    ):
        _abs = str(_root / _p)
        if _abs not in sys.path:
            sys.path.insert(0, _abs)

    from glasshat.rubric.presets import list_presets, load_preset
    from phoenix.client import Client

    base_url = os.environ.get("PHOENIX_URL") or os.environ.get("PHOENIX_COLLECTOR_ENDPOINT")
    if not base_url:
        raise SystemExit("PHOENIX_URL (or PHOENIX_COLLECTOR_ENDPOINT) must be set")
    api_key = os.environ.get("PHOENIX_API_KEY") or None

    inputs: list[dict[str, object]] = []
    outputs: list[dict[str, object]] = []
    seen: set[str] = set()
    for preset_id in list_presets():
        for crit in load_preset(preset_id).criteria:
            if crit.id in seen:  # one set of anchors per criterion id (n stays exact)
                continue
            seen.add(crit.id)
            for bucket, (mean_delta, n) in _YELLOW_DELTA_BY_BUCKET.items():
                for _ in range(n):
                    inputs.append({"hat": "yellow", "criterion": crit.id, "bucket": bucket})
                    outputs.append({"delta": mean_delta})

    client = Client(base_url=base_url, api_key=api_key)
    ds = client.datasets.create_dataset(
        name=_DATASET,
        inputs=inputs,
        outputs=outputs,
        dataset_description=(
            "spike-D YELLOW optimism over-confidence prior — delta by "
            "(hat, criterion, evidence-bucket). Read live by PhoenixMcpConsultant."
        ),
    )
    print(f"created dataset '{_DATASET}' with {len(inputs)} examples")
    print(f"  criteria seeded: {sorted(seen)}")
    print(f"  dataset: {ds}")


if __name__ == "__main__":
    main()
