"""Unit tests for export bundle module."""

import zipfile
from pathlib import Path

import pytest
import yaml

from marl_platform.export.bundle import BundleError, create_manifest, export_bundle

# Import helpers from conftest (pytest automatically loads conftest.py)
from tests.conftest import create_experiment_dir as create_minimal_experiment


class TestCreateManifest:
    """Tests for create_manifest function."""

    def test_includes_version(self, tmp_path: Path) -> None:
        """Manifest includes version field."""
        exp_dir = create_minimal_experiment(tmp_path / "exp")

        manifest = create_manifest(exp_dir)

        assert "version" in manifest
        assert manifest["version"] == "1.0"

    def test_includes_experiment_name(self, tmp_path: Path) -> None:
        """Manifest includes experiment name from directory."""
        exp_dir = create_minimal_experiment(tmp_path / "my_experiment_001")

        manifest = create_manifest(exp_dir)

        assert manifest["experiment_name"] == "my_experiment_001"

    def test_includes_export_timestamp(self, tmp_path: Path) -> None:
        """Manifest includes export timestamp in ISO format."""
        exp_dir = create_minimal_experiment(tmp_path / "exp")

        manifest = create_manifest(exp_dir)

        assert "exported_at" in manifest
        assert "T" in manifest["exported_at"]  # ISO format

    def test_includes_platform_version(self, tmp_path: Path) -> None:
        """Manifest includes platform version."""
        exp_dir = create_minimal_experiment(tmp_path / "exp")

        manifest = create_manifest(exp_dir)

        assert "platform_version" in manifest


