# Protocol-SRQ2-Efficiency

## Header

| Field | Value |
|-------|-------|
| **Protocol ID** | P-SRQ2 |
| **SRQ Reference** | SRQ2: To what extent does the platform reduce time and effort across the full experiment lifecycle (setup, training management, and analysis) compared to manual workflows? |
| **Hypothesis** | H2: The platform reduces Time-to-Complete by ≥50% and Steps-to-Complete by ≥50% compared to manual experiment workflows, measuring human effort across the full pipeline (excluding compute wait time). |
| **Success Criteria** | ≥50% reduction on Time-to-Complete AND ≥50% reduction on Steps-to-Complete |
| **Sample Size** | N ≥ 5 trials per condition |
| **Dependencies** | Platform implementation complete, baseline workflow documented |

---

## Prerequisites

### Required Artifacts
- [ ] Platform CLI operational (`run`)
- [ ] Test experiment config (`aggregation_srq2.yaml`)
- [ ] Screen recording software installed
- [ ] Step log template prepared
- [ ] Stopwatch/timer available

### Scope Boundary (Pre-existing Artifacts — NOT Measured)
The following artifacts must exist before any trial begins. They represent identical work in both conditions and are excluded from measurement:
- [ ] `.argos` scenario file prepared (same file used in both conditions)
- [ ] Training script prepared (platform condition) / RLlib config prepared (manual condition)

These are excluded because authoring scenario-specific content takes the same time regardless of platform. Measuring them would add noise, not signal.

### Environment Setup
- [ ] Same hardware for all trials
- [ ] Platform installed and accessible
- [ ] ARGoS + RLlib manual workflow components available
- [ ] Training configured for short duration (5 iterations for measurement)

### Pre-Execution Checklist
- [ ] Baseline workflow documented (8 measured steps: 6 timed + 2 counted-only)
- [ ] Platform workflow documented (2 steps, all timed)
- [ ] .argos scenario file and training script pre-prepared (not created during trials)
- [ ] Screen recording tested
- [ ] Trial order randomized or documented

---

## Definitions

### Key Terms

| Term | Definition |
|------|------------|
| **Step** | One discrete user action that advances the workflow toward completion |
| **Time-to-Complete** | Wall-clock time for human effort (excluding training wait time) |
| **Human Effort** | Time actively working (typing, clicking, reading output) |
| **Training Wait Time** | Time waiting for compute (excluded from measurement) |

### What Counts as a Step

| Counts as 1 Step | Does NOT Count |
|------------------|----------------|
| Run a command (regardless of length) | Individual keystrokes |
| Open/save a file | Mouse movements |
| Switch tool/window | Thinking/reading |
| Edit a config value | Waiting for output |

### Excluded from Measurement

| Excluded Artifact | Reason | How Handled |
|-------------------|--------|-------------|
| `.argos` scenario file | Identical work in both conditions | Pre-prepared before trial; clock starts after |
| Training script / RLlib config | Identical work in both conditions | Pre-prepared before trial; clock starts after |
| Write glue script (ARGoS ↔ RLlib) | Written once before all trials; highly variable | Counted as 1 fixed step in step metric; not timed |
| Debug integration issues | Written once before all trials; highly variable | Counted as 1 fixed step in step metric; not timed |

**Implication:** The timed time metric is a **conservative lower bound**. Glue script + debug represent substantial real manual effort that is not captured in timing. This limitation must be stated in the analysis.

### Measurement Triggers

| Metric | Condition | Start Trigger | Stop Trigger |
|--------|-----------|---------------|--------------|
| Time-to-Complete | Manual | First keystroke/click **after** .argos + training script exist | `results/aggregation_srq2/report/` folder created with CSV + PNG saved |
| Time-to-Complete | Platform | First keystroke/click **after** .argos + training script exist | Training Complete summary table printed to terminal by `platform run` |
| Steps-to-Complete | Both | First action (including uncounted glue/debug steps) | Final output ready (report folder / summary table) |
| Time-to-Setup | Both | First keystroke/click after .argos + training script exist | Training command submitted (Enter pressed) |
| Time-to-Report | Manual | First keystroke/click after training completes | `results/aggregation_srq2/report/` folder with CSV + PNG saved |
| Time-to-Report | Platform | Training completes | Training Complete summary table printed (automatic) |

