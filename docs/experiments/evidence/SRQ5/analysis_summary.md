# SRQ5 Analysis Summary

## Primary Metrics (M5.1-M5.5)

| Metric                     | Manual (Mean ± SD)  | Platform (Mean ± SD)  | Reduction (%)   | Target      |
| -------------------------- | ------------------- | --------------------- | --------------- | ----------- |
| M5.1: Steps-to-Share       | 8 (fixed)           | 1 (fixed)             | 87.5%           | Significant |
| M5.2: Time-to-Share        | 107.7 ± 24.1 sec    | 37.4 ± 18.2 sec       | 65.3%           | Significant |
| M5.3: Time-to-First-Run    | 52.6 ± 11.4 sec     | 56.5 ± 11.6 sec       | -7.4%           | Significant |
| M5.4: Time-to-Reproduce    | 122.3 ± 30.3 sec    | 66.2 ± 13.1 sec       | 45.9%           | Significant |
| M5.5: Handoff-Success-Rate | 100% (10/10)        | 100% (10/10)          | —               | High        |

Negative reduction indicates the platform condition took longer than the manual baseline.

## Secondary Metrics

| Metric                                   | Value           | Notes                                                                                                                                 |
| ---------------------------------------- | --------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| M5.6: Bundle-Completeness                | 8/8             | All required and optional components are present in the retained SRQ5 export bundle; recordings show the same structure across trials |
| M5.7: Setup-Divergence (mean mismatches) | 3.0 mismatches  | Recording comparison output shows mismatches on NumPy, PettingZoo, and PyTorch, while Python, OS, Gymnasium, Pydantic, and Ray match  |

## Formulas

```
Handoff-Success-Rate = (# successful handoffs) / (total handoffs) × 100%
Time-to-Share Reduction = (Manual_mean - Platform_mean) / Manual_mean × 100%
Time-to-First-Run Reduction = (Manual_mean - Platform_mean) / Manual_mean × 100%
Time-to-Reproduce Reduction = (Manual_mean - Platform_mean) / Manual_mean × 100%
```

## Interpretation

**Outcome:** H5 partially supported.

These timing metrics are computed from the recorded handoff trials documented in the protocol timestamp table.

| Outcome                                               | Interpretation         |
| ----------------------------------------------------- | ---------------------- |
| High success rate (≥90%) + significant time reduction | H5 strongly supported  |
| High success rate + moderate time reduction           | H5 supported           |
| High success rate + mixed timing results              | H5 partially supported |
| Low success rate regardless of time                   | H5 not supported       |

The platform preserved a 100% handoff success rate and substantially reduced sharing effort: steps-to-share fell from 8 to 1, and time-to-share fell by 65.3%. Across the recorded handoff trials, time-to-reproduce is 45.9% lower than the manual baseline.

Time-to-first-run remains 7.4% higher in the platform condition in this prepared-collaborator setup, driven by import overhead before the first execution. The platform still improves the full handoff by automating verification and reducing sharing work.
