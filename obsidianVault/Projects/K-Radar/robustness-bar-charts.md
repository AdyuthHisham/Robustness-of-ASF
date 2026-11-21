# mAP/mATE/mASE bar charts by stratification dimension — ASF, K-Radar

**Script:** `test-bed/src/Modules/robust_testing/kradar/scripts/analysis/bar_charts.py`
**Output:** `test-bed/src/Modules/robust_testing/kradar/output/bar_charts/*.png` (+`.svg`), 36 charts

Bar-chart complement to [[robustness-radar-charts]] and [[context-radar-charts]], built for
LaTeX inclusion. Two chart families against `row_table_iou03.parquet` (IoU=0.3):

1. **Severity/modality**: one bar per condition (18 = 3 sensors × {gaussian_noise,
   loss_partial} × {low,medium,high} + `original`), color = sensor, hatched if <90% frame
   coverage vs `original` (same threshold as `radar_charts.py`).
2. **Context dimensions**: grouped bar chart per (metric, dimension) for dimension in
   {label(cls), time_of_day, weather, environment, **frame_density**}. x-axis = 6 (sensor,
   effect) codes + `OG`, pooled across severity (severity already covered by chart family 1).

Both families produced in raw-value and **Rb** (Gao et al. robustness ratio, `= corrupted /
clean`, == RR/mRR/RS per [[robustness-metric-selection]]) variants. `frame_deletion` and
`loss_complete` excluded throughout, matching `heatmaps.py`'s convention (crashed Alvis runs /
not part of the core severity sweep).

**Rb charts are diverging bar charts**, not Rb plotted directly. `rb_to_signed_pct_change()`
re-expresses Rb as `(Rb-1)*100` for mAP but `(1-Rb)*100` for mATE/mASE — sign-flipped so
"positive = improved, negative = degraded" holds uniformly regardless of whether the underlying
metric is higher-is-better or lower-is-better (avoids the easy misread of "Rb_mATE > 1 = better"
that a raw ratio invites). y=0 is centered vertically (symmetric `ylim`), OG is dropped (its
Rb is trivially 1 / 0% change — shown only as the y=0 reference line), and bars are colored
green/red by sign in the single-series chart (severity/modality colors are dropped there since
sign color and x-tick condition code together already carry sensor+severity+direction).

**y-axis is symlog**, not linear (`_apply_symlog`, linthresh=1%, linscale=1.5), triggered
whenever the largest |value| exceeds 3× the linear threshold. Without it, outliers like
`LG-H`'s ~-78% mAP change squash near-zero bars (`CG-L`'s ~-0.5%) to invisible slivers on a
linear axis — symlog keeps the region near 0 linear and compresses the tail logarithmically so
both extremes stay legible on one axis, at the cost of bar length no longer being linearly
proportional to value (readers need the axis labels, not just visual bar-length ratios).

**Minimum visible bar height** (`_floor_for_visibility`, `MIN_VISIBLE_PCT = 0.05`): even under
symlog, a genuinely tiny nonzero value (e.g. lidar-loss_partial/night's mAP change of -0.011%,
found 2026-08-27 -- real data, not a missing-value gap) draws as a sub-pixel sliver,
indistinguishable from "no bar". Bars under this threshold are drawn at a fixed floor height
(sign preserved) with the true value annotated as small rotated text next to the bar, so nothing
with real data renders as empty space.

## Key finding vs. prior assumption

Project memory had mATE/mASE marked blocked pending a GT-object spatial matching module. Audit
on 2026-08-27 found this landed already: `row_table_iou03.parquet` has `is_tp/is_fp/is_fn`,
`matched_gt_row_id`, `iou`, and paired `loc_*`/`rotation_y` vs `gt_*` columns, and mATE/mASE
were already being computed from it in five other scripts (`heatmaps.py`, `box_plots.py`,
`distance_line_charts.py`, `distance_robustness_charts.py`, `context_radar_charts.py`) before
this one existed. **mAOE remains genuinely unimplemented** — `gt_rotation_y` exists but nothing
computes orientation error anywhere in the pipeline; out of scope for this chart set, logged as
follow-up work.

## New dimension: frame_density

Not previously computed anywhere. Defined as # GT objects (TP+FN rows) in a frame under
`original`, joined onto every condition by `(sequence, frame)` since it's a scene property
invariant to corruption. Distribution is right-skewed (median 2, max 16 in seq46), so binned
1 / 2-3 / 4+ rather than by tercile-of-raw-count, which would leave the top bin nearly empty.

## Design decisions carried over from siblings

- AP via `ap_metrics.compute_ap_grouped` (not reimplemented), same as every other script here.
- ATE/ASE formulas identical to `heatmaps.py`'s pooled version (mean over TP rows, both classes
  together) — except for the `label` dimension, which naturally splits by class instead.
- No coverage hatching on the context-dimension charts: pooling three severities into one
  (sensor, effect) code makes a single coverage number ambiguous per cell; documented as a
  known limitation in the script docstring rather than faked.
