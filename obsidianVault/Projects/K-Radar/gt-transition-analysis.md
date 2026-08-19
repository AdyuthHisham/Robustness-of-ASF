# GT-object transition analysis (churn/retention diagnostic)

**Code**: `repos/K-Radar/scripts/alvis/gt_transition_analysis.py` (new, 2026-08-19)

Companion to [[asf-corruption-study-alvis]] and the metric stack recommended
in [[robustness-metric-selection]]. Answers a question the aggregate `Rb^c`/AP
metrics can't: not "how much did accuracy drop" but "which specific GT
objects did a corruption cost, and did any corrupted runs *recover*
detections the clean run missed" — a corrupted run that loses N clean
detections but recovers M others nets the same AP delta as one that loses
exactly N−M cleanly, and those are very different failure profiles that a
pure retention ratio can't tell apart.

## What it does

Read-only — operates entirely on `outputs/all_predictions.parquet` (already
produced by `predictions_to_parquet.py`), touches no inference/training code.

For each GT object (keyed by `(sequence, frame, gt_obj_idx)` — see "object
identity" below), joins its match status under a clean/original run and a
corrupted run into one of four categories:

| | M_corr=1 | M_corr=0 |
|---|---|---|
| **M_clean=1** | stable | corruption_induced_miss |
| **M_clean=0** | corruption_induced_recovery | baseline_failure |

From the per-cell 2×2 counts (`N_stable, N_miss, N_recover, N_fail`), derives:
`corruption_induced_miss_rate`, `stable_detection_rate`,
`corruption_induced_recovery_rate`, `churn = N_miss + N_recover`,
`churn_rate = churn/total`, and `net_retention = (N_stable+N_recover) /
(N_stable+N_miss)` (spec's literal formula — note the numerator and
denominator aren't the same population, so this isn't bounded in [0,1] in
general; that's the formula as specified, not a computation bug). A sanity
assertion checks `N_stable+N_miss+N_recover+N_fail == total` per stratification
cell on every run.

Supports grouping by arbitrary stratification keys — built-ins for `cls`,
`distance_bin` (from GT range, user-supplied bin edges), and
`modality`/`effect`/`severity` (parsed from the condition-name convention
`{modality}_{effect}_{severity}`, e.g. `camera_gaussian_noise_high`). Occlusion
proxy and weather/time/environment are **not** derivable from the current
`all_predictions.parquet` schema (`predictions_to_parquet.py` only reads the
`all/` subdir, not the road/time/weather condition-duplicate subdirs) — the
module accepts externally-joined columns for those rather than pretending to
compute them; documented as a known gap in the module's own docstring.

## Matching protocol — explicitly not the official AP protocol

Implements its own greedy, class-conditioned, single-IoU-threshold BEV
matching. This is **not** a reimplementation of `utils/kitti_eval/eval_revised.py`'s
official KITTI AP protocol (no ignored-region/DontCare/difficulty handling,
no confidence-threshold sweep) — match counts from this module should not be
compared numerically against `complete_results.txt`'s AP numbers. They answer
different questions (per-object transition identity vs. precision-recall-
integrated accuracy).

The BEV box construction *does* reuse the official convention exactly, to stay
physically consistent: `kitti_common.py:get_label_anno` reindexes raw KITTI
dims `(h,w,l)` → `(l,h,w)`, and `eval_revised.py`'s BEV branch then takes
`bev_axes=[0,2]` of that (→ `l,w`) and of raw location (→ `loc_x,loc_z`),
giving box vector `[loc_x, loc_z, length, width, rotation_y]`. Reproduced
directly from columns already in the parquet rather than re-deriving the
reindex, to avoid drifting from the convention the rest of the repo scores
against. Rotated IoU itself reuses `utils/kitti_eval/rotate_iou_cpu.py`
verbatim (pure NumPy Sutherland-Hodgman polygon clip, no numba/GPU dependency
— the same CPU fallback already relied on elsewhere in this sweep, see
[[asf-corruption-study-alvis]]'s `KRADAR_EVAL_GPU_IOU` bug).

## GT object identity across conditions

K-Radar's raw label files carry no persistent object ID. But GT is identical
across every corruption condition for a given `(sequence, frame)` — corrupting
sensor input doesn't move or add/remove objects (already noted in
`merge_predictions_text.py`'s own docstring). One condition's GT rows per
frame are taken as canonical (prefer `"original"`, else the alphabetically-
first condition present for that frame — content is identical either way) and
`gt_obj_idx` is assigned by within-frame row order. Every condition's
predictions are matched against this single canonical GT table, not each
condition's own duplicated copy, so the `(sequence, frame, gt_obj_idx)` key is
stable across the whole sweep.

A GT object present under only one of the two conditions being compared (e.g.
that condition's run aborted before reaching eval on that frame — the
documented `frame_deletion`/`loss_complete` crash mode) is reported as a
warning and excluded from the transition table, not silently dropped or
force-classified.

## Status

Implemented and unit-verified against synthetic 3-GT-object frame data
(one stable, one corruption-induced-miss, one baseline-failure — matches
expected counts, sanity assertion passes, distance-bin and condition-parsing
helpers checked separately). **Not yet run against the real sweep output** —
next step is pointing it at `outputs/all_predictions.parquet` from the
existing 10-sequence/29-condition sweep (see [[asf-corruption-study-alvis]])
and using it for the reduced-scope `frame_deletion` vs. `loss_complete`
feasibility check that the metrics audit's open-questions resolution
(`docs/lit_survey/metrics/metrics_audit.md`, §5.4) called for.
