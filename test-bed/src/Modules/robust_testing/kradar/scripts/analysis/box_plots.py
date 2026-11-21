#!/usr/bin/env python3
"""Box plots of per-sequence metric distributions, one chart per metric, one
box per individual corruption condition (effect x severity treated as
distinct, e.g. RF-L/RF-M/RF-H each get their own box -- never merged by
effect).

Metrics: mAP, mATE, mASE (each split car/bus, separately), and mFR (pooled --
FN rate isn't class-specific in the current row_table). MOTA is out of scope --
this pipeline does frame-independent IoU-based detection matching, not
object tracking with identity linkage across frames, so there is no track
data to compute MOTA from.

Each box summarizes the metric's per-sequence values for one condition
(quartile box + median line + min/max whiskers, standard box-and-whisker --
NOT a financial OHLC candlestick, since these per-sequence samples have no
inherent open/close ordering). A dashed horizontal line marks the clean
(`original`) baseline, computed the same way: median of the per-sequence
`original` values.

Conditions with <90% frame coverage vs `original` for a given sequence (see
radar_charts.py's coverage rationale -- some frame_deletion/gaussian_noise
runs crashed mid-way on Alvis) have that sequence's value excluded from the
box, consistent with radar_charts.py's coverage handling. If a condition has
too few surviving sequences to draw a meaningful box (<3), it is skipped and
reported, not silently drawn from 1-2 points.

Usage as a library:
    from box_plots import build_all_box_plots
    build_all_box_plots(out_dir=Path("output/box_plots"))

Run standalone:
    uv run python scripts/analysis/box_plots.py
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import polars as pl

HERE = Path(__file__).resolve()
AMSCUP_ROOT = HERE.parents[7]
AP_METRICS_DIR = AMSCUP_ROOT / "repos" / "K-Radar" / "scripts" / "alvis"
ROW_TABLE_PATH = AMSCUP_ROOT / "repos" / "K-Radar" / "outputs" / "robustness_reports" / "row_table_iou03.parquet"

sys.path.insert(0, str(AP_METRICS_DIR))
from ap_metrics import compute_ap_grouped  # noqa: E402

sys.path.insert(0, str(HERE.parent))
from radar_charts import (  # noqa: E402
    SENSORS, EFFECTS, SEVERITIES, CLASS_LABEL, CLEAN_CONDITION,
    COVERAGE_THRESHOLD_PCT,
)

CLASSES = ["sed", "bus"]

# x-axis order: all 9 sensor x effect combos x 3 severities = 27 conditions,
# grouped by (sensor, effect) then ascending severity -- same axis grouping
# convention as radar_charts.py's AXIS_ORDER, just flattened with severity.
CONDITION_ORDER = [
    (sensor, effect, severity)
    for sensor in SENSORS
    for effect in EFFECTS
    for severity in SEVERITIES
]


def _condition_label(sensor: str, effect: str, severity: str) -> str:
    """Two-letter sensor+effect code (same as radar_charts.CONDITION_CODE)
    plus a severity suffix, e.g. RF-L, RF-M, RF-H."""
    code = sensor[0].upper() + {"frame_deletion": "F", "gaussian_noise": "G", "loss_partial": "P"}[effect]
    suffix = {"low": "L", "medium": "M", "high": "H"}[severity]
    return f"{code}-{suffix}"


def load_row_table() -> pl.DataFrame:
    df = pl.read_parquet(ROW_TABLE_PATH)
    if df.height == 0:
        raise ValueError(f"{ROW_TABLE_PATH} is empty")
    return df


def compute_sequence_coverage(row_table: pl.DataFrame) -> dict[tuple[str, str], float]:
    """{(condition, sequence): coverage_pct} = (# distinct frames present
    under this condition for this sequence) / (# frames under `original` for
    this same sequence) * 100. Per-sequence analogue of
    radar_charts.compute_condition_coverage's pooled version -- needed here
    because a box plot draws one point per sequence, so coverage must be
    checked per (condition, sequence), not per condition as a whole."""
    orig = (
        row_table.filter(pl.col("condition") == CLEAN_CONDITION)
        .group_by("sequence")
        .agg(pl.col("frame").n_unique().alias("orig_n"))
    )
    cov = row_table.group_by(["condition", "sequence"]).agg(pl.col("frame").n_unique().alias("n"))
    cov = cov.join(orig, on="sequence", how="left")
    cov = cov.with_columns((pl.col("n") / pl.col("orig_n") * 100).alias("pct"))
    return {(row["condition"], row["sequence"]): row["pct"] for row in cov.iter_rows(named=True)}


def _filter_low_coverage(
    values_by_seq: dict[str, dict[str, float]], coverage: dict[tuple[str, str], float]
) -> dict[str, list[float]]:
    """values_by_seq: {condition: {sequence: value}}. Drops (condition,
    sequence) points below COVERAGE_THRESHOLD_PCT and flattens to
    {condition: [values]} for boxplot input."""
    out: dict[str, list[float]] = {}
    for condition, seq_vals in values_by_seq.items():
        kept = [v for seq, v in seq_vals.items() if coverage.get((condition, seq), 0.0) >= COVERAGE_THRESHOLD_PCT]
        out[condition] = kept
    return out


def per_sequence_ap(row_table: pl.DataFrame, cls: str) -> dict[str, dict[str, float]]:
    """{condition: {sequence: ap}} for one class."""
    ap_table = compute_ap_grouped(row_table, ["condition", "cls", "sequence"])
    out: dict[str, dict[str, float]] = defaultdict(dict)
    for row in ap_table.filter(pl.col("cls") == cls).iter_rows(named=True):
        out[row["condition"]][row["sequence"]] = row["ap"]
    return out


def per_sequence_ate_ase(
    row_table: pl.DataFrame, cls: str
) -> tuple[dict[str, dict[str, float]], dict[str, dict[str, float]]]:
    """{condition: {sequence: mATE}}, {condition: {sequence: mASE}} for one
    class. Same formulas as build_figures.py's item8_ate_ase, grouped by
    (condition, sequence) instead of condition alone, and filtered to one
    class instead of pooling sed+bus (they have different box scales, so a
    pooled ASE/ATE would be skewed toward whichever class has more TPs)."""
    tp = row_table.filter(pl.col("is_tp") & (pl.col("cls") == cls))
    tp = tp.with_columns(
        (((pl.col("loc_x") - pl.col("gt_loc_x")) ** 2 + (pl.col("loc_z") - pl.col("gt_loc_z")) ** 2) ** 0.5).alias("ate"),
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
    agg = tp.group_by(["condition", "sequence"]).agg(
        pl.col("ate").mean().alias("mATE"), pl.col("ase").mean().alias("mASE")
    )
    ate: dict[str, dict[str, float]] = defaultdict(dict)
    ase: dict[str, dict[str, float]] = defaultdict(dict)
    for row in agg.iter_rows(named=True):
        ate[row["condition"]][row["sequence"]] = row["mATE"]
        ase[row["condition"]][row["sequence"]] = row["mASE"]
    return ate, ase


def per_sequence_mfr(row_table: pl.DataFrame) -> dict[str, dict[str, float]]:
    """{condition: {sequence: miss_rate}}. Same FN/(TP+FN) proxy as
    build_figures.py's item5, grouped by (condition, sequence)."""
    rate = row_table.group_by(["condition", "sequence"]).agg(
        pl.col("is_fn").sum().alias("fn"),
        (pl.col("is_tp") | pl.col("is_fn")).sum().alias("n_gt"),
    ).filter(pl.col("n_gt") > 0).with_columns((pl.col("fn") / pl.col("n_gt")).alias("miss_rate"))
    out: dict[str, dict[str, float]] = defaultdict(dict)
    for row in rate.iter_rows(named=True):
        out[row["condition"]][row["sequence"]] = row["miss_rate"]
    return out


