"""Slide 8 (Dataset and Model): two side-by-side reference tables, Datasets and Models.
Bespoke PIL script, following the deck's existing ad hoc table-figure convention
(navy/accent-blue palette, Noto Sans) -- see docs/master_presentation_figures.md
FIG-...-metrics-primer-table entry for style rationale.

Row heights are synced across both tables (row heights = max of the two tables'
wrapped-text heights at that row index) so the two tables end at the same
baseline and there's no dead space under the shorter one.
"""
from PIL import Image, ImageDraw, ImageFont

NAVY = (25, 68, 97)          # #194461 header/label text
ACCENT = (42, 96, 153)       # #2a6099 header band
WHITE = (255, 255, 255)
ROW_ALT = (240, 244, 248)
BORDER = (200, 208, 216)
TEXT = (30, 30, 30)

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
    # Safety: a single word wider than max_width (e.g. an unbroken slash-joined
    # token) would otherwise silently overflow the column and get clipped.
    for line in lines:
        if draw.textbbox((0, 0), line, font=font)[2] > max_width:
            raise ValueError(f"Cell text does not fit column width even alone: {line!r}")
    return lines


def wrap_table(draw, col_widths, rows, header_font, label_font, body_font, row_pad):
    """Returns (wrapped_rows, row_heights) -- wrapped_rows[r] = [(lines, font), ...] per cell."""
    wrapped_rows = []
    row_heights = []
    for r_idx, row in enumerate(rows):
        wrapped_cells = []
        for c_idx, cell in enumerate(row):
            cw = col_widths[c_idx] - 2 * row_pad
            fnt = header_font if r_idx == 0 else (label_font if c_idx == 0 else body_font)
            lines = wrap(draw, cell, fnt, cw)
            wrapped_cells.append((lines, fnt))
        wrapped_rows.append(wrapped_cells)
        max_lines = max(len(c[0]) for c in wrapped_cells)
        line_h = draw.textbbox((0, 0), "Ag", font=wrapped_cells[0][1])[3] + LINE_GAP
        row_heights.append(max_lines * line_h + 2 * row_pad)
    return wrapped_rows, row_heights


def draw_table(draw, x0, y0, col_widths, wrapped_rows, row_heights, row_pad):
    x_positions = [x0]
    for w in col_widths:
        x_positions.append(x_positions[-1] + w)
    total_w = x_positions[-1] - x0

    y = y0
    row_tops = [y]
    for r_idx, wrapped_cells in enumerate(wrapped_rows):
        row_h = row_heights[r_idx]
        bg = ACCENT if r_idx == 0 else (ROW_ALT if r_idx % 2 == 0 else WHITE)
        draw.rectangle([x0, y, x0 + total_w, y + row_h], fill=bg)
        for c_idx, (lines, fnt) in enumerate(wrapped_cells):
            cx = x_positions[c_idx] + row_pad
            cy = y + row_pad
            color = WHITE if r_idx == 0 else (NAVY if c_idx == 0 else TEXT)
            line_h = draw.textbbox((0, 0), "Ag", font=fnt)[3] + LINE_GAP
            for line in lines:
                draw.text((cx, cy), line, font=fnt, fill=color)
                cy += line_h
        y += row_h
        row_tops.append(y)

    for xp in x_positions:
        draw.line([xp, y0, xp, y], fill=BORDER, width=1)
    for yp in row_tops:
        draw.line([x0, yp, x0 + total_w, yp], fill=BORDER, width=1)

    return y


LINE_GAP = 8
ROW_PAD = 18

CANVAS_W = 3200
img = Image.new("RGB", (CANVAS_W, 10), WHITE)  # placeholder height, cropped at the end
draw = ImageDraw.Draw(img)

title_font = f(BOLD, 60)
header_font = f(BOLD, 42)
label_font = f(BOLD, 38)
body_font = f(REG, 38)

margin = 50
gap = 70
table_w = (CANVAS_W - 2 * margin - gap) // 2
title_top = 20
title_h = 80
table_top = title_top + title_h + 20

# --- Table 1: Datasets ---
col_w1 = [int(table_w * 0.22), int(table_w * 0.26), int(table_w * 0.26)]
col_w1.append(table_w - sum(col_w1))
rows1 = [
    ["", "nuScenes", "Waymo Open", "K-Radar"],
    ["3D boxes", "1.4M", "12M (LiDAR)", "93.3K"],
    ["Modalities", "6 cameras, 1 LiDAR, 5 radar", "Cameras + LiDAR (5 each)", "4 cameras, 2 LiDAR, 4D radar"],
    ["Diversity axes", "General scene diversity (Boston/Singapore); weather only as unstructured text",
     "Geographic spread (US cities) as primary axis; no weather annotation",
     "Structured per-sequence: 7 weather categories, environment, time of day"],
    ["Uniqueness", "First full 360° redundancy across all 3 modalities + 11-layer semantic HD maps",
     "Largest scale/density, 76 km² geographic coverage",
     "4D radar tensor (adds elevation) -> weather-robust detection, paired with explicit weather, environment, and time-of-day diversity"],
]

# --- Table 2: Models ---
x2 = margin + table_w + gap
col_w2 = [int(table_w * 0.24), int(table_w * 0.25), int(table_w * 0.25)]
col_w2.append(table_w - sum(col_w2))
rows2 = [
    ["", "BEVFusion", "MV2DFusion", "ASF"],
    ["Modalities", "Camera + LiDAR", "Camera + LiDAR", "Camera + LiDAR + 4D radar"],
    ["Trained on", "nuScenes", "nuScenes", "K-Radar"],
    ["Fusion approach", "Combines features in one shared bird's-eye view",
     "Detects per-sensor first, then merges detections",
     "Projects all sensors to one space, cross-attention combines them"],
    ["Main highlight", "Shared BEV space for camera+LiDAR",
     "Fuses after detection, not raw features",
     "Only one designed to handle a sensor going missing"],
]

wrapped1, heights1 = wrap_table(draw, col_w1, rows1, header_font, label_font, body_font, ROW_PAD)
wrapped2, heights2 = wrap_table(draw, col_w2, rows2, header_font, label_font, body_font, ROW_PAD)
synced_heights = [max(a, b) for a, b in zip(heights1, heights2)]

final_h = table_top + sum(synced_heights) + 20
img = img.resize((CANVAS_W, final_h))
draw = ImageDraw.Draw(img)
img.paste(WHITE, (0, 0, CANVAS_W, final_h))

draw.text((margin, title_top), "Datasets", font=title_font, fill=NAVY)
draw.text((x2, title_top), "Models", font=title_font, fill=NAVY)

draw_table(draw, margin, table_top, col_w1, wrapped1, synced_heights, ROW_PAD)
draw_table(draw, x2, table_top, col_w2, wrapped2, synced_heights, ROW_PAD)

img.save("/home/adhish/Productivity/AMSCUP/docs/crossproduct_figures/thesis_defense/dataset_model_tables.png")
print("saved", img.size)
