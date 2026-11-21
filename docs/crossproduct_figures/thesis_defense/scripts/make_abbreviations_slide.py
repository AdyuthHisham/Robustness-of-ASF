"""New slide (after slide 31): Abbreviations used across the deck.
Bespoke PIL script, deck's existing table-figure convention (navy/accent-blue, Noto Sans).
Three grouped two-column tables (Abbreviation | Meaning), side by side.
Canvas sized to the deck's actual slide dimensions (25.4cm x 14.288cm), 126px/cm.
"""
from PIL import Image, ImageDraw, ImageFont

NAVY = (25, 68, 97)
ACCENT = (42, 96, 153)
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
    for line in lines:
        if draw.textbbox((0, 0), line, font=font)[2] > max_width:
            raise ValueError(f"Cell text does not fit column width even alone: {line!r}")
    return lines


def wrap_table(draw, col_widths, rows, label_font, body_font, row_pad):
    wrapped_rows = []
    row_heights = []
    for row in rows:
        wrapped_cells = []
        for c_idx, cell in enumerate(row):
            cw = col_widths[c_idx] - 2 * row_pad
            fnt = label_font if c_idx == 0 else body_font
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
        bg = ROW_ALT if r_idx % 2 == 0 else WHITE
        draw.rectangle([x0, y, x0 + total_w, y + row_h], fill=bg)
        for c_idx, (lines, fnt) in enumerate(wrapped_cells):
            cx = x_positions[c_idx] + row_pad
            cy = y + row_pad
            color = NAVY if c_idx == 0 else TEXT
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


LINE_GAP = 6
ROW_PAD = 12

PX_PER_CM = 126
CANVAS_W = int(25.4 * PX_PER_CM)
CANVAS_H = int(14.288 * PX_PER_CM)

img = Image.new("RGB", (CANVAS_W, CANVAS_H), WHITE)
draw = ImageDraw.Draw(img)

heading_font = f(BOLD, 34)
label_font = f(BOLD, 26)
body_font = f(REG, 26)

margin = 40
gap = 36
col_w = (CANVAS_W - 2 * margin - 2 * gap) // 3
heading_h = 46
top = 10

groups = [
    ("Metrics & Evaluation", [
        ["AP", "Average Precision"],
        ["mAP", "mean Average Precision"],
        ["IoU", "Intersection over Union"],
        ["mATE", "mean Average Translation Error"],
        ["mASE", "mean Average Scale Error"],
        ["mAOE", "mean Average Orientation Error"],
        ["TP / FP / FN", "True Positive / False Positive / False Negative"],
["R_b^c", "Retention (robustness ratio vs. baseline)"],
        ["CRI", "Corruption Robustness Index"],
    ]),
    ("Sensors & Hardware", [
        ["LiDAR", "Light Detection and Ranging"],
        ["RADAR", "Radio Detection and Ranging"],
        ["GPS / RTK-GPS", "Global Positioning System / Real-Time Kinematic GPS"],
        ["IMU", "Inertial Measurement Unit"],
        ["GPU / CPU", "Graphics / Central Processing Unit"],
        ["HD", "High Definition (maps)"],
    ]),
    ("Model & Methodology", [
        ["ASF", "Availability-aware Sensor Fusion"],
        ["MSF", "Multimodal Sensor Fusion"],
        ["BEV", "Bird's-Eye View"],
        ["UCP", "Unified Canonical Projection"],
        ["CASAP", "Cross-Attention across Sensors Along Patches"],
        ["PN", "Post-feature Normalisation"],
        ["SCL", "Sensor Combination Loss"],
        ["FM / FV", "Feature Map / Front View"],
        ["GT", "Ground Truth"],
        ["SC", "Sensor Combination (subset)"],
        ["Obj / Cls / Reg", "Objectness / Classification / Regression (Fig. 4 labels)"],
    ]),
]

col_widths_inner = [int(col_w * 0.30), col_w - int(col_w * 0.30)]

bottoms = []
for i, (heading, rows) in enumerate(groups):
    x0 = margin + i * (col_w + gap)
    draw.text((x0, top), heading, font=heading_font, fill=NAVY)
    table_top = top + heading_h
    wrapped, heights = wrap_table(draw, col_widths_inner, rows, label_font, body_font, ROW_PAD)
    bottom = draw_table(draw, x0, table_top, col_widths_inner, wrapped, heights, ROW_PAD)
    bottoms.append(bottom)

final_h = max(bottoms) + 20
img = img.crop((0, 0, CANVAS_W, final_h))
img.save("/home/adhish/Productivity/AMSCUP/docs/crossproduct_figures/thesis_defense/abbreviations_slide.png")
print("saved", img.size)
