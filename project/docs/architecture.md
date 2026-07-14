# Sensor Identification Logic

## Mapping of Labels to Physical Sensors

Based on analysis of `info_label_rev2/*.txt` files and cross-referencing with calibration files, the following **canonical** mapping is established:

| Label | Physical Sensor | Sensor Key | Channels | Notes |
|-------|----------------|------------|----------|-------|
| `L`  | OS2-64 LiDAR   | `L1`       | 64       | `L` is an alias for `L1`. Always resolves to OS2-64. |
| `L1` | OS2-64 LiDAR   | `L1`       | 64       | Explicit form — identical to `L`. |
| `L2` | OS1-128 LiDAR  | `L2`       | 128      | Distinct sensor from `L`/`L1`. |

### Resolution Rule

**`L` MUST always be resolved to OS2-64 (L1).** The two labels are interchangeable.
There is no configuration in the K-Radar dataset where `L` refers to OS1-128; analysis
of calibration files confirms `L` consistently co-occurs with OS2-64 calibration data.

### Why This Matters

The dataset uses `L` and `L1` interchangeably in `info_label_rev2/*.txt` files.
Downstream code (visibility computation, Parquet output) must treat them as the same
sensor to avoid double-counting or missing data. The canonical key used internally is
`L1`; `L` is normalized to `L1` at parse time.

## Verification Process

To verify the mapping:

1. Parse all `*.txt` files in the `info_label_rev2/` directory.
2. Extract the sensor identification strings associated with labels `L`, `L1`, and `L2`.
3. Cross-reference these strings with the calibration file names (or contents) in the corresponding calibration directories.
4. Confirm that:
   - `L1` consistently maps to calibration files for OS2-64.
   - `L2` consistently maps to calibration files for OS1-128.
   - `L` maps predominantly (100%) to OS2-64 calibration files.

## Validation Logic

At parse time, apply the following normalization:

```python
def normalize_sensor_label(raw_label: str) -> str:
    """Normalize sensor identification label to canonical form.
    
    Returns:
        'L1' for raw labels 'L' or 'L1' (OS2-64).
        'L2' for raw label 'L2' (OS1-128).
        Other labels (R, CF, CL, CR, CRE) pass through unchanged.
    
    Raises:
        ValueError: If the label is not a recognized sensor identifier.
    """
    ALIAS_MAP = {"L": "L1", "L1": "L1", "L2": "L2"}
    if raw_label in ALIAS_MAP:
        return ALIAS_MAP[raw_label]
    if raw_label in {"R", "CF", "CL", "CR", "CRE"}:
        return raw_label
    raise ValueError(f"Unrecognized sensor label: {raw_label!r}")
```

### Verification Check

- **SENS-01**: After normalization, no row in the Parquet output shall contain `L` as the `sensor_identify` value. Only `L1`, `L2`, `R`, `CF`, `CL`, `CR`, `CRE` are valid.

## Output

The mapping rule is enforced in:
- `parser.py` — `normalize_sensor_label()` function applied during label file parsing.
- `config.py` — `SENSOR_SUITE` only contains canonical keys (`L1`, `L2`, never `L`).
- `data_loader.py` — calls `normalize_sensor_label()` when loading `info_label_rev2` files.
- `pipeline.py` — writes only canonical keys to the `sensor_identify` Parquet column.

## LiDAR Verification Methodology

### Method A: Raw Point-in-Box Counts

- Compute raw point counts for OS2-64 and OS1-128 LiDAR sensors within each oriented 3D bounding box using CPU-based point-in-box.
- Output fields: `lidar64_points_count`, `lidar128_points_count`.

### Method B: Expected-Density Normalization (Sparsity Score)

- Compute expected point count per box based on LiDAR sensor characteristics:
  - `expected_count ≈ (vertical_channels × vertical_extent_angle / total_vertical_fov) × (horizontal_extent_angle / horizontal_angular_resolution)`
  - where vertical_extent_angle and horizontal_extent_angle are derived from the object's 3D bounding box dimensions and orientation.
