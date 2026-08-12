# kradar_visibility — Architecture

## Overview

CPU-only visibility analysis pipeline for the K-Radar dataset.  Reads
`info_label_rev2/*.txt` annotations plus raw sensor data (radar zyx_cube,
OS2-64/OS1-128 LiDAR PCDs, 4-camera stereo images), computes per-object
visibility metrics for 7 sensors, and emits a single Parquet table.

The pipeline runs on toy-scale subsets (1-2 sequences, <=20 annotated frames)
in seconds on CPU.  Full-dataset and GPU-accelerated modes are out of scope.

## Module Layout

```
kradar_visibility/
├── __init__.py              # Public API re-exports
├── config.py                # Paths, sensor specs, schema, constants
├── parser.py                # info_label_rev2/*.txt parser
├── calibration.py           # Camera calibration loading (T_params_seq pickles)
├── data_loader.py           # Lazy sensor data loading (radar, lidar, camera)
├── radar_visibility.py      # SNR-weighted power density score
├── lidar_visibility.py      # CPU point-in-box count + expected-density ratio
├── camera_visibility.py     # 8-corner projection → area × centrality score
└── pipeline.py              # Orchestration: parse → compute → output
```

## Data Flow

```
sequence_ids
    │
    ▼
parser.get_sequence_label_files()        → List[Path]
    │
    ▼  (per label file)
parser.parse_label_file()                → (HeaderInfo, List[ObjectAnnotation])
    │
    ▼  (per frame)
data_loader.load_radar_cube()            → np.ndarray (Z, Y, X)
data_loader.load_lidar_points(os2-64)    → np.ndarray (N, 3)
data_loader.load_lidar_points(os1-128)   → np.ndarray (N, 3)
calibration.get_camera_params(dir, seq)  → List[dict] (intrinsics, radar2camera)
    │
    ▼  (per object in frame)
radar_visibility.compute_radar_sparsity_score()  → float [0, 1]
lidar_visibility.calculate_lidar_visibility()     → (visible, count, score) per sensor
camera_visibility.calculate_camera_visibility()   → dict{dir → float}
    │
    ▼
pipeline.compute_visibility_for_frame()   → List[dict]  (one per object)
    │
    ▼
polars.DataFrame → parquet write
```

## Module Responsibilities

### config.py

Single source of truth for all tunable parameters.  No computation; only
constants and schema definitions.

Key constants:
- `DATASET_ROOT` — absolute path to K-Radar repo
- `SENSOR_SUITE` — sensor ID → type/channels mapping
- `RADAR_FOV_AZIMUTH_DEG`, `RADAR_FOV_ELEVATION_DEG`, `RADAR_MAX_RANGE_M`
- `CAMERA_INTRINSICS`, `CAMERA_EXTRINSICS` — placeholder defaults (overridden by calibration)
- `OUTPUT_SCHEMA` — ordered list of column names in the Parquet output
- `SMOKE_SEQUENCE_IDS`, `SMOKE_FRAME_LIMIT` — toy-scale defaults

### parser.py

Parses `info_label_rev2/*.txt` files.  Pure I/O and regex; no sensor data loading.

Classes:
- `HeaderInfo(tesseract_idx, os2_64_idx, cam_front_idx, os1_128_idx, cam_lrr_idx, timestamp, raw)`
- `ObjectAnnotation(sensor_identify, tracking_id, obj_class, x, y, z, theta, length_half, width_half, height_half)`
  - Properties: `length`, `width`, `height`, `distance_ego`

Functions:
- `parse_header(line: str) -> HeaderInfo`
- `parse_object_line(line: str) -> Optional[ObjectAnnotation]`
- `parse_label_file(filepath: Path) -> (HeaderInfo, List[ObjectAnnotation])`
- `get_sequence_label_files(sequence_id, dataset_root) -> List[Path]`
- `parse_description_txt(sequence_id, dataset_root) -> dict`  (keys: location, time, weather)

### calibration.py

Loads camera calibration from `resources/cam_calib/T_params_seq/{N}` pickle files.

