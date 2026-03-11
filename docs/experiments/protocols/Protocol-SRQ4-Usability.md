# Protocol-SRQ4-Usability

## Header

| Field | Value |
|-------|-------|
| **Protocol ID** | P-SRQ4 |
| **SRQ Reference** | SRQ4: How learnable is the platform, and to what extent does its design minimize user errors, support error recovery, and reduce interaction complexity? |
| **Hypothesis** | H4: The platform demonstrates high learnability (Time-to-First-Success), low error-proneness (Error-Rate), effective error recovery (Recovery-Time), strong compliance with established usability heuristics (Heuristic-Compliance-Rate ≥80%), and significant reduction in predicted interaction time (KLM-Reduction ≥50% vs baseline). |
| **Success Criteria** | ≥80% heuristic compliance (28/35 criteria), ≥50% KLM reduction |
| **Sample Size** | 7 tasks × 3 trials = 21 data points |
| **Dependencies** | Platform implementation complete |

---

## Prerequisites

### Required Artifacts
- [ ] Platform CLI operational (all commands)
- [ ] Platform documentation/help system
- [ ] Test experiment configs prepared
- [ ] Screen recording software
- [ ] Timer/stopwatch

### Environment Setup
- [ ] Platform installed and accessible
- [ ] Fresh user profile (or "novice simulation" mode)
- [ ] Documentation accessible but not pre-read

### Pre-Execution Checklist
- [ ] 7 evaluation tasks defined and documented
- [ ] 35-criteria heuristic checklist prepared
- [ ] KLM operator definitions reviewed
- [ ] Trial recording setup tested

---

## Definitions

### Key Terms

| Term | Definition |
|------|------------|
| **Time-to-First-Success** | Time from first action to successful task completion on first attempt |
| **Error-Rate** | Total errors / Total task attempts |
| **Recovery-Time** | Time from error occurrence to error resolution |
| **Documentation-Lookups** | Count of times documentation was consulted during task |
| **Heuristic-Compliance-Rate** | Criteria met / 35 × 100% |
| **KLM-Predicted-Time** | Predicted task time using Keystroke-Level Model |
| **KLM-Reduction** | (Baseline_KLM - Platform_KLM) / Baseline_KLM × 100% |

### Measurement Triggers

| Metric | Start Trigger | Stop Trigger |
|--------|---------------|--------------|
| Time-to-First-Success | First action toward task goal | Task completed successfully |
| Error-Count | Start of task | End of task |
| Recovery-Time | Error occurs | Error resolved, task continues |
| Documentation-Lookups | Start of task | End of task |

### KLM Operator Definitions

Source: Card, Moran, Newell (1983). *The Psychology of Human-Computer Interaction*.

| Operator | Symbol | Time (sec) | Description |
|----------|--------|------------|-------------|
| Keystroke | K | 0.20 | Single key press (average typist) |
| Point | P | 1.10 | Mouse movement to target |
| Button | B | 0.10 | Mouse button click |
| Homing | H | 0.40 | Hand movement (keyboard ↔ mouse) |
| Mental | M | 1.35 | Mental preparation |
| System Response | R(t) | t | Wait for system (variable) |

---

## Procedure

### Part 1: Task-Based Metrics

#### Evaluation Tasks

| ID | Task | Description | Complexity |
|----|------|-------------|------------|
| T1 | Configure new experiment | Create config for a basic MARL experiment from scratch | Medium |
| T2 | Modify parameters | Change hyperparameters in existing config and re-run | Low |
| T3 | Start training | Initiate training run with configured experiment | Low |
| T4 | Monitor progress | View training metrics and logs during run | Low |
| T5 | View results | Access and interpret final training results | Medium |
| T6 | Export experiment | Create shareable bundle of completed experiment | Low |
| T7 | Import and reproduce | Import bundle on fresh environment and verify | Medium |

#### Trial Structure

| Trial | Condition | Purpose |
|-------|-----------|---------|
| Trial 1 | First attempt (novice) | Measure initial learnability |
| Trial 2 | Second attempt | Measure learning curve |
| Trial 3 | Third attempt | Measure skill stabilization |

#### Task Execution Protocol

For each task (T1-T7), for each trial (1-3):

1. **Start screen recording**
2. **State task ID and trial number**
3. **Start timer** at first action
4. **Perform task** as simulated novice (first trial) or with prior knowledge (trials 2-3)
5. **Stop timer** when task complete
6. **Record**: Time, Errors, Recoveries, Recovery Time, Doc Lookups, Success
7. **Stop screen recording**

### Part 2: Heuristic Compliance Audit

Evaluate platform against Nielsen's 10 heuristics using the 35-criteria checklist below.

#### H1: Visibility of System Status

| # | Criterion | Present? | Evidence |
|---|-----------|----------|----------|
| 1.1 | Progress indicator for training runs | Y/N | |
| 1.2 | Feedback after command execution | Y/N | |
| 1.3 | Current state visible (running/stopped/error) | Y/N | |
| 1.4 | Resource usage visible (if applicable) | Y/N | |

#### H2: Match Between System and Real World

