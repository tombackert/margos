# Sprint 2: Core Pipeline - GitHub Issues

## Sprint Goal

Complete the pipeline from `platform run exp` → actual training → logged results. User can run a real experiment (aggregation scenario) end-to-end with deterministic seeding.

**Milestone Target:** MS4 - "Thin Slice" End-to-End

**Entry Criteria:** Sprint 1 (CLI) completed - all commands exist as stubs

**Exit Criteria:**
- `platform run aggregation_test` executes real training via ArgosToZoo
- Metrics logged to `results/<exp>/logs/metrics.jsonl`
- Config frozen + hashed in output directory
- Environment fingerprint captured
- Reproducible with same seed (verified by 2 runs)

---

## Architecture Context

### Component Dependencies

```
                    ┌─────────────────┐
                    │      CLI        │
                    │  (Sprint 1) ✓   │
                    └────────┬────────┘
                             │
                             ▼
┌──────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Config System│◄───│    Training     │───►│ Logging System  │
│  (Issue 1)   │    │  Orchestrator   │    │   (Issue 4)     │
└──────────────┘    │   (Issue 6)     │    └─────────────────┘
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
       ┌───────────┐  ┌───────────┐  ┌─────────────┐
       │   Seeds   │  │Fingerprint│  │ ArgosToZoo  │
       │ (Issue 2) │  │ (Issue 3) │  │  (Issue 5)  │
       └───────────┘  └───────────┘  └──────┬──────┘
                                            │
                                  ┌─────────┴─────────┐
                                  ▼                   ▼
                             ┌────────┐          ┌────────┐
                             │ ARGoS  │          │ RLlib  │
                             └────────┘          └────────┘
```

### Data Flow: `platform run aggregation_test`

```
1. CLI parses command → calls run_experiment(config_path)
2. Orchestrator:
   a. load_config() → validate → hash → freeze copy
   b. capture_fingerprint() → save
   c. set_all_seeds(config.seed)
   d. create MetricsLogger callback
   e. dynamic import training script
   f. call training_script.main(config, callbacks, output_dir)
3. Training script:
   a. Create ArgosEnv (ATZ handles ARGoS subprocess)
   b. Register env with RLlib
   c. Build PPO algorithm with callbacks
   d. Training loop → callbacks log metrics
4. Results written to results/exp_<timestamp>/
```

---

## Issue 1: Config System

**Title:** `[Core] Implement config loader, schema, and validation`

**Labels:** `core`, `config`, `must`

**Requirements:** R2.1, R3.3, R4.1

### Description

Implement the configuration system that loads, validates, and hashes experiment configs. This is foundational - the orchestrator depends on it.

### Context

From LowLevelArchitectureBrainstorm.md:
- Validation library: pydantic (Decision L3)
- Config references scenario + training script (not hyperparams)

### Config Schema

```yaml
# experiments/configs/exp_v1.yaml
experiment:
  name: "aggregation_v1"
  seed: 42

scenario:
  file: "scenarios/footbot_10.argos"  # Relative to experiments/

training:
  script: "training/aggregation.py"   # Relative to experiments/
  iterations: 100                      # Training iterations

output:
  dir: "results/"
```

### Files to Create

```
platform/config/
├── __init__.py
├── loader.py    # Load, parse, resolve paths
└── schema.py    # Pydantic models + validation
```

### Interface

```python
# platform/config/schema.py
from pydantic import BaseModel

class ExperimentConfig(BaseModel):
    name: str
    seed: int

class ScenarioConfig(BaseModel):
    file: str  # Path to .argos file

class TrainingConfig(BaseModel):
    script: str  # Path to training script
    iterations: int = 100

class OutputConfig(BaseModel):
    dir: str = "results/"

class PlatformConfig(BaseModel):
    experiment: ExperimentConfig
    scenario: ScenarioConfig
    training: TrainingConfig
    output: OutputConfig
```