- Sparsity score = `actual_count / expected_count`, clamped to [0, 1] (or 0-1 range as per spec).
- Output fields: `lidar64_sparsity_score`, `lidar128_sparsity_score`.

### Gating Conditions / Verification Checks

The following verification checks are applied to ensure LiDAR data quality:

- **SMK-11**: For frames with visible objects, `lidar*_points_count > 0`.
- **SMK-12**: For each frame, OS1-128 point count ≥ OS2-64 point count (CPU point-in-box).
- **SMK-15**: For each object, OS1-128 point count ≥ OS2-64 point count.
- **VER-06**: Median `lidar64_points_count` strictly decreases with increasing object distance (or R² > 0.5 when regressing count vs. distance).
- **VER-07**: Same as VER-06 for OS1-128.
- **VER-20**: No negative point counts.
- **VER-25**: LiDAR point counts (or sparsity scores) are statistically lower in adverse weather (rain, sleet, snow) compared to clear weather.

## Weather Data Gathering

### Source
Each sequence folder contains a `description.txt` file. Format is **comma-separated** (not `weather: <label>`):

```
<location>,<time_of_day>,<weather>
```

Example:
```
urban,night,normal
highway,day,heavysnow
```

The file is located at `data/<sequence_id>/description.txt` under `DATASET_ROOT`.

### Fields
| Field | Type | Description | Allowed Values |
|-------|------|-------------|----------------|
| `location` | str | Environment type | `urban`, `highway`, `countryside`, ... |
| `time_of_day` | str | Day or night | `day`, `night` |
| `weather` | str | Raw weather condition | `normal`, `clear`, `overcast`, `fog`, `rain`, `sleet`, `snow`, `heavysnow` |

### Weather Label Normalization
The raw weather field contains values outside the canonical set. Normalize as follows:

| Raw Value | Normalized To | Reason |
|-----------|---------------|--------|
| `normal` | `clear` | Alias — treat as clear conditions |
| `heavysnow` | `snow` | Variant — bucket with snow |
| `clear`, `overcast`, `fog`, `rain`, `sleet`, `snow` | unchanged | Canonical labels |
| Any other value | logged as warning, counted under `"unknown"` | Data quality |

The normalized values must belong to: `{"clear", "overcast", "fog", "rain", "sleet", "snow"}` (matches `config.WEATHER_LABELS`).

### Allowed Labels (for SMK-04)
After normalization:
- `clear`
- `overcast`
- `fog`
- `rain`
- `sleet`
- `snow`

### Implementation
- **Parser function**: `parse_description_file(filepath: Path) -> dict | None`
  - Reads one `description.txt`, splits on comma, returns `{"location": ..., "time_of_day": ..., "weather": ...}` or `None` if file missing/malformed.
- **Sequence-level loader**: `collect_weather_for_sequence(sequence_id: str, dataset_root: Path) -> str | None`
  - Locates `data/<sequence_id>/description.txt`, calls parser, applies normalization.
  - Returns normalized weather string, or `None` if file absent.
- **Pipeline integration**: `pipeline.py` calls `collect_weather_for_sequence` once per sequence at startup, stores the result in a per-sequence lookup dict, and populates the Parquet `weather` column for all frames of that sequence.
- The weather label is joined into the output Parquet table as a new column in the Object Identity section.
- The weather column is **nullable** (some sequences may lack the file entirely).

### Schema
The weather column is defined in `config.OUTPUT_SCHEMA`:

```python
"weather": str  # nullable — one of: clear, overcast, fog, rain, sleet, snow, null
```

### Verification Checks
- **SMK-04**: Weather labels (after normalization) must be in `WEATHER_LABELS`.
- **VER-25**: Requires weather column for LiDAR adverse-weather comparison (see LiDAR Verification Methodology).
- **VER-26**: Requires weather column for radar vs LiDAR weather sensitivity (see LiDAR Verification Methodology).

Note: GPU-accelerated point-in-box (`points_in_boxes_gpu`) exists elsewhere and should be reused if available; CPU implementation is used for verification.

