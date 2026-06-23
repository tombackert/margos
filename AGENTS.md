# AGENTS.md - Margos MVP

This is the MVP (Minimum Viable Product) for a Bachelor's thesis. **Read this file completely before making any changes.**

---

## Project Purpose

Margos is **research infrastructure**, not a production product. Its sole purpose is to enable empirical evaluation of whether an integrated platform improves MARL experiment workflows compared to fragmented tooling.

**The MVP exists to collect data for thesis evaluation. Every feature must directly serve this goal.**

For full context, see:
- `docs/ResearchPlan.md` - Research questions, hypotheses, evaluation protocols
- `docs/DesignBrainstorm.md` - Requirements derivation, traceability matrix
- `docs/HighLevelArchitectureBrainstorm.md` - Architecture rationale
- `docs/LowLevelArchitectureBrainstorm.md` - Component interfaces, decisions L1-L8

---

## What We're Evaluating (SRQs)

| SRQ | Question | Key Metrics |
|-----|----------|-------------|
| SRQ2 | Does Margos reduce time/effort? | Time-to-Complete, Steps-to-Complete |
| SRQ3 | Does Margos improve reproducibility? | Reproduce-Success-Rate (≥90%), Result-Variance |
| SRQ4 | Is Margos learnable and error-tolerant? | Time-to-First-Success, Error-Rate, KLM-Reduction |
| SRQ5 | Does Margos simplify collaboration? | Time-to-Reproduce, Handoff-Success-Rate |

**Implication:** Features that don't help measure these metrics are out of scope.

---

## Architecture Overview

```
CLI (Typer)
 │
 ├─► run ────────► Training Orchestrator ──► ArgosToZoo + RLlib
 ├─► report ─────► Analysis System
 ├─► export ─────► Export System
 └─► import ─────► Export System
```

**Key Decisions:**
- A2: Typer for CLI
- A5: Direct function calls between components (no message bus)
- A6: Hybrid write model (each component writes its own concern)
- L7: Convention over configuration (user provides names, Margos resolves paths)

---

## Project Structure

```
margos/
├── margos/          # Python package
│   ├── __init__.py
│   ├── cli.py              # CLI entry point
│   ├── config/
│   │   ├── loader.py       # Load, validate configs
│   │   └── schema.py       # Pydantic schema
│   ├── orchestrator/
│   │   └── runner.py       # Training orchestration
│   ├── logging/
│   │   └── callbacks.py    # RLlib metrics callbacks
│   ├── analysis/
│   │   ├── report.py       # Report generation
│   │   └── compare.py      # Reproducibility comparison
│   ├── export/
│   │   ├── bundle.py       # Export bundling
│   │   └── importer.py     # Import unpacking
│   └── utils/
│       ├── errors.py       # Error types and display
│       ├── seeds.py        # Seed propagation
│       └── fingerprint.py  # Environment fingerprint
├── experiments/
│   ├── configs/            # Experiment configs (.yaml)
│   ├── scenarios/          # ARGoS scenarios (.argos)
│   └── training/           # Training scripts (.py)
├── results/                # Experiment outputs
├── bundles/                # Exported bundles
├── tests/
├── docs/
│   ├── ResearchPlan.md
│   ├── DesignBrainstorm.md
│   ├── HighLevelArchitectureBrainstorm.md
│   └── LowLevelArchitectureBrainstorm.md
└── pyproject.toml
```

---

## CLI Conventions (L7: Convention Over Configuration)

**Principle:** User provides names, Margos resolves paths. This serves SRQ2 (efficiency).

| Command | User Types | Margos Resolves To |
|---------|------------|---------------------|
| `margos run exp_v1` | `exp_v1` | `experiments/configs/exp_v1.yaml` |
| `margos report exp_123` | `exp_123` | `results/exp_123/` |
| `margos export exp_123` | `exp_123` | `results/exp_123/` → `bundles/exp_123.zip` |
| `margos import bundle.zip` | `bundle.zip` | `bundles/bundle.zip` |

**Override options exist** (e.g., `--config-dir`) but are not the default path.

---

## Component Interfaces

### Config System
```python
def load_config(path: str) -> dict
def validate_config(config: dict) -> tuple[bool, list[str]]
def hash_config(config: dict) -> str
```

### Training Orchestrator
```python
def run_experiment(config_path: str) -> str  # Returns output_dir
```

### Analysis System
```python
def generate_report(experiment_dir: str, reference_dir: str = None) -> str
def compare_runs(run_dir: str, reference_dir: str, tolerance: float = 0.01) -> dict
```

