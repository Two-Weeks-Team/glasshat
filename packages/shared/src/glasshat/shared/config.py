"""Runtime configuration via environment variables.

Every external system sits behind a backend selector so the implementation is a
config flip, not a rewrite (see ``docs/architecture.md`` §5). Defaults are the
zero-dependency ``mock``/``memory``/``local-fs`` backends so tests and CI run
with no external calls or credentials.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

LlmBackend = Literal["vertex", "mock"]
MonitorBackend = Literal["phoenix-local", "phoenix-cloud", "arize"]
DocStoreBackend = Literal["memory", "sqlite", "firestore"]
BlobBackend = Literal["local-fs", "gcs"]
AgentRuntime = Literal["adk-local", "adk-cloud-run"]
ConsultantBackend = Literal["table", "phoenix-mcp"]
DatasetWriterBackend = Literal["null", "phoenix-mcp"]


class Settings(BaseSettings):
    """Process configuration loaded from environment (and ``.env`` if present)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )

    # --- GCP identity ---
    google_cloud_project: str = ""
    google_cloud_region: str = "us-central1"
    google_genai_use_vertexai: bool = True

    # --- Gemini model tiers (GLASSHAT_-prefixed in .env) ---
    gemini_pro: str = Field(
        default="gemini-3.1-pro-preview", validation_alias="GLASSHAT_GEMINI_PRO"
    )
    gemini_pro_location: str = Field(
        default="global", validation_alias="GLASSHAT_GEMINI_PRO_LOCATION"
    )
    gemini_flash: str = Field(
        default="gemini-3-flash-preview", validation_alias="GLASSHAT_GEMINI_FLASH"
    )
    gemini_flash_location: str = Field(
        default="global", validation_alias="GLASSHAT_GEMINI_FLASH_LOCATION"
    )
    gemini_flash_lite: str = Field(
        default="gemini-3.1-flash-lite", validation_alias="GLASSHAT_GEMINI_FLASH_LITE"
    )
    gemini_flash_lite_location: str = Field(
        default="global", validation_alias="GLASSHAT_GEMINI_FLASH_LITE_LOCATION"
    )

    # --- Backend selectors (config flip) ---
    llm_backend: LlmBackend = "mock"
    monitor_backend: MonitorBackend = "phoenix-local"
    docstore_backend: DocStoreBackend = "memory"
    blob_backend: BlobBackend = "local-fs"
    agent_runtime: AgentRuntime = "adk-local"
    # Learning loop (Improvement A): on deployed Cloud Run the audit reads
    # accumulated calibration deltas from Phoenix via MCP and writes this run's
    # corrections back to the same dataset. Default stays on the deterministic
    # in-code table so tests / CI / mock demos remain credential-free.
    consultant_backend: ConsultantBackend = "table"
    dataset_writer_backend: DatasetWriterBackend = "null"

    # --- Phoenix / Arize ---
    phoenix_api_key: str = ""
    phoenix_collector_endpoint: str = ""
    phoenix_project_name: str = "glasshat"
    phoenix_calibration_dataset: str = "glasshat-calibration"
    # Arize AX (monitor_backend="arize"): traces go to otlp.arize.com using
    # phoenix_api_key as the AX API key + this space id (both required by AX).
    arize_space_id: str = ""

    # --- DocStore / BlobStore targets ---
    docstore_sqlite_path: str = "./var/glasshat.db"
    firestore_project_id: str = ""
    blob_local_dir: str = "./var/uploads"
    gcs_uploads_bucket: str = ""
    gcs_reports_bucket: str = ""

    # --- Misc ---
    github_token: str = ""
    port: int = 8080
    next_public_default_locale: str = "en"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide cached :class:`Settings` instance."""
    return Settings()
