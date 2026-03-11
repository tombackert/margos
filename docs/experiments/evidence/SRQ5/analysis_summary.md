# SRQ5 Analysis Summary

## Primary Metrics (M5.1-M5.5)

| Metric | Manual (Mean ± SD) | Platform (Mean ± SD) | Reduction (%) | Target |
|--------|-------------------|---------------------|---------------|--------|
| M5.1: Steps-to-Share | 8 (fixed) | | | Significant |
| M5.2: Time-to-Share | | | | Significant |
| M5.3: Time-to-First-Run | | | | Significant |
| M5.4: Time-to-Reproduce | | | | Significant |
| M5.5: Handoff-Success-Rate | | | | High |

## Secondary Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| M5.6: Bundle-Completeness | /8 | |
| M5.7: Setup-Divergence (mean mismatches) | | |

## Formulas

```
Handoff-Success-Rate = (# successful handoffs) / (total handoffs) × 100%
Time-to-Share Reduction = (Manual_mean - Platform_mean) / Manual_mean × 100%
Time-to-Reproduce Reduction = (Manual_mean - Platform_mean) / Manual_mean × 100%
```

## Interpretation

**Outcome:** [Fill after data collection]

| Outcome | Interpretation |
|---------|----------------|
| High success rate (≥90%) + significant time reduction | H5 strongly supported |
| High success rate + moderate time reduction | H5 supported |
| Low success rate regardless of time | H5 not supported |
