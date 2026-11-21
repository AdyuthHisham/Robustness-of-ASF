"""RR heatmap, split per class instead of cls-weighted average: one heatmap for
"sed" (car) and one for "bus". Same axes as generate_rr_heatmap.py (106 full
strata rows x 21 conditions), just no cross-class averaging -- each figure is
a single class's RR straight from its own (condition, stratum) row. Companion
figures -- no existing script/output touched.

Source: repos/K-Radar/outputs/robustness_reports/crossproduct_v2/summary_full_density.parquet
Run: uv run --project test-bed/src/Modules/robust_testing/kradar python docs/crossproduct_figures/generate_rr_heatmap_by_cls.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import polars as pl

REPO_ROOT = Path("/home/adhish/Productivity/AMSCUP")
BASE = REPO_ROOT / "repos/K-Radar/outputs/robustness_reports/crossproduct_v2"
OUT = REPO_ROOT / "docs/crossproduct_figures"
OUT.mkdir(parents=True, exist_ok=True)

N_FLOOR = 30
STRATUM_COLS = ["weather", "time_of_day", "environment", "distance_bucket", "frame_density"]
CLS_LABELS = {"sed": "car (sed)", "bus": "bus"}

df_all = pl.read_parquet(BASE / "summary_full_density.parquet")


def build_for_cls(cls: str):
    df = df_all.filter(pl.col("cls") == cls)

    baseline = (
        df.filter(pl.col("condition") == "original")
        .select([*STRATUM_COLS, "ap_restricted_range", "reliable"])
        .rename({"ap_restricted_range": "ap_clean", "reliable": "reliable_clean"})
    )
    corrupted = df.filter(pl.col("condition") != "original")
    joined = corrupted.join(baseline, on=STRATUM_COLS, how="inner")
    joined = joined.filter(
        pl.col("ap_restricted_range").is_not_null()
        & pl.col("ap_clean").is_not_null()
        & (pl.col("ap_clean") > 0)
    )
    joined = joined.with_columns(
        (pl.col("ap_restricted_range") / pl.col("ap_clean") - 1).alias("rr"),
        (pl.col("reliable") & pl.col("reliable_clean")).alias("cell_reliable"),
    )

    conditions = sorted(joined["condition"].unique().to_list())
    strata = joined.select(STRATUM_COLS).unique().sort(STRATUM_COLS).rows()
    strata_labels = ["|".join(s) for s in strata]

    value = np.full((len(strata), len(conditions)), np.nan)
    reliable_grid = np.zeros((len(strata), len(conditions)), dtype=bool)
    has_value = np.zeros((len(strata), len(conditions)), dtype=bool)

    stratum_idx = {s: i for i, s in enumerate(strata)}
    cond_idx = {c: j for j, c in enumerate(conditions)}

    for row in joined.iter_rows(named=True):
        s = tuple(row[c] for c in STRATUM_COLS)
        i, j = stratum_idx[s], cond_idx[row["condition"]]
        value[i, j] = row["rr"]
        reliable_grid[i, j] = row["cell_reliable"]
        has_value[i, j] = True

    keep_row = (has_value & reliable_grid).any(axis=1)
    n_dropped = (~keep_row).sum()
    value = value[keep_row]
    reliable_grid = reliable_grid[keep_row]
    has_value = has_value[keep_row]
    strata_labels = [lbl for lbl, k in zip(strata_labels, keep_row) if k]

    # --- verify plotted values against source parquet ---------------------
    kept_idx = np.nonzero(keep_row)[0][0]
    check_s = strata[kept_idx]
    check_cond = conditions[0]
    manual = joined.filter(
        (pl.col("condition") == check_cond)
        & (pl.col("weather") == check_s[0])
        & (pl.col("time_of_day") == check_s[1])
        & (pl.col("environment") == check_s[2])
        & (pl.col("distance_bucket") == check_s[3])
        & (pl.col("frame_density") == check_s[4])
    )
    manual_rr = manual["rr"][0] if manual.height else float("nan")
    print(f"[{cls}] verification: row={check_s} cond={check_cond} plotted={value[0,0]:.4f} manual={manual_rr:.4f}")
    assert np.isclose(manual_rr, value[0, 0], equal_nan=True), (manual_rr, value[0, 0])
    print(f"[{cls}] verification OK")
    print(f"[{cls}] strata: {len(strata)} total, {n_dropped} dropped, {len(strata_labels)} plotted, conditions: {len(conditions)}")

    fig_h = max(6, 0.11 * len(strata_labels))
    fig, ax = plt.subplots(figsize=(0.55 * len(conditions) + 3, fig_h))
    cmap = plt.matplotlib.colormaps["RdYlGn"].copy()
    cmap.set_bad("#F3F4F6")
    cmap.set_over("#08306b")
    cmap.set_under("#3f0000")
    masked = np.ma.masked_invalid(value)
    vlim = 1.2
    p95 = np.nanpercentile(np.abs(value), 95)
    im = ax.imshow(masked, aspect="auto", cmap=cmap, vmin=-vlim, vmax=vlim)

    for i in range(value.shape[0]):
        for j in range(value.shape[1]):
            if not has_value[i, j]:
                continue
            if not reliable_grid[i, j]:
                ax.add_patch(
                    mpatches.Rectangle(
                        (j - 0.5, i - 0.5), 1, 1, fill=False,
                        hatch="////", edgecolor="0.35", linewidth=0,
                    )
                )

    ax.set_xticks(range(len(conditions)))
    ax.set_xticklabels(conditions, rotation=90, fontsize=6.5)
    ax.set_yticks(range(len(strata_labels)))
    ax.set_yticklabels(strata_labels, fontsize=4.2)
    ax.set_xlabel("corruption condition")
    ax.set_ylabel("weather|time_of_day|environment|distance_bucket|frame_density")
    ax.set_title(
        f"RR delta, cls={CLS_LABELS.get(cls, cls)} only (no cross-class weighting)\n"
        "0 = same as clean baseline, negative = worse, positive = better; "
        f"colorbar clipped at ±{vlim:.2f} (95th pctile |delta| = {p95:.2f})\n"
        f"(hatched = N≤{N_FLOOR}; {n_dropped} strata dropped for zero reliable support)",
        fontsize=9,
    )
    fig.colorbar(im, ax=ax, shrink=0.5, label="RR delta (ratio)", extend="both")
    fig.tight_layout()
    out_path = OUT / f"rr_heatmap_{cls}.png"
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"[{cls}] saved -> {out_path}")


for cls in ["sed", "bus"]:
    build_for_cls(cls)
