"""Declarative pipeline configuration loaded from ``pipeline.yaml``.

Where ``config.py`` owns *secrets and runtime* (API keys, cost caps), this
module owns the *shape of a run*: which specialists execute, which model
engine each uses, the scoring weights, and the cross-cutting gates.

Keeping this in YAML (not code) means a non-engineer can enable a section or
swap a model engine without touching Python — and the orchestrator reads one
source of truth (CONVENTIONS.md: DRY, single source of truth).

Search order (first hit wins):
  1. ``$NICHE_RESEARCH_PIPELINE_FILE``
  2. ``./pipeline.yaml`` in the current working directory
  3. ``~/.config/niche-research/pipeline.yaml``
  4. the bundled ``engine/pipeline.yaml`` next to the source (default)
"""
from __future__ import annotations

import os
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field

from niche_research.brief.models import SectionName

_ENGINE_ROOT = Path(__file__).resolve().parent.parent.parent
_BUNDLED_PIPELINE = _ENGINE_ROOT / "pipeline.yaml"


def resolve_pipeline_file() -> Path:
    """Return the pipeline.yaml to load, honoring the search order above."""
    explicit = os.environ.get("NICHE_RESEARCH_PIPELINE_FILE")
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit).expanduser())
    candidates.extend(
        [
            Path.cwd() / "pipeline.yaml",
            Path.home() / ".config" / "niche-research" / "pipeline.yaml",
            _BUNDLED_PIPELINE,
        ]
    )
    for path in candidates:
        if path.is_file():
            return path
    # The bundled file ships with the package; if it's somehow missing the
    # loader will raise a clear FileNotFoundError naming the expected path.
    return _BUNDLED_PIPELINE


class Engines(BaseModel):
    """Model engine (a Claude model ID) per role."""

    orchestrator: str = "claude-opus-4-8"
    specialist: str = "claude-sonnet-4-6"
    reviewer: str = "claude-opus-4-8"


class Weights(BaseModel):
    demand: float = 0.22
    competition: float = 0.18
    supply: float = 0.25
    traffic: float = 0.13
    community: float = 0.22


class Gates(BaseModel):
    min_aov_usd: float = 300.0
    min_gross_margin: float = 0.25
    approve_threshold: float = 0.70


class RedditCfg(BaseModel):
    max_subreddits: int = 4
    comments_per_post: int = 25
    timeframe: str = "year"


class DiscoveryCfg(BaseModel):
    """Config for `suggest` (discovery mode)."""

    engine: str = "specialist"
    max_turns: int = 14
    default_count: int = 10
    min_aov_usd: float = 300.0


class SpecialistCfg(BaseModel):
    """One specialist's run config. Heterogeneous fields are optional with
    defaults so a single typed model covers every section (extra YAML keys are
    ignored rather than rejected, so adding a future option is non-breaking)."""

    model_config = ConfigDict(extra="ignore")

    id: str
    enabled: bool = True
    engine: str = "specialist"
    max_turns: int = 12

    # Competition options.
    top_n_products: int = 5
    marketplaces: list[str] = Field(default_factory=lambda: ["amazon", "temu", "aliexpress"])

    # Community options.
    reddit: RedditCfg = Field(default_factory=RedditCfg)
    top_needs: int = 5
    top_unmet: int = 3

    @property
    def section(self) -> SectionName:
        """Map the pipeline id to the brief SectionName. ``community`` is the
        pipeline-facing name for the COMMUNITY_NEEDS section."""
        return _ID_TO_SECTION[self.id]


_ID_TO_SECTION: dict[str, SectionName] = {
    "demand": SectionName.DEMAND,
    "competition": SectionName.COMPETITION,
    "supply": SectionName.SUPPLY,
    "traffic": SectionName.TRAFFIC,
    "community": SectionName.COMMUNITY_NEEDS,
}


class PipelineConfig(BaseModel):
    """Parsed ``pipeline.yaml``. Construct via :meth:`load`."""

    version: int = 1
    name: str = "pipeline-1-market-research"
    geo_default: str = "US"
    engines: Engines = Field(default_factory=Engines)
    weights: Weights = Field(default_factory=Weights)
    gates: Gates = Field(default_factory=Gates)
    discovery: DiscoveryCfg = Field(default_factory=DiscoveryCfg)
    specialists: list[SpecialistCfg] = Field(default_factory=list)

    @classmethod
    def load(cls, path: Path | None = None) -> "PipelineConfig":
        path = path or resolve_pipeline_file()
        if not path.is_file():
            raise FileNotFoundError(
                f"pipeline.yaml not found at {path}. "
                "Set NICHE_RESEARCH_PIPELINE_FILE or create ./pipeline.yaml."
            )
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return cls.model_validate(data)

    def resolve_model(self, spec: SpecialistCfg) -> str:
        """Resolve a specialist's ``engine:`` name to a concrete model ID.

        Unknown engine names fall back to the specialist engine rather than
        crashing a run over a typo — surfaced via the value, not an exception.
        """
        return getattr(self.engines, spec.engine, self.engines.specialist)

    def enabled_specialists(self) -> list[SpecialistCfg]:
        """Enabled specialists that have a known section mapping."""
        return [s for s in self.specialists if s.enabled and s.id in _ID_TO_SECTION]

    def weight_for(self, section: SectionName) -> float:
        return getattr(self.weights, _SECTION_TO_WEIGHT_ATTR[section])


_SECTION_TO_WEIGHT_ATTR: dict[SectionName, str] = {
    SectionName.DEMAND: "demand",
    SectionName.COMPETITION: "competition",
    SectionName.SUPPLY: "supply",
    SectionName.TRAFFIC: "traffic",
    SectionName.COMMUNITY_NEEDS: "community",
}