```python
# platform/config/loader.py
import hashlib
import yaml
from pathlib import Path
from .schema import PlatformConfig

def load_config(path: str) -> PlatformConfig:
    """
    Load and validate config from YAML file.

    Raises:
        FileNotFoundError: Config file doesn't exist
        ValidationError: Config fails schema validation
    """
    pass

def resolve_paths(config: PlatformConfig, base_dir: Path) -> PlatformConfig:
    """
    Resolve relative paths in config to absolute paths.
    Base directory is typically experiments/.
    """
    pass

def hash_config(config: PlatformConfig) -> str:
    """
    Generate SHA256 hash of config for integrity verification.
    Normalizes config (sorted keys, no whitespace variance).
    """
    pass

def save_frozen_config(config: PlatformConfig, output_dir: Path) -> Path:
    """
    Save frozen copy of config to output directory.
    Returns path to saved config.
    """
    pass
```

### Tasks

- [ ] Create `platform/config/schema.py` with pydantic models
- [ ] Create `platform/config/loader.py` with load/validate/hash functions
- [ ] Implement path resolution (relative → absolute)
- [ ] Implement config hashing (SHA256, normalized)
- [ ] Add validation for:
  - Required fields present
  - Referenced files exist (scenario, training script)
  - Seed is positive integer
- [ ] Write unit tests for loader

### Acceptance Criteria

```python
# Valid config loads successfully
config = load_config("experiments/configs/test.yaml")
assert config.experiment.name == "test"
assert config.experiment.seed == 42

# Missing required field raises ValidationError
# Invalid seed type raises ValidationError
# Non-existent scenario file raises FileNotFoundError (after path resolution)

# Hash is deterministic
hash1 = hash_config(config)
hash2 = hash_config(config)
assert hash1 == hash2

# Hash changes when config changes
config2 = config.copy()
config2.experiment.seed = 43
assert hash_config(config) != hash_config(config2)
```

### Definition of Done

- [ ] Pydantic schema validates all config fields
- [ ] `load_config()` returns validated PlatformConfig
- [ ] `resolve_paths()` converts relative to absolute paths
- [ ] `hash_config()` produces deterministic SHA256
- [ ] Validation errors include field location and fix suggestion
- [ ] Unit tests pass

---

## Issue 2: Seed Propagation Utility

**Title:** `[Core] Implement centralized seed propagation`

**Labels:** `core`, `utils`, `must`

**Requirements:** R3.1

**Depends on:** None (standalone utility)

### Description

Implement utility to propagate a single seed to all RNG sources. Critical for reproducibility.

### Context

From DesignBrainstorm.md (Seed Propagation Strategy):

| RNG Source | Seeding Method |
|------------|----------------|
| Python `random` | `random.seed(x)` |
| NumPy | `np.random.seed(x)` |
| PyTorch | `torch.manual_seed(x)` |
| PyTorch CUDA | `torch.cuda.manual_seed_all(x)` |

Note: ARGoS seeding is handled by ArgosToZoo via `env.reset(seed=X)`.

### Interface

```python
# platform/utils/seeds.py

def set_all_seeds(seed: int) -> None:
    """
    Propagate seed to all Python-side RNG sources.

    MUST be called BEFORE importing training script
    (to seed any module-level RNG initialization).

    Sources seeded:
    - random.seed(seed)
    - numpy.random.seed(seed)
    - torch.manual_seed(seed)
    - torch.cuda.manual_seed_all(seed)

    Note: ARGoS seeding handled separately by ArgosEnv.reset(seed=X)
    """
    pass

def get_seed_state() -> dict:
    """
    Capture current RNG states for debugging.
    Returns dict with states from each source.
    """
    pass
```

### Tasks

- [ ] Create `platform/utils/seeds.py`
- [ ] Implement `set_all_seeds()` for all RNG sources
- [ ] Handle case where torch/numpy not installed (graceful skip)
- [ ] Add logging to confirm which sources were seeded
- [ ] Write unit tests verifying determinism

