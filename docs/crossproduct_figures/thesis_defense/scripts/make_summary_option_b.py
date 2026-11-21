"""Slide 26/27 merge, Option B: two-panel split (Verdict | New vs Contested).
Bespoke PIL script, deck's existing table-figure convention (navy/accent-blue, Noto Sans).
"""
from PIL import Image, ImageDraw, ImageFont

NAVY = (25, 68, 97)
ACCENT = (42, 96, 153)
WHITE = (255, 255, 255)
PANEL_BG = (240, 244, 248)
BORDER = (200, 208, 216)
TEXT = (30, 30, 30)
BULLET = (42, 96, 153)

FONT_DIR = "/usr/share/fonts/noto/"
BOLD = FONT_DIR + "NotoSans-Bold.ttf"
REG = FONT_DIR + "NotoSans-Regular.ttf"


def f(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, font, max_width):
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textbbox((0, 0), trial, font=font)[2] <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    for line in lines:
        if draw.textbbox((0, 0), line, font=font)[2] > max_width:
            raise ValueError(f"Cell text does not fit column width even alone: {line!r}")
    return lines


def panel_content_height(draw, w, bullets, body_font):
    pad = 40
    line_h = draw.textbbox((0, 0), "Ag", font=body_font)[3] + 10
    bullet_gap = 22
    title_h = line_h + 30
    wrapped = [wrap(draw, b, body_font, w - 2 * pad - 30) for b in bullets]
    content_h = title_h + sum(len(lines) * line_h + bullet_gap for lines in wrapped)
    return content_h + pad


def draw_bulleted_panel(draw, x0, y0, w, panel_h, title, bullets, title_font, body_font, bg):
    pad = 40
    line_h = draw.textbbox((0, 0), "Ag", font=body_font)[3] + 10
    bullet_gap = 22
    title_h = line_h + 30
    wrapped = [wrap(draw, b, body_font, w - 2 * pad - 30) for b in bullets]

    draw.rectangle([x0, y0, x0 + w, y0 + panel_h], fill=bg, outline=BORDER, width=1)
    draw.text((x0 + pad, y0 + pad), title, font=title_font, fill=NAVY)
    y = y0 + pad + title_h
    bullet_r = 6
    for lines in wrapped:
        cy = y
        for j, line in enumerate(lines):
            if j == 0:
                draw.ellipse([x0 + pad, cy + 14, x0 + pad + 2 * bullet_r, cy + 14 + 2 * bullet_r], fill=BULLET)
            draw.text((x0 + pad + 30, cy), line, font=body_font, fill=TEXT)
            cy += line_h
        y = cy + bullet_gap
    return y0 + panel_h


PX_PER_CM = 126
CANVAS_W = int(25.4 * PX_PER_CM)
CANVAS_H = int(14.288 * PX_PER_CM)

img = Image.new("RGB", (CANVAS_W, CANVAS_H), WHITE)
draw = ImageDraw.Draw(img)

title_font = f(BOLD, 66)
body_font = f(REG, 50)

margin = 60
gap = 50
top = 40
panel_w = (CANVAS_W - 2 * margin - gap) // 2

left_bullets = [
    "T1: Robust to 17 of 22 conditions (within -8.8%); 5 collapse, frame deletion fails all 3",
    "T2: A noisy-but-present sensor is often worse than a fully absent one (LiDAR, radar)",
    "T3: Camera and radar degrade gracefully; LiDAR collapses abruptly instead",
]

right_bullets = [
    "New: degradation is driven by missed detections, not false positives, in 20/21 conditions",
    "Contested: ASF's broad claim of robustness to \"degradation or failure\" overstates what was tested",
]

h1 = panel_content_height(draw, panel_w, left_bullets, body_font)
h2 = panel_content_height(draw, panel_w, right_bullets, body_font)
panel_h = max(h1, h2)

y1 = draw_bulleted_panel(draw, margin, top, panel_w, panel_h, "Target Questions", left_bullets, title_font, body_font, PANEL_BG)
y2 = draw_bulleted_panel(draw, margin + panel_w + gap, top, panel_w, panel_h, "New vs. Contested", right_bullets, title_font, body_font, PANEL_BG)

final_h = max(y1, y2) + 20
img = img.crop((0, 0, CANVAS_W, final_h))
img.save("/home/adhish/Productivity/AMSCUP/docs/crossproduct_figures/thesis_defense/summary_option_b.png")
print("saved", img.size)
