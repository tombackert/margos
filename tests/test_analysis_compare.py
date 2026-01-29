"""Unit tests for analysis compare module."""

import json
from pathlib import Path

import pytest

from marl_platform.analysis.compare import ComparisonError, compare_runs


def create_experiment_with_metrics(path: Path, metrics: list[dict]) -> Path:
    """Helper to create an experiment directory with metrics."""
    path.mkdir(parents=True, exist_ok=True)
    log_dir = path / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "metrics.jsonl"
    with open(log_path, "w") as f:
        for m in metrics:
            f.write(json.dumps(m) + "\n")
    return path


class TestCompareRuns:
    """Tests for compare_runs function."""

    def test_identical_runs_pass(self, tmp_path: Path) -> None:
        """Identical runs pass comparison."""
        metrics = [
            {"iteration": 1, "episode_reward_mean": -100.0},
            {"iteration": 2, "episode_reward_mean": -90.0},
            {"iteration": 3, "episode_reward_mean": -80.0},
        ]
        run_dir = create_experiment_with_metrics(tmp_path / "run", metrics)
        ref_dir = create_experiment_with_metrics(tmp_path / "ref", metrics)

        result = compare_runs(str(run_dir), str(ref_dir))

        assert result["passed"] is True
        assert result["final_reward_match"] is True
        assert result["auc_match"] is True
        assert result["final_reward_deviation"] == 0.0
        assert result["auc_deviation"] == 0.0

    def test_within_tolerance_passes(self, tmp_path: Path) -> None:
        """Runs within 1% tolerance pass."""
        run_metrics = [
            {"iteration": 1, "episode_reward_mean": -100.0},
            {"iteration": 2, "episode_reward_mean": -90.0},
            {"iteration": 3, "episode_reward_mean": -80.5},  # 0.625% deviation
        ]
        ref_metrics = [
            {"iteration": 1, "episode_reward_mean": -100.0},
            {"iteration": 2, "episode_reward_mean": -90.0},
            {"iteration": 3, "episode_reward_mean": -80.0},
        ]
        run_dir = create_experiment_with_metrics(tmp_path / "run", run_metrics)
        ref_dir = create_experiment_with_metrics(tmp_path / "ref", ref_metrics)

        result = compare_runs(str(run_dir), str(ref_dir))

        assert result["passed"] is True
        assert result["final_reward_match"] is True

    def test_outside_tolerance_fails(self, tmp_path: Path) -> None:
        """Runs outside 1% tolerance fail."""
        run_metrics = [
            {"iteration": 1, "episode_reward_mean": -100.0},
            {"iteration": 2, "episode_reward_mean": -90.0},
            {"iteration": 3, "episode_reward_mean": -70.0},  # 12.5% deviation
        ]
        ref_metrics = [
            {"iteration": 1, "episode_reward_mean": -100.0},
            {"iteration": 2, "episode_reward_mean": -90.0},
            {"iteration": 3, "episode_reward_mean": -80.0},
        ]
        run_dir = create_experiment_with_metrics(tmp_path / "run", run_metrics)
        ref_dir = create_experiment_with_metrics(tmp_path / "ref", ref_metrics)

        result = compare_runs(str(run_dir), str(ref_dir))

        assert result["passed"] is False
        assert result["final_reward_match"] is False

    def test_custom_tolerance(self, tmp_path: Path) -> None:
        """Supports custom tolerance value."""
        run_metrics = [
            {"iteration": 1, "episode_reward_mean": -100.0},
            {"iteration": 2, "episode_reward_mean": -85.0},  # 5.5% deviation
        ]
        ref_metrics = [
            {"iteration": 1, "episode_reward_mean": -100.0},
            {"iteration": 2, "episode_reward_mean": -90.0},
        ]
        run_dir = create_experiment_with_metrics(tmp_path / "run", run_metrics)
        ref_dir = create_experiment_with_metrics(tmp_path / "ref", ref_metrics)

        # With 1% tolerance (default) - should fail
        result_strict = compare_runs(str(run_dir), str(ref_dir), tolerance=0.01)
        assert result_strict["passed"] is False

        # With 10% tolerance - should pass
        result_loose = compare_runs(str(run_dir), str(ref_dir), tolerance=0.10)
        assert result_loose["passed"] is True

    def test_final_reward_deviation_calculated(self, tmp_path: Path) -> None:
        """Calculates final reward deviation correctly."""
        run_metrics = [{"iteration": 1, "episode_reward_mean": -80.0}]
        ref_metrics = [{"iteration": 1, "episode_reward_mean": -100.0}]
        run_dir = create_experiment_with_metrics(tmp_path / "run", run_metrics)
        ref_dir = create_experiment_with_metrics(tmp_path / "ref", ref_metrics)

        result = compare_runs(str(run_dir), str(ref_dir))

        # |-80 - -100| / |-100| = 20 / 100 = 0.2 (20%)
        assert result["final_reward_deviation"] == pytest.approx(0.2)

    def test_auc_deviation_calculated(self, tmp_path: Path) -> None:
        """Calculates AUC deviation correctly."""
        run_metrics = [
            {"iteration": 1, "episode_reward_mean": 10.0},
            {"iteration": 2, "episode_reward_mean": 10.0},
        ]  # AUC = 10
        ref_metrics = [
            {"iteration": 1, "episode_reward_mean": 20.0},
            {"iteration": 2, "episode_reward_mean": 20.0},
        ]  # AUC = 20
        run_dir = create_experiment_with_metrics(tmp_path / "run", run_metrics)
        ref_dir = create_experiment_with_metrics(tmp_path / "ref", ref_metrics)

        result = compare_runs(str(run_dir), str(ref_dir))

        # |10 - 20| / |20| = 10 / 20 = 0.5 (50%)
        assert result["auc_deviation"] == pytest.approx(0.5)

    def test_both_conditions_required_to_pass(self, tmp_path: Path) -> None:
        """Both final reward and AUC must match to pass."""
        # Same final reward but different trajectory (different AUC)
        run_metrics = [
            {"iteration": 1, "episode_reward_mean": -100.0},
            {"iteration": 2, "episode_reward_mean": -50.0},
            {"iteration": 3, "episode_reward_mean": -80.0},
        ]
        ref_metrics = [
            {"iteration": 1, "episode_reward_mean": -100.0},
            {"iteration": 2, "episode_reward_mean": -90.0},
            {"iteration": 3, "episode_reward_mean": -80.0},
        ]
        run_dir = create_experiment_with_metrics(tmp_path / "run", run_metrics)
        ref_dir = create_experiment_with_metrics(tmp_path / "ref", ref_metrics)

        result = compare_runs(str(run_dir), str(ref_dir))

        assert result["final_reward_match"] is True  # Same final reward
        assert result["auc_match"] is False  # Different AUC
        assert result["passed"] is False  # Overall fail

    def test_handles_negative_rewards(self, tmp_path: Path) -> None:
        """Handles negative reward values correctly."""
        run_metrics = [
            {"iteration": 1, "episode_reward_mean": -150.0},
            {"iteration": 2, "episode_reward_mean": -100.0},
        ]
        ref_metrics = [
            {"iteration": 1, "episode_reward_mean": -150.0},
            {"iteration": 2, "episode_reward_mean": -100.0},
        ]
        run_dir = create_experiment_with_metrics(tmp_path / "run", run_metrics)
        ref_dir = create_experiment_with_metrics(tmp_path / "ref", ref_metrics)

        result = compare_runs(str(run_dir), str(ref_dir))

        assert result["passed"] is True

    def test_handles_zero_reference_final_reward(self, tmp_path: Path) -> None:
        """Handles zero reference final reward gracefully."""
        run_metrics = [{"iteration": 1, "episode_reward_mean": 0.0}]
        ref_metrics = [{"iteration": 1, "episode_reward_mean": 0.0}]
        run_dir = create_experiment_with_metrics(tmp_path / "run", run_metrics)
        ref_dir = create_experiment_with_metrics(tmp_path / "ref", ref_metrics)

        result = compare_runs(str(run_dir), str(ref_dir))

        assert result["passed"] is True
        assert result["final_reward_deviation"] == 0.0

    def test_returns_expected_structure(self, tmp_path: Path) -> None:
        """Returns dict with expected keys."""
        metrics = [{"iteration": 1, "episode_reward_mean": -100.0}]
        run_dir = create_experiment_with_metrics(tmp_path / "run", metrics)
        ref_dir = create_experiment_with_metrics(tmp_path / "ref", metrics)

        result = compare_runs(str(run_dir), str(ref_dir))

        assert "final_reward_match" in result
        assert "final_reward_deviation" in result
        assert "auc_match" in result
        assert "auc_deviation" in result
        assert "passed" in result
        assert isinstance(result["final_reward_match"], bool)
        assert isinstance(result["final_reward_deviation"], float)
        assert isinstance(result["passed"], bool)

    def test_different_iteration_counts(self, tmp_path: Path) -> None:
        """Handles experiments with different iteration counts."""
        run_metrics = [
            {"iteration": 1, "episode_reward_mean": -100.0},
            {"iteration": 2, "episode_reward_mean": -90.0},
        ]
        ref_metrics = [
            {"iteration": 1, "episode_reward_mean": -100.0},
            {"iteration": 2, "episode_reward_mean": -95.0},
            {"iteration": 3, "episode_reward_mean": -90.0},
        ]
        run_dir = create_experiment_with_metrics(tmp_path / "run", run_metrics)
        ref_dir = create_experiment_with_metrics(tmp_path / "ref", ref_metrics)

        # Should still work - compares final rewards
        result = compare_runs(str(run_dir), str(ref_dir))

        assert "final_reward_match" in result
        assert "auc_match" in result
