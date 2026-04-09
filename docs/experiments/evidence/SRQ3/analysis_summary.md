# SRQ3 Analysis Summary

## Reference Values

| Field | Value |
|-------|-------|
| Reference Reward | -46.8277 |
| Reference AUC | -445.2401 |
| Config Hash | b9ff14a67be24984cfc457a5116e2b70a2791b2f29bcf856c5782006e8614340 |

## Summary Statistics

| Statistic | Final Reward | AUC |
|-----------|--------------|-----|
| Reference | -46.8277 | -445.2401 |
| Mean (N=20) | -46.8277 | -445.2401 |
| SD | 0.0000 | 0.0000 |
| Min | -46.8277 | -445.2401 |
| Max | -46.8277 | -445.2401 |
| Max Deviation (%) | 0.0000% | 0.0000% |

## Primary Metrics

| Metric | Formula | Value | Target | Met? |
|--------|---------|-------|--------|------|
| Reproduce-Success-Rate (M3.1) | (# Pass) / 20 × 100% | 100% | ≥90% | Yes |
| Result-Variance (M3.2) | SD(final_rewards) | 0.0000 | Low and stable across repeated runs | Yes |

## By-Design Metrics

| Metric | Verification | Result |
|--------|--------------|--------|
| Config-Integrity (M3.3) | Unit test: config hash unchanged | Pass |
| Seed-Determinism (M3.4) | Unit test: same seed → same sequence | Pass |

## Formulas

```
Reproduce-Success-Rate = (# runs with BOTH reward AND AUC within ±1%) / 20 × 100%
Reward Deviation (%) = |run_reward - ref_reward| / ref_reward × 100
AUC Deviation (%) = |run_AUC - ref_AUC| / ref_AUC × 100
```

## Interpretation

**Outcome:** H3 strongly supported — 100% success rate (20/20) with 0.0000% deviation across all runs.

| Outcome | Interpretation |
|---------|----------------|
| ≥90% success rate | H3 supported |
| 80-89% success rate | H3 partially supported |
| <80% success rate | H3 not supported |