MIN_SEQUENCES = 3  # below this, a box is not a meaningful distribution -- skip and report


def build_box_plot(
    metric_name: str,
    values_by_condition: dict[str, list[float]],
    clean_values: list[float],
    y_label: str,
    out_dir: Path,
) -> Path | None:
    """One box plot: x = 27 conditions in CONDITION_ORDER, y = metric value,
    box = quartiles/median/min-max whiskers of per-sequence values for that
    condition, dashed line = median of clean/`original` per-sequence values.
    Conditions with no data, or fewer than MIN_SEQUENCES surviving sequences
    after coverage filtering, are still shown on the x-axis (so spacing stays
    fixed across metrics) but with an empty slot and an '(N/A)' label instead
    of a fabricated box."""
    labels: list[str] = []
    data: list[list[float]] = []
    skipped: list[str] = []

    for sensor, effect, severity in CONDITION_ORDER:
        condition = f"{sensor}_{effect}_{severity}"
        label = _condition_label(sensor, effect, severity)
        vals = values_by_condition.get(condition, [])
        if len(vals) < MIN_SEQUENCES:
            labels.append(f"{label}\n(N/A)" if not vals else f"{label}\n(n={len(vals)})")
            data.append([])
            if vals:
                skipped.append(f"{condition} (n={len(vals)})")
            else:
                skipped.append(f"{condition} (no data)")
        else:
            labels.append(label)
            data.append(vals)

    if not any(data):
        print(f"[{metric_name}] no condition has >= {MIN_SEQUENCES} sequences of data -- skipping chart")
        return None

    fig, ax = plt.subplots(figsize=(14, 6))
    positions = list(range(1, len(labels) + 1))
    box_data = [d if d else [np.nan] for d in data]
    bp = ax.boxplot(
        box_data,
        positions=positions,
        widths=0.6,
        patch_artist=True,
        showfliers=False,
        medianprops={"color": "black", "linewidth": 1.5},
        boxprops={"facecolor": "#1f6feb", "alpha": 0.6, "edgecolor": "#1f6feb"},
        whiskerprops={"color": "#1f6feb"},
        capprops={"color": "#1f6feb"},
    )
    # Blank out boxes with no real data (nan placeholder) so they don't render as a degenerate box at 0
    for i, d in enumerate(data):
        if not d:
            bp["boxes"][i].set_visible(False)
            bp["medians"][i].set_visible(False)
            bp["whiskers"][2 * i].set_visible(False)
            bp["whiskers"][2 * i + 1].set_visible(False)
            bp["caps"][2 * i].set_visible(False)
            bp["caps"][2 * i + 1].set_visible(False)

    if clean_values:
        clean_median = float(np.median(clean_values))
        ax.axhline(clean_median, color="black", linestyle="--", linewidth=1.2, label=f"clean baseline (median, n={len(clean_values)})")
        ax.legend(fontsize=9, loc="upper right")

    ax.set_xticks(positions)
    ax.set_xticklabels(labels, fontsize=8, rotation=90)
    ax.set_xlim(0, len(labels) + 1)
    ax.set_ylabel(y_label, fontsize=11)
    ax.set_title(f"{metric_name} distribution across sequences, by corruption condition", fontsize=12)
    ax.grid(axis="y", linestyle=":", alpha=0.4)
    fig.tight_layout()

    if skipped:
        print(f"[{metric_name}] skipped/undersized conditions ({len(skipped)}): {', '.join(skipped)}")

    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"box_{metric_name.lower().replace(' ', '_').replace('(', '').replace(')', '')}"
    png_path = out_dir / f"{stem}.png"
    svg_path = out_dir / f"{stem}.svg"
    fig.savefig(png_path, dpi=150)
    fig.savefig(svg_path)
    plt.close(fig)
    return png_path


