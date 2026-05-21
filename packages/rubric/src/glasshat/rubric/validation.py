"""Validation pipeline for synthesized rubrics (``docs/rubric-synthesis-spec.md`` §7).

Hard structural rules (schema, descriptor coverage, weight totals, BMAD coverage,
tie-break references) are enforced at construction by
:class:`~glasshat.rubric.models.SynthesizedRubric`. This module adds the *soft*
checks that produce warnings rather than rejections — chiefly source-clause
traceability — and the custom-YAML entry point used by Path D.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from glasshat.rubric.models import SynthesizedRubric
from glasshat.shared.errors import RubricValidationError
from pydantic import ValidationError


@dataclass(frozen=True)
class RubricWarning:
    """A non-fatal advisory about a synthesized rubric."""

    code: str
    message: str


def validate_rubric(
    rubric: SynthesizedRubric, source_text: str | None = None
) -> list[RubricWarning]:
    """Run soft checks; return warnings (empty list = clean).

    When ``source_text`` is provided, each criterion's ``source_excerpt`` must
    appear verbatim in it (traceability). Low synthesis confidence is surfaced too.
    """
    warnings: list[RubricWarning] = []

    if source_text is not None:
        for c in rubric.criteria:
            excerpt = c.source_excerpt.strip()
            if excerpt and excerpt not in source_text:
                warnings.append(
                    RubricWarning(
                        code="traceability",
                        message=(
                            f"criterion '{c.id}': source_excerpt not found verbatim in "
                            f"source text (traceability check failed)"
                        ),
                    )
                )

    if rubric.confidence < 0.5:
        warnings.append(
            RubricWarning(
                code="low_confidence",
                message=f"synthesis confidence {rubric.confidence:.2f} is below 0.5",
            )
        )

    return warnings


def validate_custom_yaml(body: dict[str, Any]) -> SynthesizedRubric:
    """Validate a user-supplied rubric body (Path D). Raises on invalid input."""
    try:
        return SynthesizedRubric.model_validate(body)
    except ValidationError as exc:
        raise RubricValidationError(str(exc)) from exc
