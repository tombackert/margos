# Protocol-SRQ1-Architecture

## Header

| Field                | Value                                                                                                                                                                                       |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Protocol ID**      | P-SRQ1                                                                                                                                                                                      |
| **SRQ Reference**    | SRQ1: What architectural design enables execution of the evaluation protocols for SRQ2-5 and collection of their required metrics?                                                          |
| **Hypothesis**       | H1: A modular, config-driven CLI architecture enables measurement of efficiency metrics (SRQ2), reproducibility metrics (SRQ3), usability metrics (SRQ4), and collaboration metrics (SRQ5). |
| **Success Criteria** | All SRQ2-5 evaluation protocols can be executed and produce the specified metrics                                                                                                           |
| **Sample Size**      | N/A (descriptive, not empirical)                                                                                                                                                            |
| **Dependencies**     | Platform implementation complete                                                                                                                                                            |

---

## Prerequisites

These prerequisites are recorded against the completed evaluation runs and evidence captured in-repo, not against the current post-hoc CI state of the repository.

### Required Artifacts
- [x] Implemented platform with all components
- [x] CLI interface operational (`run`, `compare`, `export`, `import`)
- [x] Config system functional (load, validate, hash)
- [x] Logging system producing JSONL metrics
- [x] Export/import system creating valid bundles

### Environment Setup
- [x] Platform installed and accessible via CLI
- [x] Test experiment configs prepared
- [x] ARGoS + RLlib integration working

### Pre-Execution Checklist
- [x] Relevant reproducibility unit tests executed and captured (`docs/experiments/evidence/SRQ3/unit_tests_output.txt`)
- [x] Platform can execute a basic experiment end-to-end
- [x] Documentation exists for all primary CLI commands

---

## Definitions

### Key Terms

| Term                      | Definition                                                                         |
| ------------------------- | ---------------------------------------------------------------------------------- |
| **Enablement**            | A feature is "enabled" if its corresponding SRQ protocol can execute without error |
| **Metric Collection**     | The ability to capture and record the specified measurement                        |
| **Architectural Feature** | A designed component of the platform (CLI, config system, etc.)                    |

### Controlled Variables
- N/A (descriptive evaluation)

### Validation Logic
SRQ1 is validated **indirectly**: If SRQ2-5 evaluations can be executed and produce meaningful data, then the architecture was sufficient.

---

## Procedure

### Step 1: Feature-to-Metric Traceability Audit

For each SRQ, verify the architectural feature enables the required metric collection.

| SRQ   | Required Data                         | Platform Feature                                                | Enables Metric   |
| ----- | ------------------------------------- | --------------------------------------------------------------- | ---------------- |
| SRQ2  | Time-to-Complete                      | Single CLI entry point via `platform run`                       | M2.1             |
| SRQ2  | Steps-to-Complete                     | Config-driven end-to-end execution from one command             | M2.2             |
| SRQ3  | Reproduce-Success-Rate                | Deterministic seed control + `platform compare`                 | M3.1             |
| SRQ3  | Result-Variance                       | JSONL metrics logging and comparison tooling                    | M3.2             |
| SRQ3  | Config-Integrity                      | Frozen config + SHA256 config hash                              | M3.3             |
| SRQ3  | Seed-Determinism                      | Centralized RNG propagation before dynamic import               | M3.4             |
| SRQ4  | Heuristic-Compliance-Rate             | Consistent CLI structure, help text, and structured errors      | M4.4             |
| SRQ4  | KLM-Predicted-Time / KLM-Reduction    | Compressed workflows via `run`, `compare`, `export`, `import`   | M4.5-M4.6        |
| SRQ5  | Steps-to-Share                        | `platform export` bundle creation                               | M5.1             |
| SRQ5  | Time-to-Share                         | `platform export` bundle creation                               | M5.2             |
| SRQ5  | Time-to-First-Run                     | `platform import` + imported-config execution path              | M5.3             |
| SRQ5  | Time-to-Reproduce                     | `platform import` + `platform run` / `platform compare`         | M5.4             |
| SRQ5  | Handoff-Success-Rate                  | Bundle validation and import/export flow                        | M5.5             |
| SRQ5  | Bundle-Completeness                   | Manifest + bundled config/logs/scenario/script/checkpoints      | M5.6             |
| SRQ5  | Setup-Divergence                      | Environment fingerprint capture and comparison                  | M5.7             |

### Step 2: Protocol Execution Test

Attempt to execute each SRQ2-5 protocol:

