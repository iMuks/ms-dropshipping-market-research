# ms-dropshipping-market-research

A [Claude Code](https://claude.com/claude-code) **plugin** that bundles a high-ticket Shopify dropshipping research **skill** plus a Python research **engine** (`niche-research`) — installable from GitHub in two commands, no manual Python setup, and it runs on your **Claude Pro/Max subscription** by default (no separate API billing).

It runs in **two modes**:

- **Discover** — suggest a ranked list of high-ticket product/niche ideas (AOV ≥ $300) to research.
- **Validate** — produce an evidence-cited opportunity brief for a named niche (demand with 24–36-month seasonality + next-window forecast + geographic breakdown, competition with top-5 marketplace products, community needs from verbatim Reddit comments).

Triggered as `/ms-dropshipping-market-research [niche]` or by natural language: *"suggest high-ticket products"*, *"research outdoor saunas for high-ticket dropshipping"*, *"is residential mini-split AC a viable niche?"*.

---

## Quick start (do these in order)

### 1. Install a Python runner (one-time)

The engine installs itself, but it needs [`uv`](https://docs.astral.sh/uv/) (recommended) or [`pipx`](https://pipx.pypa.io/) present:

```bash
brew install uv      # recommended  (or: brew install pipx)
```

> Without `uv`/`pipx`, the skill still works in **fallback mode** (Claude's `WebSearch` + `WebFetch`), just without the structured engine CLI.

### 2. Install the plugin (type these in the Claude Code prompt — not a terminal)

```text
/plugin marketplace add iMuks/ms-dropshipping-market-research
/plugin install ms-dropshipping-market-research
```

`/plugin` is a built-in Claude Code command. (The repo must be **public** to install it on another machine.)

### 3. Restart Claude Code

Fully quit and reopen. On relaunch, the SessionStart hook installs the `niche-research` engine and loads the skill.

### 4. Make sure you're signed in (subscription auth)

The engine reuses your Claude Code login — **no API key needed**. If you're already using Claude Code, you're set. To confirm or sign in:

```text
! claude /login        # choose your Pro/Max account
```

### 5. Use it

```text
/ms-dropshipping-market-research                          # discover product ideas
/ms-dropshipping-market-research "ergonomic standing desks"   # validate a niche
```

Or just ask in natural language:

```text
suggest high-ticket dropshipping products
research outdoor saunas for high-ticket dropshipping
is luxury home gym equipment a viable high-ticket niche?
```

---

## Running the engine directly (any terminal)

```bash
# ── One command does everything (bootstraps deps → verify login → run) ──
./research.sh                              # discover: suggest high-ticket products
./research.sh --suggest "home gym"         # focused discovery
./research.sh "ergonomic standing desks"   # validate: full opportunity brief

# ── Or call the CLI directly ──
niche-research suggest                      # discovery: ranked product ideas
niche-research suggest "aging-in-place"     # focused discovery
niche-research run "ergonomic standing desks"   # full pipeline → assembled brief

# One section at a time (debug / cheaper):
niche-research demand      "ergonomic standing desks"   # D1–D9: multi-year + forecast + geo
niche-research competition "ergonomic standing desks"   # major top-5 marketplace products
niche-research community   "ergonomic standing desks"   # verbatim Reddit user comments

niche-research verify        # smoke-test install + login — free, no tokens
```

Briefs are written to `~/niche-research/briefs/<slug>-<date>.md`.

---

## Authentication: subscription vs API key

| Mode | When | Cost |
|------|------|------|
| **Claude subscription** (default) | No `ANTHROPIC_API_KEY` set — reuses your Claude Code Pro/Max login | Draws on your plan's rate limits; no per-token bill |
| **API key** | `ANTHROPIC_API_KEY` is set (in env or `~/.config/niche-research/.env`) | Pay-per-token (~$1–4 per full `run`) |

A set `ANTHROPIC_API_KEY` always wins, so for subscription mode make sure none is set. `niche-research verify` prints which mode is active.

---

## `pipeline.yaml` — engines + which specialists run

`engine/pipeline.yaml` is the declarative control surface for a full `run`: the **model engine per role**, **scoring weights**, **cross-cutting gates**, and **which specialists are enabled**. Secrets stay in `.env`; `pipeline.yaml` decides *what* runs and *with which model*.

```yaml
engines:
  orchestrator: claude-opus-4-8
  specialist:   claude-sonnet-4-6
  reviewer:     claude-opus-4-8
specialists:
  - { id: demand,      enabled: true,  engine: specialist }
  - { id: competition, enabled: true,  engine: specialist, top_n_products: 5 }
  - { id: community,   enabled: true,  engine: specialist, reddit: { max_subreddits: 4 } }
  - { id: supply,      enabled: false }   # not yet built
  - { id: traffic,     enabled: false }   # not yet built
discovery: { engine: specialist, default_count: 10, min_aov_usd: 300 }
```

Override the location with `NICHE_RESEARCH_PIPELINE_FILE`, or drop a `pipeline.yaml` in your cwd / `~/.config/niche-research/`.

---

## What a brief contains

| Section | Highlights |
|---------|------------|
| **§1 Demand** | 24–36-month multi-year overlay with YoY peak repetition; predicted next seasonal window (confidence) + build→launch lead time; **per-region geographic breakdown**; buyer-intent mix; macro-trend alignment |
| **§2 Competition** | Organic SERP landscape + marketplace bestseller intel — the **major top-5 products** (Amazon / Temu / AliExpress) with price, reviews, brand; price-tier distribution |
| **§5 Community Needs** | Audience persona from **verbatim Reddit comments**; top stated + unmet needs; positioning angle traceable to quotes; willingness-to-pay; "what not to do" |
| **§3 Supply / §4 Traffic / §6 reconciliation** | Roadmap (not yet in the engine) — produced via the skill's fallback and merged as `mode: hybrid` |

The engine **never emits `APPROVED` on a partial run** — the verdict is capped at `PROVISIONAL` until Supply, Traffic, and the paired reviewers land. Full scoring rules: `skills/ms-dropshipping-market-research/REVIEW_CRITERIA.md` (D1–D9, C1–C10, S1–S8, T1–T5, N1–N10, F1–F13).

---

## Hard rules the skill enforces

- Every quantitative claim has a fetched URL — no hallucinated numbers, no invented suppliers/products.
- Every "buyers want X" claim has ≥2 verbatim quotes from real threads.
- Multi-year (24–36 mo) seasonality is mandatory — single-year curves are rejected (one-year spikes are often viral noise).
- Reddit and community access is **read-only** — never authenticates as a posting account.
- Cross-cutting gates: AOV ≥ $300, gross margin ≥ 25%, considered-purchase signal, operational fit.

---

## Share with a client

```bash
./package.sh        # builds dist/<name>-<version>.zip + .tar.gz + .sha256 (no secrets)
```

Then either send the `.zip` + `.sha256`, or have the client run the `/plugin marketplace add iMuks/…` flow above. Full author + client steps and a pre-ship checklist are in **[VALIDATION.md](VALIDATION.md)**.

---

## How it works — two execution paths

| Path | When | What it does |
|------|------|--------------|
| **A. Engine CLI** (preferred) | After the SessionStart hook installs `niche-research` | Claude Agent SDK + `WebSearch`/`WebFetch`, structured outputs, assembled brief. (Production data sources — DataForSEO, PRAW, pytrends, Apify — are configured in `.env.example` for the roadmap; today's specialists run on the Agent SDK web tools.) |
| **B. Built-in fallback** | If `uv`/`pipx` aren't installed, or for sections the engine hasn't built yet | Same methodology via Claude Code's `WebSearch` + `WebFetch` |

The skill mixes both — e.g. Demand/Competition/Community from Path A, Supply/Traffic from Path B (`mode: hybrid`).

---

## Repo layout

```text
ms-dropshipping-market-research/
├── .claude-plugin/{plugin.json, marketplace.json}   # plugin manifest + self-marketplace
├── skills/ms-dropshipping-market-research/
│   ├── SKILL.md            # methodology & invocation rules (two modes)
│   ├── REVIEW_CRITERIA.md  # full per-criterion rubric
│   └── SCHEMA.md           # opportunity brief format
├── engine/                 # Python research engine
│   ├── pipeline.yaml       # engines + enabled specialists (declarative)
│   ├── pyproject.toml
│   └── src/niche_research/
│       ├── cli.py          # composition root (demand/competition/community/run/suggest/verify)
│       ├── pipeline.py     # PipelineConfig loader
│       ├── config.py       # dual-mode auth + settings
│       ├── agents/         # demand, competition, community, discovery (+ _sdk, base)
│       ├── services/       # orchestrator
│       └── brief/          # models + writer
├── hooks/                  # SessionStart auto-installer
├── research.sh             # one-command entry point
├── package.sh              # build a shareable archive
├── VALIDATION.md           # share + validate guide
├── README.md
└── LICENSE
```

---

## Update

```text
/plugin update ms-dropshipping-market-research
```

Restart Claude Code. The hook compares the manifest version against `~/.local/share/ms-dropshipping-market-research/installed-version` and reinstalls the engine if it changed.

---

## Status (v0.3.0)

Shipping today: **Discovery (`suggest`)**, **Demand (D1–D9)**, **Competition (top-5 products)**, **Community (Reddit comments)**, dual-mode auth, the one-command wrapper, and client packaging. Roadmap: Supply + Traffic specialists, paired reviewers, F1–F13 reconciliation, and the production data sources in `engine/PLAN.md`.

This skill is **Pipeline 1** of a larger **Storefront Engine** — a four-pipeline AI dropshipping platform: market research → store construction → social content → organic traffic.

## License

[MIT](LICENSE)

## Author

Mukesh Sharma — [@iMuks](https://github.com/iMuks)
