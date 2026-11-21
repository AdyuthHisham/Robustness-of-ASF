# Per-metric tables — ASF robustness, K-Radar, all conditions

One table per metric defined in the repo (see [[robustness-radar-charts]] for the metric
inventory this was built from — 14 distinct metrics found). All pooled across every sequence
that reports `status: ok`, IoU=0.3 where applicable.

**2026-08-26:** these tables are built from `row_table_iou03.parquet` data affected by
[[frame-identifier-bug]] — per-frame identity is wrong, though AP/ATE/ASE/FP/FN values
themselves should be unaffected. Re-derive once the Alvis re-sweep with the fix completes.

## Regenerated 2026-08-25 — `frame_deletion` excluded for all sensors

`outputs/all_preds.txt`/`all_gts.txt` were refreshed from a fresh Alvis pull on 2026-08-25
(originals backed up as `*.bak_pre_pull_20260825`). Regenerating `row_table_iou03.parquet`
against the fresh data surfaced that **`camera_frame_deletion_{low,medium,high}` had been
silently replaced by a rerun under new condition names** (`camera_frame_deletion_new_*`), so
`scripts/alvis/ingest.py` was patched to drop the old `camera_frame_deletion_*` rows and rename
`camera_frame_deletion_new_*` down to the plain name — see `_use_new_camera_frame_deletion` in
`ingest.py`.

That didn't fix the underlying problem: **all three sensors' `frame_deletion` tier is still the
same crash-coverage artifact** described in [[robustness-radar-charts]] bug #2 (mid-run Alvis
crash, sbatch job reports `COMPLETED` on partial output) — post-fix coverage is 0.0–5.3% of
`original`'s frame count for every `{camera,lidar,radar}_frame_deletion_{low,medium,high}`
condition (see `coverage_iou03.csv`). Camera's frame_deletion tier wasn't spared by having a
"new" rerun — that rerun crashed too. **Per decision 2026-08-25: `frame_deletion` is excluded
from every table on this page** (previously it was kept and flagged with `*`) — the surviving
1–730 frames per condition aren't a usable robustness signal, they're sampling noise, and
keeping them in was giving a false impression of "mostly usable, a few caveats" rather than
"this entire tier needs a clean rerun." Frame-deletion robustness for all three sensors remains
an open item, not a reported result.

Every other condition's numbers (mAP, FP/FN, miss rate, mATE/mASE, churn, zero-ablation
retention) are **unchanged** from the pre-refresh run — the fresh pull only touched
frame_deletion data. Rb (item 12/13) and CRI (item 14) **did shift** on gaussian_noise/
loss_partial conditions even though those rows are otherwise identical, because those two
metrics are recomputed per-sequence from `all_preds.txt` directly (`run_ap_robustness.py`, not
the pooled row table) and the fresh pull changed per-sequence AP even where pooled AP didn't
move enough to show up rounded to 2dp — e.g. `radar_gaussian_noise_high` CRI: 0.8115 → 0.3489,
`lidar_gaussian_noise_high` CRI: 0.3009 → 0.1223. Treat pre-2026-08-25 Rb/CRI numbers as stale.

Metric #1 (AP, per condition × class, with num_gt/num_tp/num_fp) already has its own full
table in [[robustness-radar-charts]] — not duplicated here. Metric #5's full form (P/R curve)
and #7 (per-frame recall) are curve-shaped, not single-value-per-condition, so only the binned
recall snapshot (density-stratified) is tabulated below; the rest live only as the figures in
`repos/K-Radar/scripts/alvis/outputs/robustness_reports/figures/`.

## 2. mAP (mean AP across sed+bus)

| condition | mAP | cov |
|---|---|---|
| camera_gaussian_noise_high | 68.68 | 100.0% |
| camera_gaussian_noise_low | 69.12 | 100.0% |
| camera_gaussian_noise_medium | 69.02 | 100.0% |
| camera_loss_complete | 69.67 | 100.0% |
| camera_loss_partial_high | 69.00 | 100.0% |
| camera_loss_partial_low | 68.88 | 100.0% |
| camera_loss_partial_medium | 68.92 | 100.0% |
| lidar_gaussian_noise_high | 15.70 | 100.0% |
| lidar_gaussian_noise_low | 65.08 | 100.0% |
| lidar_gaussian_noise_medium | 17.71 | 100.0% |
| lidar_loss_complete_zero | 40.33 | 100.0% |
| lidar_loss_partial_high | 65.12 | 100.0% |
| lidar_loss_partial_low | 70.31 | 100.0% |
| lidar_loss_partial_medium | 70.49 | 100.0% |
| original | 69.27 | 100.0% |
| radar_gaussian_noise_high | 55.87 | 100.0% |
| radar_gaussian_noise_low | 70.38 | 100.0% |
| radar_gaussian_noise_medium | 60.37 | 100.0% |
| radar_loss_complete_zero | 65.36 | 100.0% |
| radar_loss_partial_high | 63.72 | 100.0% |
| radar_loss_partial_low | 70.39 | 100.0% |
| radar_loss_partial_medium | 69.40 | 100.0% |

