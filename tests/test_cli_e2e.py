"""End-to-end CLI tests for the MARL platform.

These tests exercise the full workflow through the CLI entry point,
validating the complete integration from user command to output.
"""

import json
import time
from pathlib import Path

import yaml
from typer.testing import CliRunner

from marl_platform.cli import app

runner = CliRunner()


class TestRunCommand:
    """E2E tests for `platform run` command."""

    def test_run_with_valid_experiment(self, tmp_path: Path) -> None:
        """Full pipeline via CLI creates expected outputs."""
        # Setup experiment structure
        configs_dir = tmp_path / "experiments" / "configs"
        scenarios_dir = tmp_path / "experiments" / "scenarios"
        training_dir = tmp_path / "experiments" / "training"
        results_dir = tmp_path / "results"

        configs_dir.mkdir(parents=True)
        scenarios_dir.mkdir(parents=True)
        training_dir.mkdir(parents=True)
        results_dir.mkdir(parents=True)

        # Create scenario file
        scenario = scenarios_dir / "test.argos"
        scenario.write_text("<argos></argos>")

        # Create training script
        training_script = training_dir / "train.py"
        training_script.write_text("""
def main(config, callbacks, output_dir):
    from pathlib import Path
    Path(output_dir).joinpath("training_complete.txt").write_text("done")
""")

        # Create config
        config_file = configs_dir / "test_exp.yaml"
        config_data = {
            "experiment": {"name": "test_exp", "seed": 42},
            "scenario": {"file": "scenarios/test.argos"},
            "training": {"script": "training/train.py", "tensorboard": False},
            "output": {"dir": str(results_dir)},
        }
        config_file.write_text(yaml.dump(config_data))

        # Run CLI command
        result = runner.invoke(
            app,
            ["run", str(config_file)],
        )

        # Verify CLI succeeded
        assert result.exit_code == 0, f"CLI failed: {result.stdout}"
        assert "Running experiment" in result.stdout
        assert "Output:" in result.stdout

        # Verify outputs created
        output_dirs = list(results_dir.iterdir())
        assert len(output_dirs) == 1

        output_dir = output_dirs[0]
        assert (output_dir / "config.yaml").exists()
        assert (output_dir / "config_hash.txt").exists()
        assert (output_dir / "config_integrity.yaml").exists()
        assert (output_dir / "env_fingerprint.yaml").exists()
        assert (output_dir / "logs").is_dir()
        assert (output_dir / "checkpoints").is_dir()
        assert (output_dir / "training_complete.txt").exists()

    def test_run_with_experiment_name_convention(self, tmp_path: Path) -> None:
        """Run command resolves experiment name to config path (L7 convention)."""
        # Setup experiment structure
        configs_dir = tmp_path / "experiments" / "configs"
        scenarios_dir = tmp_path / "experiments" / "scenarios"
        training_dir = tmp_path / "experiments" / "training"
        results_dir = tmp_path / "results"

        configs_dir.mkdir(parents=True)
        scenarios_dir.mkdir(parents=True)
        training_dir.mkdir(parents=True)
        results_dir.mkdir(parents=True)

        scenario = scenarios_dir / "test.argos"
        scenario.write_text("<argos></argos>")

        training_script = training_dir / "train.py"
        training_script.write_text("def main(config, callbacks, output_dir): pass")

        config_file = configs_dir / "my_experiment.yaml"
        config_data = {
            "experiment": {"name": "my_experiment", "seed": 42},
            "scenario": {"file": "scenarios/test.argos"},
            "training": {"script": "training/train.py", "tensorboard": False},
            "output": {"dir": str(results_dir)},
        }
        config_file.write_text(yaml.dump(config_data))

        # Run with just experiment name (not full path)
        result = runner.invoke(
            app,
            ["run", "my_experiment", "--config-dir", str(configs_dir)],
        )

        assert result.exit_code == 0, f"CLI failed: {result.stdout}"

    def test_run_missing_config_shows_error(self, tmp_path: Path) -> None:
        """Missing config shows user-friendly error."""
        result = runner.invoke(
            app,
            ["run", "nonexistent", "--config-dir", str(tmp_path)],
        )

        assert result.exit_code == 1
        assert "Error" in result.stdout
        assert "not found" in result.stdout.lower() or "Config" in result.stdout

    def test_run_invalid_config_shows_error(self, tmp_path: Path) -> None:
        """Invalid config shows validation error."""
        configs_dir = tmp_path / "configs"
        configs_dir.mkdir()

        # Create config missing required fields
        config_file = configs_dir / "bad.yaml"
        config_file.write_text("experiment:\n  name: test\n")

        result = runner.invoke(
            app,
            ["run", str(config_file)],
        )

        assert result.exit_code == 1
        assert "Error" in result.stdout

    def test_run_training_script_error_shows_error(self, tmp_path: Path) -> None:
        """Training script failure shows user-friendly error."""
        configs_dir = tmp_path / "experiments" / "configs"
        scenarios_dir = tmp_path / "experiments" / "scenarios"
        training_dir = tmp_path / "experiments" / "training"
        results_dir = tmp_path / "results"

        configs_dir.mkdir(parents=True)
        scenarios_dir.mkdir(parents=True)
        training_dir.mkdir(parents=True)
        results_dir.mkdir(parents=True)

        scenario = scenarios_dir / "test.argos"
        scenario.write_text("<argos></argos>")

        # Training script that raises an error
        training_script = training_dir / "train.py"
        training_script.write_text("""
def main(config, callbacks, output_dir):
    raise RuntimeError("Training failed intentionally")
""")

        config_file = configs_dir / "fail_exp.yaml"
        config_data = {
            "experiment": {"name": "fail_exp", "seed": 42},
            "scenario": {"file": "scenarios/test.argos"},
            "training": {"script": "training/train.py", "tensorboard": False},
            "output": {"dir": str(results_dir)},
        }
        config_file.write_text(yaml.dump(config_data))

        result = runner.invoke(app, ["run", str(config_file)])

        assert result.exit_code == 1
        assert "Error" in result.stdout
        assert "Training" in result.stdout or "failed" in result.stdout.lower()


