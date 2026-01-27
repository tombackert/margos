#!/usr/bin/env python3
"""Manual verification script for ARGoS integration."""

import tempfile
from pathlib import Path


def prepare_scenario() -> str:
    """Create scenario file with correct library paths."""
    repo_root = Path(__file__).parent.parent
    template = repo_root / "experiments/scenarios/footbot_aggregation.argos"

    controller_lib = repo_root / "argos_plugins/build/controllers/libmy_ipc_controller.dylib"
    loop_lib = repo_root / "argos_plugins/build/loop_functions/libzoo_loop_functions.dylib"

    if not controller_lib.exists():
        raise FileNotFoundError(f"Controller not built: {controller_lib}")
    if not loop_lib.exists():
        raise FileNotFoundError(f"Loop functions not built: {loop_lib}")

    content = template.read_text()
    content = content.replace("MARL_PLATFORM_CONTROLLER_LIB", str(controller_lib.resolve()))
    content = content.replace("MARL_PLATFORM_LOOP_LIB", str(loop_lib.resolve()))

    # Write to temp file
    fd, path = tempfile.mkstemp(suffix=".argos")
    Path(path).write_text(content)
    return path


def main():
    print("=== MARL Platform ARGoS Verification ===\n")

    # 1. Prepare scenario
    print("1. Preparing scenario file...")
    scenario_path = prepare_scenario()
    print(f"   Created: {scenario_path}\n")

    # 2. Import and create environment
    print("2. Creating ArgosEnv...")
    from marl_platform.argos_zoo import ArgosEnv
    from marl_platform.argos_zoo.scenarios.aggregation import aggregation_reward

    env = ArgosEnv(
        argos_file=scenario_path,
        max_steps=50,
        startup_delay=3.0,
        reward_fn=aggregation_reward,
    )
    print(f"   Environment created successfully\n")

    # 3. Reset and show agents
    print("3. Resetting environment (seed=42)...")
    obs, infos = env.reset(seed=42)
    print(f"   Agents discovered: {env.agents}")
    print(f"   Number of agents: {len(env.agents)}\n")

    # 4. Show observation structure
    print("4. Observation structure:")
    agent = env.agents[0]
    print(f"   Agent '{agent}':")
    print(f"     - position shape: {obs[agent]['position'].shape}")
    print(f"     - proximity shape: {obs[agent]['proximity'].shape}")
    print(f"     - position: {obs[agent]['position']}\n")

    # 5. Run a few steps
    print("5. Running 10 steps with random actions...")
    total_reward = 0.0
    for step in range(10):
        actions = {a: env.action_space(a).sample() for a in env.agents}
        obs, rewards, terms, truncs, infos = env.step(actions)
        step_reward = sum(rewards.values()) / len(rewards)
        total_reward += step_reward
        print(f"   Step {step+1}: mean_reward={step_reward:.4f}")

    print(f"\n   Total reward over 10 steps: {total_reward:.4f}\n")

    # 6. Clean up
    print("6. Closing environment...")
    env.close()
    print("   Done!\n")

    print("=== Verification Complete ===")
    print("All systems operational!")


if __name__ == "__main__":
    main()
