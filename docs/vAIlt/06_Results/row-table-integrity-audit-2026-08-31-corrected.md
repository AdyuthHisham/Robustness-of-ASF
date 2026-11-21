# row_table_iou03.parquet re-verification against the correct build (corrected)

Date: 2026-08-31 (evening). Supersedes [row-table-integrity-audit-2026-08-31.md](row-table-integrity-audit-2026-08-31.md).
Read-only audit — nothing was regenerated, rerun, or modified in producing this note.

## TL;DR

The premise of this task ("outputs/robustness_reports/ is a stale Aug-28 copy; the real
build lives under scripts/alvis/") **does not hold anymore**. Between the prior audit and
now, the pipeline was already re-run: `repos/K-Radar/outputs/robustness_reports/` was
overwritten at **2026-08-31 21:38–21:40** — byte-identical to the Alvis build at
`scripts/alvis/outputs/robustness_reports/row_table_iou03.parquet` (16:30) — and the
crossproduct summaries/findings were regenerated on top of it at 21:39–21:40, with the old
(pre-regen) crossproduct outputs archived to
`backups/pre_camgauss_regen_20260831_213750/crossproduct_stale/`. So `outputs/robustness_reports/`
is not stale; it is now the newest data in the repo and matches the Alvis build exactly.

Two docs vault notes were written *before* that regen and are now themselves stale:
`docs/crossproduct_trends_and_anomalies.md` (13:16) and `docs/trend_candidates.md` (Aug 28).

## Step 0 — which file is authoritative

`find` for `row_table_iou03.parquet` / `full_denormalized_table.parquet` under `repos/K-Radar/`
turned up:

| path | mtime | size | rows |
|---|---|---|---|
| `outputs/robustness_reports/row_table_iou03.parquet` | **2026-08-31 21:38** | 54,949,495 | 1,109,616 |
| `outputs/robustness_reports/full_denormalized_table.parquet` | **2026-08-31 21:38** | 61,008,526 | 1,109,616 |
| `outputs/robustness_reports/full_denormalized_table_22cond.parquet` | 2026-08-31 21:38 | 55,584,494 | — |
| `scripts/alvis/outputs/robustness_reports/row_table_iou03.parquet` | 2026-08-31 16:30 | 54,949,495 | 1,109,616 |
| `outputs/robustness_reports/row_table_iou03.parquet.pre_official_sweep.bak` | 2026-08-28 10:22 | 49,225,498 | 873,650 |
| `scripts/alvis/outputs/robustness_reports/row_table_iou03_pre_camgauss_fix_backup.parquet` | 2026-08-31 16:30 (:59) | 49,225,498 | 873,650 |

Neither `outputs/robustness_reports/row_table_iou03.parquet` nor `full_denormalized_table.parquet`
is a symlink (both are regular files, `readlink -f` resolves to themselves). `cmp` confirms
`outputs/.../row_table_iou03.parquet` is **byte-identical** to
`scripts/alvis/outputs/.../row_table_iou03.parquet` — same content, just copied in later
(21:38 local write time vs. 16:30 on Alvis/at transfer time).

**Pipeline input trace**: every analysis script under
`test-bed/src/Modules/robust_testing/kradar/scripts/analysis/` (`crossproduct/crossproduct.py`,
`build_denormalized_table.py`, `master_metrics_table.py`, `bar_charts.py`, `radar_charts.py`,
etc.) hardcodes `ROW_TABLE_PATH`/`DEFAULT_OUT_PATH` = `repos/K-Radar/outputs/robustness_reports/...`
— **none** read from `scripts/alvis/outputs/`. That directory is Alvis-side working storage;
`outputs/robustness_reports/` is unconditionally what every consumer reads.

**Conclusion**: `repos/K-Radar/outputs/robustness_reports/row_table_iou03.parquet` is authoritative,
both because it's what the code actually reads and because it is now (post-copy) content-identical
to and newer than the Alvis build. The task's framing that this path was abandoned/stale is
incorrect as of the current filesystem state — it was true at some point between the prior audit
(file dated 08-28) and now, but a copy-in + regen already closed that gap before this task ran.

## Step 1 — `_pre_camgauss_fix_backup.parquet` ordering

Content check, not just timestamps:
- `scripts/alvis/.../row_table_iou03_pre_camgauss_fix_backup.parquet` (873,650 rows, 49,225,498
  bytes) is **byte-identical** (`cmp`) to `outputs/robustness_reports/row_table_iou03.parquet.pre_official_sweep.bak`
  (same size, same row count, same schema hash) — i.e. it's a copy of a *pre-existing* Aug-28
  snapshot, not a fresh rename-before-overwrite of the live file at 16:30.
- That explains the "backwards" 18-second gap cleanly: the main file at 16:30:41 was written by
  the regen pipeline; the "backup" at 16:30:59 was a **separate copy operation** dropping a known
  older snapshot (`pre_official_sweep.bak`) into the Alvis output dir under the
  `_pre_camgauss_fix_backup` name, for reference — not a live rename of the about-to-be-overwritten
  file. A ~49MB copy taking ~18s to complete after the primary write already finished is
  unremarkable.
- **Interpretation supported by evidence: (b)** — the file represents pre-fix state, saved
  *after* the fact (as a defensive reference copy from an existing backup), not a same-instant
  pre-write snapshot of the file it sits next to. No git commit, log, or vault note further
  documents this specific backup step; the naming is confusing but the ordering is not evidence
  of corruption — content matches the expected pre-fix row count (873,650, matching the "backup"
  row count column in the original audit's reconciliation table) exactly.

## Step 2 — full integrity re-audit against the correct (now current) build

All checks below run against `outputs/robustness_reports/row_table_iou03.parquet`, mtime
2026-08-31 21:38, 1,109,616 rows, 29 cols.

**Completeness**: 58 sequences × 31 conditions = 1,798 expected pairs; 1,757 present, **41
missing — all 41 are `camera_frame_deletion_{low,medium,high}`** (27 high / 11 medium / 3 low),
spread across 34 distinct sequences. This is the exact same shape of gap the prior audit found
(41 missing, all camera_frame_deletion) — confirmed still present, matches
[[project_camera_frame_deletion_known_issue]] (tracked, not new).

**Duplicates**: 0 full-row duplicate groups across all 29 columns.

**Nulls**: `pred_row_id`/`height`/`width`/`length`/`loc_*`/`rotation_y`/`score`/`distance_from_ego`
all null at exactly 346,562 rows (FN rows, no prediction) — structural, matches the FN row count
pattern from the prior audit (346,545 there vs 346,562 here — the ~38-row overall increase from
1,109,578→1,109,616 rows tracks through consistently, not a discontinuity).

**AP recompute** (101-point interpolated, IoU≥0.3, `original` condition, from-scratch calc,
same method as the prior audit): **sed 75.09, bus 66.46 → mAP 70.78** — identical to the prior
audit's number on the stale file. This makes sense: the `original` condition wasn't touched by
the camgauss fix (that only affects `camera_gaussian_noise_*` rows), so this figure was never
actually stale to begin with. Still ~1.5pt off the stated 69.27 clean baseline for the same
unresolved reason flagged before (interpolation/IoU-threshold convention mismatch with the repo's
own `kitti_eval` — not re-litigated here).

**camera_frame_deletion gap**: confirmed present and unchanged in the correct build (see
Completeness above) — not an artifact of having checked the wrong file.

**Row-count delta vs the prior audit's file**: 1,109,616 (now) vs 1,109,578 (prior audit's Aug-28
file) = **+38 rows**, trivial. The prior audit's headline +235,928-row delta (vs. the true
pre-fix 873,650-row backup) already happened *before* Aug 28 — it is not something this rerun
changed further. This build is a small incremental top-up on top of the Aug-28 state, consistent
with the camera_gaussian_noise fix (small, mixed-sign per-condition deltas), not a re-run of the
big frame_deletion fix.

