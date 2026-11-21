"""Regenerate the slide-7 "Experimental Setup" pipeline diagram (the
Dataset -> Corruption Injection -> Prediction -> Consolidation -> Metrics
Generation -> Robustness Analysis flowchart).

Geometry and colors are reverse-engineered pixel-exact from the original
embedded image (Pictures/1000000100000640000002F12316E08E.png in
Thesis_Presentation_Reworked.odp, slide 7) via color-mask bounding-box
detection — this diagram itself was unlogged/unprovenanced (no prior
script existed), so this is a from-scratch recreation. Same color palette
as perception_pipeline_svg.py (sampled from this same reference image).

The left-container -> Consolidation connector is also pixel-traced from
the original: horizontal stub at y=375 from the container's right edge to
x=757, vertical up to y=166 (Consolidation's own vertical center), then
horizontal into the Consolidation box — not a simple two-segment elbow.

Supports three style variants (see build_svg(variant=...)):
  1: hatch fill on Dataset/Corruption Injection/Prediction/Metrics Generation;
     no subtext on Corruption Injection or Metrics Generation.
  2: hatch fill only on Corruption Injection/Metrics Generation; Dataset and
     Prediction get restored original-style subtext; Corruption
     Injection/Metrics Generation still have no subtext.
  3: no hatches anywhere; keeps variant-2's Dataset/Prediction subtext and
     adds subtext back to Corruption Injection ("36 conditions") and
     Metrics Generation ("AP, CRI, Rb, mATE").
"""

from __future__ import annotations

BLUE_FILL, BLUE_BORDER = "#BFD5E3", "#638DA8"
ORANGE_FILL, ORANGE_BORDER = "#EBC4A4", "#C98252"
GREEN_FILL, GREEN_BORDER = "#C4D6C2", "#71966F"
GRAY_FILL, GRAY_BORDER = "#D0D3D6", "#858B91"
TEXT_TITLE = "#42464B"
TEXT_SUB = "#858B91"
CONTAINER_BORDER = "#858B91"

FONT = "DejaVu Sans"

# Pixel-exact geometry sampled from the original 1600x753 reference PNG
CANVAS_W, CANVAS_H = 1600, 753
CONTAINER = (22, 17, 585, 734)  # x0,y0,x1,y1
LEFT_BOX_X0, LEFT_BOX_X1 = 66, 541
RIGHT_BOX_X0, RIGHT_BOX_X1 = 930, 1405
ROW_YS = [(85, 247), (318, 481), (552, 714)]  # (y0,y1) shared by left & right columns

# Pixel-traced connector path (container -> Consolidation): H stub, V bend, H into box
CONNECTOR_START_Y = 375
CONNECTOR_BEND_X = 757
CONNECTOR_END_Y = 166


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def hatch_pattern(pid: str, stroke: str) -> str:
    return (
        f'<pattern id="{pid}" width="9" height="9" patternTransform="rotate(45)" patternUnits="userSpaceOnUse">'
        f'<rect width="9" height="9" fill="white"/>'
        f'<line x1="0" y1="0" x2="0" y2="9" stroke="{stroke}" stroke-width="3.2"/>'
        f'</pattern>'
    )


def title_subtitle_box(x0, y0, x1, y1, fill, border, title, subtitle, rx=10, hatched=False):
    w, h = x1 - x0, y1 - y0
    cx = x0 + w / 2
    sub_lines = subtitle.split("\n") if subtitle else []
    title_y = y0 + h / 2 if not sub_lines else y0 + h * 0.4
    sub_svg = ""
    sy = title_y + 42
    for ln in sub_lines:
        sub_svg += (
            f'<text x="{cx}" y="{sy}" font-family="{FONT}" '
            f'font-size="21" fill="{TEXT_SUB}" text-anchor="middle" dominant-baseline="middle">{esc(ln)}</text>'
        )
        sy += 27

    plate_svg = ""
    if hatched:
        # Solid white backing plate behind the text block so the diagonal
        # hatch doesn't run through the letters and kill legibility.
        plate_top = title_y - 30
        plate_bottom = (sy - 27 + 18) if sub_lines else (title_y + 22)
        plate_svg = (
            f'<rect x="{x0 + 14}" y="{plate_top}" width="{w - 28}" height="{plate_bottom - plate_top}" '
            f'rx="6" ry="6" fill="white" fill-opacity="0.82"/>'
        )

    return (
        f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="{rx}" ry="{rx}" '
        f'fill="{fill}" stroke="{border}" stroke-width="2.5"/>'
        + plate_svg
        + f'<text x="{cx}" y="{title_y}" font-family="{FONT}" font-weight="bold" '
        f'font-size="34" fill="{TEXT_TITLE}" text-anchor="middle" dominant-baseline="middle">{esc(title)}</text>'
        + sub_svg
    )


def dashed_container(x0, y0, x1, y1, label, rx=16):
    return (
        f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="{rx}" ry="{rx}" '
        f'fill="none" stroke="{CONTAINER_BORDER}" stroke-width="2" stroke-dasharray="8,6"/>'
        f'<text x="{x0 + 28}" y="{y0 + 35}" font-family="{FONT}" font-weight="bold" '
        f'font-size="24" fill="{TEXT_TITLE}">{esc(label)}</text>'
    )


def arrowhead(x0, y0, x1, y1, color, width=3):
    import math

    ang = math.atan2(y1 - y0, x1 - x0)
    head = 13
    p1 = (x1 - head * 1.5 * math.cos(ang - 0.5), y1 - head * 1.5 * math.sin(ang - 0.5))
    p2 = (x1 - head * 1.5 * math.cos(ang + 0.5), y1 - head * 1.5 * math.sin(ang + 0.5))
    return f'<polygon points="{x1},{y1} {p1[0]},{p1[1]} {p2[0]},{p2[1]}" fill="{color}"/>'


