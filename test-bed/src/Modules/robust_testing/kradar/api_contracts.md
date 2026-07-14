# kradar_visibility — API Contracts

This document specifies the function signatures, data schemas, and I/O
contracts every module exposes.  Builders implement against these signatures;
the architect rejects any implementation that narrows or renames them without
a schema change recorded here.

---

## config.py — Constants and Schema

```python
# Paths
DATASET_ROOT: Path                    # Path("/home/adhish/Productivity/AMSCUP/repos/K-Radar")
KRADAR_ROOT: str                      # str(DATASET_ROOT)

# Sensor specs
RADAR_FOV_AZIMUTH_DEG: float          # 107.0
RADAR_FOV_ELEVATION_DEG: float        # 37.0
RADAR_MAX_RANGE_M: float              # 118.0

# Camera image dimensions (per stereo half)
CAM_HALF_WIDTH: int                   # 1280
CAM_HALF_HEIGHT: int                  # 720

# Camera visibility score weights
CAM_W1: float                         # 0.7  (area weight)
CAM_W2: float                         # 0.3  (centrality weight)

# LiDAR channel constants
OS2_64_CHANNELS: int                  # 64
OS2_64_VFOV_DEG: float               # 33.2
OS2_64_HRES_DEG: float               # 0.35
OS1_128_CHANNELS: int                 # 128
OS1_128_VFOV_DEG: float              # 44.5
OS1_128_HRES_DEG: float              # 0.17

# Allowed weather labels
ALLOWED_WEATHER: set[str]             # {"clear", "overcast", "fog", "rain", "sleet", "snow"}

# Smoke test defaults
SMOKE_SEQUENCE_IDS: list[str]         # ["1", "2"]
SMOKE_FRAME_LIMIT: int                # 20

# Sensor suite definition
SENSOR_SUITE: dict[str, dict]         # {"R": {"type": "radar"}, "L1": {"type": "lidar", "channels": 64}, ...}

# Camera intrinsics placeholder (4×4 K matrices)
CAMERA_INTRINSICS: dict[str, dict[str, float]]  # keys: fx, fy, cx, cy

# Camera extrinsics placeholder (4×4 transforms)
CAMERA_EXTRINSICS: dict[str, dict]     # keys: R (3×3 list), t (list[3])

# Output schema — ordered column names
OUTPUT_SCHEMA: list[str]              # 44 columns, see §3.1 of spec

# Weather labels list
WEATHER_LABELS: list[str]             # ["clear", "overcast", "fog", "rain", "sleet", "snow"]
```

---

## parser.py — Data Parsing

### HeaderInfo

```python
class HeaderInfo(NamedTuple):
    tesseract_idx: str       # e.g. "00282"
    os2_64_idx: str          # e.g. "00250"
    cam_front_idx: str       # e.g. "00749"
    os1_128_idx: str         # e.g. "00250"
    cam_lrr_idx: str         # e.g. "00751" — shared by left, right, rear
    timestamp: float         # Unix epoch seconds
    raw: str                 # Original header line
```

### ObjectAnnotation

```python
class ObjectAnnotation(NamedTuple):
    sensor_identify: str     # "R", "L1", "L2", "L", "RL1", etc.
    tracking_id: int         # >=1 tracked, -1 new
    obj_class: str           # "Sedan", "Bus or Truck", etc.
    x: float                 # meters, forward
    y: float                 # meters, left
    z: float                 # meters, up
    theta: float             # radians heading
    length_half: float       # meters (half-extent)
    width_half: float        # meters
    height_half: float       # meters

    @property length -> float        # length_half * 2.0
    @property width -> float         # width_half * 2.0
    @property height -> float        # height_half * 2.0
    @property distance_ego -> float  # sqrt(x²+y²+z²)
```

### Functions

