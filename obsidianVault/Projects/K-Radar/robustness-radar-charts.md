# AP radar charts by condition/severity/class — ASF, K-Radar

**Script:** `test-bed/src/Modules/robust_testing/kradar/scripts/analysis/radar_charts.py`
**Output:** `test-bed/src/Modules/robust_testing/kradar/output/radar_charts/*.png` (+`.svg`)

Built to visualize ASF detection robustness across the corruption taxonomy as spider/radar
charts, split by class (`sed`=car, `bus`) and severity (low/medium/high), for either a single
K-Radar sequence or pooled across all sequences. Complements the line/heatmap/bar figures in
[[asf-corruption-study-alvis]]'s downstream analysis (`repos/K-Radar/scripts/alvis/outputs/robustness_reports/build_figures.py`) with a per-condition, per-class, per-severity view those don't provide.
See also [[context-radar-charts]] for the context-field (weather/environment/time_of_day)
breakdown built on top of this, and [[frame-identifier-bug]] for a frame-identity bug that
breakdown surfaced.

## Design decisions

- **AP source**: reuses `ap_metrics.py`'s `compute_ap_grouped` (K-Radar's own 41-point
  interpolated-AP evaluator, ported from `utils/kitti_eval/eval_revised.py`) against
  `row_table_iou03.parquet` (IoU=0.3) — not reimplemented. Cross-submodule import via
  `sys.path.insert` from the test-bed module into `repos/K-Radar/scripts/alvis/`.
- **6 charts per run**: {sed, bus} × {low, medium, high}. 10 axes each — 9 severity-tiered
  (sensor × effect: camera/lidar/radar × frame_deletion/gaussian_noise/loss_partial) plus
  `OG` (original/clean, bold star marker, reference point). `loss_complete`/`loss_complete_zero`
  conditions are excluded from these charts — they have no severity tiers so don't fit the
  structure.
- **Two-letter axis codes**: `OG`=clean, else sensor-initial + effect-initial (`CF`/`CG`/`CP`,
  `LF`/`LG`/`LP`, `RF`/`RG`/`RP`). No collisions.
- **Scale**: shared y-limit across a class's 3 severity charts (independent per class) so
  low/medium/high are directly comparable side by side; sed and bus get independent scales.
