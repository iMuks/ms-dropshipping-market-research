# Engineering Conventions

The engine follows three rules everywhere: **SOLID**, **DRY**, and **Service Architecture**. They are not aspirations — they shape the folder layout, the class boundaries, and every PR review.

## 1. Service Architecture

Every meaningful capability is a **service** behind an interface. Code never talks to concrete classes; it talks to the interface.

### The services in this codebase

| Service interface | Concrete examples | Responsibility |
|-------------------|-------------------|----------------|
| `SpecialistService` | `DemandAgent`, `CompetitionAgent`, `SupplierAgent`, `TrafficAgent`, `RedditAgent` | Produce a section of the opportunity brief |
| `ReviewerService` | `DemandReviewer`, `CompetitionReviewer`, … | Critique a specialist's output (paired) |
| `ToolService` | `DataForSEOClient`, `RedditClient`, `TrendsClient`, `WebClient` | Wrap an external data source |
| `ObservabilityService` | `LangfuseObservability` | Open/close spans, attach metadata |
| `CostBudgetService` | `EnvelopeBudget` | Track and enforce per-brief cost cap |
| `BriefStorageService` | `GitBriefStorage` | Write brief to disk and commit |
| `OrchestratorService` | `Pipeline1Orchestrator` | Compose specialists + reviewers into a run |

### Service rules

- Services expose **methods only via their interface** (Python: an abstract base class in `*/base.py`).
- Concrete services are constructed in **one place** — the composition root (`cli.py`). No `new`-ing services deep inside other services.
- A service may depend on other services **only through their interface**.
- A service has no global state. Configuration is passed in at construction.

### Folder layout reflects this

```text
src/niche_research/
├── cli.py                # composition root — wires services together
├── config.py             # Config dataclass loaded from .env (single source of truth)
├── agents/
│   ├── base.py           # SpecialistService, ReviewerService (interfaces)
│   ├── demand.py
│   ├── competition.py
│   ├── supplier.py
│   ├── traffic.py
│   ├── reddit.py
│   └── reviewers.py
├── tools/
│   ├── base.py           # ToolService (interface)
│   ├── dataforseo.py
│   ├── reddit.py
│   ├── trends.py
│   └── web.py
├── services/
│   ├── orchestrator.py   # OrchestratorService impl
│   ├── observability.py  # ObservabilityService impl (Langfuse)
│   ├── cost_budget.py    # CostBudgetService impl
│   └── brief_storage.py  # BriefStorageService impl
└── brief/
    ├── SCHEMA.md
    ├── models.py         # pydantic models — shared schema (DRY)
    └── writer.py
```

## 2. SOLID — how each letter applies here

### S — Single Responsibility

- `DemandAgent` produces the Demand section. It does not score, write to disk, or talk to Langfuse.
- `LangfuseObservability` opens and closes spans. It does not retry tool calls or enforce budgets.
- Each file in `tools/` wraps **one** external system.

### O — Open / Closed

- Adding a sixth specialist (e.g., `SeasonalityAgent`) means writing one class implementing `SpecialistService` and registering it in `cli.py`. The orchestrator does **not** change.
- New observability backend? Implement `ObservabilityService` with a new concrete; nothing else moves.

### L — Liskov Substitution

- Any `SpecialistService` is interchangeable from the orchestrator's view. Tests use `FakeSpecialist` to drive the orchestrator without LLM calls.
- Any `ToolService` is interchangeable from a specialist's view — tests use fake tools that return canned responses.

### I — Interface Segregation

- Specialists know about `ToolService` (what they need), not `BriefStorageService` (what they don't).
- Reviewers know about `SpecialistOutput` (the artifact they review), not the tools the specialist used internally.
- No "god interfaces" with 20 methods. If an interface grows past 3–5 methods, split it.

### D — Dependency Inversion

- The orchestrator depends on `SpecialistService` and `ReviewerService` interfaces, not on `DemandAgent`/`DemandReviewer`.
- Concrete wiring happens once in `cli.py`. Everything else is constructor-injected.

## 3. DRY — applied in practice

Avoid duplicating these things; centralize each:

- **Pydantic models for the brief** — defined once in `brief/models.py`, imported everywhere.
- **Retry/back-off policy** — one `tenacity` decorator in `tools/base.py`. Every tool call uses it.
- **Prompt templates** — one loader in `agents/base.py` reading from `prompts/`. No inline prompts in agent classes.
- **LLM model selection** — one mapping in `config.py` (`orchestrator_model`, `specialist_model`, `reviewer_model`). Never hard-coded in an agent.
- **Cost accounting** — one `CostBudgetService` instance per run. Agents call `budget.charge(usd)`; no ad-hoc cost tracking.
- **URL verification** — one `verify_url(url)` helper in `tools/web.py`. Used by every specialist before citing a URL.

DRY does **not** mean "no duplication ever." Three lines that happen to look alike are not duplication. The bar is: would a real change need to be made in multiple places? Then centralize.

## 4. Parallel reviewer pattern

Each specialist is paired with a reviewer running in parallel — see `brief/SCHEMA.md` for the full pattern. The pairing is wired in `cli.py`:

```python
pairs = [
    (DemandAgent(...),       DemandReviewer(...)),
    (CompetitionAgent(...),  CompetitionReviewer(...)),
    (SupplierAgent(...),     SupplierReviewer(...)),
    (TrafficAgent(...),      TrafficReviewer(...)),
    (RedditAgent(...),       RedditReviewer(...)),
]
orchestrator = Pipeline1Orchestrator(pairs=pairs, final_reviewer=Pipeline1Reviewer(...), ...)
```

The orchestrator runs each pair concurrently. Each pair internally negotiates (specialist drafts → reviewer critiques → specialist redoes, up to `max_revisions`). Only accepted sections reach the final reviewer.

## 5. Testing convention

- **Unit tests** use fakes for every service interface. No real LLM, no real API.
- **Integration tests** use the real Claude Agent SDK against one or two niches, gated by an env var so they don't run in CI by default.
- **One trace per integration test**, archived in `tests/traces/` for regression review.

## 6. Code review checklist

Before merging anything to `main`:

- [ ] Does this PR add a new responsibility? If yes, is it behind a service interface?
- [ ] Could this be reused? If yes, is it in a shared module?
- [ ] Does this PR change more than two services? If yes, why — and can we narrow the blast radius?
- [ ] Are tests using fakes, not real APIs?
- [ ] Is every URL the agent cites actually fetched in the trace?
