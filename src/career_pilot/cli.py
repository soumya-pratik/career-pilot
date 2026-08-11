from __future__ import annotations

import typer
from rich.console import Console
from rich.panel import Panel

from career_pilot.agents import master
from career_pilot.config import get_settings

app = typer.Typer(
    name="career-pilot",
    help="Hybrid multi-agent career scout (Job Scout + Master -> Discord).",
    add_completion=False,
)
console = Console(force_terminal=True, soft_wrap=True)


@app.command("run")
def run_cmd(
    no_discord: bool = typer.Option(
        False,
        "--no-discord",
        help="Skip Discord webhook (still writes output/latest_run.json).",
    ),
    no_persist: bool = typer.Option(
        False,
        "--no-persist",
        help="Skip writing output/latest_run.json.",
    ),
) -> None:
    """Run Job Scout, then Master posts a Discord digest."""
    settings = get_settings()
    _print_banner(settings)
    try:
        result = master.run(
            settings=settings,
            notify=not no_discord,
            persist=not no_persist,
        )
    except Exception as exc:  # noqa: BLE001
        console.print(f"[red]Run failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    _print_summary(result)
    if not no_discord:
        console.print("[green]Discord digest sent.[/green]")
    if not no_persist:
        console.print(f"[dim]Wrote {settings.output_dir / 'latest_run.json'}[/dim]")


@app.command("scout-only")
def scout_only_cmd() -> None:
    """Run Job Scout only: print JSON, skip Discord."""
    settings = get_settings()
    _print_banner(settings)
    try:
        result = master.run(settings=settings, notify=False, persist=True)
    except Exception as exc:  # noqa: BLE001
        console.print(f"[red]Scout failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print_json(result.model_dump_json())
    console.print(f"[dim]Wrote {settings.output_dir / 'latest_run.json'}[/dim]")


def _print_banner(settings) -> None:
    console.print(
        Panel.fit(
            f"backend={settings.scout_backend}  model={settings.openai_model}\n"
            f"resume={settings.resume_path}\n"
            f"projects={settings.projects_path}",
            title="Career Pilot",
        )
    )


def _print_summary(result) -> None:
    console.print(
        f"[bold]Roles:[/bold] {len(result.suggested_roles)}  "
        f"[bold]Jobs:[/bold] {len(result.jobs)}  "
        f"[bold]Errors:[/bold] {len(result.errors)}"
    )
    if result.summary:
        console.print(result.summary)
    for role in result.suggested_roles:
        console.print(f"  - {role.title}")
    for job in result.jobs[:5]:
        console.print(f"  -> {job.title} @ {job.company}")
    if len(result.jobs) > 5:
        console.print(f"  ... and {len(result.jobs) - 5} more")
    for err in result.errors:
        console.print(f"[yellow]! {err}[/yellow]")


if __name__ == "__main__":
    app()
