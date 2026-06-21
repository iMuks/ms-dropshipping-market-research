"""Single source of truth for runtime configuration.

Loads from a `.env` file (search order below) or from environment variables.
Constructed once at the composition root (`cli.py`) and passed to services
via constructor injection — never read elsewhere.

When the package is installed globally (e.g. `uv tool install` or `pipx`),
the install dir is not a useful place to look for a user's `.env`. So this
module searches, in order:

  1. `$NICHE_RESEARCH_ENV_FILE` if set
  2. `./.env` in the current working directory
  3. `~/.config/niche-research/.env`
  4. The bundled `engine/.env` next to the source (dev mode only)

The first hit wins. If no file is found, `BaseSettings` still reads from
process environment variables — that is the supported deployment path for
secret managers and CI.
"""
from __future__ import annotations

import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENGINE_ROOT = Path(__file__).resolve().parent.parent.parent


def _resolve_env_file() -> Path | None:
    explicit = os.environ.get("NICHE_RESEARCH_ENV_FILE")
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit).expanduser())
    candidates.extend(
        [
            Path.cwd() / ".env",
            Path.home() / ".config" / "niche-research" / ".env",
            _ENGINE_ROOT / ".env",
        ]
    )
    for path in candidates:
        if path.is_file():
            return path
    return None


_ENV_FILE = _resolve_env_file()


class Config(BaseSettings):
    """Runtime configuration. One instance per process."""

    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,  # None = read env vars only; pydantic-settings handles it
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

    # --- Anthropic ---
    # Optional: when absent, the engine runs in "subscription" auth mode and
    # relies on the Claude Code CLI's own login (Pro/Max). When present, the
    # engine runs in "api-key" mode (pay-per-token billing). See `auth_mode`.
    anthropic_api_key: str | None = Field(None, alias="ANTHROPIC_API_KEY")

    # --- Models ---
    # Used by the single-section debug commands and as fallbacks. The full
    # `run` pipeline takes its model engines from pipeline.yaml (`engines:`),
    # which is the single source of truth for a full-pipeline run.
    orchestrator_model: str = Field("claude-opus-4-8", alias="ORCHESTRATOR_MODEL")
    specialist_model: str = Field("claude-sonnet-4-6", alias="SPECIALIST_MODEL")
    reviewer_model: str = Field("claude-opus-4-8", alias="REVIEWER_MODEL")

    # --- Budget ---
    cost_cap_usd_per_brief: float = Field(5.0, alias="COST_CAP_USD_PER_BRIEF")

    # --- Langfuse (optional until step 3 wires it) ---
    langfuse_host: str = Field("http://localhost:3000", alias="LANGFUSE_HOST")
    langfuse_public_key: str | None = Field(None, alias="LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: str | None = Field(None, alias="LANGFUSE_SECRET_KEY")

    @property
    def auth_mode(self) -> str:
        """How the engine will authenticate the Claude Agent SDK.

        - ``"api-key"``    — an API key is configured (pay-per-token billing).
        - ``"subscription"`` — no key; rely on the Claude Code CLI login (Pro/Max).
        """
        return "api-key" if self.anthropic_api_key else "subscription"

    @property
    def engine_root(self) -> Path:
        return _ENGINE_ROOT

    @property
    def briefs_dir(self) -> Path:
        """User-writable briefs directory (`~/niche-research/briefs/`)."""
        return Path.home() / "niche-research" / "briefs"

    @property
    def env_file_used(self) -> Path | None:
        """Path of the .env actually loaded, or None if pure env-var mode."""
        return _ENV_FILE
