# K-Radar frame-key derivation (`frame` column, robustness eval tables)

`row_table_iou03.parquet` / `full_denormalized_table.parquet` carry a
`frame` column whose format has changed across regenerations — important to
check every time before joining on it.

## Format history

- **Pre-2026-08-26 fix**: frame id was `enumerate()` position into
  `dataset.list_dict_item`, which silently diverged from the real frame
  whenever the test-split filter or `remove_0_obj` dropped preceding frames
  (see [[project_kradar_frame_identifier_bug]]).
- **2026-08-31, ~21:38 regen** (post camgauss-fix): `original` condition
  rows had `frame` as a plain zero-padded index (`"000013"`); every
  corrupted-condition row had `frame` as `"{radar_tesseract_idx}-{lidar_idx}"`
  (`frame_tag` from `reconstruct_object_ids.py`/`pipeline_detection_v1_0.py`
  — see that file's docstring, line ~214: `frame_tag = f"{tesseract_idx}-{ldr64_idx}"`).
  This broke every `(sequence, frame)` join between `original` and corrupted
  rows (96.36% of `full_denormalized_table.parquet` had null
  `n_objs`/`frame_density`).
- **2026-08-31, ~22:45 regen** (concurrent, independent of this session):
  `row_table_iou03.parquet` was rebuilt again and now formats `frame`
  uniformly as `"{tesseract_idx}-{lidar_idx}"` for **every** condition
  including `original` — the mismatch is gone, 100% of corrupted
  `(sequence, frame)` pairs now have a matching `original` row. **But** this
  same regen also has `environment` and `time_of_day` 100% null (`weather`
  is still populated) — a new, separate regression, most likely because that
  regeneration was caught mid-flight or its sequence-metadata join broke.
  Not diagnosed further this session (out of scope — belongs to whoever owns
  that regeneration).

## Derivation used for the (now largely moot) old-format fallback

When `original`'s `frame` is a plain int and corrupted rows are
`"tess-lidar"`, the correct join key is `tesseract_idx - C(sequence)`, where
`C(sequence) = min(tesseract_idx over all corrupted rows for that sequence)
- min(int(frame) over original rows)`. Notes:

- Use the **radar tesseract_idx** (first half of the pair), not the lidar
  idx — they differ by a per-sequence constant (e.g. 5 frames for sequence
  32) because radar and lidar streams are offset. The lidar-idx-based offset
  does NOT reproduce ground truth.
- Validated against the one available ground-truth mapping file,
  `repos/K-Radar/outputs/object_id_recon/seq32_frame_index_map.txt`
  (`tesseract_idx 270 -> kitti_frame 0`, i.e. C=270 for seq 32) — matches
  exactly.
- Also validated for internal consistency: computing C per (sequence,
  condition) instead of pooling across all corrupted conditions in a
  sequence gave 0 disagreements across 1,699 pairs — strong evidence this is
  a genuine, single, sequence-level sensor-index offset.
- A naive coordinate-based cross-check (matching GT `(loc_x, loc_y, loc_z)`
  across conditions to independently verify C) turned out to be unreliable:
  K-Radar scenes have many near-static objects whose GT coordinates repeat
  across dozens of frames, so raw coordinate matching produces many false
  candidate offsets (best candidate's vote share ranged 18–100% across
  sequences, with disagreement vs. the tesseract-based method in about half).
  Do not trust this method without restricting to frames with large,
  spatially-unique object constellations (signature matching also degrades
  for the same reason — quasi-static scenes/short sequences confound it).
  The `frame_index_map.txt` ground-truth file (written by
  `reconstruct_object_ids.py`, one file per sequence when it's rerun) is the
  only reliable independent check.
- `original`'s frame range is genuinely **shorter** than the corrupted
  conditions' physical frame range for most sequences (53/58) — likely
  because `original`'s eval used a capped/shorter test-config window per
  sequence (see `gen_sequence_configs.py`'s "10-frame-capped test configs").
  This means even a correct join will leave some corrupted rows unmatched
  (~48% in the one measurement taken) — that's expected missing coverage,
  not a bug.

## Practical takeaway

Before trusting any `(sequence, frame)` join in this pipeline, check: (1)
does `original`'s `frame` format match corrupted conditions' format for the
*current* `row_table_iou03.parquet`, and (2) are `weather`/`environment`/
`time_of_day` actually populated (not null) in the specific file being read.
Both have changed across regenerations within the same day. See
[[exhaustive-crossproduct-phase2-progress]] for the session that hit this.
