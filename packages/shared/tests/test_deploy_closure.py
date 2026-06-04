"""Lock the deploy-closure dependency invariants at the source of truth.

The Arize-track image is built with ``--extra vertex --extra arize`` (see
``infra/deploy.sh`` / ``infra/Dockerfile.api``). Two invariants must hold for the
ARIZE evaluation to run *genuinely*:

1. The ``arize`` extra ships the Phoenix-MCP client (``mcp``). Without it, the
   live ``PhoenixMcpConsultant`` / ``PhoenixMcpDatasetWriter`` raise
   ``ModuleNotFoundError`` at import and the audit's learning loop silently
   degrades to the deterministic prior — looking live while doing nothing.
2. The ``arize`` extra ships NO general-purpose LLM SDK (Gemini/Google-only
   policy). This mirrors the CI supply-chain leak gate, but as a fast unit test
   on the pyproject so a regression is caught before a build.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

_PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"


def _req_name(requirement: str) -> str:
    """Bare distribution name from a requirement string (drop version specifiers)."""
    name = requirement.strip()
    for sep in (">=", "==", "<=", "~=", ">", "<", "[", " "):
        name = name.split(sep)[0]
    return name.strip().lower()


def _arize_extra() -> list[str]:
    data = tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))
    return data["project"]["optional-dependencies"]["arize"]


def test_arize_extra_ships_phoenix_mcp_client() -> None:
    names = {_req_name(req) for req in _arize_extra()}
    assert "mcp" in names, (
        "the `arize` deploy extra must include `mcp` or the live Phoenix-MCP "
        "learning loop silently falls back to the deterministic prior"
    )


def test_arize_extra_has_no_general_purpose_llm_sdk() -> None:
    forbidden = {"openai", "anthropic", "pydantic-ai"}
    leaked = {_req_name(req) for req in _arize_extra()} & forbidden
    assert not leaked, f"forbidden LLM SDK declared in the arize deploy extra: {sorted(leaked)}"
