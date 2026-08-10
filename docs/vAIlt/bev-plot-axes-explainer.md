# BEV Plot Axes Explainer — `radar_clean.png` / `lidar_clean.png`

Scope: what X and Y actually mean in the clean-baseline radar/lidar BEV renders shown in
`repos/K-Radar/outputs/noise_visual_inspection/index.html`. Investigation only — no code or
image changes made.

## 0. Which script produced the current images

`repos/K-Radar/outputs/noise_visual_inspection/v2_regeneration_confirmation.md` hashes every
PNG from the pre-v2 run against the v2 run and shows **all `clean` images (radar and lidar,
all 3 frames) are byte-identical** — only `loss_partial` was intentionally re-styled by v2.
So the current `radar_clean.png` / `lidar_clean.png` were produced by the **original
`visualize_effects.py`** (`repos/K-Radar/datasets/effects/visualize_effects.py`), not
`visualize_effects_v2.py`. All code references below are to that file.

## 1. Plotting code (exact quotes)

No matplotlib — this is a hand-rolled cv2 canvas renderer:

```python
# visualize_effects.py:206-220
def _normalize_to_pixel(xy, ax_limits, img_w, img_h, margin):
    """Map world coords (x,y) to pixel (col,row) with margin and equal aspect."""
    x_min, x_max, y_min, y_max = ax_limits
    x_range = max(x_max - x_min, 1e-6)
    y_range = max(y_max - y_min, 1e-6)
    scale = min((img_w - 2*margin) / x_range, (img_h - 2*margin) / y_range)
    cx = (img_w - 2*margin) / 2.0
    cy = (img_h - 2*margin) / 2.0
    x_mid = (x_min + x_max) / 2.0
    y_mid = (y_min + y_max) / 2.0
    col = margin + cx + (xy[:, 0] - x_mid) * scale
    row = margin + cy - (xy[:, 1] - y_mid) * scale  # flip-y for image coords
    return col.astype(np.int32), row.astype(np.int32), scale
```

`col` = image X = plotted **X**, `row` = image Y (flipped) = plotted **Y**. `scale` is
shared between the two axes ("Keep aspect ratio equal" comment at line 211) — this is a
true equal-aspect BEV, not independently stretched axes.

Axis limits, computed once per frame from the clean point cloud and reused for every effect
variant of that modality (so clean and corrupted plots of the same frame are directly
comparable):

```python
# visualize_effects.py:355-360
def _lims(arr, pad=3):
    return [float(arr[:,0].min())-pad, float(arr[:,0].max())+pad,
            float(arr[:,1].min())-pad, float(arr[:,1].max())+pad]
rdr_lims = _lims(rdr, pad=3)
lidar_lims = _lims(lidar, pad=3)
```

i.e. `ax_limits = [x_min, x_max, y_min, y_max]` taken from **columns 0 and 1** of the raw
point array, ±3 units padding. No fixed/hardcoded limits — each frame gets its own
data-driven limits.

Data feeding the clean plot:

```python
# visualize_effects.py:378-393
clean_data = clean_item.get('rdr_sparse' if modality == 'radar' else
                            'ldr64' if modality == 'lidar' else None)
...
pts = clean_data[:, :3] if clean_data is not None and len(clean_data) > 0 else None
vals = clean_data[:, 3] if (clean_data is not None and len(clean_data) > 0 and clean_data.shape[1] >= 4) else None
...
render_bev(pts[:, :2] if pts is not None else None,
          vals, ax_limits,
          f'CLEAN | {label} | {n_pts} pts',
          mod_dir / f'{modality}_clean.png', ...)
```

So: **column 0 → X axis, column 1 → Y axis**, for both `rdr_sparse` and `ldr64`, identically.
Column 3 (power for radar, intensity for lidar) drives point color via a jet colormap
(`vals`), not axis position.

Axis labels and grid, drawn directly onto the canvas:

```python
# visualize_effects.py:280-300
for tick_pos in np.linspace(ax_limits[0], ax_limits[1], 7):
    ...cv2.putText(canvas, f'{tick_pos:.0f}', ...)   # X tick values
for tick_pos in np.linspace(ax_limits[2], ax_limits[3], 7):
    ...cv2.putText(canvas, f'{tick_pos:.0f}', ...)   # Y tick values

cv2.putText(canvas, 'X (m)', (img_w//2-15, img_h-5), ...)
cv2.putText(canvas, 'Y (m)', (5, img_h//2), ...)
```

## 2. Radar: what column 0/1 physically mean

`rdr_sparse` is loaded from the preprocessed sparse-point files, not the full 4DRT/cube:

