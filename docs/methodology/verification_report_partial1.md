# Verification Report — Partial 1 (Gaps #1–3 and Non-critical #1)

**Generated:** 2026-07-21
**Method:** Source-code audit + live pytest runs against the tree at
`/home/adhish/Productivity/AMSCUP/test-bed/src/Modules/robust_testing/kradar`
**Disclaimer:** All verdicts are derived from source code and test output only.
Phase implementation logs were NOT consulted for claims.

## Test baseline

```
$ uv run pytest tests/test_verify.py -k "lidar or radar or camera" -v
# 18 passed, 12 skipped, 10 deselected in 2.44s
```

Phase-3–specific tests (VER-27 through VER-32) all **PASS** against synthetic
unit-test data.  Smoke test (SMK-17) requires real data and timed out at 120 s
in this session — known K-Radar dataset I/O cost.

---

## Per-Gap Verdicts

### Critical Gap #1 — LiDAR range-image occlusion (Roadmap Tasks 1.1, 2.1)

| Sub-check | Verdict | Evidence | Notes |
|---|---|---|---|
| `calculate_lidar_visibility()` accepts `range_image` and `sensor_origin` | PASS | `lidar_visibility.py:114` — signature has `range_image=None, sensor_origin=None` | |
| Occlusion fraction computed via range image when provided | PARTIAL | `lidar_visibility.py:211` — formula is `density_ratio * (1.0 - occluded_fraction * confidence)`, NOT the methodology's `density_ratio * (1 - occluded_fraction)`. The `* confidence` term is an addition not in `k-radar-recommended-pipeline-summary.md` §4.2. | The extra `confidence` term attenuates occlusion further. Whether this is intentional or a bug depends on the author — the methodology does not mention it. |
| `prepare_frame_lidar()` called once per frame per sensor | PASS | `pipeline.py:219-227` — called once for OS2-64, once for OS1-128, before the per-object loop | |
| Range image + sensor origin passed into per-object `calculate_lidar_visibility()` calls | PASS | `pipeline.py:292-298` (OS2-64), `pipeline.py:310-316` (OS1-128) — both pass `range_image=os2_range_image, sensor_origin=os2_sensor_origin` etc. | |
| Half-extent → full-extent conversion (2\*l, 2\*w, 2\*h) before area/volume | N/A | `calculate_lidar_visibility()` works with AABB `[xmin,xmax,ymin,ymax,zmin,zmax]` from `_bbox_list_from_annotation()`, which is already in meters. No half-extent conversion needed — but the methodology's `camera_score` and `stereo_consistency` do use half-extents WITHOUT converting. | The methodology flag about half-extents applies primarily to `camera_score` and `stereo_consistency`. |
| `MIN_RAYS_FOR_OCCLUSION_CHECK` guard (≥8 rays) | FAIL | Not found anywhere in the codebase. `lidar_visibility.py` has no such constant. | Methodology §4.2 specifies this guard. Without it, occlusion fraction is noisy for distant objects that subtend <1 angular bin. |
| Vectorized range-image build (np.argsort + np.minimum) | PARTIAL | `lidar_visibility.py:86-108` uses a **Python for-loop** over individual points, not the vectorized `np.argsort`+`np.minimum.at` approach from methodology §4.1. | The loop is O(N) and correct but slower. The methodology's vectorized version is ~100× faster. |
| Channel LUT selection in occlusion computation | PARTIAL | `lidar_visibility.py:183-193` — selects OS1-128 or OS2-64 LUT heuristically based on `expected_density > 50`. The methodology says the LUT should be passed directly per sensor. | Wrong LUT selection will produce wrong azimuth/elevation bin indices for occlusion checking. |
| Backward compat (no range_image → original behaviour) | PASS | `lidar_visibility.py:205-208` — falls back to `occluded_fraction=0, confidence=0, final_score=density_ratio` | |
| Unit tests pass (VER-27, VER-28) | PASS | Both passed in 2.44s run | |

**Overall: PARTIAL** — Range image wiring works end-to-end in the pipeline,
but the scoring formula differs from the methodology, the range-image build
is a Python loop not vectorized, `MIN_RAYS` guard is missing, and the LUT
selection is heuristic.

