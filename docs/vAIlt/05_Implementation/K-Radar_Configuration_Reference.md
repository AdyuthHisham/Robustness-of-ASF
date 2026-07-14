---
title: K-Radar Configuration Reference
type: concept
source: home/adhish/Productivity/AMSCUP/docs/kradar_config_reference.md
date: 2026-07-02
tags: [05 Implementation]
---
# K-Radar Configuration Reference

> Source: `src/kradar_visibility/config.py`

This document describes all configuration parameters used by the K-Radar visibility analysis pipeline.

---

## Dataset Roots

| Constant | Value | Description |
|---|---|---|
| `DATASET_ROOT` | `Path("/home/adhish/Productivity/AMSCUP/repos/K-Radar")` | `pathlib.Path` object pointing to the K-Radar dataset checkout |
| `KRADAR_ROOT` | `str(DATASET_ROOT)` | Plain string alias for environments that require `str` |

**Override:** pass a different root at runtime by monkey-patching or subclassing before importing:

```python
import kradar_visibility.config as cfg
cfg.DATASET_ROOT = Path("/your/path")
cfg.KRADAR_ROOT = str(cfg.DATASET_ROOT)
```

---

## Radar Constants

| Constant | Value | Description |
|---|---|---|
| `RADAR_FOV_AZIMUTH_DEG` | `107.0` | Radar horizontal (azimuth) field of view in degrees |
| `RADAR_FOV_ELEVATION_DEG` | `37.0` | Radar vertical (elevation) field of view in degrees |
| `RADAR_MAX_RANGE_M` | `118.0` | Maximum radar detection range in metres |

---

## Camera Image Dimensions

| Constant | Value | Description |
|---|---|---|
| `CAM_HALF_WIDTH` | `1280` | Width in pixels of each stereo half (left or right) |
| `CAM_HALF_HEIGHT` | `720` | Height in pixels of each stereo half |

> Each stereo pair is therefore `2560 × 720` pixels total.

---

## Camera Visibility Score Weights

| Constant | Value | Description |
|---|---|---|
| `CAM_W1` | `0.7` | Area weight — fraction of image area covered by the object's projection |
| `CAM_W2` | `0.3` | Centrality weight — how centred the projection is |

---

## LiDAR Constants

### OS2-64 (L1 sensor)

| Constant | Value | Description |
|---|---|---|
| `OS2_64_CHANNELS` | `64` | Number of vertical channels |
| `OS2_64_VFOV_DEG` | `33.2` | Vertical field of view in degrees |
| `OS2_64_HRES_DEG` | `0.35` | Angular resolution (degrees per laser line) |

### OS1-128 (L2 sensor)

| Constant | Value | Description |
|---|---|---|
| `OS1_128_CHANNELS` | `128` | Number of vertical channels |
| `OS1_128_VFOV_DEG` | `44.5` | Vertical field of view in degrees |
| `OS1_128_HRES_DEG` | `0.17` | Angular resolution (degrees per laser line) |

---

## Sensor Suite (`SENSOR_SUITE`)

Defines the seven sensors used in the pipeline.

| Key | Type | Position | Notes |
|---|---|---|---|
| `R` | radar | — | Primary radar sensor |
| `L1` | lidar | — | Ouster OS2-64 |
| `L2` | lidar | — | Ouster OS1-128 |
| `CF` | camera | front | Front-facing stereo camera |
| `CL` | camera | left | Left-facing stereo camera |
| `CR` | camera | right | Right-facing stereo camera |
| `CRE` | camera | rear | Rear-facing stereo camera |

The `channels` field on `L1`/`L2` references the constants above.

---

## Camera Intrinsics (`CAMERA_INTRINSICS`)

> **Status: placeholder (zeros).** In a production system these would be loaded from calibration files.

| Camera | `fx` | `fy` | `cx` | `cy` |
|---|---|---|---|---|
| `CF` | 0 | 0 | 0 | 0 |
| `CL` | 0 | 0 | 0 | 0 |
| `CR` | 0 | 0 | 0 | 0 |
| `CRE` | 0 | 0 | 0 | 0 |

Intrinsics map a 3-D ray in camera space to a 2-D pixel `(u, v)`:

```
u = fx * (X/Z) + cx
v = fy * (Y/Z) + cy
```

---

## Camera Extrinsics (`CAMERA_EXTRINSICS`)

> **Status: placeholder (zero rotation, zero translation).** In a production system these would be loaded from calibration files.

Each entry contains:
- `R`: 3×3 rotation matrix (identity = no rotation)
- `t`: 3-element translation vector in metres (zeros = at origin)

| Camera | `R` | `t` |
|---|---|---|
| `CF` | `[[0,0,0],[0,0,0],[0,0,0]]` | `[0, 0, 0]` |
| `CL` | `[[0,0,0],[0,0,0],[0,0,0]]` | `[0, 0, 0]` |
| `CR` | `[[0,0,0],[0,0,0],[0,0,0]]` | `[0, 0, 0]` |
| `CRE` | `[[0,0,0],[0,0,0],[0,0,0]]` | `[0, 0, 0]` |

Extrinsics transform points from the camera frame to the ego vehicle frame.

---

## Weather Labels

