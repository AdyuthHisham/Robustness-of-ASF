#!/usr/bin/env python3
"""Radar charts breaking mAP/mASE/mATE down by scene-context field
(time_of_day, weather, environment), overlaid per context value on the same
axis layout used by radar_charts.py (OG + 9 sensor x effect codes).

For each (metric, context_field, cls, severity) this produces one radar
chart: axes = CONDITION_CODE axes (same set/order as radar_charts.py), one
overlaid polygon per distinct value of context_field (color-coded, legend).

`environment` has 8 distinct values in row_table_iou03.parquet; overlaying
all 8 on one radar chart is unreadable, so it's restricted to the 4 most
frequent values (highway/urban/alleyway/university, ~95% of rows) via
ENVIRONMENT_VALUES below. `weather` (5 values) and `time_of_day` (2 values)
use their full value sets.

time_of_day/weather/environment are already present as columns in
row_table_iou03.parquet -- no join against the visibility parquet is needed
(confirmed by audit 2026-08-25: 0 nulls, values agree with the visibility
pipeline's own copies wherever the two overlap).

Reuses radar_charts.py's condition/axis constants and coverage-threshold
convention, and box_plots.py's ATE/ASE formulas (mean over TP rows) -- pooled
across sequences per (condition, cls, context_value), same pooling as
radar_charts.py's sequence="all" mode, since a per-sequence breakdown on top
of a context breakdown would overload a single chart.

Usage as a library:
    from context_radar_charts import build_all_context_charts
    build_all_context_charts(out_dir=(FIGURES_DIR / "context_radar_charts"))

Run standalone:
    uv run python scripts/analysis/context_radar_charts.py
"""
from __future__ import annotations

from amscup_paths import ROOT, REPORTS_DIR, FIGURES_DIR  # noqa: E402
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import polars as pl

HERE = Path(__file__).resolve()
AMSCUP_ROOT = ROOT
ROW_TABLE_PATH = REPORTS_DIR / "row_table_iou03.parquet"

from robustness.ap_metrics import compute_ap_grouped  # noqa: E402

sys.path.insert(0, str(HERE.parent))
from radar_charts import (  # noqa: E402
    SEVERITIES, CLASSES, CLASS_LABEL, CLEAN_CONDITION,
    CONDITION_CODE, AXIS_ORDER, COVERAGE_THRESHOLD_PCT,
)

# Distinct values present in row_table_iou03.parquet (audit 2026-08-25).
# environment is restricted to its 4 most frequent values -- all 8 overlaid
# on one radar chart is unreadable.
CONTEXT_FIELDS: dict[str, list[str]] = {
    "time_of_day": ["day", "night"],
    "weather": ["normal", "rain", "sleet", "fog", "overcast"],
    "environment": ["highway", "urban", "alleyway", "university"],
}

# Fixed color per context value within a field (tab10-derived), consistent
# across every chart for that field.
_TAB10 = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f"]


def _context_colors(field: str) -> dict[str, str]:
    return {v: _TAB10[i % len(_TAB10)] for i, v in enumerate(CONTEXT_FIELDS[field])}


def load_row_table() -> pl.DataFrame:
    df = pl.read_parquet(ROW_TABLE_PATH)
    if df.height == 0:
        raise ValueError(f"{ROW_TABLE_PATH} is empty")
    return df


def compute_ap_by_condition_cls_context(
    row_table: pl.DataFrame, context_field: str
) -> dict[tuple[str, str, str], float]:
    """{(condition, cls, context_value): ap}, pooled across all sequences."""
    ap_table = compute_ap_grouped(row_table, ["condition", "cls", context_field])
    return {(row["condition"], row["cls"], row[context_field]): row["ap"] for row in ap_table.iter_rows(named=True)}


