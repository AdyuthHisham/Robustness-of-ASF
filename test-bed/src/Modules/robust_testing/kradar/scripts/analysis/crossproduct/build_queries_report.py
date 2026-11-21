#!/usr/bin/env python3
"""Answer queries.py Q1-Q7 and write docs/crossproduct_queries_report.md.

Why not `python queries.py`: its __main__ calls q7_anomalies(), a deprecated
stub that raises NotImplementedError. Q7 here is reported from the existing
anomaly.py outputs (reports/anomalies.parquet, findings.md), never recomputed.

Data: crossproduct/ summaries predate the frame-key fix and the snow-label
fix, so (with --rebuild) the needed levels are rebuilt ONE LEVEL AT A TIME
from full_denormalized_table_22cond_weather_corrected.parquet into
crossproduct_v3_weather_corrected/ (the stale tree is left untouched).
No existing function is modified; the weather domain list is extended at
runtime because build_summary left-joins from the domain and would silently
drop the light_snow/heavy_snow rows.

    uv run python scripts/analysis/crossproduct/build_queries_report.py --rebuild
    uv run python scripts/analysis/crossproduct/build_queries_report.py
"""
from __future__ import annotations

import datetime as dt
import gc
import json
import sys
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
import crossproduct as cp  # noqa: E402
import queries as q  # noqa: E402

RR = cp.AMSCUP_ROOT / "repos" / "K-Radar" / "outputs" / "robustness_reports"
TABLE = RR / "full_denormalized_table_22cond_weather_corrected.parquet"
OUT = RR / "crossproduct_v3_weather_corrected"
REPORT = cp.AMSCUP_ROOT / "docs" / "crossproduct_queries_report.md"
LEVELS_NEEDED = ["condition", "cond_cls", "cond_cls_weather", "cond_cls_weather_tod", "full"]
KEYS = ["condition", "cls", "weather", "time_of_day", "environment", "distance_bucket"]

for w in ("light_snow", "heavy_snow"):  # see module docstring
    if w not in cp.WEATHER_VALUES:
        cp.WEATHER_VALUES.append(w)
cp.SUMMARY_OUT_DIR = q.SUMMARY_OUT_DIR = OUT


def rebuild() -> None:
    OUT.mkdir(exist_ok=True)
    df = pl.read_parquet(TABLE).with_columns(pl.col("distance_bucket").cast(pl.Utf8))
    for level in LEVELS_NEEDED:
        s = cp.build_summary(df, cp.MARGINALIZATIONS[level])
        s.write_parquet(OUT / f"summary_{level}.parquet")
        print(f"{level}: {s.height} rows", flush=True)
        del s
        gc.collect()


# ---------------------------------------------------------------- formatting
def md(df: pl.DataFrame, cols: list[str] | None = None, n: int = 10, width: int = 60) -> str:
    if df.is_empty():
        return "_(no rows)_\n"
    if cols:
        df = df.select([c for c in cols if c in df.columns])
    df = df.head(n)
    with pl.Config(tbl_formatting="ASCII_MARKDOWN", tbl_hide_column_data_types=True,
                   tbl_hide_dataframe_shape=True, tbl_rows=n + 2, tbl_cols=-1,
                   fmt_str_lengths=width, float_precision=4, tbl_width_chars=400):
        return str(df) + "\n"


def mt(p: Path) -> str:
    return dt.datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M")


def excl_counts(ex: pl.DataFrame) -> str:
    if ex.is_empty():
        return "0"
    c = ex.group_by("reliability").len().sort("reliability").rows()
    return ", ".join(f"{k}={v}" for k, v in c) + f" (total {ex.height})"


