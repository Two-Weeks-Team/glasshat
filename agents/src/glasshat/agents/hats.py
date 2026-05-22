"""Six-hat evaluation panel.

Each hat assesses every in-scope criterion: it retrieves evidence (in-code hybrid
search), prompts the LLM with its persona, and produces a 0-10 ``HatAssessment``.
Real Gemini returns an explicit ``SCORE: <n>``; the deterministic mock backend
yields a stable hash-derived score so the whole panel runs in CI. Every
assessment opens a ``glasshat.*``-attributed tracer span.
"""

from __future__ import annotations

import asyncio
import re

from glasshat.agents.types import EvaluationInput, HatAssessment, PlanObject
from glasshat.rubric.models import Criterion, SynthesizedRubric
from glasshat.shared.enums import Hat
from glasshat.shared.ids import sha256_hex
from glasshat.shared.protocols import LlmClient, Retrieval, Tracer

HAT_PERSONAS: dict[Hat, str] = {
    Hat.WHITE: "Focus on facts and data; cite concrete evidence only.",
    Hat.RED: "Give your gut intuition and emotional read.",
    Hat.YELLOW: "Find the value and the optimistic upside.",
    Hat.BLACK: "Be the critic: risks, weaknesses, and missing rigor.",
    Hat.GREEN: "Propose alternatives and creative angles.",
    Hat.BLUE: "Synthesize the panel into a balanced judgment.",
}

_SCORE_RE = re.compile(r"SCORE:\s*([0-9]+(?:\.[0-9]+)?)")


def _extract_score(text: str, *, hat: Hat, criterion_id: str) -> float:
    match = _SCORE_RE.search(text)
    if match:
        return max(0.0, min(10.0, float(match.group(1))))
    seed = int(sha256_hex(f"{hat}:{criterion_id}:{text}")[:6], 16)
    return round((seed % 1001) / 100.0, 2)


def _hat_prompt(hat: Hat, criterion: Criterion, inp: EvaluationInput, evidence: list[str]) -> str:
    deck = (inp.deck_text or "")[:2000]
    ev = "\n".join(f"- {e}" for e in evidence) or "(none retrieved)"
    return (
        f"You are the {hat.value.upper()} hat. {HAT_PERSONAS[hat]}\n"
        f"Criterion: {criterion.label} — {criterion.descriptor_levels}\n"
        f"Deck excerpt:\n{deck}\n"
        f"Evidence refs:\n{ev}\n"
        f"Respond with 'SCORE: <0-10>' then a one-line RATIONALE."
    )


async def run_hat(
    hat: Hat,
    rubric: SynthesizedRubric,
    inp: EvaluationInput,
    llm: LlmClient,
    retrieval: Retrieval,
    tracer: Tracer,
    *,
    top_k: int = 5,
) -> list[HatAssessment]:
    """Assess every in-scope criterion from one hat's perspective."""
    out: list[HatAssessment] = []
    for criterion in rubric.criteria:
        with tracer.span(
            "hat_assess",
            **{"glasshat.hat": hat.value, "glasshat.criterion": criterion.id},
        ) as span:
            query_vector = (await llm.embed([criterion.label]))[0]
            hits = retrieval.search(criterion.label, top_k=top_k, query_vector=query_vector)
            evidence_refs = [hit.doc.id for hit in hits]
            response = await llm.generate(
                _hat_prompt(hat, criterion, inp, evidence_refs), tier="flash"
            )
            # Observable in Arize AX: a real-LLM response that doesn't emit a
            # parseable `SCORE:` falls back to a deterministic hash — flag it so a
            # malformed model output never silently masquerades as a real score.
            span.set_attr("glasshat.score_parse_failed", _SCORE_RE.search(response) is None)
            depth = min(1.0, len(hits) / top_k) if top_k else 0.0
            out.append(
                HatAssessment(
                    hat=hat,
                    criterion_id=criterion.id,
                    score=_extract_score(response, hat=hat, criterion_id=criterion.id),
                    evidence_refs=evidence_refs,
                    rationale=response[:200],
                    evidence_depth=depth,
                )
            )
    return out


async def run_panel(
    plan: PlanObject,
    rubric: SynthesizedRubric,
    inp: EvaluationInput,
    llm: LlmClient,
    retrieval: Retrieval,
    tracer: Tracer,
) -> list[HatAssessment]:
    """Run all enabled hats over the rubric and flatten their assessments."""
    batches = await asyncio.gather(
        *(run_hat(hat, rubric, inp, llm, retrieval, tracer) for hat in plan.hats_enabled)
    )
    return [assessment for batch in batches for assessment in batch]
