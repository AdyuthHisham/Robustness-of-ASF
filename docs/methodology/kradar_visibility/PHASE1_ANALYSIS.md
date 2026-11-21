# Phase 1: Comprehensive Analysis

## Original Methodology Summary

### Document: 00_orchestrator_kickoff_prompt.md
- **Purpose:** Orchestrator initialization & kickoff patterns for implementing the K-Radar Visibility Analysis Pipeline
- **Key Concepts:**
  - CPU-only, validation-only execution mode (toy-scale subsets: 1-2 sequences, ≤20 frames)
  - Package manager: uv exclusively (no pip/conda/venv)
  - Package layout per §8: `kradar_visibility/` with modules for config, parser, calibration, data_loader, radar_visibility, lidar_visibility, camera_visibility, pipeline
  - Phase 1: Sequential foundation (config → parser → calibration → data_loader)
  - Phase 2: Parallel visibility metrics (radar, lidar, camera) via delegate_task
  - Phase 3: Assembly (pipeline.py) + testing (smoke + verification)
- **Architecture:** Sequential dependency chain for foundation, parallel for metrics, integration in pipeline
- **Key Patterns:**
  - `uv run` for all commands
  - Polars for tabular data
  - Graceful degradation: missing sensor files → `visible=False, score=0.0`
  - Never load full 4DRT (`radar_tesseract/`) by default; use `radar_zyx_cube/`
  - Reuse existing `points_in_boxes_gpu` from OpenPCDet where available

### Document: 04_visibility_methodology.md
- **Purpose:** Selected methodology for each visibility score (radar/LiDAR/camera)
- **Key Concepts:**
  - Sub-Goal 2/§8.1 memory efficiency: never load full 4DRT
  - Sub-Goal 3: single oriented-bbox-in-frame primitive reused across sensors
  - Sub-Goal 4/§8.1: vectorizable per-object across all objects in frame
  - Error handling: degrade to `visible=False, score=0.0` on missing sensor files

- **Radar (§4.1) — Method B (Selected):** SNR-weighted power density on `radar_zyx_cube`
  - Formula: `score = sum(max(0, power_db - noise_floor_db) for cell in bbox) / bbox_volume_m3`
  - Per-frame noise floor estimation (median of cells outside annotated bboxes or bottom decile)
  - `radar_fov_in` / `radar_range_in` are pure geometry gates
  - Optional: binary cell-count density (Method A) as debug sidecar

- **LiDAR 64/128 (§4.2) — Methods A+B (Selected):**
  - A: CPU point-in-box count (reuse existing `points_in_boxes_gpu` pipeline via CPU equivalent)
  - B: Count normalized by theoretical expected density → `lidar*_sparsity_score`
  - Expected count model: `(vertical_channels × vertical_extent_angle / total_vertical_fov) × (horizontal_extent_angle / horizontal_angular_resolution)`
  - `lidar*_visible = points_count > 0 AND bbox center within FOV/range`

- **Camera ×4 (§4.3) — Method B (Selected):**
  - 8-corner projection → 2D bbox → area/centrality score
  - Formula: `score = w1 * (clipped_area / image_area) + w2 * (1 - normalized_dist_to_center)`, w1=0.7, w2=0.3
  - Optional occlusion discount (Method C): LiDAR depth-buffer check, gated by config flag
  - `cam_*_visible = z_cam > 0 AND clipped_area > 0`

### Document: 06_smoke_tests_scaffold.md
- **Purpose:** pytest stubs for SMK-01..17 (toy-scale, <5 min CPU)
- **Architecture:** Fixtures for dataset_root, smoke_sequence_ids (1,2), smoke_frame_limit (20), calib_loader, sample_label_file
- **Test Classes:**
  - TestParsing (SMK-01..04): header/object counts, cam-lrr index, calibrations loaded, weather labels
  - TestProjection (SMK-05..09): 8-corner projection, behind-camera rejection
  - TestLoading (SMK-10..13): radar tensor shape, OS2-64 points, OS1-128 ≥ OS2-64, camera images load
  - TestMetrics (SMK-14..17): radar monotonic w/distance, lidar count OS1≥OS2, camera center>edge, full pipeline 2 sequences