## 3. RCE (Relative Change/Error, %) — highest-coverage severity per effect

`build_figures.py::item3_rce_heatmap` picks one severity per effect (the highest-coverage one,
usually `high`) rather than all three — that's why this table has fewer rows per effect than
the others. With `frame_deletion` excluded, every remaining effect's `high` severity is at
100% coverage, so no rows are flagged `*` here anymore.

| condition | cls | ap | orig_ap | rce_pct | cov |
|---|---|---|---|---|---|
| camera_gaussian_noise_high | bus | 62.17 | 62.98 | -1.28 | 100.0% |
| camera_gaussian_noise_high | sed | 75.18 | 75.55 | -0.49 | 100.0% |
| camera_loss_partial_high | bus | 62.75 | 62.98 | -0.37 | 100.0% |
| camera_loss_partial_high | sed | 75.25 | 75.55 | -0.40 | 100.0% |
| camera_loss_complete | bus | 64.03 | 62.98 | 1.66 | 100.0% |
| camera_loss_complete | sed | 75.31 | 75.55 | -0.31 | 100.0% |
| lidar_gaussian_noise_high | bus | 20.17 | 62.98 | -67.98 | 100.0% |
| lidar_gaussian_noise_high | sed | 11.23 | 75.55 | -85.14 | 100.0% |
| lidar_loss_partial_high | bus | 57.08 | 62.98 | -9.36 | 100.0% |
| lidar_loss_partial_high | sed | 73.16 | 75.55 | -3.17 | 100.0% |
| lidar_loss_complete_zero | bus | 37.28 | 62.98 | -40.80 | 100.0% |
| lidar_loss_complete_zero | sed | 43.38 | 75.55 | -42.58 | 100.0% |
| radar_gaussian_noise_high | bus | 51.09 | 62.98 | -18.88 | 100.0% |
| radar_gaussian_noise_high | sed | 60.66 | 75.55 | -19.71 | 100.0% |
| radar_loss_partial_high | bus | 57.20 | 62.98 | -9.17 | 100.0% |
| radar_loss_partial_high | sed | 70.24 | 75.55 | -7.03 | 100.0% |
| radar_loss_complete_zero | bus | 58.32 | 62.98 | -7.40 | 100.0% |
| radar_loss_complete_zero | sed | 72.40 | 75.55 | -4.17 | 100.0% |

## 4. FP / FN counts (both classes pooled)

| condition | FP | FN | cov |
|---|---|---|---|
| camera_gaussian_noise_high | 5099 | 8997 | 100.0% |
| camera_gaussian_noise_low | 4811 | 8912 | 100.0% |
| camera_gaussian_noise_medium | 4992 | 8915 | 100.0% |
| camera_loss_complete | 5007 | 9175 | 100.0% |
| camera_loss_partial_high | 5211 | 8808 | 100.0% |
| camera_loss_partial_low | 4881 | 8835 | 100.0% |
| camera_loss_partial_medium | 4982 | 8913 | 100.0% |
| lidar_gaussian_noise_high | 543 | 32025 | 100.0% |
| lidar_gaussian_noise_low | 4224 | 10412 | 100.0% |
| lidar_gaussian_noise_medium | 882 | 31324 | 100.0% |
| lidar_loss_complete_zero | 3785 | 19957 | 100.0% |
| lidar_loss_partial_high | 4280 | 9890 | 100.0% |
| lidar_loss_partial_low | 4735 | 8414 | 100.0% |
| lidar_loss_partial_medium | 4504 | 8226 | 100.0% |
| original | 4848 | 8672 | 100.0% |
| radar_gaussian_noise_high | 2509 | 14246 | 100.0% |
| radar_gaussian_noise_low | 4733 | 8701 | 100.0% |
| radar_gaussian_noise_medium | 3236 | 12637 | 100.0% |
| radar_loss_complete_zero | 4672 | 10231 | 100.0% |
| radar_loss_partial_high | 3805 | 11047 | 100.0% |
| radar_loss_partial_low | 4729 | 8692 | 100.0% |
| radar_loss_partial_medium | 4425 | 8971 | 100.0% |

