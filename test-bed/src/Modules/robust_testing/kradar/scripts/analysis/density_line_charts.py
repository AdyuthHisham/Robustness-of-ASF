#!/usr/bin/env python3
"""Line charts of mAP, mATE, mASE vs. per-frame GT object density, one panel
per sensor modality (camera/lidar/radar), one line per (effect, severity)
within each panel -- severities NOT pooled -- plus `original` bolded as the
clean reference in every panel.

frame_deletion is excluded: its runs have incomplete/crashed frame coverage
on Alvis (see radar_charts.py's coverage rationale), so it is not a clean
apples-to-apples corruption sweep like gaussian_noise/loss_partial.

Density bins are the same GT-object-count terciles/buckets as
build_item2_density.py: derived from `original`'s per-(sequence,frame) GT
count (condition-independent), binned into 1-2/3-4/5-7/8-12/13+ objects.

mAP is averaged over classes (sed, bus) per (condition, density_bin), via
`compute_ap_grouped` (K-Radar's own 41-point AP, ported from
eval_revised.py) -- not reimplemented here. mATE/mASE pool both classes'
true positives per (condition, density_bin), same formulas as
box_plots.py's per_sequence_ate_ase.

Usage as a library:
    from density_line_charts import build_all_density_line_charts
    build_all_density_line_charts(out_dir=Path("output/density_line_charts"))

Run standalone:
    uv run python scripts/analysis/density_line_charts.py
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import polars as pl

HERE = Path(__file__).resolve()
AMSCUP_ROOT = HERE.parents[7]
AP_METRICS_DIR = AMSCUP_ROOT / "repos" / "K-Radar" / "scripts" / "alvis"
ROW_TABLE_PATH = AMSCUP_ROOT / "repos" / "K-Radar" / "outputs" / "robustness_reports" / "row_table_iou03.parquet"

sys.path.insert(0, str(AP_METRICS_DIR))
from ap_metrics import compute_ap_grouped  # noqa: E402

SENSORS = ["camera", "lidar", "radar"]
EFFECTS = ["gaussian_noise", "loss_partial"]  # frame_deletion excluded -- see module docstring
SEVERITIES = ["low", "medium", "high"]
CLASSES = ["sed", "bus"]
CLEAN_CONDITION = "original"

DENSITY_BIN_EDGES = [2, 4, 7, 12]
DENSITY_BIN_LABELS = ["1-2", "3-4", "5-7", "8-12", "13+"]

CONDITIONS = [
    f"{sensor}_{effect}_{severity}" for sensor in SENSORS for effect in EFFECTS for severity in SEVERITIES
]
CONDITION_LABEL = {
    f"{sensor}_{effect}_{severity}": (
        f"{sensor[0].upper()}{'G' if effect == 'gaussian_noise' else 'P'}-{severity[0].upper()}"
    )
    for sensor in SENSORS
    for effect in EFFECTS
    for severity in SEVERITIES
}
# Color by (sensor, effect); linestyle by severity, so the 18 lines stay
# readable -- same corruption's severities share a color, distinguished by
# dash pattern (low=dotted -> high=solid).
_SENSOR_EFFECT_COLOR = {
    (sensor, effect): color
    for (sensor, effect), color in zip(
        [(s, e) for s in SENSORS for e in EFFECTS],
        ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"],
    )
}
CONDITION_COLOR = {
    f"{sensor}_{effect}_{severity}": _SENSOR_EFFECT_COLOR[(sensor, effect)]
    for sensor in SENSORS
    for effect in EFFECTS
    for severity in SEVERITIES
}
SEVERITY_LINESTYLE = {"low": ":", "medium": "--", "high": "-"}


def load_row_table() -> pl.DataFrame:
    df = pl.read_parquet(ROW_TABLE_PATH)
    if df.height == 0:
        raise ValueError(f"{ROW_TABLE_PATH} is empty")
    return df


def add_density_bin(row_table: pl.DataFrame) -> pl.DataFrame:
    """Joins each row against `original`'s per-(sequence, frame) GT object
    count and bins it. Condition-independent (uses `original` frame/GT
    layout for every condition), matching build_item2_density.py."""
    gt_count = (
        row_table.filter(pl.col("condition") == CLEAN_CONDITION)
        .filter(pl.col("is_tp") | pl.col("is_fn"))
        .group_by(["sequence", "frame"])
        .agg(pl.len().alias("n_gt_objects"))
    )
    out = row_table.join(gt_count, on=["sequence", "frame"], how="inner")
    out = out.with_columns(
        pl.col("n_gt_objects").cut(DENSITY_BIN_EDGES, labels=DENSITY_BIN_LABELS).alias("density_bin")
    )
    return out


def compute_map_by_density(row_table: pl.DataFrame) -> dict[str, dict[str, float]]:
    """{condition: {density_bin: mAP}}, mAP = mean AP over classes, one
    entry per full (sensor, effect, severity) condition plus `original` --
    no severity pooling."""
    ap = compute_ap_grouped(row_table, ["condition", "cls", "density_bin"])
    ap = ap.group_by(["condition", "density_bin"]).agg(pl.col("ap").mean().alias("map"))

    out: dict[str, dict[str, float]] = {}
    for condition in [CLEAN_CONDITION, *CONDITIONS]:
        sub = ap.filter(pl.col("condition") == condition)
        out[condition] = {row["density_bin"]: row["map"] for row in sub.iter_rows(named=True)}
    return out


def compute_ate_ase_by_density(row_table: pl.DataFrame) -> tuple[dict[str, dict[str, float]], dict[str, dict[str, float]]]:
    """{condition: {density_bin: mATE}}, same for mASE. Pools both classes'
    true positives, same formulas as box_plots.py's per_sequence_ate_ase.
    One entry per full condition -- no severity pooling."""
    tp = row_table.filter(pl.col("is_tp"))
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
    agg = tp.group_by(["condition", "density_bin"]).agg(
        pl.col("ate").mean().alias("mATE"), pl.col("ase").mean().alias("mASE")
    )

    ate: dict[str, dict[str, float]] = {}
    ase: dict[str, dict[str, float]] = {}
    for condition in [CLEAN_CONDITION, *CONDITIONS]:
        sub = agg.filter(pl.col("condition") == condition)
        ate[condition] = {row["density_bin"]: row["mATE"] for row in sub.iter_rows(named=True)}
        ase[condition] = {row["density_bin"]: row["mASE"] for row in sub.iter_rows(named=True)}

    return ate, ase


def plot_line_chart_by_modality(
    metric_name: str,
    values_by_line: dict[str, dict[str, float]],
    y_label: str,
    out_dir: Path,
) -> Path:
    """One panel per sensor modality (camera/lidar/radar), each with its own
    effect x severity lines (2 effects x 3 severities = 6 lines) plus the
    shared `original` clean reference bolded in every panel -- so a
    modality's corruption behavior can be read without the other two
    modalities' lines cluttering it."""
    x = list(range(len(DENSITY_BIN_LABELS)))
    fig, axes = plt.subplots(1, len(SENSORS), figsize=(15, 5.5), sharey=True)

    orig_vals = values_by_line.get(CLEAN_CONDITION, {})
    orig_y = [orig_vals.get(label) for label in DENSITY_BIN_LABELS]
    orig_xi = [xi for xi, yi in zip(x, orig_y) if yi is not None]
    orig_yi = [yi for yi in orig_y if yi is not None]

    for ax, sensor in zip(axes, SENSORS):
        for effect in EFFECTS:
            for severity in SEVERITIES:
                condition = f"{sensor}_{effect}_{severity}"
                vals_by_bin = values_by_line.get(condition, {})
                y = [vals_by_bin.get(label) for label in DENSITY_BIN_LABELS]
                xi = [xi for xi, yi in zip(x, y) if yi is not None]
                yi = [yi for yi in y if yi is not None]
                if not yi:
                    continue
                ax.plot(
                    xi, yi, marker="o", markersize=4, linewidth=1.5, alpha=0.85,
                    color=CONDITION_COLOR[condition], linestyle=SEVERITY_LINESTYLE[severity],
                    label=CONDITION_LABEL[condition],
                )
        ax.plot(orig_xi, orig_yi, marker="o", linewidth=3.0, color="black", label="original (clean)")
        ax.set_xticks(x)
        ax.set_xticklabels(DENSITY_BIN_LABELS)
        ax.set_xlabel("GT objects in frame (density bin)")
        ax.set_title(sensor)
        ax.grid(axis="y", linestyle=":", alpha=0.4)
        ax.legend(fontsize=7, loc="best")

    axes[0].set_ylabel(y_label)
    fig.suptitle(f"{metric_name} vs. frame density, one panel per modality (severity shown per line)")
    fig.tight_layout()

    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"line_{metric_name.lower()}"
    png_path = out_dir / f"{stem}.png"
    svg_path = out_dir / f"{stem}.svg"
    fig.savefig(png_path, dpi=150)
    fig.savefig(svg_path)
    plt.close(fig)
    return png_path


def build_all_density_line_charts(out_dir: Path) -> list[Path]:
    row_table = load_row_table()
    row_table = add_density_bin(row_table)

    map_by_density = compute_map_by_density(row_table)
    ate_by_density, ase_by_density = compute_ate_ase_by_density(row_table)

    paths = [
        plot_line_chart_by_modality("mAP", map_by_density, "AP (IoU=0.3), mean over sed+bus", out_dir),
        plot_line_chart_by_modality("mATE", ate_by_density, "ATE (m)", out_dir),
        plot_line_chart_by_modality("mASE", ase_by_density, "ASE (1 - IoU of aligned boxes)", out_dir),
    ]
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "output" / "density_line_charts",
        help="Directory to write PNG+SVG charts to",
    )
    args = parser.parse_args()
    paths = build_all_density_line_charts(args.out_dir)
    for p in paths:
        print(p)


if __name__ == "__main__":
    main()
