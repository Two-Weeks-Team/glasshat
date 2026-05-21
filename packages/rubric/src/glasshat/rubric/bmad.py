"""BMAD evaluation vocabulary — the primitive super-set.

Every synthesized rubric criterion maps to one or more of these 17 primitives
(``bmad_mapping``). The mapping is what lets Glasshat compare scores across
different rubrics: criteria differ per evaluator, but they decompose into a
shared vocabulary. Source: ``docs/rubric-synthesis-spec.md`` §5 item 2.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Final

BMAD_VOCABULARY: Final[MappingProxyType[str, str]] = MappingProxyType(
    {
        # A — idea / market
        "A1": "problem clarity",
        "A2": "target users",
        "A3": "differentiation",
        "A4": "market impact",
        # B — architecture
        "B1": "stack fit",
        "B2": "system design",
        "B3": "scalability",
        "B4": "feasibility",
        # C — implementation
        "C1": "implementation completeness",
        "C2": "code quality",
        "C3": "testing",
        "C4": "docs",
        "C5": "reproducibility",
        # D — presentation
        "D1": "demo clarity",
        "D2": "storytelling",
        "D3": "visual polish",
        "D4": "timing",
    }
)


def is_valid_primitive(code: str) -> bool:
    """Return True iff ``code`` is a known BMAD primitive (case-sensitive)."""
    return code in BMAD_VOCABULARY
