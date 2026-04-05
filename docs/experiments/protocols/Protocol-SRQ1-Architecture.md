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

### Required Artifacts
- [ ] Implemented platform with all components
- [ ] CLI interface operational (`run`, `report`, `export`, `import`)
- [ ] Config system functional (load, validate, hash)
- [ ] Logging system producing JSONL metrics
- [ ] Export/import system creating valid bundles

### Environment Setup
- [ ] Platform installed and accessible via CLI
- [ ] Test experiment configs prepared
- [ ] ARGoS + RLlib integration working

### Pre-Execution Checklist
- [ ] All unit tests passing
- [ ] Platform can execute a basic experiment end-to-end
- [ ] Documentation exists for all CLI commands

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

| SRQ   | Required Data          | Platform Feature           | Enables Metric   |
| ----- | ---------------------- | -------------------------- | ---------------- |
| SRQ2  | Time-to-Complete       | CLI interface              | M2.1             |
| SRQ2  | Steps-to-Complete      | Single command E2E         | M2.2             |
| SRQ3  | Reproduce-Success-Rate | Deterministic seed control | M3.1             |
| SRQ3  | Result-Variance        | Structured logging         | M3.2             |
| SRQ3  | Config-Integrity       | Config hashing             | M3.3             |
| SRQ3  | Seed-Determinism       | Centralized RNG            | M3.4             |
| SRQ4  | Task-based metrics     | Clear CLI + error messages | M4.1-M4.7        |
| SRQ5  | Steps-to-Share         | Export command             | M5.1             |
| SRQ5  | Time-to-Share          | Export command             | M5.2             |
| SRQ5  | Time-to-First-Run      | Import command             | M5.3             |
| SRQ5  | Time-to-Reproduce      | Reproduce command          | M5.4             |
| SRQ5  | Handoff-Success-Rate   | Bundle system              | M5.5             |
| SRQ5  | Bundle-Completeness    | Export bundling            | M5.6             |
| SRQ5  | Setup-Divergence       | Env fingerprint            | M5.7             |

### Step 2: Protocol Execution Test

Attempt to execute each SRQ2-5 protocol:

| Protocol                 | Execution Attempt   | Result    | Blocking Issues   |
| ------------------------ | ------------------- | --------- | ----------------- |
| P-SRQ2 (Efficiency)      | [ ]                 | Pass/Fail |                   |
| P-SRQ3 (Reproducibility) | [ ]                 | Pass/Fail |                   |
| P-SRQ4 (Usability)       | [ ]                 | Pass/Fail |                   |
| P-SRQ5 (Collaboration)   | [ ]                 | Pass/Fail |                   |

### Step 3: ADR Documentation Audit

Verify all architectural decisions are documented:

| ADR ID   | Decision                                                    | Documented?   | Location   |
| -------- | ----------------------------------------------------------- | ------------- | ---------- |
| L1       | CLI command style (subcommands)                             | [ ]           |            |
| L2       | Execution model (dynamic import)                            | [ ]           |            |
| L3       | Validation library (pydantic)                               | [ ]           |            |
| L4       | Essential metrics (reward_mean, loss, iteration, timestamp) | [ ]           |            |
| L5       | Checkpoints in bundle (include by default)                  | [ ]           |            |
| L6       | Plotting library (matplotlib)                               | [ ]           |            |
| L7       | CLI argument style (convention over configuration)          | [ ]           |            |
| L8       | Error display format (structured)                           | [ ]           |            |

---

## Data Collection

### Enablement Checklist

| Component              | Required For     | Functional?   | Notes   |
| ---------------------- | ---------------- | ------------- | ------- |
| CLI `run` command      | SRQ2, SRQ4       | [ ]           |         |
| CLI `report` command   | SRQ2, SRQ4       | [ ]           |         |
| CLI `export` command   | SRQ5             | [ ]           |         |
| CLI `import` command   | SRQ5             | [ ]           |         |
| Config loader          | SRQ2, SRQ3, SRQ4 | [ ]           |         |
| Config validator       | SRQ3, SRQ4       | [ ]           |         |
| Config hasher          | SRQ3, SRQ5       | [ ]           |         |
| Seed propagation       | SRQ3             | [ ]           |         |
| Metrics logger (JSONL) | SRQ2, SRQ3       | [ ]           |         |
| Env fingerprint        | SRQ3, SRQ5       | [ ]           |         |
| Bundle creator         | SRQ5             | [ ]           |         |
| Bundle importer        | SRQ5             | [ ]           |         |

### Architecture Requirements Verification

| Requirement                | Why (Data Purpose)                            | From SRQ   | Implemented?   |
| -------------------------- | --------------------------------------------- | ---------- | -------------- |
| Single CLI entry point     | Measure Steps-to-Complete                     | SRQ2       | [ ]            |
| Unified config file        | Measure step reduction, enable config hashing | SRQ2, SRQ3 | [ ]            |
| Deterministic seed control | Measure Reproduce-Success-Rate                | SRQ3       | [ ]            |
| Config hash at runtime     | Verify Config-Integrity                       | SRQ3       | [ ]            |
| Clear error messages       | Measure Error-Rate, Recovery-Time             | SRQ4       | [ ]            |
| Export command             | Measure Steps-to-Share, Time-to-Share         | SRQ5       | [ ]            |
| Import command             | Measure Time-to-First-Run, Time-to-Reproduce  | SRQ5       | [ ]            |

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

### Reporting

In thesis, report:
1. **Evaluation-Driven Requirements**: Table mapping SRQ metrics to architectural features
2. **Architecture Description**: Layers, modules, data flow (descriptive)
3. **Design Rationale**: ADRs explaining choices, referencing literature
4. **Validation Statement**: "The architecture was validated by successful execution of SRQ2-5 evaluations"

---

## Evidence Checklist

- [ ] Feature-to-metric traceability table complete
- [ ] All SRQ2-5 protocol execution attempts documented
- [ ] ADR documentation audit complete
- [ ] Enablement checklist complete
- [ ] Screenshot/log of successful protocol initiations

---

## Limitations

| Limitation                             | Mitigation                                                                                   |
| -------------------------------------- | -------------------------------------------------------------------------------------------- |
| Architecture is necessary, not optimal | Explicitly state: "sufficient to enable measurement, not claimed to be best possible design" |
| No independent expert review           | Document rationale via ADRs referencing established patterns (12-Factor, Unix philosophy)    |
| Self-designed and self-validated       | Validation is objective: protocols either run or they don't                                  |

---

## References

- `docs/ArchitectureBrainstorm.md` - Core insight, argumentation chain, component details, and decisions (L1–L8)
- `docs/ResearchPlan.md` - SRQ1, H1, E1 definitions
