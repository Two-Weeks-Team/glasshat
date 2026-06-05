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
        # Traces the per-hat Gemini calls (google.genai) under the agent/Workflow
        # spans → the full nested AX trace tree.
        "openinference-instrumentation-google-genai>=1.0",
        # cloudpickle deserializes the pickled agent on the remote — Agent Engine
        # warns "requirements are missing: {'cloudpickle'}" without it.
        "cloudpickle>=3.0",
        # Transitive PyPI deps the glasshat wheels need (their pyproject declares
        # them); without these the remote install/import fails.
        "pydantic>=2.7",
        "pydantic-settings>=2.3",
        "numpy>=2.0",
        "rank-bm25>=0.2",
        "PyYAML>=6",
        "httpx>=0.27",
    ]


def extra_package_dirs() -> list[str]:
    """Absolute paths to the glasshat workspace packages to bundle into the agent."""
    return [str(_REPO / p) for p in _GLASSHAT_PACKAGES]


# Agent Engine sets these automatically and REJECTS them in spec.deployment_spec.env
# ("Environment variable name '…' is reserved"). The deployed agent still reads
# GOOGLE_CLOUD_PROJECT/LOCATION from the platform-provided env.
_RESERVED_ENV = frozenset({"GOOGLE_CLOUD_PROJECT", "GOOGLE_CLOUD_LOCATION", "PORT"})


def remote_env_vars() -> dict[str, str]:
    """Env for the deployed agent. The real Gemini backend is selected here; secrets
    (ARIZE_*) are passed through from the deploy env, never hard-coded. Reserved
    platform vars (GOOGLE_CLOUD_PROJECT/LOCATION) are omitted — Agent Engine provides
    them and rejects them if set explicitly.

    NOTE: ``MONITOR_BACKEND`` is intentionally NOT set to ``arize``. The genuine Arize
    AX trace tree comes from the OpenInference ADK INSTRUMENTOR registered ONCE in
    ``TracedAdkApp.set_up`` (``setup_arize_tracing``); leaving the pipeline's manual
    ArizeTracer on would double-register a tracer provider (and crash without creds).
    The manual tracer therefore stays NoOp (default backend, phoenix SDK absent on the
    remote), so the agent SERVES credential-free and tracing is single-sourced."""
    env: dict[str, str] = {
        "LLM_BACKEND": os.environ.get("LLM_BACKEND", "gemini-enterprise"),
        "AGENT_RUNTIME": "adk",
        "GOOGLE_GENAI_USE_VERTEXAI": "true",
        "ARIZE_PROJECT_NAME": os.environ.get("ARIZE_PROJECT_NAME", "glasshat"),
    }
    # Pass Arize creds through only if present (so the instrumentor tracing in
    # set_up is genuine when set).
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


def build_agent_package(staging: Path | None = None) -> Path:
    """Merge the six workspace packages' ``src/glasshat`` trees into ONE importable
    ``glasshat/`` source package and return it.

    Agent Engine's ``extra_packages`` COPIES a source path into the deployment (it
    does NOT pip-install) and puts the deployment root on ``sys.path``. So the glasshat
    namespace must be a single importable ``glasshat/`` tree at a path whose basename
    is ``glasshat`` — wheels (copied, never installed) gave ``No module named
    'glasshat'``. glasshat is a PEP 420 namespace package, so the six subpackage trees
    merge cleanly. The glasshat-* inter-package deps vanish (it is one tree); only the
    real PyPI deps remain (declared in ``remote_requirements``)."""
    import shutil

    staging = staging or (_REPO / "dist" / "agent-engine" / "build")
    pkg = staging / "glasshat"
    if pkg.exists():
        shutil.rmtree(pkg)
    pkg.mkdir(parents=True)
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc")
    for p in _GLASSHAT_PACKAGES:
        shutil.copytree(_REPO / p / "src" / "glasshat", pkg, dirs_exist_ok=True, ignore=ignore)
    return pkg


def deploy(project: str, location: str, staging_bucket: str) -> str:
    """Create the Agent Engine and return its resource name. Overlay-only."""
    import os

    import vertexai  # cloud SDK, present only in the deploy overlay

    pkg = build_agent_package()  # …/dist/agent-engine/build/glasshat
    cfg = deploy_config(staging_bucket)
    client = vertexai.Client(project=project, location=location)
    # extra_packages preserves the path's basename at the deployment root, so run
    # create from the build dir with the relative path "glasshat" → remote
    # <root>/glasshat is importable.
    prev = os.getcwd()
    os.chdir(pkg.parent)
    try:
        cfg["extra_packages"] = [pkg.name]  # "glasshat"
        remote = client.agent_engines.create(agent=build_app(), config=cfg)
    finally:
        os.chdir(prev)
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
