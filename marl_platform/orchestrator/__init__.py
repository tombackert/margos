"""Training orchestration."""

from marl_platform.orchestrator.runner import (
    create_output_dir,
    execute_training_script,
    run_experiment,
    verify_config_integrity,
)

__all__ = ["run_experiment", "create_output_dir", "execute_training_script", "verify_config_integrity"]