### Document: 07_verification_tests_scaffold.md
- **Purpose:** pytest stubs for VER-01..26 (full dataset, but toy-scale for now)
- **Architecture:** Operates on output Parquet table, uses Polars
- **Test Classes:**
  - TestSensorIdentifyConsistency (VER-01..05): sensor_identify ↔ visible flags
  - TestDistanceCorrelation (VER-06..09): median scores decrease with distance
  - TestCameraProjectionSanity (VER-10..15): proj bounds, null when invisible, directional correctness
  - TestPrimarySensorLogic (VER-16..18): primary_sensor = argmax score, count matches, null when zero visible
  - TestDataQuality (VER-19..24): no negative scores/counts, distance consistent, dims positive, no duplicate PKs, all sequences
  - TestWeatherImpact (VER-25..26, optional): weather impact on lidar/radar

### Document: 08_readme_spec.md
- **Purpose:** README requirements for kradar_visibility package
- **Required Sections:**
  1. Overview (2-3 sentences, output schema ref §3.1)
  2. Architecture (data flow diagram/list)
  3. Module reference (per §8 layout, from actual code)
  4. Methodology summary (per sensor, cross-ref 04_visibility_methodology.md)
  5. Schema reference (§3.1 table, nullable columns noted)
  6. Setup & usage (exact uv commands for minimal CPU run)
  7. Testing (smoke/verify commands, expected runtimes)
  8. Known limitations (CPU-only, toy-scale, skipped tests, TODO for GPU/full-dataset)
  9. Downstream usage examples (≥2 Polars one-liners from §10 queries)

---

## New Methodology Summary

### Document: k-radar-recommended-pipeline-summary.md
- **Purpose:** Enhanced pipeline architecture with per-frame precompute + per-object scoring
- **Key Concepts:**
  - **Per-frame precompute (once, shared across all M objects):**
    - Radar: CFAR noise-floor map over `radar_zyx_cube`
    - LiDAR (each): range-image rasterization `(channel × azimuth_bin) → nearest range`
    - Camera: project full LiDAR point cloud into each camera image (for occlusion discount)
  - **Per-object scoring (vectorized across M objects):**
    - Radar: excess-power sum / V_box (1.2); optional Doppler-coherence (1.3) on cropped sub-volume
    - LiDAR: density_ratio × (1 - occluded_fraction) merged from 2.2+2.3
    - Camera: 8-corner area/centrality (4.2) discounted by LiDAR depth-buffer (4.3); stereo (4.5) for front pair
  - **Graceful degradation:** missing sensor → `visible=False, score=0.0`
  - **Cross-sensor QA:** ghost flag `radar_visible ∧ ¬lidar_visible ∧ ¬camera_visible`

- **Theory: Why 2.2 and 2.3 merge (§3):**
  - `N_actual ≈ N_expected(geometry) × fraction_actually_reached(occlusion)`
  - 2.2 measures LHS ratio; 2.3 measures RHS via range image
  - Both query same physical fact (ray first-termination) → build range image once, ask two questions
  - Combined: `score = density_ratio × (1 - occluded_fraction)`

- **Implementation Code (§4):**
  - `prepare_frame_lidar()`: builds range_image[channel, az_bin] = nearest hit range
  - `prepare_frame_radar()`: CFAR noise floor map
  - `prepare_frame_camera()`: LiDAR→camera sparse depth maps
  - `lidar_score()`: AABB-prefiltered point-in-box, projected silhouette area, angular footprint vs range_image
  - `radar_score()`: cell indices in box, excess power vs noise_floor, optional Doppler coherence on cropped sub-volume
  - `camera_score()`: 8-corner convex hull, clip, area×centrality, sample depth_map for occlusion
  - `score_frame()`: orchestration + ghost flag

- **Key Reminders (§5):**
  - Half-extent conversion (`L,W,H = 2*l,2*w,2*h`) exactly once at top of each scoring fn
  - No per-object re-computation of per-frame precompute
  - Graceful degradation wrapper
  - Offline-audit hooks (1.4, 4.4) gated by config, not in default path

### Document: k-radar-sensor-visibility-metrics.md
- **Purpose:** Theoretical reference document for all sensor visibility methods
- **Key Concepts (shared conventions §0):**
  - K-Radar bboxes: `(x,y,z,θ,l,w,h)` with **half-extents** → convert to full `L=2l,W=2w,H=2h` before volumetric computation
  - Point-in-box: rotate to box frame, check `|Δx|≤L/2, |Δy|≤W/2, |Δz|≤H/2`
  - Vectorize via broadcasting (N×M), pre-filter with AABB/KD-tree
  - Graceful degradation: missing sensor → `visible=False, score=0.0`, log warning

