# Build Plan — Pipeline 1 CLI

Track the current step here. Don't move on until the prior step runs end-to-end.

> Architecture follows [CONVENTIONS.md](CONVENTIONS.md): SOLID, DRY, Service Architecture. Every step below adds services behind interfaces — not concrete coupling.

| # | Step | Done when… | Status |
|---|------|------------|--------|
| 1 | Bootstrap — folders, `pyproject.toml`, `.env.example`, `.gitignore`, `SCHEMA.md`, `CONVENTIONS.md` | `tree engine/` matches README; `uv sync` runs clean | ✅ done |
| 2 | Stand up Langfuse locally via docker compose | `localhost:3000` shows empty Langfuse dashboard; API keys copied into `.env` | 🔄 in progress |
| 3 | Define service interfaces (`agents/base.py`, `tools/base.py`, `services/*.py` bases) + `Config` from `.env` | All abstract classes compile; `cli.py` skeleton wires fakes end-to-end | ⬜ |
| 4 | Implement `ObservabilityService` (Langfuse) + `CostBudgetService`; hello-world agent emits one trace | Trace tree visible in Langfuse for a single trivial agent call | ⬜ |
| 5 | Build **Demand specialist + Demand reviewer (paired, parallel)** — DataForSEO + pytrends pulling **36-month** series; YoY overlay; predicted next seasonal window with confidence + recommended build-to-launch lead time | Pair runs concurrently; reviewer can demand redo; section approved with multi-year overlay + predicted window URL evidence | ⬜ |
| 6 | Build **Competition specialist + reviewer** — DataForSEO SERP + WebFetch + **marketplace intel** via DataForSEO Amazon endpoints and Apify actors for Temu / Shein / AliExpress (bestsellers, price-tier distribution, brand share) | Pair returns ≥10 verified competitor URLs + top 5 bestsellers per marketplace with prices and review counts | ⬜ |
| 7 | Build **Supplier specialist + reviewer** — Spocket/Alibaba/ThomasNet via WebFetch | Pair returns ≥3 verifiable suppliers or `INSUFFICIENT`; reviewer enforces verification | ⬜ |
| 8 | Build **Traffic specialist + reviewer** and **Community Needs specialist + reviewer** — discussion sources (PRAW deep-read of posts + top-N comments, Discord, forums, FB Groups, Quora, YouTube via WebFetch) + **marketplace voice-of-customer** (Amazon reviews/Q&A via DataForSEO; Temu/Shein/AliExpress reviews via Apify). Outputs: verbatim quotes per claim, top-5 community needs, top-3 unmet needs, top-5 marketplace pain points (1-star) + top-5 strengths (5-star), audience persona derived from evidence, recommended positioning angle traceable to quotes, willingness-to-pay distribution, "what NOT to do" list | Both pairs run; Community pair returns full audience-derived output set with both discussion and marketplace quotes; reviewer rejects any claim without source-cited verbatim evidence | ⬜ |
| 9 | Implement `Pipeline1Orchestrator` — runs all 5 pairs concurrently, then final cross-section reviewer applying F1–F13 (margin math, geo alignment, seasonality vs supply, community needs ↔ supply mapping, marketplace pricing ↔ AOV, launch window ↔ build lead time, etc.) | Brief is `APPROVED`/`REJECTED` with per-specialist + final reviewer notes in §8 | ⬜ |
| 10 | Build `niche-research` CLI (typer); `BriefStorageService` writes + git-commits | `niche-research run "<niche>"` produces brief file + git commit + Langfuse trace | ⬜ |

## Guardrails enforced from step 1

- Every claim has a fetched URL. Reviewer rejects unverified data.
- Cost cap per brief (default $5). Orchestrator stops past budget.
- Idempotent runs — re-running this week hits cache.
- Reddit is read-only — no posting account ever wired in.
- Unavailable sources return `UNAVAILABLE`, never invented data.

## Step transition rule

- Mark the current step ⬜ → 🔄 when you start it.
- Mark 🔄 → ✅ only when the "Done when…" condition is observable.
- If a step takes more than 2 days, split it.
