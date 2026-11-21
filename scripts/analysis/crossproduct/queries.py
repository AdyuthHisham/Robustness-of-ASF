#!/usr/bin/env python3
"""One function per deliverable question, each returning a ranked
polars.DataFrame sliced from the pre-built summary/delta tables -- never
rescanning the 1.1M raw rows. Every table keeps N and reliability tags;
reliable/unreliable are reported as SEPARATE frames, never merged into one
ranking (Phase 1 decision 5 + task spec's "never mixed" rule).

Q1 (beats baseline), Q2 (highest/lowest per metric), Q3 (most false
predictions), Q4 (max FP+FN jointly), Q5 (churn -- reuses the cached
gt_transition_analysis.py output from the prior exploratory pass rather than
rerunning its matcher, see q5's docstring), Q6 (loss_complete_zero
deep-dive), Q7 (anomaly finder, monotonicity + weather-interaction only --
see its docstring for what's not covered).
"""
from __future__ import annotations

from amscup_paths import ROOT, REPORTS_DIR  # noqa: E402
import json
import sys
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve()
AMSCUP_ROOT = ROOT
CHURN_DIR = REPORTS_DIR

sys.path.insert(0, str(HERE.parent))
from crossproduct import add_baseline_deltas, MARGINALIZATIONS, SUMMARY_OUT_DIR, CONDITIONS  # noqa: E402
from metrics import reliability_tag  # noqa: E402
from anomaly import SEQUENCE_CONFOUND_CEILING  # noqa: E402

METRIC_COLS = ["precision", "recall", "f1", "mATE", "mASE", "mAOE", "ap_restricted_range"]
# Metrics where LOWER is better (errors) -- inverts "beats baseline" and
# top/bottom framing relative to the rate metrics above.
LOWER_IS_BETTER = {"mATE", "mASE", "mAOE"}


def _split_reliable(df: pl.DataFrame, reliable_col: str = "reliable") -> tuple[pl.DataFrame, pl.DataFrame]:
    return df.filter(pl.col(reliable_col)), df.filter(~pl.col(reliable_col))


def load_summary(level: str) -> pl.DataFrame:
    return pl.read_parquet(SUMMARY_OUT_DIR / f"summary_{level}.parquet")


def load_deltas(level: str) -> pl.DataFrame:
    path = SUMMARY_OUT_DIR / f"deltas_{level}.parquet"
    if path.exists():
        return pl.read_parquet(path)
    summary = load_summary(level)
    deltas = add_baseline_deltas(summary, MARGINALIZATIONS[level])
    deltas.write_parquet(path)
    return deltas


# ---------------------------------------------------------------------------
# Q1 -- where does corruption beat the baseline?
# ---------------------------------------------------------------------------

def q1_beats_baseline(level: str = "condition") -> dict[str, pl.DataFrame]:
    """Cells where a corrupted metric is BETTER than `original` (higher for
    precision/recall/f1/ap, lower for mATE/mASE/mAOE). Split into (a)
    statistically significant (CI on the corrupted rate excludes the
    original point estimate, and both cells are individually reliable) vs.
    (b) within-noise fluctuation. Unfiltered improvements are NOT presented
    as findings on their own -- see the `mechanism_note` column for cases
    likely explained by corruption suppressing FPs while recall also falls
    (precision up, recall down, f1 net negative -- not a genuine
    improvement)."""
    deltas = load_deltas(level)
    rate_metrics = ["precision", "recall", "f1", "ap_restricted_range"]
    error_metrics = ["mATE", "mASE", "mAOE"]

    rows = []
    for m in rate_metrics + error_metrics:
        delta_col = f"{m}_delta"
        if delta_col not in deltas.columns:
            continue
        better = deltas.filter(
            (pl.col(delta_col) < 0) if m in error_metrics else (pl.col(delta_col) > 0)
        )
        for row in better.iter_rows(named=True):
            reliable = row.get("reliable", False) and row.get("baseline_reliable", False)
            if m in ("precision", "recall") and reliable:
                # CI-exclusion check: corrupted rate's CI lower bound must
                # exceed the original point estimate. Wilson CI exists only
                # for precision/recall (binomial rates) -- f1/AP/error
                # metrics have no CI implemented here, so for those
                # "significant" only means "both cells clear the N>=30
                # reliability floor," a weaker bar flagged explicitly via
                # ci_based=False. Do not read across metrics as if they used
                # the same standard.
                lo = row.get(f"{m}_ci_lo")
                orig_val = row.get(f"orig_{m}")
                sig = reliable and orig_val is not None and lo is not None and lo > orig_val
                ci_based = True
            else:
                sig = reliable
                ci_based = False
            mechanism = None
            if m in ("precision", "ap_restricted_range") and row.get("recall_delta", 0) is not None and row.get("recall_delta", 0) < 0:
                mechanism = "precision/AP up while recall fell -- consistent with corruption suppressing FPs, not a genuine detector improvement"
            rows.append({
                "metric": m, **{c: row[c] for c in row if c not in ("n_total",)},
                "n_total": row.get("n_total"),
                "significant": sig,
                "ci_based": ci_based,
                "mechanism_note": mechanism,
            })
    result = pl.DataFrame(rows) if rows else pl.DataFrame(schema={"metric": pl.Utf8})
    if result.is_empty():
        return {"significant": result, "noise": result}
    significant = result.filter(pl.col("significant"))
    noise = result.filter(~pl.col("significant"))
    return {"significant": significant, "noise": noise}


