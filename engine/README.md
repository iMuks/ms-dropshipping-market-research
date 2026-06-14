# Storefront Engine — CLI v0

The CLI implementation of **Pipeline 1: Market Research & Opportunity Discovery**, with the agent runtime and observability layer that future pipelines will reuse.

> Read the strategy first: [../concepts/00-README.md](../concepts/00-README.md).
> This folder is the **how**. The `concepts/` folder is the **why**.

## What v0 does

```text
$ niche-research run "ergonomic standing desks"
```

…produces a verifiable, scored opportunity brief in `briefs/`, with every claim traced in Langfuse running locally.

## Stack

| Layer | Tool | Notes |
|-------|------|-------|
| Agent runtime | Claude Agent SDK (Python) | Orchestrator + 5 specialist subagents + reviewer |
| Observability | Langfuse (self-hosted via Docker) | Full trace tree per run at `localhost:3000` |
| Keyword + SERP | DataForSEO API | $0.0006/query, no monthly minimum |
| Reddit signals | PRAW (read-only) | Free, OAuth read-only — never posts |
| Trend curves | pytrends | Free Google Trends client |
| Supplier discovery | WebFetch on Spocket / Alibaba / ThomasNet | Built into the SDK |
| LLM | Sonnet 4.6 (specialists) + Opus 4.7 (orchestrator, reviewer) | Cost-aware split |
| CLI | typer | Single `niche-research` entrypoint |
| Storage | git + SQLite | Briefs in git; run state in SQLite |

## Budget posture for v0

Target: **≤ $5 per brief**. Cost cap enforced in the orchestrator. Free-tier sources first; DataForSEO only when WebSearch is insufficient.

## Architecture principles

Follow [CONVENTIONS.md](CONVENTIONS.md): SOLID, DRY, Service Architecture. Every capability is a service behind an interface. Concrete wiring lives only in `cli.py`. Specialists are paired with parallel reviewers (Opus reviewing Sonnet) — see `src/niche_research/brief/SCHEMA.md`.

## Folder layout

```text
engine/
├── README.md                # this file
├── CONVENTIONS.md           # SOLID / DRY / Service Architecture rules
├── PLAN.md                  # 10-step build sequence with status
├── pyproject.toml           # Python deps
├── .env.example             # required API keys
├── docker/
│   └── langfuse.compose.yml # local Langfuse via docker compose
├── src/niche_research/
│   ├── __init__.py
│   ├── cli.py               # composition root — wires services
│   ├── config.py            # Config dataclass from .env
│   ├── agents/
│   │   ├── base.py          # SpecialistService, ReviewerService
│   │   ├── demand.py
│   │   ├── competition.py
│   │   ├── supplier.py
│   │   ├── traffic.py
│   │   ├── reddit.py
│   │   └── reviewers.py     # paired reviewers
│   ├── tools/
│   │   ├── base.py          # ToolService
│   │   ├── dataforseo.py
│   │   ├── reddit.py        # PRAW wrapper
│   │   ├── trends.py        # pytrends wrapper
│   │   └── web.py           # WebSearch / WebFetch wrapper
│   ├── services/
│   │   ├── orchestrator.py  # Pipeline1Orchestrator
│   │   ├── observability.py # Langfuse (ObservabilityService)
│   │   ├── cost_budget.py   # CostBudgetService
│   │   └── brief_storage.py # writes + git commits briefs
│   └── brief/
│       ├── SCHEMA.md        # brief format + parallel reviewer pattern
│       ├── models.py        # pydantic schemas
│       └── writer.py        # renders the .md file
├── briefs/                  # output — one file per run, committed to git
└── scripts/                 # helper scripts
```

## How to use this folder

1. Open [PLAN.md](PLAN.md). It's the 10-step build sequence and tracks which step is current.
2. Each step is independently runnable — you can stop after any step and the engine still works at that level.
3. Briefs are git-committed automatically when they pass review. Rejected briefs are saved too, with the rejection reason, so the engine learns.

## Read these before coding

- [Claude Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview)
- [Langfuse self-host docs](https://langfuse.com/docs/deployment/self-host)
- [DataForSEO API basics](https://docs.dataforseo.com/v3/)
- [PRAW quickstart](https://praw.readthedocs.io/en/stable/getting_started/quick_start.html)
