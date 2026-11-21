# K-Radar Visibility Pipeline — Issue Summary

> Generated after code audit of `pipeline.py`, `lidar_visibility.py`,
> `camera_visibility.py`, and `calibration.py` against the §3–§7 spec.
> Issues are ordered by fix priority (blocking → correctness → robustness).

---

## Priority 1 — Blocking: Will produce wrong output silently

### ISSUE-01 · `lidar_visibility.py` — dual-sensor return uses same point cloud for both sensors

**File:** `lidar_visibility.py` → `calculate_lidar_visibility()`  
**Symptom:** `lidar64_points_count` and `lidar128_points_count` are always identical. SMK-12, SMK-15, VER-02, VER-03 will fail.  
**Root cause:** The function fills both OS2-64 and OS1-128 slots from the single `points` argument:
```python
lidar64_points_count[i] = count
lidar128_points_count[i] = count  # ← always equal to lidar64
```
`pipeline.py` calls the function twice (once per cloud) but reads OS1-128 from slots `[3][0], [4][0], [5][0]`, which are just copies of the OS2-64 slots from that same call.

**Fix:** Simplify to a single-sensor return `(visible, points_count, sparsity_score)` per bbox. Call it once for OS2-64 and once for OS1-128 in `pipeline.py`, reading `[0][0], [1][0], [2][0]` each time.

---

### ISSUE-02 · `pipeline.py` — `cam_*_proj_x/y` not nulled when `cam_*_visible=False`

**File:** `pipeline.py` → `compute_visibility_for_frame()`  
**Symptom:** VER-11 ("invisible rows have NULL projection") will fail for objects that have `z_cam > 0` but zero clipped area (outside FOV but in front of camera).  
**Root cause:** `cam_*_visible` is derived from `cam_scores[direction] > 0` (area-based check). `cam_*_proj_x/y` is set from a separate `project_point_to_image` call that only checks `z_cam > 0`. These two conditions can disagree.  
**Fix:** After computing all projections, enforce:
```python
if not cam_front_visible:
    cam_front_proj_x = None
    cam_front_proj_y = None
# repeat for left, right, rear
```

---

### ISSUE-03 · `pipeline.py` — `_bbox_voxels_from_annotation` ignores object rotation

**File:** `pipeline.py` → `_bbox_voxels_from_annotation()`  
**Symptom:** Radar sparsity scores for angled objects (e.g. oncoming traffic, `theta ≈ ±π`) are wrong — the voxel bbox is axis-aligned using raw half-extents, not the rotated footprint. Affects VER-08, SMK-14 reliability.  
**Root cause:**
```python
z_min, y_min, x_min = _world_to_voxel(cx - hl, cy - hw, cz - hh)
z_max, y_max, x_max = _world_to_voxel(cx + hl, cy + hw, cz + hh)
```
This is only correct when `theta == 0`. For any other heading, the true AABB is larger.  
**Fix:** Compute all 8 rotated corners (same logic as `_obj_corners()`), then take `min/max` in world space before converting to voxels:
```python
corners = _obj_corners(obj)
voxels = [_world_to_voxel(*c) for c in corners]
z_min = min(v[0] for v in voxels); z_max = max(v[0] for v in voxels)
y_min = min(v[1] for v in voxels); y_max = max(v[1] for v in voxels)
x_min = min(v[2] for v in voxels); x_max = max(v[2] for v in voxels)
```

---

## Priority 2 — Correctness: Output is produced but values are unreliable

### ISSUE-04 · `pipeline.py` — radar voxel grid mapping unverified against actual `.mat` files

**File:** `pipeline.py` — top-level constants  
**Symptom:** If the actual `radar_zyx_cube` `.mat` files use a different axis order, range, or grid resolution than the hardcoded constants, all radar sparsity scores will be noise. No error is raised.  
**Root cause:** The constants are assumed, not confirmed:
```python
RADAR_Z_MIN, RADAR_Z_MAX = -30.0, 30.0
RADAR_Y_MIN, RADAR_Y_MAX = -80.0, 80.0
RADAR_X_MIN, RADAR_X_MAX = 0.0, 100.0
RADAR_GRID_Z, RADAR_GRID_Y, RADAR_GRID_X = 301, 801, 500
```
**Fix:** Before running the pipeline, load one `.mat` file and inspect:
```python
import scipy.io
mat = scipy.io.loadmat("cube_00001.mat")
key = [k for k in mat if not k.startswith("__")][0]
print(mat[key].shape)  # confirm matches (301, 801, 500)
```
Cross-reference against the K-Radar paper / README for documented grid specs. Update constants if they differ.

---

### ISSUE-05 · `lidar_visibility.py` — FOV check uses bbox corner coordinates, not object center

