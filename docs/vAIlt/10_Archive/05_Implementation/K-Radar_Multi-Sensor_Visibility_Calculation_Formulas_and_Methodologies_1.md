---
title: K-Radar Multi-Sensor Visibility Calculation Formulas and Methodologies
type: concept
source: home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/K-Radar_Multi-Sensor_Visibility_Calculation_Formulas_and_Methodologies.md
date: 2026-07-02
tags: [05 Implementation]
---
---
title: K-Radar Multi-Sensor Visibility Calculation Formulas and Methodologies
type: concept
source: home/adhish/Productivity/AMSCUP/docs/VISIBILITY_FORMULAS_AND_METHODS.md
date: 2026-07-02
tags: [05 Implementation]
---
# K-Radar Multi-Sensor Visibility Calculation Formulas and Methodologies

## 1. Executive Summary

This document provides a comprehensive technical specification of the visibility calculation methodologies implemented in the K-Radar multi-sensor visibility analysis pipeline. The pipeline computes per-object visibility scores for seven sensors across the K-Radar dataset:

- **Radar (R):** REINA-4ST 4D Radar (forward-only, 107° azimuth × 37° elevation, 0–118 m range)
- **LiDAR 64 (L1):** Ouster OS2-64 (64 channels, 33.2° vertical FOV, 0.35° horizontal resolution)
- **LiDAR 128 (L2):** Ouster OS1-128 (128 channels, 44.5° vertical FOV, 0.17° horizontal resolution)
- **Camera Front (CF):** ZED2i stereo camera (1280×720 per half)
- **Camera Left (CL):** ZED2i stereo camera (1280×720 per half)
- **Camera Right (CR):** ZED2i stereo camera (1280×720 per half)
- **Camera Rear (CRE):** ZED2i stereo camera (1280×720 per half)

**Why visibility scoring matters:** In multi-sensor autonomous driving datasets, annotated objects may be "identified" by only a subset of sensors (indicated by the `sensor_identify` field in `info_label_rev2/`). Visibility scores provide a continuous, physics-based measure of how detectable each object is by each sensor, independent of whether it was actually used for identification. This enables:
- Sensor fusion research (understanding complementary coverage)
- Robustness evaluation (performance degradation under occlusion/weather)
- Dataset bias analysis (which objects are systematically under-represented)

The methodology follows the recommendations in `04_visibility_methodology.md`:
- **Radar:** Method B — SNR-weighted power density on `radar_zyx_cube` (Doppler-collapsed 3D cube)
- **LiDAR:** Method A+B — CPU point-in-box count → expected-density normalization
- **Camera:** Method B — 8-corner projection → 2D area × centrality score (occlusion check optional, flag-gated)

---

## 2. LiDAR Visibility Calculation

### 2.1 Formulas

#### Raw Point Count (Method A)
```
N_points = Σᵢ [Pᵢ ∈ bbox]
```
Where:
- `Pᵢ` = i-th LiDAR point in the sensor frame (x, y, z coordinates)
- `bbox` = axis-aligned bounding box of the rotated object annotation in meters
- `[·]` = Iverson bracket (1 if condition true, 0 otherwise)
- `N_points` = integer count of points falling inside the bbox

**Units:** `N_points` is dimensionless (count)

#### Expected Point Density (Method B)
The theoretical expected point count for a 1 m³ volume at the sensor's angular resolution:

```
E = (N_channels × VFOV / 360°) × (360° / HRES)
```

Where:
- `N_channels` = number of vertical channels (64 for OS2-64, 128 for OS1-128)
- `VFOV` = vertical field of view in degrees (33.2° for OS2-64, 44.5° for OS1-128)
- `HRES` = horizontal angular resolution in degrees (0.35° for OS2-64, 0.17° for OS1-128)
- `E` = expected point count per cubic meter (points/m³)

**Derived constants (from `config.py`):**
```
_EXPECTED_OS2 = (64 × 33.2 / 360) × (360 / 0.35) ≈ 6,074 points/m³
_EXPECTED_OS1 = (128 × 44.5 / 360) × (360 / 0.17) ≈ 33,459 points/m³
```

#### Sparsity Score (Normalized Visibility)
```
S_lidar = clip(N_points / (E × V_bbox), 0, 1)
```

