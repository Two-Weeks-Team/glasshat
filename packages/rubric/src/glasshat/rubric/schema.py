"""JSON Schema emission for :class:`~glasshat.rubric.models.SynthesizedRubric`.

The pydantic model is the source of truth; ``packages/rubric/synthesized.schema.json``
is the generated cross-language contract (consumed by the TypeScript frontend).
CI guards against drift via :func:`schema_matches_disk`. Regenerate with
``scripts/gen_rubric_schema.py``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from glasshat.rubric.models import SynthesizedRubric

# packages/rubric/src/glasshat/rubric/schema.py -> packages/rubric/synthesized.schema.json
SCHEMA_PATH = Path(__file__).resolve().parents[3] / "synthesized.schema.json"


def synthesized_schema() -> dict[str, Any]:
    """Return the JSON Schema for :class:`SynthesizedRubric`."""
    return SynthesizedRubric.model_json_schema()


def schema_matches_disk() -> bool:
    """True iff the committed schema file matches the model-generated schema."""
    if not SCHEMA_PATH.exists():
        return False
    disk = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return bool(disk == synthesized_schema())
