"""Service interfaces for agents — Single Responsibility + Dependency Inversion.

Specialists produce sections of the brief; reviewers grade them. Concrete
implementations are wired in `cli.py` (the composition root). No service
constructs another service directly — they depend on these interfaces.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from niche_research.brief.models import DiscoveryResult, SpecialistOutput, Verdict


class SpecialistService(ABC):
    """Produces one section of the opportunity brief for a given niche."""

    @abstractmethod
    async def investigate(self, niche: str) -> SpecialistOutput:
        """Run the specialist's research and return a structured output."""


class DiscoveryService(ABC):
    """Suggests candidate high-ticket products to research (the inverse of a
    specialist: instead of validating a named niche, it *finds* niches).

    Segregated from SpecialistService (ISP): discovery and section-research are
    different jobs with different output shapes, so they are different interfaces.
    """

    @abstractmethod
    async def discover(self, seed: str | None, count: int) -> DiscoveryResult:
        """Return up to ``count`` candidate products, optionally focused by
        ``seed`` (a category/interest/constraint); ``None`` = general discovery."""


class ReviewVerdict:
    """Reviewer's verdict on a specialist's output — kept simple for v0.1."""

    def __init__(
        self,
        verdict: Verdict,
        per_criterion: dict[str, Verdict],
        notes: str,
        revision_requested: bool = False,
    ) -> None:
        self.verdict = verdict
        self.per_criterion = per_criterion
        self.notes = notes
        self.revision_requested = revision_requested


class ReviewerService(ABC):
    """Reviews a SpecialistOutput against the relevant section of REVIEW_CRITERIA.md."""

    @abstractmethod
    async def review(self, draft: SpecialistOutput) -> ReviewVerdict:
        """Apply the section's criteria and return a verdict."""