Where:
- `V_bbox` = bbox volume = (2 × half_length) × (2 × half_width) × (2 × half_height) in m³
- `E` = expected point density for the sensor (points/m³)
- `S_lidar` = normalized visibility score in [0, 1]

**Note:** The volume normalization is implicit in the pipeline because `expected_density` is passed as the total expected points for the bbox (not per m³). The actual implementation computes:
```
sparsity_score = count / expected_density
```
where `expected_density = E × V_bbox` is pre-computed per sensor type.

### 2.2 Methodology

**Approach:** CPU-based axis-aligned point-in-box test with expected-density normalization.

**Key steps:**
1. **Coordinate frame:** Object annotations are in the radar coordinate frame. Both LiDARs (OS2-64 and OS1-128) share a common coordinate system calibrated to the radar frame via `info_calib/` transforms. The pipeline assumes point clouds are already in the radar frame.
2. **BBox construction:** For each object, the 8 corners of the oriented 3D bounding box are computed in world coordinates using the annotation's center (x, y, z), half-dimensions (length_half, width_half, height_half), and heading angle (theta). The axis-aligned bounding box (AABB) enclosing these 8 corners is then used for the point-in-box test. This handles rotation correctly (fixed in `pipeline.py` ISSUE-03).
3. **Point-in-box test:** Vectorized NumPy masking checks which points fall within `[xmin, xmax] × [ymin, ymax] × [zmin, zmax]`.
4. **Visibility gating:** An object is considered `lidar*_visible = True` if:
   - `points_count > 0` (at least one point in bbox)
   - Object center is within sensor FOV: `[-200, 200] × [-200, 200]` meters (effectively no cutoff)
   - Object center is within sensor range: `[0, 120]` meters
5. **Sensor disambiguation:** The `sensor_identify` field uses `L1` (OS2-64), `L2` (OS1-128), and `L` (unspecified). For `L`, the pipeline sets both `lidar64_visible` and `lidar128_visible` to the logical OR of the two (see `pipeline.py` lines 250–254). This satisfies VER-04 (≥95% match).

**Handling multiple LiDAR sensors:** The pipeline calls `calculate_lidar_visibility()` twice per frame — once with OS2-64 points and `_EXPECTED_OS2`, once with OS1-128 points and `_EXPECTED_OS1`. Both produce independent `points_count` and `sparsity_score` columns.

### 2.3 Scoring Mechanism

| Parameter | Value | Description |
|-----------|-------|-------------|
| `lidar*_visible` | `bool` | `True` iff `count > 0 AND center_in_fov AND center_in_range` |
| `lidar*_points_count` | `int` | Raw point count in bbox (≥ 0) |
| `lidar*_sparsity_score` | `float` | `count / expected_density`, clipped to [0, 1] |

**Thresholds:**
- Minimum point count for `visible=True`: **1** (any non-zero count)
- Score range: **[0, 1]** (0 = no points / outside FOV, 1 = actual ≥ expected density)
- Distance cutoff: **120 m** (objects beyond are `visible=False` regardless of points)

**Occlusion handling:** None in the current implementation. The point-in-box test counts all points geometrically inside the bbox, regardless of whether they belong to the object or an occluder. This is a known limitation.

**Weather impact:** Not explicitly modeled in the score formula. Weather effects are captured implicitly — adverse weather (rain, sleet, snow) reduces `N_points` which lowers the score. VER-25 verifies this empirically.

---

## 3. Camera Visibility Calculation

### 3.1 Formulas

#### Projection Pipeline
For each of the 8 corners of the 3D bounding box:

```
P_camera = T_radar2camera × P_radar
P_image = K × P_camera[0:3] / P_camera[2]
```

Where:
- `P_radar` = (x, y, z, 1)ᵀ homogeneous coordinates in radar frame
- `T_radar2camera` = 4×4 extrinsic matrix (radar → camera frame)
- `K` = 4×4 camera intrinsic matrix (top-left 3×3 contains fx, fy, cx, cy)
- `P_camera` = point in camera frame (X, Y, Z, 1)ᵀ; Z = depth
- `P_image` = (u, v) pixel coordinates (raw, unclipped)

