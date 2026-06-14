---
name: ms-dropshipping-market-research
description: Investigate a niche for high-ticket Shopify dropshipping. Produces an evidence-cited opportunity brief covering demand (with 24–36 month seasonality and a predicted next launch window), competition (with marketplace bestseller intel from Amazon / Temu / Shein / AliExpress), supplier verification, traffic sizing, and community needs synthesized from Reddit and marketplace reviews. Apply a domain-specific multi-criteria rubric; every claim must be backed by a fetched URL. Use this skill whenever the user asks to research, analyze, validate, score, or pick a niche for high-ticket dropshipping; whenever they say "is X a good dropshipping niche", "find me a niche for high-ticket dropshipping", "what's the demand for X", or anything in that family.
---

# Mukesh — High-Ticket Dropshipping Market Research

This skill executes Pipeline 1 of the user's Storefront Engine. The output is a structured opportunity brief that decides whether a niche advances to store construction.

## When to trigger

Trigger this skill when the user asks anything in this family:
- "Research <niche> for high-ticket dropshipping"
- "Is <niche> a viable dropshipping niche?"
- "What's the demand and competition for <niche>?"
- "Pick a niche for high-ticket Shopify dropshipping"
- "Validate <niche> for me"
- "Score <niche>"

Do **not** trigger for: low-ticket / impulse-buy categories, generic ecommerce questions, or research unrelated to product/niche selection.

## Inputs

- **niche** (required): the niche or product category to investigate, e.g. `"ergonomic standing desks"`, `"high-end cornhole boards"`, `"residential mini-splits"`.
- **target geo** (optional, default: US): primary market to evaluate.

## How to execute — two paths

### Path A — Engine CLI is installed (preferred)

This plugin **bundles the `niche-research` Python engine** in its `engine/` directory and auto-installs it on session start via the SessionStart hook (`hooks/ensure_engine_installed.sh`). On Macs with `uv` or `pipx` installed, the CLI is on PATH the first time the plugin activates — no manual setup needed.

Check with `command -v niche-research`. If found, invoke:

```bash
niche-research demand "<niche>"
```

The engine returns a structured `SpecialistOutput` with evidence URLs and Langfuse-traced execution. Report the output verbatim, then briefly summarize the verdict at the top.

> The engine currently only ships the Demand specialist. For the other sections (Competition / Supply / Traffic / Community Needs / cross-section reconciliation), fall through to Path B and explicitly note in the response which sections came from the CLI vs from this skill's fallback. As more specialists land in the engine, the skill will use Path A for them automatically.

### Path B — Fallback (engine CLI not installed, or sections not yet built)

Execute the full methodology yourself using `WebSearch` and `WebFetch`. Follow the criteria in [REVIEW_CRITERIA.md](REVIEW_CRITERIA.md) and the brief format in [SCHEMA.md](SCHEMA.md). Both files live alongside this skill.

## Methodology — the five sections

Produce each section in order. Every quantitative claim, supplier, competitor, and quote requires a fetched URL with timestamp. If you can't verify something, mark it `UNAVAILABLE` — never invent.

### §1 Demand

- Pull **multi-year** Google Trends data (24–36 months) — single-year curves are not accepted. Use Google Trends URLs the user can verify.
- Identify the **top 10–20 commercial-intent keywords** with rough monthly search volumes; cite the source for each volume.
- Compute the **year-over-year overlay**: do peaks repeat in the same months across years? Drift in peak month ≤ 30 days = real seasonality. One-time spikes = noise.
- Output a **predicted next seasonal window** — start month, expected duration, magnitude, and confidence (HIGH / MED / LOW), with reasoning grounded in the multi-year overlay.
- Output a **recommended build → launch lead time** in weeks.
- Identify the **macro trend** the niche maps to (remote work, longevity, EV adoption, aging-in-place, home automation, sustainability, etc.) — cite a source.

### §2 Competition — including marketplace intel

