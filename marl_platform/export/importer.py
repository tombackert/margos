"""Import bundle unpacking and fingerprint comparison."""

import zipfile
from pathlib import Path
from typing import Callable

import yaml

from marl_platform.utils.errors import PlatformError
from marl_platform.utils.fingerprint import capture_fingerprint


class ImportError(PlatformError):
    """Raised when bundle import fails."""

    def __init__(self, message: str, context: dict | None = None, fix: str | None = None):
        super().__init__(
            message=message,
            context=context,
            fix=fix or "Check the bundle file is valid",
        )


def validate_bundle(bundle_path: Path) -> None:
    """Validate bundle structure.

    Args:
        bundle_path: Path to bundle ZIP file.

    Raises:
        ImportError: If bundle is invalid.
    """
    required_files = ["manifest.yaml", "config.yaml", "logs/metrics.jsonl"]

    try:
        with zipfile.ZipFile(bundle_path, "r") as zf:
            names = zf.namelist()
            for req_file in required_files:
                if req_file not in names:
                    raise ImportError(
                        message=f"Invalid bundle: missing {req_file}",
                        context={"Bundle": str(bundle_path)},
                        fix="Ensure the bundle was created with `platform export`",
                    )
    except zipfile.BadZipFile:
        raise ImportError(
            message="Invalid bundle: not a valid ZIP file",
            context={"Bundle": str(bundle_path)},
            fix="Check the bundle file is not corrupted",
        )


def import_bundle(
    bundle_path: str,
    target_dir: str | None = None,
    progress_callback: Callable[[int, int, str], None] | None = None,
) -> str:
    """Import bundle and prepare for reproduction.

    Args:
        bundle_path: Path to bundle ZIP file.
        target_dir: Optional target directory (default: experiments/imported/<name>/).
        progress_callback: Optional callback(current, total, description) for progress.

    Returns:
        Path to imported experiment directory.
    """
    bundle_path = Path(bundle_path)

    def update_progress(current: int, total: int, desc: str = "") -> None:
        if progress_callback:
            progress_callback(current, total, desc)

    if not bundle_path.exists():
        raise ImportError(
            message="Bundle file not found",
            context={"Path": str(bundle_path)},
            fix="Check the bundle path is correct",
        )

    update_progress(1, 4, "Validating bundle")

    # Validate bundle structure
    validate_bundle(bundle_path)

    update_progress(2, 4, "Reading manifest")

    # Determine target directory
    if target_dir is None:
        # Read manifest to get experiment name
        with zipfile.ZipFile(bundle_path, "r") as zf:
            manifest_data = zf.read("manifest.yaml")
            manifest = yaml.safe_load(manifest_data)
            exp_name = manifest.get("experiment_name", bundle_path.stem)

        target_dir = Path("experiments") / "imported" / exp_name
    else:
        target_dir = Path(target_dir)

    # Create target directory
    target_dir.mkdir(parents=True, exist_ok=True)

    update_progress(3, 4, "Extracting files")

    # Extract bundle
    with zipfile.ZipFile(bundle_path, "r") as zf:
        zf.extractall(target_dir)

    # Rewrite config paths to point to bundled files (relative to experiments_dir)
    # Runner computes experiments_dir = config.parent.parent, so paths must be
    # relative to target_dir.parent (i.e., prefixed with target_dir.name/)
    _rewrite_config_paths(target_dir)

    update_progress(4, 4, "Complete")

    return str(target_dir)