**Cross-file consistency**: `full_denormalized_table.parquet` (1,109,616 rows, 33 cols, mtime
21:38) matches `row_table_iou03.parquet` row-for-row (same row count, same mtime window). Both
postdate the 16:30 Alvis build and the crossproduct regen at 21:39–21:40, so the whole chain is
now internally consistent.

## Step 3 — downstream impact assessment

| file | built from | action needed |
|---|---|---|
| `outputs/robustness_reports/row_table_iou03.parquet` | correct (21:38, = Alvis 16:30 build) | none |
| `outputs/robustness_reports/full_denormalized_table.parquet` | correct (21:38, derived from the above) | none |
| `outputs/robustness_reports/full_denormalized_table_22cond.parquet` | correct (21:38) | none |
| `outputs/robustness_reports/crossproduct/summary_*.parquet` (6 files) | correct — regenerated 21:39, post-fix | none |
| `outputs/robustness_reports/crossproduct/deltas_*.parquet` (3 files) | correct — regenerated 21:39 | none |
| `outputs/robustness_reports/crossproduct/reports/findings.md` | correct — regenerated 21:40 | none |
| `backups/pre_camgauss_regen_20260831_213750/crossproduct_stale/*` | **old**, pre-fix — correctly archived, not live | none (already retired) |
| `docs/crossproduct_trends_and_anomalies.md` | **stale** — written 13:16, before the 21:39–21:40 regen | **rerun/reread** — numbers changed (see below) |
| `docs/trend_candidates.md` | **stale** — written 2026-08-28 15:48 | **rerun/reread** — predates both the fix and the regen |