```python
def parse_header(line: str) -> HeaderInfo:
    """Parse the '* idx(...)=..., timestamp=...' header line."""

def parse_object_line(line: str) -> Optional[ObjectAnnotation]:
    """Parse one '*, sensor, id, class, x, y, z, theta, lh, wh, hh' line.
    Returns None if the line has fewer than 11 fields."""

def parse_label_file(filepath: Path) -> tuple[HeaderInfo, List[ObjectAnnotation]]:
    """Parse a full info_label_rev2/*.txt file.  Raises ValueError if no header found."""

def get_sequence_label_files(
    sequence_id: str,
    dataset_root: Optional[Path] = None
) -> List[Path]:
    """Return sorted glob of data/{sequence_id}/info_label_rev2/*.txt."""

def parse_description_txt(
    sequence_id: str,
    dataset_root: Optional[Path] = None
) -> dict:
    """Parse description.txt.  Returns dict with keys: location, time, weather."""
```

---

## calibration.py — Camera Calibration

### Calibration Data Structure

```python
# Type alias for clarity
CalibEntry = dict[str, np.ndarray]   # keys: "camera_intrinsics" (4×4), "radar2camera" (4×4), "camera2radar" (4×4)
CalibrationStore = dict[str, CalibEntry]  # keys: "front0", "front1", "right0", "right1", "rear0", "rear1", "left0", "left1"
```

### Functions

```python
def load_camera_calibration(seq: int = 1) -> CalibrationStore:
    """Load T_params_seq/{seq} pickle.  Returns dict of cam_key → params.
    Raises FileNotFoundError / pickle errors on missing file."""

def get_camera_params(direction: str, seq: int = 1) -> list[dict]:
    """direction ∈ {'front', 'right', 'rear', 'left'}.
    Returns list of 2 dicts (stereo pair), each with keys:
      - 'cam_number': int
      - 'cam_key': str
      - 'camera_intrinsics': np.ndarray (4×4)
      - 'radar2camera': np.ndarray (4×4)
      - 'camera2radar': np.ndarray (4×4)
    Raises ValueError for unknown direction."""

def get_T_radar2cam(cam_number: int, seq: int = 1) -> np.ndarray:
    """Get 4×4 radar-to-camera transform for a specific camera number (1-8).
    Raises ValueError if cam_number not found."""

def get_camera_intrinsics(cam_number: int, seq: int = 1) -> np.ndarray:
    """Get 4×4 camera intrinsics matrix for a specific camera number.
    Raises ValueError if cam_number not found."""

def load_calibration(data_path) -> dict:
    """Placeholder — returns empty dict.  Reserved for future external calib loading."""
```

---

## data_loader.py — Sensor Data Loading

### Functions

```python
def load_radar_cube(
    sequence_id: str,
    frame_idx: str,
    dataset_root: Optional[Path] = None
) -> Optional[np.ndarray]:
    """Load radar_zyx_cube/cube_{frame_idx}.mat.  Shape (Z, Y, X).
    Returns None if file missing.  Uses scipy.io.loadmat."""

def read_pcd_file(filepath: Path) -> np.ndarray:
    """Read PCD file.  Returns (N, 3) float32.  Supports ascii and binary.
    Returns empty (0, 3) array on failure."""

def load_lidar_points(
    sequence_id: str,
    frame_idx: str,
    sensor: str = "os2-64",
    dataset_root: Optional[Path] = None
) -> Optional[np.ndarray]:
    """Load {sensor}/{sensor}_{frame_idx}.pcd.  Returns (N, 3) float32.
    sensor ∈ {'os2-64', 'os1-128'}.  Returns None if file missing."""

def load_camera_image(
    sequence_id: str,
    frame_idx: str,
    camera: str,
    dataset_root: Optional[Path] = None
) -> Optional[np.ndarray]:
    """Load camera image.  camera ∈ {'cam-front', 'cam-left', 'cam-right', 'cam-rear'}.
    Returns (720, 2560, 3) BGR stereo-stitched image via cv2.imread.
    Returns None if file missing or unreadable."""

def get_camera_image_path(
    sequence_id: str,
    frame_idx: str,
    camera: str,
    dataset_root: Optional[Path] = None
) -> Optional[Path]:
    """Return path to camera image without loading.  Returns None if missing."""
```

---

## radar_visibility.py — Radar Metric

### Constant

```python
DB_HEADROOM: float = 20.0   # dB above noise floor → score 1.0
```

### Functions

