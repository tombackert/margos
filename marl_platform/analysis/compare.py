"""Reproducibility comparison for experiments."""

from pathlib import Path

from marl_platform.config import read_config_hash
from marl_platform.analysis.report import calculate_auc, read_metrics
from marl_platform.utils.errors import PlatformError
from marl_platform.utils.errors import ValidationError
import yaml


class ComparisonError(PlatformError):
    """Raised when comparison fails."""

    def __init__(self, message: str, context: dict | None = None, fix: str | None = None):
        super().__init__(
            message=message,
            context=context,
            fix=fix or "Ensure both experiments have valid metrics logs",
        )


def compare_runs(
    run_dir: str, reference_dir: str, tolerance: float = 0.01, reward_window: int = 50
) -> dict:
    """Compare run against reference for reproducibility.

    Args:
        run_dir: Path to the run to evaluate.
        reference_dir: Path to the reference run.
        tolerance: Maximum allowed relative deviation (default 1%).
        reward_window: Requested tail window for reward-mean comparison.

    Returns:
        Comparison result dict with:
        - tail_reward_mean_match: bool
        - tail_reward_mean_deviation: float
        - auc_match: bool
        - auc_deviation: float (as percentage)
        - config_hash_match: bool
        - config_integrity_match: bool
        - handoff_pass: bool (SRQ5 reward-only handoff success)
        - repro_pass: bool (SRQ3 strict reproducibility success)
        - passed: bool (backward-compatible alias for handoff_pass)
    """
    run_path = Path(run_dir)
    ref_path = Path(reference_dir)

    # Read metrics from both runs
    run_log = run_path / "logs" / "metrics.jsonl"
    ref_log = ref_path / "logs" / "metrics.jsonl"

    run_metrics = read_metrics(run_log)
    ref_metrics = read_metrics(ref_log)

    run_rewards = [m["episode_reward_mean"] for m in run_metrics if m.get("episode_reward_mean") is not None]
    ref_rewards = [m["episode_reward_mean"] for m in ref_metrics if m.get("episode_reward_mean") is not None]

    run_tail_rewards = run_rewards[-reward_window:]
    ref_tail_rewards = ref_rewards[-reward_window:]
    run_tail_mean = sum(run_tail_rewards) / len(run_tail_rewards)
    ref_tail_mean = sum(ref_tail_rewards) / len(ref_tail_rewards)

    # Calculate AUCs
    run_auc = calculate_auc(run_metrics)
    ref_auc = calculate_auc(ref_metrics)

    # Resolve config identity from persisted artifacts
    try:
        run_hash, run_hash_source = read_config_hash(run_path)
        ref_hash, ref_hash_source = read_config_hash(ref_path)
    except ValidationError as e:
        raise ComparisonError(
            message="Failed to resolve config identity for comparison",
            context=e.context,
            fix=e.fix,
        ) from e

    config_hash_match = run_hash == ref_hash
    run_integrity = _read_config_integrity(run_path)
    ref_integrity = _read_config_integrity(ref_path)
    config_integrity_match = run_integrity["match"] and ref_integrity["match"]

    # Calculate deviations (handle zero reference gracefully)
    if ref_tail_mean != 0:
        tail_mean_deviation = abs(run_tail_mean - ref_tail_mean) / abs(ref_tail_mean)
    else:
        tail_mean_deviation = 0.0 if run_tail_mean == 0 else float("inf")

    if ref_auc != 0:
        auc_deviation = abs(run_auc - ref_auc) / abs(ref_auc)
    else:
        auc_deviation = 0.0 if run_auc == 0 else float("inf")

    # Check if within tolerance
    tail_mean_match = tail_mean_deviation <= tolerance
    auc_match = auc_deviation <= tolerance
    handoff_pass = tail_mean_match
    repro_pass = tail_mean_match and auc_match and config_hash_match and config_integrity_match

    return {
        "comparison_method": "tail_mean",
        "reward_window": reward_window,
        "reward_window_run": len(run_tail_rewards),
        "reward_window_ref": len(ref_tail_rewards),
        "tolerance": tolerance,
        "tail_reward_mean_match": tail_mean_match,
        "tail_reward_mean_deviation": tail_mean_deviation,
        "tail_reward_mean_run": run_tail_mean,
        "tail_reward_mean_ref": ref_tail_mean,
        # Backward-compatible aliases for existing reporting/tests/callers.
        "final_reward_match": tail_mean_match,
        "final_reward_deviation": tail_mean_deviation,
        "final_reward_run": run_tail_mean,
        "final_reward_ref": ref_tail_mean,
        "auc_match": auc_match,
        "auc_deviation": auc_deviation,
        "auc_run": run_auc,
        "auc_ref": ref_auc,
        "config_hash_match": config_hash_match,
        "config_hash_run": run_hash,
        "config_hash_ref": ref_hash,
        "config_hash_source": {
            "run": run_hash_source,
            "reference": ref_hash_source,
        },
        "config_integrity_match": config_integrity_match,
        "config_integrity_run": run_integrity,
        "config_integrity_ref": ref_integrity,
        "handoff_pass": handoff_pass,
        "repro_pass": repro_pass,
        # Backward-compatible alias used by SRQ5-oriented displays/callers.
        "passed": handoff_pass,
    }


def _read_config_integrity(output_dir: Path) -> dict:
    """Read config integrity artifact, defaulting to permissive legacy behavior."""
    integrity_path = output_dir / "config_integrity.yaml"
    if not integrity_path.exists():
        return {
            "exists": False,
            "match": True,
            "source": "missing (legacy-permissive)",
            "start_hash": None,
            "end_hash": None,
        }

    try:
        with open(integrity_path) as f:
            data = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        raise ComparisonError(
            message="Failed to read config integrity artifact",
            context={"Path": str(integrity_path), "Error": str(e)},
            fix="Ensure config_integrity.yaml is valid YAML",
        ) from e

    return {
        "exists": True,
        "match": bool(data.get("match", False)),
        "source": data.get("source", "config_integrity.yaml"),
        "start_hash": data.get("start_hash"),
        "end_hash": data.get("end_hash"),
    }
