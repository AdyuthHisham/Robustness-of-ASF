#!/usr/bin/env python3
"""Descriptive distribution charts for the K-Radar dataset itself (not model
performance): GT objects per frame, GT distance from ego, and how frame/object
counts stratify across weather / environment / time_of_day.

Source: `row_table_iou03.parquet` (IoU=0.3), filtered to `condition ==
"original"` only -- the same GT repeats identically across every corrupted
condition (only predictions differ), so including other conditions would
duplicate every GT object ~30x and, for frame_deletion conditions specifically,
under-represent the frames they drop. GT rows are `is_tp | is_fn` (matched or
missed ground truth); `is_fp` rows have no GT and are excluded.

`distance_from_ego` in the row table is the *prediction's* position for
TP/FP rows (null for FN) -- wrong for a GT-only view. Distance here is instead
computed directly from `gt_loc_x`/`gt_loc_z`, consistent for every GT row.

weather / environment / time_of_day are per-sequence metadata (constant across
all frames of a sequence), so strata charts need the full 58-sequence set --
a single sequence gives one category per stratifier.

Usage as a library:
    from dataset_distributions import build_all_charts
    build_all_charts(out_dir=Path("output/dataset_distributions"))

Run standalone:
    uv run python scripts/analysis/dataset_distributions.py
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import polars as pl

HERE = Path(__file__).resolve()
AMSCUP_ROOT = HERE.parents[7]
ROW_TABLE_PATH = (
    AMSCUP_ROOT / "repos" / "K-Radar" / "outputs" / "robustness_reports" / "row_table_iou03.parquet"
)

CLASS_LABEL = {"sed": "Car", "bus": "Bus"}
CLASS_COLOR = {"sed": "#1f77b4", "bus": "#d62728"}
COMBINED_COLOR = "#555555"
STRATA_COLOR = "#2ca02c"


def load_gt_table(row_table_path: Path = ROW_TABLE_PATH) -> pl.DataFrame:
    """One row per GT object (matched or missed), clean condition only."""
    df = pl.read_parquet(row_table_path)
    if df.height == 0:
        raise ValueError(f"{row_table_path} is empty")
    df = df.filter((pl.col("condition") == "original") & (pl.col("is_tp") | pl.col("is_fn")))
    df = df.with_columns(((pl.col("gt_loc_x") ** 2 + pl.col("gt_loc_z") ** 2) ** 0.5).alias("gt_distance"))
    return df


def build_objects_per_frame_chart(gt: pl.DataFrame, out_dir: Path) -> Path:
    per_frame_cls = gt.group_by(["sequence", "frame", "cls"]).agg(pl.len().alias("n"))
    per_frame_total = gt.group_by(["sequence", "frame"]).agg(pl.len().alias("n"))

    max_n = int(per_frame_total["n"].max() or 0)
    bins = list(range(0, max_n + 2))
    ticks = list(range(0, max_n + 1))

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    axes[0].hist(per_frame_total["n"].to_list(), bins=bins, color=COMBINED_COLOR, edgecolor="white", align="left")
    axes[0].set_title("Combined (car + bus)")
    axes[0].set_xlabel("GT objects per frame")
    axes[0].set_ylabel("Frame count")
    axes[0].set_xticks(ticks)

    for cls, label in CLASS_LABEL.items():
        vals = per_frame_cls.filter(pl.col("cls") == cls)["n"].to_list()
        axes[1].hist(vals, bins=bins, color=CLASS_COLOR[cls], edgecolor="white", alpha=0.6, align="left", label=label)
    axes[1].set_title("Per class")
    axes[1].set_xlabel("GT objects per frame")
    axes[1].set_xticks(ticks)
    axes[1].legend()

    # frame count = distinct (sequence, frame) pairs -- `frame` alone is a
    # per-sequence index (0..299 in every sequence) and collapses across
    # sequences if deduped on its own.
    n_frames = per_frame_total.height
    fig.suptitle(f"GT objects per frame (n={n_frames} frames, condition=original)", fontsize=12)
    fig.tight_layout()

    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "objects_per_frame.png"
    fig.savefig(path, dpi=150)
    fig.savefig(out_dir / "objects_per_frame.svg")
    plt.close(fig)
    return path


def build_distance_chart(gt: pl.DataFrame, out_dir: Path) -> Path:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(gt["gt_distance"].to_list(), bins=30, color=COMBINED_COLOR, edgecolor="white")
    ax.set_xlabel("Distance from ego (m)")
    ax.set_ylabel("GT object count")
    ax.set_title(f"GT object distance from ego (n={gt.height} objects, condition=original)")
    fig.tight_layout()

    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "distance_from_ego.png"
    fig.savefig(path, dpi=150)
    fig.savefig(out_dir / "distance_from_ego.svg")
    plt.close(fig)
    return path


def build_strata_chart(gt: pl.DataFrame, column: str, out_dir: Path) -> Path:
    frames = gt.select(["sequence", "frame", column]).unique().group_by(column).agg(pl.len().alias("n_frames"))
    objects = gt.group_by(column).agg(pl.len().alias("n_objects"))
    counts = frames.join(objects, on=column, how="full", coalesce=True).sort("n_objects", descending=True)

    categories = counts[column].to_list()
    n_frames = counts["n_frames"].to_list()
    n_objects = counts["n_objects"].to_list()

    x = list(range(len(categories)))
    fig, axes = plt.subplots(1, 2, figsize=(max(11, len(categories) * 1.8), 5))

    axes[0].bar(x, n_frames, color=STRATA_COLOR, alpha=0.8)
    axes[0].set_title("Frames")
    axes[0].set_ylabel("Frame count")

    axes[1].bar(x, n_objects, color=COMBINED_COLOR, alpha=0.8)
    axes[1].set_title("GT objects")
    axes[1].set_ylabel("GT object count")

    for ax in axes:
        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=30, ha="right")

    fig.suptitle(f"Frame / GT object count by {column.replace('_', ' ')} (condition=original, all sequences)", fontsize=12)
    fig.tight_layout()

    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"strata_{column}.png"
    fig.savefig(path, dpi=150)
    fig.savefig(out_dir / f"strata_{column}.svg")
    plt.close(fig)
    return path


def build_all_charts(out_dir: Path, row_table_path: Path = ROW_TABLE_PATH) -> list[Path]:
    gt = load_gt_table(row_table_path)
    paths = [
        build_objects_per_frame_chart(gt, out_dir),
        build_distance_chart(gt, out_dir),
    ]
    for column in ("weather", "environment", "time_of_day"):
        paths.append(build_strata_chart(gt, column, out_dir))
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "output" / "dataset_distributions",
        help="Directory to write PNG+SVG charts to",
    )
    args = parser.parse_args()
    for p in build_all_charts(args.out_dir):
        print(p)


if __name__ == "__main__":
    main()