**Implementation:** `camera_visibility.py::project_point_to_image()` (lines 25–56)

#### Clipped Projected Area
After projecting all 8 corners, compute the 2D axis-aligned bounding box in image coordinates:

```
u_min = min(u₁...u₈),  u_max = max(u₁...u₈)
v_min = min(v₁...v₈),  v_max = max(v₁...v₈)
```

Clip to image bounds (per stereo half: 1280 × 720):
```
u_min_c = max(0, u_min)
v_min_c = max(0, v_min)
u_max_c = min(1280, u_max)
v_max_c = min(720, v_max)
```

Clipped area:
```
A_clipped = max(0, u_max_c - u_min_c) × max(0, v_max_c - v_min_c)
```

Full image area:
```
A_image = 1280 × 720 = 921,600 pixels
```

#### Centrality Metric
Projected center of clipped bbox:
```
u_c = u_min_c + (u_max_c - u_min_c) / 2
v_c = v_min_c + (v_max_c - v_min_c) / 2
```

Normalized distance to image center (640, 360):
```
d_norm = (|u_c - 640| + |v_c - 360|) / (1280 + 720) = (|u_c - 640| + |v_c - 360|) / 2000
```

Centrality score (1 at center, 0 at corners):
```
C = 1 - d_norm
```

#### Final Visibility Score (Method B)
```
V_camera = w₁ × (A_clipped / A_image) + w₂ × C
```

Where:
- `w₁ = 0.7` (area weight, `CAM_W1` in `config.py`)
- `w₂ = 0.3` (centrality weight, `CAM_W2` in `config.py`)
- `V_camera ∈ [0, 1]`

### 3.2 Methodology

**Approach:** 8-corner projection → 2D axis-aligned bbox → area fraction + centrality weighting.

**Key steps:**
1. **Corners computation:** `_obj_corners()` in `pipeline.py` (lines 99–114) computes the 8 world-frame corners of the rotated 3D bbox using the annotation's center, half-dimensions, and theta.
2. **Projection:** Each corner is projected to each camera using the calibration loaded from `info_calib/T_params_seq/{seq}/` pickle files. The calibration provides `camera_intrinsics` (4×4 K matrix) and `radar2camera` (4×4 extrinsic).
3. **Stereo handling:** Each direction (front/left/right/rear) has **two** stereo sub-cameras (e.g., `front0` and `front1`). The pipeline computes the visibility score for both and takes the **maximum** (`camera_visibility.py` line 126).
4. **Visibility gating:** `cam_*_visible = True` iff:
   - All 8 corners have `z_cam > 0` (object in front of camera, not behind)
   - `A_clipped > 0` (projected bbox overlaps image)
5. **Projection coordinates:** `cam_*_proj_x/y` store the projected **center point** (object center, not bbox center) only when `visible=True` (ISSUE-02). Set to `None` otherwise.

**Truncation handling:** The clipping step naturally handles partial visibility at image edges — the clipped area fraction decreases as the object moves toward the edge, reducing the score proportionally.

### 3.3 Scoring Mechanism

| Parameter | Value | Description |
|-----------|-------|-------------|
| `cam_*_visible` | `bool` | `True` iff all corners `z_cam > 0` AND `A_clipped > 0` |
| `cam_*_proj_x/y` | `float` or `None` | Projected center (u, v) in pixels; `None` if not visible |
| `cam_*_visibility_score` | `float` | `0.7 × (A_clipped/A_image) + 0.3 × C` in [0, 1] |

**Thresholds:**
- Score range: **[0, 1]** (0 = not visible, 1 = fills image center)
- Minimum clipped area for `visible=True`: **> 0 pixels** (any overlap)
- Behind-camera rejection: **any corner with `z_cam ≤ 0` → score = 0**

**Occlusion handling:** **Not implemented in primary method (Method B).** An optional Method C (LiDAR depth-buffer occlusion discount) is specified in `04_visibility_methodology.md` but gated behind a config flag (`enable_occlusion_check=False` by default). The current CPU-only build does not implement it.

**Distance-based effects:** Distance is captured implicitly:
- Farther objects → smaller projected area → lower area term
- Farther objects → often nearer image center (for forward-facing cameras) → higher centrality
- Net effect: `V_camera` generally decreases with distance (verified by VER-09)

