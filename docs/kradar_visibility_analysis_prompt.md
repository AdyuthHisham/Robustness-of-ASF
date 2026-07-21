# Prompt: K-Radar Multi-Sensor Visibility Analysis Table Generator

> **Scope Note — CPU-Only Validation Build**
>
> The instructions below describe the full K-Radar pipeline.  The *current*
> implementation is intentionally constrained to **CPU execution on toy-scale
> subsets** (1–2 sequences, 10–20 frames) for rapid validation and
> debugging.  Full-dataset processing and GPU acceleration are future work.
> Any step that implies large-scale or GPU execution should be interpreted in
> this lightweight context unless explicitly marked otherwise.


## Context

You are a data processing agent working with the **K-Radar dataset** (KAIST-Radar), a large-scale 4D radar tensor-based 3D object detection dataset for autonomous driving. Your task is to generate a **Parquet table** for data analysis that quantifies how "visible" each annotated object is across all sensors in the dataset.

Repository: https://github.com/kaist-avelab/K-Radar

---

## 1. Sensor Suite Configuration

First, identify and document the following sensor setup:

### 1.1 Sensors Used for Data Gathering

| Sensor ID | Sensor Name | Type | Model | Output Format | Position on Vehicle | Purpose |
|-----------|-------------|------|-------|---------------|---------------------|---------|
| `R` | REINA-4ST | 4D Radar | REINA-4ST long range | 4D tensor (64×256×107×37) | Front grill | Primary detection sensor; forward-only (107° azimuth, 37° elevation FOV) |
| `L1` | OS2-64 | LiDAR (64-ch) | Ouster OS2-64 | Point cloud (.ped, 64 channels) | Center of roof, lower height | Long-range detection; used as main labeling reference |
| `L2` | OS1-128 | LiDAR (128-ch) | Ouster OS1-128 | Point cloud (.ped, 128 channels) | Center of roof, higher height | High-resolution; wide vertical FOV (44.5°) |
| `CF` | cam-front | Stereo Camera | ZED2i | RGB image (1280×720) | Front of vehicle | Forward view |
| `CL` | cam-left | Stereo Camera | ZED2i | RGB image (1280×720) | Left side of vehicle | Left side view |
| `CR` | cam-right | Stereo Camera | ZED2i | RGB image (1280×720) | Right side of vehicle | Right side view |
| `CRE` | cam-rear | Stereo Camera | ZED2i | RGB image (1280×720) | Rear of vehicle | Rear view |
| `CD` | cam-dash | Dash Camera | — | Video (.mp4) | Dashboard | Reference video for annotation (not used for detection) |

**Total active sensors for object detection: 7** (1 radar + 2 lidars + 4 stereo cameras). The dash cam (`CD`) is for reference only and should not be included in visibility analysis.

### 1.2 Sensor Coordinate Frames

- **Radar frame**: Origin at front grill, X forward, Y left, Z up. ROI: [0, 76.8] m (X), [-38.4, 38.4] m (Y), [-2, 10.8] m (Z).
- **LiDAR frames**: Both lidars share a common coordinate system (roof-centered), calibrated to radar frame via `info_calib/`.
- **Camera frames**: Each camera has its own intrinsic (K matrix) and extrinsic (R, t) parameters in `info_calib/`.

> **Note**: The 4D radar has a **forward-only FOV of 107°** and does not provide 360° coverage. Objects behind or significantly to the sides may not be detectable by radar even if they are within the 120m annotation radius.

---

## 2. Input Data Format: `info_label_rev2/`

Each `.txt` file in `info_label_rev2/` contains one header line and multiple object annotation lines.

### Header Line Format
```
* idx(tesseract_os2-64_cam-front_os1-128_cam-lrr)=00282_00250_00749_00250_00751, timestamp=1643292971.608162560
```

