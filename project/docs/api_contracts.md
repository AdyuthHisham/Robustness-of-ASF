# Sensor Identification Logic

## Mapping of Labels to Physical Sensors

Based on analysis of `info_label_rev2/*.txt` files and cross-referencing with calibration files, the following **canonical** mapping is established:

| Label | Physical Sensor | Canonical Key | Channels |
|-------|----------------|---------------|----------|
| `L`  | OS2-64 LiDAR   | `L1`          | 64       |
| `L1` | OS2-64 LiDAR   | `L1`          | 64       |
| `L2` | OS1-128 LiDAR  | `L2`          | 128      |

**Resolution rule:** `L` is an alias for `L1`. Both resolve to OS2-64. There is no
configuration in the K-Radar dataset where `L` refers to OS1-128.

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

### `normalize_sensor_label(raw_label: str) -> str`

Normalize raw sensor identification labels from `info_label_rev2/*.txt` to canonical form.

- **Input**: Raw label string as it appears in the dataset (e.g., `"L"`, `"L1"`, `"L2"`, `"R"`, `"CF"`, `"CL"`, `"CR"`, `"CRE"`).
- **Output**: Canonical key — one of `L1`, `L2`, `R`, `CF`, `CL`, `CR`, `CRE`.
- **Behavior**:
  - `"L"` → `"L1"` (alias resolution)
  - `"L1"` → `"L1"` (identity)
  - `"L2"` → `"L2"` (identity)
  - `"R"`, `"CF"`, `"CL"`, `"CR"`, `"CRE"` → unchanged (pass-through)
  - Any other value → raise `ValueError`
- **Module**: `parser.py`
- **Callers**: `data_loader.py` (during label file loading), `pipeline.py` (during Parquet write — guaranteed canonical by this point)

### Verification Check

- **SENS-01**: After normalization, no row in the Parquet output shall contain `L` as the `sensor_identify` value. Only canonical keys (`L1`, `L2`, `R`, `CF`, `CL`, `CR`, `CRE`) are valid in the output schema.

## Output

The mapping rule is enforced at the parse boundary. All downstream modules (visibility computation, Parquet writer, web API) receive only canonical keys. No module should accept raw `L` labels — normalization happens once at the input boundary in `parser.py`.

## Weather Column in Output Parquet Schema

As part of Task 6 (Weather Data Gathering), a new column `weather` has been added to the Object Identity section of the output Parquet schema. The column is a string that can be one of `clear`, `overcast`, `fog`, `rain`, `sleet`, `snow`, or null if the `description.txt` file is missing for a sequence (or if the weather field is absent/unparseable after normalization).

This column is used in the following verification checks:

- **SMK-04**: Weather labels (after normalization) must be in `WEATHER_LABELS`.
- **VER-25**: LiDAR point counts (or sparsity scores) are statistically lower in adverse weather (rain, sleet, snow) compared to clear weather.
- **VER-26**: Radar vs LiDAR weather sensitivity (requires weather column).

## Weather Data Parsing — Function Contracts

### `parse_description_file(filepath: Path) -> dict | None`
- **Input**: Path to a `description.txt` file.
- **Output**: `{"location": str, "time_of_day": str, "weather": str}` or `None` if the file does not exist, is empty, or does not contain exactly 3 comma-separated fields.
- **Behavior**:
  1. Read file contents, strip whitespace.
  2. Split on comma → expect exactly 3 fields: `location`, `time_of_day`, `weather`.
  3. Return dict with raw (un-normalized) field values.
  4. Return `None` if file missing, empty, or parse fails.
- **Errors**: Missing file → return `None` (do not raise). Malformed line → return `None`.

### `normalize_weather(raw_label: str) -> str`
- **Input**: Raw weather string from parsed file.
- **Output**: Normalized label — one of `clear`, `overcast`, `fog`, `rain`, `sleet`, `snow`.
- **Mapping**:
  - `"normal"` → `"clear"`
  - `"heavysnow"` → `"snow"`
  - `"clear"`, `"overcast"`, `"fog"`, `"rain"`, `"sleet"`, `"snow"` → unchanged
  - Any other value → log warning, return `"unknown"` (callers may treat as nullable)
- **Case handling**: Input is lowercased before mapping.

