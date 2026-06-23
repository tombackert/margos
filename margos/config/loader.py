"""Config loading, validation, and hashing utilities."""

import hashlib
import json
from pathlib import Path
from typing import Literal

import yaml
from pydantic import ValidationError as PydanticValidationError

from margos.utils.errors import ConfigNotFoundError, ValidationError

from .schema import MargosConfig


def load_config(path: str) -> MargosConfig:
    """Load and validate config from YAML file.

    Args:
        path: Path to the YAML config file.

    Returns:
        Validated MargosConfig object.

    Raises:
        ConfigNotFoundError: Config file doesn't exist.
        ValidationError: Config fails schema validation.
    """
    config_path = Path(path)

    if not config_path.exists():
        raise ConfigNotFoundError(str(config_path))

    try:
        with open(config_path) as f:
            raw_config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValidationError(
            message="Invalid YAML syntax",
            context={"Path": str(config_path), "Error": str(e)},
            fix="Check the YAML file for syntax errors",
        )

    if raw_config is None:
        raise ValidationError(
            message="Empty config file",
            context={"Path": str(config_path)},
            fix="Add experiment configuration to the file",
        )

    try:
        return MargosConfig(**raw_config)
    except PydanticValidationError as e:
        errors = e.errors()
        if errors:
            first_error = errors[0]
            field_path = ".".join(str(loc) for loc in first_error.get("loc", ()))
            error_msg = first_error.get("msg", "Unknown validation error")
        else:
            field_path = ""
            error_msg = "Unknown validation error"

        raise ValidationError(
            message=f"Config validation failed: {error_msg}",
            context={"Path": str(config_path), "Field": field_path},
            fix="Check the config file matches the expected schema",
        )


def resolve_paths(config: MargosConfig, base_dir: Path) -> MargosConfig:
    """Resolve relative paths in config to absolute paths.

    Args:
        config: The config to process.
        base_dir: Base directory for resolving relative paths (typically experiments/).

    Returns:
        New MargosConfig with resolved absolute paths.

    Raises:
        ValidationError: Referenced files don't exist.
    """
    base_dir = Path(base_dir).resolve()

    scenario_path = base_dir / config.scenario.file
    if not scenario_path.exists():
        raise ValidationError(
            message="Scenario file not found",
            context={"Path": str(scenario_path)},
            fix=f"Create the scenario file or check the path in config",
        )

    script_path = base_dir / config.training.script
    if not script_path.exists():
        raise ValidationError(
            message="Training script not found",
            context={"Path": str(script_path)},
            fix=f"Create the training script or check the path in config",
        )

    return MargosConfig(
        experiment=config.experiment,
        scenario=config.scenario.model_copy(update={"file": str(scenario_path)}),
        training=config.training.model_copy(update={"script": str(script_path)}),
        output=config.output,
    )


def hash_config(config: MargosConfig) -> str:
    """Generate SHA256 hash of config for integrity verification.

    Normalizes the config by converting to JSON with sorted keys
    to ensure deterministic hashing regardless of field order.

    Args:
        config: The config to hash.

    Returns:
        SHA256 hex digest string.
    """
    normalized = json.dumps(config.model_dump(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(normalized.encode()).hexdigest()


def save_frozen_config(config: MargosConfig, output_dir: Path) -> Path:
    """Save frozen copy of config to output directory.

    Args:
        config: The config to save.
        output_dir: Directory to save the config in.

    Returns:
        Path to the saved config file.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    config_path = output_dir / "config.yaml"

    with open(config_path, "w") as f:
        yaml.dump(config.model_dump(), f, default_flow_style=False, sort_keys=False)

    return config_path


def read_config_hash(output_dir: str | Path) -> tuple[str, Literal["config_hash.txt", "config.yaml"]]:
    """Read an experiment config hash from artifacts.

    Prefers the persisted ``config_hash.txt`` artifact. If it is missing,
    recomputes the hash from the frozen ``config.yaml``.

    Args:
        output_dir: Experiment output directory containing config artifacts.

    Returns:
        Tuple of (config_hash, source_artifact).

    Raises:
        ValidationError: If neither artifact is present or the frozen config is invalid.
    """
    output_path = Path(output_dir)

    config_hash_path = output_path / "config_hash.txt"
    if config_hash_path.exists():
        return config_hash_path.read_text().strip(), "config_hash.txt"

    config_path = output_path / "config.yaml"
    if not config_path.exists():
        raise ValidationError(
            message="Config integrity artifacts missing",
            context={"Path": str(output_path)},
            fix="Ensure the run contains config_hash.txt or config.yaml",
        )

    try:
        with open(config_path) as f:
            raw_config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValidationError(
            message="Frozen config is invalid YAML",
            context={"Path": str(config_path), "Error": str(e)},
            fix="Regenerate the experiment artifacts from a valid run",
        )

    if raw_config is None:
        raise ValidationError(
            message="Frozen config is empty",
            context={"Path": str(config_path)},
            fix="Regenerate the experiment artifacts from a valid run",
        )

    try:
        config = MargosConfig(**raw_config)
    except PydanticValidationError as e:
        raise ValidationError(
            message="Frozen config does not match schema",
            context={"Path": str(config_path), "Error": str(e)},
            fix="Regenerate the experiment artifacts from a valid run",
        )

    return hash_config(config), "config.yaml"