---

## 4. Radar Visibility Calculation

### 4.1 Formulas

#### Power to dB Conversion
For each valid cell in the `radar_zyx_cube` (Z×Y×X grid):
```
P_dB = 10 × log₁₀(P_linear)   for P_linear > 0
P_dB = -100 dB                 for P_linear ≤ 0 (sentinel/invalid)
```

#### Per-Frame Noise Floor
```
N_dB = median(P_dB[valid_cells])
```
Where `valid_cells` = all cells with `P_linear > 0` in the entire cube.

#### SNR-Weighted Power Density (Method B)
For the subset of cells within the object's bbox voxel region:
```
SNR_cell = max(0, P_dB - N_dB)   for each cell in bbox
Raw_score = mean(SNR_cell)        (average SNR in dB)
Score = clip(Raw_score / DB_HEADROOM, 0, 1)
```

Where:
- `DB_HEADROOM = 20.0` dB (defined in `radar_visibility.py` line 16)
- `Raw_score` = mean excess power above noise floor in dB
- `Score` = normalized visibility score in [0, 1]

**Full formula:**
```
V_radar = clip( (1/|B|) × Σ_{c∈B} max(0, 10×log₁₀(P_c) - median(10×log₁₀(P_valid))) / 20 , 0, 1 )
```

Where `B` = set of voxels in the object's bbox region.

#### FOV and Range Gating (Independent of Score)
```
radar_fov_in = |azimuth| ≤ 53.5° AND |elevation| ≤ 18.5°
radar_range_in = √(x² + y² + z²) ≤ 118 m
radar_visible = radar_fov_in AND radar_range_in
```

Where:
- `azimuth = atan2(y, x)` in degrees
- `elevation = atan2(z, √(x²+y²))` in degrees
- `RADAR_FOV_AZIMUTH_DEG = 107°`, `RADAR_FOV_ELEVATION_DEG = 37°` (from `config.py`)
- `RADAR_MAX_RANGE_M = 118.0 m`

### 4.2 Methodology

**Approach:** SNR-weighted mean power density on the Doppler-collapsed `radar_zyx_cube`.

**Key steps:**
1. **Data source:** Uses `radar_zyx_cube/` (pre-processed 3D cube, Doppler collapsed) — **NOT** the full 4DRT (64M cells/frame). This satisfies the memory-efficiency constraint (§8.1).
2. **Grid mapping:** World coordinates (meters) → voxel indices via linear interpolation over fixed ROI:
   - X: [0, 100] m → 250 voxels
   - Y: [-80, 80] m → 400 voxels
   - Z: [-30, 30] m → 150 voxels
   (Defined in `pipeline.py` lines 50–53 as `RADAR_*_MIN/MAX` and `RADAR_GRID_*`)
3. **BBox voxelization:** The 8 rotated corners are converted to voxel indices, and the AABB in voxel space is used to extract the subcube (`pipeline.py` lines 117–134).
4. **Noise floor estimation:** Per-frame median of **all valid cells** (linear power > 0) in the entire cube. Sentinel values (-1.0 or ≤0) are masked out before conversion to dB.
5. **Score computation:** Mean of `max(0, P_dB - noise_floor_dB)` over bbox voxels, normalized by 20 dB headroom.

**Why Method B over alternatives:**
- Method A (binary threshold): Ignores range-dependent noise floor → far objects unfairly zeroed
- Method C (full 4DRT): Violates memory constraint (64M cells/frame)
- Method B: Adapts per-frame, continuous, stays within zyx-cube budget

### 4.3 Scoring Mechanism

| Parameter | Value | Description |
|-----------|-------|-------------|
| `radar_visible` | `bool` | `radar_fov_in AND radar_range_in` |
| `radar_fov_in` | `bool` | Center within 107° azimuth × 37° elevation cone |
| `radar_range_in` | `bool` | Center within 0–118 m |
| `radar_sparsity_score` | `float` | SNR-weighted density normalized to [0, 1] |

**Thresholds:**
- `DB_HEADROOM = 20 dB`: Objects with mean SNR ≥ 20 dB above noise floor score 1.0
- Score = 0 when: outside FOV/range, cube missing, or mean SNR ≤ noise floor
- Score range: **[0, 1]**

