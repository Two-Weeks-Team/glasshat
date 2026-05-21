"""Canonicalization → ``rubric_schema_hash`` + ``weights_vector``.

Two rubrics that are *structurally* the same (same criteria, weights, scales,
aggregation, tie-break order) must produce the same hash regardless of criterion
ordering or volatile fields (rubric_id, fetched_at, confidence, excerpts). This
hash is the exact-match key for past-eval anchor retrieval; the weights vector
(alphabetical by criterion id) is the cosine-similarity key. Source:
``docs/rubric-synthesis-spec.md`` §3/§5/§8.
"""

from __future__ import annotations

from typing import Any

from glasshat.rubric.models import SynthesizedRubric
from glasshat.shared.ids import canonical_json, sha256_hex


def compute_weights_vector(rubric: SynthesizedRubric) -> list[float]:
    """Weights ordered alphabetically by criterion id (null → 0.0)."""
    return [c.weight or 0.0 for c in sorted(rubric.criteria, key=lambda c: c.id)]


def canonicalize(rubric: SynthesizedRubric) -> dict[str, Any]:
    """Return only the structurally significant fields, in a stable shape."""
    return {
        "schema_version": rubric.schema_version,
        "aggregation": str(rubric.scoring_rule.aggregation),
        "final_scale": rubric.scoring_rule.final_scale,
        "criteria": [
            {
                "id": c.id,
                "weight": c.weight,
                "scale": c.scale,
                "bmad_mapping": sorted(c.bmad_mapping),
            }
            for c in sorted(rubric.criteria, key=lambda c: c.id)
        ],
        "tie_breakers": [
            {"order": tb.order, "criterion_id": tb.criterion_id}
            for tb in sorted(rubric.tie_breakers, key=lambda tb: tb.order)
        ],
    }


def compute_schema_hash(rubric: SynthesizedRubric) -> str:
    """SHA-256 of the canonicalized rubric (hex)."""
    return sha256_hex(canonical_json(canonicalize(rubric)))
