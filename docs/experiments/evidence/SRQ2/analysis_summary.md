# SRQ2 Analysis Summary

## Raw Data

### Time-to-Complete

| Condition   | N   | Mean (sec)   | SD      | Min   | Max   |
| ----------- | --- | ------------ | ------- | ----- | ----- |
| Manual      | 5   | 87.0         | 15.02   | 69    | 103   |
| Platform    | 5   | 19.0         | 1.41    | 18    | 21    |

### Steps-to-Complete

| Condition   | N   | Mean   | SD    | Min   | Max   |
| ----------- | --- | ------ | ----- | ----- | ----- |
| Manual      | 5   | 6.0    | 0.0   | 6     | 6     |
| Platform    | 5   | 2.0    | 0.0   | 2     | 2     |

## Primary Metrics (M2.1, M2.2)

| Metric                    | Manual (Mean ± SD)   | Platform (Mean ± SD)   | Reduction (%)   | Target Met?   |
| ------------------------- | -------------------- | ---------------------- | --------------- | ------------- |
| Time-to-Complete (M2.1)   | 87.0 ± 15.02 s       | 19.0 ± 1.41 s          | 78.2%           | ≥50% ✓        |
| Steps-to-Complete (M2.2)  | 6.0 ± 0.0            | 2.0 ± 0.0              | 66.7%           | ≥50% ✓        |

## Formulas

```
Time Reduction = (87.0 - 19.0) / 87.0 × 100% = 78.2%
Step Reduction = (6.0 - 2.0) / 6.0 × 100% = 66.7%
```

## Interpretation

| Result                  | Interpretation         |
| ----------------------- | ---------------------- |
| ≥50% reduction on both  | H2 supported           |
| ≥50% on one metric only | H2 partially supported |
| <50% on both            | H2 not supported       |

**Outcome:** H2 supported — the platform reduces Time-to-Complete by 78.2% and Steps-to-Complete by 66.7%, both exceeding the ≥50% threshold.

## Limitations

- Time metric is conservative lower bound (glue script + debug were excluded from repeated-trial measurement)
- Self-as-evaluator; mitigated by objective metrics and screen recording
- Expert user; generalization to novices covered by SRQ4
