# ms-dropshipping-market-research

A [Claude Code](https://claude.com/claude-code) skill that investigates a niche for **high-ticket Shopify dropshipping** and produces an evidence-cited opportunity brief.

Triggered as `/ms-dropshipping-market-research <niche>` or by natural-language requests like *"research X for high-ticket dropshipping"*, *"is X a viable niche?"*, *"score X as a dropshipping opportunity"*.

## What it produces

A structured brief covering five sections, each scored against a multi-criteria rubric:

| Section | What's in it |
|---------|--------------|
| **§1 Demand** | 24–36 month trajectory, seasonality (year-over-year overlay), keyword volumes, macro-trend alignment, **predicted next seasonal window** + recommended build-to-launch lead time |
| **§2 Competition** | SERP fragmentation, content quality, price-tier coverage, **marketplace bestseller intel** (Amazon / Temu / Shein / AliExpress) |
| **§3 Supply** *(STRICT)* | ≥3 verifiable suppliers with fetched URLs, lead times, dropship support, returns / warranty terms — fail → auto-reject |
| **§4 Traffic** | Per-channel viability, implied CAC vs gross margin, long-tail keyword cluster |
| **§5 Community Needs** | Audience persona derived from **verbatim quotes** in Reddit + Discord + Quora + YouTube + marketplace reviews — top 5 stated needs, top 3 unmet needs, top 5 marketplace pain points (1-star), recommended positioning angle traceable to evidence |

Plus a **final cross-section reconciliation** (margin math, geo alignment, community needs ↔ supply mapping, launch window vs build lead time, risk register) and a `final_score` 0.0–1.0 with `APPROVED` / `REJECTED` verdict.

## Install

```bash
git clone https://github.com/<your-username>/ms-dropshipping-market-research \
  ~/.claude/skills/ms-dropshipping-market-research
```

Restart Claude Code. The skill auto-loads.

## Use

```text
/ms-dropshipping-market-research ergonomic standing desks
```

…or natural language:

```text
research outdoor saunas for high-ticket dropshipping
is residential mini-split AC a viable niche?
score luxury home gym equipment as a dropshipping opportunity
```

## How it works

The skill operates in two modes:

- **Path A — engine CLI** (preferred): if a `niche-research` CLI is on `PATH`, the skill shells out to it for the heavy work (DataForSEO keyword volumes, pytrends 36-month series, PRAW Reddit deep-reads, Apify marketplace scrapers — all going through real APIs, all traced via Langfuse). This is the way the skill is meant to run in production.
- **Path B — built-in fallback**: if the CLI isn't installed, the skill executes the same methodology using Claude Code's built-in `WebSearch` and `WebFetch`. Lower-fidelity but works anywhere with no setup.

The full rubric lives in [`REVIEW_CRITERIA.md`](REVIEW_CRITERIA.md). The brief schema is in [`SCHEMA.md`](SCHEMA.md).

## Hard rules the skill enforces

- Every quantitative claim has a fetched URL — no hallucinated numbers, no invented suppliers.
- Every "buyers want X" claim has ≥2 verbatim quotes from real threads.
- The recommended positioning angle is traceable line-by-line to community evidence — no marketing copy fluff.
- Multi-year (24–36 mo) seasonality is mandatory — single-year curves alone are not accepted because one-year spikes are often viral noise.
- Reddit and community access is read-only — never authenticates as a posting account.
- Cross-cutting gates: AOV ≥ $300, gross margin ≥ 25%, considered-purchase signal, operational fit.

A brief is `APPROVED` only if `final_score ≥ 0.70`, no FAIL on Supply (§3), no FAIL on any of the 13 cross-section reconciliations, and the risk register is populated with at least one community-grounded risk. Anything less → `REJECTED` with explicit reasons.

## Files

```text
ms-dropshipping-market-research/
├── SKILL.md              # the skill definition (Claude Code reads this)
├── REVIEW_CRITERIA.md    # full per-criterion rubric (D1–D9, C1–C10, S1–S8, T1–T5, N1–N10, F1–F13)
├── SCHEMA.md             # opportunity brief format
├── README.md             # this file
└── LICENSE               # MIT
```

## Tuning the rubric

Thresholds in `REVIEW_CRITERIA.md` are intentionally conservative. After ~20 briefs, review which criteria are letting losers through (false positives) or rejecting real winners (false negatives) and tighten accordingly. Never tune to make a specific niche pass — that's overfitting to noise.

## Related

The skill is a thin client over a larger system — the **Storefront Engine**, a four-pipeline AI-driven dropshipping platform: market research → store construction → social content → organic traffic. This skill covers Pipeline 1.

## License

[MIT](LICENSE)

## Author

Built by Mukesh Sharma.
