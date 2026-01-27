"""Unit tests for metrics logging module."""

import json
from pathlib import Path

from marl_platform.logging import MetricsLogger, create_logger, read_metrics


class TestMetricsLogger:
    """Tests for MetricsLogger class."""

    def test_creates_log_directory(self, tmp_path: Path) -> None:
        """Logger creates log directory structure."""
        logger = MetricsLogger(tmp_path / "output")

        assert logger.log_path.parent.exists()
        assert logger.log_path.parent.name == "logs"

    def test_log_path_structure(self, tmp_path: Path) -> None:
        """Log path follows expected structure."""
        logger = MetricsLogger(tmp_path)

        assert logger.log_path == tmp_path / "logs" / "metrics.jsonl"

    def test_on_train_result_logs_metrics(self, tmp_path: Path) -> None:
        """on_train_result writes metrics to log file."""
        logger = MetricsLogger(tmp_path)
        mock_result = {
            "training_iteration": 1,
            "episode_reward_mean": -150.0,
            "episode_reward_min": -200.0,
            "episode_reward_max": -100.0,
            "episode_len_mean": 500.0,
        }

        logger.on_train_result(algorithm=None, result=mock_result)

        assert logger.log_path.exists()
        with open(logger.log_path) as f:
            line = f.readline()
        metrics = json.loads(line)
        assert metrics["iteration"] == 1
        assert metrics["episode_reward_mean"] == -150.0

    def test_multiple_iterations_logged(self, tmp_path: Path) -> None:
        """Multiple training iterations are appended to log."""
        logger = MetricsLogger(tmp_path)

        for i in range(3):
            mock_result = {
                "training_iteration": i + 1,
                "episode_reward_mean": -150.0 + i * 10,
            }
            logger.on_train_result(algorithm=None, result=mock_result)

        with open(logger.log_path) as f:
            lines = f.readlines()
        assert len(lines) == 3

        # Check iteration numbers
        metrics_list = [json.loads(line) for line in lines]
        assert [m["iteration"] for m in metrics_list] == [1, 2, 3]

    def test_timestamp_included(self, tmp_path: Path) -> None:
        """Logged metrics include timestamp."""
        logger = MetricsLogger(tmp_path)
        mock_result = {"training_iteration": 1}

        logger.on_train_result(algorithm=None, result=mock_result)

        with open(logger.log_path) as f:
            metrics = json.loads(f.readline())
        assert "timestamp" in metrics
        assert "T" in metrics["timestamp"]  # ISO format

    def test_missing_metrics_handled(self, tmp_path: Path) -> None:
        """Missing metrics are logged as None."""
        logger = MetricsLogger(tmp_path)
        mock_result = {"training_iteration": 1}  # Minimal result

        logger.on_train_result(algorithm=None, result=mock_result)

        with open(logger.log_path) as f:
            metrics = json.loads(f.readline())
        assert metrics["episode_reward_mean"] is None
        assert metrics["episode_len_mean"] is None

    def test_extract_metrics_basic(self, tmp_path: Path) -> None:
        """_extract_metrics extracts basic metrics correctly."""
        logger = MetricsLogger(tmp_path)
        mock_result = {
            "training_iteration": 5,
            "episode_reward_mean": -100.0,
            "episode_reward_min": -150.0,
            "episode_reward_max": -50.0,
            "episode_len_mean": 200.0,
        }

        metrics = logger._extract_metrics(mock_result)

        assert metrics["iteration"] == 5
        assert metrics["episode_reward_mean"] == -100.0
        assert metrics["episode_reward_min"] == -150.0
        assert metrics["episode_reward_max"] == -50.0
        assert metrics["episode_len_mean"] == 200.0

    def test_extract_metrics_with_loss(self, tmp_path: Path) -> None:
        """_extract_metrics extracts policy loss when available."""
        logger = MetricsLogger(tmp_path)
        mock_result = {
            "training_iteration": 1,
            "info": {
                "learner": {
                    "default_policy": {
                        "total_loss": 0.5,
                    }
                }
            },
        }

        metrics = logger._extract_metrics(mock_result)

        assert metrics["loss"] == 0.5


class TestCreateLogger:
    """Tests for create_logger factory function."""

    def test_returns_metrics_logger(self, tmp_path: Path) -> None:
        """Factory returns MetricsLogger instance."""
        logger = create_logger(tmp_path)

        assert isinstance(logger, MetricsLogger)

    def test_configures_output_dir(self, tmp_path: Path) -> None:
        """Factory configures correct output directory."""
        output_dir = tmp_path / "my_output"
        logger = create_logger(output_dir)

        assert logger.output_dir == output_dir


class TestReadMetrics:
    """Tests for read_metrics function."""

    def test_reads_empty_file(self, tmp_path: Path) -> None:
        """Returns empty list for nonexistent file."""
        metrics = read_metrics(tmp_path / "nonexistent.jsonl")

        assert metrics == []

    def test_reads_single_entry(self, tmp_path: Path) -> None:
        """Reads single log entry."""
        log_path = tmp_path / "metrics.jsonl"
        log_path.write_text('{"iteration": 1, "episode_reward_mean": -100.0}\n')

        metrics = read_metrics(log_path)

        assert len(metrics) == 1
        assert metrics[0]["iteration"] == 1
        assert metrics[0]["episode_reward_mean"] == -100.0

    def test_reads_multiple_entries(self, tmp_path: Path) -> None:
        """Reads multiple log entries."""
        log_path = tmp_path / "metrics.jsonl"
        lines = [
            '{"iteration": 1, "episode_reward_mean": -150.0}',
            '{"iteration": 2, "episode_reward_mean": -140.0}',
            '{"iteration": 3, "episode_reward_mean": -130.0}',
        ]
        log_path.write_text("\n".join(lines) + "\n")

        metrics = read_metrics(log_path)

        assert len(metrics) == 3
        assert [m["iteration"] for m in metrics] == [1, 2, 3]
        assert [m["episode_reward_mean"] for m in metrics] == [-150.0, -140.0, -130.0]

    def test_handles_empty_lines(self, tmp_path: Path) -> None:
        """Skips empty lines in log file."""
        log_path = tmp_path / "metrics.jsonl"
        content = '{"iteration": 1}\n\n{"iteration": 2}\n\n'
        log_path.write_text(content)

        metrics = read_metrics(log_path)

        assert len(metrics) == 2

    def test_roundtrip_with_logger(self, tmp_path: Path) -> None:
        """Metrics written by logger can be read back."""
        logger = MetricsLogger(tmp_path)

        # Log some iterations
        for i in range(5):
            mock_result = {
                "training_iteration": i + 1,
                "episode_reward_mean": -150.0 + i * 10,
                "episode_reward_min": -200.0 + i * 10,
                "episode_reward_max": -100.0 + i * 10,
                "episode_len_mean": 500.0,
            }
            logger.on_train_result(algorithm=None, result=mock_result)

        # Read back
        metrics = read_metrics(logger.log_path)

        assert len(metrics) == 5
        assert metrics[0]["iteration"] == 1
        assert metrics[4]["iteration"] == 5
        assert metrics[0]["episode_reward_mean"] == -150.0
        assert metrics[4]["episode_reward_mean"] == -110.0
