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
from pydantic import BaseModel, Field, field_validator


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
    """The artifact + rubric source for one evaluation.

    Untrusted at the API boundary, so the free-text deck is length-bounded and
    ``repo_url`` is constrained to ``https://github.com/...`` — the only host the
    code grader ever contacts (defense-in-depth against cost abuse / SSRF).
    """

    rubric_source: dict[str, str]  # one of preset_id | rules_url | rules_pdf_uri | custom_yaml
    deck_text: str | None = Field(default=None, max_length=20_000)
    repo_url: str | None = Field(default=None, max_length=300)
    mode: RunMode = RunMode.PARTICIPANT

    @field_validator("repo_url")
    @classmethod
    def _repo_url_must_be_github_https(cls, value: str | None) -> str | None:
        if value is None or value == "":
            return value
        if not value.startswith("https://github.com/"):
            raise ValueError("repo_url must be an https://github.com/<owner>/<repo> URL")
        return value


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
    pre_audit_final_score: float = 0.0
    audit_corrections: list[AuditCorrection] = Field(default_factory=list)
    dataset_examples_used: int = 0
    dataset_examples_added: int = 0
    mode: RunMode = RunMode.PARTICIPANT
    created_at: str = ""
