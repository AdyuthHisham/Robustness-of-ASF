"""Configuration for K-Radar visibility analysis."""
from pathlib import Path

# Dataset root
DATASET_ROOT = Path("/home/adhish/Productivity/AMSCUP/repos/K-Radar")

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

# Smoke test defaults
SMOKE_SEQUENCE_IDS = ["1", "2"]
SMOKE_FRAME_LIMIT = 20
