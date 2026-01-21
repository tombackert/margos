# Low-Level Architecture Brainstorm

## Goal
Define component internals: module structure, classes, detailed interfaces, and implementation details for each platform component.

## Reference
- High-level architecture: See DesignBrainstorm.md
- Requirements: See DesignBrainstorm.md (Consolidated Requirements)
- Workflows: See WorkflowBrainstorm.md

## Decisions from High-Level Architecture

| Decision | Choice |
|----------|--------|
| A1 | JSONL for logs |
| A2 | Typer for CLI |
| A4 | Config file path for script params |
| A5 | Direct calls between components |
| A6 | Hybrid write model |

## Decisions Made in This Document

| # | Decision | Choice | Rationale |
|---|----------|--------|-----------|
| L1 | CLI command style | Subcommands (`platform run`) | Standard CLI convention; slashes cause shell issues |
| L2 | Execution model | Dynamic import | Can inject callbacks, shared seed state |
| L3 | Validation library | pydantic | Modern, good errors, type hints |
| L4 | Essential metrics | reward_mean, loss, iteration, timestamp | Minimal for M3.1/M3.2 + training diagnostics |
| L5 | Checkpoints in bundle | Include by default | Simplifies reproduction |
| L6 | Plotting library | matplotlib | Simple, thesis-ready PNGs |
| L7 | CLI argument style | Convention over configuration | User provides name, platform resolves path. Serves SRQ2 efficiency |
| L8 | Error display format | Structured: message + context + fix | Plain language, actionable. Serves R4.2 |

---

## Project Structure

```
platform/
├── __init__.py
├── cli.py              # CLI entry point (Typer)
├── config/
│   ├── __init__.py
│   ├── loader.py       # Load, validate configs
│   └── schema.py       # Config schema + validation
├── orchestrator/
│   ├── __init__.py
│   └── runner.py       # Training orchestration
├── logging/
│   ├── __init__.py
│   └── callbacks.py    # RLlib callbacks for metrics
├── analysis/
│   ├── __init__.py
│   ├── report.py       # Report generation
│   └── compare.py      # Reproducibility comparison
├── export/
│   ├── __init__.py
│   ├── bundle.py       # Export bundling
│   └── importer.py     # Import unpacking
└── utils/
    ├── __init__.py
    ├── seeds.py        # Seed propagation
    └── fingerprint.py  # Environment fingerprint
```

---

## Component 1: CLI

**File:** `cli.py`

**Requirements served:** R2.2, R2.5, R4.2, R4.3, R5.1, R5.2

### Commands (Convention Over Configuration - L7)

**Principle:** User provides names, platform resolves paths. Reduces steps (SRQ2) and errors (SRQ4).

| Command             | User Input   | Platform Resolves                          |
| ------------------- | ------------ | ------------------------------------------ |
| `run exp_v1`        | `exp_v1`     | `experiments/configs/exp_v1.yaml`          |
| `report exp_123`    | `exp_123`    | `results/exp_123/`                         |
| `export exp_123`    | `exp_123`    | `results/exp_123/` → `bundles/exp_123.zip` |
| `import bundle.zip` | `bundle.zip` | `bundles/bundle.zip`                       |





```python
import typer

app = typer.Typer()

@app.command()
def run(
    experiment: str = typer.Argument(..., help="Experiment name"),
    config_dir: str = typer.Option("experiments/configs", help="Override config dir")
):
    """Run an experiment from config file."""
    pass

@app.command()
def report(
    experiment: str = typer.Argument(..., help="Experiment ID"),
    reference: str = typer.Option(None, help="Reference for comparison")
):
    """Generate report for an experiment."""
    pass

@app.command()
def export(
    experiment: str = typer.Argument(..., help="Experiment ID"),
    output: str = typer.Option(None, help="Output bundle path")
):
    """Export experiment to shareable bundle."""
    pass

@app.command("import")
def import_(bundle: str = typer.Argument(..., help="Bundle file")):
    """Import experiment bundle."""
    pass
```

### Notes
- `import_` in code → Typer `name="import"` maps to `import` in CLI
- Error display format: Structured (L8) - message + context + fix suggestion

---

## Component 2: Config System

**Files:** `config/loader.py`, `config/schema.py`

**Requirements served:** R2.1, R3.1, R3.3, R4.1

### Config Schema

```yaml
# experiments/configs/exp_v1.yaml
experiment:
  name: "aggregation_v1"
  seed: 42

scenario:
  file: "scenarios/footbot_10.argos"

training:
  script: "training/aggregation.py"

output:
  dir: "results/"
```

### Interfaces

```python
# config/loader.py

def load_config(path: str) -> dict:
    """Load and parse YAML config file."""
    pass

def validate_config(config: dict) -> tuple[bool, list[str]]:
    """
    Validate config against schema.
    Returns (is_valid, list_of_errors).
    """
    pass

def hash_config(config: dict) -> str:
    """Generate SHA256 hash of config for integrity checking."""
    pass

def resolve_paths(config: dict, base_dir: str) -> dict:
    """Resolve relative paths in config to absolute paths."""
    pass
```

