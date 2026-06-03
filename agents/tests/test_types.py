import pytest
from glasshat.agents.types import (
    AuditCorrection,
    Chunk,
    CriterionScore,
    EvaluationInput,
    HatAssessment,
    PlanObject,
    RepoFacts,
    RunRecord,
)
from glasshat.rubric.presets import load_preset
from glasshat.shared.enums import Hat, RunMode
from pydantic import ValidationError


def test_chunk() -> None:
    c = Chunk(id="c1", text="hello", source="deck", vector=[0.1, 0.2])
    assert c.id == "c1" and c.source == "deck"


def test_repo_facts_defaults() -> None:
    f = RepoFacts(url="https://github.com/x/y")
    assert f.has_tests is False and f.languages == {} and f.loc == 0


def test_evaluation_input() -> None:
    inp = EvaluationInput(
        rubric_source={"preset_id": "rapid-agent"},
        deck_text="pitch",
        repo_url="https://github.com/x/y",
        mode=RunMode.PARTICIPANT,
    )
    assert inp.mode == RunMode.PARTICIPANT


def test_evaluation_input_rejects_oversized_deck() -> None:
    with pytest.raises(ValueError):
        EvaluationInput(rubric_source={"preset_id": "rapid-agent"}, deck_text="x" * 20_001)


def test_evaluation_input_rejects_non_github_repo_url() -> None:
    for bad in (
        "https://gitlab.com/x/y",
        "http://github.com/x/y",  # not https
        "https://evil.example.com/x/y",
        "ftp://github.com/x/y",
        # The Pydantic boundary uses the SAME canonical parser as the SSRF gate
        # (M3), so these — which a loose `startswith("https://github.com/")`
        # check would have waved through — are now rejected at input:
        "https://github.com/onlyowner",  # no repo segment
        "https://github.com/x/y/extra/path",  # extra path segments
        "https://github.com/x/y?a=b",  # trailing query
        "https://github.com/x/y#frag",  # trailing fragment
    ):
        with pytest.raises(ValueError):
            EvaluationInput(rubric_source={"preset_id": "rapid-agent"}, repo_url=bad)


def test_evaluation_input_allows_empty_and_valid_repo_url() -> None:
    assert (
        EvaluationInput(rubric_source={"preset_id": "rapid-agent"}, repo_url=None).repo_url is None
    )
    ok = EvaluationInput(
        rubric_source={"preset_id": "rapid-agent"}, repo_url="https://github.com/acme/widget"
    )
    assert ok.repo_url == "https://github.com/acme/widget"


def test_plan_object() -> None:
    p = PlanObject(
        hats_enabled=[Hat.WHITE, Hat.BLACK],
        criteria_in_scope=["tech-implementation"],
        retrieval_budget={"pitch_chunks": 5},
        weights={"tech-implementation": 0.25},
        code_grader_depth="lint",
    )
    assert Hat.WHITE in p.hats_enabled


def test_hat_assessment_score_and_depth_ranges() -> None:
    HatAssessment(
        hat=Hat.YELLOW,
        criterion_id="x",
        score=9.0,
        evidence_refs=["c1"],
        rationale="r",
        evidence_depth=0.3,
    )
    with pytest.raises(ValidationError):
        HatAssessment(hat=Hat.YELLOW, criterion_id="x", score=11.0, rationale="r")
    with pytest.raises(ValidationError):
        HatAssessment(
            hat=Hat.YELLOW, criterion_id="x", score=5.0, rationale="r", evidence_depth=1.5
        )


def test_audit_correction_and_criterion_score() -> None:
    ac = AuditCorrection(
        hat=Hat.YELLOW,
        criterion_id="x",
        original=9.0,
        corrected=7.6,
        mean_delta=1.7,
        n=14,
        reason="over-confident low-evidence",
    )
    cs = CriterionScore(criterion_id="x", score=3.0, evidence_refs=["c1"], audit=ac)
    assert cs.audit is not None and cs.audit.corrected == 7.6


def test_run_record() -> None:
    rubric = load_preset("rapid-agent")
    rr = RunRecord(
        run_id="r1",
        rubric=rubric,
        scores=[CriterionScore(criterion_id="tech-implementation", score=4.0)],
        final_score=80.0,
        audit_corrections=[],
        mode=RunMode.JUDGE,
        created_at="2026-05-21T00:00:00Z",
    )
    assert rr.run_id == "r1" and rr.rubric.source.identifier == "rapid-agent"
