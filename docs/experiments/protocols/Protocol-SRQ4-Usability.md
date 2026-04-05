# Protocol-SRQ4-Usability

## Header

| Field            | Value                                                                                                                                                                                                                                                                                                      |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Protocol ID      | P-SRQ4                                                                                                                                                                                                                                                                                                     |
| SRQ Reference    | SRQ4: To what extent does the platform's design comply with established usability heuristics and reduce predicted interaction complexity?                                                                                                                                                                  |
| Hypothesis       | H4: The platform demonstrates strong compliance with established usability heuristics (Heuristic-Compliance-Rate ≥80%), including learnability-related criteria (H6, H10) and error-tolerance criteria (H5, H9), and significant reduction in predicted interaction time (KLM-Reduction ≥50% vs baseline). |
| Success Criteria | ≥80% heuristic compliance (28/35 criteria), ≥50% KLM reduction                                                                                                                                                                                                                                             |
| Sample Size      | 35 heuristic criteria (1 audit session) + 7 KLM task analyses (analytical)                                                                                                                                                                                                                                 |
| Dependencies     | Platform implementation complete                                                                                                                                                                                                                                                                           |

---

## Prerequisites

### Required Artifacts
- [ ] Platform CLI operational (all commands)
- [ ] Platform documentation/help system
- [ ] Test experiment configs prepared

### Environment Setup
- [ ] Platform installed and accessible
- [ ] Documentation accessible

### Pre-Execution Checklist
- [ ] 35-criteria heuristic checklist prepared
- [ ] KLM operator definitions reviewed
- [ ] SRQ2 manual workflow steps documented (source for KLM baseline)

---

## Definitions

### Key Terms

| Term                          | Definition                                                            |
| ----------------------------- | --------------------------------------------------------------------- |
| Heuristic-Compliance-Rate | Criteria met / 35 × 100%                                              |
| KLM-Predicted-Time        | Predicted task time using Keystroke-Level Model                       |
| KLM-Reduction             | (Baseline_KLM - Platform_KLM) / Baseline_KLM × 100%                   |

### KLM Operator Definitions

Source: Card, Moran, Newell (1983). *The Psychology of Human-Computer Interaction*.

| Operator        | Symbol | Time (sec) | Description                        |
| --------------- | ------ | ---------- | ---------------------------------- |
| Keystroke       | K      | 0.20       | Single key press (average typist)  |
| Point           | P      | 1.10       | Mouse movement to target           |
| Button          | B      | 0.10       | Mouse button click                 |
| Homing          | H      | 0.40       | Hand movement (keyboard <-> mouse) |
| Mental          | M      | 1.35       | Mental preparation                 |
| System Response | R(t)   | t          | Wait for system (variable)         |

---

## Procedure

### Part 1: Heuristic Compliance Audit

Evaluate platform against Nielsen's 10 heuristics using the 35-criteria checklist below.

#### H1: Visibility of System Status

| #   | Criterion                                     | Present? | Evidence |
| --- | --------------------------------------------- | -------- | -------- |
| 1.1 | Progress indicator for training runs          | Y/N      |          |
| 1.2 | Feedback after command execution              | Y/N      |          |
| 1.3 | Current state visible (running/stopped/error) | Y/N      |          |
| 1.4 | Resource usage visible (if applicable)        | Y/N      |          |

#### H2: Match Between System and Real World

| #   | Criterion                                           | Present? | Evidence |
| --- | --------------------------------------------------- | -------- | -------- |
| 2.1 | Uses MARL/Swarm domain terminology                  | Y/N      |          |
| 2.2 | Follows conventions of similar tools (RLlib, ARGoS) | Y/N      |          |
| 2.3 | Logical ordering of operations                      | Y/N      |          |

#### H3: User Control and Freedom

| #   | Criterion                             | Present? | Evidence |
| --- | ------------------------------------- | -------- | -------- |
| 3.1 | Cancel running operations             | Y/N      |          |
| 3.2 | Undo/revert config changes            | Y/N      |          |
| 3.3 | Exit from any state without data loss | Y/N      |          |

#### H4: Consistency and Standards

