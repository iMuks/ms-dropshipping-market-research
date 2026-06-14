# Opportunity Brief Schema (v1)

Every brief produced by the engine has this exact shape. The reviewer rejects briefs that don't match.

> **Reviewers are domain experts, not generic graders.** All section-level and final-orchestrator reviewers apply the criteria defined in [`REVIEW_CRITERIA.md`](REVIEW_CRITERIA.md), which encodes high-ticket-dropshipping rules around seasonality, geography, trend trajectory, supply economics, and community needs. The file is the single source of truth — if a criterion isn't there, the reviewer isn't allowed to apply it.

## File location

`engine/briefs/<YYYY-MM-DD>-<niche-slug>.md`

## Header

```yaml
---
niche: "ergonomic standing desks"
slug: ergonomic-standing-desks
run_id: lf-<langfuse-trace-id>
run_date: 2026-06-13
engine_version: 0.1.0
verdict: APPROVED | REJECTED
score: 0.0–1.0
cost_usd: 0.00
---
```

## Sections (required, in order)

### 1. Demand
- **36-month Google Trends interest series** (URLs to fetched data points). One-year curves are not accepted.
- **Year-over-year overlay** — each year's monthly index plotted on the same axes; this is what proves the seasonal window is real, not a one-time spike.
- Computed: YoY growth %, peak month per year, peak-to-trough ratio per year, peak-month drift across years.
- Top 20 keywords with monthly search volume + intent classification (informational / commercial / transactional).
- **Geographic concentration** (top 3 countries by share).
- **Trend topic alignment** — which macro trend this niche maps to, with cited source.
- **Predicted next seasonal window** — start month, expected duration, magnitude relative to base, confidence (HIGH/MED/LOW), reasoning grounded in the multi-year overlay.
- **Recommended build → launch lead time** — given the predicted window, how many weeks before the window must Pipelines 2/3/4 be live.
- Verdict: PASS / WEAK / FAIL against criteria D1–D9 in `REVIEW_CRITERIA.md`

### 2. Competition
- Top 10 organic SERP results (URLs the agent fetched, with fetch timestamp).
- For each: positioning, price tier, content quality 1–5, freshness, geo served.
- Fragmentation count, brand dominance %, content recency.
- **Marketplace intelligence** — fetched via DataForSEO Amazon endpoints + Apify actors for Temu / Shein / AliExpress:
  - Top 5 bestsellers per platform (price, review count, ranking proxy, brand).
  - Price-tier distribution across the top 50 SKUs (counts at <$100 / $100–$300 / $300–$1k / $1k+).
  - Brand share of voice in the marketplace (by review-count concentration).
- Verdict: PASS / WEAK / FAIL against criteria C1–C10

### 3. Supply (STRICT — FAIL = auto-REJECT)
- Minimum 3 verifiable suppliers — each with:
  - Supplier name + URL (fetched)
  - Country, lead time, MOQ, dropship support
  - Returns policy, warranty, stock signal
  - Dropship cost / wholesale price if visible
- Mapping: which supplier can satisfy which unmet community need (links to §5)
- Verdict: PASS / WEAK / FAIL against criteria S1–S8

### 4. Traffic sizing
- Addressable monthly search demand (sum of top 20 keyword volumes)
- Per-channel sizing (search, social, communities) with viability per channel
- CAC math: implied CAC vs gross margin per order
- Geo addressable per channel
- Long-tail buyer-intent keyword cluster (≥30 queries for Pipeline 4)
- Verdict: PASS / WEAK / FAIL against criteria T1–T5

### 5. Community Needs — Audience Understanding

The specialist does not count posts. It **reads them, understands them, and synthesizes a buyer profile** from two source families:

- **Discussion sources** — Reddit (PRAW, primary; deep read of posts + top-N comments in target subreddits over last 12 months), Discord, niche forums, Facebook Groups, Quora, YouTube comments.
- **Marketplace voice-of-customer sources** — Amazon reviews + Q&A (DataForSEO), Temu / Shein / AliExpress reviews (Apify actors), Etsy reviews where relevant. 1-star reviews surface unmet needs; 5-star reviews show the minimum bar.

Required outputs (the reviewer rejects the section if any is missing or unsupported):

- **Top 5 stated community needs** — ranked, each with 2–4 verbatim quotes drawn from **both discussion and marketplace sources**, and ≥3 distinct users expressing it.
- **Top 3 unmet needs** — needs where buyers use workarounds/DIY because no good product exists. Each includes the workaround in the buyer's own words.
- **Top 5 marketplace pain points** — drawn from 1-star reviews on Amazon / Temu / Shein for the top SKUs in the category. Quoted, with SKU and review URL.
- **Top 5 marketplace strengths** — drawn from 5-star reviews on the same SKUs. Tells us the minimum bar a high-ticket store has to clear.
- **Audience profile (buyer persona) — derived from evidence, not invented.** 3–5 paragraphs covering:
  - Who they are (occupation, life stage, hobby, role) — inferred only from verifiable thread context.
  - What outcome they want and why it matters (deeper motivation).
  - What they already tried and why it failed.
  - The language they use — 3–5 actual phrases with citations.
  - What they distrust and what builds trust for them.