| Protocol                 | Execution Attempt   | Result   | Blocking Issues                                                                                                            |
| ------------------------ | ------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------- |
| P-SRQ2 (Efficiency)      | [x]                 | Pass     | None; completed trials produced `M2.1` and `M2.2` (`docs/experiments/evidence/SRQ2/analysis_summary.md`)                   |
| P-SRQ3 (Reproducibility) | [x]                 | Pass     | None; 20/20 reproductions and unit-test checks produced `M3.1-M3.4` (`docs/experiments/evidence/SRQ3/analysis_summary.md`) |
| P-SRQ4 (Usability)       | [x]                 | Pass     | None; heuristic audit and 7 KLM analyses produced `M4.4-M4.6` (`docs/experiments/evidence/SRQ4/analysis_summary.md`)       |
| P-SRQ5 (Collaboration)   | [x]                 | Pass     | None; 20 handoff cycles produced `M5.1-M5.7` (`docs/experiments/evidence/SRQ5/analysis_summary.md`)                        |

### Step 3: ADR Documentation Audit

Verify all architectural decisions are documented:

| ADR ID   | Decision                                                    | Documented?   | Location                                                                 |
| -------- | ----------------------------------------------------------- | ------------- | ------------------------------------------------------------------------ |
| L1       | CLI command style (subcommands)                             | [x]           | `docs/LowLevelArchitectureBrainstorm.md` (`L1`, `Q1`)                    |
| L2       | Execution model (dynamic import)                            | [x]           | `docs/LowLevelArchitectureBrainstorm.md` (`L2`, `Execution Model`, `Q3`) |
| L3       | Validation library (pydantic)                               | [x]           | `docs/LowLevelArchitectureBrainstorm.md` (`L3`, `Config System`, `Q2`)   |
| L4       | Essential metrics (reward_mean, loss, iteration, timestamp) | [x]           | `docs/LowLevelArchitectureBrainstorm.md` (`L4`, `Logging System`, `Q5`)  |
| L5       | Checkpoints in bundle (include by default)                  | [x]           | `docs/LowLevelArchitectureBrainstorm.md` (`L5`, `Export System`, `Q7`)   |
| L6       | Plotting library (matplotlib)                               | [x]           | `docs/LowLevelArchitectureBrainstorm.md` (`L6`, `Analysis`, `Q6`)        |
| L7       | CLI argument style (convention over configuration)          | [x]           | `docs/LowLevelArchitectureBrainstorm.md` (`L7`, `Commands`, `Q8`)        |
| L8       | Error display format (structured)                           | [x]           | `docs/LowLevelArchitectureBrainstorm.md` (`L8`, `Error Handling`, `Q9`)  |

---

## Data Collection

### Enablement Checklist

| Component              | Required For           | Functional?   | Notes                                                                                 |
| ---------------------- | ---------------------- | ------------- | ------------------------------------------------------------------------------------- |
| CLI `run` command      | SRQ2, SRQ4, SRQ5       | [x]           | Implemented in `marl_platform/cli.py`; used to execute configs and imported bundles   |
| CLI `compare` command  | SRQ3, SRQ5             | [x]           | Implemented in `marl_platform/cli.py`; compares reward and AUC across experiments     |
| CLI `export` command   | SRQ5                   | [x]           | Implemented in `marl_platform/cli.py` + `marl_platform/export/bundle.py`              |
| CLI `import` command   | SRQ5                   | [x]           | Implemented in `marl_platform/cli.py` + `marl_platform/export/importer.py`            |
| Config loader          | SRQ2, SRQ3, SRQ4, SRQ5 | [x]           | `load_config()` resolves YAML into validated platform config                          |
| Config validator       | SRQ2, SRQ3, SRQ4, SRQ5 | [x]           | Pydantic schema in `marl_platform/config/schema.py` with structured validation errors |
| Config hasher          | SRQ3, SRQ5             | [x]           | `hash_config()` writes `config_hash.txt` for integrity checks                         |
| Seed propagation       | SRQ3                   | [x]           | `set_all_seeds()` runs before training-script import                                  |
| Metrics logger (JSONL) | SRQ2, SRQ3             | [x]           | `MetricsLogger` writes `logs/metrics.jsonl` per iteration                             |
| Env fingerprint        | SRQ3, SRQ5             | [x]           | `capture_fingerprint()` / `save_fingerprint()` persist environment metadata           |
| Bundle creator         | SRQ5                   | [x]           | `export_bundle()` packages config, fingerprint, logs, script, scenario, checkpoints   |
| Bundle importer        | SRQ5                   | [x]           | `import_bundle()` validates bundle, extracts it, and rewrites config paths            |

### Architecture Requirements Verification