class TestCompareCommand:
    """E2E tests for `platform compare` command."""

    def test_compare_missing_experiment_shows_error(self, tmp_path: Path) -> None:
        """Missing experiment shows user-friendly error."""
        result = runner.invoke(
            app,
            ["compare", "nonexistent", "reference", "--results-dir", str(tmp_path)],
        )

        assert result.exit_code == 1
        assert "Error" in result.stdout

    def test_compare_fails_on_config_hash_mismatch(self, tmp_path: Path) -> None:
        """Compare output distinguishes SRQ5 handoff from SRQ3 strict reproducibility."""
        results_dir = tmp_path / "results"
        run_dir = results_dir / "run"
        ref_dir = results_dir / "ref"

        for target in (run_dir, ref_dir):
            (target / "logs").mkdir(parents=True)
            with open(target / "logs" / "metrics.jsonl", "w") as f:
                f.write(json.dumps({"iteration": 1, "episode_reward_mean": -100.0}) + "\n")
            (target / "config.yaml").write_text(yaml.dump({
                "experiment": {"name": target.name, "seed": 42},
                "scenario": {"file": "/tmp/scenario.argos"},
                "training": {"script": "/tmp/train.py"},
                "output": {"dir": "results"},
            }))

        (run_dir / "config_hash.txt").write_text("runhash")
        (ref_dir / "config_hash.txt").write_text("refhash")

        result = runner.invoke(
            app,
            ["compare", "run", "ref", "--results-dir", str(results_dir)],
        )

        assert result.exit_code == 0
        assert "SRQ5 Handoff" in result.stdout
        assert "SRQ3 Strict" in result.stdout
        assert "PASSED" in result.stdout
        assert "FAILED" in result.stdout
        assert "Reward Mean" in result.stdout
        assert "Config Hash" in result.stdout


