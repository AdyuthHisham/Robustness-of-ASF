#!/usr/bin/env python3
"""Line charts of mAP / mATE / mASE vs. distance from ego, restricted to the
all-zero (complete sensor loss) conditions only -- one line per sensor
(camera_loss_complete, lidar_loss_complete_zero, radar_loss_complete_zero)
plus a bold `original` baseline line.

Reuses row-table loading, binning, and metric formulas from
distance_line_charts.py (same 10m bins over 0-80m, same frame_deletion
exclusion, same MIN_GT_PER_BIN / MIN_TP_PER_BIN gating) -- this script only
narrows which conditions get drawn.

Run standalone:
    uv run python scripts/analysis/zero_ablation_line_charts.py
Each panel also carries a 95% bootstrap CI band (resampling GT/TP objects
within each (condition, distance_bin) cell, 500 resamples) so sparse tail
bins -- distant bins have far fewer GT objects, especially for radar --
don't read as equally trustworthy as the dense near-ego bins. A shared N_gt
bar subplot underneath (one bar chart, from the `original` condition's GT
counts, since GT counts don't change across corruption conditions -- only
detections do) makes the sample-size falloff explicit rather than implicit
in band width alone.
"""
from __future__ import annotations

from amscup_paths import FIGURES_DIR  # noqa: E402
import sys
from pathlib import Path

import matplotlib
import numpy as np
import polars as pl

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from distance_line_charts import (
    BIN_MIDPOINTS,
    CLEAN_CONDITION,
    MIN_GT_PER_BIN,
    compute_ate_ase_by_condition_bin,
    compute_map_by_condition_bin,
    load_row_table,
)

from robustness.ap_metrics import compute_ap  # noqa: E402

ZERO_CONDITIONS = [
    ("camera_loss_complete_zero", "camera", "#2ca02c"),
    ("lidar_loss_complete_zero", "lidar", "#e8590c"),
    ("radar_loss_complete_zero", "radar", "#7b3fe4"),
]

N_BOOTSTRAP = 500
CI_LO, CI_HI = 2.5, 97.5
RNG_SEED = 0


def _bootstrap_ap_samples(rows: pl.DataFrame, n_boot: int = N_BOOTSTRAP, seed: int = RNG_SEED) -> list[float]:
    """Bootstrap draws of AP for one (condition, distance_bin, cls) cell's
    rows, by resampling GT objects (TP+FN rows) and detections (TP+FP rows)
    independently with replacement -- each resample is itself a valid
    row-table cell fed straight through compute_ap. [] if too few rows."""
    if rows.height < 2:
        return []
    rng = np.random.default_rng(seed)
    gt_rows = rows.filter(pl.col("is_tp") | pl.col("is_fn"))
    det_only_fp = rows.filter(pl.col("is_fp") & ~pl.col("is_tp"))
    if gt_rows.height == 0:
        return []
    aps = []
    for _ in range(n_boot):
        gt_idx = rng.integers(0, gt_rows.height, gt_rows.height)
        fp_idx = rng.integers(0, det_only_fp.height, det_only_fp.height) if det_only_fp.height else np.array([], dtype=int)
        resampled = pl.concat([gt_rows[gt_idx], det_only_fp[fp_idx]]) if det_only_fp.height else gt_rows[gt_idx]
        result = compute_ap(resampled)
        if result["ap"] is not None:
            aps.append(result["ap"])
    return aps


def _bootstrap_ci_mean(values: np.ndarray, n_boot: int = N_BOOTSTRAP, seed: int = RNG_SEED) -> tuple[float, float] | None:
    """95% CI on the mean of `values` (per-TP ATE or ASE) via resampling."""
    if len(values) < 2:
        return None
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(values), (n_boot, len(values)))
    means = values[idx].mean(axis=1)
    return (float(np.percentile(means, CI_LO)), float(np.percentile(means, CI_HI)))


