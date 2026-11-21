#!/usr/bin/env python3
"""Bar charts of mAP / mATE / mASE (raw values), plus their Rb robustness-ratio
counterparts (Gao et al.; == RR/mRR/RS -- see [[robustness-metric-selection]]),
against `row_table_iou03.parquet` (IoU=0.3). mAOE is NOT included: no
orientation-error computation exists anywhere in this pipeline yet (audited
2026-08-27 -- gt_rotation_y is present in row_table but nothing consumes it),
so it's out of scope here rather than silently omitted without explanation.

Two chart families, covering the requested stratification dimensions:

1. build_severity_modality_charts(): one bar per condition (3 sensors x 2
   effects x 3 severities = 18, plus `original`), color-coded by sensor.
   Covers the severity and modality dimensions directly on the x-axis.
   frame_deletion and loss_complete are excluded, matching heatmaps.py's
   convention (frame_deletion runs crashed mid-sweep on Alvis; loss_complete
   isn't part of the core gaussian/loss_partial severity sweep used by
   radar_charts.py/heatmaps.py/box_plots.py). Coverage <90% vs `original`
   (radar_charts.compute_condition_coverage) is hatched, not silently plotted.

2. build_context_charts(): one grouped bar chart per (metric, dimension) for
   dimension in {label(cls), time_of_day, weather, environment,
   frame_density}. x-axis = heatmaps.py's 6 (sensor, effect) codes (OG + CG/
   CP/LG/LP/RG/RP), pooled across severity -- severity is already covered by
   chart family 1, so pooling here keeps the grid readable instead of
   tripling the chart count. Bars within each x position = the dimension's
   category values. No coverage hatching here: coverage is only meaningful
   per raw condition, and pooling three severities per code makes a single
   coverage number ambiguous -- flagged as a known limitation rather than
   faked.

frame_density is a new dimension (# GT objects in the frame, from `original`
condition's TP+FN rows, joined onto every condition by (sequence, frame) --
it's a scene property, invariant to corruption). Binned 1 / 2-3 / 4+ (median
GT count is 2, distribution is right-skewed up to 16 -- terciles by raw
count would leave the 4+ bin nearly empty otherwise).

Usage as a library:
    from bar_charts import build_all_bar_charts
    build_all_bar_charts(out_dir=(FIGURES_DIR / "bar_charts"))

Run standalone:
    uv run python scripts/analysis/bar_charts.py
"""
from __future__ import annotations

from amscup_paths import ROOT, REPORTS_DIR, FIGURES_DIR  # noqa: E402
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np
import polars as pl

HERE = Path(__file__).resolve()
AMSCUP_ROOT = ROOT
ROW_TABLE_PATH = REPORTS_DIR / "row_table_iou03.parquet"

from robustness.ap_metrics import compute_ap_grouped  # noqa: E402

sys.path.insert(0, str(HERE.parent))
from radar_charts import (  # noqa: E402
    SENSORS, CLASSES, CLEAN_CONDITION, COVERAGE_THRESHOLD_PCT,
    compute_condition_coverage,
)
from heatmaps import EFFECTS, SEVERITIES, EFFECT_LABEL, SEVERITY_LABEL  # noqa: E402
from box_plots import _condition_label  # noqa: E402

CLASS_LABEL = {"sed": "Car (sed)", "bus": "Bus"}
SENSOR_COLOR = {"camera": "#2ca02c", "lidar": "#e8590c", "radar": "#7b3fe4"}
OG_COLOR = "#333333"
IMPROVED_COLOR = "#1a7f37"  # positive relative change (diverging Rb charts)
DEGRADED_COLOR = "#c0392b"  # negative relative change (diverging Rb charts)

METRICS = ["mAP", "mATE", "mASE"]
HIGHER_IS_WORSE = {"mAP": False, "mATE": True, "mASE": True}
METRIC_UNIT = {"mAP": "AP (%)", "mATE": "ATE (m)", "mASE": "ASE (1 - IoU of aligned boxes)"}

DENSITY_EDGES = [1, 3]  # 2 interior breaks -> 3 bins: (-inf,1], (1,3], (3,inf)
DENSITY_LABELS = ["1", "2-3", "4+"]