### `collect_weather_for_sequence(sequence_id: str, dataset_root: Path) -> str | None`
- **Input**: Sequence folder identifier (e.g., `"1"`, `"42"`); root path of the dataset.
- **Output**: Normalized weather label, or `None` if `description.txt` does not exist for the sequence.
- **Behavior**:
  1. Construct path: `dataset_root / "data" / sequence_id / "description.txt"`.
  2. Call `parse_description_file(path)`.
  3. If `None`, return `None`.
  4. Call `normalize_weather(parsed["weather"])`.
  5. If result is `"unknown"`, log warning and return `None` (treat as missing).
  6. Otherwise return the normalized label.

### Pipeline Integration
- `pipeline.py` calls `collect_weather_for_sequence` once per sequence at the start of a run.
- The result is stored in a dict `weather_by_seq[sequence_id]: str | None`.
- When writing the Parquet output, each row's `weather` column is populated from this dict using `sequence_id` as the key.
- If `weather_by_seq[sequence_id]` is `None`, the column for that row is written as `null`.

## Error Handling for Weather Data

| Scenario | Behavior |
|----------|----------|
| `description.txt` missing for a sequence | Return `None`; weather column is `null` for all frames of that sequence |
| Malformed line (not 3 comma-separated fields) | Log warning, return `None` |
| Empty file | Log warning, return `None` |
| Unknown weather value (after normalization maps to `"unknown"`) | Log warning, return `None`; exclude from SMK-04 pass criteria |
| Sequence folder missing entirely | Log warning, skip |
## LiDAR Verification Methodology

### Method A: Raw Point-in-Box Counts

- Compute raw point counts for OS2-64 and OS1-128 LiDAR sensors within each oriented 3D bounding box using CPU-based point-in-box.
- Output fields: `lidar64_points_count`, `lidar128_points_count`.

### Method B: Expected-Density Normalization (Sparsity Score)

- Compute expected point count per box based on LiDAR sensor characteristics:
  - `expected_count ≈ (vertical_channels × vertical_extent_angle / total_vertical_fov) × (horizontal_extent_angle / horizontal_angular_resolution)`
  - where vertical_extent_angle and horizontal_extent_angle are derived from the object's 3D bounding box dimensions and orientation.
- Sparsity score = `actual_count / expected_count`, clipped to [0, 1] (or 0-1 range as per spec).
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

## Web Visualization Tool API Endpoints

The web visualization tool requires the following API endpoints to fetch data for visualization:

### Get Visualization Metadata
- **Endpoint**: `GET /api/visualization/data`
- **Query Parameters**:
  - `sequence_id` (string): Identifier of the sequence.
  - `frame_idx` (integer): Frame index within the sequence.
- **Response**:
  ```json
  {
    "sequence_id": "string",
    "frame_idx": integer,
    "timestamp": "ISO 8601 timestamp",
    "data_urls": {
      "lidar": {
        "os2-64": "/api/data/lidar/os2-64/{sequence_id}/{frame_idx}",
        "os1-128": "/api/data/lidar/os1-128/{sequence_id}/{frame_idx}"
      },
      "radar": "/api/data/radar/{sequence_id}/{frame_idx}",
      "cameras": {
        "front": "/api/data/camera/front/{sequence_id}/{frame_idx}",
        "left": "/api/data/camera/left/{sequence_id}/{frame_idx}",
        "right": "/api/data/camera/right/{sequence_id}/{frame_idx}",
        "rear": "/api/data/camera/rear/{sequence_id}/{frame_idx}"
      },
      "labels": "/api/data/labels/{sequence_id}/{frame_idx}",
      "calibration": "/api/data/calibration/{sequence_id}"
    },
    "bounding_boxes": [
      {
        "obj_tracking_id": integer,
        "obj_class": string,
        "obj_x": float,
        "obj_y": float,
        "obj_z": float,
        "obj_length": float,
        "obj_width": float,
        "obj_height": float,
        "obj_theta": float,
        "sensor_identify": string,
        "visibility_scores": {
          "radar": float | null,
          "lidar64": float | null,
          "lidar128": float | null,
          "camera_front": float | null,
          "camera_left": float | null,
          "camera_right": float | null,
          "camera_rear": float | null
        }
      }
    ]
  }
  ```

### Get LiDAR Point Cloud Data
- **Endpoint**: `GET /api/data/lidar/{sensor_type}/{sequence_id}/{frame_idx}`
- **Path Parameters**:
  - `sensor_type`: string, either `os2-64` or `os1-128`
  - `sequence_id`: string
  - `frame_idx`: integer
- **Response**: Binary point cloud data (e.g., PCD format or custom binary format) or JSON array of points.
  - Example JSON response:
    ```json
    {
      "points": [
        {"x": float, "y": float, "z": float, "intensity": float},
        ...
      ]
    }
    ```

