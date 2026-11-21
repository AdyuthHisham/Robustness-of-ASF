"""Single shared color palette for every generated thesis figure (coxcomb
charts, radar/spider charts, and any future figure script in this directory).

Anchored on the modality colors already established in the weather-corruption
radar charts (camera/LiDAR/radar spokes, e.g. weather_corruption_radar_sedan
part 1: normal/rain/overcast/sleet) -- those three colors are kept as the
first three entries of the general categorical palette below so that a
diversity-axis category color (used in the coxcomb charts) and a modality
color (used in the radar charts) draw from the same visual family across the
whole document, per the thesis writing bible's "be consistent across all
figures in color palette" hard rule.

MODALITY_COLORS is semantic (camera/lidar/radar mean specific sensors) and
must not be reassigned. CATEGORY_PALETTE is a general-purpose, colorblind-
reasonable qualitative sequence for figures whose categories carry no
modality meaning (weather, environment, time-of-day, distance, frame
density) -- assign colors to categories by indexing into it in a fixed order
so the same category always gets the same color across figures that share
categories (e.g. "Normal" is always CATEGORY_PALETTE[0] wherever a weather
category is drawn).
"""

MODALITY_COLORS = {
    "camera": "#1b7837",
    "lidar": "#2166ac",
    "radar": "#b2182b",
}

# First three entries intentionally match MODALITY_COLORS' hues (green, blue,
# red) so the coxcomb charts and radar charts read as one consistent design
# language; remaining entries extend the same qualitative family
# (ColorBrewer-style diverging/qualitative hues) rather than falling back to
# matplotlib's default tab10/tab20 cycle.
CATEGORY_PALETTE = [
    "#1b7837",  # green  (matches camera)
    "#2166ac",  # blue   (matches lidar)
    "#b2182b",  # red    (matches radar)
    "#e08214",  # orange
    "#8073ac",  # purple
    "#35978f",  # teal
    "#b35806",  # brown
    "#4d4d4d",  # gray
]

# Worst / second-worst highlight-circle colors used on the radar charts.
RANK_COLORS = {
    "worst": "#d62728",
    "second_worst": "#8c1aff",
}
