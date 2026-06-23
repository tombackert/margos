"""Unit tests for config module."""

import tempfile
from pathlib import Path

import pytest
import yaml

from margos.config import (
    MargosConfig,
    hash_config,
    load_config,
    resolve_paths,
    save_frozen_config,
)
from margos.utils.errors import ConfigNotFoundError, ValidationError


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_valid_config(self, tmp_path: Path) -> None:
        """Valid config loads successfully."""
        config_data = {
            "experiment": {"name": "test", "seed": 42},
            "scenario": {"file": "scenarios/test.argos"},
            "training": {"script": "training/test.py", "iterations": 10},
            "output": {"dir": "results/"},
        }
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        config = load_config(str(config_file))

        assert config.experiment.name == "test"
        assert config.experiment.seed == 42
        assert config.scenario.file == "scenarios/test.argos"
        assert config.training.script == "training/test.py"
        assert config.training.iterations == 10

    def test_load_config_with_defaults(self, tmp_path: Path) -> None:
        """Config loads with default values when optional fields omitted."""
        config_data = {
            "experiment": {"name": "test", "seed": 42},
            "scenario": {"file": "scenarios/test.argos"},
            "training": {"script": "training/test.py"},
        }
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        config = load_config(str(config_file))

        assert config.training.iterations == 100  # default
        assert config.output.dir == "results/"  # default

    def test_load_missing_config_raises_error(self) -> None:
        """Missing config file raises ConfigNotFoundError."""
        with pytest.raises(ConfigNotFoundError):
            load_config("/nonexistent/path/config.yaml")

    def test_load_missing_required_field_raises_error(self, tmp_path: Path) -> None:
        """Missing required field raises ValidationError."""
        config_data = {
            "experiment": {"name": "test"},  # missing seed
            "scenario": {"file": "scenarios/test.argos"},
            "training": {"script": "training/test.py"},
        }
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        with pytest.raises(ValidationError) as exc_info:
            load_config(str(config_file))

        assert "seed" in exc_info.value.context.get("Field", "")

    def test_load_invalid_seed_type_raises_error(self, tmp_path: Path) -> None:
        """Invalid seed type raises ValidationError."""
        config_data = {
            "experiment": {"name": "test", "seed": "not_a_number"},
            "scenario": {"file": "scenarios/test.argos"},
            "training": {"script": "training/test.py"},
        }
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        with pytest.raises(ValidationError):
            load_config(str(config_file))

    def test_load_negative_seed_raises_error(self, tmp_path: Path) -> None:
        """Negative seed raises ValidationError."""
        config_data = {
            "experiment": {"name": "test", "seed": -1},
            "scenario": {"file": "scenarios/test.argos"},
            "training": {"script": "training/test.py"},
        }
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        with pytest.raises(ValidationError):
            load_config(str(config_file))

    def test_load_empty_config_raises_error(self, tmp_path: Path) -> None:
        """Empty config file raises ValidationError."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("")

        with pytest.raises(ValidationError) as exc_info:
            load_config(str(config_file))

        assert "Empty config" in exc_info.value.message

    def test_load_invalid_yaml_raises_error(self, tmp_path: Path) -> None:
        """Invalid YAML syntax raises ValidationError."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("invalid: yaml: syntax: [")

        with pytest.raises(ValidationError) as exc_info:
            load_config(str(config_file))

        assert "YAML" in exc_info.value.message


class TestResolvePaths:
    """Tests for resolve_paths function."""

    def test_resolve_paths_success(self, tmp_path: Path) -> None:
        """Paths resolve correctly when files exist."""
        # Create test files
        scenarios_dir = tmp_path / "scenarios"
        scenarios_dir.mkdir()
        (scenarios_dir / "test.argos").touch()

        training_dir = tmp_path / "training"
        training_dir.mkdir()
        (training_dir / "test.py").touch()

        config = MargosConfig(
            experiment={"name": "test", "seed": 42},
            scenario={"file": "scenarios/test.argos"},
            training={"script": "training/test.py"},
        )

        resolved = resolve_paths(config, tmp_path)

        assert Path(resolved.scenario.file).is_absolute()
        assert Path(resolved.training.script).is_absolute()
        assert str(tmp_path) in resolved.scenario.file
        assert str(tmp_path) in resolved.training.script

    def test_resolve_missing_scenario_raises_error(self, tmp_path: Path) -> None:
        """Missing scenario file raises ValidationError."""
        training_dir = tmp_path / "training"
        training_dir.mkdir()
        (training_dir / "test.py").touch()

        config = MargosConfig(
            experiment={"name": "test", "seed": 42},
            scenario={"file": "scenarios/nonexistent.argos"},
            training={"script": "training/test.py"},
        )

        with pytest.raises(ValidationError) as exc_info:
            resolve_paths(config, tmp_path)

        assert "Scenario file not found" in exc_info.value.message

    def test_resolve_missing_script_raises_error(self, tmp_path: Path) -> None:
        """Missing training script raises ValidationError."""
        scenarios_dir = tmp_path / "scenarios"
        scenarios_dir.mkdir()
        (scenarios_dir / "test.argos").touch()

        config = MargosConfig(
            experiment={"name": "test", "seed": 42},
            scenario={"file": "scenarios/test.argos"},
            training={"script": "training/nonexistent.py"},
        )

        with pytest.raises(ValidationError) as exc_info:
            resolve_paths(config, tmp_path)

        assert "Training script not found" in exc_info.value.message


class TestHashConfig:
    """Tests for hash_config function."""

    def test_hash_is_deterministic(self) -> None:
        """Same config produces same hash."""
        config = MargosConfig(
            experiment={"name": "test", "seed": 42},
            scenario={"file": "scenarios/test.argos"},
            training={"script": "training/test.py"},
        )

        hash1 = hash_config(config)
        hash2 = hash_config(config)

        assert hash1 == hash2

    def test_hash_changes_with_config(self) -> None:
        """Different config produces different hash."""
        config1 = MargosConfig(
            experiment={"name": "test", "seed": 42},
            scenario={"file": "scenarios/test.argos"},
            training={"script": "training/test.py"},
        )

        config2 = MargosConfig(
            experiment={"name": "test", "seed": 43},  # different seed
            scenario={"file": "scenarios/test.argos"},
            training={"script": "training/test.py"},
        )

        assert hash_config(config1) != hash_config(config2)

    def test_hash_is_sha256(self) -> None:
        """Hash is a valid SHA256 hex string."""
        config = MargosConfig(
            experiment={"name": "test", "seed": 42},
            scenario={"file": "scenarios/test.argos"},
            training={"script": "training/test.py"},
        )

        config_hash = hash_config(config)

        assert len(config_hash) == 64  # SHA256 hex length
        assert all(c in "0123456789abcdef" for c in config_hash)


class TestSaveFrozenConfig:
    """Tests for save_frozen_config function."""

    def test_save_creates_file(self, tmp_path: Path) -> None:
        """Frozen config is saved to file."""
        config = MargosConfig(
            experiment={"name": "test", "seed": 42},
            scenario={"file": "scenarios/test.argos"},
            training={"script": "training/test.py"},
        )

        output_dir = tmp_path / "output"
        saved_path = save_frozen_config(config, output_dir)

        assert saved_path.exists()
        assert saved_path.name == "config.yaml"

    def test_save_creates_output_dir(self, tmp_path: Path) -> None:
        """Output directory is created if it doesn't exist."""
        config = MargosConfig(
            experiment={"name": "test", "seed": 42},
            scenario={"file": "scenarios/test.argos"},
            training={"script": "training/test.py"},
        )

        output_dir = tmp_path / "nested" / "output"
        save_frozen_config(config, output_dir)

        assert output_dir.exists()

    def test_saved_config_is_valid_yaml(self, tmp_path: Path) -> None:
        """Saved config can be loaded back."""
        config = MargosConfig(
            experiment={"name": "test", "seed": 42},
            scenario={"file": "scenarios/test.argos"},
            training={"script": "training/test.py", "iterations": 50},
        )

        saved_path = save_frozen_config(config, tmp_path)

        with open(saved_path) as f:
            loaded = yaml.safe_load(f)

        assert loaded["experiment"]["name"] == "test"
        assert loaded["experiment"]["seed"] == 42
        assert loaded["training"]["iterations"] == 50
