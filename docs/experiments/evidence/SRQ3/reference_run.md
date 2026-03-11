# SRQ3 Reference Run

> **Note:** This reference run used `aggregation_v1.yaml` (300 iterations) to demonstrate real
> learning behavior. The N=20 batch runs use `aggregation_srq3.yaml` (10 iterations) for speed.
> A separate reference run with `aggregation_srq3` must be recorded before launching the batch.

## Reference Run Details (aggregation_v1 — learning quality demo)

| Field | Value |
|-------|-------|
| Experiment ID | aggregation_v1_20260310-170135 |
| Config Hash | 4e502660f94eae091a85d95a2dbf465573b77f01e1e3565f94e6dea7328bc5fd |
| Seed | 42 |
| Final Reward | -19.1231 |
| AUC | -10171.7911 |
| Iterations | 300 |
| Duration | 85 min |
| Timestamp | 2026-03-10T17:01:57 → 2026-03-10T18:27:01 |

## SRQ3 Batch Reference (aggregation_srq3 — 10 iterations)

| Field | Value |
|-------|-------|
| Experiment ID | aggregation_srq3_20260311-110742 |
| Config Hash | b9ff14a67be24984cfc457a5116e2b70a2791b2f29bcf856c5782006e8614340 |
| Seed | 42 |
| Final Reward | -46.8277 |
| AUC | -445.2401 |
| Iterations | 10 |
| Duration | ~6 min |
| Timestamp | 2026-03-11T11:07:42 → 2026-03-11T11:10:06 |

## Notes

Reproducibility confirmed: two independent 300-iteration runs with seed=42 produced
bit-for-bit identical reward trajectories (max deviation = 0.000000 across all 300 iterations).
This confirms platform determinism prior to the formal N=20 batch.
