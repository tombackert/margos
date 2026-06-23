# Design Brainstorm 

## Goal
- Thesis Goal: The goal is a rigorous, scientifically proofed and structured manuscript. The MVP being built is a means to an end - the end is insights from examining the MVP (the data collected), not an economically valuable product.
- Design Goal: The MVP has the sole purpose of making the ResearchPlan possible. Every feature must be directly in favor of hitting this goal.   


## Risk
Risk: Building MVP to enable predefined hypothesis testing could be perceived as "steering results" rather than conducting novel research
Key Insights: 
- You're building an architecture that enables fair testing, not one that guarantees passing. Margos could easily fail to meet thresholds - that's what makes it science.
- Objective Comparison: Margos vs Manual baseline is an objective empirical test - the data will show the truth regardless of hopes
- SRQ1 explicitly asks "What architecture enables measurement?" not "What architecture maximizes results?"
- Even if all thresholds are missed, you've answered: "To what extent does integration improve workflow?" The answer might be "very little" - that's still a valid research contribution.


## Decisions

| #   | Decision                      | Details                                                                                                               |
| --- | ----------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| D1  | Requirements Capture Approach | SRQ-Driven Traceability Matrix: Derive requirements directly from SRQ evaluation protocols, not traditional use cases |

### D1: Requirements Capture Approach

Risk: Reviewer can ask "why choose this approach over traditional use cases/user stories?"

Justification:
- We need an MVP that enables SRQ evaluation, not a commercial product
- Every feature must trace back to an SRQ (SRQs-First Principle)
- Traditional methods (user stories, use cases) would capture "nice-to-have" features and require extra filtering
- SRQ-driven derivation guarantees minimum scope and direct traceability

Method:
1. For each SRQ, extract what the MVP must do to run its evaluation protocol
2. Create traceability matrix: Requirement → SRQ(s) served
3. MoSCoW prioritize: Must = required for evaluation, Should = significant value

Priority Key:
- Must = Required to run evaluation protocol -> Minimal Usable Subset
- Should = Give significant value, but not vital for direct Release

## Next Steps
- [x] Decide: How to systematically capture requirements? → D1
- [x] Derive requirements from SRQ2 (Efficiency)
- [x] Derive requirements from SRQ3 (Reproducibility)
- [x] Derive requirements from SRQ4 (Usability)
- [x] Derive requirements from SRQ5 (Collaboration)
- [x] Consolidate requirements + traceability matrix
- [x] Define minimal workflows → WorkflowBrainstorm.md (4 workflows + cycle)
- [x] Technical decisions (T1-T7) → See Technical Decisions section
- [x] Design the high level architecture
	- Component interaction: Direct calls (simpler for MVP)
	- Write model: Hybrid (each component writes its own concern)
	- Decisions: A1 (JSONL), A2 (Typer), A4 (config path); A3 deferred
- [x] Design the low level architecture (component internals)
	- Goal: Module structure, class diagrams, detailed interfaces
	- Decisions L1-L8 documented in LowLevelArchitectureBrainstorm.md
- [x] GitHub issues ready to be worked on → `docs/Sprint-Issues-CLI.md`

---

## SRQ2 Requirements Derivation (Efficiency)

### What SRQ2 Evaluation Needs

From EfficiencyBrainstorm, the evaluation protocol compares:

Condition A (Manual - 11 steps):

| Phase    | Step | Action                              |
| -------- | ---- | ----------------------------------- |
| Setup    | 1    | Create ARGoS config (.argos)        |
| Setup    | 2    | Create RLlib config (.yaml/.py)     |
| Setup    | 3    | Write glue script (ARGoS ↔ RLlib)   |
| Setup    | 4    | Configure paths, seeds, parameters  |
| Setup    | 5    | Debug integration issues            |
| Training | 6    | Start training manually             |
| Training | 7    | Monitor training (tensorboard/logs) |
| Training | 8    | Wait for completion                 |
| Analysis | 9    | Extract logs/metrics                |
| Analysis | 10   | Create plots                        |
| Analysis | 11   | Export results                      |

Condition B (Margos - 4 steps):

