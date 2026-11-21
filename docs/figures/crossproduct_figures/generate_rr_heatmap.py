"""RR (Resilience Rate) heatmap: one row per (weather, time_of_day, environment,
distance_bucket, frame_density) stratum, one column per corruption condition.

RR = 100 * corrupted.ap_restricted_range / clean.ap_restricted_range, where clean
is the condition=="original" row in the SAME stratum. Per-stratum RR is averaged
over cls (sed, bus), weighted by corrupted num_gt.

Source: repos/K-Radar/outputs/robustness_reports/crossproduct_v2/summary_full_density.parquet
Run: uv run --project test-bed/src/Modules/robust_testing/kradar python docs/crossproduct_figures/generate_rr_heatmap.py
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

df = pl.read_parquet(BASE / "summary_full_density.parquet")

baseline = (
    df.filter(pl.col("condition") == "original")
    .select(
        ["cls", *STRATUM_COLS, "ap_restricted_range", "reliable"]
    )
    .rename({"ap_restricted_range": "ap_clean", "reliable": "reliable_clean"})
)

corrupted = df.filter(pl.col("condition") != "original")

joined = corrupted.join(baseline, on=["cls", *STRATUM_COLS], how="inner")
joined = joined.filter(
    pl.col("ap_restricted_range").is_not_null()
    & pl.col("ap_clean").is_not_null()
    & (pl.col("ap_clean") > 0)
)
joined = joined.with_columns(
    (pl.col("ap_restricted_range") / pl.col("ap_clean") - 1).alias("rr"),
    (pl.col("reliable") & pl.col("reliable_clean")).alias("cell_reliable"),
)

# weighted (by corrupted num_gt) average of RR over cls, per (condition, stratum)
agg = joined.group_by(["condition", *STRATUM_COLS]).agg(
    ((pl.col("rr") * pl.col("num_gt")).sum() / pl.col("num_gt").sum()).alias("rr_weighted"),
    pl.col("cell_reliable").all().alias("all_reliable"),
)

conditions = sorted(agg["condition"].unique().to_list())
strata = (
    agg.select(STRATUM_COLS)
    .unique()
    .sort(STRATUM_COLS)
    .rows()
)
strata_labels = ["|".join(s) for s in strata]

value = np.full((len(strata), len(conditions)), np.nan)
reliable_grid = np.zeros((len(strata), len(conditions)), dtype=bool)
has_value = np.zeros((len(strata), len(conditions)), dtype=bool)

stratum_idx = {s: i for i, s in enumerate(strata)}
cond_idx = {c: j for j, c in enumerate(conditions)}

for row in agg.iter_rows(named=True):
    s = tuple(row[c] for c in STRATUM_COLS)
    i, j = stratum_idx[s], cond_idx[row["condition"]]
    value[i, j] = row["rr_weighted"]
    reliable_grid[i, j] = row["all_reliable"]
    has_value[i, j] = True

# drop rows (strata) with zero reliable support across all conditions
keep_row = (has_value & reliable_grid).any(axis=1)
n_dropped = (~keep_row).sum()
value = value[keep_row]
reliable_grid = reliable_grid[keep_row]
has_value = has_value[keep_row]
strata_labels = [lbl for lbl, k in zip(strata_labels, keep_row) if k]

# --- verify plotted values against source parquet -------------------------
check_row = strata_labels[0]
check_s = strata[np.nonzero(keep_row)[0][0]]
check_cond = conditions[0]
manual = joined.filter(
    (pl.col("condition") == check_cond)
    & (pl.col("weather") == check_s[0])
    & (pl.col("time_of_day") == check_s[1])
    & (pl.col("environment") == check_s[2])
    & (pl.col("distance_bucket") == check_s[3])
    & (pl.col("frame_density") == check_s[4])
)
if manual.height:
    w = (manual["rr"] * manual["num_gt"]).sum() / manual["num_gt"].sum()
    assert np.isclose(w, value[0, 0], equal_nan=True), (w, value[0, 0])
print(f"verification OK: cell [0,0] = {value[0,0]:.3f} (manual = {w if manual.height else 'n/a'})")
print(f"strata: {len(strata)} total, {n_dropped} dropped (zero reliable support), {len(strata_labels)} plotted")
print(f"conditions: {len(conditions)}")

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
    "Resilience Rate delta (RR = corrupted/clean ap_restricted_range − 1), cls-weighted\n"
    "0 = same as clean baseline, negative = worse, positive = better; "
    f"colorbar clipped at ±{vlim:.2f} (95th pctile |delta| = {p95:.2f})\n"
    f"(hatched = weighted RR includes ≥1 cell with N≤{N_FLOOR}; "
    f"{n_dropped} strata dropped for zero reliable support)",
    fontsize=9,
)
fig.colorbar(im, ax=ax, shrink=0.5, label="RR delta (ratio)", extend="both")
fig.tight_layout()
fig.savefig(OUT / "rr_heatmap.png", bbox_inches="tight")
plt.close(fig)
print("saved ->", OUT / "rr_heatmap.png")