## 5. Recall by GT-density bin (selected conditions — gaussian_noise_medium vs. original)

`build_item2_density.py` stratifies recall by how many GT objects are in the frame
(`count_bin`), showing recall degrades faster in crowded frames under some corruptions. Only
`gaussian_noise_medium` (all 3 sensors) vs. `original` is in the precomputed CSV — not every
condition. Unaffected by the 2026-08-25 refresh (identical to the prior run).

| condition | count_bin | mean_recall | n_frames |
|---|---|---|---|
| camera_gaussian_noise_medium | 1-2 | 0.8121 | 8392 |
| lidar_gaussian_noise_medium | 1-2 | 0.2573 | 8392 |
| original | 1-2 | 0.8154 | 8392 |
| radar_gaussian_noise_medium | 1-2 | 0.6666 | 8392 |
| camera_gaussian_noise_medium | 3-4 | 0.7919 | 3064 |
| lidar_gaussian_noise_medium | 3-4 | 0.0825 | 3064 |
| original | 3-4 | 0.7973 | 3064 |
| radar_gaussian_noise_medium | 3-4 | 0.7017 | 3064 |
| camera_gaussian_noise_medium | 5-7 | 0.7227 | 1905 |
| lidar_gaussian_noise_medium | 5-7 | 0.0487 | 1905 |
| original | 5-7 | 0.7324 | 1905 |
| radar_gaussian_noise_medium | 5-7 | 0.6468 | 1905 |
| camera_gaussian_noise_medium | 8-12 | 0.5527 | 335 |
| lidar_gaussian_noise_medium | 8-12 | 0.0346 | 335 |
| original | 8-12 | 0.5677 | 335 |
| radar_gaussian_noise_medium | 8-12 | 0.4318 | 335 |
| camera_gaussian_noise_medium | 13+ | 0.3260 | 31 |
| lidar_gaussian_noise_medium | 13+ | 0.0069 | 31 |
| original | 13+ | 0.3330 | 31 |
| radar_gaussian_noise_medium | 13+ | 0.1766 | 31 |

## 6. Miss rate (FN / (TP+FN), both classes pooled)

| condition | fn | n_gt | miss_rate | cov |
|---|---|---|---|---|
| camera_gaussian_noise_high | 8997 | 35456 | 0.2538 | 100.0% |
| camera_gaussian_noise_low | 8912 | 35456 | 0.2514 | 100.0% |
| camera_gaussian_noise_medium | 8915 | 35456 | 0.2514 | 100.0% |
| camera_loss_complete | 9175 | 35456 | 0.2588 | 100.0% |
| camera_loss_partial_high | 8808 | 35456 | 0.2484 | 100.0% |
| camera_loss_partial_low | 8835 | 35456 | 0.2492 | 100.0% |
| camera_loss_partial_medium | 8913 | 35456 | 0.2514 | 100.0% |
| lidar_gaussian_noise_high | 32025 | 35456 | 0.9032 | 100.0% |
| lidar_gaussian_noise_low | 10412 | 35456 | 0.2937 | 100.0% |
| lidar_gaussian_noise_medium | 31324 | 35456 | 0.8835 | 100.0% |
| lidar_loss_complete_zero | 19957 | 35456 | 0.5629 | 100.0% |
| lidar_loss_partial_high | 9890 | 35456 | 0.2789 | 100.0% |
| lidar_loss_partial_low | 8414 | 35456 | 0.2373 | 100.0% |
| lidar_loss_partial_medium | 8226 | 35456 | 0.2320 | 100.0% |
| original | 8672 | 35456 | 0.2446 | 100.0% |
| radar_gaussian_noise_high | 14246 | 35456 | 0.4018 | 100.0% |
| radar_gaussian_noise_low | 8701 | 35456 | 0.2454 | 100.0% |
| radar_gaussian_noise_medium | 12637 | 35456 | 0.3564 | 100.0% |
| radar_loss_complete_zero | 10231 | 35456 | 0.2886 | 100.0% |
| radar_loss_partial_high | 11047 | 35456 | 0.3116 | 100.0% |
| radar_loss_partial_low | 8692 | 35456 | 0.2451 | 100.0% |
| radar_loss_partial_medium | 8971 | 35456 | 0.2530 | 100.0% |

## 8. Churn / transition rates (4-way GT classification vs. clean baseline)

