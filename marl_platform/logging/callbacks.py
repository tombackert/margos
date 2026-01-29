"""RLlib callbacks for metrics logging."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from ray.rllib.algorithms.callbacks import DefaultCallbacks


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
