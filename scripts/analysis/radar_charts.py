#!/usr/bin/env python3
"""Radar (spider) charts of per-class AP by condition, for a single K-Radar
sequence, split by severity tier.

Produces 6 charts: {sed, bus} x {low, medium, high} severity. Each chart has
one axis per (sensor, effect) combo that has severity tiers (camera/lidar/radar
x frame_deletion/gaussian_noise/loss_partial = 9 axes) plus one axis for the
clean/`original` condition, bolded/distinguished as the reference point since
it isn't itself part of the severity sweep.

AP is computed with `compute_ap_grouped` from the K-Radar submodule's
`ap_metrics.py` (K-Radar's own 41-point interpolated-AP evaluator, ported
verbatim from utils/kitti_eval/eval_revised.py) -- not reimplemented here --
applied to `row_table_iou03.parquet` (IoU=0.3), filtered to one sequence, or
pooled across every sequence when sequence="all".

Usage as a library:
    from radar_charts import build_all_charts
    build_all_charts(sequence="46", out_dir=(FIGURES_DIR / "radar_charts"))
    build_all_charts(sequence="all", out_dir=(FIGURES_DIR / "radar_charts"))

Run standalone:
    uv run python scripts/analysis/radar_charts.py --sequence 46
    uv run python scripts/analysis/radar_charts.py --sequence all
"""
from __future__ import annotations

from amscup_paths import ROOT, REPORTS_DIR, FIGURES_DIR  # noqa: E402
import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import polars as pl

HERE = Path(__file__).resolve()
AMSCUP_ROOT = ROOT
ROW_TABLE_PATH = REPORTS_DIR / "row_table_iou03.parquet"

from robustness.ap_metrics import compute_ap_grouped  # noqa: E402

SENSORS = ["camera", "lidar", "radar"]
EFFECTS = ["frame_deletion", "gaussian_noise", "loss_partial"]
SEVERITIES = ["low", "medium", "high"]
CLASSES = ["sed", "bus"]
CLEAN_CONDITION = "original"

# Two-letter axis codes. OG = original/clean reference; others = first letter
# of sensor + first letter of effect. No collisions across the 9 sensor x
# effect combos (verified: C{F,G,P}, L{F,G,P}, R{F,G,P} are all distinct).
CONDITION_CODE = {CLEAN_CONDITION: "OG"}
for _sensor in SENSORS:
    for _effect in EFFECTS:
        _code = _sensor[0].upper() + {"frame_deletion": "F", "gaussian_noise": "G", "loss_partial": "P"}[_effect]
        CONDITION_CODE[(_sensor, _effect)] = _code

CLASS_LABEL = {"sed": "Car (sed)", "bus": "Bus"}

# frame_deletion excluded from radar chart axes per user request (2026-08-25)
# -- still present in EFFECTS/box_plots.py's CONDITION_ORDER, this only trims
# the radar charts' axis set, not the underlying effect sweep.
RADAR_AXIS_EFFECTS = [e for e in EFFECTS if e != "frame_deletion"]
AXIS_ORDER = [(s, e) for s in SENSORS for e in RADAR_AXIS_EFFECTS]  # 6 severity-tiered axes, fixed order for all charts


ALL_SEQUENCES = "all"


def load_row_table(sequence: str) -> pl.DataFrame:
    """Loads row_table_iou03.parquet. sequence=ALL_SEQUENCES returns every
    sequence pooled (matching build_figures.py's pooled-mAP convention);
    otherwise filtered to one sequence. Raises if the result is empty -- fail
    loud, don't silently plot an empty chart."""
    df = pl.read_parquet(ROW_TABLE_PATH)
    if sequence != ALL_SEQUENCES:
        df = df.filter(pl.col("sequence") == sequence)
    if df.height == 0:
        raise ValueError(f"sequence {sequence!r} has no rows in {ROW_TABLE_PATH}")
    return df


def compute_ap_by_condition_cls(row_table: pl.DataFrame) -> dict[tuple[str, str], float]:
    """{(condition, cls): ap} for every (condition, cls) cell present in
    row_table with num_gt > 0. Missing cells (condition/cls combo not present
    in this sequence's data at all) are simply absent from the dict -- callers
    must handle missing keys explicitly (np.nan), never default to 0.0."""
    ap_table = compute_ap_grouped(row_table, ["condition", "cls"])
    return {(row["condition"], row["cls"]): row["ap"] for row in ap_table.iter_rows(named=True)}


