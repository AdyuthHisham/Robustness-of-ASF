# Phase 2: Upgrade Strategy

## Dependency Graph

```
config.py (constants, schema)
    │
    ├── parser.py (HeaderInfo, ObjectAnnotation)
    │       │
    │       └── calibration.py (camera intrinsics/extrinsics from pickle)
    │               │
    │               └── data_loader.py (lazy sensor loads)
    │                       │
    │                       ├── radar_visibility.py
    │                       │       ├── compute_radar_sparsity_score()
    │                       │       └── [NEW] cfar_noise_floor_map()
    │                       │
    │                       ├── lidar_visibility.py
    │                       │       ├── read_pcd_file()
    │                       │       ├── calculate_lidar_visibility()  ← REPLACE
    │                       │       └── [NEW] prepare_frame_lidar()  (range-image)
    │                       │       └── [NEW] lidar_score()         (2.2+2.3 merged)
    │                       │
    │                       └── camera_visibility.py
    │                               ├── project_point_to_image()
    │                               ├── calculate_visibility_score()
    │                               ├── calculate_camera_visibility()
    │                               └── [NEW] camera_score()       (4.2+4.3 merged)
    │                               └── [NEW] prepare_frame_camera() (LiDAR→camera depth maps)
    │
    └── pipeline.py (orchestration)
            ├── compute_visibility_for_frame()  ← MAJOR REFACTOR
            └── run()
```

## Upgrade Order (respecting dependencies)

1. **config.py** - Add new schema columns, constants for new methods (MIN_RAYS, DB_HEADROOM already there, add DEPTH_MARGIN, occlusion thresholds)
2. **lidar_visibility.py** - Core architectural change: range-image precompute + merged 2.2+2.3 scoring (highest impact)
3. **radar_visibility.py** - CFAR noise-floor map + optional Doppler coherence
4. **camera_visibility.py** - LiDAR depth-buffer occlusion (default-on) + stereo consistency
5. **pipeline.py** - Integrate per-frame precompute, new scoring signatures, ghost flag, weather column
6. **tests/test_smoke.py** - Update for new method signatures and expected behaviors
7. **tests/test_verify.py** - Add tests for new columns (occluded_fraction, ghost flag, occlusion_discount)
8. **README.md** - Create from scratch per 08_readme_spec.md

---

## Detailed Upgrade Roadmap

### Phase 1: Foundation & Configuration (Estimated Effort: 3 hours)

**Goal:** Update configuration schema and constants to support new metrics

#### Task 1.1: Extend OUTPUT_SCHEMA in config.py
- **Files to modify:** `src/kradar_visibility/config.py`
- **Changes needed:**
  - Add LiDAR occlusion columns: `lidar64_occluded_fraction`, `lidar64_occlusion_reliable`, `lidar64_n_rays`, `lidar64_density_ratio`, same for lidar128
  - Add camera occlusion columns: `cam_front_occlusion_discount`, `cam_left_occlusion_discount`, `cam_right_occlusion_discount`, `cam_rear_occlusion_discount`
  - Add radar ghost flag: `probable_radar_ghost`
  - Ensure `weather` column is in schema (already present)
- **Dependencies:** None
- **Validation criteria:** Schema matches new methodology requirements; all new columns documented

#### Task 1.2: Add new methodology constants
- **Files to modify:** `src/kradar_visibility/config.py`
- **Changes needed:**
  - `MIN_RAYS_FOR_OCCLUSION_CHECK = 8` (from new methodology)
  - `DEPTH_MARGIN = 0.1` (meters, for camera depth-buffer comparison)
  - `TAU_DENSITY = 0.08` (LiDAR density threshold)
  - `RADAR_GUARD_CELLS`, `RADAR_TRAINING_CELLS` (for CFAR)
  - Camera stereo baseline/focal if available from calibration
- **Dependencies:** Task 1.1
- **Validation criteria:** Constants defined and used in new implementations

#### Task 1.3: Verify calibration loading for stereo rig
- **Files to modify:** `src/kradar_visibility/calibration.py`
- **Changes needed:**
  - Add function to verify front stereo pair overlap (check if cam_front0 and cam_front1 have sufficient baseline and overlapping FOV)
  - Return stereo capability flag per sequence
- **Dependencies:** Task 1.1
- **Validation criteria:** Can determine if 4.5 stereo consistency is applicable

**Checkpoint 1:** `config.py` schema complete; constants defined; calibration can report stereo capability

---

### Phase 2: LiDAR Metrics Engine (Estimated Effort: 6 hours)

**Goal:** Implement range-image precompute and merged 2.2+2.3 LiDAR scoring

