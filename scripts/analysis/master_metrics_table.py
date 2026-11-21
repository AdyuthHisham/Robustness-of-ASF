#!/usr/bin/env python3
"""Master metrics table: one row per severity-specific corruption condition
(21 corrupted + `original` = 22 rows -- `frame_deletion` excluded per the
2026-08-25 decision, see [[robustness-metrics-tables]]: those runs crashed
mid-sweep on Alvis, 0-5.3% frame coverage vs `original`, not a usable
robustness signal).

Metric columns: mAP, mATE, mASE, mAOE, RCE, mRR (== Rb, RoboBEV/MSC-Bench/
Gao-et-al.'s convergently-reinvented retention ratio -- see
[[robustness-metric-selection]]). mFR is deliberately omitted: no frame-level
flip/consistency computation exists anywhere in this pipeline (spec'd in
`robustness-visualization-plan.md`, never implemented) -- silently dropped
rather than filled with a blocked placeholder in every cell, per 2026-08-28
decision. mAOE is newly computed here (circular yaw diff on `is_tp` rows,
same coordinate-matching backend mATE/mASE already use) -- previously absent
per bar_charts.py's 2026-08-27 audit ("gt_rotation_y present, nothing
consumes it").

mATE/mASE/mAOE reuse heatmaps.py's pooled-over-both-classes formulas
(coordinate-fallback greedy IoU matcher, validated on real data per
`robustness-visualization-plan.md` -- distinct from, and not blocked on,
gt_transition_analysis.py's separate persistent-object-ID matcher). RCE is
per-class AP relative change vs. `original`, averaged over classes, computed
at every severity (unlike robustness-metrics-tables.md's item 3, which only
tabulates the highest-coverage severity per effect). mRR is `compute_rb`
applied to mAP.

Context breakdown: layout (a) (2026-08-28 decision) -- the master table is
condition-aggregated only; per-condition x per-bucket breakdowns live in
separate `*_by_{weather,time_of_day,environment}.csv/md` files, same metric
columns, one row per (condition, bucket). weather/time_of_day/environment
are already columns in row_table_iou03.parquet (no join needed, confirmed in
[[context-radar-charts]]).

Usage as a library:
    from master_metrics_table import build_all_tables
    build_all_tables(out_dir=(FIGURES_DIR / "robustness_reports"))

Run standalone:
    uv run python scripts/analysis/master_metrics_table.py
"""
from __future__ import annotations

from amscup_paths import ROOT, REPORTS_DIR, FIGURES_DIR  # noqa: E402
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve()
AMSCUP_ROOT = ROOT
ROW_TABLE_PATH = REPORTS_DIR / "row_table_iou03.parquet"
DEFAULT_OUT_DIR = REPORTS_DIR

from robustness.ap_metrics import compute_ap_grouped  # noqa: E402

sys.path.insert(0, str(HERE.parent))
from radar_charts import (  # noqa: E402
    SENSORS, CLASSES, CLEAN_CONDITION, compute_condition_coverage,
)

EFFECTS = ["gaussian_noise", "loss_partial"]
SEVERITIES = ["low", "medium", "high"]
COVERAGE_THRESHOLD_PCT = 90.0

# 21 corrupted conditions: 3 sensors x (3 gaussian_noise + 3 loss_partial + 1
# loss_complete_zero). frame_deletion excluded entirely.
CORRUPTED_CONDITIONS = (
    [f"{s}_{e}_{sev}" for s in SENSORS for e in EFFECTS for sev in SEVERITIES]
    + [f"{s}_loss_complete_zero" for s in SENSORS]
)
CONDITIONS = [CLEAN_CONDITION] + CORRUPTED_CONDITIONS  # 22 rows, original first

CONTEXT_DIMENSIONS = ["time_of_day", "weather", "environment"]

METRIC_COLUMNS = ["mAP", "mATE", "mASE", "mAOE", "RCE", "mRR"]


def load_row_table() -> pl.DataFrame:
    df = pl.read_parquet(ROW_TABLE_PATH)
    if df.height == 0:
        raise ValueError(f"{ROW_TABLE_PATH} is empty")
    missing = [c for c in CONDITIONS if c not in df["condition"].unique().to_list()]
    if missing:
        raise ValueError(f"row_table missing expected conditions: {missing}")
    return df


