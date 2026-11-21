"""LiDAR-relabeled variant of generate_weather_corruption_lines.py -- see
that file for full methodology documentation (R_b^c definition, N>=30 floor,
complete_zero bar-panel convention), this only documents the diff.

Diff from the original: reads full_denormalized_table_22cond_lidar_relabel.
parquet (lidar_gaussian_noise_medium/high dropped, _low relabeled to _high --
see make_relabeled_data.py) instead of the live 22cond parquet, and only
queries severity "high" for the lidar/gaussian_noise family (the other two
tiers no longer exist in the relabeled data, so querying them would just
silently return None/gap -- explicit is clearer than relying on that
fallback). Also emits, while it already has every cell's R_b^c and N in
hand, the worst-cell-per-axis-per-class data needed for the new
tab:max_drop_by_axis (worst_cell_by_axis.csv) -- no separate pass required.

Run: uv run --project test-bed python docs/crossproduct_figures/lidar_relabel/generate_corruption_lines_relabel.py
"""

import csv
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import polars as pl

REPO_ROOT = Path("/home/adhish/Productivity/AMSCUP")
sys.path.insert(0, str(REPO_ROOT / "repos/K-Radar/scripts/alvis"))
from ap_metrics import compute_ap, compute_ap_grouped  # noqa: E402

OUT = REPO_ROOT / "docs/crossproduct_figures/lidar_relabel"
OUT.mkdir(parents=True, exist_ok=True)
DATA = REPO_ROOT / "repos/K-Radar/outputs/robustness_reports/full_denormalized_table_22cond_lidar_relabel.parquet"

N_FLOOR = 30
FAMILIES = [
    ("camera", "gaussian_noise"), ("camera", "loss_partial"),
    ("lidar", "gaussian_noise"), ("lidar", "loss_partial"),
    ("radar", "gaussian_noise"), ("radar", "loss_partial"),
]
SEVERITIES = ["low", "medium", "high"]
# lidar_gaussian_noise only has the relabeled "high" tier now
SEVERITIES_FOR = {("lidar", "gaussian_noise"): ["high"]}
MODALITIES = ["camera", "lidar", "radar"]
COLORS = {"camera": "#1b7837", "lidar": "#2166ac", "radar": "#b2182b"}
LINESTYLES = {"gaussian_noise": "-", "loss_partial": "--"}
MARKERS = {"gaussian_noise": "o", "loss_partial": "s"}
# lidar_gaussian_noise is the effect this whole relabeled document is about
# (the relabeled/backed severity tier) -- give it a star marker so it stands
# out from the other five severity-laddered families sharing these axes.
MARKER_OVERRIDE = {("lidar", "gaussian_noise"): "*"}
MARKERSIZE_OVERRIDE = {("lidar", "gaussian_noise"): 16}
EFFECT_LABEL = {"gaussian_noise": "gaussian noise", "loss_partial": "partial loss"}
CLASS_LABEL = {"sed": "Sedan", "bus": "Bus/truck"}
BAR_WIDTH = 0.22
BAR_OFFSETS = {"camera": -BAR_WIDTH, "lidar": 0.0, "radar": BAR_WIDTH}

AXES = {
    "weather": ("weather", ["normal", "rain", "overcast", "sleet", "fog"],
                {"normal": "Normal", "rain": "Rain", "overcast": "Overcast", "sleet": "Sleet", "fog": "Fog"},
                "weather_corruption_lines"),
    "environment": ("environment",
                    ["urban", "highway", "university", "alleyway", "mountain", "parkinglots", "shoulder", "countryside"],
                    {"urban": "Urban", "highway": "Highway", "university": "University", "alleyway": "Alleyway",
                     "mountain": "Mountain", "parkinglots": "Parking lots", "shoulder": "Shoulder",
                     "countryside": "Countryside"},
                    "environment_corruption_lines"),
    "time_of_day": ("time_of_day", ["day", "night"], {"day": "Day", "night": "Night"},
                    "tod_corruption_lines"),
    "distance_bucket": ("distance_bucket", ["near_0_20", "mid_20_40", "far_40_60", "very_far_60_75"],
                        {"near_0_20": "0-20 m", "mid_20_40": "20-40 m", "far_40_60": "40-60 m",
                         "very_far_60_75": "60-75 m"},
                        "distance_corruption_lines"),
    "frame_density": ("frame_density", ["1", "2-3", "4+"],
                       {"1": "1 (sparsest)", "2-3": "2-3", "4+": "4+ (densest)"},
                       "density_corruption_lines"),
}

