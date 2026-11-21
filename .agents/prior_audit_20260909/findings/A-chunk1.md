# Chunk 1 — Reviewer A (Correctness & data integrity) — kradar_visibility core

## Findings

### A-1-01: `radar_visible` is not gated on radar_cube presence — violates the documented missing-sensor-degrades-to-False invariant

- **File:line**: `test-bed/src/Modules/robust_testing/kradar/src/kradar_visibility/pipeline.py:301-306`
- **Mechanism**: `radar_fov_in = _radar_fov_check(...)`, `radar_range_in = _radar_range_check(...)`, then `radar_visible = radar_fov_in and radar_range_in` — computed purely from object geometry (obj.x/y/z vs. FOV/range), with **no dependency on whether `radar_cube` loaded successfully**. Only `radar_score` is conditioned on `radar_cube is not None` (line 306: `if radar_visible and radar_cube is not None`). AGENTS.md and architecture.md both state: "Missing sensor files must degrade to `visible=False, score=0.0` — never raise on a missing frame; log and continue."
- **Failure scenario**: A frame whose `radar_zyx_cube/cube_{frame_idx}.mat` file is missing (data_loader.load_radar_cube returns `None`, logged as a warning, no exception). For any object geometrically inside the radar's FOV/range cone, the emitted row has `radar_visible=True, radar_sparsity_score=0.0` instead of `radar_visible=False, radar_sparsity_score=0.0`. This corrupts `num_sensors_visible` (over-counts by 1) and can corrupt `primary_sensor` selection: since `radar_score=0.0` ties with any other zero-score sensor, `max(visible_sensors, key=lambda x: x[1])` (line 462) picks the first tied entry — radar is checked first (line 445) — so a frame with no real radar data and only e.g. a barely-visible camera at score 0.0 would report `primary_sensor='radar'` when no radar signal exists at all.
- **Severity**: silent wrong output

### A-1-02: LiDAR occlusion channel-LUT selection heuristic is broken — both sensors' `expected_density` values exceed the threshold, so OS2-64 is always misclassified as OS1-128

- **File:line**: `test-bed/src/Modules/robust_testing/kradar/src/kradar_visibility/lidar_visibility.py:185-195`
- **Mechanism**: When `range_image`/`sensor_origin` are supplied (which they always are per-frame from `pipeline.py:257-265` whenever points exist), the function picks the occlusion channel LUT by `if expected_density > 50: channel_lut = OS1_128_CHANNEL_LUT else: channel_lut = OS2_64_CHANNEL_LUT` (comment: "Rough estimation: higher expected_density means more channels ... Arbitrary threshold"). The caller passes the real `_EXPECTED_OS2`/`_EXPECTED_OS1` constants from `pipeline.py:80-81`.
- **Repro**: `_EXPECTED_OS2 = (64 * 22.5 / 360) * (360 / 0.18) = 8000.0`; `_EXPECTED_OS1 = (128 * 45 / 360) * (360 / 0.18) = 32000.0` (verified: `uv run --project test-bed python3 -c "print((64*22.5/360)*(360/0.18)); print((128*45/360)*(360/0.18))"` → `8000.0`, `32000.0`). Both values are >> 50, so `expected_density > 50` is **always true** for both sensors — every OS2-64 call to `calculate_lidar_visibility` (called from `pipeline.py:334`, passing `expected_density=_EXPECTED_OS2`) resolves `channel_lut = OS1_128_CHANNEL_LUT`, the wrong sensor's channel LUT. `_validate_range_image_dimensions` (line 198) may catch a shape mismatch and fall back to `occluded_fraction=0.0, confidence=0.0` (i.e. occlusion correction silently disabled) rather than raising, so this can manifest either as wrong-LUT occlusion math or as occlusion correction quietly turning itself off for every OS2-64 row — neither is flagged anywhere in output or logs at the row level.
- **Severity**: silent wrong output

## Unverified / Suspicion

- **`_validate_range_image_dimensions` fallback behavior when the wrong LUT is picked (A-1-02)**: whether the dimension check actually catches the OS2/OS1 LUT mismatch (causing occlusion correction to silently no-op) or whether it passes and produces genuinely wrong occlusion fractions depends on `_compute_occlusion_fraction_from_range_image`'s indexing and the actual `OS2_64_CHANNEL_LUT`/`OS1_128_CHANNEL_LUT` shapes, which were not read in this pass. Flagged but not traced to a concrete numeric output.
- Did not read `camera_visibility.py`'s occlusion/depth-map code (`prepare_frame_camera`, `camera_score`, `stereo_consistency`) or `calibration.py` in this chunk due to scope/time — a correctness pass on those (referenced in pipeline.py:44-45, 282-295) is still open.
- Did not verify `parser.py`'s `obj.theta` degrees-vs-radians handling beyond the inline comment at `pipeline.py:132-134` claiming raw label files store degrees — worth a second reviewer's confirmation against an actual label file, not confirmed here.