def _ap_by_group_cls(row_table: pl.DataFrame, group_cols: list[str]) -> dict[tuple, float]:
    """{group_key + (cls,): ap}, only cells with GT present."""
    ap_table = compute_ap_grouped(row_table, group_cols + ["cls"])
    out: dict[tuple, float] = {}
    for row in ap_table.iter_rows(named=True):
        if row["cls"] in CLASSES and row["ap"] is not None:
            key = tuple(row[c] for c in group_cols) + (row["cls"],)
            out[key] = float(row["ap"])
    return out


def compute_map_by(row_table: pl.DataFrame, group_cols: list[str]) -> dict[tuple, float]:
    """{group_key: mAP} = mean(AP) over classes with GT present."""
    ap_by_cls = _ap_by_group_cls(row_table, group_cols)
    by_key: dict[tuple, list[float]] = {}
    for key_cls, ap in ap_by_cls.items():
        key = key_cls[:-1]
        by_key.setdefault(key, []).append(ap)
    return {k: float(np.mean(v)) for k, v in by_key.items() if v}


SUMMARY_FULL_DENSITY_PATH = REPORTS_DIR / "crossproduct_v2" / "summary_full_density.parquet"


def compute_aggregated_map_by(group_cols: list[str]) -> dict[tuple, float]:
    """{group_key: aggregated mAP}: the num_gt-weighted mean of the cell-level
    `ap_restricted_range` over the full-grain cells (cls x weather x time_of_day x
    environment x distance_bucket x frame_density) of
    crossproduct_v2/summary_full_density.parquet, pooled over both classes. This is
    the thesis's "pooled" mAP (clean = 73.99); it is NOT the mean of the two
    per-class APs (`compute_map_by`, clean = 72.89). `group_cols` must be columns of
    that summary (`condition`, `weather`, `time_of_day`, `environment`)."""
    if not SUMMARY_FULL_DENSITY_PATH.exists():
        raise FileNotFoundError(
            f"{SUMMARY_FULL_DENSITY_PATH} not found; build it with scripts/analysis/crossproduct/run_analysis.py "
            "or unpack the data bundle (see data/DATA.md)."
        )
    cells = pl.read_parquet(SUMMARY_FULL_DENSITY_PATH).filter(
        pl.col("ap_restricted_range").is_not_null() & pl.col("condition").is_in(CONDITIONS)
    )
    agg = cells.group_by(group_cols).agg(
        ((pl.col("ap_restricted_range") * pl.col("num_gt")).sum() / pl.col("num_gt").sum()).alias("map")
    )
    return {tuple(r[c] for c in group_cols): float(r["map"]) for r in agg.iter_rows(named=True) if r["map"] is not None}


def compute_rce_by(row_table: pl.DataFrame, group_cols: list[str], orig_ap_by_cls: dict[str, float]) -> dict[tuple, float]:
    """{group_key: RCE%} = mean over classes of (orig_ap - ap)/orig_ap*100,
    Dong et al.'s convention (RCE = (AP_clean - AP_corrupted)/AP_clean, positive =
    degradation, "RCE(%)-lower-is-better") -- extended to every severity (not just
    the highest-coverage one) and to arbitrary group_cols (e.g. + context bucket)."""
    ap_by_cls = _ap_by_group_cls(row_table, group_cols)
    by_key: dict[tuple, list[float]] = {}
    for key_cls, ap in ap_by_cls.items():
        key, cls = key_cls[:-1], key_cls[-1]
        orig_ap = orig_ap_by_cls.get(cls)
        if orig_ap is None or orig_ap == 0:
            continue
        by_key.setdefault(key, []).append((orig_ap - ap) / orig_ap * 100.0)
    return {k: float(np.mean(v)) for k, v in by_key.items() if v}


def compute_ate_ase_aoe_by(row_table: pl.DataFrame, group_cols: list[str]) -> tuple[dict, dict, dict]:
    """{group_key: mATE}, {group_key: mASE}, {group_key: mAOE (radians)},
    pooled over both classes' TP rows -- same ATE/ASE formulas as
    heatmaps.compute_ate_ase_by_condition. mAOE = mean absolute circular yaw
    difference (pred - gt), wrapped to [-pi, pi] before taking abs, so a
    +170 deg vs. -170 deg pair reads as a 20 deg error, not 340 deg."""
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
    raw_diff = pl.col("rotation_y") - pl.col("gt_rotation_y")
    wrapped = (raw_diff + np.pi).mod(2 * np.pi) - np.pi  # wrap to [-pi, pi]
    tp = tp.with_columns(wrapped.abs().alias("aoe"))

    agg = tp.group_by(group_cols).agg(
        pl.col("ate").mean().alias("mATE"),
        pl.col("ase").mean().alias("mASE"),
        pl.col("aoe").mean().alias("mAOE"),
    )
    ate, ase, aoe = {}, {}, {}
    for row in agg.iter_rows(named=True):
        key = tuple(row[c] for c in group_cols)
        ate[key] = row["mATE"]
        ase[key] = row["mASE"]
        aoe[key] = row["mAOE"]
    return ate, ase, aoe