Data structure loaded from pickle:
```python
{
    'front0': {
        'camera_intrinsics': np.ndarray,  # 4×4
        'radar2camera':    np.ndarray,  # 4×4
        'camera2radar':    np.ndarray,  # 4×4
    },
    'front1': { ... },
    'right0':  { ... },
    'right1':  { ... },
    'rear0':   { ... },
    'rear1':   { ... },
    'left0':   { ... },
    'left1':   { ... },
}
```

Functions:
- `load_camera_calibration(seq=1) -> dict`
- `get_camera_params(direction, seq=1) -> List[dict]`  (length 2: two stereo sub-cameras)
- `get_T_radar2cam(cam_number, seq=1) -> np.ndarray`
- `get_camera_intrinsics(cam_number, seq=1) -> np.ndarray`
- `load_calibration(data_path) -> dict`  (placeholder; returns empty dict)

### data_loader.py

Lazy, per-frame sensor data loading.  All functions return `None` when the
file is missing — callers must handle None.

Functions:
- `load_radar_cube(sequence_id, frame_idx, dataset_root) -> Optional[np.ndarray]`
  - Reads `radar_zyx_cube/cube_{frame_idx}.mat` via scipy.io.loadmat
  - Returns the first non-meta key; shape (Z, Y, X)
- `read_pcd_file(filepath) -> np.ndarray`
  - Reads PCD header, supports ascii and binary float32 data
  - Returns (N, 3) float32
- `load_lidar_points(sequence_id, frame_idx, sensor, dataset_root) -> Optional[np.ndarray]`
  - Reads `{sensor}/{sensor}_{frame_idx}.pcd`
- `load_camera_image(sequence_id, frame_idx, camera, dataset_root) -> Optional[np.ndarray]`
  - Reads `cv2.imread`; returns (720, 2560, 3) BGR (stereo pair stitched)
- `get_camera_image_path(...) -> Optional[Path]`

### radar_visibility.py

Implements §4.1 method B: SNR-weighted power density on `radar_zyx_cube`.

Algorithm:
1. Convert raw linear power to dB: `10 * log10(power)` for cells > 0
2. Estimate per-frame noise floor as median of valid dB values
3. Extract bbox voxel subset (integer indices from `_world_to_voxel`)
4. Compute mean SNR excess over noise floor
5. Normalise by `DB_HEADROOM` (20 dB) → clip to [0, 1]

Key constant: `DB_HEADROOM = 20.0`

Functions:
- `compute_radar_sparsity_score(radar_zyx_cube: np.ndarray, bbox: dict) -> float`
  - bbox keys: `z_min, z_max, y_min, y_max, x_min, x_max` (integer voxel indices)
- `radar_visibility(radar_zyx_cube, object_bboxes) -> List[float]`

### lidar_visibility.py

Implements §4.2 method A+B: CPU point-in-box count → expected-density ratio.

Algorithm per object:
1. Center-point FOV/range check (object center vs. sensor envelope)
2. Count points inside axis-aligned bbox (vectorised NumPy mask)
3. Normalise: `score = count / expected_density`
   - `expected_density = (channels * vfov / 360) * (360 / hres)`

Functions:
- `calculate_lidar_visibility(points, bboxes, fov, range_limit, expected_density) -> (visible, points_count, sparsity_score)`
  - All three return arrays are 1-D numpy, one entry per bbox
  - `visible: bool[n]`, `points_count: int[n]`, `sparsity_score: float[n]`
