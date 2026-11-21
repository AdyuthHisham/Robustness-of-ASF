#!/usr/bin/env python3
"""mAP-by-corruption x mAP-by-stratifier tables for the Results section, one
per factor (weather/environment/time_of_day/frame_density/distance_bucket),
each with bus/sed computed SEPARATELY plus a pooled "common" row (both
classes' rows combined into one AP computation, not an average of the two
per-class APs -- see reports/findings.md note added alongside these tables).

AP is K-Radar's own restricted-range AP (eval_revised.py's thresholding,
ported verbatim in ap_metrics.compute_ap -- see that module's docstring for
why this is not a reimplementation but a faithful port). Reliability is
bootstrap block-resampling by `sequence` (not by row): see
bootstrap_reliability.py for the Phase-1-approved rationale. Every cell
reports map_point/map_ci_low/map_ci_high/map_ci_width, N_rows, N_sequences,
and reliability_flag (Phase 1 audit floor extended with N_sequences>=10 per
this task's spec) -- the dual-denominator contract from crossproduct.py's
_counts_and_rates.

Source: repos/K-Radar/outputs/robustness_reports/full_denormalized_table.parquet
Run: uv run --project test-bed/src/Modules/robust_testing/kradar python docs/crossproduct_figures/generate_map_reliability_tables.py
"""
from __future__ import annotations

import sys
from multiprocessing import Pool
from pathlib import Path

import polars as pl

REPO_ROOT = Path("/home/adhish/Productivity/AMSCUP")
ROW_TABLE = REPO_ROOT / "repos/K-Radar/outputs/robustness_reports/full_denormalized_table.parquet"
OUT = REPO_ROOT / "docs/crossproduct_figures"

sys.path.insert(
    0,
    str(
        REPO_ROOT
        / "test-bed/src/Modules/robust_testing/kradar/scripts/analysis/crossproduct"
    ),
)
from bootstrap_reliability import bootstrap_map_grouped  # noqa: E402
from crossproduct import CONDITIONS  # noqa: E402

FACTORS = ["weather", "environment", "time_of_day", "frame_density", "distance_bucket"]
N_ITER = 1000
SEED = 42


def load() -> pl.DataFrame:
    df = pl.read_parquet(ROW_TABLE)
    df = df.filter(pl.col("condition").is_in(CONDITIONS))
    for c in ("distance_bucket", "frame_density"):
        if df[c].dtype != pl.Utf8:
            df = df.with_columns(pl.col(c).cast(pl.Utf8))
    return df


_WORKER_DF: pl.DataFrame | None = None


def _init_worker(df: pl.DataFrame) -> None:
    # Runs once per worker process (fork start method on Linux) -- df is
    # inherited via copy-on-write from the parent, not re-pickled per task.
    global _WORKER_DF
    _WORKER_DF = df


def _run_job(job: tuple[str, str]) -> pl.DataFrame:
    """One (factor, cls) job -- cls is 'sed'/'bus' (per-class AP) or
    'common' (both classes' rows pooled into one AP computation, not an
    average of the two per-class map_points -- pooling changes n_rows/
    n_sequences/CI, an average of point estimates would not)."""
    factor, cls = job
    d = _WORKER_DF.filter(pl.col("condition") != "original")
    if cls == "common":
        out = bootstrap_map_grouped(d, ["condition", factor], seed=SEED, n_iter=N_ITER)
        out = out.with_columns(pl.lit("common").alias("cls"))
    else:
        out = bootstrap_map_grouped(
            d.filter(pl.col("cls") == cls), ["condition", factor], seed=SEED, n_iter=N_ITER
        )
        out = out.with_columns(pl.lit(cls).alias("cls"))
    return out.rename({factor: "level"}).with_columns(pl.lit(factor).alias("factor"))


def build_all_tables(df: pl.DataFrame) -> pl.DataFrame:
    """Every (factor, cls) job is independent -- fan out across processes
    (8 cores available) instead of the ~3-4h serial runtime a single core
    would need for ~1,400 bootstrap cells x 1,000 iterations each."""
    jobs = [(f, cls) for f in FACTORS for cls in ("sed", "bus", "common")]
    with Pool(processes=8, initializer=_init_worker, initargs=(df,)) as pool:
        results = pool.map(_run_job, jobs)
    return pl.concat(results)


def to_latex_table(t: pl.DataFrame, factor: str, cls: str, caption: str, label: str) -> str:
    sub = t.filter((pl.col("factor") == factor) & (pl.col("cls") == cls)).sort(["level", "condition"])
    conditions = sorted(sub["condition"].unique().to_list())
    levels = sorted(sub["level"].unique().to_list())
    lookup = {(r["level"], r["condition"]): r for r in sub.iter_rows(named=True)}

    col_spec = "l" + "c" * len(conditions)
    lines = [
        r"\begin{table}[htbp]", r"\centering", r"\scriptsize",
        r"\begin{tabular}{" + col_spec + "}", r"\toprule",
        "Level & " + " & ".join(conditions) + r" \\", r"\midrule",
    ]
    for lvl in levels:
        cells = []
        for cond in conditions:
            r = lookup.get((lvl, cond))
            if r is None or r["map_point"] is None:
                cells.append("--")
                continue
            flag = "" if r["reliability_flag"] == "reliable" else r"$^{\dagger}$"
            cells.append(
                f"{r['map_point']:.1f}{flag} "
                f"[{r['map_ci_low']:.1f},{r['map_ci_high']:.1f}]"
                f" ({r['n_rows']}r/{r['n_sequences']}s)"
            )
        lines.append(f"{lvl} & " + " & ".join(cells) + r" \\")
    lines += [
        r"\bottomrule", r"\end{tabular}",
        r"\caption{" + caption
        + r" mAP point estimate [95\% bootstrap CI] (N\_rows/N\_sequences)."
          r" $^{\dagger}$flags a cell below the reliability floor"
          r" (N\_rows$<$30 or N\_sequences$<$10) -- interpret as a coverage gap, not a stable estimate.}",
        r"\label{" + label + "}", r"\end{table}", "",
    ]
    return "\n".join(lines)


def main() -> None:
    df = load()
    all_tables = build_all_tables(df)
    all_tables.write_parquet(OUT / "map_reliability_tables.parquet")
    all_tables.write_csv(OUT / "map_reliability_tables.csv")

    tex_parts = []
    for factor in FACTORS:
        for cls, cls_label in (("sed", "Sedan"), ("bus", "Bus"), ("common", "Common (pooled)")):
            label_factor = factor.replace("_", "-")
            tex_parts.append(
                to_latex_table(
                    all_tables, factor, cls,
                    caption=f"{cls_label} mAP by corruption and {factor.replace('_', ' ')}.",
                    label=f"tab:map_{label_factor}_{cls}",
                )
            )
    (OUT / "map_reliability_tables.tex").write_text("\n".join(tex_parts))
    print(f"wrote {len(all_tables)} cells across {len(FACTORS)} factors -> map_reliability_tables.{{parquet,csv,tex}}")


if __name__ == "__main__":
    main()