| Field | Index | File Name | Example Value | Meaning |
|-------|-------|-----------|---------------|---------|
| Index 0 | `tesseract_{idx}` | `radar_tesseract/` (4DRT) | `00282` | Radar frame index |
| Index 1 | `os2-64_{idx}` | `os2-64/` (LiDAR 64-ch) | `00250` | LiDAR 64 frame index |
| Index 2 | `cam-front_{idx}` | `cam-front/` (front image) | `00749` | Front camera frame index |
| Index 3 | `os1-128_{idx}` | `os1-128/` (LiDAR 128-ch) | `00250` | LiDAR 128 frame index |
| Index 4 | `cam-lrr_{idx}` | `cam-left/`, `cam-right/`, `cam-rear/` (all three cameras) | `00751` | **Shared index for left, right, and rear cameras** |
| Timestamp | — | — | `1643292971.608162560` | Unix epoch (seconds with nanoseconds) |

> **Important**: The `cam-lrr` index in the header is a **shared index** used for all three cameras: `cam-left`, `cam-right`, and `cam-rear`. All three cameras use the same frame index. The front camera (`cam-front`) has its own separate index. This means the header provides 5 indices total, but they map to 6 data sources: radar, OS2-64, cam-front, OS1-128, and the three L/R/Rear cameras sharing one index.

### Object Annotation Line Format
```
*, R, 1, Sedan, 47.39104220188792, -2.104020538820753, -0.4248582617725096, -0.3403999999999998, 1.6409276090572031, 0.8066192911975125, 0.7098886194067411
```

| Field | Position | Example | Type | Unit | Description |
|-------|----------|---------|------|------|-------------|
| Separator | 0 | `*` | char | — | Always `*` |
| **Sensor for identify** | 1 | `R` | string | — | **Which sensor was used to identify the object.** Codes: `R`=Radar, `L1`=OS2-64 LiDAR, `L2`=OS1-128 LiDAR. **Multiple codes may be combined** (e.g., `RL1`, `L1L2`). **Note**: `L` without a number may indicate either `L1` or `L2` — disambiguate by checking which LiDAR frame has the object, or treat as `L1` (OS2-64) by default if unclear. **Camera (`C`) is NOT used for identification in `info_label_rev2`.** |
| Tracking ID (prev) | 2 | `1` | int | — | `>=1` = tracked from previous frame; `-1` = new object |
| Class Name | 3 | `Sedan` | string | — | Object class: Sedan, Bus or Truck, Truck, Motorcycle, Bicycle, Pedestrian, etc. |
| X Center | 4 | `47.391` | float | m | Object center X (forward direction) |
| Y Center | 5 | `-2.104` | float | m | Object center Y (lateral, negative = left) |
| Z Center | 6 | `-0.425` | float | m | Object center Z (vertical, negative = below vehicle center) |
| Theta | 7 | `-0.3404` | float | rad | Heading angle (radians, NOT half-angle) |
| Length (half) | 8 | `1.6409` | float | m | Half-length (×2 for full) |
| Width (half) | 9 | `0.8066` | float | m | Half-width (×2 for full) |
| Height (half) | 10 | `0.7099` | float | m | Half-height (×2 for full) |

### Example `info_label_rev2` File
```
* idx(tesseract_os2-64_cam-front_os1-128_cam-lrr)=00282_00250_00749_00250_00751, timestamp=1643292971.608162560
*, R, 1, Sedan, 47.39104220188792, -2.104020538820753, -0.4248582617725096, -0.3403999999999998, 1.6409276090572031, 0.8066192911975125, 0.7098886194067411
*, R, 11, Sedan, 63.062500000000966, 11.087500000000002, 0.7, -179.5303, 2.188053397019174, 1.0364224280382195, 0.8593976149069411
*, L, 101, Bus or Truck, 0.10036472198321701, -8.631631663971408, 0.16241398373806343, 0.3064999999999998, 6.054276121664993, 1.4019577554678317, 1.8494146199749522
```

**Key observations from the example:**
- Object 1: Identified by **Radar only** (`R`), tracked from previous frame (`1`), Sedan at 47.4m forward, 2.1m left.
- Object 2: Identified by **Radar only** (`R`), tracked from previous frame (`11`), Sedan at 63.1m forward, 11.1m right (note: heading `-179.53` rad ≈ oncoming traffic).
- Object 3: Identified by **LiDAR** (`L`), new object (`101`), Bus or Truck at 0.1m forward, 8.6m left — very close to ego, likely passing or stationary.

**Important**: The `sensor_identify` field uses only `R`, `L1`, `L2`, and `L`. **Camera (`C`) is NOT used for object identification** in `info_label_rev2`. The cameras are present in the dataset but are not part of the identification annotation.