| # | Criterion | Present? | Evidence |
|---|-----------|----------|----------|
| 2.1 | Uses MARL/Swarm domain terminology | Y/N | |
| 2.2 | Follows conventions of similar tools (RLlib, ARGoS) | Y/N | |
| 2.3 | Logical ordering of operations | Y/N | |

#### H3: User Control and Freedom

| # | Criterion | Present? | Evidence |
|---|-----------|----------|----------|
| 3.1 | Cancel running operations | Y/N | |
| 3.2 | Undo/revert config changes | Y/N | |
| 3.3 | Exit from any state without data loss | Y/N | |

#### H4: Consistency and Standards

| # | Criterion | Present? | Evidence |
|---|-----------|----------|----------|
| 4.1 | Consistent command syntax | Y/N | |
| 4.2 | Consistent config file format | Y/N | |
| 4.3 | Consistent naming conventions | Y/N | |
| 4.4 | Consistent output formatting | Y/N | |

#### H5: Error Prevention

| # | Criterion | Present? | Evidence |
|---|-----------|----------|----------|
| 5.1 | Config validation before run | Y/N | |
| 5.2 | Confirmation for destructive actions | Y/N | |
| 5.3 | Default values for optional parameters | Y/N | |
| 5.4 | Path/file existence checks | Y/N | |

#### H6: Recognition Rather Than Recall

| # | Criterion | Present? | Evidence |
|---|-----------|----------|----------|
| 6.1 | Help/usage available for commands | Y/N | |
| 6.2 | Available options visible | Y/N | |
| 6.3 | Recent commands/configs accessible | Y/N | |

#### H7: Flexibility and Efficiency of Use

| # | Criterion | Present? | Evidence |
|---|-----------|----------|----------|
| 7.1 | Shortcuts for common operations | Y/N | |
| 7.2 | Configurable defaults | Y/N | |
| 7.3 | Batch operations supported | Y/N | |

#### H8: Aesthetic and Minimalist Design

| # | Criterion | Present? | Evidence |
|---|-----------|----------|----------|
| 8.1 | Output contains only relevant information | Y/N | |
| 8.2 | No redundant prompts/confirmations | Y/N | |
| 8.3 | Clear visual hierarchy in output | Y/N | |

#### H9: Help Users Recognize, Diagnose, and Recover from Errors

| # | Criterion | Present? | Evidence |
|---|-----------|----------|----------|
| 9.1 | Error messages in plain language | Y/N | |
| 9.2 | Error messages indicate the problem | Y/N | |
| 9.3 | Error messages suggest solution | Y/N | |
| 9.4 | Error codes for reference | Y/N | |

#### H10: Help and Documentation

| # | Criterion | Present? | Evidence |
|---|-----------|----------|----------|
| 10.1 | Built-in help command | Y/N | |
| 10.2 | Examples provided | Y/N | |
| 10.3 | Documentation accessible | Y/N | |
| 10.4 | Quick-start guide available | Y/N | |

### Part 3: GOMS/KLM Analysis

For each task, document operator sequence for both baseline and platform.

#### Task Breakdown Template

**Task: T1 - Configure new experiment**

**Baseline (Manual Workflow):**

| Step | Action | Operators |
|------|--------|-----------|
| 1 | Open text editor | M + P + B |
| 2 | Create ARGoS config | M + 20K |
| ... | ... | ... |
| **Total** | | |

**Platform:**

| Step | Action | Operators |
|------|--------|-----------|
| 1 | Type command | M + 15K |
| ... | ... | ... |
| **Total** | | |

**KLM Calculation:**
- Baseline: ΣOperators × Times = ___ seconds
- Platform: ΣOperators × Times = ___ seconds
- Reduction: ____%

### Part 4: Error Analysis

#### Error Categories

| Category | Description | Example |
|----------|-------------|---------|
| Syntax | Incorrect command/config syntax | Typo in command name |
| Config | Invalid configuration values | Wrong parameter type |
| Path | File/directory not found | Missing config file |
| Dependency | Missing requirement | Uninstalled package |
| Logic | Correct syntax, wrong approach | Wrong command for task |

---

## Data Collection

### Task-Based Metrics Template

| Task | Trial | Time (sec) | Errors | Recoveries | Recovery Time (sec) | Doc Lookups | Success? |
|------|-------|------------|--------|------------|---------------------|-------------|----------|
| T1 | 1 | | | | | | Y/N |
| T1 | 2 | | | | | | Y/N |
| T1 | 3 | | | | | | Y/N |
| T2 | 1 | | | | | | Y/N |
| T2 | 2 | | | | | | Y/N |
| T2 | 3 | | | | | | Y/N |
| T3 | 1 | | | | | | Y/N |
| T3 | 2 | | | | | | Y/N |
| T3 | 3 | | | | | | Y/N |
| T4 | 1 | | | | | | Y/N |
| T4 | 2 | | | | | | Y/N |
| T4 | 3 | | | | | | Y/N |
| T5 | 1 | | | | | | Y/N |
| T5 | 2 | | | | | | Y/N |
| T5 | 3 | | | | | | Y/N |
| T6 | 1 | | | | | | Y/N |
| T6 | 2 | | | | | | Y/N |
| T6 | 3 | | | | | | Y/N |
| T7 | 1 | | | | | | Y/N |
| T7 | 2 | | | | | | Y/N |
| T7 | 3 | | | | | | Y/N |

