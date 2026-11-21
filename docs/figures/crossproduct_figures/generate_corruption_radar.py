"""Radar-chart variant of generate_weather_corruption_lines.py: same R_b^c
computation and N>=30 floor, but each diversity-axis stratum (e.g. each
weather category) becomes one polar/radar polygon with one spoke per
individual severity-specific condition, instead of one line-plot panel with
severity on a shared x-axis plus a separate loss_complete_zero bar panel.

21 spokes total (all conditions in this thesis's severity-laddered
corruption sweep, unrelabeled data):
    camera_gaussian_noise:  low, medium, high        (3)
    camera_loss_partial:    low, medium, high        (3)
    camera_loss_complete_zero                        (1)
    lidar_gaussian_noise:   low, medium, high         (3)
    lidar_loss_partial:     low, medium, high         (3)
    lidar_loss_complete_zero                          (1)
    radar_gaussian_noise:   low, medium, high         (3)
    radar_loss_partial:     low, medium, high         (3)
    radar_loss_complete_zero                          (1)
                                                 total 21

Run: uv run --project test-bed python docs/crossproduct_figures/generate_corruption_radar.py
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import polars as pl

REPO_ROOT = Path("/home/adhish/Productivity/AMSCUP")
sys.path.insert(0, str(REPO_ROOT / "repos/K-Radar/scripts/alvis"))
from ap_metrics import compute_ap_grouped  # noqa: E402

OUT = REPO_ROOT / "docs/crossproduct_figures"
DATA = REPO_ROOT / "repos/K-Radar/outputs/robustness_reports/full_denormalized_table_22cond_weather_corrected.parquet"

sys.path.insert(0, str(Path(__file__).parent))
from palette import MODALITY_COLORS as COLORS  # noqa: E402
from palette import RANK_COLORS  # noqa: E402

N_FLOOR = 30
CLASS_LABEL = {"sed": "Sedan", "bus": "Bus/truck"}

# the 21 spokes, in a fixed display order (grouped by modality, then effect)
SPOKES = [
    ("camera", "gaussian_noise", "low"), ("camera", "gaussian_noise", "medium"), ("camera", "gaussian_noise", "high"),
    ("camera", "loss_partial", "low"), ("camera", "loss_partial", "medium"), ("camera", "loss_partial", "high"),
    ("camera", "loss_complete_zero", None),
    ("lidar", "gaussian_noise", "low"), ("lidar", "gaussian_noise", "medium"), ("lidar", "gaussian_noise", "high"),
    ("lidar", "loss_partial", "low"), ("lidar", "loss_partial", "medium"), ("lidar", "loss_partial", "high"),
    ("lidar", "loss_complete_zero", None),
    ("radar", "gaussian_noise", "low"), ("radar", "gaussian_noise", "medium"), ("radar", "gaussian_noise", "high"),
    ("radar", "loss_partial", "low"), ("radar", "loss_partial", "medium"), ("radar", "loss_partial", "high"),
    ("radar", "loss_complete_zero", None),
]
assert len(SPOKES) == 21

# two-letter spoke codes encode effect+severity only -- modality is already
# carried by the spoke's color (camera/LiDAR/radar), so the same 7 codes
# recur once per modality, just in a different color. Key given in Results.tex.
_EFFECT_SEV_CODE = {
    ("gaussian_noise", "low"): "GL", ("gaussian_noise", "medium"): "GM", ("gaussian_noise", "high"): "GH",
    ("loss_partial", "low"): "LL", ("loss_partial", "medium"): "LM", ("loss_partial", "high"): "LH",
    ("loss_complete_zero", None): "LC",
}


def spoke_label(mod: str, eff: str, sev: str | None) -> str:
    return _EFFECT_SEV_CODE[(eff, sev)]


def spoke_condition(mod: str, eff: str, sev: str | None) -> str:
    return f"{mod}_{eff}" + (f"_{sev}" if sev else "")


AXES = {
    "weather": ("weather", ["normal", "rain", "overcast", "sleet", "fog", "light_snow", "heavy_snow"],
                {"normal": "Normal", "rain": "Rain", "overcast": "Overcast", "sleet": "Sleet", "fog": "Fog",
                 "light_snow": "LightSnow", "heavy_snow": "HeavySnow"},
                "weather_corruption_radar"),
    "environment": ("environment",
                    ["urban", "highway", "university", "alleyway", "mountain", "parkinglots", "shoulder", "countryside"],
                    {"urban": "Urban", "highway": "Highway", "university": "University", "alleyway": "Alleyway",
                     "mountain": "Mountain", "parkinglots": "Parking lots", "shoulder": "Shoulder",
                     "countryside": "Countryside"},
                    "environment_corruption_radar"),
    "time_of_day": ("time_of_day", ["day", "night"], {"day": "Day", "night": "Night"},
                    "tod_corruption_radar"),
    "distance_bucket": ("distance_bucket", ["near_0_20", "mid_20_40", "far_40_60", "very_far_60_75"],
                        {"near_0_20": "0-20 m", "mid_20_40": "20-40 m", "far_40_60": "40-60 m",
                         "very_far_60_75": "60-75 m"},
                        "distance_corruption_radar"),
    "frame_density": ("frame_density", ["1", "2-3", "4+"],
                       {"1": "1 (sparsest)", "2-3": "2-3", "4+": "4+ (densest)"},
                       "density_corruption_radar"),
}

df = pl.read_parquet(DATA)
conditions_needed = ["original"] + [spoke_condition(*s) for s in SPOKES]
dff_all = df.filter(pl.col("condition").is_in(conditions_needed))


def ap_n(aps: pl.DataFrame, col: str, cond: str, cls: str, cat: str) -> tuple[float | None, int]:
    row = aps.filter((pl.col("condition") == cond) & (pl.col("cls") == cls) & (pl.col(col) == cat))
    if row.height == 0:
        return None, 0
    return row["ap"][0], row["num_gt"][0]


def compute_axis(col: str, categories: list[str]):
    aps = compute_ap_grouped(dff_all, group_by=["condition", "cls", col])
    values: dict[str, dict[str, list[float]]] = {}
    for cls in ("sed", "bus"):
        values[cls] = {}
        for cat in categories:
            bap, bn = ap_n(aps, col, "original", cls, cat)
            row = []
            for mod, eff, sev in SPOKES:
                if bap is None or bn < N_FLOOR:
                    row.append(np.nan)
                    continue
                cap, cn = ap_n(aps, col, spoke_condition(mod, eff, sev), cls, cat)
                row.append((cap / bap) if (cap is not None and cn >= N_FLOOR) else np.nan)
            values[cls][cat] = row
    return values


# circle rank -> (color, linewidth, legend text). rank 0/1 = worst/second-worst
# robustness (lowest R_b^c retention)
CIRCLE_STYLES = [
    (RANK_COLORS["worst"], 2.6, "Worst robustness (lowest $R_b^c$)"),
    (RANK_COLORS["second_worst"], 2.2, "Second-worst robustness"),
]

# contiguous (start, end) spoke-index range per modality, in SPOKES order
MOD_RANGES: dict[str, tuple[int, int]] = {}
_start = 0
for _i in range(1, len(SPOKES) + 1):
    if _i == len(SPOKES) or SPOKES[_i][0] != SPOKES[_start][0]:
        MOD_RANGES[SPOKES[_start][0]] = (_start, _i - 1)
        _start = _i


# every generated image uses the same fixed number of COLUMNS (2) and the
# same per-panel size (12.5in each), so every radar panel ends up the same
# physical size once placed at \linewidth in the report regardless of how
# many rows a given image has -- but the number of ROWS is sized to the
# actual chunk (1 row for <=2 categories, 2 rows for 3-4) so a chunk with
# few categories doesn't carry a fully blank row. Axes with more than 4
# categories are split into multiple same-panel-size images (separate LaTeX
# figures) instead of one oversized image that has to be shrunk to fit the page.
CHUNK_SIZE = 4
NCOLS = 2


def _chunk(seq: list, size: int) -> list[list]:
    return [seq[i:i + size] for i in range(0, len(seq), size)]


def make_figure(cls: str, categories: list[str], labels: dict[str, str], values, out_stem: str) -> None:
    ncols = NCOLS
    nrows = -(-len(categories) // ncols)
    angles = np.linspace(0, 2 * np.pi, len(SPOKES), endpoint=False).tolist()
    angles += angles[:1]

    fig, axes = plt.subplots(nrows, ncols, figsize=(12.5 * ncols, 12.5 * nrows),
                              subplot_kw={"projection": "polar"}, squeeze=False)
    axes_flat = axes.flatten()
    n = len(categories)
    tick_colors = [COLORS[mod] for mod, _, _ in SPOKES]
    tick_labels = [spoke_label(*s) for s in SPOKES]

    for ax, cat in zip(axes_flat, categories):
        vals = values[cls][cat]
        vals_closed = vals + vals[:1]

        # per-modality mean-robustness arc: a pastel, near-transparent wedge from
        # the center out to that modality's average R_b^c, spanning its spokes only
        for mod, (start, end) in MOD_RANGES.items():
            mod_vals = [v for v in vals[start:end + 1] if np.isfinite(v)]
            if not mod_vals:
                continue
            mean_val = float(np.mean(mod_vals))
            theta = np.linspace(angles[start], angles[end], 30)
            ax.fill_between(theta, 0, mean_val, color=COLORS[mod], alpha=0.15, zorder=0.5)
            ax.plot(theta, [mean_val] * len(theta), color=COLORS[mod], linewidth=1.5, alpha=0.7, zorder=1.3)

        ax.plot(angles, vals_closed, color="#333333", linewidth=1.6, zorder=2)
        ax.fill(angles, vals_closed, color="#333333", alpha=0.12, zorder=1)

        finite_idx = [i for i, v in enumerate(vals) if np.isfinite(v)]
        ranked = sorted(finite_idx, key=lambda i: vals[i])
        # worst, second-worst -- skip if fewer than 2 finite spokes
        picks = [i for i in (ranked[0] if ranked else None,
                              ranked[1] if len(ranked) > 1 else None) if i is not None]
        circle_angles = np.linspace(0, 2 * np.pi, 200)
        for rank, i in enumerate(picks):
            color, lw, _ = CIRCLE_STYLES[rank]
            ax.plot(circle_angles, [vals[i]] * len(circle_angles), color=color,
                    linestyle="--", linewidth=lw, zorder=1.5)
            ax.plot(angles[i], vals[i], marker="o", markersize=8,
                    markerfacecolor="none", markeredgecolor=color, markeredgewidth=2.2, zorder=3)
        min_idx = picks[0] if picks else None

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(tick_labels, fontsize=30)
        for i, (tick, color) in enumerate(zip(ax.get_xticklabels(), tick_colors)):
            tick.set_color(color)
            if i == min_idx:
                tick.set_fontweight("bold")
        ax.set_ylim(0, 1.15)
        ax.set_yticks([0.0, 0.25, 0.5, 0.75, 1.0])
        ax.set_yticklabels(["0", ".25", ".5", ".75", "1"], fontsize=15)
        # radial-axis quantity label (bible Sec. 7: axes must be labelled with
        # units) -- placed just beyond the outermost tick, at the same angle
        # matplotlib already draws the tick labels at
        rlabel_angle = np.radians(ax.get_rlabel_position())
        ax.text(rlabel_angle, 1.30, "$R_b^c$", fontsize=17, ha="center", va="center", color="0.25")
        ax.set_title(labels[cat], fontsize=26, fontweight="bold", pad=38)

    for ax in axes_flat[n:]:
        ax.axis("off")

    legend_handles = [plt.Line2D([0], [0], color=c, linestyle="--", linewidth=lw, label=lbl)
                       for c, lw, lbl in CIRCLE_STYLES]
    legend_handles += [plt.Rectangle((0, 0), 1, 1, facecolor=COLORS[mod], alpha=0.3,
                                      edgecolor=COLORS[mod], label=f"{mod.capitalize()} mean $R_b^c$ (arc)")
                        for mod in MOD_RANGES]
    # legend sized for a fixed 2x2-panel canvas (same for every image this
    # script writes), so it reads clearly regardless of how many real
    # categories are in this particular chunk
    # legend margin is an absolute amount of vertical space (in inches), so it
    # must be expressed as a LARGER fraction of total figure height for a
    # shorter (fewer-row) figure, else it would crowd or overlap the panels
    fig.legend(handles=legend_handles, loc="lower center", ncol=3, fontsize=28,
               bbox_to_anchor=(0.5, -0.09 / nrows), markerscale=1.8, handlelength=3.0)

    # extra vertical breathing room between rows so titles/labels of one row
    # never crowd the row above/below it
    fig.tight_layout(rect=(0, 0.12 / nrows, 1, 1.0), h_pad=6.0)
    fig.savefig(OUT / f"{out_stem}.png", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print("saved ->", OUT / f"{out_stem}.png")


def make_figures_chunked(cls: str, categories: list[str], labels: dict[str, str], values, out_stem: str) -> list[str]:
    """Drop unmeasurable strata, split the rest into <=CHUNK_SIZE-category
    chunks (one fixed-size image per chunk), and return the list of output
    stems written (single-element if everything fit in one image)."""
    cats = [cat for cat in categories if any(np.isfinite(v) for v in values[cls][cat])]
    chunks = _chunk(cats, CHUNK_SIZE)
    stems = []
    for k, chunk_cats in enumerate(chunks):
        stem = out_stem if len(chunks) == 1 else f"{out_stem}_part{k + 1}"
        make_figure(cls, chunk_cats, labels, values, stem)
        stems.append(stem)
    return stems


for axis_key, (col, categories, labels, stem) in AXES.items():
    values = compute_axis(col, categories)
    for cls, suffix in (("sed", "sedan"), ("bus", "bus")):
        written = make_figures_chunked(cls, categories, labels, values, f"{stem}_{suffix}")
        if len(written) > 1:
            print(f"  -> {stem}_{suffix} split into {len(written)} images: {written}")