### Acceptance Criteria

```python
# Same seed produces same sequence
set_all_seeds(42)
a = [random.random() for _ in range(5)]
set_all_seeds(42)
b = [random.random() for _ in range(5)]
assert a == b

# Works for numpy
set_all_seeds(42)
a = np.random.rand(5)
set_all_seeds(42)
b = np.random.rand(5)
assert np.array_equal(a, b)

# Works for torch
set_all_seeds(42)
a = torch.rand(5)
set_all_seeds(42)
b = torch.rand(5)
assert torch.equal(a, b)
```

### Definition of Done

- [ ] `set_all_seeds()` seeds all 4 RNG sources
- [ ] Graceful handling if torch/numpy not available
- [ ] Logging confirms seeding (debug level)
- [ ] Unit tests verify determinism for each source

---

## Issue 3: Environment Fingerprint Utility

**Title:** `[Core] Implement environment fingerprint capture`

**Labels:** `core`, `utils`, `must`

**Requirements:** R5.4

**Depends on:** None (standalone utility)

### Description

Capture environment metadata at experiment start for reproducibility tracking and cross-environment comparison during import.

### Context

From DesignBrainstorm.md:
```yaml
env_fingerprint:
  python: "3.x.x"
  os: "Linux/macOS/Windows"
  packages:
    rllib: "x.x.x"
    torch: "x.x.x"
    numpy: "x.x.x"
  captured_at: "ISO timestamp"
```

### Interface

```python
# platform/utils/fingerprint.py
from pathlib import Path

def capture_fingerprint() -> dict:
    """
    Capture current environment metadata.

    Returns:
        {
            "python": "3.10.0",
            "os": "Darwin-23.0.0",
            "platform": "macOS-14.0-arm64",
            "packages": {
                "ray": "2.x.x",
                "torch": "2.x.x",
                "numpy": "1.x.x",
                "pydantic": "2.x.x",
            },
            "captured_at": "2024-01-15T14:30:22"
        }
    """
    pass

def save_fingerprint(fingerprint: dict, output_dir: Path) -> Path:
    """
    Save fingerprint to YAML file in output directory.
    Returns path to saved file.
    """
    pass

def compare_fingerprints(current: dict, reference: dict) -> dict:
    """
    Compare two fingerprints.

    Returns:
        {
            "python": {"current": "3.10.0", "reference": "3.10.0", "match": True},
            "packages": {
                "torch": {"current": "2.0.0", "reference": "2.0.1", "match": False},
                ...
            },
            "all_match": False
        }
    """
    pass
```

### Key Packages to Track

| Package | Why |
|---------|-----|
| ray (rllib) | RL algorithm implementation |
| torch | Neural network backend |
| numpy | Numerical operations |
| pydantic | Config validation |

### Tasks

- [ ] Create `platform/utils/fingerprint.py`
- [ ] Implement `capture_fingerprint()` using `sys`, `platform`, `importlib.metadata`
- [ ] Implement `save_fingerprint()` to YAML
- [ ] Implement `compare_fingerprints()` for import verification
- [ ] Handle missing packages gracefully (mark as "not installed")
- [ ] Write unit tests

### Acceptance Criteria

```python
# Capture returns expected structure
fp = capture_fingerprint()
assert "python" in fp
assert "os" in fp
assert "packages" in fp
assert "captured_at" in fp

# Save creates valid YAML
path = save_fingerprint(fp, Path("results/test/"))
assert path.exists()
loaded = yaml.safe_load(path.read_text())
assert loaded["python"] == fp["python"]

# Compare detects mismatches
fp1 = {"python": "3.10.0", "packages": {"torch": "2.0.0"}}
fp2 = {"python": "3.10.0", "packages": {"torch": "2.0.1"}}
result = compare_fingerprints(fp1, fp2)
assert result["all_match"] == False
assert result["packages"]["torch"]["match"] == False
```

