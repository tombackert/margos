"""Centralized seed propagation for reproducibility."""

import logging
import random
from typing import Any

logger = logging.getLogger(__name__)


def set_all_seeds(seed: int) -> None:
    """Propagate seed to all Python-side RNG sources.

    MUST be called BEFORE importing training script to seed any
    module-level RNG initialization.

    Sources seeded:
    - random.seed(seed)
    - numpy.random.seed(seed)
    - torch.manual_seed(seed)
    - torch.cuda.manual_seed_all(seed)

    Note: ARGoS seeding is handled separately by ArgosEnv.reset(seed=X)

    Args:
        seed: Non-negative integer seed value.
    """
    # Python stdlib random
    random.seed(seed)
    logger.debug(f"Set random.seed({seed})")

    # NumPy
    try:
        import numpy as np

        np.random.seed(seed)
        logger.debug(f"Set numpy.random.seed({seed})")
    except ImportError:
        logger.debug("NumPy not installed, skipping numpy seeding")

    # PyTorch
    try:
        import torch

        torch.manual_seed(seed)
        logger.debug(f"Set torch.manual_seed({seed})")

        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
            logger.debug(f"Set torch.cuda.manual_seed_all({seed})")
    except ImportError:
        logger.debug("PyTorch not installed, skipping torch seeding")


def get_seed_state() -> dict[str, Any]:
    """Capture current RNG states for debugging.

    Returns:
        Dict with states from each available RNG source.
        Missing packages are marked as "not installed".
    """
    state: dict[str, Any] = {
        "random": random.getstate(),
    }

    # NumPy
    try:
        import numpy as np

        state["numpy"] = np.random.get_state()
    except ImportError:
        state["numpy"] = "not installed"

    # PyTorch
    try:
        import torch

        state["torch"] = torch.get_rng_state()
        if torch.cuda.is_available():
            state["torch_cuda"] = torch.cuda.get_rng_state_all()
        else:
            state["torch_cuda"] = "CUDA not available"
    except ImportError:
        state["torch"] = "not installed"
        state["torch_cuda"] = "not installed"

    return state
