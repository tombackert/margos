"""Aggregation training script following platform convention.

Platform calls: main(config, callbacks, output_dir, progress=None)
"""

import os
from pathlib import Path
from typing import Any, Optional

from marl_platform.utils.ray_logging import setup_ray_environment, init_ray

# Setup Ray environment before any Ray imports
setup_ray_environment()


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
    # Initialize Ray with minimal logging
    os.environ.setdefault("RAY_DISABLE_MEMORY_MONITOR", "1")
    init_ray()

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

    # Build algorithm with stable API
    algo_config = PPOConfig()
    algo_config = algo_config.api_stack(
        enable_rl_module_and_learner=False,
        enable_env_runner_and_connector_v2=False,
    )
    algo_config = algo_config.environment("aggregation")
    algo_config = algo_config.framework("torch")
    algo_config = algo_config.env_runners(
        num_env_runners=0,
        rollout_fragment_length="auto",  # aligns with train_batch_size, no episode truncation
    )
    algo_config = algo_config.training(
        entropy_coeff=0.01,              # exploration pressure on Discrete(5)
    )
    algo_config.train_batch_size = 2000     # ~20 complete episodes per update
    algo_config.sgd_minibatch_size = 500    # 25% of train_batch_size (standard PPO)
    algo_config.num_sgd_iter = 10           # standard PPO default

    # Print TensorBoard instructions
    tensorboard_dir = Path(output_dir).resolve() / "tensorboard"
    tensorboard_dir.mkdir(parents=True, exist_ok=True)

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

        # Call platform callbacks manually (avoids Ray serialization issues)
        for cb in callbacks:
            cb.on_train_result(algorithm=algo, result=result)

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
