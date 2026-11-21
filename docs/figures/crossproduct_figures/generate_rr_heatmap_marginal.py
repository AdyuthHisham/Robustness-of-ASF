"""RR heatmap: Y-axis condensed to single-dimension marginals (as in
generate_mrr_heatmap_marginal.py), X-axis expanded to all 21 individual
conditions, severities NOT merged (as in generate_rr_heatmap.py). Companion
figure -- neither existing script/output is touched.

Row = one value of one stratum dimension (weather, time_of_day, environment,
distance_bucket, or frame_density), marginalized over the other 4 dims + cls.
Column = individual condition (e.g. "lidar_gaussian_noise_low").
Cell = RR_delta = corrupted.ap_restricted_range / clean.ap_restricted_range − 1,
num_gt-weighted within each marginal group.

Source: repos/K-Radar/outputs/robustness_reports/crossproduct_v2/summary_full_density.parquet
Run: uv run --project test-bed/src/Modules/robust_testing/kradar python docs/crossproduct_figures/generate_rr_heatmap_marginal.py
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
    (pl.col("ap_restricted_range") / pl.col("ap_clean")).alias("ratio")
)

# for each dimension, marginalize over the other 4 dims + cls: weighted ratio per
# (condition, dim_value), reliability recomputed from summed n_total post-collapse.
rows = []  # (row_label, condition, rr_delta, all_reliable)
for dim in STRATUM_COLS:
    agg = joined.group_by(["condition", dim]).agg(
        ((pl.col("ratio") * pl.col("num_gt")).sum() / pl.col("num_gt").sum() - 1).alias("rr_delta"),
        pl.col("n_total").sum().alias("n_total_sum"),
        pl.col("n_total_clean").sum().alias("n_total_clean_sum"),
    )
    agg = agg.with_columns(
        ((pl.col("n_total_sum") > N_FLOOR) & (pl.col("n_total_clean_sum") > N_FLOOR)).alias("reliable")
    )
    for r in agg.iter_rows(named=True):
        rows.append((f"{dim}={r[dim]}", r["condition"], r["rr_delta"], r["reliable"]))

conditions = sorted({c for _, c, _, _ in rows})
row_order = []
for dim in STRATUM_COLS:
    vals = sorted(df[dim].unique().drop_nulls().to_list())
    row_order += [f"{dim}={v}" for v in vals]

value = np.full((len(row_order), len(conditions)), np.nan)
reliable_grid = np.zeros((len(row_order), len(conditions)), dtype=bool)
has_value = np.zeros((len(row_order), len(conditions)), dtype=bool)

row_idx = {r: i for i, r in enumerate(row_order)}
cond_idx = {c: j for j, c in enumerate(conditions)}

for label, cond, rr, rel in rows:
    i, j = row_idx[label], cond_idx[cond]
    value[i, j] = rr
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
check_cond = conditions[0]
manual = joined.filter((pl.col(check_dim) == check_val) & (pl.col("condition") == check_cond))
manual_rr = (manual["ratio"] * manual["num_gt"]).sum() / manual["num_gt"].sum() - 1
manual_rel = (manual["n_total"].sum() > N_FLOOR) and (manual["n_total_clean"].sum() > N_FLOOR)
print(f"verification: row={check_label} condition={check_cond}")
print(f"  plotted = {value[0,0]:.4f}, manual = {manual_rr:.4f}, reliable(manual)={manual_rel}")
assert np.isclose(manual_rr, value[0, 0], equal_nan=True), (manual_rr, value[0, 0])
print("verification OK")
print(f"rows: {len(row_order)} total, {n_dropped} dropped (zero reliable support), {len(row_labels)} plotted")
print(f"conditions: {len(conditions)}")

fig_h = max(5, 0.28 * len(row_labels))
fig, ax = plt.subplots(figsize=(0.5 * len(conditions) + 3, fig_h))
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
ax.set_yticks(range(len(row_labels)))
ax.set_yticklabels(row_labels, fontsize=6.5)
ax.set_xlabel("individual corruption condition (severity not merged)")
ax.set_ylabel("single stratum-dimension value (marginalized over other dims + cls)")
ax.set_title(
    "RR delta, Y-axis marginalized to single dimension, X-axis all 21 conditions\n"
    "0 = same as clean baseline, negative = worse, positive = better; "
    f"colorbar clipped at ±{vlim:.2f} (95th pctile |delta| = {p95:.2f})\n"
    f"(hatched = N≤{N_FLOOR} after marginalizing; {n_dropped} rows dropped for zero reliable support)",
    fontsize=9,
)
fig.colorbar(im, ax=ax, shrink=0.5, label="RR delta (ratio)", extend="both")
fig.tight_layout()
fig.savefig(OUT / "rr_heatmap_marginal.png", bbox_inches="tight")
plt.close(fig)
print("saved ->", OUT / "rr_heatmap_marginal.png")
