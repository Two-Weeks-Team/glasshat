"""Glasshat exception hierarchy. All domain errors derive from :class:`GlasshatError`."""

from __future__ import annotations


class GlasshatError(Exception):
    """Base class for all Glasshat domain errors."""


class RubricValidationError(GlasshatError):
    """A rubric payload failed schema or semantic validation."""


class SynthesisError(GlasshatError):
    """The RubricSynthesizer could not produce a valid rubric from the source."""


class RetrievalError(GlasshatError):
    """A retrieval/embedding operation failed."""


class LlmError(GlasshatError):
    """An LLM generation/embedding call failed."""
