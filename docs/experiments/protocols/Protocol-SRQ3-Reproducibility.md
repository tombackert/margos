# Protocol-SRQ3-Reproducibility

## Header

| Field                | Value                                                                                                                                                                                                                                                                                              |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Protocol ID**      | P-SRQ3                                                                                                                                                                                                                                                                                             |
| **SRQ Reference**    | SRQ3: To what extent does the platform's centralized configuration and seed management enable reliable self-reproducibility of MARL experiments?                                                                                                                                                   |
| **Hypothesis**       | H3: The platform achieves a Reproduce-Success-Rate of at least 90% within ±1% tolerance on final reward and AUC, while preserving configuration identity and runtime config integrity across repeated platform reproductions through centralized config management and deterministic seed control. |
| **Success Criteria** | Reproduce-Success-Rate ≥90%, low and stable Result-Variance across repeated runs                                                                                                                                                                                                                   |
| **Sample Size**      | N=20 reproduction attempts (raised from N≥10 in EvalPlanOverview to achieve 5% resolution on success rate, making the ≥90% threshold cleanly testable)                                                                                                                                             |
| **Dependencies**     | Platform implementation complete, reference run established                                                                                                                                                                                                                                        |

---

## Prerequisites

### Required Artifacts
- [x] Platform CLI operational (`run`, `compare`)
- [x] Test experiment config (`aggregation_v1.yaml`)
- [x] Comparison script for results (`analysis/compare.py`)
- [x] Reference run completed and saved

### Environment Setup
- [x] Same hardware for all runs
- [x] Platform installed and accessible
- [x] Sufficient disk space for N+1 experiment outputs
- [x] GPU non-determinism documented (if applicable)

### Pre-Execution Checklist
- [x] Reference run completed successfully
- [x] Reference final reward recorded
- [x] Reference AUC calculated
- [x] Config hash recorded
- [x] Seed value documented

---

## Definitions

### Key Terms

| Term                       | Definition                                                                                                                                                                      |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Reproduce-Success-Rate** | Percentage of runs matching reference within ±1% tolerance on BOTH final reward AND AUC, with matching configuration identity and passing runtime config-integrity verification |
| **Result-Variance**        | Standard deviation of final reward across N runs                                                                                                                                |
| **Config-Integrity**       | Config hash at start matches config hash at end (100% expected)                                                                                                                 |
| **Seed-Determinism**       | Same seed produces same RNG sequence (verified by unit test)                                                                                                                    |
| **Tolerance**              | ±1% deviation from reference value                                                                                                                                              |

### Tolerance Calculation

A reproduction is **successful** if all conditions are met:

```
| run_reward - ref_reward | / ref_reward ≤ 0.01   (Final Reward within ±1%) |
| run_AUC - ref_AUC       | / ref_AUC ≤ 0.01            (AUC within ±1%)    |
```

- The reproduced run matches the reference configuration hash.
- The runtime config-integrity check confirms that the frozen configuration remained unchanged throughout execution.

### Controlled Variables

| Variable             | How Controlled                           |
| -------------------- | ---------------------------------------- |
| Hardware             | Same machine for all runs                |
| Config               | Identical config file (hash verified)    |
| Seed                 | Fixed seed value                         |
| Time between runs    | Documented (immediate or fixed interval) |
| Background processes | Minimized, documented                    |

---

## Procedure

### Phase 1: Reference Run

1. **Execute reference experiment**
   ```bash
   platform run aggregation_v1
   ```

2. **Record reference metrics**
   - Final reward value
   - AUC (area under learning curve)
   - Config hash
   - Experiment ID

3. **Save reference data**
   - Store in `results/reference/`
   - Document as ground truth

### Phase 2: Reproduction Attempts (Platform)

For each reproduction attempt (N=20):

1. **Start reproduction**
   ```bash
   platform run aggregation_v1
   ```

2. **Wait for completion**

3. **Compare results**
   ```bash
   platform compare exp_XXX results/reference/
   ```