Every GT object is classified clean→corrupted as stable / corruption-induced miss /
corruption-induced recovery / baseline failure (`gt_transition_analysis.py`). `net_retention`
can exceed 1.0 (e.g. `lidar_loss_partial_medium` = 1.0167) when recoveries outnumber
corruption-induced misses — the corruption causes ASF to detect some objects it missed even in
the clean baseline, not just lose ones it had. `frame_deletion` was never present in this table
even before the 2026-08-25 exclusion decision — `build_figures.py::item6_churn` only computes
churn for the tiered gaussian_noise/loss_partial conditions plus complete-loss.

| corrupted_condition | stable_detection_rate | corruption_induced_miss_rate | corruption_induced_recovery_rate | net_retention |
|---|---|---|---|---|
| camera_gaussian_noise_high | 0.9746 | 0.0254 | 0.0409 | 0.9879 |
| camera_gaussian_noise_low | 0.9804 | 0.0196 | 0.0329 | 0.9910 |
| camera_gaussian_noise_medium | 0.9779 | 0.0221 | 0.0401 | 0.9909 |
| camera_loss_complete | 0.9723 | 0.0277 | 0.0277 | 0.9812 |
| camera_loss_partial_high | 0.9813 | 0.0187 | 0.0421 | 0.9949 |
| camera_loss_partial_low | 0.9821 | 0.0179 | 0.0366 | 0.9939 |
| camera_loss_partial_medium | 0.9790 | 0.0210 | 0.0371 | 0.9910 |
| lidar_gaussian_noise_high | 0.1272 | 0.8728 | 0.0027 | 0.1281 |
| lidar_gaussian_noise_low | 0.9139 | 0.0861 | 0.0653 | 0.9350 |
| lidar_gaussian_noise_medium | 0.1521 | 0.8479 | 0.0066 | 0.1543 |
| lidar_loss_complete_zero | 0.5644 | 0.4356 | 0.0440 | 0.5787 |
| lidar_loss_partial_high | 0.9024 | 0.0976 | 0.1611 | 0.9545 |
| lidar_loss_partial_low | 0.9870 | 0.0130 | 0.0699 | 1.0096 |
| lidar_loss_partial_medium | 0.9716 | 0.0284 | 0.1392 | 1.0167 |
| radar_gaussian_noise_high | 0.7839 | 0.2161 | 0.0248 | 0.7919 |
| radar_gaussian_noise_low | 0.9898 | 0.0102 | 0.0280 | 0.9989 |
| radar_gaussian_noise_medium | 0.8412 | 0.1588 | 0.0333 | 0.8520 |
| radar_loss_complete_zero | 0.9124 | 0.0876 | 0.0906 | 0.9418 |
| radar_loss_partial_high | 0.8987 | 0.1013 | 0.0390 | 0.9113 |
| radar_loss_partial_low | 0.9922 | 0.0078 | 0.0219 | 0.9993 |
| radar_loss_partial_medium | 0.9741 | 0.0259 | 0.0454 | 0.9888 |

## 9/10. mATE (mean translation error, m) and mASE (scale error proxy)

Both computed over TP matches only.

| condition | mATE | mASE | n_tp | cov |
|---|---|---|---|---|
| camera_gaussian_noise_high | 0.3301 | 0.2674 | 26459 | 100.0% |
| camera_gaussian_noise_low | 0.3231 | 0.2502 | 26544 | 100.0% |
| camera_gaussian_noise_medium | 0.3296 | 0.2598 | 26541 | 100.0% |
| camera_loss_complete | 0.3207 | 0.2428 | 26281 | 100.0% |
| camera_loss_partial_high | 0.3271 | 0.2509 | 26648 | 100.0% |
| camera_loss_partial_low | 0.3259 | 0.2513 | 26621 | 100.0% |
| camera_loss_partial_medium | 0.3260 | 0.2516 | 26543 | 100.0% |
| lidar_gaussian_noise_high | 0.5195 | 0.2050 | 3431 | 100.0% |
| lidar_gaussian_noise_low | 0.3447 | 0.2438 | 25044 | 100.0% |
| lidar_gaussian_noise_medium | 0.5440 | 0.2149 | 4132 | 100.0% |
| lidar_loss_complete_zero | 0.4396 | 0.2256 | 15499 | 100.0% |
| lidar_loss_partial_high | 0.3458 | 0.2414 | 25566 | 100.0% |
| lidar_loss_partial_low | 0.3234 | 0.2410 | 27042 | 100.0% |
| lidar_loss_partial_medium | 0.3256 | 0.2401 | 27230 | 100.0% |
| original | 0.3259 | 0.2415 | 26784 | 100.0% |
| radar_gaussian_noise_high | 0.3144 | 0.2523 | 21210 | 100.0% |
| radar_gaussian_noise_low | 0.3258 | 0.2405 | 26755 | 100.0% |
| radar_gaussian_noise_medium | 0.3224 | 0.2490 | 22819 | 100.0% |
| radar_loss_complete_zero | 0.3180 | 0.2501 | 25225 | 100.0% |
| radar_loss_partial_high | 0.3264 | 0.2479 | 24409 | 100.0% |
| radar_loss_partial_low | 0.3245 | 0.2406 | 26764 | 100.0% |
| radar_loss_partial_medium | 0.3248 | 0.2407 | 26485 | 100.0% |

