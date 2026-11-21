"""4 Results-section figures stratified by weather / environment / time_of_day /
distance-from-ego / frame-density, plus a TP/FP/FN table -- dimensions not present
in metrics_table.png (which is condition-only, pooled over all context).

Source: repos/K-Radar/outputs/robustness_reports/crossproduct_v2/summary_full_density.parquet
  (finest-grain table: condition x cls x weather x time_of_day x environment x
  distance_bucket x frame_density -- see [[exhaustive-crossproduct-phase2-progress]] for
  provenance; weather/environment/time_of_day/frame_density are 0%-null in this table,
  confirmed fixed 2026-08-31, current as of this session).

`frame_density` is a per-frame GT-object-density bucket (1 / 2-3 / 4+ objects in that frame,
see build_denormalized_table.py `_add_frame_density`). `distance_bucket` is a distance-from-ego
stratification (near_0_20 / mid_20_40 / far_40_60 / very_far_60_75, meters from ego, per GT
object). Item 2 is 4 separate single-dimension charts (environment, time_of_day, distance,
frame_density), each pooling over the other 3 context dims.

mAP = num_gt-weighted mean of ap_restricted_range (same definition as generate_metrics_table.py).
TP/FP/FN = summed counts. Reliability floor N=30 on total_pooled n_total, matching this
project's existing convention (generate_plots.py N_FLOOR, crossproduct/metrics.py reliability_tag).

Run: uv run --project test-bed/src/Modules/robust_testing/kradar python docs/crossproduct_figures/generate_results_context_figures.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import polars as pl

REPO_ROOT = Path("/home/adhish/Productivity/AMSCUP")
BASE = REPO_ROOT / "repos/K-Radar/outputs/robustness_reports/crossproduct_v2"
OUT = REPO_ROOT / "docs/crossproduct_figures"

N_FLOOR = 30
RELIABLE_ALPHA, UNRELIABLE_ALPHA = 1.0, 0.35
SEVERITY_X = {"baseline": 0, "low": 1, "medium": 2, "high": 3}
MODALITY_COLOR = {"camera": "#3B82F6", "lidar": "#F59E0B", "radar": "#10B981"}

plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 150, "font.size": 10,
    "axes.spines.top": False, "axes.spines.right": False,
})

df = pl.read_parquet(BASE / "summary_full_density.parquet")
df = df.with_columns(
    pl.when(pl.col("condition") == "original").then(pl.lit("baseline")).otherwise(pl.col("severity")).alias("severity")
)
# restrict to the severity-laddered effects (gaussian_noise/loss_partial) + baseline;
# loss_complete_zero has no low/med/high ladder so it doesn't belong on a severity x-axis
df_ladder = df.filter(pl.col("effect").is_in(["original", "gaussian_noise", "loss_partial"]))


def weighted_map(g: pl.DataFrame) -> pl.DataFrame:
    """num_gt-weighted mAP + pooled TP/FP/FN + pooled n_total, per group-by key already applied.

    `se` is a conservative (worst-case, p=0.5) proportion SE: se = sqrt(0.25/N) * 100,
    N = pooled num_gt (GT objects behind the estimate). Fixing p=0.5 (rather than the actual
    mAP) means the band is driven ONLY by sample size, not by how close the point estimate is
    to 0%/100% -- a true binomial SE shrinks near the extremes regardless of N, which would
    misleadingly show e.g. a high-mAP/low-N line as "more exact" than a mid-mAP/high-N line.
    Not a formal bootstrap AP CI (none exists in this pipeline); it's the standard
    estimator-precision proxy for "how exact is this mean given how much data went into it".
    """
    out = g.agg(
        (pl.col("ap_restricted_range") * pl.col("num_gt")).sum().alias("_apw"),
        pl.col("num_gt").sum().alias("_gtw"),
        pl.col("n_tp").sum().alias("n_tp"),
        pl.col("n_fp").sum().alias("n_fp"),
        pl.col("n_fn").sum().alias("n_fn"),
        pl.col("n_total").sum().alias("n_total"),
    ).with_columns(
        (pl.col("_apw") / pl.col("_gtw")).alias("mAP"),
        (pl.col("n_total") > N_FLOOR).alias("reliable"),
    )
    n = out["_gtw"]
    se = (100.0 * (0.25 / n).sqrt()).fill_nan(0.0).fill_null(0.0)
    return out.with_columns(se.alias("se"))


def _add_log_ticks(ax, axis="x"):
    """More than one labeled tick on a log axis -- default matplotlib often shows a single
    major tick (e.g. only 10^3) when the data spans less than a full decade, since power-of-10
    majors can fall outside the autoscaled range entirely. Labels ticks at 1x/2x/5x within (and
    across) each decade instead, so the histogram reads at a glance instead of needing the exact
    bar length compared by eye."""
    ax_axis = ax.xaxis if axis == "x" else ax.yaxis
    ax_axis.set_major_locator(plt.matplotlib.ticker.LogLocator(base=10, subs=(1, 2, 5)))
    fmt = plt.matplotlib.ticker.ScalarFormatter()
    fmt.set_scientific(False)
    ax_axis.set_major_formatter(fmt)
    ax_axis.set_minor_locator(plt.matplotlib.ticker.NullLocator())
    which_axis = "x" if axis == "x" else "y"
    ax.grid(True, which="major", axis=which_axis, color="0.88", linewidth=0.7, zorder=0)
    ax.tick_params(axis=which_axis, labelsize=7.5)
    if axis == "x":
        for label in ax.get_xticklabels():
            label.set_rotation(30)
            label.set_ha("right")


def make_class_split_fig(figsize=(11, 6.5)):
    """Shared layout: ONE histogram on the left spanning both rows, sedan line panel top-right,
    bus line panel bottom-right -- same structure as 8e_weather_rr_fan_merged.png, not the
    single-merged-panel style (one line per category, both classes pooled together) that earlier
    figures like 9a_context_map_environment.png used."""
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(2, 2, width_ratios=[1, 2.2], height_ratios=[1, 1], hspace=0.12, wspace=0.28)
    ax_hist = fig.add_subplot(gs[:, 0])
    ax_sed, ax_bus = fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, 1])
    return fig, ax_hist, ax_sed, ax_bus


def plot_lines_by_class(ax_sed, ax_bus, ax_hist, table, line_key, colors=None):
    """`table` must be weighted_map() grouped by [line_key, severity, cls] (cls = sed/bus).
    Draws one mean-mAP line per line_key value on each class panel (sedan top, bus bottom), and
    ONE shared histogram (pooled over cls, since N-per-condition doesn't depend on class) as
    horizontal grouped bars on a log x-axis. No uncertainty band -- N is shown in the histogram
    instead of implied through shading."""
    keys = table[line_key].unique().sort().to_list() if colors is None else list(colors.keys())
    class_specs = [(ax_sed, "sed", "sedan"), (ax_bus, "bus", "bus")]
    legend_handles = {}
    for ax, cls_code, cls_label in class_specs:
        for k in keys:
            g = table.filter((pl.col(line_key) == k) & (pl.col("cls") == cls_code)).with_columns(
                pl.col("severity").replace(SEVERITY_X).cast(pl.Int64).alias("_x")
            ).sort("_x")
            if g.height == 0:
                continue
            x, y, rel = g["_x"].to_list(), g["mAP"].to_list(), g["reliable"].to_list()
            color = colors[k] if colors else None
            line, = ax.plot(x, y, color=color, linewidth=1.5, zorder=2, label=k)
            if color is None:
                color = line.get_color()
            legend_handles.setdefault(k, line)
            for xi, yi, r in zip(x, y, rel):
                ax.scatter(xi, yi, color=color, s=40, alpha=RELIABLE_ALPHA if r else UNRELIABLE_ALPHA,
                           edgecolor="white", linewidth=0.5, zorder=3)
        ax.set_ylabel(f"{cls_label}\nmAP (%)", fontsize=9)
        ax.set_xticks([0, 1, 2, 3])
        ax.grid(True, axis="y", color="0.92", linewidth=0.7, zorder=0)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
    ax_sed.tick_params(labelbottom=False)
    ax_bus.set_xticklabels(["baseline", "low", "medium", "high"])
    ax_bus.set_xlabel("corruption severity")
    for ax in (ax_sed, ax_bus):
        ax.set_xlim(-0.3, 3.3)

    # single histogram, pooled over cls (N per condition doesn't depend on class)
    hist_table = table.group_by([line_key, "severity"], maintain_order=True).agg(pl.col("n_total").sum())
    n_keys = len(keys)
    bar_h = 0.8 / n_keys
    for i, k in enumerate(keys):
        g = hist_table.filter(pl.col(line_key) == k).with_columns(
            pl.col("severity").replace(SEVERITY_X).cast(pl.Int64).alias("_x")
        ).sort("_x")
        color = colors[k] if colors else legend_handles[k].get_color()
        by = [xi - 0.4 + bar_h * (i + 0.5) for xi in g["_x"].to_list()]
        ax_hist.barh(by, g["n_total"].to_list(), height=bar_h, color=color, alpha=0.85)
    ax_hist.set_xscale("log")
    ax_hist.set_yticks([0, 1, 2, 3])
    ax_hist.set_yticklabels(["baseline", "low", "medium", "high"])
    ax_hist.set_ylim(-0.5, 3.5)
    ax_hist.invert_yaxis()
    ax_hist.set_xlabel("N (TP+FP+FN, log scale)", fontsize=8)
    ax_hist.set_title("frames per condition\n(pooled sedan+bus)", fontsize=9)
    _add_log_ticks(ax_hist, axis="x")
    for spine in ("top", "right"):
        ax_hist.spines[spine].set_visible(False)
    return legend_handles


# ---------------------------------------------------------------------------
# Fig 1 -- weather-only: mAP vs severity, one line per weather condition
# ---------------------------------------------------------------------------
def fig1_weather():
    weathers = ["fog", "normal", "overcast", "rain", "sleet"]
    _rr_fan_chart("weather", weathers, "weather", "8_weather_map_by_severity")


# ---------------------------------------------------------------------------
# Fig 1b -- weather x severity mAP as an ANNOTATED HEATMAP, not a line plot. Two
# categorical factors (weather, severity) x one metric -> heatmap is the chart-
# grammar match (vs. a line plot, which forces the reader to disentangle 5 overlapping
# colored lines to do the same row/column comparison a grid shows directly). Reliability
# (N>=N_FLOOR) shown via a diagonal hatch overlay on unreliable cells instead of alpha,
# since alpha on a filled heatmap cell would also wash out the color-coded value itself.
# Sequential colormap (viridis), not diverging: mAP has no natural "100%" anchor to
# diverge around the way RR did.
# ---------------------------------------------------------------------------
def fig1b_weather_map_dotgrid():
    """Dot-matrix, not a filled heatmap: dot COLOR = mAP (RdYlGn), dot SIZE = sqrt(N). Size is a
    more directly intuitive certainty encoding than opacity (tried in a prior iteration) -- a
    small circle vs. a big circle needs no legend-reading to register as "less data went into
    this," whereas a faded color easily reads as "just a lighter shade of the same color." Ring
    (not fill) turns red for cells below N_FLOOR, on top of the continuous size encoding, same
    dual-signal idea as the reference dot-strip chart this was modeled on.
    """
    t = weighted_map(df_ladder.group_by(["weather", "severity"], maintain_order=True))

    weathers = ["fog", "normal", "overcast", "rain", "sleet"]  # sorted by baseline mAP desc, matches fig1 legend order
    sevs = ["baseline", "low", "medium", "high"]
    vals = np.full((len(weathers), len(sevs)), np.nan)
    reliable = np.ones_like(vals, dtype=bool)
    n_grid = np.zeros_like(vals)
    for i, w in enumerate(weathers):
        for j, s in enumerate(sevs):
            row = t.filter((pl.col("weather") == w) & (pl.col("severity") == s))
            if row.height:
                vals[i, j] = row["mAP"][0]
                reliable[i, j] = row["reliable"][0]
                n_grid[i, j] = row["n_total"][0]

    vmin, vmax = np.nanmin(vals), np.nanmax(vals)
    norm_val = plt.Normalize(vmin, vmax)
    cmap = plt.matplotlib.colormaps["RdYlGn"]
    # size legend anchors: sqrt scaling so area (not radius) is proportional to N, matching the
    # reference chart's "dot size = sqrt(effective N)" convention
    size_scale = 1800.0 / np.sqrt(n_grid.max())

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    xs, ys = np.meshgrid(range(len(sevs)), range(len(weathers)))
    sizes = np.sqrt(n_grid) * size_scale
    edge_colors = np.where(reliable, "0.3", "red")
    edge_widths = np.where(reliable, 0.8, 1.8)
    sc = ax.scatter(xs.ravel(), ys.ravel(), s=sizes.ravel(), c=vals.ravel(), cmap=cmap,
                     norm=norm_val, edgecolors=edge_colors.ravel(), linewidths=edge_widths.ravel(), zorder=3)
    for i in range(len(weathers)):
        for j in range(len(sevs)):
            if np.isnan(vals[i, j]):
                continue
            ax.annotate(f"{vals[i, j]:.1f}", (j, i), ha="center", va="center", fontsize=8, zorder=4)

    ax.set_xticks(range(len(sevs)), labels=sevs)
    ax.set_yticks(range(len(weathers)), labels=weathers)
    ax.set_xlim(-0.6, len(sevs) - 0.4)
    ax.set_ylim(len(weathers) - 0.4, -0.6)
    ax.set_xlabel("corruption severity")
    ax.grid(True, color="0.9", zorder=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.colorbar(sc, ax=ax, label="mAP (%, restricted range, num_gt-weighted)")

    # dot-size legend: reference N values -> matching circle sizes
    legend_ns = [max(30, int(n_grid.min())), int(np.median(n_grid)), int(n_grid.max())]
    handles = [plt.scatter([], [], s=np.sqrt(n) * size_scale, facecolor="0.6", edgecolor="0.3",
                            label=f"N={n:,}") for n in legend_ns]
    ax.legend(handles=handles, title="effective N\n(certainty)", loc="upper left",
              bbox_to_anchor=(1.32, 1.0), fontsize=7, title_fontsize=7, labelspacing=1.6, frameon=False)

    fig.text(0.02, -0.03, f"Red ring = pooled N≤{N_FLOOR} objects (below reliability floor).",
              fontsize=7, color="0.4")
    fig.tight_layout()
    fig.savefig(OUT / "8b_weather_map_dotgrid.png", bbox_inches="tight")
    fig.savefig(OUT / "8b_weather_map_dotgrid.svg", bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Fig 2 -- one chart per context dimension: environment, time_of_day,
# distance-from-ego, frame_density. Each pools over the other 3.
# ---------------------------------------------------------------------------
def fig2a_environment():
    envs = df_ladder["environment"].unique().sort().to_list()
    _rr_fan_chart("environment", envs, "environment", "9a_context_map_environment", figsize=(12.5, 7))


def fig2b_time_of_day():
    _rr_fan_chart("time_of_day", ["day", "night"], "time of day", "9b_context_map_time_of_day")


def fig2c_distance_from_ego():
    dist_order = ["near_0_20", "mid_20_40", "far_40_60", "very_far_60_75"]
    _rr_fan_chart("distance_bucket", dist_order, "distance from ego (m)", "9c_context_map_distance")


def fig2d_frame_density():
    dens_order = ["1", "2-3", "4+"]
    _rr_fan_chart("frame_density", dens_order, "frame density\n(GT objects/frame)", "9d_context_map_frame_density")


# ---------------------------------------------------------------------------
# Fig 3 -- TP/FP/FN table, all 22 conditions (baseline + 21 corrupted), plain table
# ---------------------------------------------------------------------------
def fig3_tpfpfn_table():
    agg = df.group_by("condition").agg(
        pl.col("n_tp").sum(), pl.col("n_fp").sum(), pl.col("n_fn").sum(),
        pl.col("modality").drop_nulls().first(), pl.col("effect").first(), pl.col("severity").first(),
    )
    row_order = ["original"]
    for modality in ["camera", "lidar", "radar"]:
        for effect, sevs in [("gaussian_noise", ["low", "medium", "high"]),
                              ("loss_partial", ["low", "medium", "high"]),
                              ("loss_complete_zero", [None])]:
            for sev in sevs:
                row_order.append(f"{modality}_{effect}" + (f"_{sev}" if sev else ""))

    # F1 recomputed from pooled TP/FP/FN (not averaged across strata), same convention as
    # generate_metrics_table.py -- the standard metric relating TP/FP/FN when there are no
    # true negatives to define accuracy/MCC against.
    rows = []
    for cond in row_order:
        r = agg.filter(pl.col("condition") == cond)
        tp, fp, fn = int(r["n_tp"][0]), int(r["n_fp"][0]), int(r["n_fn"][0])
        f1 = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else float("nan")
        rows.append([cond, f"{tp:,}", f"{fp:,}", f"{fn:,}", f"{f1:.3f}"])

    fig, ax = plt.subplots(figsize=(8.3, 0.28 * len(row_order) + 1))
    ax.axis("off")
    tbl = ax.table(cellText=rows, colLabels=["condition", "TP", "FP", "FN", "F1"],
                    loc="center", cellLoc="center", colLoc="center",
                    colWidths=[0.46, 0.15, 0.15, 0.15, 0.13])
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8)
    tbl.scale(1, 1.25)
    for j in range(5):
        tbl[0, j].set_text_props(weight="bold")
    orig_i = row_order.index("original") + 1  # +1 for header row
    for j in range(5):
        tbl[orig_i, j].set_facecolor("#EEF2FF")
    fig.tight_layout()
    fig.savefig(OUT / "10_tpfpfn_table.png", bbox_inches="tight", dpi=160)
    fig.savefig(OUT / "10_tpfpfn_table.svg", bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Fig 4 -- severity-level mAP by sensor/corruption family (camera/lidar/radar)
# ---------------------------------------------------------------------------
def fig4_severity_by_sensor():
    # baseline has modality=None; broadcast the single per-cls baseline mAP onto all 3 sensor lines
    base = weighted_map(df.filter(pl.col("condition") == "original").group_by(["cls"], maintain_order=True))
    base_by_cls = {r["cls"]: r for r in base.iter_rows(named=True)}

    t2 = weighted_map(
        df_ladder.filter(pl.col("modality").is_not_null()).group_by(["modality", "severity", "cls"], maintain_order=True)
    )
    modalities = list(MODALITY_COLOR)
    bar_h = 0.8 / len(modalities)
    fig, ax_hist, ax_sed, ax_bus = make_class_split_fig()
    class_specs = [(ax_sed, "sed", "sedan"), (ax_bus, "bus", "bus")]
    for ax, cls_code, cls_label in class_specs:
        base_map, base_n = base_by_cls[cls_code]["mAP"], base_by_cls[cls_code]["n_total"]
        for modality in modalities:
            color = MODALITY_COLOR[modality]
            g = t2.filter((pl.col("modality") == modality) & (pl.col("cls") == cls_code)).with_columns(
                pl.col("severity").replace(SEVERITY_X).cast(pl.Int64).alias("_x")
            ).sort("_x")
            x = [0] + g["_x"].to_list()
            y = [base_map] + g["mAP"].to_list()
            rel = [base_n > N_FLOOR] + g["reliable"].to_list()
            ax.plot(x, y, color=color, linewidth=1.5, zorder=2, label=modality)
            for xi, yi, r in zip(x, y, rel):
                ax.scatter(xi, yi, color=color, s=45, alpha=RELIABLE_ALPHA if r else UNRELIABLE_ALPHA,
                           edgecolor="white", linewidth=0.5, zorder=3)
        ax.set_ylabel(f"{cls_label}\nmAP (%)", fontsize=9)
        ax.set_xticks([0, 1, 2, 3])
        ax.set_xlim(-0.3, 3.3)
        ax.grid(True, axis="y", color="0.92", linewidth=0.7, zorder=0)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
    ax_sed.tick_params(labelbottom=False)
    ax_bus.set_xticklabels(["baseline", "low", "medium", "high"])
    ax_bus.set_xlabel("corruption severity")
    ax_sed.legend(title="sensor", fontsize=8)

    # single histogram, pooled over cls, baseline broadcast across modalities same as the lines
    base_n_total = base.group_by(pl.lit(1)).agg(pl.col("n_total").sum())["n_total"][0]
    hist_table = t2.group_by(["modality", "severity"], maintain_order=True).agg(pl.col("n_total").sum())
    for i, modality in enumerate(modalities):
        color = MODALITY_COLOR[modality]
        g = hist_table.filter(pl.col("modality") == modality).with_columns(
            pl.col("severity").replace(SEVERITY_X).cast(pl.Int64).alias("_x")
        ).sort("_x")
        by = [0 - 0.4 + bar_h * (i + 0.5)] + [xi - 0.4 + bar_h * (i + 0.5) for xi in g["_x"].to_list()]
        n_gt = [base_n_total] + g["n_total"].to_list()
        ax_hist.barh(by, n_gt, height=bar_h, color=color, alpha=0.85)
    ax_hist.set_xscale("log")
    ax_hist.set_yticks([0, 1, 2, 3])
    ax_hist.set_yticklabels(["baseline", "low", "medium", "high"])
    ax_hist.set_ylim(-0.5, 3.5)
    ax_hist.invert_yaxis()
    ax_hist.set_xlabel("N (TP+FP+FN, log scale)", fontsize=8)
    ax_hist.set_title("frames per condition\n(pooled sedan+bus)", fontsize=9)
    _add_log_ticks(ax_hist, axis="x")
    for spine in ("top", "right"):
        ax_hist.spines[spine].set_visible(False)
    fig.text(0.02, -0.03,
              f"Pooled over gaussian_noise + loss_partial per sensor (severity-laddered effects only); "
              f"loss_complete_zero excluded (no severity ladder). Faded marker = N≤{N_FLOOR}.",
              fontsize=7, color="0.4")
    fig.tight_layout()
    fig.savefig(OUT / "11_severity_map_by_sensor.png", bbox_inches="tight")
    fig.savefig(OUT / "11_severity_map_by_sensor.svg", bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Fig 1c -- weather x severity as SMALL MULTIPLES (one panel per weather
# condition), not a single overlaid-lines axis (fig1, rejected: "same plot")
# and not a heatmap/dot-matrix (fig1b, accepted direction but circle-size-for-N
# read as noisy and the shaded-band idea from an earlier line-plot attempt was
# liked but its meaning -- min/max of an 80th-percentile band -- wasn't clear).
# Here the band is the SE proxy `weighted_map` already computes: width driven
# ONLY by pooled N (see that function's docstring), stated plainly in the
# caption so there's no ambiguity about what it represents. One consistent
# accent color per panel (small multiples remove the need for a 5-way
# categorical or diverging color competition), sequential viridis reserved for
# marker fill only where it usefully encodes something continuous (unused
# here since there's nothing else to encode) -- dropped continuous size-for-N
# entirely; reliability instead flagged with a red ring only on points that
# actually breach N_FLOOR, same as fig1b's convention.
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Fig 1d -- "fan chart" (Wikipedia: Fan chart (statistics); origin: Bank of
# England inflation-report forecasts) -- central line + nested percentile
# bands, standard for showing how a distribution of realizations spreads
# around a central estimate. Distribution here = PER-FRAME detection quality
# within each (weather, severity) cell, one fan per class (sedan / bus) so
# they don't get pooled together.
#
# IMPORTANT metric-honesty note: this is NOT the pooled AP shown in fig1/1b/1c.
# True AP needs a score-ranked precision-recall sweep over many detections;
# a single frame has only 1-4 GT objects, so a per-frame "AP" isn't a
# well-posed quantity. What's plotted instead is the per-frame TP ratio,
# TP/(TP+FP+FN) -- the frame-level detection/match rate -- across all frames
# (and, since severity buckets pool every matching sensor condition, across
# all conditions in that bucket) landing in that (weather, severity, cls)
# cell. It answers "how much does detection quality vary frame-to-frame",
# which the pooled mAP number cannot show. Band = 10th-90th percentile
# (middle 80% of frames, i.e. outliers trimmed); thin whisker = true min/max.
# ---------------------------------------------------------------------------
def _per_frame_tp_ratio() -> pl.DataFrame:
    cond_map = df_ladder.select(["condition", "severity"]).unique()
    rows = pl.read_parquet(
        REPO_ROOT / "repos/K-Radar/outputs/robustness_reports/full_denormalized_table_22cond.parquet"
    ).join(cond_map, on="condition", how="inner")
    frame_tp = rows.group_by(["weather", "severity", "cls", "sequence", "frame", "condition"]).agg(
        pl.col("is_tp").sum().alias("tp"), pl.col("is_fp").sum().alias("fp"), pl.col("is_fn").sum().alias("fn"),
    )
    frame_tp = frame_tp.filter((pl.col("tp") + pl.col("fp") + pl.col("fn")) > 0).with_columns(
        (100.0 * pl.col("tp") / (pl.col("tp") + pl.col("fp") + pl.col("fn"))).alias("frame_score")
    )
    return frame_tp.group_by(["weather", "severity", "cls"], maintain_order=True).agg(
        pl.col("frame_score").mean().alias("mean"),
        pl.col("frame_score").quantile(0.1).alias("p10"),
        pl.col("frame_score").quantile(0.9).alias("p90"),
        pl.col("frame_score").min().alias("vmin"),
        pl.col("frame_score").max().alias("vmax"),
        pl.len().alias("n_frames"),
    )


def fig1d_weather_fan_by_class():
    bands = _per_frame_tp_ratio()
    weathers = ["fog", "normal", "overcast", "rain", "sleet"]
    sevs = ["baseline", "low", "medium", "high"]
    classes = [("sed", "sedan", "#2563eb"), ("bus", "bus", "#b45309")]

    fig, axes = plt.subplots(2, len(weathers), figsize=(14, 6.4), sharey=True, sharex=True)
    for row, (cls_code, cls_label, color) in enumerate(classes):
        for col, w in enumerate(weathers):
            ax = axes[row, col]
            g = bands.filter((pl.col("weather") == w) & (pl.col("cls") == cls_code)).with_columns(
                pl.col("severity").replace(SEVERITY_X).cast(pl.Int64).alias("_x")
            ).sort("_x")
            if g.height == 0:
                ax.set_axis_off()
                continue
            x = g["_x"].to_list()
            ax.fill_between(x, g["vmin"].to_list(), g["vmax"].to_list(), color=color, alpha=0.12, zorder=1)
            ax.fill_between(x, g["p10"].to_list(), g["p90"].to_list(), color=color, alpha=0.30, zorder=2)
            ax.plot(x, g["mean"].to_list(), color=color, linewidth=1.8, marker="o",
                    markersize=4, zorder=3)
            if row == 0:
                ax.set_title(w, fontsize=10)
            ax.set_xticks([0, 1, 2, 3])
            ax.set_xticklabels(sevs, rotation=30, ha="right", fontsize=7.5)
            ax.set_ylim(0, 100)
            ax.grid(True, axis="y", color="0.92", linewidth=0.7, zorder=0)
            for spine in ("top", "right"):
                ax.spines[spine].set_visible(False)
        axes[row, 0].set_ylabel(f"{cls_label}\nper-frame TP ratio (%)", fontsize=9)
    fig.text(0.02, -0.05,
              "Fan chart per class: line = mean per-frame TP/(TP+FP+FN); dark band = 10th-90th "
              "percentile of frames (outliers trimmed); pale band = true min/max. This is a "
              "per-frame match-rate proxy, NOT the pooled AP shown in the mAP-labeled figures -- "
              "true AP needs a score-ranked PR sweep that a single frame (1-4 GT objects) can't support.",
              fontsize=7.5, color="0.35", wrap=True)
    fig.tight_layout()
    fig.savefig(OUT / "8d_weather_fan_by_class.png", bbox_inches="tight")
    fig.savefig(OUT / "8d_weather_fan_by_class.svg", bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Fig 1e -- RR fan chart, one merged plot per class (not per-weather small
# multiples). Two changes from fig1d per explicit request:
#   1. Metric = RR delta = corrupted_AP / baseline_AP - 1 (0 = same as clean,
#      negative = worse), same definition as rr_dotstrip_marginal.png /
#      generate_rr_dotstrip_marginal.py -- NOT the per-frame TP-ratio proxy
#      fig1d used. AP itself = the real 41-point interpolated AP from
#      ap_metrics.compute_ap (verbatim port of K-Radar's own
#      utils/kitti_eval/eval_revised.py:eval_class, N_SAMPLE_PTS=41) computed
#      PER SEQUENCE, pooled across baseline's/RR's own matching condition set
#      only (not per-frame) -- a sequence has enough detections across its
#      frames for a real precision-recall sweep, unlike a single frame.
#   2. All 5 weather conditions merged onto ONE axis per class (not 5 panels)
#      -- band = 20th-80th percentile of per-sequence RR delta (narrower than
#      fig1d's 10th-90th, per explicit request), pale whisker = min/max.
# ---------------------------------------------------------------------------
def _per_sequence_rr_delta(group_col: str) -> pl.DataFrame:
    """RR delta (corrupted AP / baseline AP - 1) per sequence, generalized over any physical
    per-object/per-frame/per-sequence attribute (weather, environment, time_of_day,
    distance_bucket, frame_density -- NOT modality, which is null at baseline and needs the
    separate cls-only baseline-broadcast fig4 already does)."""
    from sys import path as _syspath
    _ap_metrics_dir = str(REPO_ROOT / "repos/K-Radar/scripts/alvis")
    if _ap_metrics_dir not in _syspath:
        _syspath.insert(0, _ap_metrics_dir)
    from ap_metrics import compute_ap_grouped  # noqa: E402

    cond_map = df.select(["condition", "effect", "severity"]).unique().with_columns(
        pl.when(pl.col("effect") == "original").then(pl.lit("baseline")).otherwise(pl.col("severity")).alias("severity")
    )
    rows = pl.read_parquet(
        REPO_ROOT / "repos/K-Radar/outputs/robustness_reports/full_denormalized_table_22cond.parquet"
    ).join(cond_map, on="condition", how="inner")
    rows = rows.filter(pl.col("effect").is_in(["original", "gaussian_noise", "loss_partial"]))

    ap_per_seq = compute_ap_grouped(rows, [group_col, "severity", "cls", "sequence"])
    baseline_ap = ap_per_seq.filter(pl.col("severity") == "baseline").select(
        [group_col, "cls", "sequence", "ap"]
    ).rename({"ap": "ap_base"})
    corrupted_ap = ap_per_seq.filter(pl.col("severity") != "baseline")
    joined = corrupted_ap.join(baseline_ap, on=[group_col, "cls", "sequence"], how="inner").filter(
        pl.col("ap_base") > 0
    )
    joined = joined.with_columns((pl.col("ap") / pl.col("ap_base") - 1).alias("rr_delta"))
    bands = joined.group_by([group_col, "severity", "cls"], maintain_order=True).agg(
        pl.col("rr_delta").mean().alias("mean"),
        pl.col("rr_delta").quantile(0.2).alias("p20"),
        pl.col("rr_delta").quantile(0.8).alias("p80"),
        pl.col("rr_delta").min().alias("vmin"),
        pl.col("rr_delta").max().alias("vmax"),
        pl.len().alias("n_seq"),
    )
    # True physical frame count per condition value at BASELINE ONLY -- NOT per (group_col,
    # severity): the same frame set gets re-evaluated under every corrupted condition, so
    # counting per severity would just multiply by however many sensor conditions happen to
    # share that severity label (6x for corrupted vs. 1x for baseline), which showed up as a
    # baseline/corruption mismatch that wasn't a real difference in available data (see prior
    # investigation). One flat count per group_col value, from baseline only, is correct.
    frame_counts = rows.filter(pl.col("severity") == "baseline").group_by([group_col], maintain_order=True).agg(
        pl.struct(["sequence", "frame"]).n_unique().alias("n_frames")
    )
    return bands, frame_counts


# Okabe-Ito colorblind-safe qualitative palette (first 5 kept in the original weather-chart
# order; extended to all 8 for dimensions with more categories, e.g. environment).
_CB_COLORS = ["#0072B2", "#E69F00", "#009E73", "#D55E00", "#CC79A7", "#56B4E9", "#F0E442", "#000000"]


def _rr_fan_chart(group_col: str, keys: list[str], legend_title: str, out_name: str,
                   colors: list[str] | None = None, figsize=(12, 6.5)):
    """RR-delta fan chart, class-split (sedan/bus), single baseline-only frame histogram --
    the canonical style (originally 8e_weather_rr_fan_merged.png). `keys` fixes the plotted
    order/inclusion of group_col's values; `colors` defaults to the Okabe-Ito qualitative
    palette, cycled if there are more keys than colors."""
    bands, frame_counts = _per_sequence_rr_delta(group_col)
    colors = colors or _CB_COLORS
    key_color = {k: colors[i % len(colors)] for i, k in enumerate(keys)}
    classes = [("sed", "sedan"), ("bus", "bus")]

    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(2, 2, width_ratios=[1, 2.2], height_ratios=[1, 1], hspace=0.12, wspace=0.28)
    ax_hist = fig.add_subplot(gs[:, 0])
    axes = [fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, 1])]

    # n_seq below this is where a single unusual sequence can flip the sign of the mean --
    # flagged on the plot itself (open red-ringed marker) rather than only in the caption text.
    N_SEQ_LOW = 5
    legend_handles = {}
    for ax, (cls_code, cls_label) in zip(axes, classes):
        for k in keys:
            color = key_color[k]
            g = bands.filter(
                (pl.col(group_col) == k) & (pl.col("cls") == cls_code) & (pl.col("severity") != "baseline")
            ).with_columns(pl.col("severity").replace(SEVERITY_X).cast(pl.Int64).alias("_x")).sort("_x")
            if g.height == 0:
                continue
            x, y, n_seq = g["_x"].to_list(), g["mean"].to_list(), g["n_seq"].to_list()
            line, = ax.plot(x, y, color=color, linewidth=1.8, zorder=3, label=k)
            legend_handles.setdefault(k, line)
            for xi, yi, n in zip(x, y, n_seq):
                low = n < N_SEQ_LOW
                ax.scatter(xi, yi, s=45 if low else 30, color=color, zorder=4,
                           edgecolor="red" if low else "white", linewidth=1.6 if low else 0.6)
        ax.axhline(0, color="0.3", linewidth=0.8, linestyle="--", zorder=0)
        ax.set_ylabel(f"{cls_label}\nRR delta", fontsize=9)
        ax.set_xticks([1, 2, 3])
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        ax.grid(True, axis="y", color="0.92", linewidth=0.7, zorder=0)
    axes[0].set_title("RR delta = corrupted AP / baseline AP - 1  (0.0 = baseline)", fontsize=10, loc="left")
    axes[0].tick_params(labelbottom=False)
    axes[1].set_xticklabels(["low", "medium", "high"], fontsize=9)
    axes[1].set_xlabel("corruption severity")
    means = bands.filter(pl.col("severity") != "baseline")["mean"].to_numpy()
    lo, hi = min(0.0, np.nanmin(means)), np.nanmax(means)
    pad = 0.15 * (hi - lo)
    for ax in axes:
        ax.set_xlim(0.7, 3.3)
        ax.set_ylim(lo - pad, hi + pad)
    ordered = [k for k in keys if k in legend_handles]
    axes[0].legend([legend_handles[k] for k in ordered], ordered, title=legend_title, fontsize=8, loc="lower left")

    # single histogram, one bar per group_col value at baseline only (not per severity -- the
    # physical frame set is the same regardless of corruption severity, see
    # _per_sequence_rr_delta's frame_counts note)
    g = frame_counts.filter(pl.col(group_col).is_in(keys)).sort(
        pl.col(group_col).cast(pl.Enum(keys)).cast(pl.Utf8)
    )
    ax_hist.barh(g[group_col].to_list(), g["n_frames"].to_list(),
                 color=[key_color[k] for k in g[group_col].to_list()])
    ax_hist.set_xscale("log")
    ax_hist.set_xlabel("N frames (log scale)")
    ax_hist.set_title("frames per condition\n(baseline only)", fontsize=10)
    _add_log_ticks(ax_hist, axis="x")
    for spine in ("top", "right"):
        ax_hist.spines[spine].set_visible(False)

    fig.suptitle(
        "RR delta > 0 means corrupted-condition AP was HIGHER than that sequence's own clean baseline --\n"
        "an apparent gain, not necessarily real: red-ringed points are backed by fewer than 5 sequences,\n"
        "where one atypical sequence can flip the sign. Treat positive values there as noise, not a finding.",
        fontsize=9, color="#7a1f1f", y=0.99,
    )
    fig.subplots_adjust(top=0.86)
    fig.text(0.02, -0.04,
              "AP = 41-point interpolated AP (ap_metrics.compute_ap, same formula as "
              "utils/kitti_eval/eval_revised.py), computed per sequence; line = mean RR delta "
              f"across sequences. Left: physical frame count per {group_col} value, from the "
              "baseline condition only (flat across severity -- the same frames are re-evaluated "
              "under every corruption, so a per-severity count would just multiply by how many "
              "sensor conditions share that severity label).",
              fontsize=7.5, color="0.35", wrap=True)
    fig.savefig(OUT / f"{out_name}.png", bbox_inches="tight")
    fig.savefig(OUT / f"{out_name}.svg", bbox_inches="tight")
    plt.close(fig)


def fig1e_weather_rr_fan_merged():
    weathers = ["fog", "normal", "overcast", "rain", "sleet"]
    _rr_fan_chart("weather", weathers, "weather", "8e_weather_rr_fan_merged")


def fig1c_weather_small_multiples():
    t = weighted_map(df_ladder.group_by(["weather", "severity"], maintain_order=True))
    weathers = ["fog", "normal", "overcast", "rain", "sleet"]  # baseline-mAP-desc, matches fig1/1b order
    sevs = ["baseline", "low", "medium", "high"]
    accent = "#1f6f78"  # single colorblind-safe teal, no red/green needed (one line per panel)

    fig, axes = plt.subplots(1, len(weathers), figsize=(14, 3.4), sharey=True)
    for ax, w in zip(axes, weathers):
        g = t.filter(pl.col("weather") == w).with_columns(
            pl.col("severity").replace(SEVERITY_X).cast(pl.Int64).alias("_x")
        ).sort("_x")
        x, y, se, rel = g["_x"].to_list(), g["mAP"].to_list(), g["se"].to_list(), g["reliable"].to_list()
        y_arr, se_arr = np.array(y), np.array(se)
        ax.fill_between(x, y_arr - se_arr, y_arr + se_arr, color=accent, alpha=0.18, zorder=1)
        ax.plot(x, y, color=accent, linewidth=1.8, zorder=2)
        ax.axhline(y[0], color="0.75", linewidth=0.8, linestyle="--", zorder=0)
        for xi, yi, r in zip(x, y, rel):
            ax.scatter(xi, yi, color=accent, s=45, zorder=3, edgecolor=("red" if not r else "white"),
                       linewidth=1.6 if not r else 0.6)
        ax.set_title(w, fontsize=10)
        ax.set_xticks([0, 1, 2, 3])
        ax.set_xticklabels(sevs, rotation=30, ha="right", fontsize=7.5)
        ax.set_ylim(45, 100)
        ax.grid(True, axis="y", color="0.92", linewidth=0.7, zorder=0)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
    axes[0].set_ylabel("mAP (%, restricted range,\nnum_gt-weighted)")
    fig.text(0.02, -0.06,
              "Shaded band = ±SE, a conservative estimator-precision proxy driven only by pooled "
              "object count (not a percentile range); narrower band = more objects behind that point. "
              f"Dashed line = that panel's own baseline mAP. Red ring = pooled N≤{N_FLOOR} (below reliability floor).",
              fontsize=7.5, color="0.35", wrap=True)
    fig.tight_layout()
    fig.savefig(OUT / "8c_weather_map_small_multiples.png", bbox_inches="tight")
    fig.savefig(OUT / "8c_weather_map_small_multiples.svg", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    fig1_weather()
    fig1b_weather_map_dotgrid()
    fig1c_weather_small_multiples()
    fig1d_weather_fan_by_class()
    fig1e_weather_rr_fan_merged()
    fig2a_environment()
    fig2b_time_of_day()
    fig2c_distance_from_ego()
    fig2d_frame_density()
    fig3_tpfpfn_table()
    fig4_severity_by_sensor()
    print("done ->", OUT)
