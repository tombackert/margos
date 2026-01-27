"""CLI entry point for the MARL platform."""

from pathlib import Path

import typer

from marl_platform.analysis import generate_report
from marl_platform.export import export_bundle, import_bundle
from marl_platform.orchestrator import run_experiment

app = typer.Typer(
    name="platform",
    help="Research platform for MARL experiment workflows.",
    add_completion=False,
)


def resolve_experiment_path(experiment: str, results_dir: str) -> Path:
    """Resolve experiment ID to results directory path.

    Handles:
    - "exp_v1_20240115" -> "{results_dir}/exp_v1_20240115/"
    - "/absolute/path/" -> use as-is
    """
    path = Path(experiment)

    if path.is_absolute():
        return path

    return Path(results_dir) / experiment


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
    results_dir: str = typer.Option("results", help="Override results directory"),
) -> None:
    """Generate report for an experiment."""
    experiment_path = resolve_experiment_path(experiment, results_dir)

    if not experiment_path.exists():
        typer.echo("Error: Experiment not found")
        typer.echo(f"  Path: {experiment_path}/")
        typer.echo("  Fix: Check the experiment ID or run `ls results/` to see available experiments")
        raise typer.Exit(1)

    reference_path = None
    if reference:
        reference_path = resolve_experiment_path(reference, results_dir)
        if not reference_path.exists():
            typer.echo("Error: Reference experiment not found")
            typer.echo(f"  Path: {reference_path}/")
            typer.echo("  Fix: Check the reference ID or run `ls results/` to see available experiments")
            raise typer.Exit(1)

    if reference_path:
        typer.echo("Generating report with comparison...")
        typer.echo(f"Reference: {reference_path}/")
    else:
        typer.echo(f"Generating report for: {experiment}")

    report_path = generate_report(str(experiment_path), str(reference_path) if reference_path else None)

    typer.echo(f"Report saved to: {report_path}")


@app.command()
def export(
    experiment: str = typer.Argument(..., help="Experiment ID to export"),
    output: str = typer.Option(None, help="Output bundle path (default: bundles/<experiment>.zip)"),
    results_dir: str = typer.Option("results", help="Override results directory"),
) -> None:
    """Export experiment to shareable bundle."""
    experiment_path = resolve_experiment_path(experiment, results_dir)

    if not experiment_path.exists():
        typer.echo("Error: Experiment not found")
        typer.echo(f"  Path: {experiment_path}/")
        typer.echo("  Fix: Check the experiment ID or run `ls results/` to see available experiments")
        raise typer.Exit(1)

    if output is None:
        output_path = Path("bundles") / f"{experiment}.zip"
    else:
        output_path = Path("bundles") / output if not Path(output).is_absolute() else Path(output)

    typer.echo(f"Exporting experiment: {experiment}")

    bundle_path = export_bundle(str(experiment_path), str(output_path))

    typer.echo(f"Bundle created: {bundle_path}")


def resolve_bundle_path(bundle: str, bundles_dir: str) -> Path:
    """Resolve bundle filename to full path.

    Handles:
    - "exp_v1.zip" -> "{bundles_dir}/exp_v1.zip"
    - "/absolute/path.zip" -> use as-is
    """
    path = Path(bundle)

    if path.is_absolute():
        return path

    return Path(bundles_dir) / bundle


@app.command("import")
def import_(
    bundle: str = typer.Argument(..., help="Bundle file to import"),
    bundles_dir: str = typer.Option("bundles", help="Bundles directory (override default)"),
) -> None:
    """Import experiment bundle."""
    bundle_path = resolve_bundle_path(bundle, bundles_dir)

    if not bundle_path.exists():
        typer.echo("Error: Bundle not found")
        typer.echo(f"  Path: {bundle_path}")
        typer.echo("  Fix: Check the filename or run `ls bundles/` to see available bundles")
        raise typer.Exit(1)

    typer.echo(f"Importing bundle: {bundle_path}")

    imported_path = import_bundle(str(bundle_path))

    typer.echo(f"Imported to: {imported_path}")


if __name__ == "__main__":
    app()
