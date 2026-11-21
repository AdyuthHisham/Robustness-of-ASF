"""mRR heatmap, Y-axis collapsed to single-dimension marginals: e.g. "weather=fog"
row averages over all time_of_day/environment/distance_bucket/frame_density/cls, not
one row per 5-way stratum combo. Companion to generate_mrr_heatmap.py (kept, not
overwritten) -- same column definition (modality_effect group, severities merged).

Row = one value of one stratum dimension (weather, time_of_day, environment,
distance_bucket, or frame_density), marginalized over the other 4 dims + cls.
Cell = mRR_delta = mean_over_severities(corrupted.ap_restricted_range / clean.ap_restricted_range) − 1,
num_gt-weighted within each severity across everything collapsed, before averaging severities.

Source: repos/K-Radar/outputs/robustness_reports/crossproduct_v2/summary_full_density.parquet
Run: uv run --project test-bed/src/Modules/robust_testing/kradar python docs/crossproduct_figures/generate_mrr_heatmap_marginal.py
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
    .select(["cls", *STRATUM_COLS, "ap_restricted_range", "n_total"])
    .rename({"ap_restricted_range": "ap_clean", "n_total": "n_total_clean"})
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
    (pl.col("modality") + "_" + pl.col("effect")).alias("group"),
)

# for each dimension, marginalize over the other 4 dims + cls: weighted ratio per
# (group, severity, dim_value), then mean across severities (RoboBEV RR_i).
# reliability recomputed from the SUMMED n_total after marginalizing, not from
# per-fine-cell reliability flags (which would almost never all be true post-collapse).
rows = []  # (row_label, group, mrr_delta, all_reliable)
for dim in STRATUM_COLS:
    per_severity = joined.group_by(["group", "severity", dim]).agg(
        ((pl.col("ratio") * pl.col("num_gt")).sum() / pl.col("num_gt").sum()).alias("ratio_weighted"),
        pl.col("n_total").sum().alias("n_total_sum"),
        pl.col("n_total_clean").sum().alias("n_total_clean_sum"),
    )
    per_severity = per_severity.with_columns(
        ((pl.col("n_total_sum") > N_FLOOR) & (pl.col("n_total_clean_sum") > N_FLOOR)).alias("reliable")
    )
    agg = per_severity.group_by(["group", dim]).agg(
        (pl.col("ratio_weighted").mean() - 1).alias("mrr_delta"),
        pl.col("reliable").all().alias("all_reliable"),
    )
    for r in agg.iter_rows(named=True):
        rows.append((f"{dim}={r[dim]}", r["group"], r["mrr_delta"], r["all_reliable"]))

groups = sorted({g for _, g, _, _ in rows})
row_order = []
for dim in STRATUM_COLS:
    vals = sorted(df[dim].unique().drop_nulls().to_list())
    row_order += [f"{dim}={v}" for v in vals]

value = np.full((len(row_order), len(groups)), np.nan)
reliable_grid = np.zeros((len(row_order), len(groups)), dtype=bool)
has_value = np.zeros((len(row_order), len(groups)), dtype=bool)

row_idx = {r: i for i, r in enumerate(row_order)}
group_idx = {g: j for j, g in enumerate(groups)}

for label, g, mrr, rel in rows:
    i, j = row_idx[label], group_idx[g]
    value[i, j] = mrr
    reliable_grid[i, j] = rel
    has_value[i, j] = True

keep_row = (has_value & reliable_grid).any(axis=1)
n_dropped = (~keep_row).sum()
value = value[keep_row]
reliable_grid = reliable_grid[keep_row]
has_value = has_value[keep_row]
row_labels = [lbl for lbl, k in zip(row_order, keep_row) if k]

# --- verify plotted values against source parquet -------------------------
check_label = row_labels[0]
check_dim, check_val = check_label.split("=", 1)
check_group = groups[0]
manual_rows = joined.filter(pl.col(check_dim) == check_val).filter(pl.col("group") == check_group)
sev_ratios = []
sev_reliable = []
for sev, sub in manual_rows.group_by("severity"):
    w = (sub["ratio"] * sub["num_gt"]).sum() / sub["num_gt"].sum()
    sev_ratios.append(w)
    sev_reliable.append(sub["n_total"].sum() > N_FLOOR and sub["n_total_clean"].sum() > N_FLOOR)
manual_mrr = (sum(sev_ratios) / len(sev_ratios) - 1) if sev_ratios else float("nan")
print(f"  manual reliability per severity: {sev_reliable}")
print(f"verification: row={check_label} group={check_group}")
print(f"  plotted = {value[0,0]:.4f}, manual (mean over {len(sev_ratios)} severities) = {manual_mrr:.4f}")
assert np.isclose(manual_mrr, value[0, 0], equal_nan=True), (manual_mrr, value[0, 0])
print("verification OK")
print(f"rows: {len(row_order)} total, {n_dropped} dropped (zero reliable support), {len(row_labels)} plotted")
print(f"groups: {len(groups)} -> {groups}")

fig_h = max(5, 0.28 * len(row_labels))
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
ax.set_yticks(range(len(row_labels)))
ax.set_yticklabels(row_labels, fontsize=6.5)
ax.set_xlabel("condition group (severities merged via mRR)")
ax.set_ylabel("single stratum-dimension value (marginalized over other dims + cls)")
ax.set_title(
    "mRR delta, Y-axis marginalized to single dimension — RR_i = mean_l(corrupted/clean) − 1\n"
    "0 = same as clean baseline, negative = worse, positive = better; "
    f"colorbar clipped at ±{vlim:.2f} (95th pctile |delta| = {p95:.2f})\n"
    f"(hatched = ≥1 merged severity cell has N≤{N_FLOOR}; "
    f"{n_dropped} rows dropped for zero reliable support)",
    fontsize=9,
)
fig.colorbar(im, ax=ax, shrink=0.5, label="mRR delta (ratio)", extend="both")
fig.tight_layout()
fig.savefig(OUT / "mrr_heatmap_marginal.png", bbox_inches="tight")
plt.close(fig)
print("saved ->", OUT / "mrr_heatmap_marginal.png")
