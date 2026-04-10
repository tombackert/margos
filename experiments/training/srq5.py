"""SRQ5 training script matching the manual baseline PPO setup.

Platform calls: main(config, callbacks, output_dir, progress=None)
"""

import os
from pathlib import Path
from typing import Any, Optional

from marl_platform.utils.ray_logging import init_ray, setup_ray_environment

# Setup Ray environment before any Ray imports
setup_ray_environment()


def main(
    config: dict[str, Any],
    callbacks: list,
    output_dir: str,
    progress: Optional[Any] = None,
) -> None:
    """Training entry point called by platform orchestrator."""
    os.environ.setdefault("RAY_DISABLE_MEMORY_MONITOR", "1")
    init_ray()

    from ray.rllib.algorithms.ppo import PPOConfig
    from ray.rllib.env.wrappers.pettingzoo_env import ParallelPettingZooEnv
    from ray.tune.registry import register_env

    from marl_platform.argos_zoo import ArgosEnv, aggregation_reward, prepare_scenario

    scenario_template = config["scenario"]["file"]
    scenario_path = prepare_scenario(scenario_template)
    iterations = config.get("training", {}).get("iterations", 10)
    env_name = "aggregation_srq5"

    def env_creator(env_config: dict) -> ParallelPettingZooEnv:
        env = ArgosEnv(
            argos_file=env_config.get("argos_file", scenario_path),
            expected_num_agents=env_config.get("expected_num_agents", 5),
            max_steps=100,
            reward_fn=aggregation_reward,
            quiet=True,
            controller_log_level="ERROR",
            loop_log_level="ERROR",
        )
        return ParallelPettingZooEnv(env)

    register_env(env_name, env_creator)

    # Mirror the manual SRQ5 PPOConfig setup used in ArgosToZoo.
    algo_config = (
        PPOConfig()
        .environment(
            env=env_name,
            env_config={
                "argos_file": scenario_path,
                "expected_num_agents": 5,
            },
        )
        .api_stack(
            enable_rl_module_and_learner=False,
            enable_env_runner_and_connector_v2=False,
        )
        .framework("torch")
        .env_runners(
            num_env_runners=0,
            rollout_fragment_length="auto",
        )
        .training(
            entropy_coeff=0.01,
            train_batch_size=2000,
            minibatch_size=500,
            num_epochs=10,
        )
        .debugging(log_level="ERROR")
    )

    algo = algo_config.build()

    if progress:
        progress.start(iterations, "Training")

    last_reward = 0.0
    for i in range(iterations):
        result = algo.train()

        for cb in callbacks:
            cb.on_train_result(algorithm=algo, result=result)

        last_reward = (
            result.get("episode_reward_mean")
            or result.get("env_runners", {}).get("episode_reward_mean")
            or result.get("sampler_results", {}).get("episode_reward_mean")
            or 0.0
        )

        if progress:
            progress.update(i + 1, reward=last_reward)

    checkpoint_dir = Path(output_dir) / "checkpoints" / "final"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    algo.save(str(checkpoint_dir))

    algo.stop()
