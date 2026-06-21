"""niche-research CLI — composition root.

This file is the *only* place where concrete services are constructed.
Everything else depends on interfaces (CONVENTIONS.md: Dependency Inversion).
"""
from __future__ import annotations

import asyncio
import json
import os

import typer
from pydantic import ValidationError
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from niche_research.agents.community import CommunitySpecialist
from niche_research.agents.competition import CompetitionSpecialist
from niche_research.agents.demand import DemandSpecialist
from niche_research.agents.discovery import DiscoverySpecialist
from niche_research.agents.base import SpecialistService
from niche_research.brief.models import DiscoveryResult, SpecialistOutput
from niche_research.brief.writer import BriefWriter
from niche_research.config import Config
from niche_research.pipeline import PipelineConfig, SpecialistCfg
from niche_research.services.orchestrator import Pipeline1Orchestrator

app = typer.Typer(
    name="niche-research",
    help="Pipeline 1 of the Storefront Engine — high-ticket niche research.",
    no_args_is_help=True,
)
console = Console()


@app.callback()
def _main() -> None:
    """Force Typer to keep the subcommand structure even when only one
    specialist (`demand`) is registered. As more specialists land
    (competition, supplier, traffic, community), they slot in beside
    `demand` without changing the CLI shape."""


def _load_config_or_exit() -> Config:
    """Load Config with a friendly error if required env vars are missing."""
    try:
        return Config()  # type: ignore[call-arg]  # pydantic-settings reads .env / env vars
    except ValidationError as e:
        missing = [
            err["loc"][-1]
            for err in e.errors()
            if err.get("type") == "missing"
        ]
        console.print()
        console.print("[bold red]niche-research: configuration error[/bold red]")
        if missing:
            console.print(f"  Missing required setting(s): [yellow]{', '.join(map(str, missing))}[/yellow]")
        console.print()
        console.print("[bold]Fix one of two ways:[/bold]")
        console.print()
        console.print("  [cyan]1. Set in your shell[/cyan] (one-off):")
        console.print("       export ANTHROPIC_API_KEY=sk-ant-...")
        console.print()
        console.print("  [cyan]2. Create a .env file[/cyan] (persistent — recommended):")
        console.print("       mkdir -p ~/.config/niche-research")
        console.print("       cat > ~/.config/niche-research/.env <<'EOF'")
        console.print("       ANTHROPIC_API_KEY=sk-ant-...")
        console.print("       EOF")
        console.print()
        console.print("Get a key at: [link]https://console.anthropic.com/[/link]")
        console.print()
        raise typer.Exit(code=2)


def _apply_auth(config: Config) -> str:
    """Wire up Claude Agent SDK auth and return the active mode.

    - ``"api-key"``: a key is configured → export ANTHROPIC_API_KEY (the SDK
      subprocess reads it from its own environment). Pay-per-token billing.
    - ``"subscription"``: no key → rely on the Claude Code CLI's own login
      (Pro/Max). We must NOT leave a stray/empty ANTHROPIC_API_KEY in the
      environment, or it shadows the subscription auth.
    """
    if config.anthropic_api_key:
        os.environ["ANTHROPIC_API_KEY"] = config.anthropic_api_key
        return "api-key"
    os.environ.pop("ANTHROPIC_API_KEY", None)
    return "subscription"


def _run_or_die(coro: object, what: str):
    """Run an async coroutine, turning any failure into a friendly message +
    non-zero exit instead of a raw traceback (robustness — see SKILL.md)."""
    try:
        return asyncio.run(coro)  # type: ignore[arg-type]
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted.[/yellow]")
        raise typer.Exit(code=130)
    except Exception as e:
        console.print()
        console.print(f"[bold red]niche-research: {what} failed[/bold red]")
        console.print(f"  {type(e).__name__}: {e}")
        console.print(
            "[dim]Tips: re-run (web research is non-deterministic); check your "
            "network and Claude login (niche-research verify); or try a single "
            "section command first.[/dim]"
        )
        raise typer.Exit(code=1)


def _load_pipeline_or_exit() -> PipelineConfig:
    """Load pipeline.yaml with a friendly error if it's missing or malformed."""
    try:
        return PipelineConfig.load()
    except Exception as e:  # FileNotFoundError, YAML errors, validation errors
        console.print()
        console.print("[bold red]niche-research: pipeline configuration error[/bold red]")
        console.print(f"  {e}")
        console.print()
        console.print(
            "Provide a pipeline.yaml (cwd, ~/.config/niche-research/, or set "
            "NICHE_RESEARCH_PIPELINE_FILE). A reference copy ships in engine/pipeline.yaml."
        )
        console.print()
        raise typer.Exit(code=2)


