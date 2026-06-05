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

# LLM backend selector. ``gemini-enterprise`` is the canonical name for the real
# Google cloud model backend: "Vertex AI" was renamed → **Gemini Enterprise Agent
# Platform** at Cloud Next 2026 (the product left the Cloud Console on 2026-05-21).
# The Python SDK still imports as ``vertexai``/``google.genai`` (namespace lag), so
# ``vertex`` is kept as a working deprecated alias — deployed envs that set
# ``LLM_BACKEND=vertex`` keep working unchanged. ``mock`` is the credential-free
# default used by tests/CI.
LlmBackend = Literal["gemini-enterprise", "vertex", "mock"]
MonitorBackend = Literal["phoenix-local", "phoenix-cloud", "arize"]
DocStoreBackend = Literal["memory", "sqlite", "firestore"]
BlobBackend = Literal["local-fs", "gcs"]
# Orchestration runtime for the evaluation pipeline. ``python`` (default) runs the
# stages as a plain async sequence (today's path, byte-identical). ``adk`` runs the
# SAME stages as a genuine Google ADK agent graph (Sequential → Parallel[hats] →
# Loop[audit]) so the OpenInference ADK instrumentor emits a nested span TREE to
# Arize AX instead of flat manual spans. Both paths produce an identical RunRecord
# and the identical ordered SSE stream (asserted by the parity test); ``adk`` is
# opt-in until a gated redeploy flips it.
AgentRuntime = Literal["python", "adk"]
ConsultantBackend = Literal["table", "phoenix-mcp", "anchor"]
DatasetWriterBackend = Literal["null", "phoenix-mcp"]
RepoGraderBackend = Literal["null", "github-api"]
# Hat scoring extraction strategy. ``legacy`` = the historical free-text
# ``SCORE: <n>`` regex (first match wins) — kept byte-identical as the default so
# the live demo's numbers never move. ``structured`` = a typed JSON
# ``{score, rationale}`` the model fills under a system instruction that
# quarantines the (untrusted) submission, so a literal ``SCORE: 10`` planted in a
# deck no longer maps onto the output score. Opt-in until a gated redeploy flips it.
ScoringMode = Literal["legacy", "structured"]
# Input prompt-injection guardrail. ``heuristic`` = a deterministic, offline,
# credential-free classifier (always ships). ``phoenix`` = an LLM-judge classifier
# via ``phoenix.evals.create_classifier`` (opt-in; requires ``arize-phoenix-evals``,
# which is deliberately kept OUT of the deploy closure so the supply-chain leak
# gate stays green — it falls back to ``heuristic`` when the package/endpoint is
# absent). Either way the verdict is emitted as a ``glasshat.injection_flag`` span
# attribute, observable in Arize AX.
InjectionGuardBackend = Literal["heuristic", "phoenix"]


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
    # GA model strings (Gemini API changelog, June 2026). ``gemini-3.1-pro`` and
    # ``gemini-3.5-flash`` are GA; the older ``-preview`` image/model aliases shut
    # down 2026-06-25. ``gemini-3.1-flash-lite`` is already GA. Overridable per env.
    gemini_pro: str = Field(default="gemini-3.1-pro", validation_alias="GLASSHAT_GEMINI_PRO")
    gemini_pro_location: str = Field(
        default="global", validation_alias="GLASSHAT_GEMINI_PRO_LOCATION"
    )
    gemini_flash: str = Field(default="gemini-3.5-flash", validation_alias="GLASSHAT_GEMINI_FLASH")
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
    agent_runtime: AgentRuntime = "python"
    # Learning loop (Improvement A): on deployed Cloud Run the audit reads
    # accumulated calibration deltas from Phoenix via MCP and writes this run's
    # corrections back to the same dataset. Default stays on the deterministic
    # in-code table so tests / CI / mock demos remain credential-free.
    consultant_backend: ConsultantBackend = "table"
    dataset_writer_backend: DatasetWriterBackend = "null"
    # repo_url grading (Improvement (a)): on deployed Cloud Run the code grader
    # fetches GitHub REST metadata (no clone) so repo evidence joins the deck in
    # retrieval. Default "null" keeps local/CI/mock runs deck-only and hermetic.
    repo_grader_backend: RepoGraderBackend = "null"
    # (GitHub PAT for the grader lives in the "Misc" section below as github_token —
    # lifts the 60 req/hr unauthenticated limit; public repos work without it.)
    # Scoring extraction + input guardrail (Tier A security floor). Defaults keep
    # the live demo byte-identical; flip to ``structured`` in a gated redeploy.
    scoring_mode: ScoringMode = "legacy"
    injection_guard_backend: InjectionGuardBackend = "heuristic"

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
    # Comma-separated CORS allowlist for the API. Defaults to "*" for local/dev;
    # the live deploy sets this to the deployed web origin so the API isn't
    # callable from arbitrary origins. Use "*" only when there is no browser auth.
    cors_allow_origins: str = "*"
    # Per-IP request budget for the expensive evaluate endpoints (sliding window).
    rate_limit_per_minute: int = 30
    # Judge-only actions (score override, JUDGE-mode runs, un-redacted run views)
    # require ``Authorization: Bearer <token>`` when this is set. Empty (the
    # local/CI/demo default) leaves them open but logs a one-time warning — set
    # JUDGE_API_TOKEN in any deployment that exposes the judge surface.
    judge_api_token: str = ""
    # rules_url (Path B) SSRF allowlist. Comma-separated hostnames; empty = allow
    # any *public* host (private/loopback/link-local/metadata IPs are blocked
    # unconditionally, redirects are never followed). Set to lock Path B to known
    # rules hosts. PARTICIPANT runs cannot use rules_url at all (preset-only).
    rules_url_allowed_hosts: str = ""
    # Hard cap on a fetched rules page (Path B) to bound memory / cost abuse.
    rules_url_max_bytes: int = 2_000_000


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide cached :class:`Settings` instance."""
    return Settings()