### Definition of Done

- [ ] `capture_fingerprint()` collects Python, OS, key packages
- [ ] `save_fingerprint()` writes valid YAML
- [ ] `compare_fingerprints()` identifies all mismatches
- [ ] Missing packages handled gracefully
- [ ] Unit tests pass

---

## Issue 4: Logging System (RLlib Callbacks)

**Title:** `[Core] Implement metrics logging via RLlib callbacks`

**Labels:** `core`, `logging`, `must`

**Requirements:** R2.4

**Depends on:** Issue 1 (needs output directory structure)

### Description

Implement RLlib callback that captures training metrics and writes to JSONL file. This enables automatic metric collection without user intervention.

### Context

From LowLevelArchitectureBrainstorm.md:
- Format: JSONL (Decision A1)
- Essential metrics (Decision L4): `iteration`, `episode_reward_mean`, `loss`, `timestamp`

### Interface

```python
# platform/logging/callbacks.py
from ray.rllib.algorithms.callbacks import DefaultCallbacks
from pathlib import Path
import json
from datetime import datetime

class MetricsLogger(DefaultCallbacks):
    """
    RLlib callback that logs training metrics to JSONL file.

    Logged metrics per iteration:
    - iteration: Training iteration number
    - episode_reward_mean: Average episode reward
    - episode_reward_min: Minimum episode reward
    - episode_reward_max: Maximum episode reward
    - episode_len_mean: Average episode length
    - loss: Policy loss (if available)
    - timestamp: ISO format timestamp
    """

    def __init__(self, output_dir: Path):
        super().__init__()
        self.log_path = output_dir / "logs" / "metrics.jsonl"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def on_train_result(self, *, algorithm, result, **kwargs):
        """Called after each training iteration."""
        pass

    def _extract_metrics(self, result: dict) -> dict:
        """Extract relevant metrics from RLlib result dict."""
        pass

    def _append_log(self, metrics: dict):
        """Append metrics as JSON line to log file."""
        pass
```

```python
# platform/logging/__init__.py

def create_logger(output_dir: Path) -> MetricsLogger:
    """Factory function to create configured MetricsLogger."""
    pass

def read_metrics(log_path: Path) -> list[dict]:
    """Read all metrics from JSONL log file."""
    pass
```

### Log Format

```jsonl
{"iteration": 1, "episode_reward_mean": -150.2, "episode_reward_min": -200.0, "episode_reward_max": -100.0, "episode_len_mean": 500.0, "timestamp": "2024-01-15T14:30:22"}
{"iteration": 2, "episode_reward_mean": -145.8, "episode_reward_min": -190.0, "episode_reward_max": -95.0, "episode_len_mean": 500.0, "timestamp": "2024-01-15T14:31:45"}
```

### Tasks

- [ ] Create `platform/logging/callbacks.py` with `MetricsLogger`
- [ ] Implement `on_train_result` to extract and log metrics
- [ ] Create `platform/logging/__init__.py` with factory and reader
- [ ] Handle missing metrics gracefully (use None)
- [ ] Ensure log file is created with parent directories
- [ ] Write unit tests with mock RLlib results

### Acceptance Criteria

```python
# Logger creates file and logs metrics
logger = MetricsLogger(Path("results/test/"))
mock_result = {
    "training_iteration": 1,
    "episode_reward_mean": -150.0,
    "episode_reward_min": -200.0,
    "episode_reward_max": -100.0,
    "episode_len_mean": 500.0,
}
logger.on_train_result(algorithm=None, result=mock_result)

# Log file exists and contains valid JSON
assert logger.log_path.exists()
metrics = read_metrics(logger.log_path)
assert len(metrics) == 1
assert metrics[0]["iteration"] == 1
assert metrics[0]["episode_reward_mean"] == -150.0
assert "timestamp" in metrics[0]
```

