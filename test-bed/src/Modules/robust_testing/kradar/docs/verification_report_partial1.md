# Verification Report — Partial 1

**What:** Audit covering Critical Gaps #1–3 and Non-critical Gap #1 from `04_gap_analysis.md`, Tasks 1.1–1.3 and 2.1–2.3 from `06_upgrade_roadmap.md`. Every verdict was independently re-derived from source code + live pytest runs — phase implementation logs were explicitly not trusted.

**Key verdicts:**

| Gap | Verdict | Key finding |
|-----|---------|-------------|
| Critical #1 — LiDAR range-image occlusion | **PASS** | Fully wired end-to-end. `calculate_lidar_visibility()` accepts `range_image`/`sensor_origin`, computes `density_ratio * (1 - occluded_fraction * confidence)`. Pipeline calls `prepare_frame_lidar()` once per sensor per frame. |
| Critical #2 — Radar CFAR noise-floor | **PARTIAL** | `prepare_frame_radar()` with proper guard/training-cell CFAR exists in `radar_visibility.py` but pipeline.py **never calls it** — line 274 passes `noise_floor_db=None` and uses global median only. `radar_score_with_doppler` does not exist in current source. |
| Critical #3 — Camera depth-buffer occlusion | **PASS** | Fully wired. `prepare_frame_camera()` uses vectorized `np.minimum.at` (~0.33s/frame). `calculate_visibility_score()` applies depth-buffer discount. |
| Non-critical #1 — Distortion correction | **PARTIAL** | Distortion math correct in `project_point_to_image()` and `camera_score()`, but `get_camera_params()` never extracts `dist_coeffs` from calibration pickle — pipeline cannot feed real coefficients. |

**Log reliability:** Phase 1 log fabricates 3 non-existent items (`radar_score_with_doppler`, `RADAR_FA_THRESHOLD`, wrong `HALF_WIDTH/HEIGHT`). Phase 2 log falsely claims CFAR is integrated. Phase 3/4 logs mostly accurate but have stale numbers.

**Cleanup debt:** 4 dead-code imports in pipeline.py; `OUTPUT_SCHEMA` missing `ghost_flag`/`weather`; `get_camera_params()` missing `dist_coeffs` extraction; K-Radar dataset unmounted (infra issue, not code).

**Output:** Full report at `docs/verification_report_partial1.md`.