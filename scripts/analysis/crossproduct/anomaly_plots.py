#!/usr/bin/env python3
"""Figures for the peer-group anomaly detection addendum. Same conventions
as plots.py (Agg backend, dpi=150). Minimum set implemented: a strip/dot
plot per example peer group with the deviant member highlighted and the
peer median drawn as a reference line (with an N-per-member companion
panel), a severity-ladder violation plot, and the D4 residual heatmap.
"""
from __future__ import annotations

from amscup_paths import REPORTS_DIR  # noqa: E402
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import polars as pl

HERE = Path(__file__).resolve()
FIG_OUT_DIR = REPORTS_DIR / "crossproduct" / "figures" / "anomaly"

sys.path.insert(0, str(HERE.parent))
from anomaly import score_peer_group, flag_anomalies, PEER_GROUPS  # noqa: E402
from detectors import d1_monotonicity_violation, d4_interaction_residual  # noqa: E402


def plot_peer_group_strip(peer_group: str, metric: str, group_key: dict, out_dir: Path = FIG_OUT_DIR) -> Path | None:
    """One group instance: members on x-axis, value on y, peer median as a
    reference line, deviant member(s) highlighted in red. N-per-member
    companion bar panel below."""
    scored = score_peer_group(peer_group, metric)
    fix_cols = PEER_GROUPS[peer_group]["fix"]
    mask = pl.lit(True)
    for c, v in group_key.items():
        mask = mask & (pl.col(c) == v)
    g = scored.filter(mask & (pl.col("status") == "scored"))
    if g.height == 0:
        return None
    flagged_members = set(flag_anomalies(g)["member"].to_list())
    members = g["member"].to_list()
    values = g["value"].to_list()
    ns = g["n_total"].to_list()
    median = g["group_median"][0]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(max(6, 0.8 * len(members)), 6), sharex=True, height_ratios=[3, 1])
    colors = ["#c44e52" if m in flagged_members else "#4c72b0" for m in members]
    ax1.scatter(members, values, c=colors, s=80, zorder=3)
    ax1.axhline(median, color="black", linestyle=":", linewidth=1.5, label=f"peer median ({median:.3f})")
    ax1.set_ylabel(metric)
    ax1.set_title(f"{peer_group}: {', '.join(f'{k}={v}' for k, v in group_key.items())}\n(red = flagged, |robust z| > 3.5)")
    ax1.legend(fontsize=8)
    ax2.bar(members, ns, color="grey", alpha=0.6)
    ax2.set_ylabel("N")
    plt.setp(ax2.get_xticklabels(), rotation=45, ha="right")
    fig.tight_layout()
    out_dir.mkdir(parents=True, exist_ok=True)
    key_str = "_".join(str(v) for v in group_key.values())
    path = out_dir / f"strip_{peer_group}_{metric}_{key_str}.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_severity_violations(metric: str, out_dir: Path = FIG_OUT_DIR) -> Path:
    """All severity-ladder reversals for one metric, one line per violating
    group, non-violating groups shown faint grey for context."""
    scored = score_peer_group("severity_ladder", metric)
    fix_cols = PEER_GROUPS["severity_ladder"]["fix"]
    violations = d1_monotonicity_violation(metric)
    violating_keys = set(
        tuple(row[c] for c in fix_cols) for row in violations.iter_rows(named=True)
    ) if violations.height else set()

    order = {"low": 0, "medium": 1, "high": 2}
    fig, ax = plt.subplots(figsize=(7, 5))
    for key, g in scored.filter(pl.col("status") == "scored").group_by(fix_cols, maintain_order=True):
        key_tuple = key if isinstance(key, tuple) else (key,)
        g = g.with_columns(pl.col("member").replace(order).cast(pl.Int64).alias("r")).sort("r")
        if g.height < 2:
            continue
        is_violation = key_tuple in violating_keys
        ax.plot(
            g["member"], g["value"],
            color="#c44e52" if is_violation else "#cccccc",
            linewidth=2.0 if is_violation else 0.6,
            alpha=1.0 if is_violation else 0.5,
            zorder=3 if is_violation else 1,
        )
    ax.set_xlabel("Severity")
    ax.set_ylabel(metric)
    ax.set_title(f"Severity ladders for {metric}\n(red = monotonicity violation, grey = consistent)")
    fig.tight_layout()
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"severity_violations_{metric}.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_d4_residual_heatmap(metric: str, row_dim: str = "condition", col_dim: str = "weather", cls: str = "sed", out_dir: Path = FIG_OUT_DIR) -> Path:
    result = d4_interaction_residual(metric, row_dim, col_dim, cls)
    residuals = result["residuals"]
    if residuals.is_empty():
        raise ValueError("no residuals computed -- check row_dim/col_dim/cls have overlapping reliable data")
    rows = sorted(residuals[row_dim].unique().to_list())
    cols = sorted(residuals[col_dim].unique().to_list())
    mat = np.full((len(rows), len(cols)), np.nan)
    for r in residuals.iter_rows(named=True):
        mat[rows.index(r[row_dim]), cols.index(r[col_dim])] = r["residual"]

    fig, ax = plt.subplots(figsize=(6, 0.3 * len(rows) + 2))
    vmax = np.nanmax(np.abs(mat))
    im = ax.imshow(mat, cmap="RdBu_r", vmin=-vmax, vmax=vmax, aspect="auto")
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels(cols, rotation=45, ha="right")
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(rows, fontsize=6)
    fig.colorbar(im, ax=ax, label=f"{metric} residual (observed - additive fit)")
    ax.set_title(f"D4 median-polish residuals, {cls}\nfit quality={result['fit_quality']:.2f}")
    fig.tight_layout()
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"d4_residual_heatmap_{metric}_{cls}.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def build_example_figures(out_dir: Path = FIG_OUT_DIR) -> list[Path]:
    """A representative sample, not every possible group instance --
    building all ~1800 stratum_sweep strip plots isn't useful. Picks the
    top-ranked flagged instance per illustrative peer group."""
    paths = []
    metric = "ap_restricted_range"
    flagged = flag_anomalies(score_peer_group("sibling_conditions", metric))
    if flagged.height:
        top = flagged.sort("rank_score", descending=True).row(0, named=True)
        fix_cols = PEER_GROUPS["sibling_conditions"]["fix"]
        key = {c: top[c] for c in fix_cols}
        p = plot_peer_group_strip("sibling_conditions", metric, key, out_dir)
        if p:
            paths.append(p)
    paths.append(plot_severity_violations(metric, out_dir))
    paths.append(plot_d4_residual_heatmap(metric, out_dir=out_dir))
    return paths


if __name__ == "__main__":
    for p in build_example_figures():
        print(p)