# (sensor, effect) codes pooled across severity, for the context-dimension
# charts. Same two-letter scheme as radar_charts.CONDITION_CODE, no severity
# suffix since severity is pooled away here.
CODE_ORDER = [f"{s[0].upper()}{EFFECT_LABEL[e].upper()[0]}" for s in SENSORS for e in EFFECTS]
CODE_TO_SENSOR_EFFECT = {f"{s[0].upper()}{EFFECT_LABEL[e].upper()[0]}": (s, e) for s in SENSORS for e in EFFECTS}


def load_row_table() -> pl.DataFrame:
    df = pl.read_parquet(ROW_TABLE_PATH)
    if df.height == 0:
        raise ValueError(f"{ROW_TABLE_PATH} is empty")

    gt = (
        df.filter((pl.col("condition") == CLEAN_CONDITION) & (pl.col("is_tp") | pl.col("is_fn")))
        .group_by(["sequence", "frame"])
        .agg(pl.len().alias("n_objs"))
    )
    gt = gt.with_columns(
        pl.col("n_objs").cut(DENSITY_EDGES, labels=DENSITY_LABELS).alias("frame_density")
    ).select(["sequence", "frame", "frame_density"])
    df = df.join(gt, on=["sequence", "frame"], how="left")

    # keep only the core gaussian_noise/loss_partial sweep + original,
    # matching heatmaps.py's exclusion of frame_deletion (crashed runs) and
    # loss_complete (not part of the severity-tiered sweep these charts use)
    keep = (pl.col("condition") == CLEAN_CONDITION) | (
        pl.col("condition").str.contains("gaussian_noise") | pl.col("condition").str.contains("loss_partial")
    )
    return df.filter(keep)


def _pooled_map(row_table: pl.DataFrame, group_cols: list[str]) -> dict[tuple, float]:
    """{group_key: mAP} = mean(AP) over classes with GT present, for each
    group_cols cell. If group_cols already includes 'cls' (the `label`
    dimension), AP is computed per-class directly rather than averaged."""
    if "cls" in group_cols:
        ap_table = compute_ap_grouped(row_table, group_cols)
        out: dict[tuple, float] = {}
        for row in ap_table.iter_rows(named=True):
            if row["ap"] is not None:
                out[tuple(row[c] for c in group_cols)] = float(row["ap"])
        return out
    ap_table = compute_ap_grouped(row_table, group_cols + ["cls"])
    by_key: dict[tuple, list[float]] = {}
    for row in ap_table.iter_rows(named=True):
        if row["cls"] in CLASSES and row["ap"] is not None:
            key = tuple(row[c] for c in group_cols)
            by_key.setdefault(key, []).append(row["ap"])
    return {k: float(np.mean(v)) for k, v in by_key.items() if v}


def _pooled_ate_ase(row_table: pl.DataFrame, group_cols: list[str]) -> tuple[dict[tuple, float], dict[tuple, float]]:
    """{group_key: mATE}, {group_key: mASE}, pooled over TP rows of both
    classes -- same formulas as heatmaps.compute_ate_ase_by_condition."""
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
    agg = tp.group_by(group_cols).agg(pl.col("ate").mean().alias("mATE"), pl.col("ase").mean().alias("mASE"))
    ate, ase = {}, {}
    for row in agg.iter_rows(named=True):
        key = tuple(row[c] for c in group_cols)
        ate[key] = row["mATE"]
        ase[key] = row["mASE"]
    return ate, ase


def compute_metric_by(row_table: pl.DataFrame, metric: str, group_cols: list[str]) -> dict[tuple, float]:
    if metric == "mAP":
        return _pooled_map(row_table, group_cols)
    ate, ase = _pooled_ate_ase(row_table, group_cols)
    return ate if metric == "mATE" else ase


def compute_rb(values: dict[tuple, float], clean_key_fn) -> dict[tuple, float]:
    """Rb^c = corrupted_value / clean_value (Gao et al. RR/mRR/RS), keyed by
    the same group_key tuples as `values`. clean_key_fn(key) -> the matching
    `original`-condition key to divide by; entries with no clean counterpart
    (or clean == 0) are dropped, not fabricated."""
    out = {}
    for key, v in values.items():
        clean_key = clean_key_fn(key)
        clean_v = values.get(clean_key)
        if clean_v is None or clean_v == 0:
            continue
        out[key] = v / clean_v
    return out