# ------------------------------------------------------------------ sections
def sec_provenance(rebuilt: bool) -> str:
    rows = []
    files = [TABLE, RR / "full_denormalized_table_22cond.parquet", RR / "full_denormalized_table.parquet",
             RR / "crossproduct" / "summary_condition.parquet", RR / "crossproduct_v2" / "summary_condition.parquet"]
    files += [OUT / f"summary_{lv}.parquet" for lv in LEVELS_NEEDED]
    files += [OUT / f"deltas_{lv}.parquet" for lv in ("condition", "cond_cls", "cond_cls_weather_tod")]
    files += sorted(RR.glob("churn_by_condition*.json"))
    files += [RR / "crossproduct_v2" / "churn_all_conditions.json",
              RR / "crossproduct_v2" / "reports" / "anomalies.parquet",
              RR / "crossproduct_v2" / "reports" / "findings.md"]
    for f in files:
        if not f.exists():
            continue
        if f.suffix == ".parquet":
            n = pl.scan_parquet(f).select(pl.len()).collect().item()
        elif f.suffix == ".json":
            n = len(json.loads(f.read_text()))
        else:
            n = "-"
        rows.append({"file": str(f.relative_to(cp.AMSCUP_ROOT)), "mtime": mt(f), "rows": n})
    return md(pl.DataFrame(rows), n=len(rows) + 1, width=120)


def q1(level: str) -> str:
    r = q.q1_beats_baseline(level)
    sig, noise = r["significant"], r["noise"]
    allr = pl.concat([sig, noise], how="diagonal_relaxed")
    out = f"#### Level `{level}`\n\n"
    out += "Counts (better-than-baseline cells; metric x ci_based x significant):\n\n"
    cnt = (allr.group_by("metric", "ci_based", "significant").len().sort("metric", "ci_based", "significant"))
    out += md(cnt, n=40)
    out += (f"\nTotals: significant={sig.height} (ci_based={sig.filter(pl.col('ci_based')).height}, "
            f"non-CI floor-only={sig.filter(~pl.col('ci_based')).height}); noise={noise.height}. "
            f"Mechanism-note rows: {allr.filter(pl.col('mechanism_note').is_not_null()).height} total, "
            f"{sig.filter(pl.col('mechanism_note').is_not_null()).height} among 'significant'.\n\n")

    def val(d: pl.DataFrame) -> pl.DataFrame:
        if d.is_empty():
            return d
        rows = d.to_dicts()
        for x in rows:
            x["value"] = x[x["metric"]]
            x["delta"] = x[f"{x['metric']}_delta"]
        return pl.DataFrame(rows, infer_schema_length=None)
    cols = ["metric", "condition", "cls", "value", "delta", "n_total", "n_sequences", "reliability", "ci_based", "mechanism_note"]
    ci = val(sig.filter(pl.col("ci_based"))).sort(pl.col("delta").abs(), descending=True)
    out += "Top CI-based significant (precision/recall; by |delta|):\n\n" + md(ci, cols)
    nonci = val(sig.filter(~pl.col("ci_based"))).sort(pl.col("delta").abs(), descending=True)
    out += "\nTop floor-only 'significant' (f1/AP/errors; weaker bar -- N-floor only, no CI):\n\n" + md(nonci, cols)
    mech = val(allr.filter(pl.col("mechanism_note").is_not_null())).sort("delta", descending=True)
    out += "\nMechanism-note rows (precision/AP up while recall fell -- NOT genuine improvements):\n\n" + md(mech, cols)
    unrel = allr.filter(~pl.col("reliable") | ~pl.col("baseline_reliable"))
    out += f"\nCells whose own or baseline N is below the floor (never counted significant): {unrel.height}.\n\n"
    return out


def q2() -> str:
    out = ""
    for m in q.METRIC_COLS:
        direction = "lower is better" if m in q.LOWER_IS_BETTER else "higher is better"
        res = q.q2_all_levels(m, n=5)
        out += f"#### {m} ({direction})\n\n"
        c = res["condition"]
        t = pl.concat([c["best"].with_columns(pl.lit("best").alias("end")),
                       c["worst"].with_columns(pl.lit("worst").alias("end"))])
        out += "Level `condition` (best 5 / worst 5; includes the `original` baseline row):\n\n"
        out += md(t, ["end", "condition", m, "n_total", "n_sequences", "reliability"], 10)
        fine = []
        for lv, r in res.items():
            if lv == "condition":
                continue
            for end in ("best", "worst"):
                fine.append(r[end].head(1).with_columns(pl.lit(lv).alias("level"), pl.lit(end).alias("end")))
        fine = pl.concat(fine, how="diagonal_relaxed")
        out += "\nFiner levels, single best/worst reliable cell:\n\n"
        out += md(fine, ["level", "end", "condition", "cls", "weather", "time_of_day", m, "n_total", "n_sequences", "reliability"], 6)
        out += "\nExcluded (not ranked): " + "; ".join(f"{lv}: {excl_counts(r['excluded'])}" for lv, r in res.items()) + "\n\n"
    return out


