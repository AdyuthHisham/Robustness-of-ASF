"""Emit the LaTeX tables backing the 10 radar charts (Figures 5.3-5.12) in
Results.tex -- same R_b^c values, same 21 spokes, same N>30-floor stratum
drop as generate_corruption_radar.py, just as a table instead of a polygon.

Run: uv run --project test-bed python docs/crossproduct_figures/generate_corruption_radar_tables.py
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from generate_corruption_radar import AXES, SPOKES, compute_axis, spoke_label  # noqa: E402

OUT = Path(__file__).parent / "radar_tables.tex"

FIG_LABEL = {
    "weather": ("fig:weather_corruption_lines_sedan", "fig:weather_corruption_lines_bus", "weather"),
    "environment": ("fig:environment_corruption_lines_sedan", "fig:environment_corruption_lines_bus", "environment"),
    "time_of_day": ("fig:tod_corruption_lines_sedan", "fig:tod_corruption_lines_bus", "time of day"),
    "distance_bucket": ("fig:distance_corruption_lines_sedan", "fig:distance_corruption_lines_bus", "distance from ego"),
    "frame_density": ("fig:density_corruption_lines_sedan", "fig:density_corruption_lines_bus", "frame point-density"),
}
CLASS_LABEL = {"sed": "Sedan", "bus": "Bus/truck"}


def fmt(v: float) -> str:
    return "--" if not np.isfinite(v) else f"{v:.3f}"


def make_table(axis_key: str, cls: str, categories: list[str], labels: dict[str, str],
               values, fig_label: str, axis_title: str) -> str:
    cats = [c for c in categories if any(np.isfinite(v) for v in values[cls][c])]
    ncols = len(cats)
    colspec = "l" + "r" * ncols
    header = " & ".join(["\\textbf{Condition}"] + [f"\\textbf{{{labels[c]}}}" for c in cats])
    rows = []
    for i, spoke in enumerate(SPOKES):
        row_vals = [fmt(values[cls][c][i]) for c in cats]
        rows.append("\\texttt{" + spoke_label(*spoke).replace("_", "\\_") + "} & " + " & ".join(row_vals) + " \\\\")
    body = "\n".join(rows)
    label = fig_label.replace("fig:", "tab:") + "_data"
    caption = (f"Underlying $R_b^c$ values for Figure~\\ref{{{fig_label}}} "
               f"({CLASS_LABEL[cls]} -- {axis_title}); \\texttt{{--}} marks a cell below the "
               f"$N>30$ reliability floor.")
    return (
        "\\begin{table}[H]\n\\centering\n\\footnotesize\n"
        f"\\caption{{{caption}}}\n\\label{{{label}}}\n"
        f"\\resizebox{{\\linewidth}}{{!}}{{%\n\\begin{{tabular}}{{{colspec}}}\n"
        f"\\hline\\hline\n{header} \\\\ \\hline\n{body}\n\\hline\\hline\n"
        "\\end{tabular}%\n}\n\\end{table}\n"
    )


tables = []
for axis_key, (col, categories, labels, _stem) in AXES.items():
    values = compute_axis(col, categories)
    fig_sedan, fig_bus, axis_title = FIG_LABEL[axis_key]
    tables.append(make_table(axis_key, "sed", categories, labels, values, fig_sedan, axis_title))
    tables.append(make_table(axis_key, "bus", categories, labels, values, fig_bus, axis_title))

OUT.write_text("\n".join(tables))
print("saved ->", OUT)
