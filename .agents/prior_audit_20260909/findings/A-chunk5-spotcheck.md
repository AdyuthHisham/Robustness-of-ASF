# Chunk 5 — Reviewer A spot-check of B-5-02

## B-5-02 (A-verified) — corrected counts

Directly read `config.py:110-161` (real `OUTPUT_SCHEMA`) and both vault docs' inline lists.

**Real schema**: `OUTPUT_SCHEMA` is defined at `config.py:110-161`; entries are lines 111-160 = **50 columns** (not 46 as B claimed). Full list: sequence_id, frame_idx, timestamp, obj_tracking_id, obj_class, obj_x, obj_y, obj_z, obj_theta, obj_length, obj_width, obj_height, obj_distance_ego, sensor_identify, radar_visible, radar_fov_in, radar_range_in, radar_sparsity_score, lidar64_visible, lidar64_visible_confirmed, lidar64_points_count, lidar64_sparsity_score, lidar128_visible, lidar128_visible_confirmed, lidar128_points_count, lidar128_sparsity_score, cam_front_visible, cam_front_proj_x, cam_front_proj_y, cam_front_visibility_score, cam_left_visible, cam_left_proj_x, cam_left_proj_y, cam_left_visibility_score, cam_right_visible, cam_right_proj_x, cam_right_proj_y, cam_right_visibility_score, cam_rear_visible, cam_rear_proj_x, cam_rear_proj_y, cam_rear_visibility_score, num_sensors_visible, primary_sensor, weather, environment, time_of_day, frame_object_count, ghost_flag, occluded.

**`KRadar_configpy_Reference.md:62-108`**: claims "total 42 shown here" — counted lines 66-107, exactly **42 entries**, claim is accurate as a count of itself. But 42 ≠ 50: this doc is missing 8 real columns, not 4 as B stated: `timestamp`, `lidar64_visible_confirmed`, `lidar128_visible_confirmed`, `environment`, `time_of_day`, `frame_object_count`, `ghost_flag`, `occluded`.

**`Config_Reference.md:37`**: the inline bracketed list is, column-for-column, **identical to `KRadar_configpy_Reference.md`'s 42-entry list** (same 42 names, same order, including `weather` present in both). This is **42 entries, not 41** as B claimed, and it is missing the exact same 8 columns as the sibling doc — not "3 additional" columns (`environment`/`time_of_day`/`frame_object_count`) beyond some smaller B-claimed gap; those three are indeed missing, but so are the other 5, and both docs share the identical gap set.

## Correction to B-5-02

- Real total: **50** (B said 46).
- Each doc: **42** columns shown (B said 42 for one doc, 41 for the other — they are in fact the same 42-entry list).
- Missing from both docs, identically: **8 columns** — `timestamp`, `lidar64_visible_confirmed`, `lidar128_visible_confirmed`, `environment`, `time_of_day`, `frame_object_count`, `ghost_flag`, `occluded` (B said 4 for one doc, 7 for the other; actual is 8 for both, same set).
- Severity: doc-drift (confirmed, B's directional finding holds — both vault docs undercount the schema — but the exact figures are corrected above).