### Definition of Done

- [ ] `MetricsLogger` extends `DefaultCallbacks`
- [ ] `on_train_result` extracts and logs metrics
- [ ] Metrics written as valid JSONL
- [ ] `read_metrics` utility reads log files
- [ ] Missing metrics handled gracefully
- [ ] Unit tests pass

---

## Issue 5: ArgosToZoo Bridge Integration

**Title:** `[Core] Integrate ArgosToZoo bridge as dependency`

**Labels:** `core`, `integration`, `must`

**Requirements:** R2.3

**Depends on:** None (external dependency setup)

### Description

Set up ArgosToZoo as a dependency and verify integration works. ATZ provides the ARGoS ↔ RLlib bridge - we use it as-is, not modify it.

### Context

From DesignBrainstorm.md:
- ATZ is an existing, proven implementation
- Platform wraps ATZ, doesn't modify it
- `ArgosEnv` manages ARGoS subprocess internally
- Seeding via `env.reset(seed=X)` which rewrites `.argos` file

### ArgosToZoo Components Used

| Component | Import Path | Purpose |
|-----------|-------------|---------|
| `ArgosEnv` | `zoo.argos_env.ArgosEnv` | PettingZoo ParallelEnv |
| Reward functions | `zoo.scenarios.*` | Task-specific rewards |

### Tasks

- [ ] Add ArgosToZoo to project dependencies (git submodule or pip install)
- [ ] Verify import works: `from zoo.argos_env import ArgosEnv`
- [ ] Verify ARGoS is installed and accessible
- [ ] Create integration test that:
  - Creates ArgosEnv with test scenario
  - Runs one step
  - Verifies observations returned
- [ ] Document ATZ setup in MVP README

### Integration Test

```python
# tests/test_argos_integration.py

def test_argos_env_creation():
    """Verify ArgosEnv can be created and stepped."""
    from zoo.argos_env import ArgosEnv

    env = ArgosEnv(
        argos_file="experiments/scenarios/footbot_test.argos",
        max_steps=10,
        reward_fn=lambda obs, act, info: 0.0,  # Dummy reward
        quiet=True,
    )

    obs, infos = env.reset(seed=42)
    assert obs is not None
    assert len(obs) > 0  # At least one agent

    # Take one step
    actions = {agent: env.action_space(agent).sample() for agent in env.agents}
    obs, rewards, terms, truncs, infos = env.step(actions)

    env.close()

def test_argos_seeding():
    """Verify seeding produces deterministic results."""
    from zoo.argos_env import ArgosEnv

    def run_episode(seed):
        env = ArgosEnv(
            argos_file="experiments/scenarios/footbot_test.argos",
            max_steps=10,
            reward_fn=lambda obs, act, info: 0.0,
            quiet=True,
        )
        obs, _ = env.reset(seed=seed)
        first_obs = {k: v.copy() for k, v in obs.items()}
        env.close()
        return first_obs

    obs1 = run_episode(42)
    obs2 = run_episode(42)
    obs3 = run_episode(99)

    # Same seed → same initial observation
    assert obs1.keys() == obs2.keys()
    for agent in obs1:
        assert np.array_equal(obs1[agent], obs2[agent])

    # Different seed → different observation (probabilistic, may fail rarely)
    # At minimum, verify it runs without error
```

### Acceptance Criteria

- [ ] `from zoo.argos_env import ArgosEnv` works
- [ ] ARGoS simulator launches successfully
- [ ] Integration test passes (create, step, close)
- [ ] Seeding test demonstrates determinism
- [ ] README documents ATZ setup steps

### Definition of Done

- [ ] ArgosToZoo importable from platform code
- [ ] ARGoS accessible from command line
- [ ] Integration tests pass
- [ ] Setup documented

---

## Issue 6: Training Orchestrator

**Title:** `[Core] Implement training orchestrator`

**Labels:** `core`, `orchestrator`, `must`