---

## 3. Task: Generate Visibility Analysis Parquet Table

For every object annotation in every `info_label_rev2/*.txt` file, compute visibility metrics for each sensor and output a Parquet table.

### 3.1 Table Schema

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| `sequence_id` | string | Sequence folder name (e.g., `1`, `2`, ...) |
| `frame_idx` | int | Frame index within sequence (from header, e.g., `00282` for radar) |
| `timestamp` | float64 | Unix timestamp from header |
| `obj_tracking_id` | int | Tracking ID from annotation (column 2) |
| `obj_class` | string | Object class name (column 3) |
| `obj_x` | float | Object center X (m) |
| `obj_y` | float | Object center Y (m) |
| `obj_z` | float | Object center Z (m) |
| `obj_theta` | float | Object heading (rad) |
| `obj_length` | float | Full object length (m) = 2 × half-length |
| `obj_width` | float | Full object width (m) = 2 × half-width |
| `obj_height` | float | Full object height (m) = 2 × half-height |
| `obj_distance_ego` | float | Euclidean distance from ego-vehicle to object center |
| `sensor_identify` | string | Raw sensor identification code from annotation (column 1) |
| `radar_visible` | bool | Whether object is within radar FOV and range |
| `radar_fov_in` | bool | Object center within 107° azimuth and 37° elevation |
| `radar_range_in` | bool | Object within 0–118m range |
| `radar_sparsity_score` | float | **Radar visibility metric** — see §4.1 for methodology request |
| `lidar64_visible` | bool | Whether object is within OS2-64 FOV and range |
| `lidar64_points_count` | int | **Estimated** point count from OS2-64 on object bbox |
| `lidar64_sparsity_score` | float | **LiDAR visibility metric** — see §4.2 for methodology request |
| `lidar128_visible` | bool | Whether object is within OS1-128 FOV and range |
| `lidar128_points_count` | int | **Estimated** point count from OS1-128 on object bbox |
| `lidar128_sparsity_score` | float | **LiDAR visibility metric** — see §4.2 for methodology request |
| `cam_front_visible` | bool | Whether object projects into front camera frame |
| `cam_front_proj_x` | float | Projected center X in front camera image (pixels) |
| `cam_front_proj_y` | float | Projected center Y in front camera image (pixels) |
| `cam_front_visibility_score` | float | **Camera visibility metric** — see §4.3 for methodology request |
| `cam_left_visible` | bool | Whether object projects into left camera frame |
| `cam_left_proj_x` | float | Projected center X in left camera image (pixels) |
| `cam_left_proj_y` | float | Projected center Y in left camera image (pixels) |
| `cam_left_visibility_score` | float | **Camera visibility metric** — see §4.3 for methodology request |
| `cam_right_visible` | bool | Whether object projects into right camera frame |
| `cam_right_proj_x` | float | Projected center X in right camera image (pixels) |
| `cam_right_proj_y` | float | Projected center Y in right camera image (pixels) |
| `cam_right_visibility_score` | float | **Camera visibility metric** — see §4.3 for methodology request |
| `cam_rear_visible` | bool | Whether object projects into rear camera frame |
| `cam_rear_proj_x` | float | Projected center X in rear camera image (pixels) |
| `cam_rear_proj_y` | float | Projected center Y in rear camera image (pixels) |
| `cam_rear_visibility_score` | float | **Camera visibility metric** — see §4.3 for methodology request |
| `num_sensors_visible` | int | Count of sensors with `visible=True` |
| `primary_sensor` | string | Sensor with highest visibility score |

---

## 4. Visibility Metrics: Request for Top Methodologies

The following sections describe the visibility measurement goals and request the agent to identify and propose the **top methodologies** for achieving them. The agent should evaluate candidate approaches, select the most promising ones, and justify the choice.

### 4.1 Radar Visibility (`radar_sparsity_score`)

**Goal**: Produce a rough estimate of how "visible" an object is in the 4D radar tensor. Objects that are farther away appear sparser (fewer reflecting cells). The metric should capture this sparsity as a measurable quantity.

