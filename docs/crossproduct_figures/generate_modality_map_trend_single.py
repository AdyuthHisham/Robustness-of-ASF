"""mAP-by-modality trend, single-panel version of generate_modality_map_trend.py.
Severities flattened into 7 individual corruptions on one shared x-axis (per
user request: "separate the severities into being individual corruptions" and
"merge into one plot"). Y = mAP normalized to the shared clean baseline (fair
cross-modality comparison, robustness-viz-advisor Core Principle 5 -- camera/
lidar/radar all corrupt the SAME clean scene, so one shared denominator is
correct, not per-modality). Direct line-end labels replace the legend box.

Source: repos/K-Radar/outputs/robustness_reports/crossproduct_v2/summary_full_density.parquet
Run: uv run --project test-bed/src/Modules/robust_testing/kradar python docs/crossproduct_figures/generate_modality_map_trend_single.py
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
COLORS = {"camera": "#1b7837", "lidar": "#2166ac", "radar": "#b2182b"}
MARKERS = {"camera": "o", "lidar": "s", "radar": "^"}

# (effect, severity, x-label, group) -- flattened, ordered low->high within each group
CONDITIONS = [
    ("gaussian_noise", "low", "low", "gaussian noise"),
    ("gaussian_noise", "medium", "medium", "gaussian noise"),
    ("gaussian_noise", "high", "high", "gaussian noise"),
    ("loss_partial", "low", "low", "partial loss"),
    ("loss_partial", "medium", "medium", "partial loss"),
    ("loss_partial", "high", "high", "partial loss"),
    ("loss_complete_zero", None, "complete", "complete loss"),
]

df = pl.read_parquet(BASE / "summary_full_density.parquet")
df = df.filter(pl.col("ap_restricted_range").is_not_null())

clean = df.filter(pl.col("condition") == "original")
clean_map = (clean["ap_restricted_range"] * clean["num_gt"]).sum() / clean["num_gt"].sum()
clean_n = int(clean["n_total"].sum())

corrupted = df.filter(pl.col("condition") != "original")
agg = corrupted.group_by(["modality", "effect", "severity"]).agg(
    ((pl.col("ap_restricted_range") * pl.col("num_gt")).sum() / pl.col("num_gt").sum()).alias("map"),
    pl.col("n_total").sum().alias("n_total_sum"),
)

# --- verify one point against source parquet -------------------------------
check_modality, (check_effect, check_sev, _, _) = "lidar", CONDITIONS[0]
sev_filter = pl.col("severity").is_null() if check_sev is None else pl.col("severity") == check_sev
manual = corrupted.filter(
    (pl.col("modality") == check_modality) & (pl.col("effect") == check_effect) & sev_filter
)
manual_map = (manual["ap_restricted_range"] * manual["num_gt"]).sum() / manual["num_gt"].sum()
plotted = agg.filter(
    (pl.col("modality") == check_modality) & (pl.col("effect") == check_effect)
    & (pl.col("severity").is_null() if check_sev is None else pl.col("severity") == check_sev)
)["map"][0]
assert np.isclose(manual_map, plotted), (manual_map, plotted)
print(f"verification OK: {check_modality}/{check_effect}/{check_sev} mAP={plotted:.3f}")
print(f"clean baseline mAP = {clean_map:.3f} (N={clean_n})")

x = np.arange(len(CONDITIONS))
fig, ax = plt.subplots(figsize=(10, 5.5))

# shaded bands per corruption-family group, alternating for visual separation
groups, start = [], 0
for i in range(1, len(CONDITIONS) + 1):
    if i == len(CONDITIONS) or CONDITIONS[i][3] != CONDITIONS[start][3]:
        groups.append((start, i - 1, CONDITIONS[start][3]))
        start = i
for gi, (lo, hi, name) in enumerate(groups):
    if gi % 2 == 1:
        ax.axvspan(lo - 0.5, hi + 0.5, color="0.94", zorder=0)
    ax.text((lo + hi) / 2, 1.46, name, ha="center", va="top", fontsize=9, color="0.35")

for modality in ["camera", "lidar", "radar"]:
    ys, ns = [], []
    for effect, sev, _, _ in CONDITIONS:
        rows = agg.filter(
            (pl.col("modality") == modality) & (pl.col("effect") == effect)
            & (pl.col("severity").is_null() if sev is None else pl.col("severity") == sev)
        )
        ys.append(rows["map"][0] if rows.height else np.nan)
        ns.append(rows["n_total_sum"][0] if rows.height else 0)
    ys, ns = np.array(ys), np.array(ns)
    rb = ys / clean_map
    reliable = ns > N_FLOOR
    c, m = COLORS[modality], MARKERS[modality]
    sizes = 25 + 45 * np.sqrt(np.clip(ns, 0, None) / 2000)
    # break the line at corruption-family boundaries -- connecting e.g.
    # "partial loss high" to "complete loss" would imply a false ordinal
    # trend between unrelated corruption types (severity axis honesty)
    for lo, hi, _ in groups:
        ax.plot(x[lo:hi + 1], rb[lo:hi + 1], "-", color=c, linewidth=1.6, zorder=2)
    ax.scatter(x, rb, s=sizes, c=c, marker=m, zorder=3,
               edgecolors=np.where(reliable, c, "#c0392b").tolist(), linewidths=1.3)
    ax.annotate(modality, (x[-1] + 0.15, rb[-1]), color=c, fontsize=10,
                fontweight="bold", va="center")

ax.axhline(1.0, color="0.55", linestyle="--", linewidth=1, zorder=1)
ax.text(x[-1] + 0.9, 1.0, "original", color="0.45", fontsize=11, va="center")
ax.set_xlim(-0.6, len(CONDITIONS) + 1.4)
ax.set_ylim(0, 1.5)
ax.set_xticks(x)
ax.set_xticklabels([c[2] for c in CONDITIONS])
ax.set_ylabel(r"$R_b^c$ = corrupted mAP / original mAP  (1.0 = no change)")
ax.grid(True, axis="y", color="0.9", linewidth=0.6, zorder=0)
for spine in ("top", "right"):
    ax.spines[spine].set_visible(False)
ax.set_title(
    f"$R_b^c$ robustness retention by modality across every corruption "
    f"(original baseline mAP={clean_map:.2f}, N={clean_n})\n"
    f"marker size = sqrt(N); red outline = below N>{N_FLOOR} reliability floor",
    fontsize=10,
)
fig.tight_layout()
fig.savefig(OUT / "modality_map_trend_single.png", bbox_inches="tight")
fig.savefig(OUT / "modality_map_trend_single.svg", bbox_inches="tight")
plt.close(fig)
print("saved ->", OUT / "modality_map_trend_single.png", "and .svg")