| Phase    | Step | Action                             |
| -------- | ---- | ---------------------------------- |
| Setup    | 1    | Create unified config              |
| Training | 2    | `margos run --config exp.yaml`   |
| Training | 3    | (Auto-logging during training)     |
| Analysis | 4    | `margos report --experiment exp` |

### Derived Requirements for SRQ2

From ResearchPlan.md, E2 (Efficiency) measures:
- [[M2.1]] -> Time-to-Complete (human effort time) 
- [[M2.2]] -> Steps-to-Complete (manual actions)

| ID   | Requirement                         | Rationale                                                 | Priority | Eval Metric Enabled | SRQ  | Component             |
| ---- | ----------------------------------- | --------------------------------------------------------- | -------- | ------------------- | ---- | --------------------- |
| R2.1 | Experiment config file              | Bundles scenario + training script references + seed. Enables single `run` command | Must     | [[M2.1]], [[M2.2]]  | SRQ2 | Config System         |
| R2.2 | `run` command                       | Single command to start training (replaces step 6)        | Must     | [[M2.1]], [[M2.2]]  | SRQ2 | CLI                   |
| R2.3 | Auto-integration ARGoS ↔ RLlib      | Eliminates glue script (step 3) and debugging (step 5)    | Must     | [[M2.1]], [[M2.2]]  | SRQ2 | Bridge (ArgosToZoo)   |
| R2.4 | Auto-logging during training        | Captures metrics without manual extraction (step 9)       | Must     | [[M2.1]], [[M2.2]]  | SRQ2 | Logging System        |
| R2.5 | `report` command                    | Generates analysis/plots (replaces steps 10-11)           | Must     | [[M2.1]], [[M2.2]]  | SRQ2 | CLI + Analysis System |
| R2.6 | Progress indication during training | Replaces manual monitoring (step 7)                       | Should   | [[M2.1]] (marginal) | SRQ2 | CLI                   |

Cross-SRQ Note: R2.1 (config) and R2.4 (logging) will likely also serve SRQ3 (Reproducibility). Captured during SRQ3 derivation.

### What R2.1-R2.5 Must Support (Minimum)

R2.1 Experiment Config:
- Reference to scenario file (.argos)
- Reference to training script (.py)
- Seed (single source, propagated to all RNG)
- Experiment metadata (name)
- Output directory

Note: Hyperparameters stay in training script. Config only bundles references for orchestration.

R2.2 `run` Command:
- Input: config file path
- Action: Start training with specified config
- Output: Training artifacts (logs, checkpoints)

R2.3 Auto-integration:
- Bridge between ARGoS simulator and RLlib (ArgosToZoo or similar)
- No manual glue script required from user

R2.4 Auto-logging:
- Capture training metrics (reward, loss, etc.)
- Store in structured format (for report generation, data export)
- Timestamped entries

R2.5 `report` Command:
- Input: experiment identifier
- Output: Summary plots (learning curve, final metrics)
- Export format: PNG/PDF for thesis inclusion


## SRQ3 Requirement Derivation (Reproducibility)

### What SRQ3 Evaluation Needs

From ResearchPlan.md, E3 (Reproducibility) measures:

| Metric                                 | Type        | ID       |
| -------------------------------------- | ----------- | -------- |
| Reproduce-Success-Rate (±1% tolerance) | Empirical   | [[M3.1]] |
| Result-Variance                        | Empirical   | [[M3.2]] |
| Config-Integrity                       | By Design   | [[M3.3]] |
| Seed-Determinism                       | By Design   | [[M3.4]] |

**Evaluation Protocol:**
1. Reference run → save as ground truth
2. N reproduction attempts (N≥10)
3. Compare each against reference (±1% on final reward AND AUC)
4. Calculate success rate and variance
5. Verify Config-Integrity + Seed-Determinism via unit tests

### Derived Requirements for SRQ3

| ID   | Requirement                 | Rationale                                                     | Priority | Eval Metric Enabled | SRQ  | Component       |
| ---- | --------------------------- | ------------------------------------------------------------- | -------- | ------------------- | ---- | --------------- |
| R3.1 | Centralized seed management | All RNG sources seeded from single config value               | Must     | [[M3.1]], [[M3.4]]  | SRQ3 | Config System   |
| R3.2 | Reproducibility comparison  | Compare final reward + AUC against reference (±1% tolerance)  | Must     | [[M3.1]]            | SRQ3 | Analysis System |
| R3.3 | Config hashing              | Config hash stored with experiment for integrity verification | Must     | [[M3.3]]            | SRQ3 | Config System   |

