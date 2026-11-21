"""CRI bar chart, one panel per class, x-axis = effect (the eight three-tier
effect families already reported in tab:cri_results: gaussian_noise and
loss_partial for camera/LiDAR/radar, plus lidar_frame_deletion and
radar_frame_deletion), bars colored by modality.

Values are the same already-verified CRI numbers in Results.tex's
tab:cri_results (computed via compute_robustness.py's compute_cri, RoHOI
Eq. 2, from complete_results.txt per-severity AP) -- this script only
visualizes them, it does not recompute CRI from a different source.

Run: uv run --project test-bed python docs/crossproduct_figures/generate_cri_bars.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

OUT = Path("/home/adhish/Productivity/AMSCUP/docs/crossproduct_figures")

COLORS = {"camera": "#1b7837", "lidar": "#2166ac", "radar": "#b2182b"}

EFFECTS = [
    ("camera", "gaussian_noise", "camera\ngaussian\nnoise"),
    ("camera", "loss_partial", "camera\npartial\nloss"),
    ("lidar", "gaussian_noise", "lidar\ngaussian\nnoise"),
    ("lidar", "loss_partial", "lidar\npartial\nloss"),
    ("lidar", "frame_deletion", "lidar\nframe\ndeletion"),
    ("radar", "gaussian_noise", "radar\ngaussian\nnoise"),
    ("radar", "loss_partial", "radar\npartial\nloss"),
    ("radar", "frame_deletion", "radar\nframe\ndeletion"),
]

CRI = {
    "sed": [0.915, 0.936, 0.106, 0.546, 0.203, 0.272, 0.399, 0.203],
    "bus": [0.842, 0.929, 0.153, 0.383, 0.214, 0.272, 0.348, 0.215],
}
CLASS_LABEL = {"sed": "Sedan", "bus": "Bus/truck"}

x = np.arange(len(EFFECTS))
colors = [COLORS[mod] for mod, _, _ in EFFECTS]

for cls, out_stem in (("sed", "cri_bars_sedan"), ("bus", "cri_bars_bus")):
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(x, CRI[cls], color=colors, zorder=2)
    ax.set_xticks(x)
    ax.set_xticklabels([label for _, _, label in EFFECTS], fontsize=10)
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("CRI")
    ax.set_title(f"{CLASS_LABEL[cls]}: Corruption Robustness Index by effect")
    ax.grid(True, axis="y", color="0.9", linewidth=0.6, zorder=0)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for xi, v in zip(x, CRI[cls]):
        ax.text(xi, v + 0.015, f"{v:.3f}", ha="center", va="bottom", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / f"{out_stem}.png", bbox_inches="tight", dpi=200)
    fig.savefig(OUT / f"{out_stem}.svg", bbox_inches="tight")
    plt.close(fig)
    print("saved ->", OUT / f"{out_stem}.png")
