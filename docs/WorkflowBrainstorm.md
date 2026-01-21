# Workflow Brainstorm

Goal: Define minimal required workflows for the MVP and validate against requirements from DesignBrainstorm.md

---

## Minimal Required Workflows

1. Setup
2. End-to-End Training
3. Analysis
4. Import/Export

### Workflow Cycle (Experiment Iteration)

The workflows form a natural iteration cycle. T2-Modify (from SRQ4 tasks) is not a separate workflow—it's simply returning to Setup after Analysis.

```
┌────────────────────────────────────────────────────┐
│                                                    │
│    ┌─────────┐     ┌──────────┐     ┌──────────┐   │
└───►│  Setup  │────►│ Training │────►│ Analysis │───┘
     │ (config)│     │  (run)   │     │ (report) │
     └─────────┘     └──────────┘     └──────────┘
```

Typical iteration scenarios:
- Hyperparameter tuning: analyze results → adjust learning rate → re-run
- Scenario change: same setup → different ARGoS scenario → re-run
- Debug iteration: poor results → tweak config → retry
- Post-import adjustment: import bundle → adjust for local env → run


### Workflow 1: Setup

**Experiment structure:**
```
experiments/
├── scenarios/           # ARGoS scenario files (.argos)
├── training/            # Training scripts (.py)
└── configs/             # Experiment configs (.yaml)
```

**Setup flow:**
```
User wants to configure a new experiment
    |
    v
[Create/select scenario] --> .argos file (arena, robots, physics)
    |
    v
[Create/select training script] --> .py file (algorithm, hyperparams, reward_fn)
    |
    v
[Create experiment config] --> .yaml file (references + seed)
    |
    v
[Validate config] --> check paths exist, required fields present
    |
    v
Experiment ready for training
```

**Steps:**
1. User creates/selects scenario (.argos) - manual
2. User creates/selects training script (.py) - manual
3. User creates experiment config (.yaml) - manual (minimal)
4. Platform validates config (on run or explicit command)

**Requirements:** R2.1, R4.1

**Note:** Steps 1-2 are the researcher's core work. Step 3 is minimal (just references + seed). Platform value comes from steps 4 onwards.

---

### Workflow 2: End-to-End Training

```
User wants to run an experiment
    │
    ▼
[platform run --config exp.yaml]
    │
    ├──► Load & validate config (R4.1)
    ├──► Hash config for integrity (R3.3)
    ├──► Set all RNG seeds (R3.1)
    ├──► Execute training script with scenario (R2.3)
    │
    ▼
[Training loop - inside training script]
    │
    ├──► ArgosEnv manages ARGoS subprocess
    ├──► RLlib runs training iterations
    ├──► Auto-log metrics via callbacks (R2.4)
    ├──► Show progress (R2.6 - Should)
    │
    ▼
Training complete → artifacts saved to output dir
```

**Steps:**
1. User issues `run` command with config path
2. Platform validates config, hashes it, sets all seeds
3. Platform executes training script (which uses ArgosEnv + RLlib)
4. Logging callbacks capture metrics throughout
5. Training completes, results saved

**Requirements:** R2.2, R2.3, R2.4, R3.1, R3.3, R4.1, (R2.6)

---

### Workflow 3: Analysis

```
User wants to analyze results
    │
    ▼
[platform report --experiment exp]
    │
    ├──► Load experiment logs
    ├──► Generate plots (learning curve, final metrics)
    ├──► (Optional) Compare against reference run
    │
    ▼
Report ready (PNG/PDF)
```

**Steps:**
1. User issues `report` command
2. Platform loads logs, generates plots
3. (Optional) Compare against reference for reproducibility

**Requirements:** R2.5, R3.2

---

### Workflow 4: Export/Import (Collaboration)

