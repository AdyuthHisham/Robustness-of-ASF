# Knowledge/Verification/Kradar-Verification-Partial1

**Date:** 2026-07-20
**Source:** [verification_report_partial1.md](file:///home/adhish/Productivity/AMSCUP/docs/verification_report_partial1.md)

## Summary

Independent source-code audit (not trusting implementation logs) of K-Radar visibility upgrade covering Critical Gaps #1-3 and Non-critical Gap #1.

### Verdicts

| Gap | Verdict | Root Cause |
|-----|---------|------------|
| Critical #1 — LiDAR range-image occlusion (Tasks 1.1, 2.1) | **PASS** | `calculate_lidar_visibility()` accepts range_image/sensor_origin. `prepare_frame_lidar()` called once per sensor per frame. Formula: `density_ratio * (1 - occluded_fraction * confidence)`. Tests VER-27,28 pass. |
| Critical #2 — Radar CFAR noise-floor (Tasks 1.2, 2.2) | **PARTIAL** | `prepare_frame_radar()` with guard/training-cell CFAR exists in radar_visibility.py BUT pipeline.py:274 passes `noise_floor_db=None` — uses global median only. CFAR function never called from pipeline. `radar_score_with_doppler` does not exist. Tests VER-29,30 pass. |
| Critical #3 — Camera depth-buffer occlusion (Tasks 1.3, 2.3) | **PASS** | `prepare_frame_camera()` uses vectorized `np.minimum.at` (~0.33s/frame vs ~47s Python loop). `calculate_visibility_score()` applies depth-buffer discount. Fully wired through pipeline. Tests VER-31,32 pass. |
| Non-critical #1 — Distortion correction | **PARTIAL** | Correct math in `project_point_to_image()` and `camera_score()`, but `calibration.py:19-32` `get_camera_params()` never extracts `dist_coeffs` from pickle. Pipeline cannot feed real coefficients. |

### Phase Log Reliability

| Log | Fabrications |
|-----|-------------|
| Phase 1 | `radar_score_with_doppler()` (non-existent), `RADAR_FA_THRESHOLD` (non-existent), wrong HALF_WIDTH/HEIGHT (960/540 vs 1280/720) |
| Phase 2 | Falsely claims CFAR noise-floor is integrated into pipeline |
| Phase 3 | Stale test count (19 vs actual 27 passed) |
| Phase 4 | Generally accurate. Benchmark ~0.23s vs measured ~0.33s (within noise) |

### Cleanup Debt

- **Dead code (4 items in pipeline.py):** `prepare_frame_radar`, `RADAR_GUARD_CELLS`/`RADAR_TRAINING_CELLS`, `camera_score()`, `stereo_consistency()` — all imported but never called
- **Schema drift:** `OUTPUT_SCHEMA` in config.py missing `ghost_flag` and `weather` columns (both computed in pipeline.py)
- **Calibration gap:** `get_camera_params()` doesn't return `dist_coeffs`
- **Infrastructure:** K-Radar dataset not mounted at `DATASET_ROOT` path — SMK-17 cannot run

### What to Fix Next

1. Wire `prepare_frame_radar()` call into pipeline.py's per-frame precomputation (replace global median with CFAR)
2. Update `calibration.py` to extract `dist_coeffs` from pickle and return them from `get_camera_params()`
3. Sync `OUTPUT_SCHEMA` in config.py with actual pipeline output columns (add ghost_flag, weather)
4. Remove dead-code imports from pipeline.py or implement the missing call sites

**Links:** [[04_gap_analysis]] [[06_upgrade_roadmap]]