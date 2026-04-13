"""CLI entry point for the MARL platform."""

from pathlib import Path
from typing import Optional

import typer

from marl_platform.analysis import compare_runs
from marl_platform.analysis.report import calculate_auc, calculate_duration, read_metrics
from marl_platform.export import (
    compare_fingerprints,
    export_bundle,
    get_bundle_fingerprint,
    import_bundle,
)
from marl_platform.orchestrator import run_experiment
from marl_platform.utils import (
    console,
    create_comparison_table,
    create_fingerprint_table,
    create_grouped_selection_table,
    create_list_table,
    create_selection_table,
)
from marl_platform.utils.errors import (
    BundleNotFoundError,
    ConfigNotFoundError,
    ExperimentNotFoundError,
    PlatformError,
    display_error,
)
from marl_platform.utils.fingerprint import capture_fingerprint
from marl_platform.utils.progress import OperationProgress


def list_items(
    directory: str,
    pattern: str | None = None,
    is_dir: bool = False,
    use_stem: bool = False,
) -> list[str]:
    """List items in a directory matching criteria.

    Args:
        directory: Path to directory to list
        pattern: Glob pattern for files (e.g., "*.yaml"). If None, lists directories.
        is_dir: If True and pattern is None, list directories only
        use_stem: If True, return file stems instead of full names

    Returns:
        List of item names sorted by modification time (oldest first, newest last)
    """
    path = Path(directory)
    if not path.exists():
        return []

    if pattern:
        paths = list(path.glob(pattern))
    else:
        paths = [d for d in path.iterdir() if d.is_dir()]

    # Sort by modification time (oldest first, newest last)
    paths.sort(key=lambda p: p.stat().st_mtime)

    if pattern and use_stem:
        return [p.stem for p in paths]
    return [p.name for p in paths]


def list_configs(config_dir: str = "experiments/configs") -> list[str]:
    """List available config files."""
    return list_items(config_dir, pattern="*.yaml", use_stem=True)


def list_results(results_dir: str = "results") -> list[str]:
    """List available experiment results."""
    return list_items(results_dir, is_dir=True)


def list_imported(imported_dir: str = "experiments/imported") -> list[str]:
    """List imported experiments."""
    return list_items(imported_dir, is_dir=True)


def list_bundles(bundles_dir: str = "bundles") -> list[str]:
    """List available bundles."""
    return list_items(bundles_dir, pattern="*.zip")


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

    table = create_selection_table(items, prompt, show_cancel=allow_exit)
    console.print()
    console.print(table)
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


def select_from_grouped_list(
    options: list[tuple[str, str]],
    prompt: str,
    group_labels: dict[str, str],
    exit_label: str = "Cancel / Exit",
) -> tuple[str, str] | None:
    """Prompt user to select from a grouped numbered list.

    Args:
        options: List of (source, name) tuples
        prompt: Header text to display
        group_labels: Dict mapping source to display label (e.g., {"results": "Results (results/):"})
        exit_label: Label for the exit option

    Returns:
        Selected (source, name) tuple or None if user exits
    """
    if not options:
        return None

    table = create_grouped_selection_table(options, prompt, group_labels, exit_label)
    console.print()
    console.print(table)
    console.print()

    while True:
        choice = typer.prompt("Select number (or 'q' to cancel)", default="1")

        if choice.lower() in ("q", "0", "quit", "exit", "cancel", "skip"):
            return None

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx]
            console.print(f"[red]Please enter a number between 1 and {len(options)}[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number (or 'q' to cancel)[/red]")

