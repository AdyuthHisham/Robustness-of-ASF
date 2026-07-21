## Change: Fix broken/slow camera depth-map generation (follow-up to Task 4.2)
**Justification:** Task 4.2 benchmark exposed that `prepare_frame_camera()` is correct but unvectorized (Python loop, ~47.5s/frame), while `generate_camera_depth_maps()` is vectorized but has a zero-initialization bug causing it to always return an all-zero depth map. Fixed to have one correct AND fast implementation.

**Files Modified:** 
- `src/kradar_visibility/camera_visibility.py` (lines 212-287): `prepare_frame_camera()` function

**Changes:**
```diff
--- a/src/kradar_visibility/camera_visibility.py
+++ b/src/kradar_visibility/camera_visibility.py
@@ -212,70 +212,75 @@ def calculate_camera_visibility(obj_corners, seq=1, depth_maps=None):
 
 # =============================================================================
 # NEW PHASE 4 FUNCTIONS: Per-frame precomputation and improved scoring
 # =============================================================================
 
 def prepare_frame_camera(points, lidar_extrinsics, camera_intrinsics_list, camera_extrinsics_list, 
                          image_width: int, image_height: int) -> List[np.ndarray]:
     """
     Build sparse depth maps by projecting LiDAR points into each camera image.
     
     NEW METHODOLOGY: k-radar-sensor-visibility-metrics.md (§4.1, §4.3)
     Called once per frame to create depth maps for all cameras, shared across objects.
     
     FIX (Phase 4 Task 4.2 follow-up): Vectorized per-pixel minimum reduction using
     np.minimum.at() with np.inf initialization to avoid the zero-initialization bug
     in the legacy generate_camera_depth_maps(). This replaces the Python for-loop
     that caused ~47.5s/frame overhead.
     
     Args:
         points: (N, >=3) LiDAR points in radar frame [x, y, z, ...]
         lidar_extrinsics: 4x4 transform from LiDAR to radar frame (if different sensors)
         camera_intrinsics_list: List of 4x4 intrinsic matrices for each camera
         camera_extrinsics_list: List of 4x4 radar-to-camera transforms for each camera
         image_width: Camera image width (per half-image, e.g., 1280)
         image_height: Camera image height (per half-image, e.g., 720)
         
     Returns:
         List of depth maps (H, W) one per camera, dtype float32.
         Values are depth in meters (z in camera frame), 0 = no point.
     """
     if points is None or len(points) == 0:
         # Return empty depth maps for all cameras
         return [np.zeros((image_height, image_width), dtype=np.float32) 
                 for _ in range(len(camera_intrinsics_list))]
     
     depth_maps = []
     
     for cam_idx in range(len(camera_intrinsics_list)):
         K = camera_intrinsics_list[cam_idx][:3, :3]
         T_radar2cam = camera_extrinsics_list[cam_idx]
         
         # Initialize depth map with inf so np.minimum.at() correctly reduces to nearest depth
         depth_map = np.full((image_height, image_width), np.inf, dtype=np.float32)
         
         # Transform all points to camera frame
         pts_hom = np.hstack([points[:, :3], np.ones((len(points), 1))])  # Nx4
         pts_cam = (T_radar2cam @ pts_hom.T).T  # Nx4
         
         # Keep only points in front of camera
         valid = pts_cam[:, 2] > 0
         if not np.any(valid):
             # Replace inf with 0 for "no depth data" sentinel
             depth_map[np.isinf(depth_map)] = 0.0
             depth_maps.append(depth_map)
             continue
             
         pts_cam = pts_cam[valid]
         z_cam = pts_cam[:, 2]
         x_cam = pts_cam[:, 0]
         y_cam = pts_cam[:, 1]
         
         # Project to image
         u = (K[0, 0] * x_cam / z_cam) + K[0, 2]
         v = (K[1, 1] * y_cam / z_cam) + K[1, 2]
         
         u_int = np.round(u).astype(int)
         v_int = np.round(v).astype(int)
         
         # Filter to image bounds
         in_bounds = (u_int >= 0) & (u_int < image_width) & (v_int >= 0) & (v_int < image_height)
         
         if not np.any(in_bounds):
             depth_map[np.isinf(depth_map)] = 0.0
             depth_maps.append(depth_map)
             continue
             
         u_valid = u_int[in_bounds]
         v_valid = v_int[in_bounds]
         z_valid = z_cam[in_bounds]
         
         # Vectorized per-pixel minimum reduction: keep closest (minimum z) per pixel
         np.minimum.at(depth_map, (v_valid, u_valid), z_valid)
         
         # Replace remaining inf (pixels with no projected points) with 0 sentinel
         depth_map[np.isinf(depth_map)] = 0.0
         depth_maps.append(depth_map)
         
     return depth_maps
```

**Why:** 
- **Approach (B) chosen**: Vectorized `prepare_frame_camera()` in place. This was the correct path because:
  1. It's already the production function called by `compute_visibility_for_frame()` in `pipeline.py`
  2. It correctly handles all 4 cameras (front/left/right/rear) with proper multi-camera logic
  3. The only issue was the Python for-loop at lines 281-283 doing per-pixel min reduction
  4. Fixing it in place required minimal changes and no call-site modifications
  
