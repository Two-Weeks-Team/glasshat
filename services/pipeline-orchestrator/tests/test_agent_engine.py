"""Agent-Engine deploy module (P2) — credential-free unit coverage.

Covers the deployed agent's core (tracing isolation, message→eval, agent build)
and the deploy driver's pure config. The actual ``agent_engines.create`` is
overlay-only (needs the cloud SDK + ADC) and is NOT exercised here.
"""

from __future__ import annotations

import asyncio
import importlib.util
import json
import sys
import types
from pathlib import Path
from typing import Any

import pytest
from glasshat.agents.types import EvaluationInput, RunRecord
from glasshat.pipeline import agent_engine as ae
from glasshat.shared.enums import RunMode

_REPO = Path(__file__).resolve().parents[3]


def _load_deploy_driver() -> Any:
    """Import deploy/agent_engine_deploy.py by path (it lives outside the package)."""
    path = _REPO / "deploy" / "agent_engine_deploy.py"
    spec = importlib.util.spec_from_file_location("agent_engine_deploy", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --- tracing landmine fix ------------------------------------------------------


def test_setup_arize_tracing_is_noop_without_creds(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ARIZE_SPACE_ID", raising=False)
    monkeypatch.delenv("ARIZE_API_KEY", raising=False)
    assert ae.setup_arize_tracing(force=True) is False


def test_setup_arize_tracing_uses_isolated_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    # arize/openinference are NOT in the base venv (cloud-only); inject fakes and
    # assert the isolated-provider landmine fix is applied.
    captured: dict[str, Any] = {}

    fake_otel = types.ModuleType("arize.otel")

    def _register(**kwargs: Any) -> str:
        captured.update(kwargs)
        return "provider-sentinel"

    fake_otel.register = _register  # type: ignore[attr-defined]
    fake_arize = types.ModuleType("arize")

    fake_instr_mod = types.ModuleType("openinference.instrumentation.google_adk")

    class _GoogleADKInstrumentor:
        def instrument(self, *, tracer_provider: Any) -> None:
            captured["instrumented_with"] = tracer_provider

    fake_instr_mod.GoogleADKInstrumentor = _GoogleADKInstrumentor  # type: ignore[attr-defined]

    monkeypatch.setitem(sys.modules, "arize", fake_arize)
    monkeypatch.setitem(sys.modules, "arize.otel", fake_otel)
    monkeypatch.setitem(sys.modules, "openinference", types.ModuleType("openinference"))
    monkeypatch.setitem(
        sys.modules,
        "openinference.instrumentation",
        types.ModuleType("openinference.instrumentation"),
    )
    monkeypatch.setitem(sys.modules, "openinference.instrumentation.google_adk", fake_instr_mod)
    monkeypatch.setenv("ARIZE_SPACE_ID", "space-123")
    monkeypatch.setenv("ARIZE_API_KEY", "key-456")

    assert ae.setup_arize_tracing(force=True) is True
    # THE fix: an isolated provider (Agent Engine kills a global one → dropped traces).
    assert captured["set_global_tracer_provider"] is False
    assert captured["space_id"] == "space-123" and captured["api_key"] == "key-456"
    assert captured["instrumented_with"] == "provider-sentinel"


# --- deployed agent core -------------------------------------------------------


def test_evaluate_message_runs_pipeline_on_mock() -> None:
    inp = EvaluationInput(
        rubric_source={"preset_id": "rapid-agent"},
        deck_text="A demo agent. It plans, retrieves, and acts.",
        mode=RunMode.JUDGE,
    )
    record = asyncio.run(ae.evaluate_message(inp.model_dump_json()))
    assert isinstance(record, RunRecord)
    assert 0.0 <= record.final_score <= 100.0  # rapid-agent preset scores on 0-100
    assert record.scores  # the panel produced per-criterion scores


def test_evaluate_message_matches_direct_adk_run() -> None:
    # The deployed agent's core must be the SAME pipeline as run_evaluation_adk.
    from glasshat.pipeline.adk_agents import run_evaluation_adk
    from glasshat.pipeline.engine import default_deps

    inp = EvaluationInput(
        rubric_source={"preset_id": "rapid-agent"}, deck_text="X. does Y.", mode=RunMode.JUDGE
    )
    via_agent = asyncio.run(ae.evaluate_message(inp.model_dump_json()))
    direct = asyncio.run(run_evaluation_adk(inp, default_deps()))
    # run_id / created_at / rubric_id are fresh per run; compare the deterministic
    # scoring outputs that prove it is the SAME pipeline.
    assert via_agent.final_score == direct.final_score
    assert via_agent.pre_audit_final_score == direct.pre_audit_final_score
    assert [s.model_dump() for s in via_agent.scores] == [s.model_dump() for s in direct.scores]
    assert [c.model_dump() for c in via_agent.audit_corrections] == [
        c.model_dump() for c in direct.audit_corrections
    ]


def test_build_root_agent_constructs() -> None:
    agent = ae.build_root_agent()
    assert agent.name == "glasshat_eval"


# --- deploy driver config (pure) ----------------------------------------------


def test_remote_requirements_use_adk2_not_aiplatform_adk_extra() -> None:
    mod = _load_deploy_driver()
    reqs = mod.remote_requirements()
    joined = " ".join(reqs)
    assert "google-adk>=2.0" in reqs  # Workflow API needs 2.0
    # aiplatform[adk] would pin google-adk<2 — must use [agent_engines] only.
    assert "google-cloud-aiplatform[agent_engines]>=1.112" in reqs
    assert "[adk]" not in joined
    assert "arize-otel>=0.12" in reqs
    assert "openinference-instrumentation-google-adk>=0.1" in reqs
    assert "cloudpickle>=3.0" in reqs  # Agent Engine needs it to deserialize the agent


def test_extra_package_dirs_exist_and_cover_the_pipeline() -> None:
    mod = _load_deploy_driver()
    dirs = mod.extra_package_dirs()
    for d in dirs:
        assert Path(d).is_dir(), f"missing workspace package dir: {d}"
    assert any(d.endswith("pipeline-orchestrator") for d in dirs)
    assert any(d.endswith("packages/shared") for d in dirs)


def test_deploy_config_is_well_formed() -> None:
    mod = _load_deploy_driver()
    cfg = mod.deploy_config("gs://glasshat-agent-staging")
    assert cfg["staging_bucket"] == "gs://glasshat-agent-staging"
    assert cfg["identity_type"] == "AGENT_IDENTITY"
    assert cfg["env_vars"]["AGENT_RUNTIME"] == "adk"
    assert cfg["env_vars"]["MONITOR_BACKEND"] == "arize"
    assert cfg["env_vars"]["GOOGLE_GENAI_USE_VERTEXAI"] == "true"
    # Reserved platform vars must NOT be set (Agent Engine rejects them).
    assert "GOOGLE_CLOUD_PROJECT" not in cfg["env_vars"]
    assert "GOOGLE_CLOUD_LOCATION" not in cfg["env_vars"]
    # JSON-serializable (it gets printed by --dry-run).
    json.dumps(cfg)


def test_remote_env_vars_pass_arize_creds_only_when_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mod = _load_deploy_driver()
    monkeypatch.delenv("ARIZE_SPACE_ID", raising=False)
    monkeypatch.delenv("ARIZE_API_KEY", raising=False)
    assert "ARIZE_SPACE_ID" not in mod.remote_env_vars()
    monkeypatch.setenv("ARIZE_SPACE_ID", "s")
    monkeypatch.setenv("ARIZE_API_KEY", "k")
    env = mod.remote_env_vars()
    assert env["ARIZE_SPACE_ID"] == "s" and env["ARIZE_API_KEY"] == "k"