### Controlled Variables

| Variable | How Controlled |
|----------|----------------|
| Experiment type | Same scenario (aggregation) for all trials |
| Hardware | Same machine |
| Prior knowledge | Expert user (knows both workflows) |
| Training length | Fixed (5 iterations) - short for measurement |

---

## Procedure

### Condition A: Manual Workflow (Baseline)

**Total steps: 8 (6 timed + 2 counted-only)**

*Pre-existing (not measured): `.argos` scenario file, RLlib config — identical effort in both conditions.*

| Phase | Step | Protocol Action | Concrete Command / Action | Timed? |
|-------|------|-----------------|--------------------------|--------|
| Setup | 1 | Write glue script (ARGoS ↔ RLlib) | `src/zoo/argos_env.py` (ZMQ bridge) | No — counted only |
| Setup | 2 | Debug integration issues | (resolved prior to trials) | No — counted only |
| Setup | 3 | Configure paths, seeds, parameters | Edit constants at top of `scripts/ray_footbot_aggregation_srq2.py` | Yes |
| Training | 4 | Start training manually | `PYTHONPATH=src python scripts/ray_footbot_aggregation_srq2.py` | Yes |
| Training | 5 | Monitor training | `tensorboard --logdir results/aggregation_srq2_{timestamp}/tensorboard/` → open browser | Yes |
| Training | (wait) | Wait for completion | — | Excluded |
| Analysis | 6 | Extract metrics as CSV | TensorBoard UI → `ray/tune/episode_reward_mean` → Download as CSV | Yes |
| Analysis | 7 | Save training curve image | TensorBoard UI → right-click plot → Save image as `training_curve.png` | Yes |
| Analysis | 8 | Export to report folder | `mkdir -p results/aggregation_srq2/report && mv ~/Downloads/*.csv ~/Downloads/*.png results/aggregation_srq2/report/` | Yes |

**Timed steps: 1 (setup) + 2 (training) + 3 (analysis) = 6 timed steps counted toward Time-to-Complete**

**Baseline Derivation Note:** The manual workflow was derived from the natural interface sequence of the specific toolchain used in this study (ARGoS + Ray RLlib + TensorBoard), as documented in SRQ2EfficiencyBrainstorm.md Part 5. Steps 6-8 use TensorBoard's browser UI because RLlib writes TensorBoard-compatible event files by default — the browser UI is the zero-extra-tooling path for exporting those logs. This baseline is researcher-defined, not derived from a literature survey of MARL workflows. The brainstorm explicitly acknowledges this (R2) and decision D6 specifies documenting the baseline empirically before trials begin.

### Condition B: Platform Workflow

**Total steps: 2 (all timed)**

*Pre-existing (not measured): `.argos` scenario file, custom training script — identical effort in both conditions.*

| Phase | Step | Protocol Action | Concrete Command | Timed? |
|-------|------|-----------------|------------------|--------|
| Setup | 1 | Fill unified config (from template) | Edit `experiments/configs/aggregation_srq2.yaml` | Yes |
| Training | 2 | Run experiment | `platform run aggregation_srq2` | Yes |
| Training | (wait) | (Auto-logging + Training Complete summary printed on finish) | — | Excluded |

### Trial Protocol

1. **Start screen recording**
2. **State trial ID and condition** (verbal or written)
3. **Start timer** at first keystroke/click
4. **Perform workflow** - count each step as performed
5. **Pause timer** when training starts (wait time excluded)
6. **Resume timer** when training completes
7. **Stop timer** when final report is saved
8. **Stop screen recording**
9. **Record data** in collection template

### Trial Execution Order

| Trial | Condition | Notes |
|-------|-----------|-------|
| 1 | Manual | Baseline first |
| 2 | Platform | |
| 3 | Manual | |
| 4 | Platform | |
| 5 | Manual | |
| 6 | Platform | |
| 7 | Manual | |
| 8 | Platform | |
| 9 | Manual | |
| 10 | Platform | |

---

## Data Collection

### Per-Trial Data Template