Cross-SRQ Dependencies:
- R2.1 (Unified config) also serves SRQ3: seeds defined in config
- R2.4 (Auto-logging) also serves SRQ3: reward logging enables [[M3.2]] (variance calculation)

### What R3.1-R3.3 Must Support (Minimum)

R3.1 Centralized Seed Management:
- Single seed value in config controls all RNG sources
- ARGoS simulation RNG
- RLlib/ML framework RNG
- Python random, numpy random

R3.2 Reproducibility Comparison:
- Input: current run results + reference run identifier
- Compare final reward: `|run - ref| / ref ≤ 0.01`
- Compare AUC: `|run - ref| / ref ≤ 0.01`
- Output: pass/fail + deviation values

R3.3 Config Hashing:
- Hash config at experiment start
- Store hash with experiment results
- Enable verification: hash at load vs hash at completion


## SRQ4 Requirement Derivation (Usability)

### What SRQ4 Evaluation Needs

From ResearchPlan.md, E4 (Usability) measures:

| Metric                    | Type       | ID       |
| ------------------------- | ---------- | -------- |
| Time-to-First-Success     | Empirical  | [[M4.1]] |
| Error-Rate                | Empirical  | [[M4.2]] |
| Recovery-Time             | Empirical  | [[M4.3]] |
| Heuristic-Compliance-Rate | Audit      | [[M4.4]] |
| KLM-Predicted-Time        | Analytical | [[M4.5]] |
| KLM-Reduction             | Analytical | [[M4.6]] |
| Documentation-Lookups     | Empirical  | [[M4.7]] |

Evaluation Protocol:
1. Task-based trials (7 tasks × 3 trials) → measure time, errors, recovery
2. Nielsen's heuristic audit (35 criteria) → compliance score
3. GOMS/KLM operator analysis → predicted time comparison
4. Error analysis → error patterns and recovery

Tasks: T1-Configure, T2-Modify, T3-Train, T4-Monitor, T5-Results, T6-Export, T7-Import

### Derived Requirements for SRQ4

*NH = Nielsen Heuristic (not thesis hypothesis)*

| ID   | Requirement           | Rationale                                           | Priority | Eval Metric Enabled       | SRQ  | Component     |
| ---- | --------------------- | --------------------------------------------------- | -------- | ------------------------- | ---- | ------------- |
| R4.1 | Config validation     | Enables NH5 (Error Prevention) criteria measurement | Must     | [[M4.4]] (NH5), [[M4.2]]  | SRQ4 | Config System |
| R4.2 | Clear error messages  | Enables meaningful Recovery-Time and NH9 criteria   | Must     | [[M4.3]], [[M4.4]] (NH9)  | SRQ4 | CLI           |
| R4.3 | Help command          | Enables Documentation-Lookups and NH10 criteria     | Must     | [[M4.7]], [[M4.4]] (NH10) | SRQ4 | CLI           |
| R4.4 | Consistent CLI syntax | Improves NH4 (Consistency) compliance               | Should   | [[M4.4]] (NH4)            | SRQ4 | CLI           |

Cross-SRQ Dependencies:
- R2.1-R2.5 enable tasks T1-T5 (configure, modify, train, monitor, results)
- R2.6 (Progress indication) serves SRQ4: enables NH1 (System Status) criteria
- T6-T7 (Export/Import) covered by SRQ5 requirements

### What R4.1-R4.3 Must Support (Minimum)

R4.1 Config Validation:
- Validate config structure before run starts
- Check required fields present
- Check parameter types/ranges
- Report validation errors with field location

R4.2 Clear Error Messages:
- Plain language (not stack traces)
- Identify what went wrong
- Suggest how to fix
- Include relevant context (file, line, value)

R4.3 Help Command:
- `--help` flag on all commands
- Usage examples
- Parameter descriptions
- Quick reference for common tasks


