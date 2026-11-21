#!/usr/bin/env python3
"""Line charts of mAP / mATE / mASE vs. distance from ego, one line per
corruption condition (pooled across all sequences and both classes), plotted
against `row_table_iou03.parquet` (IoU=0.3).

`frame_deletion` conditions are excluded throughout (per user instruction,
2026-08-26) -- those Alvis runs crashed mid-sweep and are not a complete
clean run, so a distance curve built from their surviving frames would not
be comparable to the other conditions'. This mirrors radar_charts.py's
existing frame_deletion exclusion from its axis set.

Distance bins are 10m wide, 0-80m (K-Radar's row_table_iou03 range is
~0.85-75m). Per-row distance is `distance_from_ego` (pred position) for
TP/FP rows; FN rows have no prediction, so distance falls back to the GT
position (sqrt(gt_loc_x^2 + gt_loc_z^2)) -- needed because mAP's num_gt
denominator must count FN rows too, and they must land in the correct bin.

Metrics, each pooling car (`sed`) + bus classes and all sequences within a
(condition, distance_bin) cell:
  - mAP: compute_ap_grouped(["condition", "distance_bin", "cls"]) from the
    K-Radar submodule's ap_metrics.py (41-point interpolated AP, same as
    radar_charts.py/box_plots.py), averaged over whichever classes have
    num_gt > 0 in that cell.
  - mATE: mean Euclidean XZ localization error over true positives.
  - mASE: mean(1 - IoU of axis-aligned dims) over true positives.
  (Same ATE/ASE formulas as box_plots.py's per_sequence_ate_ase, pooled
  across classes here instead of split -- a single line per condition is
  the point of this chart, at the cost of the car/bus scale difference
  box_plots.py avoids.)

A bin is only plotted if it clears MIN_GT_PER_BIN (for mAP) / MIN_TP_PER_BIN
(for mATE/mASE); otherwise it's a gap in that condition's line, not a
fabricated point.

Usage as a library:
    from distance_line_charts import build_all_charts
    build_all_charts(out_dir=Path("output/distance_line_charts"))

Run standalone:
    uv run python scripts/analysis/distance_line_charts.py
"""
from __future__ import annotations

import sys
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

CLEAN_CONDITION = "original"
SENSORS = ["camera", "lidar", "radar"]
EFFECTS = ["gaussian_noise", "loss_partial"]  # frame_deletion excluded
SEVERITIES = ["low", "medium", "high"]

BIN_EDGES = list(range(0, 90, 10))  # 0,10,...,80 -> 8 bins covering the ~0-75m range
BIN_MIDPOINTS = [(BIN_EDGES[i] + BIN_EDGES[i + 1]) / 2 for i in range(len(BIN_EDGES) - 1)]
# pl.Expr.cut takes INTERIOR breakpoints (len(breaks)+1 resulting bins), unlike
# BIN_EDGES which includes both outer edges -- interior-only here so the
# resulting bin count/labels line up 1:1 with BIN_MIDPOINTS. The open-ended
# outer bins (<0m, >80m) absorb a negligible tail (row_table_iou03's range is
# ~0.85-75m) rather than being dropped.
CUT_BREAKS = BIN_EDGES[1:-1]

MIN_GT_PER_BIN = 15
MIN_TP_PER_BIN = 10

SENSOR_COLOR = {"camera": "#2ca02c", "lidar": "#e8590c", "radar": "#7b3fe4"}
# Color encodes EFFECT, not sensor: within one modality panel, the two
# effects (LG vs LL etc.) previously only differed by linestyle at the same
# sensor hue, which read as near-identical at a glance. gaussian_noise/
# loss_partial/loss_complete now get three genuinely distinct hues, reused
# identically across every sensor panel.
EFFECT_COLOR = {"gaussian_noise": "#1f77b4", "loss_partial": "#d62728", "loss_complete": "#555555"}
# Linestyle encodes SEVERITY (solid=high, dashed=medium, dotted=low), matching
# density_line_charts.py's existing convention. loss_complete has no severity
# tiers -- treated as "high" (solid), the most severe end of that condition's
# own scale. Sensor is left unencoded by color/linestyle here since every
# chart that uses this either separates sensor by panel already
# (distance_line_charts_by_modality.py, distance_robustness_charts.py) or, in
# the single combined chart below, by alpha instead.
SEVERITY_STYLE = {"low": ":", "medium": "--", "high": "-"}
SENSOR_ALPHA = {"camera": 1.0, "lidar": 0.75, "radar": 0.5}


def _conditions() -> list[tuple[str, str, str]]:
    """(condition_name, sensor, label) for every non-frame_deletion condition,
    in a fixed draw order (grouped by sensor, then effect, then severity)."""
    out: list[tuple[str, str, str]] = []
    for sensor in SENSORS:
        for effect in EFFECTS:
            for severity in SEVERITIES:
                cond = f"{sensor}_{effect}_{severity}"
                label = f"{sensor[0].upper()}{effect[0].upper()}-{severity[0].upper()}"
                out.append((cond, sensor, effect, severity, label))
        loss_complete_cond = f"{sensor}_loss_complete_zero"
        out.append((loss_complete_cond, sensor, "loss_complete", "high", f"{sensor[0].upper()}LC"))
    return out


CONDITIONS = _conditions()


