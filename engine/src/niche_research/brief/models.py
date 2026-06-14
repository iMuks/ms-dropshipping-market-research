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
