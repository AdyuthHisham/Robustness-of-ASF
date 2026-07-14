# K‑Radar `config.py` Reference

> **Location:** `kradar_visibility/config.py`

This module centralises all tunable parameters for the K‑Radar visibility analysis pipeline. It defines dataset locations, sensor specifications, weather label sets, smoke‑test defaults, the sensor suite mapping, placeholder camera intrinsics and extrinsics, and the ordered output schema for the generated Parquet files. All other modules import these constants to ensure a single source of truth.

---

## Table of Configuration Variables

| Constant | Type | Default Value | Description |
|---|---|---|---|
| `DATASET_ROOT` | `Path` | `Path("/home/adhish/Productivity/AMSCUP/repos/K-Radar")` | Root directory of the K‑Radar dataset checkout. |
| `KRADAR_ROOT` | `str` | `str(DATASET_ROOT)` | Plain‑string alias of `DATASET_ROOT` for APIs that expect a string. |
| `RADAR_FOV_AZIMUTH_DEG` | `float` | `107.0` | Radar horizontal (azimuth) field‑of‑view in degrees. |
| `RADAR_FOV_ELEVATION_DEG` | `float` | `37.0` | Radar vertical (elevation) field‑of‑view in degrees. |
| `RADAR_MAX_RANGE_M` | `float` | `118.0` | Maximum radar detection range in metres. |
| `CAM_HALF_WIDTH` | `int` | `1280` | Width in pixels of each stereo half (left or right). |
| `CAM_HALF_HEIGHT` | `int` | `720` | Height in pixels of each stereo half. |
| `CAM_W1` | `float` | `0.7` | Area weight for the camera visibility score. |
| `CAM_W2` | `float` | `0.3` | Centrality weight for the camera visibility score. |
| `OS2_64_CHANNELS` | `int` | `64` | Number of vertical channels for the OS2‑64 LiDAR sensor (L1). |
| `OS2_64_VFOV_DEG` | `float` | `33.2` | Vertical field‑of‑view for OS2‑64 LiDAR (degrees). |
| `OS2_64_HRES_DEG` | `float` | `0.35` | Angular resolution for OS2‑64 LiDAR (degrees per laser line). |
| `OS1_128_CHANNELS` | `int` | `128` | Number of vertical channels for the OS1‑128 LiDAR sensor (L2). |
| `OS1_128_VFOV_DEG` | `float` | `44.5` | Vertical field‑of‑view for OS1‑128 LiDAR (degrees). |
| `OS1_128_HRES_DEG` | `float` | `0.17` | Angular resolution for OS1‑128 LiDAR (degrees per laser line). |
| `ALLOWED_WEATHER` | `set[str]` | `{"clear", "overcast", "fog", "rain", "sleet", "snow"}` | Canonical set of weather labels accepted by the pipeline. |
| `SMOKE_SEQUENCE_IDS` | `list[str]` | `["1", "2"]` | Sequence IDs used for quick CI / local smoke tests. |
| `SMOKE_FRAME_LIMIT` | `int` | `20` | Maximum number of frames processed per sequence during smoke tests. |
| `SENSOR_SUITE` | `dict[str, dict]` | See below | Mapping of sensor identifiers to their type and, where applicable, channel count. |
| `CAMERA_INTRINSICS` | `dict[str, dict]` | Placeholder zeros | Intrinsic parameters (`fx`, `fy`, `cx`, `cy`) for each camera; real values are loaded from calibration files at runtime. |
| `CAMERA_EXTRINSICS` | `dict[str, dict]` | Placeholder zeros | Extrinsic transform (`R` matrix, `t` vector) from each camera to the ego vehicle frame; real values are loaded from calibration files. |
| `OUTPUT_SCHEMA` | `list[str]` | See below | Ordered list of column names for the Parquet output file produced by the pipeline. |
| `WEATHER_LABELS` | `list[str]` | `["clear", "overcast", "fog", "rain", "sleet", "snow"]` | Subset of `ALLOWED_WEATHER` used in the final output (excludes the alias `"normal"`). |

### `SENSOR_SUITE` Details

```python
SENSOR_SUITE = {
    "R": {"type": "radar"},
    "L1": {"type": "lidar", "channels": OS2_64_CHANNELS},
    "L2": {"type": "lidar", "channels": OS1_128_CHANNELS},
    "CF": {"type": "camera", "position": "front"},
    "CL": {"type": "camera", "position": "left"},
    "CR": {"type": "camera", "position": "right"},
    "CRE": {"type": "camera", "position": "rear"},
}
```

### `OUTPUT_SCHEMA` (excerpt)

The pipeline writes a Parquet table with the following ordered columns (total 42 shown here; the full list matches the documentation in `kradar_config_reference.md`):

```python
OUTPUT_SCHEMA = [
    "sequence_id",
    "frame_idx",
    "obj_tracking_id",
    "obj_class",
    "obj_x",
    "obj_y",
    "obj_z",
    "obj_length",
    "obj_width",
    "obj_height",
    "obj_theta",
    "obj_distance_ego",
    "sensor_identify",
    "weather",
    "radar_visible",
    "radar_fov_in",
    "radar_range_in",
    "radar_sparsity_score",
    "lidar64_visible",
    "lidar64_points_count",
    "lidar64_sparsity_score",
    "lidar128_visible",
    "lidar128_points_count",
    "lidar128_sparsity_score",
    "cam_front_visible",
    "cam_front_proj_x",
    "cam_front_proj_y",
    "cam_front_visibility_score",
    "cam_left_visible",
    "cam_left_proj_x",
    "cam_left_proj_y",
    "cam_left_visibility_score",
    "cam_right_visible",
    "cam_right_proj_x",
    "cam_right_proj_y",
    "cam_right_visibility_score",
    "cam_rear_visible",
    "cam_rear_proj_x",
    "cam_rear_proj_y",
    "cam_rear_visibility_score",
    "num_sensors_visible",
    "primary_sensor",
]
```

---

## Usage Example

```python
import kradar_visibility.config as cfg

# Inspect dataset root
print("Dataset root:", cfg.DATASET_ROOT)

# Check radar specifications
print("Radar max range (m):", cfg.RADAR_MAX_RANGE_M)

# List available sensors
for sensor, spec in cfg.SENSOR_SUITE.items():
    print(f"{sensor}: {spec['type']}")
```

Running the snippet yields the configured values, confirming that the module can be imported without side‑effects.

---

## Notes

- All distances are in **metres**; angles are in **degrees** unless otherwise noted.
- Camera intrinsics and extrinsics are placeholders (zeroed). Replace them with calibration data for real evaluations.
- The `WEATHER_LABELS` list deliberately excludes the alias `"normal"` to match the convention used throughout the pipeline.

---

*Generated by the Hermes Architect as part of task **t_de76c7a7**.*