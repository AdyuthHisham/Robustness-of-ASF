#!/usr/bin/env python3
"""Line charts of the Rb robustness ratio (Gao et al.; == RR/mRR/RS -- see
[[robustness-metric-selection]]) vs. distance from ego, applied to each of
mAP / mATE / mASE, one line per corruption condition.

Rb^c = corrupted_value / clean_value, computed per (condition, distance_bin)
directly from distance_line_charts.py's already-computed per-bin metric
tables (not reimplemented) -- clean_value is `original`'s value in that same
distance bin, so this is self-relative normalization, no second baseline
model (per the note's central finding: mCE/CD/RRS all need a second
architecture and aren't computable here; Rb/RR/RS need only the model's own
clean run).

Direction of "better" is metric-dependent and NOT flipped here: mAP is
higher-is-better, so Rb_mAP > 1 would mean corruption improved detection
(essentially never observed; Rb_mAP < 1 means degradation, 0 = total
collapse). mATE/mASE are error metrics (lower-is-better), so Rb_mATE/mASE > 1
means corruption INCREASED error relative to clean -- i.e. for these two,
"worse" is above the y=1 line, not below it. Each chart's y=1 reference line
is `original` (trivially Rb=1 against itself) and is labeled accordingly.

Same condition set/styling/exclusions as distance_line_charts.py:
frame_deletion excluded, MIN_GT_PER_BIN/MIN_TP_PER_BIN filtering carried over
from amscup_paths import FIGURES_DIR  # noqa: E402
from the underlying per-bin tables, color=sensor/linestyle=effect/alpha=severity.

One figure per metric, three side-by-side panels (camera/lidar/radar)
sharing a y-axis, matching distance_line_charts_by_modality.py's layout
(and this project's existing density_line_charts.py convention) rather than
21 conditions on one axis.

Usage as a library:
    from distance_robustness_charts import build_all_charts
    build_all_charts(out_dir=(FIGURES_DIR / "distance_robustness_charts"))

Run standalone:
    uv run python scripts/analysis/distance_robustness_charts.py
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


def compute_rb(values_by_condition: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
    """{condition: {distance_bin: Rb}} = value[condition][bin] / value[original][bin],
    for every (condition, bin) where both the corrupted and the original value
    exist in that bin. `original` itself maps to a constant 1.0 in every bin
    it has data for (Rb against itself), included as the y=1 reference row."""
    clean = values_by_condition.get(CLEAN_CONDITION, {})
    out: dict[str, dict[str, float]] = {}
    for cond, bins in values_by_condition.items():
        for b, v in bins.items():
            if b not in clean or clean[b] == 0:
                continue
            out.setdefault(cond, {})[b] = v / clean[b]
    return out


def _plot_panel(ax, modality: str, rb_by_condition: dict[str, dict[str, float]]) -> None:
    ax.axhline(1.0, color="black", linewidth=3.0, label="original (Rb = 1)", zorder=5)

    for cond, sensor, effect, severity, label in CONDITIONS:
        if sensor != modality:
            continue
        vals = rb_by_condition.get(cond, {})
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
    rb_by_condition: dict[str, dict[str, float]],
    higher_is_worse: bool,
    out_dir: Path,
) -> Path:
    fig, axes = plt.subplots(1, len(SENSORS), figsize=(6 * len(SENSORS), 6), sharey=True)

    for ax, modality in zip(axes, SENSORS):
        _plot_panel(ax, modality, rb_by_condition)

    worse_note = "above y=1 = worse (more error)" if higher_is_worse else "below y=1 = worse (less detection)"
    axes[0].set_ylabel(f"Rb ({metric_name}) = corrupted / clean", fontsize=11)
    fig.suptitle(
        f"Rb robustness ratio ({metric_name}) vs. distance from ego, one panel per modality\n"
        f"(IoU=0.3, all sequences pooled, frame_deletion excluded; {worse_note})",
        fontsize=13,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.90))

    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"rb_{metric_name.lower()}"
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
        build_combined_chart("mAP", compute_rb(map_by_cond_bin), higher_is_worse=False, out_dir=out_dir),
        build_combined_chart("mATE", compute_rb(ate_by_cond_bin), higher_is_worse=True, out_dir=out_dir),
        build_combined_chart("mASE", compute_rb(ase_by_cond_bin), higher_is_worse=True, out_dir=out_dir),
    ]


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=FIGURES_DIR / "distance_robustness_charts",
        help="Directory to write PNG+SVG charts to",
    )
    args = parser.parse_args()
    for p in build_all_charts(args.out_dir):
        print(p)


if __name__ == "__main__":
    main()
