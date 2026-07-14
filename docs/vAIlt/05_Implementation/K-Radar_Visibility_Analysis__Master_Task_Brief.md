---
title: K-Radar Visibility Analysis — Master Task Brief
type: concept
source: home/adhish/Downloads/kradar_task_brief.md
date: 2026-07-02
tags: [05 Implementation]
---
# K-Radar Visibility Analysis — Master Task Brief

> **Generated:** 2026-06-24  
> **Working Directory:** `/home/adhish/Productivity/AMSCUP/test-bed/src/Modules/robust_testing/kradar`  
> **Dataset Root:** `/home/adhish/Productivity/AMSCUP/repos/K-Radar`  
> **Docs Output:** `/home/adhish/Productivity/AMSCUP/docs/`  
> **Reference Docs:** `/home/adhish/Downloads/` (source spec markdowns)

---

## 1. Executive Summary

This brief aggregates all open tasks for the **K-Radar Visibility Analysis Pipeline** — a CPU-only, toy-scale validation tool that computes per-object visibility scores across radar, LiDAR (64/128), and 4 cameras for the K-Radar dataset. The pipeline outputs a Parquet table with ~30 columns per annotated object per frame.

**Execution Mode:** CPU-Only / Validation-Only (2 sequences, ≤20 frames for smoke tests; full 58-sequence run is future scope).

---

## 2. Task Inventory

### Task 1 — Web Visualization Tool
**Goal:** Build a website to view sensors for each annotation value, showing bounding boxes and LiDAR/radar points.

**Scope:**
- Visualize oriented 3D bounding boxes from `info_label_rev2/*.txt` overlaid on:
  - LiDAR point clouds (`os2-64/`, `os1-128/`)
  - Radar `radar_zyx_cube/` (Doppler-collapsed, not full 4DRT)
  - Camera images (4× cameras: front, left, right, rear)
- Support per-sequence, per-frame navigation
- Display computed visibility scores (radar sparsity, LiDAR points, camera projection area)

**Dependencies:** Tasks 2, 3, 5, 6 (need labels, calibration, data loading, weather)

---

### Task 2 — Resolve Ambiguous Sensor Labels (`L` vs `L1`)
**Goal:** Determine which physical sensor `L` and `L1` in `info_labelRev2` actually refer to.

**Context from Spec:**
- The K-Radar dataset has **two LiDAR sensors**: OS2-64 and OS1-128
- `sensor_identify` field in labels uses codes like `R`, `L`, `L1`, `L2`, `C`, etc.
- `L` (unspecified) vs `L1` (explicit) creates ambiguity for `lidar64_visible` / `lidar128_visible` logic
- **VER-04** requires: `sensor_identify == "L"` → `lidar64_visible OR lidar128_visible` ≥95% match

**Investigation Steps:**
1. Parse `info_label_rev2/*.txt` across multiple sequences
2. Cross-reference `sensor_identify` values with actual sensor availability per sequence
3. Check calibration files to confirm which sequences have OS2-64 vs OS1-128
4. Map `L` → likely OS2-64 (older/primary) or OS1-128; map `L1` → explicit OS2-64; `L2` → OS1-128
5. Document the mapping rule for the pipeline's `primary_sensor` logic

**Output:** Document the definitive mapping in the project docs.

---

### Task 3 — Verify LiDAR Data Accuracy
**Goal:** Verify processed LiDAR data and check accuracy of point-in-box counts.

**Methodology (from §4.2):**
- **Method A:** CPU-based point-in-box for raw point counts (`lidar64_points_count`, `lidar128_points_count`)
- **Method B:** Expected-density normalization → `lidar*_sparsity_score` (range- and channel-invariant 0–1 score)
- Expected count model: `expected ≈ (vertical_channels × vertical_extent_angle / total_vertical_fov) × (horizontal_extent_angle / horizontal_angular_resolution)`

**Verification Checks:**
- **SMK-11:** N > 0 points for frames with visible objects
- **SMK-12:** OS1-128 point count ≥ OS2-64 for same frame (CPU point-in-box)
- **SMK-15:** Same object, OS1-128 point count ≥ OS2-64
- **VER-06:** Median `lidar64_points_count` strictly decreases with distance (or R² > 0.5)
- **VER-07:** Same for OS1-128
- **VER-20:** No negative point counts
- **VER-25:** LiDAR lower in adverse weather (clear vs rain/sleet/snow)

**Note:** `points_in_boxes_gpu` exists elsewhere in the test-bed repo — search for and reuse it; do not reimplement.