**All-weather capability:** Radar's all-weather nature is **not explicitly modeled** in the score formula. However, because radar returns persist in rain/fog/snow while LiDAR degrades, the radar score naturally remains higher in adverse weather for the same object. VER-26 verifies radar variance across weather < LiDAR variance.

---

## 5. Overall / Fused Visibility Score

### 5.1 Fusion Formula

The pipeline computes **per-sensor scores independently** and then derives aggregated metrics:

```
num_sensors_visible = Σ I(sensor_visible)
primary_sensor = argmax_{s: visible} (sensor_score[s])
```

Where `I(·)` is the indicator function (1 if True, 0 if False).

**There is no explicit fused visibility score column** in the output schema. The fusion is implicit in:
- `num_sensors_visible` (count of sensors with `visible=True`)
- `primary_sensor` (the visible sensor with highest score)

### 5.2 Sensor Weighting Rationale

The `primary_sensor` selection uses **raw score comparison** across sensors. This means:

| Sensor | Typical Score Range | Weighting Implication |
|--------|---------------------|----------------------|
| Radar | [0, 1] (SNR-based) | High scores for strong reflectors, low for weak |
| LiDAR 64 | [0, 1] (density ratio) | High scores for close/dense objects |
| LiDAR 128 | [0, 1] (density ratio) | Generally higher than LiDAR 64 (more channels) |
| Cameras | [0, 1] (area × centrality) | High scores for large, central projections |

**No explicit weighting factors** are applied — the sensor with the highest computed score wins. This has implications:
- **Close objects:** LiDAR 128 typically wins (high point density)
- **Far objects:** Radar may win (LiDAR sparse, radar SNR adapts)
- **Side objects:** Left/right cameras win (front/rear see nothing)
- **Sensor failure:** If a sensor file is missing, its score = 0, visible = False → automatically excluded from `primary_sensor` selection

**Handling complete sensor failure:** The pipeline degrades gracefully — missing sensor files → `visible=False, score=0.0` (logged warning, no crash). The remaining sensors determine `primary_sensor`.

---

## 6. Methodology Comparison and Selection Rationale

| Methodology | Sensor | Pros | Cons | Selected? | Reason |
|-------------|--------|------|------|-----------|--------|
| **A. Binary cell-count density** | Radar | Cheap, one pass, easy to vectorize | Single global threshold ignores range-dependent noise floor; far objects unfairly zeroed | ❌ Rejected | Fails SMK-14 (monotonic distance decrease) because fixed threshold doesn't adapt to noise floor |
| **B. SNR-weighted power density** | Radar | Range-adaptive (per-frame noise floor), continuous, one pass, satisfies SMK-14 | Slightly more sensitive to multipath/clutter | ✅ **Selected** | Best balance of accuracy, cost, and test compliance; documented in `04_visibility_methodology.md` §4.1 |
| **C. Full 4DRT integration** | Radar | Most physically complete (Doppler retained, enables motion checks) | Violates memory constraint (64M cells/frame); out of scope for CPU-only build | ❌ Rejected (optional) | Kept as `--full-tesseract` flag for future research only |
| **A. Raw point count (GPU `points_in_boxes_gpu`)** | LiDAR | Zero new code, fast, well-tested, reuses existing pipeline | Raw count not a normalized visibility score; distance-dependent | ⚠️ Partial | Used for `lidar*_points_count` column only (Method A) |
| **B. Count / expected-density ratio** | LiDAR | Range- and channel-invariant 0–1 score; distinguishes sparse-but-expected from sparse-and-anomalous | Expected-count model is approximate (ignores partial occlusion, ground strikes) | ✅ **Selected** | Primary `lidar*_sparsity_score`; satisfies VER-06/07; documented in `04_visibility_methodology.md` §4.2 |
| **C. Voxel occupancy ratio** | LiDAR | Captures spatial coverage (not just count) | Extra voxelization pass; resolution hyperparameter; marginal benefit over B | ❌ Rejected | Cost not justified; weather dominates sparsity variance (VER-25) |
| **A. Center-point projection only** | Camera | Trivial (one matrix-vector op) | Boolean only; no continuous score; fails SMK-16 | ❌ Rejected | Cannot produce `cam_*_visibility_score` |
| **B. 8-corner projection → area + centrality** | Camera | Cheap (8 matmuls + 2D hull), continuous, size- and centrality-aware, satisfies SMK-16 | No occlusion handling | ✅ **Selected** | Primary `cam_*_visibility_score`; passes all smoke/verification tests |
| **C. B + LiDAR depth-buffer occlusion** | Camera | Handles real occlusion (meaningful "visible" vs "in FOV") | Adds per-camera per-frame LiDAR projection + sparse z-test; depth sparsity → false negatives | ⚠️ Optional (flag-gated) | Not required to pass test suite; adds real cost at full-dataset scale |

