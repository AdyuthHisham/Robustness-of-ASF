import sys
sys.path.insert(0, "/home/adhish/.claude/jobs/dae2301a/tmp/slide_figs")
import matplotlib.pyplot as plt
from palette import MODALITY_COLORS as COLORS
from _lib import CIRCLE_STYLES, MOD_RANGES

OUT = "/home/adhish/.claude/jobs/dae2301a/tmp/slide_figs"

# --- Table 5.3: spoke code key (verbatim from Results.tex tab:radar_spoke_key) ---
rows = [
    ("GL", "gaussian_noise, low"),
    ("GM", "gaussian_noise, medium"),
    ("GH", "gaussian_noise, high"),
    ("LL", "loss_partial, low"),
    ("LM", "loss_partial, medium"),
    ("LH", "loss_partial, high"),
    ("LC", "loss_complete_zero"),
]

fig, ax = plt.subplots(figsize=(7.5, 3.2))
ax.axis("off")
tbl = ax.table(
    cellText=[[c, e] for c, e in rows],
    colLabels=["Code", "Effect (at that severity)"],
    cellLoc="left",
    colLoc="left",
    loc="center",
)
tbl.auto_set_font_size(False)
tbl.set_fontsize(13)
tbl.scale(1, 2.0)
for (r, c), cell in tbl.get_celld().items():
    cell.set_edgecolor("#888888")
    if r == 0:
        cell.set_text_props(fontweight="bold")
        cell.set_facecolor("#e8e8e8")
fig.tight_layout()
fig.savefig(f"{OUT}/table_5_3_spoke_key.png", bbox_inches="tight", dpi=200)
plt.close(fig)
print("saved -> table_5_3_spoke_key.png")

# --- Fig 5.8 axis labels: modality names in their spoke color ---
mods = ["camera", "lidar", "radar"]
fig2, ax2 = plt.subplots(figsize=(4, 2.2))
ax2.axis("off")
for mi, mod in enumerate(mods):
    y = 0.75 - mi * 0.3
    ax2.text(0.5, y, mod.capitalize(), color=COLORS[mod], fontsize=22, fontweight="bold",
              va="center", ha="center")
ax2.set_xlim(0, 1)
ax2.set_ylim(0, 1)
fig2.tight_layout()
fig2.savefig(f"{OUT}/fig_5_8_spoke_labels.png", bbox_inches="tight", dpi=200)
plt.close(fig2)
print("saved -> fig_5_8_spoke_labels.png")

# --- standalone legend: worst/second-worst robustness rings + per-modality mean arc ---
legend_handles = [plt.Line2D([0], [0], color=c, linestyle="--", linewidth=lw, label=lbl)
                   for c, lw, lbl in CIRCLE_STYLES]
legend_handles += [plt.Rectangle((0, 0), 1, 1, facecolor=COLORS[mod], alpha=0.3,
                                  edgecolor=COLORS[mod], label=f"{mod.capitalize()} mean $R_b^c$ (arc)")
                    for mod in MOD_RANGES]

fig3 = plt.figure(figsize=(6, 2))
fig3.legend(handles=legend_handles, loc="center", ncol=2, fontsize=14,
            markerscale=1.8, handlelength=3.0, frameon=False)
fig3.savefig(f"{OUT}/radar_chart_legend.png", bbox_inches="tight", dpi=200)
plt.close(fig3)
print("saved -> radar_chart_legend.png")
