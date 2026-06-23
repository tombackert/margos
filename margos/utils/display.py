"""Unified display utilities for CLI tables and lists."""

from rich.console import Console
from rich.table import Table

# Shared console instance
console = Console()

# Style constants
STYLE_HEADER = "bold blue"
STYLE_ROW_NUM = "dim"
STYLE_ITEM_NAME = "cyan"
STYLE_PATH = "dim"
STYLE_OK = "green"
STYLE_FAIL = "red"
STYLE_IMPORTED = "yellow"


def create_list_table(
    title: str,
    items: list[str],
    path: str,
    show_path: bool = True,
) -> Table | None:
    """Create a Rich Table for displaying a list of items.

    Args:
        title: Table title.
        items: List of item names.
        path: Base path for items.
        show_path: Whether to show the path column.

    Returns:
        Rich Table or None if items is empty.
    """
    if not items:
        return None

    table = Table(title=title, show_header=True, header_style=STYLE_HEADER)
    table.add_column("#", style=STYLE_ROW_NUM, width=4)
    table.add_column("Name", style=STYLE_ITEM_NAME)
    if show_path:
        table.add_column("Path", style=STYLE_PATH)

    for i, item in enumerate(items, 1):
        if show_path:
            table.add_row(str(i), item, f"{path}/{item}")
        else:
            table.add_row(str(i), item)

    return table


def create_selection_table(
    items: list[str],
    prompt: str,
    show_cancel: bool = True,
) -> Table:
    """Create a Rich Table for selection prompts.

    Args:
        items: List of items to choose from.
        prompt: Header text (used as table title).
        show_cancel: Whether to show cancel row.

    Returns:
        Rich Table for selection.
    """
    table = Table(title=prompt, show_header=True, header_style=STYLE_HEADER)
    table.add_column("#", style=STYLE_ROW_NUM, width=4)
    table.add_column("Name", style=STYLE_ITEM_NAME)

    for i, item in enumerate(items, 1):
        table.add_row(str(i), item)

    if show_cancel:
        table.add_row("[dim]0[/dim]", "[dim]Cancel / Exit[/dim]")

    return table


def create_grouped_selection_table(
    options: list[tuple[str, str]],
    prompt: str,
    group_labels: dict[str, str],
    exit_label: str = "Cancel / Exit",
) -> Table:
    """Create a Rich Table for grouped selection prompts.

    Args:
        options: List of (source, name) tuples.
        prompt: Table title.
        group_labels: Dict mapping source to display label.
        exit_label: Label for the exit option.

    Returns:
        Rich Table for grouped selection.
    """
    table = Table(title=prompt, show_header=True, header_style=STYLE_HEADER)
    table.add_column("#", style=STYLE_ROW_NUM, width=4)
    table.add_column("Name", style=STYLE_ITEM_NAME)
    table.add_column("Source", style=STYLE_PATH)

    for source in group_labels:
        source_items = [(idx, s, name) for idx, (s, name) in enumerate(options, 1) if s == source]
        for idx, s, name in source_items:
            source_label = group_labels.get(s, s)
            if s == "imported":
                table.add_row(str(idx), f"{name} [{STYLE_IMPORTED}](imported)[/{STYLE_IMPORTED}]", source_label)
            else:
                table.add_row(str(idx), name, source_label)

    table.add_row("[dim]0[/dim]", f"[dim]{exit_label}[/dim]", "")

    return table


