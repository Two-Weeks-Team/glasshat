"""RubricSynthesizer — official rules -> SynthesizedRubric (spec §4-§7).

Path A (preset_id) and Path D (custom_yaml) are deterministic and credential-free.
Path B (rules_url) lazily fetches the page then asks the LLM to synthesize. PDF
(Path C) is not supported in this build (use a preset, URL, or custom YAML). The
agent's behaviour *is* its prompt: ``prompts/rubric_synthesizer.md``.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from glasshat.agents.types import EvaluationInput
from glasshat.rubric.models import SynthesizedRubric
from glasshat.rubric.presets import load_preset
from glasshat.rubric.validation import validate_custom_yaml
from glasshat.shared.enums import SourceKind
from glasshat.shared.errors import SynthesisError
from glasshat.shared.protocols import LlmClient
from pydantic import ValidationError

SYNTH_PROMPT_PATH = Path(__file__).parent / "prompts" / "rubric_synthesizer.md"


def _load_prompt() -> str:
    return SYNTH_PROMPT_PATH.read_text(encoding="utf-8")


async def synthesize_from_text(
    rules_text: str,
    llm: LlmClient,
    *,
    identifier: str,
    source_kind: SourceKind = SourceKind.URL,
) -> SynthesizedRubric:
    """Synthesize a rubric from raw rules text via the LLM (Paths B/C core)."""
    prompt = f"{_load_prompt()}\n\nRULES TEXT:\n{rules_text}"
    raw = await llm.generate(prompt, tier="pro")
    try:
        data = yaml.safe_load(raw)
        rubric = SynthesizedRubric.model_validate(data)
    except (yaml.YAMLError, ValidationError) as exc:
        raise SynthesisError(f"could not synthesize a valid rubric from source: {exc}") from exc
    rubric.source.identifier = identifier
    rubric.source.type = source_kind
    return rubric


async def synthesize(inp: EvaluationInput, llm: LlmClient) -> SynthesizedRubric:
    """Produce the SynthesizedRubric for an evaluation input.

    Dispatch order: preset_id -> custom_yaml -> rules_url -> rules_pdf_uri.
    """
    src = inp.rubric_source
    if src.get("preset_id"):
        return load_preset(src["preset_id"])
    if src.get("custom_yaml"):
        return validate_custom_yaml(yaml.safe_load(src["custom_yaml"]))
    if src.get("rules_url"):  # pragma: no cover - requires network
        text = await _fetch_url(src["rules_url"])
        return await synthesize_from_text(text, llm, identifier=src["rules_url"])
    if src.get("rules_pdf_uri"):
        raise SynthesisError(
            "rules_pdf_uri is not supported in this build; use preset_id, rules_url, or custom_yaml"
        )
    raise SynthesisError(
        "no rubric source provided (one of preset_id, custom_yaml, rules_url, rules_pdf_uri)"
    )


async def _fetch_url(url: str) -> str:  # pragma: no cover - requires network
    import httpx

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return str(resp.text)