def build_all_box_plots(out_dir: Path) -> list[Path]:
    row_table = load_row_table()
    coverage = compute_sequence_coverage(row_table)

    paths: list[Path] = []

    for cls in CLASSES:
        ap_by_cond = per_sequence_ap(row_table, cls)
        clean_ap = list(ap_by_cond.get(CLEAN_CONDITION, {}).values())
        values = _filter_low_coverage(ap_by_cond, coverage)
        p = build_box_plot(f"mAP ({CLASS_LABEL[cls]})", values, clean_ap, "AP (IoU=0.3)", out_dir)
        if p:
            paths.append(p)

    for cls in CLASSES:
        ate_by_cond, ase_by_cond = per_sequence_ate_ase(row_table, cls)
        clean_ate = list(ate_by_cond.get(CLEAN_CONDITION, {}).values())
        clean_ase = list(ase_by_cond.get(CLEAN_CONDITION, {}).values())
        p = build_box_plot(f"mATE ({CLASS_LABEL[cls]})", _filter_low_coverage(ate_by_cond, coverage), clean_ate, "ATE (m)", out_dir)
        if p:
            paths.append(p)
        p = build_box_plot(f"mASE ({CLASS_LABEL[cls]})", _filter_low_coverage(ase_by_cond, coverage), clean_ase, "ASE (1 - IoU of aligned boxes)", out_dir)
        if p:
            paths.append(p)

    mfr_by_cond = per_sequence_mfr(row_table)
    clean_mfr = list(mfr_by_cond.get(CLEAN_CONDITION, {}).values())
    p = build_box_plot("mFR", _filter_low_coverage(mfr_by_cond, coverage), clean_mfr, "miss rate = FN / (TP+FN)", out_dir)
    if p:
        paths.append(p)

    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "output" / "box_plots",
        help="Directory to write PNG+SVG charts to",
    )
    args = parser.parse_args()
    paths = build_all_box_plots(args.out_dir)
    for p in paths:
        print(p)


if __name__ == "__main__":
    main()
