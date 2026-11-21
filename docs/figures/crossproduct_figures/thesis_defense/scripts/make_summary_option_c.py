"""Slide 26/27 merge, Option C: icon-row diagram with per-sensor verdict badges + headline.
Bespoke PIL script, deck's existing table-figure convention (navy/accent-blue, Noto Sans).
Icons are simple PIL primitives (no external assets/icon library used).
"""
from PIL import Image, ImageDraw, ImageFont

NAVY = (25, 68, 97)
ACCENT = (42, 96, 153)
WHITE = (255, 255, 255)
GOOD = (46, 125, 80)
WARN_Y = (191, 143, 0)
WARN_R = (176, 58, 46)
BORDER = (200, 208, 216)
TEXT = (30, 30, 30)
CARD_BG = (240, 244, 248)

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


def draw_camera_icon(draw, cx, cy, s, color):
    draw.rounded_rectangle([cx - s, cy - s * 0.6, cx + s, cy + s * 0.6], radius=s * 0.15, outline=color, width=6)
    draw.rectangle([cx - s * 0.35, cy - s * 0.85, cx + s * 0.1, cy - s * 0.6], fill=color)
    draw.ellipse([cx - s * 0.4, cy - s * 0.35, cx + s * 0.4, cy + s * 0.35], outline=color, width=6)


def draw_radar_icon(draw, cx, cy, s, color):
    for r in (s * 0.35, s * 0.65, s * 0.95):
        draw.arc([cx - r, cy - r, cx + r, cy + r], start=210, end=330, fill=color, width=6)
    draw.ellipse([cx - s * 0.08, cy - s * 0.08, cx + s * 0.08, cy + s * 0.08], fill=color)


def draw_lidar_icon(draw, cx, cy, s, color):
    draw.ellipse([cx - s * 0.5, cy + s * 0.4, cx + s * 0.5, cy + s * 0.65], outline=color, width=6)
    draw.rectangle([cx - s * 0.5, cy - s * 0.1, cx - s * 0.5 + 6, cy + s * 0.5], fill=color)
    draw.rectangle([cx + s * 0.5 - 6, cy - s * 0.1, cx + s * 0.5, cy + s * 0.5], fill=color)
    for dx in (-1, 0, 1):
        draw.line([cx + dx * s * 0.3, cy - s * 0.1, cx + dx * s * 0.3, cy - s * 0.9], fill=color, width=6)


PX_PER_CM = 126
CANVAS_W = int(25.4 * PX_PER_CM)
CANVAS_H = int(14.288 * PX_PER_CM)

img = Image.new("RGB", (CANVAS_W, CANVAS_H), WHITE)
draw = ImageDraw.Draw(img)

badge_font = f(BOLD, 32)
label_font = f(BOLD, 40)
detail_font = f(REG, 28)
headline_font = f(BOLD, 38)

margin = 80
gap = 60
top = 60
card_w = (CANVAS_W - 2 * margin - 2 * gap) // 3
card_h = 620
icon_size = 120

cards = [
    ("Camera", draw_camera_icon, GOOD, "Graceful", "Negligible impact at every severity tested"),
    ("Radar", draw_radar_icon, WARN_Y, "Noisy > Absent", "-14.9% to -22.7% under noise vs. less under total loss"),
    ("LiDAR", draw_lidar_icon, WARN_R, "Collapses", "-74.9% to -76.4% under Gaussian noise"),
]

for i, (name, icon_fn, color, badge, detail) in enumerate(cards):
    x0 = margin + i * (card_w + gap)
    draw.rounded_rectangle([x0, top, x0 + card_w, top + card_h], radius=20, fill=CARD_BG, outline=BORDER, width=1)
    icon_fn(draw, x0 + card_w / 2, top + 150, icon_size, NAVY)
    name_w = draw.textbbox((0, 0), name, font=label_font)[2]
    draw.text((x0 + (card_w - name_w) / 2, top + 300), name, font=label_font, fill=NAVY)
    badge_w = draw.textbbox((0, 0), badge, font=badge_font)[2]
    bpad = 24
    bx0 = x0 + (card_w - badge_w - 2 * bpad) / 2
    by0 = top + 370
    draw.rounded_rectangle([bx0, by0, bx0 + badge_w + 2 * bpad, by0 + 60], radius=30, fill=color)
    draw.text((bx0 + bpad, by0 + 12), badge, font=badge_font, fill=WHITE)
    detail_lines = wrap(draw, detail, detail_font, card_w - 60)
    dy = by0 + 90
    for line in detail_lines:
        w = draw.textbbox((0, 0), line, font=detail_font)[2]
        draw.text((x0 + (card_w - w) / 2, dy), line, font=detail_font, fill=TEXT)
        dy += draw.textbbox((0, 0), "Ag", font=detail_font)[3] + 6

headline = "Claims hold within the tested scope; a noisy-but-present sensor is the untested exception"
headline_top = top + card_h + 50
h_lines = wrap(draw, headline, headline_font, CANVAS_W - 2 * margin)
hy = headline_top
for line in h_lines:
    w = draw.textbbox((0, 0), line, font=headline_font)[2]
    draw.text(((CANVAS_W - w) / 2, hy), line, font=headline_font, fill=NAVY)
    hy += draw.textbbox((0, 0), "Ag", font=headline_font)[3] + 10

final_h = hy + 30
img = img.crop((0, 0, CANVAS_W, final_h))
img.save("/home/adhish/Productivity/AMSCUP/docs/crossproduct_figures/thesis_defense/summary_option_c.png")
print("saved", img.size)