## SRQ5 Requirement Derivation (Collaboration)

### What SRQ5 Evaluation Needs

From ResearchPlan.md, E5 (Collaboration) measures:

| Metric               | Type      | ID       |
| -------------------- | --------- | -------- |
| Steps-to-Share       | Empirical | [[M5.1]] |
| Time-to-Share        | Empirical | [[M5.2]] |
| Time-to-First-Run    | Empirical | [[M5.3]] |
| Time-to-Reproduce    | Empirical | [[M5.4]] |
| Handoff-Success-Rate | Empirical | [[M5.5]] |
| Bundle-Completeness  | Audit     | [[M5.6]] |
| Setup-Divergence     | Empirical | [[M5.7]] |

**Evaluation Protocol:**
1. Machine A: Run experiment → export bundle
2. Transfer bundle to Machine B (simulated via container/VM)
3. Machine B: Import bundle → run → verify results match
4. Compare baseline (8 manual steps) vs Margos (4 steps)

Baseline (Manual - 8 steps): Identify files → Copy → Write README → List deps → Document seeds → Document env → Package → Transfer

### Derived Requirements for SRQ5

| ID   | Requirement        | Rationale                                           | Priority | Eval Metric Enabled            | SRQ  | Component           |
| ---- | ------------------ | --------------------------------------------------- | -------- | ------------------------------ | ---- | ------------------- |
| R5.1 | `export` command   | Creates shareable bundle from experiment            | Must     | [[M5.1]], [[M5.2]], [[M5.6]]   | SRQ5 | CLI + Export System |
| R5.2 | `import` command   | Unpacks bundle and sets up for reproduction         | Must     | [[M5.3]], [[M5.5]]             | SRQ5 | CLI + Export System |
| R5.3 | Bundle format      | Standard format containing all required artifacts   | Must     | [[M5.6]]                       | SRQ5 | Export System       |
| R5.4 | Env-fingerprint    | Captures environment details for cross-env comparison | Must   | [[M5.7]]                       | SRQ5 | Export System       |

Cross-SRQ Dependencies:
- R2.2 (`run` command) enables [[M5.3]] (Time-to-First-Run)
- R3.2 (Reproducibility comparison) enables [[M5.4]] verification
- R3.3 (Config hashing) enables [[M5.7]] (Setup-Divergence detection)
- R5.1/R5.2 enable SRQ4 tasks T6 (Export) and T7 (Import)

### What R5.1-R5.4 Must Support (Minimum)

R5.1 `export` Command:
- Input: experiment identifier
- Output: bundle file (e.g., `.zip`)
- Action: Package all required artifacts

R5.2 `import` Command:
- Input: bundle file path
- Output: experiment ready to run
- Action: Unpack and configure for local environment

R5.3 Bundle Format (Contents):
```
bundle.zip
├── config.yaml           # Experiment config (frozen)
├── scenario.argos        # Copy of .argos file
├── train.py              # Copy of training script
├── env_fingerprint.yaml  # Environment metadata
├── logs/                 # Training logs
└── checkpoints/          # Model checkpoints (optional)
```
- NOT included: raw training data, large assets

R5.4 Env-Fingerprint:
- Python version
- Key package versions (RLlib, ARGoS bindings)
- OS info
- Stored in bundle for comparison on import


---

## Consolidated Requirements + Traceability Matrix

### Full Requirements Table