- **Radar Methods (§1):**
  - 1.1 Binary cell-count (Baseline A): fixed threshold τ, score = count/V_box
  - 1.2 **SNR-weighted power density (Baseline B — SELECTED):** per-frame CFAR noise floor, excess power sum / V_box
  - 1.3 Doppler-coherence gating (Novel): crop per-object Doppler sub-volume, weight by coherence vs expected v_exp
  - 1.4 Full 4DRT integration (Baseline C — gated): crop per-object AABB in tensor-index space

- **LiDAR Methods (§2/3):**
  - 2.1 Raw point count (Baseline A): unnormalized, range-biased
  - 2.2 **Expected-density normalization (Baseline B — SELECTED):** `N_expected ≈ (Δθ_h·Δθ_v)^-1 · A_visible / r²`, score = min(1, N_actual/N_expected)
  - 2.3 **Ray-casting/frustum occupancy (Novel — recommended upgrade):** range-image rasterization, check if rays reach box range extent
  - 2.4 Voxel occupancy (Baseline C — REJECTED): dominated by 2.2+2.3

- **Camera Methods (§4):**
  - 4.1 Center-point only (Baseline A): binary, no continuous score
  - 4.2 **8-corner projection → area/centrality (Baseline B — SELECTED):** `score = (A_clip/A_full) × centrality`
  - 4.3 Depth-buffer/LiDAR Z-buffer discount (Baseline C — flag-gated): project LiDAR→camera, compare sparse depth vs object depth
  - 4.4 Instance-segmentation mask overlap (Novel — offline only): modal/amodal ratio
  - 4.5 Stereo/optical-flow consistency (Novel): front stereo pair disparity check

- **Decision Matrix (§5):** Table comparing accuracy, weather robustness, distance invariance, occlusion awareness, CPU feasibility, implementation ease

- **Occlusion-Aware Extensions (§6):**
  - Radar: Doppler-coherence (1.3) + symmetry/mirror check (gated)
  - LiDAR: 2.2 (implicit) → 2.3 (explicit, range image) → inter-object occlusion graph (O(M²)) → class-shape-prior comparison
  - Camera: amodal completion (offline) → learned visibility classifiers → mask overlap (4.4) → stereo consistency (4.5) → cross-camera consistency (free)

- **Recommended Pipeline (§7):**
  1. Radar: keep 1.2 default, add 1.3 as optional refinement (cropped sub-volume), 1.4 offline audit
  2. LiDAR: keep 2.2 default (param per sensor via channel LUT), upgrade to 2.3 as standard occlusion-aware augmentation, add inter-object occlusion graph
  3. Camera: keep 4.2 default (distortion-corrected), **enable 4.3 by default** (LiDAR already loaded), add 4.5 for front stereo if rig confirms overlap, 4.4 offline audit
  4. Fusion-level: ghost flag `radar_visible ∧ ¬lidar_visible ∧ ¬camera_visible` for review/down-weight

- **Critical Implementation Note (§8):**
  - **Half-extent conversion applied exactly once** at top of every per-object scoring function
  - Unit test asserting V_box for canonical annotation matches hand-computed value

---

## Methodology Comparison Matrix

