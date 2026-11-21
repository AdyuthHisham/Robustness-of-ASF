#!/usr/bin/env python3
"""Context-stratified churn for Pass 3, run as a single pass over the
matcher's output instead of 3 separate full CLI reruns (or one combined
4-way group-by, which OOM'd/thrashed swap on this machine -- 6.3GB swap
used, matcher process stuck in D-state after 25 min, killed 2026-08-28).

gt_transition_analysis.py's CLI only supports group-by keys computable from
its own transition table (sequence/frame/gt_obj_idx/cls/loc_x/loc_z/
m_clean/m_corr/condition columns) -- weather/time_of_day/environment are
NOT in that table (confirmed: CLI run crashed with
`ColumnNotFoundError: unable to find column "weather"`), exactly as
gt_transition_analysis.aggregate_transition_rates's own docstring warns
("must be left-joined in by the caller on (sequence, frame[, gt_obj_idx])
before calling this"). This script does that join once, then calls
aggregate_transition_rates 3 times (once per context dim) against the same
in-memory transition table -- avoiding 3x the matching cost.

Context values come from `full_denormalized_table.parquet`, deduped to one
(sequence, frame) -> (weather, time_of_day, environment) row (these are
frame/sequence-level properties, invariant across conditions and
predictions within a frame).

Usage as a library:
    from run_churn_context import build_all_context_churn
    build_all_context_churn()

Run standalone:
    uv run python scripts/analysis/run_churn_context.py
"""
from __future__ import annotations

from amscup_paths import ROOT, OUTPUTS_DIR, REPORTS_DIR  # noqa: E402
import os
import sys
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve()
AMSCUP_ROOT = ROOT
KRADAR_OUTPUTS_DIR = OUTPUTS_DIR
REPORTS_DIR = KRADAR_OUTPUTS_DIR / "robustness_reports"
DENORM_TABLE_PATH = REPORTS_DIR / "full_denormalized_table.parquet"

from robustness.ingest import load_prediction_rows  # noqa: E402
from robustness.gt_transition_analysis import build_match_table_from_ingest, build_transition_table  # noqa: E402
import robustness.gt_transition_analysis as gta  # noqa: E402

CLEAN_CONDITION = "original"
SENSORS = ["camera", "lidar", "radar"]
EFFECTS = ["gaussian_noise", "loss_partial"]
SEVERITIES = ["low", "medium", "high"]
CORRUPTED_CONDITIONS = (
    [f"{s}_{e}_{sv}" for s in SENSORS for e in EFFECTS for sv in SEVERITIES]
    + [f"{s}_loss_complete_zero" for s in SENSORS]
)
CONTEXT_DIMENSIONS = ["time_of_day", "weather", "environment"]

# Matches row_table_iou03.parquet's threshold, which every other metric in
# this pass (mAP/mATE/mASE/mAOE/FN/FP rate) is computed at. NOT
# gta.DEFAULT_IOU_THRESHOLD (0.5) -- an earlier version of this script used
# that default without checking its value, silently computing churn at a
# stricter threshold than everything else it's tabulated/charted alongside.
# Caught 2026-08-28, all churn re-run at 0.3.
IOU_THRESHOLD = 0.3


def _context_lookup() -> pl.DataFrame:
    df = pl.read_parquet(DENORM_TABLE_PATH, columns=["sequence", "frame", "weather", "time_of_day", "environment"])
    return df.unique(subset=["sequence", "frame"])


def build_all_context_churn(out_dir: Path = REPORTS_DIR) -> dict[str, Path]:
    row_table = load_prediction_rows(
        preds_txt=os.path.join(KRADAR_OUTPUTS_DIR, "all_preds.txt"),
        gts_txt=os.path.join(KRADAR_OUTPUTS_DIR, "all_gts.txt"),
        trkid_gts_txt=os.path.join(KRADAR_OUTPUTS_DIR, "all_gts_with_trkid.txt"),
        trkid_preds_txt=os.path.join(KRADAR_OUTPUTS_DIR, "all_preds_with_trkid.txt"),
        fn_txt=os.path.join(KRADAR_OUTPUTS_DIR, "all_fn.txt"),
        iou_threshold=IOU_THRESHOLD,
    )
    match_table = build_match_table_from_ingest(row_table)

    all_transitions = []
    for cond in CORRUPTED_CONDITIONS:
        t = build_transition_table(match_table, CLEAN_CONDITION, cond)
        all_transitions.append(t)
    transitions = pl.concat(all_transitions, how="diagonal_relaxed")

    ctx = _context_lookup()
    transitions = transitions.join(ctx, on=["sequence", "frame"], how="left")
    n_unmatched = transitions.filter(pl.col("weather").is_null()).height
    if n_unmatched:
        print(f"WARNING: {n_unmatched} transition rows had no (sequence, frame) match in the context lookup.", file=sys.stderr)

    written: dict[str, Path] = {}
    out_dir.mkdir(parents=True, exist_ok=True)

    # Condition-only churn, folded into this same matching pass -- the
    # original churn_by_condition.json was built via the CLI without
    # --iou-threshold (defaults to gta.DEFAULT_IOU_THRESHOLD=0.5), so it was
    # at a different matching threshold than everything else in this pass.
    # Rebuilt here at IOU_THRESHOLD=0.3 instead of a separate CLI rerun.
    base_rates = gta.aggregate_transition_rates(transitions, group_by=["corrupted_condition"])
    base_path = REPORTS_DIR / "churn_by_condition.json"
    base_rates.write_json(base_path)
    written["condition"] = base_path
    print(f"Wrote {base_path} ({len(base_rates)} cells)")

    for dim in CONTEXT_DIMENSIONS:
        rates = gta.aggregate_transition_rates(transitions, group_by=["corrupted_condition", dim])
        out_path = out_dir / f"churn_by_condition_{dim}.json"
        rates.write_json(out_path)
        written[dim] = out_path
        print(f"Wrote {out_path} ({len(rates)} cells)")

    return written


if __name__ == "__main__":
    build_all_context_churn()