#### Task 2.1: Implement `prepare_frame_lidar()` -frame_lidar()` - range image rasterization
- **Files to modify:** `src/kradar_visibility/lidar_visibility.py` (new functions)
- **Changes needed:**
  - Build `range_image[channel_idx, azimuth_bin] = nearest hit range` once per frame
  - Accept `points`, `sensor_origin`, `channel_lut` (elevations, azimuth bins, d_azimuth, d_elevation)
  - Vectorized bin assignment using `np.argsort` for nearest hit per cell
  - Return range_image for reuse across all objects
- **Dependencies:** Phase 1 complete
- **Validation criteria:** Range image shape correct; nearest-hit semantics verified

#### Task 2.2: Implement `lidar_score()` - merged 2.2+2.3
- **Files to modify:** `src/kradar_visibility/lidar_visibility.py`
- **Changes needed:**
  - Input: box_half_extents, points, range_image, sensor_origin, channel_lut, tau_density
  - **2.2 density_ratio:** AABB-prefiltered point-in-box count / expected_count
    - `N_expected = (A_visible / r²) / (d_azimuth * d_elevation)`
    - `A_visible = projected_silhouette_area(box, sensor_origin)` (facing-area model)
  - **2.3 occlusion:** angular_footprint → query range_image → `occluded_fraction = 1 - reaching_rays / n_rays`
  - **Min-ray guard:** if `n_rays < MIN_RAYS_FOR_OCCLUSION_CHECK`, fallback to density only
  - **Combined:** `score = density_ratio * (1 - occluded_fraction)`
  - **Output:** dict with visible, score, density_ratio, occluded_fraction, occlusion_reliable, n_rays
- **Dependencies:** Task 2.1
- **Validation criteria:** Matches new methodology §4.2 exactly; unit test with canonical box

#### Task 2.3: Refactor `calculate_lidar_visibility()` to new signature
- **Files to modify:** `src/kradar_visibility/lidar_visibility.py`
- **Changes needed:**
  - New signature: `calculate_lidar_visibility(points, bboxes, fov, range_limit, expected_density, sensor_origin, channel_lut)`
  - Internally: call `prepare_frame_lidar()` once, then `lidar_score()` per bbox
  - Return arrays matching current interface for backward compatibility during transition
  - Add channel_lut constants for OS2-64 and OS1-128 (elevations, azimuth bins, resolutions)
- **Dependencies:** Task 2.2
- **Validation criteria:** Smoke tests SMK-11, SMK-12, SMK-15 still pass

#### Task 2.4: Add inter-object occlusion graph (optional but recommended)
- **Files to modify:** `src/kradar_visibility/lidar_visibility.py` (new function), `pipeline.py`
- **Changes needed:**
  - `compute_occlusion_graph(objects, range_image, sensor_origin, channel_lut)` → dict mapping object_id → occluder_id
  - O(M²) angular footprint overlap check; for rays failing occlusion check, find nearest box in that direction
  - Add to pipeline output as debug column (optional)
- **Dependencies:** Task 2.2
- **Validation criteria:** Produces plausible occluder assignments on test frames

**Checkpoint 2:** LiDAR scoring produces density_ratio, occluded_fraction, combined score; all smoke tests pass; range-image built once/frame

---

### Phase 3: Radar Metrics Engine (Estimated Effort: 4 hours)

**Goal:** CFAR noise-floor map + optional Doppler coherence gating

#### Task 3.1: Implement `cfar_noise_floor_map()` - per-frame spatially-varying noise floor
- **Files to modify:** `src/kradar_visibility/radar_visibility.py`
- **Changes needed:**
  - Input: `radar_zyx_cube`, `guard_cells`, `training_cells`
  - For each cell, compute median of training cells (guard_banded ring around cell)
  - Return `noise_floor` array same shape as cube
  - Optimize: use scipy.ndimage or manual sliding window for CPU efficiency
- **Dependencies:** Phase 1 complete
- **Validation criteria:** Noise floor varies spatially; median matches global median approximately

#### Task 3.2: Refactor `compute_radar_sparsity_score()` to use CFAR noise floor
- **Files to modify:** `src/kradar_visibility/radar_visibility.py`
- **Changes needed:**
  - New signature: `compute_radar_sparsity_score(radar_zyx_cube, bbox, noise_floor=None)`
  - If noise_floor provided, use it; else fall back to global median (backward compat)
  - Use per-cell noise_floor[bbox] instead of single scalar
- **Dependencies:** Task 3.1
- **Validation criteria:** SMK-14 (monotonic with distance) still passes; scores more stable in adverse weather

#### Task 4.1: Implement `prepare_frame_camera()` - LiDAR→camera sparse depth maps
- **Files to modify:** `src/kradar_visibility/camera_visibility.py`
- **Changes needed:**
  - Input: `points` (LiDAR), `lidar_extrinsics`, `camera_intrinsics_list`, `camera_extrinsics_list`
  - For each camera: transform points to camera frame, project to UV, build sparse depth map
  - `build_sparse_depth_map(uv, z)` → 2D array or dict for neighborhood lookup
  - Return list of depth_maps (one per camera)
