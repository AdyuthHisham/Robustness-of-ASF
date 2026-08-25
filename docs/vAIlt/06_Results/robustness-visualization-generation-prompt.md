# Standalone prompt: generate the robustness visualization suite

Self-contained brief for building the graphs specified in
`robustness-visualization-plan.md`. Written to be handed to a fresh session
with no other context from this conversation — every path, schema detail,
and known gap needed to do the work is included below.

## What this is

AMSCUP evaluates ASF (camera+LiDAR+4D-radar BEV fusion) on K-Radar for
robustness to inference-time sensor corruptions: 30 corruption conditions
(camera/lidar/radar × {frame_deletion, gaussian_noise, loss_partial} ×
{low,medium,high} severity, plus lidar/radar `loss_complete_zero` and a
`camera_loss_complete` variant) across a 58-sequence sweep, versus an
`original` uncorrupted baseline. The goal now is to turn the already-built
metrics pipeline into the 8-category visualization suite specified in
`robustness-visualization-plan.md` (read that file in full before starting —
it has the graph-by-graph spec and data dependencies this prompt only
summarizes).

The sweep covers **all 58 K-Radar sequences (1-58)**, not a 10-sequence
subset — an earlier plan draft assumed 10 sequences from a stale example
list; that's been corrected. 31 distinct conditions appear in the data (30
corrupted + `original`); note `camera_loss_complete` has no `_zero` suffix,
inconsistent with lidar/radar's `*_loss_complete_zero` naming — don't
"fix"/normalize this, just match the literal strings present.

## Precomputed artifacts — prefer reusing these over rebuilding from scratch