| ID   | Requirement                         | Priority | Primary SRQ | Also Serves | Metrics Enabled                        | Component             |
| ---- | ----------------------------------- | -------- | ----------- | ----------- | -------------------------------------- | --------------------- |
| R2.1 | Experiment config file              | Must     | SRQ2        | SRQ3        | [[M2.1]], [[M2.2]], [[M3.4]]           | Config System         |
| R2.2 | `run` command                       | Must     | SRQ2        | SRQ5        | [[M2.1]], [[M2.2]], [[M5.3]]           | CLI                   |
| R2.3 | Auto-integration ARGoS ↔ RLlib      | Must     | SRQ2        | -           | [[M2.1]], [[M2.2]]                     | Bridge (ArgosToZoo)   |
| R2.4 | Auto-logging during training        | Must     | SRQ2        | SRQ3        | [[M2.1]], [[M2.2]], [[M3.2]]           | Logging System        |
| R2.5 | `report` command                    | Must     | SRQ2        | -           | [[M2.1]], [[M2.2]]                     | CLI + Analysis System |
| R2.6 | Progress indication during training | Should   | SRQ2        | SRQ4        | [[M2.1]], [[M4.4]] (NH1)               | CLI                   |
| R3.1 | Centralized seed management         | Must     | SRQ3        | -           | [[M3.1]], [[M3.4]]                     | Config System         |
| R3.2 | Reproducibility comparison          | Must     | SRQ3        | SRQ5        | [[M3.1]], [[M5.4]]                     | Analysis System       |
| R3.3 | Config hashing                      | Must     | SRQ3        | SRQ5        | [[M3.3]], [[M5.7]]                     | Config System         |
| R4.1 | Config validation                   | Must     | SRQ4        | -           | [[M4.4]] (NH5), [[M4.2]]               | Config System         |
| R4.2 | Clear error messages                | Must     | SRQ4        | -           | [[M4.3]], [[M4.4]] (NH9)               | CLI                   |
| R4.3 | Help command                        | Must     | SRQ4        | -           | [[M4.7]], [[M4.4]] (NH10)              | CLI                   |
| R4.4 | Consistent CLI syntax               | Should   | SRQ4        | -           | [[M4.4]] (NH4)                         | CLI                   |
| R5.1 | `export` command                    | Must     | SRQ5        | SRQ4        | [[M5.1]], [[M5.2]], [[M5.6]], [[M4.1]] | CLI + Export System   |
| R5.2 | `import` command                    | Must     | SRQ5        | SRQ4        | [[M5.3]], [[M5.5]], [[M4.1]]           | CLI + Export System   |
| R5.3 | Bundle format                       | Must     | SRQ5        | -           | [[M5.6]]                               | Export System         |
| R5.4 | Env-fingerprint                     | Must     | SRQ5        | -           | [[M5.7]]                               | Export System         |

### Summary Statistics

| Category       | Count |
| -------------- | ----- |
| Total          | 17    |
| Must           | 15    |
| Should         | 2     |
| Cross-SRQ      | 8     |

### Cross-SRQ Dependency Graph

```
SRQ2 (Efficiency)
├── R2.1 ──────────► SRQ3 (seeds enable reproducibility)
├── R2.2 ──────────► SRQ5 (run enables Time-to-First-Run)
├── R2.4 ──────────► SRQ3 (logging enables variance calculation)
└── R2.6 ──────────► SRQ4 (progress enables NH1 audit)

SRQ3 (Reproducibility)
├── R3.2 ──────────► SRQ5 (comparison enables Time-to-Reproduce)
└── R3.3 ──────────► SRQ5 (config hash enables Setup-Divergence)

SRQ5 (Collaboration)
├── R5.1 ──────────► SRQ4 (export enables T6 task)
└── R5.2 ──────────► SRQ4 (import enables T7 task)
```

### Component Breakdown

| Component           | Requirements                   | Count |
| ------------------- | ------------------------------ | ----- |
| CLI                 | R2.2, R2.5, R2.6, R4.2, R4.3, R4.4, R5.1, R5.2 | 8 |
| Config System       | R2.1, R3.1, R3.3, R4.1         | 4     |
| Analysis System     | R2.5, R3.2                     | 2     |
| Logging System      | R2.4                           | 1     |
| Bridge (ArgosToZoo) | R2.3                           | 1     |
| Export System       | R5.1, R5.2, R5.3, R5.4         | 4     |

### High-Level Architecture Components

Based on requirements, the MVP needs these components:

```
┌─────────────────────────────────────────────────────────┐
│                         CLI                             │
│  run | report | export | import | --help                │
└─────────────────────┬───────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
┌───────────┐  ┌────────────┐  ┌─────────────┐
│  Config   │  │  Logging   │  │   Export    │
│  System   │  │  System    │  │   System    │
│           │  │            │  │             │
│ - Parse   │  │ - Metrics  │  │ - Bundle    │
│ - Validate│  │ - Rewards  │  │ - Env-FP    │
│ - Hash    │  │ - Timestmp │  │ - Import    │
│ - Seeds   │  │            │  │             │
└─────┬─────┘  └─────┬──────┘  └─────────────┘
      │              │
      ▼              ▼
┌─────────────────────────────────────────────────────────┐
│                  Analysis System                        │
│  - Report generation                                    │
│  - Reproducibility comparison (±1% tolerance)           │
│  - Plots (learning curve, final metrics)                │
└─────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│               Bridge (ArgosToZoo)                       │
│  - ARGoS ↔ RLlib integration                            │
│  - Environment wrapper                                  │
└─────────────────────────────────────────────────────────┘
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
    ┌───────────┐            ┌──────────┐
    │  ARGoS    │            │  RLlib   │
    │(Simulator)│            │ (MARL)   │
    └───────────┘            └──────────┘
```

### Minimal Viable Subset (Must-Have Only)

For MVP, the 15 Must requirements are:

| Component       | Must Requirements              |
| --------------- | ------------------------------ |
| CLI             | R2.2, R2.5, R4.2, R4.3, R5.1, R5.2 |
| Config System   | R2.1, R3.1, R3.3, R4.1         |
| Analysis System | R3.2                           |
| Logging System  | R2.4                           |
| Bridge          | R2.3                           |
| Export System   | R5.3, R5.4                     |

Should (defer if needed):
- R2.6 (progress)
- R4.4 (consistent syntax)

---

## Technical Decisions

### Decisions Table

| #  | Decision                | Choice                        | Rationale                                              |
|----|-------------------------|-------------------------------|--------------------------------------------------------|
| T1 | ARGoS ↔ RLlib Bridge    | ArgosToZoo (existing)         | Proven with successful E2E training runs               |
| T2 | Bridge Communication    | ZeroMQ                        | ArgosToZoo uses ZeroMQ (not ROS). Sufficient for MVP   |
| T3 | ML Framework            | PyTorch                       | State of the art, RLlib's primary backend              |
| T4 | RL Library              | RLlib (latest version)        | Best MARL support, active development                  |
| T5 | Seed Propagation        | Single seed → all RNG sources | Both ARGoS and RLlib support external seeding          |
| T6 | Containerization        | Not in MVP scope              | May containerize for distribution later, not a feature |
| T7 | Development Environment | Local Python venv             | Fast iteration during development                      |
| T8 | Config Scope            | References only (no hyperparams) | Hyperparams stay in training scripts; config bundles references |

### Experiment Structure

An experiment consists of three artifacts:

```
experiments/
├── scenarios/           # ARGoS scenario files (.argos)
│   └── footbot_10.argos
├── training/            # Training scripts (.py)
│   └── aggregation.py
└── configs/             # Experiment configs (.yaml)
    └── exp_v1.yaml
```

**Responsibility split:**

| Artifact | Contains | Created by |
|----------|----------|------------|
| Scenario (.argos) | Arena, robots, sensors, physics | User |
| Training script (.py) | Algorithm, hyperparams, reward_fn | User |
| Experiment config (.yaml) | References + seed + metadata | User (minimal) |

**Experiment config schema:**
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

**Margos' job:** Read config → inject seed → run training script with scenario → capture logs.

### ArgosToZoo Integration

**Status:** Existing, proven implementation from previous project.

**ATZ Architecture:**
```
ARGoS (C++) <--ZMQ REQ/REP--> ArgosEnv (PettingZoo) <--> RLlib
     │                              │
     └── zoo_loop_functions         └── reward_fn callback
         (batched obs/actions)          (scenario-specific)
```

**Key ATZ Components:**

| Component | Location | Role |
|-----------|----------|------|
| `ArgosEnv` | `zoo/argos_env.py` | PettingZoo ParallelEnv, manages ARGoS subprocess |
| `zmq_client` | `zoo/zmq_client.py` | ZMQ communication with retry/recovery |
| `zoo_loop_functions` | C++ plugin | Batches observations, applies actions |
| `reward_fn` | `zoo/scenarios/` | External callback for task-specific rewards |

**Margos Integration Points:**

