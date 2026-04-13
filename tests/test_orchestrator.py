"""Tests for the training orchestrator."""

import os
from pathlib import Path

import pytest
import yaml


class TestCreateOutputDir:
    """Tests for create_output_dir function."""

    def test_creates_directory(self, tmp_path: Path) -> None:
        """Output directory is created."""
        from marl_platform.config.schema import PlatformConfig, ExperimentConfig, ScenarioConfig, TrainingConfig, OutputConfig
        from marl_platform.orchestrator import create_output_dir

        config = PlatformConfig(
            experiment=ExperimentConfig(name="test_exp", seed=42),
            scenario=ScenarioConfig(file="test.argos"),
            training=TrainingConfig(script="test.py"),
            output=OutputConfig(dir=str(tmp_path)),
        )

        output_dir = create_output_dir(config)

        assert output_dir.exists()
        assert output_dir.is_dir()

    def test_creates_logs_subdir(self, tmp_path: Path) -> None:
        """Logs subdirectory is created."""
        from marl_platform.config.schema import PlatformConfig, ExperimentConfig, ScenarioConfig, TrainingConfig, OutputConfig
        from marl_platform.orchestrator import create_output_dir

        config = PlatformConfig(
            experiment=ExperimentConfig(name="test_exp", seed=42),
            scenario=ScenarioConfig(file="test.argos"),
            training=TrainingConfig(script="test.py"),
            output=OutputConfig(dir=str(tmp_path)),
        )

        output_dir = create_output_dir(config)

        assert (output_dir / "logs").exists()
        assert (output_dir / "logs").is_dir()

    def test_creates_checkpoints_subdir(self, tmp_path: Path) -> None:
        """Checkpoints subdirectory is created."""
        from marl_platform.config.schema import PlatformConfig, ExperimentConfig, ScenarioConfig, TrainingConfig, OutputConfig
        from marl_platform.orchestrator import create_output_dir

        config = PlatformConfig(
            experiment=ExperimentConfig(name="test_exp", seed=42),
            scenario=ScenarioConfig(file="test.argos"),
            training=TrainingConfig(script="test.py"),
            output=OutputConfig(dir=str(tmp_path)),
        )

        output_dir = create_output_dir(config)

        assert (output_dir / "checkpoints").exists()
        assert (output_dir / "checkpoints").is_dir()

    def test_directory_name_format(self, tmp_path: Path) -> None:
        """Directory name follows expected format."""
        from marl_platform.config.schema import PlatformConfig, ExperimentConfig, ScenarioConfig, TrainingConfig, OutputConfig
        from marl_platform.orchestrator import create_output_dir

        config = PlatformConfig(
            experiment=ExperimentConfig(name="my_experiment", seed=42),
            scenario=ScenarioConfig(file="test.argos"),
            training=TrainingConfig(script="test.py"),
            output=OutputConfig(dir=str(tmp_path)),
        )

        output_dir = create_output_dir(config)

        # Name should be my_experiment_YYYYMMDD-HHMMSS
        assert output_dir.name.startswith("my_experiment_")
        # Check timestamp format (8 digits, dash, 6 digits)
        timestamp_part = output_dir.name[len("my_experiment_"):]
        assert len(timestamp_part) == 15  # YYYYMMDD-HHMMSS
        assert timestamp_part[8] == "-"


