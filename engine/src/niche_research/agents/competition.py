"""Competition specialist — v0.1.

Produces §2 Competition: the organic SERP landscape plus *marketplace
bestseller intel* — the **major top-N products** in the category across
Amazon / Temu / AliExpress, with price, review count, and brand. This is the
"top 5 products to analyze" the brief uses to confirm a category has real
high-ticket ($300+) buyers and to map price-tier distribution.

SDK plumbing lives in ``_sdk.py``; this file is the competition prompt + schema.
"""
from __future__ import annotations

from niche_research.agents._sdk import build_evidence, run_specialist_query
from niche_research.agents.base import SpecialistService
from niche_research.brief.models import (
    SectionName,
    SpecialistOutput,
    Verdict,
)

_SYSTEM_PROMPT = """You are the Competition specialist for a high-ticket
dropshipping research pipeline. You produce ONLY competition + marketplace
evidence for a niche the user names — never demand, supply, or community data.

Two jobs:
1. Organic SERP: fetch the top commercial-intent results for the niche and note
   positioning, price tier, and content quality.
2. MARKETPLACE BESTSELLER INTEL (the priority): identify the *major top {top_n}
   products* selling in this category across these marketplaces: {marketplaces}.
   For each product capture: name, marketplace, price (USD), review_count,
   brand, and the product URL.

Rules:
- Use WebSearch to find listings and WebFetch to read product/category pages.
  Never fabricate a product, price, review count, brand, or URL. If you can only
  verify 3 of {top_n}, return 3 and say so in caveats — do NOT invent the rest.
- High-ticket means $300+. Explicitly flag whether at least one verified
  bestseller sits at >= $300 (this is the signal the category has high-ticket
  buyers). If nothing clears $300, set high_ticket_validated=false.
- Compute a price-tier distribution from the products you actually found.

Output format (return exactly this JSON in a fenced ```json block, nothing else after it):
{
  "top_products": [
    {
      "name": "<product name>",
      "marketplace": "amazon" | "temu" | "aliexpress" | "shein" | "other",
      "price_usd": <number or null>,
      "review_count": <int or null>,
      "brand": "<brand or 'unbranded'>",
      "url": "<https://...>"
    }
  ],
  "serp_results": [
    {"title": "<...>", "url": "<https://...>", "price_tier": "<$ range>", "positioning": "<one phrase>", "content_quality": <1-5>}
  ],
  "price_tier_distribution": {"under_100": <int>, "100_300": <int>, "300_1k": <int>, "over_1k": <int>},
  "high_ticket_validated": <true|false>,
  "median_price_usd": <number or null>,
  "evidence": [
    {"url": "<https://...>", "note": "<what this source supports>"}
  ],
  "summary": "<3-4 sentence narrative: how crowded, how fragmented, where the high-ticket gap is>",
  "section_score": <float 0.0-1.0 — your evidence-grounded self-assessment of competitive opportunity>,
  "confidence": "HIGH" | "MED" | "LOW",
  "caveats": "<what you couldn't verify; which products you couldn't confirm>"
}
"""


class CompetitionSpecialist(SpecialistService):
    """v0.1 Competition specialist with top-N marketplace product intel."""

    def __init__(
        self,
        model: str,
        max_turns: int = 14,
        top_n_products: int = 5,
        marketplaces: list[str] | None = None,
    ) -> None:
        self._model = model
        self._max_turns = max_turns
        self._top_n = top_n_products
        self._marketplaces = marketplaces or ["amazon", "temu", "aliexpress"]

    async def investigate(self, niche: str) -> SpecialistOutput:
        system_prompt = _SYSTEM_PROMPT.format(
            top_n=self._top_n,
            marketplaces=", ".join(self._marketplaces),
        )
        prompt = (
            f"Niche: {niche}\n\n"
            f"Analyze the competition. Identify the major top {self._top_n} products "
            f"selling in this category across {', '.join(self._marketplaces)}, plus the "
            "organic SERP landscape. Use WebSearch + WebFetch. Return the JSON block "
            "specified in your system prompt."
        )

        parsed = await run_specialist_query(
            system_prompt=system_prompt,
            prompt=prompt,
            model=self._model,
            max_turns=self._max_turns,
        )

        return SpecialistOutput(
            niche=niche,
            section=SectionName.COMPETITION,
            findings={
                "top_products": parsed.get("top_products", []),
                "serp_results": parsed.get("serp_results", []),
                "price_tier_distribution": parsed.get("price_tier_distribution", {}),
                "high_ticket_validated": parsed.get("high_ticket_validated"),
                "median_price_usd": parsed.get("median_price_usd"),
                "section_score": parsed.get("section_score"),
                "confidence": parsed.get("confidence", "LOW"),
                "caveats": parsed.get("caveats", ""),
            },
            summary=parsed.get("summary", ""),
            evidence=build_evidence(parsed.get("evidence")),
            verdict=Verdict.UNREVIEWED,
        )
