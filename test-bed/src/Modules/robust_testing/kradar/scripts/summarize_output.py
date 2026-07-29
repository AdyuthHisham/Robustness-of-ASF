#!/usr/bin/env python
"""scripts/summarize_output.py — Read a kradar_visibility Parquet output and produce a markdown report.

Usage
-----
  uv run python scripts/summarize_output.py outputs/smoke_output.parquet

This script does NOT run any part of the pipeline.  It is a pure
read-and-analyse tool that expects a companion .errors.log file
at the same stem (e.g. outputs/smoke_output.errors.log).
"""

import sys
from pathlib import Path
from typing import Optional

import polars as pl

# ---------------------------------------------------------------------------
# Sensor columns
# ---------------------------------------------------------------------------
VISIBILITY_COLS = [
    "radar_visible",
    "lidar64_visible",
    "lidar128_visible",
    "cam_front_visible",
    "cam_left_visible",
    "cam_right_visible",
    "cam_rear_visible",
]

SCORE_COLS = [
    ("radar_sparsity_score",          "radar"),
    ("lidar64_sparsity_score",        "lidar64"),
    ("lidar128_sparsity_score",       "lidar128"),
    ("cam_front_visibility_score",    "cam_front"),
    ("cam_left_visibility_score",     "cam_left"),
    ("cam_right_visibility_score",    "cam_right"),
    ("cam_rear_visibility_score",     "cam_rear"),
]

PROJ_COLS = [
    "cam_front_proj_x", "cam_front_proj_y",
    "cam_left_proj_x", "cam_left_proj_y",
    "cam_right_proj_x", "cam_right_proj_y",
    "cam_rear_proj_x", "cam_rear_proj_y",
]

# Canonical output schema from config.py (at time of writing)
CANONICAL_SCHEMA = [
    "sequence_id", "frame_idx", "obj_tracking_id", "obj_class",
    "obj_x", "obj_y", "obj_z", "obj_length", "obj_width", "obj_height",
    "obj_theta", "obj_distance_ego", "sensor_identify", "weather",
    "radar_visible", "radar_fov_in", "radar_range_in", "radar_sparsity_score",
    "lidar64_visible", "lidar64_points_count", "lidar64_sparsity_score",
    "lidar128_visible", "lidar128_points_count", "lidar128_sparsity_score",
    "cam_front_visible", "cam_front_proj_x", "cam_front_proj_y",
    "cam_front_visibility_score",
    "cam_left_visible", "cam_left_proj_x", "cam_left_proj_y",
    "cam_left_visibility_score",
    "cam_right_visible", "cam_right_proj_x", "cam_right_proj_y",
    "cam_right_visibility_score",
    "cam_rear_visible", "cam_rear_proj_x", "cam_rear_proj_y",
    "cam_rear_visibility_score",
    "num_sensors_visible", "primary_sensor",
]


def text_histogram(values: pl.Series, bins: int = 10, lo: float = 0.0, hi: float = 1.0,
                   width: int = 40) -> str:
    """Return a simple text histogram for score distributions."""
    counts, edges = values.to_numpy(), None
    import numpy as np

    arr = values.drop_nulls().to_numpy().astype(np.float64)
    if len(arr) == 0:
        return "  (no non-null values)"

    # Clip to [lo, hi] for bin assignment
    clipped = np.clip(arr, lo, hi - 1e-12)
    bin_edges = np.linspace(lo, hi, bins + 1)
    bin_idx = np.digitize(clipped, bin_edges) - 1
    bin_idx = np.clip(bin_idx, 0, bins - 1)

    counts = np.bincount(bin_idx, minlength=bins)
    max_count = counts.max()
    scale = width / max_count if max_count > 0 else 1.0

    lines = []
    for i in range(bins):
        bar_len = int(counts[i] * scale)
        bar = "█" * bar_len
        lo_label = f"{bin_edges[i]:.1f}"
        hi_label = f"{bin_edges[i + 1]:.1f}"
        lines.append(f"  [{lo_label}–{hi_label})  {bar}  {counts[i]}")

    return "\n".join(lines)


def load_errors_log(parquet_path: Path) -> str:
    """Read companion .errors.log file, if it exists."""
    error_log = parquet_path.with_suffix(".errors.log")
    if not error_log.exists():
        return "  (no companion .errors.log found — run with run_full_sequence.py to generate one)"
    content = error_log.read_text().strip()
    return content