### CPU Point-in-Box Implementation (Method A)

The CPU fallback lives in the test-bed archive at:
`/home/adhish/Productivity/AMSCUP/test-bed/src/Modules/robust_testing/kradar/src/archive/sensor_data_utils.py`

Function: `points_in_boxes_cpu(points: np.ndarray, boxes: np.ndarray) -> np.ndarray`

**Algorithm:**
1. For each box `m` with `(cx, cy, cz, dx, dy, dz, heading)`:
   - Translate points to box local frame: `local = points - [cx, cy, cz]`
   - Rotate by `-heading` around z-axis:
     - `x_rot = local[:,0]*cos(-h) - local[:,1]*sin(-h)`
     - `y_rot = local[:,0]*sin(-h) + local[:,1]*cos(-h)`
     - `z_rot = local[:,2]`
   - Test inclusion: `|x_rot| <= dx/2 AND |y_rot| <= dy/2 AND |z_rot| <= dz/2`
2. Assign each point to the first matching box (lowest index wins).
3. Return `(N,)` int64 array of box indices, `-1` for unassigned.

**Input conventions:**
- `points`: `(N, 3)` float64 — `(x, y, z)` in ego frame (meters).
- `boxes`: `(M, 7)` float64 — `(cx, cy, cz, dx, dy, dz, heading)` where `dx, dy, dz` are full box dimensions (length, width, height) and `heading` is rotation around z-axis in radians.

**Counting:** Use `counts_from_box_idxs(box_idxs, num_boxes)` to convert per-point assignments to per-box counts, or equivalently `np.bincount(box_idxs[box_idxs >= 0], minlength=num_boxes)`.

**Sensor frame → ego transform:** LiDAR points in the raw sensor frame must be transformed to ego frame before point-in-box. The K-Radar LiDAR mounting offset is `(-2.54, 0.3, 0.7)` meters (applied as `ego_point = sensor_point + offset`). See `SensorCalibrationOffset` in the same file.

### Expected-Density Normalization (Method B)

Given an oriented 3D bounding box with center `(x, y, z)`, dimensions `(l, w, h)`, and orientation `theta`:

1. Compute the box's angular extent as seen from the sensor:
   - `v_θ_extent = atan2(h, 2 * range)` (vertical half-extent → full angle)
   - `h_θ_extent = atan2(sqrt(l² + w²), 2 * range)` (horizontal diagonal → full angle)
   - where `range = sqrt(x² + y² + z²)` (distance from sensor to box center)

2. Compute expected count:
   ```
   expected = (vertical_channels * v_θ_extent / total_v_fov_rad) * (h_θ_extent / h_angular_res_rad)
   ```

3. Sparsity score:
   ```
   sparsity_score = clip(actual_count / expected, 0.0, 1.0)
   ```

**Sensor constants (from `config.py`):**

| Parameter | OS2-64 (L1) | OS1-128 (L2) |
|-----------|-------------|--------------|
| `vertical_channels` | 64 | 128 |
| `total_v_fov_deg` | 33.2 | 44.5 |
| `h_angular_res_deg` | 0.35 | 0.17 |

Convert degrees to radians: `rad = deg * pi / 180`.

### Gating: `lidar*_visible`

```
lidar*_visible = (points_count > 0) AND bbox_center_within_fov AND bbox_center_within_range
```

- **FOV check**: Box center must fall within the sensor's vertical and horizontal FOV cone.
- **Range check**: Distance from sensor to box center must be within `[0, max_range_m]`.
- For OS2-64: max range ≈ 70 m; for OS1-128: max range ≈ 120 m (per K-Radar spec).
- If no points fall inside the box, `lidar*_visible = False` and `sparsity_score = 0.0`.

### Module Boundary

