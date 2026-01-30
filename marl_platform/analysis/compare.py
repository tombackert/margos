"""Reproducibility comparison for experiments."""

from pathlib import Path

import numpy as np

from marl_platform.analysis.report import calculate_auc, read_metrics
from marl_platform.utils.errors import PlatformError


class ComparisonError(PlatformError):
    """Raised when comparison fails."""

    def __init__(self, message: str, context: dict | None = None, fix: str | None = None):
        super().__init__(
            message=message,
            context=context,
            fix=fix or "Ensure both experiments have valid metrics logs",
        )


def compare_runs(
    run_dir: str, reference_dir: str, tolerance: float = 0.01
) -> dict:
    """Compare run against reference for reproducibility.

    Args:
        run_dir: Path to the run to evaluate.
        reference_dir: Path to the reference run.
        tolerance: Maximum allowed relative deviation (default 1%).

    Returns:
        Comparison result dict with:
        - final_reward_match: bool
        - final_reward_deviation: float (as percentage)
        - auc_match: bool
        - auc_deviation: float (as percentage)
        - passed: bool (both within tolerance)
    """
    run_path = Path(run_dir)
    ref_path = Path(reference_dir)

    # Read metrics from both runs
    run_log = run_path / "logs" / "metrics.jsonl"
    ref_log = ref_path / "logs" / "metrics.jsonl"

    run_metrics = read_metrics(run_log)
    ref_metrics = read_metrics(ref_log)

    # Calculate final rewards
    run_final = run_metrics[-1]["episode_reward_mean"]
    ref_final = ref_metrics[-1]["episode_reward_mean"]

    # Calculate AUCs
    run_auc = calculate_auc(run_metrics)
    ref_auc = calculate_auc(ref_metrics)

    # Calculate deviations (handle zero reference gracefully)
    if ref_final != 0:
        final_deviation = abs(run_final - ref_final) / abs(ref_final)
    else:
        final_deviation = 0.0 if run_final == 0 else float("inf")

    if ref_auc != 0:
        auc_deviation = abs(run_auc - ref_auc) / abs(ref_auc)
    else:
        auc_deviation = 0.0 if run_auc == 0 else float("inf")

    # Check if within tolerance
    final_match = final_deviation <= tolerance
    auc_match = auc_deviation <= tolerance

    return {
        "final_reward_match": final_match,
        "final_reward_deviation": final_deviation,
        "final_reward_run": run_final,
        "final_reward_ref": ref_final,
        "auc_match": auc_match,
        "auc_deviation": auc_deviation,
        "auc_run": run_auc,
        "auc_ref": ref_auc,
        "passed": final_match and auc_match,
    }
