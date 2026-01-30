"""Metrics logging callbacks."""

import json
from pathlib import Path
from typing import Any

from .callbacks import MetricsLogger, TensorBoardLogger, TENSORBOARD_AVAILABLE


def create_logger(output_dir: Path | str) -> MetricsLogger:
    """Factory function to create configured MetricsLogger.

    Args:
        output_dir: Directory where logs will be written.

    Returns:
        Configured MetricsLogger instance.
    """
    return MetricsLogger(output_dir)


def create_tensorboard_logger(output_dir: Path | str) -> TensorBoardLogger | None:
    """Factory function to create configured TensorBoardLogger.

    Args:
        output_dir: Directory where TensorBoard logs will be written.

    Returns:
        Configured TensorBoardLogger instance, or None if TensorBoard unavailable.
    """
    if not TENSORBOARD_AVAILABLE:
        return None
    return TensorBoardLogger(output_dir)


def read_metrics(log_path: Path | str) -> list[dict[str, Any]]:
    """Read all metrics from JSONL log file.

    Args:
        log_path: Path to the metrics.jsonl file.

    Returns:
        List of metric dicts, one per training iteration.
    """
    log_path = Path(log_path)
    metrics: list[dict[str, Any]] = []

    if not log_path.exists():
        return metrics

    with open(log_path) as f:
        for line in f:
            line = line.strip()
            if line:
                metrics.append(json.loads(line))

    return metrics


__all__ = [
    "MetricsLogger",
    "TensorBoardLogger",
    "TENSORBOARD_AVAILABLE",
    "create_logger",
    "create_tensorboard_logger",
    "read_metrics",
]
