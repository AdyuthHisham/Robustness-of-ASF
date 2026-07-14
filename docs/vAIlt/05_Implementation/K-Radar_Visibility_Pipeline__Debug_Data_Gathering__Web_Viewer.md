---
title: K-Radar Visibility Pipeline — Debug, Data Gathering & Web Viewer
type: experiment
source: home/adhish/Downloads/kradar_task_full_spec.md
date: 2026-07-02
tags: [05 Implementation]
---
# K-Radar Visibility Pipeline — Debug, Data Gathering & Web Viewer

## Context

The core K-Radar visibility pipeline (Phase 1–3: `config.py` → `parser.py` → `calibration.py` → `data_loader.py` → `radar/lidar/camera_visibility.py` → `pipeline.py` → smoke/verification tests) is partially implemented at:

- **Working Directory:** `/home/adhish/Productivity/AMSCUP/test-bed/src/Modules/robust_testing/kradar`
- **Dataset Root:** `/home/adhish/Productivity/AMSCUP/repos/K-Radar`
- **Docs Output:** `/home/adhish/Productivity/AMSCUP/docs/`
- **Reference Specs:** `/home/adhish/Downloads/` (source markdowns)

### Reference Documents (read in this order)
1. `kradar_task_brief.md` — master task brief with full task inventory
2. `04_visibility_methodology.md` — radar=B, LiDAR=A+B, camera=B methodology
3. `06_smoke_tests_scaffold.md` — SMK-01..17 stubs
4. `07_verification_tests_scaffold.md` — VER-01..26 stubs
5. `08_readme_spec.md` — README requirements

---

## Goals (in order)

### 1. Assess Current State
- Run `uv run pytest tests/test_smoke.py -v` on the 2-sequence / 20-frame toy subset.
- Report: which SMK tests pass, which fail, and why.
- Run `uv run pytest tests/test_verify.py -v -m "not optional"` and report results.

### 2. Resolve Ambiguous Sensor Labels (Task 2)
- Investigate `sensor_identify` field in `info_label_rev2/*.txt` across multiple sequences.
- Cross-reference with actual sensor availability (OS2-64 vs OS1-128) and calibration files.
- Definitively map: `L` → ?, `L1` → OS2-64, `L2` → OS1-128.
- Update `parser.py` / pipeline logic so VER-04 passes (`sensor_identify == "L"` → `lidar64_visible OR lidar128_visible` ≥95%).
- Document the mapping rule in the project docs.

### 3. Document `config.py` (Task 5)
- Extract and document the contents of `config.py` in the project report at `/home/adhish/Productivity/AMSCUP/docs/`.
- Include: `KRADAR_ROOT`, sensor suite config, camera paths, output schema columns, weather mappings, CPU-only flags, toy-scale defaults.

### 4. Implement Weather Data Gathering (Task 6)
- Parse `description.txt` per sequence (format: `weather: <label>`).
- Allowed labels: `clear`, `overcast`, `fog`, `rain`, `sleet`, `snow`.
- Join weather column into the output Parquet table.
- Ensure SMK-04 (weather labels in allowed set) and VER-25/26 (weather impact tests) are unblocked.

### 5. Build Web Visualization Tool (Task 1)
- Build a lightweight web viewer to visualize sensors per annotation.
- Overlay oriented 3D bounding boxes from `info_label_rev2/*.txt` on:
  - LiDAR point clouds (`os2-64/`, `os1-128/`)
  - Radar `radar_zyx_cube/` (Doppler-collapsed)
  - Camera images (front, left, right, rear)
- Support per-sequence, per-frame navigation.
- Display computed visibility scores (radar sparsity, LiDAR points, camera projection area).
- Use a simple static HTML/JS or lightweight Python server (e.g. Flask/FastAPI) — CPU-only, no GPU required.

---

## Constraints

- **Package manager:** `uv` only. No pip.
- **DataFrame:** Polars (not pandas).
- **Execution:** CPU-only, toy-scale (2 sequences, ≤20 frames).
- **No full 4DRT:** Use `radar_zyx_cube/` only.
- **Quality gate:** Before `kanban_complete`, run `uvx ruff check .`, `uvx black --check .`, `uvx mypy .`, `uvx pre-commit run --all-files` and fix all failures.

---

## Acceptance Criteria

- [ ] Smoke tests SMK-01..17 pass on the 2-sequence subset.
- [ ] Verification tests VER-01..26 pass (optional VER-25/26 if weather data ready).
- [ ] Sensor label mapping (`L` vs `L1` vs `L2`) is documented and implemented.
- [ ] `config.py` contents are documented in `/home/adhish/Productivity/AMSCUP/docs/`.
- [ ] Weather column is present in Parquet output with valid labels.
- [ ] Web viewer runs and can display at least one sequence's frames with bounding boxes overlaid on all 4 sensors.
- [ ] All linting/type checks pass.
