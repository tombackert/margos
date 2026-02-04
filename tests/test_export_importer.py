"""Unit tests for export importer module."""

import zipfile
from pathlib import Path

import pytest
import yaml

from marl_platform.export.importer import (
    ImportError,
    compare_fingerprints,
    format_fingerprint_comparison,
    get_bundle_fingerprint,
    import_bundle,
    validate_bundle,
)

# Import helpers from conftest (pytest automatically loads conftest.py)
from tests.conftest import create_valid_bundle


class TestValidateBundle:
    """Tests for validate_bundle function."""

    def test_valid_bundle_passes(self, tmp_path: Path) -> None:
        """Valid bundle passes validation."""
        bundle_path = create_valid_bundle(tmp_path)

        # Should not raise
        validate_bundle(bundle_path)

    def test_missing_manifest_fails(self, tmp_path: Path) -> None:
        """Bundle without manifest.yaml fails validation."""
        bundle_path = tmp_path / "invalid.zip"
        with zipfile.ZipFile(bundle_path, "w") as zf:
            zf.writestr("config.yaml", "test: true")
            zf.writestr("logs/metrics.jsonl", '{"iteration": 1}')

        with pytest.raises(ImportError) as exc_info:
            validate_bundle(bundle_path)

        assert "manifest.yaml" in str(exc_info.value.message)

    def test_missing_config_fails(self, tmp_path: Path) -> None:
        """Bundle without config.yaml fails validation."""
        bundle_path = tmp_path / "invalid.zip"
        with zipfile.ZipFile(bundle_path, "w") as zf:
            zf.writestr("manifest.yaml", "version: 1.0")
            zf.writestr("logs/metrics.jsonl", '{"iteration": 1}')

        with pytest.raises(ImportError) as exc_info:
            validate_bundle(bundle_path)

        assert "config.yaml" in str(exc_info.value.message)

    def test_missing_metrics_fails(self, tmp_path: Path) -> None:
        """Bundle without logs/metrics.jsonl fails validation."""
        bundle_path = tmp_path / "invalid.zip"
        with zipfile.ZipFile(bundle_path, "w") as zf:
            zf.writestr("manifest.yaml", "version: 1.0")
            zf.writestr("config.yaml", "test: true")

        with pytest.raises(ImportError) as exc_info:
            validate_bundle(bundle_path)

        assert "metrics.jsonl" in str(exc_info.value.message)

    def test_invalid_zip_fails(self, tmp_path: Path) -> None:
        """Invalid ZIP file fails validation."""
        bundle_path = tmp_path / "not_a_zip.zip"
        bundle_path.write_text("This is not a ZIP file")

        with pytest.raises(ImportError) as exc_info:
            validate_bundle(bundle_path)

        assert "not a valid ZIP" in str(exc_info.value.message)


class TestImportBundle:
    """Tests for import_bundle function."""

    def test_extracts_to_imported_directory(self, tmp_path: Path, monkeypatch) -> None:
        """Extracts bundle to experiments/imported/<name>/."""
        monkeypatch.chdir(tmp_path)
        bundle_path = create_valid_bundle(tmp_path, exp_name="my_experiment")

        result = import_bundle(str(bundle_path))

        assert "experiments/imported/my_experiment" in result
        assert Path(result).exists()

    def test_extracts_all_files(self, tmp_path: Path, monkeypatch) -> None:
        """Extracts all files from bundle."""
        monkeypatch.chdir(tmp_path)
        bundle_path = create_valid_bundle(tmp_path)

        result = import_bundle(str(bundle_path))

        imported_path = Path(result)
        assert (imported_path / "manifest.yaml").exists()
        assert (imported_path / "config.yaml").exists()
        assert (imported_path / "env_fingerprint.yaml").exists()
        assert (imported_path / "logs" / "metrics.jsonl").exists()

    def test_custom_target_directory(self, tmp_path: Path) -> None:
        """Supports custom target directory."""
        bundle_path = create_valid_bundle(tmp_path)
        target_dir = tmp_path / "custom" / "location"

        result = import_bundle(str(bundle_path), str(target_dir))

        assert result == str(target_dir)
        assert target_dir.exists()
        assert (target_dir / "manifest.yaml").exists()

    def test_raises_error_for_missing_bundle(self, tmp_path: Path) -> None:
        """Raises ImportError when bundle doesn't exist."""
        with pytest.raises(ImportError) as exc_info:
            import_bundle(str(tmp_path / "nonexistent.zip"))

        assert "not found" in str(exc_info.value.message).lower()

    def test_raises_error_for_invalid_bundle(self, tmp_path: Path, monkeypatch) -> None:
        """Raises ImportError for invalid bundle structure."""
        monkeypatch.chdir(tmp_path)
        bundle_path = tmp_path / "invalid.zip"
        with zipfile.ZipFile(bundle_path, "w") as zf:
            zf.writestr("random.txt", "not a valid bundle")

        with pytest.raises(ImportError):
            import_bundle(str(bundle_path))

    def test_returns_imported_path(self, tmp_path: Path, monkeypatch) -> None:
        """Returns path to imported experiment directory."""
        monkeypatch.chdir(tmp_path)
        bundle_path = create_valid_bundle(tmp_path, exp_name="test123")

        result = import_bundle(str(bundle_path))

        assert "test123" in result
        assert isinstance(result, str)

    def test_creates_target_directory(self, tmp_path: Path) -> None:
        """Creates target directory if it doesn't exist."""
        bundle_path = create_valid_bundle(tmp_path)
        target_dir = tmp_path / "deep" / "nested" / "path"

        import_bundle(str(bundle_path), str(target_dir))

        assert target_dir.exists()