---

### Task 4 — Aggregate Work Report
**Goal:** Analyze the working directory and produce a report at `/home/adhish/Productivity/AMSCUP/docs/`.

**Report Contents:**
1. Current codebase status (files implemented, stubs remaining)
2. Phase 1 completion: `config.py` → `parser.py` → `calibration.py` → `data_loader.py`
3. Phase 2 status: `radar_visibility.py`, `lidar_visibility.py`, `camera_visibility.py`
4. Phase 3 status: `pipeline.py`, `tests/test_smoke.py`, `tests/test_verify.py`
5. Smoke test results (SMK-01..17 pass/fail)
6. Verification test results (VER-01..26 pass/fail)
7. Known blockers and TODOs
8. File tree of the working directory

---

### Task 5 — Document `config.py` Contents
**Goal:** Extract and document the contents of `config.py` in the project report.

**Source:** `/home/adhish/Productivity/AMSCUP/test-bed/src/Modules/robust_testing/kradar/src/kradar_visibility/config.py`

**Expected Contents:**
- Dataset root path (`KRADAR_ROOT`)
- Sensor suite configuration (7 sensors: R, L1, L2, CF, CL, CR, CRE)
- Camera intrinsics/extrinsics paths
- Output schema column lists (§3.1)
- Weather label mappings
- CPU-only flags (e.g., `ENABLE_FULL_TESSERACT = False`, `ENABLE_OCCLUSION_CHECK = False`)
- Toy-scale defaults (2 sequences, 20 frames)

---

### Task 6 — Implement Weather Data Gathering
**Goal:** Integrate weather data into the pipeline's data gathering stage.

**Source:** Each sequence folder contains `description.txt` with weather labels.

**Implementation:**
- Parse `description.txt` per sequence (format: `weather: <label>`)
- Allowed labels: `clear`, `overcast`, `fog`, `rain`, `sleet`, `snow`
- Join weather column into the output Parquet table at pipeline stage
- **SMK-04:** Weather labels must be in allowed set
- **VER-25:** Requires weather column for LiDAR adverse-weather comparison
- **VER-26:** Requires weather column for radar vs LiDAR weather sensitivity

**Pipeline Integration:**
- `data_loader.py` or `pipeline.py` should read `description.txt` once per sequence
- Weather column should be nullable (some sequences may lack the file)

---

### Task 7 — Weather & Metadata Frequency Analysis
**Goal:** Parse all `description.txt` files across the dataset and produce a frequency map.

**Source:** `/home/adhish/Productivity/AMSCUP/repos/K-Radar/data/<folder_number>/description.txt`

**Steps:**
1. Iterate all sequence folders (1..58)
2. Parse each `description.txt`
3. Extract:
   - Weather condition (clear, overcast, fog, rain, sleet, snow)
   - Any other metadata fields (time of day, location, etc.)
4. Build frequency tables:
   - Weather distribution across all 58 sequences
   - Weather distribution by distance bins
   - Sequence count per weather type
5. Visualize as bar chart / pie chart

**Output:** Document the frequency map in the project report and save as a standalone figure.

---

## 3. Architecture Overview (from Spec)

```
info_label_rev2/*.txt
        ↓
    parser.py  ──→  headers_df / objects_df (Polars)
        ↓
  calibration.py  ──→  K, R, t for 7 sensors (R, L1, L2, CF, CL, CR, CRE)
        ↓
  data_loader.py  ──→  per-frame lazy loads:
                       • radar_zyx_cube/ (NOT full 4DRT)
                       • os2-64/ & os1-128/ point clouds
                       • 4× camera images
        ↓
  ┌─────────────────┬─────────────────┬─────────────────┐
  ↓                 ↓                 ↓
radar_           lidar_           camera_
visibility.py    visibility.py    visibility.py
  • Method B       • Method A+B     • Method B
  • SNR-weighted   • CPU point-in-  • 8-corner proj
    power density    box → expected   → area × centrality
  • fov_in &         density ratio
    range_in gates
        ↓
    pipeline.py  ──→  Parquet output (per-object, per-frame)
        ↓
  tests/test_smoke.py  (SMK-01..17)
  tests/test_verify.py (VER-01..26)
```