df = pl.read_parquet(DATA)
conditions_needed = (
    ["original"]
    + [f"{mod}_{eff}_{sev}" for mod, eff in FAMILIES for sev in SEVERITIES_FOR.get((mod, eff), SEVERITIES)]
    + [f"{mod}_loss_complete_zero" for mod in MODALITIES]
)
dff_all = df.filter(pl.col("condition").is_in(conditions_needed))


def ap_n(aps: pl.DataFrame, col: str, cond: str, cls: str, cat: str) -> tuple[float | None, int]:
    row = aps.filter((pl.col("condition") == cond) & (pl.col("cls") == cls) & (pl.col(col) == cat))
    if row.height == 0:
        return None, 0
    return row["ap"][0], row["num_gt"][0]


def compute_axis(col: str, categories: list[str]):
    aps = compute_ap_grouped(dff_all, group_by=["condition", "cls", col])
    results: dict[str, dict[str, dict[tuple[str, str], dict[str, float | None]]]] = {}
    complete_zero: dict[str, dict[str, dict[str, float | None]]] = {}
    ns: dict[str, dict[str, dict]] = {}  # cn for each plotted cell, keyed the same way as results/complete_zero
    for cls in ("sed", "bus"):
        results[cls], complete_zero[cls], ns[cls] = {}, {}, {}
        for cat in categories:
            bap, bn = ap_n(aps, col, "original", cls, cat)
            results[cls][cat], complete_zero[cls][cat], ns[cls][cat] = {}, {}, {}
            for mod, eff in FAMILIES:
                results[cls][cat][(mod, eff)] = {}
                ns[cls][cat][(mod, eff)] = {}
                for sev in SEVERITIES_FOR.get((mod, eff), SEVERITIES):
                    cond = f"{mod}_{eff}_{sev}"
                    if bap is None or bn < N_FLOOR:
                        results[cls][cat][(mod, eff)][sev] = None
                        ns[cls][cat][(mod, eff)][sev] = 0
                        continue
                    cap, cn = ap_n(aps, col, cond, cls, cat)
                    ok = cap is not None and cn >= N_FLOOR
                    results[cls][cat][(mod, eff)][sev] = (cap / bap) if ok else None
                    ns[cls][cat][(mod, eff)][sev] = cn if ok else 0
            for mod in MODALITIES:
                cond = f"{mod}_loss_complete_zero"
                if bap is None or bn < N_FLOOR:
                    complete_zero[cls][cat][mod] = None
                    continue
                cap, cn = ap_n(aps, col, cond, cls, cat)
                ok = cap is not None and cn >= N_FLOOR
                complete_zero[cls][cat][mod] = ((cap / bap), cn) if ok else None
    return results, complete_zero, ns


