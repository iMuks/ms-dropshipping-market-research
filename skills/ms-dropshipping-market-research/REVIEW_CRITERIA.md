# Review Criteria — High-Ticket Dropshipping (v1)

This is the **single source of truth** every reviewer uses. Criteria are scoped to high-ticket dropshipping — reviewers are not generic; they are domain experts encoded as rubrics.

Each criterion has:
- **Weight** in its section's 0.0–1.0 score
- **PASS / WEAK / FAIL** thresholds
- **Evidence required** (URLs the specialist must have fetched)
- **Rationale** — why this criterion matters for high-ticket specifically

If evidence is missing, the criterion auto-`FAIL`s. Reviewers do not infer; they verify.

---

## Cross-cutting high-ticket fitness gates (every section checks)

These four gates are checked by the **final orchestrator reviewer** across the whole brief. Any FAIL → brief is `REJECTED` regardless of section scores.

| Gate | PASS | FAIL | Why |
|------|------|------|-----|
| AOV potential | Median competitor price ≥ $300 | < $300 | This is the definition of high-ticket. Below this the unit economics don't fund paid CAC + closing. |
| Gross margin | Implied (price − supplier cost − shipping) / price ≥ 25% | < 20% | Below 20% there's no room for ad spend + returns + payment fees. |
| Considered-purchase signal | Avg buyer query has ≥3 modifiers (brand, spec, comparison) OR Reddit shows research threads | Single-word impulse queries dominate | Impulse buys don't justify the build investment. |
| Operational fit | Returns rate <5%, supplier handles returns, no perishables/regulated goods | Hazardous, perishable, or supplier won't accept returns | High return cost on a $2K item destroys margin instantly. |

---

## §1 Demand reviewer criteria

Specialist **must pull 36 months** of pytrends data (`timeframe='today 5-y'` is acceptable; use last 36 months for analysis). Single-year curves are not accepted — one-year spikes can be viral noise, repeating multi-year peaks prove a real seasonal window. The specialist also produces a predicted next-window forecast.

| # | Criterion | Weight | PASS | WEAK | FAIL | Evidence |
|---|-----------|--------|------|------|------|----------|
| D1 | Search volume — addressable | 0.15 | Top-20 keyword sum ≥ 50k/mo | 20k–50k | < 20k | DataForSEO / WebSearch URLs |
| D2 | Multi-year trajectory (24–36 mo) | 0.15 | YoY growth ≥ 0% each of last 2 years (each year's avg ≥ prior year's) | One flat year | Declining 2 years in a row | pytrends 36-mo series |
| D3 | Multi-year seasonality repetition | 0.15 | Peak month repeats in the same calendar window across ≥2 of last 3 years (≤30-day drift); peak-to-trough magnitude consistent ±25% | Peak repeats but magnitude swings >25% | Peak month differs across years (random spike, not seasonal) | YoY overlay chart |
| D4 | Seasonality profile (planning) | 0.10 | Year-round (peak/trough ≤ 2.0×) OR clear repeating multi-month window we can plan around | 2–3× spread, partial planning window | > 3× AND single-month spike only | 36-mo curve |
| D5 | Buyer-intent mix | 0.10 | Transactional/commercial ≥ 30% of top-20 | 15–30% | < 15% (mostly informational) | Per-keyword intent |
| D6 | Geographic concentration | 0.10 | Top-3 countries align with intended supplier geo | Partial overlap | Demand geo and supply geo mismatch | Trends by region |
| D7 | Trend topic alignment | 0.10 | Niche maps to a rising macro trend (remote work, longevity, EV, sustainability, aging-in-place, home automation, etc.) with cited source | Aligns to flat trend | Tied to a fading trend | News/research URL |
| D8 | Predicted next seasonal window | 0.10 | Specialist outputs a forecast — "next peak likely begins ~MM/YYYY, lasting N weeks" — derived from repeating multi-year patterns. Confidence stated (HIGH/MED/LOW). | Window stated with LOW confidence | No prediction or contradicts the data | Multi-year overlay + reasoning |
| D9 | Query freshness | 0.05 | ≥60% of cited buyer queries appear in last 12 months | 30–60% | Mostly stale queries | Query date metadata |

