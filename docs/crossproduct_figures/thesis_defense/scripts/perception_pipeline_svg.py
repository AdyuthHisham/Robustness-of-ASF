"""Generate the perception-pipeline diagrams as native SVG, styled to match
the reference figure on slide 7 (Experimental Setup pipeline diagram,
Pictures/1000000100000640000002F12316E08E.png in Thesis_Presentation_Reworked.odp):
pastel rounded boxes with a darker matching border, charcoal title text,
dashed rounded-rect "column" containers with a bold label.

Per user instructions:
- Reuse that reference's exact color palette (sampled below), not an
  invented one.
- Sensor items are NOT boxes — plain colored text, sitting inside a big
  dashed "Data" container (mirrors how every other column gets its own
  big container block).
- Diagram 2 additionally wraps the three corruption sources in their own
  big container, each box colored to match its target sensor, and uses a
  single connector line between each pair of containers (Corruptions ->
  Data -> Model -> Output) instead of per-sensor fan lines.
- Every container's heading and its content are horizontally centered
  within the container, with padding trimmed to cut empty space (as
  opposed to the reference's own top-left-anchored label).

Colors sampled directly from the slide-7 reference PNG:
  blue   fill #BFD5E3 / border #638DA8  (Dataset box)
  orange fill #EBC4A4 / border #C98252  (Corruption Injection box)
  green  fill #C4D6C2 / border #71966F  (Prediction box)
  gray   fill #D0D3D6 / border #858B91  (Consolidation/Metrics/Robustness boxes)
  title text #42464B (charcoal), dashed container border #858B91
"""

from __future__ import annotations

from PIL import ImageFont

BLUE_FILL, BLUE_BORDER = "#BFD5E3", "#638DA8"
ORANGE_FILL, ORANGE_BORDER = "#EBC4A4", "#C98252"
GREEN_FILL, GREEN_BORDER = "#C4D6C2", "#71966F"
GRAY_FILL, GRAY_BORDER = "#D0D3D6", "#858B91"
TEXT_TITLE = "#42464B"
CONTAINER_BORDER = "#858B91"

GROUP = [(BLUE_FILL, BLUE_BORDER), (ORANGE_FILL, ORANGE_BORDER), (GREEN_FILL, GREEN_BORDER)]

SENSOR_LABELS = ["Sensor 1", "Sensor 2", "Sensor 3"]
CORRUPT_LABELS = ["Adverse Weather", "Sensor Damage", "Miscalibration"]
OUT_LABELS = ["Object Detection", "Semantic Segmentation", "Trajectory Planning"]

FONT = "DejaVu Sans"
FONT_BOLD_PATH = "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"

DEFAULT_LABELS = {"corrupt": "Corruptions", "data": "Data", "model": "Model", "output": "Output"}

SIDE_PAD = 34
TOP_PAD = 52
BOTTOM_PAD = 26


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text_width(s: str, fsize: int) -> float:
    f = ImageFont.truetype(FONT_BOLD_PATH, fsize)
    bbox = f.getbbox(s)
    return bbox[2] - bbox[0]


def rounded_box(x, y, w, h, fill, border, label, text_color=TEXT_TITLE, fsize=22, rx=14):
    lines = label.split("\n")
    cy = y + h / 2 - (len(lines) - 1) * (fsize * 0.6)
    text_svg = ""
    for ln in lines:
        text_svg += (
            f'<text x="{x + w / 2}" y="{cy}" font-family="{FONT}" font-weight="bold" '
            f'font-size="{fsize}" fill="{text_color}" text-anchor="middle" dominant-baseline="middle">{esc(ln)}</text>'
        )
        cy += fsize * 1.25
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" ry="{rx}" '
        f'fill="{fill}" stroke="{border}" stroke-width="2.5"/>' + text_svg
    )


def dashed_container(x, y, w, h, label, rx=18, fsize=21):
    cx = x + w / 2
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" ry="{rx}" '
        f'fill="none" stroke="{CONTAINER_BORDER}" stroke-width="2" stroke-dasharray="8,6"/>'
        f'<text x="{cx}" y="{y + 28}" font-family="{FONT}" font-weight="bold" '
        f'font-size="{fsize}" fill="{TEXT_TITLE}" text-anchor="middle">{esc(label)}</text>'
    )