class TestExportCommand:
    """E2E tests for `platform export` command."""

    def test_export_missing_experiment_shows_error(self, tmp_path: Path) -> None:
        """Missing experiment shows user-friendly error."""
        result = runner.invoke(
            app,
            ["export", "nonexistent", "--results-dir", str(tmp_path)],
        )

        assert result.exit_code == 1
        assert "Error" in result.stdout


class TestImportCommand:
    """E2E tests for `platform import` command."""

    def test_import_missing_bundle_shows_error(self, tmp_path: Path) -> None:
        """Missing bundle shows user-friendly error."""
        result = runner.invoke(
            app,
            ["import", "nonexistent.zip", "--bundles-dir", str(tmp_path)],
        )

        assert result.exit_code == 1
        assert "Error" in result.stdout


class TestVerboseFlag:
    """Tests for --verbose flag behavior."""

    def test_verbose_flag_accepted(self, tmp_path: Path) -> None:
        """Verbose flag is parsed correctly."""
        result = runner.invoke(
            app,
            ["--verbose", "run", "nonexistent", "--config-dir", str(tmp_path)],
        )

        # Should still fail but verbose should be accepted
        assert result.exit_code == 1


class TestDeterministicExecution:
    """E2E tests for reproducibility (SRQ3)."""

    def test_same_seed_produces_same_outputs(self, tmp_path: Path) -> None:
        """Same seed should produce deterministic results."""
        configs_dir = tmp_path / "experiments" / "configs"
        scenarios_dir = tmp_path / "experiments" / "scenarios"
        training_dir = tmp_path / "experiments" / "training"
        results_dir = tmp_path / "results"

        configs_dir.mkdir(parents=True)
        scenarios_dir.mkdir(parents=True)
        training_dir.mkdir(parents=True)
        results_dir.mkdir(parents=True)

        scenario = scenarios_dir / "test.argos"
        scenario.write_text("<argos></argos>")

        # Training script that writes random values
        training_script = training_dir / "train.py"
        training_script.write_text("""
import random
import numpy as np
from pathlib import Path

def main(config, callbacks, output_dir):
    py_rand = random.random()
    np_rand = np.random.random()

    Path(output_dir).joinpath("random_values.txt").write_text(
        f"py:{py_rand}\\nnp:{np_rand}"
    )
""")

        config_file = configs_dir / "seed_test.yaml"
        config_data = {
            "experiment": {"name": "seed_test", "seed": 42},
            "scenario": {"file": "scenarios/test.argos"},
            "training": {"script": "training/train.py", "tensorboard": False},
            "output": {"dir": str(results_dir)},
        }
        config_file.write_text(yaml.dump(config_data))

        # Run twice (with delay to ensure different timestamps)
        result1 = runner.invoke(app, ["run", str(config_file)])
        assert result1.exit_code == 0

        time.sleep(1.1)  # Ensure different timestamp (format is YYYYMMDD-HHMMSS)

        result2 = runner.invoke(app, ["run", str(config_file)])
        assert result2.exit_code == 0

        # Compare random values
        output_dirs = sorted(results_dir.iterdir())
        assert len(output_dirs) == 2, f"Expected 2 runs, got {len(output_dirs)}"

        val1 = (output_dirs[0] / "random_values.txt").read_text()
        val2 = (output_dirs[1] / "random_values.txt").read_text()

        assert val1 == val2, "Same seed should produce identical random values"

    def test_config_hash_is_deterministic(self, tmp_path: Path) -> None:
        """Config hash should be deterministic."""
        configs_dir = tmp_path / "experiments" / "configs"
        scenarios_dir = tmp_path / "experiments" / "scenarios"
        training_dir = tmp_path / "experiments" / "training"
        results_dir = tmp_path / "results"

        configs_dir.mkdir(parents=True)
        scenarios_dir.mkdir(parents=True)
        training_dir.mkdir(parents=True)
        results_dir.mkdir(parents=True)

        scenario = scenarios_dir / "test.argos"
        scenario.write_text("<argos></argos>")

        training_script = training_dir / "train.py"
        training_script.write_text("def main(config, callbacks, output_dir): pass")

        config_file = configs_dir / "hash_test.yaml"
        config_data = {
            "experiment": {"name": "hash_test", "seed": 42},
            "scenario": {"file": "scenarios/test.argos"},
            "training": {"script": "training/train.py", "tensorboard": False},
            "output": {"dir": str(results_dir)},
        }
        config_file.write_text(yaml.dump(config_data))

        # Run twice (with delay to ensure different timestamps)
        runner.invoke(app, ["run", str(config_file)])

        time.sleep(1.1)  # Ensure different timestamp

        runner.invoke(app, ["run", str(config_file)])

        # Compare hashes
        output_dirs = sorted(results_dir.iterdir())
        assert len(output_dirs) == 2, f"Expected 2 runs, got {len(output_dirs)}"
        hash1 = (output_dirs[0] / "config_hash.txt").read_text()
        hash2 = (output_dirs[1] / "config_hash.txt").read_text()

        assert hash1 == hash2, "Config hash should be deterministic"


