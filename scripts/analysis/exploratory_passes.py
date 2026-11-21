#!/usr/bin/env python3
"""Passes 1-3 of the full-granularity exploratory pass (see
docs/trend_candidates.md and the 2026-08-28 task spec): condition main
effects, context main effects, and condition x context two-way interactions.
Operates on `full_denormalized_table.parquet` (build_denormalized_table.py),
not row_table_iou03.parquet directly -- same 22-condition scope
(frame_deletion excluded, 2026-08-25 decision), mFR omitted (2026-08-28
decision, reconfirmed by user).

Reuses master_metrics_table.py's group_cols-generic mAP/mATE/mASE/mAOE/mRR
machinery and fpfn_table.py's group_cols-generic FP/FN aggregation verbatim
-- neither needed modification, both already took arbitrary group_cols.
Churn is NOT included here: gt_transition_analysis.py is a separate
per-GT-object matcher over a different source table (all_preds.txt/
all_gts.txt via ingest.py, not row_table_iou03.parquet), run separately (see
run_churn.sh / churn_by_condition.json, churn_by_{weather,time_of_day,
environment}.json) and merged into Pass 1 and Pass 3 output by
merge_churn.py once available. Pass 2 (context-only, condition collapsed)
does NOT get a churn column: churn is inherently defined relative to one
corrupted condition vs. `original` (a 2x2 stable/miss/recover/fail
classification), so "churn averaged over all corrupted conditions, ignoring
which one" has no clean interpretation -- flagged as an explicit scope
exclusion rather than silently omitted.

Low-N flagging: LOW_N_THRESHOLD = 1000 (user-specified 2026-08-28), applied
per-cell to N = TP+FP+FN (Pass 1/2) or per (condition, bucket) cell (Pass 3).
Flagged rows get low_n=True; not dropped.

Usage as a library:
    from exploratory_passes import build_all_passes
    build_all_passes(out_dir=Path("outputs/robustness_reports/exploratory"))

Run standalone:
    uv run python scripts/analysis/exploratory_passes.py
"""
from __future__ import annotations

from amscup_paths import ROOT, REPORTS_DIR  # noqa: E402
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve()
AMSCUP_ROOT = ROOT
TABLE_PATH = REPORTS_DIR / "full_denormalized_table.parquet"
DEFAULT_OUT_DIR = REPORTS_DIR / "exploratory"

from robustness.ap_metrics import compute_ap_grouped  # noqa: E402

sys.path.insert(0, str(HERE.parent))
from radar_charts import SENSORS, CLASSES, CLEAN_CONDITION  # noqa: E402
from master_metrics_table import (  # noqa: E402
    CONDITIONS, EFFECTS, SEVERITIES, CONTEXT_DIMENSIONS,
    compute_map_by, compute_ate_ase_aoe_by, compute_rb, _ap_by_group_cls,
)
from fpfn_table import _aggregate as _fpfn_aggregate  # noqa: E402

LOW_N_THRESHOLD = 1000


def load_table() -> pl.DataFrame:
    df = pl.read_parquet(TABLE_PATH)
    if df.height == 0:
        raise ValueError(f"{TABLE_PATH} is empty")
    missing = [c for c in CONDITIONS if c not in df["condition"].unique().to_list()]
    if missing:
        raise ValueError(f"table missing expected conditions: {missing}")
    return df.filter(pl.col("condition").is_in(CONDITIONS))


def _n_table(df: pl.DataFrame, group_cols: list[str]) -> dict[tuple, int]:
    agg = df.group_by(group_cols).agg(pl.len().alias("N"))
    return {tuple(row[c] for c in group_cols): row["N"] for row in agg.iter_rows(named=True)}


def _fpfn_table(df: pl.DataFrame, group_cols: list[str]) -> dict[tuple, dict]:
    agg = _fpfn_aggregate(df, group_cols)
    return {tuple(row[c] for c in group_cols): row for row in agg.iter_rows(named=True)}


def build_metric_rows(df: pl.DataFrame, group_cols: list[str], keys: list[tuple], key_names: list[str]) -> pl.DataFrame:
    """One row per key in `keys` (key = tuple aligned with group_cols),
    all 6 metrics (mAP/mATE/mASE/mAOE/mRR/RCE omitted here, see caller) plus
    FP/FN rate, N, and low_n flag. mRR needs a condition-only baseline
    (Pb 1/3) or a (bucket-local) baseline (Pass 2/3) -- caller passes
    `mrr_baseline_cols`, the group_cols to strip down to for the `original`
    lookup."""
    map_by = compute_map_by(df, group_cols)
    ate_by, ase_by, aoe_by = compute_ate_ase_aoe_by(df, group_cols)
    n_by = _n_table(df, group_cols)
    fpfn_by = _fpfn_table(df, group_cols)

    rows = []
    for key in keys:
        r = fpfn_by.get(key, {})
        n = n_by.get(key)
        row = {name: val for name, val in zip(key_names, key)}
        row.update(
            {
                "N": n,
                "mAP": map_by.get(key),
                "mATE": ate_by.get(key),
                "mASE": ase_by.get(key),
                "mAOE": aoe_by.get(key),
                "FP_rate": r.get("FP rate"),
                "FN_rate": r.get("FN rate"),
                "low_n": bool(n is not None and n < LOW_N_THRESHOLD),
            }
        )
        rows.append(row)
    return pl.DataFrame(rows)