- **Dependencies:** Phase 1 complete, LiDAR points already loaded in pipeline
- **Validation criteria:** Depth maps cover projected LiDAR points; neighborhood lookup works

#### Task 4.2: Refactor `calculate_visibility_score()` → `camera_score()` with occlusion discount
- **Files to modify:** `src/kradar_visibility/camera_visibility.py`
- **Changes needed:**
  - New function `camera_score(box_half_extents, K, extrinsics, depth_map, image_size)`
  - Reuse 8-corner projection → convex hull → clip → area × centrality (base_score)
  - **4.3 occlusion discount:** sample pixels in clipped hull, lookup depth_map with radius=3 neighborhood
  - `occluded_px = sum(d_local < z_obj - DEPTH_MARGIN)`
  - `occlusion_discount = 1 - occluded_px / n_samples`
  - `score = base_score * occlusion_discount`
  - Return dict with visible, score, occlusion_discount
- **Dependencies:** Task 4.1
- **Validation criteria:** VER-10..15 still pass; occlusion discount reduces scores for occluded objects

#### Task 4.3: Update `calculate_camera_visibility()` to use new pipeline
- **Files to modify:** `src/kradar_visibility/camera_visibility.py`
- **Changes needed:**
  - Accept precomputed `depth_maps` from `prepare_frame_camera()`
  - Call `camera_score()` per direction with appropriate depth_map
  - Return scores + occlusion_discounts per camera
- **Dependencies:** Task 4.2
- **Validation criteria:** SMK-16 (center > edge) still passes; new occlusion_discount column populated

#### Task 4.4: Implement stereo consistency check (4.5) for front pair
- **Files to modify:** `src/kradar_visibility/camera_visibility.py` (new function), `calibration.py`
- **Changes needed:**
  - `stereo_consistency(box_half_extents, K_left, K_right, T_left, T_right, image_size)`
  - Project box corners to both stereo images
  - Block-match disparity in projected ROI (small region, fast)
  - `consistency = 1 - mean(|d - d_exp|) / d_exp`
  - Apply only if calibration confirms stereo overlap (from Task 1.3)
  - Multiply front camera score by consistency
- **Dependencies:** Task 1.3, Task 4.2
- **Validation criteria:** Only activates when stereo rig confirmed; improves front camera accuracy

**Checkpoint 4:** Camera scores include occlusion_discount by default; stereo consistency optional; all smoke tests pass

---

### Phase 5: Pipeline Integration (Estimated Effort: 5 hours)

**Goal:** Wire all new per-frame precomputes and per-object scoring into pipeline

#### Task 5.1: Refactor `compute_visibility_for_frame()` for per-frame precompute
- **Files to modify:** `src/kradar_visibility/pipeline.py`
- **Changes needed:**
  - Load all sensor data once per frame (already done)
  - **Precompute once:**
    - `radar_noise_floor = cfar_noise_floor_map(radar_cube, ...)` if radar_cube exists
    - `lidar64_range_image = prepare_frame_lidar(os2_points, RADAR_ORIGIN, OS2_CHANNEL_LUT)` if os2_points exist
    - `lidar128_range_image = prepare_frame_lidar(os1_points, RADAR_ORIGIN, OS1_CHANNEL_LUT)` if os1_points exist
    - `camera_depth_maps = prepare_frame_camera(os2_points or os1_points, lidar_extrinsics, camera_intrinsics_list, camera_extrinsics_list)` if calib_available and lidar exists
  - Per-object loop: call new scoring functions with precomputed contexts
  - Collect new output columns (occluded_fraction, occlusion_discount, density_ratio, ghost flag)
- **Dependencies:** Phases 2-4 complete
- **Validation criteria:** All new columns populated; runtime per frame reasonable

#### Task 5.2: Implement cross-sensor ghost flag
- **Files to modify:** `src/kradar_visibility/pipeline.py`
- **Changes needed:**
  - After computing all sensor visibility: `probable_ghost = radar_visible and not lidar64_visible and not lidar128_visible and not any_camera_visible`
  - Add `probable_radar_ghost` column to output rows
- **Dependencies:** Task 5.1
- **Validation criteria:** Ghost flag appears in output; manual spot-check shows it catches radar-only artifacts

#### Task 5.3: Update output schema and DataFrame construction
- **Files to modify:** `src/kradar_visibility/pipeline.py`, `src/kradar_visibility/config.py`
- **Changes needed:**
  - Ensure all new columns in `OUTPUT_SCHEMA` (config.py)
  - Add schema_overrides for new nullable float columns in `pl.DataFrame()`
  - Verify weather column populated from description.txt
