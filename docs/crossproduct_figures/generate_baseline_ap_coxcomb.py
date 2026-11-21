"""Coxcomb (Nightingale rose) charts replacing Tables 5.2-5.6 in Results.tex:
a polar bar chart with one equal-angle wedge per diversity-axis category,
wedge radius = baseline AP (IoU 0.3) -- a pie chart where arc length is fixed
and radius carries the value instead, i.e. radar chart wedges rather than
radar chart spokes. Wedges are drawn edge-to-edge (no angular gap) so the
full set sums to 360 degrees, like a pie chart. Only AP is kept (FP/FN
dropped, per instruction).

Source values are the same regenerated baseline AP numbers already in
Tables 5.2-5.6 (from repos/K-Radar/outputs/robustness_reports baseline
evaluation) -- hardcoded here rather than recomputed, since they are the
thesis's own already-verified, already-cited numbers this figure replaces.

Run: uv run --project test-bed python docs/crossproduct_figures/generate_baseline_ap_coxcomb.py
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from palette import CATEGORY_PALETTE  # noqa: E402

OUT = Path("/home/adhish/Productivity/AMSCUP/docs/crossproduct_figures")

# axis -> (out_stem, categories, {cls: {cat: (ap, n) or None if N_gt=0}})
AXES = {
    "weather": ("baseline_ap_coxcomb_weather",
                ["Normal", "Rain", "Overcast", "Sleet", "Fog", "LightSnow", "HeavySnow"],
                {"sed": {"Normal": (76.93, 15988), "Rain": (69.13, 5978), "Overcast": (89.40, 1107),
                         "Sleet": (76.10, 1622), "Fog": (94.91, 1947),
                         "LightSnow": (90.78, 1360), "HeavySnow": (66.20, 1611)},
                 "bus": {"Normal": (57.43, 2763), "Rain": (7.89, 120), "Overcast": (81.67, 151),
                         "Sleet": (63.18, 1132), "Fog": None,
                         "LightSnow": (94.46, 540), "HeavySnow": (87.53, 1137)}}),
    "time_of_day": ("baseline_ap_coxcomb_tod",
                     ["Day", "Night"],
                     {"sed": {"Day": (79.85, 19961), "Night": (73.91, 9652)},
                      "bus": {"Day": (60.29, 3603), "Night": (75.93, 2240)}}),
    "environment": ("baseline_ap_coxcomb_environment",
                     ["Urban", "Highway", "University", "Alleyway", "Mountain", "Parking lots",
                      "Shoulder", "Countryside"],
                     {"sed": {"Urban": (81.16, 12032), "Highway": (84.34, 8175), "University": (75.07, 2599),
                              "Alleyway": (42.32, 3844), "Mountain": (92.32, 1086), "Parking lots": (69.34, 653),
                              "Shoulder": (99.88, 861), "Countryside": (68.05, 363)},
                      "bus": {"Urban": (88.54, 748), "Highway": (68.44, 3774), "University": (0.00, 25),
                              "Alleyway": (22.69, 164), "Mountain": (62.82, 598), "Parking lots": (69.78, 361),
                              "Shoulder": None, "Countryside": (36.04, 173)}}),
    "distance": ("baseline_ap_coxcomb_distance",
                 ["0-20 m", "20-40 m", "40-60 m", "60-75 m"],
                 {"sed": {"0-20 m": (76.02, 8695), "20-40 m": (76.23, 9204), "40-60 m": (80.23, 8163),
                          "60-75 m": (73.97, 3551)},
                  "bus": {"0-20 m": (67.71, 1678), "20-40 m": (77.10, 2531), "40-60 m": (56.82, 1093),
                          "60-75 m": (50.88, 541)}}),
    "frame_density": ("baseline_ap_coxcomb_density",
                       ["1 (sparsest)", "2-3", "4+ (densest)"],
                       {"sed": {"1 (sparsest)": (87.81, 3710), "2-3": (83.69, 9318), "4+ (densest)": (70.25, 16585)},
                        "bus": {"1 (sparsest)": (74.29, 2063), "2-3": (77.49, 1731), "4+ (densest)": (51.56, 2049)}}),
}


def make_figure(out_stem: str, categories: list[str], data: dict) -> None:
    # one color per category (shared across both class subplots) instead of
    # per-wedge text labels -- a legend on the right maps color to category.
    # Drawn from the document's shared CATEGORY_PALETTE (not matplotlib's
    # default tab10/tab20 cycle) so every figure in the thesis draws from the
    # same color family.
    if len(categories) > len(CATEGORY_PALETTE):
        raise ValueError(
            f"{len(categories)} categories requested but CATEGORY_PALETTE only has "
            f"{len(CATEGORY_PALETTE)} colors; extend palette.py's CATEGORY_PALETTE."
        )
    cat_color = {cat: CATEGORY_PALETTE[i] for i, cat in enumerate(categories)}

    fig, axes = plt.subplots(1, 2, figsize=(13, 7), subplot_kw={"projection": "polar"})
    for ax, cls in zip(axes, ("sed", "bus")):
        # wedge angular width is proportional to that category's N_gt (so the full
        # set of wedges sums to 360 deg, weighted by ground-truth support), radius
        # is the AP value -- angle carries N, radius carries AP
        total_n = sum(data[cls][cat][1] for cat in categories if data[cls][cat] is not None)
        n_na = sum(1 for cat in categories if data[cls][cat] is None)
        na_width = 2 * np.pi * 0.03
        # reserve the N/A slivers first, then scale the real wedges to fill the
        # remaining angle so the full set (real wedges + slivers) sums to exactly 360 deg
        real_span = 2 * np.pi - n_na * na_width
        angle = 0.0
        for cat in categories:
            cell = data[cls][cat]
            if cell is None:
                # N_gt=0: give it a nominal sliver, no bar drawn
                width = na_width
                ax.text(angle + width / 2, 55, "N/A", ha="center", va="center", fontsize=17, color="0.4")
                angle += width
                continue
            ap, ngt = cell
            width = real_span * ngt / total_n
            # edge-to-edge (no angular gap) so wedges touch and sum to 360 deg,
            # like a pie chart -- edgecolor keeps wedges visually distinguishable
            ax.bar(angle, ap, width=width, align="edge", color=cat_color[cat], alpha=0.6,
                   edgecolor="white", linewidth=1.5, zorder=2)
            ax.text(angle + width / 2, ap + 8, f"{ap:.1f}", ha="center", va="center", fontsize=17,
                    fontweight="bold", color="0.15")
            angle += width

        ax.set_xticks([])
        ax.set_ylim(0, 100)
        ax.set_yticks([0, 25, 50, 75, 100])
        ax.set_yticklabels(["0", "25", "50", "75", "100"], fontsize=13)
        # radial-axis quantity label (bible Sec. 7: axes must be labelled with
        # units) -- placed just beyond the outermost tick, at the same angle
        # matplotlib already draws the tick labels at (the default r-label
        # position, 0 degrees)
        rlabel_angle = np.radians(ax.get_rlabel_position())
        ax.text(rlabel_angle, 134, "AP (%)", fontsize=13, ha="center", va="center", color="0.25")

    legend_handles = [plt.Rectangle((0, 0), 1, 1, facecolor=cat_color[cat], alpha=0.6, label=cat)
                       for cat in categories]
    legend = fig.legend(handles=legend_handles, loc="center left", bbox_to_anchor=(1.0, 0.5), fontsize=16,
                         frameon=False, title="Category")
    legend.get_title().set_fontsize(16)
    fig.tight_layout()
    fig.savefig(OUT / f"{out_stem}.png", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print("saved ->", OUT / f"{out_stem}.png")


for axis_key, (out_stem, categories, data) in AXES.items():
    make_figure(out_stem, categories, data)
