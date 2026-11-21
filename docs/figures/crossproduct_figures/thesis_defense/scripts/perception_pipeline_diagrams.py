"""Generate the two generalized-perception-pipeline block diagrams for the
thesis defense Introduction slides (slide 4: clean pipeline; slide 5: same
pipeline with corruptions injected, duplicated slide for a "click to reveal
corruptions" effect when advancing 4 -> 5).

Not data-derived — hand-authored schematic diagrams, no parquet/CSV inputs.
Left-to-right flow (matches the user-supplied reference: ~/Downloads/multimodal_model.png,
vertical input stack -> elbow merge -> model -> elbow diverge -> outputs).

Per-sensor group colors reuse the repo's own established per-modality palette
(SENSOR_COLOR in scripts/analysis/bar_charts.py / distance_line_charts.py:
camera green #2ca02c, lidar orange #e8590c, radar purple #7b3fe4) rather than
inventing a new one — Sensor 1/2/3 map onto camera/lidar/radar in this project.

Two output variants:
- build(corrupt): square-ish (1800x1000), for side-by-side placement.
- build_row(corrupt): wide (2400x560, ~4.27:1), sized to fill a full-width
  slide row without distorting/stretching the square-ish version.
"""

from __future__ import annotations

import math

from PIL import Image, ImageDraw, ImageFont

BG = (255, 255, 255)
TEXT_WHITE = (255, 255, 255)
TEXT_BLACK = (20, 20, 20)
ARROW = (20, 20, 20)
MODEL_FILL = (25, 68, 97)  # deck navy #194461
OUTPUT_FILL = (42, 96, 153)  # deck accent blue #2a6099

# Repo-canonical per-modality colors (bar_charts.py / distance_line_charts.py SENSOR_COLOR)
GROUP_COLORS = [(44, 160, 44), (232, 89, 12), (123, 63, 228)]  # camera green, lidar orange, radar purple

SENSOR_LABELS = ["Sensor 1", "Sensor 2", "Sensor 3"]
CORRUPT_LABELS = ["Adverse\nWeather", "Sensor\nDamage", "Miscalibration"]
OUT_LABELS = ["Object\nDetection", "Semantic\nSegmentation", "Trajectory\nPlanning"]

FONT_BOLD = "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD, size)


def draw_box(d: ImageDraw.ImageDraw, xy, label: str, fill, text_color=TEXT_WHITE, fsize=26):
    d.rectangle(xy, fill=fill)
    f = font(fsize)
    x0, y0, x1, y1 = xy
    lines = label.split("\n")
    total_h = sum(d.textbbox((0, 0), ln, font=f)[3] for ln in lines) + (len(lines) - 1) * 6
    cy = (y0 + y1) / 2 - total_h / 2
    for ln in lines:
        bbox = d.textbbox((0, 0), ln, font=f)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        cx = (x0 + x1) / 2 - w / 2
        d.text((cx, cy), ln, font=f, fill=text_color)
        cy += h + 6


def arrowhead(d: ImageDraw.ImageDraw, p0, p1, color, width=6, head=16):
    d.line([p0, p1], fill=color, width=width)
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    for da in (0.5, -0.5):
        hx = p1[0] - head * 1.6 * math.cos(ang - da)
        hy = p1[1] - head * 1.6 * math.sin(ang - da)
        d.line([p1, (hx, hy)], fill=color, width=width)