def load_row_table() -> pl.DataFrame:
    df = pl.read_parquet(ROW_TABLE_PATH)
    if df.height == 0:
        raise ValueError(f"{ROW_TABLE_PATH} is empty")
    df = df.filter(~pl.col("condition").str.contains("frame_deletion"))
    # FN rows have no prediction -> distance_from_ego is null; fall back to
    # GT position so FN rows still land in a distance bin (needed for mAP's
    # num_gt denominator).
    df = df.with_columns(
        pl.when(pl.col("distance_from_ego").is_not_null())
        .then(pl.col("distance_from_ego"))
        .otherwise((pl.col("gt_loc_x") ** 2 + pl.col("gt_loc_z") ** 2) ** 0.5)
        .alias("distance")
    )
    df = df.with_columns(
        pl.col("distance").cut(CUT_BREAKS, labels=[str(i) for i in range(len(CUT_BREAKS) + 1)]).alias("distance_bin")
    )
    return df


def compute_map_by_condition_bin(row_table: pl.DataFrame) -> dict[str, dict[str, float]]:
    """{condition: {distance_bin: mAP}}, averaged over classes with num_gt > 0
    in that (condition, distance_bin) cell, only kept if the pooled num_gt
    across those classes clears MIN_GT_PER_BIN."""
    ap_table = compute_ap_grouped(row_table, ["condition", "distance_bin", "cls"])
    out: dict[str, dict[str, list[tuple[float, int]]]] = {}
    for row in ap_table.iter_rows(named=True):
        out.setdefault(row["condition"], {}).setdefault(row["distance_bin"], []).append((row["ap"], row["num_gt"]))
    result: dict[str, dict[str, float]] = {}
    for cond, bins in out.items():
        for b, ap_ngt in bins.items():
            total_gt = sum(n for _, n in ap_ngt)
            if total_gt < MIN_GT_PER_BIN:
                continue
            result.setdefault(cond, {})[b] = float(np.mean([ap for ap, _ in ap_ngt]))
    return result


def compute_ate_ase_by_condition_bin(
    row_table: pl.DataFrame,
) -> tuple[dict[str, dict[str, float]], dict[str, dict[str, float]]]:
    """{condition: {distance_bin: mATE}}, {condition: {distance_bin: mASE}},
    pooled across sed+bus, kept only if TP count clears MIN_TP_PER_BIN."""
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
    agg = tp.group_by(["condition", "distance_bin"]).agg(
        pl.col("ate").mean().alias("mATE"), pl.col("ase").mean().alias("mASE"), pl.len().alias("n_tp")
    )
    ate: dict[str, dict[str, float]] = {}
    ase: dict[str, dict[str, float]] = {}
    for row in agg.iter_rows(named=True):
        if row["n_tp"] < MIN_TP_PER_BIN:
            continue
        ate.setdefault(row["condition"], {})[row["distance_bin"]] = row["mATE"]
        ase.setdefault(row["condition"], {})[row["distance_bin"]] = row["mASE"]
    return ate, ase


def _line_style(sensor: str, effect: str, severity: str) -> dict:
    return dict(
        color=EFFECT_COLOR[effect],
        linestyle=SEVERITY_STYLE[severity],
        alpha=SENSOR_ALPHA[sensor],
        linewidth=1.6,
    )


def build_line_chart(
    metric_name: str,
    values_by_condition: dict[str, dict[str, float]],
    y_label: str,
    out_dir: Path,
) -> Path:
    fig, ax = plt.subplots(figsize=(11, 7))

    clean = values_by_condition.get(CLEAN_CONDITION, {})
    if clean:
        xs = [BIN_MIDPOINTS[int(b)] for b in sorted(clean, key=int)]
        ys = [clean[b] for b in sorted(clean, key=int)]
        ax.plot(xs, ys, color="black", linewidth=3.0, marker="o", markersize=5, label="original (clean)", zorder=5)

    for cond, sensor, effect, severity, label in CONDITIONS:
        vals = values_by_condition.get(cond, {})
        if not vals:
            continue
        xs = [BIN_MIDPOINTS[int(b)] for b in sorted(vals, key=int)]
        ys = [vals[b] for b in sorted(vals, key=int)]
        ax.plot(xs, ys, marker="o", markersize=3, label=label, zorder=3, **_line_style(sensor, effect, severity))

    ax.set_xlabel("Distance from ego (m)", fontsize=11)
    ax.set_ylabel(y_label, fontsize=11)
    ax.set_title(f"{metric_name} vs. distance from ego, by corruption condition\n(IoU=0.3, all sequences pooled, frame_deletion excluded)", fontsize=12)
    ax.grid(linestyle=":", alpha=0.4)
    ax.legend(fontsize=7, ncol=3, loc="best")
    fig.tight_layout()

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

    paths = [
        build_line_chart("mAP", map_by_cond_bin, "mAP (IoU=0.3, mean over sed+bus)", out_dir),
        build_line_chart("mATE", ate_by_cond_bin, "mATE (m)", out_dir),
        build_line_chart("mASE", ase_by_cond_bin, "mASE (1 - IoU of aligned boxes)", out_dir),
    ]
    return paths


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "output" / "distance_line_charts",
        help="Directory to write PNG+SVG charts to",
    )
    args = parser.parse_args()
    for p in build_all_charts(args.out_dir):
        print(p)


if __name__ == "__main__":
    main()