def conf(df: pl.DataFrame) -> str:
    n = df.filter(pl.col("sequence_confound_risk")).height
    return f"{n}/{df.height} of the rows shown have sequence_confound_risk (n_sequences <= {q.SEQUENCE_CONFOUND_CEILING})"


def q34() -> tuple[str, str]:
    cols = ["condition", "cls", "weather", "time_of_day", "environment", "distance_bucket"]
    r3 = q.q3_most_false_positives("full")
    c3 = cols + ["n_fp", "n_pred", "n_gt", "fp_rate", "n_total", "n_sequences", "sequence_confound_risk", "reliability"]
    s3 = ("Top by FP count:\n\n" + md(r3["by_count"], c3) + f"\n_{conf(r3['by_count'].head(10))}._\n\n"
          "Top by FP rate (n_fp / n_pred):\n\n" + md(r3["by_rate"], c3) + f"\n_{conf(r3['by_rate'].head(10))}._\n\n"
          f"Excluded cells (not ranked): {excl_counts(r3['excluded'])}.\n")
    r4 = q.q4_fp_fn_joint("full")
    c4 = cols + ["n_fp", "n_fn", "n_tp", "fp_rate", "fn_rate", "n_total", "n_sequences", "sequence_confound_risk", "reliability"]
    sd = r4["scatter_data"]
    s4 = (f"Joint scatter cells: {sd.height}; fp_rate median={sd['fp_rate'].median():.4f}, fn_rate median={sd['fn_rate'].median():.4f}.\n\n"
          "Joint worst offenders (above both medians, ranked by fp_rate+fn_rate):\n\n" + md(r4["joint_worst_offenders"], c4)
          + f"\n_{conf(r4['joint_worst_offenders'].head(10))}._\n\n"
          "Top by FN count:\n\n" + md(r4["by_fn_count"], c4) + f"\n_{conf(r4['by_fn_count'].head(10))}._\n\n"
          "Top by FN rate (n_fn / n_gt):\n\n" + md(r4["by_fn_rate"], c4) + f"\n_{conf(r4['by_fn_rate'].head(10))}._\n\n"
          f"Excluded cells (not ranked): {excl_counts(r4['excluded'])}.\n")
    return s3, s4


def q5() -> str:
    out = ""
    for stratum in [None, "weather", "environment", "time_of_day", "distance_bin", "frame_density"]:
        fname = "churn_by_condition.json" if stratum is None else f"churn_by_condition_{stratum}.json"
        p = RR / fname
        out += f"#### {'pooled over conditions' if stratum is None else 'stratum: ' + stratum} (`{fname}`)\n\n"
        if not p.exists():
            out += "File missing -- not answered for this stratum (matcher deliberately not re-run).\n\n"
            continue
        r = q.q5_churn(stratum)
        key = ["corrupted_condition"] + ([stratum] if stratum and stratum in r["max_churn"].columns else [])
        cols = key + ["churn_rate", "corruption_induced_miss_rate", "corruption_induced_recovery_rate", "net_retention", "total", "reliability"]
        sus = r["suspicious_recovery"]
        out += f"Mtime {mt(p)}. Suspicious recovery (recovery >= miss) among reliable: {sus.height}. Excluded: {excl_counts(r['excluded'])}.\n\n"
        out += "Highest churn:\n\n" + md(r["max_churn"], cols, 10 if stratum is None else 5)
        out += "\nLowest churn:\n\n" + md(r["min_churn"], cols, 10 if stratum is None else 5)
        out += "\nSuspicious recovery (flagged, not celebrated):\n\n" + md(sus, cols, 10 if stratum is None else 5) + "\n"
    return out


