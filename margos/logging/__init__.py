"""Metrics logging callbacks."""

from pathlib import Path

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


__all__ = [
    "MetricsLogger",
    "TensorBoardLogger",
    "TENSORBOARD_AVAILABLE",
    "create_logger",
    "create_tensorboard_logger",
]