---

## 7. Thresholds and Decision Boundaries

| Parameter | Value | Description | Rationale / Source |
|-----------|-------|-------------|-------------------|
| **Radar** | | | |
| `RADAR_FOV_AZIMUTH_DEG` | 107° | Azimuth FOV (±53.5°) | K-Radar spec / `config.py` |
| `RADAR_FOV_ELEVATION_DEG` | 37° | Elevation FOV (±18.5°) | K-Radar spec / `config.py` |
| `RADAR_MAX_RANGE_M` | 118.0 m | Maximum detection range | K-Radar spec / `config.py` |
| `DB_HEADROOM` | 20.0 dB | SNR headroom for score=1.0 | `radar_visibility.py` line 16; empirical |
| **LiDAR** | | | |
| `OS2_64_CHANNELS` | 64 | Vertical channels | `config.py` |
| `OS2_64_VFOV_DEG` | 33.2° | Vertical FOV | `config.py` (Ouster OS2-64 spec) |
| `OS2_64_HRES_DEG` | 0.35° | Horizontal resolution | `config.py` |
| `OS1_128_CHANNELS` | 128 | Vertical channels | `config.py` |
| `OS1_128_VFOV_DEG` | 44.5° | Vertical FOV | `config.py` (Ouster OS1-128 spec) |
| `OS1_128_HRES_DEG` | 0.17° | Horizontal resolution | `config.py` |
| `_LIDAR_FOV` | [-200, 200] m | X/Y FOV limits (effectively none) | `pipeline.py` line 65 |
| `_LIDAR_RANGE` | [0, 120] m | Range limits | `pipeline.py` line 66 |
| Min points for `visible=True` | 1 | Any non-zero count | `lidar_visibility.py` line 102 |
| **Camera** | | | |
| `HALF_WIDTH` | 1280 px | Image width per stereo half | `camera_visibility.py` line 17 |
| `HALF_HEIGHT` | 720 px | Image height per stereo half | `camera_visibility.py` line 18 |
| `CAM_W1` (area weight) | 0.7 | Weight for clipped area fraction | `config.py` / `camera_visibility.py` line 21 |
| `CAM_W2` (centrality weight) | 0.3 | Weight for centrality | `config.py` / `camera_visibility.py` line 22 |
| Min clipped area for `visible=True` | > 0 px | Any image overlap | `camera_visibility.py` line 94 |
| Behind-camera rejection | `z_cam ≤ 0` | Any corner behind camera → score=0 | `camera_visibility.py` line 78 |
| **Score Bins (implicit)** | | | |
| Poor visibility | [0.0, 0.3) | Very sparse / edge / occluded | Empirical; not hard-coded |
| Moderate visibility | [0.3, 0.7) | Partially visible, medium distance | Empirical |
| Good visibility | [0.7, 1.0] | Dense / large projection / central | Empirical |

---

## 8. Implementation Notes

### Key Functions and Classes

