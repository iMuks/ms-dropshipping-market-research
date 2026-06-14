# ms-dropshipping-market-research

A [Claude Code](https://claude.com/claude-code) **plugin** that bundles a high-ticket Shopify dropshipping market research skill **and** a Python research engine — installable with two commands, no manual Python setup needed.

Triggered as `/ms-dropshipping-market-research <niche>` or by natural-language requests like *"research X for high-ticket dropshipping"*, *"is X a viable niche?"*, *"score X as a dropshipping opportunity"*.

## What's in this plugin

| Component | What it is |
|-----------|------------|
| **Skill** (`/ms-dropshipping-market-research`) | The user-facing entry point — slash command + auto-trigger on natural language |
| **Engine** (`niche-research` CLI) | Python research engine with specialist agents, paired domain-expert reviewers, multi-criteria rubric, Langfuse-traced execution |
| **SessionStart hook** | Auto-installs the engine CLI on first activation via `uv` or `pipx` — no manual `pip install` needed |
| **Rubric** (`REVIEW_CRITERIA.md`) | Full per-criterion scoring rules (D1–D9, C1–C10, S1–S8, T1–T5, N1–N10, F1–F13) |
| **Schema** (`SCHEMA.md`) | Standardized opportunity brief format |

## Install (one-time)

### Prerequisites

- Mac (Linux works too; Windows untested).
- Either [`uv`](https://docs.astral.sh/uv/) (recommended) or [`pipx`](https://pipx.pypa.io/) — for installing the bundled Python engine in an isolated env:

  ```bash
  brew install uv     # recommended
  # or:  brew install pipx
  ```

  If neither is installed, the skill still works in fallback mode (WebSearch + WebFetch only), but the engine CLI won't be available.

### Add the marketplace and install the plugin

Inside Claude Code:

```text
/plugin marketplace add iMuks/ms-dropshipping-market-research
/plugin install ms-dropshipping-market-research
```

Then **restart Claude Code**. The SessionStart hook fires once and installs `niche-research` into your isolated Python tool dir. You'll see a one-line confirmation in the terminal:

```text
[ms-dropshipping-market-research] engine CLI installed. Try: niche-research demand "<niche>"
```

## Use

```text
/ms-dropshipping-market-research ergonomic standing desks
```

Or just natural language anywhere in Claude Code:

```text
research outdoor saunas for high-ticket dropshipping
is residential mini-split AC a viable niche?
score luxury home gym equipment as a dropshipping opportunity
```

You can also run the engine directly from any terminal:

```bash
niche-research demand "ergonomic standing desks"
```

## How it works — two execution paths

| Path | When | What it does |
|------|------|--------------|
| **A. Engine CLI** (preferred) | After the SessionStart hook installs `niche-research` | Real APIs (DataForSEO, PRAW, pytrends, Apify), structured `SpecialistOutput`, Langfuse traces |
| **B. Built-in fallback** | If `uv`/`pipx` aren't installed, or for sections the engine hasn't built yet | Same methodology via Claude Code's `WebSearch` + `WebFetch` |

The skill seamlessly mixes both — if Demand is available via Path A but Competition isn't yet built into the engine, the skill uses A for §1 and B for §2.

## What a brief contains

Five sections, scored on a domain-specific rubric:

| Section | Highlights |
|---------|------------|
| **§1 Demand** | 24–36 month trajectory + year-over-year overlay; predicted next seasonal window + recommended build-to-launch lead time; macro-trend alignment |
| **§2 Competition** | SERP fragmentation + marketplace bestseller intel (Amazon / Temu / Shein / AliExpress) |
| **§3 Supply** *(STRICT)* | ≥3 verifiable suppliers with fetched URLs — fail → auto-reject |
| **§4 Traffic** | Per-channel viability, implied CAC vs gross margin, long-tail keyword cluster |
| **§5 Community Needs** | Audience persona derived from **verbatim quotes** (Reddit + marketplace reviews); top-5 stated needs, top-3 unmet needs, top-5 marketplace pain points (1-star), recommended positioning angle traceable to evidence |
| **Final reconciliation** | Margin math, geo alignment, community needs ↔ supply mapping, launch window vs build lead time, risk register |

`APPROVED` only if `final_score ≥ 0.70`, no FAIL on Supply, no FAIL on any of F1–F13, and the risk register has at least one community-grounded risk. Otherwise `REJECTED` with explicit reasons.

## Hard rules the skill enforces

- Every quantitative claim has a fetched URL — no hallucinated numbers, no invented suppliers.
- Every "buyers want X" claim has ≥2 verbatim quotes from real threads.
- The recommended positioning angle is traceable line-by-line to community evidence — no marketing copy fluff.
- Multi-year (24–36 mo) seasonality is mandatory — single-year curves alone are not accepted because one-year spikes are often viral noise.
- Reddit and community access is read-only — never authenticates as a posting account.
- Cross-cutting gates: AOV ≥ $300, gross margin ≥ 25%, considered-purchase signal, operational fit.

## Repo layout

```text
ms-dropshipping-market-research/
├── .claude-plugin/
│   ├── plugin.json           # plugin manifest
│   └── marketplace.json      # makes this repo its own marketplace
├── skills/
│   └── ms-dropshipping-market-research/
│       ├── SKILL.md          # methodology & invocation rules
│       ├── REVIEW_CRITERIA.md
│       └── SCHEMA.md
├── engine/                   # Python research engine
│   ├── pyproject.toml
│   ├── src/niche_research/
│   ├── CONVENTIONS.md        # SOLID / DRY / Service Architecture
│   ├── PLAN.md               # build sequence
│   └── README.md
├── hooks/
│   ├── hooks.json
│   └── ensure_engine_installed.sh   # SessionStart auto-installer
├── README.md
└── LICENSE
```

## Update

Updating to a new plugin version:

```text
/plugin update ms-dropshipping-market-research
```

Restart Claude Code. The hook compares the bundled version against the marker file at `~/.local/share/ms-dropshipping-market-research/installed-version` and re-installs the engine if it changed.

## Engine — direct CLI use

The engine can also be used standalone, outside Claude Code:

```bash
niche-research demand "ergonomic standing desks"
```

Add your `.env` first (see `engine/.env.example`):

```env
ANTHROPIC_API_KEY=sk-ant-...
LANGFUSE_HOST=http://localhost:3000   # if you self-host Langfuse
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_SECRET_KEY=...
```

See `engine/README.md` for the full engine docs and `engine/PLAN.md` for the build sequence (only the Demand specialist ships today; more land iteratively).

## Tuning the rubric

Thresholds in `skills/ms-dropshipping-market-research/REVIEW_CRITERIA.md` are intentionally conservative. After ~20 briefs, review which criteria are letting losers through (false positives) or rejecting real winners (false negatives) and tighten accordingly. Never tune to make a specific niche pass — that's overfitting to noise.

## Related

The skill is Pipeline 1 of a larger **Storefront Engine** — a four-pipeline AI-driven dropshipping platform: market research → store construction → social content → organic traffic. Future plugins will cover the other pipelines.

## License

[MIT](LICENSE)

## Author

Mukesh Sharma — [@iMuks](https://github.com/iMuks)