### Notes
- Validation library: pydantic (Decision L3)
- Hash normalization: See Q8 in Remaining Open Questions

---

## Component 3: Training Orchestrator

**File:** `orchestrator/runner.py`

**Requirements served:** R2.2, R2.3, R3.1, R3.3

### Interface

```python
# orchestrator/runner.py

def run_experiment(config_path: str) -> str:
    """
    Execute full training pipeline.

    Steps:
    1. Load + validate config
    2. Create output directory (results/exp_<timestamp>/)
    3. Copy frozen config + write hash
    4. Capture env fingerprint
    5. Set all seeds (BEFORE importing training script)
    6. Setup logging callbacks
    7. Dynamic import + call training script main()

    Returns: output_dir path
    """
    pass
```

### Execution Model (Decision: L2 - Dynamic Import)

**Why dynamic import:**
- Can inject RLlib callbacks for logging
- Seeds set in same process (shared state with training code)
- Can capture exceptions properly
- ATZ handles ARGoS subprocess internally anyway

```python
# orchestrator/runner.py
import importlib.util

def run_experiment(config_path: str) -> str:
    config = load_config(config_path)
    output_dir = create_output_dir(config)

    # Seed BEFORE importing training script
    set_all_seeds(config["experiment"]["seed"])

    # Setup logging callback
    callbacks = [MetricsLogger(output_dir)]

    # Dynamic import
    spec = importlib.util.spec_from_file_location(
        "training_script",
        config["training"]["script"]
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Call training entry point
    module.main(config, callbacks, output_dir)

    return output_dir
```

### Training Script Convention

Training scripts must export a `main(config, callbacks, output_dir)` function:

```python
# training/aggregation.py

def main(config: dict, callbacks: list, output_dir: str):
    """
    Training entry point called by platform orchestrator.

    Args:
        config: Full experiment config dict
        callbacks: List of RLlib callbacks (includes platform's MetricsLogger)
        output_dir: Path for checkpoints (results/exp_<ts>/)
    """
    from zoo.argos_env import ArgosEnv
    from zoo.scenarios.aggregation import aggregation_reward
    from ray.rllib.algorithms.ppo import PPOConfig
    from ray.tune.registry import register_env

    # Create env (ATZ handles ARGoS subprocess internally)
    def env_creator(cfg):
        return ArgosEnv(
            argos_file=config["scenario"]["file"],
            max_steps=config.get("max_steps", 500),
            reward_fn=aggregation_reward,
            quiet=True,
        )

    register_env("argos_env", env_creator)

    # Build algorithm with platform-injected callbacks
    algo = (
        PPOConfig()
        .environment("argos_env")
        .callbacks(callbacks)  # Platform's MetricsLogger included
        .framework("torch")
        .build()
    )

    # Training loop
    iterations = config.get("training", {}).get("iterations", 100)
    for i in range(iterations):
        result = algo.train()

        # Save checkpoint periodically
        if (i + 1) % 10 == 0:
            algo.save(f"{output_dir}/checkpoints/iter_{i+1}")

    algo.stop()
```

### ATZ Integration Notes

From ArgosToZooArchitecture.md:
- `ArgosEnv` manages ARGoS subprocess internally
- Seeding: `env.reset(seed=X)` rewrites `.argos` file and restarts simulator
- No manual glue script needed (R2.3 satisfied)
- Reward logic via external `reward_fn` callback (task-agnostic design)

---

## Component 4: Logging System

**File:** `logging/callbacks.py`

**Requirements served:** R2.4

### Interface

```python
# logging/callbacks.py
from ray.rllib.algorithms.callbacks import DefaultCallbacks

class MetricsLogger(DefaultCallbacks):
    """RLlib callback that logs metrics to JSONL file."""

    def __init__(self, output_dir: str):
        super().__init__()
        self.log_path = Path(output_dir) / "logs" / "metrics.jsonl"

    def on_train_result(self, *, algorithm, result, **kwargs):
        """Called after each training iteration."""
        metrics = {
            "iteration": result["training_iteration"],
            "episode_reward_mean": result["episode_reward_mean"],
            "timestamp": datetime.now().isoformat(),
            # ... other metrics
        }
        self._append_log(metrics)

    def _append_log(self, metrics: dict):
        with open(self.log_path, "a") as f:
            f.write(json.dumps(metrics) + "\n")
```

### Logged Metrics

| Metric | Source | Purpose |
|--------|--------|---------|
| `iteration` | RLlib result | Progress tracking |
| `episode_reward_mean` | RLlib result | Learning curve, M3.1/M3.2 |
| `episode_reward_min/max` | RLlib result | Variance analysis |
| `timestamp` | System | Timing analysis |
| `loss` | RLlib result | Training diagnostics |

### Notes
- Essential metrics for MVP (Decision L4): `iteration`, `episode_reward_mean`, `loss`, `timestamp`
- Log frequency: every iteration (simple, can optimize later if needed)
- Extensible: can add more metrics without breaking changes

---

## Component 5: Analysis System

**Files:** `analysis/report.py`, `analysis/compare.py`

**Requirements served:** R2.5, R3.2