def compute_map_ci_by_condition_bin(row_table: pl.DataFrame) -> dict[str, dict[str, tuple[float, float]]]:
    """{condition: {distance_bin: (ci_lo, ci_hi)}} on the *mean-of-per-class-AP*
    statistic -- must match compute_map_by_condition_bin's estimator exactly
    (bootstrap each class's AP independently, then average per resample
    draw), not AP computed on classes pooled together, since those two
    statistics diverge whenever per-class AP levels differ (e.g. sed vs. bus)
    and produce a CI band that doesn't actually bracket the plotted line."""
    out: dict[str, dict[str, tuple[float, float]]] = {}
    for (cond, dbin), bin_group in row_table.group_by(["condition", "distance_bin"], maintain_order=True):
        per_class_samples = []
        total_gt = 0
        for cls, cls_group in bin_group.group_by("cls", maintain_order=True):
            gt_n = cls_group.filter(pl.col("is_tp") | pl.col("is_fn")).height
            if gt_n == 0:
                continue
            samples = _bootstrap_ap_samples(cls_group)
            if not samples:
                continue
            total_gt += gt_n
            per_class_samples.append(samples)
        if total_gt < MIN_GT_PER_BIN or not per_class_samples:
            continue
        n = min(len(s) for s in per_class_samples)
        if n < N_BOOTSTRAP // 2:
            continue
        means = np.mean([s[:n] for s in per_class_samples], axis=0)
        out.setdefault(cond, {})[dbin] = (float(np.percentile(means, CI_LO)), float(np.percentile(means, CI_HI)))
    return out


def compute_ate_ase_ci_by_condition_bin(
    row_table: pl.DataFrame,
) -> tuple[dict[str, dict[str, tuple[float, float]]], dict[str, dict[str, tuple[float, float]]]]:
    tp = row_table.filter(pl.col("is_tp"))
    tp = tp.with_columns(
        (((pl.col("loc_x") - pl.col("gt_loc_x")) ** 2 + (pl.col("loc_z") - pl.col("gt_loc_z")) ** 2) ** 0.5).alias("ate")
    )
    intersection = (
        pl.min_horizontal("width", "gt_width")
        * pl.min_horizontal("length", "gt_length")
        * pl.min_horizontal("height", "gt_height")
    )
    union = (
        pl.col("width") * pl.col("length") * pl.col("height")
        + pl.col("gt_width") * pl.col("gt_length") * pl.col("gt_height")
        - intersection
    )
    tp = tp.with_columns((1 - intersection / union).alias("ase"))
    ate_ci: dict[str, dict[str, tuple[float, float]]] = {}
    ase_ci: dict[str, dict[str, tuple[float, float]]] = {}
    for (cond, dbin), group in tp.group_by(["condition", "distance_bin"], maintain_order=True):
        ate_ci_val = _bootstrap_ci_mean(group["ate"].to_numpy())
        ase_ci_val = _bootstrap_ci_mean(group["ase"].to_numpy())
        if ate_ci_val is not None:
            ate_ci.setdefault(cond, {})[dbin] = ate_ci_val
        if ase_ci_val is not None:
            ase_ci.setdefault(cond, {})[dbin] = ase_ci_val
    return ate_ci, ase_ci


def compute_n_gt_by_bin(row_table: pl.DataFrame, condition: str = CLEAN_CONDITION) -> dict[str, int]:
    """N_gt per distance bin for one condition (default `original`), used as
    the shared sample-size bar chart -- GT counts don't change across
    corruption conditions, only detections do."""
    sub = row_table.filter((pl.col("condition") == condition) & (pl.col("is_tp") | pl.col("is_fn")))
    counts = sub.group_by("distance_bin").agg(pl.len().alias("n"))
    return {row["distance_bin"]: row["n"] for row in counts.iter_rows(named=True)}


