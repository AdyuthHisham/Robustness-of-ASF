# Robustness metric implementation plan (ASF / K-Radar)

Planning only — no code written in this pass. Metric selection is settled
(see `obsidianVault/Knowledge/robustness-metric-selection.md` and
`docs/lit_survey/metrics/metrics_audit.md`); this document plans how to build
the five-item stack, redesigned around **per-prediction row-level output**,
against the actual state of `repos/K-Radar/outputs/all_preds.txt` /
`all_gts.txt` and `test-bed/.../kradar/outputs/kradar_test_split_full.parquet`
as read on 2026-08-19.

**Scope change from the prior version of this plan**: `predictions_to_parquet.py`
and any per-run parquet under `repos/K-Radar/outputs/` are now explicitly
**out of scope**. `all_preds.txt` (274,551 lines) and `all_gts.txt` (35,456
lines, deduped across conditions) are the sole inference data of record. The
`kradar_visibility` module's `kradar_test_split_full.parquet` (55,527 rows,
44 cols, a *different* project's output — visibility scoring, not this
sweep's predictions) is added as a **GT-side enrichment source** for
distance-from-ego and weather, joined in at ingestion time.

## 1. Data source audit

### 1.1 `all_preds.txt` / `all_gts.txt` (unchanged from prior audit)

- `all_preds.txt`: `<sequence>_<frame>_<condition> <KITTI pred line>`, 274,551
  lines, one row per predicted object per condition per frame.
- `all_gts.txt`: `<sequence>_<frame> <KITTI gt line>`, 35,456 lines, GT
  deduplicated across conditions (`merge_predictions_text.py:86-97`) —
  confirmed both files cover all 58 K-Radar sequences (`awk -F'_'
  '{print $1}' all_gts.txt | sort -u` → `1..58`).
- KITTI line layout (`scripts/alvis/kitti_boxes.py:1-20`, matching
  `utils/util_pipeline.py:334-382` in the K-Radar submodule):
  `cls trunc occ alpha bbox_l bbox_t bbox_r bbox_b h w l loc_x loc_y loc_z rot_y [score]`.
  GT lines carry **no tracking ID** — confirmed via `head all_gts.txt`
  (plain `sed 0.00 0 0 50 50 150 150 2.3 2.34 4.42 3.43 1.0 24.27 3.06`, 14
  fields, no id column).

### 1.2 `kradar_test_split_full.parquet` — schema and coordinate frame

Read directly (`polars.read_parquet`): 55,527 rows × 44 columns, one row per
GT object per frame, covering all 58 sequences (`sequence_id` values `1..58`,
verified). Columns of interest: `sequence_id, frame_idx, obj_tracking_id,
obj_class, obj_x, obj_y, obj_z, obj_distance_ego, weather, ...`.

This parquet is written by `kradar_visibility/pipeline.py:460-479` from
`ObjectAnnotation` objects parsed **directly from the raw
`info_label_rev2/*.txt` label files** (`kradar_visibility/parser.py:82-100`)
— the *same* raw annotation source K-Radar's own eval pipeline converts to
KITTI format. `obj_x/obj_y/obj_z` are the raw native-frame `x, y, z` fields
from that file (`parser.py:96-98`), and `obj_distance_ego` is
`sqrt(x²+y²+z²)` (`parser.py:46-48`) — Euclidean range from the sensor
origin, used here as the distance-from-ego value.

