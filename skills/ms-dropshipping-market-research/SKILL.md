---
name: ms-dropshipping-market-research
description: High-ticket Shopify dropshipping market research (Storefront Engine Pipeline 1). Runs in two modes. DISCOVER — suggest a ranked list of high-ticket product/niche ideas (AOV ≥ $300) to research. VALIDATE — produce an evidence-cited opportunity brief for a named niche covering demand (24–36 month multi-year seasonality, a forecast of the next seasonal window with confidence, and a per-region geographic breakdown), competition (marketplace bestseller intel — the major top products from Amazon / Temu / AliExpress), supplier verification, traffic sizing, and community needs synthesized from verbatim Reddit comments and marketplace reviews. Scored on a domain-specific multi-criteria rubric; every claim must be backed by a fetched URL. Use this skill whenever the user asks to research, analyze, validate, score, or pick a high-ticket dropshipping niche — OR to suggest, find, or list high-ticket products to sell. Triggers include "is X a good dropshipping niche", "research X for high-ticket dropshipping", "what's the demand for X", "validate X", "suggest high-ticket products", "what should I sell", "find me a high-ticket niche", and anything in that family.
---

# Mukesh — High-Ticket Dropshipping Market Research

This skill executes Pipeline 1 of the Storefront Engine. It runs in two modes — **discover** candidate high-ticket products, or **validate** a named niche into a structured opportunity brief that decides whether it advances to store construction.

## When to trigger

Trigger this skill when the user asks anything in this family. There are **two modes**:

**Validate a named niche** (the user gives a product/niche):
- "Research <niche> for high-ticket dropshipping"
- "Is <niche> a viable dropshipping niche?"
- "What's the demand and competition for <niche>?"
- "Validate <niche> for me" / "Score <niche>"

**Discover products** (the user gives no niche, or asks for ideas):
- "/ms-dropshipping-market-research" (no argument)
- "Suggest high-ticket dropshipping products" / "What should I sell?"
- "Find me high-ticket product ideas" / "Pick a niche for high-ticket Shopify dropshipping"
- "Give me a list of products/items for high-ticket dropshipping"

Do **not** trigger for: low-ticket / impulse-buy categories, generic ecommerce questions, or research unrelated to product/niche selection.

## Inputs

- **niche** (optional): the niche or product category to investigate, e.g. `"ergonomic standing desks"`, `"high-end cornhole boards"`, `"residential mini-splits"`. **If omitted, run discovery mode** — suggest a ranked list of high-ticket products to research.
- **seed/focus** (optional): a category or interest to focus discovery, e.g. `"aging-in-place"`, `"home gym"`.
- **target geo** (optional, default: US): primary market to evaluate.

## How to execute

This is a one-shot: **preflight → login (only if needed) → discover or validate → present the result.** The bundled `research.sh` chains every step, so prefer it; the manual CLI equivalents follow so you can drive each piece or handle the login stop.

### The one command (preferred)

```bash
# DISCOVER — suggest high-ticket products (no niche given):
"${CLAUDE_PLUGIN_ROOT:-.}/research.sh"
"${CLAUDE_PLUGIN_ROOT:-.}/research.sh" --suggest "<optional focus>"

# VALIDATE — full opportunity brief for a named niche:
"${CLAUDE_PLUGIN_ROOT:-.}/research.sh" "<niche>"
```

If `research.sh` stops at the login step, relay its sign-in instruction to the user and stop until they've completed it (browser sign-in is interactive — only the user can do it):

> Sign in to your Claude account first — run this in the prompt, pick your **Pro/Max** account, then re-invoke:
> ```
> ! claude /login
> ```

### What it does, step by step (manual equivalents)

1. **Locate the engine CLI:** `command -v niche-research` (installed by the SessionStart hook `hooks/ensure_engine_installed.sh`), else `uv run --project "${CLAUDE_PLUGIN_ROOT:-engine}" niche-research …`. If neither runs, use **Path B**.
2. **Preflight + login (free — no tokens, no API call):** `niche-research verify`. Auth is **subscription** by default (reuses the Claude Code Pro/Max login — no API key) or **api-key** if `ANTHROPIC_API_KEY` is set. If verify's `Auth:` line is ✗, STOP and have the user run `! claude /login`, then re-invoke.
3. **Pick the mode from what the user gave you:**
   - **No niche / "suggest products" → DISCOVER:** `niche-research suggest [focus]`. Returns a ranked shortlist (see *Discovery output* below). Present it; note each can be deep-validated with `niche-research run "<name>"`, and offer to validate the top pick.
   - **A niche is named → VALIDATE:** `niche-research run "<niche>"`. Runs the enabled specialists in `engine/pipeline.yaml` — **§1 Demand** (24–36-month multi-year overlay, predicted next seasonal window, per-region geographic breakdown), **§2 Competition** (major top-5 marketplace products), **§5 Community Needs** (verbatim Reddit comments) — scores them, and writes the brief to `~/niche-research/briefs/<slug>-<date>.md`. **Read that file and present it**, leading with the verdict + score.

