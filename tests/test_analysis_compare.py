"""Unit tests for analysis compare module."""

import json
from pathlib import Path

import pytest
import yaml

from margos.analysis.compare import ComparisonError, compare_runs


def create_experiment_with_metrics(
    path: Path,
    metrics: list[dict],
    *,
    config: dict | None = None,
    config_hash: str | None = None,
    config_integrity_match: bool = True,
    write_hash: bool = True,
    write_config: bool = True,
) -> Path:
    """Helper to create an experiment directory with metrics."""
    path.mkdir(parents=True, exist_ok=True)
    log_dir = path / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "metrics.jsonl"
    with open(log_path, "w") as f:
        for m in metrics:
            f.write(json.dumps(m) + "\n")

    if config is None:
        config = {
            "experiment": {"name": "test_experiment", "seed": 42},
            "scenario": {"file": "/tmp/scenario.argos"},
            "training": {"script": "/tmp/train.py"},
            "output": {"dir": "results"},
        }

    if write_config:
        (path / "config.yaml").write_text(yaml.dump(config))

    if write_hash:
        if config_hash is None:
            from margos.config import MargosConfig, hash_config

            config_hash = hash_config(MargosConfig(**config))
        (path / "config_hash.txt").write_text(config_hash)

    (path / "config_integrity.yaml").write_text(
        yaml.dump(
            {
                "start_hash": config_hash or "computed",
                "end_hash": config_hash or "computed",
                "match": config_integrity_match,
                "source": "config.yaml",
            }
        )
    )

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

        assert result["handoff_pass"] is True
        assert result["repro_pass"] is True
        assert result["passed"] is True
        assert result["tail_reward_mean_match"] is True
        assert result["config_hash_match"] is True
        assert result["config_integrity_match"] is True
        assert result["tail_reward_mean_deviation"] == 0.0

    def test_within_default_tolerance_passes(self, tmp_path: Path) -> None:
        """Runs within 1% tolerance pass."""
        run_metrics = [
            {"iteration": 1, "episode_reward_mean": -100.0},
            {"iteration": 2, "episode_reward_mean": -90.0},
            {"iteration": 3, "episode_reward_mean": -81.0},
        ]
        ref_metrics = [
            {"iteration": 1, "episode_reward_mean": -100.0},
            {"iteration": 2, "episode_reward_mean": -90.0},
            {"iteration": 3, "episode_reward_mean": -80.0},
        ]
        run_dir = create_experiment_with_metrics(tmp_path / "run", run_metrics)
        ref_dir = create_experiment_with_metrics(tmp_path / "ref", ref_metrics)

        result = compare_runs(str(run_dir), str(ref_dir))

        assert result["handoff_pass"] is True
        assert result["repro_pass"] is True
        assert result["passed"] is True
        assert result["tail_reward_mean_match"] is True
        assert result["config_hash_match"] is True

    def test_outside_tolerance_fails(self, tmp_path: Path) -> None:
        """Runs outside 1% tolerance fail."""
        run_metrics = [
            {"iteration": 1, "episode_reward_mean": -100.0},
            {"iteration": 2, "episode_reward_mean": -90.0},
            {"iteration": 3, "episode_reward_mean": -60.0},
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
        assert result["tail_reward_mean_match"] is False

    def test_custom_tolerance(self, tmp_path: Path) -> None:
        """Supports custom tolerance value."""
        run_metrics = [
            {"iteration": 1, "episode_reward_mean": -100.0},
            {"iteration": 2, "episode_reward_mean": -80.0},
        ]
        ref_metrics = [
            {"iteration": 1, "episode_reward_mean": -100.0},
            {"iteration": 2, "episode_reward_mean": -90.0},
        ]
        run_dir = create_experiment_with_metrics(tmp_path / "run", run_metrics)
        ref_dir = create_experiment_with_metrics(tmp_path / "ref", ref_metrics)

        # With 1% tolerance - should fail
        result_strict = compare_runs(str(run_dir), str(ref_dir), tolerance=0.01)
        assert result_strict["handoff_pass"] is False
        assert result_strict["repro_pass"] is False
        assert result_strict["passed"] is False

        # With 10% tolerance - should pass
        result_loose = compare_runs(str(run_dir), str(ref_dir), tolerance=0.10)
        assert result_loose["handoff_pass"] is True
        assert result_loose["repro_pass"] is True
        assert result_loose["passed"] is True

    def test_tail_reward_mean_deviation_calculated(self, tmp_path: Path) -> None:
        """Calculates tail reward mean deviation correctly."""
        run_metrics = [{"iteration": 1, "episode_reward_mean": -80.0}]
        ref_metrics = [{"iteration": 1, "episode_reward_mean": -100.0}]
        run_dir = create_experiment_with_metrics(tmp_path / "run", run_metrics)
        ref_dir = create_experiment_with_metrics(tmp_path / "ref", ref_metrics)

        result = compare_runs(str(run_dir), str(ref_dir))

        # |-80 - -100| / |-100| = 20 / 100 = 0.2 (20%)
        assert result["tail_reward_mean_deviation"] == pytest.approx(0.2)

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

    def test_auc_difference_keeps_handoff_pass_but_fails_strict_repro(self, tmp_path: Path) -> None:
        """AUC outside tolerance remains an SRQ5 pass but fails SRQ3 strict reproducibility."""
        run_metrics = [
            {"iteration": 1, "episode_reward_mean": -100.0},
            {"iteration": 2, "episode_reward_mean": -50.0},
            {"iteration": 3, "episode_reward_mean": -120.0},
        ]
        ref_metrics = [
            {"iteration": 1, "episode_reward_mean": -100.0},
            {"iteration": 2, "episode_reward_mean": -90.0},
            {"iteration": 3, "episode_reward_mean": -80.0},
        ]
        run_dir = create_experiment_with_metrics(tmp_path / "run", run_metrics)
        ref_dir = create_experiment_with_metrics(tmp_path / "ref", ref_metrics)

        result = compare_runs(str(run_dir), str(ref_dir))

        assert result["tail_reward_mean_match"] is True
        assert result["auc_match"] is False
        assert result["handoff_pass"] is True
        assert result["repro_pass"] is False
        assert result["passed"] is True

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

        assert result["handoff_pass"] is True
        assert result["repro_pass"] is True
        assert result["passed"] is True

    def test_handles_zero_reference_final_reward(self, tmp_path: Path) -> None:
        """Handles zero reference final reward gracefully."""
        run_metrics = [{"iteration": 1, "episode_reward_mean": 0.0}]
        ref_metrics = [{"iteration": 1, "episode_reward_mean": 0.0}]
        run_dir = create_experiment_with_metrics(tmp_path / "run", run_metrics)
        ref_dir = create_experiment_with_metrics(tmp_path / "ref", ref_metrics)

        result = compare_runs(str(run_dir), str(ref_dir))

        assert result["handoff_pass"] is True
        assert result["repro_pass"] is True
        assert result["passed"] is True
        assert result["tail_reward_mean_deviation"] == 0.0

    def test_returns_expected_structure(self, tmp_path: Path) -> None:
        """Returns dict with expected keys."""
        metrics = [{"iteration": 1, "episode_reward_mean": -100.0}]
        run_dir = create_experiment_with_metrics(tmp_path / "run", metrics)
        ref_dir = create_experiment_with_metrics(tmp_path / "ref", metrics)

        result = compare_runs(str(run_dir), str(ref_dir))

        assert "comparison_method" in result
        assert "tail_reward_mean_match" in result
        assert "tail_reward_mean_deviation" in result
        assert "tail_reward_mean_run" in result
        assert "tail_reward_mean_ref" in result
        assert "reward_window" in result
        assert "reward_window_run" in result
        assert "reward_window_ref" in result
        assert "tolerance" in result
        assert "final_reward_match" in result
        assert "final_reward_deviation" in result
        assert "auc_match" in result
        assert "auc_deviation" in result
        assert "handoff_pass" in result
        assert "repro_pass" in result
        assert "passed" in result
        assert "config_hash_match" in result
        assert "config_integrity_match" in result
        assert "config_hash_run" in result
        assert "config_hash_ref" in result
        assert "config_hash_source" in result
        assert isinstance(result["tail_reward_mean_match"], bool)
        assert isinstance(result["tail_reward_mean_deviation"], float)
        assert isinstance(result["handoff_pass"], bool)
        assert isinstance(result["repro_pass"], bool)
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

        # Should still work - compares tail means using all available values
        result = compare_runs(str(run_dir), str(ref_dir))

        assert "tail_reward_mean_match" in result
        assert "auc_match" in result

    def test_uses_last_50_rewards_when_available(self, tmp_path: Path) -> None:
        """Tail mean uses exactly the last 50 reward values."""
        run_metrics = [{"iteration": i, "episode_reward_mean": float(i)} for i in range(1, 61)]
        ref_metrics = [{"iteration": i, "episode_reward_mean": float(i)} for i in range(1, 61)]
        run_dir = create_experiment_with_metrics(tmp_path / "run", run_metrics)
        ref_dir = create_experiment_with_metrics(tmp_path / "ref", ref_metrics)

        result = compare_runs(str(run_dir), str(ref_dir))

        assert result["reward_window"] == 50
        assert result["reward_window_run"] == 50
        assert result["reward_window_ref"] == 50
        assert result["tail_reward_mean_run"] == pytest.approx(sum(range(11, 61)) / 50)

    def test_uses_all_rewards_when_fewer_than_50_exist(self, tmp_path: Path) -> None:
        """Tail mean falls back to all rewards on short runs."""
        metrics = [{"iteration": i, "episode_reward_mean": float(i)} for i in range(1, 6)]
        run_dir = create_experiment_with_metrics(tmp_path / "run", metrics)
        ref_dir = create_experiment_with_metrics(tmp_path / "ref", metrics)

        result = compare_runs(str(run_dir), str(ref_dir))

        assert result["reward_window_run"] == 5
        assert result["reward_window_ref"] == 5
        assert result["tail_reward_mean_run"] == pytest.approx(3.0)

    def test_config_hash_mismatch_fails(self, tmp_path: Path) -> None:
        """Different config hashes fail strict reproducibility comparison."""
        metrics = [{"iteration": 1, "episode_reward_mean": -100.0}]
        run_dir = create_experiment_with_metrics(tmp_path / "run", metrics, config_hash="runhash")
        ref_dir = create_experiment_with_metrics(tmp_path / "ref", metrics, config_hash="refhash")

        result = compare_runs(str(run_dir), str(ref_dir))

        assert result["config_hash_match"] is False
        assert result["handoff_pass"] is True
        assert result["repro_pass"] is False
        assert result["passed"] is True

    def test_config_integrity_mismatch_fails(self, tmp_path: Path) -> None:
        """Failed runtime config integrity fails comparison."""
        metrics = [{"iteration": 1, "episode_reward_mean": -100.0}]
        run_dir = create_experiment_with_metrics(tmp_path / "run", metrics, config_integrity_match=False)
        ref_dir = create_experiment_with_metrics(tmp_path / "ref", metrics, config_integrity_match=True)

        result = compare_runs(str(run_dir), str(ref_dir))

        assert result["config_integrity_match"] is False
        assert result["handoff_pass"] is True
        assert result["repro_pass"] is False
        assert result["passed"] is True

    def test_missing_config_integrity_is_permissive_for_legacy_artifacts(self, tmp_path: Path) -> None:
        """Missing runtime config integrity artifact preserves legacy replayability."""
        metrics = [{"iteration": 1, "episode_reward_mean": -100.0}]
        run_dir = create_experiment_with_metrics(tmp_path / "run", metrics)
        ref_dir = create_experiment_with_metrics(tmp_path / "ref", metrics)
        (run_dir / "config_integrity.yaml").unlink()

        result = compare_runs(str(run_dir), str(ref_dir))

        assert result["config_integrity_run"]["exists"] is False
        assert result["config_integrity_run"]["match"] is True
        assert result["config_integrity_run"]["source"] == "missing (legacy-permissive)"
        assert result["config_integrity_match"] is True
        assert result["handoff_pass"] is True
        assert result["repro_pass"] is True
        assert result["passed"] is True

    def test_recomputes_hash_from_frozen_config_when_hash_missing(self, tmp_path: Path) -> None:
        """Falls back to config.yaml when config_hash.txt is missing."""
        metrics = [{"iteration": 1, "episode_reward_mean": -100.0}]
        config = {
            "experiment": {"name": "shared", "seed": 42},
            "scenario": {"file": "/tmp/scenario.argos"},
            "training": {"script": "/tmp/train.py"},
            "output": {"dir": "results"},
        }
        run_dir = create_experiment_with_metrics(
            tmp_path / "run",
            metrics,
            config=config,
            write_hash=False,
        )
        ref_dir = create_experiment_with_metrics(
            tmp_path / "ref",
            metrics,
            config=config,
            write_hash=False,
        )

        result = compare_runs(str(run_dir), str(ref_dir))

        assert result["config_hash_match"] is True
        assert result["config_hash_source"] == {
            "run": "config.yaml",
            "reference": "config.yaml",
        }

    def test_missing_config_artifacts_raise_error(self, tmp_path: Path) -> None:
        """Comparison fails when config identity cannot be resolved."""
        metrics = [{"iteration": 1, "episode_reward_mean": -100.0}]
        run_dir = create_experiment_with_metrics(
            tmp_path / "run",
            metrics,
            write_hash=False,
            write_config=False,
        )
        ref_dir = create_experiment_with_metrics(tmp_path / "ref", metrics)

        with pytest.raises(ComparisonError) as exc_info:
            compare_runs(str(run_dir), str(ref_dir))

        assert "config identity" in exc_info.value.message.lower()
