"""Shared enumerations used across the engine.

All are ``str``-backed so they serialize transparently to JSON/YAML and compare
equal to their string values.
"""

from __future__ import annotations

from enum import StrEnum


class Hat(StrEnum):
    """The six de Bono thinking hats run by the evaluation panel."""

    BLUE = "blue"
    WHITE = "white"
    RED = "red"
    YELLOW = "yellow"
    BLACK = "black"
    GREEN = "green"


class RunMode(StrEnum):
    """Which viewport owns a run (Hybrid mode)."""

    JUDGE = "judge"
    PARTICIPANT = "participant"


class Aggregation(StrEnum):
    """How per-criterion scores combine into a final score."""

    WEIGHTED_SUM = "weighted_sum"
    SIMPLE_AVERAGE = "simple_average"
    TIE_BREAK_ORDERED = "tie_break_ordered"


class SourceKind(StrEnum):
    """Where a synthesized rubric was derived from."""

    PRESET = "preset"
    URL = "url"
    PDF = "pdf"
    CUSTOM = "custom"