def compute_rb(values_by_condition: dict[str, float]) -> dict[str, float]:
    """Rb^c = corrupted_value / original_value (mRR/RS/Rb -- see
    [[robustness-metric-selection]]), against the single global `original`
    baseline."""
    orig = values_by_condition.get(CLEAN_CONDITION)
    if orig is None or orig == 0:
        return {}
    return {cond: val / orig for cond, val in values_by_condition.items()}


def build_master_table(row_table: pl.DataFrame) -> pl.DataFrame:
    row_table = row_table.filter(pl.col("condition").is_in(CONDITIONS))

    map_by_cond = compute_aggregated_map_by(["condition"])
    ate_by_cond, ase_by_cond, aoe_by_cond = compute_ate_ase_aoe_by(row_table, ["condition"])
    mrr_by_cond = compute_rb({cond: v for (cond,), v in map_by_cond.items()})
    coverage = compute_condition_coverage(row_table)

    orig_ap_by_cls: dict[str, float] = {}
    for row in compute_ap_grouped(row_table.filter(pl.col("condition") == CLEAN_CONDITION), ["cls"]).iter_rows(named=True):
        if row["ap"] is not None:
            orig_ap_by_cls[row["cls"]] = float(row["ap"])
    rce_by_cond = compute_rce_by(row_table, ["condition"], orig_ap_by_cls)

    rows = []
    for cond in CONDITIONS:
        is_original = cond == CLEAN_CONDITION
        rows.append(
            {
                "Condition": cond,
                "mAP": map_by_cond.get((cond,)),
                "mATE": ate_by_cond.get((cond,)),
                "mASE": ase_by_cond.get((cond,)),
                "mAOE": aoe_by_cond.get((cond,)),
                "RCE": None if is_original else rce_by_cond.get((cond,)),
                "mRR": 1.0 if is_original else mrr_by_cond.get(cond),
                "Coverage (%)": coverage.get(cond),
            }
        )
    return pl.DataFrame(rows)


def build_context_table(row_table: pl.DataFrame, dimension: str) -> pl.DataFrame:
    row_table = row_table.filter(pl.col("condition").is_in(CONDITIONS))
    group_cols = ["condition", dimension]

    map_by = compute_aggregated_map_by(group_cols)
    ate_by, ase_by, aoe_by = compute_ate_ase_aoe_by(row_table, group_cols)
    coverage = compute_condition_coverage(row_table)  # condition-level only; buckets don't get their own coverage denominator

    orig_ap_by_cls_bucket: dict[tuple, float] = {}
    orig_slice = row_table.filter(pl.col("condition") == CLEAN_CONDITION)
    for row in compute_ap_grouped(orig_slice, [dimension, "cls"]).iter_rows(named=True):
        if row["ap"] is not None:
            orig_ap_by_cls_bucket[(row[dimension], row["cls"])] = float(row["ap"])

    # RCE per (condition, bucket) needs the original AP for that SAME bucket
    # (e.g. rain-only original AP), not the global original AP -- otherwise a
    # bucket with an intrinsically harder scene reads as "corruption damage"
    # that's actually baseline difficulty.
    ap_by_cls_bucket = _ap_by_group_cls(row_table, group_cols)
    rce_by: dict[tuple, list[float]] = {}
    for key_cls, ap in ap_by_cls_bucket.items():
        cond, bucket, cls = key_cls
        orig_ap = orig_ap_by_cls_bucket.get((bucket, cls))
        if orig_ap is None or orig_ap == 0:
            continue
        rce_by.setdefault((cond, bucket), []).append((orig_ap - ap) / orig_ap * 100.0)
    rce_by = {k: float(np.mean(v)) for k, v in rce_by.items() if v}

    # mRR per (condition, bucket) against that bucket's own original mAP.
    orig_map_by_bucket = {
        bucket: map_by.get((CLEAN_CONDITION, bucket)) for bucket in row_table.select(dimension).unique().to_series().to_list()
    }

    buckets = sorted(row_table.select(dimension).unique().to_series().drop_nulls().to_list())
    rows = []
    for cond in CONDITIONS:
        for bucket in buckets:
            is_original = cond == CLEAN_CONDITION
            key = (cond, bucket)
            orig_map = orig_map_by_bucket.get(bucket)
            mrr = 1.0 if is_original else (
                map_by.get(key) / orig_map if map_by.get(key) is not None and orig_map else None
            )
            rows.append(
                {
                    "Condition": cond,
                    dimension: bucket,
                    "mAP": map_by.get(key),
                    "mATE": ate_by.get(key),
                    "mASE": ase_by.get(key),
                    "mAOE": aoe_by.get(key),
                    "RCE": None if is_original else rce_by.get(key),
                    "mRR": mrr,
                }
            )
    return pl.DataFrame(rows)


