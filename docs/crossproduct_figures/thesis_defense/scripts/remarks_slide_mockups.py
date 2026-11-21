"""Three layout mockups for the Slide 23 "Remarks" concept — brainstorm
visuals only, not final/verified figures. Not data-derived (option C is an
illustrative placeholder standing in for a real cropped/annotated chart,
not the actual slide-22 numbers) — these exist to let the user pick a
direction before any real figure is built or any slide is touched.

Colors: deck navy #194461 / accent blue #2A6099 for chrome and headlines;
per-modality colors match the palette already used in a published thesis
figure (per docs/master_presentation_figures.md, FIG log entry citing the
upstream script's matplotlib hex codes): camera #1B7837 (green), lidar
#2166AC (blue), radar #B2182B (red) — reused as-is rather than the
bar_charts.py SENSOR_COLOR convention used in earlier mockups, since the
user asked for this specific blue/red/green scheme.
"""

from __future__ import annotations

NAVY = "#194461"
ACCENT = "#2A6099"
TEXT_TITLE = "#1A1A1A"
TEXT_SUB = "#6B7075"

LIDAR, LIDAR_D = "#2166AC", "#17497D"
RADAR, RADAR_D = "#B2182B", "#7E111E"
CAMERA, CAMERA_D = "#1B7837", "#124F25"

FONT = "DejaVu Sans"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=20, weight="normal", fill=TEXT_TITLE, anchor="start"):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-weight="{weight}" '
            f'font-size="{size}" fill="{fill}" text-anchor="{anchor}">{esc(s)}</text>')


def wrap_text(x, y, s, size, fill, anchor, line_h, max_chars):
    import textwrap
    lines = textwrap.wrap(s, max_chars)
    out = ""
    for i, ln in enumerate(lines):
        out += text(x, y + i * line_h, ln, size=size, fill=fill, anchor=anchor)
    return out, y + (len(lines) - 1) * line_h


# ---------------------------------------------------------------- Option A
def build_a() -> str:
    W, H = 2000, 700
    parts = [f'<rect width="{W}" height="{H}" fill="white"/>']

    parts.append(text(60, 60, "Impact when corrupted", size=22, weight="bold", fill=TEXT_SUB))

    bar_y = 130
    bar_x0, bar_x1 = 80, 1920
    parts.append(f'<line x1="{bar_x0}" y1="{bar_y}" x2="{bar_x1}" y2="{bar_y}" stroke="#D0D3D6" stroke-width="10"/>')
    parts.append(text(bar_x0, bar_y - 20, "High", size=18, fill=TEXT_SUB))
    parts.append(text(bar_x1, bar_y - 20, "Low", size=18, fill=TEXT_SUB, anchor="end"))

    modalities = [
        (300, LIDAR, LIDAR_D, "LiDAR", "localization-critical", 70),
        (1000, RADAR, RADAR_D, "Radar", "moderate reliance", 55),
        (1700, CAMERA, CAMERA_D, "Camera", "conditions-limited training", 40),
    ]
    for cx, fill, border, name, tag, r in modalities:
        parts.append(f'<circle cx="{cx}" cy="{bar_y}" r="{r}" fill="{fill}" stroke="{border}" stroke-width="4"/>')
        parts.append(text(cx, bar_y + r + 45, name, size=30, weight="bold", fill=TEXT_TITLE, anchor="middle"))
        parts.append(text(cx, bar_y + r + 78, tag, size=19, fill=TEXT_SUB, anchor="middle"))

    # two callout boxes
    def callout(x, headline, sub):
        w, h = 860, 150
        parts.append(f'<rect x="{x}" y="380" width="{w}" height="{h}" rx="14" fill="#F4F6F8" stroke="{ACCENT}" stroke-width="2"/>')
        parts.append(text(x + 30, 430, headline, size=26, weight="bold", fill=NAVY))
        sub_svg, _ = wrap_text(x + 30, 470, sub, 19, TEXT_SUB, "start", 26, 46)
        parts.append(sub_svg)

    callout(120, "Noise > Loss", "Noisy-but-present data isn't downweighted the way absent data implicitly is.")
    callout(1020, "Partial loss: well tolerated", "Consistent with the model being trained under adverse conditions.")

    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{"".join(parts)}</svg>'


