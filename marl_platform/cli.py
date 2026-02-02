"""CLI entry point for the MARL platform."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

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
from marl_platform.utils.progress import OperationProgress

console = Console()


def list_configs(config_dir: str = "experiments/configs") -> list[str]:
    """List available config files."""
    config_path = Path(config_dir)
    if not config_path.exists():
        return []
    return sorted([f.stem for f in config_path.glob("*.yaml")])


def list_results(results_dir: str = "results") -> list[str]:
    """List available experiment results."""
    results_path = Path(results_dir)
    if not results_path.exists():
        return []
    return sorted(
        [d.name for d in results_path.iterdir() if d.is_dir()],
        reverse=True,  # Most recent first
    )


def list_imported(imported_dir: str = "experiments/imported") -> list[str]:
    """List imported experiments."""
    imported_path = Path(imported_dir)
    if not imported_path.exists():
        return []
    return sorted(
        [d.name for d in imported_path.iterdir() if d.is_dir()],
        reverse=True,
    )


def list_bundles(bundles_dir: str = "bundles") -> list[str]:
    """List available bundles."""
    bundles_path = Path(bundles_dir)
    if not bundles_path.exists():
        return []
    return sorted([f.name for f in bundles_path.glob("*.zip")])


def select_from_list(items: list[str], prompt: str, allow_exit: bool = True) -> str | None:
    """Prompt user to select from a numbered list.

    Args:
        items: List of items to choose from
        prompt: Header text to display
        allow_exit: If True, allows 'q' or '0' to exit and returns None

    Returns:
        Selected item or None if user exits
    """
    if not items:
        raise typer.Exit(1)

    console.print(f"\n[bold]{prompt}[/bold]")
    for i, item in enumerate(items, 1):
        console.print(f"  [{i}] {item}")
    if allow_exit:
        console.print(f"  [dim][0] Cancel / Exit[/dim]")
    console.print()

    while True:
        choice = typer.prompt("Select number (or 'q' to cancel)", default="1")

        # Check for exit
        if allow_exit and choice.lower() in ("q", "0", "quit", "exit", "cancel"):
            return None

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(items):
                return items[idx]
            if idx == -1 and allow_exit:  # User entered 0
                return None
            console.print(f"[red]Please enter a number between 1 and {len(items)}[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number (or 'q' to cancel)[/red]")

app = typer.Typer(
    name="platform",
    help="Research platform for MARL experiment workflows.\n\nUsage: platform [run | report | export | import | show]",
    add_completion=False,  # Disabled - shell completion install is too slow
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
    experiment: Optional[str] = typer.Argument(
        None,
        help="Experiment name (resolves to experiments/configs/<name>.yaml)",
    ),
    config_dir: str = typer.Option("experiments/configs", "--config-dir", "-c", help="Override config directory"),
    imported_dir: str = typer.Option("experiments/imported", "--imported-dir", "-i", help="Imported experiments directory"),
) -> None:
    """Run an experiment from config file.

    If no experiment name is provided, shows a selection list.
    TensorBoard logging is enabled by default (config: training.tensorboard).
    """
    try:
        # Interactive selection if no experiment provided
        if experiment is None:
            configs = list_configs(config_dir)
            imported = list_imported(imported_dir)

            all_options = []
            for c in configs:
                all_options.append(("config", c))
            for i in imported:
                all_options.append(("imported", i))

            if not all_options:
                typer.echo("No experiments found in configs or imported directories.")
                raise typer.Exit(1)

            console.print("\n[bold]Available experiments:[/bold]")
            console.print("[dim]  Configs (experiments/configs/):[/dim]")
            config_start = 1
            for idx, (source, name) in enumerate(all_options, 1):
                if source == "config":
                    console.print(f"  [{idx}] {name}")
                else:
                    break
                config_start = idx + 1

            if any(s == "imported" for s, _ in all_options):
                console.print("[dim]  Imported (experiments/imported/):[/dim]")
                for idx, (source, name) in enumerate(all_options, 1):
                    if source == "imported":
                        console.print(f"  [{idx}] {name} [yellow](imported)[/yellow]")

            console.print(f"  [dim][0] Cancel / Exit[/dim]")
            console.print()

            while True:
                choice = typer.prompt("Select number (or 'q' to cancel)", default="1")

                # Check for exit
                if choice.lower() in ("q", "0", "quit", "exit", "cancel"):
                    console.print("[dim]Cancelled.[/dim]")
                    raise typer.Exit(0)

                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(all_options):
                        source, experiment = all_options[idx]
                        break
                    console.print(f"[red]Please enter a number between 1 and {len(all_options)}[/red]")
                except ValueError:
                    console.print("[red]Please enter a valid number (or 'q' to cancel)[/red]")

            if source == "imported":
                config_path = Path(imported_dir) / experiment / "config.yaml"
            else:
                config_path = resolve_config_path(experiment, config_dir)
        else:
            # Check if experiment is in imported directory
            imported_config = Path(imported_dir) / experiment / "config.yaml"
            if imported_config.exists():
                config_path = imported_config
            else:
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


def resolve_experiment_path_extended(experiment: str, results_dir: str, imported_dir: str) -> Path:
    """Resolve experiment ID to path, checking both results and imported directories."""
    path = Path(experiment)

    if path.is_absolute():
        return path

    # Check results directory first
    results_path = Path(results_dir) / experiment
    if results_path.exists():
        return results_path

    # Check imported directory
    imported_path = Path(imported_dir) / experiment
    if imported_path.exists():
        return imported_path

    # Default to results dir (will fail with appropriate error)
    return results_path


@app.command()
def report(
    experiment: Optional[str] = typer.Argument(
        None,
        help="Experiment ID (resolves to results/<id>/)",
    ),
    reference: Optional[str] = typer.Option(
        None,
        "--reference", "-r",
        help="Reference experiment for comparison",
    ),
    compare: bool = typer.Option(False, "--compare", help="Enable comparison mode (select reference interactively)"),
    results_dir: str = typer.Option("results", "--results-dir", "-d", help="Override results directory"),
    imported_dir: str = typer.Option("experiments/imported", "--imported-dir", "-i", help="Imported experiments directory"),
) -> None:
    """Generate report for an experiment.

    Examples:
        platform report exp_v1_20240115
        platform report exp_v1_20240115 --reference exp_v1_20240114
        platform report --compare  # Interactive selection for both
    """
    try:
        # Build list of all available experiments
        results = list_results(results_dir)
        imported = list_imported(imported_dir)

        all_options = []
        for r in results:
            all_options.append(("results", r))
        for i in imported:
            all_options.append(("imported", i))

        # Interactive selection if no experiment provided
        if experiment is None:
            if not all_options:
                typer.echo("No experiments found in results or imported directories.")
                raise typer.Exit(1)

            console.print("\n[bold]Select experiment for report:[/bold]")
            console.print("[dim]  Results (results/):[/dim]")
            for idx, (source, name) in enumerate(all_options, 1):
                if source == "results":
                    console.print(f"  [{idx}] {name}")

            if any(s == "imported" for s, _ in all_options):
                console.print("[dim]  Imported (experiments/imported/):[/dim]")
                for idx, (source, name) in enumerate(all_options, 1):
                    if source == "imported":
                        console.print(f"  [{idx}] {name} [yellow](imported)[/yellow]")

            console.print(f"  [dim][0] Cancel / Exit[/dim]")
            console.print()

            while True:
                choice = typer.prompt("Select number (or 'q' to cancel)", default="1")

                if choice.lower() in ("q", "0", "quit", "exit", "cancel"):
                    console.print("[dim]Cancelled.[/dim]")
                    raise typer.Exit(0)

                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(all_options):
                        source, experiment = all_options[idx]
                        break
                    console.print(f"[red]Please enter a number between 1 and {len(all_options)}[/red]")
                except ValueError:
                    console.print("[red]Please enter a valid number (or 'q' to cancel)[/red]")

        experiment_path = resolve_experiment_path_extended(experiment, results_dir, imported_dir)

        if not experiment_path.exists():
            raise ExperimentNotFoundError(str(experiment_path))

        # Interactive reference selection if --compare flag or no reference provided
        reference_path = None
        if reference:
            reference_path = resolve_experiment_path_extended(reference, results_dir, imported_dir)
            if not reference_path.exists():
                raise ExperimentNotFoundError(str(reference_path))
        elif compare:
            # Filter out the selected experiment from options
            ref_options = [(s, n) for s, n in all_options if n != experiment]

            if not ref_options:
                typer.echo("No other experiments available for comparison.")
            else:
                console.print("\n[bold]Select reference experiment for comparison:[/bold]")
                console.print("[dim]  Results (results/):[/dim]")
                for idx, (source, name) in enumerate(ref_options, 1):
                    if source == "results":
                        console.print(f"  [{idx}] {name}")

                if any(s == "imported" for s, _ in ref_options):
                    console.print("[dim]  Imported (experiments/imported/):[/dim]")
                    for idx, (source, name) in enumerate(ref_options, 1):
                        if source == "imported":
                            console.print(f"  [{idx}] {name} [yellow](imported)[/yellow]")

                console.print(f"  [dim][0] Skip comparison[/dim]")
                console.print()

                while True:
                    choice = typer.prompt("Select reference (or 'q' to skip)", default="0")

                    if choice.lower() in ("q", "0", "quit", "skip", "cancel"):
                        console.print("[dim]Skipping comparison.[/dim]")
                        break

                    try:
                        idx = int(choice) - 1
                        if 0 <= idx < len(ref_options):
                            _, ref_name = ref_options[idx]
                            reference_path = resolve_experiment_path_extended(ref_name, results_dir, imported_dir)
                            break
                        console.print(f"[red]Please enter a number between 1 and {len(ref_options)}[/red]")
                    except ValueError:
                        console.print("[red]Please enter a valid number (or 'q' to skip)[/red]")

        if reference_path:
            typer.echo(f"Generating report for: {experiment}")
            typer.echo(f"Reference: {reference}")
        else:
            typer.echo(f"Generating report for: {experiment}")

        with OperationProgress("Generating report") as progress:
            report_path = generate_report(
                str(experiment_path),
                str(reference_path) if reference_path else None,
                progress_callback=progress.callback,
            )

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
    experiment: Optional[str] = typer.Argument(
        None,
        help="Experiment ID to export",
    ),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output bundle path (default: bundles/<experiment>.zip)"),
    results_dir: str = typer.Option("results", "--results-dir", "-d", help="Override results directory"),
) -> None:
    """Export experiment to shareable bundle.

    Examples:
        platform export exp_v1_20240115
        platform export exp_v1_20240115 --output my_bundle.zip
    """
    try:
        # Interactive selection if no experiment provided
        if experiment is None:
            results = list_results(results_dir)
            if not results:
                typer.echo("No experiments found in results directory.")
                raise typer.Exit(1)

            experiment = select_from_list(results, "Available experiments:")
            if experiment is None:
                console.print("[dim]Cancelled.[/dim]")
                raise typer.Exit(0)

        experiment_path = resolve_experiment_path(experiment, results_dir)

        if not experiment_path.exists():
            raise ExperimentNotFoundError(str(experiment_path))

        typer.echo(f"Exporting experiment: {experiment}")

        with OperationProgress("Creating bundle") as progress:
            bundle_path = export_bundle(
                str(experiment_path),
                output,
                progress_callback=progress.callback,
            )

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
    bundle: Optional[str] = typer.Argument(
        None,
        help="Bundle file to import",
    ),
    bundles_dir: str = typer.Option("bundles", "--bundles-dir", "-b", help="Bundles directory (override default)"),
) -> None:
    """Import experiment bundle.

    Examples:
        platform import exp_v1.zip
        platform import /path/to/bundle.zip
    """
    try:
        # Interactive selection if no bundle provided
        if bundle is None:
            bundles = list_bundles(bundles_dir)
            if not bundles:
                typer.echo("No bundles found in bundles directory.")
                raise typer.Exit(1)

            bundle = select_from_list(bundles, "Available bundles:")
            if bundle is None:
                console.print("[dim]Cancelled.[/dim]")
                raise typer.Exit(0)

        bundle_path = resolve_bundle_path(bundle, bundles_dir)

        if not bundle_path.exists():
            raise BundleNotFoundError(str(bundle_path))

        typer.echo(f"Importing bundle: {bundle_path}")

        with OperationProgress("Importing bundle") as progress:
            imported_path = import_bundle(
                str(bundle_path),
                progress_callback=progress.callback,
            )

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


@app.command()
def show(
    category: Optional[str] = typer.Argument(
        None,
        help="Category to show: configs, results, imported, bundles, or all",
    ),
    config_dir: str = typer.Option("experiments/configs", "--config-dir", "-c", help="Config directory"),
    results_dir: str = typer.Option("results", "--results-dir", "-d", help="Results directory"),
    imported_dir: str = typer.Option("experiments/imported", "--imported-dir", "-i", help="Imported experiments directory"),
    bundles_dir: str = typer.Option("bundles", "--bundles-dir", "-b", help="Bundles directory"),
) -> None:
    """Show available configs, experiments, or bundles.

    Examples:
        platform show              # Show all categories
        platform show configs      # Show only config files
        platform show results      # Show experiment results
        platform show imported     # Show imported experiments
        platform show bundles      # Show available bundles
    """
    valid_categories = ["configs", "results", "imported", "bundles", "all"]

    if category is None:
        category = "all"

    if category not in valid_categories:
        typer.echo(f"Invalid category: {category}")
        typer.echo(f"Valid categories: {', '.join(valid_categories)}")
        raise typer.Exit(1)

    def show_table(title: str, items: list[str], path: str) -> None:
        """Display a category table."""
        table = Table(title=title, show_header=True, header_style="bold blue")
        table.add_column("#", style="dim", width=4)
        table.add_column("Name", style="cyan")
        table.add_column("Path", style="dim")

        if not items:
            console.print(f"\n[dim]No {title.lower()} found in {path}[/dim]")
            return

        for i, item in enumerate(items, 1):
            table.add_row(str(i), item, f"{path}/{item}")

        console.print()
        console.print(table)

    if category in ["configs", "all"]:
        configs = list_configs(config_dir)
        show_table("Configs", configs, config_dir)

    if category in ["results", "all"]:
        results = list_results(results_dir)
        show_table("Results", results, results_dir)

    if category in ["imported", "all"]:
        imported = list_imported(imported_dir)
        show_table("Imported Experiments", imported, imported_dir)

    if category in ["bundles", "all"]:
        bundles = list_bundles(bundles_dir)
        show_table("Bundles", bundles, bundles_dir)


if __name__ == "__main__":
    app()