### Get Radar Data Cube
- **Endpoint**: `GET /api/data/radar/{sequence_id}/{frame_idx}`
- **Path Parameters**:
  - `sequence_id`: string
  - `frame_idx`: integer
- **Response**: Radar data cube (Doppler-collapsed) as a 3D array or binary format.
  - Example JSON response:
    ```json
    {
      "data": [[[float]]],  // 3D array: [azimuth, elevation, range] or similar
      "shape": [int, int, int],
      "unit": "dB"
    }
    ```

### Get Camera Image
- **Endpoint**: `GET /api/data/camera/{camera_name}/{sequence_id}/{frame_idx}`
- **Path Parameters**:
  - `camera_name`: string, one of `front`, `left`, `right`, `rear`
  - `sequence_id`: string
  - `frame_idx`: integer
- **Response**: Image data (e.g., JPEG, PNG) or binary image data.
  - If returning JSON (for base64 encoded image):
    ```json
    {
      "image": "base64 encoded string",
      "format": "jpeg",
      "width": int,
      "height": int
    }
    ```

### Get Labels for Frame
- **Endpoint**: `GET /api/data/labels/{sequence_id}/{frame_idx}`
- **Path Parameters**:
  - `sequence_id`: string
  - `frame_idx`: integer
- **Response**: Label information for the frame (parsed from `info_label_rev2/*.txt`).
  - Example JSON response:
    ```json
    {
      "sequence_id": "string",
      "frame_idx": integer,
      "objects": [
        {
          "obj_tracking_id": integer,
          "obj_class": string,
          "obj_x": float,
          "obj_y": float,
          "obj_z": float,
          "obj_length": float,
          "obj_width": float,
          "obj_height": float,
          "obj_theta": float,
          "sensor_identify": string
        }
      ]
    }
    ```

### Get Calibration Data
- **Endpoint**: `GET /api/data/calibration/{sequence_id}`
- **Path Parameters**:
  - `sequence_id`: string
- **Response**: Calibration matrices for all sensors.
  - Example JSON response:
    ```json
    {
      "sequence_id": "string",
      "calibration": {
        "os2-64": {
          "K": [[float]],  // 3x3 intrinsics
          "R": [[float]],  // 3x3 rotation
          "t": [float]     // 3x1 translation
        },
        "os1-128": {
          "K": [[float]],
          "R": [[float]],
          "t": [float]
        },
        "radar": {
          // radar calibration if applicable
        },
        "cameras": {
          "front": {"K": [[float]], "R": [[float]], "t": [float]},
          "left": {"K": [[float]], "R": [[float]], "t": [float]},
          "right": {"K": [[float]], "R": [[float]], "t": [float]},
          "rear": {"K": [[float]], "R": [[float]], "t": [float]}
        }
      }
    }
    ```

## Aggregate Work Report Endpoint

The aggregate work report endpoint serves the generated work report content (see architecture.md, "Aggregate Work Report" section).

### Get Work Report
- **Endpoint**: `GET /api/report/work_report/{run_id}`
- **Path Parameters**:
  - `run_id` (string): Unique identifier for the pipeline run (e.g., `20260625_143000`)
- **Response**:
  - `200 OK`: Returns the full work report as JSON.
  - `404 Not Found`: No report exists for the given `run_id`.
  - `500 Internal Server Error`: Report generation or read failed.

  ```json
  {
    "run_id": "string",
    "generated_at": "ISO 8601 timestamp",
    "report_file": "/home/adhish/Productivity/AMSCUP/docs/work_report_{run_id}.md",
    "content": {
      "codebase_status": {
        "total_files": int,
        "files_implemented": int,
        "stubs_remaining": int,
        "phase_1_complete": bool,
        "phase_2_complete": bool,
        "phase_3_complete": bool
      },
      "phase_completion": {
        "phase_1": {
          "config": "functional | stub | missing",
          "parser": "functional | stub | missing",
          "calibration": "functional | stub | missing",
          "data_loader": "functional | stub | missing"
        },
        "phase_2": {
          "radar_visibility": "functional | stub | missing",
          "lidar_visibility": "functional | stub | missing",
          "camera_visibility": "functional | stub | missing"
        },
        "phase_3": {
          "pipeline": "functional | stub | missing",
          "test_smoke": "functional | stub | missing",
          "test_verify": "functional | stub | missing"
        }
      },
      "smoke_test_results": {
        "passed": "int",
        "total": 17,
        "tests": [
          {
            "id": "SMK-01",
            "module": "parser",
            "status": "PASS | FAIL",
            "notes": "string"
          }
        ]
      },
      "verification_test_results": {
        "passed": "int",
        "total": 26,
        "tests": [
          {
            "id": "VER-01",
            "category": "Sensor Identify",
            "status": "PASS | FAIL",
            "notes": "string"
          }
        ]
      },
      "blockers": [
        {
          "description": "string",
          "affected_modules": ["string"],
          "kanban_task_id": "string (optional)"
        }
      ],
      "todos": [
        {
          "description": "string",
          "affected_modules": ["string"]
        }
      ],
      "file_tree": "string (directory tree as text)"
    }
  }
  ```