def _print_run_summary(output_dir: str) -> None:
    """Print a Rich summary table after training completes."""
    from rich.table import Table

    output_path = Path(output_dir)
    log_path = output_path / "logs" / "metrics.jsonl"

    try:
        metrics = read_metrics(log_path)
    except Exception:
        typer.echo(f"\nOutput: {output_dir}")
        return

    rewards = [m["episode_reward_mean"] for m in metrics if m.get("episode_reward_mean") is not None]
    final_reward = rewards[-1] if rewards else None
    best_reward = max(rewards) if rewards else None
    auc = calculate_auc(metrics) if rewards else None
    duration = calculate_duration(metrics)
    iterations = len(metrics)

    config_hash = "N/A"
    config_hash_path = output_path / "config_hash.txt"
    if config_hash_path.exists():
        full_hash = config_hash_path.read_text().strip()
        config_hash = full_hash[:8] + "..." if len(full_hash) > 8 else full_hash

    table = Table(title="Training Complete", show_header=True, header_style="bold")
    table.add_column("Metric", style="dim")
    table.add_column("Value", justify="right")

    table.add_row("Final Reward", f"{final_reward:.2f}" if final_reward is not None else "N/A")
    table.add_row("Best Reward", f"{best_reward:.2f}" if best_reward is not None else "N/A")
    table.add_row("AUC", f"{auc:.1f}" if auc is not None else "N/A")
    table.add_row("Duration", duration)
    table.add_row("Iterations", str(iterations))
    table.add_row("Config Hash", config_hash)
    table.add_row("Output", str(output_path))

    console.print()
    console.print(table)


