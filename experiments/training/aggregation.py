"""Aggregation training script following platform convention.

Platform calls: main(config, callbacks, output_dir, progress=None)
"""

import logging
import os
import warnings
from pathlib import Path
from typing import Any, Optional

# Suppress warnings and verbose logging BEFORE any Ray imports
os.environ["PYTHONWARNINGS"] = "ignore"
os.environ["RAY_DEDUP_LOGS"] = "0"
# Disable Ray's default logging to stderr
os.environ["RAY_LOG_TO_STDERR"] = "0"

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*gputil.*")
warnings.filterwarnings("ignore", message=".*deprecated.*")

# Suppress Ray's verbose logging at module level
for logger_name in ["ray", "ray.rllib", "ray.tune", "ray.data", "ray.train"]:
    logging.getLogger(logger_name).setLevel(logging.ERROR)


class _DeprecationFilter(logging.Filter):
    """Filter out deprecation warnings from Ray."""

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        skip_patterns = [
            "DeprecationWarning",
            "has been deprecated",
            "Install gputil",
            "will raise an error in the future",
        ]
        return not any(pattern in msg for pattern in skip_patterns)


def _install_logging_filter() -> None:
    """Install deprecation filter on all handlers."""
    filt = _DeprecationFilter()
    # Add filter to root logger and all Ray loggers
    for name in [None, "ray", "ray.rllib", "ray.tune"]:
        logger = logging.getLogger(name)
        for handler in logger.handlers:
            handler.addFilter(filt)
        logger.addFilter(filt)


def main(
    config: dict[str, Any],
    callbacks: list,
    output_dir: str,
    progress: Optional[Any] = None,
) -> None:
    """Training entry point called by platform orchestrator.

    Args:
        config: Full experiment config (PlatformConfig as dict)
        callbacks: List of RLlib callbacks (includes MetricsLogger)
        output_dir: Path for checkpoints
        progress: Optional TrainingProgress for reporting progress
    """
    # Check if tensorboard is enabled
    tensorboard_enabled = config.get("training", {}).get("tensorboard", False)

    # Initialize Ray with minimal logging before any other Ray imports
    import ray
    if not ray.is_initialized():
        ray.init(
            logging_level=logging.WARNING if tensorboard_enabled else logging.ERROR,
            log_to_driver=tensorboard_enabled,
            configure_logging=tensorboard_enabled,
        )

    # Suppress all Ray-related loggers and install deprecation filter (unless tensorboard enabled)
    if not tensorboard_enabled:
        for name in ["ray", "ray.rllib", "ray.tune", "ray.data", "ray.train"]:
            logging.getLogger(name).setLevel(logging.ERROR)
        _install_logging_filter()

    # Delayed imports to ensure seeds are set first
    from ray.rllib.algorithms.ppo import PPOConfig
    from ray.rllib.env.wrappers.pettingzoo_env import ParallelPettingZooEnv
    from ray.tune.registry import register_env

    from marl_platform.argos_zoo import ArgosEnv, aggregation_reward, prepare_scenario

    # Prepare scenario file with library paths
    scenario_template = config["scenario"]["file"]
    scenario_path = prepare_scenario(scenario_template)

    # Get training iterations
    iterations = config.get("training", {}).get("iterations", 10)

    # Start progress bar
    if progress:
        progress.start(iterations + 2, "Initializing")  # +2 for init and checkpoint steps

    # Environment creator
    def env_creator(cfg: dict) -> ParallelPettingZooEnv:
        env = ArgosEnv(
            argos_file=scenario_path,
            max_steps=100,
            reward_fn=aggregation_reward,
            quiet=True,
            startup_delay=3.0,
        )
        return ParallelPettingZooEnv(env)

    register_env("aggregation", env_creator)

    # Create a combined callback that delegates to all callbacks from orchestrator
    # (includes MetricsLogger + TensorBoardLogger if enabled)
    from ray.rllib.algorithms.callbacks import DefaultCallbacks

    class CombinedCallbacks(DefaultCallbacks):
        """Wraps multiple callback instances and delegates to all of them."""

        def __init__(self, *args: Any, **kwargs: Any):
            super().__init__(*args, **kwargs)
            self._callbacks = callbacks  # Capture callbacks from outer scope

        def on_train_result(self, *, algorithm: Any, result: dict, **kwargs: Any) -> None:
            super().on_train_result(algorithm=algorithm, result=result, **kwargs)
            for cb in self._callbacks:
                cb.on_train_result(algorithm=algorithm, result=result, **kwargs)

    # Build algorithm with stable API
    algo_config = PPOConfig()
    algo_config = algo_config.api_stack(
        enable_rl_module_and_learner=False,
        enable_env_runner_and_connector_v2=False,
    )
    algo_config = algo_config.environment("aggregation")
    algo_config = algo_config.framework("torch")
    algo_config = algo_config.callbacks(CombinedCallbacks)
    algo_config = algo_config.env_runners(
        num_env_runners=0,
        rollout_fragment_length=50,
    )
    algo_config.train_batch_size = 200
    algo_config.sgd_minibatch_size = 64
    algo_config.num_sgd_iter = 5

    # Configure TensorBoard logging if enabled
    if tensorboard_enabled:
        tensorboard_dir = Path(output_dir).resolve() / "tensorboard"
        tensorboard_dir.mkdir(parents=True, exist_ok=True)

        # Print prominent TensorBoard instructions
        print("")
        print("=" * 60)
        print("TENSORBOARD ENABLED")
        print("=" * 60)
        print(f"Log directory: {tensorboard_dir}")
        print("")
        print("To view live training progress, run in a new terminal:")
        print(f"  tensorboard --logdir {tensorboard_dir}")
        print("")
        print("Then open: http://localhost:6006")
        print("=" * 60)
        print("")

    algo = algo_config.build()

    # Update progress after initialization
    if progress:
        progress.update(1, description="Training")

    # Training loop
    last_reward = 0.0
    for i in range(iterations):
        result = algo.train()
        # Extract reward - check multiple locations for compatibility
        last_reward = (
            result.get("episode_reward_mean")
            or result.get("env_runners", {}).get("episode_reward_mean")
            or result.get("sampler_results", {}).get("episode_reward_mean")
            or 0.0
        )

        # Update progress
        if progress:
            progress.update(i + 2, reward=last_reward)  # +2 because init was step 1

    # Save checkpoint
    if progress:
        progress.update(iterations + 1, description="Saving checkpoint", reward=last_reward)

    checkpoint_dir = Path(output_dir) / "checkpoints" / "final"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    algo.save(str(checkpoint_dir))

    algo.stop()

    # Mark complete
    if progress:
        progress.update(iterations + 2, description="Complete", reward=last_reward)
