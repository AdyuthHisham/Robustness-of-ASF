#!/usr/bin/env python3
"""FP/FN table: one row per severity-specific corruption condition (21
corrupted + `original` = 22 rows -- `frame_deletion` excluded, same scope
as master_metrics_table.py, see [[robustness-metrics-tables]]).

Pure post-hoc aggregation of `is_fp`/`is_fn`/`is_tp` (mutually exclusive
booleans, already labeled by the coordinate-matching backend at IoU=0.3 --
no GT-object trk_id-based matching module needed, confirmed against
row_table_iou03.parquet directly: 0 nulls across all three flag columns,
exactly one true per row). weather/time_of_day/environment are already
columns in the row table (no join needed).

Rate convention (2026-08-28 decision): FP rate = FP/(FP+TP) (== 1-precision),
FN rate = FN/(FN+TP) (== miss rate, same definition already used in
robustness-metrics-tables.md item 6). Both computed per (condition[, bucket])
cell independently -- FP rate's TP is "TP among predictions", FN rate's TP is
"TP among GT", they happen to share the same `is_tp` column since every row
is exactly one of TP/FP/FN.

Table layout (2026-08-28 decision): separate stratified tables, not one wide
dense table -- matches master_metrics_table_by_*.md convention already
established in this directory. `fpfn_table.md` is condition-only (no
stratification); `fpfn_table_by_{weather,time_of_day,environment}.md` each
have one row per (condition, bucket).

Low-N flagging: cells are flagged `*` when N (= FP+FN+TP for that cell) is
below LOW_N_THRESHOLD. Sparsest observed cells in practice: environment x
condition min N=552 (countryside), weather x condition min N=1296 (overcast)
-- both well above zero but far below the median bucket size, so rates there
carry much wider sampling noise than e.g. `normal`/`urban`/`highway` cells.

Usage as a library:
    from fpfn_table import build_all_tables
    build_all_tables(out_dir=(FIGURES_DIR / "robustness_reports"))

Run standalone:
    uv run python scripts/analysis/fpfn_table.py
"""
from __future__ import annotations

from amscup_paths import ROOT, REPORTS_DIR, FIGURES_DIR  # noqa: E402
import sys
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve()
AMSCUP_ROOT = ROOT
ROW_TABLE_PATH = REPORTS_DIR / "row_table_iou03.parquet"
DEFAULT_OUT_DIR = REPORTS_DIR

sys.path.insert(0, str(HERE.parent))
from radar_charts import SENSORS, CLEAN_CONDITION  # noqa: E402

EFFECTS = ["gaussian_noise", "loss_partial"]
SEVERITIES = ["low", "medium", "high"]

# 21 corrupted conditions: 3 sensors x (3 gaussian_noise + 3 loss_partial + 1
# loss_complete_zero). frame_deletion excluded entirely.
CORRUPTED_CONDITIONS = (
    [f"{s}_{e}_{sev}" for s in SENSORS for e in EFFECTS for sev in SEVERITIES]
    + [f"{s}_loss_complete_zero" for s in SENSORS]
)
CONDITIONS = [CLEAN_CONDITION] + CORRUPTED_CONDITIONS  # 22 rows, original first

CONTEXT_DIMENSIONS = ["time_of_day", "weather", "environment"]

LOW_N_THRESHOLD = 2000


def load_row_table() -> pl.DataFrame:
    df = pl.read_parquet(ROW_TABLE_PATH)
    if df.height == 0:
        raise ValueError(f"{ROW_TABLE_PATH} is empty")
    missing = [c for c in CONDITIONS if c not in df["condition"].unique().to_list()]
    if missing:
        raise ValueError(f"row_table missing expected conditions: {missing}")
    return df


def _aggregate(row_table: pl.DataFrame, group_cols: list[str]) -> pl.DataFrame:
    agg = row_table.group_by(group_cols).agg(
        pl.col("is_fp").sum().alias("FP"),
        pl.col("is_fn").sum().alias("FN"),
        pl.col("is_tp").sum().alias("TP"),
    )
    return agg.with_columns(
        (pl.col("FP") + pl.col("FN") + pl.col("TP")).alias("N"),
        (pl.col("FP") / (pl.col("FP") + pl.col("TP"))).alias("FP rate"),
        (pl.col("FN") / (pl.col("FN") + pl.col("TP"))).alias("FN rate"),
    )


