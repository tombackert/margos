"""Environment fingerprint capture for reproducibility tracking."""

import hashlib
import platform
import subprocess
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
    "pyzmq",
    "tensorboard",
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

    runtime = {
        "machine": platform.machine(),
        "processor": platform.processor() or "unknown",
        "gpu": _detect_gpu(),
        "argos": _detect_argos_version(),
    }
    build = {
        "git_commit": _detect_git_commit(),
        "controller_plugin": _fingerprint_file(_repo_root() / "argos_plugins/build/controllers/libmy_ipc_controller.dylib"),
        "loop_plugin": _fingerprint_file(_repo_root() / "argos_plugins/build/loop_functions/libzoo_loop_functions.dylib"),
    }

    return {
        "python": platform.python_version(),
        "os": platform.system() + "-" + platform.release(),
        "platform": platform.platform(),
        "packages": packages,
        "runtime": runtime,
        "build": build,
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


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def _detect_argos_version() -> str:
    try:
        result = subprocess.run(
            ["argos3", "-v"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
    except (FileNotFoundError, subprocess.SubprocessError, OSError):
        return "not installed"

    output = (result.stdout or result.stderr or "").strip()
    return output or "unknown"


def _detect_git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=_repo_root(),
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
    except (FileNotFoundError, subprocess.SubprocessError, OSError):
        return "unknown"

    commit = (result.stdout or "").strip()
    return commit or "unknown"


def _detect_gpu() -> str:
    try:
        import torch
    except Exception:
        return "unknown"

    try:
        return "available" if torch.cuda.is_available() else "not available"
    except Exception:
        return "unknown"


def _fingerprint_file(path: Path) -> str:
    if not path.exists():
        return "missing"

    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return f"sha256:{digest[:16]}"