**Requirements:** R2.2 (backend implementation)

**Depends on:** Issues 1-5 (all foundational components)

### Description

Implement the training orchestrator that coordinates the full experiment pipeline: load config → set seeds → capture fingerprint → execute training → log metrics.

### Context

From LowLevelArchitectureBrainstorm.md:
- Execution model: Dynamic import (Decision L2)
- Training script convention: `main(config, callbacks, output_dir)`

### Interface

```python
# platform/orchestrator/runner.py
from pathlib import Path
from datetime import datetime

def run_experiment(config_path: str) -> str:
    """
    Execute full training pipeline.

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
    pass

def create_output_dir(config: PlatformConfig) -> Path:
    """
    Create timestamped output directory.

    Format: results/<exp_name>_YYYYMMDD-HHMMSS/

    Creates subdirectories:
    - logs/
    - checkpoints/
    """
    pass

def execute_training_script(
    script_path: Path,
    config: PlatformConfig,
    callbacks: list,
    output_dir: Path
) -> None:
    """
    Dynamic import and execute training script.

    Training script must export:
        main(config: dict, callbacks: list, output_dir: str)
    """
    pass
```

### Orchestrator Flow

```python
def run_experiment(config_path: str) -> str:
    # 1. Load and validate config
    config = load_config(config_path)
    config = resolve_paths(config, Path("experiments"))

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
    logger = MetricsLogger(output_dir)
    callbacks = [logger]

    # 7. Execute training script
    execute_training_script(
        Path(config.training.script),
        config,
        callbacks,
        output_dir
    )

    return str(output_dir)
```

### Tasks

- [ ] Create `platform/orchestrator/runner.py`
- [ ] Implement `run_experiment()` with full pipeline
- [ ] Implement `create_output_dir()` with timestamp format
- [ ] Implement `execute_training_script()` with dynamic import
- [ ] Update CLI `run` command to call orchestrator (remove stub)
- [ ] Handle errors with clear messages (using error framework from Sprint 1)
- [ ] Write integration test with mock training script

### Error Handling

```python
# Wrap training execution with clear errors
try:
    execute_training_script(...)
except ModuleNotFoundError as e:
    raise TrainingError(
        message="Training script import failed",
        context={"script": str(script_path), "error": str(e)},
        fix="Check that the training script exists and has no import errors"
    )
except AttributeError:
    raise TrainingError(
        message="Training script missing main() function",
        context={"script": str(script_path)},
        fix="Ensure training script exports: def main(config, callbacks, output_dir)"
    )
```

### Acceptance Criteria

```bash
# Run with valid config
$ platform run test_exp
Running experiment: test_exp
Config: experiments/configs/test_exp.yaml
Output: results/test_exp_20240115-143022/

# Verify output structure
$ ls results/test_exp_20240115-143022/
config.yaml
config_hash.txt
env_fingerprint.yaml
logs/
  metrics.jsonl
checkpoints/
```

### Definition of Done

- [ ] `run_experiment()` executes full pipeline
- [ ] Output directory created with correct structure
- [ ] Frozen config saved with hash
- [ ] Fingerprint captured and saved
- [ ] Seeds set before training script import
- [ ] Training script executed via dynamic import
- [ ] CLI `run` command integrated (stub replaced)
- [ ] Errors display clear messages with fixes

---

## Issue 7: Minimal Aggregation Test Scenario

**Title:** `[Core] Create minimal aggregation scenario for E2E testing`

**Labels:** `core`, `test`, `must`

**Depends on:** Issues 1-6 (full pipeline)

### Description

Create a minimal but real aggregation scenario that validates the entire pipeline works end-to-end. This serves as both a test fixture and an example for users.

### Context

The aggregation scenario is a standard swarm robotics task where robots must cluster together. It's simple enough for quick testing but real enough to validate the full pipeline.

### Files to Create

