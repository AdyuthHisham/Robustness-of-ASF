---
name: dataset-distribution-histograms
description: Descriptive (non-model) distribution charts of K-Radar GT — objects/frame, distance from ego, weather/environment/time_of_day strata
---

# Dataset distribution histograms

For the AMSCUP thesis: pure dataset-description figures (not model performance), built from
`row_table_iou03.parquet` rather than raw K-Radar label files, since that table already joins
GT boxes with per-sequence `weather`/`environment`/`time_of_day` metadata.

Script: `test-bed/src/Modules/robust_testing/kradar/scripts/analysis/dataset_distributions.py`
Output: `test-bed/src/Modules/robust_testing/kradar/output/dataset_distributions/*.{png,svg}`

## Key methodology decisions

- **Condition filter: `condition == "original"` only.** GT is identical across every corrupted
  condition (only predictions change), so including all conditions would duplicate every GT
  object ~30x and, for `frame_deletion` conditions specifically, under-count the frames they drop
  — would have skewed the distribution shape, not just scaled it.
- **GT rows = `is_tp | is_fn`.** `is_fp` rows have no matched GT.
- **Distance recomputed from `gt_loc_x`/`gt_loc_z`**, not the table's `distance_from_ego` column
  — that column holds the *prediction's* position for TP/FP rows (null for FN), wrong for a
  GT-only view.
- **Strata (weather/environment/time_of_day) are per-sequence, not per-frame** — a single
  sequence has exactly one value for each. Confirmed via seq 46 (normal/highway/night, single
  point). Full 58-sequence set has 23 distinct combinations. Strata charts therefore use the full
  dataset, not just seq 46, while objects-per-frame and distance histograms could go either way
  (built against the full set here per user direction).
- Strata charts are **bar charts**, not histograms — the variables are categorical.

## Data scope actually used

13,727 frames, 35,456 GT objects (car=`sed` + bus), full 58-sequence set, condition=original.

**Bug caught 2026-08-27**: `frame` is a per-sequence index (0-299, reused identically by every
sequence) — `gt['frame'].n_unique()` collapses frame 0 of sequence 1 with frame 0 of sequence 46,
undercounting total frames to ~598. Fixed to dedupe on `(sequence, frame)` pairs, matching what
`build_strata_chart` was already doing correctly (which is how the discrepancy surfaced — its bar
totals didn't match the title's frame count).

## No shared plotting module existed

`scripts/analysis/` had no common styling/IO helper before this — `distance_line_charts.py`,
`density_line_charts.py`, etc. each duplicate matplotlib boilerplate. `dataset_distributions.py`
follows the same standalone-script pattern (PNG+SVG output, `build_all_charts(out_dir)` as the
library entry point) rather than introducing a new shared module, to match existing convention.
If more descriptive/EDA charts get added later, extracting a shared style module becomes worth it.

Related: [[robustness-metrics-tables]], [[context-radar-charts]]