- **Notes**:
  - The endpoint reads the generated markdown report and serves it as structured JSON.
  - If the report has not been generated yet for the given `run_id`, return 404.
  - The `content` field may also be served as raw Markdown via `Accept: text/markdown` content negotiation (returns the raw file content with `Content-Type: text/markdown`).

### List Work Reports
- **Endpoint**: `GET /api/report/work_reports`
- **Query Parameters**:
  - `limit` (integer, optional): Maximum number of reports to return (default 10)
  - `offset` (integer, optional): Pagination offset (default 0)
- **Response**:
  ```json
  {
    "reports": [
      {
        "run_id": "string",
        "generated_at": "ISO 8601 timestamp",
        "report_file": "/home/adhish/Productivity/AMSCUP/docs/work_report_{run_id}.md",
        "pipeline_duration_seconds": float,
        "sequences_processed": int,
        "smoke_pass_rate": "float (0.0-1.0)",
        "verify_pass_rate": "float (0.0-1.0)"
      }
    ],
    "total": int
  }
  ```

## LiDAR Visibility Module — Function Contracts

The `lidar_visibility.py` module implements Method A (CPU point-in-box) and Method B (expected-density normalization). It must expose the following functions:

### `compute_lidar_points_count(points: np.ndarray, boxes: np.ndarray) -> np.ndarray`
- **Input**: `(N, 3)` LiDAR points in ego frame; `(M, 7)` boxes `(cx, cy, cz, dx, dy, dz, heading)`.
- **Output**: `(M,)` int64 per-box point counts.
- **Implementation**: Call `points_in_boxes_cpu` from the test-bed archive, then `counts_from_box_idxs`.

### `compute_expected_count(box: np.ndarray, sensor_params: dict) -> float`
- **Input**: `(7,)` array for a single box `(cx, cy, cz, dx, dy, dz, heading)`; `sensor_params` dict with keys `vertical_channels`, `total_v_fov_deg`, `h_angular_res_deg`.
- **Output**: Expected point count (float) per the Method B formula.
- **Implementation**: See architecture.md § "Expected-Density Normalization".

### `compute_lidar_sparsity_score(actual_count: int, expected_count: float) -> float`
- **Input**: Actual point count and expected count for a single box/sensor.
- **Output**: `clip(actual / expected, 0.0, 1.0)`; returns `0.0` if `expected <= 0` or `actual <= 0`.

### `check_lidar_visible(points_count: int, box: np.ndarray, sensor_params: dict) -> bool`
- **Input**: Point count, `(7,)` box, sensor params dict (must include `max_range_m`, `h_fov_deg`, `v_fov_deg`).
- **Output**: `True` if `points_count > 0` AND box center within FOV cone AND within range.

### `process_frame_lidar(lidar_points: np.ndarray, boxes: np.ndarray, sensor_params: dict) -> dict`
- **Input**: `(N, 3)` LiDAR points for one frame; `(M, 7)` boxes; sensor params.
- **Output**: Dict with keys `lidar_visible` (M bool array), `lidar_points_count` (M int64 array), `lidar_sparsity_score` (M float array, nullable via `None` or `np.nan`).
- **Implementation**: Orchestrates the above functions per box per frame.

### Sensor Parameter Dictionaries

```python
OS2_64_PARAMS = {
    "vertical_channels": 64,
    "total_v_fov_deg": 33.2,
    "h_angular_res_deg": 0.35,
    "max_range_m": 70.0,
    "h_fov_deg": 180.0,   # 360° scan, but effective FOV for object detection is ~180°
    "v_fov_deg": 33.2,
}

OS1_128_PARAMS = {
    "vertical_channels": 128,
    "total_v_fov_deg": 44.5,
    "h_angular_res_deg": 0.17,
    "max_range_m": 120.0,
    "h_fov_deg": 180.0,
    "v_fov_deg": 44.5,
}
```

