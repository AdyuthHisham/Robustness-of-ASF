"""RR dot-strip: same data as generate_rr_heatmap_marginal.py, alternate
encoding chosen after the heatmap's binary N>=30 hatch failed to show density
continuously (see session_transfer_density_viz.md). One row per marginal
stratum value, one dot per condition: color=RR delta, size=sqrt(min(N_corrupted,
N_clean)) continuous -- density readable at a glance, no second figure needed.

Source: repos/K-Radar/outputs/robustness_reports/crossproduct_v2/summary_full_density.parquet
Run: uv run --project test-bed/src/Modules/robust_testing/kradar python docs/crossproduct_figures/generate_rr_dotstrip_marginal.py
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
joined = joined.with_columns((pl.col("ap_restricted_range") / pl.col("ap_clean")).alias("ratio"))

points = []  # (row_label, condition, rr_delta, n_effective, reliable)
for dim in STRATUM_COLS:
    agg = joined.group_by(["condition", dim]).agg(
        ((pl.col("ratio") * pl.col("num_gt")).sum() / pl.col("num_gt").sum() - 1).alias("rr_delta"),
        pl.col("n_total").sum().alias("n_total_sum"),
        pl.col("n_total_clean").sum().alias("n_total_clean_sum"),
    )
    agg = agg.with_columns(
        pl.min_horizontal("n_total_sum", "n_total_clean_sum").alias("n_effective"),
        ((pl.col("n_total_sum") > N_FLOOR) & (pl.col("n_total_clean_sum") > N_FLOOR)).alias("reliable"),
    )
    for r in agg.iter_rows(named=True):
        points.append((f"{dim}={r[dim]}", r["condition"], r["rr_delta"], r["n_effective"], r["reliable"]))

conditions = sorted({c for _, c, _, _, _ in points})
row_order = []
for dim in STRATUM_COLS:
    vals = sorted(df[dim].unique().drop_nulls().to_list())
    row_order += [f"{dim}={v}" for v in vals]

by_row = {r: [] for r in row_order}
for label, cond, rr, n_eff, rel in points:
    by_row[label].append((cond, rr, n_eff, rel))

keep_row = [r for r in row_order if any(p[3] and p[3] > 0 for p in by_row[r])]
n_dropped = len(row_order) - len(keep_row)

# --- verify one plotted point against source parquet -----------------------
check_label = keep_row[0]
check_dim, check_val = check_label.split("=", 1)
check_cond, check_rr, check_n, check_rel = by_row[check_label][0]
manual = joined.filter((pl.col(check_dim) == check_val) & (pl.col("condition") == check_cond))
manual_rr = (manual["ratio"] * manual["num_gt"]).sum() / manual["num_gt"].sum() - 1
manual_n = min(manual["n_total"].sum(), manual["n_total_clean"].sum())
assert np.isclose(manual_rr, check_rr), (manual_rr, check_rr)
assert manual_n == check_n, (manual_n, check_n)
print(f"verification OK: row={check_label} condition={check_cond} rr={check_rr:.4f} n={check_n}")
print(f"rows: {len(row_order)} total, {n_dropped} dropped (no reliable cell), {len(keep_row)} plotted")
print(f"conditions: {len(conditions)}")

row_idx = {r: i for i, r in enumerate(keep_row)}
cond_idx = {c: j for j, c in enumerate(conditions)}

xs, ys, colors, sizes, edge_colors = [], [], [], [], []
for label in keep_row:
    for cond, rr, n_eff, rel in by_row[label]:
        xs.append(cond_idx[cond])
        ys.append(row_idx[label])
        colors.append(rr)
        sizes.append(20 + 80 * np.sqrt(max(n_eff, 0) / 200))  # continuous, sqrt scale, area-proportional-ish
        edge_colors.append("0.25" if rel else "#c0392b")

fig_h = max(5, 0.32 * len(keep_row))
fig, ax = plt.subplots(figsize=(0.5 * len(conditions) + 3.5, fig_h))
cmap = plt.matplotlib.colormaps["RdYlGn"].copy()
# rr_delta is hard-floored at -1 (ratio can't go below 0); vlim=1 matches that
# floor exactly so the color range isn't wasted on unreachable values. Gamma
# stretches contrast near the extremes -- linear scaling crushed -0.3..-1.0
# into near-identical saturated red since most bad cells cluster near the floor.
vlim = 1.0
gamma = 1.8
norm = plt.matplotlib.colors.FuncNorm(
    (lambda x: np.sign(x) * np.abs(x) ** gamma, lambda y: np.sign(y) * np.abs(y) ** (1 / gamma)),
    vmin=-vlim, vmax=vlim,
)
p95 = np.nanpercentile(np.abs(colors), 95)
sc = ax.scatter(
    xs, ys, c=colors, s=sizes, cmap=cmap, norm=norm,
    edgecolors=edge_colors, linewidths=0.6, zorder=3,
)
ax.set_xlim(-0.5, len(conditions) - 0.5)
ax.set_ylim(-0.5, len(keep_row) - 0.5)
ax.invert_yaxis()
ax.set_xticks(range(len(conditions)))
ax.set_xticklabels(conditions, rotation=90, fontsize=6.5)
ax.set_yticks(range(len(keep_row)))
ax.set_yticklabels(keep_row, fontsize=6.5)
ax.grid(True, axis="both", color="0.9", linewidth=0.5, zorder=0)
ax.set_xlabel("individual corruption condition (severity not merged)")
ax.set_ylabel("single stratum-dimension value (marginalized over other dims + cls)")
ax.set_title(
    "RR delta by condition x stratum -- dot color = RR, dot size = sqrt(effective N)\n"
    "0 = same as clean, negative = worse, positive = better; colorbar clipped at "
    f"±{vlim:.2f} (95th pctile |delta| = {p95:.2f})\n"
    f"red outline = below N>{N_FLOOR} reliability floor; no dot = no data; "
    f"{n_dropped} rows dropped for zero reliable support",
    fontsize=9,
)
fig.colorbar(sc, ax=ax, shrink=0.5, label="RR delta (ratio)", extend="both")

# size legend
for n_ref, label in [(30, "N=30"), (200, "N=200"), (1000, "N=1000")]:
    ax.scatter([], [], s=20 + 80 * np.sqrt(n_ref / 200), c="0.6", edgecolors="0.25", linewidths=0.6, label=label)
ax.legend(title="effective N", loc="upper left", bbox_to_anchor=(1.02, 1.0), fontsize=7, title_fontsize=7)

fig.tight_layout()
fig.savefig(OUT / "rr_dotstrip_marginal.png", bbox_inches="tight")
fig.savefig(OUT / "rr_dotstrip_marginal.svg", bbox_inches="tight")
plt.close(fig)
print("saved ->", OUT / "rr_dotstrip_marginal.png", "and .svg")
