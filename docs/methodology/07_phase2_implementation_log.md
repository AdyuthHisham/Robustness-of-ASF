# Phase 2 Implementation Log: KRADAR Visibility Pipeline Upgrade

## Date: 2026-07-03
## Session: Hermes Agent (theasstnt profile)

### Summary of Changes
Completed Phase 2 of the KRADAR visibility upgrade roadmap by implementing:
1. Updated LiDAR visibility calls to use the new single-sensor `calculate_lidar_visibility()` signature (ISSUE-01)
2. Revised radar noise-floor map computation using CFAR-like approach
3. Added precomputation of sensor data (LiDAR range images, radar noise floors, camera depth maps) for efficiency
4. Added ghost flag detection (radar visible but no other sensors detect object)
5. Enhanced metadata collection with weather labeling
6. Maintained backward compatibility where possible

### Files Modified
- `/home/adhish/Productivity/AMSCUP/test-bed/src/Modules/robust_testing/kradar/src/kradar_visibility/pipeline.py`

### Detailed Changes

#### 1. LiDAR Visibility Updates (ISSUE-01)
**Location:** `compute_visibility_for_frame()` function, lines ~200-230
**Changes:**
- Replaced separate calls to `calculate_lidar_visibility()` for OS2-64 and OS1-128 with single calls that return tuples
- Modified to only use `[0][0], [1][0], [2][0]` elements from each result array as specified
- Added `range_image` and `sensor_origin` parameters for precomputed data support
- Maintained backward compatibility by making these parameters optional

**Before:**
```python
lidar64_visible, lidar64_points, lidar64_score = calculate_lidar_visibility(
    os2_points, bbox_list,
    fov=_LIDAR_FOV, range_limit=_LIDAR_RANGE,
    expected_density=_EXPECTED_OS2
)
```

**After:**
```python
vis, cnt, sco = calculate_lidar_visibility(
    os2_points, bbox_list,
    fov=_LIDAR_FOV, range_limit=_LIDAR_RANGE,
    expected_density=_EXPECTED_OS2,
    range_image=os2_range_image,
    sensor_origin=os2_sensor_origin,
)
lidar64_visible = bool(vis[0])
lidar64_points = int(cnt[0])
lidar64_score = float(sco[0])
```

#### 2. Radar Noise-Floor Map Computation
**Location:** `compute_radar_noise_floor_map()` function in pipeline.py
**Changes:**
- Replaced simple max-filter approach with CFAR-like noise floor estimation
- Implemented sliding window approach with guard cells and training cells
- Computed noise floor as the mean of surrounding cells excluding guard cells
- Added proper handling of edge cases and NaN values
- Maintains same interface: takes radar cube, returns 2D noise floor map

**Key Improvements:**
- More accurate noise estimation that adapts to local clutter statistics
- Better handling of non-uniform noise across range/Doppler dimensions
- Configurable window sizes via constants

#### 3. Precomputation Framework
**Location:** `compute_visibility_for_frame()` function, lines ~180-220
**New Features:**
- **LiDAR Range Images:** Computed once per frame using `prepare_frame_lidar()`
- **Radar Noise Floor:** Computed once per frame using `compute_radar_noise_floor_map()`
- **Camera Depth Maps:** Computed once per direction per frame using `generate_camera_depth_maps()`

**Performance Impact:**
- Reduced redundant computations from O(N_objects) to O(1) per sensor type per frame
- Especially beneficial for frames with many objects

#### 4. Ghost Flag Detection
**Location:** `compute_visibility_for_frame()` function, lines ~320-330
**Added:**
```python
ghost_flag = (
    radar_visible and
    not lidar64_visible and
    not lidar128_visible and
    not cam_front_visible and
    not cam_left_visible and
    not cam_right_visible and
    not cam_rear_visible
)
```
**Purpose:** Identifies radar-only detections that may be false positives or weather returns

#### 5. Metadata Enhancements
**Changes:**
- Added `weather_label` parameter to `compute_visibility_for_frame()` (defaults to "normal")
- Added `weather` field to output rows for downstream analysis
- Maintains backward compatibility with existing code

#### 6. API Consistency
**Changes:**
- Updated function signature to include optional `weather_label` parameter
- Updated docstring to document new parameters and return values
- Added methodology document references as inline comments

### Methodology Documentation References
Added inline comments referencing the updated methodology documents:
- ISSUE-01: LiDAR single-sensor interface update
- ISSUE-04: Radar cube shape validation
- ISSUE-07: Graceful degradation when calibration unavailable
- ISSUE-08: Empty result guarding

### Verification Results
**Smoke Tests:** ✅ PASSED (19/19)
- All basic functionality tests pass
- No regressions in data loading, projection, or metric computation

**Verification Tests:** ✅ PASSED (19/19, 13 skipped)
- Core data validation tests pass
- Skipped tests are due to missing weather-specific test data (expected)

**Performance:** Not formally benchmarked, but structural changes should reduce per-frame computation time significantly for dense scenes.

### Backward Compatibility
- All existing function signatures preserved where possible
- New parameters have sensible defaults
- No changes to output schema beyond added `ghost_flag` and `weather` fields
- Existing code using the pipeline should continue to work unchanged

### Next Steps (Phase 3)
Based on the roadmap, future work should focus on:
1. Implementing adaptive SNR thresholds for radar
2. Adding micro-Doppler signature analysis
3. Incorporating weather-specific propagation models
4. Expanding camera visibility with semantic segmentation cues