class TestOutputStructure:
    """E2E tests for output directory structure."""

    def test_output_follows_naming_convention(self, tmp_path: Path) -> None:
        """Output directory follows exp_<name>_<timestamp> format."""
        configs_dir = tmp_path / "experiments" / "configs"
        scenarios_dir = tmp_path / "experiments" / "scenarios"
        training_dir = tmp_path / "experiments" / "training"
        results_dir = tmp_path / "results"

        configs_dir.mkdir(parents=True)
        scenarios_dir.mkdir(parents=True)
        training_dir.mkdir(parents=True)
        results_dir.mkdir(parents=True)

        scenario = scenarios_dir / "test.argos"
        scenario.write_text("<argos></argos>")

        training_script = training_dir / "train.py"
        training_script.write_text("def main(config, callbacks, output_dir): pass")

        config_file = configs_dir / "my_exp.yaml"
        config_data = {
            "experiment": {"name": "my_exp", "seed": 42},
            "scenario": {"file": "scenarios/test.argos"},
            "training": {"script": "training/train.py", "tensorboard": False},
            "output": {"dir": str(results_dir)},
        }
        config_file.write_text(yaml.dump(config_data))

        runner.invoke(app, ["run", str(config_file)])

        output_dirs = list(results_dir.iterdir())
        assert len(output_dirs) == 1

        dir_name = output_dirs[0].name
        assert dir_name.startswith("my_exp_")
        # Check timestamp format: YYYYMMDD-HHMMSS
        timestamp = dir_name[len("my_exp_"):]
        assert len(timestamp) == 15  # 8 + 1 + 6
        assert timestamp[8] == "-"

    def test_frozen_config_matches_input(self, tmp_path: Path) -> None:
        """Frozen config preserves input values."""
        configs_dir = tmp_path / "experiments" / "configs"
        scenarios_dir = tmp_path / "experiments" / "scenarios"
        training_dir = tmp_path / "experiments" / "training"
        results_dir = tmp_path / "results"

        configs_dir.mkdir(parents=True)
        scenarios_dir.mkdir(parents=True)
        training_dir.mkdir(parents=True)
        results_dir.mkdir(parents=True)

        scenario = scenarios_dir / "test.argos"
        scenario.write_text("<argos></argos>")

        training_script = training_dir / "train.py"
        training_script.write_text("def main(config, callbacks, output_dir): pass")

        config_file = configs_dir / "freeze_test.yaml"
        config_data = {
            "experiment": {"name": "freeze_test", "seed": 123},
            "scenario": {"file": "scenarios/test.argos"},
            "training": {"script": "training/train.py", "tensorboard": False},
            "output": {"dir": str(results_dir)},
        }
        config_file.write_text(yaml.dump(config_data))

        runner.invoke(app, ["run", str(config_file)])

        output_dirs = list(results_dir.iterdir())
        frozen_config = yaml.safe_load((output_dirs[0] / "config.yaml").read_text())

        assert frozen_config["experiment"]["name"] == "freeze_test"
        assert frozen_config["experiment"]["seed"] == 123
