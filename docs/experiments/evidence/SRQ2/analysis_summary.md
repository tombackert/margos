# SRQ2 Analysis Summary

## Raw Data

### Time-to-Complete

| Condition | N | Mean (sec) | SD | Min | Max |
|-----------|---|------------|-----|-----|-----|
| Manual | 5 | | | | |
| Platform | 5 | | | | |

### Steps-to-Complete

| Condition | N | Mean | SD | Min | Max |
|-----------|---|------|-----|-----|-----|
| Manual | 5 | | | | |
| Platform | 5 | | | | |

## Primary Metrics (M2.1, M2.2)

| Metric | Manual (Mean ± SD) | Platform (Mean ± SD) | Reduction (%) | Target Met? |
|--------|-------------------|---------------------|---------------|-------------|
| Time-to-Complete (M2.1) | | | | ≥50%? |
| Steps-to-Complete (M2.2) | | | | ≥50%? |

## Formulas

```
Time Reduction = (Mean_Manual - Mean_Platform) / Mean_Manual × 100%
Step Reduction = (Mean_Manual - Mean_Platform) / Mean_Manual × 100%
```

## Interpretation

| Result | Interpretation |
|--------|----------------|
| ≥50% reduction on both | H2 supported |
| ≥50% on one metric only | H2 partially supported |
| <50% on both | H2 not supported |

**Outcome:** [Fill after data collection]

## Limitations

- Time metric is conservative lower bound (glue script + debug excluded)
- Self-as-evaluator; mitigated by objective metrics and screen recording
- Expert user; generalization to novices covered by SRQ4