These should be defined in `config.py` and imported by `lidar_visibility.py`.

## Notes
- All endpoints should return appropriate HTTP status codes (200 for success, 404 for not found, 500 for server errors).
- Binary data endpoints may optionally support raw binary responses with appropriate Content-Type headers.
- The visualization tool may cache or prefetch data as needed.
- Authentication and rate limiting are out of scope for this validation tool but may be added in production.

## Configuration

All pipeline configuration constants are defined in `config.py` (`kradar_visibility/config.py`). See `architecture.md` § "config.py — Pipeline Configuration Constants" for the full reference.

There are currently no API endpoints that expose or modify these configuration values, as they are intended to be set at import time and used internally by the pipeline components.

### Config Constants Reference

| Constant | Type | Value | Used By |
|----------|------|-------|---------|
| `DATASET_ROOT` | `Path` | `/home/adhish/Productivity/AMSCUP/repos/K-Radar` | `data_loader.py` |
| `KRADAR_ROOT` | `str` | `str(DATASET_ROOT)` | Legacy string paths |
| `RADAR_FOV_AZIMUTH_DEG` | `float` | `107.0` | `radar_visibility.py` |
| `RADAR_FOV_ELEVATION_DEG` | `float` | `37.0` | `radar_visibility.py` |
| `RADAR_MAX_RANGE_M` | `float` | `118.0` | `radar_visibility.py` |
| `CAM_HALF_WIDTH` | `int` | `1280` | `camera_visibility.py` |
| `CAM_HALF_HEIGHT` | `int` | `720` | `camera_visibility.py` |
| `CAM_W1` | `float` | `0.7` | `camera_visibility.py` (area weight) |
| `CAM_W2` | `float` | `0.3` | `camera_visibility.py` (centrality weight) |
| `OS2_64_CHANNELS` | `int` | `64` | `lidar_visibility.py` |
| `OS2_64_VFOV_DEG` | `float` | `33.2` | `lidar_visibility.py` |
| `OS2_64_HRES_DEG` | `float` | `0.35` | `lidar_visibility.py` |
| `OS1_128_CHANNELS` | `int` | `128` | `lidar_visibility.py` |
| `OS1_128_VFOV_DEG` | `float` | `44.5` | `lidar_visibility.py` |
| `OS1_128_HRES_DEG` | `float` | `0.17` | `lidar_visibility.py` |
| `ALLOWED_WEATHER` | `set` | `{"clear","overcast","fog","rain","sleet","snow","normal"}` | `data_loader.py` |
| `WEATHER_LABELS` | `list` | `["clear","overcast","fog","rain","sleet","snow"]` | Output schema |
| `SMOKE_SEQUENCE_IDS` | `list` | `["1","2"]` | `tests/test_smoke.py` |
| `SMOKE_FRAME_LIMIT` | `int` | `20` | `tests/test_smoke.py` |
| `SENSOR_SUITE` | `dict` | See below | `pipeline.py`, `data_loader.py` |
| `CAMERA_INTRINSICS` | `dict` | Placeholder (all zeros) | `camera_visibility.py` |
| `CAMERA_EXTRINSICS` | `dict` | Placeholder (all zeros) | `camera_visibility.py` |
| `OUTPUT_SCHEMA` | `list[str]` | 48 columns | `pipeline.py` (Parquet writer) |

### Sensor Suite Dict

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

> **Note:** `"L"` is NOT a separate key. It is an alias resolved to `"L1"` by
> `normalize_sensor_label()` before any lookup into this dict.

### Camera Intrinsics Schema

```python
CAMERA_INTRINSICS = {
    "CAM_ID": {"fx": float, "fy": float, "cx": float, "cy": float},
    # ... one entry per camera: CF, CL, CR, CRE
}
```

### Camera Extrinsics Schema

```python
CAMERA_EXTRINSICS = {
    "CAM_ID": {"R": [[float]*3]*3, "t": [float]*3},
    # ... one entry per camera: CF, CL, CR, CRE
}
```

### Output Schema (48 columns)

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

### Sensor Mounting Offsets (Ego Frame Transform)

Raw LiDAR point clouds are reported in the sensor frame. To perform point-in-box in ego frame (where annotations live), apply the mounting offset:

| Sensor | Offset (x, y, z) meters |
|--------|------------------------|
| LiDAR (OS2-64 / OS1-128) | `(-2.54, 0.3, 0.7)` |
| Radar | `(-0.18, -0.12, 0.19)` |

Transform: `ego_point = sensor_point + offset`