| Constant | Value | Description |
|---|---|---|
| `ALLOWED_WEATHER` | `{"clear", "overcast", "fog", "rain", "sleet", "snow", "normal"}` | Complete set of permitted weather tags (Python `set`) |
| `WEATHER_LABELS` | `["clear", "overcast", "fog", "rain", "sleet", "snow"]` | Subset used in output (excludes `"normal"`); matches `api_contracts.md` |

---

## Smoke-Test Defaults

Used for fast CI / local smoke tests.

| Constant | Value | Description |
|---|---|---|
| `SMOKE_SEQUENCE_IDS` | `["1", "2"]` | Only process sequences `1` and `2` |
| `SMOKE_FRAME_LIMIT` | `20` | Cap at 20 frames per sequence |

---

## Output Schema (`OUTPUT_SCHEMA`)

The pipeline writes a Parquet file with the following 37 columns:

| # | Column | Description |
|---|---|---|
| 1 | `sequence_id` | K-Radar sequence identifier (string) |
| 2 | `frame_idx` | Frame index within the sequence (int) |
| 3 | `obj_tracking_id` | Per-object tracking ID assigned by the annotation pipeline (int) |
| 4 | `obj_class` | Object class, e.g. `"car"`, `"pedestrian"` (string) |
| 5 | `obj_x` | Object centre X coordinate in ego-vehicle frame (m) (float) |
| 6 | `obj_y` | Object centre Y coordinate in ego-vehicle frame (m) (float) |
| 7 | `obj_z` | Object centre Z coordinate in ego-vehicle frame (m) (float) |
| 8 | `obj_length` | Object bounding-box length along X (m) (float) |
| 9 | `obj_width` | Object bounding-box width along Y (m) (float) |
| 10 | `obj_height` | Object bounding-box height along Z (m) (float) |
| 11 | `obj_theta` | Object heading angle in ego-vehicle frame (rad) (float) |
| 12 | `obj_distance_ego` | Euclidean distance from object centre to ego vehicle origin (m) (float) |
| 13 | `sensor_identify` | Sensor for which visibility is being evaluated, e.g. `"R"`, `"L1"` (string) |
| 14 | `weather` | Weather condition label from `WEATHER_LABELS` (string) |
| 15 | `radar_visible` | Whether the object is visible to the radar (bool) |
| 16 | `radar_fov_in` | Whether the object is inside the radar azimuth FOV — `RADAR_FOV_AZIMUTH_DEG` (bool) |
| 17 | `radar_range_in` | Whether the object is inside `RADAR_MAX_RANGE_M` (bool) |
| 18 | `radar_sparsity_score` | Radar sparsity score: point density relative to a reference at 5 m (float) |
| 19 | `lidar64_visible` | Whether the OS2-64 sensor detected the object (bool) |
| 20 | `lidar64_points_count` | Raw number of OS2-64 returns from the object's bounding box (int) |
| 21 | `lidar64_sparsity_score` | OS2-64 sparsity score (float) |
| 22 | `lidar128_visible` | Whether the OS1-128 sensor detected the object (bool) |
| 23 | `lidar128_points_count` | Raw number of OS1-128 returns from the object's bounding box (int) |
| 24 | `lidar128_sparsity_score` | OS1-128 sparsity score (float) |
| 25 | `cam_front_visible` | Whether the object projects into the front camera's image and meets the visibility threshold (bool) |
| 26 | `cam_front_proj_x` | Front camera projection X coordinate of the object centre (px, float) |
| 27 | `cam_front_proj_y` | Front camera projection Y coordinate of the object centre (px, float) |
| 28 | `cam_front_visibility_score` | Front camera visibility score `= CAM_W1 * area_fraction + CAM_W2 * centrality` (float) |
| 29 | `cam_left_visible` | Same as above for the left camera (bool) |
| 30 | `cam_left_proj_x` | Left camera projection X (px, float) |
| 31 | `cam_left_proj_y` | Left camera projection Y (px, float) |
| 32 | `cam_left_visibility_score` | Left camera visibility score (float) |
| 33 | `cam_right_visible` | Same as above for the right camera (bool) |
| 34 | `cam_right_proj_x` | Right camera projection X (px, float) |
| 35 | `cam_right_proj_y` | Right camera projection Y (px, float) |
| 36 | `cam_right_visibility_score` | Right camera visibility score (float) |
| 37 | `cam_rear_visible` | Same as above for the rear camera (bool) |
| 38 | `cam_rear_proj_x` | Rear camera projection X (px, float) |
| 39 | `cam_rear_proj_y` | Rear camera projection Y (px, float) |
| 40 | `cam_rear_visibility_score` | Rear camera visibility score (float) |
| 41 | `num_sensors_visible` | Count of sensors for which the object is visible (int) |
| 42 | `primary_sensor` | Sensor with the highest combined visibility score; used as the default detection source (string) |

---

## Notes

- All lengths/distances are in **metres**, angles in **degrees** unless stated otherwise.
- Camera intrinsics and extrinsics are **placeholders** (zeroed); replace with calibration data for real evaluations.
- `WEATHER_LABELS` intentionally excludes `"normal"` to match the convention in `api_contracts.md`.