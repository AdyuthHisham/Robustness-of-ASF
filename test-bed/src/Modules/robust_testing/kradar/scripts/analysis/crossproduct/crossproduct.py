#!/usr/bin/env python3
"""Cross-product enumeration and the summary-table builder (Step 2.1/2.2 of
the exhaustive cross-product analysis task). Build the summary ONCE at
several marginalization levels so every downstream query
(queries.py/plots.py) slices a small parquet instead of rescanning the 1.1M
detection-outcome rows.

Keyed by (condition, cls, weather, time_of_day, environment,
distance_bucket) at full grain, with modality/effect/severity carried as
derived (non-key) columns for filtering/readability -- they're a
deterministic function of condition, not an independent dimension, so they
are NOT cross-joined separately (that would just recreate invalid
modality/effect/severity combinations for conditions where they don't
apply, e.g. "original").

Restricted to the 22-condition scope (master_metrics_table.CONDITIONS --
frame_deletion excluded, confirmed by user as expected crash-coverage
behaviour, not a bug to work around).
"""
from __future__ import annotations

import itertools
import sys
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve()
AMSCUP_ROOT = HERE.parents[8]
AP_METRICS_DIR = AMSCUP_ROOT / "repos" / "K-Radar" / "scripts" / "alvis"
ROW_TABLE_PATH = AMSCUP_ROOT / "repos" / "K-Radar" / "outputs" / "robustness_reports" / "full_denormalized_table.parquet"
SUMMARY_OUT_DIR = AMSCUP_ROOT / "repos" / "K-Radar" / "outputs" / "robustness_reports" / "crossproduct"

sys.path.insert(0, str(AP_METRICS_DIR))
from ap_metrics import compute_ap_grouped  # noqa: E402
from gt_transition_analysis import parse_condition  # noqa: E402

sys.path.insert(0, str(HERE.parents[1]))
from master_metrics_table import CONDITIONS, CLEAN_CONDITION  # noqa: E402

sys.path.insert(0, str(HERE.parent))
from metrics import angle_error, precision_recall_f1, reliability_tag, retention_ratio, absolute_delta  # noqa: E402

CLASSES = ["sed", "bus"]
WEATHER_VALUES = ["fog", "normal", "overcast", "rain", "sleet"]
TOD_VALUES = ["day", "night"]
ENVIRONMENT_VALUES = ["alleyway", "countryside", "highway", "mountain", "parkinglots", "shoulder", "university", "urban"]
DISTANCE_BUCKET_VALUES = ["near_0_20", "mid_20_40", "far_40_60", "very_far_60_75"]
FRAME_DENSITY_VALUES = ["1", "2-3", "4+"]

# Full grain (Step 2.1's key). Rollups drop trailing dims -- each is a
# strict subset of the full grain's keys so every query can pick the
# coarsest level with adequate N instead of re-aggregating raw rows.
FULL_GRAIN = ["condition", "cls", "weather", "time_of_day", "environment", "distance_bucket"]
# Richest level, adds frame_density -- needed for the anomaly-addendum's
# A1.3 "stratum sweep" peer group (fix condition+cls, vary the full
# weather x environment x distance_bucket x frame_density x time_of_day
# cross). Kept separate from FULL_GRAIN (not a rollup superset relationship
# for every other level) since no other query needs frame_density as a key.
FULL_GRAIN_WITH_DENSITY = FULL_GRAIN + ["frame_density"]
MARGINALIZATIONS: dict[str, list[str]] = {
    "full_density": FULL_GRAIN_WITH_DENSITY,
    "full": FULL_GRAIN,
    "cond_cls_weather_tod_env": ["condition", "cls", "weather", "time_of_day", "environment"],
    "cond_cls_weather_tod": ["condition", "cls", "weather", "time_of_day"],
    "cond_cls_weather": ["condition", "cls", "weather"],
    "cond_cls": ["condition", "cls"],
    "condition": ["condition"],
}


def load_scoped_table() -> pl.DataFrame:
    df = pl.read_parquet(ROW_TABLE_PATH)
    df = df.filter(pl.col("condition").is_in(CONDITIONS))
    missing = set(CONDITIONS) - set(df["condition"].unique().to_list())
    if missing:
        raise ValueError(f"22-condition scope missing from table: {missing}")
    # distance_bucket/frame_density come out of build_denormalized_table.py's
    # .cut() as Categorical; cast to Utf8 so every join key here is a plain
    # string (join dtype mismatches otherwise, e.g. against the domain
    # cross-join's plain-Python string columns).
    for cat_col in ("distance_bucket", "frame_density"):
        if cat_col in df.columns:
            df = df.with_columns(pl.col(cat_col).cast(pl.Utf8))
    return df


