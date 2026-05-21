import asyncio
from collections.abc import Sequence
from typing import Any

import pytest
import yaml
from glasshat.agents.rubric_synthesizer import (
    SYNTH_PROMPT_PATH,
    synthesize,
    synthesize_from_text,
)
from glasshat.agents.types import EvaluationInput
from glasshat.rubric.presets import PRESETS_DIR
from glasshat.shared.errors import SynthesisError
from glasshat.shared.llm import MockLlmClient

CANNED_YAML = """
schema_version: "1.0"
source: { type: url, identifier: "https://example/rules" }
scoring_rule: { aggregation: weighted_sum, final_scale: "0-100" }
criteria:
  - id: tech
    label: Tech
    weight: 0.5
    scale: 5
    bmad_mapping: [C1]
    descriptor_levels: {1: a, 2: b, 3: c, 4: d, 5: e}
    source_clause: "axis 1"
    source_excerpt: "Technical"
  - id: idea
    label: Idea
    weight: 0.5
    scale: 5
    bmad_mapping: [A1]
    descriptor_levels: {1: a, 2: b, 3: c, 4: d, 5: e}
    source_clause: "axis 2"
    source_excerpt: "Idea"
confidence: 0.9
"""


class _CannedLlm:
    async def generate(self, prompt: str, *, tier: str = "flash", **kw: Any) -> str:
        return CANNED_YAML

    async def embed(self, texts: Sequence[str]) -> list[list[float]]:
        return [[0.0] for _ in texts]


def test_prompt_file_exists() -> None:
    assert SYNTH_PROMPT_PATH.exists()
    assert "RubricSynthesizer" in SYNTH_PROMPT_PATH.read_text()


def test_synthesize_preset_path_returns_rapid_agent_25() -> None:
    inp = EvaluationInput(rubric_source={"preset_id": "rapid-agent"})
    r = asyncio.run(synthesize(inp, MockLlmClient()))
    assert [c.weight for c in r.criteria] == [0.25, 0.25, 0.25, 0.25]


def test_synthesize_custom_yaml_path() -> None:
    body = yaml.safe_load((PRESETS_DIR / "qdrant.yaml").read_text())["synthesized"]
    inp = EvaluationInput(rubric_source={"custom_yaml": yaml.safe_dump(body)})
    r = asyncio.run(synthesize(inp, MockLlmClient()))
    assert r.scoring_rule.aggregation == "simple_average"


def test_synthesize_no_source_raises() -> None:
    with pytest.raises(SynthesisError):
        asyncio.run(synthesize(EvaluationInput(rubric_source={}), MockLlmClient()))


def test_synthesize_from_text_parses_llm_yaml() -> None:
    r = asyncio.run(synthesize_from_text("the rules", _CannedLlm(), identifier="u"))
    assert len(r.criteria) == 2
    assert r.source.identifier == "u"


def test_synthesize_from_text_rejects_invalid_yaml() -> None:
    class BadLlm:
        async def generate(self, prompt: str, *, tier: str = "flash", **kw: Any) -> str:
            return "not: [a, valid, rubric"

        async def embed(self, texts: Sequence[str]) -> list[list[float]]:
            return [[0.0]]

    with pytest.raises(SynthesisError):
        asyncio.run(synthesize_from_text("rules", BadLlm(), identifier="u"))
