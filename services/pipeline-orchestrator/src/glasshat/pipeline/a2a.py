"""Expose the glasshat evaluation agent over the **A2A protocol** (AgentCard + RPC).

``to_a2a(root_agent)`` (ADK) wraps the deployed ADK Workflow agent as an A2A
Starlette app that serves the **AgentCard** at ``/.well-known/agent-card.json`` and
the A2A JSON-RPC methods — so other agents can discover and call glasshat. The
``a2a-sdk`` + ADK a2a deps are overlay-only (NOT in the lean image), so the
``to_a2a`` call is imported lazily; the AgentCard **metadata** is a pure, testable
dict and is also the source of truth passed to ``to_a2a``.
"""

from __future__ import annotations

from typing import Any

A2A_SKILL_ID = "evaluate-submission"
A2A_AGENT_NAME = "glasshat"
A2A_VERSION = "0.1.0"


def agent_card_dict(
    *, host: str = "0.0.0.0", port: int = 8080, protocol: str = "http"
) -> dict[str, Any]:
    """The glasshat **AgentCard** metadata for A2A discovery. Pure + testable; it is
    also the card passed to ``to_a2a`` so the served card matches this exactly."""
    return {
        "name": A2A_AGENT_NAME,
        "description": (
            "Rubric-aware hackathon-submission evaluator: a six-hat Google ADK 2.0 "
            "Workflow panel with an audit/calibration pass. Returns a 0-100 score "
            "with per-criterion rationale."
        ),
        "version": A2A_VERSION,
        "url": f"{protocol}://{host}:{port}/",
        "default_input_modes": ["text"],
        "default_output_modes": ["text"],
        "skills": [
            {
                "id": A2A_SKILL_ID,
                "name": "Evaluate a submission",
                "description": (
                    "Score a hackathon submission against a rubric preset — a JSON "
                    "EvaluationInput in, the RunRecord JSON out."
                ),
                "tags": ["evaluation", "rubric", "scoring", "hackathon"],
                "examples": [
                    '{"rubric_source": {"preset_id": "rapid-agent"}, '
                    '"deck_text": "A RAG agent that books meetings.", "mode": "judge"}'
                ],
            }
        ],
    }


def build_agent_card(*, host: str = "0.0.0.0", port: int = 8080, protocol: str = "http") -> Any:
    """Build the typed ``a2a`` AgentCard from :func:`agent_card_dict`. Overlay-only
    (``a2a-sdk``)."""
    from a2a.types import AgentCapabilities, AgentCard, AgentSkill

    meta = agent_card_dict(host=host, port=port, protocol=protocol)
    skills = [
        AgentSkill(
            id=s["id"],
            name=s["name"],
            description=s["description"],
            tags=s["tags"],
            examples=s.get("examples"),
        )
        for s in meta["skills"]
    ]
    return AgentCard(
        name=meta["name"],
        description=meta["description"],
        version=meta["version"],
        url=meta["url"],
        default_input_modes=meta["default_input_modes"],
        default_output_modes=meta["default_output_modes"],
        capabilities=AgentCapabilities(streaming=True),
        skills=skills,
    )


def build_a2a_app(*, host: str = "0.0.0.0", port: int = 8080, protocol: str = "http") -> Any:
    """Build the A2A Starlette app wrapping the glasshat ADK agent. Overlay-only
    (``a2a-sdk`` + ADK a2a). Serves the AgentCard (from :func:`build_agent_card`)
    plus the A2A JSON-RPC methods; run it with uvicorn. Set ``protocol="https"`` when
    serving behind a TLS proxy so the advertised card URL is correct."""
    from glasshat.pipeline.agent_engine import build_root_agent
    from google.adk.a2a.utils.agent_to_a2a import to_a2a

    return to_a2a(
        build_root_agent(),
        host=host,
        port=port,
        protocol=protocol,
        agent_card=build_agent_card(host=host, port=port, protocol=protocol),
    )
