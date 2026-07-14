## Upgrade Roadmap - Phased Approach

### Phase 1: Foundation - Sensor Module Updates 
**Goal:** Update individual sensor visibility modules to support precomputed data inputs and improve core algorithms while maintaining backward compatibility.
- **Task 1.1:** LiDAR visibility - Add support for precomputed range image
  - Files to modify: `src/kradar_visibility/lidar_visibility.py`
  - Changes needed: 
    - Modify `lidar_score` function to accept optional `range_image` and `sensor_origin` parameters
    - Implement occlusion fraction calculation using range image when provided
    - Keep existing behavior when parameters are not provided (backward compatibility)
    - Add helper function to validate range image dimensions
  - Dependencies: None (can be done independently)
  - Validation criteria: 
    - Unit tests pass with and without range image
    - Occlusion fraction computes correctly when range image provided
    - No regression in existing test suite

- **Task 1.2:** Radar visibility - Add support for precomputed noise-floor map
  - Files to modify: `src/kradar_visibility/radar_visibility.py`
  - Changes needed:
    - Modify `compute_radar_sparsity_score` to accept optional `noise_floor_map` parameter
    - Implement CFAR-style thresholding using noise floor map when provided
    - Keep existing behavior when parameter not provided (backward compatibility)
    - Add helper function to compute noise floor map from radar cube
  - Dependencies: None (can be done independently)
  - Validation criteria:
    - Unit tests pass with and without noise floor map
    - Score adapts to local noise variations when map provided
    - No regression in existing test suite

- **Task 1.3:** Camera visibility - Add support for depth buffer and distortion correction
  - Files to modify: `src/kradar_visibility/camera_visibility.py`
  - Changes needed:
    - Modify `calculate_visibility_score` to accept optional `depth_map` parameter
    - Implement depth-buffer occlusion discount when depth map provided
    - Add distortion correction to `project_point_to_image` using calibration coefficients
    - Keep existing behavior when parameters not provided (backward compatibility)
  - Dependencies: None (can be done independently)
  - Validation criteria:
    - Unit tests pass with and without depth map
    - Depth buffer discount reduces score appropriately for occluded points
    - Distortion correction improves projection accuracy near image edges
    - No regression in existing test suite

**Checkpoint 1:** All sensor modules updated and backward-compatible unit tests passing. Manual verification of new features with synthetic data.

### Phase 2: Metrics Engine - Pipeline Integration 
**Goal:** Update the pipeline to compute and pass precomputed data to sensor modules and add fusion-level features.
- **Task 2.1:** Pipeline - Add per-frame precomputation for LiDAR range images
  - Files to modify: `src/kradar_visibility/pipeline.py`
  - Changes needed:
    - Add function `prepare_frame_lidar` (or import from lidar_visibility) for each LiDAR sensor
    - Call once per frame per LiDAR sensor before object loop
    - Pass range image and sensor origin to `lidar_score` calls
  - Dependencies: Phase 1 Task 1.1 (lidar_visibility.py)
  - Validation criteria:
    - Precomputed range images generated per frame
    - LiDAR scores use range image when available
    - No performance regression (check timing)

- **Task 2.2:** Pipeline - Add per-frame precomputation for radar noise-floor map
  - Files to modify: `src/kradar_visibility/pipeline.py`
  - Changes needed:
    - Add function to compute CFAR-style noise floor map from radar cube
    - Call once per frame before object loop
    - Pass noise floor map to `compute_radar_sparsity_score` calls
  - Dependencies: Phase 1 Task 1.2 (radar_visibility.py)
  - Validation criteria:
    - Noise floor map computed per frame
    - Radar scores use noise floor map when available
    - No performance regression

- **Task 2.3:** Pipeline - Add per-frame precomputation for camera depth maps
  - Files to modify: `src/kradar_visibility/pipeline.py`
  - Changes needed:
    - Add function to project LiDAR point cloud into each camera image to build sparse depth maps
    - Call once per frame per camera before object loop
    - Pass depth map to `calculate_visibility_score` calls
  - Dependencies: Phase 1 Task 1.3 (camera_visibility.py)
  - Validation criteria:
    - Depth maps generated per frame per camera
    - Camera scores use depth map when available
    - No performance regression

