"""Integration tests for ArgosEnv with actual ARGoS simulator.

These tests require:
1. ARGoS3 installed and accessible via `argos3` command
2. Margos plugins built in argos_plugins/build/

Run with: pytest tests/test_argos_integration.py -v
Skip with: pytest tests/test_argos_integration.py -v -m "not argos"
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import pytest


def argos_available() -> bool:
    """Check if ARGoS is available."""
    try:
        result = subprocess.run(
            ["argos3", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def margos_plugins_available() -> bool:
    """Check if Margos plugins are built."""
    repo_root = Path(__file__).parent.parent
    controller = repo_root / "argos_plugins/build/controllers/libmy_ipc_controller.dylib"
    loop_fn = repo_root / "argos_plugins/build/loop_functions/libzoo_loop_functions.dylib"
    return controller.exists() and loop_fn.exists()


def get_plugin_paths() -> tuple[Path, Path]:
    """Get absolute paths to built plugin libraries."""
    repo_root = Path(__file__).parent.parent
    controller = repo_root / "argos_plugins/build/controllers/libmy_ipc_controller.dylib"
    loop_fn = repo_root / "argos_plugins/build/loop_functions/libzoo_loop_functions.dylib"
    return controller.resolve(), loop_fn.resolve()


def prepare_scenario_file(template_path: Path, output_path: Path) -> None:
    """Prepare a scenario file by substituting library paths."""
    controller_lib, loop_lib = get_plugin_paths()

    content = template_path.read_text()
    content = content.replace("MARGOS_CONTROLLER_LIB", str(controller_lib))
    content = content.replace("MARGOS_LOOP_LIB", str(loop_lib))

    output_path.write_text(content)


# Skip marker for tests requiring ARGoS
requires_argos = pytest.mark.skipif(
    not (argos_available() and margos_plugins_available()),
    reason="ARGoS or Margos plugins not available",
)


@requires_argos
class TestArgosEnvIntegration:
    """Integration tests with actual ARGoS simulator."""

    @pytest.fixture
    def scenario_file(self, tmp_path: Path) -> str:
        """Create a prepared scenario file with substituted library paths."""
        repo_root = Path(__file__).parent.parent
        template = repo_root / "experiments/scenarios/footbot_aggregation.argos"
        output = tmp_path / "test_scenario.argos"
        prepare_scenario_file(template, output)
        return str(output)

    def test_env_creation(self, scenario_file: str) -> None:
        """ArgosEnv can be created with valid scenario."""
        from margos.argos_zoo import ArgosEnv

        env = ArgosEnv(
            argos_file=scenario_file,
            max_steps=10,
            quiet=True,
            startup_delay=3.0,
        )
        assert env is not None
        env.close()

    def test_reset_returns_observations(self, scenario_file: str) -> None:
        """Reset returns observations for all agents."""
        from margos.argos_zoo import ArgosEnv

        env = ArgosEnv(
            argos_file=scenario_file,
            max_steps=10,
            quiet=True,
            startup_delay=3.0,
        )

        obs, infos = env.reset(seed=42)

        assert obs is not None
        assert len(obs) > 0  # At least one agent
        assert len(env.agents) == 5  # 5 footbots in scenario

        # Check observation structure
        for agent_id, agent_obs in obs.items():
            assert "proximity" in agent_obs
            assert "position" in agent_obs
            assert agent_obs["proximity"].shape == (24,)
            assert agent_obs["position"].shape == (3,)

        env.close()

    def test_step_executes(self, scenario_file: str) -> None:
        """Step executes actions and returns new observations."""
        from margos.argos_zoo import ArgosEnv

        env = ArgosEnv(
            argos_file=scenario_file,
            max_steps=10,
            quiet=True,
            startup_delay=3.0,
        )

        obs, _ = env.reset(seed=42)

        # Take random actions
        actions = {agent: env.action_space(agent).sample() for agent in env.agents}
        obs2, rewards, terms, truncs, infos = env.step(actions)

        assert obs2 is not None
        assert len(obs2) == len(env.possible_agents)
        assert all(agent in rewards for agent in env.possible_agents)

        env.close()

    def test_seeding_determinism(self, scenario_file: str) -> None:
        """Same seed produces same initial observations."""
        from margos.argos_zoo import ArgosEnv

        # Run 1
        env1 = ArgosEnv(
            argos_file=scenario_file,
            max_steps=10,
            quiet=True,
            startup_delay=3.0,
        )
        obs1, _ = env1.reset(seed=42)
        positions1 = env1.get_last_positions()
        env1.close()

        # Run 2 with same seed
        env2 = ArgosEnv(
            argos_file=scenario_file,
            max_steps=10,
            quiet=True,
            startup_delay=3.0,
        )
        obs2, _ = env2.reset(seed=42)
        positions2 = env2.get_last_positions()
        env2.close()

        # Positions should match
        assert positions1 is not None
        assert positions2 is not None
        np.testing.assert_array_almost_equal(
            np.array(positions1),
            np.array(positions2),
            decimal=5,
        )

    def test_episode_truncation(self, scenario_file: str) -> None:
        """Episode truncates after max_steps."""
        from margos.argos_zoo import ArgosEnv

        env = ArgosEnv(
            argos_file=scenario_file,
            max_steps=5,  # Short episode
            quiet=True,
            startup_delay=3.0,
        )

        env.reset(seed=42)

        # Run until truncation
        for step in range(10):
            actions = {agent: 0 for agent in env.agents}  # stop action
            if not env.agents:
                break
            obs, rewards, terms, truncs, infos = env.step(actions)

        # Should have truncated
        assert env.timestep >= 5
        assert len(env.agents) == 0  # Episode done

        env.close()