```python
def compute_radar_sparsity_score(
    radar_zyx_cube: np.ndarray,
    bbox: dict
) -> float:
    """SNR-weighted power density, normalised to [0, 1].

    Args:
        radar_zyx_cube: (Z, Y, X) float64, raw linear power.  Sentinels ≤ 0.
        bbox: dict with keys z_min, z_max, y_min, y_max, x_min, x_max
              (integer voxel indices, exclusive upper bound).

    Returns:
        float in [0, 1].  0.0 when no valid signal or empty subset.
    """

def radar_visibility(
    radar_zyx_cube: np.ndarray,
    object_bboxes: list[dict]
) -> list[float]:
    """Compute scores for multiple bboxes.  Returns list of floats."""
```

---

## lidar_visibility.py — LiDAR Metric

### Functions

```python
def calculate_lidar_visibility(
    points: np.ndarray,
    bboxes: list[list[float]],
    fov: list[float],
    range_limit: list[float],
    expected_density: float
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute point-in-box count and sparsity score for one sensor cloud.

    Args:
        points: (N, 3) float32 LiDAR points in radar/sensor frame.
        bboxes: list of [xmin, xmax, ymin, ymax, zmin, zmax] (axis-aligned, meters).
        fov: [x_min, x_max, y_min, y_max] sensor FOV limits (meters).
        range_limit: [min_range, max_range] sensor range limits (meters).
        expected_density: theoretical point count for a 1-m³ bbox at this sensor's
                         angular resolution.

    Returns:
        Tuple of three 1-D numpy arrays, one entry per bbox:
          visible: bool[n]       — center in FOV AND in range AND count > 0
          points_count: int[n]   — raw point count inside bbox
          sparsity_score: float[n] — count / expected_density (unclipped)
    """

def read_pcd_file(filepath: Path) -> np.ndarray:
    """Read PCD file.  Returns (N, 3) float32.  Duplicate of data_loader's version."""
```

---

## camera_visibility.py — Camera Metric

### Constants

```python
HALF_WIDTH: int = 1280
HALF_HEIGHT: int = 720
W1: float = 0.7   # area weight
W2: float = 0.3   # centrality weight
```

### Functions

```python
def project_point_to_image(
    point_3d: np.ndarray,
    camera_intrinsics: np.ndarray,
    T_radar2cam: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Project 3D radar-frame point(s) to 2D image pixel coordinates.

    Args:
        point_3d: (3,) or (N, 3) array in radar coordinates.
        camera_intrinsics: 4×4 camera intrinsic matrix (K in top-left 3×3).
        T_radar2cam: 4×4 extrinsic transform from radar frame to camera frame.

    Returns:
        u: (N,) — raw pixel x (may be outside image bounds).
        v: (N,) — raw pixel y (may be outside image bounds).
        z_cam: (N,) — depth in camera frame; positive = in front of camera.

    Note: No clipping is applied.  Callers must use z_cam > 0 and
    clipped-area logic for visibility decisions.
    """

def calculate_visibility_score(
    obj_corners: np.ndarray,
    cam_params: dict
) -> float:
    """Camera visibility score for one object and one camera.

    Args:
        obj_corners: (8, 3) array of 3D corners in radar frame.
        cam_params: dict with 'camera_intrinsics' (4×4) and 'radar2camera' (4×4).

    Returns:
        float in [0, 1].  0.0 means not visible (behind camera or outside FOV).
        Score = W1 * (clipped_area / image_area) + W2 * centrality.
    """

def calculate_camera_visibility(
    obj_corners: np.ndarray,
    seq: int = 1
) -> dict[str, float]:
    """Calculate visibility scores for all four camera directions.

    Args:
        obj_corners: (8, 3) array of 3D corners in radar frame.
        seq: sequence ID for calibration lookup.

    Returns:
        Dict with keys 'front', 'left', 'right', 'rear'.
        Each value is max(score_subcam0, score_subcam1).
        Score > 0 means visible.
    """
```

---

## pipeline.py — Orchestration

### Internal Helpers