def _counts_and_rates(df: pl.DataFrame, group_cols: list[str]) -> pl.DataFrame:
    """`n_total` (row count) is NOT the effective sample size wherever
    weather/environment/time_of_day are involved -- those are fixed PER
    SEQUENCE (confirmed: every sequence carries exactly one weather/
    environment/tod value), so a cell's rows are pseudo-replicated draws
    from however many sequences share that combination, not independent
    detections. `n_sequences` (distinct sequence count backing the cell) is
    carried alongside n_total for exactly this reason -- a cell can clear
    the N>=100 ROW floor while resting on only 1-2 actual sequences, and
    that must be visible, not silently absorbed into "reliable"."""
    counts = df.group_by(group_cols).agg(
        pl.col("is_tp").sum().alias("n_tp"),
        pl.col("is_fp").sum().alias("n_fp"),
        pl.col("is_fn").sum().alias("n_fn"),
        pl.col("score").mean().alias("mean_score"),
        pl.col("iou").filter(pl.col("is_tp")).mean().alias("mean_iou"),
        pl.col("sequence").n_unique().alias("n_sequences"),
    )
    rows = []
    for row in counts.iter_rows(named=True):
        n_tp, n_fp, n_fn = int(row["n_tp"]), int(row["n_fp"]), int(row["n_fn"])
        n_total = n_tp + n_fp + n_fn
        prf1 = precision_recall_f1(n_tp, n_fp, n_fn)
        out = {c: row[c] for c in group_cols}
        out.update({
            "n_tp": n_tp, "n_fp": n_fp, "n_fn": n_fn, "n_total": n_total,
            "n_sequences": int(row["n_sequences"]),
            "mean_score": row["mean_score"], "mean_iou": row["mean_iou"],
            **prf1,
            "reliable": reliability_tag(n_total) == "reliable",
            "reliability": reliability_tag(n_total),
        })
        rows.append(out)
    return pl.DataFrame(rows)


def _tp_error_metrics(df: pl.DataFrame, group_cols: list[str]) -> pl.DataFrame:
    """TP-only mATE/mASE/mAOE. Never computed from distance_from_ego (mixed
    provenance across TP/FP/FN, per Phase 1 caveat 1 of the task spec) --
    these use loc_x/z and rotation_y directly, which are pred-only and
    exist unconditionally on TP rows."""
    tp = df.filter(pl.col("is_tp"))
    tp = tp.with_columns(
        (((pl.col("loc_x") - pl.col("gt_loc_x")) ** 2 + (pl.col("loc_z") - pl.col("gt_loc_z")) ** 2) ** 0.5).alias("ate"),
        (
            1
            - (
                pl.min_horizontal("width", "gt_width")
                * pl.min_horizontal("length", "gt_length")
                * pl.min_horizontal("height", "gt_height")
            )
            / (
                pl.max_horizontal("width", "gt_width")
                * pl.max_horizontal("length", "gt_length")
                * pl.max_horizontal("height", "gt_height")
            )
        ).alias("ase"),
    )
    tp_pd = tp.select(group_cols + ["rotation_y", "gt_rotation_y", "ate", "ase"]).to_pandas()
    tp_pd["aoe"] = angle_error(tp_pd["rotation_y"].to_numpy(), tp_pd["gt_rotation_y"].to_numpy())
    agg = pl.from_pandas(tp_pd).group_by(group_cols).agg(
        pl.col("ate").mean().alias("mATE"),
        pl.col("ase").mean().alias("mASE"),
        pl.col("aoe").mean().alias("mAOE"),
        pl.len().alias("n_tp_error"),
    )
    return agg


def _ap_metrics(df: pl.DataFrame, group_cols: list[str]) -> pl.DataFrame:
    """Restricted-range AP (Phase 1 decision 1) -- labeled explicitly.
    compute_ap_grouped sorts by score within each group, so this cannot be
    derived from the simple sum-based aggregate above; computed separately
    and joined in."""
    ap_table = compute_ap_grouped(df, group_cols + ["cls"]) if "cls" not in group_cols else compute_ap_grouped(df, group_cols)
    ap_table = ap_table.rename({"ap": "ap_restricted_range"})
    return ap_table


