"""mRR heatmap: severities merged per RoboBEV's RR_i = (1/L)*sum_l(M_corrupted/M_clean),
one column per (modality, effect) condition group (e.g. "lidar_loss_partial"), not per
individual severity. Companion to generate_rr_heatmap.py (kept, not overwritten).

Row = (weather, time_of_day, environment, distance_bucket, frame_density) stratum.
Cell = mRR_delta = mean_over_severities(corrupted.ap_restricted_range / clean.ap_restricted_range) − 1,
cls-weighted (by corrupted num_gt) within each severity before averaging across severities.

Source: repos/K-Radar/outputs/robustness_reports/crossproduct_v2/summary_full_density.parquet
Run: uv run --project test-bed/src/Modules/robust_testing/kradar python docs/crossproduct_figures/generate_mrr_heatmap.py
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
    .select(["cls", *STRATUM_COLS, "ap_restricted_range", "reliable"])
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
    (pl.col("ap_restricted_range") / pl.col("ap_clean")).alias("ratio"),
    (pl.col("reliable") & pl.col("reliable_clean")).alias("cell_reliable"),
    (pl.col("modality") + "_" + pl.col("effect")).alias("group"),
)

# step 1: cls-weighted ratio per (group, severity, stratum) -- this is one RR_{i,l} term
per_severity = joined.group_by(["group", "severity", *STRATUM_COLS]).agg(
    ((pl.col("ratio") * pl.col("num_gt")).sum() / pl.col("num_gt").sum()).alias("ratio_weighted"),
    pl.col("cell_reliable").all().alias("all_reliable"),
)

# step 2: mRR_i = mean over severities (RoboBEV: sum_l / L)
agg = per_severity.group_by(["group", *STRATUM_COLS]).agg(
    (pl.col("ratio_weighted").mean() - 1).alias("mrr_delta"),
    pl.col("all_reliable").all().alias("all_reliable"),
    pl.col("severity").n_unique().alias("n_severities"),
)

groups = sorted(agg["group"].unique().to_list())
strata = agg.select(STRATUM_COLS).unique().sort(STRATUM_COLS).rows()
strata_labels = ["|".join(s) for s in strata]

value = np.full((len(strata), len(groups)), np.nan)
reliable_grid = np.zeros((len(strata), len(groups)), dtype=bool)
has_value = np.zeros((len(strata), len(groups)), dtype=bool)

stratum_idx = {s: i for i, s in enumerate(strata)}
group_idx = {g: j for j, g in enumerate(groups)}

for row in agg.iter_rows(named=True):
    s = tuple(row[c] for c in STRATUM_COLS)
    i, j = stratum_idx[s], group_idx[row["group"]]
    value[i, j] = row["mrr_delta"]
    reliable_grid[i, j] = row["all_reliable"]
    has_value[i, j] = True

keep_row = (has_value & reliable_grid).any(axis=1)
n_dropped = (~keep_row).sum()
value = value[keep_row]
reliable_grid = reliable_grid[keep_row]
has_value = has_value[keep_row]
strata_labels = [lbl for lbl, k in zip(strata_labels, keep_row) if k]

# --- verify plotted values against source parquet -------------------------
kept_idx = np.nonzero(keep_row)[0][0]
check_s = strata[kept_idx]
check_group = groups[0]
manual_sev = joined.filter(
    (pl.col("group") == check_group)
    & (pl.col("weather") == check_s[0])
    & (pl.col("time_of_day") == check_s[1])
    & (pl.col("environment") == check_s[2])
    & (pl.col("distance_bucket") == check_s[3])
    & (pl.col("frame_density") == check_s[4])
)
sev_ratios = []
for sev, sub in manual_sev.group_by("severity"):
    w = (sub["ratio"] * sub["num_gt"]).sum() / sub["num_gt"].sum()
    sev_ratios.append(w)
manual_mrr = (sum(sev_ratios) / len(sev_ratios) - 1) if sev_ratios else float("nan")
print(f"verification: cell [0,0] group={check_group} stratum={check_s}")
print(f"  plotted = {value[0,0]:.4f}, manual (mean over {len(sev_ratios)} severities) = {manual_mrr:.4f}")
assert np.isclose(manual_mrr, value[0, 0], equal_nan=True), (manual_mrr, value[0, 0])
print("verification OK")
print(f"strata: {len(strata)} total, {n_dropped} dropped (zero reliable support), {len(strata_labels)} plotted")
print(f"groups (modality_effect, severity-merged): {len(groups)} -> {groups}")

fig_h = max(6, 0.11 * len(strata_labels))
fig, ax = plt.subplots(figsize=(0.55 * len(groups) + 3, fig_h))
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

ax.set_xticks(range(len(groups)))
ax.set_xticklabels(groups, rotation=90, fontsize=7)
ax.set_yticks(range(len(strata_labels)))
ax.set_yticklabels(strata_labels, fontsize=4.2)
ax.set_xlabel("condition group (severities merged via mRR)")
ax.set_ylabel("weather|time_of_day|environment|distance_bucket|frame_density")
ax.set_title(
    "mRR delta — severities merged (RoboBEV RR_i = mean_l(corrupted/clean) − 1), cls-weighted\n"
    "0 = same as clean baseline, negative = worse, positive = better; "
    f"colorbar clipped at ±{vlim:.2f} (95th pctile |delta| = {p95:.2f})\n"
    f"(hatched = ≥1 merged severity cell has N≤{N_FLOOR}; "
    f"{n_dropped} strata dropped for zero reliable support)",
    fontsize=9,
)
fig.colorbar(im, ax=ax, shrink=0.5, label="mRR delta (ratio)", extend="both")
fig.tight_layout()
fig.savefig(OUT / "mrr_heatmap.png", bbox_inches="tight")
plt.close(fig)
print("saved ->", OUT / "mrr_heatmap.png")
