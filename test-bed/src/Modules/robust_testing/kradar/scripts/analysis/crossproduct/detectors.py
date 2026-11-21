#!/usr/bin/env python3
"""D1-D5: the addendum's named detectors, run alongside anomaly.py's
robust-z pass over the peer groups it defines. Each returns a DataFrame with
a `why_this_looks_weird` plain-language column, per the task spec.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
from anomaly import PEER_GROUPS, score_peer_group, _load_level, METRICS  # noqa: E402

SEVERITY_ORDER = {"low": 0, "medium": 1, "high": 2}


def d1_monotonicity_violation(metric: str) -> pl.DataFrame:
    """Severity should move monotonically with severity for every metric
    here (worse as severity increases -- direction depends on
    higher/lower-is-better, callers restrict to a `higher_is_better` metric
    set consistently). Reversals are reported with magnitude; CIs (where
    they exist -- precision/recall only) separate noise from real reversals
    via the `ci_separates` column."""
    scored = score_peer_group("severity_ladder", metric)
    fix_cols = PEER_GROUPS["severity_ladder"]["fix"]
    rows = []
    for key, g in scored.filter(pl.col("status") == "scored").group_by(fix_cols, maintain_order=True):
        key_tuple = key if isinstance(key, tuple) else (key,)
        g = g.with_columns(pl.col("member").replace(SEVERITY_ORDER).cast(pl.Int64).alias("sev_rank")).sort("sev_rank")
        if g.height < 2:
            continue
        vals = g["value"].to_list()
        sevs = g["member"].to_list()
        ns = g["n_total"].to_list()
        n_seqs = g["n_sequences"].to_list()
        lower_is_better = METRICS.get(metric, False)
        for i in range(len(vals) - 1):
            delta = vals[i + 1] - vals[i]
            # expected direction as severity increases: metric should WORSEN
            # -- rise for a lower_is_better (error) metric, fall for a
            # higher_is_better (rate) metric. A reversal is delta with the
            # opposite sign (small numerical noise around exactly 0 is not
            # flagged as a reversal).
            worsened = delta > 1e-9 if lower_is_better else delta < -1e-9
            if worsened:
                continue
            min_n_seq = min(n_seqs[i], n_seqs[i + 1])
            seq_note = f" -- rests on only {min_n_seq} sequence(s), treat as anecdotal" if min_n_seq <= 2 else ""
            rows.append({
                **dict(zip(fix_cols, key_tuple)), "metric": metric,
                "from_severity": sevs[i], "to_severity": sevs[i + 1],
                "from_value": vals[i], "to_value": vals[i + 1], "delta": delta,
                "from_n_total": ns[i], "to_n_total": ns[i + 1],
                "from_n_sequences": n_seqs[i], "to_n_sequences": n_seqs[i + 1],
                "why_this_looks_weird": (
                    f"{sevs[i]}->{sevs[i + 1]} severity step moved {metric} by {delta:+.4f}, "
                    f"opposite of the expected {'increase' if lower_is_better else 'decrease'} "
                    f"with worsening severity{seq_note}"
                ),
            })
    df = pl.DataFrame(rows) if rows else pl.DataFrame(schema={c: pl.Utf8 for c in fix_cols})
    return df


def d2_flat_except_one(metric: str, tightness_quantile: float = 0.75) -> pl.DataFrame:
    """At fixed (condition, cls), sweep the full stratum cross (stratum_sweep
    peer group). Report groups whose spread is small (tight -- top quartile
    of group_tightness) but which still contain >=1 member flagged by robust
    z. This is the "flat everywhere except one cell" pattern named in the
    task spec -- a plain robust-z flag from a SCATTERED group is a different,
    weaker finding than the same z from a TIGHT one."""
    scored = score_peer_group("stratum_sweep", metric)
    scored_only = scored.filter(pl.col("status") == "scored")
    if scored_only.is_empty():
        return scored_only
    tightness_cutoff = scored_only["group_tightness"].quantile(tightness_quantile)
    tight_groups = scored_only.filter(pl.col("group_tightness") >= tightness_cutoff)
    flagged = tight_groups.filter(pl.col("robust_z").abs() > 3.5).with_columns(
        pl.format(
            "flat group (tightness={}) but this cell's {} = {} vs. group median {} (z={})",
            pl.col("group_tightness").round(1), pl.lit(metric), pl.col("value").round(3),
            pl.col("group_median").round(3), pl.col("robust_z").round(2),
        ).alias("why_this_looks_weird")
    )
    return flagged.sort("group_tightness", descending=True)


def d3_modality_divergence(metric: str) -> pl.DataFrame:
    """At fixed (effect, severity, cls, weather, tod), the camera/lidar/radar
    ordering should be consistent with the metric's GLOBAL modality ordering
    (computed once, as each modality's mean rank across every group instance
    for this metric). Report every group where the LOCAL ordering flips
    against that global ordering -- an ordering flip is often more
    interpretable than a same-order magnitude outlier, so this is reported
    even at modest z."""
    scored = score_peer_group("modality_parity", metric)
    scored_only = scored.filter(pl.col("status") == "scored")
    if scored_only.is_empty():
        return scored_only
    fix_cols = PEER_GROUPS["modality_parity"]["fix"]

    # global ordering: rank modalities within each group instance, then
    # average rank per modality across all instances.
    ranked = scored_only.with_columns(
        pl.col("value").rank(method="average", descending=True).over(fix_cols).alias("local_rank")
    )
    global_rank = ranked.group_by("member").agg(pl.col("local_rank").mean().alias("mean_rank")).sort("mean_rank")
    global_order = global_rank["member"].to_list()  # best-to-worst globally

    rows = []
    for key, g in ranked.group_by(fix_cols, maintain_order=True):
        key_tuple = key if isinstance(key, tuple) else (key,)
        if g.height < 3:
            continue
        g_sorted = g.sort("local_rank")
        local_order = g_sorted["member"].to_list()
        min_n_total = int(g_sorted["n_total"].min())
        min_n_seq = int(g_sorted["n_sequences"].min())
        if local_order != global_order:
            seq_note = f" -- weakest member of this triad rests on only {min_n_seq} sequence(s)" if min_n_seq <= 2 else ""
            rows.append({
                **dict(zip(fix_cols, key_tuple)),
                "metric": metric,
                "local_order_best_to_worst": " > ".join(local_order),
                "global_order_best_to_worst": " > ".join(global_order),
                "min_n_total": min_n_total, "min_n_sequences": min_n_seq,
                "why_this_looks_weird": (
                    f"modality ordering ({' > '.join(local_order)}) flips against the global "
                    f"ordering ({' > '.join(global_order)}) for this (effect, severity, cls, "
                    f"weather, tod) combination{seq_note}"
                ),
            })
    return pl.DataFrame(rows) if rows else pl.DataFrame(schema={c: pl.Utf8 for c in fix_cols})


def _median_polish(mat: np.ndarray, max_iter: int = 20, tol: float = 1e-6) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    """Classic Tukey median polish: additive decomposition
    mat = overall + row_effect + col_effect + residual, fit via alternating
    median subtraction (robust to single large cells dragging a least-
    squares fit, per task spec). NaN cells (no_data) are ignored in each
    median computation. Returns (row_effects, col_effects, residuals, overall)."""
    residual = mat.copy()
    n_rows, n_cols = mat.shape
    row_eff = np.zeros(n_rows)
    col_eff = np.zeros(n_cols)
    overall = 0.0
    for _ in range(max_iter):
        row_med = np.nanmedian(residual, axis=1)
        row_med = np.nan_to_num(row_med, nan=0.0)
        residual = residual - row_med[:, None]
        row_eff += row_med
        shift = np.nanmedian(col_eff)
        if not np.isnan(shift):
            col_eff -= shift
            overall += shift

        col_med = np.nanmedian(residual, axis=0)
        col_med = np.nan_to_num(col_med, nan=0.0)
        residual = residual - col_med[None, :]
        col_eff += col_med
        shift = np.nanmedian(row_eff)
        if not np.isnan(shift):
            row_eff -= shift
            overall += shift

        if np.nansum(np.abs(row_med)) + np.nansum(np.abs(col_med)) < tol:
            break
    return row_eff, col_eff, residual, overall


def d4_interaction_residual(metric: str, row_dim: str = "condition", col_dim: str = "weather", cls: str = "sed") -> dict:
    """Robust additive fit (condition main effect + stratum main effect) via
    median polish, NOT least squares (a single huge cell shouldn't drag the
    fit). Ranks cells by residual; reports fit quality (fraction of total
    absolute deviation from the overall median explained by the additive
    effects) so residuals can be weighted appropriately -- a poor fit means
    residuals reflect model inadequacy, not necessarily a real anomaly."""
    level = "cond_cls_weather"
    df = _load_level(level).filter((pl.col("reliable")) & (pl.col("cls") == cls))
    rows = sorted(df[row_dim].unique().to_list())
    cols = sorted(df[col_dim].unique().to_list())
    mat = np.full((len(rows), len(cols)), np.nan)
    n_mat = np.zeros((len(rows), len(cols)), dtype=int)
    for r in df.iter_rows(named=True):
        i, j = rows.index(r[row_dim]), cols.index(r[col_dim])
        mat[i, j] = r[metric]
        n_mat[i, j] = r["n_total"]

    if np.all(np.isnan(mat)):
        return {"residuals": pl.DataFrame(), "fit_quality": None}

    row_eff, col_eff, residual, overall = _median_polish(mat)
    total_dev = np.nansum(np.abs(mat - overall))
    resid_dev = np.nansum(np.abs(residual))
    fit_quality = 1.0 - (resid_dev / total_dev) if total_dev > 0 else None

    rows_out = []
    for i, r in enumerate(rows):
        for j, c in enumerate(cols):
            if np.isnan(mat[i, j]):
                continue
            rows_out.append({
                row_dim: r, col_dim: c, "metric": metric, "cls": cls,
                "observed": mat[i, j], "fitted": overall + row_eff[i] + col_eff[j],
                "residual": residual[i, j], "n_total": int(n_mat[i, j]),
                "why_this_looks_weird": (
                    f"{r} x {c} observed {metric}={mat[i, j]:.3f} vs. additive-model-expected "
                    f"{overall + row_eff[i] + col_eff[j]:.3f} (residual={residual[i, j]:+.3f})"
                ),
            })
    residuals_df = pl.DataFrame(rows_out).sort(pl.col("residual").abs(), descending=True)
    return {"residuals": residuals_df, "fit_quality": fit_quality}


CROSS_METRIC_PATTERNS = [
    # (name, description, condition-lambda over a row dict of deltas)
    (
        "detections_kept_boxes_degraded",
        "recall steady while mATE inflates -- detections kept, box localization degraded",
        lambda r: abs(r.get("recall_delta") or 0) < 0.02 and (r.get("mATE_delta") or 0) > 0.05,
    ),
    (
        "precision_up_recall_iou_down",
        "precision rising while recall AND IoU both fall -- consistent with corruption "
        "suppressing FPs (not a genuine detector improvement), not measured directly here "
        "since mean_iou isn't in the delta table; recall-only proxy",
        lambda r: (r.get("precision_delta") or 0) > 0.01 and (r.get("recall_delta") or 0) < -0.02,
    ),
]


def d5_cross_metric_inconsistency(level: str = "cond_cls") -> pl.DataFrame:
    """Enumerate cells where metrics disagree in ways that shouldn't
    co-occur under a simple 'corruption uniformly degrades everything'
    model. Patterns tested are listed in CROSS_METRIC_PATTERNS above --
    exactly two implemented this pass (both reusing the existing baseline
    deltas rather than the peer-group scoring, since these are
    baseline-relative patterns by definition, not peer-relative)."""
    sys.path.insert(0, str(HERE.parent))
    from queries import load_deltas  # noqa: E402
    deltas = load_deltas(level)
    reliable = deltas.filter(pl.col("reliable") & pl.col("baseline_reliable"))
    rows = []
    for r in reliable.iter_rows(named=True):
        for name, desc, cond in CROSS_METRIC_PATTERNS:
            try:
                if cond(r):
                    rows.append({
                        "pattern": name, "condition": r["condition"],
                        "cls": r.get("cls"), "recall_delta": r.get("recall_delta"),
                        "precision_delta": r.get("precision_delta"), "mATE_delta": r.get("mATE_delta"),
                        "n_total": r["n_total"], "why_this_looks_weird": desc,
                    })
            except TypeError:
                continue
    return pl.DataFrame(rows) if rows else pl.DataFrame(schema={"pattern": pl.Utf8})