def create_comparison_table(comparison: dict) -> Table:
    """Create a Rich Table for reproducibility comparison results.

    Args:
        comparison: Result dict from compare_runs().

    Returns:
        Rich Table displaying comparison results.
    """
    handoff_pass = comparison["handoff_pass"]
    repro_pass = comparison["repro_pass"]
    handoff_status = "PASSED" if handoff_pass else "FAILED"
    handoff_style = STYLE_OK if handoff_pass else STYLE_FAIL
    repro_status = "PASSED" if repro_pass else "FAILED"
    repro_style = STYLE_OK if repro_pass else STYLE_FAIL

    table = Table(
        title=(
            "Reproducibility Comparison - "
            f"SRQ5 Handoff [{handoff_style}]{handoff_status}[/{handoff_style}] / "
            f"SRQ3 Strict [{repro_style}]{repro_status}[/{repro_style}]"
        ),
        show_header=True,
        header_style=STYLE_HEADER,
    )
    table.add_column("Metric", style=STYLE_ITEM_NAME)
    table.add_column("Run", justify="right")
    table.add_column("Reference", justify="right")
    table.add_column("Deviation / Source", justify="right")
    table.add_column("Match", justify="center")

    handoff_match_text = f"[{handoff_style}]{handoff_status}[/{handoff_style}]"
    repro_match_text = f"[{repro_style}]{repro_status}[/{repro_style}]"
    table.add_row("SRQ5 Handoff", "-", "-", "reward mean only", handoff_match_text)
    table.add_row("SRQ3 Strict", "-", "-", "reward + AUC + config checks", repro_match_text)

    # Tail reward mean row
    final_match = comparison["tail_reward_mean_match"]
    final_match_text = f"[{STYLE_OK}]Yes[/{STYLE_OK}]" if final_match else f"[{STYLE_FAIL}]No[/{STYLE_FAIL}]"
    table.add_row(
        f"Reward Mean (last {comparison['reward_window']})",
        f"{comparison['tail_reward_mean_run']:.4f}",
        f"{comparison['tail_reward_mean_ref']:.4f}",
        (
            f"{comparison['tail_reward_mean_deviation']:.2%} "
            f"(n={comparison['reward_window_run']}/{comparison['reward_window_ref']}, "
            f"tol={comparison['tolerance']:.0%})"
        ),
        final_match_text,
    )

    # AUC remains visible because it gates strict SRQ3 reproducibility.
    auc_match = comparison["auc_match"]
    auc_match_text = f"[{STYLE_OK}]Yes[/{STYLE_OK}]" if auc_match else f"[{STYLE_FAIL}]No[/{STYLE_FAIL}]"
    table.add_row(
        "AUC (SRQ3)",
        f"{comparison['auc_run']:.4f}",
        f"{comparison['auc_ref']:.4f}",
        f"{comparison['auc_deviation']:.2%}",
        auc_match_text,
    )

    # Config row
    config_match = comparison["config_hash_match"]
    config_match_text = f"[{STYLE_OK}]Yes[/{STYLE_OK}]" if config_match else f"[{STYLE_FAIL}]No[/{STYLE_FAIL}]"
    run_hash = comparison["config_hash_run"]
    ref_hash = comparison["config_hash_ref"]
    table.add_row(
        "Config Hash",
        run_hash[:12],
        ref_hash[:12],
        comparison["config_hash_source"]["run"],
        config_match_text,
    )

    integrity_match = comparison["config_integrity_match"]
    integrity_match_text = f"[{STYLE_OK}]Yes[/{STYLE_OK}]" if integrity_match else f"[{STYLE_FAIL}]No[/{STYLE_FAIL}]"
    table.add_row(
        "Config Integrity",
        "pass" if comparison["config_integrity_run"]["match"] else "fail",
        "pass" if comparison["config_integrity_ref"]["match"] else "fail",
        comparison["config_integrity_run"]["source"],
        integrity_match_text,
    )

    return table


def create_fingerprint_table(comparison: dict) -> Table:
    """Create a Rich Table for environment fingerprint comparison.

    Args:
        comparison: Result from compare_fingerprints().

    Returns:
        Rich Table displaying fingerprint comparison.
    """
    all_match = comparison["all_match"]
    critical_match = comparison.get("critical_match", all_match)
    if all_match:
        status = "All Match"
        status_style = STYLE_OK
    elif critical_match:
        status = "Non-critical Differences"
        status_style = "yellow"
    else:
        status = "Critical Differences"
        status_style = STYLE_FAIL

    table = Table(
        title=f"Environment Comparison - [{status_style}]{status}[/{status_style}]",
        show_header=True,
        header_style=STYLE_HEADER,
    )
    table.add_column("Component", style=STYLE_ITEM_NAME)
    table.add_column("Bundle", justify="left")
    table.add_column("Current", justify="left")
    table.add_column("Status", justify="center")

    def status_text(match: bool) -> str:
        return f"[{STYLE_OK}]OK[/{STYLE_OK}]" if match else f"[{STYLE_FAIL}]MISMATCH[/{STYLE_FAIL}]"

    # Python version
    py_bundle, py_current, py_match = comparison["python"]
    table.add_row("Python", py_bundle, py_current, status_text(py_match))

    # OS
    os_bundle, os_current, os_match = comparison["os"]
    table.add_row("OS", os_bundle, os_current, status_text(os_match))

    # Packages
    for pkg, (bundle_ver, current_ver, match) in comparison["packages"].items():
        table.add_row(f"  {pkg}", bundle_ver, current_ver, status_text(match))

    for name, (bundle_val, current_val, match) in comparison.get("runtime", {}).items():
        table.add_row(f"  {name}", bundle_val, current_val, status_text(match))

    for name, (bundle_val, current_val, match) in comparison.get("build", {}).items():
        table.add_row(f"  {name}", bundle_val, current_val, status_text(match))

    return table
