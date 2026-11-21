# Frame-identifier bug: root cause and fix (2026-08-26)

## Symptom

Context-breakdown radar charts (mAP/mASE/mATE by `time_of_day`/`weather`/`environment`) showed `bus`/`university` at exactly 0% across every corruption condition, including the clean `original` baseline — a signal that pointed at the measurement pipeline rather than the detector.

## Root cause

`repos/K-Radar/pipelines/pipeline_detection_v1_0.py` (`validate()` and `test()`) named every dumped GT/prediction `.txt` file using `idx_name = str(idx_datum).zfill(6)`, where `idx_datum` is the position from `enumerate(data_loader)` — not the real per-sequence frame number. `self.dataset_test` (`datasets/kradar_detection_v2_1.py`, `load_dict_item()`) is filtered before the loader ever sees it: only frames in `resources/split/test.txt` survive, then (`remove_0_obj: True`) any frame with zero in-ROI objects of a considered class (`Sedan`, `Bus or Truck`) is dropped entirely. So `idx_datum` silently diverges from the real frame index — downstream (`scripts/alvis/merge_predictions_text.py` → `outputs/all_gts.txt`/`all_preds.txt` → `scripts/alvis/ingest.py` → `outputs/robustness_reports/row_table_iou03.parquet`), every "frame" value in the eval data was actually this positional counter, misread as a real frame identity by anything that cross-referenced it against the raw dataset.

Proven, not just theorized: replaying the real filter chain (test-split membership → ROI/class-filtered `remove_0_obj`, matching config `configs/ASF_v2_0_seq8_alvis.yml`) against sequence 8's real UWIPL-refined labels on Alvis showed `idx_datum=117` maps to true raw frame **450** — exactly where sequence 8's real `Bus or Truck` objects begin (frames 450–531). The claimed "bus FN" block (`idx_datum` 117–141) landed precisely inside that real range once decoded correctly.

**Important nuance:** prediction and its GT for a given `idx_datum` are dumped from the same inference call on the same real underlying frame, so IoU matching (TP/FP/FN) and everything computed from it (AP, ATE, ASE) is *not* corrupted by this bug — the pairing is internally consistent. Only the frame **identifier** attached to each row is wrong, which breaks per-frame cross-referencing against the raw dataset (exactly the debugging this investigation was doing), any future frame-keyed join, and tools that re-index the dataset by that identifier (see below).

## Fix (2026-08-26)

Canonical frame id going forward: `f"{rdr}-{ldr64}"` (hyphen-joined; `dict_out['meta'][0]['idx']['rdr']`/`['ldr64']`, already parsed in `datasets/kradar_detection_v2_1.py`'s `get_label()` from the label file's header line). Hyphen, not the underscore the raw filenames use (`00151_00120.txt`), to stay compatible with `merge_predictions_text.py`/`ingest.py`'s existing underscore-delimited tag scheme (`seq_frame_condition`) without touching that parsing code.

Changed:
- `repos/K-Radar/pipelines/pipeline_detection_v1_0.py` — `validate()` and `test()`, `idx_name` computation.
- `repos/K-Radar/scripts/main_fusion_eval_0.py` — same fix, same pattern.
- `repos/K-Radar/scripts/alvis/reconstruct_object_ids.py` — `frame_tag` computation updated to match; docstring updated (previously described the old positional convention as intentional design).
- `repos/K-Radar/scripts/alvis/render_recon_review.py` — `render_frame()` previously re-indexed `dataset.list_dict_item[int(frame)]`, which assumed `frame` was the raw loop position; now looks the item up by the real frame id via a `frame_to_dict_item` map built once from `dataset.list_dict_item`.

## Follow-up fix (same day): stale/undefined `dict_out` on inference failure

`validate()`/`test()` (and `main_fusion_eval_0.py`) each had `except: print('* Meta info: ', dict_out['meta'])` after a failed `dict_out = self.network(dict_datum)`. Since `dict_out` is only ever assigned inside the `try`, a failure meant this line either crashed with `NameError` (first iteration, `dict_out` never assigned) or silently printed a *previous, unrelated* frame's stale metadata (later iterations). Worse, that same stale/undefined `dict_out` also feeds `idx_name` computation (this fix's own new frame-id line) and `update_dict_feat_not_inferenced(dict_out)` on the failure path — so an inference failure could have both crashed the whole first-sample case and, on later failures, silently mislabeled a failed frame's dump files under a previous frame's identity, reintroducing the exact class of frame-identity bug this fix exists to remove.

Fixed by reassigning `dict_out = dict_datum` at the top of each `except` block, before any use — `dict_datum` (this iteration's actual input) always has a correct `meta` for the frame that just failed, and `update_dict_feat_not_inferenced()` only ever needs `meta`, so the substitution is safe.

## Status

Code fix only — no retroactive relabeling of already-completed sweep data was done, since the user is re-running the full 58-sequence × corruption × severity sweep on Alvis regardless (raw `test_kitti/` dumps for already-processed sequences were already deleted post-merge to reclaim Alvis's file-count quota, so retroactive relabeling wasn't viable for that data anyway). All existing `outputs/all_gts.txt`/`all_preds.txt`/`row_table_iou03.parquet` and everything built from them (current radar/box/context charts) still carry the old, frame-mislabeled data until the re-run completes.

**Before trusting the re-run's output:** spot-check a handful of dumped `test_kitti/.../gts/*.txt` filenames against the real label files (`info_label_rev2`/UWIPL-refined, matching `{rdr}_{ldr64}.txt`) to confirm the dumped GT content matches the file now literally named for that frame — same cross-check methodology that surfaced this bug in the first place.
