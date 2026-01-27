"""Environment fingerprint capture for reproducibility tracking."""

import platform
from datetime import datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

import yaml

# Key packages to track for reproducibility
TRACKED_PACKAGES = [
    "ray",
    "torch",
    "numpy",
    "pydantic",
    "gymnasium",
    "pettingzoo",
]


def capture_fingerprint() -> dict[str, Any]:
    """Capture current environment metadata.

    Returns:
        Dict containing:
        - python: Python version
        - os: OS identifier
        - platform: Full platform string
        - packages: Dict of package versions
        - captured_at: ISO timestamp
    """
    packages = {}
    for pkg in TRACKED_PACKAGES:
        try:
            packages[pkg] = version(pkg)
        except PackageNotFoundError:
            packages[pkg] = "not installed"

    return {
        "python": platform.python_version(),
        "os": platform.system() + "-" + platform.release(),
        "platform": platform.platform(),
        "packages": packages,
        "captured_at": datetime.now().isoformat(timespec="seconds"),
    }


def save_fingerprint(fingerprint: dict[str, Any], output_dir: Path) -> Path:
    """Save fingerprint to YAML file in output directory.

    Args:
        fingerprint: The fingerprint dict to save.
        output_dir: Directory to save the fingerprint in.

    Returns:
        Path to the saved fingerprint file.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    fingerprint_path = output_dir / "env_fingerprint.yaml"

    with open(fingerprint_path, "w") as f:
        yaml.dump(fingerprint, f, default_flow_style=False, sort_keys=False)

    return fingerprint_path


def compare_fingerprints(
    current: dict[str, Any], reference: dict[str, Any]
) -> dict[str, Any]:
    """Compare two fingerprints and identify mismatches.

    Args:
        current: The current environment fingerprint.
        reference: The reference fingerprint to compare against.

    Returns:
        Dict containing:
        - python: {current, reference, match}
        - os: {current, reference, match}
        - packages: {pkg: {current, reference, match}, ...}
        - all_match: bool indicating if everything matches
    """
    python_match = current.get("python") == reference.get("python")
    os_match = current.get("os") == reference.get("os")

    packages_result: dict[str, dict[str, Any]] = {}
    all_packages_match = True

    # Compare packages
    current_pkgs: dict[str, str] = current.get("packages", {})
    reference_pkgs: dict[str, str] = reference.get("packages", {})

    # Get all package names from both fingerprints
    all_packages = set(current_pkgs.keys()) | set(reference_pkgs.keys())

    for pkg in all_packages:
        current_ver = current_pkgs.get(pkg, "not present")
        reference_ver = reference_pkgs.get(pkg, "not present")
        match = current_ver == reference_ver

        packages_result[pkg] = {
            "current": current_ver,
            "reference": reference_ver,
            "match": match,
        }

        if not match:
            all_packages_match = False

    return {
        "python": {
            "current": current.get("python"),
            "reference": reference.get("python"),
            "match": python_match,
        },
        "os": {
            "current": current.get("os"),
            "reference": reference.get("os"),
            "match": os_match,
        },
        "packages": packages_result,
        "all_match": python_match and os_match and all_packages_match,
    }