**Module Layout (`kradar_visibility/`):**
| File | Phase | Purpose |
|------|-------|---------|
| `config.py` | 1 | Paths, constants, schema columns, flags |
| `parser.py` | 1 | Parse `info_label_rev2/*.txt` → structured DataFrames |
| `calibration.py` | 1 | Load 7-sensor calibration (K, R, t) |
| `data_loader.py` | 1 | Lazy per-frame sensor data loading |
| `radar_visibility.py` | 2 | `radar_sparsity_score` (Method B) |
| `lidar_visibility.py` | 2 | `lidar*_points_count` + `lidar*_sparsity_score` (A+B) |
| `camera_visibility.py` | 2 | `cam_*_visibility_score` (Method B) + projection |
| `pipeline.py` | 3 | Orchestrate → Parquet output |
| `tests/test_smoke.py` | 3 | SMK-01..17 |
| `tests/test_verify.py` | 3 | VER-01..26 |

---

## 4. Methodology Reference (from §4)

### 4.1 Radar — `radar_sparsity_score`
- **Method:** B (SNR-weighted power density on `radar_zyx_cube`)
- **Formula:** `score = Σ(max(0, power_db - noise_floor_db)) / bbox_volume_m3`
- **Noise floor:** Per-frame median/bottom-decile of cells outside annotated bboxes
- **Gating:** `radar_visible = fov_in AND range_in` (107° azimuth, 37° elevation, 0–118 m)
- **Optional:** Full 4DRT integration gated behind `--full-tesseract` flag (future scope)

### 4.2 LiDAR — `lidar64_sparsity_score`, `lidar128_sparsity_score`
- **Method:** A + B
- **A:** CPU point-in-box count → `lidar*_points_count`
- **B:** Expected-density normalization → `lidar*_sparsity_score = clip(actual / expected, 0, 1)`
- **Expected model:** `(vertical_channels × v_θ_extent / total_v_fov) × (h_θ_extent / h_angular_res)`
- **Gating:** `lidar*_visible = points_count > 0 AND bbox center within sensor FOV/range`

### 4.3 Camera — `cam_*_visibility_score`
- **Method:** B (8-corner projection → 2D area + centrality)
- **Formula:** `score = 0.7 × (clipped_area / image_area) + 0.3 × (1 - normalized_dist_to_center)`
- **Projection:** `K[R|t]` on 8 bbox corners → convex hull → clip to `[0,1280) × [0,720)`
- **Gating:** `cam_*_visible = z_cam > 0 AND clipped_area > 0`
- **Optional:** LiDAR depth-buffer occlusion discount (gated by `enable_occlusion_check`)

---

## 5. Schema Reference (§3.1 Output Columns)

### Object Identity
| Column | Type | Nullable |
|--------|------|----------|
| `sequence_id` | str | No |
| `frame_idx` | int | No |
| `obj_tracking_id` | int | No |
| `obj_class` | str | No |
| `obj_x`, `obj_y`, `obj_z` | float | No |
| `obj_length`, `obj_width`, `obj_height` | float | No |
| `obj_theta` | float | No |
| `obj_distance_ego` | float | No |
| `sensor_identify` | str | No |
| `weather` | str | Yes (Task 6) |

### Radar
| Column | Type | Nullable |
|--------|------|----------|
| `radar_visible` | bool | No |
| `radar_fov_in` | bool | No |
| `radar_range_in` | bool | No |
| `radar_sparsity_score` | float | Yes (0.0 if not visible) |

### LiDAR 64 (OS2-64)
| Column | Type | Nullable |
|--------|------|----------|
| `lidar64_visible` | bool | No |
| `lidar64_points_count` | int | No |
| `lidar64_sparsity_score` | float | Yes |

### LiDAR 128 (OS1-128)
| Column | Type | Nullable |
|--------|------|----------|
| `lidar128_visible` | bool | No |
| `lidar128_points_count` | int | No |
| `lidar128_sparsity_score` | float | Yes |

### Camera (×4: front, left, right, rear)
| Column | Type | Nullable |
|--------|------|----------|
| `cam_front_visible`, etc. | bool | No |
| `cam_front_proj_x`, `cam_front_proj_y` | float | Yes (null if not visible) |
| `cam_front_visibility_score` | float | Yes |

### Aggregated
| Column | Type | Nullable |
|--------|------|----------|
| `num_sensors_visible` | int | No |
| `primary_sensor` | str | Yes (null if none visible) |

---

## 6. Smoke & Verification Test Matrix

