#!/usr/bin/env python3
"""Line charts of the Rb robustness ratio (Rb^c = corrupted_metric /
clean_metric, per compute_robustness.py's definition -- see
obsidianVault/Knowledge/robustness-metric-selection.md) vs. per-frame GT
object density, for mAP, mATE, mASE. One panel per sensor modality
(camera/lidar/radar), one line per (effect, severity) within each panel.

Rb=1.0 (dashed reference line) is the clean baseline in every panel --
there is no separate bolded "original" line here (original/original = 1.0
identically, not an interesting line to draw). For mAP, Rb<1 means the
corruption hurt detection (lower is worse); for mATE/mASE (error metrics),
Rb>1 means the corruption hurt localization/size fit (higher is worse) --
the two families read in opposite directions along the same axis, so
compare each metric's panel to its own Rb=1 line, not across metrics.

Each metric's chart auto-scales its own y-axis (matplotlib default) --
mAP/mATE/mASE are not forced onto a shared range, since mAP's much larger
swings would otherwise flatten mATE/mASE's smaller-magnitude variation.

Reuses density_line_charts.py's data loading, density binning, and
mAP/mATE/mASE computation (same row_table_iou03.parquet, same
frame_deletion exclusion, same density bins) -- just divides each
corrupted condition's per-(density_bin) value by `original`'s value in
the same bin.

Usage as a library:
    from robustness_line_charts import build_all_robustness_line_charts
    build_all_robustness_line_charts(out_dir=Path("output/robustness_line_charts"))

Run standalone:
    uv run python scripts/analysis/robustness_line_charts.py
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from density_line_charts import (
    CLEAN_CONDITION,
    CONDITION_COLOR,
    CONDITION_LABEL,
    DENSITY_BIN_LABELS,
    EFFECTS,
    SENSORS,
    SEVERITIES,
    SEVERITY_LINESTYLE,
    add_density_bin,
    compute_ate_ase_by_density,
    compute_map_by_density,
    load_row_table,
)


def compute_rb(values_by_condition: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
    """{condition: {density_bin: Rb}} = corrupted_value / clean_value in the
    same density bin. Omits (condition, density_bin) cells where either side
    is missing or the clean value is 0 (undefined ratio), rather than
    fabricating a 0 or inf."""
    clean = values_by_condition.get(CLEAN_CONDITION, {})
    out: dict[str, dict[str, float]] = {}
    for condition, vals_by_bin in values_by_condition.items():
        if condition == CLEAN_CONDITION:
            continue
        rb_by_bin = {}
        for density_bin, clean_val in clean.items():
            corrupted_val = vals_by_bin.get(density_bin)
            if corrupted_val is None or clean_val is None or clean_val == 0:
                continue
            rb_by_bin[density_bin] = corrupted_val / clean_val
        out[condition] = rb_by_bin
    return out


def plot_rb_by_modality(
    metric_name: str,
    rb_by_condition: dict[str, dict[str, float]],
    out_dir: Path,
) -> Path:
    x = list(range(len(DENSITY_BIN_LABELS)))
    fig, axes = plt.subplots(1, len(SENSORS), figsize=(15, 5.5), sharey=True)

    for ax, sensor in zip(axes, SENSORS):
        for effect in EFFECTS:
            for severity in SEVERITIES:
                condition = f"{sensor}_{effect}_{severity}"
                vals_by_bin = rb_by_condition.get(condition, {})
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
        ax.axhline(1.0, color="black", linestyle="--", linewidth=1.2, label="Rb=1 (clean baseline)")
        ax.set_xticks(x)
        ax.set_xticklabels(DENSITY_BIN_LABELS)
        ax.set_xlabel("GT objects in frame (density bin)")
        ax.set_title(sensor)
        ax.grid(axis="y", linestyle=":", alpha=0.4)
        ax.legend(fontsize=7, loc="best")

    direction_note = "lower = worse" if metric_name == "mAP" else "higher = worse"
    axes[0].set_ylabel(f"Rb ({metric_name}) = corrupted / clean")
    fig.suptitle(f"Robustness ratio Rb ({metric_name}) vs. frame density, one panel per modality ({direction_note})")
    fig.tight_layout()

    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"rb_{metric_name.lower()}"
    png_path = out_dir / f"{stem}.png"
    svg_path = out_dir / f"{stem}.svg"
    fig.savefig(png_path, dpi=150)
    fig.savefig(svg_path)
    plt.close(fig)
    return png_path


def build_all_robustness_line_charts(out_dir: Path) -> list[Path]:
    row_table = load_row_table()
    row_table = add_density_bin(row_table)

    map_by_density = compute_map_by_density(row_table)
    ate_by_density, ase_by_density = compute_ate_ase_by_density(row_table)

    return [
        plot_rb_by_modality("mAP", compute_rb(map_by_density), out_dir),
        plot_rb_by_modality("mATE", compute_rb(ate_by_density), out_dir),
        plot_rb_by_modality("mASE", compute_rb(ase_by_density), out_dir),
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "output" / "robustness_line_charts",
        help="Directory to write PNG+SVG charts to",
    )
    args = parser.parse_args()
    paths = build_all_robustness_line_charts(args.out_dir)
    for p in paths:
        print(p)


if __name__ == "__main__":
    main()