```
Researcher A wants to share experiment
    │
    ▼
[platform export --experiment exp --output bundle.zip]
    │
    ├──► Package: config, seeds, env-fingerprint, checkpoints
    │
    ▼
Bundle transferred to Researcher B
    │
    ▼
[platform import bundle.zip]
    │
    ├──► Unpack bundle
    ├──► Compare env-fingerprint (warn if mismatch)
    │
    ▼
[platform run ...] ──► reproduce experiment
```

**Steps:**
1. User A exports experiment to bundle
2. Bundle contains: config, seeds, env-FP, checkpoints
3. User B imports bundle
4. User B runs to reproduce

**Requirements:** R5.1, R5.2, R5.3, R5.4

---

### Cross-Cutting: CLI UX

```
All commands support:
├──► --help (R4.3)
├──► Clear error messages (R4.2)
└──► Consistent syntax (R4.4 - Should)
```

---

## Gap Analysis: Workflows vs Requirements

| Workflow      | Requirements Used                          | Coverage    |
| ------------- | ------------------------------------------ | ----------- |
| Setup         | R2.1, R4.1                                 | ✅ Complete |
| Training      | R2.2, R2.3, R2.4, R3.1, R3.3, R4.1, (R2.6) | ✅ Complete |
| Analysis      | R2.5, R3.2                                 | ✅ Complete |
| Export/Import | R5.1, R5.2, R5.3, R5.4                     | ✅ Complete |
| CLI UX        | R4.2, R4.3, (R4.4)                         | ✅ Complete |

**Result:** All 17 requirements mapped to workflows. No gaps identified.

---

## Requirements Coverage Matrix

| Requirement | Workflow(s)            |
| ----------- | ---------------------- |
| R2.1        | Setup, Training        |
| R2.2        | Training               |
| R2.3        | Training               |
| R2.4        | Training               |
| R2.5        | Analysis               |
| R2.6        | Training (Should)      |
| R3.1        | Training               |
| R3.2        | Analysis               |
| R3.3        | Training               |
| R4.1        | Setup, Training        |
| R4.2        | CLI UX (all)           |
| R4.3        | CLI UX (all)           |
| R4.4        | CLI UX (Should)        |
| R5.1        | Export/Import          |
| R5.2        | Export/Import          |
| R5.3        | Export/Import          |
| R5.4        | Export/Import          |

---

## CLI Commands Summary

| Command                              | Workflow      | Primary Requirements |
| ------------------------------------ | ------------- | -------------------- |
| `platform run --config <file>`       | Training      | R2.2, R2.3, R2.4     |
| `platform report --experiment <exp>` | Analysis      | R2.5, R3.2           |
| `platform export --experiment <exp>` | Export/Import | R5.1, R5.3, R5.4     |
| `platform import <bundle>`           | Export/Import | R5.2                 |
| `platform <cmd> --help`              | CLI UX        | R4.3                 |


## Design Notes

- **T2-Modify Resolution:** Initially identified as a potential gap. Resolved: Modify is not a separate workflow—it's the natural cycle back to Setup after Analysis. See "Workflow Cycle" section above.
- **Reproducibility Evaluation:** The platform enables running experiments; the evaluator orchestrates N repetitions by invoking `run` multiple times. No batch/automation feature needed in MVP.
- **Env-Fingerprint on Import:** Platform displays fingerprint comparison (match/mismatch). User decides how to proceed—no automated handling required.
- **Containerization:** Decided against containerization as a platform feature. MVP runs locally (Python venv). May containerize at the end for easy setup/distribution, but not a built-in feature. Rationale: Doesn't directly serve answering an SRQ—scope control.
- **Experiment Structure (T8):** An experiment consists of three artifacts: scenario (.argos), training script (.py), and experiment config (.yaml). The config only bundles references + seed; hyperparameters stay in training scripts. This is an honest model—researchers still create scenarios and training logic, platform orchestrates and adds reproducibility/logging/export.
- **Efficiency Baseline Note:** The manual vs platform step counts in EfficiencyBrainstorm need revision to reflect this model. Platform eliminates glue scripting, debugging, log extraction, plotting, and export—but does NOT eliminate scenario/script creation. More rigorous analysis needed before evaluation.