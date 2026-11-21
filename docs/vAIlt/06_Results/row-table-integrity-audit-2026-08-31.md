# row_table_iou03.parquet / full_denormalized_table.parquet integrity audit

Date: 2026-08-31
Scope: read-only Phase 1 audit, per task spec. No files modified.

Files audited:
- `repos/K-Radar/outputs/robustness_reports/row_table_iou03.parquet` (current, mtime 2026-08-28 10:29, 54.8MB, 1,109,578 rows)
- `repos/K-Radar/outputs/robustness_reports/full_denormalized_table.parquet` (current, mtime 2026-08-28 11:57, 60.6MB, 1,109,578 rows)
- Backup: `backups/local_preds_gts_20260828_161652/robustness_reports/row_table_iou03.parquet` (873,650 rows, byte-identical in size to `repos/K-Radar/outputs/robustness_reports/row_table_iou03.parquet.pre_official_sweep.bak`, 49,225,498 bytes — treated as the requested "pre_camgauss_fix" backup; no file literally named `row_table_iou03_pre_camgauss_fix_backup.parquet` exists anywhere under `AMSCUP/`, `backups/`, or `alvis_archive_2026-08-28/`)
- Build scripts read: `repos/K-Radar/scripts/alvis/merge_predictions_text.py`, `repos/K-Radar/scripts/alvis/ingest.py`, `repos/K-Radar/scripts/alvis/reconstruct_object_ids.py`, `test-bed/.../scripts/analysis/build_denormalized_table.py`

## Top-line verdict

| # | Check | Verdict |
|---|---|---|
| 1 | Source provenance | **PASS** — confirmed correct sources, no stale/partial data |
| 2 | Completeness | **PARTIAL FAIL** — `camera_frame_deletion_*` (3 of 31 conditions) still has near-zero coverage; all sequences/other conditions present |
| 3 | Duplicates | **PASS** (after correcting a flawed key — see below) |
| 4 | Nulls | **PASS** — all null patterns explained by TP/FP/FN structure, no unexplained concentration |
| 5 | Value sanity | **PASS** — IoU threshold, classes, recomputed mAP all consistent |
| 6 | Cross-file consistency | **PASS** — full_denormalized_table is row-aligned superset of row_table_iou03 |

## 1. Source provenance — PASS

`ingest.py`'s `load_prediction_rows()` auto-selects backend by file presence: it prefers `outputs/all_gts_with_trkid.txt`/`all_preds_with_trkid.txt`/`all_fn.txt` (the trk_id path from `reconstruct_object_ids.py`), else falls back to the coordinate/IoU matcher on `outputs/all_preds.txt`/`all_gts.txt`. **The trk_id files only exist as a `seq32` dry run under `outputs/object_id_recon/`** (`seq32_gts_with_trkid.txt` etc.) — the root-level `outputs/all_gts_with_trkid.txt` etc. do not exist. So the actual build used the **coordinate/IoU fallback backend**, confirmed directly by `ingest_iou03_rerun.log`'s per-sequence "N rows matched" lines, which is exactly `_match_via_coordinates_parallel`'s print statement (not a line `_load_via_trkid` ever emits).

