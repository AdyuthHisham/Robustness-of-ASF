"""Multi-metric table, one row per corruption condition, styled like
mrr_heatmap_marginal.png (annotated imshow grid + colorbar-style legend)
but with each column its own metric instead of one RR value per cell.

Metrics follow the inventory in obsidianVault/Projects/K-Radar/
robustness-metrics-tables.md and obsidianVault/Knowledge/robustness-metric-
selection.md, but are RECOMPUTED here from summary_full_density.parquet (the
dataset behind every other figure in this directory) rather than reused from
that vault page's numbers -- those come from a different, now-stale Alvis
row_table_iou03.parquet run (frame-identifier bug, Alvis permanently
unavailable, see project memory) and mixing sources would be a silent-
transform violation. mFR is excluded per the 2026-09-01 decision (project
memory); mAVE/mAAE excluded (no velocity/attribute GT in K-Radar's schema,
per the vault note); churn/transition, RCE-per-class, and recall-by-density
are per-object/curve-shaped and not reproducible from this pooled parquet, so
they're left out rather than faked from the stale table.

Columns: mAP, Rb^c (retention), mATE, mASE, mAOE (TP-error, n_tp-weighted),
precision/recall/F1 (recomputed from pooled TP/FP/FN, not averaged), FP, FN,
net_retention and churn_rate (per-object GT transition rates -- stable /
corruption-induced-miss / corruption-induced-recovery, see
gt_transition_analysis.py). Churn WAS initially left out (see above) but is
computable after all: it needs outputs/all_preds.txt + all_gts.txt directly
(not summary_full_density.parquet), and those are dated the same day as this
session's parquet (2026-09-01) -- current data, not the vault page's stale
Alvis snapshot -- so it was run fresh (21 conditions, single invocation,
IoU=0.3 to match crossproduct_v2) and merged in from
crossproduct_v2/churn_all_conditions.json. net_retention can exceed 1.0 when
recoveries outnumber corruption-induced misses (see vault table's note on
this) -- that's real, not a bug. churn_rate = (n_miss+n_recover)/total, total
object movement regardless of direction; a condition can have high churn_rate
but net_retention near 1.0 if misses and recoveries cancel out.

Each column is colored by its own min-max rank across rows (direction-aware:
green=better) -- color is a relative-rank cue only, exact values are always
annotated in the cell, so color is never the sole encoding (Scientific
Validity Checklist).

Source: repos/K-Radar/outputs/robustness_reports/crossproduct_v2/summary_full_density.parquet
         repos/K-Radar/outputs/robustness_reports/crossproduct_v2/churn_all_conditions.json
Run: uv run --project test-bed/src/Modules/robust_testing/kradar python docs/crossproduct_figures/generate_metrics_table.py
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import polars as pl

REPO_ROOT = Path("/home/adhish/Productivity/AMSCUP")
BASE = REPO_ROOT / "repos/K-Radar/outputs/robustness_reports/crossproduct_v2"
OUT = REPO_ROOT / "docs/crossproduct_figures"
OUT.mkdir(parents=True, exist_ok=True)

df = pl.read_parquet(BASE / "summary_full_density.parquet")

# pooled per-condition aggregation (all strata + both cls combined)
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

# --- verify one row's mAP and precision against source parquet ------------
check_cond = "lidar_gaussian_noise_high"
raw = df.filter(pl.col("condition") == check_cond)
manual_map = (raw["ap_restricted_range"] * raw["num_gt"]).sum() / raw["num_gt"].sum()
manual_prec = raw["n_tp"].sum() / (raw["n_tp"].sum() + raw["n_fp"].sum())
row = agg.filter(pl.col("condition") == check_cond)
assert np.isclose(manual_map, row["mAP"][0]), (manual_map, row["mAP"][0])
assert np.isclose(manual_prec, row["precision"][0]), (manual_prec, row["precision"][0])
print(f"verification OK: {check_cond} mAP={row['mAP'][0]:.3f} precision={row['precision'][0]:.4f}")
print(f"original baseline mAP = {clean_ap:.3f}")

churn = json.loads((BASE / "churn_all_conditions.json").read_text())
churn_by_cond = {c["corrupted_condition"]: c for c in churn}
for c in churn:
    c["churn_rate"] = (c["n_miss"] + c["n_recover"]) / c["total"]
check_churn = churn_by_cond[check_cond]
assert check_churn["total"] == check_churn["n_stable"] + check_churn["n_miss"] + check_churn["n_recover"] + check_churn["n_fail"]
print(f"verification OK: {check_cond} net_retention={check_churn['net_retention']:.4f} "
      f"churn_rate={check_churn['churn_rate']:.4f}")

ROW_ORDER = ["original"]
for modality in ["camera", "lidar", "radar"]:
    for effect, sevs in [("gaussian_noise", ["low", "medium", "high"]),
                          ("loss_partial", ["low", "medium", "high"]),
                          ("loss_complete_zero", [None])]:
        for sev in sevs:
            cond = f"{modality}_{effect}" + (f"_{sev}" if sev else "")
            ROW_ORDER.append(cond)

COLUMNS = [  # (col_key, display_label, fmt, higher_is_better)
    ("mAP", "mAP", "{:.2f}", True),
    ("rb", "$R_b^c$", "{:.3f}", True),
    ("mATE", "mATE\n(m)", "{:.3f}", False),
    ("mASE", "mASE", "{:.3f}", False),
    ("mAOE", "mAOE\n(rad)", "{:.3f}", False),
    ("n_fp", "FP", "{:.0f}", False),
    ("n_fn", "FN", "{:.0f}", False),
]


def wrap_condition(cond: str) -> str:
    """'camera_gaussian_noise_low' -> 'camera gaussian\\nnoise low' (no
    underscores, wrapped onto two lines split near the midpoint)."""
    words = cond.replace("_", " ").split(" ")
    if len(words) < 2:
        return cond
    mid = 0
    half = sum(len(w) for w in words) / 2
    running = 0
    for k, w in enumerate(words):
        running += len(w)
        if running >= half:
            mid = k + 1
            break
    return " ".join(words[:mid]) + "\n" + " ".join(words[mid:])

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

BOLD_CONDITIONS = {
    "lidar_gaussian_noise_medium", "lidar_gaussian_noise_high",
    "lidar_loss_complete_zero", "radar_gaussian_noise_medium", "radar_gaussian_noise_high",
}


def render_table(rows: list[str], out_stem: str) -> None:
    """Render one table image for `rows` (a subset of ROW_ORDER), with its own
    column header -- so splitting ROW_ORDER into halves and calling this twice
    gives each half a header, not just the first."""
    n_rows, n_cols = len(rows), len(COLUMNS)
    LABEL_W = 2.6  # reserved x-width (data units) for the row-label column
    fig, ax = plt.subplots(figsize=(0.95 * n_cols + LABEL_W + 1.0, 0.46 * n_rows + 1.8))
    cmap_good = plt.matplotlib.colormaps["RdYlGn"]

    for j, (key, label, fmt, higher_better) in enumerate(COLUMNS):
        # rank color is computed across ALL rows (full ROW_ORDER), not just this
        # half, so a cell's color still means "relative rank within its column"
        # across the whole table, matching the figure caption.
        all_vals = np.array(data[key], dtype=float)
        lo, hi = np.nanmin(all_vals), np.nanmax(all_vals)
        idx = [ROW_ORDER.index(c) for c in rows]
        vals = all_vals[idx]
        norm = (vals - lo) / (hi - lo) if hi > lo else np.full_like(vals, 0.5)
        if not higher_better:
            norm = 1 - norm
        for i in range(n_rows):
            color = cmap_good(norm[i]) if np.isfinite(norm[i]) else "#F3F4F6"
            ax.add_patch(plt.Rectangle((j, n_rows - 1 - i), 1, 1, facecolor=color, edgecolor="white", linewidth=1))
            if np.isfinite(vals[i]):
                ax.text(j + 0.5, n_rows - 1 - i + 0.5, fmt.format(vals[i]), ha="center", va="center", fontsize=12)

    for i, cond in enumerate(rows):
        weight = "bold" if cond in BOLD_CONDITIONS else "normal"
        ax.text(-0.15, n_rows - 1 - i + 0.5, wrap_condition(cond), ha="right", va="center",
                 fontsize=14, fontweight=weight)
    for i in range(n_rows + 1):
        ax.plot([-LABEL_W, n_cols], [i, i], color="0.75", linewidth=0.8, zorder=0, clip_on=False)

    if "original" in rows:
        orig_i = rows.index("original")
        ax.add_patch(plt.Rectangle((0, n_rows - 1 - orig_i), n_cols, 1, fill=False, edgecolor="black", linewidth=1.6))

    ax.set_xlim(-LABEL_W, n_cols)
    ax.set_ylim(0, n_rows)
    ax.set_xticks(np.arange(n_cols) + 0.5)
    ax.set_xticklabels([c[1] for c in COLUMNS], fontsize=13)
    ax.xaxis.set_ticks_position("top")
    ax.xaxis.set_label_position("top")
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(length=0)
    # Figure-level title removed 2026-09-07 (thesis writing-bible convention:
    # captions carry this role, not in-figure titles) -- see docs/FINAL_CHECK_LOG.md T1-016.
    fig.tight_layout()
    fig.savefig(OUT / f"{out_stem}.png", bbox_inches="tight", dpi=160)
    fig.savefig(OUT / f"{out_stem}.svg", bbox_inches="tight")
    plt.close(fig)
    print("saved ->", OUT / f"{out_stem}.png", "and .svg")


mid = (len(ROW_ORDER) + 1) // 2
render_table(ROW_ORDER[:mid], "metrics_table_top")
render_table(ROW_ORDER[mid:], "metrics_table_bottom")
