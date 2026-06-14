"""Single source of truth for runtime configuration.

Loads from `engine/.env` (or env vars). Constructed once at the composition root
(`cli.py`) and passed to services via constructor injection — never read elsewhere.
"""
from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENGINE_ROOT = Path(__file__).resolve().parent.parent.parent


class Config(BaseSettings):
    """Runtime configuration. One instance per process."""

    model_config = SettingsConfigDict(
        env_file=_ENGINE_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

    # --- Anthropic ---
    anthropic_api_key: str = Field(..., alias="ANTHROPIC_API_KEY")

    # --- Models ---
    orchestrator_model: str = Field("claude-opus-4-7", alias="ORCHESTRATOR_MODEL")
    specialist_model: str = Field("claude-sonnet-4-6", alias="SPECIALIST_MODEL")
    reviewer_model: str = Field("claude-opus-4-7", alias="REVIEWER_MODEL")

    # --- Budget ---
    cost_cap_usd_per_brief: float = Field(5.0, alias="COST_CAP_USD_PER_BRIEF")

    # --- Langfuse (optional until step 3 wires it) ---
    langfuse_host: str = Field("http://localhost:3000", alias="LANGFUSE_HOST")
    langfuse_public_key: str | None = Field(None, alias="LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: str | None = Field(None, alias="LANGFUSE_SECRET_KEY")

    @property
    def engine_root(self) -> Path:
        return _ENGINE_ROOT

    @property
    def briefs_dir(self) -> Path:
        return _ENGINE_ROOT / "briefs"
