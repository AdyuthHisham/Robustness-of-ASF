"""Slide 26/27 merge, Option A: verdict stat-strip + 3-column claims table.
Bespoke PIL script, deck's existing table-figure convention (navy/accent-blue, Noto Sans).
Canvas sized to the deck's actual slide dimensions (25.4cm x 14.288cm, 16:9), 126px/cm.
"""
from PIL import Image, ImageDraw, ImageFont

NAVY = (25, 68, 97)
ACCENT = (42, 96, 153)
WHITE = (255, 255, 255)
ROW_ALT = (240, 244, 248)
BORDER = (200, 208, 216)
TEXT = (30, 30, 30)
WARN = (176, 58, 46)      # for the collapse/severity numbers
STAT_BG = (235, 241, 247)

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


PX_PER_CM = 126
CANVAS_W = int(25.4 * PX_PER_CM)
CANVAS_H = int(14.288 * PX_PER_CM)

img = Image.new("RGB", (CANVAS_W, CANVAS_H), WHITE)
draw = ImageDraw.Draw(img)

num_font = f(BOLD, 68)
stat_label_font = f(REG, 30)
header_font = f(BOLD, 36)
body_font = f(REG, 30)

margin = 60
top = 40

# --- Stat strip: 3 callout boxes ---
stat_gap = 40
stat_w = (CANVAS_W - 2 * margin - 2 * stat_gap) // 3
stat_h = 260

stats = [
    ("17 / 22", "conditions stayed within -8.8% of baseline", NAVY),
    ("-74.9% to -76.4%", "LiDAR Gaussian-noise collapse", WARN),
    ("3 / 3 modalities", "fail outright under frame deletion", WARN),
]

for i, (num, label, color) in enumerate(stats):
    x0 = margin + i * (stat_w + stat_gap)
    draw.rectangle([x0, top, x0 + stat_w, top + stat_h], fill=STAT_BG, outline=BORDER, width=1)
    num_lines = wrap(draw, num, num_font, stat_w - 40)
    ny = top + 30
    for line in num_lines:
        w = draw.textbbox((0, 0), line, font=num_font)[2]
        draw.text((x0 + (stat_w - w) / 2, ny), line, font=num_font, fill=color)
        ny += draw.textbbox((0, 0), "Ag", font=num_font)[3] + 6
    label_lines = wrap(draw, label, stat_label_font, stat_w - 40)
    ly = ny + 10
    for line in label_lines:
        w = draw.textbbox((0, 0), line, font=stat_label_font)[2]
        draw.text((x0 + (stat_w - w) / 2, ly), line, font=stat_label_font, fill=TEXT)
        ly += draw.textbbox((0, 0), "Ag", font=stat_label_font)[3] + 4

# --- 3-column claims table ---
table_top = top + stat_h + 40
col_w = (CANVAS_W - 2 * margin) // 3
headers = ["Reinforced", "New Findings", "Contested"]
cells = [
    "LiDAR costliest to lose, camera least, confirmed even more sharply than ASF's own ablation",
    "A noisy-but-present sensor is often worse than a fully absent one (LiDAR, radar)",
    "ASF's broad claim of robustness to \"degradation or failure\" is not fully supported",
]

ROW_PAD = 22
LINE_GAP = 8

x_positions = [margin + i * col_w for i in range(4)]
header_h = 70

# headers
for i, h in enumerate(headers):
    draw.rectangle([x_positions[i], table_top, x_positions[i + 1], table_top + header_h], fill=ACCENT)
    w = draw.textbbox((0, 0), h, font=header_font)[2]
    draw.text((x_positions[i] + (col_w - w) / 2, table_top + 16), h, font=header_font, fill=WHITE)

# body cells (single row, height = max wrapped height)
wrapped = []
for i, c in enumerate(cells):
    lines = wrap(draw, c, body_font, col_w - 2 * ROW_PAD)
    wrapped.append(lines)
line_h = draw.textbbox((0, 0), "Ag", font=body_font)[3] + LINE_GAP
max_lines = max(len(w) for w in wrapped)
body_h = max_lines * line_h + 2 * ROW_PAD

body_top = table_top + header_h
draw.rectangle([margin, body_top, margin + 3 * col_w, body_top + body_h], fill=ROW_ALT)
for i, lines in enumerate(wrapped):
    cy = body_top + ROW_PAD
    for line in lines:
        draw.text((x_positions[i] + ROW_PAD, cy), line, font=body_font, fill=TEXT)
        cy += line_h

# grid lines
for xp in x_positions:
    draw.line([xp, table_top, xp, body_top + body_h], fill=BORDER, width=1)
draw.line([margin, table_top + header_h, margin + 3 * col_w, table_top + header_h], fill=BORDER, width=1)
draw.line([margin, body_top + body_h, margin + 3 * col_w, body_top + body_h], fill=BORDER, width=1)

final_h = body_top + body_h + 20
img = img.crop((0, 0, CANVAS_W, final_h))
img.save("/home/adhish/Productivity/AMSCUP/docs/crossproduct_figures/thesis_defense/summary_option_a.png")
print("saved", img.size)
