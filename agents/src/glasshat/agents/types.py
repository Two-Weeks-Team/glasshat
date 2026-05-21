"""Engine data contracts (SDD).

These pydantic models flow through the pipeline: ingest -> synthesize -> plan ->
hats -> audit -> score -> report. Hat scores are on an internal 0-10 scale;
``CriterionScore`` is on the criterion's native scale; ``RunRecord.final_score``
is on the rubric's ``final_scale``. Source: ``docs/architecture.md`` §3/§6,
``docs/rubric-synthesis-spec.md``.
"""

from __future__ import annotations

from glasshat.rubric.models import SynthesizedRubric
from glasshat.shared.enums import Hat, RunMode
from pydantic import BaseModel, Field


class Chunk(BaseModel):
    """A retrievable text chunk from a deck or repo."""

    id: str
    text: str
    source: str  # e.g. "deck" | "repo"
    vector: list[float] | None = None


class RepoFacts(BaseModel):
    """Static facts extracted from a repository by the code grader."""

    url: str
    languages: dict[str, int] = Field(default_factory=dict)  # extension -> file count
    loc: int = 0
    has_tests: bool = False
    has_ci: bool = False
    readme_excerpt: str = ""
    heuristics: dict[str, object] = Field(default_factory=dict)


class EvaluationInput(BaseModel):
    """The artifact + rubric source for one evaluation."""

    rubric_source: dict[str, str]  # one of preset_id | rules_url | rules_pdf_uri | custom_yaml
    deck_text: str | None = None
    repo_url: str | None = None
    mode: RunMode = RunMode.PARTICIPANT


class PlanObject(BaseModel):
    """BluePlanner output, shown at human gate 1 (architecture §6)."""

    hats_enabled: list[Hat]
    criteria_in_scope: list[str]
    retrieval_budget: dict[str, int] = Field(default_factory=dict)
    weights: dict[str, float] = Field(default_factory=dict)
    code_grader_depth: str = "lint"


class HatAssessment(BaseModel):
    """One hat's assessment of one criterion (internal 0-10 score)."""

    hat: Hat
    criterion_id: str
    score: float = Field(ge=0.0, le=10.0)
    evidence_refs: list[str] = Field(default_factory=list)
    rationale: str = ""
    evidence_depth: float = Field(default=0.5, ge=0.0, le=1.0)


class AuditCorrection(BaseModel):
    """A calibration-driven self-correction of one hat assessment."""

    hat: Hat
    criterion_id: str
    original: float
    corrected: float
    mean_delta: float
    n: int
    reason: str = ""


class CriterionScore(BaseModel):
    """Aggregated score for one rubric criterion (native scale)."""

    criterion_id: str
    score: float
    evidence_refs: list[str] = Field(default_factory=list)
    audit: AuditCorrection | None = None


class RunRecord(BaseModel):
    """The immutable evaluation result persisted to the docstore."""

    run_id: str
    rubric: SynthesizedRubric
    scores: list[CriterionScore]
    final_score: float
    audit_corrections: list[AuditCorrection] = Field(default_factory=list)
    mode: RunMode = RunMode.PARTICIPANT
    created_at: str = ""
