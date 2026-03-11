# SRQ3 Analysis Summary

## Reference Values

| Field | Value |
|-------|-------|
| Reference Reward | |
| Reference AUC | |
| Config Hash | |

## Summary Statistics

| Statistic | Final Reward | AUC |
|-----------|--------------|-----|
| Reference | | |
| Mean (N=20) | | |
| SD | | |
| Min | | |
| Max | | |
| Max Deviation (%) | | |

## Primary Metrics

| Metric | Formula | Value | Target | Met? |
|--------|---------|-------|--------|------|
| Reproduce-Success-Rate (M3.1) | (# Pass) / 20 × 100% | | ≥90% | |
| Result-Variance (M3.2) | SD(final_rewards) | | Lower than baseline | |

## By-Design Metrics

| Metric | Verification | Result |
|--------|--------------|--------|
| Config-Integrity (M3.3) | Unit test: config hash unchanged | Pass/Fail |
| Seed-Determinism (M3.4) | Unit test: same seed → same sequence | Pass/Fail |

## Formulas

```
Reproduce-Success-Rate = (# runs with BOTH reward AND AUC within ±1%) / 20 × 100%
Reward Deviation (%) = |run_reward - ref_reward| / ref_reward × 100
AUC Deviation (%) = |run_AUC - ref_AUC| / ref_AUC × 100
```

## Interpretation

**Outcome:** [Fill after data collection]

| Outcome | Interpretation |
|---------|----------------|
| ≥90% success rate | H3 supported |
| 80-89% success rate | H3 partially supported |
| <80% success rate | H3 not supported |