def rb_to_signed_pct_change(rb: dict[tuple, float], metric: str) -> dict[tuple, float]:
    """Re-expresses Rb as a signed % change with a metric-independent sign
    convention: positive = improvement vs. clean, negative = degradation --
    regardless of whether the underlying metric is higher-is-better (mAP) or
    lower-is-better (mATE/mASE). For mAP, Rb>1 already means "better", so
    signed = (Rb-1)*100. For mATE/mASE, Rb>1 means MORE error (worse), so the
    sign is flipped: signed = (1-Rb)*100. This is Rb re-expressed, not a
    separate metric -- values are algebraically equivalent, just centered at
    0 instead of 1 and sign-normalized for a diverging bar chart."""
    if HIGHER_IS_WORSE[metric]:
        return {k: (1.0 - v) * 100.0 for k, v in rb.items()}
    return {k: (v - 1.0) * 100.0 for k, v in rb.items()}


SYMLOG_LINTHRESH = 1.0  # % change below which the axis stays linear


def _apply_symlog(ax, values: list[float]) -> None:
    """Symmetric-log y-scale for diverging Rb charts: linear near 0 (so
    small changes like CG-L's ~0.5% aren't squashed to invisible slivers by
    a large outlier like LG-H's ~-78%), logarithmic beyond SYMLOG_LINTHRESH.
    No-ops if every value already fits inside the linear region -- symlog
    only helps when there's an order-of-magnitude spread to compress."""
    if not values or max(abs(v) for v in values) <= SYMLOG_LINTHRESH * 3:
        return
    ax.set_yscale("symlog", linthresh=SYMLOG_LINTHRESH, linscale=1.5)
    ax.yaxis.set_minor_locator(matplotlib.ticker.NullLocator())


MIN_VISIBLE_PCT = 0.05  # floor for diverging-bar rendering, see _floor_for_visibility


def _floor_for_visibility(true_heights: list[float]) -> tuple[list[float], list[bool]]:
    """A true value under MIN_VISIBLE_PCT (e.g. LL/night's mAP change of
    -0.011%) draws as a sub-pixel sliver even under symlog -- not a data gap,
    just genuinely negligible, but visually indistinguishable from "no bar
    drawn". Floors the DRAWN height's magnitude to MIN_VISIBLE_PCT (sign
    preserved) so every real value gets a visible bar; the true value is
    annotated as text by the caller rather than silently overstating the
    bar's length. Returns (drawn_heights, was_floored)."""
    drawn, floored = [], []
    for h in true_heights:
        if 0 < abs(h) < MIN_VISIBLE_PCT:
            drawn.append(MIN_VISIBLE_PCT if h > 0 else -MIN_VISIBLE_PCT)
            floored.append(True)
        else:
            drawn.append(h)
            floored.append(False)
    return drawn, floored


def _annotate_floored_bars(ax, bars, true_heights: list[float], floored: list[bool]) -> None:
    for bar, true_v, was_floored in zip(bars, true_heights, floored):
        if not was_floored:
            continue
        y = bar.get_height()
        va = "bottom" if y >= 0 else "top"
        ax.text(bar.get_x() + bar.get_width() / 2, y, f"{true_v:+.3f}%", ha="center", va=va, fontsize=6, rotation=90)