4. **Record outcome**
   - Final reward
   - AUC
   - Pass/Fail status
   - Config hash match
   - Config integrity match

### Phase 3: By-Design Verification

These are platform controls verified by the finalized implementation and supporting unit tests:

| Feature          | Verification Method                                      | Expected Outcome   |
| ---------------- | -------------------------------------------------------- | ------------------ |
| Config-Integrity | Runtime hash comparison: frozen config at start vs end   | 100% match         |
| Seed-Determinism | Unit test: same seed → same RNG sequence                 | Deterministic      |

---

## Data Collection

### Reference Run Data

| Field           | Value                                                            |
| --------------- | ---------------------------------------------------------------- |
| Experiment ID   | aggregation_srq3_20260413-171009                                 |
| Platform Commit | `ff77ced`                                                        |
| Config Hash     | 4bf92694c011b30981974b14e29a53fa69ac8d39cf754820cf04f608ade1aecd |
| Seed            | 42                                                               |
| Final Reward    | -46.8277                                                         |
| AUC             | -445.2401                                                        |
| Timestamp       | 2026-04-13T17:10:30 → 2026-04-13T17:11:48                        |

### Reproduction Attempts Template

| Run #   | Final Reward   | AUC       | Reward Deviation (%)  | AUC Deviation (%)   | Pass?   | Config Hash Match   | Config Integrity Match |
| ------- | -------------- | --------- | --------------------- | ------------------- | ------- | ------------------- | ---------------------- |
| 1       | -46.8277       | -445.2401 | 0.0000                | 0.0000              | Y       | Y                   | Y                      |
| 2       | -46.8277       | -445.2401 | 0.0000                | 0.0000              | Y       | Y                   | Y                      |
| 3       | -46.8277       | -445.2401 | 0.0000                | 0.0000              | Y       | Y                   | Y                      |
| 4       | -46.8277       | -445.2401 | 0.0000                | 0.0000              | Y       | Y                   | Y                      |
| 5       | -46.8277       | -445.2401 | 0.0000                | 0.0000              | Y       | Y                   | Y                      |
| 6       | -46.8277       | -445.2401 | 0.0000                | 0.0000              | Y       | Y                   | Y                      |
| 7       | -46.8277       | -445.2401 | 0.0000                | 0.0000              | Y       | Y                   | Y                      |
| 8       | -46.8277       | -445.2401 | 0.0000                | 0.0000              | Y       | Y                   | Y                      |
| 9       | -46.8277       | -445.2401 | 0.0000                | 0.0000              | Y       | Y                   | Y                      |
| 10      | -46.8277       | -445.2401 | 0.0000                | 0.0000              | Y       | Y                   | Y                      |
| 11      | -46.8277       | -445.2401 | 0.0000                | 0.0000              | Y       | Y                   | Y                      |
| 12      | -46.8277       | -445.2401 | 0.0000                | 0.0000              | Y       | Y                   | Y                      |
| 13      | -46.8277       | -445.2401 | 0.0000                | 0.0000              | Y       | Y                   | Y                      |
| 14      | -46.8277       | -445.2401 | 0.0000                | 0.0000              | Y       | Y                   | Y                      |
| 15      | -46.8277       | -445.2401 | 0.0000                | 0.0000              | Y       | Y                   | Y                      |
| 16      | -46.8277       | -445.2401 | 0.0000                | 0.0000              | Y       | Y                   | Y                      |
| 17      | -46.8277       | -445.2401 | 0.0000                | 0.0000              | Y       | Y                   | Y                      |
| 18      | -46.8277       | -445.2401 | 0.0000                | 0.0000              | Y       | Y                   | Y                      |
| 19      | -46.8277       | -445.2401 | 0.0000                | 0.0000              | Y       | Y                   | Y                      |
| 20      | -46.8277       | -445.2401 | 0.0000                | 0.0000              | Y       | Y                   | Y                      |

### Deviation Calculation

