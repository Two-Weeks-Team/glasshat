import asyncio

from glasshat.agents.blue_planner import plan
from glasshat.agents.hats import run_hat, run_panel
from glasshat.agents.types import EvaluationInput
from glasshat.rubric.presets import load_preset
from glasshat.shared.enums import Hat
from glasshat.shared.llm import MockLlmClient
from glasshat.shared.retrieval import Document, HybridIndex
from glasshat.shared.tracing import NoOpTracer


def _indexed() -> HybridIndex:
    idx = HybridIndex()
    idx.index(
        [
            Document(id="c1", text="we built a custom multi-agent architecture in python"),
            Document(id="c2", text="the design is clean and the demo is smooth"),
        ]
    )
    return idx


def test_run_hat_returns_one_assessment_per_criterion() -> None:
    r = load_preset("rapid-agent")
    inp = EvaluationInput(rubric_source={"preset_id": "rapid-agent"}, deck_text="we built X")
    out = asyncio.run(
        run_hat(Hat.WHITE, r, inp, MockLlmClient(embedding_dim=8), _indexed(), NoOpTracer())
    )
    assert {a.criterion_id for a in out} == {c.id for c in r.criteria}
    assert all(a.hat == Hat.WHITE for a in out)
    assert all(0.0 <= a.score <= 10.0 for a in out)


def test_run_hat_parses_explicit_score() -> None:
    class ScoringLlm(MockLlmClient):
        async def generate(self, prompt: str, *, tier: str = "flash", **kw: object) -> str:
            return "SCORE: 8.5\nRATIONALE: solid engineering"

    r = load_preset("rapid-agent")
    inp = EvaluationInput(rubric_source={"preset_id": "rapid-agent"})
    out = asyncio.run(
        run_hat(Hat.YELLOW, r, inp, ScoringLlm(embedding_dim=8), _indexed(), NoOpTracer())
    )
    assert all(a.score == 8.5 for a in out)


def test_run_hat_score_is_deterministic() -> None:
    r = load_preset("rapid-agent")
    inp = EvaluationInput(rubric_source={"preset_id": "rapid-agent"})
    a = asyncio.run(
        run_hat(Hat.RED, r, inp, MockLlmClient(embedding_dim=8), _indexed(), NoOpTracer())
    )
    b = asyncio.run(
        run_hat(Hat.RED, r, inp, MockLlmClient(embedding_dim=8), _indexed(), NoOpTracer())
    )
    assert [x.score for x in a] == [x.score for x in b]


def test_run_panel_covers_all_hat_criterion_pairs() -> None:
    r = load_preset("rapid-agent")  # 4 criteria
    inp = EvaluationInput(rubric_source={"preset_id": "rapid-agent"}, deck_text="we built X")
    p = plan(r, inp)
    assessments = asyncio.run(
        run_panel(p, r, inp, MockLlmClient(embedding_dim=8), _indexed(), NoOpTracer())
    )
    pairs = {(a.hat, a.criterion_id) for a in assessments}
    assert len(pairs) == 6 * 4