ROWS = [
    (LIDAR, LIDAR_D, "LiDAR is the most critical sensor", 50,
     "Localizes objects; both noise and loss hit performance hardest."),
    (RADAR, RADAR_D, "Radar: intermediate reliance", 38,
     "Corruption hurts, but less severely than LiDAR, more than camera."),
    (CAMERA, CAMERA_D, "Camera corruption: little effect", 28,
     "Trained mainly on normal/overcast; likely already downweighted by fusion."),
]


def draw_rows(parts, right_edge, wrap_chars, row_h=170, top=30):
    for i, (fill, border, headline, radius, sub) in enumerate(ROWS):
        y0 = top + i * row_h
        cy = y0 + 60
        parts.append(f'<circle cx="90" cy="{cy}" r="{radius}" fill="{fill}" stroke="{border}" stroke-width="4"/>')
        parts.append(text(180, cy - 8, headline, size=30, weight="bold", fill=TEXT_TITLE))
        sub_svg, _ = wrap_text(180, cy + 28, sub, 19, TEXT_SUB, "start", 26, wrap_chars)
        parts.append(sub_svg)
        if i < 2:
            parts.append(f'<line x1="60" y1="{y0 + row_h - 15}" x2="{right_edge}" y2="{y0 + row_h - 15}" stroke="#E4E6E8" stroke-width="2"/>')
    box_y = top + 3 * row_h + 5
    parts.append(f'<rect x="60" y="{box_y}" width="{right_edge - 60}" height="120" rx="12" fill="#F4F6F8" stroke="{ACCENT}" stroke-width="2"/>')
    parts.append(text(90, box_y + 45, "Partial loss is well tolerated", size=24, weight="bold", fill=NAVY))
    parts.append(text(90, box_y + 82, "Consistent with training under adverse conditions.", size=20, fill=TEXT_SUB))
    return box_y + 120


# ---------------------------------------------------------------- Option B
def build_b() -> str:
    W, H = 2000, 780
    parts = [f'<rect width="{W}" height="{H}" fill="white"/>']
    draw_rows(parts, W - 60, wrap_chars=80)
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{"".join(parts)}</svg>'


def mockup_flag(parts, x, y):
    parts.append(text(x, y, "MOCKUP — illustrative values, not real numbers", size=16, fill="#B23A3A"))


# ------------------------------------------------- Option B + paired bars
def build_b_bar() -> str:
    W, H = 2200, 780
    parts = [f'<rect width="{W}" height="{H}" fill="white"/>']
    left_edge = 1150
    draw_rows(parts, left_edge, wrap_chars=44)

    gx0, gy0, gy1 = left_edge + 90, 150, 560
    gx1 = W - 60
    parts.append(text(gx0, 90, "LiDAR: noise costs far more retention than complete loss", size=20, weight="bold", fill=NAVY))
    parts.append(f'<line x1="{gx0}" y1="{gy1}" x2="{gx1}" y2="{gy1}" stroke="{TEXT_TITLE}" stroke-width="3"/>')

    # Real values: AP-restricted-range retention, pooled per condition (N=58
    # sequences, all reliable), computed from full_denormalized_table_22cond_weather_corrected.parquet
    # (the freshest canonical table, 2026-09-23) via crossproduct.py's own
    # build_summary/add_baseline_deltas -- not the stale deltas_condition.parquet
    # cached under crossproduct_v2 (built 2026-09-01, predates the weather
    # correction). NOTE: LiDAR's loss_complete_zero retention here (0.578)
    # differs from findings.md's Q6 entry (0.4996), which used the stale table.
    groups = [("LiDAR", LIDAR, 0.578, 0.296), ("Radar", RADAR, 0.916, 0.741), ("Camera", CAMERA, 0.980, 0.976)]
    group_w = (gx1 - gx0) / 3
    bar_w = 48
    max_h = gy1 - gy0
    for i, (name, color, loss_val, noise_val) in enumerate(groups):
        gcx = gx0 + group_w * (i + 0.5)
        for j, (label, val, shade) in enumerate([("Loss", loss_val, 0.55), ("Noise", noise_val, 1.0)]):
            bx = gcx - bar_w - 6 + j * (bar_w + 12)
            bh = val * max_h
            by = gy1 - bh
            opacity = shade
            parts.append(f'<rect x="{bx}" y="{by}" width="{bar_w}" height="{bh}" fill="{color}" fill-opacity="{opacity}"/>')
            parts.append(text(bx + bar_w / 2, gy1 + 24, label, size=15, fill=TEXT_SUB, anchor="middle"))
        parts.append(text(gcx, gy1 + 56, name, size=20, weight="bold", fill=TEXT_TITLE, anchor="middle"))

    parts.append(text((gx0 + gx1) / 2, gy1 + 92, "Retention under corruption", size=19, fill=TEXT_SUB, anchor="middle"))
    parts.append(text(gx0, gy1 + 130, "N = 58 sequences per condition, all reliable. AP-restricted-range retention, high severity.", size=14, fill=TEXT_SUB))

    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{"".join(parts)}</svg>'


