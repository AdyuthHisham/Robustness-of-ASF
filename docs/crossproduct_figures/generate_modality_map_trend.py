"""mAP-by-modality trend: does camera/lidar/radar degrade differently across
corruption type x severity? One panel per effect (gaussian_noise, loss_partial,
loss_complete_zero), one line per modality, x=severity. Top row = absolute mAP
(cls-weighted mean of ap_restricted_range, aggregated over ALL strata -- global,
not per-stratum, per the user's "one plot, all corruptions" ask). Bottom row =
same ratio to that modality's own clean baseline, since camera/lidar/radar clean
mAP differs and "which modality fails more" is only a fair comparison normalized
(robustness-viz-advisor Core Principle 5).

Source: repos/K-Radar/outputs/robustness_reports/crossproduct_v2/summary_full_density.parquet
Run: uv run --project test-bed/src/Modules/robust_testing/kradar python docs/crossproduct_figures/generate_modality_map_trend.py
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
COLORS = {"camera": "#1b7837", "lidar": "#2166ac", "radar": "#b2182b"}  # colorblind-safe, distinct
MARKERS = {"camera": "o", "lidar": "s", "radar": "^"}  # redundant with color, not color-only
EFFECT_ORDER = ["gaussian_noise", "loss_partial", "loss_complete_zero"]
SEV_ORDER = {"gaussian_noise": ["low", "medium", "high"], "loss_partial": ["low", "medium", "high"],
             "loss_complete_zero": ["zero"]}
EFFECT_TITLE = {"gaussian_noise": "gaussian noise", "loss_partial": "partial loss", "loss_complete_zero": "complete loss"}

df = pl.read_parquet(BASE / "summary_full_density.parquet")
df = df.filter(pl.col("ap_restricted_range").is_not_null())

# global (all-strata) cls-weighted mAP per condition, and per modality clean baseline
clean = df.filter(pl.col("condition") == "original")
clean_map = (
    (clean["ap_restricted_range"] * clean["num_gt"]).sum() / clean["num_gt"].sum()
)
clean_n = int(clean["n_total"].sum())

corrupted = df.filter(pl.col("condition") != "original")
agg = corrupted.group_by(["modality", "effect", "severity"]).agg(
    ((pl.col("ap_restricted_range") * pl.col("num_gt")).sum() / pl.col("num_gt").sum()).alias("map"),
    pl.col("n_total").sum().alias("n_total_sum"),
)

# --- verify one point against source parquet -------------------------------
check = agg.row(0, named=True)
sev_filter = pl.col("severity").is_null() if check["severity"] is None else pl.col("severity") == check["severity"]
manual = corrupted.filter(
    (pl.col("modality") == check["modality"]) & (pl.col("effect") == check["effect"]) & sev_filter
)
manual_map = (manual["ap_restricted_range"] * manual["num_gt"]).sum() / manual["num_gt"].sum()
assert np.isclose(manual_map, check["map"]), (manual_map, check["map"])
print(f"verification OK: {check['modality']}/{check['effect']}/{check['severity']} mAP={check['map']:.3f}")
print(f"clean baseline mAP (all modalities pooled) = {clean_map:.3f} (N={clean_n})")

fig, axes = plt.subplots(2, 3, figsize=(13, 7), sharex="col")

for col, effect in enumerate(EFFECT_ORDER):
    sev_labels = SEV_ORDER[effect]
    x = np.arange(len(sev_labels))
    ax_abs, ax_norm = axes[0, col], axes[1, col]
    for modality in ["camera", "lidar", "radar"]:
        ys, ns = [], []
        for sev in sev_labels:
            rows = agg.filter(
                (pl.col("modality") == modality) & (pl.col("effect") == effect)
                & (pl.col("severity").fill_null("zero") == sev)
            )
            ys.append(rows["map"][0] if rows.height else np.nan)
            ns.append(rows["n_total_sum"][0] if rows.height else 0)
        ys = np.array(ys)
        sizes = 15 + 35 * np.sqrt(np.clip(ns, 0, None) / 2000)
        reliable = np.array(ns) > N_FLOOR
        c, m = COLORS[modality], MARKERS[modality]
        ax_abs.plot(x, ys, "-", color=c, linewidth=1.3, zorder=2)
        ax_abs.scatter(x, ys, s=sizes, c=c, marker=m, label=modality, zorder=3,
                        edgecolors=np.where(reliable, c, "#c0392b").tolist(), linewidths=1.2)
        ax_norm.plot(x, ys / clean_map, "-", color=c, linewidth=1.3, zorder=2)
        ax_norm.scatter(x, ys / clean_map, s=sizes, c=c, marker=m, zorder=3,
                         edgecolors=np.where(reliable, c, "#c0392b").tolist(), linewidths=1.2)

    ax_abs.axhline(clean_map, color="0.5", linestyle="--", linewidth=1, zorder=1)
    ax_norm.axhline(1.0, color="0.5", linestyle="--", linewidth=1, zorder=1)
    ax_abs.set_title(EFFECT_TITLE[effect])
    ax_abs.set_xticks(x)
    ax_norm.set_xticks(x)
    ax_norm.set_xticklabels(sev_labels)
    ax_abs.set_ylim(0, max(clean_map, np.nanmax(agg["map"])) * 1.15)
    ax_norm.set_ylim(0, 1.5)
    ax_abs.grid(True, axis="y", color="0.92", linewidth=0.6)
    ax_norm.grid(True, axis="y", color="0.92", linewidth=0.6)

axes[0, 0].set_ylabel("mAP (ap_restricted_range,\ncls-weighted, all strata pooled)")
axes[1, 0].set_ylabel("mAP / clean mAP\n(ratio, 1.0 = no change)")
axes[0, 2].legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), fontsize=8, title="modality", title_fontsize=8)
fig.suptitle(
    "mAP by modality across all corruption type x severity (global, N-pooled across strata)\n"
    f"dashed line = clean baseline (mAP={clean_map:.3f}); marker size = sqrt(N); "
    f"red outline = below N>{N_FLOOR} reliability floor",
    fontsize=10,
)
fig.tight_layout(rect=(0, 0, 1, 0.93))
fig.savefig(OUT / "modality_map_trend.png", bbox_inches="tight")
fig.savefig(OUT / "modality_map_trend.svg", bbox_inches="tight")
plt.close(fig)
print("saved ->", OUT / "modality_map_trend.png", "and .svg")