```
experiments/
├── scenarios/
│   └── aggregation_test.argos    # Minimal ARGoS scenario (5 robots, small arena)
├── training/
│   └── aggregation.py            # Training script following platform convention
└── configs/
    └── aggregation_test.yaml     # Test config (10 iterations for fast testing)
```

### Test Scenario Spec

**Arena:** 2m × 2m (small for fast simulation)
**Robots:** 5 foot-bots (minimal swarm)
**Sensors:** Proximity, light, RAB (range-and-bearing)
**Actuators:** Differential steering
**Max steps per episode:** 100 (short for testing)

### Training Script Convention

```python
# experiments/training/aggregation.py
"""
Aggregation training script following platform convention.

Platform calls: main(config, callbacks, output_dir)
"""

def aggregation_reward(observations: dict, actions: dict, info: dict) -> dict:
    """
    Simple aggregation reward: closer to center of mass = higher reward.
    """
    # Implementation based on robot positions from observations
    pass

def main(config: dict, callbacks: list, output_dir: str):
    """
    Training entry point called by platform orchestrator.

    Args:
        config: Full experiment config (PlatformConfig as dict)
        callbacks: List of RLlib callbacks (includes MetricsLogger)
        output_dir: Path for checkpoints
    """
    from zoo.argos_env import ArgosEnv
    from ray.rllib.algorithms.ppo import PPOConfig
    from ray.tune.registry import register_env

    # Create environment
    def env_creator(cfg):
        return ArgosEnv(
            argos_file=config["scenario"]["file"],
            max_steps=100,
            reward_fn=aggregation_reward,
            quiet=True,
        )

    register_env("aggregation", env_creator)

    # Build algorithm
    algo = (
        PPOConfig()
        .environment("aggregation")
        .callbacks(callbacks[0] if callbacks else None)  # MetricsLogger
        .framework("torch")
        .training(train_batch_size=200)  # Small for testing
        .build()
    )

    # Training loop
    iterations = config.get("training", {}).get("iterations", 10)
    for i in range(iterations):
        result = algo.train()
        print(f"Iteration {i+1}/{iterations}: reward={result['episode_reward_mean']:.2f}")

        # Save checkpoint at end
        if i == iterations - 1:
            algo.save(f"{output_dir}/checkpoints/final")

    algo.stop()
```

### Test Config

```yaml
# experiments/configs/aggregation_test.yaml
experiment:
  name: "aggregation_test"
  seed: 42

scenario:
  file: "scenarios/aggregation_test.argos"

training:
  script: "training/aggregation.py"
  iterations: 10  # Short for testing

output:
  dir: "results/"
```

### Tasks

- [ ] Create `aggregation_test.argos` scenario file (minimal arena, 5 robots)
- [ ] Create `aggregation.py` training script following convention
- [ ] Create `aggregation_test.yaml` config
- [ ] Implement simple aggregation reward function
- [ ] Run full E2E test: `platform run aggregation_test`
- [ ] Verify output directory structure
- [ ] Verify metrics logged
- [ ] Verify reproducibility: run twice with same seed, compare results

### E2E Test Script

```bash
#!/bin/bash
# tests/e2e_aggregation.sh

echo "=== E2E Test: Aggregation Scenario ==="

# Run 1
echo "Running first experiment..."
platform run aggregation_test
RUN1_DIR=$(ls -td results/aggregation_test_* | head -1)

# Run 2 (same seed should produce same results)
echo "Running second experiment (same seed)..."
platform run aggregation_test
RUN2_DIR=$(ls -td results/aggregation_test_* | head -1)

# Compare final rewards
echo "Comparing results..."
REWARD1=$(tail -1 "$RUN1_DIR/logs/metrics.jsonl" | jq '.episode_reward_mean')
REWARD2=$(tail -1 "$RUN2_DIR/logs/metrics.jsonl" | jq '.episode_reward_mean')

echo "Run 1 final reward: $REWARD1"
echo "Run 2 final reward: $REWARD2"

if [ "$REWARD1" == "$REWARD2" ]; then
    echo "✓ Reproducibility verified: rewards match"
else
    echo "✗ Reproducibility issue: rewards differ"
    exit 1
fi

echo "=== E2E Test Complete ==="
```

