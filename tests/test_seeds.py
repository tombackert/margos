"""Unit tests for seed propagation module."""

import random

import numpy as np
import pytest
import torch

from marl_platform.utils.seeds import get_seed_state, set_all_seeds


class TestSetAllSeeds:
    """Tests for set_all_seeds function."""

    def test_python_random_determinism(self) -> None:
        """Same seed produces same random sequence."""
        set_all_seeds(42)
        a = [random.random() for _ in range(5)]

        set_all_seeds(42)
        b = [random.random() for _ in range(5)]

        assert a == b

    def test_numpy_determinism(self) -> None:
        """Same seed produces same numpy random sequence."""
        set_all_seeds(42)
        a = np.random.rand(5)

        set_all_seeds(42)
        b = np.random.rand(5)

        assert np.array_equal(a, b)

    def test_torch_determinism(self) -> None:
        """Same seed produces same torch random sequence."""
        set_all_seeds(42)
        a = torch.rand(5)

        set_all_seeds(42)
        b = torch.rand(5)

        assert torch.equal(a, b)

    def test_different_seeds_produce_different_results(self) -> None:
        """Different seeds produce different sequences."""
        set_all_seeds(42)
        a = [random.random() for _ in range(5)]

        set_all_seeds(99)
        b = [random.random() for _ in range(5)]

        assert a != b

    def test_seed_zero(self) -> None:
        """Seed zero works correctly."""
        set_all_seeds(0)
        a = [random.random() for _ in range(5)]

        set_all_seeds(0)
        b = [random.random() for _ in range(5)]

        assert a == b

    def test_large_seed(self) -> None:
        """Large seed values work correctly."""
        set_all_seeds(2**31 - 1)
        a = [random.random() for _ in range(5)]

        set_all_seeds(2**31 - 1)
        b = [random.random() for _ in range(5)]

        assert a == b


class TestGetSeedState:
    """Tests for get_seed_state function."""

    def test_returns_dict(self) -> None:
        """Returns a dictionary with expected keys."""
        state = get_seed_state()

        assert isinstance(state, dict)
        assert "random" in state
        assert "numpy" in state
        assert "torch" in state

    def test_state_captures_random(self) -> None:
        """Captures Python random state."""
        set_all_seeds(42)
        state = get_seed_state()

        assert state["random"] is not None
        assert isinstance(state["random"], tuple)

    def test_state_captures_numpy(self) -> None:
        """Captures NumPy random state."""
        set_all_seeds(42)
        state = get_seed_state()

        # NumPy state is a tuple with specific structure
        assert state["numpy"] is not None
        assert not isinstance(state["numpy"], str)

    def test_state_captures_torch(self) -> None:
        """Captures PyTorch random state."""
        set_all_seeds(42)
        state = get_seed_state()

        assert state["torch"] is not None
        assert not isinstance(state["torch"], str)


class TestCrossLibraryDeterminism:
    """Tests for determinism across multiple libraries."""

    def test_combined_operations_deterministic(self) -> None:
        """Combined operations from multiple RNG sources are deterministic."""
        def generate_values():
            set_all_seeds(42)
            py_val = random.random()
            np_val = np.random.rand()
            torch_val = torch.rand(1).item()
            return py_val, np_val, torch_val

        result1 = generate_values()
        result2 = generate_values()

        assert result1 == result2

    def test_interleaved_calls_deterministic(self) -> None:
        """Interleaved calls to different RNGs are deterministic."""
        def generate_interleaved():
            set_all_seeds(123)
            values = []
            for _ in range(3):
                values.append(random.random())
                values.append(np.random.rand())
                values.append(torch.rand(1).item())
            return values

        result1 = generate_interleaved()
        result2 = generate_interleaved()

        assert result1 == result2