def _draw_pipeline(d, corrupt, box_h, box_gap, stack_top, corrupt_x, sensor_x, model_x, model_y, model_w, model_h,
                    output_x, corrupt_w, sensor_w, out_w, H, merge_x, diverge_x, head_y, f_head_size):
    box_ys = [stack_top + i * (box_h + box_gap) for i in range(3)]

    f_head = font(f_head_size)
    heading = "Data"
    bbox = d.textbbox((0, 0), heading, font=f_head)
    hx = sensor_x + sensor_w / 2 - (bbox[2] - bbox[0]) / 2
    d.text((hx, head_y), heading, font=f_head, fill=TEXT_BLACK)

    if corrupt:
        for i, y in enumerate(box_ys):
            cbox = (corrupt_x, y, corrupt_x + corrupt_w, y + box_h)
            draw_box(d, cbox, CORRUPT_LABELS[i], fill=GROUP_COLORS[i], fsize=22)
            cy = y + box_h / 2
            arrowhead(d, (corrupt_x + corrupt_w, cy), (sensor_x, cy), color=GROUP_COLORS[i], width=6)

    for i, y in enumerate(box_ys):
        box = (sensor_x, y, sensor_x + sensor_w, y + box_h)
        draw_box(d, box, SENSOR_LABELS[i], fill=GROUP_COLORS[i], fsize=26)

    for i, y in enumerate(box_ys):
        cy = y + box_h / 2
        d.line([(sensor_x + sensor_w, cy), (merge_x, cy)], fill=GROUP_COLORS[i], width=6)
    d.line([(merge_x, box_ys[0] + box_h / 2), (merge_x, box_ys[2] + box_h / 2)], fill=ARROW, width=6)
    arrowhead(d, (merge_x, H / 2), (model_x, H / 2), color=ARROW, width=6)

    draw_box(d, (model_x, model_y, model_x + model_w, model_y + model_h), "Perception\nModel", fill=MODEL_FILL, fsize=30)

    d.line([(model_x + model_w, H / 2), (diverge_x, H / 2)], fill=ARROW, width=6)
    d.line([(diverge_x, box_ys[0] + box_h / 2), (diverge_x, box_ys[2] + box_h / 2)], fill=ARROW, width=6)
    for y in box_ys:
        cy = y + box_h / 2
        arrowhead(d, (diverge_x, cy), (output_x, cy), color=ARROW, width=6)

    for i, y in enumerate(box_ys):
        box = (output_x, y, output_x + out_w, y + box_h)
        draw_box(d, box, OUT_LABELS[i], fill=OUTPUT_FILL, fsize=24)


def build(corrupt: bool) -> Image.Image:
    W, H = 1800, 1000
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)

    box_h, box_gap = 130, 70
    stack_h = 3 * box_h + 2 * box_gap
    stack_top = (H - stack_h) // 2

    corrupt_w, sensor_w, out_w = 230, 260, 300
    model_w, model_h = 300, 160
    left_margin = 90
    gap1, gap2, gap3 = 110, 130, 130

    corrupt_x = left_margin
    sensor_x = (corrupt_x + corrupt_w + gap1) if corrupt else left_margin
    model_x = sensor_x + sensor_w + gap2
    model_y = H // 2 - model_h // 2
    output_x = model_x + model_w + gap3
    merge_x = model_x - 60
    diverge_x = output_x - 60

    _draw_pipeline(d, corrupt, box_h, box_gap, stack_top, corrupt_x, sensor_x, model_x, model_y, model_w, model_h,
                   output_x, corrupt_w, sensor_w, out_w, H, merge_x, diverge_x, stack_top - 60, 30)
    return im


def build_row(corrupt: bool) -> Image.Image:
    """Wide (~4.27:1) full-row variant — sized to fill a full-width slide
    row without stretching/distorting the boxes from build()."""
    W, H = 2400, 560
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)

    box_h, box_gap = 108, 26
    stack_h = 3 * box_h + 2 * box_gap
    head_h = 46
    stack_top = head_h + (H - head_h - stack_h) // 2

    corrupt_w, sensor_w, model_w, out_w = 300, 280, 320, 320
    model_h = 150
    model_y = H // 2 - model_h // 2

    fixed_w = (corrupt_w if corrupt else 0) + sensor_w + model_w + out_w
    n_gaps = 4 if corrupt else 3
    margin = 110
    total_gap_space = W - 2 * margin - fixed_w
    if corrupt:
        gap1 = int(total_gap_space * 0.18)
        gap2 = int(total_gap_space * 0.41)
        gap3 = total_gap_space - gap1 - gap2
    else:
        gap1 = 0
        gap2 = int(total_gap_space * 0.5)
        gap3 = total_gap_space - gap2

    corrupt_x = margin
    sensor_x = (corrupt_x + corrupt_w + gap1) if corrupt else margin
    model_x = sensor_x + sensor_w + gap2
    output_x = model_x + model_w + gap3
    merge_x = model_x - 70
    diverge_x = output_x - 70

    _draw_pipeline(d, corrupt, box_h, box_gap, stack_top, corrupt_x, sensor_x, model_x, model_y, model_w, model_h,
                   output_x, corrupt_w, sensor_w, out_w, H, merge_x, diverge_x, 6, 28)
    return im


if __name__ == "__main__":
    out_dir = "/home/adhish/Productivity/AMSCUP/docs/crossproduct_figures/thesis_defense"
    build(corrupt=False).save(f"{out_dir}/generalized_perception_task.png")
    build(corrupt=True).save(f"{out_dir}/corruptions_in_system.png")
    build_row(corrupt=False).save(f"{out_dir}/generalized_perception_task_row.png")
    build_row(corrupt=True).save(f"{out_dir}/corruptions_in_system_row.png")
    print("wrote square and full-row variants")