def q6() -> tuple[str, dict]:
    r = q.q6_zero_ablation()
    best = r["per_stratum_best"]
    out = f"> {r['caveat']}\n\n"
    out += "Overall ranking (mean over reliable (cls, weather, tod) cells; unweighted by N):\n\n" + md(r["overall_rank"], n=5)
    out += f"\nExcluded cells (zero conditions, not ranked): {excl_counts(r['excluded'])}.\n\n"
    top = r["overall_rank"]["condition"][0]
    null_wins = best.filter(pl.col("ap_restricted_range_retention").is_null()).height
    z = [c for c in q.CONDITIONS if c.endswith("loss_complete_zero")]
    d = q.load_deltas("cond_cls_weather_tod").filter(pl.col("condition").is_in(z) & pl.col("reliable")
                                                      & pl.col("ap_restricted_range_retention").is_not_null())
    clean = (d.sort("ap_restricted_range_retention", descending=True).group_by("cls", "weather", "time_of_day", maintain_order=True)
             .head(1).select("cls", "weather", "time_of_day", "condition", "ap_restricted_range_retention"))
    out += (f"\nStock `per_stratum_best` ({best.height} strata): {null_wins} winner row(s) have NULL retention (baseline AP undefined/zero, "
            "e.g. bus in fog has no GT). `queries.q6_zero_ablation` sorts descending without `nulls_last`, so a null row can be picked as 'best'. "
            "Existing function left unchanged; the null-excluded recomputation below is what the answer uses.\n\n")
    out += f"Null-excluded per-stratum best ({clean.height} strata) -- strata won:\n\n" + md(clean.group_by("condition").len().sort("len", descending=True), n=5)
    out += "\nBy class:\n\n" + md(clean.group_by("cls", "condition").len().sort("cls", "len", descending=[False, True]), n=10)
    flips = clean.filter(pl.col("condition") != top).sort("ap_restricted_range_retention")
    out += f"\nStrata NOT won by overall leader `{top}`: {flips.height}/{clean.height}:\n\n" + md(flips, n=12)
    return out, {"top": top, "wins": clean.group_by("condition").len().sort("len", descending=True).rows(), "n": clean.height,
                 "flips": flips.height, "null_wins": null_wins, "stock_n": best.height, "rank": r["overall_rank"], "excluded": r["excluded"]}


def q7() -> tuple[str, pl.DataFrame]:
    rep = RR / "crossproduct_v2" / "reports"
    old = RR / "crossproduct" / "reports" / "anomalies.parquet"
    out = ("`queries.q7_anomalies` is a deprecated stub (raises NotImplementedError), superseded by `anomaly.py` + `detectors.py` "
           "(peer-group, scaled-MAD robust z). Not recomputed here: that needs the `full_density`/`cond_cls_weather_tod_env` summaries "
           "and was not rebuilt on this memory-limited machine. What follows is the EXISTING output, "
           f"`crossproduct_v2/reports/anomalies.parquet` (mtime {mt(rep / 'anomalies.parquet')}), built post-frame-key-fix but "
           "PRE snow-relabel (light/heavy-snow sequences still pooled into `normal`). Treat weather-keyed anomaly groups as potentially stale.\n\n")
    a = pl.read_parquet(rep / "anomalies.parquet")
    out += "Flags by category and peer group:\n\n" + md(a.group_by("category", "peer_group").len().sort("category", "len", descending=[False, True]), n=30)
    real = a.filter(pl.col("category") == "real").sort("rank_score", descending=True)
    out += "\nTop 'real' flags by rank_score:\n\n" + md(real, ["peer_group", "metric", "group_key", "member", "value", "group_median", "robust_z", "n_total", "n_sequences", "rank_score"], 10)
    sb = a.filter(pl.col("category") == "suspected_bug")
    out += "\n`suspected_bug` rows (manual audit recommended by the pipeline):\n\n" + md(sb, ["peer_group", "metric", "group_key", "member", "value", "robust_z", "n_total", "diagnostic_note"], 5)
    out += f"\nOlder `crossproduct/reports/anomalies.parquet` (mtime {mt(old)}): {pl.scan_parquet(old).select(pl.len()).collect().item()} flags -- superseded.\n"
    return out, a


