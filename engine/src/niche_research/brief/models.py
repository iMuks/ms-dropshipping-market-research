"""Pydantic models shared across the engine.

These are the typed artifacts services exchange. Schema lives in
`brief/SCHEMA.md` and `brief/REVIEW_CRITERIA.md`; this file makes those
contracts executable.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, HttpUrl


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SectionName(str, Enum):
    DEMAND = "demand"
    COMPETITION = "competition"
    SUPPLY = "supply"
    TRAFFIC = "traffic"
    COMMUNITY_NEEDS = "community_needs"


class Verdict(str, Enum):
    PASS = "PASS"
    WEAK = "WEAK"
    FAIL = "FAIL"
    UNREVIEWED = "UNREVIEWED"  # producer ran, reviewer hasn't yet


class EvidenceURL(BaseModel):
    url: HttpUrl
    fetched_at: datetime
    note: str = ""


class SpecialistOutput(BaseModel):
    """The artifact a SpecialistService produces. Reviewers consume this."""

    niche: str
    section: SectionName
    findings: dict[str, Any] = Field(
        default_factory=dict,
        description="Structured per-section data — keys match REVIEW_CRITERIA.md criterion IDs where possible.",
    )
    summary: str
    evidence: list[EvidenceURL] = Field(default_factory=list)
    verdict: Verdict = Verdict.UNREVIEWED
    produced_at: datetime = Field(default_factory=_utcnow)
    cost_usd: float = 0.0


class ProductCandidate(BaseModel):
    """One suggested high-ticket dropshipping product/niche from discovery mode.

    Each candidate is a *lead* to deep-validate with the full pipeline
    (`niche-research run "<name>"`), not a finished brief.
    """

    name: str
    category: str = ""
    price_range_usd: str = ""  # e.g. "$400–$900"
    est_aov_usd: float | None = None
    demand_signal: str = ""  # short phrase, e.g. "rising, ~40k searches/mo"
    competition_level: str = "unknown"  # low | medium | high | unknown
    supplier_availability: str = ""  # short phrase
    opportunity_score: float = 0.0  # 0..1, higher = stronger lead
    rationale: str = ""  # why this is a high-ticket opportunity
    evidence: list[EvidenceURL] = Field(default_factory=list)


class DiscoveryResult(BaseModel):
    """A ranked list of candidate products produced by discovery mode."""

    seed: str | None = None  # optional focus the user gave, or None for general
    geo: str = "US"
    candidates: list[ProductCandidate] = Field(default_factory=list)
    summary: str = ""
    produced_at: datetime = Field(default_factory=_utcnow)