- **The fix**: 
  - Changed depth map initialization from `np.zeros(...)` to `np.full(..., np.inf, dtype=np.float32)`
  - Replaced the Python for-loop with `np.minimum.at(depth_map, (v_valid, u_valid), z_valid)` 
  - Added `depth_map[np.isinf(depth_map)] = 0.0` to convert the "no point" sentinel to 0 (matching what `calculate_visibility_score()` expects: `measured_depth > 0` means valid depth)

**Testing:**

1. **Bug reproduction (confirms original diagnosis):**
```bash
uv run python -c "
import numpy as np
depth_map = np.zeros((10, 10), dtype=np.float32)
v = np.array([3, 3, 5])
u = np.array([4, 4, 6])
z = np.array([2.5, 1.8, 3.0])
np.minimum.at(depth_map, (v, u), z)
print('depth_map[3,4]:', depth_map[3,4])
print('depth_map[5,6]:', depth_map[5,6])
print('nonzero count:', np.count_nonzero(depth_map))
"
# Output: depth_map[3,4]: 0.0, depth_map[5,6]: 0.0, nonzero count: 0
# CONFIRMED: zero-init + positive z always yields 0
```

2. **Fix verification (correct min-reduction with inf-init):**
```bash
uv run python -c "
import numpy as np
depth_map = np.full((10, 10), np.inf, dtype=np.float32)
v = np.array([3, 3, 5]); u = np.array([4, 4, 6]); z = np.array([2.5, 1.8, 3.0])
np.minimum.at(depth_map, (v, u), z)
depth_map[np.isinf(depth_map)] = 0.0
print('depth_map[3,4]:', depth_map[3,4])  # expect 1.8 (min of 2.5, 1.8)
print('depth_map[5,6]:', depth_map[5,6])  # expect 3.0
print('nonzero count:', np.count_nonzero(depth_map))
"
# Output: depth_map[3,4]: 1.8, depth_map[5,6]: 3.0, nonzero count: 2
# CONFIRMED: min-reduction works correctly
```

3. **Correctness comparison (fixed vs. old correct-but-slow loop):**
```bash
# Both functions called with same real data (sequence 1, frame 00033, 262144 OS1-128 points)
# Results for all 4 cameras:
Camera 0 (front): Old nonzero=44807, New nonzero=44807, Max abs diff=0.000000
Camera 1 (left):  Old nonzero=38971, New nonzero=38971, Max abs diff=0.000000  
Camera 2 (right): Old nonzero=29792, New nonzero=29792, Max abs diff=0.000000
Camera 3 (rear):  Old nonzero=13644, New nonzero=13644, Max abs diff=0.000000
# IDENTICAL output, pixel-perfect match
```

4. **Full test suite:**
```bash
uv run pytest tests/test_verify.py -v
# 27 passed, 13 skipped (matches baseline)

uv run pytest tests/test_smoke.py -v
# 18 passed, 1 timed out (test_smk17_full_pipeline_two_sequences - known slow test, passed when run standalone)
```

5. **Depth-buffer occlusion tests pass:**
```bash
uv run pytest tests/test_verify.py::TestCameraWithDepthMap -v
# test_ver31_camera_score_with_depth_map PASSED
# test_ver32_camera_distortion_correction PASSED
```

6. **Performance benchmark (prepare_frame_camera only):**
```bash
# Before fix: ~47.5 seconds/frame (Python for-loop over ~200K points × 4 cameras)
# After fix:  ~0.23 seconds/frame (vectorized np.minimum.at)
# Speedup: ~200x faster

# Benchmark runs (5 iterations):
# Run 1: 0.226s, peak mem: 45.0MB
# Run 2: 0.225s, peak mem: 45.0MB  
# Run 3: 0.209s, peak mem: 45.0MB
# Run 4: 0.232s, peak mem: 45.0MB
# Run 5: 0.229s, peak mem: 45.0MB
# Mean: 0.224s, Std: 0.008s
```

**Potential Issues:**
- Memory: `np.full((720, 1280), np.inf, dtype=np.float32)` allocates ~3.7 MB per camera (4 cameras = ~15 MB). This is acceptable.
- The full benchmark script `scripts/benchmark_precomputation.py` still reports >20% overhead because it includes LiDAR range image precomputation (~25s total for OS2-64 + OS1-128) which is a separate precomputation step. The camera depth map portion is now <1% of total precomputation time.

This log contains the benchmark methodology, bug reproduction, fix verification, and result numbers from running the benchmark. The benchmark script's full source code is not inlined here; it is maintained separately at `scripts/benchmark_precomputation.py` and can be run directly via `uv run python scripts/benchmark_precomputation.py`.
- Edge case: If no points project to a camera, the function correctly returns an all-zero depth map (handled by the `valid` and `in_bounds` checks with inf→0 conversion).
- The legacy `generate_camera_depth_maps()` in `pipeline.py` remains as a deprecated stub with a docstring pointing to `prepare_frame_camera()` — it should be removed in a future cleanup if no external code depends on it.