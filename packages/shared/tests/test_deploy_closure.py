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
_ROOT = Path(__file__).resolve().parents[3]
_ROOT_PYPROJECT = _ROOT / "pyproject.toml"
_CLOUD_REQS = _ROOT / "deploy" / "requirements-cloud.txt"

# Cloud SDKs that pin google-adk<2 (directly or transitively) and would, if locked
# into the workspace, drag the deploy closure's google-adk down from the 2.0 the
# ADK 2.0 Workflow API needs — ballooning the lean image. They must stay OUT of
# every uv dependency-group and live only in the standalone cloud requirements
# file installed via an ephemeral overlay.
_CLOUD_ONLY_SDKS = {"google-cloud-aiplatform", "arize", "arize-phoenix-evals"}


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


def test_arize_extra_declares_no_forbidden_sdk_or_carrier() -> None:
    # Forbid both the leaf LLM SDKs AND their known transitive carriers: the most
    # likely regression here is someone adding the `phoenix` extra's packages
    # (arize-phoenix / arize-phoenix-otel) to `arize`, which would *transitively*
    # pull openai/anthropic past a leaf-only check. The CI `uv export` gate is the
    # full transitive backstop; this unit test guards the realistic direct slip.
    forbidden = {"openai", "anthropic", "pydantic-ai", "arize-phoenix", "arize-phoenix-otel"}
    leaked = {_req_name(req) for req in _arize_extra()} & forbidden
    assert not leaked, (
        f"forbidden LLM SDK / transitive carrier in the arize deploy extra: {sorted(leaked)}"
    )


def _root_dependency_groups() -> dict[str, list[str]]:
    data = tomllib.loads(_ROOT_PYPROJECT.read_text(encoding="utf-8"))
    return data.get("dependency-groups", {})


def test_cloud_sdks_are_not_in_any_uv_dependency_group() -> None:
    # Regression guard: locking google-cloud-aiplatform / arize / arize-phoenix-evals
    # into ANY uv group conflicts with google-adk 2.0 under uv's single universal
    # resolution and silently perturbs the deploy closure (google-adk 2.0 -> 1.x,
    # +~55 packages). They must stay out of every group.
    for group, reqs in _root_dependency_groups().items():
        # uv groups may include non-string entries (e.g. group inheritance via an
        # inline table {"include-group": "other"}); only parse string requirements.
        names = {_req_name(r) for r in reqs if isinstance(r, str)}
        leaked = names & _CLOUD_ONLY_SDKS
        assert not leaked, (
            f"cloud-only SDK(s) {sorted(leaked)} found in uv dependency-group "
            f"'{group}' — they perturb the deploy closure; keep them in "
            f"deploy/requirements-cloud.txt instead"
        )


def test_cloud_requirements_file_carries_the_cloud_sdks() -> None:
    # The cloud tooling must exist *somewhere* reproducible — the standalone file
    # is the agreed home (installed via an ephemeral `uv run --with-requirements`).
    assert _CLOUD_REQS.exists(), "deploy/requirements-cloud.txt is missing"
    names = {
        _req_name(line.split("#")[0])
        for line in _CLOUD_REQS.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    missing = _CLOUD_ONLY_SDKS - names
    assert not missing, f"deploy/requirements-cloud.txt is missing cloud SDK(s): {sorted(missing)}"