**Section verdict logic:** PASS = weighted score ≥ 0.7 AND no individual FAIL on D1, D2, D3, D8.

**Specialist output requirement (reviewer enforces):**
- 36-month pytrends interest series for ≥3 head keywords + the niche topic.
- A **year-over-year overlay** comparing each year's monthly index (this is what proves seasonal repetition).
- Computed metrics: YoY growth %, peak month per year, peak-to-trough ratio per year, peak-month drift across years.
- **Predicted next seasonal window** — start month, expected duration, magnitude relative to base, confidence (HIGH/MED/LOW), reasoning grounded in the multi-year overlay.
- **Recommended build → launch lead time** — given the predicted window, how many weeks before the window must Pipelines 2/3/4 be live to capture it.

---

## §2 Competition reviewer criteria

| # | Criterion | Weight | PASS | WEAK | FAIL | Evidence |
|---|-----------|--------|------|------|------|----------|
| C1 | SERP fragmentation | 0.20 | ≥6 distinct domains in top 10, ≤3 marketplaces | 4–5 domains | Dominated by 1–2 brands or marketplaces | Fetched SERP screenshot/URLs |
| C2 | Content quality gap | 0.15 | Avg competitor quality ≤ 3/5 | 3–3.5 | ≥ 3.5 (already strong) | Fetched pages with reviewer notes |
| C3 | Price-tier coverage at high-ticket | 0.15 | ≥2 incumbents at ≥$300 AOV | 1 incumbent | No competitor at high-ticket (signals no validated buyer) | Fetched product pages |
| C4 | Brand dominance | 0.10 | No brand >40% share of voice | 40–60% | Single brand owns >60% | SERP + branded search volume |
| C5 | Geo overlap (defensible gap) | 0.10 | Top competitors don't serve our target geo well | Partial overlap | Strong competitor in our geo | Competitor shipping/availability pages |
| C6 | Content recency | 0.10 | Avg incumbent content ≤ 24 months old | 24–48 months | > 48 months (stale, signals dying or sleepy) | Page publish/update dates |
| C7 | Channel mix gap | 0.05 | Incumbents over-reliant on paid (organic opportunity for us) | Mixed | Incumbents already strong on organic + social | Traffic source signal |
| C8 | Trust signal floor | 0.05 | Incumbents show reviews, warranty, support — proves buyers want these | Mixed | No trust infrastructure (signals not really high-ticket) | Fetched policy/review pages |
| C9 | Marketplace bestseller intel | 0.10 | Top 5 bestsellers identified per platform from **Amazon (DataForSEO)** + **Temu / Shein / AliExpress (Apify actors)**, with price, review count, ranking proxy (BSR or popularity), brand. At least one bestseller at ≥ $300 AOV. | Bestsellers identified but no high-ticket SKU | No bestseller data fetched, or all marketplace SKUs are <$50 (no high-ticket buyer signal) | Scrape output URLs + run IDs |
| C10 | Marketplace pricing distribution | 0.10 | Price-tier distribution mapped (count of SKUs at <$100, $100–$300, $300–$1k, $1k+); ≥10% of top-50 SKUs in target category sit at high-ticket | Some high-ticket SKUs exist but thin | Almost no high-ticket SKUs (signals buyers buy elsewhere — e.g., specialty retail — not our model) | Per-SKU price table |

**Section verdict logic:** PASS = score ≥ 0.7 AND no FAIL on C1, C3, C9.

---

## §3 Supplier reviewer criteria — STRICT (Supply FAIL → auto-REJECT)

