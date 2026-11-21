# Gap Analysis Report

## Critical Gaps (Must Fix)
1. **Gap:** Missing per-frame LiDAR range-image precomputation and usage in LiDAR visibility scoring.
   - Current Implementation: LiDAR visibility (`lidar_visibility.py`) does not use a precomputed range image; the pipeline calls `calculate_lidar_visibility` without range image or sensor origin parameters.
   - New Requirement: Per-frame range image (one per LiDAR sensor) built once per frame and shared across all objects for merged density_ratio × (1 - occluded_fraction) scoring.
   - Affected Files: `src/kradar_visibility/lidar_visibility.py`, `src/kradar_visibility/pipeline.py`
   - Complexity: Medium
   - Impact: High (LiDAR scores are not occlusion-aware and do not follow the recommended merged methodology)

2. **Gap:** Missing per-frame radar noise-floor map precomputation and usage.
   - Current Implementation: Radar visibility uses `compute_radar_sparsity_score` without a per-frame noise-floor map; appears to rely on a static or per-cell threshold.
   - New Requirement: CFAR-style per-frame noise-floor map over `radar_zyx_cube`, computed once per frame and shared across all objects.
   - Affected Files: `src/kradar_visibility/radar_visibility.py`, `src/kradar_visibility/pipeline.py`
   - Complexity: Medium
   - Impact: Medium (radar scores may be less robust to weather-induced noise floor variations)

3. **Gap:** Missing per-frame LiDAR→camera projection for depth-buffer occlusion discount in camera visibility.
   - Current Implementation: Camera visibility (`camera_visibility.py`) implements only 8-corner projection area/centrality score; no depth-buffer discount.
   - New Requirement: Enable LiDAR depth-buffer occlusion discount (4.3) by default; requires per-frame projection of LiDAR point cloud into each camera image to build sparse depth maps.
   - Affected Files: `src/kradar_visibility/camera_visibility.py`, `src/kradar_visibility/pipeline.py`
   - Complexity: Medium
   - Impact: High (camera scores lack explicit occlusion handling, a key requirement)

4. **Gap:** Missing fusion-level ghost flag output.
   - Current Implementation: Pipeline outputs per-sensor visibility flags but does not compute or store the cross-sensor ghost flag (`radar_visible=True ∧ lidar_visible=False ∧ camera_visible=False`).
   - New Requirement: Flag probable radar-ghost/multipath cases as a fusion-level sanity check (free, no extra compute).
   - Affected Files: `src/kradar_visibility/pipeline.py`
   - Complexity: Low
   - Impact: Medium (missed opportunity for automatic down-weighting of radar ghosts)

### Non-Critical Gaps (Should Improve)
1. **Gap:** Missing distortion-corrected corner projection for camera visibility.
   - Current Implementation: Camera projection uses pinhole model without applying distortion coefficients from calibration files.
   - New Requirement: Explicitly apply stereo cameras' distortion coefficients before corner projection to improve accuracy, especially near image edges.
   - Affected Files: `src/kradar_visibility/camera_visibility.py`
   - Complexity: Low
   - Impact: Medium (improves projection accuracy for wide-FOV stereo rigs)

2. **Gap:** Missing inter-object occlusion graph for LiDAR (QA/debugging by-product).
   - Current Implementation: LiDAR visibility does not compute which specific object is causing occlusion.
   - New Requirement: Once LiDAR flags `occluded_fraction>0`, determine the occluder by checking failing rays' angular footprint against other boxes at nearer range; useful as O(M²) by-product for QA/debugging.
   - Affected Files: `src/kradar_visibility/lidar_visibility.py`
   - Complexity: Low
   - Impact: Low (valuable for debugging but not required for core visibility scores)

### Enhancements Recommended
1. **Enhancement:** Implement optional Doppler-coherence gating for radar (1.3) as a flag-gated upgrade.
   - Current Implementation: `radar_visibility.py` provides `radar_score_with_doppler` function but it is not integrated into the pipeline; default radar score uses SNR-weighted power only.
   - New Requirement: Add Doppler-coherence gating as an optional refinement restricted to per-object cropped Doppler sub-volume (not full 4DRT) to improve precision against multipath ghosts.
   - Affected Files: `src/kradar_visibility/radar_visibility.py`, `src/kradar_visibility/pipeline.py`
   - Effort: Medium
   - Impact: Medium (reduces false positives from radar multipath ghosts)

2. **Enhancement:** Implement LiDAR voxel occupancy ratio (2.4) as an offline-audit tool.
   - Current Implementation: Not present; LiDAR uses expected-density normalization and ray-casting occlusion.
   - New Requirement: Retain voxel occupancy ratio for completeness/comparison but only as an offline-audit tool run on a sampled subset.
   - Affected Files: `src/kradar_visibility/lidar_visibility.py` (optional)
   - Effort: Low
   - Impact: Low (useful for periodic validation)

3. **Enhancement:** Implement camera instance-segmentation-mask overlap (4.4) as an offline-audit tool.
   - Current Implementation: Not present.
   - New Requirement: Treat as offline-only audit method, consistent with LiDAR/radar pattern of gating the most expensive/highest-fidelity method behind an explicit flag.
   - Affected Files: `src/kradar_visibility/camera_visibility.py` (optional)
   - Effort: High (requires segmentation model inference)
   - Impact: Low (only for offline audit due to CPU-only constraint)

## Prioritized Gap List
| Priority | Gap | Component | Effort | Impact |
|----------|-----|-----------|--------|--------|
| 1 | Missing per-frame LiDAR range-image precomputation and usage | LiDAR visibility | Medium | High |
| 2 | Missing per-frame LiDAR→camera projection for depth-buffer discount | Camera visibility | Medium | High |
| 3 | Missing per-frame radar noise-floor map precomputation and usage | Radar visibility | Medium | Medium |
| 4 | Missing fusion-level ghost flag output | Pipeline | Low | Medium |
| 5 | Missing distortion-corrected corner projection for cameras | Camera visibility | Low | Medium |
| 6 | Missing inter-object occlusion graph for LiDAR | LiDAR visibility | Low | Low |
