import pytest
from glasshat.agents.bmad_scorer import score
from glasshat.agents.types import AuditCorrection, HatAssessment
from glasshat.rubric.models import SynthesizedRubric
from glasshat.rubric.presets import load_preset
from glasshat.shared.enums import Hat


def _assessments(rubric: SynthesizedRubric, overrides: dict[str, float]) -> list[HatAssessment]:
    return [
        HatAssessment(
            hat=h, criterion_id=c.id, score=overrides.get(c.id, 5.0), evidence_refs=[f"{c.id}-e"]
        )
        for c in rubric.criteria
        for h in Hat
    ]


def test_score_rescales_internal_to_native_scale() -> None:
    r = load_preset("rapid-agent")  # scale 5
    scores = score(r, _assessments(r, {}), [])
    assert len(scores) == 4
    tech = next(s for s in scores if s.criterion_id == "tech-implementation")
    assert tech.score == pytest.approx(3.0)  # internal 5.0 -> 1 + 5/10*4
    assert tech.audit is None
    assert tech.evidence_refs == ["tech-implementation-e"]


def test_score_uses_corrected_value_and_attaches_audit() -> None:
    r = load_preset("rapid-agent")
    assessments = _assessments(r, {"tech-implementation": 9.0})
    correction = AuditCorrection(
        hat=Hat.YELLOW,
        criterion_id="tech-implementation",
        original=9.0,
        corrected=7.6,
        mean_delta=1.74,
        n=14,
    )
    baseline = next(s for s in score(r, assessments, []) if s.criterion_id == "tech-implementation")
    corrected = next(
        s for s in score(r, assessments, [correction]) if s.criterion_id == "tech-implementation"
    )
    assert corrected.score < baseline.score  # the correction pulled the score down
    assert corrected.audit is not None and corrected.audit.corrected == 7.6
