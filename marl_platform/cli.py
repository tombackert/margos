"""CLI entry point for the MARL platform."""

import typer

app = typer.Typer(
    name="platform",
    help="Research platform for MARL experiment workflows.",
    add_completion=False,
)


@app.command()
def run(
    experiment: str = typer.Argument(..., help="Experiment name (resolves to experiments/configs/<name>.yaml)"),
    config_dir: str = typer.Option("experiments/configs", help="Override config directory"),
) -> None:
    """Run an experiment from config file."""
    raise NotImplementedError("run command not yet implemented")


@app.command()
def report(
    experiment: str = typer.Argument(..., help="Experiment ID (resolves to results/<id>/)"),
    reference: str = typer.Option(None, help="Reference experiment for comparison"),
) -> None:
    """Generate report for an experiment."""
    raise NotImplementedError("report command not yet implemented")


@app.command()
def export(
    experiment: str = typer.Argument(..., help="Experiment ID to export"),
    output: str = typer.Option(None, help="Output bundle path"),
) -> None:
    """Export experiment to shareable bundle."""
    raise NotImplementedError("export command not yet implemented")


@app.command("import")
def import_(
    bundle: str = typer.Argument(..., help="Bundle file path"),
) -> None:
    """Import experiment bundle."""
    raise NotImplementedError("import command not yet implemented")


if __name__ == "__main__":
    app()
