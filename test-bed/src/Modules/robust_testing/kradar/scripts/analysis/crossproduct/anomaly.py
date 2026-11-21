#!/usr/bin/env python3
"""Peer-group anomaly detection (the addendum's second detection mode --
supersedes and satisfies the parent prompt's Q7; do not also run
queries.q7_anomalies for the same purpose).

Every OTHER deliverable in this analysis measures a cell against `original`.
This module measures a cell against its PEERS -- the set of cells expected
to behave alike. Distance from baseline is not the signal here; distance
from the peer cluster is.

Resolved Phase-1-addendum decisions this module implements directly:
  - A2: frame_density keeps the existing 3-bin {1, 2-3, 4+} scheme.
  - Detection gate: SINGLE-GATE. Robust z-score is the actual filter;
    CI-overlap is computed and recorded (precision/recall only -- no CI
    exists for f1/AP/error metrics) but never used to suppress a flag. A4's
    audit found 78%/52% of precision/recall cells have a CI wider than 2x
    the typical peer-group spread -- a double gate would have suppressed
    almost every real finding.
  - A1.5b (cross-stratum hold-all-but-weather) redefined looser: pools over
    frame_density too (fix condition+cls+environment+distance_bucket+tod,
    vary weather) rather than run as originally specified, which had 0%
    viable groups.
  - Severity ladder (49% viable) and cross-stratum-by-tod (5% viable) are
    run anyway, exclusions reported in the coverage statement -- maximal
    inclusion per the addendum's convention, not silently narrowed.

Center/spread is ALWAYS median/scaled-MAD, never mean/SD (contamination by
the very outlier being searched for). MAD==0 falls back to a stated
absolute floor rather than dividing by zero.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
from crossproduct import load_scoped_table, MARGINALIZATIONS, SUMMARY_OUT_DIR  # noqa: E402

MAD_SCALE = 1.4826
ROBUST_Z_THRESHOLD = 3.5  # Iglewicz & Hoaglin's conventional modified-z cutoff
MIN_MEMBERS = 4  # below this, mark the group `insufficient` and skip scoring
RELIABLE_FLOOR = 100  # DEAD CODE (verified 2026-09-01, grepped: never
# referenced anywhere in this file or imported elsewhere). The floor
# actually in effect is metrics.RELIABILITY_FLOOR (=30, see crossproduct.py's
# reliability_tag() call), which feeds the `reliable` boolean column this
# module reads at line ~136. Left in place rather than deleted -- flag for a
# human decision on whether to remove it or wire it in; a second
# same-named-in-spirit constant sitting at the old wrong value (100) right
# next to the real one is exactly the kind of thing that caused the
# RELIABILITY_FLOOR regression this session found and fixed.

# metric -> lower_is_better
METRICS = {
    "precision": False, "recall": False, "f1": False, "ap_restricted_range": False,
    "mATE": True, "mASE": True, "mAOE": True,
}

# Absolute MAD floor per metric, used only when the group's scaled MAD is
# exactly 0 (all members identical) -- prevents a division by zero from
# turning a trivial numerical tie into an infinite z-score. Chosen as a
# small fraction of each metric's natural range (rates are in [0,1]; error
# metrics are in meters/dimensionless-ratio/radians respectively).
MAD_FLOOR = {
    "precision": 0.005, "recall": 0.005, "f1": 0.005, "ap_restricted_range": 0.5,
    "mATE": 0.01, "mASE": 0.005, "mAOE": 0.01,
}

# Peer-group definitions: name -> (fix_cols, vary_col, summary_level to read).
# `min_members` overrides MIN_MEMBERS where a group can never have 4 members
# by construction (modality parity = 3, severity ladder = 3).
PEER_GROUPS: dict[str, dict] = {
    "sibling_conditions": {
        "fix": ["cls", "weather", "time_of_day"], "vary": "condition",
        "level": "cond_cls_weather_tod", "min_members": 4,
    },
    "modality_parity": {
        "fix": ["effect", "severity", "cls", "weather", "time_of_day"], "vary": "modality",
        "level": "cond_cls_weather_tod", "min_members": 3,
    },
    "severity_ladder": {
        "fix": ["modality", "effect", "cls", "weather", "time_of_day"], "vary": "severity",
        "level": "cond_cls_weather_tod", "min_members": 3,
    },
    "stratum_sweep": {
        "fix": ["condition", "cls"], "vary": "stratum_cell",
        "level": "full_density", "min_members": 4,
    },
    "cross_stratum_tod": {
        "fix": ["condition", "cls", "weather", "environment", "distance_bucket"], "vary": "time_of_day",
        "level": "full", "min_members": 2,
    },
    # A1.5b, redefined looser per user decision: pool over frame_density too
    # (0% viable as originally specified -- fix EVERYTHING but weather).
    # min_members=3, not 4: even after loosening, at most 3 of the 5
    # possible weather values ever co-occur with N>=30 while holding
    # condition+cls+environment+distance_bucket+tod fixed (checked
    # empirically -- 1062 groups top out at 1, 318 at 2, 154 at 3, zero at
    # 4 or 5; re-verified 2026-09-01 after correcting the reliability floor
    # from a since-fixed N>=100 regression back to the documented N>=30 --
    # the ceiling of 3 is structural (driven by which sequences share a
    # stratum), not floor-sensitive). Requiring 4 here would silently zero out this entire peer
    # group; 3 is the actual achievable ceiling, reported as such rather
    # than forcing an unmeetable threshold.
    "cross_stratum_weather": {
        "fix": ["condition", "cls", "environment", "distance_bucket", "time_of_day"], "vary": "weather",
        "level": "full", "min_members": 3,
    },
}


def _mad_scaled(values: np.ndarray, metric: str) -> tuple[float, float]:
    """(median, scaled MAD). Falls back to MAD_FLOOR[metric] when MAD==0
    (all members numerically tied) rather than dividing by zero."""
    med = float(np.median(values))
    mad = MAD_SCALE * float(np.median(np.abs(values - med)))
    if mad == 0:
        mad = MAD_FLOOR[metric]
    return med, mad


def _load_level(level: str) -> pl.DataFrame:
    df = pl.read_parquet(SUMMARY_OUT_DIR / f"summary_{level}.parquet")
    if level == "full_density":
        df = df.with_columns(
            pl.concat_str(["weather", "environment", "distance_bucket", "frame_density", "time_of_day"], separator="|")
            .alias("stratum_cell")
        )
    return df


def score_peer_group(group_name: str, metric: str) -> pl.DataFrame:
    """One row per (group instance, member) with robust z, CI-overlap flag
    (where available), group tightness, and a `status` of
    scored/insufficient. Never mixes metrics of different scale/polarity --
    call once per metric."""
    spec = PEER_GROUPS[group_name]
    fix_cols, vary_col, level = spec["fix"], spec["vary"], spec["level"]
    min_members = spec["min_members"]
    df = _load_level(level)
    if metric not in df.columns:
        raise ValueError(f"{metric} not in summary_{level} columns")

    reliable = df.filter(pl.col("reliable"))
    has_ci = f"{metric}_ci_lo" in df.columns

    rows = []
    for key, g in reliable.group_by(fix_cols, maintain_order=True):
        key_tuple = key if isinstance(key, tuple) else (key,)
        g = g.filter(pl.col(metric).is_not_null())
        n_members = g.height
        if n_members < min_members:
            for r in g.iter_rows(named=True):
                rows.append({
                    **dict(zip(fix_cols, key_tuple)), "peer_group": group_name, "metric": metric,
                    "member": r[vary_col], "value": r[metric], "n_total": r["n_total"],
                    "n_sequences": r.get("n_sequences"),
                    "status": "insufficient", "n_members_in_group": n_members,
                    "group_median": None, "group_mad": None, "robust_z": None,
                    "ci_overlaps_median": None, "group_tightness": None,
                })
            continue

        values = g[metric].to_numpy()
        med, mad = _mad_scaled(values, metric)
        # group tightness: MAD relative to |median| (coefficient-of-variation
        # style) -- a tight group has a small ratio, so 1/ratio ranks tight
        # groups above scattered ones when multiplied by member deviation.
        tightness = 1.0 / (mad / (abs(med) + 1e-9))

        for r in g.iter_rows(named=True):
            v = r[metric]
            z = (v - med) / mad
            ci_overlap = None
            if has_ci:
                lo, hi = r.get(f"{metric}_ci_lo"), r.get(f"{metric}_ci_hi")
                if lo is not None and hi is not None:
                    ci_overlap = lo <= med <= hi
            rows.append({
                **dict(zip(fix_cols, key_tuple)), "peer_group": group_name, "metric": metric,
                "member": r[vary_col], "value": v, "n_total": r["n_total"],
                "n_sequences": r.get("n_sequences"),
                "status": "scored", "n_members_in_group": n_members,
                "group_median": med, "group_mad": mad, "robust_z": z,
                "ci_overlaps_median": ci_overlap, "group_tightness": tightness,
            })
    return pl.DataFrame(rows) if rows else pl.DataFrame(
        schema={c: pl.Utf8 for c in fix_cols} | {"peer_group": pl.Utf8, "metric": pl.Utf8}
    )


def flag_anomalies(scored: pl.DataFrame, z_threshold: float = ROBUST_Z_THRESHOLD) -> pl.DataFrame:
    """Single-gate: |robust_z| > threshold flags. CI-overlap is carried as
    a column for context, never used to filter (Phase-1-addendum decision,
    see module docstring)."""
    scored_only = scored.filter(pl.col("status") == "scored")
    if scored_only.is_empty():
        return scored_only
    flagged = scored_only.filter(pl.col("robust_z").abs() > z_threshold)
    return flagged.with_columns(
        (pl.col("group_tightness") * pl.col("robust_z").abs()).alias("rank_score")
    ).sort("rank_score", descending=True)


def run_all_peer_groups(metric: str) -> dict[str, pl.DataFrame]:
    return {name: score_peer_group(name, metric) for name in PEER_GROUPS}


SMALL_N_CEILING = 90  # a flagged cell just above the N>=30 reliability
# floor is still a plausible small-N artifact even though it clears the
# floor -- this is a soft second tier, not a re-litigation of the floor.
# 3x the reliability floor (metrics.RELIABILITY_FLOOR=30), same ratio as
# the original 300-at-floor-100 pairing -- rescaled 2026-09-01 by user
# decision after the floor regression (100->30) was corrected, to preserve
# the intended 3x-floor relationship rather than leave a now-10x-floor gap.
SEQUENCE_CONFOUND_CEILING = 2  # a cell backed by <=2 distinct sequences is
# pseudo-replicated regardless of its row count -- weather/environment/tod
# are fixed PER SEQUENCE (confirmed on all 58 sequences), so hundreds of
# rows from 1-2 sequences are hundreds of correlated draws from the same
# underlying scene(s), not independent evidence. This is a harder ceiling
# than SMALL_N_CEILING because no amount of additional rows from the SAME
# sequences fixes it.


def classify_anomaly(row: dict, metric: str) -> str:
    """Three-way split per task spec:
      - 'suspected_bug': an impossibly good/perfect value at low-moderate N,
        or a value outside the metric's valid range -- more likely a
        matching/join/parsing bug than a discovery.
      - 'small_n_artifact': N clears the reliability floor but is still
        close to it (< SMALL_N_CEILING), the peer group itself has the bare
        minimum member count, OR the cell rests on <=2 distinct sequences
        (row count is pseudo-replicated, not real N, in that case) --
        each inflates variance and shrinks the MAD estimate itself, which
        can manufacture large robust-z values from ordinary sampling noise
        or from a single unusual sequence rather than a general effect.
      - 'real': survives all checks.
    Maximal inclusion, not conservative omission -- every category is
    reported, none silently dropped.
    """
    value = row.get("value")
    n_total = row.get("n_total") or 0
    n_sequences = row.get("n_sequences")
    n_members = row.get("n_members_in_group") or 0
    min_members = PEER_GROUPS[row["peer_group"]]["min_members"]

    # Only a SUSPICIOUSLY PERFECT score is bug-like -- 0.0 is a legitimate,
    # mechanistically expected outcome under e.g. total sensor loss on a
    # rare class (lidar_loss_complete_zero + bus + adverse weather really
    # can produce 0 detections; that's a finding, not a bug). A value at or
    # near 1.0 with only a handful of predictions/GT backing it is the
    # actual red flag -- e.g. 1/1 correct is not evidence of a robust
    # detector, it's evidence of too little data to conclude anything.
    if metric in ("precision", "recall", "f1") and value is not None and value >= 0.999 and n_total < 200:
        return "suspected_bug"
    if metric == "ap_restricted_range" and value is not None and (value < 0 or value > 100):
        return "suspected_bug"
    if n_sequences is not None and n_sequences <= SEQUENCE_CONFOUND_CEILING:
        return "small_n_artifact"
    if n_total < SMALL_N_CEILING or n_members <= min_members:
        return "small_n_artifact"
    return "real"


def build_anomalies_table(metrics: list[str] | None = None) -> pl.DataFrame:
    """One row per flagged cell across every (peer_group, metric) combo --
    the `anomalies.parquet`/`.csv` output. Includes the three-way
    real/small_n_artifact/suspected_bug classification and a plain-language
    diagnostic note."""
    if metrics is None:
        metrics = list(METRICS)
    all_flagged = []
    for metric in metrics:
        for group_name in PEER_GROUPS:
            scored = score_peer_group(group_name, metric)
            flagged = flag_anomalies(scored)
            if flagged.is_empty():
                continue
            fix_cols = PEER_GROUPS[group_name]["fix"]
            for r in flagged.iter_rows(named=True):
                category = classify_anomaly(r, metric)
                direction = "higher" if r["value"] > r["group_median"] else "lower"
                # peer groups have different fix_cols (e.g. "modality" exists
                # for modality_parity but not sibling_conditions) -- flatten
                # the group-defining keys into one string column instead of
                # concatenating rows with mismatched top-level schemas.
                group_key = ", ".join(f"{c}={r[c]}" for c in fix_cols)
                n_seq = r.get("n_sequences")
                seq_note = f", backed by only {n_seq} sequence(s) -- pseudo-replicated, treat as anecdotal" if (n_seq is not None and n_seq <= SEQUENCE_CONFOUND_CEILING) else ""
                note = (
                    f"[{group_name}] {metric} for member='{r['member']}' ({group_key}) is {direction} "
                    f"than its {r['n_members_in_group']}-member peer group's median "
                    f"({r['group_median']:.4f}) by robust z={r['robust_z']:.2f} "
                    f"(value={r['value']:.4f}, N_rows={r['n_total']}, N_sequences={n_seq}{seq_note})"
                )
                all_flagged.append({
                    "peer_group": group_name, "metric": metric, "group_key": group_key,
                    "member": r["member"], "value": r["value"], "group_median": r["group_median"],
                    "group_mad": r["group_mad"], "robust_z": r["robust_z"],
                    "ci_overlaps_median": r.get("ci_overlaps_median"),
                    "n_total": r["n_total"], "n_sequences": n_seq,
                    "n_members_in_group": r["n_members_in_group"],
                    "group_tightness": r["group_tightness"], "rank_score": r["rank_score"],
                    "category": category, "diagnostic_note": note,
                })
    # infer_schema_length=None: `ci_overlaps_median` is None for most of the
    # first 100 rows (only precision/recall carry a CI) -- polars' default
    # 100-row schema inference sees an all-null column, then chokes when a
    # later row supplies a real bool. Scan every row for schema inference.
    return (
        pl.DataFrame(all_flagged, infer_schema_length=None)
        if all_flagged
        else pl.DataFrame(schema={"peer_group": pl.Utf8, "metric": pl.Utf8})
    )


def coverage_statement(metric: str) -> pl.DataFrame:
    """Fraction of each peer-group's instances that were scored vs.
    insufficient -- without this, absence of anomalies in a region is
    uninterpretable (task spec)."""
    rows = []
    for name in PEER_GROUPS:
        scored = score_peer_group(name, metric)
        if scored.is_empty():
            rows.append({"peer_group": name, "metric": metric, "n_group_instances": 0, "n_scored": 0, "n_insufficient": 0, "pct_scored": None})
            continue
        by_status = scored.group_by(PEER_GROUPS[name]["fix"] + ["status"]).agg(pl.len())
        insts = scored.select(PEER_GROUPS[name]["fix"]).unique()
        status_per_inst = scored.group_by(PEER_GROUPS[name]["fix"]).agg(pl.col("status").first())
        n_total = status_per_inst.height
        n_scored = status_per_inst.filter(pl.col("status") == "scored").height
        rows.append({
            "peer_group": name, "metric": metric,
            "n_group_instances": n_total, "n_scored": n_scored,
            "n_insufficient": n_total - n_scored,
            "pct_scored": n_scored / n_total if n_total else None,
        })
    return pl.DataFrame(rows)


def full_coverage_statement(metrics: list[str] | None = None) -> pl.DataFrame:
    """Coverage across every (peer_group, metric) combo -- without this,
    absence of anomalies in a region is uninterpretable (task spec)."""
    if metrics is None:
        metrics = list(METRICS)
    return pl.concat([coverage_statement(m) for m in metrics])


if __name__ == "__main__":
    for metric in ["ap_restricted_range", "precision", "recall", "mATE"]:
        print(f"\n=== {metric} ===")
        cov = coverage_statement(metric)
        print(cov)
        for name in PEER_GROUPS:
            scored = score_peer_group(name, metric)
            flagged = flag_anomalies(scored)
            print(f"  {name}: {scored.filter(pl.col('status')=='scored').height} scored, {flagged.height} flagged")
