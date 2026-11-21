#!/usr/bin/env python3
"""Ingestion layer: turn the sweep's raw text output into one canonical
prediction-row-grain polars.DataFrame that every downstream metric
(RR/mRR, CRI, stratified AP, TP-error decomposition, GT-object transition
analysis) consumes, instead of each metric script re-parsing/re-matching on
its own. See docs/vAIlt/06_Results/robustness-metric-implementation-plan.md
for the design rationale.

Two matching backends, auto-selected by file presence (§2.5 of the plan):

  1. trk_id path (preferred): reconstruct_object_ids.py's output --
     outputs/all_gts_with_trkid.txt, outputs/all_preds_with_trkid.txt,
     outputs/all_fn.txt. Object identity comes from K-Radar's own persistent
     trk_id (rejoined from the UWIPL-refined label tree) plus IoU-based
     pred<->GT matching using the repo's own bev_box_overlap -- the same
     metric complete_results.txt's AP numbers use. Requires running
     reconstruct_object_ids.py on Alvis first (needs torch/open3d/cv2 + the
     real dataset); NOT present as of this writing, so this path is
     implemented but unvalidated against real data -- see plan §1.3/§2.5.

  2. Coordinate/IoU fallback (this repo's own matcher): parses
     outputs/all_preds.txt / all_gts.txt directly and matches each frame's
     predictions against that frame's GT using
     gt_transition_analysis.match_frame_pairs (BEV IoU, class-conditioned,
     greedy highest-score-first). This is the only path actually testable
     on this machine right now (both files are present locally) -- used for
     local dev/iteration and as a cross-check once the trk_id path exists.

Output grain: one row per (sequence, condition, frame, prediction), plus one
synthesized row per unmatched GT object (is_fn=True; prediction-specific
columns null). Every row also carries `distance_from_ego` (3D Euclidean norm
of that row's own loc_x/loc_y/loc_z -- these are already ego/sensor-frame
KITTI coordinates, no pose transform needed) and sequence-level `weather`/
`environment`/`time_of_day` (joined by `sequence` alone from each sequence's
description.txt -- see `_sequence_metadata`). This sidesteps the still-open
tesseract_idx -> kitti_frame_number mapping (plan §1.3): that mapping is only
needed to join the *visibility* parquet's per-frame columns, not for these,
which are either computable from the KITTI row itself or sequence-level.
"""
from __future__ import annotations

import os
import re
import sys
from typing import Optional

import polars as pl

from robustness.gt_transition_analysis import match_frame_pairs

# Mirrors kradar_visibility/parser.py's parse_description_txt + pipeline.py's
# weather fallback (ALLOWED_WEATHER / "normal" default) verbatim, reimplemented
# standalone here rather than cross-imported: kradar_visibility is a separate
# uv project (test-bed/src/Modules/robust_testing/kradar/) with its own
# lockfile, not a dependency of this submodule's scripts.
#
# "lightsnow"/"heavysnow" added 2026-09-23: the original set omitted these two
# raw K-Radar weather tokens (confirmed verbatim in K-Radar's own
# tools/tag_generator/tag_generation.py and scripts/main_fusion_eval_0.py),
# so sequences 42/43/48/49 (lightsnow) and 46/47/54/55/56/57/58 (heavysnow)
# were silently falling back to "normal" below -- contaminating every
# per-weather AP figure derived from this table's "normal" bucket.
_ALLOWED_WEATHER = {
    "clear", "overcast", "fog", "rain", "sleet", "snow", "normal",
    "lightsnow", "heavysnow",
}

# camera_frame_deletion_{low,medium,high} was a buggy run (see coverage_iou03.csv --
# effectively 0% frame coverage); camera_frame_deletion_new_{low,medium,high} is its
# fixed rerun. Drop the old rows and rename the new_* condition down to the plain
# name so every downstream consumer (which only knows about camera_frame_deletion_*)
# picks up the fixed data without a code change on their end.
_OLD_CAMERA_FRAME_DELETION = {
    "camera_frame_deletion_low", "camera_frame_deletion_medium", "camera_frame_deletion_high",
}


