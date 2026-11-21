#!/usr/bin/env python3
"""Dumbbell plots of mAP / mATE / mASE at near vs. far range, one row per
corruption condition, sorted by |far - near|.

Same underlying data and metric formulas as distance_line_charts.py (reused
directly, not reimplemented) -- this just trades the line chart's full
7-bin trajectory for a near/far comparison that's actually readable at 21+
conditions: a line chart needs 21 distinguishable color x dash-style
combinations (already exhausted here -- LLC/RLC visually blur into LL-H/RL-H
in the line chart), and comparing two lines still means finding both among
the pack and eyeballing the vertical gap by hand. A dumbbell needs 2 marker
colors total (near/far), reused identically on every row, and the near-far
gap is a literal segment length you read straight off a y-axis that's
already sorted by degradation magnitude -- no color discrimination problem,
scales to more conditions as more rows rather than more colors.

Traded away: the mid-range shape (e.g. a condition that dips at 25m and
partially recovers by 45m before falling off past 55m) collapses to two
points. Use distance_line_charts.py when that trajectory detail matters.

near = distance bin 0 (0-10m), far = distance bin 7 (70-80m) -- the two
extreme bins already computed by distance_line_charts.py's per-bin
aggregation (pooled across all sequences and both classes, MIN_GT_PER_BIN /
MIN_TP_PER_BIN filtering still applies). frame_deletion excluded, same as
distance_line_charts.py. `original` is included as its own row, styled
distinctly (bold label) rather than as a separate reference line -- so its
near-far delta is directly comparable to every corruption's.

Usage as a library:
    from distance_dumbbell_charts import build_all_charts
    build_all_charts(out_dir=Path("output/distance_dumbbell_charts"))

Run standalone:
    uv run python scripts/analysis/distance_dumbbell_charts.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from distance_line_charts import (
    CLEAN_CONDITION,
    CONDITIONS,
    compute_ate_ase_by_condition_bin,
    compute_map_by_condition_bin,
    load_row_table,
)

NEAR_BIN = "0"  # 0-10m
FAR_BIN = "7"  # 70-80m

NEAR_COLOR = "#4c72b0"
FAR_COLOR = "#c44e52"


def _condition_label(cond: str) -> str:
    if cond == CLEAN_CONDITION:
        return "original (clean)"
    for c, sensor, effect, severity, label in CONDITIONS:
        if c == cond:
            return label
    return cond


def build_dumbbell_chart(
    metric_name: str,
    values_by_condition: dict[str, dict[str, float]],
    x_label: str,
    out_dir: Path,
    higher_is_better: bool,
) -> Path | None:
    """values_by_condition: {condition: {distance_bin: value}}. Rows are every
    condition with data at BOTH NEAR_BIN and FAR_BIN (near-only or far-only
    conditions are skipped and reported -- a dumbbell needs both ends), sorted
    by |far - near| descending so the worst near/far divergence is at top."""
    rows: list[tuple[str, float, float]] = []
    skipped: list[str] = []
    all_conditions = [CLEAN_CONDITION] + [c for c, *_ in CONDITIONS]
    for cond in all_conditions:
        vals = values_by_condition.get(cond, {})
        if NEAR_BIN not in vals or FAR_BIN not in vals:
            skipped.append(cond)
            continue
        rows.append((cond, vals[NEAR_BIN], vals[FAR_BIN]))

    if not rows:
        print(f"[{metric_name}] no condition has data at both near and far bins -- skipping chart")
        return None

    rows.sort(key=lambda r: abs(r[2] - r[1]), reverse=True)

    fig, ax = plt.subplots(figsize=(9, 0.32 * len(rows) + 1.5))
    y_positions = list(range(len(rows), 0, -1))  # top row = biggest |delta|

    for y, (cond, near, far) in zip(y_positions, rows):
        is_clean = cond == CLEAN_CONDITION
        ax.plot([near, far], [y, y], color="#999999", linewidth=1.2, zorder=1)
        ax.scatter([near], [y], color=NEAR_COLOR, s=45 if not is_clean else 70, zorder=3, edgecolor="black" if is_clean else "none", linewidth=1.2)
        ax.scatter([far], [y], color=FAR_COLOR, s=45 if not is_clean else 70, zorder=3, edgecolor="black" if is_clean else "none", linewidth=1.2)

    ax.set_yticks(y_positions)
    labels = [_condition_label(cond) for cond, _, _ in rows]
    ax.set_yticklabels(labels, fontsize=9)
    for tick, (cond, _, _) in zip(ax.get_yticklabels(), rows):
        if cond == CLEAN_CONDITION:
            tick.set_fontweight("bold")

    ax.scatter([], [], color=NEAR_COLOR, label="near (0-10m)")
    ax.scatter([], [], color=FAR_COLOR, label="far (70-80m)")
    ax.legend(fontsize=9, loc="lower right" if higher_is_better else "upper right")

    ax.set_xlabel(x_label, fontsize=11)
    ax.set_ylim(0.3, len(rows) + 0.7)
    ax.set_title(
        f"{metric_name}: near (0-10m) vs. far (70-80m), by corruption condition\n"
        "(IoU=0.3, all sequences pooled, frame_deletion excluded, sorted by |far - near|)",
        fontsize=12,
    )
    ax.grid(axis="x", linestyle=":", alpha=0.4)
    fig.tight_layout()

    if skipped:
        print(f"[{metric_name}] skipped (missing near or far bin data): {', '.join(skipped)}")

    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"dumbbell_{metric_name.lower()}"
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

    paths = []
    p = build_dumbbell_chart("mAP", map_by_cond_bin, "mAP (IoU=0.3, mean over sed+bus)", out_dir, higher_is_better=True)
    if p:
        paths.append(p)
    p = build_dumbbell_chart("mATE", ate_by_cond_bin, "mATE (m)", out_dir, higher_is_better=False)
    if p:
        paths.append(p)
    p = build_dumbbell_chart("mASE", ase_by_cond_bin, "mASE (1 - IoU of aligned boxes)", out_dir, higher_is_better=False)
    if p:
        paths.append(p)
    return paths


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "output" / "distance_dumbbell_charts",
        help="Directory to write PNG+SVG charts to",
    )
    args = parser.parse_args()
    for p in build_all_charts(args.out_dir):
        print(p)


if __name__ == "__main__":
    main()
