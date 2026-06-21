"""Demand specialist — v0.3 (full D1–D9 rubric).

Gathers source-cited demand evidence for a niche, covering the complete §1
Demand criteria in REVIEW_CRITERIA.md:
  - D1 addressable search volume + per-keyword intent
  - D2 multi-year (24–36 month) trajectory with YoY growth per year
  - D3 multi-year seasonality REPETITION (peak month repeats across years)
  - D4 seasonality profile (peak-to-trough)
  - D5 buyer-intent mix
  - D6 geographic breakdown (per-region demand)
  - D7 macro-trend alignment
  - D8 PREDICTED next seasonal window (start month, duration, magnitude, confidence)
  - D9 query freshness
  - recommended build → launch lead time

The engine has not wired pytrends/DataForSEO yet (PLAN.md step 5), so this uses
the Claude Agent SDK with WebSearch + WebFetch over multi-year Google Trends and
keyword sources. It must cite the multi-year Trends URL and be honest (LOW
confidence + caveats) where exact monthly indices aren't extractable from the
web — never fabricate numbers.
"""
from __future__ import annotations

from niche_research.agents._sdk import build_evidence, run_specialist_query
from niche_research.agents.base import SpecialistService
from niche_research.brief.models import (
    SectionName,
    SpecialistOutput,
    Verdict,
)

_SYSTEM_PROMPT = """You are the Demand specialist for a high-ticket dropshipping
research pipeline. You produce ONLY demand evidence — real and source-cited.

You MUST analyze demand over a MULTI-YEAR window (24–36 months), not a single
year. One-year spikes are often viral noise; only peaks that REPEAT across years
prove a real, plannable seasonal window. You also forecast the NEXT window.

Method (use WebSearch + WebFetch; cite a URL for every quantitative claim):
1. Pull a MULTI-YEAR Google Trends curve for the niche + its head keywords. Use a
   24–36 month (or 5-year) range and cite the exact Trends URL (it encodes the
   date range and geo). This is the backbone of D2/D3.
2. From the multi-year curve, determine, per year: average level (for YoY growth),
   the PEAK month, and the peak-to-trough ratio. Then check whether the peak month
   REPEATS in the same calendar window across years (drift ≤ 30 days = real
   seasonality; different peak months = random spike).
3. Pull Google Trends "by region/subregion" to get the GEOGRAPHIC breakdown — the
   top countries/regions and their relative demand. Cite the by-region URL.
4. Identify the top 10–20 commercial-intent keywords with rough monthly volumes,
   each with its source URL, and label each keyword's intent
   (transactional / commercial / informational). Estimate the % that is
   transactional+commercial (buyer intent) and the % of queries seen in the last
   12 months (freshness).
5. Map the niche to a rising macro trend (remote work, longevity, EV, aging-in-place,
   home automation, sustainability, …) with a cited source.
6. FORECAST the next seasonal window from the repeating multi-year pattern: start
   month (MM/YYYY), expected duration in weeks, magnitude vs base, and a confidence
   (HIGH/MED/LOW) with reasoning grounded in the overlay. Then state the recommended
   build→launch lead time in weeks (how far ahead of the window the store must be live).

High-ticket lens: buyers spend $300+ on considered purchases — value buyer-intent
demand over raw volume. Be honest: if you cannot extract exact monthly indices from
the web, give your best read, mark confidence LOW, and explain in caveats. NEVER
fabricate numbers, peaks, or URLs.

Output format (return exactly this JSON in a fenced ```json block, nothing else after it):
{
  "head_keywords": ["...", "..."],
  "keyword_volumes": [
    {"keyword": "...", "approx_monthly_volume": <int or null>, "intent": "transactional|commercial|informational", "url": "<https://...>"}
  ],
  "approx_total_monthly_volume": <int or null>,
  "buyer_intent_mix_pct": {"transactional_commercial": <int 0-100 or null>, "informational": <int 0-100 or null>},
  "trajectory": "rising" | "stable" | "declining" | "unknown",
  "multi_year": {
    "window_months": <int — should be 24-36>,
    "trends_url": "<multi-year Google Trends URL>",
    "yoy_growth_pct_by_year": [{"year": <int>, "growth_pct": <number or null>}],
    "peak_month_by_year": [{"year": <int>, "peak_month": "<Jan..Dec>"}],
    "peak_to_trough_ratio_by_year": [{"year": <int>, "ratio": <number or null>}],
    "peak_month_drift_days": <int or null>,
    "seasonality_profile": "year-round" | "seasonal-window" | "single-spike" | "unknown",
    "repeats_across_years": <true|false|null>
  },
  "seasonality_note": "<2-3 sentences: do peaks repeat across years in the same window?>",
  "predicted_next_window": {
    "start_month": "<MM/YYYY>",
    "duration_weeks": <int or null>,
    "magnitude_vs_base": "<e.g. '2.1x base'>",
    "confidence": "HIGH" | "MED" | "LOW",
    "reasoning": "<grounded in the multi-year overlay>"
  },
  "recommended_build_to_launch_lead_weeks": <int or null>,
  "geographic_breakdown": [
    {"geo": "<country/region>", "relative_demand": "<index 0-100 or High/Med/Low>", "note": "<short>", "url": "<trends-by-region URL>"}
  ],
  "macro_trend_alignment": "<which macro trend>",
  "macro_trend_url": "<source URL>",
  "query_freshness_pct": <int 0-100 or null>,
  "evidence": [
    {"url": "<https://...>", "note": "<what this source supports>"}
  ],
  "summary": "<3-4 sentence narrative for a human reading the brief>",
  "section_score": <float 0.0-1.0 — grounded in D1-D9; lower it hard if D2/D3/D8 are unmet>,
  "confidence": "HIGH" | "MED" | "LOW",
  "caveats": "<what you couldn't verify — especially if monthly indices were not extractable>"
}
"""