**Data available**:
- 4D radar tensor: `radar_tesseract/` (64×256×107×37 = ~64M cells, range×Doppler×azimuth×elevation)
- Pre-processed 3D cube: `radar_zyx_cube/` (Doppler collapsed, reduced density)
- Object 3D bounding box from annotation (X, Y, Z, L, W, H, theta)
- Calibration: `info_calib/` for coordinate transforms

**Constraints and considerations**:
- The 4DRT is very large (~64M cells per frame). Processing the full tensor for every object may be computationally expensive.
- The radar has a forward-only FOV of 107° azimuth × 37° elevation. Objects outside this cone are not in the radar data at all.
- Radar returns are sparse by nature — even close objects may only have tens of high-power cells, not hundreds.
- The sensor_identify field tells us whether radar (`R`) was used to identify the object, but we want a continuous visibility score for ALL objects within radar FOV, not just identified ones.

**Request**: Identify and propose the **top 2–3 methodologies** for computing a radar sparsity/visibility score. For each method, provide:
- A brief description of the algorithm
- The expected input data (which radar representation to use)
- The formula or computation steps
- Pros and cons (computational cost, accuracy, robustness)
- A recommendation for which method to implement as the primary `radar_sparsity_score`

### 4.2 LiDAR Visibility (`lidar64_sparsity_score`, `lidar128_sparsity_score`)

**Goal**: Produce a rough estimate of how "visible" an object is in each LiDAR point cloud. Objects that are farther away have fewer points on their surface. The metric should capture this sparsity as a measurable quantity.

**Data available**:
- OS2-64 point cloud: `os2-64/` (`.ped` format, 64 channels)
- OS1-128 point cloud: `os1-128/` (`.ped` format, 128 channels)
- Object 3D bounding box from annotation
- Calibration: `info_calib/` for LiDAR-to-radar frame transforms
- Weather conditions per sequence: `description.txt`

**Constraints and considerations**:
- OS2-64 (64 channels) is sparser than OS1-128 (128 channels). The same object at the same distance will have roughly half the points in OS2-64.
- LiDAR performance degrades significantly in adverse weather (rain, sleet, snow). The `description.txt` provides weather labels.
- Point clouds become sparser with distance. A Sedan at 10m may have 50–200 points, while at 80m it may have only 1–10 points.
- The `sensor_identify` field tells us which LiDAR (`L1`, `L2`, or `L`) identified the object, but we want a continuous score for ALL objects within LiDAR range.
- The `L` code (without number) requires disambiguation — check which LiDAR point cloud contains the object.

**Request**: Identify and propose the **top 2–3 methodologies** for computing a LiDAR sparsity/visibility score. For each method, provide:
- A brief description of the algorithm
- The expected input data (point cloud format, coordinate frame)
- The formula or computation steps
- Pros and cons (computational cost, accuracy, weather robustness)
- A recommendation for which method to implement as the primary `lidar*_sparsity_score`

### 4.3 Camera Visibility (`cam_*_visibility_score`)

**Goal**: Determine which of the 4 cameras (front, left, right, rear) has the object in its frame, and produce a rough estimate of how "visible" the object is in that camera. The `sensor_identify` field does NOT use camera (`C`) for identification, so we must compute camera visibility independently.

**Data available**:
- 4 camera image sequences: `cam-front/`, `cam-left/`, `cam-right/`, `cam-rear/` (1280×720 RGB)
- Object 3D bounding box from annotation
- Camera calibration: `info_calib/` with intrinsic matrix `K` and extrinsic `R`, `t` for each camera
- LiDAR point clouds (can be used for occlusion checking via depth projection)

**Constraints and considerations**:
- The header provides `cam-front` index and `cam-lrr` index. The `cam-lrr` index is **shared** by `cam-left`, `cam-right`, and `cam-rear`. All three use the same frame index.
- Each camera has its own coordinate frame. The object must be projected from the common annotation frame (radar/LiDAR) to each camera frame.
- Objects behind the camera (negative Z in camera frame) are not visible.
- Objects may be partially or fully occluded by other objects or the ego vehicle.
- The ZED2i cameras have 110° horizontal × 70° vertical FOV.
- We want to know: (a) which camera(s) see the object, and (b) how prominently it appears (size, centrality, occlusion).