# ---------------------------------------------------------------------------
# Q2 -- highest / lowest metric per cross-product, at several levels
# ---------------------------------------------------------------------------

def q2_top_bottom(level: str, metric: str, n: int = 10) -> dict[str, pl.DataFrame]:
    """Top-N / bottom-N cells for one metric at one marginalization level.
    Reliable cells ranked separately from excluded (unreliable/no_data)
    cells -- the latter listed, never silently dropped."""
    summary = load_summary(level)
    reliable, excluded = _split_reliable(summary)
    reliable = reliable.filter(pl.col(metric).is_not_null())
    ascending = metric in LOWER_IS_BETTER
    best = reliable.sort(metric, descending=not ascending).head(n)
    worst = reliable.sort(metric, descending=ascending).head(n)
    return {"best": best, "worst": worst, "excluded": excluded}


def q2_all_levels(metric: str, n: int = 10) -> dict[str, dict[str, pl.DataFrame]]:
    levels = ["condition", "cond_cls", "cond_cls_weather", "cond_cls_weather_tod"]
    return {level: q2_top_bottom(level, metric, n) for level in levels}


# ---------------------------------------------------------------------------
# Q3 -- most false predictions (FP count vs. FP rate diverge)
# ---------------------------------------------------------------------------

def q3_most_false_positives(level: str = "full", n: int = 15) -> dict[str, pl.DataFrame]:
    summary = load_summary(level).with_columns(
        pl.when(pl.col("n_pred") > 0).then(pl.col("n_fp") / pl.col("n_pred")).otherwise(None).alias("fp_rate"),
        (pl.col("n_sequences") <= SEQUENCE_CONFOUND_CEILING).alias("sequence_confound_risk"),
    )
    reliable, excluded = _split_reliable(summary)
    by_count = reliable.filter(pl.col("n_fp") > 0).sort("n_fp", descending=True).head(n)
    by_rate = reliable.filter(pl.col("fp_rate").is_not_null()).sort("fp_rate", descending=True).head(n)
    return {"by_count": by_count, "by_rate": by_rate, "excluded": excluded}


# ---------------------------------------------------------------------------
# Q4 -- max FP and FN jointly
# ---------------------------------------------------------------------------

