import sys
sys.path.insert(0, "/home/adhish/.claude/jobs/dae2301a/tmp/slide_figs")
import matplotlib.pyplot as plt
import numpy as np
from _lib import compute_axis, AXES, SPOKES, COLORS, MOD_RANGES, CIRCLE_STYLES

OUT = "/home/adhish/.claude/jobs/dae2301a/tmp/slide_figs"


def make_single_panel(cls, cat, label, values, out_stem, axis_name):
    angles = np.linspace(0, 2 * np.pi, len(SPOKES), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(9, 9), subplot_kw={"projection": "polar"})
    vals = values[cls][cat]
    vals_closed = vals + vals[:1]
    tick_colors = [COLORS[mod] for mod, _, _ in SPOKES]
    from _lib import spoke_label
    tick_labels = [spoke_label(*s) for s in SPOKES]

    for mod, (start, end) in MOD_RANGES.items():
        mod_vals = [v for v in vals[start:end + 1] if np.isfinite(v)]
        if not mod_vals:
            continue
        mean_val = float(np.mean(mod_vals))
        theta = np.linspace(angles[start], angles[end], 30)
        ax.fill_between(theta, 0, mean_val, color=COLORS[mod], alpha=0.15, zorder=0.5)
        ax.plot(theta, [mean_val] * len(theta), color=COLORS[mod], linewidth=1.5, alpha=0.7, zorder=1.3)

    ax.plot(angles, vals_closed, color="#333333", linewidth=1.8, zorder=2)
    ax.fill(angles, vals_closed, color="#333333", alpha=0.12, zorder=1)

    finite_idx = [i for i, v in enumerate(vals) if np.isfinite(v)]
    ranked = sorted(finite_idx, key=lambda i: vals[i])
    picks = [i for i in (ranked[0] if ranked else None,
                          ranked[1] if len(ranked) > 1 else None) if i is not None]
    circle_angles = np.linspace(0, 2 * np.pi, 200)
    min_idx = picks[0] if picks else None
    for rank, i in enumerate(picks):
        color, lw, _ = CIRCLE_STYLES[rank]
        ax.plot(circle_angles, [vals[i]] * len(circle_angles), color=color,
                linestyle="--", linewidth=lw, zorder=1.5)
        ax.plot(angles[i], vals[i], marker="o", markersize=9,
                markerfacecolor="none", markeredgecolor=color, markeredgewidth=2.4, zorder=3)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(tick_labels, fontsize=15)
    for i, (tick, color) in enumerate(zip(ax.get_xticklabels(), tick_colors)):
        tick.set_color(color)
        if i == min_idx:
            tick.set_fontweight("bold")
    ax.set_ylim(0, 1.15)
    ax.set_yticks([0.0, 0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["0", ".25", ".5", ".75", "1"], fontsize=11)
    rlabel_angle = np.radians(ax.get_rlabel_position())
    ax.text(rlabel_angle, 1.30, "$R_b^c$", fontsize=13, ha="center", va="center", color="0.25")

    cls_name = "Sedan" if cls == "sed" else "Bus"
    title = f"{axis_name} - {label}  ({cls_name})"
    ax.set_title(title, fontsize=18, fontweight="bold", pad=34)

    fig.tight_layout()
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    fig.savefig(f"{OUT}/{out_stem}.png", bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig)
    print("saved ->", f"{OUT}/{out_stem}.png")


REQUESTS = [
    # (axis_key, cls, category, out_stem, axis_display_name)
    ("weather", "sed", "normal", "sedan_weather_normal", "Weather"),
    ("time_of_day", "sed", "day", "sedan_time_day", "Time of Day"),
    ("time_of_day", "sed", "night", "sedan_time_night", "Time of Day"),
    ("environment", "sed", "highway", "sedan_env_highway", "Environment"),
    ("weather", "bus", "normal", "bus_weather_normal", "Weather"),
    ("environment", "bus", "highway", "bus_env_highway", "Environment"),
]

# compute each axis's values once
axis_values_cache = {}
for axis_key, cls, cat, out_stem, axis_name in REQUESTS:
    if axis_key not in axis_values_cache:
        col, categories, labels, stem = AXES[axis_key]
        axis_values_cache[axis_key] = (compute_axis(col, categories), labels)
    values, labels = axis_values_cache[axis_key]
    make_single_panel(cls, cat, labels[cat], values, out_stem, axis_name)
