#!/usr/bin/env python3
"""Line charts of the Rb robustness ratio (corrupted / clean, per bin) vs.
distance from ego, for mAP, mATE, and mASE, restricted to the all-zero
(complete sensor loss) conditions -- one line per sensor
(camera_loss_complete, lidar_loss_complete_zero, radar_loss_complete_zero).

Rb^c = metric(condition) / metric(original) in the same distance bin, matching
the Rb/mRb definition used elsewhere in this repo (see
obsidianVault/Knowledge/robustness-metric-selection.md): Rb=1 means no
degradation vs. clean. For mAP, Rb<1 is worse (less AP retained). For mATE
and mASE -- both error metrics where lower is better -- Rb>1 is worse (more
error than clean), so a dashed horizontal line at Rb=1 marks "no change" on
every plot rather than assuming a single "degradation direction".

Only bins where BOTH the corrupted and clean conditions cleared the parent
script's MIN_GT_PER_BIN/MIN_TP_PER_BIN gates produce a ratio point (a
bin missing on one side is dropped, not divided against a stale value).

Reuses row-table loading, binning, and metric formulas from
distance_line_charts.py -- see zero_ablation_line_charts.py for the raw
(non-ratio) version of these same three metrics.

Run standalone:
    uv run python scripts/analysis/zero_ablation_robustness_line_charts.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from distance_line_charts import (
    BIN_MIDPOINTS,
    CLEAN_CONDITION,
    compute_ate_ase_by_condition_bin,
    compute_map_by_condition_bin,
    load_row_table,
)

ZERO_CONDITIONS = [
    ("camera_loss_complete_zero", "camera", "#2ca02c"),
    ("lidar_loss_complete_zero", "lidar", "#e8590c"),
    ("radar_loss_complete_zero", "radar", "#7b3fe4"),
]


def compute_rb_by_condition_bin(values_by_condition: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
    """{condition: {distance_bin: Rb}} where Rb = metric(condition, bin) /
    metric(original, bin); only bins present on both sides."""
    clean = values_by_condition.get(CLEAN_CONDITION, {})
    result: dict[str, dict[str, float]] = {}
    for cond, sensor, _color in ZERO_CONDITIONS:
        vals = values_by_condition.get(cond, {})
        for b, v in vals.items():
            if b not in clean or clean[b] == 0:
                continue
            result.setdefault(cond, {})[b] = v / clean[b]
    return result


def build_rb_chart(metric_name: str, rb_by_condition: dict[str, dict[str, float]], out_dir: Path) -> Path:
    fig, ax = plt.subplots(figsize=(9, 6))

    ax.axhline(1.0, color="black", linewidth=1.5, linestyle="--", alpha=0.6, label="Rb = 1 (no change)", zorder=1)

    for cond, sensor, color in ZERO_CONDITIONS:
        vals = rb_by_condition.get(cond, {})
        if not vals:
            continue
        xs = [BIN_MIDPOINTS[int(b)] for b in sorted(vals, key=int)]
        ys = [vals[b] for b in sorted(vals, key=int)]
        ax.plot(xs, ys, color=color, linestyle="-", linewidth=2.0, marker="o", markersize=4, label=f"{sensor} all-zero", zorder=3)

    worse_direction = "lower Rb = worse" if metric_name == "mAP" else "higher Rb = worse"
    ax.set_xlabel("Distance from ego (m)", fontsize=11)
    ax.set_ylabel(f"Rb ({metric_name}, corrupted / clean)", fontsize=11)
    ax.set_title(
        f"Rb robustness ratio ({metric_name}) vs. distance from ego, all-zero sensor ablations\n"
        f"(IoU=0.3, all sequences pooled, frame_deletion excluded, {worse_direction})",
        fontsize=11,
    )
    ax.grid(linestyle=":", alpha=0.4)
    ax.legend(fontsize=9, loc="best")
    fig.tight_layout()

    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"zero_ablation_rb_{metric_name.lower()}"
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
        build_rb_chart("mAP", compute_rb_by_condition_bin(map_by_cond_bin), out_dir),
        build_rb_chart("mATE", compute_rb_by_condition_bin(ate_by_cond_bin), out_dir),
        build_rb_chart("mASE", compute_rb_by_condition_bin(ase_by_cond_bin), out_dir),
    ]


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "output" / "zero_ablation_robustness_line_charts",
        help="Directory to write PNG+SVG charts to",
    )
    args = parser.parse_args()
    for p in build_all_charts(args.out_dir):
        print(p)


if __name__ == "__main__":
    main()