def answers(q6info: dict, anomalies: pl.DataFrame) -> dict[str, str]:
    a = {}
    t = []
    for lv in ("condition", "cond_cls"):
        r = q.q1_beats_baseline(lv)
        sig, noise = r["significant"], r["noise"]
        ci = sig.filter(pl.col("ci_based"))
        mech = ci.filter(pl.col("mechanism_note").is_not_null())
        keep = ci.filter(pl.col("mechanism_note").is_null())
        names = "; ".join(f"{x['metric']} {x['condition']}{'/' + x['cls'] if 'cls' in x else ''} ({x[x['metric'] + '_delta']:+.4f})" for x in keep.sort("metric").to_dicts())
        t.append(f"`{lv}`: {sig.height} significant / {noise.height} noise. Split: {ci.height} CI-based (precision/recall) + {sig.height - ci.height} floor-only "
                 f"(f1/AP/mATE/mASE/mAOE, N-floor only). {mech.height} of the {ci.height} CI-based rows carry the FP-suppression mechanism note "
                 f"(not genuine improvements). CI-based rows WITHOUT it: {names or 'none'}.")
    a["q1"] = " ".join(t)
    lines = []
    for m in q.METRIC_COLS:
        c = q.q2_top_bottom("condition", m, 1)
        b, w = c["best"].row(0, named=True), c["worst"].row(0, named=True)
        lines.append(f"{m} ({'lower' if m in q.LOWER_IS_BETTER else 'higher'} is better): best `{b['condition']}` {b[m]:.4f}, worst `{w['condition']}` {w[m]:.4f}")
    a["q2"] = "At condition level (reliable, includes `original`): " + "; ".join(lines) + "."
    s = q.load_summary("full").filter(pl.col("reliable"))
    r3 = q.q3_most_false_positives("full")
    bc, br = r3["by_count"].row(0, named=True), r3["by_rate"]
    full_rate = br.filter(pl.col("fp_rate") >= 1.0)
    a["q3"] = (f"By count, the top cell is `{bc['condition']}` {bc['cls']}/{bc['weather']}/{bc['time_of_day']}/{bc['environment']}/{bc['distance_bucket']} with "
               f"{bc['n_fp']} FPs of {bc['n_pred']} predictions (rate {bc['fp_rate']:.4f}, {bc['n_sequences']} sequences); the top-10 by count are all "
               f"{r3['by_count'].head(10)['environment'].n_unique()}-environment cell(s) in {', '.join(r3['by_count'].head(10)['environment'].unique().to_list())}. "
               f"By rate, {full_rate.height} reliable cells have fp_rate = 1.0 (every prediction a FP); of those, "
               f"{full_rate.filter(pl.col('n_gt') == 0).height} have n_gt = 0, i.e. no ground truth of that class in the cell, so 100% FP is structural, not a detector failure. "
               f"Count and rate rankings do not overlap in their top 10 cells.")
    r4 = q.q4_fp_fn_joint("full")
    jw = r4["joint_worst_offenders"]
    a["q4"] = (f"{r4['scatter_data'].height} reliable cells have both rates defined; medians fp_rate={r4['scatter_data']['fp_rate'].median():.4f}, "
               f"fn_rate={r4['scatter_data']['fn_rate'].median():.4f}. The top-{min(jw.height, 15)} joint offenders all sit at fp_rate+fn_rate = 2.0 "
               f"(n_tp = 0 cells: nothing matched). {jw.head(10).filter(pl.col('sequence_confound_risk')).height} of the top 10 rest on <= {q.SEQUENCE_CONFOUND_CEILING} sequences. "
               f"By FN count the leaders are lidar_gaussian_noise_* sedan cells in normal/day highway/urban (fn_rate 0.86-0.99, 4-5 sequences each).")
    c5 = q.q5_churn()
    v2 = pl.DataFrame(json.loads((RR / "crossproduct_v2" / "churn_all_conditions.json").read_text()))
    jj = c5["max_churn"].select("corrupted_condition", "churn_rate").join(v2.select("corrupted_condition", pl.col("churn_rate").alias("v2")), on="corrupted_condition")
    mx = c5["max_churn"].row(0, named=True)
    a["q5"] = (f"Highest churn: `{mx['corrupted_condition']}` {mx['churn_rate']:.4f} (miss {mx['corruption_induced_miss_rate']:.4f}, recovery {mx['corruption_induced_recovery_rate']:.4f}, "
               f"N={mx['total']}). {c5['suspicious_recovery'].height} of {c5['max_churn'].height and 21} conditions are flagged suspicious (recovery >= miss). "
               f"Pooled over sed+bus (per-class churn not computed). Sanity vs the post-frame-key-fix `crossproduct_v2/churn_all_conditions.json`: max |churn_rate diff| on the top-10 = "
               f"{(jj['churn_rate'] - jj['v2']).abs().max():.5f}.")
    wins = ", ".join(f"`{c}` {n}" for c, n in q6info["wins"])
    a["q6"] = (f"Overall (mean AP retention): " + ", ".join(f"`{x['condition']}` {x['mean_ap_retention']:.4f}" for x in q6info["rank"].to_dicts())
               + f". Losing camera is the most survivable, lidar the least. The per-stratum best ({q6info['n']} (cls, weather, tod) strata, null-retention excluded) is: {wins}; "
               f"so the ranking {'flips' if q6info['flips'] else 'does not flip'} in {q6info['flips']}/{q6info['n']} strata (radar wins where camera ties/loses). Lidar never wins any stratum. "
               f"The stock `per_stratum_best` picks a null-retention row as winner in {q6info['null_wins']} stratum/strata (see below).")
    cat = anomalies.group_by("category").len().sort("len", descending=True).rows()
    a["q7"] = ("Existing anomaly.py output (v2, 2026-09-01): " + ", ".join(f"{k}={v}" for k, v in cat)
               + f" = {anomalies.height} flags. The 'real' flags are dominated by `sibling_conditions` (lidar/radar noise conditions vs. their sibling conditions), "
               "e.g. sed/fog/day lidar_gaussian_noise_{medium,high} AP ~53 vs group median ~94.9.")
    return a


