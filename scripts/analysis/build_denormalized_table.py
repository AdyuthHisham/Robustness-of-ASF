#!/usr/bin/env python3
"""Full-granularity denormalized analysis table: one row per prediction/GT
outcome (TP/FP/FN) from `row_table_iou03.parquet`, with two additions the
existing analysis scripts don't need but this exploratory pass does:

1. `distance_from_ego` filled for FN rows. The upstream table only computes
   it from pred loc_x/y/z, so every FN row (no prediction exists) is null
   (346,545 / 1,109,578 rows -- confirmed by direct query 2026-08-28). FN
   rows do have GT coords, so this fills `distance_from_ego` from
   sqrt(gt_loc_x**2 + gt_loc_z**2) for FN rows only, leaving TP/FP rows
   untouched (their existing values already agree with the GT-based formula
   to within ~3m, consistent with loc_y/pitch not being included upstream --
   good enough not to touch already-correct rows). Original value is kept in
   `distance_from_ego_orig` for traceability.

2. `frame_density`: reused verbatim from bar_charts.py's definition (GT
   sed+bus object count per frame in the `original` condition, joined onto
   every condition by (sequence, frame), binned by DENSITY_EDGES=[1,3] ->
   {"1","2-3","4+"}) -- confirmed by user 2026-08-28 this is the intended
   definition (GT count from Sedan/Bus), not a sensor point-count proxy.

   2026-08-31 fix: this join used to be keyed on the raw `frame` column
   directly, which silently failed for every corrupted-condition row (96.36%
   of the table) because `frame` is formatted differently per condition --
   plain zero-padded index ("000013") under `original`, but
   "{radar_tesseract_idx}-{lidar_idx}" under every corrupted condition (see
   repos/K-Radar/scripts/alvis/reconstruct_object_ids.py line ~214,
   frame_tag = f"{tesseract_idx}-{ldr64_idx}"). A new `frame_key_int` column
   is added (see `_add_frame_key`) as a physical-frame join key comparable
   across conditions; `frame` itself is left untouched. Verified against the
   one available ground-truth mapping file,
   repos/K-Radar/outputs/object_id_recon/seq32_frame_index_map.txt (radar
   tesseract_idx 270-290 -> kitti frame 0-20 for sequence 32): C(seq32)=270
   derived independently via min(tesseract_idx) - min(original frame) matches
   the file exactly. Also verified for all 58 sequences that the per-sequence
   offset C is identical whether computed by pooling all corrupted rows or
   computed separately per condition (0/1699 (sequence, condition)
   disagreements) -- strong evidence this is a genuine per-sequence sensor
   frame-index offset, not noise. The naive lidar_idx-based offset (second
   half of `frame`) does NOT reproduce the seq32 ground truth (off by the
   constant rdr-ldr64 desync, e.g. 5 frames for seq32) -- radar tesseract_idx
   (first half of `frame`) is the correct half to use. Full derivation notes:
   [[frame-key-derivation-kradar]] (obsidianVault/Knowledge/).

3. `distance_bucket`: quantile-free fixed-width bins over the observed
   1.0-74.7m range (2026-08-28 query), chosen for round, interpretable edges
   rather than exact quantile equality: [0,20) near, [20,40) mid,
   [40,60) far, [60,75] very_far.

Usage as a library:
    from build_denormalized_table import build_denormalized_table
    build_denormalized_table(out_path=Path("outputs/robustness_reports/full_denormalized_table.parquet"))

Run standalone:
    uv run python scripts/analysis/build_denormalized_table.py
"""
from __future__ import annotations

from amscup_paths import ROOT, REPORTS_DIR  # noqa: E402
import sys
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve()
AMSCUP_ROOT = ROOT
ROW_TABLE_PATH = REPORTS_DIR / "row_table_iou03.parquet"
DEFAULT_OUT_PATH = REPORTS_DIR / "full_denormalized_table.parquet"

sys.path.insert(0, str(HERE.parent))
from radar_charts import CLEAN_CONDITION  # noqa: E402
from master_metrics_table import CONDITIONS  # noqa: E402