- **Task 2.4:** Pipeline - Add fusion-level ghost flag output
  - Files to modify: `src/kradar_visibility/pipeline.py`
  - Changes needed:
    - In per-object loop, compute `ghost_flag = radar_visible and not lidar64_visible and not lidar128_visible and not any camera visible`
    - Add `ghost_flag` column to output rows
  - Dependencies: None (but requires sensor visibility flags)
  - Validation criteria:
    - Ghost flag correctly set for synthetic radar-only detections
    - Column added to output Parquet

**Checkpoint 2:** Pipeline updated with all precomputation steps and ghost flag. Integration test running on a small subset (e.g., one sequence) without errors. Output validated for new columns and sensible values.

### Phase 3: Test Scaffolding - Validation & Test Updates 
**Goal:** Update test suites and add validation scripts to ensure correctness of new features.
- **Task 3.1:** Update unit tests for sensor modules
  - Files to modify: `tests/test_verify.py` (and potentially add new test files)
  - Changes needed:
    - Add test cases for lidar_score with range image
    - Add test cases for compute_radar_sparsity_score with noise floor map
    - Add test cases for calculate_visibility_score with depth map and distortion
    - Ensure existing tests still pass
  - Dependencies: Phase 1 and Phase 2
  - Validation criteria:
    - All unit tests pass
    - New test cases cover edge cases (empty inputs, invalid dimensions)

- **Task 3.2:** Add validation script for precomputation outputs
  - Files to modify: Create `scripts/validate_precomputation.py`
  - Changes needed:
    - Script that runs pipeline on a test sequence and verifies:
      - Range images have correct dimensions and reasonable values
      - Noise floor maps are non-negative and correlate with radar cube statistics
      - Depth maps have valid values where LiDAR points project
      - Ghost flag behaves as expected
  - Dependencies: Phase 2
  - Validation criteria:
    - Script runs without errors
    - Outputs validation report (pass/fail per check)

- **Task 3.3:** Update smoke tests to include new features
  - Files to modify: `tests/test_smoke.py`
  - Changes needed:
    - Extend smoke test to verify new columns exist in output
    - Verify ghost flag is boolean
    - Verify precomputation does not break existing functionality
  - Dependencies: Phase 2
  - Validation criteria:
    - Smoke test passes

**Checkpoint 3:** All tests (unit, smoke, validation) passing. Validation script shows correct behavior for new features on test data.

### Phase 4: Integration & Testing - Full Validation 
**Goal:** Perform full integration testing on representative data and finalize documentation.
- **Task 4.1:** Run integration test on multiple sequences
  - Files to modify: None (use existing run_pipeline.py)
  - Changes needed:
    - Execute pipeline on a subset of sequences (e.g., 5 sequences) with new features enabled
    - Monitor for errors, performance impact, and output correctness
  - Dependencies: Phase 3
  - Validation criteria:
    - Pipeline runs to completion without errors
    - Output files generated with expected columns
    - Basic sanity checks on output (e.g., scores in [0,1], ghost flag sparse)

- **Task 4.2:** Performance benchmark
  - Files to modify: Create `scripts/benchmark_precomputation.py`
  - Changes needed:
    - Compare runtime per frame with and without precomputation (should be similar or slightly better due to shared computation)
    - Report overhead of precomputation steps
  - Dependencies: Phase 2
  - Validation criteria:
    - Precomputation overhead < 20% per frame
    - No significant increase in memory usage

- **Task 4.3:** Documentation update
  - Files to modify: 
    - Update `src/kradar_visibility/lidar_visibility.py` docstring
    - Update `src/kradar_visibility/radar_visibility.py` docstring
    - Update `src/kradar_visibility/camera_visibility.py` docstring
    - Update `src/kradar_visibility/pipeline.py` docstring
    - Optionally update `docs/` directory with new methodology notes
  - Changes needed:
    - Document new parameters and their usage
    - Explain precomputation workflow
    - Note backward compatibility
  - Dependencies: All previous phases
  - Validation criteria:
    - Documentation builds without errors (if using Sphinx, etc.)
    - Content accurately reflects implementation

**Checkpoint 4:** Integration testing complete, performance acceptable, documentation updated. Overall system ready for use.

## Overall Effort Estimate
- Analysis:  (already completed via gap analysis)
- Implementation:  (Phase 1: 16, Phase 2: 12, Phase 3: 10, Phase 4: 8)
- Testing:  (included in phases, but dedicated testing effort)
- Documentation:  (included in Phase 4)

Note: Effort estimates are approximate and assume familiarity with the codebase. Actual time may vary based on complexity of integration and unforeseen issues.
