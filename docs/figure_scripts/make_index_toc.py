from PIL import Image, ImageDraw, ImageFont
import math

W, H = 2340, 1000  # px, ~22cm x 9.4cm at 300dpi-ish scaling for crispness
SCALE = 3
W, H = W*1, H*1

img = Image.new('RGBA', (W, H), (255,255,255,0))
d = ImageDraw.Draw(img)

ACCENT = (42,96,153)      # #2a6099
DARK   = (25,68,97)       # #194461
GREY   = (102,102,102)    # #666666
WHITE  = (255,255,255)

FONT_DIR = "/usr/share/fonts/noto/"
num_font = ImageFont.truetype(FONT_DIR+"NotoSans-Bold.ttf", 50)
label_font = ImageFont.truetype(FONT_DIR+"NotoSans-Bold.ttf", 40)

left_items = [
    "Context: Reality Gap",
    "Aim",
    "Dataset: K-Radar",
    "Availability-aware Sensor Fusion",
    "Corruptions",
    "Metrics",
    "Experimental Setup",
]
right_items = [
    "Results table",
    "Findings",
    "Discussion",
    "Limitation/Open Questions",
    "Future Work",
    "ASF Robustness Study Summary",
    "Conclusions",
]

rows = 7
R = 58  # circle radius
top_margin = 70
bottom_margin = 70
first_c = top_margin + R
last_c = H - bottom_margin - R
row_gap = (last_c - first_c) / (rows - 1)

col_x = {'left': 190, 'right': 1290}
label_x_offset = R + 40

def connector(cx, y0, y1, r, dy_from_center):
    # tapered vesica connector; endpoints exactly match the circle's own
    # boundary width at that height so there's no protrusion/kink where it meets the circle.
    hw_edge = math.sqrt(max(r*r - dy_from_center*dy_from_center, 1))
    pinch_min = 0.55  # fraction of hw_edge at the narrowest waist point
    steps = 40
    left_pts = []
    right_pts = []
    for i in range(steps+1):
        t = i/steps
        y = y0 + (y1-y0)*t
        pinch = pinch_min + (1-pinch_min)*((2*abs(t-0.5))**2)
        hw = hw_edge*pinch
        left_pts.append((cx-hw, y))
        right_pts.append((cx+hw, y))
    poly = left_pts + right_pts[::-1]
    d.polygon(poly, fill=ACCENT)

for col, items, cx in [('left', left_items, col_x['left']), ('right', right_items, col_x['right'])]:
    centers = [first_c + i*row_gap for i in range(rows)]
    # connectors first (behind circles)
    for i in range(rows-1):
        dy = R*0.55
        connector(cx, centers[i]+dy, centers[i+1]-dy, R, dy)
    # circles + numbers
    for i, cy in enumerate(centers):
        d.ellipse([cx-R, cy-R, cx+R, cy+R], fill=ACCENT)
        num = f"{i+1 if col=='left' else i+8:02d}"
        bbox = d.textbbox((0,0), num, font=num_font)
        tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
        d.text((cx-tw/2-bbox[0], cy-th/2-bbox[1]), num, font=num_font, fill=WHITE)
        # label
        label = items[i]
        lbbox = d.textbbox((0,0), label, font=label_font)
        lh = lbbox[3]-lbbox[1]
        d.text((cx+label_x_offset, cy-lh/2-lbbox[1]), label, font=label_font, fill=DARK)

img.save('/tmp/claude-1000/-home-adhish-Productivity-AMSCUP/7b95acae-83da-4f4e-a2c7-25cad7eface0/scratchpad/index_fig/index_fig.png')
print("saved", img.size)