class DemandSpecialist(SpecialistService):
    """v0.3 Demand specialist covering the full D1–D9 criteria."""

    def __init__(self, model: str, max_turns: int = 14) -> None:
        self._model = model
        self._max_turns = max_turns

    async def investigate(self, niche: str) -> SpecialistOutput:
        prompt = (
            f"Niche: {niche}\n\n"
            "Investigate buyer demand for this niche as a high-ticket dropshipping "
            "opportunity. Analyze a MULTI-YEAR (24–36 month) Google Trends window, "
            "determine whether seasonal peaks REPEAT across years, give the GEOGRAPHIC "
            "breakdown, and FORECAST the next seasonal window + build→launch lead time. "
            "Use WebSearch + WebFetch and cite a URL for every number. Return the JSON "
            "block specified in your system prompt."
        )

        parsed = await run_specialist_query(
            system_prompt=_SYSTEM_PROMPT,
            prompt=prompt,
            model=self._model,
            max_turns=self._max_turns,
        )

        return SpecialistOutput(
            niche=niche,
            section=SectionName.DEMAND,
            findings={
                "head_keywords": parsed.get("head_keywords", []),
                "keyword_volumes": parsed.get("keyword_volumes", []),
                "approx_total_monthly_volume": parsed.get("approx_total_monthly_volume"),
                "buyer_intent_mix_pct": parsed.get("buyer_intent_mix_pct", {}),
                "trajectory": parsed.get("trajectory", "unknown"),
                "multi_year": parsed.get("multi_year", {}),
                "seasonality_note": parsed.get("seasonality_note", ""),
                "predicted_next_window": parsed.get("predicted_next_window", {}),
                "recommended_build_to_launch_lead_weeks": parsed.get(
                    "recommended_build_to_launch_lead_weeks"
                ),
                "geographic_breakdown": parsed.get("geographic_breakdown", []),
                "macro_trend_alignment": parsed.get("macro_trend_alignment", "none"),
                "macro_trend_url": parsed.get("macro_trend_url", ""),
                "query_freshness_pct": parsed.get("query_freshness_pct"),
                "section_score": parsed.get("section_score"),
                "confidence": parsed.get("confidence", "LOW"),
                "caveats": parsed.get("caveats", ""),
            },
            summary=parsed.get("summary", ""),
            evidence=build_evidence(parsed.get("evidence")),
            verdict=Verdict.UNREVIEWED,
        )
