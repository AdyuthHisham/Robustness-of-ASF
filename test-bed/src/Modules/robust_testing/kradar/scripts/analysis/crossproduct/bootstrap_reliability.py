#!/usr/bin/env python3
"""Shared bootstrap-CI utility for stratified mAP, reused by every
stratifier (weather/environment/time_of_day/frame_density/distance_bucket)
instead of per-stratifier bootstrap code.

Phase 1 decision (approved): BLOCK bootstrap by `sequence`, not row-level.
Weather/environment/time_of_day are fixed per sequence (see metrics.py's
_counts_and_rates docstring in crossproduct.py) -- row-level resampling
would treat frames from one sequence as independent draws and understate CI
width exactly where n_sequences is small, which is the case the reliability
floor exists to catch. Each bootstrap iteration resamples sequence IDs
within the cell with replacement, then takes ALL rows belonging to each
drawn sequence (with repeats), and recomputes AP.

AP itself is K-Radar's own eval_revised.py thresholding/interpolation,
identical to ap_metrics.compute_ap (same _get_thresholds import) --
`_ap_from_arrays` below is that same logic re-expressed on plain NumPy
arrays instead of a per-call Polars DataFrame. This is a PERFORMANCE fix,
not a metric change: the original version called ap_metrics.compute_ap
(which filters/sorts/converts a Polars DataFrame) once per bootstrap
iteration -- with ~1,400 cells x 1,000 iterations that meant ~1.4M Polars
DataFrame constructions for data that fits in a few NumPy arrays,
which was the actual bottleneck (concat/filter overhead per call, not the
statistics). Per-sequence (score, is_tp) arrays and per-sequence num_gt are
computed ONCE per cell; each bootstrap iteration only does an integer
resample + np.concatenate + the same thresholding math.

Reliability floor (Phase 1 audit + this task's spec): N_rows > 30 AND
N_sequences > 10 -> "reliable"; occurs but fails either floor ->
"unreliable"; cell absent entirely -> "no_data". Extends
crossproduct/metrics.py's row-only RELIABILITY_FLOOR with the sequence
floor requested for this task without changing that module (other callers
of reliability_tag are untouched).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[8] / "repos" / "K-Radar" / "scripts" / "alvis"))
from ap_metrics import N_SAMPLE_PTS, _get_thresholds  # noqa: E402

N_ROW_FLOOR = 30
N_SEQ_FLOOR = 10
N_BOOTSTRAP = 1000


def reliability_flag(n_rows: int, n_sequences: int) -> str:
    if n_rows == 0:
        return "no_data"
    if n_rows <= N_ROW_FLOOR or n_sequences <= N_SEQ_FLOOR:
        return "unreliable"
    return "reliable"


def _ap_from_arrays(det_scores: np.ndarray, det_is_tp: np.ndarray, num_gt: int) -> float:
    """Same math as ap_metrics.compute_ap, minus the Polars I/O. `det_scores`/
    `det_is_tp` cover TP+FP detection rows only (FN rows carry no score and
    contribute only to num_gt, handled by the caller)."""
    if num_gt == 0:
        return 0.0  # only reached via pooled-sequence draws; per-cell guard below handles the real zero-GT case
    tp_scores = det_scores[det_is_tp]
    thresholds = _get_thresholds(tp_scores, num_gt, N_SAMPLE_PTS)
    if not thresholds:
        return 0.0

    order = np.argsort(-det_scores)
    sorted_scores = det_scores[order]
    sorted_is_tp = det_is_tp[order]
    cum_tp = np.cumsum(sorted_is_tp)
    cum_fp = np.cumsum(~sorted_is_tp)

    precisions = np.zeros(len(thresholds))
    for k, t in enumerate(thresholds):
        idx = np.searchsorted(-sorted_scores, -t, side="right") - 1
        if idx < 0:
            continue
        tp_at_t, fp_at_t = cum_tp[idx], cum_fp[idx]
        precisions[k] = tp_at_t / (tp_at_t + fp_at_t) if (tp_at_t + fp_at_t) > 0 else 0.0

    for k in range(len(precisions) - 2, -1, -1):
        precisions[k] = max(precisions[k], precisions[k + 1])

    return float(np.sum(precisions) / N_SAMPLE_PTS * 100.0)


def bootstrap_map_cell(
    cell_rows: pl.DataFrame, seed: int, n_iter: int = N_BOOTSTRAP
) -> dict:
    """One (condition, cls|pooled, factor-level) cell. `cell_rows` must carry
    is_tp/is_fp/is_fn/score/sequence (ingest.py's row schema). Returns
    map_point/map_ci_low/map_ci_high/map_ci_width/n_rows/n_sequences/
    reliability_flag -- the dual-denominator + CI contract for every caller."""
    n_rows = cell_rows.height
    sequences = cell_rows["sequence"].unique().to_list()
    n_sequences = len(sequences)
    flag = reliability_flag(n_rows, n_sequences)

    if n_rows == 0:
        return {
            "map_point": None, "map_ci_low": None, "map_ci_high": None,
            "map_ci_width": None, "n_rows": 0, "n_sequences": 0,
            "reliability_flag": flag,
        }

    # Precompute per-sequence NumPy arrays ONCE -- the bootstrap loop below
    # never touches Polars again.
    seq_scores: dict = {}
    seq_is_tp: dict = {}
    seq_num_gt: dict = {}
    for s in sequences:
        srows = cell_rows.filter(pl.col("sequence") == s)
        dets = srows.filter(pl.col("is_tp") | pl.col("is_fp"))
        seq_scores[s] = dets["score"].fill_null(0.0).to_numpy()
        seq_is_tp[s] = dets["is_tp"].to_numpy()
        seq_num_gt[s] = int(srows["is_tp"].sum()) + int(srows["is_fn"].sum())

    full_num_gt = sum(seq_num_gt.values())
    if full_num_gt == 0:
        return {
            "map_point": None, "map_ci_low": None, "map_ci_high": None,
            "map_ci_width": None, "n_rows": n_rows, "n_sequences": n_sequences,
            "reliability_flag": flag,
        }
    all_scores = np.concatenate([seq_scores[s] for s in sequences]) if any(len(seq_scores[s]) for s in sequences) else np.array([])
    all_is_tp = np.concatenate([seq_is_tp[s] for s in sequences]) if any(len(seq_is_tp[s]) for s in sequences) else np.array([], dtype=bool)
    point = _ap_from_arrays(all_scores, all_is_tp, full_num_gt)

    rng = np.random.default_rng(seed)
    seq_arr = np.array(sequences)
    boot_aps = np.empty(n_iter)
    for i in range(n_iter):
        draw = rng.choice(seq_arr, size=n_sequences, replace=True)
        scores = np.concatenate([seq_scores[s] for s in draw])
        is_tp = np.concatenate([seq_is_tp[s] for s in draw])
        num_gt = sum(seq_num_gt[s] for s in draw)
        boot_aps[i] = _ap_from_arrays(scores, is_tp, num_gt) if num_gt > 0 else 0.0

    ci_low, ci_high = np.percentile(boot_aps, [2.5, 97.5])
    return {
        "map_point": point,
        "map_ci_low": float(ci_low),
        "map_ci_high": float(ci_high),
        "map_ci_width": float(ci_high - ci_low),
        "n_rows": n_rows,
        "n_sequences": n_sequences,
        "reliability_flag": flag,
    }


def bootstrap_map_grouped(
    df: pl.DataFrame, group_cols: list[str], seed: int = 42, n_iter: int = N_BOOTSTRAP
) -> pl.DataFrame:
    """Grouped version: one bootstrap_map_cell per distinct group_cols
    combination present in df. Seed is derived deterministically per cell
    (seed + stable hash of the cell's key tuple) so results are reproducible
    across reruns regardless of group iteration order."""
    rows = []
    for key_vals, cell in df.group_by(group_cols, maintain_order=True):
        cell_seed = seed + (abs(hash(key_vals)) % 10_000)
        stats = bootstrap_map_cell(cell, seed=cell_seed, n_iter=n_iter)
        row = dict(zip(group_cols, key_vals))
        row.update(stats)
        rows.append(row)
    return pl.DataFrame(rows)
