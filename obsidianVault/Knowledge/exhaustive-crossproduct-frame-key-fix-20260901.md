---
name: exhaustive-crossproduct-frame-key-fix-20260901
description: Root cause and fix for the original/corrupted frame-key mismatch that nulled frame_density for 96% of the K-Radar robustness table; local ingest also silently dropped environment/time_of_day, now backfilled
metadata:
  type: project
---

Fixed a structural bug in the K-Radar robustness pipeline: `original` condition
rows used a different `frame`-string format than every corrupted condition,
so every `(sequence, frame)` join between them silently produced nulls (96.36%
of `full_denormalized_table.parquet`'s `frame_density`/`n_objs`, and blocked
churn/baseline-delta joins entirely). See [[frame-key-derivation-kradar]] for
the format history this adds to.

**Why:** `ingest.py` has two backends — corrupted conditions read
`all_preds.txt`/`all_gts.txt` (tags like `seq_XXXXX-YYYYY_condition`, a
tesseract/lidar frame-index pair); `original` was, at various points, sourced
from a different path with plain zero-padded frame indices (`"000178"`).
A same-day local fix (`all_preds_original_refresh.txt`/
`all_gts_original_refresh.txt` in `outputs/batches/`, built 2026-08-27)
already re-tagged `original` into the paired format — but the Aug-31
camgauss-RNG-fix regen (see `docs/vAIlt/06_Results/robustness-pipeline-bug-audit-2026-08-31.md`)
ran entirely on Alvis against Alvis's own `all_preds.txt`, which still had
the *old* plain-format `original` rows — so the fix and the regen never
landed in the same file.

**How to apply:** before trusting any `(sequence, frame)` join in this
pipeline, verify `original`'s frame format matches corrupted conditions' in
the *specific* file being read — this has flipped at least three times across
regenerations on 2026-08-31 alone (see [[frame-key-derivation-kradar]]).

## The fix (2026-09-01)

1. Pulled Alvis's current `all_preds.txt`/`all_gts.txt` (824,946 / 70,912
   lines, camgauss-fixed but `original` still plain-format) down locally —
   Alvis compute nodes were down but the login node/filesystem was reachable.
2. Spliced: dropped `all_preds.txt`'s plain-format `original` rows (32,844),
   appended the local `all_preds_original_refresh.txt` (paired format, same
   count) — clean 1:1 swap.
3. **First attempt at the GT side was wrong** and worth recording as a
   pitfall: GT rows carry no per-condition tag (shared by design across
   conditions via the frame key alone), so the already-present paired-frame
   GT rows already covered `original` — appending
   `all_gts_original_refresh.txt` on top created exact duplicates for all
   13,727 (sequence, frame) pairs, doubling `gt_groups` in
   `_match_via_coordinates` and inflating FN 4x (346,562 → 1,341,042 on a
   1.1M→2.1M row blowup). **Fix: for GTs, just drop the plain-frame rows and
   keep the paired ones — do not append the refresh file.** Re-running with
   this correction reproduced the exact target totals (1,109,616 rows,
   648,047/115,007/346,562 TP/FP/FN).
4. Re-ran `ingest.py --force-backend coordinate --iou-threshold 0.3` locally,
   then `build_denormalized_table.py`. `frame_density`/`n_objs` null count:
   1,069,260 → 0.

## Second bug found only at verification time

Running `ingest.py` locally (no K-Radar raw dataset mirrored on this
machine — `_parse_description_txt` needs `{dataset_root}/data/{seq}/description.txt`,
which only exists on Alvis) silently nulled `environment`/`time_of_day` for
**all** 1,109,616 rows (the code's own missing-file-degrades-gracefully
convention — no error, no warning). `weather` stayed populated only because
it has an explicit `"normal"` fallback; `environment`/`time_of_day` do not.
Caught by diffing against [[frame-key-derivation-kradar]]'s note about a
similar-looking regression from a separate concurrent session, then confirmed
directly against a pre-change backup.

**Fix:** `weather`/`environment`/`time_of_day` are pure per-sequence metadata
(58 distinct sequences, 1:1), so backfilled via a `sequence`-only join from
the pre-change backup rather than re-running ingest against the real dataset
root. Applied to `row_table_iou03.parquet`, `full_denormalized_table.parquet`,
and `full_denormalized_table_22cond.parquet`.

**Takeaway for next time:** running this repo's `ingest.py` locally (vs. on
Alvis) will always silently drop `environment`/`time_of_day` unless
`--dataset-root` points at a real local mirror of the K-Radar `data/`
tree with `description.txt` files — which doesn't exist on this machine.
Anyone re-running ingest locally must either point at a real dataset root or
remember to backfill sequence-metadata columns afterward the same way.

## State after this session

- `repos/K-Radar/outputs/all_preds.txt`/`all_gts.txt`: now the corrected
  merge (camgauss fix + original frame-key fix). Pre-splice originals backed
  up at `repos/K-Radar/outputs/pre_camgauss_original_merge_backup_20260901/`.
- `row_table_iou03.parquet`, `full_denormalized_table.parquet`,
  `full_denormalized_table_22cond.parquet`: rebuilt and verified — 0 nulls in
  `weather`/`environment`/`time_of_day`/`frame_density`/`n_objs`, correct
  camgauss TP/FP/FN, `original` and every corrupted condition share frame
  keys. Pre-rebuild versions backed up at
  `repos/K-Radar/outputs/robustness_reports/pre_original_reingest_backup_20260831/`.
- **Not yet rebuilt**: the `crossproduct/` deliverable tree
  (`summary_*.parquet`, `q1`–`q6` CSVs, `anomalies.*`, `findings.md`,
  figures) — still reflects the table from before this fix. Needs a rebuild
  before anything in it (especially density-stratified or churn numbers) is
  trusted. See [[exhaustive-crossproduct-phase2-progress]] and the Phase 1
  audit doc for the still-open blocking questions from before this fix
  (Q0: fresh build vs. refresh of that existing tree; camera_frame_deletion_*
  is to be excluded per user instruction, not a bug to chase).

## Alvis is permanently gone (2026-09-01)

User confirmed Alvis compute will never be back — this is not a temporary
outage. Practical consequences for this whole project, not just this fix:

- No more inference reruns, no more `sbatch` jobs, no more new corruption
  sweeps. Whatever raw prediction/GT data already exists (local `all_preds.txt`/
  `all_gts.txt`, `outputs/batches/*.txt`, everything already synced down) is
  now the **permanent ceiling** on what this pipeline can regenerate or
  extend — there is no "push the fix upstream and resync" path anymore.
  The equivalent-fix suggestion in this note's fix section (push the
  `original_refresh` merge into Alvis's `outputs/batches/`) is now moot;
  the corrected merge only exists as the local `all_preds.txt`/`all_gts.txt`
  produced in this session (see State section above) — **that local file
  pair is now the sole source of truth**, not a stopgap.
- The dataset root (`{root}/data/{seq}/description.txt` etc., needed for
  `environment`/`time_of_day` and any real re-ingest from scratch) lived on
  Alvis and is now unreachable — this repo has no local mirror of the raw
  K-Radar dataset. Any future full re-ingest must either find another way to
  get that dataset locally, or continue the backfill-from-existing-metadata
  pattern used in this session (only viable because the metadata was already
  captured in an old parquet before Alvis went down — this will not
  generalize to any *new* sequence or condition, since there'll be no way to
  regenerate its metadata).
- Any bug found from here on in noise injection, inference, or Alvis-side
  merge logic is **not fixable by rerunning** — only by
  reprocessing/re-deriving from data already resident locally, or by
  documenting it as a known, permanent limitation of the published results.
