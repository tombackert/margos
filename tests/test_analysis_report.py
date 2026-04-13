"""Unit tests for analysis report module."""

from pathlib import Path

import pytest

from marl_platform.analysis.report import (
    ReportError,
    calculate_auc,
    calculate_duration,
    format_comparison,
    generate_report,
    generate_summary,
    plot_learning_curve,
    read_metrics,
)

# Import helpers from conftest (pytest automatically loads conftest.py)
from tests.conftest import create_experiment_dir, create_metrics_file


class TestReadMetrics:
    """Tests for read_metrics function."""

    def test_reads_valid_metrics(self, tmp_path: Path) -> None:
        """Reads metrics from valid JSONL file."""
        metrics = [
            {"iteration": 1, "episode_reward_mean": -100.0, "timestamp": "2024-01-01T10:00:00"},
            {"iteration": 2, "episode_reward_mean": -90.0, "timestamp": "2024-01-01T10:01:00"},
        ]
        log_path = create_metrics_file(tmp_path, metrics)

        result = read_metrics(log_path)

        assert len(result) == 2
        assert result[0]["iteration"] == 1
        assert result[1]["episode_reward_mean"] == -90.0

    def test_raises_error_for_missing_file(self, tmp_path: Path) -> None:
        """Raises ReportError when file doesn't exist."""
        with pytest.raises(ReportError) as exc_info:
            read_metrics(tmp_path / "nonexistent.jsonl")

        assert "Metrics log not found" in str(exc_info.value.message)

    def test_raises_error_for_empty_file(self, tmp_path: Path) -> None:
        """Raises ReportError when file is empty."""
        log_path = tmp_path / "logs" / "metrics.jsonl"
        log_path.parent.mkdir(parents=True)
        log_path.write_text("")

        with pytest.raises(ReportError) as exc_info:
            read_metrics(log_path)

        assert "empty" in str(exc_info.value.message).lower()

    def test_skips_empty_lines(self, tmp_path: Path) -> None:
        """Skips empty lines in log file."""
        log_path = tmp_path / "metrics.jsonl"
        log_path.write_text('{"iteration": 1}\n\n{"iteration": 2}\n')

        result = read_metrics(log_path)

        assert len(result) == 2


class TestPlotLearningCurve:
    """Tests for plot_learning_curve function."""

    def test_creates_png_file(self, tmp_path: Path) -> None:
        """Creates a PNG file at the specified path."""
        metrics = [
            {"iteration": 1, "episode_reward_mean": -100.0, "timestamp": "2024-01-01T10:00:00"},
            {"iteration": 2, "episode_reward_mean": -90.0, "timestamp": "2024-01-01T10:01:00"},
            {"iteration": 3, "episode_reward_mean": -80.0, "timestamp": "2024-01-01T10:02:00"},
        ]
        log_path = create_metrics_file(tmp_path, metrics)
        output_path = tmp_path / "report" / "learning_curve.png"

        result = plot_learning_curve(log_path, output_path)

        assert result == output_path
        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_creates_output_directory(self, tmp_path: Path) -> None:
        """Creates parent directories if they don't exist."""
        metrics = [{"iteration": 1, "episode_reward_mean": -100.0, "timestamp": "2024-01-01T10:00:00"}]
        log_path = create_metrics_file(tmp_path, metrics)
        output_path = tmp_path / "deep" / "nested" / "plot.png"

        plot_learning_curve(log_path, output_path)

        assert output_path.exists()

    def test_handles_single_iteration(self, tmp_path: Path) -> None:
        """Handles single data point gracefully."""
        metrics = [{"iteration": 1, "episode_reward_mean": -100.0, "timestamp": "2024-01-01T10:00:00"}]
        log_path = create_metrics_file(tmp_path, metrics)
        output_path = tmp_path / "plot.png"

        plot_learning_curve(log_path, output_path)

        assert output_path.exists()

    def test_handles_negative_rewards(self, tmp_path: Path) -> None:
        """Handles negative reward values correctly."""
        metrics = [
            {"iteration": i, "episode_reward_mean": -200.0 + i * 10, "timestamp": f"2024-01-01T10:0{i}:00"}
            for i in range(1, 6)
        ]
        log_path = create_metrics_file(tmp_path, metrics)
        output_path = tmp_path / "plot.png"

        plot_learning_curve(log_path, output_path)

        assert output_path.exists()


