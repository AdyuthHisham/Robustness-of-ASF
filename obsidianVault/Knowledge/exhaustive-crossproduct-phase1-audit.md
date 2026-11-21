---
name: exhaustive-crossproduct-phase1-audit
description: Phase 1 read-only audit findings for the exhaustive cross-product analysis task on full_denormalized_table.parquet — AP feasibility, GT-pairing stability, coverage raggedness, cell sparsity, orientation convention
metadata:
  type: project
---

# Phase 1 audit: exhaustive cross-product analysis of full_denormalized_table.parquet

Read-only audit (no writes, no metric computation) for a new task: build a
reusable, parameterized cross-product analysis module (`metrics.py` /
`crossproduct.py` / `queries.py` / `plots.py`) over
`repos/K-Radar/outputs/robustness_reports/full_denormalized_table.parquet`
(1,109,578 rows, 33 cols — same file documented in
[[full-denormalized-exploratory-pass]]). This note captures the audit's
findings and the two still-open decisions; complements (does not replace)
[[asf-map-eval-mechanics]] and [[gt-transition-analysis]].

## AP feasibility — restricted-range is correct, matches K-Radar's own convention

Traced `all_preds.txt` (source of `row_table_iou03.parquet` →
`full_denormalized_table.parquet`) back through
`models/model_utils/centernet_utils.py:213` (`SCORE_THRESH` post-NMS filter,
configured `0.1` across every `ASF_v2_0_*.yml`) and confirmed K-Radar's own
official benchmark AP (`pipelines/pipeline_detection_v1_0.py:651` →
`get_official_eval_result_revised`, see [[asf-map-eval-mechanics]] step 3)
reads predictions from the **same** post-NMS-filtered text files, with no
further score filtering (`eval_revised.py`'s `score_thresh=-1` default). This
is standard KITTI-style protocol, not a gap specific to this table: AP is
always computed on a detector's post-processed output, never on raw
unfiltered scores. **True unbounded AP was never available at any point in
this pipeline, K-Radar's own leaderboard number included** — so reporting a
score-range-restricted AP alongside fixed-threshold P/R/F1 is not a
compromise relative to some more-correct alternative that exists upstream.

Open, low-priority thread: observed score floor in the table is **0.30**,
not the configured 0.10. Not found in `ingest.py`/`build_denormalized_table.py`
— either a different eval config produced this sweep, or the checkpoint
simply never emitted scores in [0.1, 0.3) in practice (plausible — post-NMS
confidence distributions are often bimodal). Doesn't change the AP-framing
conclusion either way; just needs a caveat line in the eventual report.

## GT-object pairing (churn) — confirmed stable, unblocked

`matched_gt_row_id` is stable: for all 35,455 distinct GT objects (keyed by
exact `(sequence, frame, gt_loc_x/y/z, gt_rotation_y, gt_height/width/length,
cls)`), exactly one `matched_gt_row_id` value appears everywhere that object
shows up, across all 31 conditions — 0 collisions, 0 reassignment. Same
conclusion [[gt-transition-analysis]] reached independently via the
canonical-GT-table approach; this is just the direct empirical check on the
denormalized table's own ID column. `gt_transition_analysis.py`'s existing
matcher can be called directly (`iou_threshold=0.3` explicit — its library
default is 0.5, the bug documented in
[[full-denormalized-exploratory-pass]]).

## Coverage raggedness — quantified

Across all 31 conditions: the 22 healthy conditions (`original` +
gaussian_noise/loss_partial/loss_complete_zero × 3 modalities) have
58/58 sequences, ~40k rows each. The 9 `*_frame_deletion_*` conditions have
**102–1,674 rows, 31–55 sequences** — 25-400x smaller (known crash-coverage
issue, see [[full-denormalized-exploratory-pass]]). Common sequence
intersection across all 31 conditions: only 23/58. Confirmed the right fix
is what the prior pass already did — drop `frame_deletion` to the
22-condition scope, not shrink every condition to the 23-sequence
intersection (frame_deletion crashing is expected/by design per user,
2026-08-31).

## Cell sparsity at full cross-product granularity

`(condition × cls × weather × time_of_day)`, 22-cond scope: 396/440 possible
cells populated, 7.8% N<30, 17.2% N<100 — reportable.
`(condition × cls × weather × time_of_day × environment)`: only 979/3,520
possible cells populated (72% of the cross-product is empty), 19.7% N<30,
36.7% N<100. → environment should be a targeted drill-down, not a primary
stratification axis in every table.

## Orientation error convention — confirmed full heading, not axis

`rotation_y` (pred) ranges `[0.79, 7.07]` rad (unwrapped ~`[0,2π]`);
`gt_rotation_y` ranges `[-3.29, 3.44]` rad (`[-π,π]`) — naive subtraction
breaks near the wrap boundary. Resolved by checking K-Radar's own AOS
(Average Orientation Similarity) formula, `utils/kitti_eval/eval_revised.py:296,324`:
`similarity = (1 + cos(gt_alpha - dt_alpha)) / 2`. `cos` is inherently full-period
(2π): a 180°-flipped box scores **0** similarity (worst possible), not 1.0 as
it would under an axis/mod-π convention. This confirms K-Radar treats
orientation as a genuine heading (front/back distinct), so mAOE must wrap
mod 2π, not mod π:

```python
def angle_error(pred_rad, gt_rad):
    diff = pred_rad - gt_rad
    return np.abs((diff + np.pi) % (2 * np.pi) - np.pi)
```

This also keeps mAOE relatable to K-Radar's own AOS via
`AOS = (1 + cos(mAOE)) / 2` for cross-checking.

## Still open (as of 2026-08-31)

1. Report restricted-range AP as a labeled secondary metric alongside
   fixed-threshold P/R/F1, or skip AP reporting entirely and report only
   P/R/F1? (User leaning toward: AP framing is legitimate per the above, so
   likely include it — not yet explicitly confirmed.)
2. Minimum-N reliability floor: proposed 30, not yet confirmed (alternative:
   100, stricter).