### After a validation run — fill the gaps

The engine does not yet produce **§3 Supply**, **§4 Traffic**, or the **F1–F13** reconciliation. Produce those via **Path B** and merge into the same template; mark `mode: hybrid`. The engine **never emits `APPROVED` on a partial run** (capped at `PROVISIONAL`) — only upgrade to `APPROVED`/`REJECTED` after Supply + Traffic + reconciliation exist and all cross-cutting gates are evaluated. To run one section for debugging (cheaper): `niche-research demand|competition|community "<niche>"`.

### Path B — Fallback (engine unavailable)

Execute the methodology yourself with `WebSearch` + `WebFetch`, following [REVIEW_CRITERIA.md](REVIEW_CRITERIA.md) and [SCHEMA.md](SCHEMA.md) (both alongside this skill). For **discovery**, produce the ranked list in *Discovery output* below; for **validation**, produce the full brief template. Mark `mode: skill-fallback`.

## Methodology — the five sections

Produce each section in order. Every quantitative claim, supplier, competitor, and quote requires a fetched URL with timestamp. If you can't verify something, mark it `UNAVAILABLE` — never invent.

### §1 Demand

- Pull **multi-year** Google Trends data (24–36 months) — single-year curves are not accepted. Cite the multi-year Trends URL (it encodes the date range + geo) so the user can verify it. *(D2/D3)*
- Compute the **year-over-year overlay**: per year, the average level (for YoY growth %), the peak month, and the peak-to-trough ratio. Then check whether the peak month **repeats** in the same calendar window across years — drift ≤ 30 days = real seasonality; different peak months = viral noise, not seasonal. *(D2/D3/D4)*
- Output a **predicted next seasonal window** — start month, expected duration, magnitude vs base, and confidence (HIGH / MED / LOW), with reasoning grounded in the multi-year overlay. *(D8 — a hard-fail criterion)*
- Output a **recommended build → launch lead time** in weeks (how far ahead of the window the store must be live).
- Identify the **top 10–20 commercial-intent keywords** with rough monthly search volumes (cite each), label each keyword's intent, and state the **buyer-intent mix** (% transactional/commercial) and **query freshness** (% of queries from the last 12 months). *(D1/D5/D9)*
- Produce a **geographic breakdown** — the top countries/regions by relative demand (use Google Trends "by region"), cited. This drives geo-alignment with supply/traffic in §6 F2. *(D6)*
- Identify the **macro trend** the niche maps to (remote work, longevity, EV adoption, aging-in-place, home automation, sustainability, etc.) — cite a source. *(D7)*

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

## Discovery output (suggest mode)

In discovery mode the deliverable is a **ranked shortlist**, not a brief. Lead with a one-line theme, then a ranked table:

```markdown
| # | Product / niche | Category | Price range | ~AOV | Competition | Opportunity (0–1) |
```

Then, per candidate: a 1–2 sentence rationale (why it clears high-ticket + where the wedge is), the demand and supplier signal, **one source URL**, and the exact next step `niche-research run "<name>"`. Apply the same hard rules as a brief — each candidate must clear **AOV ≥ $300**, be a considered purchase, and be dropship-operable; cite a real URL for each claimed signal; never invent a product, price, or URL. Close by offering to validate the top pick.

## Required output template — the customer's "designed output"

Every brief MUST be a single markdown document with this exact structure. This is what the customer pays for; it does not vary by niche.