class TestExecuteTrainingScript:
    """Tests for execute_training_script function."""

    def test_script_not_found_raises_error(self, tmp_path: Path) -> None:
        """Missing script raises TrainingError."""
        from marl_platform.orchestrator import execute_training_script
        from marl_platform.utils.errors import TrainingError

        with pytest.raises(TrainingError) as exc_info:
            execute_training_script(
                script_path=tmp_path / "nonexistent.py",
                config=None,
                callbacks=[],
                output_dir=tmp_path,
            )

        assert "not found" in exc_info.value.message

    def test_script_missing_main_raises_error(self, tmp_path: Path) -> None:
        """Script without main() raises TrainingError."""
        from marl_platform.orchestrator import execute_training_script
        from marl_platform.utils.errors import TrainingError

        # Create script without main
        script = tmp_path / "no_main.py"
        script.write_text("x = 1\n")

        with pytest.raises(TrainingError) as exc_info:
            execute_training_script(
                script_path=script,
                config=None,
                callbacks=[],
                output_dir=tmp_path,
            )

        assert "missing main()" in exc_info.value.message

    def test_script_syntax_error_raises_error(self, tmp_path: Path) -> None:
        """Script with syntax error raises TrainingError."""
        from marl_platform.orchestrator import execute_training_script
        from marl_platform.utils.errors import TrainingError

        # Create script with syntax error
        script = tmp_path / "syntax_error.py"
        script.write_text("def main( broken\n")

        with pytest.raises(TrainingError) as exc_info:
            execute_training_script(
                script_path=script,
                config=None,
                callbacks=[],
                output_dir=tmp_path,
            )

        assert "syntax error" in exc_info.value.message

    def test_valid_script_executes(self, tmp_path: Path) -> None:
        """Valid training script executes successfully."""
        from marl_platform.config.schema import PlatformConfig, ExperimentConfig, ScenarioConfig, TrainingConfig, OutputConfig
        from marl_platform.orchestrator import execute_training_script

        # Create valid training script
        script = tmp_path / "train.py"
        script.write_text("""
def main(config, callbacks, output_dir):
    # Write marker file to prove execution
    from pathlib import Path
    Path(output_dir).joinpath("executed.txt").write_text("success")
""")

        config = PlatformConfig(
            experiment=ExperimentConfig(name="test", seed=42),
            scenario=ScenarioConfig(file="test.argos"),
            training=TrainingConfig(script=str(script)),
            output=OutputConfig(dir=str(tmp_path)),
        )

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        execute_training_script(
            script_path=script,
            config=config,
            callbacks=[],
            output_dir=output_dir,
        )

        # Verify script executed
        assert (output_dir / "executed.txt").exists()
        assert (output_dir / "executed.txt").read_text() == "success"