**Request**: Identify and propose the **top 2–3 methodologies** for computing a camera visibility score and determining which camera has the object. For each method, provide:
- A brief description of the algorithm
- The expected input data (images, calibration, LiDAR for occlusion)
- The formula or computation steps
- Pros and cons (computational cost, accuracy, occlusion handling)
- A recommendation for which method to implement as the primary `cam_*_visibility_score`

---

## 5. Goals and Sub-Goals for Implementation

### 5.1 Overarching Goal

Build a complete, robust, and thoroughly tested Python pipeline that:
1. Reads all `info_label_rev2/` annotations across all K-Radar sequences
2. Loads corresponding sensor data (radar tensors, LiDAR point clouds, camera images)
3. Computes per-object visibility metrics for all 7 sensors using the selected methodologies from §4
4. Outputs a single Parquet file containing the full visibility analysis table
5. Passes all smoke tests (§6) on a minimal subset; verification tests (§7) are defined but only run on toy-scale data in this build

### 5.2 Sub-Goals (Milestones)

#### Sub-Goal 1: Data Ingestion and Parsing
- [ ] Parse `info_label_rev2/*.txt` files correctly (header + all object lines) — test on ≤20 frames first
- [ ] Handle the `cam-lrr` shared index correctly (maps to left, right, rear cameras)
- [ ] Load `info_calib/` calibration files for all sensors
- [ ] Load `description.txt` weather metadata for each sequence
- [ ] Build a sequence/frame lookup table mapping indices to file paths

#### Sub-Goal 2: Sensor Data Loading
- [ ] Load 4D radar tensors (`radar_zyx_cube/` only — `radar_tesseract/` is too large for CPU memory)
- [ ] Load OS2-64 and OS1-128 point clouds (`.ped` format)
- [ ] Load camera images for all 4 cameras using correct indices
- [ ] Implement lazy loading / caching to avoid memory exhaustion

#### Sub-Goal 3: Coordinate Transformations
- [ ] Transform object bboxes from annotation frame to each sensor's native frame
- [ ] Implement 3D-to-2D projection for all 4 cameras using calibration
- [ ] Validate projections against known ground-truth (e.g., objects at known positions)

#### Sub-Goal 4: Visibility Metric Implementation
- [ ] Implement the selected radar sparsity methodology from §4.1
- [ ] Implement the selected LiDAR sparsity methodology from §4.2 (for both L1 and L2)
- [ ] Implement the selected camera visibility methodology from §4.3 (for all 4 cameras)
- [ ] Compute `num_sensors_visible` and `primary_sensor` per object

#### Sub-Goal 5: Table Construction and Output
- [ ] Build the full DataFrame with all columns from §3.1 schema
- [ ] Ensure correct data types (bool, int, float, string, nullable types)
- [ ] Write to a single small Parquet file (no partitioning needed at toy scale)
- [ ] Generate summary statistics (row count, null counts, per-sequence counts)

#### Sub-Goal 6: Smoke Testing
- [ ] All smoke tests from §6 pass
- [ ] Fix any issues identified during smoke testing
- [ ] Document any deviations or known limitations

#### Sub-Goal 7: Verification Testing
- [ ] All verification tests from §7 pass
- [ ] Generate a verification report with pass/fail status for each test
- [ ] Address any failures with fixes or documented explanations

---

## 6. Smoke Tests

Smoke tests are quick sanity checks that run on a small subset of data (e.g., 1–2 sequences, 10–20 frames) to catch major errors early. They should complete in under 5 minutes.

### 6.1 Data Parsing Smoke Tests

| Test ID | Description | Expected Result | Pass Criteria |
|---------|-------------|-----------------|---------------|
| SMK-01 | Parse a single `info_label_rev2/*.txt` file and count header + object lines | Header count = 1, object count = N | No parsing exceptions; counts match manual inspection |
| SMK-02 | Verify `cam-lrr` index maps to left, right, AND rear camera file paths | All three camera files exist at the shared index | `os.path.exists()` returns True for all three |
| SMK-03 | Load calibration for all 7 sensors from `info_calib/` | 7 calibration objects loaded | No missing calibrations; all matrices are valid (correct shapes) |
| SMK-04 | Parse `description.txt` for 3 random sequences | Weather labels extracted | Labels are from allowed set: clear, overcast, fog, rain, sleet, snow |

