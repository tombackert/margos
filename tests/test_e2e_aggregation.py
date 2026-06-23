"""E2E tests for the aggregation scenario (Issue #15).

These tests validate the full pipeline from CLI to trained model:
1. `margos run aggregation_test` completes successfully
2. Output directory has correct structure
3. Metrics logged to JSONL
4. Two runs with same seed produce identical final reward

Requirements:
- ARGoS3 installed and accessible via `argos3` command
- Margos plugins built in argos_plugins/build/

Run with: pytest tests/test_e2e_aggregation.py -v
Skip with: pytest -m "not argos"
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from margos.cli import app


def argos_available() -> bool:
    """Check if ARGoS is available."""
    try:
        result = subprocess.run(
            ["argos3", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def margos_plugins_available() -> bool:
    """Check if Margos plugins are built."""
    repo_root = Path(__file__).parent.parent
    controller = repo_root / "argos_plugins/build/controllers/libmy_ipc_controller.dylib"
    loop_fn = repo_root / "argos_plugins/build/loop_functions/libzoo_loop_functions.dylib"
    return controller.exists() and loop_fn.exists()


# Skip marker for tests requiring ARGoS
requires_argos = pytest.mark.skipif(
    not (argos_available() and margos_plugins_available()),
    reason="ARGoS or Margos plugins not available",
)

runner = CliRunner()


@requires_argos
@pytest.mark.slow
class TestAggregationScenarioE2E:
    """E2E tests for aggregation scenario (Issue #15 acceptance criteria)."""

    @pytest.fixture
    def repo_root(self) -> Path:
        """Get repository root path."""
        return Path(__file__).parent.parent

    @pytest.fixture
    def aggregation_config_path(self, repo_root: Path) -> Path:
        """Path to aggregation_test.yaml config."""
        return repo_root / "experiments" / "configs" / "aggregation_test.yaml"

    @pytest.fixture
    def experiment_setup(self, repo_root: Path, tmp_path: Path) -> dict[str, Path]:
        """Set up experiment structure with temp results dir.

        Copies experiment files to temp location to allow isolated testing
        while preserving relative path resolution.
        """
        # Copy experiments directory to tmp_path
        src_experiments = repo_root / "experiments"
        dst_experiments = tmp_path / "experiments"
        shutil.copytree(src_experiments, dst_experiments, dirs_exist_ok=True)

        # Create results dir
        results_dir = tmp_path / "results"
        results_dir.mkdir()

        # Update config to use temp results dir
        config_path = dst_experiments / "configs" / "aggregation_test.yaml"
        config_data = yaml.safe_load(config_path.read_text())
        config_data["output"]["dir"] = str(results_dir)
        config_path.write_text(yaml.dump(config_data))

        return {
            "config_path": config_path,
            "results_dir": results_dir,
            "experiments_dir": dst_experiments,
        }

    def test_config_valid_and_loads(self, aggregation_config_path: Path) -> None:
        """Config file is valid and loads correctly."""
        from margos.config import load_config

        assert aggregation_config_path.exists(), (
            f"Config not found: {aggregation_config_path}"
        )

        config = load_config(str(aggregation_config_path))

        assert config.experiment.name == "aggregation_test"
        assert config.experiment.seed == 42
        assert "aggregation" in config.scenario.file
        assert "aggregation" in config.training.script

    def test_scenario_file_exists(self, repo_root: Path) -> None:
        """ARGoS scenario file exists and is valid XML."""
        scenario_path = repo_root / "experiments" / "scenarios" / "footbot_aggregation.argos"
        assert scenario_path.exists(), f"Scenario not found: {scenario_path}"

        content = scenario_path.read_text()
        assert "<argos-configuration>" in content
        assert "foot-bot" in content
        assert 'quantity="5"' in content  # 5 robots as per spec

    def test_training_script_follows_convention(self, repo_root: Path) -> None:
        """Training script exports main(config, callbacks, output_dir)."""
        script_path = repo_root / "experiments" / "training" / "aggregation.py"
        assert script_path.exists(), f"Script not found: {script_path}"

        content = script_path.read_text()
        assert "def main(" in content
        assert "config" in content
        assert "callbacks" in content
        assert "output_dir" in content

    def test_margos_run_completes(self, experiment_setup: dict[str, Path]) -> None:
        """Full pipeline: `margos run aggregation_test` completes successfully."""
        config_path = experiment_setup["config_path"]
        results_dir = experiment_setup["results_dir"]

        # Run via CLI
        result = runner.invoke(app, ["run", str(config_path)], catch_exceptions=False)

        # Check success
        assert result.exit_code == 0, f"CLI failed: {result.stdout}"
        assert "Running experiment" in result.stdout
        assert "Output:" in result.stdout

        # Verify output created
        output_dirs = list(results_dir.glob("aggregation_test_*"))
        assert len(output_dirs) == 1

    def test_output_directory_structure(self, experiment_setup: dict[str, Path]) -> None:
        """Output directory has correct structure per docs."""
        config_path = experiment_setup["config_path"]
        results_dir = experiment_setup["results_dir"]

        runner.invoke(app, ["run", str(config_path)], catch_exceptions=False)

        # Find output directory
        output_dirs = list(results_dir.glob("aggregation_test_*"))
        assert len(output_dirs) == 1, f"Expected 1 output dir, got {len(output_dirs)}"

        output_dir = output_dirs[0]

        # Verify structure (per docs/LowLevelArchitectureBrainstorm.md)
        assert (output_dir / "config.yaml").exists(), "Frozen config missing"
        assert (output_dir / "config_hash.txt").exists(), "Config hash missing"
        assert (output_dir / "env_fingerprint.yaml").exists(), "Fingerprint missing"
        assert (output_dir / "logs").is_dir(), "Logs directory missing"
        assert (output_dir / "checkpoints").is_dir(), "Checkpoints directory missing"
        assert (output_dir / "checkpoints" / "final").is_dir(), "Final checkpoint missing"

    def test_metrics_logged_to_jsonl(self, experiment_setup: dict[str, Path]) -> None:
        """Metrics are logged to logs/metrics.jsonl."""
        config_path = experiment_setup["config_path"]
        results_dir = experiment_setup["results_dir"]

        runner.invoke(app, ["run", str(config_path)], catch_exceptions=False)

        output_dir = list(results_dir.glob("aggregation_test_*"))[0]
        metrics_file = output_dir / "logs" / "metrics.jsonl"

        assert metrics_file.exists(), "metrics.jsonl not created"

        # Verify JSONL format and required fields
        lines = metrics_file.read_text().strip().split("\n")
        assert len(lines) >= 1, "No metrics logged"

        for line in lines:
            if not line.strip():
                continue
            entry = json.loads(line)
            assert "iteration" in entry, "Missing 'iteration' field"
            assert "timestamp" in entry, "Missing 'timestamp' field"

    def test_reproducibility_same_seed(self, experiment_setup: dict[str, Path]) -> None:
        """Two runs with same seed produce identical final reward (SRQ3)."""
        config_path = experiment_setup["config_path"]
        results_dir = experiment_setup["results_dir"]

        # Run 1
        runner.invoke(app, ["run", str(config_path)], catch_exceptions=False)

        # Run 2
        runner.invoke(app, ["run", str(config_path)], catch_exceptions=False)

        # Compare results
        output_dirs = sorted(results_dir.glob("aggregation_test_*"))
        assert len(output_dirs) == 2, f"Expected 2 runs, got {len(output_dirs)}"

        # Get final rewards
        def get_final_reward(output_dir: Path) -> float | None:
            metrics_file = output_dir / "logs" / "metrics.jsonl"
            if not metrics_file.exists():
                return None
            lines = [l for l in metrics_file.read_text().strip().split("\n") if l.strip()]
            if not lines:
                return None
            last_entry = json.loads(lines[-1])
            return last_entry.get("episode_reward_mean")

        reward1 = get_final_reward(output_dirs[0])
        reward2 = get_final_reward(output_dirs[1])

        # Both should have rewards
        assert reward1 is not None, "Run 1 has no final reward"
        assert reward2 is not None, "Run 2 has no final reward"

        # Same seed should produce same result
        assert reward1 == reward2, (
            f"Reproducibility failed: run1={reward1}, run2={reward2}"
        )

    def test_config_hash_deterministic(self, experiment_setup: dict[str, Path]) -> None:
        """Config hash is deterministic across runs."""
        config_path = experiment_setup["config_path"]
        results_dir = experiment_setup["results_dir"]

        # Run twice
        runner.invoke(app, ["run", str(config_path)], catch_exceptions=False)
        runner.invoke(app, ["run", str(config_path)], catch_exceptions=False)

        output_dirs = sorted(results_dir.glob("aggregation_test_*"))
        hash1 = (output_dirs[0] / "config_hash.txt").read_text().strip()
        hash2 = (output_dirs[1] / "config_hash.txt").read_text().strip()

        assert hash1 == hash2, "Config hash should be deterministic"


@requires_argos
@pytest.mark.slow
class TestAggregationRewardFunction:
    """Tests for aggregation reward function."""

    def test_reward_function_importable(self) -> None:
        """Aggregation reward can be imported from Margos."""
        from margos.argos_zoo import aggregation_reward

        assert callable(aggregation_reward)

    def test_reward_function_returns_expected_format(self) -> None:
        """Reward function returns (team_reward, per_agent, metrics)."""
        from margos.argos_zoo import aggregation_reward
        import numpy as np

        # Simulate data
        data = {
            "agents": ["robot0", "robot1", "robot2"],
            "positions": np.array([[0, 0, 0], [1, 0, 0], [0.5, 0.5, 0]]),
            "prev": {},
            "first_step": True,
        }

        reward, per_agent, metrics = aggregation_reward(data)

        assert isinstance(reward, float)
        assert per_agent is None  # Disabled in current implementation
        assert isinstance(metrics, dict)
        assert "reward" in metrics


class TestAggregationFilesExist:
    """Basic checks that required files exist (no ARGoS needed)."""

    def test_config_file_exists(self) -> None:
        """aggregation_test.yaml exists."""
        repo_root = Path(__file__).parent.parent
        config_path = repo_root / "experiments" / "configs" / "aggregation_test.yaml"
        assert config_path.exists()

    def test_scenario_file_exists(self) -> None:
        """footbot_aggregation.argos exists."""
        repo_root = Path(__file__).parent.parent
        scenario_path = repo_root / "experiments" / "scenarios" / "footbot_aggregation.argos"
        assert scenario_path.exists()

    def test_training_script_exists(self) -> None:
        """aggregation.py exists."""
        repo_root = Path(__file__).parent.parent
        script_path = repo_root / "experiments" / "training" / "aggregation.py"
        assert script_path.exists()

    def test_config_references_correct_files(self) -> None:
        """Config references existing scenario and script."""
        repo_root = Path(__file__).parent.parent
        config_path = repo_root / "experiments" / "configs" / "aggregation_test.yaml"

        config_data = yaml.safe_load(config_path.read_text())

        # Verify references
        scenario_ref = config_data["scenario"]["file"]
        script_ref = config_data["training"]["script"]

        scenario_path = repo_root / "experiments" / scenario_ref
        script_path = repo_root / "experiments" / script_ref

        assert scenario_path.exists(), f"Scenario not found: {scenario_path}"
        assert script_path.exists(), f"Script not found: {script_path}"