- Fetch the top 10 organic SERP results for the niche's commercial-intent head keywords; for each, note positioning, price tier, content quality (1–5), freshness, geo served.
- **Marketplace bestseller intel**: fetch top 5 bestsellers on Amazon for the category and at least one of Temu / Shein / AliExpress. Report price, review count, brand. Confirm at least one bestseller is at ≥ $300 AOV — otherwise this category does not validate high-ticket buyers.
- Compute price-tier distribution: counts of SKUs at <$100, $100–$300, $300–$1k, $1k+.

### §3 Supply — STRICT

Without verifiable suppliers, the niche is automatically `REJECTED`.

- Find **≥ 3 verifiable suppliers** with fetched URLs. Acceptable: US-based suppliers via dropship programs, Spocket, Doba, ThomasNet, AliExpress (with dropship support), Alibaba (verified Gold suppliers).
- For each supplier capture: country, lead time to target geo, MOQ, dropship support, returns policy, warranty, stock signal, pricing visibility.
- At least one supplier must ship to the target geo in ≤ 7 days. If not — `REJECTED`.

### §4 Traffic

- Sum addressable monthly search demand from §1.
- Estimate channel viability across: search (SEO + paid), social (TikTok / Instagram / Pinterest), communities (Reddit / niche forums).
- Implied CAC vs gross margin per order: if implied CAC > 0.5 × margin → flag.
- Identify ≥ 30 long-tail buyer-intent queries for Pipeline 4 content.

### §5 Community Needs — Audience Understanding (read, don't count)

This is the section that gives the niche its positioning angle.

- **Read** real threads, do not just count posts.
- **Reddit** (primary): Identify 2–4 relevant subreddits; deep-read top posts + top-N comments from the last 12 months. Use the Reddit `.json` endpoint via `WebFetch` (e.g. `https://www.reddit.com/r/<sub>/top.json?t=year&limit=25`) — no auth required for read-only.
- **Facebook Groups** (when active groups exist for the niche): production mode uses the bundled engine's Apify Facebook Group Scraper actor (`APIFY_ACTOR_FB_GROUP`). For the skill's Path B fallback, use Google site-searches to find indexed *public* Group posts and comments:
  - `site:facebook.com/groups <niche keywords>` — surface public posts indexed by Google.
  - `site:facebook.com/groups "<specific pain phrase>" <niche>` — target specific complaints/needs.
  - For each hit, `WebFetch` the URL; many Group pages render basic post content to non-logged-in users (full comment threads typically require login).
  - If no active Group ≥1k members surfaces, mark Facebook `UNAVAILABLE` with reason — never invent.
  - Read-only, sample size, respect Meta ToS. Do not authenticate as a posting account.
- **Facebook Pages** (always public): identify the niche's most-followed Pages (brands, communities, experts). `WebFetch` the public Page URL; fetch comment threads under product-related posts — high signal for pain points.
- Supporting: Discord, niche forums, Quora, YouTube comments.
- Marketplace voice-of-customer: Amazon reviews + Q&A, Temu / Shein / AliExpress reviews for top SKUs in the category. **1-star reviews are unmet-need gold; 5-star reviews show the minimum bar.**

Required outputs (no claim without verbatim quote evidence):

1. **Top 5 stated community needs** — ranked, 2–4 verbatim quotes per need with thread/review URL, ≥ 3 distinct users per need.
2. **Top 3 unmet needs** — needs for which buyers use workarounds / DIY because no good product exists; include the workaround in the buyer's own words.
3. **Top 5 marketplace pain points (from 1-star reviews)** — quoted, with SKU + review URL.
4. **Top 5 marketplace strengths (from 5-star reviews)** — quoted, with SKU + review URL. This is the minimum bar a high-ticket store must clear.
5. **Audience persona (3–5 paragraphs)** — derived from evidence, not invented: occupation/life stage, what outcome they want and why, what they already tried, the language they actually use (3–5 cited phrases), what they distrust and what builds trust.
6. **Recommended positioning angle** — one paragraph stating how the high-ticket store should position the product, with every claim linked to a numbered piece of evidence above. No invented copy.
7. **Willingness-to-pay distribution** — quoted price ranges.
8. **What NOT to do** — at least 2 traps the community has explicitly warned against.

### §6 Cross-section reconciliation (the final review)

After all five sections are produced, apply these checks:

- **F1 Margin math** — median competitor price (§2) − supplier cost (§3) − shipping (§3) ≥ 25% of price.
- **F2 Geo alignment** — demand geo (§1) overlaps supplier geo (§3) overlaps traffic geo (§4).
- **F3 Seasonality vs supply** — can supply ramp meet seasonal demand?
- **F4 Trend trajectory vs incumbents** — rising demand + stale incumbents = strong; falling demand + fragmented incumbents = trap.
- **F5 Channel-CAC vs margin** — sum of viable channel CACs ÷ margin ≤ 0.5.
- **F6 Community needs ↔ supply mapping** — ≥ 2 of top-3 unmet needs (§5) satisfiable by a verified supplier in §3.
- **F7 Price tolerance ↔ AOV** — community willingness-to-pay (§5) within ±25% of median competitor price (§2).
- **F8 Positioning grounded in evidence** — recommended angle (§5) cites ≥ 3 specific community quotes; no invented copy.
- **F9 Audience-needs ↔ supply-feature mapping** — each top-3 unmet need maps to a supplier feature or is in the risk register.
- **F10 Risk register** — 3–5 risks with mitigations; ≥ 1 grounded in community evidence.
- **F11 Marketplace pricing ↔ AOV ↔ supply** — median high-ticket marketplace SKU price within ±30% of (supplier cost × target margin).
- **F12 Marketplace pain → supply mitigation** — ≥ 3 of top-5 marketplace pain points solvable by supplier features, or logged as risks.
- **F13 Launch window ↔ build lead time** — predicted seasonal window (§1) starts ≥ 8 weeks out, or flagged for next-year cycle.

## Cross-cutting gates (any FAIL → `REJECTED`)

- **AOV ≥ $300** — median competitor price for the niche.
- **Gross margin ≥ 25%** — implied (price − supplier cost − shipping) / price.
- **Considered-purchase signal** — buyer queries have ≥ 3 modifiers, or Reddit shows research threads. Single-word impulse queries dominating → FAIL.
- **Operational fit** — return rate < 5%, supplier accepts returns, no perishables / regulated goods.

## Final verdict

```text
final_score = 0.22 * demand + 0.18 * competition + 0.25 * supply + 0.13 * traffic + 0.22 * community

APPROVED iff:
  - All 4 cross-cutting gates PASS
  - No FAIL on Supply (§3) or on the predicted seasonal window (D8)
  - No FAIL on any cross-section reconciliation (F1–F13)
  - final_score ≥ 0.70
  - Risk register populated with at least one community-grounded risk
```

Otherwise: `REJECTED`, with the failing criteria and reasons explicit.

## Output format

Produce a markdown brief with this header:

```yaml
---
niche: "<niche>"
slug: <niche-slug>
run_date: <YYYY-MM-DD>
verdict: APPROVED | REJECTED
score: <0.0–1.0>
---
```

…followed by sections §1 through §6 with per-criterion verdicts, an Evidence Appendix listing every URL fetched (with timestamps), and the final verdict.

When run via Path A (engine CLI), trust the CLI's output structure. When run via Path B (fallback), produce this format yourself.

## Hard rules

- **Never invent suppliers, search volumes, review quotes, or URLs.** If a source is unavailable, mark it `UNAVAILABLE` — do not paper over the gap.
- **Every quantitative claim** has a URL the user can click.
- **Every "buyers want X" statement** has ≥ 2 verbatim quotes from real threads.
- **The recommended positioning angle** is traceable line-by-line to the quoted evidence; no marketing copy fluff.
- **Reddit, marketplace, and community access is read-only** — never post, comment, or authenticate as a posting account.
- **No bulk scraping** — fetch what the analysis genuinely needs, not a category-wide dump.
- **Multi-year is mandatory for seasonality** — 12-month curves alone are not accepted because one-year spikes are often viral noise.

## Reference files

- [REVIEW_CRITERIA.md](REVIEW_CRITERIA.md) — full per-criterion rubric with weights, thresholds, and evidence requirements.
- [SCHEMA.md](SCHEMA.md) — opportunity brief format.

These are kept in sync with the canonical files at `Dropshipping/engine/src/niche_research/brief/` in the user's Storefront Engine project.
