"""CLI entry point for the MARL platform."""

from pathlib import Path
from typing import Optional

import typer

from marl_platform.analysis import compare_runs, generate_report
from marl_platform.export import (
    compare_fingerprints,
    export_bundle,
    format_fingerprint_comparison,
    get_bundle_fingerprint,
    import_bundle,
)
from marl_platform.orchestrator import run_experiment
from marl_platform.utils.errors import (
    BundleNotFoundError,
    ConfigNotFoundError,
    ExperimentNotFoundError,
    PlatformError,
    display_error,
)
from marl_platform.utils.fingerprint import capture_fingerprint
from marl_platform.utils.progress import mock_progress

app = typer.Typer(
    name="platform",
    help="Research platform for MARL experiment workflows.",
    add_completion=False,
)

# Global state for verbose flag
_verbose: bool = False


@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show full traceback on errors"),
) -> None:
    """Research platform for MARL experiment workflows."""
    global _verbose
    _verbose = verbose


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
    try:
        config_path = resolve_config_path(experiment, config_dir)

        if not config_path.exists():
            raise ConfigNotFoundError(str(config_path))

        typer.echo(f"Running experiment: {experiment}")
        typer.echo(f"Config: {config_path}")
        typer.echo("")

        output_dir = run_experiment(str(config_path))

        typer.echo("")
        typer.echo(f"Output: {output_dir}")
    except PlatformError as e:
        display_error(e, verbose=_verbose)
        raise typer.Exit(1)


@app.command()
def report(
    experiment: str = typer.Argument(..., help="Experiment ID (resolves to results/<id>/)"),
    reference: Optional[str] = typer.Option(None, help="Reference experiment for comparison"),
    results_dir: str = typer.Option("results", help="Override results directory"),
) -> None:
    """Generate report for an experiment.

    Examples:
        platform report exp_v1_20240115
        platform report exp_v1_20240115 --reference exp_v1_20240114
    """
    try:
        experiment_path = resolve_experiment_path(experiment, results_dir)

        if not experiment_path.exists():
            raise ExperimentNotFoundError(str(experiment_path))

        reference_path = None
        if reference:
            reference_path = resolve_experiment_path(reference, results_dir)
            if not reference_path.exists():
                raise ExperimentNotFoundError(str(reference_path))

        if reference_path:
            typer.echo(f"Generating report for: {experiment}")
            typer.echo(f"Reference: {reference}")
        else:
            typer.echo(f"Generating report for: {experiment}")

        with mock_progress("Generating report..."):
            report_path = generate_report(str(experiment_path), str(reference_path) if reference_path else None)

        # Display summary
        summary_path = Path(report_path) / "summary.txt"
        if summary_path.exists():
            typer.echo("")
            typer.echo(summary_path.read_text())

        typer.echo(f"Report saved to: {report_path}")
    except PlatformError as e:
        display_error(e, verbose=_verbose)
        raise typer.Exit(1)


@app.command()
def export(
    experiment: str = typer.Argument(..., help="Experiment ID to export"),
    output: Optional[str] = typer.Option(None, help="Output bundle path (default: bundles/<experiment>.zip)"),
    results_dir: str = typer.Option("results", help="Override results directory"),
) -> None:
    """Export experiment to shareable bundle.

    Examples:
        platform export exp_v1_20240115
        platform export exp_v1_20240115 --output my_bundle.zip
    """
    try:
        experiment_path = resolve_experiment_path(experiment, results_dir)

        if not experiment_path.exists():
            raise ExperimentNotFoundError(str(experiment_path))

        typer.echo(f"Exporting experiment: {experiment}")

        with mock_progress("Creating bundle..."):
            bundle_path = export_bundle(str(experiment_path), output)

        typer.echo(f"Bundle created: {bundle_path}")
    except PlatformError as e:
        display_error(e, verbose=_verbose)
        raise typer.Exit(1)


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
    """Import experiment bundle.

    Examples:
        platform import exp_v1.zip
        platform import /path/to/bundle.zip
    """
    try:
        bundle_path = resolve_bundle_path(bundle, bundles_dir)

        if not bundle_path.exists():
            raise BundleNotFoundError(str(bundle_path))

        typer.echo(f"Importing bundle: {bundle_path}")

        with mock_progress("Importing bundle..."):
            imported_path = import_bundle(str(bundle_path))

        typer.echo(f"Imported to: {imported_path}")

        # Compare fingerprints
        bundle_fp = get_bundle_fingerprint(imported_path)
        if bundle_fp:
            current_fp = capture_fingerprint()
            comparison = compare_fingerprints(bundle_fp, current_fp)
            typer.echo(format_fingerprint_comparison(comparison))

    except PlatformError as e:
        display_error(e, verbose=_verbose)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
