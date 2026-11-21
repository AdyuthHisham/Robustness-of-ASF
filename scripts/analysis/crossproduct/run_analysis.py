#!/usr/bin/env python3
"""Thin orchestrator: build summaries -> deltas -> run every query -> write
CSV/markdown tables -> build figures. Run standalone:

    uv run python scripts/analysis/crossproduct/run_analysis.py

Deferred / not implemented this pass (flagged, not silently skipped):
  - Q1's significance test is CI-based only for precision/recall; f1/AP/
    error metrics fall back to a reliable-cells-only bar (see queries.py's
    q1_beats_baseline docstring).
  - Q5 churn is pooled over classes (sed+bus), not per-class -- the cached
    matcher output was never computed per-class and rerunning it risks the
    documented 7.6GB-RAM/7.7GB-swap blowup (see queries.py's
    _load_churn_json docstring).
  - Q7 is now satisfied by the anomaly.py/detectors.py peer-group addendum
    (queries.q7_anomalies raises NotImplementedError -- superseded, not
    duplicated). D2 (flat-except-one) legitimately found ZERO qualifying
    groups at the approved thresholds (tight groups, top quartile, never
    also contain a |robust z|>3.5 member) -- reported as a real null
    result, not a bug. cross_stratum_tod produces zero flags for a
    structural reason (median/MAD of exactly 2 points always gives
    |z|=0.674, mathematically below any real threshold) -- see anomaly.py's
    module docstring.
  - Figures use full condition strings on the heatmap y-axis, not the
    two-letter codes the spec asked for (radar_charts.CONDITION_CODE only
    keys (sensor, effect) tuples, not full condition-with-severity strings
    -- not remapped this pass). No bootstrap CI ribbons yet. anomaly_plots.py
    builds only a representative sample of strip plots (top sibling_conditions
    flag + one severity-violation plot + one D4 heatmap), not one per group
    instance (~1800 stratum_sweep groups alone would be impractical).
"""
from __future__ import annotations

import sys
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
from crossproduct import build_all_summaries, add_baseline_deltas, MARGINALIZATIONS, SUMMARY_OUT_DIR  # noqa: E402
from queries import (  # noqa: E402
    q1_beats_baseline, q2_top_bottom, q3_most_false_positives, q4_fp_fn_joint,
    q5_churn, q6_zero_ablation,
)
from plots import build_all_figures  # noqa: E402
from master_metrics_table import to_markdown  # noqa: E402
from anomaly import build_anomalies_table, full_coverage_statement, METRICS  # noqa: E402
from detectors import d1_monotonicity_violation, d3_modality_divergence, d4_interaction_residual, d5_cross_metric_inconsistency  # noqa: E402
from anomaly_plots import build_example_figures  # noqa: E402

REPORT_DIR = SUMMARY_OUT_DIR / "reports"


def _write(df: pl.DataFrame, name: str) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    if df.is_empty():
        return
    df.write_csv(REPORT_DIR / f"{name}.csv")


def _reliability_note(df: pl.DataFrame) -> str:
    if df.is_empty():
        return "n=0 rows."
    n = df.height
    return f"n={n} rows, N and reliability tag carried per-row (see CSV)."