app = typer.Typer(
    name="platform",
    help="Research platform for MARL experiment workflows.\n\nUsage: platform [run | compare | export | import | show]",
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


def resolve_path(name: str, base_dir: str, extension: str | None = None) -> Path:
    """Resolve a name to a path within a base directory.

    Args:
        name: The name or path to resolve
        base_dir: The base directory for relative paths
        extension: Optional extension to add if not present (e.g., ".yaml")

    Returns:
        Resolved Path object
    """
    path = Path(name)
    if path.is_absolute():
        return path

    if extension and not name.endswith(extension):
        name = f"{name}{extension}"

    return Path(base_dir) / name


def resolve_config_path(experiment: str, config_dir: str) -> Path:
    """Resolve experiment name to config file path."""
    return resolve_path(experiment, config_dir, extension=".yaml")


def resolve_experiment_path(experiment: str, results_dir: str) -> Path:
    """Resolve experiment ID to results directory path."""
    return resolve_path(experiment, results_dir)


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
    TensorBoard launches automatically and is available at http://localhost:6006.
    """
    tb_process = None
    try:
        source = "config"  # Default source

        # Interactive selection if no experiment provided
        if experiment is None:
            configs = list_configs(config_dir)
            imported = list_imported(imported_dir)

            all_options = [("config", c) for c in configs] + [("imported", i) for i in imported]

            if not all_options:
                typer.echo("No experiments found in configs or imported directories.")
                raise typer.Exit(1)

            result = select_from_grouped_list(
                all_options,
                "Available experiments:",
                {"config": "Configs (experiments/configs/):", "imported": "Imported (experiments/imported/):"},
            )
            if result is None:
                console.print("[dim]Cancelled.[/dim]")
                raise typer.Exit(0)

            source, experiment = result

        # Resolve config path based on source
        if source == "imported" or (Path(imported_dir) / experiment / "config.yaml").exists():
            config_path = Path(imported_dir) / experiment / "config.yaml"
        else:
            config_path = resolve_config_path(experiment, config_dir)

        if not config_path.exists():
            raise ConfigNotFoundError(str(config_path))

        typer.echo(f"Running experiment: {experiment}")
        typer.echo(f"Config: {config_path}")
        typer.echo("")

        output_dir, tb_process = run_experiment(str(config_path))
        _print_run_summary(output_dir)

        typer.echo("")

    except PlatformError as e:
        display_error(e, verbose=_verbose)
        raise typer.Exit(1)
    finally:
        if tb_process is not None and tb_process.poll() is None:
            tb_process.kill()


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
def compare(
    experiment: Optional[str] = typer.Argument(
        None,
        help="Experiment to evaluate",
    ),
    reference: Optional[str] = typer.Argument(
        None,
        help="Reference experiment",
    ),
    results_dir: str = typer.Option("results", "--results-dir", "-d", help="Override results directory"),
    imported_dir: str = typer.Option("experiments/imported", "--imported-dir", "-i", help="Imported experiments directory"),
) -> None:
    """Compare two experiments and report SRQ5 and SRQ3 outcomes.

    Compares the mean reward over the last 50 logged values, or all available
    values if fewer than 50 are present, using the platform's default ±1%
    tolerance. The command reports:
    - SRQ5 handoff success from reward agreement only
    - SRQ3 strict reproducibility from reward, AUC, config identity, and runtime config integrity

    Examples:
        platform compare                           # Interactive selection for both
        platform compare exp_v1 exp_v2             # Compare exp_v1 against exp_v2
        platform compare exp_v1                    # Select reference interactively
    """
    group_labels = {"results": "Results (results/):", "imported": "Imported (experiments/imported/):"}

    try:
        # Build list of all available experiments
        results = list_results(results_dir)
        imported = list_imported(imported_dir)
        all_options = [("results", r) for r in results] + [("imported", i) for i in imported]

        # Interactive selection if no experiment provided
        if experiment is None:
            if not all_options:
                typer.echo("No experiments found in results or imported directories.")
                raise typer.Exit(1)

            result = select_from_grouped_list(all_options, "Select experiment to evaluate:", group_labels)
            if result is None:
                console.print("[dim]Cancelled.[/dim]")
                raise typer.Exit(0)

            _, experiment = result

        experiment_path = resolve_experiment_path_extended(experiment, results_dir, imported_dir)

        if not experiment_path.exists():
            raise ExperimentNotFoundError(str(experiment_path))

        # Interactive reference selection if no reference provided
        reference_path = None
        if reference:
            reference_path = resolve_experiment_path_extended(reference, results_dir, imported_dir)
            if not reference_path.exists():
                raise ExperimentNotFoundError(str(reference_path))
        else:
            ref_options = [(s, n) for s, n in all_options if n != experiment]

            if not ref_options:
                typer.echo("No other experiments available for comparison.")
                raise typer.Exit(1)

            result = select_from_grouped_list(
                ref_options,
                "Select reference experiment:",
                group_labels,
            )
            if result is None:
                console.print("[dim]Cancelled.[/dim]")
                raise typer.Exit(0)

            _, ref_name = result
            reference_path = resolve_experiment_path_extended(ref_name, results_dir, imported_dir)

        typer.echo(f"Comparing: {experiment}")
        typer.echo(f"Reference: {reference_path.name}")
        typer.echo("")

        # Run comparison
        comparison = compare_runs(str(experiment_path), str(reference_path))

        # Display Rich comparison table
        table = create_comparison_table(comparison)
        console.print()
        console.print(table)

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
    """Resolve bundle filename to full path."""
    return resolve_path(bundle, bundles_dir)


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
            table = create_fingerprint_table(comparison)
            console.print()
            console.print(table)
            if not comparison.get("critical_match", comparison["all_match"]):
                console.print(
                    "\n[yellow]Warning:[/yellow] Critical environment mismatches detected. "
                    "Import and reproduction remain allowed, but validity is weakened until "
                    "the environments are better aligned."
                )
            elif not comparison["all_match"]:
                console.print(
                    "\n[yellow]Warning:[/yellow] Non-critical environment differences detected. "
                    "Reproduction remains allowed."
                )

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
        table = create_list_table(title, items, path)

        if table is None:
            console.print(f"\n[dim]No {title.lower()} found in {path}[/dim]")
            return

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


p_app = typer.Typer(
    name="p",
    help="Short aliases: p r=run, p s=show, p c=compare, p e=export, p i=import",
    add_completion=False,
)


@p_app.callback()
def p_main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show full traceback on errors"),
) -> None:
    global _verbose
    _verbose = verbose


p_app.command("r")(run)
p_app.command("s")(show)
p_app.command("c")(compare)
p_app.command("e")(export)
p_app.command("i")(import_)


if __name__ == "__main__":
    app()