def build_fpfn_table(row_table: pl.DataFrame) -> pl.DataFrame:
    row_table = row_table.filter(pl.col("condition").is_in(CONDITIONS))
    agg = _aggregate(row_table, ["condition"])
    by_cond = {row["condition"]: row for row in agg.iter_rows(named=True)}

    rows = []
    for cond in CONDITIONS:
        r = by_cond.get(cond, {})
        rows.append(
            {
                "Condition": cond,
                "N": r.get("N"),
                "FP": r.get("FP"),
                "FN": r.get("FN"),
                "TP": r.get("TP"),
                "FP rate": r.get("FP rate"),
                "FN rate": r.get("FN rate"),
            }
        )
    return pl.DataFrame(rows)


def build_fpfn_context_table(row_table: pl.DataFrame, dimension: str) -> pl.DataFrame:
    row_table = row_table.filter(pl.col("condition").is_in(CONDITIONS))
    agg = _aggregate(row_table, ["condition", dimension])
    by_key = {(row["condition"], row[dimension]): row for row in agg.iter_rows(named=True)}

    buckets = sorted(row_table.select(dimension).unique().to_series().drop_nulls().to_list())
    rows = []
    for cond in CONDITIONS:
        for bucket in buckets:
            r = by_key.get((cond, bucket), {})
            rows.append(
                {
                    "Condition": cond,
                    dimension: bucket,
                    "N": r.get("N"),
                    "FP": r.get("FP"),
                    "FN": r.get("FN"),
                    "TP": r.get("TP"),
                    "FP rate": r.get("FP rate"),
                    "FN rate": r.get("FN rate"),
                }
            )
    return pl.DataFrame(rows)


def _fmt(col: str, v) -> str:
    if v is None:
        return "N/A"
    if col in ("FP rate", "FN rate") and isinstance(v, float):
        return f"{v:.4f}"
    return str(v)


def to_markdown(df: pl.DataFrame) -> str:
    """Rows with N below LOW_N_THRESHOLD get a `*` appended to the first
    column (Condition) so the flag survives even when the table is re-sorted
    or filtered downstream -- consistent with treating low-N rates as lower
    confidence rather than presenting every rate at equal apparent precision."""
    cols = df.columns
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for row in df.iter_rows(named=True):
        n = row.get("N")
        flag = " *" if n is not None and n < LOW_N_THRESHOLD else ""
        cells = []
        for i, c in enumerate(cols):
            val = _fmt(c, row[c])
            if i == 0:
                val += flag
            cells.append(val)
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def build_all_tables(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    row_table = load_row_table()
    written: dict[str, Path] = {}

    master = build_fpfn_table(row_table)
    csv_path = out_dir / "fpfn_table.csv"
    master.write_csv(csv_path)
    md_path = out_dir / "fpfn_table.md"
    md_path.write_text(
        "# FP / FN table -- ASF / K-Radar robustness sweep\n\n"
        "22 rows: `original` + 21 severity-specific corrupted conditions (`frame_deletion` excluded -- "
        "crashed-run coverage artifact, see robustness-metrics-tables.md). FP rate = FP/(FP+TP) "
        "(1-precision). FN rate = FN/(FN+TP) (miss rate). Rows marked `*` have N < "
        f"{LOW_N_THRESHOLD} (FP+FN+TP for that condition) -- treat their rates as noisier than the rest.\n\n"
        + to_markdown(master)
        + "\n"
    )
    written["master_csv"] = csv_path
    written["master_md"] = md_path

    for dim in CONTEXT_DIMENSIONS:
        ctx = build_fpfn_context_table(row_table, dim)
        csv_p = out_dir / f"fpfn_table_by_{dim}.csv"
        ctx.write_csv(csv_p)
        md_p = out_dir / f"fpfn_table_by_{dim}.md"
        md_p.write_text(
            f"# FP / FN table by {dim} -- ASF / K-Radar robustness sweep\n\n"
            f"One row per (condition, {dim}) cell. FP rate = FP/(FP+TP) (1-precision). "
            "FN rate = FN/(FN+TP) (miss rate). Rows marked `*` have N < "
            f"{LOW_N_THRESHOLD} (FP+FN+TP for that cell) -- treat their rates as noisier than the rest; "
            f"sparsest {dim} buckets can run one to two orders of magnitude smaller than the largest.\n\n"
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