class TestExportBundle:
    """Tests for export_bundle function."""

    def test_creates_zip_file(self, tmp_path: Path) -> None:
        """Creates a ZIP file at the specified path."""
        exp_dir = create_minimal_experiment(tmp_path / "exp")
        output_path = tmp_path / "bundles" / "test.zip"

        result = export_bundle(str(exp_dir), str(output_path))

        assert Path(result).exists()
        assert result == str(output_path)

    def test_creates_default_output_path(self, tmp_path: Path, monkeypatch) -> None:
        """Creates bundle in bundles/ directory by default."""
        monkeypatch.chdir(tmp_path)
        exp_dir = create_minimal_experiment(tmp_path / "my_exp_001")

        result = export_bundle(str(exp_dir))

        assert "bundles/my_exp_001.zip" in result
        assert Path(result).exists()

    def test_creates_bundles_directory(self, tmp_path: Path) -> None:
        """Creates bundles directory if it doesn't exist."""
        exp_dir = create_minimal_experiment(tmp_path / "exp")
        output_path = tmp_path / "new_bundles_dir" / "test.zip"

        export_bundle(str(exp_dir), str(output_path))

        assert output_path.parent.exists()

    def test_raises_error_for_missing_experiment(self, tmp_path: Path) -> None:
        """Raises BundleError when experiment directory doesn't exist."""
        with pytest.raises(BundleError) as exc_info:
            export_bundle(str(tmp_path / "nonexistent"), str(tmp_path / "out.zip"))

        assert "not found" in str(exc_info.value.message).lower()

    def test_raises_error_for_missing_config(self, tmp_path: Path) -> None:
        """Raises BundleError when config.yaml is missing."""
        exp_dir = tmp_path / "exp"
        exp_dir.mkdir()
        # Don't create config.yaml

        with pytest.raises(BundleError) as exc_info:
            export_bundle(str(exp_dir), str(tmp_path / "out.zip"))

        assert "config.yaml" in str(exc_info.value.message)

    def test_raises_error_for_missing_fingerprint(self, tmp_path: Path) -> None:
        """Raises BundleError when env_fingerprint.yaml is missing."""
        exp_dir = tmp_path / "exp"
        exp_dir.mkdir()
        (exp_dir / "config.yaml").write_text("experiment: {}")
        # Don't create env_fingerprint.yaml

        with pytest.raises(BundleError) as exc_info:
            export_bundle(str(exp_dir), str(tmp_path / "out.zip"))

        assert "env_fingerprint.yaml" in str(exc_info.value.message)

    def test_raises_error_for_missing_metrics(self, tmp_path: Path) -> None:
        """Raises BundleError when metrics.jsonl is missing."""
        exp_dir = tmp_path / "exp"
        exp_dir.mkdir()
        (exp_dir / "config.yaml").write_text("experiment: {}")
        (exp_dir / "env_fingerprint.yaml").write_text("python: 3.12")
        # Don't create logs/metrics.jsonl

        with pytest.raises(BundleError) as exc_info:
            export_bundle(str(exp_dir), str(tmp_path / "out.zip"))

        assert "metrics.jsonl" in str(exc_info.value.message)

    def test_bundle_contains_manifest(self, tmp_path: Path) -> None:
        """Bundle contains manifest.yaml."""
        exp_dir = create_minimal_experiment(tmp_path / "exp")
        output_path = tmp_path / "test.zip"

        export_bundle(str(exp_dir), str(output_path))

        with zipfile.ZipFile(output_path, "r") as zf:
            assert "manifest.yaml" in zf.namelist()
            manifest = yaml.safe_load(zf.read("manifest.yaml"))
            assert "version" in manifest
            assert "experiment_name" in manifest

    def test_bundle_contains_config(self, tmp_path: Path) -> None:
        """Bundle contains config.yaml."""
        exp_dir = create_minimal_experiment(tmp_path / "exp")
        output_path = tmp_path / "test.zip"

        export_bundle(str(exp_dir), str(output_path))

        with zipfile.ZipFile(output_path, "r") as zf:
            assert "config.yaml" in zf.namelist()

    def test_bundle_contains_fingerprint(self, tmp_path: Path) -> None:
        """Bundle contains env_fingerprint.yaml."""
        exp_dir = create_minimal_experiment(tmp_path / "exp")
        output_path = tmp_path / "test.zip"

        export_bundle(str(exp_dir), str(output_path))

        with zipfile.ZipFile(output_path, "r") as zf:
            assert "env_fingerprint.yaml" in zf.namelist()

    def test_bundle_contains_config_hash(self, tmp_path: Path) -> None:
        """Bundle contains config_hash.txt."""
        exp_dir = create_minimal_experiment(tmp_path / "exp")
        output_path = tmp_path / "test.zip"

        export_bundle(str(exp_dir), str(output_path))

        with zipfile.ZipFile(output_path, "r") as zf:
            assert "config_hash.txt" in zf.namelist()

    def test_bundle_contains_metrics(self, tmp_path: Path) -> None:
        """Bundle contains logs/metrics.jsonl."""
        exp_dir = create_minimal_experiment(tmp_path / "exp")
        output_path = tmp_path / "test.zip"

        export_bundle(str(exp_dir), str(output_path))

        with zipfile.ZipFile(output_path, "r") as zf:
            assert "logs/metrics.jsonl" in zf.namelist()

    def test_bundle_contains_scenario_file(self, tmp_path: Path) -> None:
        """Bundle contains scenario file when it exists."""
        scenario_path = tmp_path / "scenario.argos"
        scenario_path.write_text("<argos>test</argos>")
        exp_dir = create_minimal_experiment(tmp_path / "exp", scenario_path=scenario_path)
        output_path = tmp_path / "test.zip"

        export_bundle(str(exp_dir), str(output_path))

        with zipfile.ZipFile(output_path, "r") as zf:
            assert "scenario.argos" in zf.namelist()

    def test_bundle_contains_training_script(self, tmp_path: Path) -> None:
        """Bundle contains training script when it exists."""
        script_path = tmp_path / "train.py"
        script_path.write_text("def main(): pass")
        exp_dir = create_minimal_experiment(tmp_path / "exp", script_path=script_path)
        output_path = tmp_path / "test.zip"

        export_bundle(str(exp_dir), str(output_path))

        with zipfile.ZipFile(output_path, "r") as zf:
            assert "train.py" in zf.namelist()

    def test_bundle_contains_checkpoints(self, tmp_path: Path) -> None:
        """Bundle contains checkpoints directory when present."""
        exp_dir = create_minimal_experiment(tmp_path / "exp")
        # Create checkpoints
        checkpoint_dir = exp_dir / "checkpoints" / "checkpoint_001"
        checkpoint_dir.mkdir(parents=True)
        (checkpoint_dir / "model.pkl").write_bytes(b"model data")
        output_path = tmp_path / "test.zip"

        export_bundle(str(exp_dir), str(output_path))

        with zipfile.ZipFile(output_path, "r") as zf:
            names = zf.namelist()
            assert any("checkpoints/" in name for name in names)

    def test_bundle_is_valid_zip(self, tmp_path: Path) -> None:
        """Created bundle is a valid ZIP file."""
        exp_dir = create_minimal_experiment(tmp_path / "exp")
        output_path = tmp_path / "test.zip"

        export_bundle(str(exp_dir), str(output_path))

        assert zipfile.is_zipfile(output_path)

    def test_returns_output_path(self, tmp_path: Path) -> None:
        """Returns the path to the created bundle."""
        exp_dir = create_minimal_experiment(tmp_path / "exp")
        output_path = tmp_path / "test.zip"

        result = export_bundle(str(exp_dir), str(output_path))

        assert result == str(output_path)