def pass1_condition_main_effects(df: pl.DataFrame) -> pl.DataFrame:
    keys = [(c,) for c in CONDITIONS]
    out = build_metric_rows(df, ["condition"], keys, ["condition"])
    map_by_cond = {row["condition"]: row["mAP"] for row in out.iter_rows(named=True)}
    mrr = compute_rb(map_by_cond)
    return out.with_columns(
        pl.col("condition").map_elements(lambda c: 1.0 if c == CLEAN_CONDITION else mrr.get(c), return_dtype=pl.Float64).alias("mRR")
    )


def pass2_context_main_effects(df: pl.DataFrame, dimension: str) -> pl.DataFrame:
    """Condition collapsed (pooled over all 22 conditions including
    `original`) -- answers "which context buckets are inherently harder",
    not corruption-specific. mRR is not meaningful here (no single baseline
    to ratio against across pooled conditions) -- omitted, not faked."""
    buckets = sorted(df.select(dimension).unique().to_series().drop_nulls().to_list())
    keys = [(b,) for b in buckets]
    out = build_metric_rows(df, [dimension], keys, [dimension])
    return out


def pass3_condition_x_context(df: pl.DataFrame, dimension: str, pass1: pl.DataFrame) -> pl.DataFrame:
    """condition x bucket cells, with two deviation columns -- see
    2026-08-28 correction, do not sort/rank by the first one:

    - mAP_delta_from_main_effect = cell mAP - condition's OVERALL Pass-1 mAP
      (collapsed over context). Kept for backward compatibility only. This
      conflates the context's own baseline difficulty (finding #4 in
      trend_candidates.md -- `alleyway` is ~40 points harder than average
      for EVERY condition, including uncorrupted `original`) with the
      condition's actual interaction with that context. Confirmed broken by
      inspection: `original` itself shows a -40 delta in `alleyway`, despite
      having no corruption to interact with anything -- proof this column
      measures "is this bucket hard" more than "does this condition react
      unusually to this bucket".

    - interaction_delta = cell mAP - `original`'s mAP in that SAME bucket
      (double-difference). This nets out the bucket's baseline difficulty
      (identical term in both the cell and the same-bucket `original` value)
      and isolates the condition-specific interaction. This is the column to
      sort/rank by for Pass 3's "largest deviation from main effect"
      requirement -- `mAP_delta_from_main_effect` should not be used for
      that despite the name."""
    buckets = sorted(df.select(dimension).unique().to_series().drop_nulls().to_list())
    keys = [(c, b) for c in CONDITIONS for b in buckets]
    out = build_metric_rows(df, ["condition", dimension], keys, ["condition", dimension])
    main_effect = {row["condition"]: row["mAP"] for row in pass1.iter_rows(named=True)}
    out = out.with_columns(
        (pl.col("mAP") - pl.col("condition").map_elements(lambda c: main_effect.get(c), return_dtype=pl.Float64)).alias(
            "mAP_delta_from_main_effect"
        )
    )

    orig_by_bucket = {
        row[dimension]: row["mAP"] for row in out.filter(pl.col("condition") == CLEAN_CONDITION).iter_rows(named=True)
    }
    out = out.with_columns(
        (pl.col("mAP") - pl.col(dimension).map_elements(lambda b: orig_by_bucket.get(b), return_dtype=pl.Float64)).alias(
            "interaction_delta"
        )
    )

    return out.sort(pl.col("interaction_delta").abs(), descending=True, nulls_last=True)


def _write(df: pl.DataFrame, out_dir: Path, name: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    df.write_csv(out_dir / f"{name}.csv")
    (out_dir / f"{name}.md").write_text(_to_markdown(df))


def _fmt(v) -> str:
    if v is None:
        return "N/A"
    if isinstance(v, bool):
        return "YES" if v else ""
    if isinstance(v, float):
        return f"{v:.4f}"
    return str(v)


def _to_markdown(df: pl.DataFrame) -> str:
    cols = df.columns
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for row in df.iter_rows(named=True):
        lines.append("| " + " | ".join(_fmt(row[c]) for c in cols) + " |")
    return "\n".join(lines)


def build_all_passes(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, pl.DataFrame]:
    df = load_table()
    results: dict[str, pl.DataFrame] = {}

    pass1 = pass1_condition_main_effects(df)
    _write(pass1, out_dir, "pass1_condition_main_effects")
    results["pass1"] = pass1
    low_n_p1 = pass1.filter(pl.col("low_n"))["condition"].to_list()
    print(f"Pass 1: {pass1.height} conditions. Low-N (<{LOW_N_THRESHOLD}): {low_n_p1 or 'none'}")

    for dim in CONTEXT_DIMENSIONS:
        p2 = pass2_context_main_effects(df, dim)
        _write(p2, out_dir, f"pass2_context_main_effects_{dim}")
        results[f"pass2_{dim}"] = p2
        low_n_p2 = p2.filter(pl.col("low_n"))[dim].to_list()
        print(f"Pass 2 ({dim}): {p2.height} buckets. Low-N: {low_n_p2 or 'none'}")

        p3 = pass3_condition_x_context(df, dim, pass1)
        _write(p3, out_dir, f"pass3_condition_x_{dim}")
        results[f"pass3_{dim}"] = p3
        n_low_n_p3 = p3.filter(pl.col("low_n")).height
        print(f"Pass 3 (condition x {dim}): {p3.height} cells, {n_low_n_p3} flagged low-N.")

    return results


if __name__ == "__main__":
    build_all_passes()
