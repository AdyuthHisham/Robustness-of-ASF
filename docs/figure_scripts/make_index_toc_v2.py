"""Slide 5 "Index" TOC figure, v2 -- single-column 5-item rewrite.

Copied from make_index_toc.py (not overwritten, per instruction to never
overwrite an old agent's script) and adapted: original was a 2-column,
14-item layout; this is a single-column, 5-item layout matching the new
agenda the user gave. Same style (accent blue circles/connectors, navy
labels, tapered vesica connectors) and canvas aspect (2.34:1) as the
original, to match the existing slide-5 image frame (20.5cm x 8.761cm).
"""

from PIL import Image, ImageDraw, ImageFont
import math

W, H = 2340, 1000

img = Image.new('RGBA', (W, H), (255, 255, 255, 0))
d = ImageDraw.Draw(img)

ACCENT = (42, 96, 153)     # #2a6099
DARK = (25, 68, 97)        # #194461
WHITE = (255, 255, 255)

FONT_DIR = "/usr/share/fonts/noto/"
num_font = ImageFont.truetype(FONT_DIR + "NotoSans-Bold.ttf", 58)
label_font = ImageFont.truetype(FONT_DIR + "NotoSans-Bold.ttf", 48)

items = [
    "Target",
    "Robustness Analysis Methodology",
    "Dataset, Model, Metrics & Corruptions",
    "Robustness Analysis of ASF",
    "Summary of Robustness Analysis",
]

rows = len(items)
R = 68
top_margin = 90
bottom_margin = 90
first_c = top_margin + R
last_c = H - bottom_margin - R
row_gap = (last_c - first_c) / (rows - 1)

cx = 300
label_x_offset = R + 50


def connector(cx, y0, y1, r, dy_from_center):
    hw_edge = math.sqrt(max(r * r - dy_from_center * dy_from_center, 1))
    pinch_min = 0.55
    steps = 40
    left_pts = []
    right_pts = []
    for i in range(steps + 1):
        t = i / steps
        y = y0 + (y1 - y0) * t
        pinch = pinch_min + (1 - pinch_min) * ((2 * abs(t - 0.5)) ** 2)
        hw = hw_edge * pinch
        left_pts.append((cx - hw, y))
        right_pts.append((cx + hw, y))
    poly = left_pts + right_pts[::-1]
    d.polygon(poly, fill=ACCENT)


centers = [first_c + i * row_gap for i in range(rows)]

for i in range(rows - 1):
    dy = R * 0.55
    connector(cx, centers[i] + dy, centers[i + 1] - dy, R, dy)

for i, cy in enumerate(centers):
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=ACCENT)
    num = f"{i + 1:02d}"
    bbox = d.textbbox((0, 0), num, font=num_font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text((cx - tw / 2 - bbox[0], cy - th / 2 - bbox[1]), num, font=num_font, fill=WHITE)
    label = items[i]
    lbbox = d.textbbox((0, 0), label, font=label_font)
    lh = lbbox[3] - lbbox[1]
    d.text((cx + label_x_offset, cy - lh / 2 - lbbox[1]), label, font=label_font, fill=DARK)

out_path = "/home/adhish/Productivity/AMSCUP/docs/crossproduct_figures/thesis_defense/index_toc_v2.png"
img.save(out_path)
print("saved", img.size, "->", out_path)