def compute_ate_ase_by_condition_cls_context(
    row_table: pl.DataFrame, context_field: str
) -> tuple[dict[tuple[str, str, str], float], dict[tuple[str, str, str], float]]:
    """{(condition, cls, context_value): mATE}, {...: mASE}, pooled across
    sequences -- same formulas as box_plots.per_sequence_ate_ase, grouped by
    (condition, cls, context_field) instead of (condition, sequence)."""
    tp = row_table.filter(pl.col("is_tp"))
    tp = tp.with_columns(
        (((pl.col("loc_x") - pl.col("gt_loc_x")) ** 2 + (pl.col("loc_z") - pl.col("gt_loc_z")) ** 2) ** 0.5).alias(
            "ate"
        ),
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
    agg = tp.group_by(["condition", "cls", context_field]).agg(
        pl.col("ate").mean().alias("mATE"), pl.col("ase").mean().alias("mASE")
    )
    ate: dict[tuple[str, str, str], float] = {}
    ase: dict[tuple[str, str, str], float] = {}
    for row in agg.iter_rows(named=True):
        key = (row["condition"], row["cls"], row[context_field])
        ate[key] = row["mATE"]
        ase[key] = row["mASE"]
    return ate, ase


def compute_condition_coverage_by_context(row_table: pl.DataFrame, context_field: str) -> dict[tuple[str, str], float]:
    """{(condition, context_value): coverage_pct} -- same rationale as
    radar_charts.compute_condition_coverage, computed per context value since
    a crashed run may have skewed frame coverage differently across, e.g.,
    day vs night frames."""
    orig = (
        row_table.filter(pl.col("condition") == CLEAN_CONDITION)
        .group_by(context_field)
        .agg(pl.struct(["sequence", "frame"]).n_unique().alias("orig_n"))
    )
    cov = row_table.group_by(["condition", context_field]).agg(pl.struct(["sequence", "frame"]).n_unique().alias("n"))
    cov = cov.join(orig, on=context_field, how="left")
    cov = cov.with_columns((pl.col("n") / pl.col("orig_n") * 100).alias("pct"))
    return {(row["condition"], row[context_field]): row["pct"] for row in cov.iter_rows(named=True)}


def build_context_radar_chart(
    values_by_cond_cls_ctx: dict[tuple[str, str, str], float],
    coverage_by_cond_ctx: dict[tuple[str, str], float],
    context_field: str,
    cls: str,
    severity: str,
    ylim: float,
    y_label: str,
    metric_name: str,
    out_dir: Path,
) -> Path:
    """One radar chart: same OG + 9-axis layout as radar_charts.py, one
    overlaid polygon per distinct value of context_field. Per-series,
    low-coverage points (<90% frame coverage vs original within that same
    context value) get a hollow 'x' in the series color and are excluded from
    the connecting line -- same rule as radar_charts.py, evaluated
    per-context-value rather than pooled."""
    context_values = CONTEXT_FIELDS[context_field]
    colors = _context_colors(context_field)

    labels = [CONDITION_CODE[CLEAN_CONDITION]] + [CONDITION_CODE[(s, e)] for s, e in AXIS_ORDER]
    conditions = [CLEAN_CONDITION] + [f"{s}_{e}_{severity}" for s, e in AXIS_ORDER]
    n = len(labels)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={"projection": "polar"})
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_ylim(0, ylim)

    any_low_coverage = False
    any_na = False
    for ctx_val in context_values:
        color = colors[ctx_val]
        values = np.array(
            [values_by_cond_cls_ctx.get((cond, cls, ctx_val), np.nan) for cond in conditions], dtype=float
        )
        low_cov = np.array(
            [
                (not np.isnan(v)) and coverage_by_cond_ctx.get((cond, ctx_val), 0.0) < COVERAGE_THRESHOLD_PCT
                for cond, v in zip(conditions, values)
            ]
        )
        any_low_coverage = any_low_coverage or bool(low_cov.any())
        any_na = any_na or bool(np.isnan(values).any())

        values_closed = np.concatenate([values, values[:1]])
        angles_closed = np.array(angles + angles[:1])
        low_cov_closed = np.concatenate([low_cov, low_cov[:1]])
        present_mask = ~np.isnan(values_closed) & ~low_cov_closed

        run_start = None
        first_run = True
        for i in range(len(values_closed)):
            if present_mask[i] and run_start is None:
                run_start = i
            if (not present_mask[i] or i == len(values_closed) - 1) and run_start is not None:
                run_end = i if present_mask[i] else i
                end = run_end + (1 if present_mask[i] else 0)
                label = ctx_val if first_run else None
                ax.plot(
                    angles_closed[run_start:end],
                    values_closed[run_start:end],
                    color=color,
                    linewidth=1.5,
                    zorder=2,
                    label=label,
                )
                first_run = False
                run_start = None

        for angle, val, lc in zip(angles, values, low_cov):
            if np.isnan(val):
                continue
            if lc:
                ax.scatter([angle], [val], color=color, marker="x", s=60, linewidths=2, zorder=3)
            else:
                ax.scatter([angle], [val], color=color, marker="o", s=30, zorder=3)

    ax.set_xticks(angles)
    tick_labels = ax.set_xticklabels(labels, fontsize=9)
    for lbl, code in zip(tick_labels, [CLEAN_CONDITION] + AXIS_ORDER):
        if code == CLEAN_CONDITION:
            lbl.set_fontweight("bold")
            lbl.set_fontsize(11)

    ax.set_title(
        f"{metric_name} by condition x {context_field} -- {CLASS_LABEL[cls]}, severity={severity} (pooled, IoU=0.3)",
        fontsize=12,
        pad=20,
    )
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.1), fontsize=9, title=context_field)

    footer_bits = []
    if any_low_coverage:
        footer_bits.append(
            f"'x' = <{COVERAGE_THRESHOLD_PCT:.0f}% frame coverage vs original within that {context_field} value"
        )
    if any_na:
        footer_bits.append("gap = no data for that condition x context-value combo")
    if footer_bits:
        fig.text(0.5, 0.02, "; ".join(footer_bits), ha="center", fontsize=8, color="#555555")
    fig.tight_layout()

    out_dir.mkdir(parents=True, exist_ok=True)
    metric_stem = metric_name.lower().replace(" ", "_").replace("(", "").replace(")", "")
    stem = f"radar_{metric_stem}_{context_field}_{cls}_{severity}"
    png_path = out_dir / f"{stem}.png"
    svg_path = out_dir / f"{stem}.svg"
    fig.savefig(png_path, dpi=150, bbox_inches="tight")
    fig.savefig(svg_path, bbox_inches="tight")
    plt.close(fig)
    return png_path