def build_zero_ablation_chart(
    metric_name: str,
    values_by_condition: dict[str, dict[str, float]],
    ci_by_condition: dict[str, dict[str, tuple[float, float]]],
    n_gt_by_bin: dict[str, int],
    y_label: str,
    out_dir: Path,
) -> Path:
    fig, (ax, ax_n) = plt.subplots(
        2, 1, figsize=(9, 7.5), sharex=True, height_ratios=[3, 1], gridspec_kw={"hspace": 0.08}
    )

    def _plot_line(cond: str, color: str, label: str, linewidth: float, zorder: int) -> None:
        vals = values_by_condition.get(cond, {})
        if not vals:
            return
        bins_sorted = sorted(vals, key=int)
        xs = [BIN_MIDPOINTS[int(b)] for b in bins_sorted]
        ys = [vals[b] for b in bins_sorted]
        ax.plot(xs, ys, color=color, linewidth=linewidth, marker="o", markersize=5 if linewidth > 2 else 4, label=label, zorder=zorder)
        ci = ci_by_condition.get(cond, {})
        ci_xs, ci_lo, ci_hi = [], [], []
        for b in bins_sorted:
            if b in ci:
                ci_xs.append(BIN_MIDPOINTS[int(b)])
                ci_lo.append(ci[b][0])
                ci_hi.append(ci[b][1])
        if ci_xs:
            ax.fill_between(ci_xs, ci_lo, ci_hi, color=color, alpha=0.15, zorder=zorder - 1, linewidth=0)

    _plot_line(CLEAN_CONDITION, "black", "original (clean)", 3.0, 5)
    for cond, sensor, color in ZERO_CONDITIONS:
        _plot_line(cond, color, f"{sensor} all-zero", 2.0, 3)

    ax.set_ylabel(y_label, fontsize=11)
    ax.set_title(
        f"{metric_name} vs. distance from ego, all-zero sensor ablations\n"
        f"(IoU=0.3, all sequences pooled, frame_deletion excluded; shaded band = 95% bootstrap CI, n={N_BOOTSTRAP})",
        fontsize=11,
    )
    ax.grid(linestyle=":", alpha=0.4)
    ax.legend(fontsize=9, loc="best")

    n_bins_sorted = sorted(n_gt_by_bin, key=int)
    ax_n.bar(
        [BIN_MIDPOINTS[int(b)] for b in n_bins_sorted],
        [n_gt_by_bin[b] for b in n_bins_sorted],
        width=8.0,
        color="#888888",
    )
    ax_n.set_ylabel("N_gt\n(original)", fontsize=9)
    ax_n.set_xlabel("Distance from ego (m)", fontsize=11)
    ax_n.grid(linestyle=":", alpha=0.3, axis="y")

    fig.tight_layout()

    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"zero_ablation_{metric_name.lower()}"
    png_path = out_dir / f"{stem}.png"
    svg_path = out_dir / f"{stem}.svg"
    fig.savefig(png_path, dpi=150)
    fig.savefig(svg_path)
    plt.close(fig)
    return png_path


def build_all_charts(out_dir: Path) -> list[Path]:
    row_table = load_row_table()
    map_by_cond_bin = compute_map_by_condition_bin(row_table)
    ate_by_cond_bin, ase_by_cond_bin = compute_ate_ase_by_condition_bin(row_table)
    map_ci = compute_map_ci_by_condition_bin(row_table)
    ate_ci, ase_ci = compute_ate_ase_ci_by_condition_bin(row_table)
    n_gt_by_bin = compute_n_gt_by_bin(row_table)

    return [
        build_zero_ablation_chart("mAP", map_by_cond_bin, map_ci, n_gt_by_bin, "mAP (IoU=0.3, mean over sed+bus)", out_dir),
        build_zero_ablation_chart("mATE", ate_by_cond_bin, ate_ci, n_gt_by_bin, "mATE (m)", out_dir),
        build_zero_ablation_chart("mASE", ase_by_cond_bin, ase_ci, n_gt_by_bin, "mASE (1 - IoU of aligned boxes)", out_dir),
    ]


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=FIGURES_DIR / "zero_ablation_line_charts",
        help="Directory to write PNG+SVG charts to",
    )
    args = parser.parse_args()
    for p in build_all_charts(args.out_dir):
        print(p)


if __name__ == "__main__":
    main()