### Acceptance Criteria

```bash
# Full E2E flow works
$ platform run aggregation_test
Running experiment: aggregation_test
Config: experiments/configs/aggregation_test.yaml
Iteration 1/10: reward=-150.23
Iteration 2/10: reward=-145.67
...
Iteration 10/10: reward=-98.45
Output: results/aggregation_test_20240115-143022/

# Output directory contains expected files
$ ls results/aggregation_test_20240115-143022/
config.yaml
config_hash.txt
env_fingerprint.yaml
logs/metrics.jsonl
checkpoints/final/

# Metrics logged correctly
$ head -2 results/aggregation_test_20240115-143022/logs/metrics.jsonl
{"iteration": 1, "episode_reward_mean": -150.23, ...}
{"iteration": 2, "episode_reward_mean": -145.67, ...}

# Reproducibility: same seed → same final reward
$ platform run aggregation_test  # seed=42
$ platform run aggregation_test  # seed=42
# Both runs should have identical final episode_reward_mean
```

### Definition of Done

- [ ] ARGoS scenario file created and valid
- [ ] Training script follows platform convention
- [ ] Config file valid and loads correctly
- [ ] `platform run aggregation_test` completes successfully
- [ ] Output directory has correct structure
- [ ] Metrics logged to JSONL
- [ ] Two runs with same seed produce identical final reward
- [ ] E2E test script passes

---

## Sprint Summary

| # | Issue | Requirements | Priority | Depends On |
|---|-------|--------------|----------|------------|
| 1 | Config System | R2.1, R3.3, R4.1 | Must | - |
| 2 | Seed Propagation | R3.1 | Must | - |
| 3 | Environment Fingerprint | R5.4 | Must | - |
| 4 | Logging System | R2.4 | Must | 1 |
| 5 | ArgosToZoo Integration | R2.3 | Must | - |
| 6 | Training Orchestrator | R2.2 | Must | 1-5 |
| 7 | Aggregation Test Scenario | - | Must | 1-6 |

**Sprint Goal:** `platform run aggregation_test` executes real training with reproducible results.

**Critical Path:** Issues 1, 2, 3, 5 can be done in parallel → Issue 4 → Issue 6 → Issue 7

```
[1: Config] ──────────┐
[2: Seeds] ───────────┤
[3: Fingerprint] ─────┼──► [4: Logging] ──► [6: Orchestrator] ──► [7: E2E Test]
[5: ATZ Integration] ─┘
```

---

## Risks

| # | Risk | Severity | Mitigation |
|---|------|----------|------------|
| R1 | ArgosToZoo integration issues | High | Test ATZ independently first (Issue 5); have fallback to mock env for other issues |
| R2 | ARGoS not installed on dev machine | High | Docker environment or skip integration tests with clear documentation |
| R3 | RLlib API changes | Medium | Pin RLlib version; use stable callback API |
| R4 | Non-determinism from GPU | Medium | Document limitation; test on CPU first; accept small variance |
| R5 | Training too slow for testing | Low | Use minimal scenario (5 robots, 10 iterations, 100 steps/episode) |

---

## Notes for MVP Repo

When creating issues in the MVP repo:

1. **Labels to create:** `core`, `config`, `utils`, `logging`, `orchestrator`, `integration`, `test`, `must`

2. **Milestone:** Create "Sprint 2: Core Pipeline" milestone

3. **Issue template:** Use the structure above (Description, Context, Interface, Tasks, Acceptance Criteria, Definition of Done)

4. **Dependencies:** Use GitHub's "blocked by #X" syntax in issue descriptions
