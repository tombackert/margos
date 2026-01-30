"""Report generation for experiment analysis."""

import json
from datetime import datetime
from pathlib import Path
from typing import Callable

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from marl_platform.utils.errors import PlatformError

# Use non-interactive backend for thesis-ready output
matplotlib.use("Agg")


class ReportError(PlatformError):
    """Raised when report generation fails."""

    def __init__(self, message: str, context: dict | None = None, fix: str | None = None):
        super().__init__(
            message=message,
            context=context,
            fix=fix or "Check the experiment directory contains valid logs",
        )


def read_metrics(log_path: Path) -> list[dict]:
    """Read metrics from JSONL log file.

    Args:
        log_path: Path to metrics.jsonl file.

    Returns:
        List of metric dicts, one per iteration.

    Raises:
        ReportError: If log file is missing or empty.
    """
    if not log_path.exists():
        raise ReportError(
            message="Metrics log not found",
            context={"Path": str(log_path)},
            fix="Ensure the experiment completed training successfully",
        )

    metrics = []
    with open(log_path) as f:
        for line in f:
            line = line.strip()
            if line:
                metrics.append(json.loads(line))

    if not metrics:
        raise ReportError(
            message="Metrics log is empty",
            context={"Path": str(log_path)},
            fix="Ensure training ran for at least one iteration",
        )

    return metrics


def plot_learning_curve(log_path: str | Path, output_path: str | Path) -> Path:
    """Generate learning curve plot from metrics log.

    Args:
        log_path: Path to metrics.jsonl file.
        output_path: Path for output PNG file.

    Returns:
        Path to the generated plot file.
    """
    log_path = Path(log_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    metrics = read_metrics(log_path)

    iterations = [m["iteration"] for m in metrics]
    rewards = [m["episode_reward_mean"] for m in metrics]

    # Create thesis-ready plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(iterations, rewards, linewidth=2, marker="o", markersize=4)
    ax.set_xlabel("Iteration", fontsize=12)
    ax.set_ylabel("Episode Reward Mean", fontsize=12)
    ax.set_title("Learning Curve", fontsize=14)
    ax.grid(True, alpha=0.3)

    # Tight layout for clean output
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    return output_path


def calculate_auc(metrics: list[dict]) -> float:
    """Calculate area under learning curve using trapezoidal integration.

    Args:
        metrics: List of metric dicts with iteration and episode_reward_mean.

    Returns:
        Area under the curve.
    """
    iterations = np.array([m["iteration"] for m in metrics])
    rewards = np.array([m["episode_reward_mean"] for m in metrics])
    return float(np.trapezoid(rewards, iterations))


def calculate_duration(metrics: list[dict]) -> str:
    """Calculate training duration from first to last timestamp.

    Args:
        metrics: List of metric dicts with timestamp field.

    Returns:
        Human-readable duration string.
    """
    if len(metrics) < 2:
        return "N/A"

    first_ts = datetime.fromisoformat(metrics[0]["timestamp"])
    last_ts = datetime.fromisoformat(metrics[-1]["timestamp"])
    duration = last_ts - first_ts

    total_seconds = int(duration.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


def generate_summary(experiment_dir: Path, metrics: list[dict]) -> str:
    """Generate summary text for experiment.

    Args:
        experiment_dir: Path to experiment results directory.
        metrics: List of metric dicts.

    Returns:
        Summary text content.
    """
    # Read config hash
    config_hash_path = experiment_dir / "config_hash.txt"
    config_hash = "N/A"
    if config_hash_path.exists():
        config_hash = config_hash_path.read_text().strip()

    # Calculate statistics
    rewards = [m["episode_reward_mean"] for m in metrics]
    final_reward = rewards[-1]
    best_reward = max(rewards)
    auc = calculate_auc(metrics)
    duration = calculate_duration(metrics)

    # Format summary
    lines = [
        "Experiment Summary",
        "=" * 40,
        "",
        f"Name: {experiment_dir.name}",
        f"Config Hash: {config_hash}",
        "",
        "Training Statistics",
        "-" * 40,
        f"Total Iterations: {len(metrics)}",
        f"Final Reward: {final_reward:.4f}",
        f"Best Reward: {best_reward:.4f}",
        f"AUC (Area Under Curve): {auc:.4f}",
        f"Training Duration: {duration}",
        "",
    ]

    return "\n".join(lines)


def generate_report(
    experiment_dir: str,
    reference_dir: str | None = None,
    progress_callback: Callable[[int, int, str], None] | None = None,
) -> str:
    """Generate analysis report for experiment.

    Args:
        experiment_dir: Path to experiment results directory.
        reference_dir: Optional path to reference experiment for comparison.
        progress_callback: Optional callback(current, total, description) for progress.

    Returns:
        Path to generated report directory.
    """
    from marl_platform.analysis.compare import compare_runs

    def update_progress(current: int, total: int, desc: str = "") -> None:
        if progress_callback:
            progress_callback(current, total, desc)

    total_steps = 4 if reference_dir else 3

    exp_path = Path(experiment_dir)
    report_dir = exp_path / "report"
    report_dir.mkdir(parents=True, exist_ok=True)

    update_progress(1, total_steps, "Reading metrics")

    log_path = exp_path / "logs" / "metrics.jsonl"
    metrics = read_metrics(log_path)

    update_progress(2, total_steps, "Generating learning curve")

    # Generate learning curve plot
    plot_path = report_dir / "learning_curve.png"
    plot_learning_curve(log_path, plot_path)

    # Generate summary
    summary_text = generate_summary(exp_path, metrics)

    # Add comparison if reference provided
    if reference_dir:
        update_progress(3, total_steps, "Comparing with reference")
        comparison = compare_runs(experiment_dir, reference_dir)
        summary_text += format_comparison(comparison)

    update_progress(total_steps, total_steps, "Writing report")

    # Write summary
    summary_path = report_dir / "summary.txt"
    summary_path.write_text(summary_text)

    return str(report_dir)


def format_comparison(comparison: dict) -> str:
    """Format comparison result for summary.

    Args:
        comparison: Result dict from compare_runs().

    Returns:
        Formatted comparison text.
    """
    status = "PASSED" if comparison["passed"] else "FAILED"
    lines = [
        "Reproducibility Comparison",
        "-" * 40,
        f"Status: {status}",
        "",
        "Final Reward:",
        f"  Run:       {comparison['final_reward_run']:.4f}",
        f"  Reference: {comparison['final_reward_ref']:.4f}",
        f"  Deviation: {comparison['final_reward_deviation']:.2%}",
        f"  Match:     {'Yes' if comparison['final_reward_match'] else 'No'}",
        "",
        "AUC (Area Under Curve):",
        f"  Run:       {comparison['auc_run']:.4f}",
        f"  Reference: {comparison['auc_ref']:.4f}",
        f"  Deviation: {comparison['auc_deviation']:.2%}",
        f"  Match:     {'Yes' if comparison['auc_match'] else 'No'}",
        "",
    ]
    return "\n".join(lines)