### Interfaces

```python
# analysis/report.py

def generate_report(experiment_dir: str, reference_dir: str = None) -> str:
    """
    Generate analysis report for experiment.

    Args:
        experiment_dir: Path to experiment results
        reference_dir: Optional reference for comparison (M3.1)

    Returns: Path to report directory
    """
    pass

def plot_learning_curve(log_path: str, output_path: str):
    """Generate learning curve plot from metrics log."""
    pass
```

```python
# analysis/compare.py

def compare_runs(run_dir: str, reference_dir: str, tolerance: float = 0.01) -> dict:
    """
    Compare run against reference for reproducibility (M3.1).

    Returns:
        {
            "final_reward_match": bool,
            "final_reward_deviation": float,
            "auc_match": bool,
            "auc_deviation": float,
            "passed": bool  # both within tolerance
        }
    """
    pass

def calculate_auc(log_path: str) -> float:
    """Calculate area under learning curve."""
    pass
```

### Notes
- Plotting library: matplotlib (Decision L6) - simple, thesis-ready PNGs
- AUC calculation: trapezoidal integration (standard approach)

---

## Component 6: Export System

**Files:** `export/bundle.py`, `export/importer.py`

**Requirements served:** R5.1, R5.2, R5.3, R5.4

### Bundle Format

```
bundle.zip
├── manifest.yaml         # Bundle metadata
├── config.yaml           # Frozen experiment config
├── scenario.argos        # Copy of scenario file
├── train.py              # Copy of training script
├── env_fingerprint.yaml  # Environment metadata
├── logs/
│   └── metrics.jsonl
└── checkpoints/          # Optional
```

### Interfaces

```python
# export/bundle.py

def export_bundle(experiment_dir: str, output_path: str = None) -> str:
    """
    Create shareable bundle from experiment.

    Returns: Path to created bundle.zip
    """
    pass

def create_manifest(experiment_dir: str) -> dict:
    """Create bundle manifest with metadata."""
    pass
```

```python
# export/importer.py

def import_bundle(bundle_path: str, target_dir: str = None) -> str:
    """
    Import bundle and prepare for reproduction.

    Returns: Path to imported experiment directory
    """
    pass

def compare_fingerprints(bundle_fp: dict, current_fp: dict) -> dict:
    """
    Compare environment fingerprints.

    Returns: {field: (bundle_value, current_value, match)}
    """
    pass
```

### Notes
- Include checkpoints: by default (Decision L5) - simplifies reproduction
- Bundle compression: standard ZIP deflate (good enough for MVP)

---

## Component 7: Utils

**Files:** `utils/seeds.py`, `utils/fingerprint.py`

### Seed Propagation

```python
# utils/seeds.py

def set_all_seeds(seed: int):
    """
    Propagate seed to all RNG sources.

    Sources:
    - random.seed(seed)
    - np.random.seed(seed)
    - torch.manual_seed(seed)
    - torch.cuda.manual_seed_all(seed)
    """
    pass
```

### Environment Fingerprint

```python
# utils/fingerprint.py

def capture_fingerprint() -> dict:
    """
    Capture current environment metadata.

    Returns:
        {
            "python": "3.x.x",
            "os": "Linux/macOS",
            "packages": {
                "rllib": "x.x.x",
                "torch": "x.x.x",
                "numpy": "x.x.x",
            },
            "captured_at": "ISO timestamp"
        }
    """
    pass

def save_fingerprint(fingerprint: dict, path: str):
    """Save fingerprint to YAML file."""
    pass
```

---

## Resolved Questions

| # | Component | Question | Decision | Rationale |
|---|-----------|----------|----------|-----------|
| Q1 | CLI | Command style | Subcommands (L1) | Standard CLI; Typer handles `import_` → `import` |
| Q2 | Config | Validation library | pydantic (L3) | Modern, good errors, type hints |
| Q3 | Orchestrator | Execution model | Dynamic import (L2) | Can inject callbacks, shared seed state |
| Q4 | Orchestrator | Training script signature | `main(config, callbacks, output_dir)` | Matches ATZ patterns |
| Q5 | Logging | Essential metrics | reward_mean, loss, iteration, timestamp (L4) | M3.1/M3.2 + training diagnostics |
| Q6 | Analysis | Plotting library | matplotlib (L6) | Simple, thesis-ready PNGs |
| Q7 | Export | Include checkpoints | By default (L5) | Simplifies reproduction |

## Remaining Open Questions

| #   | Component | Question                | Status | Resolution |
| --- | --------- | ----------------------- | ------ | ---------- |
| Q8  | Config    | Hash: include comments? | Open   | Probably normalize (strip comments) - decide during implementation |
| Q9  | CLI       | Error display format    | Resolved | L8: Structured format (message + context + fix) |

---

## Next Steps
- [x] Finalize remaining open questions (Q9 resolved)
- [x] Review interfaces for completeness
- [x] Create GitHub issues for implementation → See `docs/Sprint-Issues-CLI.md`
- [ ] Create MVP repository (separate from thesis repo)
- [ ] Set up MVP repo with CLAUDE.md context