class TestCalculateAuc:
    """Tests for calculate_auc function."""

    def test_calculates_auc_correctly(self) -> None:
        """Calculates area under curve using trapezoidal rule."""
        # Simple case: rectangle with height 10 from x=1 to x=3
        metrics = [
            {"iteration": 1, "episode_reward_mean": 10.0},
            {"iteration": 3, "episode_reward_mean": 10.0},
        ]

        auc = calculate_auc(metrics)

        assert auc == 20.0  # width=2, height=10

    def test_calculates_auc_for_increasing_values(self) -> None:
        """Handles increasing reward values."""
        metrics = [
            {"iteration": 1, "episode_reward_mean": 0.0},
            {"iteration": 2, "episode_reward_mean": 10.0},
            {"iteration": 3, "episode_reward_mean": 20.0},
        ]

        auc = calculate_auc(metrics)

        # Triangle: (2 * 20) / 2 = 20
        assert auc == 20.0

    def test_handles_negative_rewards(self) -> None:
        """Handles negative reward values."""
        metrics = [
            {"iteration": 1, "episode_reward_mean": -100.0},
            {"iteration": 2, "episode_reward_mean": -100.0},
        ]

        auc = calculate_auc(metrics)

        assert auc == -100.0  # width=1, height=-100

    def test_single_point_returns_zero(self) -> None:
        """Single point has zero area."""
        metrics = [{"iteration": 1, "episode_reward_mean": 100.0}]

        auc = calculate_auc(metrics)

        assert auc == 0.0


class TestCalculateDuration:
    """Tests for calculate_duration function."""

    def test_calculates_duration_in_seconds(self) -> None:
        """Calculates duration for short experiments."""
        metrics = [
            {"timestamp": "2024-01-01T10:00:00"},
            {"timestamp": "2024-01-01T10:00:30"},
        ]

        duration = calculate_duration(metrics)

        assert duration == "30s"

    def test_calculates_duration_in_minutes(self) -> None:
        """Calculates duration with minutes."""
        metrics = [
            {"timestamp": "2024-01-01T10:00:00"},
            {"timestamp": "2024-01-01T10:05:30"},
        ]

        duration = calculate_duration(metrics)

        assert duration == "5m 30s"

    def test_calculates_duration_in_hours(self) -> None:
        """Calculates duration with hours."""
        metrics = [
            {"timestamp": "2024-01-01T10:00:00"},
            {"timestamp": "2024-01-01T12:30:45"},
        ]

        duration = calculate_duration(metrics)

        assert duration == "2h 30m 45s"

    def test_single_entry_returns_na(self) -> None:
        """Returns N/A for single entry."""
        metrics = [{"timestamp": "2024-01-01T10:00:00"}]

        duration = calculate_duration(metrics)

        assert duration == "N/A"

    def test_empty_metrics_returns_na(self) -> None:
        """Returns N/A for empty metrics."""
        metrics: list[dict] = []

        duration = calculate_duration(metrics)

        assert duration == "N/A"


