#!/usr/bin/env python
"""Deploy the glasshat evaluation agent to the Gemini Enterprise Agent Platform
(Agent Runtime / Agent Engine).

OWNER-RUN, deploy-time tooling. The cloud SDK (``google-cloud-aiplatform
[agent_engines]``) is NOT in the project lock (it pins google-adk<2, which would
break the lean image's ADK 2.0 Workflow API). Run this in an isolated overlay:

    GOOGLE_CLOUD_PROJECT=panelyst-hackathon GOOGLE_CLOUD_LOCATION=us-central1 \\
    uv run --with-requirements deploy/requirements-cloud.txt \\
        python deploy/agent_engine_deploy.py --staging-bucket gs://glasshat-agent-staging

(The project env brings glasshat + google-adk 2.0; the overlay adds the cloud SDK.
``--no-project`` would drop glasshat, so it is intentionally NOT used.)

Add ``--dry-run`` to print the deploy config (requirements / extra packages / env)
without creating anything — that path imports no cloud SDK and is what CI exercises.

The deployed remote agent declares its OWN runtime deps here (in ``requirements``),
a separate pip environment on Agent Engine independent of the project lock.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

# Repo root = two levels up from this file (deploy/agent_engine_deploy.py).
_REPO = Path(__file__).resolve().parents[1]

# uv-managed CPython does not process the editable .pth files, so put the glasshat
# src layouts on the path explicitly (same dirs as the pytest `pythonpath`) — the
# overlay run brings the cloud SDK + google-adk but not the editable workspace.
for _pkg in (
    "packages/shared",
    "packages/rubric",
    "agents",
    "services/ingest",
    "services/code-grader",
    "services/pipeline-orchestrator",
):
    _src = str(_REPO / _pkg / "src")
    if _src not in sys.path:
        sys.path.insert(0, _src)

# The workspace packages the deployed agent needs, in dependency order. Each is a
# pip-installable package (has its own pyproject.toml + src/glasshat namespace);
# Agent Engine bundles + installs them via ``extra_packages``.
_GLASSHAT_PACKAGES = (
    "packages/shared",
    "packages/rubric",
    "agents",
    "services/ingest",
    "services/code-grader",
    "services/pipeline-orchestrator",
)


def remote_requirements() -> list[str]:
    """PyPI deps for the deployed agent's own pip env on Agent Engine.

    We pin ``google-adk>=2.0`` (the Workflow API) and use
    ``google-cloud-aiplatform[agent_engines]`` WITHOUT the ``[adk]`` extra, which
    would pin google-adk<2 — the same conflict avoided in the lean image."""
    return [
        "google-cloud-aiplatform[agent_engines]>=1.112",
        "google-adk>=2.0",
        "google-genai>=0.3",
        "arize-otel>=0.12",
        "openinference-instrumentation-google-adk>=0.1",
        "pydantic>=2.7",
        "pydantic-settings>=2.3",
        "numpy>=2.0",
        "rank-bm25>=0.2",
    ]


def extra_package_dirs() -> list[str]:
    """Absolute paths to the glasshat workspace packages to bundle into the agent."""
    return [str(_REPO / p) for p in _GLASSHAT_PACKAGES]


# Agent Engine sets these automatically and REJECTS them in spec.deployment_spec.env
# ("Environment variable name '…' is reserved"). The deployed agent still reads
# GOOGLE_CLOUD_PROJECT/LOCATION from the platform-provided env.
_RESERVED_ENV = frozenset({"GOOGLE_CLOUD_PROJECT", "GOOGLE_CLOUD_LOCATION", "PORT"})


def remote_env_vars() -> dict[str, str]:
    """Env for the deployed agent. The real Gemini backend + Arize tracer are
    selected here; secrets (ARIZE_*) are passed through from the deploy env, never
    hard-coded. Reserved platform vars (GOOGLE_CLOUD_PROJECT/LOCATION) are omitted —
    Agent Engine provides them and rejects them if set explicitly. Defaults keep the
    agent functional even without Arize creds (tracing just no-ops)."""
    env: dict[str, str] = {
        "LLM_BACKEND": os.environ.get("LLM_BACKEND", "gemini-enterprise"),
        "AGENT_RUNTIME": "adk",
        "MONITOR_BACKEND": "arize",
        "GOOGLE_GENAI_USE_VERTEXAI": "true",
        "ARIZE_PROJECT_NAME": os.environ.get("ARIZE_PROJECT_NAME", "glasshat"),
    }
    # Pass Arize creds through only if present (so tracing is genuine when set).
    for key in ("ARIZE_SPACE_ID", "ARIZE_API_KEY"):
        if os.environ.get(key):
            env[key] = os.environ[key]
    return {k: v for k, v in env.items() if v and k not in _RESERVED_ENV}


def deploy_config(staging_bucket: str) -> dict[str, Any]:
    """The full ``agent_engines.create`` config — a pure dict (no cloud SDK), so it
    is unit-testable and ``--dry-run`` printable."""
    return {
        "requirements": remote_requirements(),
        "extra_packages": extra_package_dirs(),
        "staging_bucket": staging_bucket,
        "env_vars": remote_env_vars(),
        # AGENT_IDENTITY = the platform-managed agent identity (governance pillar).
        "identity_type": "AGENT_IDENTITY",
    }


def build_app() -> Any:
    """Build the ``AdkApp`` wrapping the glasshat agent, with Arize tracing set up
    REMOTELY at agent startup (the documented Agent-Engine pattern). Imports the
    cloud SDK + the agent lazily (overlay only)."""
    from glasshat.pipeline.agent_engine import build_root_agent, setup_arize_tracing

    try:  # SDK namespace moved across aiplatform versions; support both.
        from vertexai.agent_engines import AdkApp  # type: ignore
    except ImportError:  # pragma: no cover - overlay-only path
        from vertexai.preview.reasoning_engines import AdkApp  # type: ignore

    class TracedAdkApp(AdkApp):  # type: ignore[misc]
        """AdkApp whose remote ``set_up`` registers Arize tracing FIRST (isolated
        provider) so the nested Workflow span tree lands in Arize AX."""

        def set_up(self) -> None:  # pragma: no cover - runs remotely on Agent Engine
            setup_arize_tracing()
            super().set_up()

    return TracedAdkApp(agent=build_root_agent())


def build_wheels(out_dir: Path | None = None) -> list[str]:
    """Build a wheel for each glasshat workspace package (src-layout namespace
    packages), returning the wheel paths. Agent Engine pip-installs ``.whl`` files
    passed in ``extra_packages`` — the reliable way to make the namespace package
    importable on the remote (a bare src dir would not be)."""
    import subprocess

    out = out_dir or (_REPO / "dist" / "agent-engine")
    out.mkdir(parents=True, exist_ok=True)
    for existing in out.glob("*.whl"):
        existing.unlink()
    for pkg in _GLASSHAT_PACKAGES:
        subprocess.run(
            ["uv", "build", "--wheel", "--out-dir", str(out), str(_REPO / pkg)],
            check=True,
            cwd=str(_REPO),
        )
    return sorted(str(w) for w in out.glob("*.whl"))


def deploy(project: str, location: str, staging_bucket: str) -> str:
    """Create the Agent Engine and return its resource name. Overlay-only."""
    import vertexai  # cloud SDK, present only in the deploy overlay

    client = vertexai.Client(project=project, location=location)
    cfg = deploy_config(staging_bucket)
    # Swap the source-dir documentation value for the actually-installable wheels.
    cfg["extra_packages"] = build_wheels()
    remote = client.agent_engines.create(agent=build_app(), config=cfg)
    return str(getattr(remote, "resource_name", remote))


def main() -> int:
    ap = argparse.ArgumentParser(description="Deploy glasshat to Agent Engine.")
    ap.add_argument(
        "--project", default=os.environ.get("GOOGLE_CLOUD_PROJECT", "panelyst-hackathon")
    )
    ap.add_argument("--location", default=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1"))
    ap.add_argument("--staging-bucket", default=os.environ.get("GLASSHAT_AGENT_STAGING_BUCKET", ""))
    ap.add_argument("--dry-run", action="store_true", help="print the config; create nothing")
    args = ap.parse_args()

    bucket = args.staging_bucket or "gs://glasshat-agent-staging"
    if args.dry_run:
        print(
            json.dumps(
                {"project": args.project, "location": args.location, **deploy_config(bucket)},
                indent=2,
            )
        )
        return 0

    if not args.project:
        print("ERROR: set --project or GOOGLE_CLOUD_PROJECT")
        return 2
    resource = deploy(args.project, args.location, bucket)
    print(f"DEPLOYED agent_engine resource: {resource}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
