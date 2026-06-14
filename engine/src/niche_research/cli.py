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