## 11. mAP retention % (zero-ablation: one sensor fully zeroed out)

| condition | cls | ap | orig_ap | retention_pct |
|---|---|---|---|---|
| camera_loss_complete | bus | 64.03 | 62.98 | 101.66 |
| camera_loss_complete | sed | 75.31 | 75.55 | 99.69 |
| lidar_loss_complete_zero | bus | 37.28 | 62.98 | 59.20 |
| lidar_loss_complete_zero | sed | 43.38 | 75.55 | 57.42 |
| radar_loss_complete_zero | bus | 58.32 | 62.98 | 92.60 |
| radar_loss_complete_zero | sed | 72.40 | 75.55 | 95.83 |

## 12/13. Rb (mean_rb per condition, corrupted_AP/original_AP, averaged over per-sequence ratios)

**Different from every other table on this page**: computed by `run_ap_robustness.py` as the
mean of each sequence's own `corrupted_AP/original_AP` ratio, not the ratio of pooled APs
(i.e. `mean(rb_seq1, rb_seq2, ...)`, not `pooled_AP_corrupt / pooled_AP_orig`). Recomputed
2026-08-25 against the fresh `all_preds.txt` pull, IoU=0.3, coordinate-fallback matcher
(no `*_with_trkid.txt`/`all_fn.txt` present locally, so the auto-detect correctly stayed on
coordinate matching, same backend the sbatch job forces explicitly). All 58/58 sequences
contributed for every surviving (non-frame_deletion) condition — the `n/58 < 58` crash-coverage
caveat from the previous version of this table applied only to frame_deletion, which is now
excluded outright.

| Condition | mean(mean_rb) | n sequences contributing |
|---|---|---|
| camera_gaussian_noise_high | 0.9868 | 58/58 |
| camera_gaussian_noise_low | 1.0046 | 58/58 |
| camera_gaussian_noise_medium | 1.0002 | 58/58 |
| camera_loss_complete | 0.9765 | 58/58 |
| camera_loss_partial_high | 1.0056 | 58/58 |
| camera_loss_partial_low | 0.9967 | 58/58 |
| camera_loss_partial_medium | 0.9962 | 58/58 |
| lidar_gaussian_noise_high | 0.2008 | 58/58 |
| lidar_gaussian_noise_low | 0.9207 | 58/58 |
| lidar_gaussian_noise_medium | 0.2332 | 58/58 |
| lidar_loss_complete_zero | 0.5506 | 58/58 |
| lidar_loss_partial_high | 0.8830 | 58/58 |
| lidar_loss_partial_low | 0.9988 | 58/58 |
| lidar_loss_partial_medium | 0.9805 | 58/58 |
| radar_gaussian_noise_high | 0.7695 | 58/58 |
| radar_gaussian_noise_low | 1.0087 | 58/58 |
| radar_gaussian_noise_medium | 0.8056 | 58/58 |
| radar_loss_complete_zero | 0.9156 | 58/58 |
| radar_loss_partial_high | 0.8562 | 58/58 |
| radar_loss_partial_low | 1.0008 | 58/58 |
| radar_loss_partial_medium | 0.9891 | 58/58 |

## 14. CRI (Corruption Robustness Index, per effect across severities)

Per RoHOI (Wen et al., arXiv:2507.09111v3, Eq. 2): `CRI = (mean_AP_across_severities /
clean_AP) * (1/(log(1+std_AP)+1))`, per effect (severities collapsed into one number),
averaged across sequences. `frame_deletion` effects excluded per the 2026-08-25 decision above
— their CRI (previously 0.03–0.08, `*`-flagged) was an artifact of the same crash, not signal.

| Effect | mean CRI | n sequences contributing |
|---|---|---|
| camera_gaussian_noise | 0.7460 | 58/58 |
| camera_loss_partial | 0.7952 | 58/58 |
| lidar_gaussian_noise | 0.1223 | 58/58 |
| lidar_loss_partial | 0.4936 | 58/58 |
| radar_gaussian_noise | 0.3489 | 58/58 |
| radar_loss_partial | 0.4791 | 58/58 |