### Smoke Tests (SMK-01..17) — `tests/test_smoke.py`
| ID | Module | What it tests |
|----|--------|---------------|
| SMK-01 | parser | Header count==1, object count==N |
| SMK-02 | parser | cam-lrr index resolves to existing files |
| SMK-03 | calibration | 7 calibrations loaded, matrices valid |
| SMK-04 | data_loader | Weather labels in allowed set |
| SMK-05..08 | camera | Projection of center points to 4 cameras |
| SMK-09 | camera | Behind-camera rejection (z < 0) |
| SMK-10 | data_loader | Radar tensor shape valid, no OOM |
| SMK-11 | data_loader | OS2-64 pointcloud N > 0 |
| SMK-12 | data_loader | OS1-128 ≥ OS2-64 point count |
| SMK-13 | data_loader | 4 camera images load, shape (720,1280,3) |
| SMK-14 | radar | Close object score > far object score |
| SMK-15 | lidar | OS1-128 count ≥ OS2-64 for same object |
| SMK-16 | camera | Center-of-frame score > edge-of-FOV score |
| SMK-17 | pipeline | End-to-end 2-seq/20-frame run → Parquet |

### Verification Tests (VER-01..26) — `tests/test_verify.py`
| ID | Category | What it tests |
|----|----------|---------------|
| VER-01..05 | Sensor Identify | `sensor_identify` chars imply correct visibility booleans |
| VER-06..09 | Distance Correlation | Scores decrease with distance (monotonic / R²) |
| VER-10..15 | Camera Projection | In-bounds projections, null when invisible, camera-side consistency |
| VER-16..18 | Primary Sensor | Argmax logic, count consistency, null when zero |
| VER-19..24 | Data Quality | Non-negative scores, positive dimensions, distance consistency, no dupes |
| VER-25..26 | Weather Impact | LiDAR lower in adverse weather; radar less sensitive than LiDAR |

---

## 7. Dependencies & Tooling

- **Package Manager:** `uv` only (no pip/conda/venv directly)
- **DataFrame:** Polars (not pandas)
- **Testing:** `pytest` via `uv run pytest`
- **Math:** NumPy, SciPy (for `pearsonr`, `mannwhitneyu`)
- **Point-in-box:** CPU-based (NumPy or Open3D), no GPU kernels
- **Image loading:** PIL / OpenCV for camera images
- **Output:** Parquet format

---

## 8. Known Limitations (Current Build)

1. **CPU-only:** No GPU kernels (`points_in_boxes_gpu` not used)
2. **Toy-scale validation:** 2 sequences, ≤20 frames for smoke tests
3. **No full 4DRT:** `radar_zyx_cube/` only; `radar_tesseract/` is future scope
4. **No occlusion discount:** Camera Method C (LiDAR depth-buffer) is flag-gated off
5. **Weather column:** Requires Task 6 implementation
6. **Full-dataset verification:** 58-sequence run is future scope

---

## 9. Task Priority & Dependencies

```
Phase 0 (Foundation)
  ├── Task 5: Read config.py → document constants
  ├── Task 2: Resolve L/L1 ambiguity → unblock label parsing
  └── Task 6: Implement weather gathering → unblock VER-25/26

Phase 1 (Core Pipeline — Sequential)
  ├── config.py
  ├── parser.py
  ├── calibration.py
  └── data_loader.py
       └── Task 7: Weather frequency analysis (parallel)

Phase 2 (Metrics — Parallel)
  ├── radar_visibility.py
  ├── lidar_visibility.py  ← Task 3: verify accuracy
  └── camera_visibility.py

Phase 3 (Integration)
  ├── pipeline.py
  ├── tests/test_smoke.py
  ├── tests/test_verify.py
  └── Task 4: Generate aggregate work report

Phase 4 (Visualization)
  └── Task 1: Build web viewer (depends on all above)
```

---

## 10. Reference Documents

| Document | Path | Purpose |
|----------|------|---------|
| Orchestrator Kickoff | `/home/adhish/Downloads/00_orchestrator_kickoff_prompt.md` | Full spec, goals, package layout, delegation strategy |
| Visibility Methodology | `/home/adhish/Downloads/04_visibility_methodology.md` | Radar=B, LiDAR=A+B, Camera=B formulas |
| Smoke Tests Scaffold | `/home/adhish/Downloads/06_smoke_tests_scaffold.md` | SMK-01..17 pytest stubs |
| Verification Tests Scaffold | `/home/adhish/Downloads/07_verification_tests_scaffold.md` | VER-01..26 pytest stubs |
| README Spec | `/home/adhish/Downloads/08_readme_spec.md` | Required README sections |

---

*End of Task Brief*