class TestGenerateSummary:
    """Tests for generate_summary function."""

    def test_includes_experiment_name(self, tmp_path: Path) -> None:
        """Summary includes experiment directory name."""
        exp_dir = tmp_path / "my_experiment_001"
        metrics = [{"iteration": 1, "episode_reward_mean": -100.0, "timestamp": "2024-01-01T10:00:00"}]
        create_experiment_dir(exp_dir, metrics)

        summary = generate_summary(exp_dir, metrics)

        assert "my_experiment_001" in summary

    def test_includes_config_hash(self, tmp_path: Path) -> None:
        """Summary includes config hash."""
        exp_dir = tmp_path / "exp"
        metrics = [{"iteration": 1, "episode_reward_mean": -100.0, "timestamp": "2024-01-01T10:00:00"}]
        create_experiment_dir(exp_dir, metrics, config_hash="sha256hash123")

        summary = generate_summary(exp_dir, metrics)

        assert "sha256hash123" in summary

    def test_includes_total_iterations(self, tmp_path: Path) -> None:
        """Summary includes total iteration count."""
        exp_dir = tmp_path / "exp"
        metrics = [
            {"iteration": i, "episode_reward_mean": -100.0 + i, "timestamp": f"2024-01-01T10:0{i}:00"}
            for i in range(1, 6)
        ]
        create_experiment_dir(exp_dir, metrics)

        summary = generate_summary(exp_dir, metrics)

        assert "Total Iterations: 5" in summary

    def test_includes_final_reward(self, tmp_path: Path) -> None:
        """Summary includes final reward value."""
        exp_dir = tmp_path / "exp"
        metrics = [
            {"iteration": 1, "episode_reward_mean": -100.0, "timestamp": "2024-01-01T10:00:00"},
            {"iteration": 2, "episode_reward_mean": -75.5, "timestamp": "2024-01-01T10:01:00"},
        ]
        create_experiment_dir(exp_dir, metrics)

        summary = generate_summary(exp_dir, metrics)

        assert "Final Reward: -75.5" in summary

    def test_includes_best_reward(self, tmp_path: Path) -> None:
        """Summary includes best (max) reward value."""
        exp_dir = tmp_path / "exp"
        metrics = [
            {"iteration": 1, "episode_reward_mean": -100.0, "timestamp": "2024-01-01T10:00:00"},
            {"iteration": 2, "episode_reward_mean": -50.0, "timestamp": "2024-01-01T10:01:00"},
            {"iteration": 3, "episode_reward_mean": -75.0, "timestamp": "2024-01-01T10:02:00"},
        ]
        create_experiment_dir(exp_dir, metrics)

        summary = generate_summary(exp_dir, metrics)

        assert "Best Reward: -50.0" in summary

    def test_includes_auc(self, tmp_path: Path) -> None:
        """Summary includes AUC value."""
        exp_dir = tmp_path / "exp"
        metrics = [
            {"iteration": 1, "episode_reward_mean": -100.0, "timestamp": "2024-01-01T10:00:00"},
            {"iteration": 2, "episode_reward_mean": -100.0, "timestamp": "2024-01-01T10:01:00"},
        ]
        create_experiment_dir(exp_dir, metrics)

        summary = generate_summary(exp_dir, metrics)

        assert "AUC" in summary

    def test_includes_duration(self, tmp_path: Path) -> None:
        """Summary includes training duration."""
        exp_dir = tmp_path / "exp"
        metrics = [
            {"iteration": 1, "episode_reward_mean": -100.0, "timestamp": "2024-01-01T10:00:00"},
            {"iteration": 2, "episode_reward_mean": -90.0, "timestamp": "2024-01-01T10:05:00"},
        ]
        create_experiment_dir(exp_dir, metrics)

        summary = generate_summary(exp_dir, metrics)

        assert "Training Duration:" in summary