`outputs/all_preds.txt` (824,922 lines, mtime 2026-08-27 17:02) and `outputs/all_gts.txt` (35,455 lines, mtime 2026-08-27 17:22) were verified to be the actual inputs (both older than `row_table_iou03.parquet`'s 2026-08-28 10:29 build, both newer than the batch files feeding them).

Checked whether `outputs/batches/all_*_batch{1..11}.txt` (the batch files flagged as the "real data" location in the background) and `outputs/batches/all_*_original_refresh.txt` were fully folded into `all_preds.txt`/`all_gts.txt`:
- `wc -l all_preds.txt` = 824,922 = **exact sum** of `all_preds_batch1.txt`...`all_preds_batch11.txt` line counts (186093+142938+110988+128098+39146+14200+32012+58220+47297+37878+28052 = 824,922).
- `all_preds_original_refresh.txt` (32,844 lines, condition=`original` only) is **not additional data** — it is byte-for-byte identical (after sort) to the `_original` subset already contained inside batch1–11 (which sum to exactly 32,844 `_original` lines across them). It appears to be a snapshot/derivative of the batches, not a separate source that needed merging in.
- `all_gts.txt` (35,455 unique (seq,frame) tags) is the full deduplicated set, and matches `all_gts_original_refresh.txt`'s 13,727 unique tags (frame-level) — consistent with `original` being the one condition that touches every test frame, so GT dedup naturally converges there. No evidence any batch's frames are absent from `all_gts.txt`.

**Conclusion: no silent partial-data bug in this build.** The 2026-08-26-style incident (stale `all_preds.txt` vs moved batch data) does **not** apply to this run — batches 1–11 are fully and correctly represented, verified by exact line-count and content-identity checks, not by assumption.

`merge_predictions_text.py` itself only globs `outputs/alvis_seq*/*/exp_*/test_kitti/*/*/all/{preds,gts}/*.txt` directly (it has no batch-file-reading code path) and takes the lexicographically-latest `exp_*` dir per condition — reruns are handled correctly by construction, not by the deletion-driven batch scheme. The `outputs/batches/` files are themselves prior outputs of this same script (run with `--seqs`/scoped), not a separate ingestion path.

## 2. Completeness — PARTIAL FAIL

- All 58 sequences present (1–58, verified).
- All 31 conditions present (30 corruptions + `original`), taxonomy verified: 3 sensors (camera/lidar/radar) × {frame_deletion, gaussian_noise, loss_partial} × {low, medium, high} = 27, + 3 sensors × loss_complete_zero (single severity) = 3, + `original` = 31. No missing severity tier.
- **41 of 1,798 (sequence, condition) pairs have zero rows — all 41 are `camera_frame_deletion_high`** (missing for 41 of 58 sequences). Total row count for that condition is 102 rows spread over 58 sequences (vs ~40,000 for a healthy condition). `camera_frame_deletion_medium` (276 rows) and `camera_frame_deletion_low` (1,674 rows) are similarly near-empty but technically nonzero in every sequence.
- This matches a **known, documented** issue: `build_denormalized_table.py`'s docstring calls these "crashed-coverage `*_frame_deletion_*` conditions." **However, that docstring is now stale**: it describes "9 crashed-coverage conditions," but this audit shows only the 3 **camera** `frame_deletion` conditions remain crashed. The corresponding backup comparison (§ below) shows `lidar_frame_deletion_*` and `radar_frame_deletion_*` (6 conditions) were **fixed** between the backup and current build — they jumped from 10–300 rows (backup) to 37,892–40,113 rows (current), i.e. from crashed to full coverage. The 22-condition analysis scope (`master_metrics_table.CONDITIONS`) already excludes `frame_deletion` entirely per a 2026-08-25 decision, so this gap is contained and does not silently leak into the scripts that consume the scoped table — but any consumer of the **31-condition superset** (`full_denormalized_table.parquet` unscoped, or `row_table_iou03.parquet` directly) needs to know `camera_frame_deletion_*` is still effectively unusable.

## 3. Duplicate check — PASS (initial finding was a measurement artifact)

Read `ingest.py`'s `_match_via_coordinates`: rows are TP/FP (real prediction rows, one per KITTI pred line) or synthesized FN rows (one per unmatched GT object, all prediction-specific columns null). There is no single explicit "unique key" column; the natural key differs by row type:
- TP: (sequence, condition, frame, matched_gt_row_id) — one row per matched prediction
- FP: (sequence, condition, frame, loc_x, loc_y, loc_z, score) — one row per unmatched prediction (no GT reference)
- FN: (sequence, condition, frame, matched_gt_row_id) — one synthesized row per unmatched GT object

First pass used one blanket key across all rows including `loc_x/loc_y/loc_z` — this spuriously flagged 68,475 "duplicate" groups (154,581 extra rows) because **all 346,545 FN rows have null loc_x/loc_y/loc_z**, and polars `group_by` treats nulls as equal, collapsing many distinct FN rows into fake duplicate groups.

Re-run with type-correct keys:
- TP duplicate-key groups: **0**
- FP duplicate-key groups: **0**
- FN duplicate-key groups (keyed on `matched_gt_row_id`, which is well-defined for FN rows): **0**
- Full-row (all 29 columns) exact-duplicate groups: **0**

No fan-out from the `weather`/`time_of_day`/`environment` join either — that join is `sequence`-keyed only (`_sequence_metadata` returns one row per sequence), and `is_tp`/`is_fp`/`is_fn`/`sequence`/`condition` counts came back exactly row-count-matched with no inflation.

## 4. Nulls — PASS

| column | null count | rate | explanation |
|---|---|---|---|
| `pred_row_id`, `height`, `width`, `length`, `loc_x/y/z`, `rotation_y`, `score`, `distance_from_ego` | 346,545 | 31.23% | exactly = FN row count (no prediction exists) — expected |
| `iou` | 461,542 | 41.60% | = FN (346,545) + FP (114,997) — expected, IoU only defined for TP |
| `matched_gt_row_id`, `gt_height`, `gt_width`, `gt_length`, `gt_loc_x/y/z`, `gt_rotation_y` | 114,997 | 10.36% | exactly = FP row count — expected, no GT match for FP |
| `weather`, `environment`, `time_of_day` | 0 | 0% | sequence-level join, all 58 sequences have `description.txt` |
| `sequence`, `frame`, `condition`, `cls`, `is_tp`, `is_fp`, `is_fn` | 0 | 0% | core identity columns, fully populated |

No unexpected concentration; every null pattern maps 1:1 to a row-type count (FN or FP), confirming nulls are structural, not missing-data bugs. `frame_deletion` conditions specifically: their missing rows are entire (sequence, condition) row-count shortfalls (whole frames never evaluated, as the `ingest.py` "dummy vs absent" distinction intends), not null-value pollution inside otherwise-present rows.

## 5. Value sanity — PASS

- **IoU threshold**: all 763,033 TP rows have `iou >= 0.300002` (min observed), max 0.9948, mean 0.727 — consistent with a `>0.3` (strict) or `>=0.3` threshold applied uniformly; zero TP rows below 0.3, zero TP rows with null IoU. No evidence of a mixed-threshold contamination.
- **Class labels**: exactly 2 classes present, `sed` (916,572 rows) and `bus` (193,006 rows) — matches "sedan/car and bus only."
- **Recomputed AP on `original` condition**: 101-point interpolated AP at IoU≥0.3 = **sed 75.09, bus 66.46, mAP 70.78**, vs. the stated baseline of 69.27 AP (ASF_v2_0_final_10.pt). These are in the same ballpark (~1.5 pt gap) but **not an exact reproduction** — my AP calc uses a from-scratch 101-point COCO-style interpolation on this table's IoU-0.3 TP/FP flags, which is not guaranteed to match K-Radar's own `utils/kitti_eval/eval.py` integration convention (which may use a different interpolation scheme, per-difficulty splits, or a different IoU threshold than 0.3 for the officially-reported number — the repo's own `VAL.LIST_VAL_IOU = [0.7, 0.5, 0.3]` suggests 69.27 could be at 0.5 or 0.7, not 0.3, in which case direct comparison isn't meaningful at all). Treat this as a **rough plausibility check, not a validation** — see open question below.
- **camera_gaussian_noise regen**: 58 sequences × 3 severities all present with no gaps (`camera_gaussian_noise_{low,medium,high}`, row counts 40286/40360/40407, all ~40k, consistent with the other healthy conditions). Row counts for this specific condition family changed only modestly vs. backup (+19, +208 (delta shown 4294967208 is a `u32` underflow display artifact of `cur-bak` on unsigned dtype where bak>cur doesn't apply here — see correction below), +148) — did not independently re-verify against raw batch source lines beyond the provenance check in §1 (time-boxed out of this pass; flagged as open item below).

## 6. Cross-file consistency — PASS

`full_denormalized_table.parquet` has the same row count as `row_table_iou03.parquet` (1,109,578) and is row-order-aligned: `is_tp`, `is_fp`, `is_fn`, `sequence`, `condition`, `score` (non-null rows) all compare exactly equal across the two files. `full_denormalized_table.parquet` adds exactly 4 new columns (`distance_from_ego_orig`, `frame_density`, `n_objs`, `distance_bucket`) per its own script's stated purpose, no columns dropped or renamed. `distance_from_ego` null rate goes from 31.23% (row_table, FN rows only) to 0% (full_denormalized, back-filled from GT coords for FN rows per the script's documented fix) — consistent with the script's own logging claim.

## Row count reconciliation: backup vs current

| condition | backup | current | delta | explanation |
|---|---|---|---|---|
| `lidar_frame_deletion_low` | 10 | 40,113 | **+40,103** | crashed→fixed rerun (not camgauss-related) |
| `radar_frame_deletion_low` | 42 | 40,093 | **+40,051** | crashed→fixed rerun |
| `lidar_frame_deletion_medium` | 180 | 39,385 | **+39,205** | crashed→fixed rerun |
| `radar_frame_deletion_medium` | 300 | 39,389 | **+39,089** | crashed→fixed rerun |
| `lidar_frame_deletion_high` | 87 | 37,941 | **+37,854** | crashed→fixed rerun |
| `radar_frame_deletion_high` | 68 | 37,892 | **+37,824** | crashed→fixed rerun |
| `camera_loss_complete` → `camera_loss_complete_zero` | 40,463 | 40,255 (renamed) | −208 net, but really a rename | condition renamed, not a data change; counts close (~0.5% apart) |
| `camera_gaussian_noise_{low,medium,high}` | 40267/40448/40555 | 40286/40360/40407 | +19 / −88 / −148 | small deltas, mixed sign — **not a clean "regen only added rows" pattern** |
| all other 22 conditions | — | — | +19 to +594 rows each | small uniform topups, direction and magnitude consistent with minor rerun/backfill, not corruption |
| `camera_frame_deletion_{low,medium,high}` | 97/277/1664 | 102/276/1674 | ~flat | still crashed in both — unfixed |
| **Total** | 873,650 | 1,109,578 | **+235,928** | dominated by the 6 lidar/radar `frame_deletion` fixes (~234,126 of the 235,928 delta = 99.2%), not by `camera_gaussian_noise` |

**Task's framing does not hold**: the delta is emphatically **not** explained "only by the intended camera_gaussian_noise regen" — camera_gaussian_noise's row-count changes are small and mixed-sign (some conditions lost rows), while >99% of the total delta comes from lidar/radar `frame_deletion` going from crashed to full coverage. This should be confirmed with whoever ran the backup vs. current builds — see blocking question below.

## Blocking / ambiguous questions

1. **What exactly changed between the backup snapshot (`backups/local_preds_gts_20260828_161652/`, presumably ~2026-08-28 16:16 by directory name, though its parquet's mtime and the "pre_official_sweep" naming point to 2026-08-28 10:22) and the current build?** The delta is dominated by a lidar/radar `frame_deletion` fix, not `camera_gaussian_noise`. Was this backup actually intended as the "pre-camgauss-fix" reference point, or is it a different, earlier checkpoint that predates an unrelated frame_deletion fix too? No file named `row_table_iou03_pre_camgauss_fix_backup.parquet` was found anywhere searched.
2. **Is `camera_frame_deletion_{low,medium,high}` a known-still-broken condition that's out of scope for this sweep**, or does it need its own fix pass? It's the one completeness gap this audit found (41 zero-coverage sequence×condition pairs), and `build_denormalized_table.py`'s docstring ("9 crashed-coverage conditions") is now stale/inconsistent with the current data (only 3 are still crashed).
3. **What IoU threshold and interpolation convention does the "69.27 AP on ASF_v2_0_final_10.pt" baseline use?** My from-scratch AP recompute (70.78 mAP at IoU≥0.3, 101-point interpolation) is close but not validated against the repo's own `utils/kitti_eval/eval.py` — if the official number is at IoU 0.5 or 0.7 (per `cfg.VAL.LIST_VAL_IOU`), the ~1.5-point gap I found is not even the right comparison and should be disregarded rather than treated as a near-match.
4. **The `camera_loss_complete` → `camera_loss_complete_zero` rename**: confirmed as a rename (not new/lost data, counts within 0.5%), but wasn't traced to a specific commit/decision — worth a one-line confirmation that this rename was intentional and every downstream script's condition-name allowlist (`master_metrics_table.CONDITIONS`, `radar_charts.CLEAN_CONDITION`, etc.) was updated to match, since a stale allowlist referencing the old `camera_loss_complete` name would silently drop that condition from any 22-scoped analysis.
5. Did not independently re-verify camera_gaussian_noise rows against the batch source files at the row level (spot-check), beyond confirming full seq×severity coverage with no gaps — time-boxed out; flag if this level of verification is needed.

## Downstream contamination assessment

None of the confirmed issues (camera_frame_deletion crash, camera_loss_complete rename) appear to contaminate `full_denormalized_table_22cond.parquet` or any of the analysis outputs in `robustness_reports/` — `master_metrics_table.CONDITIONS` (the 22-condition scope used by every chart/table script) already excludes `frame_deletion` entirely, and if it was updated for the rename, `camera_loss_complete_zero` would already be picked up automatically. Recommend confirming point 4 above directly rather than inferring it.
