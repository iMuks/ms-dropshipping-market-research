"""niche-research CLI — composition root.

This file is the *only* place where concrete services are constructed.
Everything else depends on interfaces (CONVENTIONS.md: Dependency Inversion).
"""
from __future__ import annotations

import asyncio
import json

import typer
from pydantic import ValidationError
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from niche_research.agents.demand import DemandSpecialist
from niche_research.brief.models import SpecialistOutput
from niche_research.config import Config

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


@app.command()
def demand(
    niche: str = typer.Argument(..., help='Niche to investigate, e.g. "ergonomic standing desks"'),
) -> None:
    """Run the Demand specialist for NICHE and print the structured output."""
    config = _load_config_or_exit()
    specialist = DemandSpecialist(model=config.specialist_model)

    console.print(Panel.fit(f"[bold]Demand specialist[/bold] investigating: [cyan]{niche}[/cyan]"))

    output: SpecialistOutput = asyncio.run(specialist.investigate(niche))
    _print_output(output)


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
        config = None  # type: ignore[assignment]

    # 3. API key shape (no network call — just sanity-check the value).
    if config is not None:
        key = config.anthropic_api_key
        looks_valid = key.startswith("sk-ant-") and len(key) > 40
        _check(
            "ANTHROPIC_API_KEY shape",
            looks_valid,
            "starts with sk-ant- and is long enough" if looks_valid else "doesn't look like an Anthropic API key",
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

    console.rule()
    if ok:
        console.print("[bold green]All checks passed.[/bold green] Try: niche-research demand \"<niche>\"")
        raise typer.Exit(code=0)
    else:
        console.print("[bold red]Some checks failed.[/bold red] Fix the items above and re-run 'niche-research verify'.")
        raise typer.Exit(code=1)


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
