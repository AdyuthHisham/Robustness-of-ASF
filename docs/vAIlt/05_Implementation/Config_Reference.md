---
title: Config Reference
type: concept
source: home/adhish/Productivity/AMSCUP/docs/config_reference.md
date: 2026-07-02
tags: [05 Implementation]
---
## K-Radar Visibility Analysis Configuration

### Dataset Root

* KRADAR_ROOT: /home/adhish/Productivity/AMSCUP/repos/K-Radar

### Sensor Suite Configuration

* RADAR_FOV_AZIMUTH_DEG: 107.0
* RADAR_FOV_ELEVATION_DEG: 37.0
* RADAR_MAX_RANGE_M: 118.0
* OS2_64_CHANNELS: 64
* OS2_64_VFOV_DEG: 22.5 (corrected from 33.2 — see [[../06_Results/lidar128-legacy-remap-visibility-anomaly]])
* OS2_64_HRES_DEG: 0.18 (corrected from 0.35 — table 7's resolution row is azimuth res 0.18°, elevation res 0.35°, identical for both LiDARs; 0.35 had been mistaken for OS2-64's azimuth res)
* OS2_64_MAX_RANGE_M: 240.0 (new; previously LiDAR range was a single shared 120m cutoff)
* OS1_128_CHANNELS: 128
* OS1_128_VFOV_DEG: 45.0 (corrected from 44.5)
* OS1_128_HRES_DEG: 0.18 (corrected from 0.17)
* OS1_128_MAX_RANGE_M: 120.0 (new)

### Camera Configuration

* CAM_HALF_WIDTH: 1280
* CAM_HALF_HEIGHT: 720
* CAM_W1: 0.7
* CAM_W2: 0.3

### Output Schema

* OUTPUT_SCHEMA: ["sequence_id", "frame_idx", "obj_tracking_id", "obj_class", "obj_x", "obj_y", "obj_z", "obj_length", "obj_width", "obj_height", "obj_theta", "obj_distance_ego", "sensor_identify", "weather", "radar_visible", "radar_fov_in", "radar_range_in", "radar_sparsity_score", "lidar64_visible", "lidar64_points_count", "lidar64_sparsity_score", "lidar128_visible", "lidar128_points_count", "lidar128_sparsity_score", "cam_front_visible", "cam_front_proj_x", "cam_front_proj_y", "cam_front_visibility_score", "cam_left_visible", "cam_left_proj_x", "cam_left_proj_y", "cam_left_visibility_score", "cam_right_visible", "cam_right_proj_x", "cam_right_proj_y", "cam_right_visibility_score", "cam_rear_visible", "cam_rear_proj_x", "cam_rear_proj_y", "cam_rear_visibility_score", "num_sensors_visible", "primary_sensor"]

### Weather Labels

* WEATHER_LABELS: ["clear", "overcast", "fog", "rain", "sleet", "snow"]