For each run:
```
Reward Deviation (%) = |run_reward - ref_reward| / ref_reward × 100
AUC Deviation (%) = |run_AUC - ref_AUC| / ref_AUC × 100
Pass = (Reward Deviation ≤ 1%) AND (AUC Deviation ≤ 1%)
```

---

## Analysis

### Primary Metrics (M3.1, M3.2)

| Metric                        | Formula             | Target                              |
| ----------------------------- | ------------------- | ----------------------------------- |
| Reproduce-Success-Rate (M3.1) | (# Pass) / N × 100% | ≥90%                                |
| Result-Variance (M3.2)        | SD(final_rewards)   | Low and stable across repeated runs |

### Summary Statistics Template

| Statistic         | Final Reward   | AUC       |
| ----------------- | -------------- | --------- |
| Reference         | -46.8277       | -445.2401 |
| Mean (N runs)     | -46.8277       | -445.2401 |
| SD                | 0.0000         | 0.0000    |
| Min               | -46.8277       | -445.2401 |
| Max               | -46.8277       | -445.2401 |
| Max Deviation (%) | 0.0000%        | 0.0000%   |

### Success Rate Calculation

```
Reproduce-Success-Rate = (# runs matching reward and AUC within ±1%, with matching config hash and passing config-integrity check) / N × 100%
```

### By-Design Metrics (M3.3, M3.4)

| Metric                  | Verification                                                  | Result   |
| ----------------------- | ------------------------------------------------------------- | -------- |
| Config-Integrity (M3.3) | Runtime verification: config hash unchanged from start to end | Pass     |
| Seed-Determinism (M3.4) | Unit test: same seed → same sequence                          | Pass     |

### Interpretation Guidelines

| Outcome             | Interpretation                                          |
| ------------------- | ------------------------------------------------------- |
| ≥90% success rate   | H3 supported - platform achieves reproducibility target |
| 80-89% success rate | H3 partially supported - investigate failures           |
| <80% success rate   | H3 not supported - analyze variance sources             |

### Variance Analysis

If success rate < 90%, analyze failure modes:

| Failure Mode            | Count   | Possible Cause   |
| ----------------------- | ------- | ---------------- |
| Reward out of tolerance |         |                  |
| AUC out of tolerance    |         |                  |
| Both out of tolerance   |         |                  |

---

## Evidence Checklist

- [x] Reference run logs saved
- [x] All N reproduction run logs saved
- [x] Comparison reports generated
- [x] Config hashes recorded for all runs
- [x] Unit test results for Config-Integrity
- [x] Unit test results for Seed-Determinism

### Required Evidence Files

| File                                  | Description                                        |
| ------------------------------------- | -------------------------------------------------- |
| `results/reference/`                  | Reference run directory                            |
| `results/run_01/` - `results/run_20/` | Reproduction run directories                       |
| `comparison_results.csv`              | All deviation calculations                         |
| `unit_tests_output.txt`               | Config-Integrity and Seed-Determinism test results |
| `analysis_summary.md`                 | Computed statistics                                |

---

## Limitations

| Limitation                     | Mitigation                                                         |
| ------------------------------ | ------------------------------------------------------------------ |
| GPU non-determinism            | Document GPU usage, use same hardware, report as limitation        |
| Single hardware environment    | Acknowledged - results specific to test hardware                   |
| Self-as-evaluator              | Objective metrics (automated comparison), transparent methodology  |
| Short training for measurement | Acknowledge - longer training may show different variance patterns |

### GPU Non-Determinism Note

Training on GPU may introduce non-deterministic behavior due to parallel computation ordering. This is a known limitation.

**Mitigations:**
- Use same hardware for all runs
- Report variance bounds
- Document GPU model and CUDA version
- Consider CPU-only runs for strict determinism test

---

## References

- `docs/ReproBrainstorm.md` - Full rationale and decisions
- `docs/ResearchPlan.md` - SRQ3, H3, E3 definitions
- Card, Moran, Newell (1983) - GOMS methodology reference