| #   | Criterion                     | Present? | Evidence |
| --- | ----------------------------- | -------- | -------- |
| 4.1 | Consistent command syntax     | Y/N      |          |
| 4.2 | Consistent config file format | Y/N      |          |
| 4.3 | Consistent naming conventions | Y/N      |          |
| 4.4 | Consistent output formatting  | Y/N      |          |

#### H5: Error Prevention

| #   | Criterion                              | Present? | Evidence |
| --- | -------------------------------------- | -------- | -------- |
| 5.1 | Config validation before run           | Y/N      |          |
| 5.2 | Confirmation for destructive actions   | Y/N      |          |
| 5.3 | Default values for optional parameters | Y/N      |          |
| 5.4 | Path/file existence checks             | Y/N      |          |

#### H6: Recognition Rather Than Recall

| #   | Criterion                          | Present? | Evidence |
| --- | ---------------------------------- | -------- | -------- |
| 6.1 | Help/usage available for commands  | Y/N      |          |
| 6.2 | Available options visible          | Y/N      |          |
| 6.3 | Recent commands/configs accessible | Y/N      |          |

#### H7: Flexibility and Efficiency of Use

| #   | Criterion                       | Present? | Evidence |
| --- | ------------------------------- | -------- | -------- |
| 7.1 | Shortcuts for common operations | Y/N      |          |
| 7.2 | Configurable defaults           | Y/N      |          |
| 7.3 | Batch operations supported      | Y/N      |          |

#### H8: Aesthetic and Minimalist Design

| #   | Criterion                                 | Present? | Evidence |
| --- | ----------------------------------------- | -------- | -------- |
| 8.1 | Output contains only relevant information | Y/N      |          |
| 8.2 | No redundant prompts/confirmations        | Y/N      |          |
| 8.3 | Clear visual hierarchy in output          | Y/N      |          |

#### H9: Help Users Recognize, Diagnose, and Recover from Errors

| #   | Criterion                           | Present? | Evidence |
| --- | ----------------------------------- | -------- | -------- |
| 9.1 | Error messages in plain language    | Y/N      |          |
| 9.2 | Error messages indicate the problem | Y/N      |          |
| 9.3 | Error messages suggest solution     | Y/N      |          |
| 9.4 | Error codes for reference           | Y/N      |          |

#### H10: Help and Documentation

| #    | Criterion                   | Present? | Evidence |
| ---- | --------------------------- | -------- | -------- |
| 10.1 | Built-in help command       | Y/N      |          |
| 10.2 | Examples provided           | Y/N      |          |
| 10.3 | Documentation accessible    | Y/N      |          |
| 10.4 | Quick-start guide available | Y/N      |          |

### Part 2: GOMS/KLM Analysis

For each task, document operator sequence for both baseline and platform. Baseline operator sequences must be derived from the pre-documented SRQ2 manual workflow steps - do not redefine them independently.

#### Task List

| ID  | Task                     | Description                                            | Complexity |
| --- | ------------------------ | ------------------------------------------------------ | ---------- |
| T1  | Configure new experiment | Create config for a basic MARL experiment from scratch | Medium     |
| T2  | Modify parameters        | Change hyperparameters in existing config and re-run   | Low        |
| T3  | Start training           | Initiate training run with configured experiment       | Low        |
| T4  | Monitor progress         | View training metrics and logs during run              | Low        |
| T5  | View results             | Access and interpret final training results            | Medium     |
| T6  | Export experiment        | Create shareable bundle of completed experiment        | Low        |
| T7  | Import and reproduce     | Import bundle on fresh environment and verify          | Medium     |

#### Task Breakdown Template

**Task: T1 - Configure new experiment**

**Baseline (Manual Workflow):**

| Step      | Action              | Operators |
| --------- | ------------------- | --------- |
| 1         | Open text editor    | M + P + B |
| 2         | Create ARGoS config | M + 20K   |
| ...       | ...                 | ...       |
| **Total** |                     |           |

**Platform:**

| Step      | Action       | Operators |
| --------- | ------------ | --------- |
| 1         | Type command | M + 15K   |
| ...       | ...          | ...       |
| **Total** |              |           |

**KLM Calculation:**
- Baseline: ΣOperators × Times = ___ seconds
- Platform: ΣOperators × Times = ___ seconds
- Reduction: ____%

---

## Data Collection