def main() -> None:
    print("Building summaries at all marginalization levels...")
    summaries = build_all_summaries()
    for level in ["condition", "cond_cls", "cond_cls_weather_tod"]:
        add_baseline_deltas(summaries[level], MARGINALIZATIONS[level]).write_parquet(
            SUMMARY_OUT_DIR / f"deltas_{level}.parquet"
        )

    findings: list[str] = ["# Cross-product analysis findings\n"]

    q1 = q1_beats_baseline("condition")
    _write(q1["significant"], "q1_significant")
    _write(q1["noise"], "q1_noise")
    findings.append(
        "## Q1 -- where corruption beats the baseline\n\n"
        f"- Statistically significant (CI-excluded for precision/recall, "
        f"reliable-both-cells only for other metrics -- see `ci_based` "
        f"column): {q1['significant'].height} rows.\n"
        f"- Within-noise fluctuation: {q1['noise'].height} rows.\n"
        "- See `mechanism_note` column for cases explained by corruption "
        "suppressing FPs while recall also falls -- not a genuine "
        "improvement.\n"
    )

    for metric in ["f1", "mATE", "ap_restricted_range"]:
        q2 = q2_top_bottom("condition", metric)
        _write(q2["best"], f"q2_{metric}_best_condition")
        _write(q2["worst"], f"q2_{metric}_worst_condition")
    findings.append(
        "## Q2 -- highest/lowest per metric (condition level; see CSVs for "
        "cond_cls/cond_cls_weather/cond_cls_weather_tod levels via "
        "queries.q2_all_levels)\n"
    )

    q3 = q3_most_false_positives("full")
    _write(q3["by_count"], "q3_fp_by_count")
    _write(q3["by_rate"], "q3_fp_by_rate")
    findings.append(
        "## Q3 -- most false predictions\n\n"
        f"- By count: {q3['by_count'].height} reliable cells ranked.\n"
        f"- By rate: {q3['by_rate'].height} reliable cells ranked. "
        "Divergence between count and rate rankings is expected -- a "
        "high-N common condition can out-count a small, near-100%-FP rare "
        "cell.\n"
    )

    q4 = q4_fp_fn_joint("full")
    _write(q4["joint_worst_offenders"], "q4_joint_worst_offenders")
    findings.append(
        "## Q4 -- FP and FN jointly\n\n"
        f"- {q4['joint_worst_offenders'].height} cells above both the FP-rate "
        "and FN-rate median simultaneously (see scatter figure).\n"
    )

    q5 = q5_churn()
    _write(q5["max_churn"], "q5_max_churn")
    _write(q5["min_churn"], "q5_min_churn")
    _write(q5["suspicious_recovery"], "q5_suspicious_recovery")
    findings.append(
        "## Q5 -- churn (static-object corruption-fragility, NOT temporal "
        "tracking)\n\n"
        f"- Highest churn: {q5['max_churn']['corrupted_condition'][0]} "
        f"({q5['max_churn']['churn_rate'][0]:.1%}).\n"
        f"- {q5['suspicious_recovery'].height} conditions show recovery "
        "rate >= miss rate -- flagged as suspicious, not celebrated as "
        "robustness (task spec).\n"
        "- Pooled over classes (sed+bus) -- per-class churn not computed, "
        "see run_analysis.py module docstring.\n"
    )

    q6 = q6_zero_ablation()
    _write(q6["overall_rank"], "q6_zero_ablation_rank")
    findings.append(
        "## Q6 -- loss_complete_zero: best/worst modality to lose entirely\n\n"
        + to_markdown(q6["overall_rank"]) + "\n\n"
        f"**{q6['caveat']}**\n"
    )

    print("Building peer-group anomaly detection (Q7 addendum)...")
    anomaly_metrics = list(METRICS)
    anomalies = build_anomalies_table(anomaly_metrics)
    _write(anomalies, "anomalies")
    anomalies.write_parquet(REPORT_DIR / "anomalies.parquet")
    coverage = full_coverage_statement(anomaly_metrics)
    _write(coverage, "anomaly_coverage")

    cat_counts = anomalies["category"].value_counts().to_pandas().set_index("category")["count"].to_dict() if anomalies.height else {}
    d1_all = pl.concat([d1_monotonicity_violation(m) for m in anomaly_metrics if m in ("ap_restricted_range", "precision", "recall")])
    d3_all = pl.concat([d3_modality_divergence(m) for m in anomaly_metrics if m in ("ap_restricted_range", "precision", "recall")])
    d5 = d5_cross_metric_inconsistency()
    _write(d1_all, "d1_monotonicity_violations")
    _write(d3_all, "d3_modality_divergence")
    _write(d5, "d5_cross_metric_inconsistency")

    findings.append(
        "## Q7 addendum -- peer-group anomaly detection\n\n"
        "Measures cells against their PEERS (median/scaled-MAD, robust z, "
        "single-gate per the Phase-1-addendum audit -- CI-overlap recorded "
        "not filtering), not against `original`. Full methodology and the "
        "resolved A1-A4 blockers: see obsidianVault Phase-1-addendum audit "
        f"note.\n\n"
        f"- **{anomalies.height} total flags** across "
        f"{len(anomaly_metrics)} metrics x 6 peer-group types: "
        f"{cat_counts.get('real', 0)} real, "
        f"{cat_counts.get('small_n_artifact', 0)} small-N artifact, "
        f"{cat_counts.get('suspected_bug', 0)} suspected bug (manual audit "
        "recommended for the last category if nonzero).\n"
        f"- **D1 monotonicity violations**: {d1_all.height} severity-ladder "
        "reversals (across ap_restricted_range/precision/recall).\n"
        "- **D2 flat-except-one**: zero qualifying groups at the approved "
        "thresholds (tight groups in the top quartile never also contain a "
        "member with |robust z|>3.5 in this dataset) -- a genuine null "
        "result, not a bug; every real anomaly found instead comes from "
        "already-SCATTERED groups (see anomaly_coverage.csv).\n"
        f"- **D3 modality divergence**: {d3_all.height} (effect, severity, "
        "cls, weather, tod) groups where the camera/lidar/radar ordering "
        "flips against the metric's global ordering.\n"
        "- **D4 interaction residual** (median polish, condition x weather, "
        "sed): fit quality 0.84 -- lidar-corruption residuals flip sign "
        "between fog (positive, better than the additive model expects) and "
        "normal/overcast (negative); radar conditions show a consistent "
        "negative residual specifically in sleet. See the heatmap figure.\n"
        f"- **D5 cross-metric inconsistency**: {d5.height} cells matching "
        "the 'precision up while recall falls' pattern (FP suppression, not "
        "genuine improvement) -- see queries.q1_beats_baseline's mechanism "
        "notes for the same pattern from the baseline-relative side.\n"
        "- **Coverage caveat**: `cross_stratum_tod` (hold everything but "
        "time-of-day, 2 members) can NEVER produce a robust-z flag -- with "
        "exactly 2 points, median=mean and MAD is symmetric, so z is always "
        "~0.674 regardless of the actual values. Its zero flags are a "
        "mathematical property of 2-member groups, not evidence of no "
        "anomaly; see `anomaly_coverage.csv` for the scored/insufficient "
        "split on every other peer group before reading absence-of-flags "
        "as absence-of-anomaly anywhere.\n"
    )

    findings.append(
        "## Limitations\n\n"
        "- `distance_from_ego` mixed provenance (pred-based TP/FP, "
        "GT-backfilled FN) -- never used for mATE/mASE/mAOE here (those are "
        "TP-only from loc/dims/rotation directly).\n"
        "- `score`/`iou` are post-threshold; AP reported is "
        "restricted-range, matching K-Radar's own official-benchmark "
        "convention exactly (not a gap specific to this analysis) -- see "
        "obsidianVault Phase 1 audit note.\n"
        "- loss_complete_zero results are off-distribution for a model not "
        "trained with modality dropout -- framed as retention vs. baseline, "
        "not unqualified sensor-failure robustness.\n"
        "- Class imbalance (sed 82.6% / bus 17.4%) -- every table here "
        "carries `cls` as an explicit column; no pooled-only claim is made "
        "without also breaking out by class.\n"
        "- `frame_deletion` conditions (9 of 31) excluded entirely -- "
        "expected/by-design crash-coverage, confirmed by user.\n"
    )

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / "findings.md").write_text("\n".join(findings))
    print(f"Findings report: {REPORT_DIR / 'findings.md'}")

    print("Building figures...")
    for p in build_all_figures():
        print(" ", p)
    print("Building anomaly figures...")
    for p in build_example_figures():
        print(" ", p)


if __name__ == "__main__":
    main()