def _use_new_camera_frame_deletion(df: pl.DataFrame) -> pl.DataFrame:
    if "condition" not in df.columns or df.is_empty():
        return df
    return (
        df.filter(~pl.col("condition").is_in(_OLD_CAMERA_FRAME_DELETION))
        .with_columns(pl.col("condition").str.replace("^camera_frame_deletion_new_", "camera_frame_deletion_"))
    )
_DEFAULT_DATASET_ROOT = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
)


def _parse_description_txt(sequence_id: str, dataset_root: str) -> dict:
    path = os.path.join(dataset_root, "data", sequence_id, "description.txt")
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        content = f.read().strip()
    keys = ("location", "time", "weather")
    parts = [p.strip() for p in content.split(",")]
    return dict(zip(keys, parts))


def _sequence_metadata(sequences: list[str], dataset_root: str) -> pl.DataFrame:
    """One row per sequence_id: weather (falls back to "normal" if missing/
    invalid, same as pipeline.py), environment (=location, None if absent),
    time_of_day (=time, None if absent). A missing description.txt degrades to
    an all-null/normal row rather than raising, consistent with this repo's
    missing-file-degrades-gracefully convention.
    """
    rows = []
    for seq in sequences:
        desc = _parse_description_txt(seq, dataset_root)
        weather = desc.get("weather", "normal")
        if weather not in _ALLOWED_WEATHER:
            weather = "normal"
        rows.append({
            "sequence": seq,
            "weather": weather,
            "environment": desc.get("location") or None,
            "time_of_day": desc.get("time") or None,
        })
    return pl.DataFrame(rows, schema={
        "sequence": pl.Utf8, "weather": pl.Utf8, "environment": pl.Utf8, "time_of_day": pl.Utf8,
    })


def _enrich(df: pl.DataFrame, dataset_root: str) -> pl.DataFrame:
    """Additive schema evolution only: appends distance_from_ego (3D Euclidean,
    null where loc_x/y/z are null e.g. FN rows) and the three sequence-level
    metadata columns. Never renames/removes existing columns.
    """
    df = df.with_columns(
        (pl.col("loc_x") ** 2 + pl.col("loc_y") ** 2 + pl.col("loc_z") ** 2)
        .sqrt()
        .alias("distance_from_ego")
    )
    sequences = df["sequence"].unique().to_list()
    seq_meta = _sequence_metadata(sequences, dataset_root)
    return df.join(seq_meta, on="sequence", how="left")

# cls trunc occ alpha bbox_l bbox_t bbox_r bbox_b h w l loc_x loc_y loc_z rot_y [score]
#   0    1   2    3     4      5      6      7    8 9 10  11    12    13    14    15
_LINE_RE = re.compile(
    r"^(\S+)\s+(?:\S+\s+){7}(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)(?:\s+(\S+))?\s*$"
)


def _parse_kitti_line(line: str) -> Optional[dict]:
    m = _LINE_RE.match(line)
    if not m:
        return None
    cls, h, w, l, x, y, z, rot, score = m.groups()
    return {
        "cls": cls, "height": float(h), "width": float(w), "length": float(l),
        "loc_x": float(x), "loc_y": float(y), "loc_z": float(z),
        "rotation_y": float(rot), "score": float(score) if score is not None else None,
    }


