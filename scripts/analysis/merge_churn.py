#!/usr/bin/env python3
"""Merges gt_transition_analysis.py's churn output into Pass 1 (condition
main effects) and Pass 3 (condition x context). Run only after both:
  - churn_by_condition.json           (--group-by corrupted_condition)
  - churn_by_condition_context.json   (--group-by corrupted_condition
    --group-by weather --group-by time_of_day --group-by environment)
exist (see run commands in docs/trend_candidates.md / session log).

Pass 2 (context alone, condition collapsed) intentionally gets no churn
column -- see exploratory_passes.py's module docstring for why that
aggregation has no clean interpretation for churn.

`original` rows get churn_rate = 0.0 / null by definition (nothing to
compare it to) -- shown as null (not 0.0) to distinguish "not applicable"
from amscup_paths import ROOT, REPORTS_DIR  # noqa: E402
from "measured zero churn".

Pass 3's context churn is derived from the single 4-way run
(corrupted_condition x weather x time_of_day x environment) by re-summing
the raw N_stable/N_miss/N_recover/N_fail counts down to (condition, single
dimension) -- avoids three separate full-sweep matcher reruns.

Usage as a library:
    from merge_churn import merge_all
    merge_all()

Run standalone:
    uv run python scripts/analysis/merge_churn.py
"""
from __future__ import annotations

import json
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve()
AMSCUP_ROOT = ROOT
REPORTS_DIR = REPORTS_DIR
EXPLORATORY_DIR = REPORTS_DIR / "exploratory"

CHURN_COND_PATH = REPORTS_DIR / "churn_by_condition.json"

CONTEXT_DIMENSIONS = ["time_of_day", "weather", "environment"]


def _load_json_df(path: Path) -> pl.DataFrame:
    return pl.DataFrame(json.loads(path.read_text()))


def merge_pass1() -> pl.DataFrame:
    pass1 = pl.read_csv(EXPLORATORY_DIR / "pass1_condition_main_effects.csv")
    churn = _load_json_df(CHURN_COND_PATH).select(
        pl.col("corrupted_condition").alias("condition"), "churn", "churn_rate", "net_retention", "total"
    )
    out = pass1.join(churn, on="condition", how="left")
    out.write_csv(EXPLORATORY_DIR / "pass1_condition_main_effects.csv")
    return out


def merge_pass3(dim: str) -> pl.DataFrame:
    path = REPORTS_DIR / f"churn_by_condition_{dim}.json"
    ctx = _load_json_df(path)
    agg = ctx.rename({"corrupted_condition": "condition"}).select(
        ["condition", dim, "churn", "churn_rate", "net_retention", "total"]
    ).rename({"total": "gt_total"})

    p3_path = EXPLORATORY_DIR / f"pass3_condition_x_{dim}.csv"
    p3 = pl.read_csv(p3_path)
    out = p3.join(agg, on=["condition", dim], how="left")
    out.write_csv(p3_path)
    return out


def merge_all() -> None:
    if not CHURN_COND_PATH.exists():
        raise FileNotFoundError(f"{CHURN_COND_PATH} missing -- run gt_transition_analysis.py --group-by corrupted_condition first")
    p1 = merge_pass1()
    print(f"Merged churn into Pass 1 ({p1.height} rows).")

    for dim in CONTEXT_DIMENSIONS:
        dim_path = REPORTS_DIR / f"churn_by_condition_{dim}.json"
        if not dim_path.exists():
            print(f"WARNING: {dim_path} missing -- Pass 3 x {dim} churn not merged.")
            continue
        p3 = merge_pass3(dim)
        print(f"Merged churn into Pass 3 x {dim} ({p3.height} rows).")


if __name__ == "__main__":
    merge_all()