def q4_fp_fn_joint(level: str = "full", n: int = 15) -> dict[str, pl.DataFrame]:
    """`n_total` (row count) is not the effective sample size wherever
    weather/environment/tod are in the key -- those are fixed PER SEQUENCE,
    so a cell can clear the N>=30 row floor while resting on only 1-2
    actual sequences (row-level pseudo-replication, not independent
    evidence). `sequence_confound_risk` flags this explicitly rather than
    letting `reliable=True` imply more independent evidence than exists."""
    summary = load_summary(level).with_columns(
        pl.when(pl.col("n_pred") > 0).then(pl.col("n_fp") / pl.col("n_pred")).otherwise(None).alias("fp_rate"),
        pl.when(pl.col("n_gt") > 0).then(pl.col("n_fn") / pl.col("n_gt")).otherwise(None).alias("fn_rate"),
        (pl.col("n_sequences") <= SEQUENCE_CONFOUND_CEILING).alias("sequence_confound_risk"),
    )
    reliable, excluded = _split_reliable(summary)
    by_fn_count = reliable.filter(pl.col("n_fn") > 0).sort("n_fn", descending=True).head(n)
    by_fn_rate = reliable.filter(pl.col("fn_rate").is_not_null()).sort("fn_rate", descending=True).head(n)
    scatter_data = reliable.filter(pl.col("fp_rate").is_not_null() & pl.col("fn_rate").is_not_null())
    # joint worst offenders: high on both axes (above median on each)
    fp_med = scatter_data["fp_rate"].median()
    fn_med = scatter_data["fn_rate"].median()
    joint_worst = scatter_data.filter((pl.col("fp_rate") > fp_med) & (pl.col("fn_rate") > fn_med)).sort(
        (pl.col("fp_rate") + pl.col("fn_rate")), descending=True
    ).head(n)
    return {
        "by_fn_count": by_fn_count, "by_fn_rate": by_fn_rate,
        "scatter_data": scatter_data, "joint_worst_offenders": joint_worst,
        "excluded": excluded,
    }


# ---------------------------------------------------------------------------
# Q5 -- churn: max and min GT-object transition rates
# ---------------------------------------------------------------------------

def _load_churn_json(name: str) -> pl.DataFrame:
    path = CHURN_DIR / name
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Q5 reuses the churn output already computed "
            "by the prior exploratory pass (gt_transition_analysis.py, "
            "iou_threshold=0.3 explicit) rather than rerunning its matcher -- "
            "see [[full-denormalized-exploratory-pass]] for why: a single "
            "combined run drove a 7.6GB-RAM machine to <150MB free / 7.7GB "
            "swap over ~19min. If this file is genuinely missing, rerun "
            "run_churn_context.py per-dimension (not combined) rather than "
            "regenerating everything at once."
        )
    return pl.DataFrame(json.loads(path.read_text()))


def q5_churn(stratum: str | None = None, n: int = 10) -> dict[str, pl.DataFrame]:
    """Max/min churn_rate across corrupted conditions, optionally stratified
    by weather/environment/time_of_day/distance_bin/frame_density. Pooled
    across classes (sed+bus) -- the cached churn output was never computed
    per-class, and rerunning the matcher with an added group-by risks the
    same memory blowup documented above; this is a real gap, not silently
    worked around. High recovery_rate is flagged as suspicious per the task
    spec ("worth flagging, not celebrating") -- it usually means the
    corruption made an unrelated part of the scene easier to detect by
    accident, not that the model became robust.
    """
    fname = "churn_by_condition.json" if stratum is None else f"churn_by_condition_{stratum}.json"
    df = _load_churn_json(fname)
    df = df.with_columns(
        pl.col("total").map_elements(reliability_tag, return_dtype=pl.Utf8).alias("reliability")
    )
    reliable = df.filter(pl.col("reliability") == "reliable")
    excluded = df.filter(pl.col("reliability") != "reliable")

    max_churn = reliable.sort("churn_rate", descending=True).head(n)
    min_churn = reliable.sort("churn_rate", descending=False).head(n)
    # suspicious recovery: recovery rate high relative to miss rate (recovery
    # should be rare and roughly symmetric with miss under pure noise; a
    # recovery rate approaching or exceeding the miss rate suggests the
    # matcher or corruption is doing something other than pure degradation)
    suspicious_recovery = reliable.filter(
        pl.col("corruption_induced_recovery_rate") >= pl.col("corruption_induced_miss_rate")
    ).sort("corruption_induced_recovery_rate", descending=True)

    return {
        "max_churn": max_churn, "min_churn": min_churn,
        "suspicious_recovery": suspicious_recovery, "excluded": excluded,
    }


# ---------------------------------------------------------------------------
# Q6 -- loss_complete_zero: best and worst modality to lose entirely
# ---------------------------------------------------------------------------

ZERO_ABLATION_CAVEAT = (
    "Zeroing a BEV branch is off-distribution for a model not trained with "
    "modality dropout -- conv biases and BatchNorm map zeros to nonzero "
    "constants, not 'no signal.' Frame every result below as retention "
    "relative to the full-sensor baseline, NOT as an unqualified claim about "
    "sensor-failure robustness in deployment."
)


