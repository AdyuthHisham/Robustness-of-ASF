# API Contracts

Function signatures and I/O contracts for every `kradar_visibility` module. This is the literal interface spec — implementations are rejected if they narrow or rename a signature without a schema change recorded here. Companion to [[System_Architecture]] (the module-shape overview) and [[Output_Schema]] (the Parquet column reference).

## Core signatures by module

**`parser.py`** — pure I/O/regex, no sensor loading.
```python
parse_header(line: str) -> HeaderInfo
parse_object_line(line: str) -> Optional[ObjectAnnotation]   # None if <11 fields
parse_label_file(filepath: Path) -> tuple[HeaderInfo, List[ObjectAnnotation]]  # raises ValueError if no header
get_sequence_label_files(sequence_id: str, dataset_root=None) -> List[Path]
parse_description_txt(sequence_id: str, dataset_root=None) -> dict  # keys: location, time, weather
```

**`calibration.py`** — loads `T_params_seq/{seq}` pickles.
```python
load_camera_calibration(seq: int = 1) -> CalibrationStore   # raises on missing file
get_camera_params(direction: str, seq: int = 1) -> list[dict]   # 2 dicts (stereo pair); raises ValueError on unknown direction
get_T_radar2cam(cam_number: int, seq: int = 1) -> np.ndarray
get_camera_intrinsics(cam_number: int, seq: int = 1) -> np.ndarray
```

**`data_loader.py`** — every function returns `None` on missing file, never raises.
```python
load_radar_cube(sequence_id, frame_idx, dataset_root=None) -> Optional[np.ndarray]   # (Z,Y,X)
read_pcd_file(filepath: Path) -> np.ndarray    # (N,3) float32; empty array on failure
load_lidar_points(sequence_id, frame_idx, sensor="os2-64", dataset_root=None) -> Optional[np.ndarray]
load_camera_image(sequence_id, frame_idx, camera, dataset_root=None) -> Optional[np.ndarray]   # (720,2560,3) BGR
```

**`radar_visibility.py`**
```python
DB_HEADROOM: float = 20.0
compute_radar_sparsity_score(radar_zyx_cube: np.ndarray, bbox: dict) -> float   # bbox: z/y/x_min/max voxel indices
radar_visibility(radar_zyx_cube, object_bboxes: list[dict]) -> list[float]
```

**`lidar_visibility.py`**
```python
calculate_lidar_visibility(
    points: np.ndarray,              # (N,3)
    bboxes: list[list[float]],       # [xmin,xmax,ymin,ymax,zmin,zmax] per object
    fov: list[float], range_limit: list[float], expected_density: float
) -> tuple[np.ndarray, np.ndarray, np.ndarray]   # (visible: bool[n], points_count: int[n], sparsity_score: float[n], unclipped)
```

**`camera_visibility.py`**
```python
HALF_WIDTH, HALF_HEIGHT = 1280, 720
W1, W2 = 0.7, 0.3   # area, centrality

project_point_to_image(point_3d, camera_intrinsics, T_radar2cam) -> tuple[u, v, z_cam]   # raw, unclipped
calculate_visibility_score(obj_corners: (8,3), cam_params: dict) -> float                 # 0.0 if behind camera / no overlap
calculate_camera_visibility(obj_corners: (8,3), seq: int = 1) -> dict[str, float]         # keys: front/left/right/rear, max of stereo pair
```

**`pipeline.py`** — orchestration, public entry points.
```python
compute_visibility_for_frame(
    sequence_id, header: HeaderInfo, objects: List[ObjectAnnotation],
    dataset_root: Path, calib_available: bool = True
) -> List[dict]   # one dict per object, keys match config.OUTPUT_SCHEMA

run(
    sequence_ids: List[str], frame_limit: Optional[int] = None,
    dataset_root: Optional[Path] = None, output_path: Optional[Path] = None
) -> pl.DataFrame   # empty DataFrame if no rows produced; frame_limit skips zero-object frames
```

Internal voxel/geometry helpers (`_world_to_voxel`, `_radar_fov_check`, `_obj_corners`, `_bbox_voxels_from_annotation`, `_assert_radar_cube_shape`) are private to `pipeline.py` — not part of the external contract, listed in the canonical source for implementers only.

## Viewer API (`viewer/server.py`)

Pydantic response models: `SensorVisibility{visible, score, points_count?, proj_x?, proj_y?}` → `ObjectVisibility{radar, lidar64, lidar128, cam_front/left/right/rear, num_sensors_visible, primary_sensor}` → `ObjectData{tracking_id, obj_class, x/y/z, length/width/height, theta, corners_3d, corners_2d_cam, visibility}` → `FrameResponse{sequence_id, frame_idx, timestamp, objects[]}`.

| Endpoint | Returns |
|---|---|
| `GET /api/sequences` | `[{id, path}]` |
| `GET /api/frames/{seq_id}` | `[{frame_idx, label_file}]` |
| `GET /api/frame/{seq_id}/{frame_idx}` | `FrameResponse` |
| `GET /api/image/{seq_id}/{cam}/{frame_idx}` | JPEG binary |
| `GET /api/lidar/{seq_id}/{sensor}/{frame_idx}` | `{points: [[x,y,z],...]}` |
| `GET /api/radar/{seq_id}/{frame_idx}` | PNG binary (top-down heatmap) |

## Cross-module contract note

All three metric functions (`radar_visibility`, `lidar_visibility`, `camera_visibility`) are **independent of each other** — they share only the parsed annotation data (bbox corners, center coordinates). This is a deliberate design constraint: it allows the three metric modules to be implemented and tested in parallel with no shared state.

## Source

- `test-bed/src/Modules/robust_testing/kradar/api_contracts.md` (584 L, canonical — every field/type in full, `config.py` constant table, CLI arg spec)
