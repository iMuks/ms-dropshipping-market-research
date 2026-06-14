"""Demand specialist — v0.1.

Minimal first agent. Uses the Claude Agent SDK with WebSearch + WebFetch to
gather a *first cut* of demand evidence for a niche. Returns a structured
SpecialistOutput.

This is intentionally limited:
  - No DataForSEO yet (step 5 of PLAN.md).
  - No pytrends 36-month overlay yet (step 5 of PLAN.md).
  - No paired reviewer yet (step 5 of PLAN.md).
It exists to prove: the SDK works, the interface design works, a real agent
runs end-to-end. Future revisions extend `investigate()` to satisfy the full
D1–D9 criteria in REVIEW_CRITERIA.md.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone

from claude_agent_sdk import ClaudeAgentOptions, query

from niche_research.agents.base import SpecialistService
from niche_research.brief.models import (
    EvidenceURL,
    SectionName,
    SpecialistOutput,
    Verdict,
)

_SYSTEM_PROMPT = """You are the Demand specialist for a high-ticket dropshipping
research pipeline. Your job is to gather *real, source-cited* demand signals for
a niche the user names. You are not a generalist — you only produce demand
evidence.

Rules:
- Use the WebSearch tool to find current information. Use WebFetch to read
  specific pages. Never fabricate numbers, sources, or URLs.
- For every quantitative claim (search volume, trend direction, seasonality,
  growth %), cite the URL you got it from.
- High-ticket means buyers spend $300+ on considered purchases. Frame demand
  through that lens — search volume alone is not the goal; *buyer-intent*
  volume is.
- Be honest about uncertainty. If you can't verify something, say so.

Output format (return exactly this JSON in a fenced ```json block, nothing else after it):
{
  "head_keywords": ["...", "..."],
  "approx_total_monthly_volume": <int or null>,
  "trajectory": "rising" | "stable" | "declining" | "unknown",
  "seasonality_note": "<one sentence — when do peaks occur?>",
  "macro_trend_alignment": "<which macro trend, or 'none'>",
  "geographic_concentration": ["<country>", "<country>"],
  "evidence": [
    {"url": "<https://...>", "note": "<what this source supports>"}
  ],
  "summary": "<3-4 sentence narrative for a human reading the brief>",
  "confidence": "HIGH" | "MED" | "LOW",
  "caveats": "<what you couldn't verify>"
}
"""

_JSON_BLOCK_RE = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL)


class DemandSpecialist(SpecialistService):
    """v0.1 Demand specialist. Implements SpecialistService."""

    def __init__(self, model: str, max_turns: int = 12) -> None:
        self._model = model
        self._max_turns = max_turns

    async def investigate(self, niche: str) -> SpecialistOutput:
        prompt = (
            f"Niche: {niche}\n\n"
            "Investigate buyer demand for this niche as a high-ticket dropshipping "
            "opportunity. Use WebSearch + WebFetch as needed. Return the JSON block "
            "specified in your system prompt."
        )

        options = ClaudeAgentOptions(
            system_prompt=_SYSTEM_PROMPT,
            allowed_tools=["WebSearch", "WebFetch"],
            model=self._model,
            max_turns=self._max_turns,
        )

        transcript_chunks: list[str] = []
        async for message in query(prompt=prompt, options=options):
            # The SDK emits structured message objects. We collect any text
            # the assistant produced; tool calls are handled internally.
            text = _extract_text(message)
            if text:
                transcript_chunks.append(text)

        full_transcript = "\n".join(transcript_chunks)
        parsed = _parse_json_block(full_transcript)

        evidence = [
            EvidenceURL(
                url=item["url"],
                fetched_at=datetime.now(timezone.utc),
                note=item.get("note", ""),
            )
            for item in parsed.get("evidence", [])
            if isinstance(item, dict) and item.get("url")
        ]

        return SpecialistOutput(
            niche=niche,
            section=SectionName.DEMAND,
            findings={
                "head_keywords": parsed.get("head_keywords", []),
                "approx_total_monthly_volume": parsed.get("approx_total_monthly_volume"),
                "trajectory": parsed.get("trajectory", "unknown"),
                "seasonality_note": parsed.get("seasonality_note", ""),
                "macro_trend_alignment": parsed.get("macro_trend_alignment", "none"),
                "geographic_concentration": parsed.get("geographic_concentration", []),
                "confidence": parsed.get("confidence", "LOW"),
                "caveats": parsed.get("caveats", ""),
            },
            summary=parsed.get("summary", full_transcript[:800]),
            evidence=evidence,
            verdict=Verdict.UNREVIEWED,
        )


def _extract_text(message: object) -> str:
    """Best-effort text extraction from an SDK message object.

    The SDK uses typed message objects; we duck-type for `content` or `text`
    to stay resilient across minor SDK versions.
    """
    if isinstance(message, str):
        return message
    content = getattr(message, "content", None)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            text = getattr(block, "text", None) or (block.get("text") if isinstance(block, dict) else None)
            if text:
                parts.append(text)
        return "".join(parts)
    text = getattr(message, "text", None)
    return text if isinstance(text, str) else ""


def _parse_json_block(transcript: str) -> dict:
    """Extract the final ```json block. Raise if the model didn't produce one."""
    matches = _JSON_BLOCK_RE.findall(transcript)
    if not matches:
        raise ValueError(
            "DemandSpecialist: model did not return a ```json block. "
            "Transcript was:\n" + transcript[-2000:]
        )
    return json.loads(matches[-1])
