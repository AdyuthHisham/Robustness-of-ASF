"""Generate the 6 candidate figures for the K-Radar crossproduct robustness
results (see docs/crossproduct_trends_and_anomalies.md for write-up).

Source: repos/K-Radar/outputs/robustness_reports/crossproduct_v2/
Run: uv run --project test-bed/src/Modules/robust_testing/kradar python docs/crossproduct_figures/generate_plots.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import polars as pl

REPO_ROOT = Path("/home/adhish/Productivity/AMSCUP")
BASE = REPO_ROOT / "repos/K-Radar/outputs/robustness_reports/crossproduct_v2"
REPORTS = BASE / "reports"
OUT = REPO_ROOT / "docs/crossproduct_figures"
OUT.mkdir(parents=True, exist_ok=True)

SEVERITY_ORDER = {"low": 1, "medium": 2, "high": 3}
MODALITY_COLOR = {"camera": "#3B82F6", "lidar": "#F59E0B", "radar": "#10B981"}
RELIABLE_ALPHA = 1.0
UNRELIABLE_ALPHA = 0.35
N_FLOOR = 30

plt.rcParams.update(
    {
        "figure.dpi": 150,
        "savefig.dpi": 150,
        "font.size": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
    }
)


def load(name: str) -> pl.DataFrame:
    return pl.read_parquet(BASE / f"{name}.parquet")


def load_csv(name: str) -> pl.DataFrame:
    return pl.read_csv(REPORTS / f"{name}.csv")


# ---------------------------------------------------------------------------
# Plot 1 — severity-degradation line plot, one line per (modality, effect)
# ---------------------------------------------------------------------------
def plot1_severity_degradation():
    df = load("summary_condition")
    df = df.filter(pl.col("effect").is_in(["gaussian_noise", "loss_partial"]))
    baseline = load("summary_condition").filter(pl.col("condition") == "original")
    baseline_f1 = baseline["f1"][0]
    baseline_n = baseline["n_sequences"][0]

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.axhline(baseline_f1, color="0.6", linestyle=":", linewidth=1, zorder=1)
    ax.annotate(
        f"original (F1={baseline_f1:.3f}, N_seq={baseline_n})",
        xy=(1.0, baseline_f1),
        xytext=(0, 6),
        textcoords="offset points",
        fontsize=8,
        color="0.4",
        va="bottom",
    )

    for (modality, effect), group in df.group_by(["modality", "effect"], maintain_order=True):
        g = group.with_columns(
            pl.col("severity").replace(SEVERITY_ORDER).cast(pl.Int64).alias("_sev_rank")
        ).sort("_sev_rank")
        x = [SEVERITY_ORDER[s] for s in g["severity"]]
        y = g["f1"].to_list()
        reliable = g["reliable"].to_list()
        n_seq = g["n_sequences"].to_list()
        linestyle = "-" if effect == "gaussian_noise" else "--"
        color = MODALITY_COLOR[modality]
        ax.plot(x, y, linestyle=linestyle, color=color, linewidth=1.5, zorder=2)
        for xi, yi, rel, n in zip(x, y, reliable, n_seq):
            ax.scatter(
                xi,
                yi,
                color=color,
                s=50,
                alpha=RELIABLE_ALPHA if rel else UNRELIABLE_ALPHA,
                edgecolor="white",
                linewidth=0.5,
                zorder=3,
            )

    ax.set_xticks([1, 2, 3])
    ax.set_xticklabels(["low", "medium", "high"])
    ax.set_xlim(0.8, 3.6)
    ax.set_xlabel("severity")
    ax.set_ylabel("F1 (condition-level, N=58 sequences per cell)")
    ax.set_title("F1 vs. severity by modality × effect")

    modality_handles = [
        plt.Line2D([0], [0], color=c, lw=2, label=m) for m, c in MODALITY_COLOR.items()
    ]
    effect_handles = [
        plt.Line2D([0], [0], color="0.3", lw=1.5, linestyle="-", label="gaussian_noise"),
        plt.Line2D([0], [0], color="0.3", lw=1.5, linestyle="--", label="loss_partial"),
    ]
    leg1 = ax.legend(handles=modality_handles, loc="lower left", title="modality", fontsize=8)
    ax.add_artist(leg1)
    ax.legend(handles=effect_handles, loc="lower right", title="effect", fontsize=8)

    fig.text(
        0.02, -0.02,
        f"All condition-level cells reliable at N>{N_FLOOR} sequences (n_sequences=58 for every point shown); "
        "faded-marker convention reserved for cells below the floor, none occur at this aggregation level.",
        fontsize=7, color="0.4", ha="left",
    )
    fig.tight_layout()
    fig.savefig(OUT / "1_severity_degradation.png", bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Plot 2 — corruption-type damage ranking (sorted horizontal bar)
# ---------------------------------------------------------------------------
def plot2_damage_ranking():
    df = load("deltas_condition").sort("f1_delta")
    conditions = df["condition"].to_list()
    deltas = df["f1_delta"].to_list()
    reliable = df["reliable"].to_list()

    fig, ax = plt.subplots(figsize=(8, 7))
    colors = []
    for c in conditions:
        modality = c.split("_")[0]
        colors.append(MODALITY_COLOR.get(modality, "0.5"))

    bars = ax.barh(range(len(conditions)), deltas, color=colors)
    for bar, r in zip(bars, reliable):
        bar.set_alpha(RELIABLE_ALPHA if r else UNRELIABLE_ALPHA)
        if not r:
            bar.set_hatch("///")
            bar.set_edgecolor("0.3")

    ax.set_yticks(range(len(conditions)))
    ax.set_yticklabels(conditions, fontsize=7.5)
    ax.axvline(0, color="0.2", linewidth=0.8)
    ax.set_xlabel("Δ F1 vs. original baseline")
    ax.set_title("Corruption-type damage ranking (F1 delta, all 21 non-baseline conditions)")

    handles = [mpatches.Patch(color=c, label=m) for m, c in MODALITY_COLOR.items()]
    if not all(reliable):
        handles.append(mpatches.Patch(facecolor="0.7", hatch="///", edgecolor="0.3", label=f"N≤{N_FLOOR} (unreliable)"))
    ax.legend(handles=handles, loc="lower right", fontsize=8)

    fig.tight_layout()
    fig.savefig(OUT / "2_damage_ranking.png", bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Plot 3 — modality x class heatmap (F1, annotated)
# ---------------------------------------------------------------------------
def plot3_modality_class_heatmap():
    df = load("summary_cond_cls")
    df = df.sort("condition")
    conditions = df["condition"].unique().sort().to_list()
    classes = ["sed", "bus"]

    grid = pl.DataFrame({"condition": conditions})
    matrix = []
    reliability_matrix = []
    for cls in classes:
        row_vals = []
        row_rel = []
        for cond in conditions:
            cell = df.filter((pl.col("condition") == cond) & (pl.col("cls") == cls))
            if cell.height == 0:
                row_vals.append(float("nan"))
                row_rel.append(True)
            else:
                row_vals.append(cell["f1"][0])
                row_rel.append(cell["reliable"][0])
        matrix.append(row_vals)
        reliability_matrix.append(row_rel)

    fig, ax = plt.subplots(figsize=(11, 3.2))
    im = ax.imshow(matrix, aspect="auto", cmap="RdYlGn", vmin=0.5, vmax=0.9)

    for i, cls in enumerate(classes):
        for j, cond in enumerate(conditions):
            val = matrix[i][j]
            rel = reliability_matrix[i][j]
            text = f"{val:.2f}" if val == val else "n/a"
            ax.text(j, i, text, ha="center", va="center", fontsize=6.5,
                    color="black" if rel else "0.35")
            if not rel:
                ax.add_patch(
                    mpatches.Rectangle(
                        (j - 0.5, i - 0.5), 1, 1, fill=False,
                        hatch="////", edgecolor="0.3", linewidth=0,
                    )
                )

    ax.set_xticks(range(len(conditions)))
    ax.set_xticklabels(conditions, rotation=90, fontsize=6.5)
    ax.set_yticks(range(len(classes)))
    ax.set_yticklabels(classes)
    ax.set_title("F1 by condition × class (hatched = N≤%d unreliable)" % N_FLOOR)
    fig.colorbar(im, ax=ax, shrink=0.6, label="F1")
    fig.tight_layout()
    fig.savefig(OUT / "3_modality_class_heatmap.png", bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Plot 4 — D1 monotonicity-violation spotlight (small multiples)
# ---------------------------------------------------------------------------
def plot4_monotonicity_spotlight():
    d1 = load_csv("d1_monotonicity_violations")
    full = load("summary_cond_cls_weather_tod")

    # d1 only carries precision/recall/ap_restricted_range (no f1) — use precision,
    # the largest-count metric (106/222 rows). `delta` here is already the pipeline's
    # magnitude of the non-monotonic step (verified: min=0.0, max>0, no negative
    # values in this file), so "largest violations" = largest delta, descending.
    METRIC = "precision"
    viol = d1.filter(pl.col("metric") == METRIC).sort("delta", descending=True)
    top = viol.head(8).to_dicts()

    fig, axes = plt.subplots(2, 4, figsize=(15, 6), sharey=False)
    axes = axes.flatten()

    for ax, row in zip(axes, top):
        modality, effect, cls, weather, tod = (
            row["modality"], row["effect"], row["cls"], row["weather"], row["time_of_day"]
        )
        sub = full.filter(
            (pl.col("modality") == modality)
            & (pl.col("effect") == effect)
            & (pl.col("cls") == cls)
            & (pl.col("weather") == weather)
            & (pl.col("time_of_day") == tod)
        ).with_columns(
            pl.col("severity").replace(SEVERITY_ORDER).cast(pl.Int64).alias("_sev_rank")
        ).sort("_sev_rank")

        baseline = full.filter(
            (pl.col("condition") == "original") & (pl.col("cls") == cls)
            & (pl.col("weather") == weather) & (pl.col("time_of_day") == tod)
        )

        x = [SEVERITY_ORDER[s] for s in sub["severity"]]
        y = sub[METRIC].to_list()
        rel = sub["reliable"].to_list()
        n = sub["n_total"].to_list()

        if baseline.height > 0:
            x = [0] + x
            y = [baseline[METRIC][0]] + y
            rel = [baseline["reliable"][0]] + rel
            n = [baseline["n_total"][0]] + n

        colors = [MODALITY_COLOR[modality]] * len(x)
        ax.plot(x, y, color=MODALITY_COLOR[modality], linewidth=1.2, zorder=1)
        for xi, yi, r in zip(x, y, rel):
            ax.scatter(xi, yi, color=MODALITY_COLOR[modality], s=45,
                       alpha=RELIABLE_ALPHA if r else UNRELIABLE_ALPHA,
                       marker="o" if r else "x", zorder=2)

        # mark the flagged step
        fs, ts = SEVERITY_ORDER[row["from_severity"]], SEVERITY_ORDER[row["to_severity"]]
        ax.axvspan(fs - 0.15, ts + 0.15, color="red", alpha=0.08)

        ax.set_xticks([0, 1, 2, 3])
        ax.set_xticklabels(["orig", "low", "med", "high"], fontsize=7)
        min_n = min(n)
        title_color = "black" if min(rel) else "firebrick"
        ax.set_title(
            f"{modality}/{effect}\n{cls},{weather},{tod}\nΔ={row['delta']:.3f} (min N={min_n})",
            fontsize=7.5, color=title_color,
        )
        ax.set_ylabel(METRIC, fontsize=7)

    fig.suptitle(
        f"D1 monotonicity violations — 8 largest |Δ{METRIC}| non-monotonic severity steps\n"
        f"(x-marker/faded = source cell N≤{N_FLOOR}; titles in red = violation rests on ≥1 unreliable cell)",
        fontsize=10,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.90])
    fig.savefig(OUT / "4_monotonicity_spotlight.png", bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Plot 5 — reliability coverage map (condition x weather*tod)
# ---------------------------------------------------------------------------
def plot5_reliability_coverage():
    # Use summary_cond_cls_weather_tod directly (native granularity, no distance_bucket/
    # environment collapse needed) and show fraction of the 2 cls cells that are
    # reliable per (condition, weather, tod) — "any-reliable" would hide that most
    # sub-cells fail the floor, so this plots the actual reliable fraction (0, 0.5, 1).
    df = load("summary_cond_cls_weather_tod")
    agg = df.group_by(["condition", "weather", "time_of_day"]).agg(
        pl.col("n_total").sum().alias("n_total_sum"),
        pl.col("reliable").mean().alias("reliable_frac"),
    )
    conditions = sorted(agg["condition"].unique().to_list())
    strata = sorted({(w, t) for w, t in zip(agg["weather"], agg["time_of_day"])})
    strata_labels = [f"{w}/{t}" for w, t in strata]

    state = []  # NaN = no_data, else fraction of cls cells reliable (0, 0.5, 1)
    for cond in conditions:
        row = []
        for w, t in strata:
            cell = agg.filter(
                (pl.col("condition") == cond) & (pl.col("weather") == w) & (pl.col("time_of_day") == t)
            )
            if cell.height == 0 or cell["n_total_sum"][0] == 0:
                row.append(float("nan"))
            else:
                row.append(cell["reliable_frac"][0])
        state.append(row)

    fig, ax = plt.subplots(figsize=(9, 8))
    cmap = plt.matplotlib.colormaps["RdYlGn"].copy()
    cmap.set_bad("#F3F4F6")
    im = ax.imshow(state, aspect="auto", cmap=cmap, vmin=0, vmax=1)
    ax.set_xticks(range(len(strata_labels)))
    ax.set_xticklabels(strata_labels, rotation=90, fontsize=7)
    ax.set_yticks(range(len(conditions)))
    ax.set_yticklabels(conditions, fontsize=6.5)
    ax.set_title(
        "Reliability coverage: fraction of {sed,bus} cells reliable (N≥%d),\n"
        "per condition × (weather/time_of_day) — grey = no_data" % N_FLOOR
    )
    fig.colorbar(im, ax=ax, shrink=0.6, label="fraction of cls cells reliable")
    fig.tight_layout()
    fig.savefig(OUT / "5_reliability_coverage.png", bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Plot 6 — modality-divergence scatter (camera vs lidar vs radar, y=x reference)
# ---------------------------------------------------------------------------
def plot6_modality_divergence():
    full = load("summary_cond_cls_weather_tod")
    d3 = load_csv("d3_modality_divergence")

    # For every (effect, severity, cls, weather, tod) stratum with all 3 modalities present,
    # get F1 for camera/lidar/radar.
    corrupted = full.filter(pl.col("modality").is_not_null())
    pivot = corrupted.pivot(
        index=["effect", "severity", "cls", "weather", "time_of_day"],
        on="modality",
        values="f1",
    )
    rel_pivot = corrupted.pivot(
        index=["effect", "severity", "cls", "weather", "time_of_day"],
        on="modality",
        values="reliable",
    )
    pivot = pivot.filter(
        pl.col("camera").is_not_null() & pl.col("lidar").is_not_null() & pl.col("radar").is_not_null()
    )
    rel_pivot = rel_pivot.join(
        pivot.select(["effect", "severity", "cls", "weather", "time_of_day"]),
        on=["effect", "severity", "cls", "weather", "time_of_day"],
        how="inner",
    )

    flagged_keys = set(
        zip(d3["effect"], d3["severity"], d3["cls"], d3["weather"], d3["time_of_day"])
    )

    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5))
    pairs = [("camera", "lidar"), ("camera", "radar")]
    for ax, (a, b) in zip(axes, pairs):
        xa = pivot[a].to_list()
        yb = pivot[b].to_list()
        rel_a = rel_pivot[a].to_list()
        rel_b = rel_pivot[b].to_list()
        keys = list(zip(pivot["effect"], pivot["severity"], pivot["cls"], pivot["weather"], pivot["time_of_day"]))
        flagged = [k in flagged_keys for k in keys]

        both_reliable = [ra and rb for ra, rb in zip(rel_a, rel_b)]
        for xi, yi, br, fl in zip(xa, yb, both_reliable, flagged):
            ax.scatter(
                xi, yi,
                color="crimson" if fl else "0.3",
                alpha=RELIABLE_ALPHA if br else UNRELIABLE_ALPHA,
                s=22 if not fl else 34,
                zorder=3 if fl else 2,
                edgecolor="none",
            )
        lims = [0, 1]
        ax.plot(lims, lims, color="0.6", linestyle=":", linewidth=1, zorder=1)
        ax.set_xlim(lims)
        ax.set_ylim(lims)
        ax.set_xlabel(f"{a} F1")
        ax.set_ylabel(f"{b} F1")
        ax.set_title(f"{a} vs {b} (per condition×cls×weather×tod stratum)")

    handles = [
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="0.3", markersize=7, label="not flagged"),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="crimson", markersize=8, label="in d3_modality_divergence.csv"),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="0.3", alpha=UNRELIABLE_ALPHA, markersize=7, label=f"≥1 modality N≤{N_FLOOR}"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=8, bbox_to_anchor=(0.5, -0.02))
    fig.suptitle("Modality parity: F1 above y=x means the y-axis modality wins that stratum")
    fig.tight_layout(rect=[0, 0.05, 1, 0.95])
    fig.savefig(OUT / "6_modality_divergence.png", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    plot1_severity_degradation()
    plot2_damage_ranking()
    plot3_modality_class_heatmap()
    plot4_monotonicity_spotlight()
    plot5_reliability_coverage()
    plot6_modality_divergence()
    print("done ->", OUT)