| Requirement                | Why (Data Purpose)                            | From SRQ   | Implemented?   | Implemented Behavior                                                                                       |
| -------------------------- | --------------------------------------------- | ---------- | -------------- | ---------------------------------------------------------------------------------------------------------- |
| Single CLI entry point     | Measure Steps-to-Complete                     | SRQ2       | [x]            | Typer app exposes a single `platform` entry point with subcommands in `marl_platform/cli.py`               |
| Unified config file        | Measure step reduction, enable config hashing | SRQ2, SRQ3 | [x]            | `load_config()` + `PlatformConfig` validate one YAML file; `save_frozen_config()` stores the executed copy |
| Deterministic seed control | Measure Reproduce-Success-Rate                | SRQ3       | [x]            | `set_all_seeds()` seeds Python, NumPy, and Torch before dynamic import in `run_experiment()`               |
| Config hash at runtime     | Verify Config-Integrity                       | SRQ3       | [x]            | `hash_config()` computes SHA256 and writes `config_hash.txt` into the result bundle                        |
| Clear error messages       | Measure Error-Rate, Recovery-Time             | SRQ4       | [x]            | `PlatformError` + `display_error()` emit `message`, contextual fields, and a concrete fix                  |
| Export command             | Measure Steps-to-Share, Time-to-Share         | SRQ5       | [x]            | `platform export` packages the experiment into a validated shareable ZIP bundle                            |
| Import command             | Measure Time-to-First-Run, Time-to-Reproduce  | SRQ5       | [x]            | `platform import` extracts the bundle, rewrites config paths, and enables direct rerun / comparison        |

---

## Analysis

### Validation Criteria

H1 is validated if:
1. **All SRQ2-5 protocols execute** without architectural blockers
2. **All specified metrics are collectable** via platform features
3. **ADRs are documented** for all design decisions

### Interpretation

| Outcome             | Interpretation                          |
| ------------------- | --------------------------------------- |
| All protocols run   | Architecture sufficient - H1 supported  |
| Some protocols fail | Architecture incomplete - identify gaps |
| No protocols run    | Architecture fundamentally inadequate   |

### Validation Statement

`SRQ2`, `SRQ3`, `SRQ4`, and `SRQ5` were executed successfully and produced the required metrics: `M2.1-M2.2`, `M3.1-M3.4`, `M4.4-M4.6`, and `M5.1-M5.7`. Their downstream hypothesis outcomes differ (`H2` supported, `H3` strongly supported, `H4` supported, `H5` partially supported based on the corrected SRQ5 evidence), but none of the protocols encountered an architectural blocker and each produced the intended evidence. On that basis, `H1` is supported: the implemented architecture was sufficient to execute the evaluation plan and collect its required metrics.

### Reporting

In thesis, report:
1. **Evaluation-Driven Requirements**: Table mapping SRQ metrics to architectural features
2. **Architecture Description**: Layers, modules, data flow (descriptive)
3. **Design Rationale**: ADRs explaining choices, referencing literature
4. **Validation Statement**: "The architecture was validated by successful execution of SRQ2-5 evaluations"

---

## Evidence Checklist

- [x] Feature-to-metric traceability table complete
- [x] All SRQ2-5 protocol execution attempts documented
- [x] ADR documentation audit complete
- [x] Enablement checklist complete
- [ ] Screenshot/log of successful protocol initiations (optional for closeout; not added in-repo)

---

## Limitations

| Limitation                             | Mitigation                                                                                   |
| -------------------------------------- | -------------------------------------------------------------------------------------------- |
| Architecture is necessary, not optimal | Explicitly state: "sufficient to enable measurement, not claimed to be best possible design" |
| No independent expert review           | Document rationale via ADRs referencing established patterns (12-Factor, Unix philosophy)    |
| Self-designed and self-validated       | Validation is objective: protocols either run or they don't                                  |

---

## References

- `docs/HighLevelArchitectureBrainstorm.md` - SRQ1 reframing, evaluation-driven validation logic, and reporting expectations
- `docs/LowLevelArchitectureBrainstorm.md` - component structure and documented decisions `L1-L8`
- `docs/ResearchPlan.md` - SRQ1, H1, E1 definitions
- `docs/experiments/evidence/SRQ2/analysis_summary.md` - SRQ2 completion and metrics
- `docs/experiments/evidence/SRQ3/analysis_summary.md` - SRQ3 completion and metrics
- `docs/experiments/evidence/SRQ4/analysis_summary.md` - SRQ4 completion and metrics
- `docs/experiments/evidence/SRQ5/analysis_summary.md` - SRQ5 completion and metrics