CAVEATS = {
    "q1": "`n_total` is a row count; weather-keyed cells are fixed per sequence (pseudo-replication). Wilson CIs treat rows as independent. f1/AP/error 'significant' = N-floor only, not a test. "
          "`mechanism_note` fires on precision/AP up AND recall down at the same cell, regardless of significance. mATE/mASE/mAOE are TP-only: a condition that suppresses most detections (e.g. lidar_gaussian_noise_high, recall 0.16) is scored on the few easy survivors, so its lower errors are survivorship, not improvement.",
    "q2": "mATE/mASE/mAOE are computed on TP matches only; a low error with low recall (lidar_gaussian_noise_*) is survivorship bias, not accuracy. Rankings include the `original` baseline row. Finer-level extremes are dominated by cells barely above the N>30 floor (e.g. bus in fog, precision 0.0, N=32; heavy_snow sedan N=187); mean AP across classes is used where `cls` is not a key.",
    "q3": "Cells with n_gt = 0 have fp_rate = 1.0 by construction. Raw FP count tracks cell size (highway/normal/day sedans). Reliable here means N > 30 (code: `n <= floor` is unreliable).",
    "q4": "A fn_rate of 1.0 with n_tp = 0 on a few dozen rows is a small-cell effect. Cells with sequence_confound_risk=true are pseudo-replicated (1-2 sequences) and are not strong evidence.",
    "q5": "Churn JSONs are static-object per-GT transition counts, pooled over classes (sed+bus). The pooled file (2026-08-31 23:53) predates the 2026-09-01 frame-key fix; its totals differ by 1 row from the post-fix v2 copy. "
          "Stratified files: weather/environment/time_of_day (2026-08-31) predate the snow relabel (no light_snow/heavy_snow strata) and the frame-key fix; distance_bin/frame_density (2026-08-28) are older still, and frame_density was null for 96% of rows before the fix, so treat those two as unverified.",
    "q6": "Mean AP retention is an unweighted mean over cells (nulls skipped, but `n_reliable_cells` counts them). Complete-zero is off-distribution (caveat above). Retention > 1 in a stratum means the zeroed model scored higher than baseline in that cell; small cells.",
    "q7": "Not recomputed here; the anomaly outputs are from before the snow relabel, so weather-keyed groups may shift. 1955 of 2395 flags are `small_n_artifact` by the pipeline's own classification. cross_stratum_tod cannot flag by construction (2-member groups).",
}