| Margos Component | Integrates With | How |
|--------------------|-----------------|-----|
| **Config System** | `ArgosEnv` constructor | Pass: `argos_file`, `max_steps`, `reward_fn`, `quiet` |
| **Config System** | `.argos` file | Reference path in unified config |
| **Config System** | RLlib config | Algorithm, hyperparams, framework="torch" |
| **CLI (`run`)** | `ArgosEnv` | Create env instance with config params |
| **CLI (`run`)** | RLlib | `register_env()` + `algo.train()` |
| **Logging System** | RLlib callbacks | Hook training metrics (reward, loss, etc.) |
| **Seed Propagation** | `ArgosEnv.reset(seed=X)` | ATZ handles ARGoS restart + `.argos` seed rewrite |
| **Seed Propagation** | RLlib config | `config.debugging(seed=X)` |
| **Seed Propagation** | PyTorch | `torch.manual_seed(X)` before training |

**What Margos Does NOT Touch:**
- ZMQ bridge internals (ATZ handles)
- ARGoS subprocess management (ATZ handles)
- Observation/action encoding (ATZ handles)
- Reward computation (ATZ callback handles)

**Architecture Implication:**
- Margos wraps ATZ, doesn't modify it
- R2.3 satisfied by using `ArgosEnv` as-is
- Margos' job: unified config → split to ATZ params + RLlib params → orchestrate

### Seed Propagation Strategy

**Approach:** Single seed value in config propagates to all RNG sources.

| RNG Source | Seeding Method | Supported |
|------------|----------------|-----------|
| Python `random` | `random.seed(x)` | ✅ |
| NumPy | `np.random.seed(x)` | ✅ |
| PyTorch | `torch.manual_seed(x)` | ✅ |
| RLlib | Config parameter | ✅ |
| ARGoS | Config parameter | ✅ |

**Enables:** R3.1 (Centralized seed management), M3.4 (Seed-Determinism)

### Environment Fingerprint

**Purpose:** Capture environment metadata for reproducibility comparison on import.

**Contents:**
```yaml
env_fingerprint:
  python: "3.x.x"
  os: "Linux/macOS/Windows"
  packages:
    rllib: "x.x.x"
    torch: "x.x.x"
    numpy: "x.x.x"
    argos3: "x.x.x"
  captured_at: "ISO timestamp"
```

**Behavior on Import:** Display comparison (match/mismatch). User decides—no automated handling.

**Enables:** R5.4 (Env-fingerprint), M5.7 (Setup-Divergence)

---

## High-Level Architecture

### Architectural Principles

**Component Interaction: Direct Calls**
- Components import and call each other directly (function calls)
- Simpler for MVP: single process, easy debugging, type-safe
- No filesystem-mediated communication between components

**Write Model: Hybrid**
- Each component writes its own concern to the experiment directory
- Orchestrator: creates `results/exp_<ts>/`, writes `config.yaml`, `config_hash.txt`, `env_fingerprint.yaml`
- Logging System: writes to `results/exp_<ts>/logs/` (path provided by Orchestrator)
- RLlib: writes checkpoints to `results/exp_<ts>/checkpoints/`

*See Figma diagram for visual architecture.*

### Component Boundaries

| Component                 | Single Responsibility                    | Called By     | Writes To                     |
| ------------------------- | ---------------------------------------- | ------------- | ----------------------------- |
| **CLI**                   | Parse commands, route to components      | User          | -                             |
| **Config System**         | Load, validate, hash configs             | Orchestrator  | -                             |
| **Training Orchestrator** | Set seeds, execute training, coordinate  | CLI           | results/<exp>/ (config, hash, env_fp) |
| **Logging System**        | Capture metrics via RLlib callbacks      | Orchestrator  | results/<exp>/logs/           |
| **Analysis System**       | Generate reports, compare runs           | CLI           | results/<exp>/report/         |
| **Export System**         | Bundle/unbundle experiments              | CLI           | bundles/, experiments/imported/ |

### CLI Command Routing

```
CLI
 │
 ├─► run ────────► Training Orchestrator
 ├─► report ─────► Analysis System
 ├─► export ─────► Export System
 └─► import ─────► Export System
```