class TestCompareFingerprints:
    """Tests for compare_fingerprints function."""

    def test_identical_fingerprints_all_match(self) -> None:
        """Identical fingerprints show all matches."""
        fp = {
            "python": "3.12.0",
            "os": "Linux-5.10.0",
            "packages": {"ray": "2.0.0", "torch": "2.0.0"},
        }

        result = compare_fingerprints(fp, fp)

        assert result["all_match"] is True
        assert result["python"][2] is True  # match flag
        assert result["os"][2] is True

    def test_different_python_version(self) -> None:
        """Detects different Python versions."""
        bundle_fp = {"python": "3.11.0", "os": "Linux", "packages": {}}
        current_fp = {"python": "3.12.0", "os": "Linux", "packages": {}}

        result = compare_fingerprints(bundle_fp, current_fp)

        assert result["python"] == ("3.11.0", "3.12.0", False)
        assert result["all_match"] is False

    def test_different_os(self) -> None:
        """Detects different OS."""
        bundle_fp = {"python": "3.12.0", "os": "Linux-5.10.0", "packages": {}}
        current_fp = {"python": "3.12.0", "os": "Darwin-21.0.0", "packages": {}}

        result = compare_fingerprints(bundle_fp, current_fp)

        assert result["os"][2] is False
        assert result["all_match"] is False

    def test_different_package_versions(self) -> None:
        """Detects different package versions."""
        bundle_fp = {
            "python": "3.12.0",
            "os": "Linux",
            "packages": {"ray": "2.0.0", "torch": "2.0.0"},
        }
        current_fp = {
            "python": "3.12.0",
            "os": "Linux",
            "packages": {"ray": "2.1.0", "torch": "2.0.0"},
        }

        result = compare_fingerprints(bundle_fp, current_fp)

        assert result["packages"]["ray"] == ("2.0.0", "2.1.0", False)
        assert result["packages"]["torch"][2] is True
        assert result["all_match"] is False

    def test_missing_package_in_current(self) -> None:
        """Handles package missing in current environment."""
        bundle_fp = {
            "python": "3.12.0",
            "os": "Linux",
            "packages": {"ray": "2.0.0", "special": "1.0.0"},
        }
        current_fp = {
            "python": "3.12.0",
            "os": "Linux",
            "packages": {"ray": "2.0.0"},
        }

        result = compare_fingerprints(bundle_fp, current_fp)

        assert result["packages"]["special"] == ("1.0.0", "not installed", False)
        assert result["all_match"] is False

    def test_extra_package_in_current(self) -> None:
        """Handles extra package in current environment."""
        bundle_fp = {
            "python": "3.12.0",
            "os": "Linux",
            "packages": {"ray": "2.0.0"},
        }
        current_fp = {
            "python": "3.12.0",
            "os": "Linux",
            "packages": {"ray": "2.0.0", "extra": "1.0.0"},
        }

        result = compare_fingerprints(bundle_fp, current_fp)

        assert result["packages"]["extra"] == ("not installed", "1.0.0", False)

    def test_returns_expected_structure(self) -> None:
        """Returns dict with expected structure."""
        fp = {"python": "3.12.0", "os": "Linux", "packages": {"ray": "2.0.0"}}

        result = compare_fingerprints(fp, fp)

        assert "python" in result
        assert "os" in result
        assert "packages" in result
        assert "all_match" in result
        assert len(result["python"]) == 3  # (bundle, current, match)

    def test_handles_empty_packages(self) -> None:
        """Handles fingerprints with no packages."""
        fp = {"python": "3.12.0", "os": "Linux", "packages": {}}

        result = compare_fingerprints(fp, fp)

        assert result["all_match"] is True
        assert result["packages"] == {}