| Trial | Condition | Steps | Time (sec) | Errors | Notes |
|-------|-----------|-------|------------|--------|-------|
| 1 | Manual | | | | |
| 2 | Platform | | | | |
| 3 | Manual | | | | |
| 4 | Platform | | | | |
| 5 | Manual | | | | |
| 6 | Platform | | | | |
| 7 | Manual | | | | |
| 8 | Platform | | | | |
| 9 | Manual | | | | |
| 10 | Platform | | | | |

### Phase Breakdown Template

For granular analysis, record phase-specific times:

| Trial | Condition | Setup Time | Training Overhead | Analysis Time | Total Time |
|-------|-----------|------------|-------------------|---------------|------------|
| | | | | | |

### Step Log Template

For each trial, log individual steps:

| Trial ID: ___ | Condition: ___ |
|---------------|----------------|

| Step # | Action Description | Timestamp |
|--------|-------------------|-----------|
| 1 | | |
| 2 | | |
| ... | | |

---

## Analysis

### Primary Metrics Calculation

| Metric | Formula |
|--------|---------|
| Mean Time (Manual) | Σ Time_Manual / N_Manual |
| Mean Time (Platform) | Σ Time_Platform / N_Platform |
| Time Reduction | (Mean_Manual - Mean_Platform) / Mean_Manual × 100% |
| Mean Steps (Manual) | Σ Steps_Manual / N_Manual |
| Mean Steps (Platform) | Σ Steps_Platform / N_Platform |
| Step Reduction | (Mean_Manual - Mean_Platform) / Mean_Manual × 100% |

### Summary Statistics Template

| Metric | Manual (Mean ± SD) | Platform (Mean ± SD) | Reduction (%) | Target Met? |
|--------|-------------------|---------------------|---------------|-------------|
| Time-to-Complete (M2.1) | | | | ≥50%? |
| Steps-to-Complete (M2.2) | | | | ≥50%? |

### Statistical Analysis

1. **Descriptive statistics**: Mean, SD, Min, Max for each condition
2. **Paired comparison**: If using repeated measures design
3. **Effect size**: Report absolute reduction and percentage

### Interpretation Guidelines

| Result | Interpretation |
|--------|----------------|
| ≥50% reduction on both | H2 supported - platform achieves efficiency target |
| ≥50% on one metric only | H2 partially supported - discuss implications |
| <50% on both | H2 not supported - report actual values, discuss significance |

---

## Evidence Checklist

- [ ] Screen recordings of all trials (saved with trial ID in filename)
- [ ] Step logs for all trials
- [ ] Per-trial data collection template completed
- [ ] Phase breakdown recorded (optional but recommended)
- [ ] Raw timing data preserved
- [ ] Post-hoc verification: times re-checked from video

### Required Evidence Files

| File | Description |
|------|-------------|
| `trial_01_manual.mp4` | Screen recording trial 1 |
| `trial_02_platform.mp4` | Screen recording trial 2 |
| ... | ... |
| `step_logs.csv` | All step logs |
| `timing_data.csv` | All timing data |
| `analysis_summary.md` | Computed statistics |

---

## Limitations

| Limitation | Mitigation |
|------------|------------|
| Self-as-evaluator | Objective metrics (time, steps), documented methodology, screen recording for verification |
| Learning effects | Multiple trials, interleaved conditions, document trial order |
| Training time excluded | Clearly stated — measures workflow efficiency, not compute optimization |
| Expert user | Acknowledged — results may not generalize to novices (covered by SRQ4) |
| Time metric is conservative lower bound | Glue script + debug excluded from timing (written once, highly variable). Clearly stated in results. Step metric (75% reduction, 8→2) is the primary evidence for H2. Time reduction is expected to exceed 50% but may understate true advantage. |
| Manual baseline is researcher-defined, not literature-derived | Documented explicitly in SRQ2EfficiencyBrainstorm.md with tool-by-tool rationale (Part 5). Risk R2 acknowledged in brainstorm; mitigated by D6 (empirical documentation before trials). Comparison is internally valid: both conditions use the same underlying tools; the platform adds orchestration on top. |

---

## References

- `docs/EfficiencyBrainstorm.md` - Full rationale and decisions
- `docs/ResearchPlan.md` - SRQ2, H2, E2 definitions
- `docs/ArchitectureBrainstorm.md` - Baseline workflow documentation (Section 5)