| File | Function/Class | Purpose | Key Lines |
|------|----------------|---------|-----------|
| `radar_visibility.py` | `compute_radar_sparsity_score()` | Core radar SNR-weighted density | 19–56 |
| `radar_visibility.py` | `radar_visibility()` | Batch compute for multiple bboxes | 59–61 |
| `lidar_visibility.py` | `calculate_lidar_visibility()` | Point-in-box + sparsity score (single sensor) | 54–106 |
| `lidar_visibility.py` | `read_pcd_file()` | PCD (.ped) point cloud loader | 19–51 |
| `camera_visibility.py` | `project_point_to_image()` | 3D→2D projection (radar→camera→image) | 25–56 |
| `camera_visibility.py` | `calculate_visibility_score()` | Area + centrality score for one camera | 59–105 |
| `camera_visibility.py` | `calculate_camera_visibility()` | Scores for all 4 cameras (max of stereo) | 108–127 |
| `calibration.py` | `get_camera_params()` | Load K, T_radar2camera from pickle | 19–32 |
| `pipeline.py` | `_obj_corners()` | 8 world-frame corners of rotated bbox | 99–114 |
| `pipeline.py` | `_bbox_voxels_from_annotation()` | Radar voxel AABB from rotated corners | 117–134 |
| `pipeline.py` | `_bbox_list_from_annotation()` | LiDAR AABB in meters | 137–144 |
| `pipeline.py` | `compute_visibility_for_frame()` | Per-frame orchestration | 161–387 |
| `pipeline.py` | `run()` | Public entry point | 393–489 |
| `parser.py` | `parse_label_file()` | Parse header + objects from .txt | 104–127 |
| `parser.py` | `parse_description_txt()` | Parse weather from description.txt | 140–163 |
| `data_loader.py` | `load_radar_cube()` | Load radar_zyx_cube .mat file | 9–27 |
| `data_loader.py` | `load_lidar_points()` | Load OS2-64 / OS1-128 .ped files | 64–76 |
| `data_loader.py` | `load_camera_image()` | Load stitched camera PNG | 79–95 |

### Dependencies
- **NumPy:** Core array operations, linear algebra
- **Polars:** DataFrame construction, Parquet I/O
- **SciPy:** `scipy.io.loadmat` for radar .mat files
- **OpenCV (cv2):** Camera image loading
- **Pickle:** Camera calibration loading

### Known Limitations / TODOs

1. **No GPU acceleration:** CPU point-in-box only; `points_in_boxes_gpu` (OpenPCDet) exists elsewhere in repo but not integrated.
2. **No occlusion handling for cameras:** Method C (LiDAR depth-buffer) is specified but not implemented.
3. **Approximate radar voxel mapping:** Linear interpolation over fixed ROI; may not perfectly align with calibration (see `kradar_visual_verification_spec.md` §9).
4. **Axis-aligned LiDAR bbox for point-in-box:** The rotated bbox is reduced to AABB for the point test; this over-counts points near corners when theta ≠ 0.
5. **Fixed expected-density model:** Ignores partial occlusion, ground returns, and beam divergence.
6. **Weather column:** Added in `pipeline.py` (WEATHER-01) but depends on `description.txt` format consistency.
7. **Sensor label ambiguity:** `L` (unspecified LiDAR) mapped to OR of both LiDARs; may not reflect ground truth.
8. **Radar grid constants:** Hard-coded in `pipeline.py`; runtime shape assertion guards against mismatch (ISSUE-04).

---

## 9. Verification and Smoke Tests

### Formula Verification (from `06_smoke_tests_scaffold.md`)

| Test ID | Formula Verified | Expected Behavior |
|---------|------------------|-------------------|
| **SMK-14** | Radar score vs distance | Close object (10m) score > far object (80m) score |
| **SMK-15** | LiDAR count OS1-128 ≥ OS2-64 | Same object, denser sensor yields ≥ count |
| **SMK-16** | Camera score center vs edge | Center-of-frame object score > edge-of-FOV object |

### Verification Tests (from `07_verification_tests_scaffold.md`)

| Test ID | Category | Check |
|---------|----------|-------|
| **VER-06/07** | LiDAR distance correlation | Median points decrease with distance (R² > 0.5) |
| **VER-08** | Radar distance correlation | Monotonic decrease with distance (R² > 0.3) |
| **VER-09** | Camera distance correlation | Negative correlation for visible objects (p < 0.05) |
| **VER-10** | Camera projection bounds | Visible → 0≤proj_x<1280, 0≤proj_y<720 (100%) |
| **VER-11** | Camera projection nulls | Invisible → proj_x/proj_y are NULL (100%) |
| **VER-19** | Non-negative scores | All scores ≥ 0 |
| **VER-20** | Non-negative point counts | All counts ≥ 0 |
| **VER-25** | Weather impact (LiDAR) | Median points lower in rain/sleet/snow vs clear (p < 0.05) |
| **VER-26** | Weather impact (radar vs LiDAR) | Radar score variance < LiDAR score variance across weather |