class TestGetBundleFingerprint:
    """Tests for get_bundle_fingerprint function."""

    def test_reads_fingerprint_from_imported_dir(self, tmp_path: Path) -> None:
        """Reads fingerprint from imported experiment directory."""
        imported_dir = tmp_path / "imported_exp"
        imported_dir.mkdir()
        fingerprint = {"python": "3.12.0", "os": "Linux", "packages": {}}
        (imported_dir / "env_fingerprint.yaml").write_text(yaml.dump(fingerprint))

        result = get_bundle_fingerprint(str(imported_dir))

        assert result is not None
        assert result["python"] == "3.12.0"

    def test_returns_none_for_missing_fingerprint(self, tmp_path: Path) -> None:
        """Returns None when fingerprint file doesn't exist."""
        imported_dir = tmp_path / "imported_exp"
        imported_dir.mkdir()
        # Don't create env_fingerprint.yaml

        result = get_bundle_fingerprint(str(imported_dir))

        assert result is None


class TestFormatFingerprintComparison:
    """Tests for format_fingerprint_comparison function."""

    def test_formats_matching_fingerprints(self) -> None:
        """Formats all-matching comparison."""
        comparison = {
            "python": ("3.12.0", "3.12.0", True),
            "os": ("Linux", "Linux", True),
            "packages": {"ray": ("2.0.0", "2.0.0", True)},
            "all_match": True,
        }

        result = format_fingerprint_comparison(comparison)

        assert "[OK]" in result
        assert "All environments match" in result

    def test_formats_mismatched_fingerprints(self) -> None:
        """Formats comparison with mismatches."""
        comparison = {
            "python": ("3.11.0", "3.12.0", False),
            "os": ("Linux", "Linux", True),
            "packages": {"ray": ("2.0.0", "2.1.0", False)},
            "all_match": False,
        }

        result = format_fingerprint_comparison(comparison)

        assert "[MISMATCH]" in result
        assert "Warning" in result or "differences" in result.lower()

    def test_includes_python_version(self) -> None:
        """Output includes Python version comparison."""
        comparison = {
            "python": ("3.11.0", "3.12.0", False),
            "os": ("Linux", "Linux", True),
            "packages": {},
            "all_match": False,
        }

        result = format_fingerprint_comparison(comparison)

        assert "Python" in result
        assert "3.11.0" in result
        assert "3.12.0" in result

    def test_includes_os_comparison(self) -> None:
        """Output includes OS comparison."""
        comparison = {
            "python": ("3.12.0", "3.12.0", True),
            "os": ("Linux-5.10", "Darwin-21.0", False),
            "packages": {},
            "all_match": False,
        }

        result = format_fingerprint_comparison(comparison)

        assert "OS" in result
        assert "Linux" in result
        assert "Darwin" in result

    def test_includes_package_comparison(self) -> None:
        """Output includes package version comparison."""
        comparison = {
            "python": ("3.12.0", "3.12.0", True),
            "os": ("Linux", "Linux", True),
            "packages": {
                "ray": ("2.0.0", "2.0.0", True),
                "torch": ("2.0.0", "2.1.0", False),
            },
            "all_match": False,
        }

        result = format_fingerprint_comparison(comparison)

        assert "Packages" in result
        assert "ray" in result
        assert "torch" in result

    def test_output_is_readable(self) -> None:
        """Output is formatted for terminal display."""
        comparison = {
            "python": ("3.12.0", "3.12.0", True),
            "os": ("Linux", "Linux", True),
            "packages": {"ray": ("2.0.0", "2.0.0", True)},
            "all_match": True,
        }

        result = format_fingerprint_comparison(comparison)

        # Should have multiple lines
        assert "\n" in result
        # Should have some structure
        assert "=" in result or "-" in result