COVERAGE_THRESHOLD_PCT = 90.0  # matches build_figures.py's convention


def compute_condition_coverage(row_table: pl.DataFrame) -> dict[str, float]:
    """{condition: coverage_pct} = (# distinct (sequence, frame) pairs with
    predictions under this condition) / (# under `original`) * 100, in this
    row_table's scope (one sequence, or pooled). Several conditions --
    frame_deletion at higher severities especially -- had their inference run
    crash partway through on Alvis, so their row count reflects only whatever
    frames finished before the crash, not the full frame set. An AP computed
    from a handful of surviving frames is not comparable to one computed from
    the full sequence; this coverage number is how build_radar_chart decides
    which axes to flag rather than plot at face value."""
    orig_frames = row_table.filter(pl.col("condition") == CLEAN_CONDITION).select(["sequence", "frame"]).unique().height
    if orig_frames == 0:
        return {}
    cov = row_table.group_by("condition").agg(pl.struct(["sequence", "frame"]).n_unique().alias("n"))
    cov = cov.with_columns((pl.col("n") / orig_frames * 100).alias("pct"))
    return {row["condition"]: row["pct"] for row in cov.iter_rows(named=True)}


def build_radar_chart(
    ap_by_cond_cls: dict[tuple[str, str], float],
    coverage_by_condition: dict[str, float],
    cls: str,
    severity: str,
    sequence: str,
    ylim: float,
    out_dir: Path,
) -> Path:
    """One radar chart: 9 severity-tiered axes (fixed AXIS_ORDER) + 1 clean
    axis, for one class at one severity. Axes with no data for this sequence
    (condition absent entirely) are drawn as a gap in the line and labeled
    with a trailing '(N/A)'. Axes with data but <90% frame coverage vs
    `original` (crashed-mid-run conditions -- AP computed from a handful of
    surviving frames) are still plotted so the point isn't hidden, but with a
    hollow orange 'x' marker and a coverage-pct label instead of the normal
    filled dot, and excluded from the connecting line -- never silently
    presented as equivalent to a fully-covered condition."""
    labels: list[str] = []
    values: list[float] = []
    is_clean: list[bool] = []
    has_data: list[bool] = []
    low_coverage: list[bool] = []

    clean_ap = ap_by_cond_cls.get((CLEAN_CONDITION, cls))
    labels.append(CONDITION_CODE[CLEAN_CONDITION])
    values.append(clean_ap if clean_ap is not None else np.nan)
    is_clean.append(True)
    has_data.append(clean_ap is not None)
    low_coverage.append(False)

    for sensor, effect in AXIS_ORDER:
        condition = f"{sensor}_{effect}_{severity}"
        ap = ap_by_cond_cls.get((condition, cls))
        code = CONDITION_CODE[(sensor, effect)]
        cov_pct = coverage_by_condition.get(condition)
        is_low_cov = ap is not None and (cov_pct is None or cov_pct < COVERAGE_THRESHOLD_PCT)
        if ap is None:
            label = f"{code}\n(N/A)"
        elif is_low_cov:
            label = f"{code}\n({cov_pct:.1f}% cov)"
        else:
            label = code
        labels.append(label)
        values.append(ap if ap is not None else np.nan)
        is_clean.append(False)
        has_data.append(ap is not None)
        low_coverage.append(is_low_cov)

    n = len(labels)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    angles_closed = angles + angles[:1]
    values_arr = np.array(values, dtype=float)

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw={"projection": "polar"})
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_ylim(0, ylim)

    # Plot only contiguous runs of present, adequately-covered data; matplotlib's
    # automatic NaN-gap handling doesn't apply cleanly on a polar axis (a NaN
    # radius renders as r=0, not a break), so missing/low-coverage conditions
    # are excluded from the connecting line by hand instead of drawn as if
    # they were a normal, trustworthy AP value.
    values_closed = np.concatenate([values_arr, values_arr[:1]])
    angles_arr = np.array(angles_closed)
    low_coverage_closed = np.array(low_coverage + low_coverage[:1])
    present_mask = ~np.isnan(values_closed) & ~low_coverage_closed
    run_start = None
    for i in range(len(values_closed)):
        if present_mask[i] and run_start is None:
            run_start = i
        if (not present_mask[i] or i == len(values_closed) - 1) and run_start is not None:
            run_end = i if present_mask[i] else i  # stop before the missing point
            ax.plot(
                angles_arr[run_start : run_end + (1 if present_mask[i] else 0)],
                values_closed[run_start : run_end + (1 if present_mask[i] else 0)],
                color="#1f6feb",
                linewidth=1.5,
                zorder=2,
            )
            run_start = None
    # No shaded fill: with gaps present, a fill polygon would connect
    # non-adjacent axes across the missing points and misrepresent the shape.

    any_low_coverage = False
    for angle, val, clean, present, low_cov in zip(angles, values_arr, is_clean, has_data, low_coverage):
        if not present:
            continue
        if low_cov:
            ax.scatter([angle], [val], color="#e8590c", marker="x", s=70, linewidths=2, zorder=3)
            any_low_coverage = True
        elif clean:
            ax.scatter([angle], [val], color="black", marker="*", s=220, zorder=4, label="clean (reference)")
        else:
            ax.scatter([angle], [val], color="#1f6feb", marker="o", s=40, zorder=3)

    ax.set_xticks(angles)
    tick_labels = ax.set_xticklabels(labels, fontsize=9)
    for lbl, clean, low_cov in zip(tick_labels, is_clean, low_coverage):
        if clean:
            lbl.set_fontweight("bold")
            lbl.set_fontsize(11)
        elif low_cov:
            lbl.set_color("#e8590c")

    seq_label = "all sequences (pooled)" if sequence == ALL_SEQUENCES else f"sequence {sequence}"
    ax.set_title(
        f"AP by condition -- {CLASS_LABEL[cls]}, severity={severity}, {seq_label}\n(IoU=0.3)",
        fontsize=12,
        pad=20,
    )
    if any_low_coverage:
        fig.text(
            0.5, 0.02,
            f"orange x = <{COVERAGE_THRESHOLD_PCT:.0f}% frame coverage vs original (run crashed mid-way) -- AP not directly comparable",
            ha="center", fontsize=8, color="#e8590c",
        )
    fig.tight_layout()

    out_dir.mkdir(parents=True, exist_ok=True)
    seq_stem = "allseq" if sequence == ALL_SEQUENCES else f"seq{sequence}"
    stem = f"radar_{seq_stem}_{cls}_{severity}"
    png_path = out_dir / f"{stem}.png"
    svg_path = out_dir / f"{stem}.svg"
    fig.savefig(png_path, dpi=150)
    fig.savefig(svg_path)
    plt.close(fig)
    return png_path