def _parse_preds_txt(path: str) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Returns (real_prediction_rows, attempted_zero_detection_frames).

    The second frame tracks every (sequence, frame, condition) whose only
    line was the `dummy` placeholder -- i.e. inference actually ran on that
    frame and legitimately produced zero detections, as distinct from a
    frame that's simply absent from the file (crashed/never-run job). This
    distinction matters downstream: a dummy frame's GT objects are all real
    misses (should synthesize FN rows for every one of them); an absent
    frame was never evaluated at all and must not be scored either way.
    Confirmed empirically: some conditions (e.g. lidar_gaussian_noise_high)
    have FULL frame coverage in this file but are >99% dummy lines for
    individual sequences -- treating those as "missing data" and excluding
    them (as an earlier pass of this analysis did) silently drops real
    catastrophic-miss frames from AP instead of counting them as misses,
    inflating mAP for exactly the conditions this pipeline exists to catch.
    """
    rows = []
    dummy_frames = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            tag, _, rest = line.partition(" ")
            seq, frame, condition = tag.split("_", 2)
            if rest.split(" ", 1)[0] == "dummy":
                # K-Radar's own placeholder for "this frame had zero
                # predictions" -- same 16-token layout as a real scored KITTI
                # line (cls=dummy, all-zero box, score=0), so it parses
                # successfully as a spurious zero-volume prediction if not
                # filtered here. Confirmed via all_preds.txt: 47307 such rows
                # as of 2026-08-20, all silently counted as FP before this
                # fix -- see docs/vAIlt/06_Results/robustness-metric-implementation-plan.md S6.
                dummy_frames.append({"sequence": seq, "frame": frame, "condition": condition})
                continue
            parsed = _parse_kitti_line(rest)
            if parsed is None:
                continue
            parsed.update(sequence=seq, frame=frame, condition=condition)
            rows.append(parsed)
    if not rows:
        preds_df = pl.DataFrame(schema={
            "sequence": pl.Utf8, "frame": pl.Utf8, "condition": pl.Utf8, "cls": pl.Utf8,
            "height": pl.Float64, "width": pl.Float64, "length": pl.Float64,
            "loc_x": pl.Float64, "loc_y": pl.Float64, "loc_z": pl.Float64,
            "rotation_y": pl.Float64, "score": pl.Float64,
        })
    else:
        preds_df = pl.DataFrame(rows)
    if not dummy_frames:
        dummy_df = pl.DataFrame(schema={"sequence": pl.Utf8, "frame": pl.Utf8, "condition": pl.Utf8})
    else:
        dummy_df = pl.DataFrame(dummy_frames).unique()
    return _use_new_camera_frame_deletion(preds_df), _use_new_camera_frame_deletion(dummy_df)


def _parse_gts_txt(path: str) -> pl.DataFrame:
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            tag, _, rest = line.partition(" ")
            seq, frame = tag.split("_", 1)
            parsed = _parse_kitti_line(rest)
            if parsed is None:
                continue
            parsed.pop("score", None)
            parsed.update(sequence=seq, frame=frame)
            rows.append(parsed)
    if not rows:
        return pl.DataFrame(schema={
            "sequence": pl.Utf8, "frame": pl.Utf8, "cls": pl.Utf8,
            "height": pl.Float64, "width": pl.Float64, "length": pl.Float64,
            "loc_x": pl.Float64, "loc_y": pl.Float64, "loc_z": pl.Float64,
            "rotation_y": pl.Float64,
        })
    return pl.DataFrame(rows)


def _match_via_coordinates(
    preds: pl.DataFrame, gts: pl.DataFrame, iou_threshold: float,
    dummy_frames: Optional[pl.DataFrame] = None,
) -> pl.DataFrame:
    """Fallback backend: per-(sequence, frame, condition) BEV IoU matching
    against that frame's raw all_gts.txt rows (no cross-condition dedup --
    GT content is identical across conditions by construction, so matching
    condition-by-condition against its own GT copy gives the same result as
    matching against a canonical copy, just recomputed per condition).

    `dummy_frames` (sequence, frame, condition) are frames that were
    genuinely attempted but produced zero real predictions -- these are
    iterated in addition to `preds`' own groups (with an empty pred_frame),
    so every GT object in them correctly synthesizes an FN row instead of
    silently vanishing because no prediction row exists to key a groupby on.
    """
    preds = preds.with_row_index("pred_row_id")
    gts = gts.with_row_index("gt_row_id")

    out_rows: list[dict] = []
    gt_groups = {(s, f): df for (s, f), df in gts.group_by(["sequence", "frame"], maintain_order=True)}

    pred_keys = {(s, f, c) for s, f, c in preds.select("sequence", "frame", "condition").iter_rows()}
    dummy_only_keys: list[tuple[str, str, str]] = []
    if dummy_frames is not None and dummy_frames.height > 0:
        for s, f, c in dummy_frames.select("sequence", "frame", "condition").iter_rows():
            if (s, f, c) not in pred_keys:
                dummy_only_keys.append((s, f, c))

    empty_pred_frame = preds.clear()

    def _frame_groups():
        for (seq, frame, cond), pred_frame in preds.group_by(["sequence", "frame", "condition"], maintain_order=True):
            yield seq, frame, cond, pred_frame
        for seq, frame, cond in dummy_only_keys:
            yield seq, frame, cond, empty_pred_frame

    for seq, frame, cond, pred_frame in _frame_groups():
        gt_frame = gt_groups.get((seq, frame))
        if gt_frame is None or len(gt_frame) == 0:
            gt_frame = gts.clear()

        pairs = match_frame_pairs(gt_frame, pred_frame, iou_threshold)
        matched_gt_idx = {gi for gi, _, _ in pairs}
        matched_pred_idx = {pi for _, pi, _ in pairs}
        iou_by_pred = {pi: iou for _, pi, iou in pairs}
        gt_row_id_by_local_idx = {i: int(gt_frame["gt_row_id"][i]) for i in range(len(gt_frame))}

        for i in range(len(pred_frame)):
            row = {c: pred_frame[c][i] for c in pred_frame.columns}
            is_tp = i in matched_pred_idx
            row["is_tp"] = is_tp
            row["is_fp"] = not is_tp
            row["is_fn"] = False
            row["iou"] = iou_by_pred.get(i)
            if is_tp:
                gt_local = next(gi for gi, pi, _ in pairs if pi == i)
                row["matched_gt_row_id"] = gt_row_id_by_local_idx[gt_local]
                row["gt_height"] = gt_frame["height"][gt_local]
                row["gt_width"] = gt_frame["width"][gt_local]
                row["gt_length"] = gt_frame["length"][gt_local]
                row["gt_loc_x"] = gt_frame["loc_x"][gt_local]
                row["gt_loc_y"] = gt_frame["loc_y"][gt_local]
                row["gt_loc_z"] = gt_frame["loc_z"][gt_local]
                row["gt_rotation_y"] = gt_frame["rotation_y"][gt_local]
            else:
                for c in ("matched_gt_row_id", "gt_height", "gt_width", "gt_length",
                          "gt_loc_x", "gt_loc_y", "gt_loc_z", "gt_rotation_y"):
                    row[c] = None
            out_rows.append(row)

        for gi in range(len(gt_frame)):
            if gi in matched_gt_idx:
                continue
            fn_row = {c: None for c in pred_frame.columns if c not in ("sequence", "frame", "condition")}
            fn_row.update(sequence=seq, frame=frame, condition=cond)
            fn_row["is_tp"] = False
            fn_row["is_fp"] = False
            fn_row["is_fn"] = True
            fn_row["iou"] = None
            fn_row["matched_gt_row_id"] = int(gt_frame["gt_row_id"][gi])
            fn_row["cls"] = gt_frame["cls"][gi]
            fn_row["gt_height"] = gt_frame["height"][gi]
            fn_row["gt_width"] = gt_frame["width"][gi]
            fn_row["gt_length"] = gt_frame["length"][gi]
            fn_row["gt_loc_x"] = gt_frame["loc_x"][gi]
            fn_row["gt_loc_y"] = gt_frame["loc_y"][gi]
            fn_row["gt_loc_z"] = gt_frame["loc_z"][gi]
            fn_row["gt_rotation_y"] = gt_frame["rotation_y"][gi]
            out_rows.append(fn_row)

    return pl.DataFrame(out_rows)


def _match_via_coordinates_one_seq(args: tuple) -> pl.DataFrame:
    """Process-pool worker: run _match_via_coordinates for a single
    sequence's predictions/GT. Matching is entirely per-(sequence, frame,
    condition) -- no cross-sequence state -- so sharding by sequence is
    embarrassingly parallel, same reasoning as reconstruct_object_ids.py's
    Stage B parallelism.
    """
    preds_seq, gts_seq, iou_threshold, dummy_seq = args
    return _match_via_coordinates(preds_seq, gts_seq, iou_threshold, dummy_seq)


def _match_via_coordinates_parallel(
    preds: pl.DataFrame, gts: pl.DataFrame, iou_threshold: float, workers: int,
    dummy_frames: Optional[pl.DataFrame] = None,
) -> pl.DataFrame:
    """Same result as _match_via_coordinates, sharded across sequences and
    run in a process pool. Use for real-scale runs (hundreds of thousands of
    pred rows) -- the underlying matcher is a per-row Python loop, so at that
    scale single-process is impractically slow (see plan doc S6 timing note).

    Uses the "spawn" start method explicitly, NOT the Linux default "fork".
    By the time this function runs, `preds`/`gts` are already-built polars
    DataFrames, which means polars' internal query-engine thread pool is
    already live in this process (confirmed empirically: 24 threads on an
    8-core machine). fork()ing a process with live background threads is
    unsafe -- the child inherits a single-threaded copy of process memory but
    any locks those threads held are frozen mid-state, which deadlocked every
    worker (0 CPU time, stuck on futex_do_wait) on the first attempt at this,
    44m36s wall time for ~6.5s of total CPU work. "spawn" starts each worker
    as a fresh interpreter instead of forking, at the cost of some startup
    overhead (~1s/worker for module re-imports) -- a real cost, but tiny
    against a hang that never completes.
    """
    import multiprocessing
    from concurrent.futures import ProcessPoolExecutor, as_completed

    dummy_frames = dummy_frames if dummy_frames is not None else preds.clear().select("sequence", "frame", "condition")
    sequences = sorted(set(preds["sequence"].unique().to_list()) | set(dummy_frames["sequence"].unique().to_list()))
    tasks = []
    for seq in sequences:
        preds_seq = preds.filter(pl.col("sequence") == seq)
        gts_seq = gts.filter(pl.col("sequence") == seq)
        dummy_seq = dummy_frames.filter(pl.col("sequence") == seq)
        tasks.append((seq, preds_seq, gts_seq, iou_threshold, dummy_seq))

    results: list[pl.DataFrame] = []
    ctx = multiprocessing.get_context("spawn")
    with ProcessPoolExecutor(max_workers=workers, mp_context=ctx) as pool:
        futures = {pool.submit(_match_via_coordinates_one_seq, t[1:]): t[0] for t in tasks}
        for fut in as_completed(futures):
            seq = futures[fut]
            df = fut.result()
            print(f"  seq {seq}: {len(df)} rows matched", flush=True)
            results.append(df)

    return pl.concat(results, how="vertical")


def _load_via_trkid(gts_path: str, preds_path: str, fn_path: str) -> pl.DataFrame:
    """Preferred backend: parse reconstruct_object_ids.py's output.

    outputs/all_gts_with_trkid.txt columns:
        seq_frame cls_kw trk_id ambiguous h w l loc_x loc_y loc_z rot_y
    outputs/all_preds_with_trkid.txt columns:
        seq_frame_condition cls_kw trk_id is_fp h w l loc_x loc_y loc_z rot_y score
    outputs/all_fn.txt columns:
        seq_frame_condition gt_line_idx=<idx>
    """
    gt_rows = []
    with open(gts_path) as f:
        for line_idx_in_file, line in enumerate(f):
            parts = line.split()
            if not parts:
                continue
            tag = parts[0]
            seq, frame = tag.split("_", 1)
            gt_rows.append({
                "sequence": seq, "frame": frame, "cls": parts[1],
                "trk_id": int(parts[2]) if parts[2] != "None" else None,
                "ambiguous": bool(int(parts[3])),
                "height": float(parts[4]), "width": float(parts[5]), "length": float(parts[6]),
                "loc_x": float(parts[7]), "loc_y": float(parts[8]), "loc_z": float(parts[9]),
                "rotation_y": float(parts[10]),
            })
    gt_df = pl.DataFrame(gt_rows)

    pred_rows = []
    with open(preds_path) as f:
        for line in f:
            parts = line.split()
            if not parts:
                continue
            tag = parts[0]
            seq, frame, condition = tag.split("_", 2)
            pred_rows.append({
                "sequence": seq, "frame": frame, "condition": condition, "cls": parts[1],
                "trk_id": int(parts[2]) if parts[2] != "None" else None,
                "is_fp": bool(int(parts[3])),
                "height": float(parts[4]), "width": float(parts[5]), "length": float(parts[6]),
                "loc_x": float(parts[7]), "loc_y": float(parts[8]), "loc_z": float(parts[9]),
                "rotation_y": float(parts[10]), "score": float(parts[11]),
            })
    pred_df = _use_new_camera_frame_deletion(pl.DataFrame(pred_rows))

    # Join preds -> matched GT box on (sequence, frame, trk_id) where trk_id
    # is not null and is_fp is False (FP preds have no matched GT by
    # construction -- reconstruct_object_ids.py's greedy_match_frame only
    # sets trk_id on a match).
    gt_for_join = gt_df.rename({
        "trk_id": "trk_id", "height": "gt_height", "width": "gt_width", "length": "gt_length",
        "loc_x": "gt_loc_x", "loc_y": "gt_loc_y", "loc_z": "gt_loc_z", "rotation_y": "gt_rotation_y",
    }).select("sequence", "frame", "trk_id", "gt_height", "gt_width", "gt_length",
              "gt_loc_x", "gt_loc_y", "gt_loc_z", "gt_rotation_y")

    # Defensive check: the join below assumes trk_id is unique within every
    # (sequence, frame) group of gt_for_join. reconstruct_object_ids.py's
    # used[] guard prevents *it* from creating a duplicate, but a duplicate
    # trk_id upstream in the raw label files would silently fan out this
    # left-join and inflate is_tp counts. Fail loudly instead.
    dup_keys = (
        gt_for_join.group_by(["sequence", "frame", "trk_id"])
        .agg(pl.len().alias("n"))
        .filter(pl.col("n") > 1)
    )
    if dup_keys.height > 0:
        raise ValueError(
            f"Duplicate (sequence, frame, trk_id) in gt_for_join -- join at "
            f"line below would fan out rows and inflate is_tp counts:\n{dup_keys}"
        )

    pred_df = pred_df.with_columns(
        (~pl.col("is_fp") & pl.col("trk_id").is_not_null()).alias("is_tp"),
    ).with_columns(
        pl.col("is_fp").alias("is_fp"),
        pl.lit(False).alias("is_fn"),
    )
    pred_df = pred_df.join(gt_for_join, on=["sequence", "frame", "trk_id"], how="left")

    # FN rows: outputs/all_fn.txt references gt_line_idx into all_gts.txt's
    # per-(seq,frame) block, NOT this trk_id file's row order -- but since
    # both are written in the same per-frame order as all_gts.txt (see
    # reconstruct_object_ids.py's parse_gts_file), the Nth gt row per
    # (seq, frame) in gt_df corresponds to gt_line_idx==N here too.
    gt_df = gt_df.with_columns(pl.int_range(pl.len()).over(["sequence", "frame"]).alias("gt_line_idx"))

    fn_rows = []
    with open(fn_path) as f:
        for line in f:
            parts = line.split()
            if not parts:
                continue
            tag, kv = parts[0], parts[1]
            seq, frame, condition = tag.split("_", 2)
            gt_line_idx = int(kv.split("=")[1])
            fn_rows.append({"sequence": seq, "frame": frame, "condition": condition, "gt_line_idx": gt_line_idx})
    fn_df = pl.DataFrame(fn_rows) if fn_rows else pl.DataFrame(
        schema={"sequence": pl.Utf8, "frame": pl.Utf8, "condition": pl.Utf8, "gt_line_idx": pl.Int64})
    fn_df = _use_new_camera_frame_deletion(fn_df)

    fn_df = fn_df.join(
        gt_df.select("sequence", "frame", "gt_line_idx", "cls", "trk_id",
                      "height", "width", "length", "loc_x", "loc_y", "loc_z", "rotation_y"),
        on=["sequence", "frame", "gt_line_idx"], how="left",
    ).rename({
        "height": "gt_height", "width": "gt_width", "length": "gt_length",
        "loc_x": "gt_loc_x", "loc_y": "gt_loc_y", "loc_z": "gt_loc_z", "rotation_y": "gt_rotation_y",
    }).with_columns(
        pl.lit(False).alias("is_tp"), pl.lit(False).alias("is_fp"), pl.lit(True).alias("is_fn"),
        pl.lit(None, dtype=pl.Float64).alias("height"), pl.lit(None, dtype=pl.Float64).alias("width"),
        pl.lit(None, dtype=pl.Float64).alias("length"), pl.lit(None, dtype=pl.Float64).alias("loc_x"),
        pl.lit(None, dtype=pl.Float64).alias("loc_y"), pl.lit(None, dtype=pl.Float64).alias("loc_z"),
        pl.lit(None, dtype=pl.Float64).alias("rotation_y"), pl.lit(None, dtype=pl.Float64).alias("score"),
    ).drop("gt_line_idx")

    common_cols = ["sequence", "frame", "condition", "cls", "trk_id",
                    "height", "width", "length", "loc_x", "loc_y", "loc_z", "rotation_y", "score",
                    "is_tp", "is_fp", "is_fn", "gt_height", "gt_width", "gt_length",
                    "gt_loc_x", "gt_loc_y", "gt_loc_z", "gt_rotation_y"]
    pred_df = pred_df.select(common_cols)
    fn_df = fn_df.select(common_cols)
    return pl.concat([pred_df, fn_df], how="vertical_relaxed")


def load_prediction_rows(
    preds_txt: str = "outputs/all_preds.txt",
    gts_txt: str = "outputs/all_gts.txt",
    trkid_gts_txt: str = "outputs/all_gts_with_trkid.txt",
    trkid_preds_txt: str = "outputs/all_preds_with_trkid.txt",
    fn_txt: str = "outputs/all_fn.txt",
    iou_threshold: float = 0.5,
    force_backend: Optional[str] = None,
    workers: int = 1,
    dataset_root: str = _DEFAULT_DATASET_ROOT,
) -> pl.DataFrame:
    """Canonical entry point: one row per (sequence, condition, frame,
    prediction) plus synthesized FN rows, with TP/FP/FN status and (where
    matched) both the predicted and matched-GT box for TP-error decomposition.
    Every row additionally carries distance_from_ego, weather, environment,
    time_of_day (see _enrich).

    Backend selection: trk_id path if all three of trkid_gts_txt/
    trkid_preds_txt/fn_txt exist, else the coordinate/IoU fallback on
    preds_txt/gts_txt. Pass force_backend="trkid"|"coordinate" to override.

    workers > 1 only affects the coordinate backend -- shards the per-row
    matching loop across sequences in a process pool (see
    _match_via_coordinates_parallel). The trk_id backend is already a direct
    file parse/join, no per-row loop to parallelize.

    dataset_root: directory whose data/{sequence_id}/description.txt holds
    weather/location/time metadata. Defaults to this file's own repo root
    (repos/K-Radar), i.e. ../.. from scripts/alvis/.
    """
    use_trkid = (
        force_backend == "trkid"
        or (force_backend is None
            and os.path.exists(trkid_gts_txt) and os.path.exists(trkid_preds_txt) and os.path.exists(fn_txt))
    )
    if use_trkid:
        df = _load_via_trkid(trkid_gts_txt, trkid_preds_txt, fn_txt)
    else:
        preds, dummy_frames = _parse_preds_txt(preds_txt)
        gts = _parse_gts_txt(gts_txt)
        if workers > 1:
            df = _match_via_coordinates_parallel(preds, gts, iou_threshold, workers, dummy_frames)
        else:
            df = _match_via_coordinates(preds, gts, iou_threshold, dummy_frames)
    return _enrich(df, dataset_root)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--outputs-dir", default="outputs")
    ap.add_argument("--iou-threshold", type=float, default=0.5)
    ap.add_argument("--force-backend", choices=["trkid", "coordinate"], default=None)
    ap.add_argument("--workers", type=int, default=1,
                     help="parallelize the coordinate-fallback matcher across sequences (no effect on the trk_id backend)")
    ap.add_argument("--out", default=None, help="optional parquet path to write the row table to")
    ap.add_argument("--dataset-root", default=_DEFAULT_DATASET_ROOT,
                     help="dir whose data/{sequence_id}/description.txt holds weather/location/time")
    args = ap.parse_args()

    df = load_prediction_rows(
        preds_txt=os.path.join(args.outputs_dir, "all_preds.txt"),
        gts_txt=os.path.join(args.outputs_dir, "all_gts.txt"),
        trkid_gts_txt=os.path.join(args.outputs_dir, "all_gts_with_trkid.txt"),
        trkid_preds_txt=os.path.join(args.outputs_dir, "all_preds_with_trkid.txt"),
        fn_txt=os.path.join(args.outputs_dir, "all_fn.txt"),
        iou_threshold=args.iou_threshold,
        force_backend=args.force_backend,
        workers=args.workers,
        dataset_root=args.dataset_root,
    )
    print(f"Loaded {len(df)} rows: {df['is_tp'].sum()} TP, {df['is_fp'].sum()} FP, {df['is_fn'].sum()} FN")
    if args.out:
        df.write_parquet(args.out)
        print(f"Wrote {args.out}")