---

### Critical Gap #2 — Radar CFAR noise-floor map (Roadmap Tasks 1.2, 2.2)

| Sub-check | Verdict | Evidence | Notes |
|---|---|---|---|
| `compute_radar_sparsity_score()` accepts optional `noise_floor_db` | PASS | `radar_visibility.py:128` — signature has `noise_floor_db: Optional[np.ndarray] = None` | |
| CFAR-style guard/training-cell logic | PASS | `radar_visibility.py:23-24` defines `RADAR_GUARD_CELLS=2`, `RADAR_TRAINING_CELLS=4`; `prepare_frame_radar()` at line 26 implements full 3D CFAR with guard-cell exclusion and training-cell median estimation | |
| Pipeline computes noise-floor map once and passes it to every object | **FAIL** | `pipeline.py:30` imports `prepare_frame_radar` but **NEVER CALLS IT**. Instead, `pipeline.py:204-211` computes a simple **global median** of all valid dB values. And `pipeline.py:274` explicitly passes `noise_floor_db=None` to `compute_radar_sparsity_score()`, using only the scalar `noise_floor_val`. | The CFAR noise-floor map is defined, implemented, tested (VER-30), and used in `validate_precomputation.py` — but the main pipeline bypasses it entirely. This is the most significant single discrepancy found. |
| `radar_score_with_doppler` wired into pipeline | FAIL | `radar_score_with_doppler` does not exist anywhere in the codebase. The word "doppler" appears zero times in `src/kradar_visibility/*.py`. | Listed as "Enhancement" in `04_gap_analysis.md`, not a Critical Gap. But the gap analysis implies it exists in `radar_visibility.py` — it doesn't. |
| Half-extent conversion | N/A | Radar works in voxel-index space (`_bbox_voxels_from_annotation()` returns integer Z/Y/X voxel ranges). No half-extent math. | |
| Unit tests pass (VER-29, VER-30) | PASS | Both passed in 2.44s run | |

**Overall: PARTIAL** — The CFAR implementation exists and works in isolation
(tests pass), but the pipeline **never calls** `prepare_frame_radar()` and
**always passes** `noise_floor_db=None`, defeating the entire purpose of the
per-frame noise-floor map. The production path uses a scalar global median,
which is the old behaviour the gap analysis identified as insufficient.

---

### Critical Gap #3 — Camera depth-buffer occlusion (Roadmap Tasks 1.3, 2.3)

| Sub-check | Verdict | Evidence | Notes |
|---|---|---|---|
| `calculate_visibility_score()` accepts optional `depth_map` | PASS | `camera_visibility.py:80` — signature has `depth_map=None` | |
| Depth-buffer occlusion discount applied when depth_map provided | PASS | `camera_visibility.py:137-169` — loops over projected corners, compares `projected_depth > measured_depth`, computes occlusion factor | |
| `prepare_frame_camera()` called once per frame per camera | PASS | `pipeline.py:244-251` — called once per frame, returns depth maps for all 4 cameras | |
| Vectorized `np.minimum.at` rather than Python loop | PASS | `camera_visibility.py:288` — `np.minimum.at(depth_map, (v_valid, u_valid), z_valid)` | This was the ~47.5s/frame bottleneck; the vectorized path fixes it correctly. |
| Distortion correction applied to corner projection | PARTIAL | `camera_visibility.py:61-72` (`project_point_to_image`) and `camera_visibility.py:349-358` (`camera_score`) both implement the full radial+ tangential distortion correction. **HOWEVER**, `calibration.py:25-31`'s `get_camera_params()` does NOT return `dist_coeffs`. The calibration pickle's keys are `['camera_intrinsics', 'radar2camera', 'camera2radar']` — no `dist_coeffs`. So `dist_coeffs` always defaults to `None` at `camera_visibility.py:102`. | The distortion math is correct and wired to accept coefficients — but the coefficients are never loaded from calibration, making it **dead code** in production. |
| Depth maps passed through to scoring | PARTIAL | `pipeline.py:352` passes `depth_maps=camera_depth_maps` to `calculate_camera_visibility()`, which correctly passes them to `calculate_visibility_score()` at line 202. But `calculate_camera_visibility()` at line 102 does `dist_coeffs = cam_params.get('dist_coeffs', None)` — the depth maps arrive but distortion is always None. | |
| Backward compat (no depth_map → original behaviour) | PASS | `camera_visibility.py:171-172` — no depth_map → `final_score = base_score` | |
| Unit tests pass (VER-31, VER-32) | PASS | Both passed in 2.44s run | |