### Manual Verification Steps (from `kradar_visual_verification_spec.md`)

1. **Select 5 diverse instances** covering weather, sensor count, distance, class
2. **Render per-instance figures** with:
   - Radar: max-projection heatmap + bbox overlay
   - LiDAR: 3D scatter + in-box points (red) + wireframe (blue)
   - Camera: stitched image + projected 8 corners + center dot
3. **Compare expected vs observed:** Does `radar_sparsity_score` reflect actual SNR? Does `lidar*_points_count` match red points? Does projected bbox align with object?

---

## Source Citations

| Section | Primary Source |
|---------|----------------|
| Executive Summary | `04_visibility_methodology.md` (header), `kradar_visibility_analysis_prompt.md` §1 |
| LiDAR Formulas | `04_visibility_methodology.md` §4.2, `lidar_visibility.py`, `pipeline.py` lines 56–62 |
| LiDAR Methodology | `04_visibility_methodology.md` §4.2, `lidar_visibility.py`, `pipeline.py` lines 215–247 |
| Camera Formulas | `04_visibility_methodology.md` §4.3, `camera_visibility.py`, `config.py` lines 22–24 |
| Camera Methodology | `04_visibility_methodology.md` §4.3, `camera_visibility.py`, `pipeline.py` lines 274–314 |
| Radar Formulas | `04_visibility_methodology.md` §4.1, `radar_visibility.py`, `pipeline.py` lines 49–53 |
| Radar Methodology | `04_visibility_methodology.md` §4.1, `radar_visibility.py`, `pipeline.py` lines 194362–365 |
| Fusion / Aggregation | `kradar_visibility_analysis_prompt.md` §3.1, `pipeline.py` lines 316–339 |
| Methodology Comparison | `04_visibility_methodology.md` §4.1–4.3 (candidate methods tables) |
| Thresholds | `config.py`, `radar_visibility.py`, `lidar_visibility.py`, `camera_visibility.py` |
| Implementation Notes | All `.py` files in `src/kradar_visibility/` |
| Verification Tests | `06_smoke_tests_scaffold.md`, `07_verification_tests_scaffold.md`, `kradar_visual_verification_spec.md` |

---

## Discrepancy Notes

1. **LiDAR expected density formula:** The methodology doc (§4.2 Method B) gives:
   ```
   expected ≈ (vertical_channels × vertical_extent_angle / total_vertical_fov) × (horizontal_extent_angle / horizontal_angular_resolution)
   ```
   But the implementation uses a **constant** `_EXPECTED_OS2` and `_EXPECTED_OS1` per sensor (pre-computed from channels, VFOV, HRES), not per-object vertical/horizontal extent. The code comment says "Approximate theoretical point count that would strike a 1-m² surface" — effectively using a fixed density per sensor type. **Code takes precedence**; the doc formula describes the theoretical model, the code implements a simplified constant-density approximation.

2. **Radar noise floor:** Methodology doc says "median power of cells outside any annotated bbox, or bottom decile." Implementation uses **median of ALL valid cells in the cube** (including inside bboxes). This is a simplification but more robust (no need for per-frame bbox union). **Code takes precedence.**

3. **Camera stereo handling:** Methodology doc implies single camera per direction. Implementation has **two stereo sub-cameras per direction** and takes the max score. This is a practical improvement not in the original spec.

4. **LiDAR FOV:** `config.py` and methodology imply 360° coverage. Implementation uses `[-200, 200] × [-200, 200]` m (effectively no cutoff). This matches the physical LiDAR placement (roof-mounted, 360°).

5. **Annotation format — HALF dimensions:** The annotation provides half-length, half-width, half-height. The code correctly multiplies by 2 for `obj_length`, `obj_width`, `obj_height` in `parser.py` ObjectAnnotation properties, and uses half-extents directly for corner computation in `_obj_corners()`. No discrepancy — correctly handled.

---
*Document generated from K-Radar visibility pipeline codebase and specification documents. All formulas and parameters reflect the actual implementation in `src/kradar_visibility/` as of the analysis date.*