Note: CLI does NOT directly call Config System or Logging System.
- Config System is used internally by Training Orchestrator
- Logging System receives data from Training Orchestrator (not CLI)

### Data Flow: `margos run --config exp.yaml`

```
CLI ──► Training Orchestrator
              │
              ├─► Config System (internal)
              │    ├─► load(exp.yaml) from experiments/configs/
              │    ├─► validate (paths exist, required fields)
              │    ├─► hash config
              │    └─► return config dict
              │
              ├─► Create results/exp_<timestamp>/
              │    ├─► copy config.yaml (frozen)
              │    ├─► write config_hash.txt
              │    └─► write env_fingerprint.yaml
              │
              ├─► Set seeds (Python, NumPy, PyTorch, RLlib)
              │
              ├─► Setup Logging System (callbacks)
              │
              └─► Execute training script
                   │
                   └─► Training loop (ArgosToZoo + RLlib)
                        │
                        ├─► Logging callbacks → Orchestrator → results/logs/
                        └─► Checkpoints → results/checkpoints/
```

### Data Flow: `margos report --experiment <dir>`

```
CLI ──► Analysis System
              │
              ├─► Read results/<dir>/logs/
              ├─► Parse metrics (episode_reward, loss, etc.)
              ├─► Generate plots
              ├─► (Optional) Compare against reference dir
              │    └─► Compute ±1% tolerance check
              └─► Write to results/<dir>/report/
```

### Data Flow: `margos export --experiment <dir>`

```
CLI ──► Export System
              │
              ├─► Read results/<dir>/
              │    ├─► config.yaml
              │    ├─► env_fingerprint.yaml
              │    ├─► logs/
              │    └─► checkpoints/
              │
              ├─► Resolve and copy source files
              │    ├─► scenario.argos
              │    └─► train.py
              │
              └─► Write bundles/bundle.zip
```

### Data Flow: `margos import <bundle.zip>`

```
CLI ──► Export System
              │
              ├─► Read bundle.zip
              │
              ├─► Extract to experiments/imported/<name>/
              │
              ├─► Compare env_fingerprint (display match/mismatch)
              │
              └─► Return path (ready for `margos run`)
```

### Component Interfaces

```python
# Config System (internal, called by Orchestrator)
def load_config(path: str) -> dict
def validate_config(config: dict) -> (bool, list[str])  # valid, errors
def hash_config(config: dict) -> str

# Training Orchestrator (called by CLI)
def run_experiment(config_path: str) -> str  # returns output_dir

# Logging System (internal, managed by Orchestrator)
def create_callbacks(output_dir: str) -> RLlibCallback

# Analysis System (called by CLI)
def generate_report(experiment_dir: str, reference_dir: str = None) -> str

# Export System (called by CLI)
def export_bundle(experiment_dir: str, output_path: str = None) -> str
def import_bundle(bundle_path: str) -> str  # returns imported dir
```

### Experiment Output Structure

```
results/
└── exp_YYYYMMDD-HHMMss/
    ├── config.yaml           # Frozen copy
    ├── config_hash.txt       # SHA256
    ├── env_fingerprint.yaml  # Captured at start
    ├── logs/
    │   └── metrics.jsonl     # Per-iteration metrics
    ├── checkpoints/          # RLlib checkpoints
    └── report/               # After `margos report`
        ├── learning_curve.png
        └── summary.txt
```

### Architecture Decisions

| #   | Question                               | Choice                  | Rationale                                              | Status   |
| --- | -------------------------------------- | ----------------------- | ------------------------------------------------------ | -------- |
| A1  | Log format                             | **JSONL**               | Append-friendly, streaming, easy to parse              | Decided  |
| A2  | CLI framework                          | **Typer**               | Modern, type hints, auto --help, minimal boilerplate   | Decided  |
| A3  | Report format                          | -                       | Needs research on standard practices                   | Deferred |
| A4  | Seed/config passing to training script | **Config file path**    | Script reads config, extracts what it needs            | Decided  |
| A5  | Component interaction model            | **Direct calls**        | Simpler for MVP: single process, easy debugging        | Decided  |
| A6  | Write model                            | **Hybrid**              | Each component writes its own concern to experiment dir| Decided  |