def straight(x0, y0, x1, y1, color=TEXT_TITLE, width=3):
    return f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="{color}" stroke-width="{width}"/>' + arrowhead(x0, y0, x1, y1, color, width)


def container_to_consolidation_connector(color=TEXT_TITLE, width=3):
    """Pixel-traced dogleg: container edge -> bend -> Consolidation box."""
    x0 = CONTAINER[2]
    path = (
        f'<path d="M {x0} {CONNECTOR_START_Y} H {CONNECTOR_BEND_X} V {CONNECTOR_END_Y} '
        f'H {RIGHT_BOX_X0 - 13}" fill="none" stroke="{color}" stroke-width="{width}"/>'
    )
    return path + arrowhead(RIGHT_BOX_X0 - 20, CONNECTOR_END_Y, RIGHT_BOX_X0, CONNECTOR_END_Y, color, width)


def build_svg(variant: int) -> str:
    assert variant in (1, 2, 3)

    if variant == 1:
        hatch_set = {"dataset", "corrupt", "prediction", "metrics"}
        dataset_sub, pred_sub = "Run on test split", "Inference from Object Detection Model"
        corrupt_sub, metrics_sub = "", ""
    elif variant == 2:
        hatch_set = {"corrupt", "metrics"}
        dataset_sub = "K-Radar, 58-Seq, test-split"
        pred_sub = "ASF inference, official checkpoint\n-> KITTI-format prediction / GT"
        corrupt_sub, metrics_sub = "", ""
    else:  # variant == 3
        hatch_set = set()
        dataset_sub = "K-Radar, 58-Seq, test-split"
        pred_sub = "ASF inference, official checkpoint\n-> KITTI-format prediction / GT"
        corrupt_sub, metrics_sub = "36 conditions", "AP, CRI, Rb, mATE"

    box_defs = {
        "dataset": (BLUE_FILL, BLUE_BORDER, "Dataset", dataset_sub, "hatch-dataset"),
        "corrupt": (ORANGE_FILL, ORANGE_BORDER, "Corruption Injection", corrupt_sub, "hatch-corrupt"),
        "prediction": (GREEN_FILL, GREEN_BORDER, "Prediction", pred_sub, "hatch-prediction"),
    }
    right_labels = [
        ("consolidation", GRAY_FILL, GRAY_BORDER, "Consolidation", "Individual inference files\nconsolidated into single database", "hatch-consolidation"),
        ("metrics", GRAY_FILL, GRAY_BORDER, "Metrics Generation", metrics_sub, "hatch-metrics"),
        ("robustness", GRAY_FILL, GRAY_BORDER, "Robustness Analysis", "per-condition, per-stratum breakdown", "hatch-robustness"),
    ]

    defs = []
    parts = []

    for key, (fill, border, title, subtitle, pid) in box_defs.items():
        y0, y1 = ROW_YS[list(box_defs).index(key)]
        is_hatched = key in hatch_set
        use_fill = f"url(#{pid})" if is_hatched else fill
        if is_hatched:
            defs.append(hatch_pattern(pid, border))
        parts.append(title_subtitle_box(LEFT_BOX_X0, y0, LEFT_BOX_X1, y1, use_fill, border, title, subtitle, hatched=is_hatched))
    parts.append(dashed_container(*CONTAINER, "Run once per corruption condition"))

    for i, (key, fill, border, title, subtitle, pid) in enumerate(right_labels):
        y0, y1 = ROW_YS[i]
        is_hatched = key in hatch_set
        use_fill = f"url(#{pid})" if is_hatched else fill
        if is_hatched:
            defs.append(hatch_pattern(pid, border))
        parts.append(title_subtitle_box(RIGHT_BOX_X0, y0, RIGHT_BOX_X1, y1, use_fill, border, title, subtitle, hatched=is_hatched))

    # vertical connectors within each column
    for a, b in zip(ROW_YS[:-1], ROW_YS[1:]):
        cx_left = (LEFT_BOX_X0 + LEFT_BOX_X1) / 2
        parts.append(straight(cx_left, a[1], cx_left, b[0], TEXT_TITLE))
        cx_right = (RIGHT_BOX_X0 + RIGHT_BOX_X1) / 2
        parts.append(straight(cx_right, a[1], cx_right, b[0], TEXT_TITLE))

    parts.append(container_to_consolidation_connector(TEXT_TITLE))

    defs_svg = f'<defs>{"".join(defs)}</defs>' if defs else ""
    body = "\n".join(parts)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CANVAS_W} {CANVAS_H}" '
        f'width="{CANVAS_W}" height="{CANVAS_H}">\n{defs_svg}\n'
        f'<rect x="0" y="0" width="{CANVAS_W}" height="{CANVAS_H}" fill="white"/>\n'
        f'{body}\n</svg>\n'
    )


if __name__ == "__main__":
    out_dir = "/home/adhish/Productivity/AMSCUP/docs/crossproduct_figures/thesis_defense"
    names = {
        1: "experimental_setup_pipeline_v1_hatch.svg",
        2: "experimental_setup_pipeline_v2_hatch.svg",
        3: "experimental_setup_pipeline_v3.svg",
    }
    for v, name in names.items():
        with open(f"{out_dir}/{name}", "w") as f:
            f.write(build_svg(v))
    print("wrote", ", ".join(names.values()))
