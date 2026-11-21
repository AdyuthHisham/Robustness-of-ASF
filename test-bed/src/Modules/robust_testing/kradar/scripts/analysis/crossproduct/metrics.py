#!/usr/bin/env python3
"""Pure aggregation functions for the cross-product analysis. No I/O, no
plotting -- everything here takes/returns plain numbers or numpy arrays so it
can be unit-tested without touching the parquet files.

Reliability floor and orientation-wrap convention are fixed by the Phase 1
audit decisions (see [[exhaustive-crossproduct-phase1-audit]] in
obsidianVault/Knowledge/): N<30 -> "unreliable" (not dropped), N==0 (cell
absent from the real cross-product, e.g. a (weather, environment,
time_of_day) triple that never occurs in any of the 58 sequences) ->
"no_data" (distinct from "tested and noisy"). mAOE wraps mod 2*pi, matching
K-Radar's own AOS formula (full heading, not axis-symmetric).
"""
from __future__ import annotations

import math

import numpy as np

RELIABILITY_FLOOR = 30


def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float | None, float | None]:
    """Wilson score interval for a binomial rate k/n. Returns (None, None)
    for n == 0 -- there is no rate to bound. Preferred over the normal
    (Wald) approximation because it stays inside [0, 1] and doesn't degrade
    at small n or p near 0/1, both of which are common in this dataset's
    long tail of small cells."""
    if n == 0:
        return None, None
    p = k / n
    denom = 1 + z**2 / n
    centre = p + z**2 / (2 * n)
    half_width = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    lo = (centre - half_width) / denom
    hi = (centre + half_width) / denom
    return max(0.0, lo), min(1.0, hi)


def precision_recall_f1(n_tp: int, n_fp: int, n_fn: int) -> dict[str, float | None]:
    """Fixed-threshold P/R/F1 (the primary metrics per Phase 1 decision 1 --
    true unbounded AP is not computable from this table)."""
    n_pred = n_tp + n_fp
    n_gt = n_tp + n_fn
    precision = n_tp / n_pred if n_pred > 0 else None
    recall = n_tp / n_gt if n_gt > 0 else None
    if precision is None or recall is None or (precision + recall) == 0:
        f1 = None
    else:
        f1 = 2 * precision * recall / (precision + recall)
    prec_lo, prec_hi = wilson_ci(n_tp, n_pred)
    rec_lo, rec_hi = wilson_ci(n_tp, n_gt)
    return {
        "precision": precision, "precision_ci_lo": prec_lo, "precision_ci_hi": prec_hi,
        "recall": recall, "recall_ci_lo": rec_lo, "recall_ci_hi": rec_hi,
        "f1": f1,
        "n_pred": n_pred, "n_gt": n_gt,
    }


def angle_error(pred_rad: np.ndarray, gt_rad: np.ndarray) -> np.ndarray:
    """Absolute heading error wrapped to [-pi, pi], mod 2*pi (Phase 1
    decision 4). NOT mod pi -- K-Radar's own AOS similarity
    (1+cos(gt-pred))/2 scores a 180-degree-flipped box 0 (worst), confirming
    orientation here is a genuine heading, not an axis."""
    diff = np.asarray(pred_rad) - np.asarray(gt_rad)
    return np.abs((diff + np.pi) % (2 * np.pi) - np.pi)


def reliability_tag(n: int, floor: int = RELIABILITY_FLOOR) -> str:
    """'no_data' (cell structurally never occurs), 'unreliable' (occurs but
    N <= floor -- keep, tag, never drop), 'reliable' (N > floor)."""
    if n == 0:
        return "no_data"
    if n <= floor:
        return "unreliable"
    return "reliable"


def retention_ratio(corrupted: float | None, original: float | None) -> float | None:
    """corrupted / original, guarding against a zero or missing baseline
    (a delta against a zero/absent baseline is undefined, not infinite)."""
    if corrupted is None or original is None or original == 0:
        return None
    return corrupted / original


def absolute_delta(corrupted: float | None, original: float | None) -> float | None:
    if corrupted is None or original is None:
        return None
    return corrupted - original