### Heuristic Compliance Summary

| Heuristic            | Criteria Count | Met | Score   |
| -------------------- | -------------- | --- | ------- |
| H1: Visibility       | 4              |     | /4      |
| H2: Real World Match | 3              |     | /3      |
| H3: User Control     | 3              |     | /3      |
| H4: Consistency      | 4              |     | /4      |
| H5: Error Prevention | 4              |     | /4      |
| H6: Recognition      | 3              |     | /3      |
| H7: Flexibility      | 3              |     | /3      |
| H8: Minimalist       | 3              |     | /3      |
| H9: Error Recovery   | 4              |     | /4      |
| H10: Help/Docs       | 4              |     | /4      |
| **Total**            | **35**         |     | **/35** |

### KLM Comparison Summary

| Task                 | Baseline (sec) | Platform (sec) | Reduction (%) |
| -------------------- | -------------- | -------------- | ------------- |
| T1: Configure        |                |                |               |
| T2: Modify           |                |                |               |
| T3: Train            |                |                |               |
| T4: Monitor          |                |                |               |
| T5: Results          |                |                |               |
| T6: Export           |                |                |               |
| T7: Import/Reproduce |                |                |               |
| **Average**          |                |                |               |

---

## Analysis

### Metrics Summary (M4.4-M4.6)

| Metric                              | Value | Target       | Met? |
| ----------------------------------- | ----- | ------------ | ---- |
| M4.4: Heuristic-Compliance-Rate     |       | ≥80% (28/35) |      |
| M4.5: KLM-Predicted-Time (platform) |       |              |      |
| M4.6: KLM-Reduction                 |       | ≥50%         |      |

### Interpretation Guidelines

| Outcome                                          | Interpretation         |
| ------------------------------------------------ | ---------------------- |
| ≥80% heuristic compliance AND ≥50% KLM reduction | H4 supported           |
| ≥80% heuristic OR ≥50% KLM (not both)            | H4 partially supported |
| <80% heuristic AND <50% KLM                      | H4 not supported       |

---

## Evidence Checklist

- [ ] Heuristic audit complete with evidence per criterion
- [ ] KLM operator analysis complete for all 7 tasks

### Required Evidence Files

| File                  | Description                         |
| --------------------- | ----------------------------------- |
| `heuristic_audit.md`  | Complete checklist with evidence    |
| `klm_analysis.md`     | Operator breakdown and calculations |
| `analysis_summary.md` | Computed statistics                 |

---

## Limitations

| Limitation                                                                                                            | Mitigation                                                                                    |
| --------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| Single evaluator for heuristic audit (developer evaluating own design; Nielsen recommends 3-5 independent evaluators) | Use structured checklist; require evidence citation per criterion; state explicitly in thesis |
| KLM assumes error-free execution                                                                                      | Conservative operator estimates; noted as model limitation                                    |
| H6/H10 measure design properties indicative of learnability, not behavioral learnability directly                     | Scoped as design-property proxies; bridged to behavioral interpretation in Discussion chapter |
| Both methods (KLM + heuristics) are analytical; zero behavioral data in SRQ4                                          | Consistent with empiricism-first principle; stated as limitation in thesis                    |

---

## Comparison: SRQ4 vs SRQ2

| Aspect      | SRQ2: Efficiency                               | SRQ4: Usability                                                                                |
| ----------- | ---------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Question    | How much does the platform reduce time/effort? | Does the platform's design comply with usability heuristics and reduce interaction complexity? |
| Perspective | Experienced user (knows system)                | Design-property analysis (analytical + structured audit)                                       |
| Focus       | Throughput, step reduction                     | Heuristic compliance, interaction complexity (KLM)                                             |
| Metrics     | Time-to-Complete, Steps-to-Complete            | Heuristic-Compliance-Rate, KLM-Predicted-Time, KLM-Reduction                                   |

---

## References

- `docs/SRQ4UsabilityBrainstorm.md` - Full rationale and decisions
- `docs/ResearchPlan.md` - SRQ4, H4, E4 definitions
- Card, Moran, Newell (1983). *The Psychology of Human-Computer Interaction*. Lawrence Erlbaum Associates.
- Nielsen, J. (1994). *10 Usability Heuristics for User Interface Design*.
