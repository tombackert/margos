"""Export bundle creation."""

import zipfile
from datetime import datetime
from pathlib import Path
from typing import Callable

import yaml

from margos.utils.errors import MargosError


class BundleError(MargosError):
    """Raised when bundle creation fails."""

    def __init__(self, message: str, context: dict | None = None, fix: str | None = None):
        super().__init__(
            message=message,
            context=context,
            fix=fix or "Check the experiment directory structure",
        )


def create_manifest(experiment_dir: Path) -> dict:
    """Create bundle manifest with metadata.

    Args:
        experiment_dir: Path to experiment results directory.

    Returns:
        Manifest dict with bundle metadata.
    """
    return {
        "version": "1.0",
        "experiment_name": experiment_dir.name,
        "exported_at": datetime.now().isoformat(timespec="seconds"),
        "margos_version": "0.1.0",
    }


def export_bundle(
    experiment_dir: str,
    output_path: str | None = None,
    progress_callback: Callable[[int, int, str], None] | None = None,
) -> str:
    """Create shareable bundle from experiment.

    Args:
        experiment_dir: Path to experiment results directory.
        output_path: Path for output bundle file (default: bundles/<exp_name>.zip).
        progress_callback: Optional callback(current, total, description) for progress.

    Returns:
        Path to created bundle.
    """
    exp_path = Path(experiment_dir)

    def update_progress(current: int, total: int, desc: str = "") -> None:
        if progress_callback:
            progress_callback(current, total, desc)

    if not exp_path.exists():
        raise BundleError(
            message="Experiment directory not found",
            context={"Path": str(exp_path)},
            fix="Check the experiment ID or path",
        )

    # Determine output path
    if output_path is None:
        bundles_dir = Path("bundles")
        output_path = str(bundles_dir / f"{exp_path.name}.zip")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Required files
    required_files = [
        "config.yaml",
        "env_fingerprint.yaml",
        "logs/metrics.jsonl",
    ]

    update_progress(1, 6, "Validating files")

    # Check required files exist
    for req_file in required_files:
        file_path = exp_path / req_file
        if not file_path.exists():
            raise BundleError(
                message=f"Required file missing: {req_file}",
                context={"Experiment": str(exp_path)},
                fix="Ensure the experiment completed successfully",
            )

    # Read config to get source file paths
    config_path = exp_path / "config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)

    update_progress(2, 6, "Creating manifest")

    # Create bundle ZIP
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add manifest
        manifest = create_manifest(exp_path)
        zf.writestr("manifest.yaml", yaml.dump(manifest, default_flow_style=False))

        update_progress(3, 6, "Adding config files")

        # Add config
        zf.write(config_path, "config.yaml")

        # Add env fingerprint
        zf.write(exp_path / "env_fingerprint.yaml", "env_fingerprint.yaml")

        # Add config hash if present
        config_hash_path = exp_path / "config_hash.txt"
        if config_hash_path.exists():
            zf.write(config_hash_path, "config_hash.txt")

        config_integrity_path = exp_path / "config_integrity.yaml"
        if config_integrity_path.exists():
            zf.write(config_integrity_path, "config_integrity.yaml")

        update_progress(4, 6, "Adding logs")

        # Add logs directory
        logs_dir = exp_path / "logs"
        if logs_dir.exists():
            for log_file in logs_dir.iterdir():
                if log_file.is_file():
                    zf.write(log_file, f"logs/{log_file.name}")

        # Add scenario file if it exists
        scenario_path = config.get("scenario", {}).get("file")
        if scenario_path:
            scenario_path = Path(scenario_path)
            if scenario_path.exists():
                zf.write(scenario_path, f"scenario{scenario_path.suffix}")

        # Add training script if it exists
        train_script = config.get("training", {}).get("script")
        if train_script:
            train_path = Path(train_script)
            if train_path.exists():
                zf.write(train_path, "train.py")

        update_progress(5, 6, "Adding checkpoints")

        # Add checkpoints directory (included by default per L5)
        checkpoints_dir = exp_path / "checkpoints"
        if checkpoints_dir.exists():
            for item in checkpoints_dir.rglob("*"):
                if item.is_file():
                    arcname = f"checkpoints/{item.relative_to(checkpoints_dir)}"
                    zf.write(item, arcname)

    update_progress(6, 6, "Complete")

    return str(output_path)
