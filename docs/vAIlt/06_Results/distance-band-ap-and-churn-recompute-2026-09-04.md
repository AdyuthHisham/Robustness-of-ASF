# Distance-band AP (41-point) and per-class churn — recompute record

Date: 2026-09-04. Source: fork task "Recompute distance-band AP and per-class churn."
Written into `thesis_report/include/Results.tex` (`tab:baseline_distance_weather`, `sec:distance_density`, `sec:churn_results`, `sec:headline_finding`).

## Distance-band AP (IoU 0.3 BEV, 41-point interpolation via `ap_metrics.compute_ap_grouped`)

Source: `full_denormalized_table_22cond.parquet`, grouped by `[cls, distance_bucket]`, `condition=='original'`.
Bands: `distance_bucket` edges `[20,40,60]` → 0–20m / 20–40m / 40–60m / 60–75m.

| Band | Sedan AP | Sedan N | Bus AP | Bus N |
|---|---|---|---|---|
| 0–20m | 76.02 | 8,695 | 67.71 | 1,678 |
| 20–40m | 76.23 | 9,204 | 77.10 | 2,531 |
| 40–60m | 80.23 | 8,163 | 56.82 | 1,093 |
| 60–75m | 73.97 | 3,551 | 50.88 | 541 |

Supersedes prior sedan-only numbers (55.4/54.9/48.7/41.8), which were computed on an over-stratified table (crossed with weather×tod×env) rather than marginal-by-distance, and did not sum near the 77.86 baseline. Also invalidated the prior "corruption hurts near-range more" claim — far range is hit hardest for both classes.

## Per-class churn (transition-table pipeline, `run_churn_pass4.py` matcher, grouped by `[condition, cls]`)

`camera_frame_deletion*` excluded from all conditions per standing instruction.

Headline: `lidar_gaussian_noise_high` churn — sedan 63.8%, bus 46.4% (17.4pt gap).

Pattern: bus churns more than sedan under every radar (7/7) and camera (7/7) condition; LiDAR conditions mixed (sedan higher 4/7, bus higher 3/7).

Full per-condition table not re-listed here — see `sec:churn_results` in Results.tex for the values as published.