def _fmt(v) -> str:
    if v is None:
        return "N/A"
    if isinstance(v, str):
        return v
    if isinstance(v, float):
        return f"{v:.4f}"
    return str(v)


def to_markdown(df: pl.DataFrame) -> str:
    """RCE is undefined for `original` (nothing to compare it to) -- shown as
    '--' rather than 'N/A' (which reads as 'missing/blocked', not
    'not applicable by definition'). mRR is trivially 1.0 for `original` --
    annotated '1.00 (baseline)' rather than a bare number, so it doesn't read
    as an ordinary data point in the same column as its own comparison
    targets."""
    cols = df.columns
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for row in df.iter_rows(named=True):
        is_original = row.get("Condition") == CLEAN_CONDITION
        cells = []
        for c in cols:
            if is_original and c == "RCE":
                cells.append("--")
            elif is_original and c == "mRR":
                cells.append("1.00 (baseline)")
            else:
                cells.append(_fmt(row[c]))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def build_all_tables(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    row_table = load_row_table()
    written: dict[str, Path] = {}

    master = build_master_table(row_table)
    # mAP is the thesis's aggregated (pooled) mAP: clean baseline 73.99 (see
    # compute_aggregated_map_by). The earlier per-class mean was 72.89
    # ((77.86 + 67.93) / 2, the official eval_revised.py BEV AP@IoU=0.3 per class);
    # that is the class-mean, not the aggregate, and is no longer what this table reports.
    EXPECTED_ORIGINAL_MAP = 73.99
    orig_map = master.filter(pl.col("Condition") == CLEAN_CONDITION)["mAP"][0]
    if orig_map is not None and abs(orig_map - EXPECTED_ORIGINAL_MAP) > 0.01:
        print(f"WARNING: original mAP = {orig_map:.4f}, expected {EXPECTED_ORIGINAL_MAP} (verified clean baseline) -- investigate before trusting this table.", file=sys.stderr)

    csv_path = out_dir / "master_metrics_table.csv"
    master.write_csv(csv_path)
    md_path = out_dir / "master_metrics_table.md"
    md_path.write_text(
        "# Master metrics table -- ASF / K-Radar robustness sweep\n\n"
        f"22 rows: `original` + 21 severity-specific corrupted conditions (`frame_deletion` excluded -- "
        "crashed-run coverage artifact, see robustness-metrics-tables.md). mFR omitted (not implemented). "
        f"mAP is the aggregated mAP (num_gt-weighted over both classes and all stratum cells, from `crossproduct_v2/summary_full_density.parquet`): "
        f"original = {orig_map:.2f}. It is not the mean of the two per-class APs (72.89). RCE is still computed per class.\n\n"
        + to_markdown(master)
        + "\n"
    )
    written["master_csv"] = csv_path
    written["master_md"] = md_path

    for dim in CONTEXT_DIMENSIONS:
        ctx = build_context_table(row_table, dim)
        csv_p = out_dir / f"master_metrics_table_by_{dim}.csv"
        ctx.write_csv(csv_p)
        md_p = out_dir / f"master_metrics_table_by_{dim}.md"
        md_p.write_text(
            f"# Master metrics table by {dim} -- ASF / K-Radar robustness sweep\n\n"
            f"One row per (condition, {dim}) cell. RCE/mRR computed against that {dim} bucket's own "
            "`original` AP, not the global original -- isolates corruption effect from baseline scene difficulty.\n\n"
            + to_markdown(ctx)
            + "\n"
        )
        written[f"{dim}_csv"] = csv_p
        written[f"{dim}_md"] = md_p

    return written


if __name__ == "__main__":
    paths = build_all_tables()
    for name, path in paths.items():
        print(f"{name}: {path}")