- **Dependencies:** Task 1.1, Task 5.1
- **Validation criteria:** Parquet writes without schema errors; all columns present

**Checkpoint 5:** Full pipeline runs end-to-end; produces Parquet with all new columns; smoke test SMK-17 passes

---

### Phase 6: Testing & Validation (Estimated Effort: 4 hours)

**Goal:** Update tests for new methodology; run full verification

#### Task 6.1: Update smoke tests for new signatures
- **Files to modify:** `tests/test_smoke.py`
- **Changes needed:**
  - SMK-14: Verify radar monotonic with CFAR noise floor
  - SMK-15: Verify LiDAR OS1≥OS2 counts still holds with new scoring
  - Add SMK-18: LiDAR occluded_fraction in [0,1], occlusion_reliable boolean
  - Add SMK-19: Camera occlusion_discount in [0,1]
  - Add SMK-20: Ghost flag boolean
- **Dependencies:** Phase 5 complete
- **Validation criteria:** All smoke tests pass on 2 sequences / 20 frames

#### Task 6.2: Update verification tests for new columns
- **Files to modify:** `tests/test_verify.py`
- **Changes needed:**
  - Add VER-27: `lidar64_occluded_fraction` in [0,1], `occlusion_reliable` boolean when n_rays >= 8
  - Add VER-28: `lidar128_occluded_fraction` same
  - Add VER-29: `cam_*_occlusion_discount` in [0,1]
  - Add VER-30: `probable_radar_ghost` boolean, log rate for review
  - Add VER-31: `lidar64_density_ratio` in [0,1], combined score = density × (1-occluded)
  - Add VER-32: Weather column populated and in ALLOWED_WEATHER
- **Dependencies:** Phase 5 complete
- **Validation criteria:** Verification report generated with new VER IDs; no regressions

#### Task 6.3: Run full test suite and generate verification report
- **Commands:**
  - `uv run pytest tests/test_smoke.py -v --timeout=300`
  - `uv run python scripts/run_pipeline.py --sequences 1 2 --frame-limit 20 --output outputs/upgrade_test.parquet`
  - `uv run pytest tests/test_verify.py -v -m "not optional" --json-report --json-report-file=outputs/verify_report.json`
- **Validation criteria:** All smoke tests pass; verification report shows ≥95% pass rate on non-optional tests

**Checkpoint 6:** All tests pass; verification report generated; no regressions

---

### Phase 7: Documentation (Estimated Effort: 3 hours)

**Goal:** Create README.md per 08_readme_spec.md

#### Task 7.1: Write README.md
- **Files to create:** `README.md`
- **Sections per 08_readme_spec.md:**
  1. Overview (2-3 sentences, output schema ref)
  2. Architecture (data flow list from pipeline.py)
  3. Module reference (from actual code signatures)
  4. Methodology summary (per sensor, cross-ref both old and new methodology docs)
  5. Schema reference (from config.py OUTPUT_SCHEMA, note nullable columns)
  6. Setup & usage (uv commands for minimal CPU run)
  7. Testing (smoke/verify commands, expected runtimes)
  8. Known limitations (CPU-only, toy-scale, VER-25/26 optional, GPU TODOs)
  9. Downstream usage examples (2+ Polars one-liners)
- **Dependencies:** All implementation complete
- **Validation criteria:** README compiles (markdown lint); all sections populated from actual code

---

## Overall Effort Estimate

| Phase | Task | Hours |
|-------|------|-------|
| **Phase 1** | Foundation & Configuration | 3 |
| **Phase 2** | LiDAR Metrics Engine | 6 |
| **Phase 3** | Radar Metrics Engine | 4 |
| **Phase 4** | Camera Metrics Engine | 4 |
| **Phase 5** | Pipeline Integration | 5 |
| **Phase 6** | Testing & Validation | 4 |
| **Phase 7** | Documentation | 3 |
| **Total Implementation** | | **29 hours** |
| **Buffer (20%)** | | **6 hours** |
| **Grand Total** | | **~35 hours** |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| LiDAR range-image performance on CPU | Use vectorized NumPy; profile on 1 frame first; fallback to density-only if too slow |
| Missing dataset for testing | Use existing output.parquet for verification tests; smoke tests that need data will skip gracefully |
| Doppler cube not available (radar_tesseract) | Keep Doppler coherence fully flag-gated; default path unchanged |
| Stereo rig overlap unconfirmed | Make stereo consistency strictly conditional on calibration check; default off |
| Schema migration breaks existing consumers | Add new columns only; don't rename/remove existing; document in README |
| Half-extent bugs in new code | Add unit test with canonical box (e.g., x=10,y=0,z=0,θ=0,l=1,w=1,h=1 → V=8, A_front=4) |