- **`--sequence all`** pools every sequence into one AP computation (same convention as
  `build_figures.py`'s pooled mAP) vs `--sequence <N>` for a single sequence.

## Bugs this surfaced (both about silently-plotted bad data)

1. **Missing conditions ≠ zero.** Sequence 46 has zero rows at all for
   `radar_frame_deletion_medium`, `lidar_frame_deletion_medium`, `lidar_frame_deletion_high`.
   Fix: render as a genuine gap in the line, axis labeled `(N/A)`, never zero-filled or
   interpolated across.
2. **Low frame coverage from mid-run Alvis crashes, computed as if complete.** Several
   `frame_deletion` conditions (esp. radar/lidar, medium/high) only have 0.2–5% of the
   `original` baseline's frame count for a given sequence — e.g. seq46's
   `radar_frame_deletion_high` AP was computed from **1 surviving frame**. This is the same
   crash class as [[asf-corruption-study-alvis]]'s "silent-completeness" disk-quota bug — the
   sbatch job's success check only looks at whether prediction files exist, not whether the
   full frame set got processed, so a partial run reports clean `COMPLETED`.
   Fix: `compute_condition_coverage()` computes each condition's frame-pair count vs
   `original` (same scope: per-sequence or pooled) and flags anything under the 90% threshold
   `build_figures.py` already uses elsewhere in the repo — drawn as a disconnected orange `x`
   with an explicit `(N.N% cov)` label instead of a normal filled dot on the line, plus a
   footnote on any chart that has one. Never silently presented as equivalent to a
   fully-covered condition.

## 2026-08-25 update: `frame_deletion` excluded, not just flagged

`outputs/all_preds.txt`/`all_gts.txt` were refreshed from a fresh Alvis pull on 2026-08-25.
Regenerating `row_table_iou03.parquet` against the fresh data showed `camera_frame_deletion_*`
had silently been replaced by a rerun logged under `camera_frame_deletion_new_*` condition
names — `scripts/alvis/ingest.py` was patched (`_use_new_camera_frame_deletion`) to drop the
stale `camera_frame_deletion_*` rows and rename `camera_frame_deletion_new_*` down to the plain
name, so all three sensors are parsed under one consistent condition-naming scheme again.

That rerun crashed too, the same way lidar/radar's `frame_deletion` always did (bug #2 above):
post-fix coverage is still 0.0–5.3% of `original` for every sensor's `frame_deletion_{low,
medium,high}` (`coverage_iou03.csv`). **Decision: `frame_deletion` is now excluded from every
metrics table on this page and in [[robustness-metrics-tables]]**, not just `*`-flagged — 1–730
surviving frames per condition isn't a usable robustness signal for any of the three sensors.
The radar-chart PNGs themselves still render all 9 severity-tiered axes including `CF`/`LF`/`RF`
(the script's own low-coverage-flagging from bug #2 already marks them, and reworking the chart
script to drop 3 of its 9 axes was out of scope for this pass) — only the **tabulated data
below** on this page has frame_deletion removed. Every other condition's AP is unchanged from
before the refresh; the underlying row-level match data for gaussian_noise/loss_partial/
loss_complete didn't move.

## AP by condition, severity, class — 22 conditions (pooled, IoU=0.3, frame_deletion excluded)

mAP for `sed` (car) and `bus`, `--sequence all`. All rows now at 100% coverage. Includes the 3
severity-less conditions (`CC`/`LC`/`RC`, ad hoc codes — not used in the radar charts
themselves, see "Not in the charts" below) alongside the 18 severity-tiered ones (gaussian_noise
+ loss_partial only — frame_deletion dropped per the note above).

| Code                          | Severity | sed AP | bus AP | Coverage |
| ----------------------------- | -------- | ------ | ------ | -------- |
| OG (clean)                    | —        | 75.55  | 62.98  | 100%     |
| CG (camera gaussian_noise)    | low      | 75.35  | 62.90  | 100%     |
| CG                            | medium   | 75.28  | 62.77  | 100%     |
| CG                            | high     | 75.18  | 62.17  | 100%     |
| CP (camera loss_partial)      | low      | 75.30  | 62.45  | 100%     |
| CP                            | medium   | 75.26  | 62.58  | 100%     |
| CP                            | high     | 75.25  | 62.75  | 100%     |
| CC (camera_loss_complete)     | —        | 75.31  | 64.03  | 100%     |
| LG (lidar gaussian_noise)     | low      | 70.62  | 59.53  | 100%     |
| LG                            | medium   | 11.07  | 24.35  | 100%     |
| LG                            | high     | 11.23  | 20.17  | 100%     |
| LP (lidar loss_partial)       | low      | 77.79  | 62.82  | 100%     |
| LP                            | medium   | 78.04  | 62.94  | 100%     |
| LP                            | high     | 73.16  | 57.08  | 100%     |
| LC (lidar_loss_complete_zero) | —        | 43.38  | 37.28  | 100%     |
| RG (radar gaussian_noise)     | low      | 75.53  | 65.24  | 100%     |
| RG                            | medium   | 65.56  | 55.18  | 100%     |
| RG                            | high     | 60.66  | 51.09  | 100%     |
| RP (radar loss_partial)       | low      | 75.54  | 65.24  | 100%     |
| RP                            | medium   | 75.44  | 63.36  | 100%     |
| RP                            | high     | 70.24  | 57.20  | 100%     |
| RC (radar_loss_complete_zero) | —        | 72.40  | 58.32  | 100%     |

**Not in the charts:** `CC`/`LC`/`RC` (`*_loss_complete`/`*_loss_complete_zero`) have no
severity tier and don't appear as axes in `radar_charts.py`'s 6 spider charts — they're
included in this table only, not the PNG/SVG figures. Their codes aren't defined in
`CONDITION_CODE` in the script. `frame_deletion` (`CF`/`LF`/`RF`) still appear as chart axes
(low-coverage-flagged, per bug #2) even though they're dropped from this table.

Lidar gaussian noise is the dominant *partial*-severity failure mode — AP collapses to ~11–24
at medium/high severity for both classes, far below every other severity-tiered effect. But
`lidar_loss_complete_zero` (LC) is worse than any of those: 43.38/37.28 — a full sensor
zero-out degrades ASF more than even high-severity lidar gaussian noise, which makes sense
(total information loss vs. corrupted-but-present signal). Camera and radar complete-loss (CC,
RC) are comparatively mild — CC barely moves off baseline (75.31 vs 75.55 clean), RC costs ~3
sed / ~5 bus points — consistent with ASF's fusion weighting relying on lidar more heavily than
camera or radar.

## Full metrics table — 22 conditions × 2 classes (source: all_preds.txt via row_table_iou03.parquet, frame_deletion excluded)

`all_preds.txt` (`repos/K-Radar/outputs/`) is the source `ingest.py` matches against
`all_gts.txt` to produce `row_table_iou03.parquet` (adds `is_tp`/`is_fp`/`is_fn`/`iou` per row
at IoU=0.3) — the same table every other section on this page draws from. This table is every
field `ap_metrics.py`'s `compute_ap_grouped` returns, not just AP: `num_gt` (ground truth boxes
for that condition+class), `num_tp`/`num_fp` (at the recall-optimal threshold sweep), and
coverage. Sorted alphabetically by condition, both classes per row group.

| Condition                    | Class | AP    | num_gt | num_tp | num_fp | Coverage |
| ---------------------------- | ----- | ----- | ------ | ------ | ------ | -------- |
| camera_gaussian_noise_high   | bus   | 62.17 | 5843   | 3839   | 958    | 100.0%   |
| camera_gaussian_noise_high   | sed   | 75.18 | 29613  | 22620  | 4141   | 100.0%   |
| camera_gaussian_noise_low    | bus   | 62.90 | 5843   | 3936   | 984    | 100.0%   |
| camera_gaussian_noise_low    | sed   | 75.35 | 29613  | 22608  | 3827   | 100.0%   |
| camera_gaussian_noise_medium | bus   | 62.77 | 5843   | 3910   | 955    | 100.0%   |
| camera_gaussian_noise_medium | sed   | 75.28 | 29613  | 22631  | 4037   | 100.0%   |
| camera_loss_complete         | bus   | 64.03 | 5843   | 3965   | 1443   | 100.0%   |
| camera_loss_complete         | sed   | 75.31 | 29613  | 22316  | 3564   | 100.0%   |
| camera_loss_partial_high     | bus   | 62.75 | 5843   | 3942   | 1026   | 100.0%   |
| camera_loss_partial_high     | sed   | 75.25 | 29613  | 22706  | 4185   | 100.0%   |
| camera_loss_partial_low      | bus   | 62.45 | 5843   | 3926   | 977    | 100.0%   |
| camera_loss_partial_low      | sed   | 75.30 | 29613  | 22695  | 3904   | 100.0%   |
| camera_loss_partial_medium   | bus   | 62.58 | 5843   | 3936   | 992    | 100.0%   |
| camera_loss_partial_medium   | sed   | 75.26 | 29613  | 22607  | 3990   | 100.0%   |
| lidar_gaussian_noise_high    | bus   | 20.17 | 5843   | 1100   | 216    | 100.0%   |
| lidar_gaussian_noise_high    | sed   | 11.23 | 29613  | 2331   | 327    | 100.0%   |
| lidar_gaussian_noise_low     | bus   | 59.53 | 5843   | 3644   | 912    | 100.0%   |
| lidar_gaussian_noise_low     | sed   | 70.62 | 29613  | 21400  | 3312   | 100.0%   |
| lidar_gaussian_noise_medium  | bus   | 24.35 | 5843   | 1361   | 309    | 100.0%   |
| lidar_gaussian_noise_medium  | sed   | 11.07 | 29613  | 2771   | 573    | 100.0%   |
| lidar_loss_complete_zero     | bus   | 37.28 | 5843   | 2290   | 866    | 100.0%   |
| lidar_loss_complete_zero     | sed   | 43.38 | 29613  | 13209  | 2919   | 100.0%   |
| lidar_loss_partial_high      | bus   | 57.08 | 5843   | 3555   | 844    | 100.0%   |
| lidar_loss_partial_high      | sed   | 73.16 | 29613  | 22011  | 3436   | 100.0%   |
| lidar_loss_partial_low       | bus   | 62.82 | 5843   | 3889   | 1010   | 100.0%   |
| lidar_loss_partial_low       | sed   | 77.79 | 29613  | 23153  | 3725   | 100.0%   |
| lidar_loss_partial_medium    | bus   | 62.94 | 5843   | 3849   | 907    | 100.0%   |
| lidar_loss_partial_medium    | sed   | 78.04 | 29613  | 23381  | 3597   | 100.0%   |
| original                     | bus   | 62.98 | 5843   | 3925   | 1068   | 100.0%   |
| original                     | sed   | 75.55 | 29613  | 22859  | 3780   | 100.0%   |
| radar_gaussian_noise_high    | bus   | 51.09 | 5843   | 3173   | 711    | 100.0%   |
| radar_gaussian_noise_high    | sed   | 60.66 | 29613  | 18037  | 1798   | 100.0%   |
| radar_gaussian_noise_low     | bus   | 65.24 | 5843   | 3962   | 1039   | 100.0%   |
| radar_gaussian_noise_low     | sed   | 75.53 | 29613  | 22793  | 3694   | 100.0%   |
| radar_gaussian_noise_medium  | bus   | 55.18 | 5843   | 3403   | 1071   | 100.0%   |
| radar_gaussian_noise_medium  | sed   | 65.56 | 29613  | 19416  | 2165   | 100.0%   |
| radar_loss_complete_zero     | bus   | 58.32 | 5843   | 3716   | 1297   | 100.0%   |
| radar_loss_complete_zero     | sed   | 72.40 | 29613  | 21509  | 3375   | 100.0%   |
| radar_loss_partial_high      | bus   | 57.20 | 5843   | 3565   | 1074   | 100.0%   |
| radar_loss_partial_high      | sed   | 70.24 | 29613  | 20844  | 2731   | 100.0%   |
| radar_loss_partial_low       | bus   | 65.24 | 5843   | 3950   | 1046   | 100.0%   |
| radar_loss_partial_low       | sed   | 75.54 | 29613  | 22814  | 3683   | 100.0%   |
| radar_loss_partial_medium    | bus   | 63.36 | 5843   | 3934   | 996    | 100.0%   |
| radar_loss_partial_medium    | sed   | 75.44 | 29613  | 22551  | 3429   | 100.0%   |

`num_gt` is identical across every surviving condition — 29,613 `sed` / 5,843 `bus` GT boxes
pooled across all sequences (matching `original`) — since every remaining row is at 100%
coverage; `frame_deletion`'s far smaller GT counts (13–64 GT boxes total in the pre-exclusion
version of this table) are exactly why it was dropped rather than kept `*`-flagged.

See [[robustness-metrics-tables]] for individual per-condition tables of every other metric
defined in the repo (mAP, RCE, FP/FN, miss rate, churn, mATE/mASE, zero-ablation retention, Rb,
CRI) — this page only covers AP.

## Known gaps not yet handled

- `condition_frame_coverage.csv`/`coverage_iou03.csv` in
  `repos/K-Radar/scripts/alvis/outputs/robustness_reports/` already contain this exact
  coverage computation pooled across all sequences — `radar_charts.py` recomputes it directly
  from the row table instead of reading those, so it stays correct at the single-sequence
  scope those pooled CSVs don't cover. Worth being aware these are two independent
  computations of the same thing at different scopes, not one canonical source.
- Radar-chart PNGs/SVGs weren't regenerated in this pass (test-bed's `kradar_visibility` uv
  venv is missing `matplotlib` locally despite it being declared in `pyproject.toml` — `uv
  sync` reports "already installed" but the import fails; unresolved, needs a fresh
  investigation before the figures can be rebuilt). Only the tabulated data above reflects the
  2026-08-25 regeneration; the PNG/SVG files under `output/radar_charts/` are stale relative to
  it, still show 9 axes without any exclusion applied, and should not be treated as current.
- `frame_deletion` robustness (all 3 sensors) remains unmeasured pending a clean, non-crashing
  rerun — it is excluded from tables, not silently zero.