def summarize(parquet_path: Path) -> str:
    """Produce a markdown report from a kradar_visibility Parquet output."""
    if not parquet_path.exists():
        return f"# Error\n\nFile not found: `{parquet_path}`"

    df = pl.read_parquet(parquet_path)
    n_rows = df.height
    n_cols = len(df.columns)
    actual_cols = set(df.columns)

    lines: list[str] = []
    sep = lambda: lines.append("")

    # ------------------------------------------------------------------ #
    lines.append("# K-Radar Visibility — Output Summary")
    sep()
    lines.append(f"**Source:** `{parquet_path}`")
    lines.append(f"**Generated:** {_now()}")
    sep()

    # ------------------------------------------------------------------ #
    # Overview
    # ------------------------------------------------------------------ #
    lines.append("## 1. Overview")
    sep()
    seq_ids = sorted(df["sequence_id"].unique().to_list())
    n_frames = df["frame_idx"].n_unique()
    n_objects = df["obj_tracking_id"].n_unique()
    object_classes = sorted(df["obj_class"].unique().to_list()) if "obj_class" in df.columns else []

    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Row count | {n_rows} |")
    lines.append(f"| Column count | {n_cols} |")
    lines.append(f"| Unique sequences | {seq_ids} |")
    lines.append(f"| Unique frames | {n_frames} |")
    lines.append(f"| Unique objects (tracking ID) | {n_objects} |")
    if object_classes:
        lines.append(f"| Object classes | {object_classes} |")
    sep()

    # ------------------------------------------------------------------ #
    # Per-sensor visibility rates
    # ------------------------------------------------------------------ #
    lines.append("## 2. Per-sensor Visibility Rates")
    sep()
    lines.append("Fraction of rows where each sensor reports the object as visible.")
    sep()
    lines.append("| Sensor | Visible | % of rows |")
    lines.append("|--------|---------|-----------|")
    for col in VISIBILITY_COLS:
        if col not in df.columns:
            lines.append(f"| {col} | *missing* | — |")
            continue
        n_visible = df[col].sum()
        pct = n_visible / n_rows * 100
        bar_len = int(pct / 100 * 30)
        bar = "█" * bar_len
        lines.append(f"| {col} | {n_visible} | {pct:>5.1f}% {bar} |")
    sep()

    # ------------------------------------------------------------------ #
    # Ghost flag analysis
    # ------------------------------------------------------------------ #
    lines.append("## 3. Ghost Flag Analysis")
    sep()
    if "ghost_flag" not in df.columns:
        lines.append("*ghost_flag column not present in this output.*")
    else:
        n_ghost = df["ghost_flag"].sum()
        ghost_rate = n_ghost / n_rows * 100
        lines.append(f"| Metric | Value |")
        lines.append(f"|--------|-------|")
        lines.append(f"| ghost_flag=True | {n_ghost} |")
        lines.append(f"| ghost_flag rate | {ghost_rate:.2f}% |")
        lines.append(f"")
        if n_ghost == 0 and n_rows > 0:
            lines.append("> ⚠ **Zero ghost flags** — if there are radar-only objects in this dataset,")
            lines.append("> this rate should be non-zero.  May indicate ghost detection is not firing,")
            lines.append("> or this particular sequence has no radar-only objects.")
        elif ghost_rate > 50:
            lines.append(f"> ⚠ **High ghost rate ({ghost_rate:.1f}%)** — a majority of rows are flagged as")
            lines.append("> ghosts, which likely indicates the heuristic is too aggressive.")
        elif ghost_rate > 20:
            lines.append(f"> ⚠ **Elevated ghost rate ({ghost_rate:.1f}%)** — worth verifying against")
            lines.append("> ground truth that this many objects are truly radar-only.")
        else:
            lines.append("> ✓ Ghost rate looks plausible (small minority).")
    sep()

    # ------------------------------------------------------------------ #
    # Per-sensor score distribution
    # ------------------------------------------------------------------ #
    lines.append("## 4. Per-sensor Score Distributions")
    sep()
    lines.append("Statistics for every `*_score` column present in the output.")
    sep()

    for col, label in SCORE_COLS:
        if col not in df.columns:
            lines.append(f"### `{col}` — *missing*")
            sep()
            continue

        vals = df[col]
        n_nz = (vals > 0).sum()
        n_zero = (vals == 0).sum()
        n_null = vals.null_count()

        lines.append(f"### `{col}` ({label})")
        sep()
        lines.append(f"| Stat | Value |")
        lines.append(f"|------|-------|")
        lines.append(f"| Count | {len(vals)} |")
        lines.append(f"| Non-zero | {n_nz} |")
        lines.append(f"| Zero | {n_zero} |")
        lines.append(f"| Null | {n_null} |")
        lines.append(f"| Min | {vals.min():.6f} |")
        lines.append(f"| Max | {vals.max():.6f} |")
        lines.append(f"| Mean | {vals.mean():.6f} |")
        lines.append(f"| Median | {vals.median():.6f} |")
        lines.append(f"| Std | {vals.std():.6f} |")
        sep()

        # Check for out-of-range scores
        if n_null < len(vals):
            non_null = vals.drop_nulls()
            oob_lo = (non_null < 0.0).sum()
            oob_hi = (non_null > 1.0).sum()
            if oob_lo > 0 or oob_hi > 0:
                lines.append(f"> 🚨 **Out-of-range values:** {oob_lo} < 0.0, {oob_hi} > 1.0")
                sep()

        lines.append("**Histogram (0.1-wide bins):**")
        sep()
        lines.append(text_histogram(vals, bins=10, lo=0.0, hi=1.0))
        sep()

    # ------------------------------------------------------------------ #
    # NaN / null / out-of-range analysis
    # ------------------------------------------------------------------ #
    lines.append("## 5. Data Quality — Nulls, NaNs, and Out-of-Range Scores")
    sep()

    all_score_cols = [c for c, _ in SCORE_COLS]
    null_report: list[tuple[str, int, str]] = []  # (column, count, note)

    for col in df.columns:
        n_null = df[col].null_count()
        if n_null > 0:
            null_report.append((col, n_null, "null"))
        # Also check for NaN in float columns that Polars may not report as null
        if df[col].dtype in (pl.Float32, pl.Float64):
            arr = df[col].to_numpy()
            import numpy as np
            n_nan = int(np.isnan(arr).sum())
            if n_nan > 0:
                null_report.append((col, n_nan, "NaN"))

    if null_report:
        lines.append("| Column | Count | Type |")
        lines.append("|--------|-------|------|")
        for col, cnt, typ in null_report:
            lines.append(f"| {col} | {cnt} | {typ} |")
    else:
        lines.append("No null or NaN values in any column.")
    sep()

    # Out-of-range score check
    lines.append("### Out-of-range scores")
    sep()
    oob_found = False
    for col, label in SCORE_COLS:
        if col not in df.columns:
            continue
        vals = df[col].drop_nulls()
        oob_lo = (vals < 0.0).sum()
        oob_hi = (vals > 1.0).sum()
        if oob_lo > 0 or oob_hi > 0:
            oob_found = True
            lines.append(f"- `{col}`: {oob_lo} below 0, {oob_hi} above 1")
    if not oob_found:
        lines.append("All score values are within [0, 1].")
    sep()

    # ------------------------------------------------------------------ #
    # Column cross-check against config.py OUTPUT_SCHEMA
    # ------------------------------------------------------------------ #
    lines.append("## 6. Schema Cross-check (Config vs Actual)")
    sep()
    lines.append("Columns **expected** by `config.py`'s `OUTPUT_SCHEMA` list **vs** what the Parquet actually contains.")
    sep()

    expected_set = set(CANONICAL_SCHEMA)
    extra = actual_cols - expected_set
    missing = expected_set - actual_cols

    lines.append(f"| | Count |")
    lines.append(f"|---|-------|")
    lines.append(f"| Columns in config schema | {len(expected_set)} |")
    lines.append(f"| Columns in actual Parquet | {len(actual_cols)} |")
    lines.append(f"| Extra (in Parquet but not config) | {len(extra)} |")
    lines.append(f"| Missing (in config but not Parquet) | {len(missing)} |")
    sep()

    if extra:
        lines.append("**Extra columns** (pipeline emits, config schema doesn't list):")
        for c in sorted(extra):
            lines.append(f"  - `{c}`")
        sep()

    if missing:
        lines.append("**Missing columns** (config schema lists, Parquet doesn't have):")
        for c in sorted(missing):
            lines.append(f"  - `{c}`")
        sep()
    else:
        lines.append("All config schema columns are present in the actual output.")
        sep()

    # ------------------------------------------------------------------ #
    # Per-frame errors from companion .errors.log
    # ------------------------------------------------------------------ #
    lines.append("## 7. Per-frame Errors")
    sep()

    error_log_content = load_errors_log(parquet_path)
    error_log_path = parquet_path.with_suffix(".errors.log")

    if "No errors" in error_log_content or (not error_log_content.strip()):
        lines.append("✓ No per-frame errors recorded.")
    else:
        # Count errors
        error_lines = error_log_content.split("\n")
        error_count = sum(1 for l in error_lines if l.startswith("[FRAME"))
        lines.append(f"{error_count} frame(s) had errors.")
        sep()
        lines.append("```")
        lines.append(error_log_content)
        lines.append("```")
    sep()

    # ------------------------------------------------------------------ #
    lines.append("---")
    lines.append(f"*Report generated by `scripts/summarize_output.py` at {_now()}*")
    sep()

    return "\n".join(lines)


def _now() -> str:
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Summarise a kradar_visibility Parquet output as markdown.",
    )
    parser.add_argument(
        "parquet_path",
        type=Path,
        help="Path to a .parquet file produced by the kradar_visibility pipeline.",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Write report to this file instead of stdout.",
    )

    args = parser.parse_args()
    report = summarize(args.parquet_path)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report)
        print(f"Report written to {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()