| Aspect | Original Methodology | New Methodology | Key Differences |
|--------|---------------------|-----------------|-----------------|
| **Radar Score** | SNR-weighted power density (Method B) on zyx_cube | Same core (1.2), + optional Doppler-coherence (1.3) on cropped sub-volume, + offline 4DRT audit (1.4) | Adds Doppler refinement as optional upgrade; keeps 1.2 as default |
| **Radar Noise Floor** | Per-frame median of valid cells | CFAR-style guard/training cell noise-floor map (precomputed once/frame) | More sophisticated, spatially-varying noise floor |
| **LiDAR Score** | Expected-density normalization (Method B) | Same core (2.2) + **explicit ray-casting occlusion (2.3) merged multiplicatively** | Major upgrade: occlusion-aware via range image, not implicit |
| **LiDAR Per-Frame Precompute** | None (per-object point-in-box) | **Range-image rasterization once/frame** shared across all objects | Enables efficient 2.3; amortizes cost |
| **Camera Score** | 8-corner area/centrality (Method B) | Same core (4.2) + **LiDAR depth-buffer occlusion discount (4.3) enabled by default** | 4.3 was flag-gated optional; now default-on since LiDAR already loaded |
| **Camera Per-Frame Precompute** | None | **LiDAR→camera projection once/frame** (sparse depth maps) | Enables efficient 4.3; amortized across objects |
| **Stereo Consistency** | Not mentioned | Added (4.5) for front pair if rig overlap confirmed | New optional cross-check |
| **Cross-Sensor QA** | VER-01..05 (identify consistency) | **+ Ghost flag: radar_visible ∧ ¬lidar ∧ ¬camera** | Free, high-leverage sanity check |
| **Half-Extent Conversion** | Implied in code comments | **Explicitly mandated: apply exactly once at function entry** with unit test | Critical bug prevention (8× volume / 4× area error if skipped) |
| **Weather Tests** | VER-25/26 optional, skipped | Same, but pipeline now wires weather_label from description.txt | Implementation gap being closed |
| **Calibration Handling** | Basic loading | Graceful degradation wrapped per-sequence (ISSUE-07) | Already partially implemented |

---

## Current Implementation Inventory

### Directory Structure

```
/home/adhish/Productivity/AMSCUP/test-bed/src/Modules/robust_testing/kradar
├── src/
│   └── kradar_visibility/
│       ├── __init__.py              # Exports all public APIs
│       ├── config.py                # Configuration, schema, constants
│       ├── parser.py                # Label file parsing (HeaderInfo, ObjectAnnotation)
│       ├── calibration.py           # Camera calibration loading (pickle T_params_seq)
│       ├── data_loader.py           # Lazy loaders for radar, lidar, camera
│       ├── radar_visibility.py      # compute_radar_sparsity_score (Method B)
│       ├── lidar_visibility.py      # calculate_lidar_visibility (Methods A+B)
│       ├── camera_visibility.py     # calculate_camera_visibility (Method B)
│       └── pipeline.py              # Orchestration: parse → load → score → Parquet
├── scripts/
│   └── run_pipeline.py              # CLI entry point with verification report
├── tests/
│   ├── conftest.py                  # Fixtures: dataset_root, sequences, output_table
│   ├── test_smoke.py                # SMK-01..17 (19 tests collected)
│   └── test_verify.py               # VER-01..26 (operates on output Parquet)
├── output.parquet                   # Existing toy-scale output
├── outputs/verification_report.md   # Existing verification report
├── pyproject.toml                   # uv package config
├── AGENTS.md                        # Project conventions (uv, Polars, GPU reuse, etc.)
├── architecture.md                  # Architecture documentation
├── api_contracts.md                 # API contracts for web visualization
├── README.md                        # Empty (needs creation per 08_readme_spec.md)
├── README_projection.md             # Projection documentation
└── venv/ + .venv/                   # Virtual environments
```

### File Inventory

| File | Type | Purpose | Aligned To | Status |
|------|------|---------|------------|--------|
| `src/kradar_visibility/__init__.py` | Python | Package exports | §8 layout | ✅ Complete |
| `src/kradar_visibility/config.py` | Python | Constants, schema, sensor suite | §3.1, §8.1 | ✅ Complete |
| `src/kradar_visibility/parser.py` | Python | Label parsing (HeaderInfo, ObjectAnnotation) | SMK-01..04 | ✅ Complete |
| `src/kradar_visibility/calibration.py` | Python | Camera calibration from pickle | SMK-03 | ✅ Complete |
| `src/kradar_visibility/data_loader.py` | Python | Lazy sensor data loading | SMK-10..13 | ✅ Complete |
| `src/kradar_visibility/radar_visibility.py` | Python | SNR-weighted power density (Method B) | §4.1, SMK-14, VER-01/06/08 | ✅ Complete |
| `src/kradar_visibility/lidar_visibility.py` | Python | Point-in-box + expected-density (A+B) | §4.2, SMK-11/12/15, VER-02/03/06/07 | ✅ Complete |
| `src/kradar_visibility/camera_visibility.py` | Python | 8-corner projection area/centrality (Method B) | §4.3, SMK-05..09/16, VER-10..15 | ✅ Complete |
| `src/kradar_visibility/pipeline.py` | Python | End-to-end orchestration | §5, SMK-17, all VER | ✅ Complete |
| `scripts/run_pipeline.py` | Python | CLI + verification report generation | §7 report gen | ✅ Complete |
| `tests/conftest.py` | Python | Pytest fixtures | §6, §7 fixtures | ✅ Complete |
| `tests/test_smoke.py` | Python | SMK-01..17 implementations | §6 scaffold | ✅ Complete (19 tests) |
| `tests/test_verify.py` | Python | VER-01..26 implementations | §7 scaffold | ✅ Complete (26 tests) |
| `pyproject.toml` | TOML | Package config, deps, pytest | Project setup | ✅ Complete |
| `README.md` | Markdown | Package documentation | §8_readme_spec | ❌ Empty |
| `output.parquet` | Parquet | Existing toy-scale output | Validation artifact | ✅ Exists |