### 6.2 Coordinate Transformation Smoke Tests

| Test ID | Description | Expected Result | Pass Criteria |
|---------|-------------|-----------------|---------------|
| SMK-05 | Project an object at (10, 0, 0) to front camera | Projects to center of image (~640, 360) | Projected coordinates within ±50 pixels of image center |
| SMK-06 | Project an object at (-10, 0, 0) to rear camera | Projects to center of rear image | Object behind ego; rear camera sees it |
| SMK-07 | Project an object at (0, 10, 0) to left camera | Projects within left image bounds | `0 <= u < 1280` and `0 <= v < 720` |
| SMK-08 | Project an object at (0, -10, 0) to right camera | Projects within right image bounds | `0 <= u < 1280` and `0 <= v < 720` |
| SMK-09 | Project an object behind the front camera (negative Z in cam frame) | `cam_front_visible = False` | Projection correctly rejects behind-camera points |

### 6.3 Sensor Data Loading Smoke Tests

| Test ID | Description | Expected Result | Pass Criteria |
|---------|-------------|-----------------|---------------|
| SMK-10 | Load one 4D radar tensor frame | Shape = (64, 256, 107, 37) or valid ZYX cube shape | No memory errors; shape matches expected |
| SMK-11 | Load one OS2-64 point cloud | Returns array of (N, 3+) points | N > 0 for a frame with visible objects |
| SMK-12 | Load one OS1-128 point cloud | Returns array of (N, 3+) points | N > 0; OS1-128 has more points than OS2-64 for same frame |
| SMK-13 | Load one image from each of the 4 cameras | Shape = (720, 1280, 3) | All images loadable; pixel values in [0, 255] |

### 6.4 Visibility Metric Smoke Tests

| Test ID | Description | Expected Result | Pass Criteria |
|---------|-------------|-----------------|---------------|
| SMK-14 | Compute radar sparsity for a close object (10m) vs. far object (80m) | Close object score > far object score | Monotonic decrease with distance (within tolerance) |
| SMK-15 | Compute LiDAR point count for same object in OS2-64 vs. OS1-128 | OS1-128 count >= OS2-64 count | 128-channel denser than 64-channel |
| SMK-16 | Compute camera visibility for an object directly in front vs. at edge of FOV | Center object score > edge object score | Higher score for more central, larger projection |
| SMK-17 | Run full pipeline on 2 sequences (20 frames) | Parquet file generated with >0 rows | No crashes; all expected columns present |

---

## 7. Verification Tests

Verification tests are comprehensive checks that run on the full dataset (or a statistically significant sample) to validate correctness, consistency, and data quality.

### 7.1 Sensor Identify Consistency Verification

| Test ID | Description | Method | Pass Criteria |
|---------|-------------|--------|---------------|
| VER-01 | If `sensor_identify` contains `R`, then `radar_visible` must be `True` | For all rows where `sensor_identify` contains `R`, check `radar_visible` | 100% match; any mismatch is flagged for review |
| VER-02 | If `sensor_identify` contains `L1`, then `lidar64_visible` must be `True` | For all rows where `sensor_identify` contains `L1`, check `lidar64_visible` | 100% match |
| VER-03 | If `sensor_identify` contains `L2`, then `lidar128_visible` must be `True` | For all rows where `sensor_identify` contains `L2`, check `lidar128_visible` | 100% match |
| VER-04 | If `sensor_identify` contains `L` (unspecified), at least one LiDAR must be visible | For all rows where `sensor_identify` == `L`, check `lidar64_visible OR lidar128_visible` | >= 95% match (allowing for edge cases) |
| VER-05 | `sensor_identify` must NOT contain `C` (camera) | Check all unique values of `sensor_identify` | No `C` found in any value |

### 7.2 Distance Correlation Verification

| Test ID | Description | Method | Pass Criteria |
|---------|-------------|--------|---------------|
| VER-06 | `lidar64_points_count` decreases with `obj_distance_ego` | Bin objects by distance (0–20m, 20–40m, 40–60m, 60–80m, 80–120m); compute median points per bin | Median strictly decreases across bins (or monotonic with R² > 0.5) |
| VER-07 | `lidar128_points_count` decreases with `obj_distance_ego` | Same as VER-06 for OS1-128 | Same criteria as VER-06 |
| VER-08 | `radar_sparsity_score` decreases with `obj_distance_ego` | Same binning approach for radar | Monotonic decrease with R² > 0.3 (radar is noisier than LiDAR) |
| VER-09 | `cam_*_visibility_score` decreases with `obj_distance_ego` for visible cameras | For objects with `cam_front_visible=True`, correlate score with distance | Negative correlation with p < 0.05 |