`scripts/alvis/outputs/robustness_reports/` already has:
- **`row_table_iou03.parquet`** — the current, valid row-level table
  (`ingest.py`'s output): IoU=0.3, coordinate-fallback backend,
  **post**-dummy-filter-fix (see finding below). Use this as the base table
  for anything row-grain (FP/FN, PR curves, TP-error decomposition,
  transition analysis).
- **`row_table.parquet`** — IoU=0.5, **pre**-dummy-fix. **Stale — do not
  use**, kept on disk only for before/after comparison if needed.
- **`ap_robustness_local.json`** — the latest full AP/RR/mRR/CRI report:
  IoU=0.5, post-dummy-fix, all 58 sequences, produced by
  `run_ap_robustness.py`. Usable as a starting point, but **re-verify
  `all_preds.txt`'s current line count first** — it was still growing
  (617K → 711K → 743K+ lines) when this was generated, so the report may be
  stale relative to what's on disk now. Re-run `run_ap_robustness.py` if the
  line count has changed.

If you rebuild rather than reuse, `run_ap_robustness.py` is the reference
end-to-end driver (`ingest.py` → `ap_metrics.py` grouped by `(sequence,
condition, cls)` → per-sequence RR/mRR/CRI → JSON) — read it before writing
a new pipeline from these lower-level pieces.

## Two validated findings worth building figures around

- **Full mAP-per-condition table** (58 sequences, coordinate backend,
  dummy-filtered, IoU=0.5): baseline (`original`) mAP=55.41.
  `frame_deletion` on radar/lidar is catastrophic (mAP 3.8-12.6 at
  high/medium severity). Camera corruptions are nearly flat vs. baseline
  (mAP 57.0-57.9). **This fusion model is clearly radar/lidar-dominant** —
  this is the headline finding item 1 (mAP tables/lines) should surface
  clearly, not bury in a big table.
- **Pooled-AP validation against official numbers**: `ap_metrics.compute_ap`
  matches `complete_results.txt` bit-for-bit for a single condition
  (`68.39447680321193` exact, seq1/`sed`/IoU=0.5). At full 58-sequence
  scale, **AP must be pooled across sequences (group by class only) before
  comparing to any official/published number** — macro-averaging
  per-sequence-then-averaging biases rare classes (`bus`/`Truck`, present in
  only ~29-53/58 sequences) by ~30 points low. Pooled at IoU=0.3 (BEV,
  matching official methodology): Sedan 77.92 (official 82.5), Bus 67.42
  (official 70.2) — within expected noise for a 58-sequence subset. If any
  figure claims agreement/disagreement with official K-Radar benchmark
  numbers, use pooled AP, not per-sequence-macro-averaged AP, or the
  comparison is invalid.

## Data sources — read/verify each, don't assume

1. **`repos/K-Radar/outputs/all_preds.txt`** / **`all_gts.txt`** — the sole
   inference data of record (flat KITTI-format text, tag-prefixed
   `<seq>_<frame>_<condition>` / `<seq>_<frame>`). Check current line counts
   before use — this file grows as inference jobs land; it grew three times
   during the metrics-pipeline build (617K → 711K → 743K+ pred lines). Watch
   for `dummy` placeholder lines (`cls="dummy"`, all-zero box, e.g.
   `34_000003_original dummy -1 -1 0 0 0 0 0 0 0 0 0 0 0 0 0`) — these are
   K-Radar's "zero predictions this frame" convention, not real predictions,
   and MUST be filtered before any matching/AP step (see `ingest.py`'s
   `_parse_preds_txt`, which already does this — reuse it, don't re-parse
   these files by hand). This was a real bug found and fixed this pass:
   before the fix, ~47K dummy lines were counted as spurious false
   positives (FP count dropped 187,896 → 148,332 after filtering) — if you
   see FP counts anywhere near the higher number, you're looking at
   pre-fix/stale output.

2. **`scripts/alvis/ingest.py`** (`load_prediction_rows`) — the canonical
   ingestion layer. Produces one row per `(sequence, condition, frame,
   prediction)` plus synthesized FN rows, with `is_tp`/`is_fp`/`is_fn`, IoU,
   and (where matched) both predicted and matched-GT box fields for
   ATE/ASE/AOE. **Force the coordinate-fallback matcher explicitly**
   (`force_backend="coordinate"` / `--force-backend coordinate`) — the
   trk_id backend (`reconstruct_object_ids.py`'s output,
   `all_*_with_trkid.txt`) is flawed as of 2026-08-20 (Stage B box-format bug:
   passes 7-column 3D boxes to a function requiring 5-column BEV boxes) and
   must not be used even if those files exist on disk. Matching at scale
   (hundreds of thousands of rows) needs `--workers N` — the single-process
   path is a per-row Python loop and impractically slow; the parallel path
   uses `multiprocessing.get_context("spawn")` deliberately (fork-after-polars-threads
   deadlocks otherwise — do not "simplify" this back to default fork).

3. **`scripts/alvis/ap_metrics.py`** (`compute_ap`, `compute_ap_grouped`) —
   41-point KITTI-style AP, validated bit-for-bit against
   `complete_results.txt`'s official numbers. Use `compute_ap_grouped(rows,
   [...])` for any stratified AP (by class, condition, distance bin, etc.) —
   **group by `["cls"]` only (pooled across sequences) for anything meant to
   be compared against an official/published number** — macro-averaging
   per-sequence-then-averaging biases rare-class (e.g. `bus`) numbers badly
   low versus pooled evaluation (empirically: 30-point gap on `bus` AP from
   this exact mistake, resolved by pooling). IoU threshold matters a lot for
   any comparison to official/published numbers — K-Radar's own benchmark
   tables commonly report AP@IoU=0.3; match whatever threshold you're
   comparing against explicitly via `--iou-threshold`.

4. **Enrichment parquet for stratification** —
   `/home/adhish/Productivity/AMSCUP/test-bed/src/Modules/robust_testing/kradar/output/output_with_env_density.parquet`
   (49 columns: `obj_distance_ego`, `weather`, `environment`, `time_of_day`,
   `frame_object_count`, `obj_tracking_id`, `sequence_id`, `frame_idx` [=
   tesseract index, NOT the KITTI frame number in all_preds.txt/all_gts.txt
   — see blocker below], plus per-sensor visibility/sparsity columns).
   **Verify row/sequence coverage before use** — as of 2026-08-20 this file
   has only 471 rows covering 5 sequences (`1, 9, 13, 23, 38`) out of the
   58-sequence sweep. Any stratified graph (distance/weather/environment/
   time-of-day) built from this file today can only cover those 5
   sequences — either explicitly scope those graphs to this 5-sequence
   subset and say so in every such figure's caption, or regenerate the
   parquet for the full sweep before building distance/weather/environment
   breakdowns, per your judgment on which is more useful right now. Do not
   silently present a 5-sequence-derived stratified graph as if it covers
   the full sweep.

## Known blockers — do not attempt to route around these silently

- **Frame-index join is unresolved.** The enrichment parquet's `frame_idx`
  is a raw tesseract-cube index; `all_preds.txt`/`all_gts.txt`'s embedded
  frame number (e.g. `1_000215`) is a *different*, DataLoader-enumeration-order
  index. A recipe to build the `(sequence, tesseract_idx) →
  kitti_frame_number` mapping exists (`reconstruct_object_ids.py`'s Stage A
  now emits `outputs/frame_index_map.txt` as a byproduct) but **that script
  has not been successfully run** — it needs Alvis (torch/open3d/cv2 +
  real K-Radar dataset), and its Stage B has the box-format bug noted above
  (Stage A, which produces the frame-index map, is unaffected by that bug
  and can be trusted once run — Stage B's output should still not be used).
  **Any graph needing distance/weather/environment/time-of-day stratification
  is blocked on this join being built and validated** — do not fake it with
  a coordinate-based fallback join; that was explicitly analyzed and
  rejected (ambiguous for slow-moving/stationary objects across frames).
- **Occlusion stratification is a dead end, not just blocked.** K-Radar's
  own KITTI GT output hardcodes `occ=0` for every object
  (`utils/util_pipeline.py:339`); no real occlusion signal exists anywhere
  in the pipeline. Do not build this graph even as a stub.
- **The trk_id backend is excluded per standing instruction** (see point 2
  above) — do not re-enable it even if `reconstruct_object_ids.py` gets
  fixed, without an explicit new instruction to do so and a re-validation
  pass first.
- **`lidar_frame_deletion_{high,medium}` and `radar_frame_deletion_{high,medium,low}`
  are missing for a large fraction of sequences** (33/58, 29/58, 30/58,
  15/58, 5/58 respectively — severity-correlated, consistent with the model
  crashing on aggressive frame deletion). Any graph aggregating over these
  conditions is implicitly averaging over fewer, and different, sequences
  than graphs for other conditions — note the actual `n_seq` per condition
  in any figure or table that compares across conditions, don't silently
  treat all conditions as equally-sampled.
- **`radar_loss_partial_{low,medium,high}` and `radar_loss_complete_zero`
  are missing specifically for sequence 12 only** — an isolated, likely
  infrastructure-level gap (not severity-correlated), separate from the
  pattern above.
- **`original` has no per-directory `complete_results.txt`** for any
  sequence — an earlier plan draft assumed this existed and built
  `run_metrics.sbatch` on that assumption; that script is wrong. All
  conditions, including `original`, are merged into the flat
  `all_preds.txt`/`all_gts.txt` — use `ingest.py`/`run_ap_robustness.py`,
  not anything expecting per-directory eval output.

## Execution environment

This machine (not Alvis) is fine for anything that fits in `all_preds.txt`
at its current size and doesn't need torch/open3d/cv2 or the real K-Radar
dataset paths — run Python via `uv run --with polars --with numpy` (or
whatever libs you need), never a host-level pip/conda install, matching the
no-host-installs constraint that applies on Alvis and is applied here
defensively too. Full-sweep `ingest.py` runs need `--workers N`
(`ProcessPoolExecutor` + `multiprocessing.get_context("spawn")`, not
default fork — plain fork deadlocked at ~44 minutes wall time / ~6.5s total
CPU, because polars' internal thread pool and `fork()` don't mix safely).
Only reach for an actual Alvis sbatch job if you need
`reconstruct_object_ids.py` (torch/open3d/cv2 + real dataset paths) or a
genuinely new inference run (e.g. item 7's zero-sensor ablation) — two such
jobs were submitted and then cancelled by user request earlier in this
work; don't resubmit either without checking whether they're still needed
first.

## Task

1. Build the denormalized per-prediction analysis table: `ingest.py`'s row
   table, enriched with the parquet's stratification fields wherever the
   frame-index join is available (currently: nowhere, until the blocker
   above is resolved — build the table's schema/join logic now regardless,
   so it activates automatically once `frame_index_map.txt` exists).
2. Work through `robustness-visualization-plan.md`'s 8 categories in
   priority order: **items 1, 3, 4, and 5 have no blockers and should be
   built first** (mAP tables/lines, RCE heatmap, FP/FN + PR curves,
   frame_deletion-vs-loss_complete comparison — all derivable from
   `ingest.py` + `ap_metrics.py` alone). **Item 8** (mATE/mASE) needs the
   matched TP box pairs `ingest.py` already produces — also unblocked.
   **Item 6** (GT-transition churn) needs `gt_transition_analysis.py`,
   already adapted to consume `ingest.py`'s output — unblocked. **Item 2**
   (object-count density) can use `frame_object_count` directly from the
   parquet for the 5 covered sequences, or derive per-frame GT counts from
   `all_gts.txt` directly for full 58-sequence coverage — prefer the latter
   unless the parquet's density computation differs meaningfully (check
   before assuming they're the same number). **Item 7** (zero-sensor
   ablation) needs new inference runs (radar=0, lidar=0, camera=0 baselines)
   that do not exist yet — flag as needing a new Alvis sweep, don't attempt
   to synthesize from existing corrupted-condition data.
3. For every figure: state which sequences/conditions it actually covers
   (not "all 58" unless verified true for that specific figure), and which
   IoU threshold and matching backend were used.
4. Output as a single markdown document (or a notebook, if the visualization
   library needs iterative rendering) — cite exact file:line for any
   metric/column claim, matching this project's existing verification
   standard (see `robustness-metric-implementation-plan.md` for the
   citation style to follow).

Do not implement item 7 (needs new inference data) or occlusion
stratification (dead end) — flag both explicitly as out of scope for this
pass rather than skipping silently.