```python
# visualize_effects.py:94-99
def load_rdr_sparse(seq: int, rdr_idx: int) -> np.ndarray:
    path = RDR_SPARSE_DIR / str(seq) / f'sprdr_{rdr_idx:05d}.npy'
    arr = np.load(str(path)).astype(np.float64)
    mask = ~((arr[:, 0] == 0) & (arr[:, 1] == 0) & (arr[:, 2] == 0))
    return arr[mask]
```

Empirically inspecting `sprdr_00033.npy` (seq 1, the `seq001_rdr033` example frame) after
the same zero-padding filter, per-column min/max:

| col | min | max | matches |
|---|---|---|---|
| 0 | 0.2 | 99.4 | `arr_x_cb = np.arange(0, 100, 0.4)` |
| 1 | -80.2 | 79.4 | `arr_y_cb = np.arange(-80, 80, 0.4)` |
| 2 | -30.2 | 29.4 | `arr_z_cb = np.arange(-30, 30, 0.4)` |
| 3 | 0.03 | 29.7 | power (unbounded, data-dependent) |

Those `arr_x_cb`/`arr_y_cb`/`arr_z_cb` ranges are the documented radar-cube axis
definitions in `datasets/kradar_detection_v1_0.py:108-110`:

```python
self.arr_z_cb = np.arange(-30, 30, 0.4)
self.arr_y_cb = np.arange(-80, 80, 0.4)
self.arr_x_cb = np.arange(0, 100, 0.4)
```

So `rdr_sparse` columns are `[x, y, z, power]` in K-Radar's standard cube convention:
**column 0 = x = forward/range (0–100 m ahead of the radar), column 1 = y = lateral
(−80…+80 m, left positive), column 2 = z = vertical**. This is the `radar_zyx_cube`
convention referenced in `radar-mat-vs-npy-corruption-point-report.md` (its "~100m x-range /
~160m y-range" matches exactly: 100 m span in x, 160 m span in y).

**Frame origin for radar**: `sprdr_*.npy` is generated directly from the radar cube/tensor
with no calibration offset applied (`tools/get_1st_points/main_get_1st_points.py` only
applies the radar↔lidar calib translation to *labels* and to *lidar points*, never to the
radar sparse points themselves — see §5). So radar-frame x/y/z origin = **the radar
sensor's own mounting location**, x forward along the radar boresight, y left, z up.

## 3. Lidar: what column 0/1 physically mean, and same-frame check

```python
# visualize_effects.py:102-151 (relevant excerpt)
def load_lidar_pcd(seq: int, ldr64_idx: int) -> np.ndarray:
    path = DATA_DIR / str(seq) / 'os2-64' / f'os2-64_{ldr64_idx:05d}.pcd'
    ...
    pc = values[:, :4].copy()      # first 4 PCD fields
    mask = ~((pc[:, 0] == 0) & (pc[:, 1] == 0) & (pc[:, 2] == 0))
    return pc[mask]
```

The raw `.pcd` header (checked directly, `data/1/os2-64/os2-64_00001.pcd`):

```
FIELDS x y z intensity t reflectivity ring ambient range
```

`values[:, :4]` = `[x, y, z, intensity]` in field order — so, same as radar, **column 0 = x
= forward, column 1 = y = lateral** in the Ouster os2-64's own sensor frame (x forward, y
left, z up — this is the raw driver output convention, matches radar's REP-103-style axes).

**This is NOT the same origin as the radar plot.** The real K-Radar dataset loader
(`datasets/kradar_detection_v2_0.py:310-334`, `get_ldr64`) applies a per-sequence
radar↔lidar calibration translation before using lidar points for anything downstream:

```python
# kradar_detection_v2_0.py:329-332
if self.ldr64.calib:
    n_pts, _ = pc_lidar.shape
    calib_vals = np.array(dict_item['meta']['calib']).reshape(-1,3).repeat(n_pts, axis=0)
    pc_lidar[:,:3] = pc_lidar[:,:3] + calib_vals
```

where the calib values come from the per-sequence file:

```python
# kradar_detection_v2_0.py:288-294
def get_calib_values(self, path_calib):
    ...
    list_calib = list(map(lambda x: float(x), lines[1].split(',')))
    list_values = [list_calib[1], list_calib[2], self.calib['z_offset']] # X, Y, Z
    return list_values
```

For seq 1 (`data/1/info_calib/calib_radar_lidar.txt`, checked directly):

```
frame difference,x,y
32,-2.54,0.3
```

→ `(dx, dy, dz) = (-2.54, 0.3, 0.7)` m (z_offset is a config constant, `calib = dict(z_offset=0.7)`).

**`visualize_effects.py`'s own `load_lidar_pcd` never applies this offset** — it parses the
raw `.pcd` and stops. So:

- `radar_clean.png` is in the radar sensor's native frame (rdr_sparse already generated in
  that frame, no shift applied by the script).
