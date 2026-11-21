#!/usr/bin/env python3
"""Figures for the cross-product analysis, PNG for LaTeX inclusion. Reuses
this repo's existing styling conventions (matplotlib Agg backend, dpi=150,
two-letter condition codes, `original` bolded/distinguished) from
radar_charts.py rather than inventing a new style.

Minimum set implemented this pass: severity-monotonicity lines (per effect
family), a retention heatmap (condition x weather), the FP-vs-FN scatter,
and churn ranking bars. N-per-bin bars and bootstrap CI ribbons are NOT
included yet -- see run_analysis.py's docstring for what's deferred.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import polars as pl

HERE = Path(__file__).resolve()
AMSCUP_ROOT = HERE.parents[8]
FIG_OUT_DIR = AMSCUP_ROOT / "repos" / "K-Radar" / "outputs" / "robustness_reports" / "crossproduct" / "figures"

sys.path.insert(0, str(HERE.parents[1]))
from radar_charts import CONDITION_CODE, CLEAN_CONDITION  # noqa: E402

sys.path.insert(0, str(HERE.parent))
from queries import load_summary, load_deltas, q4_fp_fn_joint, q5_churn  # noqa: E402

SENSOR_COLOR = {"camera": "#4c72b0", "lidar": "#55a868", "radar": "#c44e52"}
SEVERITY_MARKER = {"low": "o", "medium": "s", "high": "^"}
EFFECTS = ["gaussian_noise", "loss_partial"]
SEVERITIES = ["low", "medium", "high"]
SENSORS = ["camera", "lidar", "radar"]


def _log_size(n: int, lo: float = 15.0, hi: float = 120.0) -> float:
    """Marker size scaled by log(N), so a 40k-row condition and a 120-row
    edge case are visually distinguishable at a glance."""
    if n <= 1:
        return lo
    return lo + (hi - lo) * min(1.0, np.log10(n) / 5.0)


def plot_severity_monotonicity(out_dir: Path = FIG_OUT_DIR) -> Path:
    """One line per (sensor, effect) family, AP vs. severity, `original`
    plotted as a bolded horizontal reference line."""
    summary = load_summary("condition")
    orig_ap = summary.filter(pl.col("condition") == CLEAN_CONDITION)["ap_restricted_range"].item()

    fig, ax = plt.subplots(figsize=(9, 6))
    for sensor in SENSORS:
        for effect in EFFECTS:
            xs, ys, ns = [], [], []
            for i, sev in enumerate(SEVERITIES):
                cond = f"{sensor}_{effect}_{sev}"
                row = summary.filter(pl.col("condition") == cond)
                if row.height == 0:
                    continue
                xs.append(i)
                ys.append(row["ap_restricted_range"].item())
                ns.append(row["n_total"].item())
            if not xs:
                continue
            sizes = [_log_size(n) for n in ns]
            ax.plot(xs, ys, color=SENSOR_COLOR[sensor], linestyle="-" if effect == "gaussian_noise" else "--",
                    marker="o", label=f"{sensor} {effect}", alpha=0.85)
            ax.scatter(xs, ys, s=sizes, color=SENSOR_COLOR[sensor], zorder=3)
    ax.axhline(orig_ap, color="black", linewidth=2.0, linestyle=":", label=f"original ({orig_ap:.1f})", zorder=1)
    ax.set_xticks(range(len(SEVERITIES)))
    ax.set_xticklabels(SEVERITIES)
    ax.set_ylabel("Restricted-range AP")
    ax.set_xlabel("Severity")
    ax.set_title("Severity monotonicity by (sensor, effect) family\n(marker size ~ log(N); dotted = original baseline)")
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout()
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "severity_monotonicity.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_retention_heatmap(out_dir: Path = FIG_OUT_DIR) -> Path:
    """Condition x weather AP-retention heatmap, pooled over cls/tod/env.
    Unreliable/no_data cells are masked (shown as hatched grey), never
    silently colored as if they were a real 0%/100% retention value."""
    level = "cond_cls_weather"
    deltas = load_deltas(level)
    agg = deltas.group_by(["condition", "weather"]).agg(
        pl.col("ap_restricted_range_retention").mean().alias("retention"),
        pl.col("reliable").all().alias("all_reliable"),
        pl.col("n_total").sum().alias("n_total"),
    )
    conditions = sorted(agg["condition"].unique().to_list())
    weathers = ["normal", "overcast", "fog", "rain", "sleet"]
    mat = np.full((len(conditions), len(weathers)), np.nan)
    mask = np.zeros_like(mat, dtype=bool)
    for i, cond in enumerate(conditions):
        for j, w in enumerate(weathers):
            row = agg.filter((pl.col("condition") == cond) & (pl.col("weather") == w))
            if row.height == 0 or not row["all_reliable"].item():
                mask[i, j] = True
                continue
            mat[i, j] = row["retention"].item()

    fig, ax = plt.subplots(figsize=(7, 0.32 * len(conditions) + 2))
    masked = np.ma.masked_array(mat, mask=mask | np.isnan(mat))
    cmap = plt.get_cmap("RdYlGn").copy()
    cmap.set_bad(color="#dddddd", alpha=0.6)
    im = ax.imshow(masked, cmap=cmap, vmin=0.0, vmax=1.1, aspect="auto")
    ax.set_xticks(range(len(weathers)))
    ax.set_xticklabels(weathers, rotation=45, ha="right")
    ax.set_yticks(range(len(conditions)))
    ax.set_yticklabels([CONDITION_CODE.get(c, c) for c in conditions], fontsize=7)
    fig.colorbar(im, ax=ax, label="AP retention vs. original")
    ax.set_title("AP retention by condition x weather\n(grey = unreliable/no_data, masked not zero)")
    fig.tight_layout()
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "retention_heatmap_condition_weather.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_fp_fn_scatter(out_dir: Path = FIG_OUT_DIR) -> Path:
    q4 = q4_fp_fn_joint("full")
    data = q4["scatter_data"]
    fig, ax = plt.subplots(figsize=(7, 7))
    sizes = [_log_size(n) for n in data["n_total"].to_list()]
    colors = [SENSOR_COLOR.get(m, "grey") for m in data["modality"].to_list()]
    ax.scatter(data["fp_rate"], data["fn_rate"], s=sizes, c=colors, alpha=0.5, edgecolor="none")
    worst = q4["joint_worst_offenders"]
    if worst.height:
        ax.scatter(worst["fp_rate"], worst["fn_rate"], s=[_log_size(n) * 1.3 for n in worst["n_total"]],
                   facecolors="none", edgecolors="black", linewidths=1.2, label="joint worst offenders")
    ax.set_xlabel("FP rate")
    ax.set_ylabel("FN rate")
    ax.set_title("FP rate vs. FN rate, all reliable full-grain cells\n(marker size ~ log(N); color = modality)")
    for sensor, color in SENSOR_COLOR.items():
        ax.scatter([], [], color=color, label=sensor)
    ax.legend(fontsize=8)
    fig.tight_layout()
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "fp_fn_scatter.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_churn_ranking(out_dir: Path = FIG_OUT_DIR) -> Path:
    q5 = q5_churn()
    df = q5["max_churn"].to_pandas() if hasattr(q5["max_churn"], "to_pandas") else q5["max_churn"]
    df = df.sort_values("churn_rate")
    colors = [SENSOR_COLOR.get(c.split("_")[0], "grey") for c in df["corrupted_condition"]]
    fig, ax = plt.subplots(figsize=(8, 0.4 * len(df) + 1.5))
    ax.barh(df["corrupted_condition"], df["churn_rate"], color=colors)
    ax.set_xlabel("Churn rate (miss + recovery over total GT objects)")
    ax.set_title("Highest-churn conditions (static-object corruption-fragility, not tracking)")
    fig.tight_layout()
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "churn_ranking.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def build_all_figures(out_dir: Path = FIG_OUT_DIR) -> list[Path]:
    return [
        plot_severity_monotonicity(out_dir),
        plot_retention_heatmap(out_dir),
        plot_fp_fn_scatter(out_dir),
        plot_churn_ranking(out_dir),
    ]


if __name__ == "__main__":
    paths = build_all_figures()
    for p in paths:
        print(p)