### Error Log Template

| Task | Trial | Error Type | Error Description | Recovery Action | Recovery Time (sec) |
|------|-------|------------|-------------------|-----------------|---------------------|
| | | | | | |

### Heuristic Compliance Summary

| Heuristic | Criteria Count | Met | Score |
|-----------|----------------|-----|-------|
| H1: Visibility | 4 | | /4 |
| H2: Real World Match | 3 | | /3 |
| H3: User Control | 3 | | /3 |
| H4: Consistency | 4 | | /4 |
| H5: Error Prevention | 4 | | /4 |
| H6: Recognition | 3 | | /3 |
| H7: Flexibility | 3 | | /3 |
| H8: Minimalist | 3 | | /3 |
| H9: Error Recovery | 4 | | /4 |
| H10: Help/Docs | 4 | | /4 |
| **Total** | **35** | | **/35** |

### KLM Comparison Summary

| Task | Baseline (sec) | Platform (sec) | Reduction (%) |
|------|----------------|----------------|---------------|
| T1: Configure | | | |
| T2: Modify | | | |
| T3: Train | | | |
| T4: Monitor | | | |
| T5: Results | | | |
| T6: Export | | | |
| T7: Import/Reproduce | | | |
| **Average** | | | |

---

## Analysis

### Metrics Summary (M4.1-M4.7)

| Metric | Value | Target | Met? |
|--------|-------|--------|------|
| M4.1: Time-to-First-Success (mean) | | Learning curve shows improvement | |
| M4.2: Error-Rate | | Decreasing over trials | |
| M4.3: Recovery-Time (mean) | | | |
| M4.4: Heuristic-Compliance-Rate | | ≥80% (28/35) | |
| M4.5: KLM-Predicted-Time (platform) | | | |
| M4.6: KLM-Reduction | | ≥50% | |
| M4.7: Documentation-Lookups (mean) | | | |

### Error Metrics

| Metric | Formula | Value |
|--------|---------|-------|
| Error-Rate | Total errors / Total task attempts | |
| Mean-Recovery-Time | Σ Recovery times / # recoveries | |
| Error-Free-Rate | Tasks with 0 errors / Total tasks | |

### Learning Curve Analysis

| Task | Trial 1 Time | Trial 2 Time | Trial 3 Time | Improvement (T1→T3) |
|------|--------------|--------------|--------------|---------------------|
| T1 | | | | |
| T2 | | | | |
| ... | | | | |

### Interpretation Guidelines

| Outcome | Interpretation |
|---------|----------------|
| ≥80% heuristic compliance AND ≥50% KLM reduction | H4 supported |
| ≥80% heuristic OR ≥50% KLM (not both) | H4 partially supported |
| <80% heuristic AND <50% KLM | H4 not supported |

---

## Evidence Checklist

- [ ] Screen recordings of all 21 task trials
- [ ] Task-based metrics data complete
- [ ] Error logs complete
- [ ] Heuristic audit complete with evidence
- [ ] KLM operator analysis complete for all 7 tasks
- [ ] Learning curve data recorded

### Required Evidence Files

| File | Description |
|------|-------------|
| `task_trials/T1_trial1.mp4` ... | Screen recordings |
| `task_metrics.csv` | All task timing and error data |
| `error_log.csv` | All errors recorded |
| `heuristic_audit.md` | Complete checklist with evidence |
| `klm_analysis.md` | Operator breakdown and calculations |
| `analysis_summary.md` | Computed statistics |

---

## Limitations

| Limitation | Mitigation |
|------------|------------|
| Self-as-user (not independent users) | Transparent methodology; state explicitly in thesis |
| Single evaluator for heuristics | Use established checklist; document evidence |
| KLM assumes error-free execution | Combine with empirical error data (Part 4) |
| Learning curve from single subject | Report as case study, not generalizable |

---

## Comparison: SRQ4 vs SRQ2

| Aspect | SRQ2: Efficiency | SRQ4: Usability |
|--------|------------------|-----------------|
| Question | How much does the platform reduce time/effort? | How learnable and error-tolerant is the platform? |
| Perspective | Experienced user (knows system) | Novice user (learning system) |
| Focus | Throughput, step reduction | Learnability, error handling, design quality |
| Metrics | Time-to-Setup, Steps-per-Task | Time-to-First-Success, Error-Rate, Heuristic-Compliance, KLM |

---

## References

- `docs/UsabilityBrainstorm.md` - Full rationale and decisions
- `docs/ResearchPlan.md` - SRQ4, H4, E4 definitions
- Card, Moran, Newell (1983). *The Psychology of Human-Computer Interaction*. Lawrence Erlbaum Associates.
- Nielsen, J. (1994). *10 Usability Heuristics for User Interface Design*.
