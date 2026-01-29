"""Unit tests for environment fingerprint module."""

from pathlib import Path

import yaml

from marl_platform.utils.fingerprint import (
    capture_fingerprint,
    compare_fingerprints,
    save_fingerprint,
)


class TestCaptureFingerprint:
    """Tests for capture_fingerprint function."""

    def test_returns_expected_structure(self) -> None:
        """Fingerprint contains all expected keys."""
        fp = capture_fingerprint()

        assert "python" in fp
        assert "os" in fp
        assert "platform" in fp
        assert "packages" in fp
        assert "captured_at" in fp

    def test_python_version_format(self) -> None:
        """Python version is a valid version string."""
        fp = capture_fingerprint()

        # Should be like "3.10.0" or "3.12.8"
        parts = fp["python"].split(".")
        assert len(parts) >= 2
        assert all(p.isdigit() for p in parts[:2])

    def test_os_is_string(self) -> None:
        """OS is a non-empty string."""
        fp = capture_fingerprint()

        assert isinstance(fp["os"], str)
        assert len(fp["os"]) > 0

    def test_packages_is_dict(self) -> None:
        """Packages is a dictionary."""
        fp = capture_fingerprint()

        assert isinstance(fp["packages"], dict)

    def test_tracked_packages_present(self) -> None:
        """All tracked packages have entries (installed or not)."""
        fp = capture_fingerprint()

        # These are the packages we track
        expected_packages = ["ray", "torch", "numpy", "pydantic", "gymnasium", "pettingzoo"]
        for pkg in expected_packages:
            assert pkg in fp["packages"]

    def test_installed_package_has_version(self) -> None:
        """Installed packages have version strings."""
        fp = capture_fingerprint()

        # pydantic should definitely be installed (it's a core dependency)
        assert fp["packages"]["pydantic"] != "not installed"
        # Version should be like "2.0.0"
        assert "." in fp["packages"]["pydantic"]

    def test_captured_at_is_iso_format(self) -> None:
        """Timestamp is in ISO format."""
        fp = capture_fingerprint()

        # Should be like "2024-01-15T14:30:22"
        assert "T" in fp["captured_at"]
        assert "-" in fp["captured_at"]
        assert ":" in fp["captured_at"]


class TestSaveFingerprint:
    """Tests for save_fingerprint function."""

    def test_creates_file(self, tmp_path: Path) -> None:
        """Saves fingerprint to file."""
        fp = capture_fingerprint()

        saved_path = save_fingerprint(fp, tmp_path)

        assert saved_path.exists()
        assert saved_path.name == "env_fingerprint.yaml"

    def test_creates_output_dir(self, tmp_path: Path) -> None:
        """Creates output directory if needed."""
        fp = capture_fingerprint()

        output_dir = tmp_path / "nested" / "output"
        save_fingerprint(fp, output_dir)

        assert output_dir.exists()

    def test_saved_file_is_valid_yaml(self, tmp_path: Path) -> None:
        """Saved file contains valid YAML."""
        fp = capture_fingerprint()

        saved_path = save_fingerprint(fp, tmp_path)

        with open(saved_path) as f:
            loaded = yaml.safe_load(f)

        assert loaded["python"] == fp["python"]
        assert loaded["os"] == fp["os"]
        assert loaded["packages"] == fp["packages"]

    def test_roundtrip_preserves_data(self, tmp_path: Path) -> None:
        """Save and load preserves all data."""
        fp = capture_fingerprint()

        saved_path = save_fingerprint(fp, tmp_path)

        with open(saved_path) as f:
            loaded = yaml.safe_load(f)

        # All keys should match
        assert set(loaded.keys()) == set(fp.keys())
        assert loaded["packages"] == fp["packages"]


class TestCompareFingerprints:
    """Tests for compare_fingerprints function."""

    def test_identical_fingerprints_match(self) -> None:
        """Identical fingerprints report all_match=True."""
        fp1 = {
            "python": "3.10.0",
            "os": "Darwin-23.0.0",
            "packages": {"torch": "2.0.0", "numpy": "1.24.0"},
        }
        fp2 = {
            "python": "3.10.0",
            "os": "Darwin-23.0.0",
            "packages": {"torch": "2.0.0", "numpy": "1.24.0"},
        }

        result = compare_fingerprints(fp1, fp2)

        assert result["all_match"] is True
        assert result["python"]["match"] is True
        assert result["os"]["match"] is True

    def test_different_python_version_mismatch(self) -> None:
        """Different Python versions report mismatch."""
        fp1 = {"python": "3.10.0", "os": "Darwin", "packages": {}}
        fp2 = {"python": "3.11.0", "os": "Darwin", "packages": {}}

        result = compare_fingerprints(fp1, fp2)

        assert result["all_match"] is False
        assert result["python"]["match"] is False
        assert result["python"]["current"] == "3.10.0"
        assert result["python"]["reference"] == "3.11.0"

    def test_different_package_version_mismatch(self) -> None:
        """Different package versions report mismatch."""
        fp1 = {"python": "3.10.0", "os": "Darwin", "packages": {"torch": "2.0.0"}}
        fp2 = {"python": "3.10.0", "os": "Darwin", "packages": {"torch": "2.0.1"}}

        result = compare_fingerprints(fp1, fp2)

        assert result["all_match"] is False
        assert result["packages"]["torch"]["match"] is False
        assert result["packages"]["torch"]["current"] == "2.0.0"
        assert result["packages"]["torch"]["reference"] == "2.0.1"

    def test_missing_package_in_current(self) -> None:
        """Missing package in current is detected."""
        fp1 = {"python": "3.10.0", "os": "Darwin", "packages": {}}
        fp2 = {"python": "3.10.0", "os": "Darwin", "packages": {"torch": "2.0.0"}}

        result = compare_fingerprints(fp1, fp2)

        assert result["all_match"] is False
        assert result["packages"]["torch"]["current"] == "not present"
        assert result["packages"]["torch"]["reference"] == "2.0.0"

    def test_missing_package_in_reference(self) -> None:
        """Missing package in reference is detected."""
        fp1 = {"python": "3.10.0", "os": "Darwin", "packages": {"torch": "2.0.0"}}
        fp2 = {"python": "3.10.0", "os": "Darwin", "packages": {}}

        result = compare_fingerprints(fp1, fp2)

        assert result["all_match"] is False
        assert result["packages"]["torch"]["current"] == "2.0.0"
        assert result["packages"]["torch"]["reference"] == "not present"

    def test_not_installed_matches_not_installed(self) -> None:
        """Both 'not installed' counts as match."""
        fp1 = {"python": "3.10.0", "os": "Darwin", "packages": {"torch": "not installed"}}
        fp2 = {"python": "3.10.0", "os": "Darwin", "packages": {"torch": "not installed"}}

        result = compare_fingerprints(fp1, fp2)

        assert result["packages"]["torch"]["match"] is True

    def test_multiple_mismatches_detected(self) -> None:
        """Multiple mismatches are all reported."""
        fp1 = {
            "python": "3.10.0",
            "os": "Darwin",
            "packages": {"torch": "2.0.0", "numpy": "1.24.0"},
        }
        fp2 = {
            "python": "3.11.0",
            "os": "Linux",
            "packages": {"torch": "2.1.0", "numpy": "1.25.0"},
        }

        result = compare_fingerprints(fp1, fp2)

        assert result["all_match"] is False
        assert result["python"]["match"] is False
        assert result["os"]["match"] is False
        assert result["packages"]["torch"]["match"] is False
        assert result["packages"]["numpy"]["match"] is False