class TestFormatComparison:
    """Tests for format_comparison function."""

    @staticmethod
    def _comparison(**overrides) -> dict:
        comparison = {
            "tail_reward_mean_match": True,
            "tail_reward_mean_deviation": 0.005,
            "tail_reward_mean_run": 100.5,
            "tail_reward_mean_ref": 100.0,
            "reward_window": 50,
            "reward_window_run": 50,
            "reward_window_ref": 50,
            "tolerance": 0.05,
            "final_reward_match": True,
            "final_reward_deviation": 0.005,
            "final_reward_run": 100.5,
            "final_reward_ref": 100.0,
            "auc_match": True,
            "auc_deviation": 0.003,
            "auc_run": 1003.0,
            "auc_ref": 1000.0,
            "config_hash_match": True,
            "config_hash_run": "abc123def456",
            "config_hash_ref": "abc123def456",
            "config_hash_source": {"run": "config_hash.txt", "reference": "config_hash.txt"},
            "config_integrity_match": True,
            "config_integrity_run": {"match": True, "source": "config.yaml"},
            "config_integrity_ref": {"match": True, "source": "config.yaml"},
            "passed": True,
        }
        comparison.update(overrides)
        return comparison

    def test_formats_passed_comparison(self) -> None:
        """Formats passed comparison result."""
        comparison = self._comparison()

        result = format_comparison(comparison)

        assert "PASSED" in result
        assert "| Yes" in result  # Table format has "| Yes"
        assert "Config Hash" in result
        assert "Reward Mean L50" in result

    def test_formats_failed_comparison(self) -> None:
        """Formats failed comparison result."""
        comparison = self._comparison(
            tail_reward_mean_match=False,
            tail_reward_mean_deviation=0.15,
            tail_reward_mean_run=115.0,
            tail_reward_mean_ref=100.0,
            final_reward_match=False,
            final_reward_deviation=0.15,
            final_reward_run=115.0,
            final_reward_ref=100.0,
            passed=False,
        )

        result = format_comparison(comparison)

        assert "FAILED" in result
        assert "| No" in result  # Table format has "| No"

    def test_includes_deviation_percentages(self) -> None:
        """Includes deviation as percentage."""
        comparison = self._comparison(
            tail_reward_mean_deviation=0.0075,
            tail_reward_mean_run=100.75,
            auc_deviation=0.0025,
            auc_run=1002.5,
        )

        result = format_comparison(comparison)

        assert "0.75%" in result
        assert "0.25%" in result

    def test_includes_actual_values(self) -> None:
        """Includes actual run and reference values."""
        comparison = self._comparison(
            tail_reward_mean_deviation=0.01,
            tail_reward_mean_run=101.0,
            auc_deviation=0.01,
            auc_run=505.0,
            auc_ref=500.0,
        )

        result = format_comparison(comparison)

        assert "101.0000" in result
        assert "100.0000" in result
        assert "505.0000" in result
        assert "500.0000" in result


class TestGenerateReport:
    """Tests for generate_report function."""

    def test_creates_report_directory(self, tmp_path: Path) -> None:
        """Creates report directory."""
        exp_dir = tmp_path / "exp"
        metrics = [
            {"iteration": i, "episode_reward_mean": -100.0 + i * 10, "timestamp": f"2024-01-01T10:0{i}:00"}
            for i in range(1, 4)
        ]
        create_experiment_dir(exp_dir, metrics)

        report_path = generate_report(str(exp_dir))

        assert Path(report_path).exists()
        assert Path(report_path).is_dir()

    def test_creates_learning_curve_png(self, tmp_path: Path) -> None:
        """Creates learning curve plot."""
        exp_dir = tmp_path / "exp"
        metrics = [
            {"iteration": i, "episode_reward_mean": -100.0 + i * 10, "timestamp": f"2024-01-01T10:0{i}:00"}
            for i in range(1, 4)
        ]
        create_experiment_dir(exp_dir, metrics)

        report_path = generate_report(str(exp_dir))

        plot_path = Path(report_path) / "learning_curve.png"
        assert plot_path.exists()

    def test_creates_summary_txt(self, tmp_path: Path) -> None:
        """Creates summary text file."""
        exp_dir = tmp_path / "exp"
        metrics = [
            {"iteration": i, "episode_reward_mean": -100.0 + i * 10, "timestamp": f"2024-01-01T10:0{i}:00"}
            for i in range(1, 4)
        ]
        create_experiment_dir(exp_dir, metrics)

        report_path = generate_report(str(exp_dir))

        summary_path = Path(report_path) / "summary.txt"
        assert summary_path.exists()
        content = summary_path.read_text()
        assert "Experiment Summary" in content

    def test_with_reference_includes_comparison(self, tmp_path: Path) -> None:
        """Report with reference includes comparison section."""
        # Create two identical experiments
        metrics = [
            {"iteration": i, "episode_reward_mean": -100.0 + i * 10, "timestamp": f"2024-01-01T10:0{i}:00"}
            for i in range(1, 4)
        ]
        exp_dir = create_experiment_dir(tmp_path / "exp", metrics)
        ref_dir = create_experiment_dir(tmp_path / "ref", metrics)

        report_path = generate_report(str(exp_dir), str(ref_dir))

        summary_path = Path(report_path) / "summary.txt"
        content = summary_path.read_text()
        assert "Reproducibility Comparison" in content
        assert "PASSED" in content