def build_severity_modality_chart(
    metric: str, values: dict[tuple, float], coverage: dict[str, float], rb: bool, out_dir: Path
) -> Path:
    # Rb charts drop OG entirely: OG is trivially Rb=1 (dividing by itself),
    # not an informative bar -- shown instead as the y=1 reference line below.
    condition_rows = [(CLEAN_CONDITION, CLEAN_CONDITION, None)] if not rb else []
    condition_rows += [
        (_condition_label(sensor, effect, severity), f"{sensor}_{effect}_{severity}", sensor)
        for sensor in SENSORS
        for effect in EFFECTS
        for severity in SEVERITIES
    ]

    labels, heights, colors, hatches = [], [], [], []
    for cond_label, cond, sensor in condition_rows:
        v = values.get((cond,))
        if v is None:
            continue
        labels.append("OG" if cond == CLEAN_CONDITION else cond_label)
        heights.append(v)
        if rb:
            colors.append(IMPROVED_COLOR if v >= 0 else DEGRADED_COLOR)
        else:
            colors.append(OG_COLOR if sensor is None else SENSOR_COLOR[sensor])
        cov = coverage.get(cond, 100.0)
        hatches.append("///" if cov < COVERAGE_THRESHOLD_PCT else "")

    drawn_heights = heights
    floored = [False] * len(heights)
    if rb:
        drawn_heights, floored = _floor_for_visibility(heights)

    fig, ax = plt.subplots(figsize=(max(10, len(labels) * 0.5), 5.5))
    bars = ax.bar(labels, drawn_heights, color=colors)
    for bar, hatch in zip(bars, hatches):
        bar.set_hatch(hatch)
        if hatch:
            bar.set_edgecolor("darkorange")
    if rb:
        # Diverging bar chart: 0 = no change vs. clean, bars extend up
        # (positive = improved) or down (negative = degraded). ylim is
        # symmetric around 0 so the zero-line sits at the vertical center of
        # the plot regardless of which direction dominates.
        ax.axhline(0.0, color="black", linewidth=1.2, zorder=5)
        deviation = max((abs(h) for h in drawn_heights), default=1.0)
        pad = deviation * 0.15 or 1.0
        ax.set_ylim(-deviation - pad, deviation + pad)
        _apply_symlog(ax, drawn_heights)
        _annotate_floored_bars(ax, bars, heights, floored)
    ax.set_ylabel("Relative change vs. clean (%, + = improved)" if rb else METRIC_UNIT[metric])
    title = f"{metric} by condition (severity + modality)" + (" -- relative change vs. clean" if rb else "")
    ax.set_title(title, fontsize=12)
    ax.tick_params(axis="x", rotation=60, labelsize=8)
    ax.grid(axis="y", linestyle=":", alpha=0.4)
    fig.tight_layout()

    out_dir.mkdir(parents=True, exist_ok=True)
    fname = f"bar_severity_modality_{'rb_' if rb else ''}{metric.lower()}"
    paths = []
    for ext in ("png", "svg"):
        p = out_dir / f"{fname}.{ext}"
        fig.savefig(p, dpi=150)
        paths.append(p)
    plt.close(fig)
    return paths[0]


def build_context_chart(
    metric: str, dimension: str, values: dict[tuple, float], dim_values: list[str], dim_label: dict, rb: bool, out_dir: Path
) -> Path:
    # Rb charts drop OG entirely: OG is trivially Rb=1 (dividing by itself),
    # not an informative bar -- shown instead as the y=1 reference line below.
    x_labels = CODE_ORDER if rb else (["OG"] + CODE_ORDER)
    x = np.arange(len(x_labels))
    width = 0.8 / max(len(dim_values), 1)

    fig, ax = plt.subplots(figsize=(max(10, len(x_labels) * 1.3), 5.5))
    all_heights: list[float] = []
    all_bars_true_floored: list[tuple] = []  # (bar, true_value, was_floored) for annotation, rb only
    for i, dv in enumerate(dim_values):
        heights = []
        for code in x_labels:
            key = (CLEAN_CONDITION, dv) if code == "OG" else (CODE_TO_SENSOR_EFFECT[code][0], CODE_TO_SENSOR_EFFECT[code][1], dv)
            heights.append(values.get(key))
        offsets = x + (i - (len(dim_values) - 1) / 2) * width
        heights_plot = [h if h is not None else 0 for h in heights]
        floored = [False] * len(heights_plot)
        if rb:
            heights_plot, floored = _floor_for_visibility(heights_plot)
        bars = ax.bar(offsets, heights_plot, width=width * 0.95, label=dim_label.get(dv, str(dv)))
        for bar, h, was_floored in zip(bars, heights, floored):
            if h is None:
                bar.set_visible(False)
            else:
                all_heights.append(bar.get_height())
                if was_floored:
                    all_bars_true_floored.append((bar, h))

    if rb:
        # Diverging bar chart: 0 = no change vs. clean, bars extend up
        # (positive = improved) or down (negative = degraded), ylim symmetric
        # around 0 so the zero-line sits at the vertical center of the plot.
        ax.axhline(0.0, color="black", linewidth=1.2, zorder=5)
        deviation = max((abs(h) for h in all_heights), default=1.0)
        pad = deviation * 0.15 or 1.0
        ax.set_ylim(-deviation - pad, deviation + pad)
        _apply_symlog(ax, all_heights)
        for bar, true_v in all_bars_true_floored:
            y = bar.get_height()
            va = "bottom" if y >= 0 else "top"
            ax.text(bar.get_x() + bar.get_width() / 2, y, f"{true_v:+.3f}%", ha="center", va=va, fontsize=5, rotation=90)
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels)
    ax.set_ylabel("Relative change vs. clean (%, + = improved)" if rb else METRIC_UNIT[metric])
    title = f"{metric} by {dimension}" + (" -- relative change vs. clean" if rb else "") + " (pooled over severity)"
    ax.set_title(title, fontsize=12)
    ax.grid(axis="y", linestyle=":", alpha=0.4)
    ax.legend(fontsize=8, loc="best", ncol=min(len(dim_values), 4))
    fig.tight_layout()

    out_dir.mkdir(parents=True, exist_ok=True)
    fname = f"bar_context_{'rb_' if rb else ''}{metric.lower()}_{dimension}"
    paths = []
    for ext in ("png", "svg"):
        p = out_dir / f"{fname}.{ext}"
        fig.savefig(p, dpi=150)
        paths.append(p)
    plt.close(fig)
    return paths[0]