### Implementation Summary
- **Total Files:** 17 (core package + tests + scripts + config)
- **Fully Implemented:** 100% of original methodology modules
- **Partially Implemented:** 0%
- **Not Started:** README.md (per 08_readme_spec.md), new methodology upgrades
- **Test Status:** 19 smoke tests collected, 26 verify tests collected; **6 smoke tests failing** due to missing dataset

---

## Gap Analysis Report

### Critical Gaps (Must Fix)

| # | Gap | Current Implementation | New Requirement | Affected Files | Complexity | Impact |
|---|-----|------------------------|-----------------|----------------|------------|--------|
| 1 | **LiDAR per-frame range-image precompute** | Per-object point-in-box loop (O(M×N)) | Build range_image[channel, az_bin] once/frame; reuse for density + occlusion | `lidar_visibility.py`, `pipeline.py` | High | Core architecture change; enables 2.3 occlusion |
| 2 | **LiDAR occlusion-aware score (2.3)** | Implicit via density ratio only | Explicit `occluded_fraction` from range-image ray queries; combined score = density × (1-occluded) | `lidar_visibility.py`, `pipeline.py` | High | Major accuracy improvement; addresses explicit occlusion ask |
| 3 | **Radar CFAR noise-floor map** | Global median of valid cells | Spatially-varying noise floor via guard/training cells (precomputed once/frame) | `radar_visibility.py`, `pipeline.py` | Medium | Better weather robustness; matches new spec 1.2 |
| 4 | **Radar Doppler-coherence gating (1.3)** | Not implemented | Optional refinement: crop per-object Doppler sub-volume, weight by coherence vs v_exp | `radar_visibility.py` (new function), `pipeline.py` (flag-gated) | Medium | Rejects multipath ghosts; key radar upgrade |
| 5 | **Camera LiDAR depth-buffer occlusion (4.3)** | Not implemented (was flag-gated optional) | **Enable by default**: project LiDAR→camera once/frame, discount camera score by occluded pixel fraction | `camera_visibility.py`, `pipeline.py` | Medium | Closes major occlusion gap; LiDAR already loaded |
| 6 | **Camera stereo consistency (4.5)** | Not implemented | Front stereo pair disparity check if rig overlap confirmed | `camera_visibility.py` (new), `calibration.py` (verify rig) | Low-Medium | Low-cost occlusion cross-check |
| 7 | **Cross-sensor ghost flag** | Not implemented | `radar_visible ∧ ¬lidar64 ∧ ¬lidar128 ∧ ¬any_camera` → `probable_radar_ghost` column | `pipeline.py` | Low | Free high-leverage QA signal |
| 8 | **Half-extent conversion enforcement** | Done in `ObjectAnnotation.length/width/height` properties and `_obj_corners()` | **Explicit conversion at top of every scoring function** + unit test for canonical box | `radar_visibility.py`, `lidar_visibility.py`, `camera_visibility.py`, tests | Low | Prevents 8× volume / 4× area silent bugs |
| 9 | **Weather label in pipeline output** | Parsed in pipeline.py but not verified in output schema | Ensure `weather` column present and validated in Parquet | `pipeline.py`, `config.py` (OUTPUT_SCHEMA), tests | Low | Enables VER-25/26 |
| 10 | **README.md creation** | Empty file | Full documentation per 08_readme_spec.md sections 1-9 | `README.md` | Medium | Required deliverable |

### Non-Critical Gaps (Should Improve)

