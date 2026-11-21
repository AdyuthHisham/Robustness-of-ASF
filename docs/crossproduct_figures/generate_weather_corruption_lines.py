"""mAP robustness (R_b^c) by diversity-axis category, one subplot per
category, one line per corruption family (camera/lidar/radar x
gaussian_noise/loss_partial), x-axis = severity (low/medium/high), plus a
separate bar-chart panel for loss_complete_zero (no severity ladder).
Generated as two SEPARATE figures per axis, one per class (sedan,
bus/truck) -- per-class R_b^c is not pooled/averaged across classes.

Covers all five diversity axes used in Chapter 4 (weather, environment,
time-of-day, distance, frame-density), replacing the five R_b^c tables in
that section with figures of this kind.

R_b^c per (class, axis category, family, severity) is the ratio of that
cell's AP to the same class/category's clean-baseline AP, with the same
N>30 reliability floor used throughout this chapter: a cell is always
plotted (never dropped or left as a gap) if the ratio is computable, but is
marked unreliable (hollow marker / red outline) if either the baseline or
the corrupted-condition object count for that class/category does not
clear the floor. A cell is only omitted outright when the ratio itself is
not computable (no rows for that condition/class/category at all).

`loss_complete_zero` (per modality) has no severity ladder -- it is a
single-tier condition, not low/medium/high -- so it does not belong on the
same axes as the severity lines. It is given its own bar-chart panel
(x-axis = axis category, grouped bars = modality) as part of the same
figure, rather than being appended into each line-plot panel.

Source: repos/K-Radar/outputs/robustness_reports/full_denormalized_table_22cond.parquet
Run: uv run --project test-bed python docs/crossproduct_figures/generate_weather_corruption_lines.py
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import polars as pl

REPO_ROOT = Path("/home/adhish/Productivity/AMSCUP")
sys.path.insert(0, str(REPO_ROOT / "repos/K-Radar/scripts/alvis"))
from ap_metrics import compute_ap, compute_ap_grouped  # noqa: E402

OUT = REPO_ROOT / "docs/crossproduct_figures"
DATA = REPO_ROOT / "repos/K-Radar/outputs/robustness_reports/full_denormalized_table_22cond.parquet"

N_FLOOR = 30
FAMILIES = [
    ("camera", "gaussian_noise"), ("camera", "loss_partial"),
    ("lidar", "gaussian_noise"), ("lidar", "loss_partial"),
    ("radar", "gaussian_noise"), ("radar", "loss_partial"),
]
SEVERITIES = ["low", "medium", "high"]
MODALITIES = ["camera", "lidar", "radar"]
COLORS = {"camera": "#1b7837", "lidar": "#2166ac", "radar": "#b2182b"}
LINESTYLES = {"gaussian_noise": "-", "loss_partial": "--"}
MARKERS = {"gaussian_noise": "o", "loss_partial": "s"}
EFFECT_LABEL = {"gaussian_noise": "gaussian noise", "loss_partial": "partial loss"}
CLASS_LABEL = {"sed": "Sedan", "bus": "Bus/truck"}
BAR_WIDTH = 0.22
BAR_OFFSETS = {"camera": -BAR_WIDTH, "lidar": 0.0, "radar": BAR_WIDTH}

# axis name -> (dataframe column, ordered categories, display labels, out-file stem)
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
    + [f"{mod}_{eff}_{sev}" for mod, eff in FAMILIES for sev in SEVERITIES]
    + [f"{mod}_loss_complete_zero" for mod in MODALITIES]
)
dff_all = df.filter(pl.col("condition").is_in(conditions_needed))


def ap_n(aps: pl.DataFrame, col: str, cond: str, cls: str, cat: str) -> tuple[float | None, int]:
    row = aps.filter((pl.col("condition") == cond) & (pl.col("cls") == cls) & (pl.col(col) == cat))
    if row.height == 0:
        return None, 0
    return row["ap"][0], row["num_gt"][0]


def compute_axis(col: str, categories: list[str]):
    """Returns (results, reliable, complete_zero, complete_zero_reliable, aps).
    `results`/`complete_zero` hold the R_b^c ratio whenever it is computable
    from existing rows (never nulled out just for being below the floor);
    the paired `reliable`/`complete_zero_reliable` dicts hold whether that
    cell's baseline AND corrupted-condition object counts both clear
    N_FLOOR, for the caller to render (hollow marker / red outline) rather
    than to suppress."""
    aps = compute_ap_grouped(dff_all, group_by=["condition", "cls", col])
    results: dict[str, dict[str, dict[tuple[str, str], dict[str, float | None]]]] = {}
    reliable: dict[str, dict[str, dict[tuple[str, str], dict[str, bool]]]] = {}
    complete_zero: dict[str, dict[str, dict[str, float | None]]] = {}
    complete_zero_reliable: dict[str, dict[str, dict[str, bool]]] = {}
    for cls in ("sed", "bus"):
        results[cls], reliable[cls] = {}, {}
        complete_zero[cls], complete_zero_reliable[cls] = {}, {}
        for cat in categories:
            bap, bn = ap_n(aps, col, "original", cls, cat)
            results[cls][cat], reliable[cls][cat] = {}, {}
            complete_zero[cls][cat], complete_zero_reliable[cls][cat] = {}, {}
            for mod, eff in FAMILIES:
                results[cls][cat][(mod, eff)] = {}
                reliable[cls][cat][(mod, eff)] = {}
                for sev in SEVERITIES:
                    cond = f"{mod}_{eff}_{sev}"
                    cap, cn = ap_n(aps, col, cond, cls, cat)
                    ratio = (cap / bap) if (bap is not None and cap is not None) else None
                    results[cls][cat][(mod, eff)][sev] = ratio
                    reliable[cls][cat][(mod, eff)][sev] = bool(bn > N_FLOOR and cn > N_FLOOR)
            for mod in MODALITIES:
                cond = f"{mod}_loss_complete_zero"
                cap, cn = ap_n(aps, col, cond, cls, cat)
                ratio = (cap / bap) if (bap is not None and cap is not None) else None
                complete_zero[cls][cat][mod] = ratio
                complete_zero_reliable[cls][cat][mod] = bool(bn > N_FLOOR and cn > N_FLOOR)
    return results, reliable, complete_zero, complete_zero_reliable, aps


# --- verify one cell (weather axis) against a direct, independent recomputation --
_results_w, _, _, _, _ = compute_axis("weather", AXES["weather"][1])
b = dff_all.filter((pl.col("condition") == "original") & (pl.col("cls") == "sed") & (pl.col("weather") == "normal"))
c = dff_all.filter(
    (pl.col("condition") == "lidar_gaussian_noise_high") & (pl.col("cls") == "sed") & (pl.col("weather") == "normal")
)
b_res, c_res = compute_ap(b), compute_ap(c)
manual = c_res["ap"] / b_res["ap"]
plotted = _results_w["sed"]["normal"][("lidar", "gaussian_noise")]["high"]
assert np.isclose(manual, plotted), (manual, plotted)
print(f"verification OK: sed/normal/lidar_gaussian_noise_high R_b^c={plotted:.3f}")


def make_figure(cls: str, axis_name: str, categories: list[str], labels: dict[str, str],
                results, reliable, complete_zero, complete_zero_reliable, out_stem: str) -> None:
    n = len(categories)
    ncols = 3
    nrows = -(-(n + 1) // ncols)  # ceil((n+1)/ncols)
    fig, axes = plt.subplots(nrows, ncols, figsize=(15, 5 * nrows), sharey=True, squeeze=False)
    axes_flat = axes.flatten()
    x = np.arange(len(SEVERITIES))

    for ax, cat in zip(axes_flat, categories):
        for mod, eff in FAMILIES:
            ys = [results[cls][cat][(mod, eff)][sev] for sev in SEVERITIES]
            rel = [reliable[cls][cat][(mod, eff)][sev] for sev in SEVERITIES]
            ys_arr = np.array([np.nan if v is None else v for v in ys])
            c, ls, mk = COLORS[mod], LINESTYLES[eff], MARKERS[eff]
            ax.plot(x, ys_arr, ls, color=c, linewidth=2.2, zorder=2)
            face = [c if r else "none" for r in rel]
            edge = [c if r else "red" for r in rel]
            ax.scatter(x, ys_arr, marker=mk, s=64, facecolors=face, edgecolors=edge,
                       linewidths=1.4, zorder=3)
        ax.axhline(1.0, color="0.6", linestyle=":", linewidth=1, zorder=1)
        ax.set_xticks(x)
        ax.set_xticklabels(SEVERITIES, fontsize=13)
        ax.tick_params(axis="y", labelsize=13)
        ax.set_title(labels[cat], fontsize=15)
        ax.set_ylim(-0.02, 1.15)
        ax.grid(True, axis="y", color="0.9", linewidth=0.6, zorder=0)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)

    # bar-chart panel for loss_complete_zero, immediately after the last category panel
    bar_ax = axes_flat[n]
    wx = np.arange(n)
    for mod in MODALITIES:
        vals = [complete_zero[cls][cat][mod] for cat in categories]
        rel = [complete_zero_reliable[cls][cat][mod] for cat in categories]
        vals_arr = np.array([np.nan if v is None else v for v in vals])
        hatch = ["///" if not r else None for r in rel]
        for xi, v, h in zip(wx + BAR_OFFSETS[mod], vals_arr, hatch):
            bar_ax.bar(xi, v, width=BAR_WIDTH, color=COLORS[mod], hatch=h,
                       edgecolor="red" if h else "none", linewidth=1.2 if h else 0, zorder=2)
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
        plt.Line2D([0], [0], color=COLORS[mod], linestyle=LINESTYLES[eff], marker=MARKERS[eff],
                   markersize=8, linewidth=2.2, label=f"{mod} {EFFECT_LABEL[eff]}")
        for mod, eff in FAMILIES
    ]
    bar_handles = [
        plt.Rectangle((0, 0), 1, 1, color=COLORS[mod], label=f"{mod} complete loss")
        for mod in MODALITIES
    ]
    fig.legend(handles=line_handles + bar_handles, loc="lower center", ncol=5, fontsize=11,
               bbox_to_anchor=(0.5, -0.05 / nrows))
    fig.text(0.5, -0.09 / nrows, f"Hollow marker / hatched bar with red outline = below N>{N_FLOOR} reliability floor",
              ha="center", fontsize=10, color="0.3")

    # Figure-level title removed 2026-09-07 (thesis writing-bible convention:
    # captions carry this role, not in-figure titles) -- see docs/FINAL_CHECK_LOG.md T1-016.
    fig.tight_layout(rect=(0, 0.03 / nrows, 1, 1.0))
    fig.savefig(OUT / f"{out_stem}.png", bbox_inches="tight", dpi=200)
    fig.savefig(OUT / f"{out_stem}.svg", bbox_inches="tight")
    plt.close(fig)
    print("saved ->", OUT / f"{out_stem}.png", "and .svg")


AXIS_TITLE = {
    "weather": "weather condition", "environment": "environment category",
    "time_of_day": "time of day", "distance_bucket": "distance band",
    "frame_density": "frame point-density bin",
}

for axis_key, (col, categories, labels, stem) in AXES.items():
    results, reliable, complete_zero, complete_zero_reliable, _ = compute_axis(col, categories)
    for cls, suffix in (("sed", "sedan"), ("bus", "bus")):
        make_figure(cls, AXIS_TITLE[axis_key], categories, labels, results, reliable,
                    complete_zero, complete_zero_reliable, f"{stem}_{suffix}")