# ------------------------------------------------ Option B + slope chart
def build_b_slope() -> str:
    W, H = 2200, 780
    parts = [f'<rect width="{W}" height="{H}" fill="white"/>']
    left_edge = 1150
    draw_rows(parts, left_edge, wrap_chars=44)

    gx0, gy0, gy1 = left_edge + 200, 180, 540
    gx1 = W - 140
    mockup_flag(parts, left_edge + 90, 30)

    parts.append(text(gx0, gy0 - 60, "Complete Loss", size=19, weight="bold", fill=TEXT_SUB, anchor="middle"))
    parts.append(text(gx1, gy0 - 60, "Noise (high)", size=19, weight="bold", fill=TEXT_SUB, anchor="middle"))

    groups = [("LiDAR", LIDAR, 0.90, 0.14, 22), ("Radar", RADAR, 0.92, 0.46, 0), ("Camera", CAMERA, 0.99, 0.97, -22)]
    for name, color, loss_val, noise_val, label_dy in groups:
        y_loss = gy1 - loss_val * (gy1 - gy0)
        y_noise = gy1 - noise_val * (gy1 - gy0)
        parts.append(f'<line x1="{gx0}" y1="{y_loss}" x2="{gx1}" y2="{y_noise}" stroke="{color}" stroke-width="5"/>')
        parts.append(f'<circle cx="{gx0}" cy="{y_loss}" r="9" fill="{color}"/>')
        parts.append(f'<circle cx="{gx1}" cy="{y_noise}" r="9" fill="{color}"/>')
        parts.append(text(gx0 - 24, y_loss + 6 + label_dy, name, size=18, weight="bold", fill=color, anchor="end"))

    parts.append(text((gx0 + gx1) / 2, gy1 + 60, "LiDAR drops the most going from loss to noise", size=18, weight="bold", fill=NAVY, anchor="middle"))

    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{"".join(parts)}</svg>'


# ------------------------------------------------- Option B + icon panel
def build_b_icon() -> str:
    W, H = 2200, 780
    parts = [f'<rect width="{W}" height="{H}" fill="white"/>']
    left_edge = 1150
    draw_rows(parts, left_edge, wrap_chars=44)

    cx = left_edge + (W - left_edge) / 2
    mockup_flag(parts, left_edge + 90, 40)

    # noisy-but-present icon (static-filled circle)
    y1 = 220
    parts.append(f'<circle cx="{cx - 220}" cy="{y1}" r="70" fill="{LIDAR}" fill-opacity="0.35" stroke="{LIDAR}" stroke-width="4" stroke-dasharray="6,5"/>')
    parts.append(text(cx - 220, y1 + 8, "?", size=48, weight="bold", fill=LIDAR, anchor="middle"))
    parts.append(text(cx - 220, y1 + 120, "Noisy but present", size=20, weight="bold", fill=TEXT_TITLE, anchor="middle"))
    parts.append(text(cx - 220, y1 + 150, "retention: 14%", size=18, fill=TEXT_SUB, anchor="middle"))

    parts.append(text(cx, y1 + 20, "vs", size=26, fill=TEXT_SUB, anchor="middle"))

    # complete loss icon (empty dashed outline)
    parts.append(f'<circle cx="{cx + 220}" cy="{y1}" r="70" fill="white" stroke="{TEXT_SUB}" stroke-width="4" stroke-dasharray="10,6"/>')
    parts.append(text(cx + 220, y1 + 120, "Completely absent", size=20, weight="bold", fill=TEXT_TITLE, anchor="middle"))
    parts.append(text(cx + 220, y1 + 150, "retention: 90%", size=18, fill=TEXT_SUB, anchor="middle"))

    parts.append(text(cx, y1 + 260, "For LiDAR, present-but-wrong data hurts far", size=20, weight="bold", fill=NAVY, anchor="middle"))
    parts.append(text(cx, y1 + 292, "more than data that's simply missing.", size=20, weight="bold", fill=NAVY, anchor="middle"))

    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{"".join(parts)}</svg>'