- `read_pcd_file(filepath) -> np.ndarray`  (duplicate of data_loader's version)

### camera_visibility.py

Implements §4.3 method B: 8-corner projection → 2D bbox → area/centrality score.

Algorithm per object per camera:
1. Project all 8 3D bbox corners via `K * [R|t] * X_world`
2. Reject if any corner has `z_cam <= 0`
3. Compute 2D AABB from projected (u, v); clip to image bounds
4. Score = `W1 * (clipped_area / image_area) + W2 * (1 - normalised_center_dist)`

Constants: `W1 = 0.7` (area), `W2 = 0.3` (centrality), `HALF_WIDTH = 1280`, `HALF_HEIGHT = 720`

Functions:
- `project_point_to_image(point_3d, camera_intrinsics, T_radar2cam) -> (u, v, z_cam)`
  - Returns raw (u, v) — no clipping.  `z_cam > 0` gates visibility.
- `calculate_visibility_score(obj_corners, cam_params) -> float`
  - Returns 0.0 if behind camera or completely outside image
- `calculate_camera_visibility(obj_corners, seq=1) -> dict{dir → float}`
  - Keys: 'front', 'left', 'right', 'rear'
  - Each direction uses max(score_subcam0, score_subcam1)

### pipeline.py

Top-level orchestration.  Wires all modules together.

Key internal helpers:
- `_world_to_voxel(x, y, z) -> (vz, vy, vx)` — meters → radar cube indices
- `_radar_fov_check(x, y, z) -> bool` — azimuth/elevation cone test
- `_radar_range_check(x, y, z) -> bool` — 0–118 m test
- `_obj_corners(obj) -> np.ndarray` — (8, 3) rotated bbox corners
- `_bbox_voxels_from_annotation(obj) -> dict` — rotated AABB in voxel space
- `_bbox_list_from_annotation(obj) -> list` — [xmin,xmax,ymin,ymax,zmin,zmax] in meters
- `_assert_radar_cube_shape(cube)` — runtime shape guard (logs warning on mismatch)

Grid constants (radar zyx_cube):
- X: [0, 100] m, grid 250
- Y: [-80, 80] m, grid 400
- Z: [-30, 30] m, grid 150

Public functions:
- `compute_visibility_for_frame(sequence_id, header, objects, dataset_root, calib_available) -> List[dict]`
  - Loads sensor data once per frame; iterates objects; returns row dicts
- `run(sequence_ids, frame_limit, dataset_root, output_path) -> pl.DataFrame`
  - Main entry point.  Handles calibration pre-check, frame selection (skips empty frames), per-sequence iteration.
  - `frame_limit` selects N annotated frames (not raw file count), skipping files with zero objects.

## Error Handling Strategy

- Missing sensor file → `None` from data_loader → `visible=False, score=0.0`
- Calibration load failure → log warning, `calib_available=False` → camera metrics zeroed
- Empty result set → log warning, return empty `pl.DataFrame()`
- Per-frame exceptions → log warning, skip frame, continue

## Configuration Format

All configuration is in `config.py` as module-level constants.  No external config
file is loaded at runtime.  To change behavior, edit the constants in `config.py`.

For the CLI entry point (`scripts/run_pipeline.py`), configuration is via
command-line arguments:
- `--sequences`: sequence IDs (default: 1, 2)
- `--frame-limit`: max annotated frames per sequence (default: 20)
- `--output`: Parquet output path (default: outputs/visibility_output.parquet)
- `--dataset-root`: override `DATASET_ROOT`
- `--no-report`: skip verification report generation

## Output Schema

One row per (sequence, frame, tracked object).  Columns defined in `config.OUTPUT_SCHEMA`:

| Column | Type | Source |
|--------|------|--------|
| sequence_id | str | folder name |
| frame_idx | int | header tesseract_idx |
| timestamp | float64 | header |
| obj_tracking_id | int | annotation |
| obj_class | str | annotation |
| obj_x/y/z | float | annotation (meters) |
| obj_theta | float | annotation (radians) |
| obj_length/width/height | float | annotation (full, meters) |
| obj_distance_ego | float | computed (meters) |
| sensor_identify | str | annotation |
| weather | str | description.txt field 3 (validated against ALLOWED_WEATHER, fallback "normal") |
| environment | str \| null | description.txt field 1 (`location` key), unvalidated |
| time_of_day | str \| null | description.txt field 2 (`time` key), unvalidated |
| frame_object_count | int | computed: len(objects) for this frame, broadcast to all its rows |
| radar_visible | bool | computed |
| radar_fov_in | bool | computed |
| radar_range_in | bool | computed |
| radar_sparsity_score | float | radar_visibility |
| lidar64_visible | bool | computed |
| lidar64_points_count | int | lidar_visibility |
| lidar64_sparsity_score | float | lidar_visibility |
| lidar128_visible | bool | computed |
| lidar128_points_count | int | lidar_visibility |
| lidar128_sparsity_score | float | lidar_visibility |
| cam_{dir}_visible | bool | camera_visibility |
| cam_{dir}_proj_x/y | float | camera_visibility (pixels) |
| cam_{dir}_visibility_score | float | camera_visibility |
| num_sensors_visible | int | computed |
| primary_sensor | str | computed (argmax of scores) |

## Test Structure

- `tests/conftest.py` — session-scoped fixtures: `dataset_root`, `smoke_sequence_ids`, `smoke_frame_limit`, `output_table`
- `tests/test_smoke.py` — SMK-01..17 + extra sanity checks (frame_limit selection, all-sequences accessibility)
- `tests/test_verify.py` — VER-01..26 (sensor-id consistency, distance correlation, projection sanity, primary-sensor logic, data quality, optional weather impact)
- `scripts/run_pipeline.py` — CLI entry point with argparse, summary printing, and verification report generation via pytest JSON report

## Dependencies

- numpy — array operations, point-in-box, projection
- polars — DataFrame construction, Parquet I/O
- pyarrow — Parquet support
- scipy.io — radar .mat loading
- opencv-python-headless — camera image loading
- pyyaml — (reserved for future config)
- pytest + pytest-json-report — testing infrastructure

## K-Radar Web Viewer — Architecture Addendum

### Overview

A lightweight FastAPI web server that serves K-Radar sensor data and annotations
as JSON/image API endpoints, backed by a static single-page HTML/JS frontend.
CPU-only; no GPU.  Runs on toy-scale (2 sequences, ≤20 frames) with no pagination.

### Architecture Decision: FastAPI + Static HTML/JS

**Chosen over Flask/Jinja2** because:
- Clean separation between API (JSON) and frontend (static files) mirrors the
  existing module boundary between `pipeline.py` (computation) and the viewer.
- FastAPI's Pydantic models give automatic request/response validation, useful
  as the canonical source of truth for what the frontend can expect.
- uvicorn is ASGI-based and production-viable; swapping to the Jinja2 approach
  later would require a full rewrite.
- The `kradar_visibility` package and the viewer share `config.py` and
  `data_loader.py` — no duplication of file-loading logic.

**New files only** (existing files untouched):

```
src/kradar_visibility/viewer/
├── __init__.py
├── server.py        # FastAPI app + endpoints
└── static/
    ├── index.html   # Single-page app shell
    ├── style.css    # Layout + panel styling
    └── app.js       # DOM wiring + render loops
```

### API Endpoints

| Method | Path | Description | Response |
|--------|------|-------------|----------|
| GET | `/api/sequences` | List available sequence IDs | `[{id: str, path: str}]` |
| GET | `/api/frames/{seq_id}` | Frame indices for a sequence | `[{frame_idx: int, label_file: str}]` |
| GET | `/api/frame/{seq_id}/{frame_idx}` | Full frame: annotations + visibility scores + box corners | `FrameResponse` |
| GET | `/api/image/{seq_id}/{cam}/{frame_idx}` | Camera JPEG (2560×720 stereo-stitched) | binary JPEG |
| GET | `/api/lidar/{seq_id}/{sensor}/{frame_idx}` | LiDAR points as JSON | `{points: [[x,y,z], ...]}` |
| GET | `/api/radar/{seq_id}/{frame_idx}` | Radar zyx_cube as top-down PNG heatmap | binary PNG |

**`FrameResponse` schema**: JSON with `sequence_id`, `frame_idx`, `timestamp`,
`objects[]`.  Each object has `tracking_id`, `obj_class`, `x/y/z`, `length/width/height`,
`theta`, `corners_3d` (8 corners, radar frame), `corners_2d_cam` (per direction,
null if invisible), and `visibility` (radar/lidar64/lidar128/cam_front/cam_left/
cam_right/cam_rear scores plus `num_sensors_visible` and `primary_sensor`).

### Frontend Layout (Single Page)

```
+-----------------------------------------------------------------------+
|  [Sequence ▼] [Frame ────── slider ──────]  [282/20]                  |
+-----------------------+-----------------------------------------------+
|                       |                                               |
|   Camera View         |   Radar Heatmap (top-down)                 |
|   (<img> + SVG box    |   - X: forward, Y: left                    |
|   overlays)           |   - Color: mean SNR (dark=high)             |
|                       |   - Oriented 3D AABB drawn as polygon       |
+-----------------------+-----------------------------------------------+
|                       |                                               |
|   LiDAR Top-Down      |   Visibility Scores Table                  |
|   (2D scatter,        |   - Per-object, per-sensor scores          |
|   color=Z height)     |   - Color-coded bar indicators              |
|                       |   - Primary sensor highlight               |
+-----------------------+-----------------------------------------------+
```

- **Camera View**: `<img>` stereo-stitched 2560×720 image.  SVG overlay draws 2D
  projected box as a polygon from `corners_2d_cam`.  Class label + tracking ID
  as SVG text.
- **Radar Heatmap**: `<canvas>` renders top-down (XZ plane collapsed via max
  projection).  Color-mapped canvas.  Oriented 3D AABB drawn as rotated rectangle.
- **LiDAR Top-Down**: `<canvas>` 2D scatter (X-Y plane), colored by Z height.
  Oriented box drawn as rotated rectangle.
- **Visibility Table**: HTML table with per-object rows.  Score bars as colored
  `<div>` width.  Columns: object ID, class, radar score, lidar64 pts/score,
  lidar128 pts/score, cam_front/left/right/rear scores, primary sensor.

### Data Flow

```
Browser                    FastAPI server (server.py)
  │                               │
  │ GET /api/sequences            │ ← reads data/{1,2}/ directories
  │  ← [{id:"1"},{id:"2"}]        │
  │                               │
  │ GET /api/frame/1/282          │ ← pipeline.compute_visibility_for_frame()
  │  ← FrameResponse              │    (reuses existing modules; can pre-compute to Parquet)
  │                               │
  │ GET /api/image/1/cam-front/282│ ← data_loader.load_camera_image()
  │  ← JPEG binary                │
  │                               │
  │ GET /api/lidar/1/os2-64/282   │ ← data_loader.load_lidar_points()
  │  ← {points: [...]}           │
  │                               │
  │ GET /api/radar/1/282         │ ← radar zyx_cube → numpy → PNG encode
  │  ← PNG binary                │
```

**Performance note**: Toy scale (2 seq × 20 frames) — all data fits in RAM.
No caching needed.  `functools.lru_cache` on API routes is the first escalation
step if needed.

### Reuse of Existing Modules

| Module | Role in Viewer |
|--------|---------------|
| `config.py` | `DATASET_ROOT`, sensor constants |
| `data_loader.py` | `load_radar_cube`, `load_lidar_points`, `load_camera_image` — reused as-is |
| `calibration.py` | `get_camera_params` — used to project 3D corners |
| `camera_visibility.py` | `project_point_to_image` — used to compute 2D box corners |
| `pipeline.py` | `compute_visibility_for_frame` — called to get per-object scores.  Output can be pre-computed to Parquet and served via `pl.scan_parquet()` |

**Viewer does NOT call**: `radar_visibility`, `lidar_visibility` — those are
already invoked inside `compute_visibility_for_frame`.

### New Dependencies (add to pyproject.toml)

```toml
dependencies = [
    ...
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
]
```

No new frontend dependencies — pure HTML5 Canvas + Vanilla JS + SVG keeps the
bundle zero and avoids any build step.

### Running the Viewer

```bash
cd src/kradar_visibility/viewer
uv run uvicorn server:app --reload --port 8000
# Open http://localhost:8000/static/index.html
```
