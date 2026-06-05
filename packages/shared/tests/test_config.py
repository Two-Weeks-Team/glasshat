import pytest
from glasshat.shared.config import Settings, get_settings

_BACKEND_KEYS = [
    "LLM_BACKEND",
    "MONITOR_BACKEND",
    "DOCSTORE_BACKEND",
    "BLOB_BACKEND",
    "AGENT_RUNTIME",
    "GOOGLE_CLOUD_REGION",
    "GOOGLE_CLOUD_PROJECT",
]


def test_defaults_load_without_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for k in _BACKEND_KEYS:
        monkeypatch.delenv(k, raising=False)
    s = Settings(_env_file=None)  # type: ignore[call-arg]
    assert s.google_cloud_region == "us-central1"
    assert s.llm_backend == "mock"
    assert s.monitor_backend == "phoenix-local"
    assert s.docstore_backend == "memory"
    assert s.blob_backend == "local-fs"
    assert s.agent_runtime == "python"
    assert s.phoenix_project_name == "glasshat"


def test_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_BACKEND", "vertex")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "panelyst-hackathon")
    s = Settings(_env_file=None)  # type: ignore[call-arg]
    assert s.llm_backend == "vertex"
    assert s.google_cloud_project == "panelyst-hackathon"


def test_gemini_model_alias_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GLASSHAT_GEMINI_PRO", "gemini-3.1-pro-custom")
    s = Settings(_env_file=None)  # type: ignore[call-arg]
    assert s.gemini_pro == "gemini-3.1-pro-custom"


def test_get_settings_is_cached() -> None:
    assert get_settings() is get_settings()
