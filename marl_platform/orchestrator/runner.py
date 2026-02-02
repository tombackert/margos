"""Training orchestrator - coordinates the full experiment pipeline."""

import importlib.util
import inspect
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from marl_platform.config import load_config, resolve_paths, save_frozen_config, hash_config
from marl_platform.logging import create_logger, create_tensorboard_logger
from marl_platform.utils.errors import ConfigNotFoundError, TrainingError, ValidationError
from marl_platform.utils.fingerprint import capture_fingerprint, save_fingerprint
from marl_platform.utils.progress import TrainingProgress
from marl_platform.utils.seeds import set_all_seeds


def run_experiment(config_path: str) -> str:
    """Execute full training pipeline.

    Steps:
    1. Load + validate config
    2. Create output directory (results/exp_<name>_<timestamp>/)
    3. Copy frozen config + write hash
    4. Capture environment fingerprint
    5. Set all seeds (BEFORE importing training script)
    6. Setup logging callbacks
    7. Dynamic import + call training script main()

    Args:
        config_path: Path to experiment config YAML

    Returns:
        output_dir: Path to results directory

    Raises:
        ConfigNotFoundError: Config file doesn't exist
        ValidationError: Config validation failed
        TrainingError: Training script failed
    """
    config_path_obj = Path(config_path)

    # 1. Load and validate config
    if not config_path_obj.exists():
        raise ConfigNotFoundError(str(config_path_obj))

    config = load_config(str(config_path_obj))

    # Resolve paths relative to experiments directory
    experiments_dir = config_path_obj.parent.parent
    config = resolve_paths(config, experiments_dir)

    # 2. Create output directory
    output_dir = create_output_dir(config)

    # 3. Save frozen config + hash
    save_frozen_config(config, output_dir)
    config_hash = hash_config(config)
    (output_dir / "config_hash.txt").write_text(config_hash)

    # 4. Capture environment fingerprint
    fingerprint = capture_fingerprint()
    save_fingerprint(fingerprint, output_dir)

    # 5. Set seeds BEFORE importing training script
    set_all_seeds(config.experiment.seed)

    # 6. Setup logging
    logger = create_logger(output_dir)
    callbacks = [logger]

    # Add TensorBoard logging if enabled
    if config.training.tensorboard:
        tb_logger = create_tensorboard_logger(output_dir)
        if tb_logger:
            callbacks.append(tb_logger)

    # 7. Execute training script
    script_path = Path(config.training.script)
    execute_training_script(script_path, config, callbacks, output_dir)

    return str(output_dir)


def create_output_dir(config: Any) -> Path:
    """Create timestamped output directory.

    Format: results/<exp_name>_YYYYMMDD-HHMMSS/

    Creates subdirectories:
    - logs/
    - checkpoints/

    Args:
        config: Validated PlatformConfig

    Returns:
        Path to created output directory
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    exp_name = config.experiment.name

    # Use config output.dir or default to "results"
    base_dir = Path(config.output.dir)
    output_dir = base_dir / f"{exp_name}_{timestamp}"

    # Create directory structure
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "logs").mkdir(exist_ok=True)
    (output_dir / "checkpoints").mkdir(exist_ok=True)

    return output_dir


def execute_training_script(
    script_path: Path,
    config: Any,
    callbacks: list,
    output_dir: Path,
) -> None:
    """Dynamic import and execute training script.

    Training script must export:
        main(config: dict, callbacks: list, output_dir: str)

    Optionally accepts:
        main(config: dict, callbacks: list, output_dir: str, progress: TrainingProgress)

    Args:
        script_path: Path to training script
        config: PlatformConfig object
        callbacks: List of RLlib callbacks
        output_dir: Path for checkpoints/logs

    Raises:
        TrainingError: If script import or execution fails
    """
    if not script_path.exists():
        raise TrainingError(
            message="Training script not found",
            context={"script": str(script_path)},
            fix="Check that the training script path in config is correct",
        )

    # Dynamic import
    try:
        spec = importlib.util.spec_from_file_location("training_script", script_path)
        if spec is None or spec.loader is None:
            raise TrainingError(
                message="Failed to load training script",
                context={"script": str(script_path)},
                fix="Ensure the file is a valid Python module",
            )

        module = importlib.util.module_from_spec(spec)
        sys.modules["training_script"] = module
        spec.loader.exec_module(module)

    except SyntaxError as e:
        raise TrainingError(
            message="Training script has syntax error",
            context={"script": str(script_path), "error": str(e)},
            fix="Fix the syntax error in the training script",
        )
    except ModuleNotFoundError as e:
        raise TrainingError(
            message="Training script import failed",
            context={"script": str(script_path), "error": str(e)},
            fix="Check that the training script exists and has no import errors",
        )

    # Check for main function
    if not hasattr(module, "main"):
        raise TrainingError(
            message="Training script missing main() function",
            context={"script": str(script_path)},
            fix="Ensure training script exports: def main(config, callbacks, output_dir)",
        )

    # Check if main() accepts a progress parameter
    main_sig = inspect.signature(module.main)
    accepts_progress = "progress" in main_sig.parameters

    # Create progress reporter
    progress = TrainingProgress()

    # Execute training
    try:
        # Convert config to dict for training script
        config_dict = config.model_dump()

        if accepts_progress:
            module.main(config_dict, callbacks, str(output_dir), progress=progress)
        else:
            module.main(config_dict, callbacks, str(output_dir))

    except Exception as e:
        raise TrainingError(
            message="Training script execution failed",
            context={"script": str(script_path), "error": str(e)},
            fix="Check the training script for runtime errors",
        )
    finally:
        # Ensure progress bar is cleaned up
        progress.finish()
