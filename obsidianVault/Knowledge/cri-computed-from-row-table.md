# CRI is computable directly from row_table_iou03.parquet — prior "blocked" status was stale

CRI (Corruption Robustness Index, RoHOI Eq. 2) was flagged blocked across
several session logs (most recently
`docs/vAIlt/06_Results/exhaustive-crossproduct-phase1-audit-20260831.md`,
closed 2026-09-01) on the grounds that it needs raw per-severity AP from a
separate source, `ap_robustness_local.json`, that was never joined to the
crossproduct pipeline. **That reasoning no longer holds.** Verified
2026-09-01: `row_table_iou03.parquet`'s `condition` column already encodes
severity per corruption effect (e.g. `camera_gaussian_noise_low/medium/high`),
and `compute_ap_grouped(row_table, ["condition", "cls"])` — the same helper
`master_metrics_table.py` already calls for mAP/RCE — gives exactly the raw
`M_{c,l}` per-severity AP that CRI's formula needs. The `ap_robustness_local.json`
dependency was a real blocker only before this helper existed in its current
form; the note calling CRI "blocked" was never updated after the tooling
caught up. See [[robustness-metric-selection]] and
`crossproduct_trends_and_anomalies_metrics_coverage.md` (project doc) for
the audit that surfaced this.

## Formula (RoHOI Eq. 2, Wen et al. arXiv:2507.09111v3)

```
CRI_c = (mean(AP_low, AP_medium, AP_high) / AP_clean) / (log(1 + pstdev(AP_low, AP_medium, AP_high)) + 1)
```

Population stdev, not sample — severity tiers are a fixed complete set, not
a sample. Requires >=2 severity tiers with data and a non-zero clean AP;
single-tier effects (`*_loss_complete_zero`, no low/medium/high split) return
None rather than a misleading sigma=0 "perfectly stable" score.

**Important gotcha** (from `compute_robustness.py`'s own docstring): stdev
must be taken on raw AP, not on the pre-normalized Rb ratio (`AP/AP_clean`) —
stdev isn't scale-invariant under division, so computing sigma from Rb
instead of raw AP silently rescales the variance penalty by `1/AP_clean`
before it hits the log stabilizer, weakening it by ~2.8x in the worst
observed case.

## Computed values (2026-09-01, current `row_table_iou03.parquet`, IoU=0.3, classes sed/bus only — this table's own class coverage)

| Effect | Class | AP low/med/high | Clean AP | CRI |
|---|---|---|---|---|
| camera_gaussian_noise | sed | 75.50 / 75.39 / 75.36 | 77.86 | 0.9153 |
| camera_gaussian_noise | bus | 67.46 / 67.25 / 66.99 | 67.93 | 0.8417 |
| camera_loss_partial | sed | 75.49 / 75.42 / 75.41 | 77.86 | 0.9358 |
| camera_loss_partial | bus | 67.40 / 67.34 / 67.51 | 67.93 | 0.9292 |
| camera_frame_deletion | sed | 83.79 / 84.35 / 83.49 | 77.86 | 0.8272 |
| camera_frame_deletion | bus | 74.97 / 75.22 / 43.90 | 67.93 | 0.2537 |
| lidar_gaussian_noise | sed | 72.97 / 17.81 / 16.06 | 77.86 | 0.1061 |
| lidar_gaussian_noise | bus | 63.76 / 29.60 / 27.07 | 67.93 | 0.1525 |
| lidar_loss_partial | sed | 78.02 / 78.19 / 75.43 | 77.86 | 0.5462 |
| lidar_loss_partial | bus | 67.97 / 67.89 / 60.37 | 67.93 | 0.3825 |
| lidar_frame_deletion | sed | 73.21 / 61.48 / 40.09 | 77.86 | 0.2029 |
| lidar_frame_deletion | bus | 63.49 / 54.42 / 35.89 | 67.93 | 0.2141 |
| radar_gaussian_noise | sed | 77.85 / 65.79 / 58.70 | 77.86 | 0.2719 |
| radar_gaussian_noise | bus | 68.12 / 57.75 / 49.35 | 67.93 | 0.2721 |
| radar_loss_partial | sed | 77.86 / 75.60 / 70.53 | 77.86 | 0.3991 |
| radar_loss_partial | bus | 68.04 / 68.02 / 58.06 | 67.93 | 0.3476 |
| radar_frame_deletion | sed | 73.21 / 61.48 / 40.08 | 77.86 | 0.2028 |
| radar_frame_deletion | bus | 63.49 / 54.38 / 36.00 | 67.93 | 0.2145 |
| {camera,lidar,radar}_loss_complete_zero | sed, bus | single-tier only | — | None (formula requires >=2 tiers) |

## Reading the numbers

CRI is lowest (worst) for **lidar_gaussian_noise** (0.11-0.15) — both the
biggest mean-AP collapse (sed: 77.9->73.0->17.8->16.1) and a huge stdev
compound into the score, consistent with [[robustness-metric-selection]] and
prior findings that LiDAR gaussian noise is the most destructive single
corruption in this study. **frame_deletion** on camera is a striking split:
`sed` scores 0.83 (stable) while `bus` scores 0.25 (collapses only at
`high` severity, 75.2->43.9) — same effect, same modality, opposite class
outcomes. CRI correctly flags the `bus` case as unstable despite its `low`/
`medium` AP being on par with `sed`'s, because the formula penalizes the
volatility, not just the mean.

**Anomaly worth a follow-up**: `radar_frame_deletion` and `lidar_frame_deletion`
AP values are nearly identical (e.g. sed high: 40.09 vs 40.08) despite being
different modalities corrupted independently — this needs checking against
[[frame-key-derivation-kradar]] / the 2026-09-01 frame-key fix to rule out a
data-pipeline artifact (e.g. both conditions accidentally reading the same
underlying frame-drop mask) rather than a genuine coincidence. Not
investigated further here — flagging for [[exhaustive-crossproduct-anomaly-addendum]]
or a dedicated follow-up.

## Caveat on class coverage

These numbers only cover `sed` and `bus` because that's what's populated in
the current `row_table_iou03.parquet` pull used for this computation — check
against the full class list the crossproduct pipeline reports elsewhere
before treating this as the final CRI table; if more classes are present in
a fuller run, rerun the same `compute_ap_grouped` + CRI formula against them.
