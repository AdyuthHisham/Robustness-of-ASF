#!/usr/bin/env python3
"""Heatmaps of mAP/mATE/mASE (raw values), plus their Rb robustness-ratio
counterparts, over corruption condition, pooled across sequences and across
classes (sed, bus) -- six charts total, matching the pooled-mAP convention
used elsewhere in this analysis suite (radar_charts.py's sequence="all"
mode).

Grid layout (all six charts): rows = modality (camera/lidar/radar), columns
= `original` (highlighted clean baseline) + 6 (effect, severity) combos
(gaussian_noise/loss_partial x low/medium/high). Each (sensor, effect,
severity) triple is its own independent cell -- severity is never merged
with its siblings, e.g. camera-gaussian-low and camera-gaussian-high are two
unrelated cells. frame_deletion is excluded entirely: those runs crashed
mid-way on Alvis and aren't a complete clean run at any severity, so
including them would mix partial-coverage cells into the same grid as
complete ones.

mAP here is the textbook mean-AP: mean(AP_sed, AP_bus) per condition, not
split by class like box_plots.py/context_radar_charts.py. mATE/mASE are
pooled the same way: mean over all TP rows (both classes together), not
per-class.

The robustness-ratio heatmaps (Rb) follow asf-corruption-study-alvis.md's
definition: Rb^c = corrupted_value / original_value, per (sensor, effect,
severity) cell, against the single global `original` baseline (there's no
per-sensor clean run to ratio against). For mAP, Rb < 1 means degraded
(worse than clean); for mATE/mASE, Rb > 1 means degraded (worse than clean)
since those are lower-is-better error metrics.

Cells with <90% frame coverage vs `original` (crashed runs -- see
radar_charts.py's coverage rationale) are drawn with a hatched overlay and an
annotated coverage pct instead of silently plotting a value computed from a
handful of surviving frames.

Usage as a library:
    from heatmaps import build_all_heatmaps
    build_all_heatmaps(out_dir=Path("output/heatmaps"))

Run standalone:
    uv run python scripts/analysis/heatmaps.py
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

sys.path.insert(0, str(HERE.parent))
from radar_charts import (  # noqa: E402
    SENSORS, CLASSES, CLEAN_CONDITION, COVERAGE_THRESHOLD_PCT,
    compute_condition_coverage,
)

# frame_deletion dropped entirely -- crashed runs, not a complete clean run
# at any severity (2026-08-26).
EFFECTS = ["gaussian_noise", "loss_partial"]
SEVERITIES = ["low", "medium", "high"]
EFFECT_LABEL = {"gaussian_noise": "gauss", "loss_partial": "loss"}
SENSOR_ROW_LABEL = {"camera": "Camera", "lidar": "LiDAR", "radar": "Radar"}
SEVERITY_LABEL = {"low": "L", "medium": "M", "high": "H"}

# Column order: 2 effects x 3 severities = 6 independent (effect, severity)
# combos, grouped by effect then ascending severity.
COLUMN_ORDER = [(e, sev) for e in EFFECTS for sev in SEVERITIES]


def _column_label(effect: str, severity: str) -> str:
    return f"{EFFECT_LABEL[effect]}\n{SEVERITY_LABEL[severity]}"


def load_row_table() -> pl.DataFrame:
    df = pl.read_parquet(ROW_TABLE_PATH)
    if df.height == 0:
        raise ValueError(f"{ROW_TABLE_PATH} is empty")
    return df


def compute_map_by_condition(row_table: pl.DataFrame) -> dict[str, float]:
    """{condition: mAP} = mean(AP_sed, AP_bus), only over classes that have
    GT present for that condition (AP is None/absent otherwise)."""
    ap_table = compute_ap_grouped(row_table, ["condition", "cls"])
    by_cond: dict[str, list[float]] = {}
    for row in ap_table.iter_rows(named=True):
        if row["cls"] in CLASSES and row["ap"] is not None:
            by_cond.setdefault(row["condition"], []).append(row["ap"])
    return {cond: float(np.mean(vals)) for cond, vals in by_cond.items() if vals}


def compute_ate_ase_by_condition(row_table: pl.DataFrame) -> tuple[dict[str, float], dict[str, float]]:
    """{condition: mATE}, {condition: mASE}, pooled over both classes'
    TP rows -- same formulas as box_plots.py's per-class version, grouped by
    condition alone."""
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
    agg = tp.group_by("condition").agg(pl.col("ate").mean().alias("mATE"), pl.col("ase").mean().alias("mASE"))
    ate = {row["condition"]: row["mATE"] for row in agg.iter_rows(named=True)}
    ase = {row["condition"]: row["mASE"] for row in agg.iter_rows(named=True)}
    return ate, ase


def compute_rb(values_by_condition: dict[str, float]) -> dict[str, float]:
    """Rb^c = corrupted_value / original_value (asf-corruption-study-alvis.md
    convention), against the single global `original` baseline."""
    orig = values_by_condition.get(CLEAN_CONDITION)
    if orig is None or orig == 0:
        return {}
    return {cond: val / orig for cond, val in values_by_condition.items()}


def build_heatmap(
    metric_name: str,
    values_by_condition: dict[str, float],
    coverage_by_condition: dict[str, float],
    cmap_name: str,
    y_label: str,
    out_dir: Path,
    fmt: str | None = None,
) -> Path:
    """Grid: rows = modality (camera/lidar/radar), columns = OG (highlighted
    clean baseline, same global value repeated down every row) + 6 (effect,
    severity) combos. Cell color = metric value; a hatched '//' overlay +
    coverage-pct annotation marks cells with <90% frame coverage vs original.
    A thick black border isolates the OG column from the sweep, since it
    isn't part of it (and isn't sensor-specific)."""
    n_rows = len(SENSORS)
    n_cols = 1 + len(COLUMN_ORDER)  # OG + 6 (effect, severity) combos

    grid = np.full((n_rows, n_cols), np.nan)
    low_cov = np.zeros((n_rows, n_cols), dtype=bool)
    na = np.zeros((n_rows, n_cols), dtype=bool)

    clean_val = values_by_condition.get(CLEAN_CONDITION)
    for r in range(n_rows):
        if clean_val is None:
            na[r, 0] = True
        else:
            grid[r, 0] = clean_val

    for r, sensor in enumerate(SENSORS):
        for c, (effect, severity) in enumerate(COLUMN_ORDER, start=1):
            condition = f"{sensor}_{effect}_{severity}"
            val = values_by_condition.get(condition)
            if val is None:
                na[r, c] = True
                continue
            grid[r, c] = val
            cov_pct = coverage_by_condition.get(condition)
            if cov_pct is None or cov_pct < COVERAGE_THRESHOLD_PCT:
                low_cov[r, c] = True

    col_labels = ["original"] + [_column_label(e, sev) for e, sev in COLUMN_ORDER]
    row_labels = [SENSOR_ROW_LABEL[s] for s in SENSORS]

    fig, ax = plt.subplots(figsize=(9, 4))
    masked = np.ma.masked_invalid(grid)
    cmap = plt.get_cmap(cmap_name).copy()
    cmap.set_bad(color="#dddddd")
    im = ax.imshow(masked, cmap=cmap, aspect="auto")

    for r in range(n_rows):
        for c in range(n_cols):
            if na[r, c]:
                ax.text(c, r, "N/A", ha="center", va="center", fontsize=8, color="#555555")
                continue
            val = grid[r, c]
            text = f"{val:{fmt}}" if fmt else (f"{val:.3f}" if abs(val) < 10 else f"{val:.2f}")
            ax.text(c, r, text, ha="center", va="center", fontsize=9, color="black")
            if low_cov[r, c]:
                ax.add_patch(
                    plt.Rectangle((c - 0.5, r - 0.5), 1, 1, fill=False, hatch="//", edgecolor="#00A550", linewidth=0)
                )
                effect, severity = COLUMN_ORDER[c - 1]
                cov_pct = coverage_by_condition.get(f"{SENSORS[r]}_{effect}_{severity}")
                ax.text(c, r + 0.32, f"{cov_pct:.0f}% cov", ha="center", va="center", fontsize=6, color="#00A550")

    # Highlight the OG column: thick black border isolating it from the sweep.
    ax.add_patch(plt.Rectangle((-0.5, -0.5), 1, n_rows, fill=False, edgecolor="black", linewidth=2.5))

    ax.set_xticks(range(n_cols))
    ax.set_xticklabels(col_labels, fontsize=8.5)
    ax.set_yticks(range(n_rows))
    ax.set_yticklabels(row_labels, fontsize=10)
    ax.set_xticks(np.arange(-0.5, n_cols, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, n_rows, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.5)
    ax.tick_params(which="minor", length=0)

    cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
    cbar.set_label(y_label, fontsize=9)

    ax.set_title(
        f"{metric_name} by modality x condition (each severity independent, pooled across sequences and classes, IoU=0.3)\n"
        f"'original' column bordered = clean baseline; hatched = <{COVERAGE_THRESHOLD_PCT:.0f}% frame coverage",
        fontsize=10,
    )
    fig.tight_layout()

    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"heatmap_{metric_name.lower().replace(' ', '_').replace('(', '').replace(')', '')}"
    png_path = out_dir / f"{stem}.png"
    svg_path = out_dir / f"{stem}.svg"
    fig.savefig(png_path, dpi=150)
    fig.savefig(svg_path)
    plt.close(fig)
    return png_path


def build_all_heatmaps(out_dir: Path) -> list[Path]:
    row_table = load_row_table()
    # frame_deletion rows dropped up front -- not part of this analysis at all.
    row_table = row_table.filter(pl.col("condition").str.contains("frame_deletion").not_())
    coverage = compute_condition_coverage(row_table)

    map_vals = compute_map_by_condition(row_table)
    ate_vals, ase_vals = compute_ate_ase_by_condition(row_table)

    # coolwarm: for mAP (higher=better) coolwarm_r reads low=red/bad,
    # high=blue/good; for mATE/mASE (lower=better) plain coolwarm keeps
    # low=blue/good, high=red/bad -- red means "bad" consistently everywhere.
    paths = [
        build_heatmap("mAP", map_vals, coverage, "coolwarm_r", "AP (IoU=0.3)", out_dir),
        build_heatmap("mATE", ate_vals, coverage, "coolwarm", "ATE (m)", out_dir),
        build_heatmap("mASE", ase_vals, coverage, "coolwarm", "ASE (1 - IoU of aligned boxes)", out_dir),
    ]

    rb_map = compute_rb(map_vals)
    rb_ate = compute_rb(ate_vals)
    rb_ase = compute_rb(ase_vals)

    paths += [
        build_heatmap("Rb (mAP)", rb_map, coverage, "coolwarm_r", "Rb = corrupted AP / original AP", out_dir, fmt=".3f"),
        build_heatmap("Rb (mATE)", rb_ate, coverage, "coolwarm", "Rb = corrupted ATE / original ATE", out_dir, fmt=".3f"),
        build_heatmap("Rb (mASE)", rb_ase, coverage, "coolwarm", "Rb = corrupted ASE / original ASE", out_dir, fmt=".3f"),
    ]
    return paths


def main() -> None:
    out_dir = Path(__file__).resolve().parents[2] / "output" / "heatmaps" / "v2_official"
    paths = build_all_heatmaps(out_dir)
    for p in paths:
        print(p)


if __name__ == "__main__":
    main()
