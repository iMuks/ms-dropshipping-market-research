"""Community Needs specialist — v0.1.

Produces §5 Community Needs, the section that gives a niche its positioning
angle. Its core job here is to surface **real Reddit user comments** — verbatim
quotes from actual threads — and synthesize them into stated needs, unmet
needs, willingness-to-pay, and a positioning angle that traces back to the
quotes.

Reddit access is READ-ONLY via the public ``.json`` endpoints fetched with
WebFetch (e.g. ``https://www.reddit.com/r/<sub>/top.json?t=year&limit=25`` and a
post's ``<permalink>.json`` for its comment tree). No auth, no posting account.

The system prompt is STATIC (no str.format) so the literal JSON braces in the
schema example are never misparsed; per-run values (subreddit/comment limits,
timeframe) go in the user prompt. SDK plumbing lives in ``_sdk.py``.
"""
from __future__ import annotations

from niche_research.agents._sdk import build_evidence, run_specialist_query
from niche_research.agents.base import SpecialistService
from niche_research.brief.models import (
    SectionName,
    SpecialistOutput,
    Verdict,
)

_SYSTEM_PROMPT = """You are the Community Needs specialist for a high-ticket
dropshipping research pipeline. You produce ONLY audience-understanding evidence
for a niche the user names. Your superpower is READING real threads and quoting
real people — not counting posts.

Primary source — REDDIT (read-only):
- Identify the relevant subreddits for this niche (how many is given in your task).
- Use WebFetch on the public JSON endpoints — NO auth, NO login, NO posting:
    https://www.reddit.com/r/<sub>/top.json?t=<timeframe>&limit=25   (top posts)
    https://www.reddit.com/<post_permalink>.json                     (comment tree)
  The timeframe and the number of comments to read per post are given in your task.
- Deep-read the top posts and their comments from the last 12 months. Pull
  VERBATIM user comments — the buyer's own words.
Supporting sources (optional, when they surface real quotes): niche forums,
Quora, YouTube comments. Marketplace 1-star reviews are unmet-need gold.

Hard rules:
- Never invent a quote, username, subreddit, or URL. Every "buyers want X" claim
  needs >= 2 verbatim quotes from >= 2 distinct users, each with a source URL.
- Quote real text exactly; do not paraphrase into a quote.
- The positioning angle must trace line-by-line to numbered quotes — no copy fluff.
- If you genuinely cannot find active community discussion, say so in caveats and
  lower section_score; do NOT pad with invented needs.

Output format (return exactly this JSON in a fenced ```json block, nothing else after it):
{
  "subreddits": ["r/...", "r/..."],
  "reddit_comments": [
    {"subreddit": "r/...", "quote": "<verbatim user comment>", "url": "<https://reddit.com/...>", "theme": "<one phrase>"}
  ],
  "top_needs": [
    {"need": "<stated need>", "quotes": [{"quote": "<verbatim>", "url": "<https://...>"}]}
  ],
  "top_unmet_needs": [
    {"need": "<unmet need>", "workaround_quote": "<verbatim, in buyer's words>", "url": "<https://...>"}
  ],
  "willingness_to_pay": "<quoted price ranges buyers mention, with a URL each where possible>",
  "positioning_angle": "<one paragraph; each claim references a numbered quote above>",
  "what_not_to_do": ["<trap the community explicitly warned against>", "..."],
  "evidence": [
    {"url": "<https://...>", "note": "<what this source supports>"}
  ],
  "summary": "<3-4 sentence narrative: who these buyers are and what they actually want>",
  "section_score": <float 0.0-1.0 — your evidence-grounded self-assessment of how clear the community signal is>,
  "confidence": "HIGH" | "MED" | "LOW",
  "caveats": "<what you couldn't verify; which sources were unreachable>"
}
"""


class CommunitySpecialist(SpecialistService):
    """v0.1 Community Needs specialist grounded in verbatim Reddit comments."""

    def __init__(
        self,
        model: str,
        max_turns: int = 26,
        max_subreddits: int = 4,
        comments_per_post: int = 25,
        timeframe: str = "year",
        top_needs: int = 5,
        top_unmet: int = 3,
    ) -> None:
        self._model = model
        self._max_turns = max_turns
        self._max_subreddits = max_subreddits
        self._comments_per_post = comments_per_post
        self._timeframe = timeframe
        self._top_needs = top_needs
        self._top_unmet = top_unmet

    async def investigate(self, niche: str) -> SpecialistOutput:
        prompt = (
            f"Niche: {niche}\n\n"
            f"Read real Reddit threads (read-only, via the public .json endpoints). "
            f"Identify up to {self._max_subreddits} relevant subreddits; use t={self._timeframe} "
            f"in the top.json URL and read up to {self._comments_per_post} comments per top post. "
            f"Pull verbatim user comments and synthesize the top {self._top_needs} stated needs "
            f"and top {self._top_unmet} unmet needs, willingness-to-pay, and a positioning angle "
            "traceable to the quotes. Use WebFetch on reddit .json URLs. Return the JSON block "
            "specified in your system prompt."
        )

        parsed = await run_specialist_query(
            system_prompt=_SYSTEM_PROMPT,
            prompt=prompt,
            model=self._model,
            max_turns=self._max_turns,
        )

        return SpecialistOutput(
            niche=niche,
            section=SectionName.COMMUNITY_NEEDS,
            findings={
                "subreddits": parsed.get("subreddits", []),
                "reddit_comments": parsed.get("reddit_comments", []),
                "top_needs": parsed.get("top_needs", []),
                "top_unmet_needs": parsed.get("top_unmet_needs", []),
                "willingness_to_pay": parsed.get("willingness_to_pay", ""),
                "positioning_angle": parsed.get("positioning_angle", ""),
                "what_not_to_do": parsed.get("what_not_to_do", []),
                "section_score": parsed.get("section_score"),
                "confidence": parsed.get("confidence", "LOW"),
                "caveats": parsed.get("caveats", ""),
            },
            summary=parsed.get("summary", ""),
            evidence=build_evidence(parsed.get("evidence")),
            verdict=Verdict.UNREVIEWED,
        )