- **Owner:** `lidar_visibility.py` in `kradar_visibility/`
- **Function contracts:** See `api_contracts.md` § "LiDAR Visibility Module — Function Contracts" for the 5 public functions (`compute_lidar_points_count`, `compute_expected_count`, `compute_lidar_sparsity_score`, `check_lidar_visible`, `process_frame_lidar`) and the `OS2_64_PARAMS` / `OS1_128_PARAMS` dict definitions.
- **Config dependency:** `config.py` must define `OS2_64_PARAMS` and `OS1_128_PARAMS` dicts (see api_contracts.md for schema).
- **Upstream:** `data_loader.py` provides `(N, 3)` LiDAR points in ego frame and `(M, 7)` boxes.
- **Downstream:** `pipeline.py` calls `process_frame_lidar()` per frame per sensor and writes results to Parquet.

## Data Structures for LiDAR Verification Results

The LiDAR verification results are incorporated into the main Parquet output schema as defined in §3.1 of the task brief. The relevant columns are:

### LiDAR 64 (OS2-64)

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `lidar64_visible` | bool | No | True if LiDAR point count > 0 and bbox center within sensor FOV/range |
| `lidar64_points_count` | int | No | Raw CPU point-in-box count for OS2-64 |
| `lidar64_sparsity_score` | float | Yes | Normalized sparsity score (actual/expected, clipped to [0,1]) |

### LiDAR 128 (OS1-128)

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `lidar128_visible` | bool | No | True if LiDAR point count > 0 and bbox center within sensor FOV/range |
| `lidar128_points_count` | int | No | Raw CPU point-in-box count for OS1-128 |
| `lidar128_sparsity_score` | float | Yes | Normalized sparsity score (actual/expected, clipped to [0,1]) |

## Verification Report Structure (Optional API Endpoint)

If a verification report or metrics endpoint is exposed, it should follow this structure:

### Verification Metrics Endpoint (GET `/metrics/lidar_verification`)

Returns a JSON object with aggregated verification statistics over a dataset or sequence.

```json
{
  "sequence_id": "string",
  "frame_range": [int, int],
  "metrics": {
    "lidar64": {
      "total_frames": int,
      "frames_with_points": int,
      "mean_points_per_frame": float,
      "mean_sparsity_score": float,
      "smk_11_pass_rate": float,
      "smk_12_pass_rate": float,
      "ver_06_slope": float,
      "ver_06_r2": float
    },
    "lidar128": {
      "total_frames": int,
      "frames_with_points": int,
      "mean_points_per_frame": float,
      "mean_sparsity_score": float,
      "smk_11_pass_rate": float,
      "smk_12_pass_rate": float,
      "ver_07_slope": float,
      "ver_07_r2": float
    },
    "weather_impact": {
      "clear_vs_rain_sparsity_ratio_lidar64": float,
      "clear_vs_rain_sparsity_ratio_lidar128": float,
      "clear_vs_snow_sparsity_ratio_lidar64": float,
      "clear_vs_snow_sparsity_ratio_lidar128": float
    }
  },
  "timestamp": "ISO 8601 timestamp"
}
```

### Verification Report Endpoint (GET `/report/lidar_verification/{sequence_id}`)

Returns a detailed verification report for a specific sequence, including per-frame data and failure cases.

```json
{
  "sequence_id": "string",
  "generated_at": "ISO 8601 timestamp",
  "frames": [
    {
      "frame_idx": int,
      "lidar64": {
        "visible": bool,
        "points_count": int,
        "sparsity_score": float | null,
        "expected_count": float,
        "gates": {
          "fov_in": bool,
          "range_in": bool
        }
      },
      "lidar128": {
        "visible": bool,
        "points_count": int,
        "sparsity_score": float | null,
        "expected_count": float,
        "gates": {
          "fov_in": bool,
          "range_in": bool
        }
      },
      "verification_checks": {
        "smk_11": bool,
        "smk_12": bool,
        "smk_15": bool,
        "ver_06": bool,
        "ver_07": bool,
        "ver_20": bool,
        "ver_25": bool
      }
    }
  ],
  "summary": {
    "total_frames": int,
    "passed_checks": {
      "smk_11": int,
      "smk_12": int,
      "smk_15": int,
      "ver_06": int,
      "ver_07": int,
      "ver_20": int,
      "ver_25": int
    },
    "failure_cases": [
      {
        "frame_idx": int,
        "check_failed": string,
        "details": string
      }
    ]
  }
}
```

