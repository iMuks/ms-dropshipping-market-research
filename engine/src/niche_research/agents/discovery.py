"""Discovery specialist — suggest a ranked list of high-ticket products.

The inverse of the section specialists: instead of validating a niche the user
names, this *finds* candidate high-ticket dropshipping products/items, ranks
them, and returns leads to deep-validate with the full pipeline
(`niche-research run "<name>"`).

SDK plumbing lives in ``_sdk.py``; this file is the discovery prompt + schema.
"""
from __future__ import annotations

from pydantic import ValidationError

from niche_research.agents._sdk import build_evidence, run_specialist_query
from niche_research.agents.base import DiscoveryService
from niche_research.brief.models import DiscoveryResult, ProductCandidate

_SYSTEM_PROMPT = """You are the Discovery specialist for a high-ticket
dropshipping research pipeline. Your job is to SUGGEST candidate products/niches
worth researching — not to validate one. Return a ranked shortlist.

What "high-ticket dropshipping" requires (filter HARD on these):
- **AOV >= ${min_aov}** — typical order value at or above this. Reject impulse /
  low-ticket items.
- **Considered purchase** — buyers research before buying (multi-word queries,
  comparison threads), not impulse.
- **Dropship-operable** — a real supplier path exists; NOT perishable, heavily
  regulated, hazmat, counterfeit-prone, or so oversized it can't ship affordably.
- **Real demand + a wedge** — there is search/community demand AND a gap
  (stale incumbents, unmet need, weak high-ticket options).

Rules:
- Use WebSearch + WebFetch. Cite a real URL for the signals you claim (a price
  range, a demand stat, a bestseller). NEVER invent products, prices, or URLs.
- Prefer specific, researchable products over vague categories: "infrared sauna
  blankets" not "wellness". Each candidate must be something you could then run a
  full niche validation on.
- Diversify across macro-trends (aging-in-place, home automation, longevity,
  remote work, EV/outdoor, sustainability) — don't return 10 variants of one item.
- If you are unsure a candidate clears the AOV bar, leave it OUT rather than pad.

Return exactly {count} candidates (or fewer if you can't verify {count}).

Output format (return exactly this JSON in a fenced ```json block, nothing else after it):
{{
  "candidates": [
    {{
      "name": "<specific product/niche>",
      "category": "<broader category>",
      "price_range_usd": "<e.g. $400-$900>",
      "est_aov_usd": <number or null>,
      "demand_signal": "<short phrase, e.g. 'rising, comparison threads on Reddit'>",
      "competition_level": "low" | "medium" | "high" | "unknown",
      "supplier_availability": "<short phrase, e.g. 'US dropship via Spocket'>",
      "opportunity_score": <float 0.0-1.0 — your overall lead strength>,
      "rationale": "<1-2 sentences: why high-ticket + where the wedge is>",
      "evidence": [{{"url": "<https://...>", "note": "<what this supports>"}}]
    }}
  ],
  "summary": "<2-3 sentence overview of the shortlist and the strongest theme>"
}}
"""


class DiscoverySpecialist(DiscoveryService):
    """Suggests ranked high-ticket product candidates."""

    def __init__(self, model: str, max_turns: int = 14, min_aov_usd: float = 300.0) -> None:
        self._model = model
        self._max_turns = max_turns
        self._min_aov = min_aov_usd

    async def discover(self, seed: str | None, count: int) -> DiscoveryResult:
        system_prompt = _SYSTEM_PROMPT.format(min_aov=int(self._min_aov), count=count)
        focus = (
            f"Focus the discovery on: {seed}.\n\n"
            if seed
            else "No specific focus — survey strong high-ticket categories broadly.\n\n"
        )
        prompt = (
            f"{focus}"
            f"Suggest {count} high-ticket dropshipping product candidates (AOV >= "
            f"${int(self._min_aov)}), ranked by opportunity. Use WebSearch + WebFetch and "
            "cite real URLs. Return the JSON block specified in your system prompt."
        )

        parsed = await run_specialist_query(
            system_prompt=system_prompt,
            prompt=prompt,
            model=self._model,
            max_turns=self._max_turns,
        )

        candidates: list[ProductCandidate] = []
        for item in parsed.get("candidates", []) or []:
            if not (isinstance(item, dict) and item.get("name")):
                continue
            try:
                candidates.append(
                    ProductCandidate(
                        name=str(item["name"]),
                        category=str(item.get("category", "")),
                        price_range_usd=str(item.get("price_range_usd", "")),
                        est_aov_usd=_coerce_float(item.get("est_aov_usd")),
                        demand_signal=str(item.get("demand_signal", "")),
                        competition_level=str(item.get("competition_level", "unknown")),
                        supplier_availability=str(item.get("supplier_availability", "")),
                        opportunity_score=_clamp01(item.get("opportunity_score")),
                        rationale=str(item.get("rationale", "")),
                        evidence=build_evidence(item.get("evidence")),
                    )
                )
            except ValidationError:
                continue

        # Strongest leads first; the model's ranking is advisory, the score is canonical.
        candidates.sort(key=lambda c: c.opportunity_score, reverse=True)

        return DiscoveryResult(
            seed=seed,
            candidates=candidates,
            summary=str(parsed.get("summary", "")),
        )


def _coerce_float(value: object) -> float | None:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def _clamp01(value: object) -> float:
    f = _coerce_float(value)
    if f is None:
        return 0.0
    return max(0.0, min(1.0, f))