### 7.3 Camera Projection Sanity Verification

| Test ID | Description | Method | Pass Criteria |
|---------|-------------|--------|---------------|
| VER-10 | All projected camera coordinates are within image bounds | For all rows where `cam_*_visible=True`, check `0 <= proj_x < 1280` and `0 <= proj_y < 720` | 100% of visible projections in bounds |
| VER-11 | No projected coordinates for invisible objects | For all rows where `cam_*_visible=False`, check `proj_x` and `proj_y` are NULL/NaN | 100% match |
| VER-12 | Front camera primarily sees forward objects (X > 0) | For rows with `cam_front_visible=True`, compute % with `obj_x > 0` | >= 90% have `obj_x > 0` |
| VER-13 | Rear camera primarily sees behind objects (X < 0) | For rows with `cam_rear_visible=True`, compute % with `obj_x < 0` | >= 90% have `obj_x < 0` |
| VER-14 | Left camera primarily sees left-side objects (Y > 0) | For rows with `cam_left_visible=True`, compute % with `obj_y > 0` | >= 70% have `obj_y > 0` (allowing for wide FOV) |
| VER-15 | Right camera primarily sees right-side objects (Y < 0) | For rows with `cam_right_visible=True`, compute % with `obj_y < 0` | >= 70% have `obj_y < 0` |

### 7.4 Primary Sensor Logic Verification

| Test ID | Description | Method | Pass Criteria |
|---------|-------------|--------|---------------|
| VER-16 | `primary_sensor` matches the sensor with highest visibility score | For each row, find max score among visible sensors; compare to `primary_sensor` | >= 98% match (allowing for ties) |
| VER-17 | `num_sensors_visible` equals count of `*_visible=True` | For each row, count True values across all sensor visible columns | 100% match |
| VER-18 | `primary_sensor` is NULL when `num_sensors_visible == 0` | Check rows with no visible sensors | 100% match |

### 7.5 Data Quality Verification

| Test ID | Description | Method | Pass Criteria |
|---------|-------------|--------|---------------|
| VER-19 | No negative visibility scores | Check `radar_sparsity_score`, `lidar*_sparsity_score`, `cam*_visibility_score` | All scores >= 0 |
| VER-20 | No negative point counts | Check `lidar*_points_count` | All counts >= 0 |
| VER-21 | `obj_distance_ego` is consistent with X, Y, Z | Recompute sqrt(X²+Y²+Z²) and compare to stored value | 100% match within 0.01m |
| VER-22 | Object dimensions are positive | Check `obj_length`, `obj_width`, `obj_height` | All > 0 |
| VER-23 | No duplicate (sequence_id, frame_idx, obj_tracking_id) tuples | Check for duplicate primary keys | 0 duplicates |
| VER-24 | All sequences from 1–58 are represented | Count distinct `sequence_id` values | Count == 58 (or matches actual dataset size) |

### 7.6 Weather Impact Verification (Optional but Recommended)

| Test ID | Description | Method | Pass Criteria |
|---------|-------------|--------|---------------|
| VER-25 | LiDAR point counts are lower in rain/sleet/snow vs. clear | Compare median `lidar*_points_count` per distance bin across weather conditions | Significant difference (p < 0.05) between clear and adverse weather |
| VER-26 | Radar sparsity is less affected by weather than LiDAR | Compare radar score variance across weather vs. LiDAR variance | Radar variance < LiDAR variance |

---

## 8. Implementation Code Structure

The implementation should be organized as a well-structured Python package with the following modules:

```
kradar_visibility/
├── __init__.py
├── config.py              # Paths, constants, sensor specs
├── parser.py              # info_label_rev2 parsing, header extraction
├── calibration.py         # Load and apply info_calib transformations
├── data_loader.py         # Lazy loading for radar, LiDAR, camera data
├── radar_visibility.py    # Radar sparsity metric implementation
├── lidar_visibility.py    # LiDAR sparsity metric implementation (L1 + L2)
├── camera_visibility.py   # Camera visibility metric implementation (4 cameras)
├── pipeline.py            # Main orchestration: parse -> compute -> output
├── tests/
│   ├── __init__.py
│   ├── test_smoke.py      # All smoke tests from §6
│   └── test_verify.py     # All verification tests from §7
├── scripts/
│   └── run_pipeline.py    # CLI entry point
└── requirements.txt       # pandas, pyarrow, numpy, opencv-python, etc.
```

### 8.1 Key Implementation Requirements

- **Memory efficiency**: The 4DRT is ~64M cells per frame and must **not** be loaded.  Use `radar_zyx_cube/` only, and process one frame at a time.
- **Parallelization**: Sequential processing is fine at toy scale; `multiprocessing` may be added later for full-dataset runs.
- **Error handling**: If a sensor file is missing for a frame, log a warning and set `visible=False` with `score=0`.
- **Progress logging**: Use `tqdm` or similar to show progress per sequence and per frame.
- **Reproducibility**: Set random seeds if any stochastic steps are used. Document all hyperparameters (thresholds, bin sizes, etc.).

---

## 9. Example Output Row

```python
{
    "sequence_id": "1",
    "frame_idx": 282,
    "timestamp": 1643292971.608162,
    "obj_tracking_id": 1,
    "obj_class": "Sedan",
    "obj_x": 47.391,
    "obj_y": -2.104,
    "obj_z": -0.425,
    "obj_theta": -0.3404,
    "obj_length": 3.2819,
    "obj_width": 1.6132,
    "obj_height": 1.4198,
    "obj_distance_ego": 47.438,
    "sensor_identify": "R",  # Identified by Radar only
    "radar_visible": True,
    "radar_fov_in": True,
    "radar_range_in": True,
    "radar_sparsity_score": 0.12,  # Computed via selected methodology
    "lidar64_visible": False,
    "lidar64_points_count": 0,
    "lidar64_sparsity_score": 0.0,
    "lidar128_visible": False,
    "lidar128_points_count": 0,
    "lidar128_sparsity_score": 0.0,
    "cam_front_visible": True,
    "cam_front_proj_x": 845.2,
    "cam_front_proj_y": 380.1,
    "cam_front_visibility_score": 0.03,  # Computed via selected methodology
    "cam_left_visible": False,
    "cam_left_proj_x": None,
    "cam_left_proj_y": None,
    "cam_left_visibility_score": 0.0,
    "cam_right_visible": False,
    "cam_right_proj_x": None,
    "cam_right_proj_y": None,
    "cam_right_visibility_score": 0.0,
    "cam_rear_visible": False,
    "cam_rear_proj_x": None,
    "cam_rear_proj_y": None,
    "cam_rear_visibility_score": 0.0,
    "num_sensors_visible": 2,  # R, CF
    "primary_sensor": "radar"
}
```

---

## 10. Suggested Analysis Queries (for downstream use)

Once the Parquet table is generated, you can run analyses like:

- **Q1**: What percentage of objects are visible in all 7 sensors vs. only 1 sensor?
- **Q2**: How does LiDAR sparsity correlate with distance for each weather condition?
- **Q3**: Which camera captures the most objects per frame? (Front vs. Left vs. Right vs. Rear)
- **Q4**: What is the radar detection rate (radar_visible=True) vs. LiDAR detection rate at >60m?
- **Q5**: How often does the `sensor_identify` field disagree with computed visibility (e.g., `sensor_identify` says `R` but computed `radar_visible=False`)?
- **Q6**: Distribution of `primary_sensor` by object class and distance.
- **Q7**: For objects marked `L` (unspecified LiDAR), what is the breakdown of which LiDAR actually sees them? (L1-only, L2-only, both)
- **Q8**: How does radar sparsity score vary for objects at different distances and orientations (e.g., oncoming vs. same-direction)?
- **Q9**: What is the correlation between camera visibility score and the object's distance / projected size / centrality in the frame?

---

*Generated for K-Radar dataset analysis. Refer to the official repository (https://github.com/kaist-avelab/K-Radar) and NeurIPS 2022 paper for complete dataset details.*