SCOPED_OUT_PATH = REPORTS_DIR / "full_denormalized_table_22cond.parquet"

DENSITY_EDGES = [1, 3]
DENSITY_LABELS = ["1", "2-3", "4+"]

DISTANCE_EDGES = [20.0, 40.0, 60.0]
DISTANCE_LABELS = ["near_0_20", "mid_20_40", "far_40_60", "very_far_60_75"]


def _add_frame_key(df: pl.DataFrame) -> pl.DataFrame:
    """Derive `frame_key_int`: intended as a physical-frame join key
    comparable across `original` and every corrupted condition, for cases
    where raw `frame` is not directly comparable (module docstring point 2).

    2026-08-31 history: a Phase-1 audit of a 21:38 build of
    `full_denormalized_table.parquet` found `frame` formatted as a plain
    zero-padded index ("000013") under `original` but as
    "{radar_tesseract_idx}-{lidar_idx}" under every corrupted condition (see
    reconstruct_object_ids.py line ~214), breaking `_add_frame_density`'s
    join for 96.36% of rows. A same-day fix was implemented here (derive
    frame_key_int = tesseract_idx - C(sequence), C validated against
    outputs/object_id_recon/seq32_frame_index_map.txt and against 1,699
    per-(sequence,condition) internal-consistency checks -- see git history
    on this function for that derivation) -- but before it was run against a
    live rebuild, the upstream `row_table_iou03.parquet` was independently
    regenerated (mtime 2026-08-31 22:45, by a separate/concurrent process --
    not this session) and now formats `frame` as "tess-lidar" uniformly
    across ALL conditions including `original`, with a directly-joinable raw
    `frame` column (100% of corrupted (sequence, frame) pairs now have a
    matching `original` row, verified by direct query). The upstream bug this
    function worked around is gone.

    This function is kept (rather than deleted) as defensive plumbing: it
    detects whether `original`'s `frame` already matches the corrupted
    format (the now-current, expected case) and if so just copies `frame`
    into `frame_key_int` unchanged, so downstream code has a stable column
    name regardless of which upstream format is live. Only if `original`'s
    `frame` is a plain non-dashed integer (the old, now-stale format) does it
    fall back to the tesseract_idx-offset derivation. If that fallback path
    is ever exercised again, re-verify it against a real frame_index_map.txt
    before trusting it -- see [[frame-key-derivation-kradar]] in
    obsidianVault/Knowledge/ for the full derivation and validation.
    """
    orig_frame_sample = df.filter(pl.col("condition") == CLEAN_CONDITION)["frame"]
    orig_is_dashed = orig_frame_sample.str.contains("-").all() if orig_frame_sample.len() else True

    if orig_is_dashed:
        # Current, expected case: frame is already directly comparable across
        # conditions -- no derivation needed.
        return df.with_columns(pl.col("frame").alias("frame_key_int"))

    # Fallback: old plain-index `original` format alongside dashed corrupted
    # rows. Derive frame_key_int = tesseract_idx - C(sequence).
    orig_key = (
        df.filter(pl.col("condition") == CLEAN_CONDITION)
        .with_columns(pl.col("frame").cast(pl.Int64).cast(pl.Utf8).alias("frame_key_int"))
    )
    min_orig = orig_key.group_by("sequence").agg(pl.col("frame_key_int").cast(pl.Int64).min().alias("min_orig_frame"))

    corrupt_parts = df.filter(pl.col("condition") != CLEAN_CONDITION).with_columns(
        pl.col("frame").str.split("-").list.get(0).cast(pl.Int64).alias("_tess_idx")
    )
    offsets = (
        corrupt_parts.group_by("sequence")
        .agg(pl.col("_tess_idx").min().alias("min_tess_idx"))
        .join(min_orig, on="sequence", how="left")
        .with_columns((pl.col("min_tess_idx") - pl.col("min_orig_frame")).alias("frame_key_offset"))
        .select(["sequence", "frame_key_offset"])
    )
    corrupt_keyed = corrupt_parts.join(offsets, on="sequence", how="left").with_columns(
        (pl.col("_tess_idx") - pl.col("frame_key_offset")).cast(pl.Utf8).alias("frame_key_int")
    ).drop(["_tess_idx", "frame_key_offset"])

    return pl.concat([orig_key, corrupt_keyed], how="vertical").sort(["sequence", "condition", "frame"])


