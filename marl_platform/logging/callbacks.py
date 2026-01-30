"""RLlib callbacks for metrics logging."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from ray.rllib.algorithms.callbacks import DefaultCallbacks

try:
    from torch.utils.tensorboard import SummaryWriter

    TENSORBOARD_AVAILABLE = True
except ImportError:
    TENSORBOARD_AVAILABLE = False
    SummaryWriter = None


class MetricsLogger(DefaultCallbacks):
    """RLlib callback that logs training metrics to JSONL file.

    Logged metrics per iteration:
    - iteration: Training iteration number
    - episode_reward_mean: Average episode reward
    - episode_reward_min: Minimum episode reward
    - episode_reward_max: Maximum episode reward
    - episode_len_mean: Average episode length
    - loss: Policy loss (if available)
    - timestamp: ISO format timestamp
    """

    def __init__(self, output_dir: Path | str):
        """Initialize the metrics logger.

        Args:
            output_dir: Directory where logs will be written.
        """
        super().__init__()
        self.output_dir = Path(output_dir)
        self.log_path = self.output_dir / "logs" / "metrics.jsonl"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def on_train_result(
        self,
        *,
        algorithm: Any,
        result: dict[str, Any],
        **kwargs: Any,
    ) -> None:
        """Called after each training iteration.

        Args:
            algorithm: The RLlib algorithm instance.
            result: The result dict from the training iteration.
            **kwargs: Additional keyword arguments.
        """
        metrics = self._extract_metrics(result)
        self._append_log(metrics)

    def _extract_metrics(self, result: dict[str, Any]) -> dict[str, Any]:
        """Extract relevant metrics from RLlib result dict.

        Args:
            result: The raw result dict from RLlib training iteration.

        Returns:
            Dict containing the metrics to log.
        """
        # RLlib result structure varies by version and API stack
        # Try multiple possible keys for compatibility
        metrics: dict[str, Any] = {
            "iteration": result.get("training_iteration"),
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }

        # Episode rewards - try old and new API stack locations
        env_runners = result.get("env_runners", {})
        sampler_results = result.get("sampler_results", {})

        metrics["episode_reward_mean"] = (
            result.get("episode_reward_mean")
            or env_runners.get("episode_reward_mean")
            or sampler_results.get("episode_reward_mean")
        )
        metrics["episode_reward_min"] = (
            result.get("episode_reward_min")
            or env_runners.get("episode_reward_min")
            or sampler_results.get("episode_reward_min")
        )
        metrics["episode_reward_max"] = (
            result.get("episode_reward_max")
            or env_runners.get("episode_reward_max")
            or sampler_results.get("episode_reward_max")
        )
        metrics["episode_len_mean"] = (
            result.get("episode_len_mean")
            or env_runners.get("episode_len_mean")
            or sampler_results.get("episode_len_mean")
        )

        # Try to get policy loss from various locations in result dict
        info = result.get("info", {})
        learner_info = info.get("learner", {})

        # Default policy loss location
        if "default_policy" in learner_info:
            policy_info = learner_info["default_policy"]
            metrics["loss"] = policy_info.get("learner_stats", {}).get(
                "total_loss"
            ) or policy_info.get("total_loss")
        else:
            # Fallback: check top-level learner stats
            metrics["loss"] = learner_info.get("total_loss")

        return metrics

    def _append_log(self, metrics: dict[str, Any]) -> None:
        """Append metrics as JSON line to log file.

        Args:
            metrics: The metrics dict to log.
        """
        with open(self.log_path, "a") as f:
            f.write(json.dumps(metrics) + "\n")


class TensorBoardLogger(DefaultCallbacks):
    """RLlib callback that logs training metrics to TensorBoard.

    Logs the same metrics as MetricsLogger but to TensorBoard format
    for real-time visualization during training.

    Usage:
        tensorboard --logdir results/<exp>/tensorboard
    """

    def __init__(self, output_dir: Path | str):
        """Initialize the TensorBoard logger.

        Args:
            output_dir: Directory where TensorBoard logs will be written.
        """
        super().__init__()
        if not TENSORBOARD_AVAILABLE:
            raise RuntimeError(
                "TensorBoard logging requires torch.utils.tensorboard. "
                "Install with: pip install tensorboard"
            )
        self.output_dir = Path(output_dir)
        self.tb_dir = self.output_dir / "tensorboard"
        self.tb_dir.mkdir(parents=True, exist_ok=True)
        self._writer: Optional[SummaryWriter] = None

    @property
    def writer(self) -> SummaryWriter:
        """Lazy-initialize the SummaryWriter."""
        if self._writer is None:
            self._writer = SummaryWriter(log_dir=str(self.tb_dir))
        return self._writer

    def on_train_result(
        self,
        *,
        algorithm: Any,
        result: dict[str, Any],
        **kwargs: Any,
    ) -> None:
        """Called after each training iteration.

        Args:
            algorithm: The RLlib algorithm instance.
            result: The result dict from the training iteration.
            **kwargs: Additional keyword arguments.
        """
        iteration = result.get("training_iteration", 0)

        # Episode rewards - try old and new API stack locations
        env_runners = result.get("env_runners", {})
        sampler_results = result.get("sampler_results", {})

        episode_reward_mean = (
            result.get("episode_reward_mean")
            or env_runners.get("episode_reward_mean")
            or sampler_results.get("episode_reward_mean")
        )
        episode_reward_min = (
            result.get("episode_reward_min")
            or env_runners.get("episode_reward_min")
            or sampler_results.get("episode_reward_min")
        )
        episode_reward_max = (
            result.get("episode_reward_max")
            or env_runners.get("episode_reward_max")
            or sampler_results.get("episode_reward_max")
        )
        episode_len_mean = (
            result.get("episode_len_mean")
            or env_runners.get("episode_len_mean")
            or sampler_results.get("episode_len_mean")
        )

        # Log to TensorBoard
        if episode_reward_mean is not None:
            self.writer.add_scalar("reward/mean", episode_reward_mean, iteration)
        if episode_reward_min is not None:
            self.writer.add_scalar("reward/min", episode_reward_min, iteration)
        if episode_reward_max is not None:
            self.writer.add_scalar("reward/max", episode_reward_max, iteration)
        if episode_len_mean is not None:
            self.writer.add_scalar("episode/length_mean", episode_len_mean, iteration)

        # Try to get policy loss
        info = result.get("info", {})
        learner_info = info.get("learner", {})

        if "default_policy" in learner_info:
            policy_info = learner_info["default_policy"]
            loss = policy_info.get("learner_stats", {}).get(
                "total_loss"
            ) or policy_info.get("total_loss")
            if loss is not None:
                self.writer.add_scalar("loss/total", loss, iteration)

        self.writer.flush()

    def close(self) -> None:
        """Close the TensorBoard writer."""
        if self._writer is not None:
            self._writer.close()
            self._writer = None
