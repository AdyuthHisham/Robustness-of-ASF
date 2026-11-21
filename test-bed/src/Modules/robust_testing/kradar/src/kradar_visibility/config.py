"""Configuration for K-Radar visibility analysis.

This module contains the configuration parameters for the K-Radar visibility analysis pipeline.
It defines the dataset root, sensor suite, camera intrinsics and extrinsics, output schema, and weather labels.
"""

import os
from pathlib import Path

# Dataset root.
# Resolution order:
#   1. KRADAR_DATASET_ROOT env var (set this on clusters / other machines
#      where the K-Radar checkout doesn't live at the repo-relative default,
#      e.g. `export KRADAR_DATASET_ROOT=/opt/K-Radar` on Alvis).
#   2. repo-relative default: <repo_root>/repos/K-Radar, computed from this
#      file's location so it works on any machine that checked out the
#      AMSCUP repo (submodule included) without extra configuration.
_REPO_ROOT = Path(__file__).resolve().parents[7]  # .../kradar_visibility/src/kradar_visibility/config.py -> AMSCUP/
_DEFAULT_DATASET_ROOT = _REPO_ROOT / "repos" / "K-Radar"

DATASET_ROOT = Path(os.environ.get("KRADAR_DATASET_ROOT", str(_DEFAULT_DATASET_ROOT)))
KRADAR_ROOT = str(DATASET_ROOT)

# Camera calibration resources root.
# Resolution order mirrors DATASET_ROOT: KRADAR_CALIB_ROOT env var, else
# derived from DATASET_ROOT (this is where K-Radar's calib resources live
# by convention: <dataset_root>/resources/cam_calib).
CALIB_ROOT = Path(os.environ.get("KRADAR_CALIB_ROOT", str(DATASET_ROOT / "resources" / "cam_calib")))

# Sensor specs
RADAR_FOV_AZIMUTH_DEG = 107.0
RADAR_FOV_ELEVATION_DEG = 37.0
RADAR_MAX_RANGE_M = 118.0

# Camera image dimensions (per stereo half)
CAM_HALF_WIDTH = 1280
CAM_HALF_HEIGHT = 720

# Camera weights for visibility score
CAM_W1 = 0.7  # area weight
CAM_W2 = 0.3  # centrality weight

# LiDAR expected density constants
# Source: K-Radar dataset paper (docs/lit_survey/noise_addition/kradar.pdf),
# p.12, Appendix B, Table 7 "Sensor suite details".
OS2_64_CHANNELS = 64
OS2_64_VFOV_DEG = 22.5   # paper: 22.5 (was 33.2 — did not match table 7)
OS2_64_HRES_DEG = 0.18   # paper: azimuth res 0.18 for both sensors (was 0.35)
OS1_128_CHANNELS = 128
OS1_128_VFOV_DEG = 45.0  # paper: 45 (was 44.5)
OS1_128_HRES_DEG = 0.18  # paper: azimuth res 0.18 for both sensors (was 0.17)

# LiDAR per-sensor max range (Table 7). Previously pipeline.py used a single
# shared 120m cutoff for both sensors — os2-64's real range is 240m.
OS2_64_MAX_RANGE_M = 240.0
OS1_128_MAX_RANGE_M = 120.0

# Allowed weather labels
# "lightsnow"/"heavysnow" added 2026-09-23: the original set omitted these two
# raw K-Radar weather tokens (confirmed verbatim in K-Radar's own
# tools/tag_generator/tag_generation.py and scripts/main_fusion_eval_0.py),
# so sequences 42/43/48/49 (lightsnow) and 46/47/54/55/56/57/58 (heavysnow)
# were silently falling back to "normal" -- see ingest.py's mirrored constant.
ALLOWED_WEATHER = {
    "clear", "overcast", "fog", "rain", "sleet", "snow", "normal",
    "lightsnow", "heavysnow",
}