```python
def _world_to_voxel(x: float, y: float, z: float) -> tuple[int, int, int]:
    """Convert world (meter) coords to radar zyx_cube integer voxel indices.
    Returns (vz, vy, vx), clamped to grid bounds."""

def _radar_fov_check(x: float, y: float, z: float) -> bool:
    """True if object center is within radar's 107° azimuth / 37° elevation cone."""

def _radar_range_check(x: float, y: float, z: float) -> bool:
    """True if object center is within 0–118 m of radar origin."""

def _obj_corners(obj: ObjectAnnotation) -> np.ndarray:
    """Return (8, 3) world-frame corners of a rotated 3D bbox."""

def _bbox_voxels_from_annotation(obj: ObjectAnnotation) -> dict:
    """AABB of rotated bbox in voxel space.
    Returns dict{z_min, z_max, y_min, y_max, x_min, x_max}."""

def _bbox_list_from_annotation(obj: ObjectAnnotation) -> list:
    """Axis-aligned bbox as [xmin, xmax, ymin, ymax, zmin, zmax] in meters."""

def _assert_radar_cube_shape(cube: np.ndarray) -> None:
    """Runtime guard — logs warning if cube shape doesn't match grid constants."""
```

### Grid Constants (pipeline.py)

```python
RADAR_Z_MIN, RADAR_Z_MAX = -30.0, 30.0
RADAR_Y_MIN, RADAR_Y_MAX = -80.0, 80.0
RADAR_X_MIN, RADAR_X_MAX = 0.0, 100.0
RADAR_GRID_Z, RADAR_GRID_Y, RADAR_GRID_X = 150, 400, 250

# LiDAR expected-density constants
_EXPECTED_OS2 = (OS2_64_CHANNELS * OS2_64_VFOV_DEG / 360.0) * (360.0 / OS2_64_HRES_DEG)
_EXPECTED_OS1 = (OS1_128_CHANNELS * OS1_128_VFOV_DEG / 360.0) * (360.0 / OS1_128_HRES_DEG)

# LiDAR FOV/range (center-point check)
_LIDAR_FOV = [-200.0, 200.0, -200.0, 200.0]
_LIDAR_RANGE = [0.0, 120.0]
```

### Public API

```python
def compute_visibility_for_frame(
    sequence_id: str,
    header: HeaderInfo,
    objects: List[ObjectAnnotation],
    dataset_root: Path,
    calib_available: bool = True
) -> List[dict]:
    """Compute all visibility metrics for every object in one frame.

    Returns:
        List of row dicts (one per object).  Dict keys match OUTPUT_SCHEMA.
    """

def run(
    sequence_ids: List[str],
    frame_limit: Optional[int] = None,
    dataset_root: Optional[Path] = None,
    output_path: Optional[Path] = None
) -> pl.DataFrame:
    """Run the full visibility pipeline.

    Args:
        sequence_ids: sequence folder names (e.g. ["1", "2"]).
        frame_limit: max annotated frames per sequence (skips empty frames).
                     None means all frames.
        dataset_root: K-Radar dataset root.  Defaults to config.DATASET_ROOT.
        output_path: if provided, write Parquet here.

    Returns:
        Polars DataFrame with one row per (frame, object).
        Returns empty DataFrame if no rows produced.
    """
```

---

## scripts/run_pipeline.py — CLI Entry Point

```python
def parse_args() -> argparse.Namespace:
    """CLI arguments:
    --sequences (default: ["1", "2"])
    --frame-limit (default: 20)
    --no-frame-limit (flag)
    --output (default: outputs/visibility_output.parquet)
    --dataset-root (default: from config)
    --no-report (flag)
    --report-output (default: outputs/verification_report.md)
    """

def print_summary(df: pl.DataFrame, elapsed: float) -> None:
    """Print compact terminal summary of pipeline output."""

def generate_verification_report(parquet_path: Path, report_path: Path) -> None:
    """Run pytest with --json-report, parse results, emit verification_report.md."""

def main() -> None:
    """Parse args, run pipeline, print summary, generate report."""
```

---

## Cross-Module Data Flow Summary

