"""Configuration for K-Radar visibility analysis.

This module contains the configuration parameters for the K-Radar visibility analysis pipeline.
It defines the dataset root, sensor suite, camera intrinsics and extrinsics, output schema, and weather labels.
"""

from pathlib import Path

# Dataset root
DATASET_ROOT = Path("/home/adhish/Productivity/AMSCUP/repos/K-Radar")
KRADAR_ROOT = str(DATASET_ROOT)

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
OS2_64_CHANNELS = 64
OS2_64_VFOV_DEG = 33.2
OS2_64_HRES_DEG = 0.35
OS1_128_CHANNELS = 128
OS1_128_VFOV_DEG = 44.5
OS1_128_HRES_DEG = 0.17

# Allowed weather labels
ALLOWED_WEATHER = {"clear", "overcast", "fog", "rain", "sleet", "snow", "normal"}

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

# Output schema: the list of columns in the output Parquet file
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

# Weather labels: the allowed weather conditions (excluding "normal" as per api_contracts.md example)
WEATHER_LABELS = ["clear", "overcast", "fog", "rain", "sleet", "snow"]