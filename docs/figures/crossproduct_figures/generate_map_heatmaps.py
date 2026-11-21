"""mAP heatmaps: condition-factor levels (y) x corruption type (x).

Analytical question: for each experimental factor (weather, time_of_day,
environment, distance_bucket, frame_density), which corruption types cause
the largest mAP drop at which factor levels?

A single heatmap crossing all 5 factors x 21 corruptions was checked and
rejected: at that granularity (summary_full_density.parquet) only 5,347/
42,240 cells have a non-null ap_restricted_range and 38,973/42,240 fail the
repo's N_FLOOR=30 reliability floor -- see docs/crossproduct_figures/
generate_plots.py. Instead this produces 5 small-multiple heatmaps, each
marginalizing the OTHER 4 factors out via a num_gt-weighted mean of
reliable, non-null ap_restricted_range values (unweighted mean-of-means
across sparse cells would let near-empty cells dominate the average).
Cells with zero reliable support are left blank; cells whose mAP is a
weighted blend that includes some unreliable rows are hatched.

mAP = ap_restricted_range averaged over `cls` (repo's AP proxy; not a
literal "mAP" column -- see reports/findings.md in the source dir).
'original' (uncorrupted baseline) is excluded from the corruption axis.

Source: repos/K-Radar/outputs/robustness_reports/crossproduct_v2/
Run: uv run --project test-bed/src/Modules/robust_testing/kradar python docs/crossproduct_figures/generate_map_heatmaps.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import polars as pl

REPO_ROOT = Path("/home/adhish/Productivity/AMSCUP")
BASE = REPO_ROOT / "repos/K-Radar/outputs/robustness_reports/crossproduct_v2"
OUT = REPO_ROOT / "docs/crossproduct_figures"
OUT.mkdir(parents=True, exist_ok=True)

N_FLOOR = 30
DISTANCE_MERGE = {
    "near_0_20": "near_0_20",
    "mid_20_40": "mid_20_40",
    "far_40_60": "far_40_plus",
    "very_far_60_75": "far_40_plus",
}
CORRUPTION_ORDER = None  # filled after load, sorted by modality then name


def load(name: str) -> pl.DataFrame:
    return pl.read_parquet(BASE / f"{name}.parquet")


def weighted_map_by_factor(df: pl.DataFrame, factor: str) -> pl.DataFrame:
    """Weighted-mean mAP per (factor level, condition), weighted by num_gt.

    Weighting by num_gt (not a plain mean of ap_restricted_range rows)
    avoids letting near-empty (weather, tod, env, distance, density, cls)
    cells pull the marginal average as hard as well-supported ones.
    """
    d = df.filter(pl.col("condition") != "original")
    d = d.filter(pl.col("ap_restricted_range").is_not_null())
    agg = (
        d.group_by([factor, "condition"])
        .agg(
            weighted_map=(pl.col("ap_restricted_range") * pl.col("num_gt")).sum()
            / pl.col("num_gt").sum(),
            n_total=pl.col("n_total").sum(),
            all_reliable=pl.col("reliable").all(),
            any_reliable=pl.col("reliable").any(),
        )
        .filter(pl.col("any_reliable"))  # drop cells with zero reliable support
    )
    return agg.rename({factor: "level"})


def plot_heatmap(agg: pl.DataFrame, title: str, ylabel: str, ax) -> None:
    conditions = sorted(agg["condition"].unique().to_list())
    levels = sorted(agg["level"].unique().to_list())
    grid = np.full((len(levels), len(conditions)), np.nan)
    unreliable_mask = np.zeros_like(grid, dtype=bool)

    row_idx = {v: i for i, v in enumerate(levels)}
    col_idx = {v: i for i, v in enumerate(conditions)}
    for r in agg.iter_rows(named=True):
        i, j = row_idx[r["level"]], col_idx[r["condition"]]
        grid[i, j] = r["weighted_map"]
        unreliable_mask[i, j] = not r["all_reliable"]

    im = ax.imshow(grid, aspect="auto", cmap="RdYlGn", vmin=0, vmax=100)
    for i in range(len(levels)):
        for j in range(len(conditions)):
            if unreliable_mask[i, j]:
                ax.add_patch(
                    plt.Rectangle(
                        (j - 0.5, i - 0.5), 1, 1, fill=False, hatch="///",
                        edgecolor="0.3", linewidth=0,
                    )
                )
    ax.set_xticks(range(len(conditions)))
    ax.set_xticklabels(conditions, rotation=90, fontsize=6)
    ax.set_yticks(range(len(levels)))
    ax.set_yticklabels(levels, fontsize=7)
    ax.set_title(title, fontsize=9)
    ax.set_ylabel(ylabel, fontsize=8)
    return im


def main() -> None:
    full_no_density = load("summary_full")  # weather, tod, env, distance_bucket
    full_density = load("summary_full_density")  # + frame_density
    full_density = full_density.with_columns(
        pl.col("distance_bucket").replace(DISTANCE_MERGE).alias("distance_bucket")
    )
    full_no_density = full_no_density.with_columns(
        pl.col("distance_bucket").replace(DISTANCE_MERGE).alias("distance_bucket")
    )

    factors = [
        ("weather", "Weather", full_no_density),
        ("time_of_day", "Time of day", full_no_density),
        ("environment", "Environment", full_no_density),
        ("distance_bucket", "Distance from ego", full_no_density),
        ("frame_density", "Frame density", full_density),
    ]

    fig, axes = plt.subplots(len(factors), 1, figsize=(11, 22))
    plt.rcParams.update({"figure.dpi": 150, "savefig.dpi": 150})

    im = None
    for ax, (factor, label, src) in zip(axes, factors):
        agg = weighted_map_by_factor(src, factor)
        im = plot_heatmap(agg, f"mAP by {label} x corruption (num_gt-weighted)", label, ax)

    fig.suptitle(
        "K-Radar crossproduct: mAP (ap_restricted_range) by condition factor x corruption\n"
        f"Hatched = weighted mean includes >=1 cell at or below N_FLOOR={N_FLOOR}; "
        "blank = zero reliable support; 'original' baseline excluded from x-axis",
        fontsize=10,
    )
    fig.colorbar(im, ax=axes, label="mAP (ap_restricted_range, %)", fraction=0.015, pad=0.01)
    fig.subplots_adjust(left=0.12, right=0.88, top=0.95, bottom=0.03, hspace=0.9)

    out_path = OUT / "7_map_by_factor_heatmaps.png"
    fig.savefig(out_path)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