def _build_specialist(spec: SpecialistCfg, model: str) -> SpecialistService | None:
    """Construct a specialist from its pipeline config, or None if not yet built.

    This is the composition root for specialists — the one place that maps a
    pipeline id to a concrete class (CONVENTIONS.md: services constructed in one
    place). Supply/Traffic return None until their specialists land.
    """
    if spec.id == "demand":
        return DemandSpecialist(model=model, max_turns=spec.max_turns)
    if spec.id == "competition":
        return CompetitionSpecialist(
            model=model,
            max_turns=spec.max_turns,
            top_n_products=spec.top_n_products,
            marketplaces=spec.marketplaces,
        )
    if spec.id == "community":
        return CommunitySpecialist(
            model=model,
            max_turns=spec.max_turns,
            max_subreddits=spec.reddit.max_subreddits,
            comments_per_post=spec.reddit.comments_per_post,
            timeframe=spec.reddit.timeframe,
            top_needs=spec.top_needs,
            top_unmet=spec.top_unmet,
        )
    return None


@app.command()
def demand(
    niche: str = typer.Argument(..., help='Niche to investigate, e.g. "ergonomic standing desks"'),
) -> None:
    """Run the Demand specialist for NICHE and print the structured output."""
    config = _load_config_or_exit()
    _apply_auth(config)

    specialist = DemandSpecialist(model=config.specialist_model)

    console.print(Panel.fit(f"[bold]Demand specialist[/bold] investigating: [cyan]{niche}[/cyan]"))

    output: SpecialistOutput = _run_or_die(specialist.investigate(niche), "research")
    _print_output(output)


@app.command()
def competition(
    niche: str = typer.Argument(..., help='Niche to investigate, e.g. "ergonomic standing desks"'),
) -> None:
    """Run the Competition specialist (major top-5 marketplace products) for NICHE."""
    config = _load_config_or_exit()
    _apply_auth(config)

    specialist = CompetitionSpecialist(model=config.specialist_model)
    console.print(Panel.fit(f"[bold]Competition specialist[/bold] investigating: [cyan]{niche}[/cyan]"))

    output: SpecialistOutput = _run_or_die(specialist.investigate(niche), "research")
    _print_output(output)


@app.command()
def community(
    niche: str = typer.Argument(..., help='Niche to investigate, e.g. "ergonomic standing desks"'),
) -> None:
    """Run the Community Needs specialist (verbatim Reddit user comments) for NICHE."""
    config = _load_config_or_exit()
    _apply_auth(config)

    specialist = CommunitySpecialist(model=config.specialist_model)
    console.print(Panel.fit(f"[bold]Community specialist[/bold] investigating: [cyan]{niche}[/cyan]"))

    output: SpecialistOutput = _run_or_die(specialist.investigate(niche), "research")
    _print_output(output)


@app.command()
def run(
    niche: str = typer.Argument(..., help='Niche to investigate, e.g. "ergonomic standing desks"'),
) -> None:
    """Run the FULL pipeline (every enabled specialist in pipeline.yaml) and write a brief.

    Reads engine/pipeline.yaml for which specialists run and which model engine
    each uses, runs them concurrently, scores what came back, and writes an
    assembled opportunity brief to the briefs dir. The verdict is capped at
    PROVISIONAL until Supply, Traffic, and the paired reviewers land.
    """
    config = _load_config_or_exit()
    auth_mode = _apply_auth(config)
    pipeline = _load_pipeline_or_exit()

    specialists: dict = {}
    skipped: list[str] = []
    for spec in pipeline.enabled_specialists():
        model = pipeline.resolve_model(spec)
        instance = _build_specialist(spec, model)
        if instance is None:
            skipped.append(spec.id)
            continue
        specialists[spec.section] = instance

    if not specialists:
        console.print("[bold red]No runnable specialists enabled in pipeline.yaml.[/bold red]")
        console.print("Enable at least one of: demand, competition, community.")
        raise typer.Exit(code=1)

    enabled = ", ".join(s.value for s in specialists)
    auth_label = "Claude subscription" if auth_mode == "subscription" else "API key (pay-per-token)"
    console.print(
        Panel.fit(
            f"[bold]Pipeline 1[/bold] — [cyan]{niche}[/cyan]\n"
            f"specialists: {enabled}\nauth: {auth_label}"
        )
    )
    if skipped:
        console.print(f"[dim]Skipped (not yet implemented): {', '.join(skipped)}[/dim]")

    orchestrator = Pipeline1Orchestrator(
        specialists=specialists,
        pipeline=pipeline,
        writer=BriefWriter(),
        briefs_dir=config.briefs_dir,
    )

    result = _run_or_die(orchestrator.run(niche), "pipeline run")

    console.rule("[bold]Run complete[/bold]")
    color = "yellow" if result.verdict == "PROVISIONAL" else ("green" if result.verdict == "APPROVED" else "red")
    console.print(f"  Verdict: [{color}]{result.verdict}[/{color}]   Score: {result.score:.2f}")
    console.print(f"  Sections produced: {', '.join(s.value for s in result.sections_produced) or 'none'}")
    for section, reason in result.failures.items():
        console.print(f"  [yellow]✗ {section.value}: {reason}[/yellow]")
    console.print(f"  Brief written to: [cyan]{result.brief_path}[/cyan]")