## config.py — Pipeline Configuration Constants

`config.py` (`kradar_visibility/config.py`) defines all runtime constants for the K-Radar visibility analysis pipeline. It is imported by every downstream module (`lidar_visibility.py`, `radar_visibility.py`, `camera_visibility.py`, `data_loader.py`, `pipeline.py`).

### Dataset Paths

| Constant | Type | Value | Description |
|----------|------|-------|-------------|
| `DATASET_ROOT` | `Path` | `"/home/adhish/Productivity/AMSCUP/repos/K-Radar"` | Root directory of the K-Radar dataset |
| `KRADAR_ROOT` | `str` | `str(DATASET_ROOT)` | String alias for the dataset root |

### Sensor Specifications

| Constant | Type | Value | Description |
|----------|------|-------|-------------|
| `RADAR_FOV_AZIMUTH_DEG` | `float` | `107.0` | Radar horizontal field of view (degrees) |
| `RADAR_FOV_ELEVATION_DEG` | `float` | `37.0` | Radar vertical field of view (degrees) |
| `RADAR_MAX_RANGE_M` | `float` | `118.0` | Radar maximum detection range (meters) |

### Camera Image Dimensions

| Constant | Type | Value | Description |
|----------|------|-------|-------------|
| `CAM_HALF_WIDTH` | `int` | `1280` | Width per stereo half-image (pixels) |
| `CAM_HALF_HEIGHT` | `int` | `720` | Height per stereo half-image (pixels) |

### Camera Visibility Score Weights

| Constant | Type | Value | Description |
|----------|------|-------|-------------|
| `CAM_W1` | `float` | `0.7` | Weight for area component in visibility score |
| `CAM_W2` | `float` | `0.3` | Weight for centrality component in visibility score |

### LiDAR Channel Constants

| Constant | Type | Value | Description |
|----------|------|-------|-------------|
| `OS2_64_CHANNELS` | `int` | `64` | Number of vertical channels for OS2-64 LiDAR |
| `OS2_64_VFOV_DEG` | `float` | `33.2` | Vertical FOV for OS2-64 (degrees) |
| `OS2_64_HRES_DEG` | `float` | `0.35` | Horizontal angular resolution for OS2-64 (degrees) |
| `OS1_128_CHANNELS` | `int` | `128` | Number of vertical channels for OS1-128 LiDAR |
| `OS1_128_VFOV_DEG` | `float` | `44.5` | Vertical FOV for OS1-128 (degrees) |
| `OS1_128_HRES_DEG` | `float` | `0.17` | Horizontal angular resolution for OS1-128 (degrees) |

### Weather Labels

| Constant | Type | Value | Description |
|----------|------|-------|-------------|
| `ALLOWED_WEATHER` | `set` | `{"clear", "overcast", "fog", "rain", "sleet", "snow", "normal"}` | Set of valid weather labels (including "normal") |
| `WEATHER_LABELS` | `list` | `["clear", "overcast", "fog", "rain", "sleet", "snow"]` | List of weather labels excluding "normal" |

### Smoke Test Defaults

| Constant | Type | Value | Description |
|----------|------|-------|-------------|
| `SMOKE_SEQUENCE_IDS` | `list` | `["1", "2"]` | Sequence IDs used for smoke testing |
| `SMOKE_FRAME_LIMIT` | `int` | `20` | Maximum number of frames to process during smoke tests |

### Sensor Suite Configuration

`SENSOR_SUITE` (dict) defines the full sensor suite with type and properties:

```python
SENSOR_SUITE = {
    "R":   {"type": "radar"},
    "L1":  {"type": "lidar", "channels": 64},   # OS2-64 (alias: "L")
    "L2":  {"type": "lidar", "channels": 128},  # OS1-128
    "CF":  {"type": "camera", "position": "front"},
    "CL":  {"type": "camera", "position": "left"},
    "CR":  {"type": "camera", "position": "right"},
    "CRE": {"type": "camera", "position": "rear"},
}
```

