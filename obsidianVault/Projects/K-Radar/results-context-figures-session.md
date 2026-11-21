---
name: results-context-figures-session
description: Session-transfer summary of the 8 Results-section figures built for weather/environment/tod/distance/frame_density stratification and TP/FP/FN, script state and open decisions
metadata:
  type: project
---

# Results-section context figures — session state (2026-09-04)

**Script:** `docs/crossproduct_figures/generate_results_context_figures.py`
**Source:** `repos/K-Radar/outputs/robustness_reports/crossproduct_v2/summary_full_density.parquet`
(finest-grain: condition x cls x weather x time_of_day x environment x distance_bucket x
frame_density — 0%-null, fixed 2026-08-31 per [[exhaustive-crossproduct-phase2-progress]])
**Run:** `uv run --project test-bed/src/Modules/robust_testing/kradar python docs/crossproduct_figures/generate_results_context_figures.py`

## 8 outputs (+.svg each)

| file | content |
|---|---|
| `8_weather_map_by_severity.png` | mAP vs severity, 1 line/weather (5: normal/fog/rain/sleet/overcast) |
| `9a_context_map_environment.png` | mAP vs severity, 1 line/environment (8 categories) |
| `9b_context_map_time_of_day.png` | mAP vs severity, day/night |
| `9c_context_map_distance.png` | mAP vs severity, 1 line/distance-from-ego bucket |
| `9d_context_map_frame_density.png` | mAP vs severity, 1 line/per-frame GT-object-density bucket |
| `10_tpfpfn_table.png` | plain table, 22 rows (baseline + 21 corrupted), TP/FP/FN/F1 cols |
| `11_severity_map_by_sensor.png` | mAP vs severity, 1 line/sensor (camera/lidar/radar), pooled over effect |

Items 8/9a-d/11 all now use a **2-panel layout**: top = mAP line, bottom = grouped bar chart of
`n_total` (=TP+FP+FN) on log y-axis, sharing the severity x-axis.

## Key decisions this session (in order)

1. Data source found by tracing `generate_metrics_table.py` -> `summary_full_density.parquet`;
   confirmed weather/env/tod/distance_bucket/frame_density are populated (not the earlier
   frame-identifier-bug-era stale data).
2. mAP = num_gt-weighted mean of `ap_restricted_range`, matching `generate_metrics_table.py`'s
   definition exactly. Severity ladder = `gaussian_noise`+`loss_partial` only (`loss_complete_zero`
   excluded, no low/med/high steps; `frame_deletion` excluded project-wide, pre-existing decision).
3. Item 2 (env/tod/distance/frame_density) split into 4 separate single-dimension charts per user
   request, not one faceted chart.
4. Uncertainty encoding went through 3 iterations, all superseded:
   - v1: shaded band = weighted SE across pooled sub-strata (dominated by variance of ~2-cell
     groups, not by real N — user rejected, looked like min/max).
   - v2: shaded band = binomial proportion SE using actual mAP as p — rejected because p(1-p)
     dominates near 0/100%, made low-N/high-mAP lines (fog) look more certain than high-N/mid-mAP
     lines (normal) — backwards from intent.
   - v3 (also superseded): shaded band = conservative proportion SE (p fixed at 0.5), driven only
     by N. Still just a band overlaid on the metric.
   - **Current (final): dropped the band entirely.** 2-panel layout instead — N shown as its own
     bar chart on its own axis, nothing inferred/decoded by the reader.
5. N-panel metric went through 1 correction: first used `num_gt` (pooled GT-object count) —
   **wrong**, because GT annotations are identical across original and every corrupted condition
   (corruption only touches sensor input, never labels) — bars were flat/misleading, and
   pooling multiple corrupted conditions into one severity point inflated N via pure duplication.
   Fixed to `n_total` (TP+FP+FN) — genuinely varies with corruption since a degraded detector
   produces different match counts; matches the project's own existing reliability convention
   (`N_FLOOR=30` on `n_total`, used everywhere else in `crossproduct/metrics.py`).
6. F1 (recomputed from pooled TP/FP/FN, not averaged) added as 5th column to the TP/FP/FN table —
   recommended as the standard TP/FP/FN-relating metric (no true negatives exist in detection, so
   accuracy/MCC don't apply).
7. **Open, not yet resolved**: true frame count (distinct sequence+frame pairs) was checked and
   found to be *constant across severity* within a weather category (corruption doesn't drop
   frames for the effects on this ladder) — so it's a valid "how much raw test data exists for
   this category" fact but cannot replace the `n_total` bars (which need to vary by severity to be
   useful). Could add as a static per-line annotation (e.g. legend `fog (N=1,445 frames)`) —
   not built yet, user hasn't confirmed they want it.

## Not touched

`thesis_report/include/Results.tex` — no `\includegraphics`/table LaTeX added yet, no captions or
placement decided. Waiting on user review of the 8 figures.