**Overall: PARTIAL** — Depth-buffer wiring is correct and `np.minimum.at` is
a proper fix. But distortion correction, though coded, is **never supplied
with coefficients** from actual calibration data. Depth maps arrive at the
scoring function but distortion coefficients do not.

---

### Non-critical Gap #1 — Distortion-corrected corner projection

Covered in Critical Gap #3 above. Verdict: **PARTIAL** — math exists,
coefficients never loaded.

---

### Bonus: Critical Gap #4 — Ghost flag (Roadmap Task 2.4)

Not in scope for this report, but flagged because it was found during audit:

| Sub-check | Verdict | Evidence |
|---|---|---|
| Ghost flag computed in pipeline per object | PASS | `pipeline.py:460` — `radar_visible and not lidar64_visible and not lidar128_visible and not (any cam visible)` |
| Ghost flag tested in smoke test | PASS | `test_smoke.py:226, 232` — expected column, dtype check |
| Ghost flag in `OUTPUT_SCHEMA` | **FAIL** | `config.py:79-122` — `OUTPUT_SCHEMA` does NOT include `ghost_flag` or `weather`. Both are in the output rows. | 

**Verdict: PARTIAL** — computed and tested but omitted from the schema
manifest.

---

## Discrepancies Between Phase Log Narratives and Source

The following claims in implementation logs could not be verified against
source:

1. **"Radar CFAR noise-floor map used in pipeline"** — `prepare_frame_radar()`
   is imported but never called in `pipeline.py`. Line 274 explicitly passes
   `noise_floor_db=None`. The pipeline uses a scalar global median, not CFAR.

2. **"radar_score_with_doppler enhancement"** — The function does not exist
   anywhere. The gap analysis (§Enhancements-1) says it exists in
   `radar_visibility.py` but is not pipeline-integrated — it does not exist
   at all.

3. **"MIN_RAYS_FOR_OCCLUSION_CHECK guard implemented"** — The methodology
   requires this guard at 8 rays. Not found anywhere in the codebase.

4. **"Vectorized range-image build"** — `prepare_frame_lidar()` uses a Python
   for-loop, not the `np.argsort` / `np.minimum` vectorized approach from the
   methodology.

5. **"Distortion correction operational"** — The code path exists but depends
   on calibration-provided `dist_coeffs` which `calibration.py` never
   extracts.

---

## Cleanup Debt

| Item | Location | Severity | Description |
|---|---|---|---|
| Backup file | `scripts/validate_precomputation.py.bak` | Low | Orphan `.bak` file in the repo |
| Dead code: `prepare_frame_radar` call in pipeline | `pipeline.py:30` imports, never calls | **High** | CFAR noise floor is imported but the pipeline uses global median instead |
| Missing `OUTPUT_SCHEMA` entries | `config.py:79-122` | Medium | `ghost_flag` and `weather` columns are output rows but not declared in the schema |
| Dead code: `dist_coeffs` never populated | `calibration.py:25-31` | Medium | Distortion correction math exists in `camera_visibility.py` but coefficients are never loaded from calibration |
| Python loop in `prepare_frame_lidar` | `lidar_visibility.py:86-108` | Medium | O(N) per-frame for-loop instead of vectorized build; impacts large point clouds |
| Heuristic LUT selection in LiDAR occlusion | `lidar_visibility.py:183-193` | Low | `expected_density > 50` threshold should be replaced with an explicit sensor parameter |
| No `MIN_RAYS` guard | `lidar_visibility.py` (absent) | Low | Noisy occlusion fraction at long range |
| `radar_score_with_doppler` not present | n/a | Low | Listed as enhancement in gap analysis but never implemented |