**File:** `lidar_visibility.py` → `calculate_lidar_visibility()`  
**Symptom:** `lidar64_visible` / `lidar128_visible` can be `False` for objects clearly within sensor range, because the check compares raw bbox `[xmin, xmax, ymin, ymax]` bounds against the FOV limits — an object straddling the FOV boundary (e.g. at `x=49m` with `hl=2m` giving `xmin=47`) will fail the check `bbox[0] >= fov[0]` if `fov[0]=50`.  
**Root cause:**
```python
if (bbox[0] >= sensor_metadata['os2_fov'][0] and
    bbox[1] <= sensor_metadata['os2_fov'][1] ...):
    lidar64_visible[i] = True
```
This requires the *entire* bbox to be inside the FOV, not just the center.  
**Fix:** Check object center point (midpoint of bbox) against FOV, or use `bbox[0] <= fov[1] and bbox[1] >= fov[0]` (overlap test) instead of containment.

---

### ISSUE-06 · `camera_visibility.py` — `project_point_to_image` clips `u, v` before returning

**File:** `camera_visibility.py` → `project_point_to_image()`  
**Symptom:** The returned `u, v` values are always within `[0, 1279] × [0, 719]` even for points that project outside the image. This masks out-of-bounds projections and makes VER-10 trivially pass while hiding real errors.  
**Root cause:**
```python
u = np.clip(u, 0, HALF_WIDTH - 1)
v = np.clip(v, 0, HALF_HEIGHT - 1)
```
**Fix:** Remove the clip from `project_point_to_image`. Clipping (if needed) should happen only in `calculate_visibility_score` when computing the 2D bbox area, not in the raw projection function. The pipeline reads `u, v` as stored proj_x/y — these must be the true projected values.

---

## Priority 3 — Robustness: Will crash rather than degrade gracefully

### ISSUE-07 · `calibration.py` — missing calibration file raises unhandled `FileNotFoundError`

**File:** `calibration.py` → `load_camera_calibration()`  
**Symptom:** If a sequence doesn't have a calibration pickle at the hardcoded path, the entire pipeline crashes mid-run rather than skipping that sequence with `cam_*_visible=False`.  
**Fix:** Wrap in try/except in `pipeline.py` at the frame level (already has a broad `except Exception` — but the calibration is loaded per-object inside `calculate_camera_visibility`, so a crash inside `cam_scores = calculate_camera_visibility(...)` will silently skip the whole object row via the outer `except`). Better: pre-check calibration availability per sequence at the top of the sequence loop and skip/warn early.

---

### ISSUE-08 · `pipeline.py` — `pl.DataFrame(all_rows)` will fail if `all_rows` is empty

**File:** `pipeline.py` → `run()`  
**Symptom:** If all label files fail to parse (e.g. wrong `dataset_root`), `all_rows = []` and `pl.DataFrame([])` raises a `ValueError`.  
**Fix:**
```python
if not all_rows:
    print("Warning: no rows produced. Check dataset_root and sequence_ids.")
    return pl.DataFrame()
df = pl.DataFrame(all_rows)
```

---

## Summary Table

| ID | File | Severity | Breaks Tests | Fix Size |
|----|------|----------|-------------|----------|
| ISSUE-01 | `lidar_visibility.py` | **Blocking** | SMK-12, SMK-15, VER-02, VER-03 | Small — refactor return signature |
| ISSUE-02 | `pipeline.py` | **Blocking** | VER-11 | Small — add 4 null-enforcement lines |
| ISSUE-03 | `pipeline.py` | **Blocking** | SMK-14, VER-08 | Small — reuse `_obj_corners()` |
| ISSUE-04 | `pipeline.py` constants | Correctness | SMK-14, VER-06/07/08 | Verify only — no code change if grid matches |
| ISSUE-05 | `lidar_visibility.py` | Correctness | VER-02, VER-03, VER-04 | Small — change containment to overlap/center check |
| ISSUE-06 | `camera_visibility.py` | Correctness | VER-10, stored proj values | Small — remove `np.clip` from projection |
| ISSUE-07 | `calibration.py` / `pipeline.py` | Robustness | None (crash, not wrong value) | Small — add early check per sequence |
| ISSUE-08 | `pipeline.py` | Robustness | None (crash on empty) | Trivial — guard before `pl.DataFrame()` |

---

## Recommended Fix Order

```
ISSUE-01  →  ISSUE-02  →  ISSUE-03   # fix these first; run SMK-17 to confirm clean parquet
ISSUE-04                               # verify manually against one .mat file
ISSUE-05  →  ISSUE-06                 # correctness pass
ISSUE-07  →  ISSUE-08                 # robustness pass
```

After ISSUE-01/02/03 are fixed, run:
```bash
uv run pytest tests/test_smoke.py -v --timeout=300
```
Then fill in `tests/test_verify.py` once a clean Parquet is produced.