> **Note:** `"L"` is NOT a separate key in `SENSOR_SUITE`. It is an alias resolved
> to `"L1"` by `normalize_sensor_label()` before any lookup into this dict.

### Camera Intrinsics

`CAMERA_INTRINSICS` (dict) holds placeholder camera intrinsic parameters for each camera. Currently all values are zeros (to be loaded from calibration files in production):

```python
CAMERA_INTRINSICS = {
    "CF":  {"fx": 0, "fy": 0, "cx": 0, "cy": 0},
    "CL":  {"fx": 0, "fy": 0, "cx": 0, "cy": 0},
    "CR":  {"fx": 0, "fy": 0, "cx": 0, "cy": 0},
    "CRE": {"fx": 0, "fy": 0, "cx": 0, "cy": 0},
}
```

Keys: `fx`, `fy` (focal lengths), `cx`, `cy` (principal point).

### Camera Extrinsics

`CAMERA_EXTRINSICS` (dict) holds placeholder camera extrinsic parameters (rotation matrix + translation vector). Currently all zeros:

```python
CAMERA_EXTRINSICS = {
    "CF":  {"R": [[0,0,0],[0,0,0],[0,0,0]], "t": [0,0,0]},
    "CL":  {"R": [[0,0,0],[0,0,0],[0,0,0]], "t": [0,0,0]},
    "CR":  {"R": [[0,0,0],[0,0,0],[0,0,0]], "t": [0,0,0]},
    "CRE": {"R": [[0,0,0],[0,0,0],[0,0,0]], "t": [0,0,0]},
}
```

Keys: `R` (3×3 rotation matrix), `t` (3-element translation vector in meters).

### Output Schema

`OUTPUT_SCHEMA` (list of str) defines the 48-column Parquet output table:

```
sequence_id, frame_idx, obj_tracking_id, obj_class,
obj_x, obj_y, obj_z, obj_length, obj_width, obj_height, obj_theta,
obj_distance_ego,
sensor_identify, weather,
radar_visible, radar_fov_in, radar_range_in, radar_sparsity_score,
lidar64_visible, lidar64_points_count, lidar64_sparsity_score,
lidar128_visible, lidar128_points_count, lidar128_sparsity_score,
cam_front_visible, cam_front_proj_x, cam_front_proj_y, cam_front_visibility_score,
cam_left_visible, cam_left_proj_x, cam_left_proj_y, cam_left_visibility_score,
cam_right_visible, cam_right_proj_x, cam_right_proj_y, cam_right_visibility_score,
cam_rear_visible, cam_rear_proj_x, cam_rear_proj_y, cam_rear_visibility_score,
num_sensors_visible, primary_sensor
```

### CPU-Only Flags

There are no explicit CPU-only boolean flags in `config.py`. CPU vs. GPU execution is controlled by:
- The `points_in_boxes_cpu` import path (always CPU in the current implementation)
- The absence of GPU-accelerated `points_in_boxes_gpu` in the active pipeline
- Future additions: a `FORCE_CPU = True` flag may be added here when GPU acceleration is introduced

### Module Boundary

- **Owner:** `config.py` is the single source of truth for all pipeline constants.
- **Consumers:** All modules in `kradar_visibility/` import from `config.py`. No module should hardcode these values.
- **Mutability:** Constants are not modified at runtime. To change configuration, edit the file and restart the pipeline.
- **Relationship to api_contracts.md:** The `OS2_64_PARAMS` and `OS1_128_PARAMS` dicts referenced in `api_contracts.md` § "Sensor Parameter Dictionaries" are derived from these `OS2_64_*` and `OS1_128_*` constants.

## Web Visualization Tool

The web visualization tool provides a user interface to visualize the sensor data and computed visibility scores.

It depends on the output of the pipeline (Parquet file) and the raw sensor data (point clouds, radar cubes, camera images).

