"""ArgosToZoo bridge - ARGoS simulator integration for MARL.

This module provides the ArgosEnv class which wraps ARGoS simulation
as a PettingZoo ParallelEnv for use with RLlib and other RL frameworks.
"""

from .argos_env import ArgosEnv
from .scenarios.aggregation import aggregation_reward

__all__ = [
    "ArgosEnv",
    "aggregation_reward",
]