def straight(x0, y0, x1, y1, color, width=3, arrow=True):
    path = f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="{color}" stroke-width="{width}"/>'
    if arrow:
        path += arrowhead(x1 - 14, y1, x1, y1, color, width)
    return path


def arrowhead(x0, y0, x1, y1, color, width=3):
    import math

    ang = math.atan2(y1 - y0, x1 - x0)
    head = 11
    p1 = (x1 - head * 1.5 * math.cos(ang - 0.5), y1 - head * 1.5 * math.sin(ang - 0.5))
    p2 = (x1 - head * 1.5 * math.cos(ang + 0.5), y1 - head * 1.5 * math.sin(ang + 0.5))
    return f'<polygon points="{x1},{y1} {p1[0]},{p1[1]} {p2[0]},{p2[1]}" fill="{color}"/>'


def build_svg(corrupt: bool, gap: float = 90, simple_links: bool = False, labels: dict | None = None) -> tuple[str, float, float]:
    labels = {**DEFAULT_LABELS, **(labels or {})}

    box_h, box_gap = 96, 24
    stack_h = 3 * box_h + 2 * box_gap
    content_top = TOP_PAD + 20  # 20px canvas top margin before the container starts
    box_ys = [content_top + i * (box_h + box_gap) for i in range(3)]
    stack_center = content_top + stack_h / 2
    container_y0 = content_top - TOP_PAD
    container_h = TOP_PAD + stack_h + BOTTOM_PAD

    data_w_text = max(text_width(s, 24) for s in SENSOR_LABELS)
    data_w = data_w_text + 2 * SIDE_PAD

    model_w, model_h = 300, 140
    out_w = 300
    corrupt_w = 260

    margin = 30
    x = margin
    parts = []

    if corrupt:
        cx0 = x
        corrupt_container_w = corrupt_w + 2 * SIDE_PAD
        for i, y in enumerate(box_ys):
            fill, border = GROUP[i]
            parts.append(rounded_box(cx0 + SIDE_PAD, y, corrupt_w, box_h, fill, border, CORRUPT_LABELS[i], fsize=19))
            if not simple_links:
                parts.append(straight(cx0 + SIDE_PAD + corrupt_w, y + box_h / 2, cx0 + corrupt_container_w, y + box_h / 2, GROUP[i][1]))
        corrupt_right = cx0 + corrupt_container_w
        parts.append(dashed_container(cx0, container_y0, corrupt_container_w, container_h, labels["corrupt"]))
        x = corrupt_right + gap

    # Data container (sensor labels, no box), heading + text both centered
    dx0 = x
    data_cx = dx0 + data_w / 2
    for i, y in enumerate(box_ys):
        _, border = GROUP[i]
        ty = y + box_h / 2
        parts.append(
            f'<text x="{data_cx}" y="{ty}" font-family="{FONT}" font-weight="bold" '
            f'font-size="24" fill="{border}" text-anchor="middle" dominant-baseline="middle">{esc(SENSOR_LABELS[i])}</text>'
        )
    parts.append(dashed_container(dx0, container_y0, data_w, container_h, labels["data"]))
    data_right = dx0 + data_w

    if corrupt and simple_links:
        parts.append(straight(corrupt_right, stack_center, dx0, stack_center, TEXT_TITLE))

    model_container_w = model_w + 2 * SIDE_PAD
    model_x = data_right + gap + (0 if simple_links else 30) + SIDE_PAD

    if simple_links:
        parts.append(straight(data_right, stack_center, model_x - SIDE_PAD, stack_center, TEXT_TITLE))
    else:
        merge_x = model_x - SIDE_PAD - 30
        for i, y in enumerate(box_ys):
            cy = y + box_h / 2
            parts.append(f'<line x1="{data_right - 10}" y1="{cy}" x2="{merge_x}" y2="{cy}" stroke="{GROUP[i][1]}" stroke-width="3"/>')
        parts.append(f'<line x1="{merge_x}" y1="{box_ys[0] + box_h / 2}" x2="{merge_x}" y2="{box_ys[2] + box_h / 2}" stroke="{TEXT_TITLE}" stroke-width="3"/>')
        parts.append(straight(merge_x, stack_center, model_x - SIDE_PAD, stack_center, TEXT_TITLE))

    model_y = stack_center - model_h / 2
    parts.append(rounded_box(model_x - SIDE_PAD, model_y, model_w, model_h, GRAY_FILL, GRAY_BORDER, "Perception\nModel", fsize=24))
    parts.append(dashed_container(model_x - SIDE_PAD - SIDE_PAD, container_y0, model_container_w, container_h, labels["model"]))
    model_right = model_x - SIDE_PAD + model_w

    out_container_w = out_w + 2 * SIDE_PAD
    output_x = model_right + gap + (0 if simple_links else 30) + SIDE_PAD

    if simple_links:
        parts.append(straight(model_right, stack_center, output_x - SIDE_PAD, stack_center, TEXT_TITLE))
    else:
        diverge_x = output_x - SIDE_PAD - 30
        parts.append(f'<line x1="{model_right}" y1="{stack_center}" x2="{diverge_x}" y2="{stack_center}" stroke="{TEXT_TITLE}" stroke-width="3"/>')
        parts.append(f'<line x1="{diverge_x}" y1="{box_ys[0] + box_h / 2}" x2="{diverge_x}" y2="{box_ys[2] + box_h / 2}" stroke="{TEXT_TITLE}" stroke-width="3"/>')
        for y in box_ys:
            cy = y + box_h / 2
            parts.append(straight(diverge_x, cy, output_x - SIDE_PAD, cy, TEXT_TITLE))

    for i, y in enumerate(box_ys):
        parts.append(rounded_box(output_x - SIDE_PAD, y, out_w, box_h, GRAY_FILL, GRAY_BORDER, OUT_LABELS[i], fsize=18))
    parts.append(dashed_container(output_x - SIDE_PAD - SIDE_PAD, container_y0, out_container_w, container_h, labels["output"]))

    total_w = output_x - SIDE_PAD + out_w + SIDE_PAD + margin
    total_h = container_y0 + container_h + margin

    body = "\n".join(parts)
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_w} {total_h}" '
        f'width="{total_w}" height="{total_h}">\n'
        f'<rect x="0" y="0" width="{total_w}" height="{total_h}" fill="white"/>\n'
        f'{body}\n</svg>\n'
    )
    return svg, total_w, total_h