def build_all_context_charts(out_dir: Path) -> list[Path]:
    """Builds every (metric, context_field, cls, severity) chart: 3 metrics x
    3 context fields x 2 classes x 3 severities = 54 charts."""
    row_table = load_row_table()
    paths: list[Path] = []

    for context_field in CONTEXT_FIELDS:
        coverage = compute_condition_coverage_by_context(row_table, context_field)

        ap_vals = compute_ap_by_condition_cls_context(row_table, context_field)
        ate_vals, ase_vals = compute_ate_ase_by_condition_cls_context(row_table, context_field)

        for cls in CLASSES:
            ap_cls_vals = [v for (_, c, _), v in ap_vals.items() if c == cls]
            ap_ylim = max(ap_cls_vals) * 1.1 if ap_cls_vals else 100.0
            ate_cls_vals = [v for (_, c, _), v in ate_vals.items() if c == cls]
            ate_ylim = max(ate_cls_vals) * 1.1 if ate_cls_vals else 5.0
            ase_cls_vals = [v for (_, c, _), v in ase_vals.items() if c == cls]
            ase_ylim = max(ase_cls_vals) * 1.1 if ase_cls_vals else 1.0

            for severity in SEVERITIES:
                paths.append(
                    build_context_radar_chart(
                        ap_vals, coverage, context_field, cls, severity, ap_ylim,
                        "AP (IoU=0.3)", f"mAP ({CLASS_LABEL[cls]})", out_dir,
                    )
                )
                paths.append(
                    build_context_radar_chart(
                        ate_vals, coverage, context_field, cls, severity, ate_ylim,
                        "ATE (m)", f"mATE ({CLASS_LABEL[cls]})", out_dir,
                    )
                )
                paths.append(
                    build_context_radar_chart(
                        ase_vals, coverage, context_field, cls, severity, ase_ylim,
                        "ASE (1 - IoU of aligned boxes)", f"mASE ({CLASS_LABEL[cls]})", out_dir,
                    )
                )
    return paths


def main() -> None:
    out_dir = FIGURES_DIR / "context_radar_charts" / "v2_official"
    paths = build_all_context_charts(out_dir)
    for p in paths:
        print(p)


if __name__ == "__main__":
    main()