- **Recommended positioning angle** — one paragraph stating how a high-ticket store should position the product, with each claim linked to a numbered piece of evidence above.
- **Willingness-to-pay distribution** — counts of users citing specific price ranges, with quotes.
- **Sentiment toward existing brands** — fragmentation, dominance, direction.
- **Geographic distribution** of the conversation.
- **What NOT to do** — ≥2 traps the community has explicitly warned against (e.g., specific brand failures, shipping nightmares).
- Verdict: PASS / WEAK / FAIL against criteria N1–N10.

### 6. Cross-section reconciliation (computed by the final reviewer)
- **F1 Margin math** — median competitor price (§2) − supplier cost (§3) − shipping (§3) = gross margin
- **F2 Geo alignment** — demand geo (§1) ∩ supplier geo (§3) ∩ traffic geo (§4)
- **F3 Seasonality vs supply** — can supply ramp meet seasonal demand?
- **F4 Trend trajectory vs incumbents** — rising demand + stale incumbents = strong; falling demand + fragmented incumbents = trap
- **F5 Channel-CAC vs margin** — sum of viable channel CACs / margin ≤ 0.5
- **F6 Community needs ↔ supply mapping** — which top-3 unmet needs (§5) are satisfied by which suppliers (§3)
- **F7 Price tolerance ↔ AOV** — community willingness-to-pay (§5) vs competitor median (§2)
- **F8 Positioning grounded in evidence** — recommended angle (§5) cites ≥3 specific community quotes; no invented copy
- **F9 Audience-needs ↔ supply-feature mapping** — each top-3 unmet need maps to a supplier feature or is flagged in the risk register
- **F10 Risk register** — 3–5 risks, each with mitigation; ≥1 risk grounded in community evidence
- **F11 Marketplace pricing ↔ AOV ↔ supply** — median high-ticket marketplace SKU price within ±30% of supplier landed cost × target margin
- **F12 Marketplace pain → supply mitigation** — ≥3 of top-5 marketplace pain points (§5) either solvable by a supplier feature or logged as a risk
- **F13 Launch window ↔ build lead time** — predicted next seasonal window (§1) starts ≥ 8 weeks out (room to build, content, ramp ads); else flag for next-year cycle

### 7. Final scoring

```text
final_score = 0.22*D + 0.18*C + 0.25*S + 0.13*T + 0.22*N
```

Each section scored 0.0–1.0. **APPROVED iff**: all 4 cross-cutting gates PASS + no FAIL on Supply + no FAIL on F1–F7 + `final_score ≥ 0.70` + risk register populated.

### 8. Reviewer notes
- Per-specialist reviewer verdict with per-criterion outcomes (D1–D7, C1–C8, S1–S8, T1–T5, N1–N10).
- Per-specialist revision count (how many redos the reviewer demanded).
- Final reviewer cross-section verdicts (F1–F8).
- Any unverified claims that were dropped.
- Overall reviewer summary.

### 9. Evidence appendix
- Every URL fetched during the run, with timestamp.
- Cache hits noted explicitly.
- DataForSEO query IDs (if used).
- Community thread IDs (Reddit, Discord, forums, etc.).
- Trend topic source citations.

## Parallel reviewer pattern

Each specialist subagent is paired with a **dedicated reviewer subagent** that runs in parallel with it. The pair works as:

```text
┌──────────────────┐   draft output    ┌──────────────────┐
│  Demand agent    │ ───────────────▶  │ Demand reviewer  │
│  (Sonnet 4.6)    │                   │  (Opus 4.7)      │
│                  │ ◀── critique ──── │                  │
└──────────────────┘     until pass    └──────────────────┘
```

Rules:

- The reviewer uses a **different model** than the specialist (Opus reviewing Sonnet) to avoid same-model rubber-stamping.
- The reviewer is **domain-loaded**: its prompt is the relevant section of [`REVIEW_CRITERIA.md`](REVIEW_CRITERIA.md). It applies that rubric criterion-by-criterion — not a generic "looks good" judgment.
- The reviewer sees the specialist's tool calls and intermediate outputs, not just the final summary — so it can spot unfetched URLs, missing fields, and shaky reasoning at source.
- The reviewer can demand a **redo** of any subtask up to N times (default 2). Past N, the specialist's section is flagged `WEAK` and the orchestrator decides.
- Each criterion is evaluated as an independent check (one `ReviewCriterion` object — Single Responsibility). The section verdict is the weighted aggregate.
- Reviewer verdicts are recorded per-specialist in §8 — so we can see which specialists are reliable and which need prompt tuning.
- A final **orchestrator-level reviewer** still runs at the end for cross-section consistency (F1–F8 in `REVIEW_CRITERIA.md`) — margin math reconciles, geo aligns, community needs map to supply, etc.

This catches hallucinations and missing evidence **at the source**, not at the end. It's also what makes the trace UI in Langfuse useful — every specialist/reviewer exchange is its own span.
