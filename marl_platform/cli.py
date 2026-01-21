"""CLI entry point for the MARL platform."""

from pathlib import Path

import typer

from marl_platform.orchestrator import run_experiment

app = typer.Typer(
    name="platform",
    help="Research platform for MARL experiment workflows.",
    add_completion=False,
)


def resolve_config_path(experiment: str, config_dir: str) -> Path:
    """Resolve experiment name to config file path.

    Handles:
    - "exp_v1" -> "{config_dir}/exp_v1.yaml"
    - "exp_v1.yaml" -> "{config_dir}/exp_v1.yaml"
    - "/absolute/path.yaml" -> use as-is
    """
    path = Path(experiment)

    if path.is_absolute():
        return path

    if not experiment.endswith(".yaml"):
        experiment = f"{experiment}.yaml"

    return Path(config_dir) / experiment


@app.command()
def run(
    experiment: str = typer.Argument(..., help="Experiment name (resolves to experiments/configs/<name>.yaml)"),
    config_dir: str = typer.Option("experiments/configs", help="Override config directory"),
) -> None:
    """Run an experiment from config file."""
    config_path = resolve_config_path(experiment, config_dir)

    if not config_path.exists():
        typer.echo(f"Error: Config file not found")
        typer.echo(f"  Path: {config_path}")
        typer.echo(f"  Fix: Create the config file or check the experiment name")
        raise typer.Exit(1)

    typer.echo(f"Running experiment: {experiment}")
    typer.echo(f"Config: {config_path}")

    output_dir = run_experiment(str(config_path))

    typer.echo(f"Output: {output_dir}")


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
