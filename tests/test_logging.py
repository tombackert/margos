"""Unit tests for metrics logging module."""

import json
from pathlib import Path

from marl_platform.logging import MetricsLogger, create_logger
from marl_platform.logging.callbacks import extract_metrics


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
        """extract_metrics extracts basic metrics correctly."""
        mock_result = {
            "training_iteration": 5,
            "episode_reward_mean": -100.0,
            "episode_reward_min": -150.0,
            "episode_reward_max": -50.0,
            "episode_len_mean": 200.0,
        }

        metrics = extract_metrics(mock_result)

        assert metrics["iteration"] == 5
        assert metrics["episode_reward_mean"] == -100.0
        assert metrics["episode_reward_min"] == -150.0
        assert metrics["episode_reward_max"] == -50.0
        assert metrics["episode_len_mean"] == 200.0

    def test_extract_metrics_with_loss(self, tmp_path: Path) -> None:
        """extract_metrics extracts policy loss when available."""
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

        metrics = extract_metrics(mock_result)

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


class TestExtractMetrics:
    """Tests for extract_metrics module-level function."""

    def test_extracts_from_env_runners(self) -> None:
        """Extracts metrics from env_runners location (new RLlib API)."""
        mock_result = {
            "training_iteration": 1,
            "env_runners": {
                "episode_reward_mean": -100.0,
                "episode_len_mean": 200.0,
            },
        }

        metrics = extract_metrics(mock_result)

        assert metrics["episode_reward_mean"] == -100.0
        assert metrics["episode_len_mean"] == 200.0

    def test_extracts_from_sampler_results(self) -> None:
        """Extracts metrics from sampler_results location (old RLlib API)."""
        mock_result = {
            "training_iteration": 1,
            "sampler_results": {
                "episode_reward_mean": -100.0,
                "episode_len_mean": 200.0,
            },
        }

        metrics = extract_metrics(mock_result)

        assert metrics["episode_reward_mean"] == -100.0
        assert metrics["episode_len_mean"] == 200.0

    def test_includes_timestamp(self) -> None:
        """Extracted metrics include timestamp."""
        mock_result = {"training_iteration": 1}

        metrics = extract_metrics(mock_result)

        assert "timestamp" in metrics
        assert "T" in metrics["timestamp"]  # ISO format
