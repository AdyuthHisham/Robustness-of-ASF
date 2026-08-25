# AP radar charts by condition/severity/class — ASF, K-Radar

**Script:** `test-bed/src/Modules/robust_testing/kradar/scripts/analysis/radar_charts.py`
**Output:** `test-bed/src/Modules/robust_testing/kradar/output/radar_charts/*.png` (+`.svg`)

Built to visualize ASF detection robustness across the corruption taxonomy as spider/radar
charts, split by class (`sed`=car, `bus`) and severity (low/medium/high), for either a single
K-Radar sequence or pooled across all sequences. Complements the line/heatmap/bar figures in
[[asf-corruption-study-alvis]]'s downstream analysis (`repos/K-Radar/scripts/alvis/outputs/robustness_reports/build_figures.py`) with a per-condition, per-class, per-severity view those don't provide.

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

## AP by condition, severity, class — all 31 conditions (pooled across all sequences, IoU=0.3)

mAP for `sed` (car) and `bus`, `--sequence all`. Coverage <90% marked `*` (AP computed from a
crashed-mid-run subset of frames — see bug 2 above — not directly comparable to full-coverage
rows). Includes the 3 severity-less conditions (`CC`/`LC`/`RC`, ad hoc codes — not used in the
radar charts themselves, see "Not in the charts" below) alongside the 27 severity-tiered ones.

| Code                          | Severity | sed AP | bus AP | Coverage |
| ----------------------------- | -------- | ------ | ------ | -------- |
| OG (clean)                    | —        | 75.55  | 62.98  | 100%     |
| CF (camera frame_deletion)    | low      | 75.53  | 62.91  | 100%     |
| CF                            | medium   | 75.49  | 62.80  | 100%     |
| CF                            | high     | 75.42  | 62.54  | 100%     |
| CG (camera gaussian_noise)    | low      | 75.35  | 62.90  | 100%     |
| CG                            | medium   | 75.28  | 62.77  | 100%     |
| CG                            | high     | 75.18  | 62.17  | 100%     |
| CP (camera loss_partial)      | low      | 75.30  | 62.45  | 100%     |
| CP                            | medium   | 75.26  | 62.58  | 100%     |
| CP                            | high     | 75.25  | 62.75  | 100%     |
| CC (camera_loss_complete)     | —        | 75.31  | 64.03  | 100%     |
| LF (lidar frame_deletion)     | low      | 79.58  | 76.01  | 1.8%*    |
| LF                            | medium   | 72.42  | 64.44  | 0.4%*    |
| LF                            | high     | 74.05  | 26.02  | 0.2%*    |
| LG (lidar gaussian_noise)     | low      | 70.62  | 59.53  | 100%     |
| LG                            | medium   | 11.07  | 24.35  | 100%     |
| LG                            | high     | 11.23  | 20.17  | 100%     |
| LP (lidar loss_partial)       | low      | 77.79  | 62.82  | 100%     |
| LP                            | medium   | 78.04  | 62.94  | 100%     |
| LP                            | high     | 73.16  | 57.08  | 100%     |
| LC (lidar_loss_complete_zero) | —        | 43.38  | 37.28  | 100%     |
| RF (radar frame_deletion)     | low      | 81.22  | 73.12  | 4.1%*    |
| RF                            | medium   | 79.39  | 84.59  | 0.8%*    |
| RF                            | high     | 82.00  | 18.70  | 0.2%*    |
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
`CONDITION_CODE` in the script.

Reading the coverage-safe (100%) rows: lidar gaussian noise is the dominant *partial*-severity
failure mode — AP collapses to ~11–24 at medium/high severity for both classes, far below every
other severity-tiered effect. But `lidar_loss_complete_zero` (LC) is worse than any of those:
43.38/37.28 — a full sensor zero-out degrades ASF more than even high-severity lidar gaussian
noise, which makes sense (total information loss vs. corrupted-but-present signal). Camera and
radar complete-loss (CC, RC) are comparatively mild — CC barely moves off baseline (75.31 vs
75.55 clean), RC costs ~3 sed / ~5 bus points — consistent with ASF's fusion weighting relying
on lidar more heavily than camera or radar. The `*`-flagged frame_deletion rows can't be
trusted as robustness numbers — they're artifacts of the Alvis crash, not genuine severity
behavior; the 1-2 surviving frames per condition happened to be easy/hard by chance (e.g.
RF-high bus AP of 18.70 from a single frame, RF-medium bus AP of 84.59 from ~100 frames — no
monotonic severity trend visible, consistent with sampling noise rather than a real effect).

## Known gaps not yet handled

- `condition_frame_coverage.csv`/`coverage_iou03.csv` in
  `repos/K-Radar/scripts/alvis/outputs/robustness_reports/` already contain this exact
  coverage computation pooled across all sequences — `radar_charts.py` recomputes it directly
  from the row table instead of reading those, so it stays correct at the single-sequence
  scope those pooled CSVs don't cover. Worth being aware these are two independent
  computations of the same thing at different scopes, not one canonical source.