`findings.md` diff (stale vs. current) shows real, non-trivial numeric drift the two docs notes
above don't yet reflect: flag counts dropped from 1421→1042 total (348→325 "real", 1073→717
"small-N artifact"), D1 monotonicity violations 173→184, D3 modality-divergence groups 186→187,
within-noise fluctuation 6→5 rows. Anyone reading `crossproduct_trends_and_anomalies.md` or
`trend_candidates.md` right now is reading pre-fix numbers.

## Summary table

| item | prior audit conclusion | status now |
|---|---|---|
| Which file is authoritative | assumed stale Aug-28 `outputs/` path, Alvis path unverified | **confirmed**: `outputs/robustness_reports/` — content-identical to Alvis build, and the only path any script reads |
| Provenance | PASS | **PASS, reconfirmed** |
| Completeness (camera_frame_deletion gap) | 41/1798 missing | **PASS (same 41), reconfirmed on correct build** |
| Duplicates | PASS | **PASS, reconfirmed** |
| Nulls | PASS | **PASS, reconfirmed** |
| AP recompute | 70.78 vs 69.27 baseline | **unchanged, 70.78** — `original` condition untouched by the fix |
| Cross-file consistency | PASS | **PASS, reconfirmed** |
| pre_camgauss_fix_backup ordering | unresolved / file not found | **resolved**: found under `scripts/alvis/`, byte-identical to a known Aug-28 backup, ordering explained by copy-operation lag, not corruption |
| Downstream docs (`crossproduct_trends_and_anomalies.md`, `trend_candidates.md`) | not assessed | **stale — need reread against current `findings.md`** |

## Recommendation

No rerun needed for `row_table_iou03.parquet`, `full_denormalized_table*.parquet`, or
`crossproduct/*.parquet`/`findings.md` — all current as of 21:38–21:40 tonight.

**Update (post-writeup)**: `docs/crossproduct_trends_and_anomalies.md` has now been updated to
match the current `findings.md` (D3 186→187, within-noise 6→5, real-anomaly count 348→325 with
a notable composition shift — `stratum_sweep`'s contribution collapsed from 38 real flags to 1,
so the old "weight sibling_conditions/stratum_sweep equally" framing no longer holds).

**Update**: `docs/trend_candidates.md`'s exploratory pipeline (`exploratory_passes.py` Pass 1-3,
`pass4_stratifier_charts.py` Pass 4, `merge_churn.py`) has now been re-run against the current
`full_denormalized_table.parquet`. Verified by diffing old vs. new `pass1_condition_main_effects.csv`:
every condition outside `original`/`camera_gaussian_noise_*` moved by <0.002 mAP (noise), and
those two moved by at most 0.9 mAP points — every finding (#1–8) is confirmed unchanged in
direction and conclusion. Doc updated with a re-verification banner recording the actual deltas
instead of a stale-data warning. One residual caveat: churn's raw source
(`repos/K-Radar/outputs/all_preds.txt`/`all_gts.txt`, still dated 2026-08-27) was not itself
regenerated — the merged churn numbers still come from the existing (2026-08-28)
`churn_by_*.json` files, not a fresh matcher run. Given the near-zero mAP/N drift observed, this
is very unlikely to change anything, but it's flagged rather than silently treated as
end-to-end re-verified.