# Camera occlusion parameters (NEW: Phase 4 - k-radar-sensor-visibility-metrics.md §4.3)
DEPTH_MARGIN = 0.1       # meters, for camera depth-buffer comparison
DEPTH_SAMPLE_RADIUS = 3  # pixels, neighborhood radius for depth map sampling

# Smoke test defaults
SMOKE_SEQUENCE_IDS = ["1", "2"]
SMOKE_FRAME_LIMIT = 20

# --- Variables for the web visualization tool API ---

# Sensor suite: defines the types and properties of each sensor
SENSOR_SUITE = {
    "R": {"type": "radar"},
    "L1": {"type": "lidar", "channels": OS2_64_CHANNELS},
    "L2": {"type": "lidar", "channels": OS1_128_CHANNELS},
    "CF": {"type": "camera", "position": "front"},
    "CL": {"type": "camera", "position": "left"},
    "CR": {"type": "camera", "position": "right"},
    "CRE": {"type": "camera", "position": "rear"},
}

# Camera intrinsics (focal length, principal point) for each camera
# In a real system, these would be loaded from calibration files.
# Here we use placeholder values (zeros) as per the api_contracts.md example.
CAMERA_INTRINSICS = {
    "CF": {"fx": 0, "fy": 0, "cx": 0, "cy": 0},
    "CL": {"fx": 0, "fy": 0, "cx": 0, "cy": 0},
    "CR": {"fx": 0, "fy": 0, "cx": 0, "cy": 0},
    "CRE": {"fx": 0, "fy": 0, "cx": 0, "cy": 0},
}

# Camera extrinsics (rotation matrix and translation vector) for each camera
# In a real system, these would be loaded from calibration files.
# Here we use placeholder values (zero rotation, zero translation) as per the api_contracts.md example.
CAMERA_EXTRINSICS = {
    "CF": {"R": [[0, 0, 0], [0, 0, 0], [0, 0, 0]], "t": [0, 0, 0]},
    "CL": {"R": [[0, 0, 0], [0, 0, 0], [0, 0, 0]], "t": [0, 0, 0]},
    "CR": {"R": [[0, 0, 0], [0, 0, 0], [0, 0, 0]], "t": [0, 0, 0]},
    "CRE": {"R": [[0, 0, 0], [0, 0, 0], [0, 0, 0]], "t": [0, 0, 0]},
}

# Output schema: the list of columns in the output Parquet file.
# NOTE: order here must match the row-dict build order in
# pipeline.py's compute_visibility_for_frame() (rows.append({...})) exactly —
# this list previously drifted out of sync (obj_theta position; weather/
# environment/time_of_day/frame_object_count listed near the top but actually
# appended at the very end of the row dict). Harmless in practice since
# polars.DataFrame(list[dict]) keys columns by name, not list position, but
# keep these in sync so this list stays trustworthy as documentation.
OUTPUT_SCHEMA = [
    "sequence_id",
    "frame_idx",
    "timestamp",
    "obj_tracking_id",
    "obj_class",
    "obj_x",
    "obj_y",
    "obj_z",
    "obj_theta",
    "obj_length",
    "obj_width",
    "obj_height",
    "obj_distance_ego",
    "sensor_identify",
    "radar_visible",
    "radar_fov_in",
    "radar_range_in",
    "radar_sparsity_score",
    "lidar64_visible",
    "lidar64_visible_confirmed",
    "lidar64_points_count",
    "lidar64_sparsity_score",
    "lidar128_visible",
    "lidar128_visible_confirmed",
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
    "weather",
    "environment",
    "time_of_day",
    "frame_object_count",
    "ghost_flag",
    "occluded",
]

# Weather labels: the allowed weather conditions (excluding "normal" as per api_contracts.md example)
WEATHER_LABELS = ["clear", "overcast", "fog", "rain", "sleet", "snow", "lightsnow", "heavysnow"]