def build_summary(df: pl.DataFrame, group_cols: list[str]) -> pl.DataFrame:
    """One marginalization level's summary: counts/rates (with reliability
    tag) + TP-only localization error + restricted-range AP, joined on
    group_cols. `no_data` cells (combinations never occurring in the source
    data, e.g. a (weather, environment, time_of_day) triple absent from all
    58 sequences) are added explicitly by cross-joining the full domain of
    each key column and left-joining the observed stats -- a blank row here
    means "structurally never tested," not "tested and noisy"."""
    base = _counts_and_rates(df, group_cols)
    errors = _tp_error_metrics(df, group_cols)
    ap = _ap_metrics(df, group_cols)
    if "cls" in group_cols:
        out = base.join(errors, on=group_cols, how="left").join(ap, on=group_cols, how="left")
    else:
        # AP table always carries cls (compute_ap_grouped requires it internally
        # for per-class AP); when cls isn't a requested key, average AP over
        # classes with GT present rather than dropping class information silently.
        ap_mean = ap.group_by(group_cols).agg(pl.col("ap_restricted_range").mean())
        out = base.join(errors, on=group_cols, how="left").join(ap_mean, on=group_cols, how="left")

    domain = {
        "condition": CONDITIONS, "cls": CLASSES, "weather": WEATHER_VALUES,
        "time_of_day": TOD_VALUES, "environment": ENVIRONMENT_VALUES,
        "distance_bucket": DISTANCE_BUCKET_VALUES, "frame_density": FRAME_DENSITY_VALUES,
    }
    full_domain_cols = [domain[c] for c in group_cols]
    full_index = pl.DataFrame(
        list(itertools.product(*full_domain_cols)), schema=group_cols, orient="row",
    )
    out = full_index.join(out, on=group_cols, how="left")
    out = out.with_columns(
        pl.col("n_tp").fill_null(0), pl.col("n_fp").fill_null(0),
        pl.col("n_fn").fill_null(0), pl.col("n_total").fill_null(0),
        pl.col("n_sequences").fill_null(0),
        pl.col("reliability").fill_null("no_data"),
        pl.col("reliable").fill_null(False),
    )
    if "condition" in group_cols:
        parsed = [parse_condition(c) for c in out["condition"]]
        out = out.with_columns(
            pl.Series("modality", [p["modality"] for p in parsed]),
            pl.Series("effect", [p["effect"] for p in parsed]),
            pl.Series("severity", [p["severity"] for p in parsed]),
        )
    return out


def build_all_summaries(df: pl.DataFrame | None = None, out_dir: Path = SUMMARY_OUT_DIR) -> dict[str, pl.DataFrame]:
    if df is None:
        df = load_scoped_table()
    out_dir.mkdir(parents=True, exist_ok=True)
    summaries = {}
    for name, group_cols in MARGINALIZATIONS.items():
        summary = build_summary(df, group_cols)
        path = out_dir / f"summary_{name}.parquet"
        summary.write_parquet(path)
        print(f"summary_{name}: {summary.height} rows -> {path}")
        summaries[name] = summary
    return summaries


def add_baseline_deltas(summary: pl.DataFrame, group_cols: list[str]) -> pl.DataFrame:
    """Join each corrupted cell to its `original` cell on all non-condition
    keys (Step 2.2). Flags cells where the ORIGINAL baseline cell itself is
    unreliable -- a delta against a noisy baseline is noise, not a finding."""
    join_keys = [c for c in group_cols if c != "condition"]
    baseline = summary.filter(pl.col("condition") == CLEAN_CONDITION)
    if not join_keys:
        # condition-only summary: baseline is a single row, broadcast.
        base_row = baseline.row(0, named=True)
        corrupted = summary.filter(pl.col("condition") != CLEAN_CONDITION)
        metric_cols = ["precision", "recall", "f1", "mATE", "mASE", "mAOE", "ap_restricted_range"]
        exprs = []
        for m in metric_cols:
            exprs.append((pl.col(m) - pl.lit(base_row[m])).alias(f"{m}_delta"))
            exprs.append(
                pl.when(pl.lit(base_row[m]).is_not_null() & (pl.lit(base_row[m]) != 0) & pl.col(m).is_not_null())
                .then(pl.col(m) / pl.lit(base_row[m]))
                .otherwise(None)
                .alias(f"{m}_retention")
            )
        out = corrupted.with_columns(exprs).with_columns(
            pl.lit(base_row["reliability"] == "reliable").alias("baseline_reliable"),
            pl.lit(base_row["precision"]).alias("orig_precision"),
            pl.lit(base_row["recall"]).alias("orig_recall"),
        )
        return out

    baseline_renamed = baseline.drop("condition").rename(
        {c: f"orig_{c}" for c in baseline.columns if c not in join_keys and c != "condition"}
    )
    corrupted = summary.filter(pl.col("condition") != CLEAN_CONDITION)
    merged = corrupted.join(baseline_renamed, on=join_keys, how="left")

    metric_cols = ["precision", "recall", "f1", "mATE", "mASE", "mAOE", "ap_restricted_range"]
    exprs = []
    for m in metric_cols:
        exprs.append((pl.col(m) - pl.col(f"orig_{m}")).alias(f"{m}_delta"))
        exprs.append(
            pl.when(pl.col(f"orig_{m}").is_not_null() & (pl.col(f"orig_{m}") != 0) & pl.col(m).is_not_null())
            .then(pl.col(m) / pl.col(f"orig_{m}"))
            .otherwise(None)
            .alias(f"{m}_retention")
        )
    merged = merged.with_columns(exprs).with_columns(
        (pl.col("orig_reliability") == "reliable").alias("baseline_reliable")
    )
    return merged


if __name__ == "__main__":
    build_all_summaries()
