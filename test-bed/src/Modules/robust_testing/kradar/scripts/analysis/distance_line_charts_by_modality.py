#!/usr/bin/env python3
"""Line charts of mAP / mATE / mASE vs. distance from ego, same data and
formulas as distance_line_charts.py, but one figure per metric with three
side-by-side panels (camera / lidar / radar) sharing a y-axis, instead of
all 21 conditions crammed onto one axis or split into 9 separate files.

Rationale (per user feedback 2026-08-26): the full 21-condition line chart
needs 21 distinguishable color x dash-style combinations and already blurs
some together (LLC/RLC vs. LL-H/RL-H); a dumbbell plot fixes that but throws
away the mid-range trajectory shape; splitting into 9 separate per-modality
files loses the direct visual comparison across modalities. One figure per
metric, three panels (7 conditions each: 2 effects x 3 severities + loss_complete,
plus the shared `original` reference line, bold black in every panel), matches
this project's existing density_line_charts.py convention (one figure per
metric, one panel per modality, shared y-axis).

Usage as a library:
    from distance_line_charts_by_modality import build_all_charts
    build_all_charts(out_dir=Path("output/distance_line_charts_by_modality"))

Run standalone:
    uv run python scripts/analysis/distance_line_charts_by_modality.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from distance_line_charts import (
    BIN_MIDPOINTS,
    CLEAN_CONDITION,
    CONDITIONS,
    SENSORS,
    _line_style,
    compute_ate_ase_by_condition_bin,
    compute_map_by_condition_bin,
    load_row_table,
)


def _plot_panel(ax, modality: str, values_by_condition: dict[str, dict[str, float]]) -> None:
    clean = values_by_condition.get(CLEAN_CONDITION, {})
    if clean:
        xs = [BIN_MIDPOINTS[int(b)] for b in sorted(clean, key=int)]
        ys = [clean[b] for b in sorted(clean, key=int)]
        ax.plot(xs, ys, color="black", linewidth=3.0, marker="o", markersize=5, label="original (clean)", zorder=5)

    for cond, sensor, effect, severity, label in CONDITIONS:
        if sensor != modality:
            continue
        vals = values_by_condition.get(cond, {})
        if not vals:
            continue
        xs = [BIN_MIDPOINTS[int(b)] for b in sorted(vals, key=int)]
        ys = [vals[b] for b in sorted(vals, key=int)]
        ax.plot(xs, ys, marker="o", markersize=4, label=label, zorder=3, **_line_style(sensor, effect, severity))

    ax.set_title(modality, fontsize=13)
    ax.set_xlabel("Distance from ego (m)", fontsize=11)
    ax.grid(linestyle=":", alpha=0.4)
    ax.legend(fontsize=8, loc="best")


def build_combined_chart(
    metric_name: str,
    values_by_condition: dict[str, dict[str, float]],
    y_label: str,
    out_dir: Path,
) -> Path:
    fig, axes = plt.subplots(1, len(SENSORS), figsize=(6 * len(SENSORS), 6), sharey=True)

    for ax, modality in zip(axes, SENSORS):
        _plot_panel(ax, modality, values_by_condition)

    axes[0].set_ylabel(y_label, fontsize=11)
    fig.suptitle(
        f"{metric_name} vs. distance from ego, one panel per modality\n"
        "(IoU=0.3, all sequences pooled, frame_deletion excluded)",
        fontsize=13,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.92))

    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"distance_{metric_name.lower()}"
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

    return [
        build_combined_chart("mAP", map_by_cond_bin, "AP (IoU=0.3), mean over sed+bus", out_dir),
        build_combined_chart("mATE", ate_by_cond_bin, "ATE (m)", out_dir),
        build_combined_chart("mASE", ase_by_cond_bin, "ASE (1 - IoU of aligned boxes)", out_dir),
    ]


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "output" / "distance_line_charts_by_modality",
        help="Directory to write PNG+SVG charts to",
    )
    args = parser.parse_args()
    for p in build_all_charts(args.out_dir):
        print(p)


if __name__ == "__main__":
    main()
