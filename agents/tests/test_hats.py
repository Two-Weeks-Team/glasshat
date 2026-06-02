import asyncio
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from glasshat.agents.blue_planner import plan
from glasshat.agents.hats import run_hat, run_panel
from glasshat.agents.types import EvaluationInput
from glasshat.rubric.presets import load_preset
from glasshat.shared.enums import Hat
from glasshat.shared.llm import MockLlmClient
from glasshat.shared.retrieval import Document, HybridIndex
from glasshat.shared.tracing import NoOpTracer


class _RecordingSpan:
    def __init__(self, sink: list[tuple[str, Any]]) -> None:
        self._sink = sink

    def set_attr(self, key: str, value: Any) -> None:
        self._sink.append((key, value))


class _RecordingTracer:
    """Tracer capturing set_attr calls so tests can assert span attributes."""

    def __init__(self) -> None:
        self.attrs: list[tuple[str, Any]] = []

    @contextmanager
    def span(self, name: str, **a: Any) -> Iterator[_RecordingSpan]:
        yield _RecordingSpan(self.attrs)

    def set_attr(self, key: str, value: Any) -> None:
        self.attrs.append((key, value))


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


def test_run_hat_flags_score_parse_failure_on_span() -> None:
    """Mock LLM emits no `SCORE:` → the hash fallback fires and the span is flagged."""
    tracer = _RecordingTracer()
    r = load_preset("rapid-agent")
    inp = EvaluationInput(rubric_source={"preset_id": "rapid-agent"})
    asyncio.run(run_hat(Hat.WHITE, r, inp, MockLlmClient(embedding_dim=8), _indexed(), tracer))
    flags = [v for k, v in tracer.attrs if k == "glasshat.score_parse_failed"]
    assert flags and all(v is True for v in flags)


def test_run_hat_no_parse_failure_with_real_score() -> None:
    class ScoringLlm(MockLlmClient):
        async def generate(self, prompt: str, *, tier: str = "flash", **kw: object) -> str:
            return "SCORE: 7.0\nRATIONALE: ok"

    tracer = _RecordingTracer()
    r = load_preset("rapid-agent")
    inp = EvaluationInput(rubric_source={"preset_id": "rapid-agent"})
    asyncio.run(run_hat(Hat.WHITE, r, inp, ScoringLlm(embedding_dim=8), _indexed(), tracer))
    flags = [v for k, v in tracer.attrs if k == "glasshat.score_parse_failed"]
    assert flags and all(v is False for v in flags)


def test_run_panel_covers_all_hat_criterion_pairs() -> None:
    r = load_preset("rapid-agent")  # 4 criteria
    inp = EvaluationInput(rubric_source={"preset_id": "rapid-agent"}, deck_text="we built X")
    p = plan(r, inp)
    assessments = asyncio.run(
        run_panel(p, r, inp, MockLlmClient(embedding_dim=8), _indexed(), NoOpTracer())
    )
    pairs = {(a.hat, a.criterion_id) for a in assessments}
    assert len(pairs) == 6 * 4


class _CountingEmbedLlm(MockLlmClient):
    """Records every text passed to embed() so we can assert label dedupe."""

    def __init__(self, embedding_dim: int = 8) -> None:
        super().__init__(embedding_dim=embedding_dim)
        self.embed_batches: list[list[str]] = []

    async def embed(self, texts: object) -> list[list[float]]:
        self.embed_batches.append(list(texts))  # type: ignore[arg-type]
        return await super().embed(texts)  # type: ignore[arg-type]


def test_run_panel_embeds_each_criterion_label_once_across_all_hats() -> None:
    """Embeddings depend only on the label, not the hat — the panel must embed
    the 4 unique criterion labels once, not 4 × 6 = 24 times."""
    r = load_preset("rapid-agent")  # 4 criteria
    inp = EvaluationInput(rubric_source={"preset_id": "rapid-agent"}, deck_text="we built X")
    p = plan(r, inp)  # 6 hats enabled
    llm = _CountingEmbedLlm(embedding_dim=8)
    asyncio.run(run_panel(p, r, inp, llm, _indexed(), NoOpTracer()))

    # All criterion labels embedded in a single batch; total embedded texts == 4.
    embedded = [t for batch in llm.embed_batches for t in batch]
    labels = [c.label for c in r.criteria]
    assert sorted(embedded) == sorted(labels)
    assert len(embedded) == 4  # not 24


def test_run_hat_still_embeds_on_demand_without_shared_vectors() -> None:
    # Direct run_hat call (no label_vectors) embeds each criterion label itself.
    r = load_preset("rapid-agent")
    inp = EvaluationInput(rubric_source={"preset_id": "rapid-agent"}, deck_text="x")
    llm = _CountingEmbedLlm(embedding_dim=8)
    asyncio.run(run_hat(Hat.WHITE, r, inp, llm, _indexed(), NoOpTracer()))
    embedded = [t for batch in llm.embed_batches for t in batch]
    assert sorted(embedded) == sorted(c.label for c in r.criteria)
