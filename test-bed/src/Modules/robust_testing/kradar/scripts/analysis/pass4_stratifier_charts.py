#!/usr/bin/env python3
"""Pass 4 of the exploratory pass: distance_from_ego / frame_density as
x-axis, one of the 6 row-grain metrics (mAP/mATE/mASE/mAOE/FN_rate/FP_rate)
as y-axis, one panel per sensor modality (to avoid the 22-condition
overplot), one line per (effect, severity) within that panel plus `original`
bolded -- same per-sensor-panel convention as distance_line_charts_by_modality.py
/ density_line_charts.py, extended here to the 3 metrics those charts don't
cover (mAOE, FN_rate, FP_rate) and to frame_density's GT-count bins in
addition to distance.

N-per-bin encoding (2026-08-28 low-N convention, LOW_N_THRESHOLD=1000):
marker area scaled by N (capped), and any point with N < LOW_N_THRESHOLD is
drawn as a hollow/open marker instead of filled -- visually distinct from a
merely-small-but-trustworthy marker, not just smaller.

Distance buckets are the coarse 4-bin `distance_bucket` from
build_denormalized_table.py (near/mid/far/very_far, 20m-wide except the
final 15m bin) -- coarser than distance_line_charts.py's 8x10m bins, adequate
for a first exploratory pass across 6 metrics x 3 sensors x 2 stratifiers
without ballooning to 100+ charts. frame_density uses bar_charts.py's
existing 1/2-3/4+ GT-count bins (confirmed by user 2026-08-28: GT sed+bus
count, not a sensor point-count proxy).

Usage as a library:
    from pass4_stratifier_charts import build_all_pass4_charts
    build_all_pass4_charts(out_dir=Path("outputs/robustness_reports/exploratory"))

Run standalone:
    uv run python scripts/analysis/pass4_stratifier_charts.py
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
TABLE_PATH = AMSCUP_ROOT / "repos" / "K-Radar" / "outputs" / "robustness_reports" / "full_denormalized_table.parquet"
DEFAULT_OUT_DIR = AMSCUP_ROOT / "repos" / "K-Radar" / "outputs" / "robustness_reports" / "exploratory"

sys.path.insert(0, str(AP_METRICS_DIR))
from ap_metrics import compute_ap_grouped  # noqa: E402

sys.path.insert(0, str(HERE.parent))
from radar_charts import SENSORS, CLEAN_CONDITION  # noqa: E402
from fpfn_table import _aggregate as _fpfn_aggregate  # noqa: E402

EFFECTS = ["gaussian_noise", "loss_partial"]
SEVERITIES = ["low", "medium", "high"]
LOW_N_THRESHOLD = 1000

DISTANCE_ORDER = ["near_0_20", "mid_20_40", "far_40_60", "very_far_60_75"]
DISTANCE_MID = {"near_0_20": 10, "mid_20_40": 30, "far_40_60": 50, "very_far_60_75": 67.5}
DENSITY_ORDER = ["1", "2-3", "4+"]
DENSITY_X = {"1": 0, "2-3": 1, "4+": 2}

EFFECT_COLOR = {"gaussian_noise": "#1f77b4", "loss_partial": "#d62728", "loss_complete": "#555555"}
SEVERITY_STYLE = {"low": ":", "medium": "--", "high": "-"}

METRICS = ["mAP", "mATE", "mASE", "mAOE", "FN_rate", "FP_rate"]


def _conditions_for_sensor(sensor: str) -> list[tuple[str, str, str, str]]:
    out = []
    for effect in EFFECTS:
        for severity in SEVERITIES:
            cond = f"{sensor}_{effect}_{severity}"
            out.append((cond, effect, severity, f"{effect[:4]}-{severity[0].upper()}"))
    out.append((f"{sensor}_loss_complete_zero", "loss_complete", "high", "loss_complete"))
    return out


def load_table() -> pl.DataFrame:
    df = pl.read_parquet(TABLE_PATH)
    return df.filter(~pl.col("condition").str.contains("frame_deletion"))


def _tp_errors(df: pl.DataFrame) -> pl.DataFrame:
    tp = df.filter(pl.col("is_tp"))
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
    tp = tp.with_columns(
        (((pl.col("loc_x") - pl.col("gt_loc_x")) ** 2 + (pl.col("loc_z") - pl.col("gt_loc_z")) ** 2) ** 0.5).alias("ate"),
        (1 - intersection / union).alias("ase"),
    )
    raw_diff = pl.col("rotation_y") - pl.col("gt_rotation_y")
    wrapped = (raw_diff + np.pi).mod(2 * np.pi) - np.pi
    return tp.with_columns(wrapped.abs().alias("aoe"))


def compute_metric_by_condition_bucket(df: pl.DataFrame, bucket_col: str) -> dict[str, dict]:
    """{condition: {bucket: {metric: value, N: n}}}"""
    ap_table = compute_ap_grouped(df, ["condition", bucket_col, "cls"])
    map_acc: dict[tuple, list[float]] = {}
    for row in ap_table.iter_rows(named=True):
        if row["ap"] is not None:
            map_acc.setdefault((row["condition"], row[bucket_col]), []).append(row["ap"])
    map_by = {k: float(np.mean(v)) for k, v in map_acc.items()}

    tp = _tp_errors(df)
    err_agg = tp.group_by(["condition", bucket_col]).agg(
        pl.col("ate").mean().alias("mATE"), pl.col("ase").mean().alias("mASE"), pl.col("aoe").mean().alias("mAOE")
    )
    err_by = {(row["condition"], row[bucket_col]): row for row in err_agg.iter_rows(named=True)}

    fpfn_by = {(row["condition"], row[bucket_col]): row for row in _fpfn_aggregate(df, ["condition", bucket_col]).iter_rows(named=True)}

    out: dict[str, dict] = {}
    buckets = df.select(bucket_col).unique().to_series().drop_nulls().to_list()
    conditions = df.select("condition").unique().to_series().to_list()
    for cond in conditions:
        for b in buckets:
            key = (cond, b)
            r = fpfn_by.get(key, {})
            e = err_by.get(key, {})
            n = r.get("N")
            out.setdefault(cond, {})[b] = {
                "mAP": map_by.get(key),
                "mATE": e.get("mATE"),
                "mASE": e.get("mASE"),
                "mAOE": e.get("mAOE"),
                "FN_rate": r.get("FN rate"),
                "FP_rate": r.get("FP rate"),
                "N": n,
            }
    return out


# gt_transition_analysis.add_distance_bin's label format ("[0,20)" etc, GT
# range only) differs from build_denormalized_table.py's distance_bucket
# labels (near_0_20 etc, pred-location-with-GT-fallback) -- same edges
# [0,20,40,60,75], different label strings and slightly different per-row
# distance source (churn is always GT range; mAP/etc charts use pred
# location for TP/FP, GT for FN) -- close enough for a bucket-level overlay,
# not claimed to be identical row-for-row.
CHURN_DISTANCE_LABEL_MAP = {"[0,20)": "near_0_20", "[20,40)": "mid_20_40", "[40,60)": "far_40_60", "[60,75)": "very_far_60_75"}


def _load_churn(bucket_col: str, churn_file_key: str, label_map: dict[str, str] | None) -> dict[tuple, dict]:
    path = DEFAULT_OUT_DIR.parent / f"churn_by_condition_{churn_file_key}.json"
    if not path.exists():
        print(f"WARNING: {path} missing -- churn_rate not plotted for {bucket_col}.")
        return {}
    cells = pl.read_json(path).to_dicts()
    out: dict[tuple, dict] = {}
    for c in cells:
        bucket = c[churn_file_key]
        if label_map is not None:
            bucket = label_map.get(bucket)
            if bucket is None:
                continue
        out[(c["corrupted_condition"], bucket)] = {"churn_rate": c["churn_rate"], "churn_N": c["total"]}
    return out


def merge_churn_into_values(values: dict[str, dict], churn_by_key: dict[tuple, dict]) -> None:
    """Mutates `values` in place, adding churn_rate/churn_N alongside the
    existing per-(condition, bucket) metric dicts."""
    for (cond, bucket), churn_cell in churn_by_key.items():
        values.setdefault(cond, {}).setdefault(bucket, {}).update(churn_cell)


def _plot_metric(
    metric: str,
    sensor: str,
    values: dict[str, dict],
    bucket_order: list[str],
    x_of: dict[str, float],
    x_label: str,
    out_path: Path,
) -> bool:
    fig, ax = plt.subplots(figsize=(8, 5.5))
    plotted = False

    n_key = "churn_N" if metric == "churn_rate" else "N"

    def _draw(cond: str, label: str, color: str, ls: str, lw: float, zorder: int):
        nonlocal plotted
        cell = values.get(cond, {})
        xs, ys, ns = [], [], []
        for b in bucket_order:
            d = cell.get(b, {})
            v = d.get(metric)
            n = d.get(n_key)
            if v is None or n is None:
                continue
            xs.append(x_of[b])
            ys.append(v)
            ns.append(n)
        if not xs:
            return
        plotted = True
        ax.plot(xs, ys, color=color, linestyle=ls, linewidth=lw, zorder=zorder, label=label)
        sizes = [min(220, 25 + 0.015 * n) for n in ns]
        facecolors = [color if n >= LOW_N_THRESHOLD else "none" for n in ns]
        ax.scatter(xs, ys, s=sizes, facecolors=facecolors, edgecolors=color, linewidths=1.2, zorder=zorder + 1)

    _draw(CLEAN_CONDITION, "original (clean)", "black", "-", 3.0, 5)
    for cond, effect, severity, label in _conditions_for_sensor(sensor):
        _draw(cond, label, EFFECT_COLOR[effect], SEVERITY_STYLE[severity], 1.6, 3)

    if not plotted:
        plt.close(fig)
        return False

    ax.set_xlabel(x_label)
    ax.set_ylabel(metric)
    ax.set_title(f"{metric} vs {x_label} -- {sensor}")
    ax.legend(fontsize=8, loc="best")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=140)
    plt.close(fig)
    return True


def build_all_pass4_charts(out_dir: Path = DEFAULT_OUT_DIR) -> list[Path]:
    df = load_table()
    written: list[Path] = []

    for bucket_col, bucket_order, x_of, x_label, subdir, churn_file_key, churn_label_map in [
        ("distance_bucket", DISTANCE_ORDER, DISTANCE_MID, "distance from ego (m, bucket midpoint)", "pass4_distance", "distance_bin", CHURN_DISTANCE_LABEL_MAP),
        ("frame_density", DENSITY_ORDER, DENSITY_X, "frame density (GT sed+bus count bucket)", "pass4_frame_density", "frame_density", None),
    ]:
        values = compute_metric_by_condition_bucket(df, bucket_col)
        churn_by_key = _load_churn(bucket_col, churn_file_key, churn_label_map)
        merge_churn_into_values(values, churn_by_key)
        for metric in METRICS + (["churn_rate"] if churn_by_key else []):
            for sensor in SENSORS:
                out_path = out_dir / subdir / f"{metric}_{sensor}.png"
                if _plot_metric(metric, sensor, values, bucket_order, x_of, x_label, out_path):
                    written.append(out_path)

    print(f"Wrote {len(written)} Pass 4 charts to {out_dir}")
    return written


if __name__ == "__main__":
    build_all_pass4_charts()