class TestRunExperiment:
    """Tests for run_experiment function."""

    def test_config_not_found_raises_error(self, tmp_path: Path) -> None:
        """Missing config raises ConfigNotFoundError."""
        from marl_platform.orchestrator import run_experiment
        from marl_platform.utils.errors import ConfigNotFoundError

        with pytest.raises(ConfigNotFoundError):
            run_experiment(str(tmp_path / "nonexistent.yaml"))

    def test_full_pipeline_executes(self, tmp_path: Path) -> None:
        """Full pipeline creates expected outputs."""
        from marl_platform.orchestrator import run_experiment

        # Create directory structure
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
            "training": {"script": "training/train.py"},
            "output": {"dir": str(results_dir)},
        }
        config_file.write_text(yaml.dump(config_data))

        # Run experiment
        output_dir, _ = run_experiment(str(config_file))

        # Verify outputs
        output_path = Path(output_dir)
        assert output_path.exists()
        assert (output_path / "config.yaml").exists()
        assert (output_path / "config_hash.txt").exists()
        assert (output_path / "config_integrity.yaml").exists()
        assert (output_path / "env_fingerprint.yaml").exists()
        assert (output_path / "logs").exists()
        assert (output_path / "checkpoints").exists()
        assert (output_path / "training_complete.txt").exists()

        integrity = yaml.safe_load((output_path / "config_integrity.yaml").read_text())
        assert integrity["match"] is True
        assert integrity["source"] == "config.yaml"

    def test_seeds_set_before_training(self, tmp_path: Path) -> None:
        """Seeds are set before training script imports."""
        from marl_platform.orchestrator import run_experiment
        import random

        # Create directory structure
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

        # Create training script that captures random state
        training_script = training_dir / "train.py"
        training_script.write_text("""
import random
from pathlib import Path

def main(config, callbacks, output_dir):
    # Record random value (should be deterministic with seed=42)
    val = random.random()
    Path(output_dir).joinpath("random_value.txt").write_text(str(val))
""")

        # Create config with seed=42
        config_file = configs_dir / "seed_test.yaml"
        config_data = {
            "experiment": {"name": "seed_test", "seed": 42},
            "scenario": {"file": "scenarios/test.argos"},
            "training": {"script": "training/train.py"},
            "output": {"dir": str(results_dir)},
        }
        config_file.write_text(yaml.dump(config_data))

        # Run twice and compare
        output1, _ = run_experiment(str(config_file))
        val1 = Path(output1).joinpath("random_value.txt").read_text()

        output2, _ = run_experiment(str(config_file))
        val2 = Path(output2).joinpath("random_value.txt").read_text()

        # Same seed should produce same random value
        assert val1 == val2

    def test_config_integrity_recomputed_after_training(self, tmp_path: Path) -> None:
        """Runtime integrity artifact records start/end config hashes."""
        from marl_platform.orchestrator import run_experiment

        configs_dir = tmp_path / "experiments" / "configs"
        scenarios_dir = tmp_path / "experiments" / "scenarios"
        training_dir = tmp_path / "experiments" / "training"
        results_dir = tmp_path / "results"

        configs_dir.mkdir(parents=True)
        scenarios_dir.mkdir(parents=True)
        training_dir.mkdir(parents=True)
        results_dir.mkdir(parents=True)

        (scenarios_dir / "test.argos").write_text("<argos></argos>")
        (training_dir / "train.py").write_text("def main(config, callbacks, output_dir): pass")

        config_file = configs_dir / "integrity.yaml"
        config_file.write_text(
            yaml.dump(
                {
                    "experiment": {"name": "integrity", "seed": 42},
                    "scenario": {"file": "scenarios/test.argos"},
                    "training": {"script": "training/train.py", "tensorboard": False},
                    "output": {"dir": str(results_dir)},
                }
            )
        )

        output_dir, _ = run_experiment(str(config_file))
        output_dir = Path(output_dir)
        integrity = yaml.safe_load((output_dir / "config_integrity.yaml").read_text())

        assert integrity["match"] is True
        assert integrity["start_hash"] == integrity["end_hash"]

    def test_config_integrity_mismatch_fails_run(self, tmp_path: Path) -> None:
        """Run fails when the frozen config changes during execution."""
        from marl_platform.orchestrator import run_experiment
        from marl_platform.utils.errors import TrainingError

        configs_dir = tmp_path / "experiments" / "configs"
        scenarios_dir = tmp_path / "experiments" / "scenarios"
        training_dir = tmp_path / "experiments" / "training"
        results_dir = tmp_path / "results"

        configs_dir.mkdir(parents=True)
        scenarios_dir.mkdir(parents=True)
        training_dir.mkdir(parents=True)
        results_dir.mkdir(parents=True)

        (scenarios_dir / "test.argos").write_text("<argos></argos>")
        (training_dir / "train.py").write_text("""
from pathlib import Path

def main(config, callbacks, output_dir):
    config_path = Path(output_dir) / "config.yaml"
    config_path.write_text(config_path.read_text().replace("seed: 42", "seed: 43"))
""")

        config_file = configs_dir / "integrity_fail.yaml"
        config_file.write_text(
            yaml.dump(
                {
                    "experiment": {"name": "integrity_fail", "seed": 42},
                    "scenario": {"file": "scenarios/test.argos"},
                    "training": {"script": "training/train.py", "tensorboard": False},
                    "output": {"dir": str(results_dir)},
                }
            )
        )

        with pytest.raises(TrainingError) as exc_info:
            run_experiment(str(config_file))

        assert "frozen config changed" in exc_info.value.message.lower()

    def test_fingerprint_captured(self, tmp_path: Path) -> None:
        """Environment fingerprint is captured."""
        from marl_platform.orchestrator import run_experiment

        # Create directory structure
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

        config_file = configs_dir / "fp_test.yaml"
        config_data = {
            "experiment": {"name": "fp_test", "seed": 42},
            "scenario": {"file": "scenarios/test.argos"},
            "training": {"script": "training/train.py"},
            "output": {"dir": str(results_dir)},
        }
        config_file.write_text(yaml.dump(config_data))

        output_dir, _ = run_experiment(str(config_file))

        # Verify fingerprint
        fp_path = Path(output_dir) / "env_fingerprint.yaml"
        assert fp_path.exists()

        fp_content = yaml.safe_load(fp_path.read_text())
        assert "python" in fp_content
        assert "packages" in fp_content
