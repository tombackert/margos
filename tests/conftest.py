"""Shared fixtures for MARL platform tests."""

import json
import zipfile
from pathlib import Path

import pytest
import yaml


# --- Helper functions (used by fixtures and tests) ---


def create_metrics_file(path: Path, metrics: list[dict]) -> Path:
    """Helper to create a metrics.jsonl file."""
    log_dir = path / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "metrics.jsonl"
    with open(log_path, "w") as f:
        for m in metrics:
            f.write(json.dumps(m) + "\n")
    return log_path


def create_experiment_dir(
    path: Path,
    metrics: list[dict] | None = None,
    config_hash: str = "abc123",
    scenario_path: Path | None = None,
    script_path: Path | None = None,
) -> Path:
    """Helper to create a minimal experiment directory.

    Args:
        path: Directory path for the experiment
        metrics: Optional metrics list (defaults to single iteration)
        config_hash: Config hash string
        scenario_path: Optional path to scenario file to reference
        script_path: Optional path to training script to reference

    Returns:
        Path to created experiment directory
    """
    path.mkdir(parents=True, exist_ok=True)

    if metrics is None:
        metrics = [{"iteration": 1, "episode_reward_mean": -100.0}]

    create_metrics_file(path, metrics)
    (path / "config_hash.txt").write_text(config_hash)

    # Create config.yaml
    config = {
        "experiment": {"name": path.name, "seed": 42},
        "scenario": {"file": str(scenario_path) if scenario_path else "/path/to/scenario.argos"},
        "training": {"script": str(script_path) if script_path else "/path/to/train.py"},
        "output": {"dir": "results/"},
    }
    (path / "config.yaml").write_text(yaml.dump(config))

    # Create env_fingerprint.yaml
    fingerprint = {
        "python": "3.12.0",
        "os": "Linux",
        "packages": {"ray": "2.0.0", "torch": "2.0.0"},
    }
    (path / "env_fingerprint.yaml").write_text(yaml.dump(fingerprint))

    return path


def create_valid_bundle(path: Path, exp_name: str = "test_exp") -> Path:
    """Helper to create a valid bundle ZIP file."""
    bundle_path = path / f"{exp_name}.zip"

    with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Manifest
        manifest = {
            "version": "1.0",
            "experiment_name": exp_name,
            "exported_at": "2024-01-01T10:00:00",
            "platform_version": "0.1.0",
        }
        zf.writestr("manifest.yaml", yaml.dump(manifest))

        # Config
        config = {
            "experiment": {"name": exp_name, "seed": 42},
            "scenario": {"file": "scenario.argos"},
            "training": {"script": "train.py"},
        }
        zf.writestr("config.yaml", yaml.dump(config))

        # Fingerprint
        fingerprint = {
            "python": "3.12.0",
            "os": "Linux-5.10.0",
            "packages": {"ray": "2.0.0", "torch": "2.0.0", "numpy": "1.24.0"},
        }
        zf.writestr("env_fingerprint.yaml", yaml.dump(fingerprint))

        # Metrics
        metrics = [{"iteration": 1, "episode_reward_mean": -100.0}]
        zf.writestr("logs/metrics.jsonl", "\n".join(json.dumps(m) for m in metrics))

    return bundle_path


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