**Coordinate-frame verdict (verified, not assumed)**: K-Radar's own KITTI
conversion (`utils/util_pipeline.py:346-349`, cross-confirmed by
`scripts/alvis/kitti_boxes.py:6-19`'s documented inverse mapping) writes:

```
loc_x (KITTI col 11) = native yc (lateral)
loc_y (KITTI col 12) = native zc (height)
loc_z (KITTI col 13) = native xc (forward)
```

i.e. `parquet.obj_x → gt.loc_z`, `parquet.obj_y → gt.loc_x`,
`parquet.obj_z → gt.loc_y`. This is a **deterministic axis permutation, not
an independent measurement** — both sides derive from the same
`info_label_rev2` source file. Empirically verified: GT line `1_000215`
(`loc_x=9.3, loc_z=19.52`, class `sed`=Sedan) matches parquet row
`sequence_id=1, obj_x=19.5625, obj_y=9.3925, obj_class=Sedan` to within KITTI's
own 2-decimal rounding (`util_pipeline.py:341`: `np.round(xc, 2)` etc.) — the
match is exact modulo that rounding, not a fuzzy nearest-neighbor coincidence.
**So the coordinate join itself (once two objects are known to be the same
frame) is safe and near-exact** — join on rounded `(x,y,z)` with a tolerance
of ~0.02 (matching KITTI's own rounding), not a loose spatial-tolerance
heuristic.

### 1.3 Frame-identity join — resolved (was the blocker; now a known recipe, not yet scripted)

- `kradar_visibility`'s `frame_idx` = `int(header.tesseract_idx)`
  (`pipeline.py:468`), the raw tesseract-cube index from the `info_label_rev2`
  header line (`idx(tesseract_os2-64_cam-front_os1-128_cam-lrr)=00553_00521_...`).
- The frame number embedded in `all_gts.txt`/`all_preds.txt` filenames (e.g.
  `1_000215`) is **neither** the tesseract index **nor** the os2-64 index —
  it's `idx_name = str(idx_datum).zfill(6)` (`main_fusion_eval_0.py:760`),
  where `idx_datum` is the **plain `enumerate()` counter over the
  per-sequence DataLoader's iteration order** (`:738`).
- **The DataLoader's iteration order is fully determined and reproducible
  without re-running inference:**
  1. `datasets/kradar_fusion_v1_0.py:300`: sequences are ordered numerically
     ascending.
  2. `:304`: `list_labels = sorted(os.listdir(.../'info_label'))` — label
     filenames are `<tesseract_idx>_<os2_64_idx>_...txt`, zero-padded, so a
     lexicographic sort **is** an ascending-`tesseract_idx` sort. This is the
     base per-sequence order.
  3. Two filters apply after that, both order-preserving (Python's `filter()`
     never reorders): the train/test split filter (`:326`, using
     `resources/split/{train,test}.txt`) and `remove_0_obj` (`:329`,
     `num_obj>0`). Both confirmed active for the real run:
     `main_fusion_eval_0.py:615` calls `build_dataset(self, split='test')`,
     and the actual sweep configs (`configs/ASF_v2_0_seq{2,7,8,9,15,16,18,41,
     48,55}_alvis.yml`, e.g. `seq2_alvis.yml:132`) set
     `'remove_0_obj': True`.
  4. No `max_per_seq`/`frame_select` cap is active for the real sweep —
     confirmed by reading the actual config headers, e.g.
     `ASF_v2_0_seq2_alvis.yml:1-3,143`: "all frames surviving class/ROI/
     remove_0_obj filtering, no frame subsetting." (A vault note describing
     an earlier config-generation stage mentions `max_per_seq: 10,
     frame_select: 'first'` — that was superseded before the actual sweep
     ran and does not apply to `all_preds.txt`/`all_gts.txt`; flagged as a
     stale detail in that note, not corrected there since it's a historical
     log.) `frame_select: 'first'` would in any case have preserved order too
     (truncation, not reordering) — only `'most_objects'` would have broken
     the rank correspondence, and it was never used.
  5. `main_fusion_eval_0.py:641-642`, `is_shuffle = False` (`:638`) — the
     DataLoader itself does not reorder.

**Conclusion**: for each sequence, `idx_datum` (→ `kitti_frame_number`) is
exactly the 0-indexed rank of a label file within
`sorted(os.listdir(info_label))`, after keeping only files with
`split=='test'` and `num_obj>0`. This yields a
`(sequence, tesseract_idx) → kitti_frame_number` mapping directly from the
label directory listing and the split file — **no dataset-class
instantiation or model run required**, just replaying steps 1–3 above in a
small script. That script (§2.1 below) should still cross-check its output
against the coordinate match from §1.2 on a sample of frames before being
trusted at scale, since this reasoning hasn't yet been executed end-to-end
against the real `info_label_rev2` directories and `resources/split/test.txt`
for all 10 swept sequences.

### 1.4 `obj_tracking_id` stability

`obj_tracking_id` is parsed straight from the raw label line's tracking-id
field (`parser.py:94`, `parts[2]`) — this is K-Radar's own annotated
tracking ID, stable across frames within a sequence by construction (the
dataset's own multi-frame tracking annotation), confirmed observationally:
`obj_tracking_id=1` in `sequence_id=1` appears in a contiguous run of frames.
It is **not** present in `all_gts.txt`/`all_preds.txt` at all (KITTI format
carries no tracking ID) — so it cannot be used as a join key against the
KITTI files directly; it only lets you follow one GT object across frames
*within the parquet itself*, useful once the frame-mapping problem (§1.3) is
solved, for validating that a coordinate match landed on a temporally
sensible object.

## 2. Implementation plan — per-prediction row-level output

### 2.0 Design change: everything downstream of ingestion is prediction-row-grain

The prior plan's ingestion layer targeted an aggregate-metrics-first design
(dedupe GT, feed `compute_robustness.py`-style summaries). The user's actual
requirement is **every row of `all_preds.txt` gets metrics attached** — TP/FP
status, matched IoU, distance bin, TP-error components where matched, class,
sequence, condition/severity. Aggregates (RR/mRR, CRI, stratified AP) should
be **`group_by/agg` queries over this row-level table**, not a separately
computed parallel path.

### 2.1 Ingestion layer

**New module**: `scripts/alvis/ingest.py`, producing one canonical
`polars.DataFrame` at **prediction-row grain**:

```python
def load_prediction_rows(
    preds_txt: str = "outputs/all_preds.txt",
    gts_txt: str = "outputs/all_gts.txt",
    enrichment_parquet: str | None = "kradar_test_split_full.parquet",
) -> pl.DataFrame:
    ...
```

Pipeline:
1. Parse `all_preds.txt` into typed columns (`sequence, frame, condition,
   cls, h, w, l, loc_x, loc_y, loc_z, rot_y, score`) — reuse the KITTI-field
   regex/parsing already written in `predictions_to_parquet.py:44-64` (the
   *parsing logic* is still reusable even though the parquet output itself
   is out of scope), adapted to the tag-prefix format instead of a
   path-derived prefix.
2. Parse `all_gts.txt` the same way (no `condition` column — GT is
   condition-invariant).
3. **Match** each frame's predictions against that frame's GT using
   `gt_transition_analysis.py`'s matcher (§2.5 below covers the
   pair-returning refactor) to attach `matched_gt_id, iou, is_tp, is_fp,
   is_fn` per predicted row (`is_fn` rows are synthesized for unmatched GT —
   these have no predicted box, so most prediction-specific columns are
   null).
4. **Enrich with distance/weather** from `kradar_test_split_full.parquet`,
   *only once* the frame-index mapping from §1.3 is built and validated —
   until then, this column is left null with a logged warning rather than
   silently joined on the wrong key.

Output grain: one row per `(sequence, condition, frame, prediction)`, plus
synthesized FN rows per unmatched GT. This directly satisfies "every
individual prediction gets metrics."

### 2.2 Mapping the 5 items onto row-level vs. aggregate

| # | Item | Grain | How computed |
|---|---|---|---|
| 4 | TP-error decomposition (ATE/ASE/AOE) | **Row-level** | Computed per matched `(pred, gt)` pair at ingestion time (§2.1 step 3) — becomes columns on the row table directly, not a separate script's output joined back in. |
| 5 | GT-object transition analysis | **Row-level** (per matched pair, per condition-pair) | `gt_transition_analysis.py`'s churn classification (stable/corruption_induced_miss/.../baseline_failure) is inherently a per-GT-object, per-condition-pair label — also belongs as row-table columns (joined on `(sequence, frame, gt_object)` across a clean/corrupted condition pair), not a standalone report. |
| 1 | RR/mRR | **Aggregate** | `group_by(condition, cls) .agg(AP)` then `corrupted_AP / clean_AP` over the row table — still needs an AP computation (precision/recall integration over confidence-sorted predictions), not literally derivable from a `group_by.mean()`. See §2.3 caveat. |
| 2 | CRI | **Aggregate** | Variance-penalized aggregation over the same per-condition AP values RR/mRR produces, grouped further by severity triple. |
| 3 | Absolute AP, stratified | **Aggregate**, with a real gap | `group_by(distance_bin, cls, ...).agg(AP)` over the row table — mechanically straightforward once distance is a row-table column (§1.3), *if* AP itself is computed off this table rather than off `complete_results.txt` (see §2.3). |

### 2.3 The AP-computation caveat (carried over, sharpened)

`compute_robustness.py` currently computes `Rb^c`/`mRb` from
`complete_results.txt`, which is the **official KITTI-eval-computed AP**
(precision/recall curve, 40/11-point interpolation) — not something you get
by counting TP/FP rows in a table. Two options, not yet reconciled:

- **(a) Keep `compute_robustness.py` as the AP source**, and treat
  `complete_results.txt`'s class/view/IoU stratification as the ceiling for
  items 1-3 (no distance-bin AP), using the row-level table only for items
  4-5 plus distance-stratified diagnostics that don't require a rigorous AP
  (e.g. TP/FN rate by distance bin, not distance-stratified *AP*).
- **(b) Implement AP computation directly on the row-level table**
  (precision/recall integration over `is_tp`/`score`-sorted predictions,
  grouped by any stratification key including distance bin) — this is the
  only way to get a real distance-stratified AP number, but it means
  reimplementing (or vendoring) the official KITTI AP integration logic
  rather than reusing `complete_results.txt`. Higher effort, but it is the
  only path to satisfying "distance-stratified AP" as opposed to
  "distance-stratified TP rate."

**Recommendation**: build (a) first — it's already 90% done via
`compute_robustness.py` — and treat (b) as a follow-on scoped only if
distance-stratified *AP* (not just row-level TP/FN counts) turns out to be
required. Flag this as an open question for review (§4) rather than
resolving unilaterally, since it changes the amount of new eval-metric code
this project takes on.

### 2.4 Occlusion / weather — gap status update

- **Weather**: previously flagged as unavailable — **no longer true**.
  `kradar_test_split_full.parquet.weather` carries it per GT object, and
  once the frame-index mapping (§1.3) is solved, it joins onto the row table
  exactly like distance does. Downgrade from "upstream gap" to "blocked on
  the same join-mapping work as distance."
- **Occlusion proxy**: still absent from every source read in this pass —
  neither `all_preds.txt`/`all_gts.txt` nor `kradar_test_split_full.parquet`
  carry an occlusion label (the parquet's per-sensor `*_visible`/
  `sparsity_score` columns are a *visibility* proxy from the
  `kradar_visibility` module's own scoring, not K-Radar's KITTI `occ` column
  — and the KITTI `occ` field in `all_gts.txt` is hardcoded to `0`
  everywhere, per the fixed `header_gt = '0.00 0 0 50 50 150 150'` in
  `util_pipeline.py:339`, i.e. K-Radar doesn't populate real occlusion
  values at all). This remains a genuine upstream gap — no downstream
  script can synthesize occlusion labels that were never annotated.

### 2.5a Object identity — third option: instantiate the real dataset class (added 2026-08-19, supersedes part of §1.3/§2.5's plan)

A peer session wrote `scripts/alvis/reconstruct_object_ids.py` (458 lines,
on disk) while this implementation pass was underway. It solves the frame-
identity/object-identity problem more directly than either option in the
original §1.3:

- **Discovery**: `dict_datum_to_kitti()` (`utils/util_pipeline.py`)
  discards a real, persistent `trk_id` field when writing KITTI text.
  `KRadarFusion_v1_0.get_label()` parses `trk_id` from column 2 of the
  UWIPL-refined v2.0 label tree and carries it through `collate_fn` --
  i.e. K-Radar's own dataset class already treats this as a stable
  cross-frame object identity, it just never reaches the KITTI output.
- **Method**: instead of replaying the DataLoader's filter/sort logic by
  hand (this document's original §1.3 approach -- real replication risk,
  e.g. getting the exact interaction of `consider_cls`/`consider_roi`/
  `remove_0_obj`/calib-offset order wrong), it instantiates the real
  `KRadarFusion_v1_0(cfg, split='test')` class read-only, per sequence, and
  indexes into `.list_dict_item` directly. Zero replication risk, but only
  runs where `KRadarFusion_v1_0`'s dependencies (torch, open3d, cv2) and
  the real dataset paths are available -- i.e. on Alvis via a container,
  submitted with sbatch, never on the login node.
- **Stage A** (GT rejoin): matches `all_gts.txt`'s rounded KITTI columns
  back to `dict_item['meta']['label']`'s `trk_id` by float-tolerance
  equality on the same rounding/permutation `dict_datum_to_kitti` used.
  Ambiguous cases (two same-class objects rounding to identical values) are
  flagged, not silently resolved.
- **Stage B** (pred matching): greedy per-class, highest-score-first BEV-IoU
  matching reusing `utils/kitti_eval/eval.py:bev_box_overlap` -- the same
  metric `complete_results.txt`'s AP numbers use, so this stays consistent
  with the paper's own evaluation rather than an arbitrarily-chosen metric.
- **Output** (not yet produced -- see status below): `outputs/all_gts_with_trkid.txt`,
  `outputs/all_preds_with_trkid.txt`, `outputs/all_fn.txt`. Only a single
  `--iou-thresh` (default 0.5) is emitted, not the repo's full
  `[0.7, 0.5, 0.3]` threshold list `complete_results.txt` reports --
  flagged as a possible follow-up, not fixed in this pass.

This is now the **preferred** object-identity source; the coordinate/IoU
fallback matcher (this module's own `match_frame_pairs`, §2.5 below) is
kept as the local-dev/cross-check path, not replaced. `ingest.py` (§2.1)
auto-selects between them by file presence -- see its module docstring.

**Status: integrated, unvalidated on real data.** `reconstruct_object_ids.py`
has not yet been run (no `outputs/all_*_with_trkid.txt` / `outputs/all_fn.txt`
present as of this writing) -- it needs an Alvis sbatch job. `ingest.py`'s
trk_id-backend parser was written against its documented output format but
has not been exercised against real output.

### 2.5 TP-error decomposition and transition analysis — matcher reuse (unchanged reasoning, now row-level output)

`gt_transition_analysis.py`'s `match_frame` (`gt_transition_analysis.py:150-183`)
does greedy class-conditioned BEV IoU matching but collapses the result to a
binary flag. Factor it into `match_frame_pairs` (returns actual `(gt_idx,
pred_idx, iou)` triples) with `match_frame` kept as a thin wrapper for
backward compatibility. The ingestion layer (§2.1 step 3) calls
`match_frame_pairs` directly and writes ATE/ASE/AOE onto the row table at
ingestion time, rather than through a separate `tp_error_decomposition.py`
script that would need to re-join its output back onto the predictions
table — the row-level design makes that a non-issue: matching happens once,
at ingestion, and both TP-error columns and transition-analysis columns are
written from the same match pass.

`gt_transition_analysis.py`'s `main()` (currently `pl.read_parquet` at
`gt_transition_analysis.py:451`, expecting `predictions_to_parquet.py`'s
schema) should be changed to call `load_prediction_rows()` (§2.1) instead —
`build_match_table`/`build_transition_table`/`aggregate_transition_rates`
(`gt_transition_analysis.py:219-433`) operate on the abstract schema and
need no changes beyond the one call site, per the prior version of this
plan.

## 3. Sequencing

1. **Build and validate the frame-index mapping (§1.3)** — recipe is known
   (sort `info_label` filenames per sequence, filter by
   `split=='test' & num_obj>0`, rank = `kitti_frame_number`); write the
   script, run it against the real `info_label_rev2` directories and
   `resources/split/test.txt` for all 10 swept sequences, and cross-check a
   sample against the §1.2 coordinate match. Still **blocking** for any
   distance/weather enrichment until validated; nothing else in this plan
   depends on it, so it can proceed in parallel with steps 2-4.
2. **Build `ingest.py`** (§2.1) without enrichment first — parse
   `all_preds.txt`/`all_gts.txt`, run matching, produce the row-level table
   with TP/FP/FN, IoU, ATE/ASE/AOE, class, sequence, condition. This alone
   unblocks items 4 and non-distance/weather parts of item 5.
3. **Factor `match_frame` → `match_frame_pairs`** (§2.5) — do this against
   real data (not just the existing synthetic tests) as part of step 2, so
   the matcher is validated on real data before TP-error columns are trusted.
4. **Wire in distance/weather enrichment** (§2.1 step 4) once step 1's
   mapping is validated — add `distance_bin`/`weather` columns to the row
   table.
5. **Adapt `gt_transition_analysis.py`'s `main()`** to call
   `load_prediction_rows()` (§2.5) — small, mechanical.
6. **Decide (a) vs (b) from §2.3** (AP computation source) — needs review,
   not a default decision; blocks items 1-3's final form but not items 4-5.
7. **Extend `compute_robustness.py` with CRI** (unchanged from prior plan —
   independent of steps 1-6, operates on `complete_results.txt`) and run the
   full 10-sequence/29-condition sweep (currently only the seq46 pilot has
   been run).

## 4. Decisions (resolved 2026-08-19)

- **§2.3 — RESOLVED: option (b).** Build real distance-stratified AP by
  reimplementing precision/recall-curve AP integration directly on the
  row-level table (grouped by an arbitrary key, including distance bin), not
  just TP/FN rates. Validate the reimplementation against
  `complete_results.txt`'s unstratified per-class AP as a correctness check
  before trusting the distance-binned output.
- **Distance bin edges — set from documented per-sensor max range**
  (`docs/vAIlt/05_Implementation/K-Radar_Configuration_Reference.md`,
  `KRadar_configpy_Reference.md`): Radar `RADAR_MAX_RANGE_M=118.0`,
  OS1-128 LiDAR `OS1_128_MAX_RANGE_M=120.0`, OS2-64 LiDAR
  `OS2_64_MAX_RANGE_M=240.0`. Cameras have no documented hard range cutoff
  (FOV/projection-limited, not distance-limited). Bins:
  `[0,50)`, `[50,100)`, `[100,120)` (radar/OS1-128 cutoff boundary),
  `[120,240)` (OS2-64-only zone), `[240,inf)` (beyond all sensors — expect
  near-zero recall here; useful as a sanity bin, not a headline result).
- **§1.3**: resolved — frame ordering is a deterministic sort + two
  order-preserving filters, confirmed against the actual sweep configs (no
  `max_per_seq`/`frame_select` cap, `shuffle=False`). The mapping table can
  be built once per sequence and cached; it only needs regenerating if the
  `info_label_rev2` directory contents or `resources/split/test.txt` change.
- **§2.4 — RESOLVED: occlusion dropped entirely.** No real occlusion signal
  exists anywhere in the pipeline (K-Radar hardcodes `occ=0`; the enrichment
  parquet has visibility, not occlusion). Not built, not stubbed.

## 6. Alvis run steps (2026-08-19)

**Real inference driver, confirmed** (resolving an earlier false alarm): the
sweep was produced by `pipelines/pipeline_detection_v1_0.py`'s
`PipelineDetection_v1_0`, invoked via `scripts/main_cond_0_args.py` (see
`scripts/alvis/asf_run.sbatch`) — **not** `scripts/main_fusion_eval_0.py`'s
`ResultVis` (which overrides `DATASET.NAME` to a class,
`KRadarFusion_v1_0_AffectedSensor`, that is never registered in
`datasets/__init__.py.__all__` anywhere in this repo's history — that class
is unrelated to the real sweep, confirmed via `configs/ASF_v2_0_seq2_alvis.yml:36`
setting `DATASET.NAME: 'KRadarFusion_v1_0'` plain). `reconstruct_object_ids.py`
importing plain `KRadarFusion_v1_0` is therefore correct.

**`reconstruct_object_ids.py` extended**: Stage A now also emits
`outputs/frame_index_map.txt` (`seq tesseract_idx kitti_frame_number`) as a
free byproduct of its existing `enumerate(dataset.list_dict_item)` walk
(`dict_item['meta']['idx']['rdr']` is the tesseract index) — this resolves
§1.3's enrichment join without a second replay script.

Run order on Alvis:

1. `sbatch --export=SEQS=32 scripts/alvis/reconstruct_object_ids.sbatch` —
   dry run on one sequence not in the swept set, cheap correctness check.
2. Inspect `outputs/all_gts_ambiguous.txt` (should be empty/small) and the
   Stage A/B unmatched-GT and FP/FN counts in the job log before trusting it.
3. `sbatch scripts/alvis/reconstruct_object_ids.sbatch` — full run, all 10
   swept sequences (`2,7,8,9,15,16,18,41,48,55`), ~4h walltime requested.
   Produces `all_gts_with_trkid.txt`, `all_preds_with_trkid.txt`, `all_fn.txt`,
   `all_gts_ambiguous.txt`, `frame_index_map.txt`.
4. Re-run `ingest.py` with the trk_id backend now available (files present)
   and cross-check its output against the already-validated coordinate-fallback
   path on the same sequence, as a correctness gate before trusting it at scale.
5. Wire `frame_index_map.txt` into `ingest.py`'s distance/weather enrichment
   step (joins `kradar_test_split_full.parquet` on `(seq, tesseract_idx)` →
   `kitti_frame_number`).
6. Run the full `ingest.py` + `ap_metrics.py` pipeline at scale via sbatch
   (local runs timed out past 5 minutes on the 274K-row sweep — expected,
   not a bug, just needs to run where the data lives).
7. Run the full 10-sequence/29-condition sweep through `compute_robustness.py`
   (with CRI) — currently only the seq46 pilot has been run.

## 5. Implementation status (2026-08-19)

Built and validated against real local data (`repos/K-Radar/outputs/all_preds.txt`,
`all_gts.txt`, `complete_results.txt`) unless noted otherwise. Full sequencing
of §3 followed except step 4 (distance/weather enrichment), which is still
blocked as documented in §1.3.

**Files created/modified** (all under `repos/K-Radar/scripts/alvis/`):
- `ingest.py` (new) -- `load_prediction_rows()`, dual-backend (trk_id /
  coordinate-fallback), per §2.1 and §2.5a.
- `ap_metrics.py` (new) -- `compute_ap`/`compute_ap_grouped`, 41-point
  KITTI-style AP reimplementation, per §2.3 option (b).
- `gt_transition_analysis.py` (modified) -- `match_frame` factored into
  `match_frame_pairs` (pair-returning, `match_frame` kept as a thin
  wrapper); added `build_match_table_from_ingest` adapter; `main()` now
  calls `ingest.load_prediction_rows()` instead of `pl.read_parquet` on the
  old `predictions_to_parquet.py` schema.
- `compute_robustness.py` (modified) -- added `compute_cri()` and wired
  `cri_by_effect`/`mean_cri` into the JSON + Markdown reports.

### 2.5a Object identity — third option: instantiate the real dataset class

A peer session wrote `scripts/alvis/reconstruct_object_ids.py` (458 lines,
on disk) while this implementation pass was underway. It solves the
frame-identity/object-identity problem more directly than either option in
§1.3:

- **Discovery**: `dict_datum_to_kitti()` (`utils/util_pipeline.py`) discards
  a real, persistent `trk_id` field when writing KITTI text.
  `KRadarFusion_v1_0.get_label()` parses `trk_id` from column 2 of the
  UWIPL-refined v2.0 label tree and carries it through `collate_fn` -- i.e.
  K-Radar's own dataset class already treats this as a stable cross-frame
  object identity, it just never reaches the KITTI output.
- **Method**: instead of replaying the DataLoader's filter/sort logic by
  hand (§1.3's approach -- real replication risk, e.g. getting the exact
  interaction of `consider_cls`/`consider_roi`/`remove_0_obj`/calib-offset
  order wrong), it instantiates the real `KRadarFusion_v1_0(cfg,
  split='test')` class read-only, per sequence, and indexes into
  `.list_dict_item` directly. Zero replication risk, but only runs where
  `KRadarFusion_v1_0`'s dependencies (torch, open3d, cv2) and the real
  dataset paths are available -- i.e. on Alvis via a container, submitted
  with sbatch, never on the login node.
- **Stage A** (GT rejoin): matches `all_gts.txt`'s rounded KITTI columns
  back to `dict_item['meta']['label']`'s `trk_id` by float-tolerance
  equality on the same rounding/permutation `dict_datum_to_kitti` used.
  Ambiguous cases are flagged, not silently resolved.
- **Stage B** (pred matching): greedy per-class, highest-score-first
  BEV-IoU matching reusing `utils/kitti_eval/eval.py:bev_box_overlap` --
  the same metric `complete_results.txt`'s AP numbers use.
- **Output** (not yet produced): `outputs/all_gts_with_trkid.txt`,
  `outputs/all_preds_with_trkid.txt`, `outputs/all_fn.txt`. Only a single
  `--iou-thresh` (default 0.5) is emitted, not the repo's full
  `[0.7, 0.5, 0.3]` threshold list -- flagged as a possible follow-up.

This is now the **preferred** object-identity source; the coordinate/IoU
fallback matcher (`match_frame_pairs`) is kept as the local-dev/cross-check
path, not replaced. `ingest.py` auto-selects between them by file presence.

### Validated against real data

- `match_frame_pairs` vs. `match_frame`: consistency-checked on a synthetic
  2-object frame (`(gt_idx, pred_idx, iou)` triples agree with the boolean
  wrapper's output).
- `ingest.py` coordinate-fallback backend: run end-to-end on real
  `all_preds.txt`/`all_gts.txt` slices (seq32 2-object smoke test; seq1
  `camera_gaussian_noise_{low,medium}` + `original`, ~2,400 pred lines).
  Produces sane TP/FP/FN counts.
- `ap_metrics.compute_ap`: **exact match** against `complete_results.txt`'s
  official AP for seq1, class `sed`, BEV, IoU=0.5, condition
  `camera_gaussian_noise_low` -- computed `68.39447680321193` against
  `complete_results.txt`'s own `68.39447680321193`. This is the
  load-bearing correctness check from §2.3 and it passed exactly.
- `gt_transition_analysis.py`'s adapted `main()`: run end-to-end
  (`ingest.py` → `build_match_table_from_ingest` → `build_transition_table`
  → `aggregate_transition_rates`) on the same seq1 slice, `--group-by cls`,
  clean=`original` vs. two corrupted conditions. Produced a 4-cell report
  with internally consistent counts (seq1 sed: 736 GT objects total,
  matching `ap_metrics`'s independently-computed `num_gt` for the same
  class/condition).
- `compute_cri`: unit-checked (stable-Rb sequence scores higher than a
  volatile-same-mean sequence; single-tier effect returns `None`, not a
  silently-wrong zero-variance value). End-to-end wiring smoke-tested
  through `compute_robustness.py` using a stand-in baseline (no real
  `original` `complete_results.txt` exists locally for seq1 -- only
  corrupted conditions do) -- confirms the code path runs and produces
  `cri_by_effect`/`mean_cri`, **not** a real robustness number.

### Not validated / blocked on Alvis

- The trk_id backend (`ingest.py`'s `_load_via_trkid`) is implemented
  against `reconstruct_object_ids.py`'s documented output format but **has
  not been run against real output** -- that script itself hasn't been
  executed yet (Alvis-only, needs torch/open3d/cv2). Parser correctness for
  this path is unverified.
- Distance/weather enrichment (§2.1 step 4, §1.3) remains unwired -- the
  `(sequence, tesseract_idx) → kitti_frame_number` mapping recipe is known
  but not yet scripted or run against the real `info_label_rev2`
  directories for all 10 swept sequences.
- The full 10-sequence/29-condition sweep has not been re-run through this
  new pipeline -- only local slices. `ingest.py`'s coordinate-fallback
  backend was attempted against the full `all_preds.txt` (274,551 lines)
  and **did not complete within ~5 minutes** -- its per-(sequence, frame,
  condition) Python-level loop does not scale to the full sweep locally.
  Fine for local dev/validation (as demonstrated above); the intended
  full-scale path is the trk_id backend once `reconstruct_object_ids.py`
  has run on Alvis (already parallelized across sequences via
  `ProcessPoolExecutor`). If that path is delayed, the coordinate fallback
  would need vectorizing before it could run over the full sweep.

### Remaining follow-ups, in priority order

1. Run `reconstruct_object_ids.py` on Alvis (sbatch), then validate
   `ingest.py`'s trk_id backend against its real output.
2. Script and run the `(sequence, tesseract_idx) → kitti_frame_number`
   mapping (§1.3) against the real `info_label_rev2` directories, wire it
   into `ingest.py` step 4, cross-check against §1.2's coordinate match.
3. If the coordinate-fallback backend is still needed at full scale for any
   reason, vectorize it.
4. Re-run `compute_robustness.py` with CRI across the full 10-sequence/
   29-condition sweep once `original` baselines are all present.
