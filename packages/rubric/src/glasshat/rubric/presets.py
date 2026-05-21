"""Hand-curated, version-pinned rubric presets (Path A).

Each ``presets/<id>.yaml`` carries provenance frontmatter plus a ``synthesized:``
block matching :class:`~glasshat.rubric.models.SynthesizedRubric`. The loader
validates the block and back-fills the canonical ``rubric_schema_hash`` and
``weights_vector`` so a loaded preset is fully populated. Source:
``docs/rubric-synthesis-spec.md`` §4.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from glasshat.rubric.canonical import compute_schema_hash, compute_weights_vector
from glasshat.rubric.models import SynthesizedRubric

PRESETS_DIR = Path(__file__).parent / "presets"


def list_presets() -> list[str]:
    """Return the available preset ids (filenames without extension)."""
    return sorted(p.stem for p in PRESETS_DIR.glob("*.yaml"))


def load_preset(preset_id: str) -> SynthesizedRubric:
    """Load, validate, and canonicalize the named preset.

    Raises:
        KeyError: if ``preset_id`` is unknown.
    """
    path = PRESETS_DIR / f"{preset_id}.yaml"
    if not path.exists():
        raise KeyError(f"unknown preset: {preset_id!r}")
    raw: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8"))
    body: dict[str, Any] = raw["synthesized"]
    rubric = SynthesizedRubric.model_validate(body)
    rubric.weights_vector = compute_weights_vector(rubric)
    rubric.rubric_schema_hash = compute_schema_hash(rubric)
    return rubric