def _rewrite_config_paths(target_dir: Path) -> None:
    """Rewrite absolute paths in extracted config to use bundled files.

    After extraction, scenario.argos and train.py are at target_dir/.
    The runner resolves paths relative to config.parent.parent (= target_dir.parent),
    so we rewrite to '<target_dir.name>/scenario.argos' etc.

    Args:
        target_dir: Path to extracted experiment directory.
    """
    config_path = target_dir / "config.yaml"
    if not config_path.exists():
        return

    with open(config_path) as f:
        config = yaml.safe_load(f)

    if config is None:
        return

    prefix = target_dir.name
    modified = False

    # Rewrite scenario path if bundled scenario file exists
    scenario_section = config.get("scenario", {})
    if scenario_section and scenario_section.get("file"):
        # Find any scenario file in the extracted dir
        for candidate in target_dir.iterdir():
            if candidate.suffix in (".argos", ".xml") and candidate.is_file():
                config["scenario"]["file"] = f"{prefix}/{candidate.name}"
                modified = True
                break

    # Rewrite training script path if bundled train.py exists
    training_section = config.get("training", {})
    if training_section and training_section.get("script"):
        train_file = target_dir / "train.py"
        if train_file.exists():
            config["training"]["script"] = f"{prefix}/train.py"
            modified = True

    if modified:
        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def compare_fingerprints(bundle_fp: dict, current_fp: dict) -> dict:
    """Compare environment fingerprints.

    Args:
        bundle_fp: Fingerprint from the imported bundle.
        current_fp: Current environment fingerprint.

    Returns:
        Comparison dict with structure:
        {
            "python": (bundle_value, current_value, match),
            "os": (bundle_value, current_value, match),
            "packages": {pkg: (bundle_value, current_value, match), ...},
            "all_match": bool
        }
    """
    result = {}

    # Compare Python version
    bundle_python = bundle_fp.get("python", "unknown")
    current_python = current_fp.get("python", "unknown")
    result["python"] = (bundle_python, current_python, bundle_python == current_python)

    # Compare OS
    bundle_os = bundle_fp.get("os", "unknown")
    current_os = current_fp.get("os", "unknown")
    result["os"] = (bundle_os, current_os, bundle_os == current_os)

    # Compare packages
    bundle_pkgs = bundle_fp.get("packages", {})
    current_pkgs = current_fp.get("packages", {})
    all_pkgs = set(bundle_pkgs.keys()) | set(current_pkgs.keys())

    packages = {}
    all_packages_match = True
    for pkg in sorted(all_pkgs):
        bundle_ver = bundle_pkgs.get(pkg, "not installed")
        current_ver = current_pkgs.get(pkg, "not installed")
        match = bundle_ver == current_ver
        packages[pkg] = (bundle_ver, current_ver, match)
        if not match:
            all_packages_match = False

    result["packages"] = packages

    # Overall match
    result["all_match"] = (
        result["python"][2] and result["os"][2] and all_packages_match
    )

    return result


def get_bundle_fingerprint(imported_dir: str) -> dict | None:
    """Read fingerprint from imported bundle directory.

    Args:
        imported_dir: Path to imported experiment directory.

    Returns:
        Fingerprint dict or None if not found.
    """
    fp_path = Path(imported_dir) / "env_fingerprint.yaml"
    if not fp_path.exists():
        return None

    with open(fp_path) as f:
        return yaml.safe_load(f)


def format_fingerprint_comparison(comparison: dict) -> str:
    """Format fingerprint comparison for CLI display.

    Args:
        comparison: Result from compare_fingerprints().

    Returns:
        Formatted table string.
    """
    lines = [
        "",
        "Environment Comparison",
        "=" * 60,
    ]

    # Python version
    py_bundle, py_current, py_match = comparison["python"]
    status = "[OK]" if py_match else "[MISMATCH]"
    lines.append(f"Python:    {py_bundle:20} -> {py_current:20} {status}")

    # OS
    os_bundle, os_current, os_match = comparison["os"]
    status = "[OK]" if os_match else "[MISMATCH]"
    lines.append(f"OS:        {os_bundle:20} -> {os_current:20} {status}")

    # Packages
    lines.append("")
    lines.append("Packages:")
    lines.append("-" * 60)

    for pkg, (bundle_ver, current_ver, match) in comparison["packages"].items():
        status = "[OK]" if match else "[MISMATCH]"
        lines.append(f"  {pkg:15} {bundle_ver:15} -> {current_ver:15} {status}")

    # Summary
    lines.append("")
    if comparison["all_match"]:
        lines.append("All environments match.")
    else:
        lines.append("Warning: Environment differences detected. Results may vary.")

    return "\n".join(lines)