def build_severity_modality_charts(row_table: pl.DataFrame, out_dir: Path) -> list[Path]:
    coverage = compute_condition_coverage(row_table)
    out = []
    for metric in METRICS:
        raw = compute_metric_by(row_table, metric, ["condition"])
        out.append(build_severity_modality_chart(metric, raw, coverage, rb=False, out_dir=out_dir))
        rb = compute_rb(raw, clean_key_fn=lambda _k: (CLEAN_CONDITION,))
        signed = rb_to_signed_pct_change(rb, metric)
        out.append(build_severity_modality_chart(metric, signed, coverage, rb=True, out_dir=out_dir))
    return out


DIMENSIONS: dict[str, tuple[list[str], dict[str, str]]] = {
    "label": (CLASSES, CLASS_LABEL),
    "time_of_day": (["day", "night"], {}),
    "weather": (["normal", "sleet", "fog", "rain", "snow"], {}),
    "environment": (["highway", "urban", "alleyway", "university"], {}),
    "frame_density": (DENSITY_LABELS, {"1": "1 object", "2-3": "2-3 objects", "4+": "4+ objects"}),
}
DIMENSION_COLUMN = {"label": "cls", "time_of_day": "time_of_day", "weather": "weather", "environment": "environment", "frame_density": "frame_density"}


def build_context_charts(row_table: pl.DataFrame, out_dir: Path) -> list[Path]:
    out = []
    for dimension, (declared_values, dim_label) in DIMENSIONS.items():
        col = DIMENSION_COLUMN[dimension]
        present = set(row_table[col].drop_nulls().unique().to_list())
        dim_values = [v for v in declared_values if v in present]
        if not dim_values:
            print(f"[bar_charts] skipping {dimension}: no values of {col!r} present in row_table", file=sys.stderr)
            continue

        for metric in METRICS:
            group_cols = ["sensor", "effect", col]
            df = row_table.with_columns(
                pl.col("condition").str.extract(r"^(camera|lidar|radar)_").alias("sensor"),
                pl.when(pl.col("condition").str.contains("gaussian_noise"))
                .then(pl.lit("gaussian_noise"))
                .when(pl.col("condition").str.contains("loss_partial"))
                .then(pl.lit("loss_partial"))
                .otherwise(None)
                .alias("effect"),
            )
            og_vals = compute_metric_by(df.filter(pl.col("condition") == CLEAN_CONDITION), metric, [col])
            cond_vals = compute_metric_by(df.filter(pl.col("condition") != CLEAN_CONDITION), metric, group_cols)
            values = {(CLEAN_CONDITION, k[0]): v for k, v in og_vals.items()}
            values.update(cond_vals)

            out.append(build_context_chart(metric, dimension, values, dim_values, dim_label, rb=False, out_dir=out_dir))

            def clean_key_fn(key, dv_col=col):
                if key[0] == CLEAN_CONDITION:
                    return None
                return (CLEAN_CONDITION, key[2])

            rb = compute_rb(values, clean_key_fn=clean_key_fn)
            signed = rb_to_signed_pct_change(rb, metric)
            out.append(build_context_chart(metric, dimension, signed, dim_values, dim_label, rb=True, out_dir=out_dir))
    return out


def build_all_bar_charts(out_dir: Path = (FIGURES_DIR / "bar_charts/v2_official")) -> list[Path]:
    row_table = load_row_table()
    paths = build_severity_modality_charts(row_table, out_dir)
    paths += build_context_charts(row_table, out_dir)
    print(f"[bar_charts] wrote {len(paths)} charts (PNG+SVG each) to {out_dir}")
    return paths


if __name__ == "__main__":
    build_all_bar_charts()