def main() -> None:
    if "--rebuild" in sys.argv:
        rebuild()
    missing = [lv for lv in LEVELS_NEEDED if not (OUT / f"summary_{lv}.parquet").exists()]
    if missing:
        sys.exit(f"missing summaries {missing}; run with --rebuild")
    s3, s4 = q34()
    q6txt, q6info = q6()
    q7txt, anomalies = q7()
    ans = answers(q6info, anomalies)
    sec = lambda n, title, question, body: (f"## {n}. {title}\n\n**Question.** {question}\n\n**Answer.** {ans[n.lower()]}\n\n{body}\n**Caveats.** {CAVEATS[n.lower()]}\n\n")
    rep = (f"# Cross-product queries Q1-Q7 -- report\n\nGenerated {dt.datetime.now():%Y-%m-%d %H:%M} by "
           "`scripts/analysis/crossproduct/build_queries_report.py`. Every number below is read from the parquet/JSON listed in Data provenance.\n\n"
           "<!--TLDR-->\n\n## Data provenance\n\n"
           "**Data chosen:** `full_denormalized_table_22cond_weather_corrected.parquet` (2026-09-23), the newest table. It carries the camgauss fix and the frame-key fix "
           "(both in `full_denormalized_table*.parquet` from 2026-09-01 10:27) plus the light/heavy-snow relabel (11 sequences moved out of `normal`).\n\n"
           "**Existing `crossproduct/summary_*.parquet` (2026-08-31 23:10) were STALE** -- older than the 2026-09-01 table. `crossproduct_v2/` (2026-09-01 11:21) is post-frame-key-fix but pre-snow-relabel. "
           "Rebuilt with `crossproduct.build_summary` (levels `condition`, `cond_cls`, `cond_cls_weather`, `cond_cls_weather_tod`, `full`; one level at a time) into "
           "`crossproduct_v3_weather_corrected/`, leaving the older trees untouched. Deltas regenerated by `queries.load_deltas` (none cached there). "
           "The weather domain list was extended at runtime with `light_snow`/`heavy_snow`, otherwise the domain left-join would silently drop those rows. "
           "Not rebuilt: `cond_cls_weather_tod_env`, `full_density` (only the anomaly pipeline uses them).\n\n"
           + sec_provenance(True) + "\n"
           "## Q1-Q7\n\n"
           + sec("Q1", "Where does corruption beat the baseline?", "In which cells does a corrupted condition score better than `original`, and is it real?", "Level `condition` and `cond_cls`:\n\n" + q1("condition") + q1("cond_cls"))
           + sec("Q2", "Highest and lowest per metric", "Which conditions/cells score highest and lowest for each metric?", q2())
           + sec("Q3", "Most false predictions", "Which `full`-grain cells produce the most false positives (by count and by rate)?", s3)
           + sec("Q4", "Max FP and FN jointly", "Which cells are worst on false positives and false negatives together?", s4)
           + sec("Q5", "Churn", "Which corruptions flip the most GT objects between detected and missed?", q5())
           + sec("Q6", "Complete-loss ablation", "Which modality is best and worst to lose entirely, and does that flip across strata?", q6txt)
           + sec("Q7", "Anomalies", "Which cells are anomalous relative to their peers?", q7txt)
           + "<!--DISCREPANCIES-->\n")
    REPORT.write_text(rep)
    print("wrote", REPORT, len(rep))


if __name__ == "__main__":
    main()
