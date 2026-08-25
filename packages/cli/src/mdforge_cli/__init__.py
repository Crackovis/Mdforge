from __future__ import annotations

import json

import typer
from mdforge_application import MdforgeApplication
from rich.console import Console
from rich.table import Table

app = typer.Typer(add_completion=False, no_args_is_help=True, help="MDForge runtime diagnostics")
console = Console()


def _json(data: object) -> None:
    typer.echo(json.dumps(data, sort_keys=True, separators=(",", ":")))


@app.command()
def doctor(
    json_output: bool = typer.Option(False, "--json", help="Emit stable structured JSON."),
) -> None:
    """Inspect the runtime foundation and installed capabilities."""
    report = MdforgeApplication().doctor()
    if json_output:
        _json(report.to_dict())
        return
    status = "READY" if report.ready else "DEGRADED"
    console.print(f"MDForge runtime: {status}")
    console.print(f"Capabilities: {report.capability_count}")
    if report.discovery_failures:
        console.print(f"Discovery failures: {len(report.discovery_failures)}")


@app.command("capabilities")
def capabilities_command(
    json_output: bool = typer.Option(False, "--json", help="Emit stable structured JSON."),
) -> None:
    """List capability contracts visible to the application runtime."""
    items = MdforgeApplication().inspect_capabilities()
    data = [item.to_dict() for item in items]
    if json_output:
        _json(data)
        return
    table = Table(title="MDForge capabilities")
    table.add_column("Capability")
    table.add_column("Version")
    table.add_column("Kind")
    table.add_column("Provides")
    table.add_column("Requires")
    for item in items:
        table.add_row(
            item.id,
            item.version,
            item.kind,
            ", ".join(item.provides) or "-",
            ", ".join(item.requires) or "-",
        )
    console.print(table)


__all__ = ["app"]
