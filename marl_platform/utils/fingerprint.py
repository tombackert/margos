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
