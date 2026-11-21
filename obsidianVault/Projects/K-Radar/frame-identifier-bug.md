# Frame-identifier corruption bug — root cause and fix (2026-08-26)

**Full writeup:** `docs/vAIlt/06_Results/frame-identifier-bug-fix-report.md` (this project's
methodology-doc vault, checked in alongside the code it documents — see that file for complete
detail, this note is a pointer + summary for the broader research vault).

## Symptom

[[context-radar-charts]] showed `bus`/`university` at exactly 0% mAP across every corruption
condition, including the clean `original` baseline — a signal that pointed at the measurement
pipeline, not the detector.

## Root cause

`repos/K-Radar/pipelines/pipeline_detection_v1_0.py` named every dumped GT/prediction file using
`idx_name = str(idx_datum).zfill(6)`, where `idx_datum` is just the `enumerate(data_loader)`
position — not the real frame number. The test dataset is filtered (test-split membership, then
`remove_0_obj` drops frames with zero in-ROI considered-class objects) before the loader sees it,
so `idx_datum` silently diverges from true frame identity. This flows through to
`row_table_iou03.parquet`, corrupting every frame identifier in the eval data.

Confirmed on real Alvis data: `idx_datum=117` for sequence 8 maps to real raw frame **450** —
exactly where sequence 8's real buses begin.

**Important nuance:** TP/FP/FN/AP/ATE/ASE are *not* corrupted — pred+GT for a given `idx_datum`
always come from the same real frame, so matching stays internally consistent. Only the frame
**identity label** is wrong, which breaks cross-referencing/debugging (exactly what surfaced it).

## Fix (2026-08-26, plan-mode approved)

Canonical frame id: `{rdr}-{ldr64}` (hyphen-joined, from `dict_out['meta'][0]['idx']`), chosen to
stay compatible with existing underscore-delimited tag parsing in `ingest.py`/
`merge_predictions_text.py`.

Changed: `pipeline_detection_v1_0.py`, `scripts/main_fusion_eval_0.py`,
`scripts/alvis/reconstruct_object_ids.py`, `scripts/alvis/render_recon_review.py`. Plus a
follow-up fix: the `except: print(dict_out['meta'])` blocks in the eval loops had `dict_out`
undefined-on-first-failure or stale-from-a-previous-frame on later failures — which would have
fed a wrong/stale frame id into `idx_name` and `update_dict_feat_not_inferenced`, silently
reintroducing the same bug class on any inference failure. Fixed by reassigning
`dict_out = dict_datum` at the top of each `except` before use.

## Correction (2026-08-26, later same day): the fix was never actually deployed

Discovered while verifying the official-checkpoint re-run (see [[official-checkpoint-rerun-2026-08-26]]):
`scripts/alvis/asf_run.sbatch`'s apptainer bind-mount list overlays `main_cond_0_args.py`,
`kradar_fusion_v1_0.py`, `datasets/effects`, and the KITTI eval utils onto the container — but
**not** `pipelines/pipeline_detection_v1_0.py`, the file this fix actually lives in. Every job
(smoke tests, the corruption-sweep batch, the full 58-sequence `original` re-run) executed the
container's baked-in copy of that file from whenever `kradarV0.sif` was built, completely
ignoring both the frame-id fix and the `dict_out = dict_datum` exception-handling fix. Confirmed
empirically: raw dump filenames from the 2026-08-26 `original` re-run are still plain
`000013.txt` (positional index), not the hyphenated `rdr-ldr64.txt` the fix should produce.

The AP-correctness nuance above still held (verified independently — see
[[official-checkpoint-rerun-2026-08-26]]'s cross-validation against K-Radar's own
`eval_revised.py`), so this did not invalidate any mAP numbers computed from that run. But the
frame-identity bug itself is **still live** in every run to date. Fix: add
`$AM/pipelines/pipeline_detection_v1_0.py:/opt/K-Radar/pipelines/pipeline_detection_v1_0.py` to
`asf_run.sbatch`'s `BINDS` list before the next run.

## Status

Code fix implemented and statically/logic verified (no GPU access locally — spconv missing from
local venv). No retroactive relabeling of already-completed sweep data (user is re-running the
full 58-sequence sweep regardless; raw `test_kitti/` dumps for already-processed sequences were
already deleted post-merge to reclaim Alvis's file-count quota anyway). All current charts/tables
([[context-radar-charts]], [[robustness-metrics-tables]], [[robustness-radar-charts]]) still
reflect pre-fix, frame-mislabeled data as of 2026-08-26 — metric values themselves should be
unaffected per the nuance above, but re-derive once the Alvis re-sweep completes.

**Next steps once the Alvis GPU sweep with the fix finishes:**
1. Spot-check a real dumped `test_kitti/.../gts/*.txt` file against the real label to confirm the
   fix works in production, not just simulation.
2. Re-run `ingest.py` to rebuild `row_table_iou03.parquet`.
3. Regenerate `radar_charts.py`/`box_plots.py`/`context_radar_charts.py` outputs.