def q6_zero_ablation(level: str = "cond_cls_weather_tod") -> dict[str, pl.DataFrame | str]:
    """Rank the three loss_complete_zero conditions (camera/lidar/radar)
    across every reliable cell at `level`, to see which modality's total
    loss is most survivable and whether the ranking flips across strata."""
    zero_conditions = [c for c in CONDITIONS if c.endswith("loss_complete_zero")]
    deltas = load_deltas(level)
    zero = deltas.filter(pl.col("condition").is_in(zero_conditions))
    reliable, excluded = _split_reliable(zero)

    overall_rank = (
        reliable.group_by("condition")
        .agg(
            pl.col("f1_delta").mean().alias("mean_f1_delta"),
            pl.col("ap_restricted_range_retention").mean().alias("mean_ap_retention"),
            pl.len().alias("n_reliable_cells"),
        )
        .sort("mean_ap_retention", descending=True)
    )
    strata_cols = [c for c in ["cls", "weather", "time_of_day", "environment"] if c in reliable.columns]
    flips = None
    if strata_cols:
        per_stratum_best = (
            reliable.sort("ap_restricted_range_retention", descending=True)
            .group_by(strata_cols, maintain_order=True)
            .head(1)
            .select(strata_cols + ["condition", "ap_restricted_range_retention"])
        )
        flips = per_stratum_best
    return {
        "overall_rank": overall_rank, "per_stratum_best": flips,
        "excluded": excluded, "caveat": ZERO_ABLATION_CAVEAT,
    }


# ---------------------------------------------------------------------------
# Q7 -- anomaly finder
# ---------------------------------------------------------------------------
#
# SUPERSEDED. Q7 is now satisfied by anomaly.py + detectors.py (the
# peer-group anomaly-detection addendum) rather than this ad-hoc pair of
# checks -- per the addendum's explicit instruction not to duplicate
# outputs. This function is kept only as a deprecated pointer so old
# call sites fail loudly instead of silently computing the superseded
# (and, per the addendum's A1/A3 audit, methodologically weaker --
# no reliability-floor-gated peer groups, no robust z, mean/SD-adjacent
# MAD-ratio scoring instead of scaled-MAD robust z) version.


def q7_anomalies(*args, **kwargs):
    raise NotImplementedError(
        "q7_anomalies is superseded by anomaly.run_all_peer_groups / "
        "detectors.py (D1-D5) -- see anomaly.py's module docstring. Use "
        "run_analysis.py's anomaly section instead of calling this."
    )


if __name__ == "__main__":
    for level in ["condition", "cond_cls", "cond_cls_weather_tod"]:
        add_baseline_deltas(load_summary(level), MARGINALIZATIONS[level]).write_parquet(
            SUMMARY_OUT_DIR / f"deltas_{level}.parquet"
        )
    q1 = q1_beats_baseline("condition")
    print("Q1 significant:", q1["significant"].height, "noise:", q1["noise"].height)
    q2 = q2_top_bottom("condition", "f1")
    print("Q2 f1 best:\n", q2["best"].select(["condition", "f1", "n_total"]))
    q3 = q3_most_false_positives("full")
    print("Q3 by_rate top:\n", q3["by_rate"].select(["condition", "cls", "n_fp", "fp_rate", "n_total"]).head(5))
    q4 = q4_fp_fn_joint("full")
    print("Q4 joint worst:\n", q4["joint_worst_offenders"].select(["condition", "cls", "fp_rate", "fn_rate", "n_total"]).head(5))

    q5 = q5_churn()
    print("\nQ5 max churn:\n", q5["max_churn"].select(["corrupted_condition", "churn_rate", "total"]).head(5))
    print("Q5 suspicious recovery:\n", q5["suspicious_recovery"].select(["corrupted_condition", "corruption_induced_miss_rate", "corruption_induced_recovery_rate"]).head(5))

    q6 = q6_zero_ablation()
    print("\nQ6 overall rank:\n", q6["overall_rank"])

    q7 = q7_anomalies()
    print("\nQ7 non-monotonic severity groups:", q7["non_monotonic_severity"].height)
    print("Q7 deviation outliers:", q7["group_median_deviation_outliers"].height)