```
parser.parse_label_file()
    → HeaderInfo, List[ObjectAnnotation]
        │
        ▼
data_loader.load_radar_cube(seq, header.tesseract_idx)
    → np.ndarray | None
        │
        ▼  [if not None]
radar_visibility.compute_radar_sparsity_score(cube, bbox_voxels)
    → float

data_loader.load_lidar_points(seq, header.os2_64_idx, "os2-64")
data_loader.load_lidar_points(seq, header.os1_128_idx, "os1-128")
    → np.ndarray | None
        │
        ▼  [if not None]
lidar_visibility.calculate_lidar_visibility(points, bboxes, fov, range, expected)
    → (visible, count, score)

calibration.get_camera_params(direction, seq)
    → list[dict]  (stereo pair)
        │
        ▼
camera_visibility.calculate_camera_visibility(obj_corners, seq)
    → dict{dir → float}
        │
        ▼  [if visible]
camera_visibility.project_point_to_image(center, K, T)
    → (u, v, z_cam)
```

All three metric functions are independent of each other — they share only
the parsed annotation data (bbox corners, center coordinates).  This allows
parallel implementation of the three metric modules with no shared state.

---

## viewer/server.py — FastAPI Web Viewer API

### Pydantic Models

```python
from pydantic import BaseModel
from typing import Optional

class SensorVisibility(BaseModel):
    visible: bool
    score: float
    points_count: Optional[int] = None   # lidar only
    proj_x: Optional[float] = None       # camera only
    proj_y: Optional[float] = None       # camera only

class ObjectVisibility(BaseModel):
    radar: SensorVisibility
    lidar64: SensorVisibility
    lidar128: SensorVisibility
    cam_front: SensorVisibility
    cam_left: SensorVisibility
    cam_right: SensorVisibility
    cam_rear: SensorVisibility
    num_sensors_visible: int
    primary_sensor: Optional[str]

class ObjectData(BaseModel):
    tracking_id: int
    obj_class: str
    x: float; y: float; z: float
    length: float; width: float; height: float
    theta: float
    corners_3d: list[list[float]]           # 8 corners, radar frame (X,Y,Z)
    corners_2d_cam: dict[str, Optional[list[list[float]]]]  # null if invisible
    visibility: ObjectVisibility

class FrameResponse(BaseModel):
    sequence_id: str
    frame_idx: int
    timestamp: float
    objects: list[ObjectData]
```

### Endpoints

```python
# GET /api/sequences
# Returns: list of {id: str, path: str} for sequences that have data/ folders
def list_sequences() -> list[dict[str, str]]:
    """Scan DATASET_ROOT/data/ for sequence directories."""

# GET /api/frames/{seq_id}
# Returns: [{frame_idx: int, label_file: str}] for the given sequence
def list_frames(seq_id: str) -> list[dict]:
    """Globs data/{seq_id}/info_label_rev2/*.txt, returns frame metadata."""

# GET /api/frame/{seq_id}/{frame_idx}
# Returns: FrameResponse
# Calls pipeline.compute_visibility_for_frame() and augments with box corners.
def get_frame(seq_id: str, frame_idx: int) -> FrameResponse:
    """Parse label file, load all sensor data, compute visibility, return FrameResponse."""

# GET /api/image/{seq_id}/{cam}/{frame_idx}
# cam ∈ {'cam-front', 'cam-left', 'cam-right', 'cam-rear'}
# Returns: JPEG binary (image/jpeg)
def get_camera_image(seq_id: str, cam: str, frame_idx: int) -> bytes:
    """Serves data/{seq_id}/{cam}/{cam}_{frame_idx:05d}.jpg via data_loader."""

# GET /api/lidar/{seq_id}/{sensor}/{frame_idx}
# sensor ∈ {'os2-64', 'os1-128'}
# Returns: {"points": [[x, y, z], ...]}
def get_lidar_points(seq_id: str, sensor: str, frame_idx: int) -> dict:
    """Loads PCD via data_loader, returns JSON-serialisable point list."""

# GET /api/radar/{seq_id}/{frame_idx}
# Returns: PNG binary (image/png) — top-down heatmap of radar_zyx_cube
#   Collapses Z axis via mean; maps X→width, Y→height; colormap = viridis/grayscale.
def get_radar_heatmap(seq_id: str, frame_idx: int) -> bytes:
    """Loads .mat via data_loader, encodes as PNG using numpy + PIL."""
```