@app.command()
def suggest(
    seed: str = typer.Argument(
        "",
        help='Optional focus, e.g. "home gym" or "aging-in-place". Empty = general high-ticket discovery.',
    ),
    count: int = typer.Option(
        0, "--count", "-n", help="How many product ideas to return (default: pipeline.yaml discovery.default_count)."
    ),
) -> None:
    """Suggest a ranked list of high-ticket dropshipping PRODUCTS to research.

    Discovery mode: instead of validating a niche you name, this returns
    candidate products/items with price range, demand/competition signal, and an
    opportunity score — each ready to deep-validate with `niche-research run`.
    """
    config = _load_config_or_exit()
    auth_mode = _apply_auth(config)
    pipeline = _load_pipeline_or_exit()

    dcfg = pipeline.discovery
    n = count if count > 0 else dcfg.default_count
    model = getattr(pipeline.engines, dcfg.engine, pipeline.engines.specialist)

    specialist = DiscoverySpecialist(model=model, max_turns=dcfg.max_turns, min_aov_usd=dcfg.min_aov_usd)
    seed_label = seed or "general high-ticket categories"
    auth_label = "Claude subscription" if auth_mode == "subscription" else "API key (pay-per-token)"
    console.print(
        Panel.fit(
            f"[bold]Discovery[/bold] — {n} high-ticket product ideas\n"
            f"focus: [cyan]{seed_label}[/cyan]\nauth: {auth_label}"
        )
    )

    result: DiscoveryResult = _run_or_die(specialist.discover(seed or None, n), "discovery")
    _print_candidates(result)


@app.command()
def verify() -> None:
    """Smoke-test the install — no Claude API call, no money spent.

    Confirms the engine is installed correctly, the env file is being
    found, and the API key is in shape (length + prefix only — we never
    actually call the API). Returns exit code 0 on success, non-zero on
    failure. Run this first when distributing the plugin to a customer
    so they know everything wires up before they spend tokens.
    """
    console.rule("[bold]niche-research verify[/bold]")

    ok = True

    def _check(label: str, condition: bool, detail: str = "") -> None:
        nonlocal ok
        if condition:
            console.print(f"  [green]✓[/green] {label}")
            if detail:
                console.print(f"    [dim]{detail}[/dim]")
        else:
            console.print(f"  [red]✗[/red] {label}")
            if detail:
                console.print(f"    [yellow]{detail}[/yellow]")
            ok = False

    # 1. Package import.
    try:
        from niche_research import __version__

        _check("Package importable", True, f"version {__version__}")
    except Exception as e:  # pragma: no cover
        _check("Package importable", False, str(e))

    # 2. Config load (this also verifies the env file search order).
    # Bind config up front so a config failure can never leave it unbound for
    # the checks below — a smoke test must degrade gracefully, never crash.
    config: Config | None = None
    try:
        config = Config()  # type: ignore[call-arg]
        env_file = config.env_file_used
        _check(
            "Config loads from .env / env vars",
            True,
            f"env file: {env_file}" if env_file else "env file: none (using process env vars)",
        )
    except ValidationError as e:
        missing = [str(err["loc"][-1]) for err in e.errors() if err.get("type") == "missing"]
        _check(
            "Config loads from .env / env vars",
            False,
            f"missing: {', '.join(missing)} — see 'niche-research demand --help' for fix",
        )
    except Exception as e:  # malformed .env, parse errors, etc. — don't crash the smoke test
        _check(
            "Config loads from .env / env vars",
            False,
            f"unexpected error loading config: {e}",
        )

    # 3. Auth mode (no network call). Either a valid API key OR the Claude Code
    #    CLI being present for subscription auth counts as a pass.
    if config is not None:
        key = config.anthropic_api_key
        if key:
            looks_valid = key.startswith("sk-ant-") and len(key) > 40
            _check(
                "Auth: API key (pay-per-token)",
                looks_valid,
                "ANTHROPIC_API_KEY starts with sk-ant- and is long enough"
                if looks_valid
                else "value doesn't look like an Anthropic API key",
            )
        else:
            import shutil

            has_cli = shutil.which("claude") is not None
            _check(
                "Auth: Claude subscription",
                has_cli,
                "no API key set — will use the Claude Code CLI login (Pro/Max subscription)"
                if has_cli
                else "no API key AND 'claude' CLI not found — log in to Claude Code (claude → /login) or set ANTHROPIC_API_KEY",
            )

        # 4. Models configured.
        _check(
            "Models configured",
            bool(config.specialist_model and config.orchestrator_model and config.reviewer_model),
            f"specialist={config.specialist_model}, orchestrator={config.orchestrator_model}, reviewer={config.reviewer_model}",
        )

        # 5. Cost cap sane.
        _check(
            "Cost cap configured",
            config.cost_cap_usd_per_brief > 0,
            f"${config.cost_cap_usd_per_brief:.2f} per brief",
        )

        # 6. Briefs dir writable.
        briefs_dir = config.briefs_dir
        try:
            briefs_dir.mkdir(parents=True, exist_ok=True)
            test_file = briefs_dir / ".verify-write-test"
            test_file.write_text("ok")
            test_file.unlink()
            _check("Briefs dir writable", True, str(briefs_dir))
        except Exception as e:
            _check("Briefs dir writable", False, f"{briefs_dir}: {e}")

    # 7. Claude Agent SDK importable.
    try:
        from claude_agent_sdk import query as _q  # noqa: F401

        _check("claude_agent_sdk importable", True)
    except Exception as e:
        _check("claude_agent_sdk importable", False, str(e))

    # 8. pipeline.yaml loads and has at least one runnable specialist.
    try:
        pipeline = PipelineConfig.load()
        runnable = [s.id for s in pipeline.enabled_specialists() if _build_specialist(s, "x")]
        _check(
            "pipeline.yaml loads",
            bool(runnable),
            f"engines: specialist={pipeline.engines.specialist}, "
            f"orchestrator={pipeline.engines.orchestrator}; "
            f"runnable specialists: {', '.join(runnable) if runnable else 'none'}",
        )
    except Exception as e:
        _check("pipeline.yaml loads", False, str(e))

    console.rule()
    if ok:
        console.print("[bold green]All checks passed.[/bold green] Try: niche-research demand \"<niche>\"")
        raise typer.Exit(code=0)
    else:
        console.print("[bold red]Some checks failed.[/bold red] Fix the items above and re-run 'niche-research verify'.")
        raise typer.Exit(code=1)