| # | Gap | Current | New Requirement | Affected Files | Complexity | Impact |
|---|-----|---------|-----------------|----------------|------------|--------|
| 11 | **Inter-object occlusion graph (LiDAR)** | Not implemented | O(M²) box-pair angular overlap check for occluder attribution | `pipeline.py` (new function) | Medium | Rich QA/debug artifact; downstream fusion feature |
| 12 | **Class-shape-prior occlusion check (LiDAR)** | Not implemented | Compare observed extent vs class-median L/W/H as occlusion evidence | `pipeline.py` (new), needs class stats | Medium | Lightweight amodal proxy |
| 13 | **Cross-camera consistency (Camera)** | Not implemented | Compare visibility scores across overlapping FOV cameras | `pipeline.py` | Low | Free occlusion signal |
| 14 | **Offline audit hooks (1.4, 4.4)** | Not implemented | Config-gated functions for full-4DRT radar & instance-mask camera on sampled frames | New module or `pipeline.py` | Low | Periodic calibration validation |
| 15 | **Output schema: add new columns** | Current OUTPUT_SCHEMA in config.py | Add: `lidar64_occluded_fraction`, `lidar128_occluded_fraction`, `lidar64_occlusion_reliable`, `lidar128_occlusion_reliable`, `probable_radar_ghost`, `cam_*_occlusion_discount` | `config.py`, `pipeline.py` | Low | Schema evolution for new metrics |

### Enhancements Recommended

| # | Enhancement | Description | Effort |
|---|-------------|-------------|--------|
| 16 | **Vectorized per-object scoring** | Current loops over objects; new methodology emphasizes vectorization across M objects using broadcasting | Medium |
| 17 | **Range-image based expected density** | Compute `N_expected` directly from range-image angular footprint instead of analytic formula | Low |
| 18 | **Radar per-object sub-volume cropping** | For 1.3 Doppler coherence, index only box's Doppler bins instead of full 4DRT | Medium |
| 19 | **Structured logging for missing sensors** | Current: debug log; upgrade to structured warning with frame/object context | Low |
| 20 | **Config-driven sensor enable/disable** | Toggle sensors via config flags for ablation studies | Low |

---

## Prioritized Gap List

| Priority | Gap | Component | Effort | Impact |
|----------|-----|-----------|--------|--------|
| 1 | LiDAR range-image precompute + occlusion (2.2+2.3 merged) | `lidar_visibility.py`, `pipeline.py` | High | **Core architecture upgrade**; enables explicit occlusion |
| 2 | Radar CFAR noise-floor map | `radar_visibility.py`, `pipeline.py` | Medium | Weather robustness; matches new spec |
| 3 | Camera LiDAR depth-buffer occlusion (4.3 default-on) | `camera_visibility.py`, `pipeline.py` | Medium | Closes major camera occlusion gap |
| 4 | Radar Doppler-coherence gating (1.3 flag-gated) | `radar_visibility.py`, `pipeline.py` | Medium | Ghost rejection; key radar upgrade |
| 5 | Cross-sensor ghost flag | `pipeline.py` | Low | Free QA signal |
| 6 | Half-extent conversion enforcement + unit test | All visibility modules + tests | Low | Bug prevention |
| 7 | Weather label validation in output | `pipeline.py`, `config.py`, tests | Low | Enables VER-25/26 |
| 8 | README.md creation | `README.md` | Medium | Required deliverable |
| 9 | Output schema extensions | `config.py`, `pipeline.py` | Low | Schema evolution |
| 10 | Inter-object occlusion graph | `pipeline.py` | Medium | QA/debug richness |
| 11 | Stereo consistency (front pair) | `camera_visibility.py`, `calibration.py` | Low-Medium | Low-cost occlusion check |
| 12 | Class-shape-prior occlusion | `pipeline.py` | Medium | Amodal proxy |
| 13 | Cross-camera consistency | `pipeline.py` | Low | Free signal |
| 14 | Offline audit hooks | New module | Low | Calibration validation |
| 15 | Vectorized per-object scoring | All visibility modules | Medium | Performance at scale |
| 16 | Range-image expected density | `lidar_visibility.py` | Low | Cleaner computation |
| 17 | Radar sub-volume cropping | `radar_visibility.py` | Medium | Memory efficiency for 1.3 |
| 18 | Structured missing-sensor logging | `pipeline.py` | Low | Debuggability |
| 19 | Config-driven sensor toggles | `config.py`, `pipeline.py` | Low | Ablation support |