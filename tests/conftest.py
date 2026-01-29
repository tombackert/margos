"""Shared fixtures for MARL platform tests."""

from pathlib import Path

import pytest
import yaml


@pytest.fixture
def experiment_structure(tmp_path: Path) -> dict[str, Path]:
    """Create standard experiment directory structure.

    Creates:
        experiments/configs/
        experiments/scenarios/
        experiments/training/
        results/

    Returns:
        Dict with keys: configs_dir, scenarios_dir, training_dir, results_dir, base_dir
    """
    configs_dir = tmp_path / "experiments" / "configs"
    scenarios_dir = tmp_path / "experiments" / "scenarios"
    training_dir = tmp_path / "experiments" / "training"
    results_dir = tmp_path / "results"

    configs_dir.mkdir(parents=True)
    scenarios_dir.mkdir(parents=True)
    training_dir.mkdir(parents=True)
    results_dir.mkdir(parents=True)

    return {
        "base_dir": tmp_path,
        "configs_dir": configs_dir,
        "scenarios_dir": scenarios_dir,
        "training_dir": training_dir,
        "results_dir": results_dir,
    }


@pytest.fixture
def simple_scenario(experiment_structure: dict[str, Path]) -> Path:
    """Create a minimal ARGoS scenario file.

    Returns:
        Path to created scenario file.
    """
    scenario = experiment_structure["scenarios_dir"] / "test.argos"
    scenario.write_text("<argos></argos>")
    return scenario


@pytest.fixture
def simple_training_script(experiment_structure: dict[str, Path]) -> Path:
    """Create a minimal training script.

    Returns:
        Path to created training script.
    """
    script = experiment_structure["training_dir"] / "train.py"
    script.write_text("def main(config, callbacks, output_dir): pass")
    return script


@pytest.fixture
def marker_training_script(experiment_structure: dict[str, Path]) -> Path:
    """Create a training script that writes a marker file.

    Returns:
        Path to created training script.
    """
    script = experiment_structure["training_dir"] / "train.py"
    script.write_text("""
def main(config, callbacks, output_dir):
    from pathlib import Path
    Path(output_dir).joinpath("training_complete.txt").write_text("done")
""")
    return script


@pytest.fixture
def simple_config(
    experiment_structure: dict[str, Path],
    simple_scenario: Path,
    simple_training_script: Path,
) -> Path:
    """Create a minimal valid config file.

    Returns:
        Path to created config file.
    """
    config_file = experiment_structure["configs_dir"] / "test_exp.yaml"
    config_data = {
        "experiment": {"name": "test_exp", "seed": 42},
        "scenario": {"file": "scenarios/test.argos"},
        "training": {"script": "training/train.py"},
        "output": {"dir": str(experiment_structure["results_dir"])},
    }
    config_file.write_text(yaml.dump(config_data))
    return config_file


@pytest.fixture
def marker_config(
    experiment_structure: dict[str, Path],
    simple_scenario: Path,
    marker_training_script: Path,
) -> Path:
    """Create a config that uses the marker training script.

    Returns:
        Path to created config file.
    """
    config_file = experiment_structure["configs_dir"] / "test_exp.yaml"
    config_data = {
        "experiment": {"name": "test_exp", "seed": 42},
        "scenario": {"file": "scenarios/test.argos"},
        "training": {"script": "training/train.py"},
        "output": {"dir": str(experiment_structure["results_dir"])},
    }
    config_file.write_text(yaml.dump(config_data))
    return config_file
