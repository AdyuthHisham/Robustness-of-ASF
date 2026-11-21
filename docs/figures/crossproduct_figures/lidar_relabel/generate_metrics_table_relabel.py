"""LiDAR-relabeled variant of generate_metrics_table.py -- see that file for
full column/metric documentation, this only documents the diff.

Diff from the original: reads summary_full_density_lidar_relabel.parquet
(lidar_gaussian_noise_medium/high dropped, _low relabeled to _high -- see
make_relabeled_data.py) instead of the live summary_full_density.parquet.
churn_all_conditions.json has no run for the relabeled data (it's the same
underlying _low run, just renamed), so its lidar_gaussian_noise_low entry is
relabeled the same way in memory, and its medium/high entries are dropped,
to keep net_retention/churn_rate consistent with the relabeled mAP row.

Run: uv run --project test-bed python docs/crossproduct_figures/lidar_relabel/generate_metrics_table_relabel.py
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import polars as pl

REPO_ROOT = Path("/home/adhish/Productivity/AMSCUP")
BASE = REPO_ROOT / "repos/K-Radar/outputs/robustness_reports/crossproduct_v2"
OUT = REPO_ROOT / "docs/crossproduct_figures/lidar_relabel"
OUT.mkdir(parents=True, exist_ok=True)

df = pl.read_parquet(BASE / "summary_full_density_lidar_relabel.parquet")

agg = df.group_by("condition").agg(
    pl.col("n_tp").sum(), pl.col("n_fp").sum(), pl.col("n_fn").sum(),
    pl.col("n_total").sum().alias("n_total_sum"),
    (pl.col("ap_restricted_range") * pl.col("num_gt")).sum().alias("_ap_w"),
    pl.col("num_gt").sum().alias("_gt_w"),
    (pl.col("mATE") * pl.col("n_tp")).sum().alias("_ate_w"),
    (pl.col("mASE") * pl.col("n_tp")).sum().alias("_ase_w"),
    (pl.col("mAOE") * pl.col("n_tp")).sum().alias("_aoe_w"),
)
agg = agg.with_columns(
    (pl.col("_ap_w") / pl.col("_gt_w")).alias("mAP"),
    (pl.col("n_tp") / (pl.col("n_tp") + pl.col("n_fp"))).alias("precision"),
    (pl.col("n_tp") / (pl.col("n_tp") + pl.col("n_fn"))).alias("recall"),
    (pl.col("_ate_w") / pl.col("n_tp")).alias("mATE"),
    (pl.col("_ase_w") / pl.col("n_tp")).alias("mASE"),
    (pl.col("_aoe_w") / pl.col("n_tp")).alias("mAOE"),
)
agg = agg.with_columns(
    (2 * pl.col("precision") * pl.col("recall") / (pl.col("precision") + pl.col("recall"))).alias("f1"),
)
clean_ap = agg.filter(pl.col("condition") == "original")["mAP"][0]
agg = agg.with_columns((pl.col("mAP") / clean_ap).alias("rb"))

churn = json.loads((BASE / "churn_all_conditions.json").read_text())
churn = [c for c in churn if c["corrupted_condition"] not in
         ("lidar_gaussian_noise_medium", "lidar_gaussian_noise_high")]
for c in churn:
    if c["corrupted_condition"] == "lidar_gaussian_noise_low":
        c["corrupted_condition"] = "lidar_gaussian_noise_high"
    c["churn_rate"] = (c["n_miss"] + c["n_recover"]) / c["total"]
churn_by_cond = {c["corrupted_condition"]: c for c in churn}

check_cond = "lidar_gaussian_noise_high"
raw = df.filter(pl.col("condition") == check_cond)
manual_map = (raw["ap_restricted_range"] * raw["num_gt"]).sum() / raw["num_gt"].sum()
row = agg.filter(pl.col("condition") == check_cond)
assert np.isclose(manual_map, row["mAP"][0]), (manual_map, row["mAP"][0])
print(f"verification OK: {check_cond} (relabeled from _low) mAP={row['mAP'][0]:.3f}")
print(f"original baseline mAP = {clean_ap:.3f}")

ROW_ORDER = ["original"]
for modality in ["camera", "lidar", "radar"]:
    if modality == "lidar":
        effects = [("gaussian_noise", ["high"]), ("loss_partial", ["low", "medium", "high"]),
                   ("loss_complete_zero", [None])]
    else:
        effects = [("gaussian_noise", ["low", "medium", "high"]), ("loss_partial", ["low", "medium", "high"]),
                   ("loss_complete_zero", [None])]
    for effect, sevs in effects:
        for sev in sevs:
            cond = f"{modality}_{effect}" + (f"_{sev}" if sev else "")
            ROW_ORDER.append(cond)

COLUMNS = [
    ("mAP", "mAP", "{:.2f}", True),
    ("rb", "$R_b^c$", "{:.3f}", True),
    ("mATE", "mATE (m)", "{:.3f}", False),
    ("mASE", "mASE", "{:.3f}", False),
    ("mAOE", "mAOE (rad)", "{:.3f}", False),
    ("f1", "F1", "{:.3f}", True),
    ("n_fp", "FP", "{:.0f}", False),
    ("n_fn", "FN", "{:.0f}", False),
    ("net_retention", "net retention", "{:.3f}", True),
    ("churn_rate", "churn rate", "{:.3f}", False),
]

data = {c[0]: [] for c in COLUMNS}
for cond in ROW_ORDER:
    row = agg.filter(pl.col("condition") == cond)
    for key, *_ in COLUMNS:
        if key in ("net_retention", "churn_rate"):
            data[key].append(churn_by_cond[cond][key] if cond in churn_by_cond else np.nan)
        else:
            data[key].append(row[key][0] if row.height and key in row.columns else np.nan)
        if key == "rb" and cond == "original":
            data[key][-1] = 1.0

n_rows, n_cols = len(ROW_ORDER), len(COLUMNS)
fig, ax = plt.subplots(figsize=(1.35 * n_cols + 2.5, 0.32 * n_rows + 1.5))
cmap_good = plt.matplotlib.colormaps["RdYlGn"]

for j, (key, label, fmt, higher_better) in enumerate(COLUMNS):
    vals = np.array(data[key], dtype=float)
    lo, hi = np.nanmin(vals), np.nanmax(vals)
    norm = (vals - lo) / (hi - lo) if hi > lo else np.full_like(vals, 0.5)
    if not higher_better:
        norm = 1 - norm
    for i in range(n_rows):
        color = cmap_good(norm[i]) if np.isfinite(norm[i]) else "#F3F4F6"
        ax.add_patch(plt.Rectangle((j, n_rows - 1 - i), 1, 1, facecolor=color, edgecolor="white", linewidth=1))
        if np.isfinite(vals[i]):
            ax.text(j + 0.5, n_rows - 1 - i + 0.5, fmt.format(vals[i]), ha="center", va="center", fontsize=7)

orig_i = ROW_ORDER.index("original")
ax.add_patch(plt.Rectangle((0, n_rows - 1 - orig_i), n_cols, 1, fill=False, edgecolor="black", linewidth=1.6))

ax.set_xlim(0, n_cols)
ax.set_ylim(0, n_rows)
ax.set_xticks(np.arange(n_cols) + 0.5)
ax.set_xticklabels([c[1] for c in COLUMNS], fontsize=8)
ax.xaxis.set_ticks_position("top")
ax.xaxis.set_label_position("top")
ax.set_yticks(np.arange(n_rows) + 0.5)
ax.set_yticklabels(list(reversed(ROW_ORDER)), fontsize=11)
for spine in ax.spines.values():
    spine.set_visible(False)
ax.tick_params(length=0)
fig.tight_layout()
fig.savefig(OUT / "metrics_table.png", bbox_inches="tight", dpi=160)
plt.close(fig)
print("saved ->", OUT / "metrics_table.png")