def build_all_charts(sequence: str, out_dir: Path) -> list[Path]:
    """Builds all 6 charts ({sed,bus} x {low,medium,high}) for one sequence.
    Same axis order and the same radial scale across a class's 3 severity
    charts (shared ylim per class) so low/medium/high are directly comparable
    side by side; sed and bus get independent scales since their AP
    magnitudes aren't expected to be comparable."""
    row_table = load_row_table(sequence)
    ap_by_cond_cls = compute_ap_by_condition_cls(row_table)
    coverage_by_condition = compute_condition_coverage(row_table)

    paths: list[Path] = []
    for cls in CLASSES:
        class_values = [v for (cond, c), v in ap_by_cond_cls.items() if c == cls]
        ylim = max(class_values) * 1.1 if class_values else 100.0
        for severity in SEVERITIES:
            paths.append(
                build_radar_chart(ap_by_cond_cls, coverage_by_condition, cls, severity, sequence, ylim, out_dir)
            )
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sequence", required=True, help="K-Radar sequence id, e.g. 46, or 'all' to pool every sequence"
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=FIGURES_DIR / "radar_charts",
        help="Directory to write PNG+SVG charts to",
    )
    args = parser.parse_args()
    paths = build_all_charts(args.sequence, args.out_dir)
    for p in paths:
        print(p)


if __name__ == "__main__":
    main()