```markdown
---
niche: "<niche>"
slug: <niche-slug>
run_date: <YYYY-MM-DD>
verdict: APPROVED | REJECTED | PROVISIONAL
score: <0.0–1.0>
mode: engine-CLI | skill-fallback | hybrid
---

# Opportunity Brief — <Niche Title>

> One-paragraph executive summary: the verdict, the score, the headline reason, the recommended sub-niche / positioning angle if APPROVED, or the disqualifying factor if REJECTED.

## §1 Demand — <PASS / WEAK / FAIL>
- Per-criterion table (D1–D9 with PASS/WEAK/FAIL and a URL per row)
- 24–36 month multi-year overlay: YoY growth, peak month, and peak/trough per year
- Predicted next seasonal window (confidence) + build→launch lead time
- Geographic breakdown (top regions by relative demand) + buyer-intent mix

## §2 Competition — <PASS / WEAK / FAIL>
- Per-criterion table (C1–C10)
- Top 10 organic SERP results with fetched URLs
- Marketplace bestseller intel (Amazon + at least one of Temu/Shein/AliExpress)
- Price-tier distribution

## §3 Supply — <PASS / WEAK / FAIL>   *(strict — FAIL → entire brief auto-REJECTED)*
- ≥3 verifiable suppliers, each with: name, URL, country, lead time, MOQ, dropship support, returns, warranty
- S1–S8 per-criterion verdicts

## §4 Traffic — <PASS / WEAK / FAIL>
- Per-channel viability (search / social / community)
- CAC vs gross margin math
- ≥30 long-tail buyer-intent queries for Pipeline 4

## §5 Community Needs — <PASS / WEAK / FAIL>
- Top 5 stated needs (≥2 verbatim quotes each, source URLs)
- Top 3 unmet needs (with workaround quotes)
- Top 5 marketplace pain points (from 1-star reviews; SKU + URL)
- Top 5 marketplace strengths (from 5-star reviews; SKU + URL)
- Audience persona (3–5 paragraphs, evidence-cited)
- **Recommended positioning angle** (every claim numbered → evidence)
- Willingness-to-pay distribution
- "What NOT to do" — ≥2 community-cited traps

## §6 Cross-section reconciliation
- F1–F13 per-check verdicts (table)
- Risk register (3–5 risks; each with mitigation; ≥1 community-grounded)

## §7 Final verdict
- final_score = 0.22*D + 0.18*C + 0.25*S + 0.13*T + 0.22*N
- Numeric score with each section's contribution
- APPROVED / REJECTED / PROVISIONAL with explicit reasons

## §8 Reviewer notes
- Per-section per-criterion notes
- Any unverified claims that were dropped

## §9 Evidence appendix
- Every URL fetched, with fetch timestamp
- All sources marked UNAVAILABLE with reason
- DataForSEO query IDs (if used)
- Reddit / FB Group / forum thread IDs

## §10 Self-verification checklist
The skill MUST end the brief with this checklist, ticking each box that applies:
- [ ] §1 includes 24–36 month multi-year overlay with YoY repetition (NOT 12-month only)
- [ ] §1 includes predicted next seasonal window with confidence (HIGH/MED/LOW)
- [ ] §1 includes a per-region geographic breakdown (D6)
- [ ] §2 includes marketplace bestseller intel with at least one platform fetched
- [ ] §3 has ≥3 verifiable suppliers, each with a fetched URL
- [ ] §5 includes at least one source from Reddit / Facebook Group / Facebook Page
- [ ] §5 audience persona derived from evidence (not invented)
- [ ] §5 recommended positioning angle has every claim linked to numbered evidence
- [ ] §6 has all F1–F13 checks with a verdict (PASS / WEAK / FAIL / N/A)
- [ ] §6 risk register has ≥3 risks each with a mitigation
- [ ] §9 evidence appendix lists EVERY URL the brief cites
- [ ] No invented suppliers, search volumes, quotes, or URLs anywhere in the brief
- [ ] Verdict at top matches §7 final verdict (no contradiction)

Any unchecked box means the brief is incomplete — DO NOT emit a verdict of APPROVED if any box is unchecked; downgrade to PROVISIONAL with the missing items listed in the executive summary.
```

When run via **Path A (engine CLI)**, trust the CLI's output structure for sections it implements and produce only the sections it doesn't (mark `mode: hybrid` at the top). When run via **Path B (fallback)**, produce this entire structure yourself (mark `mode: skill-fallback`).

## Hard rules (non-negotiable)

You MUST follow every rule below. A brief that violates any rule must NOT be emitted as APPROVED.

1. **Never invent** suppliers, search volumes, review quotes, or URLs. If a source is unavailable, mark it `UNAVAILABLE` with a reason — do NOT paper over the gap.
2. **Every quantitative claim** has a URL the user can click in §9.
3. **Every "buyers want X" statement** has ≥2 verbatim quotes from real threads, each with a source URL.
4. **The recommended positioning angle** is traceable line-by-line to numbered quoted evidence; NO marketing copy fluff.
5. **Reddit, marketplace, and community access is read-only.** Never post, comment, or authenticate as a posting account.
6. **No bulk scraping.** Fetch what the analysis genuinely needs, not a category-wide dump.
7. **Multi-year (24–36 mo) is mandatory for seasonality.** 12-month curves alone are NOT accepted because one-year spikes are often viral noise.
8. **Facebook coverage:** when the niche has identifiable Facebook Groups ≥1k members, evidence from them is required OR the brief explicitly marks Facebook `UNAVAILABLE` with reason. Silent omission is a FAIL.
9. **Match the output template exactly** — every section header, every checklist box. Customers depend on a stable output shape.
10. **Self-verification checklist (§10) is mandatory.** A brief without it is incomplete.

If you cannot satisfy a rule (e.g., a source is genuinely unreachable), document the gap in §9 evidence appendix AND downgrade the brief verdict to `PROVISIONAL` with a one-line explanation in the executive summary. Never silently fail and emit `APPROVED`.

## Reference files

- [REVIEW_CRITERIA.md](REVIEW_CRITERIA.md) — full per-criterion rubric with weights, thresholds, and evidence requirements.
- [SCHEMA.md](SCHEMA.md) — opportunity brief format.

These ship alongside this skill and are kept in sync with the engine's canonical copies in `engine/src/niche_research/brief/`.