- `lidar_clean.png` is in the **raw Ouster os2-64 sensor's native frame**, uncorrected — a
  frame offset from the radar frame by roughly `(-2.54, +0.3, +0.7)` m for sequence 1 (this
  offset is per-sequence, since each sequence has its own `calib_radar_lidar.txt`).

**Conclusion: radar and lidar clean plots do NOT share a common coordinate origin.** Both
use the same *axis convention* (x forward, y left, in meters, equal aspect), but the (0,0)
point in `radar_clean.png` is the radar's mounting point, while (0,0) in `lidar_clean.png` is
the LiDAR's mounting point — offset by the vehicle's radar-lidar baseline (~2.5 m
longitudinal for seq 1). Comparing the two images side by side to reason about "does this
lidar point correspond to that radar point" is only valid to within that few-meter offset;
it is not a true apples-to-apples same-origin comparison as it might appear.

## 4. Units

Both axes are meters on both plots — confirmed three ways:
1. Labels rendered directly on the canvas: `'X (m)'`, `'Y (m)'` (visualize_effects.py:297-300).
2. Radar data range (0–100, −80–80) matches the K-Radar cube's documented meter-scale ROI
   (`arr_x_cb`/`arr_y_cb`, 0.4 m bins, in `datasets/kradar_detection_v1_0.py:108-110`).
3. Lidar `.pcd` fields are the Ouster driver's native XYZ output, which is meters by Ouster
   SDK convention (no unit conversion happens anywhere in `load_lidar_pcd`).

## 5. Origin placement, and the loss-partial-zeroout diagnostic's assumption

`loss-partial-zeroout-visibility-diagnostic.md` assumes zeroed-out points land at
"world-origin (0,0,0)". Given the above: for the **radar** plot, (0,0,0) is at the radar
sensor's own location — consistent with that assumption if "world origin" is read as "sensor
origin," which is what the loss-injection code operates on (it zeroes raw `rdr_sparse` /
`ldr64` array rows in place, i.e. in whatever frame those arrays are already in). For the
**lidar** plot specifically, since `visualize_effects.py` never applies the radar-lidar
calib shift, a zeroed lidar point collapses to the *lidar sensor's* own mounting location,
not the radar's — the diagnostic's "world-origin" language is still correct in the sense
that it's a fixed, non-physical point distinct from any real return, but it is a different
physical point in the two plots. Anyone using both plots to visually judge "the zeroed
points collapsed to the sensor" should keep in mind that's two different sensors' zero
points, roughly 2.5 m apart in the seq 1 example frame.

## 6. Are axis labels actually present in the current PNGs?

**Yes — contrary to what's often a documentation gap, labels are present.** Confirmed by
reading the code path that unconditionally runs whenever there are points to plot
(`visualize_effects.py:296-300`, quoted in §1): `'X (m)'` centered under the plot, `'Y (m)'`
along the left edge, plus tick gridlines with numeric labels at 7 positions per axis spanning
`ax_limits` (`visualize_effects.py:280-294`). This only skips if `pts_xy is None or
len(pts_xy) == 0` (the `NO DATA` branch, line 261-263), which doesn't apply to any of the
three clean frames (radar: 150000 pts pre-filter; lidar and radar both report non-zero point
counts in the title text baked into the image, e.g. `CLEAN | seq001_rdr033 | N pts`).

So there is no missing-labels gap here. What *is* worth flagging as a follow-up (not
implemented, just noted): the two plots' identical-looking axis conventions obscure the
origin mismatch in §3 — a one-line annotation on each PNG (or in the HTML index) noting
"origin = radar sensor" / "origin = raw LiDAR sensor, uncalibrated" would prevent the
side-by-side misread described above. This is a documentation/UX recommendation only; no
code change was made as part of this investigation.

## Summary table

| | Radar (`radar_clean.png`) | Lidar (`lidar_clean.png`) |
|---|---|---|
| Source array | `rdr_sparse` (`sprdr_*.npy`, preprocessed sparse points) | `ldr64` (raw `os2-64_*.pcd`, parsed directly, **no calib applied**) |
| X axis = column | 0 | 0 |
| Y axis = column | 1 | 1 |
| X physical meaning | forward/range from radar | forward/range from raw LiDAR sensor |
| Y physical meaning | lateral, left positive, from radar | lateral, left positive, from raw LiDAR sensor |
| Units | meters | meters |
| Axis limits | data min/max ±3 m, radar frame | data min/max ±3 m, lidar frame |
| Origin | radar sensor mounting point | raw LiDAR (os2-64) sensor mounting point — **not** shifted into radar frame |
| Aspect ratio | equal (shared scale factor) | equal (shared scale factor) |
| Axis labels rendered in PNG | yes (`X (m)`, `Y (m)`, tick grid) | yes (same) |
| Shares frame with the other modality | **No** — offset by per-sequence radar-lidar calib translation (seq 1: ≈(−2.54, +0.3, +0.7) m), never applied by this script |
