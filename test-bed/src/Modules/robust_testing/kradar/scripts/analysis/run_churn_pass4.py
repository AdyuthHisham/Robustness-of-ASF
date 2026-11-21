#!/usr/bin/env python3
"""Churn stratified by the two continuous stratifiers Pass 4 covers for
every other metric (distance_from_ego, frame_density) but churn was
deferred on (see docs/trend_candidates.md's "not yet covered" section,
2026-08-28). Same pattern as run_churn_context.py: one matching pass over
the 21 corrupted conditions, then two separate group-by aggregations from
the same in-memory transition table (cheaper than rerunning the matcher
per dimension, and avoids the swap-thrashing seen when combining multiple
stratification dimensions into one over-wide group-by -- see
run_churn_context.py's docstring for that incident).

distance_bin: gt_transition_analysis.add_distance_bin() bins GT range
(sqrt(loc_x^2 + loc_z^2)) -- same edges as build_denormalized_table.py's
DISTANCE_EDGES=[20,40,60] (near/mid/far/very_far), for consistency with the
rest of Pass 4's charts, even though the bin label format differs
(add_distance_bin produces "[0,20)" style labels, not the
near_0_20/mid_20_40/... names used elsewhere).

frame_density: not derivable from the transition table (same situation as
weather/time_of_day/environment -- gt_obj_idx-keyed, not a column the
matcher produces) -- joined in from full_denormalized_table.parquet's
existing frame_density column, deduped to one (sequence, frame) -> bucket
row, same approach run_churn_context.py used for the categorical context
dims.

Usage as a library:
    from run_churn_pass4 import build_pass4_churn
    build_pass4_churn()

Run standalone:
    uv run python scripts/analysis/run_churn_pass4.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve()
AMSCUP_ROOT = HERE.parents[7]
KRADAR_ALVIS_DIR = AMSCUP_ROOT / "repos" / "K-Radar" / "scripts" / "alvis"
KRADAR_OUTPUTS_DIR = AMSCUP_ROOT / "repos" / "K-Radar" / "outputs"
REPORTS_DIR = KRADAR_OUTPUTS_DIR / "robustness_reports"
DENORM_TABLE_PATH = REPORTS_DIR / "full_denormalized_table.parquet"

sys.path.insert(0, str(KRADAR_ALVIS_DIR))
from ingest import load_prediction_rows  # noqa: E402
from gt_transition_analysis import build_match_table_from_ingest, build_transition_table, add_distance_bin  # noqa: E402
import gt_transition_analysis as gta  # noqa: E402

CLEAN_CONDITION = "original"
SENSORS = ["camera", "lidar", "radar"]
EFFECTS = ["gaussian_noise", "loss_partial"]
SEVERITIES = ["low", "medium", "high"]
CORRUPTED_CONDITIONS = (
    [f"{s}_{e}_{sv}" for s in SENSORS for e in EFFECTS for sv in SEVERITIES]
    + [f"{s}_loss_complete_zero" for s in SENSORS]
)

# Matches build_denormalized_table.py's DISTANCE_EDGES=[20,40,60] over the
# observed 1-75m range (near/mid/far/very_far, last bin open-ended to 75m).
DISTANCE_BIN_EDGES = [0, 20, 40, 60, 75]

# See run_churn_context.py's IOU_THRESHOLD comment: matches
# row_table_iou03.parquet, NOT gta.DEFAULT_IOU_THRESHOLD (0.5) -- an earlier
# version of this script used that default silently. Caught 2026-08-28.
IOU_THRESHOLD = 0.3


def _frame_density_lookup() -> pl.DataFrame:
    df = pl.read_parquet(DENORM_TABLE_PATH, columns=["sequence", "frame", "frame_density"])
    return df.unique(subset=["sequence", "frame"])


def build_pass4_churn(out_dir: Path = REPORTS_DIR) -> dict[str, Path]:
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
    del all_transitions

    transitions = add_distance_bin(transitions, DISTANCE_BIN_EDGES)

    density = _frame_density_lookup()
    transitions = transitions.join(density, on=["sequence", "frame"], how="left")
    n_unmatched = transitions.filter(pl.col("frame_density").is_null()).height
    if n_unmatched:
        print(f"WARNING: {n_unmatched} transition rows had no frame_density match.", file=sys.stderr)

    written: dict[str, Path] = {}
    out_dir.mkdir(parents=True, exist_ok=True)
    for dim in ["distance_bin", "frame_density"]:
        rates = gta.aggregate_transition_rates(transitions, group_by=["corrupted_condition", dim])
        out_path = out_dir / f"churn_by_condition_{dim}.json"
        rates.write_json(out_path)
        written[dim] = out_path
        print(f"Wrote {out_path} ({len(rates)} cells)")

    return written


if __name__ == "__main__":
    build_pass4_churn()