def _add_frame_density(df: pl.DataFrame) -> pl.DataFrame:
    density = (
        df.filter((pl.col("condition") == CLEAN_CONDITION) & (pl.col("is_tp") | pl.col("is_fn")))
        .group_by(["sequence", "frame_key_int"])
        .agg(pl.len().alias("n_objs"))
        .with_columns(
            pl.col("n_objs").cut(DENSITY_EDGES, labels=DENSITY_LABELS).alias("frame_density")
        )
        .select(["sequence", "frame_key_int", "n_objs", "frame_density"])
    )
    return df.join(density, on=["sequence", "frame_key_int"], how="left")


def _fix_distance_from_ego(df: pl.DataFrame) -> pl.DataFrame:
    gt_dist = (pl.col("gt_loc_x") ** 2 + pl.col("gt_loc_z") ** 2).sqrt()
    return df.with_columns(pl.col("distance_from_ego").alias("distance_from_ego_orig")).with_columns(
        pl.when(pl.col("distance_from_ego").is_null())
        .then(gt_dist)
        .otherwise(pl.col("distance_from_ego"))
        .alias("distance_from_ego")
    )


def _add_distance_bucket(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(
        pl.col("distance_from_ego").cut(DISTANCE_EDGES, labels=DISTANCE_LABELS).alias("distance_bucket")
    )


def build_denormalized_table(out_path: Path = DEFAULT_OUT_PATH) -> pl.DataFrame:
    df = pl.read_parquet(ROW_TABLE_PATH)
    n_before = df.height
    df = _fix_distance_from_ego(df)
    n_dist_null_before = df.filter(pl.col("distance_from_ego_orig").is_null()).height
    n_dist_null_after = df.filter(pl.col("distance_from_ego").is_null()).height
    df = _add_frame_key(df)
    df = _add_frame_density(df)
    df = _add_distance_bucket(df)

    assert df.height == n_before, f"row count changed: {n_before} -> {df.height}"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(out_path)
    print(
        f"Wrote {out_path} ({df.height} rows). "
        f"distance_from_ego null: {n_dist_null_before} -> {n_dist_null_after}. "
        f"frame_density null: {df.filter(pl.col('frame_density').is_null()).height}."
    )
    return df


def build_scoped_table(full_df: pl.DataFrame | None = None, out_path: Path = SCOPED_OUT_PATH) -> pl.DataFrame:
    """22-condition subset of the full table (`original` + 21
    severity-specific corrupted conditions, `frame_deletion` excluded --
    2026-08-25 decision, see [[robustness-metrics-tables]]).

    `full_denormalized_table.parquet` deliberately keeps all 31 conditions
    present in `row_table_iou03.parquet` (including the 9 crashed-coverage
    `*_frame_deletion_*` conditions, 102-40,113 rows each vs. ~40k for a
    healthy condition) as a documented superset, rather than silently
    dropping data at build time -- every analysis script (exploratory_passes.py,
    pass4_stratifier_charts.py, both churn scripts) already filters to this
    same 22-condition scope independently before computing anything, so no
    prior result was affected by the superset. This function exists so a
    consumer who wants the exact scope used everywhere else doesn't have to
    re-derive the filter -- confirmed to produce exactly 872,713 rows,
    matching Pass 1/2's independently-computed totals.
    """
    if full_df is None:
        full_df = pl.read_parquet(DEFAULT_OUT_PATH)
    scoped = full_df.filter(pl.col("condition").is_in(CONDITIONS))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    scoped.write_parquet(out_path)
    print(f"Wrote {out_path} ({scoped.height} rows, {scoped['condition'].n_unique()} conditions).")
    return scoped


if __name__ == "__main__":
    full = build_denormalized_table()
    build_scoped_table(full)
