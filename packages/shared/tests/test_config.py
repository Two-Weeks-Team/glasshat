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


def test_default_gemini_models_are_ga(monkeypatch: pytest.MonkeyPatch) -> None:
    # GA model strings (Gemini API changelog, June 2026). The ``-preview`` aliases
    # shut down 2026-06-25 — the defaults must be the GA ids, not preview ids.
    for k in ("GLASSHAT_GEMINI_PRO", "GLASSHAT_GEMINI_FLASH", "GLASSHAT_GEMINI_FLASH_LITE"):
        monkeypatch.delenv(k, raising=False)
    s = Settings(_env_file=None)  # type: ignore[call-arg]
    assert s.gemini_pro == "gemini-3.1-pro"
    assert s.gemini_flash == "gemini-3.5-flash"
    assert s.gemini_flash_lite == "gemini-3.1-flash-lite"
    for model in (s.gemini_pro, s.gemini_flash, s.gemini_flash_lite):
        assert not model.endswith("-preview"), f"{model} is a retired preview id"


def test_llm_backend_accepts_gemini_enterprise_and_vertex(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # ``gemini-enterprise`` is the canonical name (Vertex AI → Gemini Enterprise
    # Agent Platform, 2026); ``vertex`` is the kept-working deprecated alias so
    # deployed envs setting LLM_BACKEND=vertex never break.
    for value in ("gemini-enterprise", "vertex", "mock"):
        monkeypatch.setenv("LLM_BACKEND", value)
        assert Settings(_env_file=None).llm_backend == value  # type: ignore[call-arg]


def test_get_settings_is_cached() -> None:
    assert get_settings() is get_settings()