| # | Criterion | Weight | PASS | WEAK | FAIL | Evidence |
|---|-----------|--------|------|------|------|----------|
| S1 | Verifiable supplier count | 0.20 | ≥3 suppliers with fetched URLs and contact info | 1–2 | 0 verifiable | Fetched supplier pages |
| S2 | Geographic fit (lead time) | 0.20 | ≥1 supplier ships to target geo in ≤7 days | 7–14 days | > 14 days (high-ticket buyers won't wait) | Supplier shipping page |
| S3 | Dropship support | 0.15 | Confirmed dropship program (no wholesale MOQ trap) | Single-unit possible but not advertised | Wholesale-only, MOQ ≥10 | Supplier dropship/B2B page |
| S4 | Returns policy | 0.10 | Supplier accepts returns or runs a returns process | Returns possible with restock fees | No returns accepted | Supplier returns policy URL |
| S5 | Warranty / damage terms | 0.10 | Explicit warranty period ≥ 12 months | 3–12 months | None | Warranty page |
| S6 | Stock & reliability signal | 0.10 | Active inventory shown; reorder cycle ≤ 30 days | Some items out of stock | Most items out of stock | Inventory snapshot |
| S7 | Pricing transparency | 0.05 | Dropship cost or wholesale price visible (verifiable margin math) | Quote required | No pricing info, no quote channel | Pricing page or quote portal |
| S8 | Compliance & paperwork | 0.10 | Supplier provides invoices, certifications, customs docs as needed | Partial | Missing for regulated/imported categories | Certification page |

**Section verdict logic:** PASS = score ≥ 0.75 AND no FAIL on S1, S2, S3. **Any FAIL on S1, S2, or S3 → entire brief is auto-`REJECTED`.**

---

## §4 Traffic reviewer criteria

| # | Criterion | Weight | PASS | WEAK | FAIL | Evidence |
|---|-----------|--------|------|------|------|----------|
| T1 | Channel diversity | 0.25 | Viable on ≥2 channels (search, social, communities) | 1 strong channel | No clear channel | Per-channel sizing data |
| T2 | CAC viability | 0.30 | Implied CAC < 0.5 × gross margin per order | 0.5–0.8 × | > 0.8 × | Per-keyword CPC + AOV math |
| T3 | Geo match | 0.15 | Traffic geo aligns with supplier and demand geo | Partial | Mismatch | Channel-level geo data |
| T4 | Content addressability | 0.15 | ≥30 long-tail buyer-intent queries we can rank for in Pipeline 4 | 10–30 | < 10 | Keyword cluster export |
| T5 | Social trend overlap | 0.15 | Niche topic has live momentum on TikTok/Reddit/Pinterest in last 90 days | Flat | Declining momentum | Platform trend URL |

**Section verdict logic:** PASS = score ≥ 0.65 AND no FAIL on T2.

---

## §5 Community Needs reviewer criteria

This section mines **what real buyers are asking for** across two source families:

**Discussion sources:**

- **Reddit** (primary, via PRAW) — public, no login required.
- **Facebook Groups** (membership-gated) — for many niches, the highest-density buyer conversations live in private Groups (e.g., "Standing Desk Enthusiasts," "Outdoor Sauna Owners US"). Production access: **Apify Facebook Group Scraper actor** (`APIFY_ACTOR_FB_GROUP`) with a logged-in cookie session — handles anti-bot and rate limits. Fallback (skill / no Apify): Google search `site:facebook.com/groups/<niche>` to find indexed *public* posts and pages; many Groups expose top posts publicly. **Always respect Meta ToS — read-only, sample size, never post.**
- **Facebook Pages** (public) — brand pages, niche communities, expert pages and their public posts + comments. Fetch via public URL with `WebFetch`. The comment threads under product-related posts are often gold for pain points.
- **Discord** — niche-specific servers; check pinned channels + recent activity.
- **Niche forums** (e.g., Houzz for home decor, AVS Forum for AV, Garage Journal for tools).
- **Quora** — search for buyer-intent questions; read top-voted answers + comments.
- **YouTube comments** — under top product review videos; pain points often surface in long comment threads.

**Marketplace voice-of-customer sources:**

- **Amazon reviews + Q&A** (via DataForSEO).
- **Temu / Shein / AliExpress reviews** (via Apify actors).
- **Etsy reviews** (where relevant — handmade and small-batch niches).

1-star reviews are unmet-need gold; 5-star reviews show what buyers actually value and the minimum bar.

The point is not "is there activity" but **"what needs are unmet that suppliers can satisfy."**

| # | Criterion | Weight | PASS | WEAK | FAIL | Evidence |
|---|-----------|--------|------|------|------|----------|
| N1 | Multi-source presence | 0.10 | Active discussion across ≥2 sources, **including at least one of Reddit / Facebook Group / Facebook Page** (i.e., a real buyer community, not just an article comment section). When ≥1 active FB Group with ≥1k members exists for the niche, evidence from it is required or explicitly marked `UNAVAILABLE` with reason (e.g., "no Apify token configured"). | Single community OR FB skipped without reason | None, or FB skipped silently when active groups exist | Community URLs + member counts |
| N2 | Buying-intent thread volume | 0.15 | ≥10 buying-intent threads in last 90 days | 3–10 | < 3 | Thread IDs with timestamps |
| N3 | Unmet-need signal | 0.20 | ≥3 distinct "I wish there was…" / "Why doesn't anyone make…" threads in last 6 months | 1–3 | None (market is satisfied) | Thread excerpts with URLs |
| N4 | Workaround signal | 0.15 | Buyers using inferior DIY / cobbled-together solutions (= unmet demand) | Some workarounds | Buyers content with existing options | Thread excerpts |
| N5 | Feature request frequency | 0.10 | Top 3 requested features identifiable with ≥5 mentions each | 2 features identifiable | Requests too scattered to act on | Mention-count table |
| N6 | Willingness-to-pay signal | 0.10 | Buyers state target price ranges; median ≥ $300 | Mixed; some willingness signals | Mostly bargain-hunting / "I'd never pay that" | Excerpt quotes |
| N7 | Frustration with current options | 0.05 | Recurring complaints about existing products/brands | Some grumbling | Buyers love what exists | Thread excerpts |
| N8 | Brand fragmentation in discourse | 0.05 | No single brand dominates conversations | 1 brand dominates | Conversation captured by one incumbent | Mention counts |
| N9 | Geographic representation | 0.05 | Communities include users from target geo | Partial | All discussion from non-target geo | User flair / location signals |
| N10 | Sentiment toward paid ads | 0.05 | Mixed (community tolerates promotion done well) | Mostly anti-ad | Strong anti-ad sentiment (will hurt paid traffic) | Sample replies |

**Section verdict logic:** PASS = weighted score ≥ 0.65 AND no FAIL on N2, N3.

**Specialist output requirement (the reviewer enforces — missing any item = automatic redo):**

The Community Needs specialist does not count posts. It **reads them, understands them, and synthesizes a buyer profile**. Primary source: Reddit via PRAW (deep read of top threads in target subreddits over the last 12 months). Supporting sources: Discord, niche forums, Facebook Groups, Quora, YouTube comments, Amazon Q&A, product review sections.

1. **Verbatim-quote evidence per claim.** Every "buyers want X" / "buyers hate Y" / "buyers pay Z" statement is backed by **≥2 direct quotes with source URLs and timestamps**. No paraphrasing without quotes underneath.
2. **Top 5 stated community needs.** Ranked, each with 2–4 verbatim quotes drawn from **both discussion and marketplace sources** and at least 3 distinct users expressing it.
3. **Top 3 unmet needs** — needs for which buyers are using workarounds or DIY solutions because no good product exists. Each must include the workaround/DIY described in the buyer's own words.
3a. **Top 5 marketplace pain points (from 1-star reviews)** — what existing products in the category fail at, drawn from Amazon / Temu / Shein 1-star reviews. Quoted, with product SKU and review URL.
3b. **Top 5 marketplace strengths (from 5-star reviews)** — what existing products in the category get right; tells us the minimum bar. Quoted, with product SKU and review URL.
4. **Audience profile (buyer persona) — derived from evidence, not invented.** 3–5 paragraphs covering:
   - Who they are (occupation, life stage, hobby, role) inferred only from verifiable thread context.
   - What outcome they want and why it matters to them (the deeper motivation).
   - What they have already tried and why it failed.
   - What language they use (3–5 phrases they actually say, with citations).
   - What they distrust and what builds trust for them.
5. **Recommended positioning angle.** One paragraph stating how a high-ticket store should position the product, derived directly from items 2–4. Each claim in this paragraph links to a numbered piece of evidence above.
6. **Willingness-to-pay distribution** — counts of users mentioning specific price ranges, with quotes.
7. **Target-geo split** of the conversation — based on user flair, country mentions, regional product references.
8. **What NOT to do** — at least 2 traps the community has explicitly warned against (e.g., specific brand failures, false promises, bad shipping experiences).

The reviewer rejects the section if any output above is missing, if any claim lacks the required quote evidence, or if the recommended positioning is not traceable to the quoted evidence.

---

## Final orchestrator reviewer — cross-section reconciliation

Runs after all 5 paired pairs complete. Checks consistency that no individual section can see:

| # | Reconciliation check | Required outcome |
|---|----------------------|------------------|
| F1 | Margin math reconciles | Median competitor price (§2) − supplier cost (§3) − shipping (§3) ≥ 25% of price |
| F2 | Geo alignment | Demand geo (§1 D5) overlaps supplier geo (§3 S2) overlaps traffic geo (§4 T3) |
| F3 | Seasonality vs supply | If §1 D3 is single-season (FAIL), can supplier support Q4-only ramp? If not → reject |
| F4 | Trend trajectory vs incumbents | If §1 D2 rising + §2 C6 incumbents stale → strong signal. If §1 D2 declining + §2 C1 fragmented → trap |
| F5 | Channel-CAC vs margin | Sum of viable channel CACs (§4 T2) ÷ margin (§F1) ≤ 0.5 |
| F6 | Community needs ↔ supply | ≥2 of top-3 unmet community needs (§5 N3, N4) are satisfiable by at least one verified supplier in §3 — with feature mapping cited |
| F7 | Community price tolerance ↔ AOV | Median stated willingness-to-pay (§5 N6) is within ±25% of median competitor price (§2 C3) |
| F8 | Positioning grounded in evidence | Recommended positioning angle (§5 output 5) cites at least 3 specific community quotes from §5 outputs 2–4. Every claim in the angle is traceable to a verbatim quote — not invented or generic copy. |
| F9 | Audience-needs ↔ supply-feature mapping | Each top-3 unmet need (§5 output 3) maps to either: (a) a verified supplier in §3 that can satisfy it, or (b) an explicit gap noted in the risk register (§F10) |
| F10 | Risk register | Reviewer must list 3–5 risks that could kill this niche + a mitigation for each. Must include at least one risk grounded in community evidence (e.g., "Community has explicitly warned against brand X failures — we must avoid pattern Y"). |
| F11 | Marketplace pricing ↔ AOV ↔ supply | Median Amazon high-ticket SKU price (§2 C10) within ±30% of supplier landed cost × target margin (§3 + F1) — verifies we can price competitively and still hit margin. |
| F12 | Marketplace pain → supply mitigation | Top 5 marketplace pain points (§5 output 3a) — at least 3 must be either solvable by a verified supplier feature in §3, or explicitly listed as risks in F10. Unaddressable pain points are why incumbents lose; we either fix them or we know we can't. |
| F13 | Launch window ↔ build lead time | Predicted next seasonal window (§1 D8) starts ≥ 8 weeks from today (room to build store + warm up content + ramp ads). If less than 8 weeks → flag for next-year cycle. |

## Final verdict

```text
final_score = 0.22*D + 0.18*C + 0.25*S + 0.13*T + 0.22*N

APPROVED if and only if:
  - All 4 cross-cutting gates PASS
  - No section FAIL on Supply (§3) or on D8 (predicted seasonal window)
  - No FAIL on any cross-section reconciliation (F1–F13)
  - final_score ≥ 0.70
  - Risk register populated with community-grounded risk (F10)

Otherwise REJECTED, with the failing criteria and reasons explicit in §7 of the brief.
```

---

## How specialists and reviewers use this file

- **Specialists** read the criteria for their section so their tool-calling plan covers every required piece of evidence. No criterion → no point producing the data.
- **Reviewers** run each criterion as a discrete check (one `ReviewCriterion` object per row above — Single Responsibility) and aggregate into a section verdict.
- **DRY:** This file is the single source. The pydantic models in `brief/models.py` are generated from these tables; reviewer code references criterion IDs (`D1`, `S2`, etc.), not literal strings.
- **OCP:** Adding a new criterion = adding a row here + a new `ReviewCriterion` subclass. No reviewer logic changes.

## Tuning policy

These thresholds will be wrong at first. After every batch of ~20 briefs, review which thresholds rejected actual winners (false negatives) and which let losers through (false positives). Tighten or loosen per criterion. **Never tune to make a specific niche pass** — that's overfitting to noise.
