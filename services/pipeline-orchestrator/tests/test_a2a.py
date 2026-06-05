"""A2A AgentCard (P4) — credential-free unit coverage.

The AgentCard metadata (the A2A discovery artifact) is fully tested here. The typed
``a2a`` AgentCard + the ``to_a2a`` Starlette app are overlay-only (a2a-sdk + ADK
a2a, not in the lean image), so they are asserted to fail gracefully without it.
"""

from __future__ import annotations

import pytest
from glasshat.pipeline.a2a import (
    A2A_AGENT_NAME,
    A2A_SKILL_ID,
    agent_card_dict,
    build_a2a_app,
    build_agent_card,
)


def test_agent_card_dict_is_well_formed() -> None:
    card = agent_card_dict(host="glasshat.example", port=443, protocol="https")
    assert card["name"] == A2A_AGENT_NAME == "glasshat"
    assert card["version"]
    assert card["url"] == "https://glasshat.example:443/"
    assert card["default_input_modes"] == ["text"]
    assert len(card["skills"]) == 1
    skill = card["skills"][0]
    assert skill["id"] == A2A_SKILL_ID
    assert "rubric" in " ".join(skill["tags"])
    assert skill["examples"]  # a callable example for discovery


def test_agent_card_dict_default_url() -> None:
    assert agent_card_dict()["url"] == "http://0.0.0.0:8080/"


def test_a2a_builders_need_the_overlay_sdk() -> None:
    # a2a-sdk / ADK a2a are deliberately overlay-only (not in the lean image); the
    # typed-card + server builders should fail clearly without them, not silently.
    with pytest.raises((ImportError, ModuleNotFoundError)):
        build_agent_card()
    with pytest.raises((ImportError, ModuleNotFoundError)):
        build_a2a_app()
