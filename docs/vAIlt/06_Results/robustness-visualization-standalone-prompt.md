# Prompt: build the ASF/K-Radar robustness visualization suite

Paste everything below into a fresh Claude Code session in the AMSCUP repo
root. It is self-contained — no other conversation context is assumed.

---

You are working in the AMSCUP repo. AMSCUP evaluates ASF
(camera+LiDAR+4D-radar BEV fusion) on K-Radar for robustness to
inference-time sensor corruptions: 30 corruption conditions
(camera/lidar/radar × {frame_deletion, gaussian_noise, loss_partial} ×
{low,medium,high} severity, plus lidar/radar `loss_complete_zero` and a
`camera_loss_complete` variant — note the missing `_zero` suffix on the
camera one, that's real, don't "fix" it) across a 58-sequence sweep
(sequences 1-58), versus an `original` uncorrupted baseline. 31 distinct
conditions appear in the data (30 corrupted + `original`).

Your job: turn the already-built metrics pipeline (below) into the
visualization suite specified in
`docs/vAIlt/06_Results/robustness-visualization-plan.md`. **Read that file
in full before starting** — it has the graph-by-graph spec (8 categories)
and per-figure data dependencies; this prompt gives you the pipeline,
gotchas, and validated findings needed to execute it correctly, not the
graph spec itself.

## Step 0: re-verify data freshness before trusting anything

`repos/K-Radar/outputs/all_preds.txt` grows as inference jobs land (it went
617K → 711K → 743K+ lines during pipeline development). Check its current
line count first. If it has grown since the precomputed artifacts below
were produced, re-run `run_ap_robustness.py` rather than trusting them.

## Precomputed artifacts — reuse these, don't rebuild from scratch unless stale

In `scripts/alvis/outputs/robustness_reports/`:

- **`row_table_iou03.parquet`** — the current, valid row-level table
  (`ingest.py`'s output): IoU=0.3, coordinate-fallback backend,
  post-dummy-filter-fix (see bug below). Use this as the base table for any
  row-grain work: FP/FN, PR curves, TP-error decomposition, transition
  analysis.
- **`row_table.parquet`** — IoU=0.5, **pre**-dummy-fix. Stale. Do not use;
  it's kept only for before/after comparison.
- **`ap_robustness_local.json`** — full AP/RR/mRR/CRI report: IoU=0.5,
  post-dummy-fix, all 58 sequences, produced by `run_ap_robustness.py`.
  Subject to the Step 0 freshness check above.

If you rebuild rather than reuse, `scripts/alvis/run_ap_robustness.py` is
the reference end-to-end driver: `ingest.py` → `ap_metrics.py` grouped by
`(sequence, condition, cls)` → per-sequence RR/mRR/CRI → JSON. Read it
before writing a new pipeline from the lower-level pieces below.

## The pipeline you're building on

1. **`repos/K-Radar/outputs/all_preds.txt`** / **`all_gts.txt`** — sole
   inference data of record. Flat KITTI-format text, tag-prefixed
   `<seq>_<frame>_<condition>` / `<seq>_<frame>`. Watch for `dummy`
   placeholder lines (`cls="dummy"`, all-zero box, e.g.
   `34_000003_original dummy -1 -1 0 0 0 0 0 0 0 0 0 0 0 0 0`) — K-Radar's
   "zero predictions this frame" convention, not real predictions. **Real
   bug found and fixed**: these weren't being filtered, inflating FP counts
   by ~47K (187,896 → 148,332 after the fix). `ingest.py`'s
   `_parse_preds_txt` filters them correctly now — reuse it, don't re-parse
   these files by hand. If you see FP counts near the higher number, you're
   looking at stale pre-fix output.

2. **`scripts/alvis/ingest.py`** (`load_prediction_rows`) — canonical
   ingestion layer. One row per `(sequence, condition, frame, prediction)`
   plus synthesized FN rows, with `is_tp`/`is_fp`/`is_fn`, IoU, and (where
   matched) predicted + matched-GT box fields for ATE/ASE/AOE. **Force the
   coordinate-fallback matcher explicitly** (`force_backend="coordinate"` /
   `--force-backend coordinate`) — the trk_id backend
   (`reconstruct_object_ids.py`'s `all_*_with_trkid.txt` output) has an
   unfixed Stage B box-format bug (passes 7-column 3D boxes to a function
   requiring 5-column BEV boxes) and must not be used even if those files
   exist on disk. Matching at scale (hundreds of thousands of rows) needs
   `--workers N` — the single-process path is a per-row Python loop and
   impractically slow. The parallel path uses
   `multiprocessing.get_context("spawn")` deliberately — fork-after-polars-
   threads deadlocks (confirmed: ~44 min wall time, ~6.5s total CPU with
   plain fork). Do not "simplify" this back to default fork.

3. **`scripts/alvis/ap_metrics.py`** (`compute_ap`, `compute_ap_grouped`) —
   41-point KITTI-style AP, validated bit-for-bit against
   `complete_results.txt`'s official AP (exact match:
   `68.39447680321193`, seq1/`sed`/IoU=0.5). Use `compute_ap_grouped(rows,
   [...])` for any stratified AP. **Group by `["cls"]` only (pooled across
   sequences) for anything compared against an official/published number**
   — macro-averaging per-sequence-then-averaging biases rare classes
   (`bus`/`Truck`, present in only ~29-53/58 sequences) low by ~30 points.
   Pooled at IoU=0.3 BEV (matching official methodology): Sedan 77.92
   (official 82.5), Bus 67.42 (official 70.2) — within expected noise for a
   58-sequence subset. Pass `--iou-threshold` explicitly whenever comparing
   to a published number.

4. **Enrichment parquet for stratification** —
   `test-bed/src/Modules/robust_testing/kradar/output/output_with_env_density.parquet`
   (49 columns: `obj_distance_ego`, `weather`, `environment`, `time_of_day`,
   `frame_object_count`, `obj_tracking_id`, `sequence_id`, `frame_idx` [=
   tesseract index, NOT the KITTI frame number in `all_preds.txt`/
   `all_gts.txt` — see blocker below]). **Verify coverage before use** —
   currently only 471 rows covering 5 sequences (`1, 9, 13, 23, 38`) of 58.
   Either scope stratified graphs explicitly to these 5 sequences and say
   so in every such figure's caption, or regenerate the parquet at full
   scale first. Never silently present a 5-sequence-derived stratified
   graph as if it covers the full sweep.

## Headline finding to build figures around

Full mAP-per-condition table (58 sequences, coordinate backend,
dummy-filtered, IoU=0.5): baseline (`original`) mAP=55.41.
`frame_deletion` on radar/lidar is catastrophic (mAP 3.8-12.6 at
high/medium severity). Camera corruptions are nearly flat vs. baseline
(mAP 57.0-57.9). **This fusion model is clearly radar/lidar-dominant** —
make this the headline of item 1 (mAP tables/lines), not buried in a big
table.

## Blockers — do not silently route around these

- **Frame-index join is unresolved.** The enrichment parquet's `frame_idx`
  is a raw tesseract-cube index; `all_preds.txt`/`all_gts.txt`'s embedded
  frame number (e.g. `1_000215`) is a different, DataLoader-enumeration-order
  index. A recipe exists (`reconstruct_object_ids.py`'s Stage A emits
  `outputs/frame_index_map.txt` as a byproduct) but that script has not
  been successfully run — needs Alvis (torch/open3d/cv2 + real dataset).
  Stage A itself is unaffected by Stage B's bug and can be trusted once
  run. **Any graph needing distance/weather/environment/time-of-day
  stratification is blocked on this** — do not fake it with a
  coordinate-based fallback join (explicitly analyzed and rejected:
  ambiguous for slow-moving/stationary objects across frames).
- **Occlusion stratification is a dead end, not just blocked.** K-Radar's
  own KITTI GT output hardcodes `occ=0` for every object
  (`utils/util_pipeline.py:339`). Do not build this graph even as a stub.
- **trk_id backend is excluded per standing instruction.** Do not re-enable
  it even if `reconstruct_object_ids.py` gets fixed, without an explicit
  new instruction and a re-validation pass.
- **`lidar_frame_deletion_{high,medium}` / `radar_frame_deletion_{high,medium,low}`
  are missing for a large fraction of sequences** (33/58, 29/58, 30/58,
  15/58, 5/58 respectively — severity-correlated, consistent with model
  crashes at high corruption). Note actual `n_seq` per condition in any
  figure/table comparing across conditions — don't treat all conditions as
  equally sampled.
- **`radar_loss_partial_{low,medium,high}` / `radar_loss_complete_zero`
  missing for sequence 12 only** — isolated, likely infrastructure failure,
  unrelated to the pattern above.
- **`original` has no per-directory `complete_results.txt`** for any
  sequence. All conditions, including `original`, are merged into the flat
  `all_preds.txt`/`all_gts.txt` — use `ingest.py`/`run_ap_robustness.py`,
  never anything expecting per-directory eval output.

## Execution environment

This machine is fine for anything that fits `all_preds.txt` at its current
size and doesn't need torch/open3d/cv2 or real K-Radar dataset paths — run
Python via `uv run --with polars --with numpy` (or whatever else you need),
never a host-level pip/conda install. Full-sweep `ingest.py` runs need
`--workers N` with the spawn context described above. Only reach for an
actual Alvis sbatch job if you need `reconstruct_object_ids.py` or a
genuinely new inference run (e.g. the zero-sensor ablation below) — don't
submit one without checking whether it's actually needed first.

## Task

1. Build the denormalized per-prediction analysis table: `ingest.py`'s row
   table (or the precomputed `row_table_iou03.parquet`), enriched with the
   parquet's stratification fields wherever the frame-index join is
   available (currently: nowhere, until the blocker above is resolved —
   build the schema/join logic now regardless, so it activates
   automatically once `frame_index_map.txt` exists).
2. Work through `robustness-visualization-plan.md`'s 8 categories in
   priority order:
   - **Unblocked, build first**: item 1 (mAP tables/lines — lead with the
     radar/lidar-dominant finding above), item 3 (per-sensor/class RCE
     heatmap), item 4 (FP/FN + PR curves), item 5 (frame_deletion-vs-
     loss_complete comparison), item 8 (mATE/mASE, from `ingest.py`'s
     matched TP box pairs), item 6 (GT-transition churn, via
     `gt_transition_analysis.py`, already adapted to `ingest.py`'s output).
   - **Item 2** (object-count density): use `frame_object_count` from the
     parquet for the 5 covered sequences, or derive per-frame GT counts
     directly from `all_gts.txt` for full 58-sequence coverage — prefer the
     latter unless the parquet's density computation differs meaningfully
     (check before assuming they're the same number).
   - **Item 7** (zero-sensor ablation): needs new inference runs (radar=0,
     lidar=0, camera=0) that don't exist yet. Do not implement — flag
     explicitly as out of scope, needing a new Alvis sweep. Do not attempt
     to synthesize it from existing corrupted-condition data.
   - **Occlusion stratification**: do not build, even as a stub (dead end
     per blockers above).
3. For every figure, state which sequences/conditions it actually covers
   (never "all 58" unless verified true for that specific figure), and
   which IoU threshold and matching backend were used.
4. Output as a single markdown document (or a notebook if the
   visualization library needs iterative rendering). Cite exact file:line
   for any metric/column claim — match the verification standard in
   `docs/vAIlt/06_Results/robustness-metric-implementation-plan.md`.

Flag item 7 and occlusion stratification explicitly as out of scope for
this pass rather than skipping them silently or faking them.