def make_figure(cls: str, categories: list[str], labels: dict[str, str],
                results, complete_zero, out_stem: str) -> None:
    n = len(categories)
    ncols = 3
    nrows = -(-(n + 1) // ncols)
    fig, axes = plt.subplots(nrows, ncols, figsize=(15, 5 * nrows), sharey=True, squeeze=False)
    axes_flat = axes.flatten()
    x = np.arange(len(SEVERITIES))

    for ax, cat in zip(axes_flat, categories):
        for mod, eff in FAMILIES:
            sevs = SEVERITIES_FOR.get((mod, eff), SEVERITIES)
            ys = [results[cls][cat][(mod, eff)].get(sev) for sev in sevs]
            xs = [SEVERITIES.index(sev) for sev in sevs]
            c, ls = COLORS[mod], LINESTYLES[eff]
            mk = MARKER_OVERRIDE.get((mod, eff), MARKERS[eff])
            msize = MARKERSIZE_OVERRIDE.get((mod, eff), 9 if len(xs) == 1 else 8)
            z = 3 if (mod, eff) in MARKER_OVERRIDE else 2
            if len(xs) == 1:
                ax.plot(xs, ys, mk, color=c, markersize=msize, zorder=z)
            else:
                ys_arr = np.array([np.nan if v is None else v for v in ys])
                ax.plot(xs, ys_arr, ls, color=c, marker=mk, linewidth=2.2, markersize=msize, zorder=z)
        ax.axhline(1.0, color="0.6", linestyle=":", linewidth=1, zorder=1)
        ax.set_xticks(x)
        ax.set_xticklabels(SEVERITIES, fontsize=13)
        ax.tick_params(axis="y", labelsize=13)
        ax.set_title(labels[cat], fontsize=15)
        ax.set_ylim(-0.02, 1.15)
        ax.grid(True, axis="y", color="0.9", linewidth=0.6, zorder=0)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)

    bar_ax = axes_flat[n]
    wx = np.arange(n)
    for mod in MODALITIES:
        vals = [complete_zero[cls][cat][mod] for cat in categories]
        vals_arr = np.array([np.nan if v is None else v[0] for v in vals])
        bar_ax.bar(wx + BAR_OFFSETS[mod], vals_arr, width=BAR_WIDTH, color=COLORS[mod], zorder=2)
    bar_ax.axhline(1.0, color="0.6", linestyle=":", linewidth=1, zorder=1)
    bar_ax.set_xticks(wx)
    bar_ax.set_xticklabels([labels[cat] for cat in categories], fontsize=11, rotation=25, ha="right")
    bar_ax.tick_params(axis="y", labelsize=13)
    bar_ax.set_title("Complete loss (loss_complete_zero)", fontsize=14)
    bar_ax.set_ylim(-0.02, 1.15)
    bar_ax.grid(True, axis="y", color="0.9", linewidth=0.6, zorder=0)
    for spine in ("top", "right"):
        bar_ax.spines[spine].set_visible(False)

    for ax in axes_flat[n + 1:]:
        ax.axis("off")
    for ax in axes_flat[0::ncols]:
        ax.set_ylabel(r"$R_b^c$ (mAP robustness)", fontsize=13)

    line_handles = [
        plt.Line2D([0], [0], color=COLORS[mod], linestyle=LINESTYLES[eff],
                   marker=MARKER_OVERRIDE.get((mod, eff), MARKERS[eff]),
                   markersize=MARKERSIZE_OVERRIDE.get((mod, eff), 8), linewidth=2.2,
                   label=f"{mod} {EFFECT_LABEL[eff]}")
        for mod, eff in FAMILIES
    ]
    bar_handles = [
        plt.Rectangle((0, 0), 1, 1, color=COLORS[mod], label=f"{mod} complete loss")
        for mod in MODALITIES
    ]
    fig.legend(handles=line_handles + bar_handles, loc="lower center", ncol=5, fontsize=11,
               bbox_to_anchor=(0.5, -0.05 / nrows))
    fig.tight_layout(rect=(0, 0.03 / nrows, 1, 1.0))
    fig.savefig(OUT / f"{out_stem}.png", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print("saved ->", OUT / f"{out_stem}.png")


worst_rows = []  # axis, cls, rb, drop_pct, condition, stratum, n
for axis_key, (col, categories, labels, stem) in AXES.items():
    results, complete_zero, ns = compute_axis(col, categories)
    for cls, suffix in (("sed", "sedan"), ("bus", "bus")):
        make_figure(cls, categories, labels, results, complete_zero, f"{stem}_{suffix}")
        best = None  # (rb, cond, cat, n)
        for cat in categories:
            for mod, eff in FAMILIES:
                for sev in SEVERITIES_FOR.get((mod, eff), SEVERITIES):
                    rb = results[cls][cat][(mod, eff)].get(sev)
                    if rb is None:
                        continue
                    cn = ns[cls][cat][(mod, eff)][sev]
                    cond = f"{mod}_{eff}_{sev}"
                    if best is None or rb < best[0]:
                        best = (rb, cond, cat, cn)
            for mod in MODALITIES:
                cz = complete_zero[cls][cat][mod]
                if cz is None:
                    continue
                rb, cn = cz
                cond = f"{mod}_loss_complete_zero"
                if best is None or rb < best[0]:
                    best = (rb, cond, cat, cn)
        rb, cond, cat, cn = best
        worst_rows.append({
            "axis": axis_key, "cls": CLASS_LABEL[cls], "rb": round(rb, 3),
            "drop_pct": round((1 - rb) * 100, 1), "condition": cond,
            "stratum": labels[cat], "n": cn,
        })

with open(OUT / "worst_cell_by_axis.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["axis", "cls", "rb", "drop_pct", "condition", "stratum", "n"])
    writer.writeheader()
    writer.writerows(worst_rows)
print("saved ->", OUT / "worst_cell_by_axis.csv")
for row in worst_rows:
    print(row)