# ---------------------------------------------------------------- Option C
def build_c() -> str:
    """Illustrative placeholder only — stands in for a real cropped/annotated
    chart from slide 22; the trend shapes here are NOT real numbers."""
    W, H = 2000, 800
    parts = [f'<rect width="{W}" height="{H}" fill="white"/>']
    parts.append(text(W / 2, 40, "MOCKUP — illustrative shapes only, not real data", size=18, fill="#B23A3A", anchor="middle"))

    # axes
    ax_x0, ax_y0, ax_x1, ax_y1 = 140, 650, 1860, 120
    parts.append(f'<line x1="{ax_x0}" y1="{ax_y0}" x2="{ax_x1}" y2="{ax_y0}" stroke="{TEXT_TITLE}" stroke-width="3"/>')
    parts.append(f'<line x1="{ax_x0}" y1="{ax_y0}" x2="{ax_x0}" y2="{ax_y1}" stroke="{TEXT_TITLE}" stroke-width="3"/>')
    parts.append(text((ax_x0 + ax_x1) / 2, 700, "Severity", size=20, fill=TEXT_SUB, anchor="middle"))
    parts.append(text(60, (ax_y0 + ax_y1) / 2, "Retention", size=20, fill=TEXT_SUB, anchor="middle") .replace('text-anchor="middle">', 'text-anchor="middle" transform="rotate(-90 60 385)">'))

    def line(pts, color, label):
        d = "M " + " L ".join(f"{x},{y}" for x, y in pts)
        return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="5"/>'

    xs = [ax_x0 + i * (ax_x1 - ax_x0) / 4 for i in range(5)]
    lidar_ys = [220, 260, 340, 480, 610]
    radar_ys = [220, 240, 280, 330, 380]
    camera_ys = [220, 225, 228, 232, 235]

    parts.append(line(list(zip(xs, lidar_ys)), LIDAR, "LiDAR"))
    parts.append(line(list(zip(xs, radar_ys)), RADAR, "Radar"))
    parts.append(line(list(zip(xs, camera_ys)), CAMERA, "Camera"))

    # callouts
    def callout(px, py, dx, dy, label):
        tx, ty = px + dx, py + dy
        return (f'<line x1="{px}" y1="{py}" x2="{tx}" y2="{ty}" stroke="{TEXT_TITLE}" stroke-width="2"/>'
                f'<circle cx="{px}" cy="{py}" r="7" fill="{TEXT_TITLE}"/>'
                + text(tx + (10 if dx >= 0 else -10), ty, label, size=20, weight="bold", fill=TEXT_TITLE, anchor=("start" if dx >= 0 else "end")))

    parts.append(callout(xs[4], lidar_ys[4], -280, -20, "LiDAR noise: sharpest drop"))
    parts.append(callout(xs[4], camera_ys[4], -320, -50, "Camera: flat, likely downweighted"))
    parts.append(callout(xs[1], radar_ys[1] - 5, -120, -90, "Partial loss: minimal decrease"))

    # legend
    leg_x, leg_y = ax_x1 - 260, 150
    for i, (c, name) in enumerate([(LIDAR, "LiDAR"), (RADAR, "Radar"), (CAMERA, "Camera")]):
        yy = leg_y + i * 34
        parts.append(f'<rect x="{leg_x}" y="{yy - 14}" width="26" height="10" fill="{c}"/>')
        parts.append(text(leg_x + 36, yy - 4, name, size=20, fill=TEXT_TITLE))

    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{"".join(parts)}</svg>'


if __name__ == "__main__":
    out_dir = "/home/adhish/Productivity/AMSCUP/docs/crossproduct_figures/thesis_defense"
    variants = [
        ("remarks_option_a", build_a),
        ("remarks_option_b", build_b),
        ("remarks_option_c", build_c),
        ("remarks_option_b_bar", build_b_bar),
        ("remarks_option_b_slope", build_b_slope),
        ("remarks_option_b_icon", build_b_icon),
    ]
    for name, fn in variants:
        with open(f"{out_dir}/{name}.svg", "w") as f:
            f.write(fn())
    print("wrote", ", ".join(n for n, _ in variants))