def build_svg_fit(corrupt: bool, target_aspect: float, simple_links: bool = False, labels: dict | None = None) -> str:
    """Two-pass sizing: widen the inter-container gaps until width/height
    matches target_aspect, so the diagram fills a full slide row without
    distorting box shapes or text (only connector length changes)."""
    _, w0, h0 = build_svg(corrupt, gap=90, simple_links=simple_links, labels=labels)
    n_gaps = 3 if corrupt else 2
    needed_w = target_aspect * h0
    extra = max(0.0, needed_w - w0)
    new_gap = 90 + extra / n_gaps
    svg, _, _ = build_svg(corrupt, gap=new_gap, simple_links=simple_links, labels=labels)
    return svg


if __name__ == "__main__":
    out_dir = "/home/adhish/Productivity/AMSCUP/docs/crossproduct_figures/thesis_defense"
    TARGET_ASPECT = 23.495 / 5.482  # matches the slide's full-row image frame (cm/cm)
    with open(f"{out_dir}/generalized_perception_task.svg", "w") as f:
        f.write(build_svg_fit(corrupt=False, target_aspect=TARGET_ASPECT))
    # preserve the user's hand-edited container labels for the corruptions diagram
    corrupt_labels = {"corrupt": "Possible Corruptions", "data": "Data", "model": "Perception Model", "output": "Perception Output"}
    with open(f"{out_dir}/corruptions_in_system.svg", "w") as f:
        f.write(build_svg_fit(corrupt=True, target_aspect=TARGET_ASPECT, simple_links=True, labels=corrupt_labels))
    print("wrote SVGs")
