"""Unit tests for argos_zoo module.

Note: Tests that require ARGoS simulator are marked with pytest.mark.argos
and will be skipped if ARGoS is not installed.
"""

import numpy as np
import pytest

from margos.argos_zoo import ArgosEnv, aggregation_reward
from margos.argos_zoo.scenarios.aggregation import aggregation_reward as agg_reward_direct


class TestArgosZooImports:
    """Tests for argos_zoo module imports."""

    def test_argos_env_importable(self) -> None:
        """ArgosEnv class is importable."""
        assert ArgosEnv is not None

    def test_aggregation_reward_importable(self) -> None:
        """aggregation_reward function is importable from main module."""
        assert aggregation_reward is not None
        assert callable(aggregation_reward)

    def test_aggregation_reward_from_scenarios(self) -> None:
        """aggregation_reward is same function from scenarios submodule."""
        assert aggregation_reward is agg_reward_direct


class TestAggregationReward:
    """Tests for aggregation reward function (no ARGoS needed)."""

    def test_first_step_returns_zero(self) -> None:
        """First step returns zero reward and initializes cache."""
        positions = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
        data = {
            "agents": ["robot_0", "robot_1", "robot_2"],
            "positions": positions,
            "proximities": {},
            "prev": {},
            "first_step": True,
        }

        team_reward, per_agent, metrics = aggregation_reward(data)

        assert team_reward == 0.0
        assert per_agent is None
        assert "reward" in metrics
        assert metrics["reward"] == 0.0

    def test_subsequent_step_computes_reward(self) -> None:
        """Subsequent steps compute actual reward."""
        # Initialize cache with first step
        prev_cache: dict = {}
        positions_t0 = np.array([[0.0, 0.0, 0.0], [2.0, 0.0, 0.0], [0.0, 2.0, 0.0]])
        data_t0 = {
            "agents": ["robot_0", "robot_1", "robot_2"],
            "positions": positions_t0,
            "proximities": {},
            "prev": prev_cache,
            "first_step": True,
        }
        aggregation_reward(data_t0)

        # Second step: robots move closer to centroid
        positions_t1 = np.array([[0.5, 0.5, 0.0], [1.5, 0.5, 0.0], [0.5, 1.5, 0.0]])
        data_t1 = {
            "agents": ["robot_0", "robot_1", "robot_2"],
            "positions": positions_t1,
            "proximities": {},
            "prev": prev_cache,  # Same cache, now populated
            "first_step": False,
        }
        team_reward, per_agent, metrics = aggregation_reward(data_t1)

        # Should get some non-zero reward (robots moved closer)
        assert isinstance(team_reward, float)
        assert per_agent is None
        assert "cohesion_mean" in metrics
        assert "team_reward" in metrics

    def test_empty_agents_returns_zero(self) -> None:
        """Empty agents list returns zero reward."""
        data = {
            "agents": [],
            "positions": None,
            "prev": {},
            "first_step": False,
        }

        team_reward, per_agent, metrics = aggregation_reward(data)

        assert team_reward == 0.0
        assert metrics["reward"] == 0.0

    def test_none_positions_returns_zero(self) -> None:
        """None positions returns zero reward."""
        data = {
            "agents": ["robot_0"],
            "positions": None,
            "prev": {},
            "first_step": False,
        }

        team_reward, per_agent, metrics = aggregation_reward(data)

        assert team_reward == 0.0

    def test_custom_hyperparameters(self) -> None:
        """Custom hyperparameters are applied."""
        positions = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
        data = {
            "agents": ["robot_0", "robot_1"],
            "positions": positions,
            "prev": {},
            "first_step": True,
        }

        _, _, metrics = aggregation_reward(data, alpha=0.5, beta=2.0, gamma=0.1, mu=0.3)

        assert metrics["alpha"] == 0.5
        assert metrics["beta"] == 2.0
        assert metrics["gamma"] == 0.1
        assert metrics["mu"] == 0.3


class TestArgosEnvStructure:
    """Tests for ArgosEnv class structure (no simulator needed)."""

    def test_argos_env_is_parallel_env(self) -> None:
        """ArgosEnv inherits from PettingZoo ParallelEnv."""
        from pettingzoo import ParallelEnv

        assert issubclass(ArgosEnv, ParallelEnv)

    def test_argos_env_has_metadata(self) -> None:
        """ArgosEnv has required metadata."""
        assert hasattr(ArgosEnv, "metadata")
        assert "name" in ArgosEnv.metadata

    def test_argos_env_rejects_legacy_params(self) -> None:
        """ArgosEnv rejects removed legacy parameters."""
        with pytest.raises(TypeError, match="Removed legacy"):
            # This would fail anyway since argos_file doesn't exist,
            # but the legacy param check happens first
            ArgosEnv(
                argos_file="/nonexistent.argos",
                w_coh=1.0,  # Legacy parameter
            )
