#!/usr/bin/env python3
"""Regenerate packages/rubric/synthesized.schema.json from the pydantic model.

Run from the repo root:
    PYTHONPATH=packages/shared/src:packages/rubric/src uv run python scripts/gen_rubric_schema.py
"""

from __future__ import annotations

import json

from glasshat.rubric.schema import SCHEMA_PATH, synthesized_schema


def main() -> None:
    text = json.dumps(synthesized_schema(), indent=2, sort_keys=True) + "\n"
    SCHEMA_PATH.write_text(text, encoding="utf-8")
    print(f"wrote {SCHEMA_PATH}")


if __name__ == "__main__":
    main()