The tool fetches data via the following API endpoints (defined in api_contracts.md):
- GET /api/visualization/data: returns metadata and URLs for the raw data for a given sequence and frame.
- GET /api/data/lidar/{sensor_type}/{sequence_id}/{frame_idx}: returns point cloud data.
- GET /api/data/radar/{sequence_id}/{frame_idx}: returns radar data.
- GET /api/data/camera/{camera_name}/{sequence_id}/{frame_idx}: returns camera image data.

The tool allows per-sequence, per-frame navigation and overlays oriented 3D bounding boxes on the sensor data.

It displays the computed visibility scores for each sensor modality.

## Aggregate Work Report

### Purpose

The Aggregate Work Report is a human-readable summary of the codebase state, test results, and known blockers. It is generated after a pipeline run (post-pipeline, post-test) and serves as a snapshot for debugging, progress tracking, and handoff between workers.

### Output Location

- **Directory:** `/home/adhish/Productivity/AMSCUP/docs/`
- **Filename:** `work_report_{run_id}.md` (e.g., `work_report_20260625_143000.md`)
- One file per pipeline run; reports are append-only and never overwritten.

### Report Generation Strategy

The report is generated by the `pipeline.py` module (or a dedicated `report_generator.py` if the logic grows complex). Generation is triggered:

1. **Primary trigger:** After `pipeline.py` completes a full run (end of `run_pipeline()` in `scripts/run_pipeline.py`).
2. **Secondary trigger:** When a builder or orchestrator explicitly calls `generate_work_report()` with the run context.

The generator collects data from:
- The pipeline's run metadata (run ID, timestamp, duration, sequences processed)
- Smoke test results (`tests/test_smoke.py` output)
- Verification test results (`tests/test_verify.py` output)
- The codebase file tree (working directory scan)
- Known blockers/TODOs (parsed from code comments and test failures)

### Report Sections

#### 1. Codebase Status
- Total files implemented vs. stubs remaining
- Phase completion indicators:
  - Phase 1: `config.py`, `parser.py`, `calibration.py`, `data_loader.py`
  - Phase 2: `radar_visibility.py`, `lidar_visibility.py`, `camera_visibility.py`
  - Phase 3: `pipeline.py`, `tests/test_smoke.py`, `tests/test_verify.py`
- Missing or incomplete files flagged explicitly

#### 2. Phase 1-3 Completion
- Per-phase summary: which modules are functional, which have known issues
- Dependency graph status (are all upstream inputs available?)

#### 3. Smoke Test Results (SMK-01..17)
- Table with columns: `Test ID | Module | Status (PASS/FAIL) | Notes`
- Summary line: `X/17 passed`

#### 4. Verification Test Results (VER-01..26)
- Table with columns: `Test ID | Category | Status (PASS/FAIL) | Notes`
- Summary line: `X/26 passed`

#### 5. Known Blockers and TODOs
- List of blockers (items that prevent further progress)
- List of TODOs (items deferred but not blocking)
- Cross-reference to kanban task IDs where applicable

#### 6. File Tree
- Full directory tree of the working directory (`/home/adhish/Productivity/AMSCUP/test-bed/src/Modules/robust_testing/kradar/`)
- Generated via `tree -L 4 --dirsfirst` or equivalent

### Report Data Flow

```
pipeline.py (run completes)
    ↓
scripts/run_pipeline.py
    ↓ calls
generate_work_report(run_metadata, test_results, codebase_state)
    ↓ writes
/home/adhish/Productivity/AMSCUP/docs/work_report_{run_id}.md
    ↓ optionally served by
GET /api/report/work_report/{run_id}  (see api_contracts.md)
```

### Module Boundary

- **Owner:** `pipeline.py` (or `report_generator.py` if split out)
- **Inputs:** Run metadata, test output, filesystem scan
- **Outputs:** Markdown file in `/home/adhish/Productivity/AMSCUP/docs/`
- **Downstream consumers:** Web visualization tool (Task 1), orchestrator dashboards, human reviewers
- **Excluded from this component:** The report does NOT generate Parquet data, does NOT run tests, and does NOT modify the codebase. It is a read-only observer.