### Export System
```python
def export_bundle(experiment_dir: str, output_path: str = None) -> str
def import_bundle(bundle_path: str) -> str  # Returns imported dir
```

---

## Error Handling (L8)

All errors must follow this format:
```
Error: <What went wrong>
  <Key>: <value>
  <Key>: <value>
  Fix: <Actionable suggestion>
```

Example:
```
Error: Config file not found
  Path: experiments/configs/nonexistent.yaml
  Fix: Create the config file or check the experiment name
```

Use `--verbose` flag to show full traceback for debugging.

---

## Training Script Convention

Training scripts must export a `main()` function:

```python
def main(config: dict, callbacks: list, output_dir: str):
    """
    Args:
        config: Full experiment config dict
        callbacks: RLlib callbacks (includes Margos' MetricsLogger)
        output_dir: Path for checkpoints
    """
    # Setup env, algorithm, training loop...
```

The orchestrator calls this via dynamic import (L2).

---

## Experiment Config Schema

```yaml
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

**Note:** Hyperparameters stay in training scripts. Config only bundles references (T8).

---

## Output Structure

```
results/exp_YYYYMMDD-HHMMss/
├── config.yaml           # Frozen copy
├── config_hash.txt       # SHA256
├── env_fingerprint.yaml  # Python/package versions
├── logs/
│   └── metrics.jsonl     # Per-iteration: reward, loss, timestamp
├── checkpoints/          # RLlib checkpoints
└── report/               # After `margos report`
    ├── learning_curve.png
    └── summary.txt
```

---

## Requirements Traceability

Every feature traces to an SRQ. See `docs/DesignBrainstorm.md` for full matrix.

| Requirement | What | SRQ |
|-------------|------|-----|
| R2.2 | `run` command | SRQ2 |
| R2.5 | `report` command | SRQ2 |
| R3.1 | Centralized seed management | SRQ3 |
| R3.3 | Config hashing | SRQ3 |
| R4.2 | Clear error messages | SRQ4 |
| R5.1 | `export` command | SRQ5 |
| R5.2 | `import` command | SRQ5 |

---

## Development Guidelines

### Do
- Keep implementations minimal (MVP, not production)
- Trace features to requirements
- Follow existing patterns in codebase
- Write clear error messages with fix suggestions
- Test the happy path and common error cases

### Don't
- Add features not in requirements
- Over-engineer or add "nice-to-have" flexibility
- Create abstractions for single-use code
- Add comments to obvious code
- Build for hypothetical future needs
- Add your name to commit messages

### When Unsure
Ask: *"Does this directly help evaluate SRQ2/3/4/5?"*
- If yes → implement minimally
- If no → don't build it

---

## Key Files to Read

When starting work:
1. This file (AGENTS.md)
2. `docs/LowLevelArchitectureBrainstorm.md` - For interfaces and decisions
3. The specific component's existing code

When implementing a feature:
1. Check `docs/DesignBrainstorm.md` for requirement details
2. Check `docs/LowLevelArchitectureBrainstorm.md` for interface spec
3. Follow existing patterns in adjacent components

---

## Dependencies

Core:
- `typer` - CLI framework
- `pydantic` - Config validation
- `pyyaml` - Config parsing
- `matplotlib` - Report plots

ML/Simulation (used by training scripts):
- `ray[rllib]` - RL algorithms
- `torch` - ML backend
- ArgosToZoo - ARGoS ↔ RLlib bridge (external)

---

## Cautious Coding Workflow

For all non-trivial coding tasks, bug fixes, refactors, reviews, feature implementation, test writing, and repository edits, follow the `cautious-coding` workflow. If the skill system is available, load/use `$cautious-coding` before planning or editing.

Bias toward caution over speed:
- State assumptions before implementation when ambiguity exists.
- Surface tradeoffs instead of silently choosing between plausible interpretations.
- Prefer the simplest sufficient solution; do not add speculative abstractions or features.
- Make surgical changes only; every changed line should trace to the request.
- Define verifiable success criteria and verify before finishing.

| Principle | Prevents |
| --------- | -------- |
| Think Before Coding | Wrong assumptions, hidden confusion, missed tradeoffs |
| Simplicity First | Overengineering, speculative flexibility, bloated abstractions |
| Surgical Changes | Unrelated edits, accidental refactors, noisy diffs |
| Goal-Driven Execution | Weak success criteria, unverified fixes, incomplete task loops |