def _money(value: float | None) -> str:
    return "—" if value is None else f"${value:,.0f}"


def _print_candidates(result: DiscoveryResult) -> None:
    if result.summary:
        console.rule("[bold]Summary[/bold]")
        console.print(result.summary)

    console.rule("[bold]High-ticket product ideas (ranked)[/bold]")
    if not result.candidates:
        console.print(
            "[yellow]No candidates returned. Try a narrower focus "
            '(e.g. suggest "aging-in-place") or re-run.[/yellow]'
        )
        return

    table = Table(show_header=True, header_style="bold")
    for col in ("#", "Product", "Price range", "~AOV", "Competition", "Score"):
        table.add_column(col)
    for i, c in enumerate(result.candidates, 1):
        table.add_row(
            str(i),
            c.name,
            c.price_range_usd or "—",
            _money(c.est_aov_usd),
            c.competition_level,
            f"{c.opportunity_score:.2f}",
        )
    console.print(table)

    console.rule("[bold]Why each is a lead — and how to validate[/bold]")
    for i, c in enumerate(result.candidates, 1):
        console.print(f"[bold]{i}. {c.name}[/bold]  [dim]({c.category})[/dim]")
        if c.rationale:
            console.print(f"   {c.rationale}")
        if c.demand_signal:
            console.print(f"   [dim]demand:[/dim] {c.demand_signal}    [dim]supply:[/dim] {c.supplier_availability or '—'}")
        if c.evidence:
            console.print(f"   [dim]source:[/dim] {c.evidence[0].url}")
        console.print(f'   [green]validate →[/green] niche-research run "{c.name}"')
        console.print()


def _print_output(output: SpecialistOutput) -> None:
    console.rule("[bold]Summary[/bold]")
    console.print(output.summary)

    console.rule("[bold]Findings[/bold]")
    table = Table(show_header=True, header_style="bold")
    table.add_column("Field")
    table.add_column("Value")
    for k, v in output.findings.items():
        table.add_row(k, json.dumps(v, default=str) if not isinstance(v, str) else v)
    console.print(table)

    console.rule("[bold]Evidence[/bold]")
    if not output.evidence:
        console.print("[yellow]No evidence URLs cited — the specialist's output is suspect.[/yellow]")
    for ev in output.evidence:
        console.print(f"  • {ev.url}  [dim]{ev.note}[/dim]")

    console.rule()
    console.print(f"[dim]Verdict: {output.verdict.value} (no reviewer wired yet — step 5)[/dim]")


if __name__ == "__main__":
    app()
