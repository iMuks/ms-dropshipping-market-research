"""Pipeline 1 orchestrator — runs the enabled specialists and assembles a brief.

Depends only on the ``SpecialistService`` interface (Dependency Inversion);
concrete specialists are constructed in the composition root (``cli.py``) and
handed in keyed by section. The orchestrator runs them concurrently, scores
what came back, and renders the markdown brief via ``BriefWriter``.

Honest by construction: while Supply (strict), Traffic, and the paired
reviewers are not yet implemented, the verdict is capped at ``PROVISIONAL`` —
the engine never emits ``APPROVED`` on a partial run.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from niche_research.agents.base import SpecialistService
from niche_research.brief.models import SectionName, SpecialistOutput
from niche_research.brief.writer import BriefWriter, slugify
from niche_research.pipeline import PipelineConfig


@dataclass
class RunResult:
    niche: str
    verdict: str
    score: float
    brief_path: Path
    sections_produced: list[SectionName]
    failures: dict[SectionName, str] = field(default_factory=dict)


class Pipeline1Orchestrator:
    """Runs specialists concurrently and writes the assembled brief."""

    def __init__(
        self,
        *,
        specialists: dict[SectionName, SpecialistService],
        pipeline: PipelineConfig,
        writer: BriefWriter,
        briefs_dir: Path,
    ) -> None:
        self._specialists = specialists
        self._pipeline = pipeline
        self._writer = writer
        self._briefs_dir = briefs_dir

    async def run(self, niche: str) -> RunResult:
        sections = list(self._specialists.keys())

        # Run every specialist concurrently. A failure in one section must not
        # sink the whole brief — capture it and mark that section UNAVAILABLE.
        results = await asyncio.gather(
            *(self._specialists[s].investigate(niche) for s in sections),
            return_exceptions=True,
        )

        outputs: dict[SectionName, SpecialistOutput] = {}
        failures: dict[SectionName, str] = {}
        for section, result in zip(sections, results):
            if isinstance(result, Exception):
                failures[section] = f"{type(result).__name__}: {result}"
            else:
                outputs[section] = result

        score, contributions = self._score(outputs)
        verdict, reasons = self._verdict(outputs)
        mode = "engine-CLI" if not failures else "engine-CLI (partial)"

        run_date = datetime.now(timezone.utc).date().isoformat()
        markdown = self._writer.render(
            niche=niche,
            geo=self._pipeline.geo_default,
            run_date=run_date,
            verdict=verdict,
            score=score,
            mode=mode,
            contributions=contributions,
            outputs=outputs,
            failures=failures,
            provisional_reasons=reasons,
        )

        self._briefs_dir.mkdir(parents=True, exist_ok=True)
        brief_path = self._briefs_dir / f"{slugify(niche)}-{run_date}.md"
        brief_path.write_text(markdown, encoding="utf-8")

        return RunResult(
            niche=niche,
            verdict=verdict,
            score=score,
            brief_path=brief_path,
            sections_produced=list(outputs.keys()),
            failures=failures,
        )

    # --- scoring ---------------------------------------------------------------

    def _score(
        self, outputs: dict[SectionName, SpecialistOutput]
    ) -> tuple[float, dict[SectionName, float]]:
        """Weighted score over sections that returned a numeric self-assessment.

        Weights are renormalized over the present sections so a 3-of-5 run isn't
        unfairly capped — the missing weight isn't silently counted as zero.
        """
        scored: dict[SectionName, float] = {}
        for section, out in outputs.items():
            raw = out.findings.get("section_score")
            value = _coerce_unit(raw)
            if value is not None:
                scored[section] = value

        if not scored:
            return 0.0, {}

        total_weight = sum(self._pipeline.weight_for(s) for s in scored)
        if total_weight <= 0:
            return 0.0, {}

        contributions: dict[SectionName, float] = {}
        final = 0.0
        for section, value in scored.items():
            norm_weight = self._pipeline.weight_for(section) / total_weight
            contrib = norm_weight * value
            contributions[section] = contrib
            final += contrib
        return round(final, 3), contributions

    def _verdict(
        self, outputs: dict[SectionName, SpecialistOutput]
    ) -> tuple[str, list[str]]:
        """Verdict + reasons. Capped at PROVISIONAL until the pipeline is whole."""
        reasons: list[str] = []
        if SectionName.SUPPLY not in outputs:
            reasons.append("Supply (strict) not produced")
        if SectionName.TRAFFIC not in outputs:
            reasons.append("Traffic not produced")
        reasons.append("paired reviewers not yet wired (no F1–F13 reconciliation)")
        # Today this is always PROVISIONAL by design; the structure is ready for
        # APPROVED/REJECTED once the remaining specialists + reviewers land.
        return "PROVISIONAL", reasons


def _coerce_unit(value: object) -> float | None:
    """Coerce a model-supplied score to a float in [0, 1], or None if unusable."""
    try:
        f = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return max(0.0, min(1.0, f))
