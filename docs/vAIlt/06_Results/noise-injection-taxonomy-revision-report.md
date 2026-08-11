# Noise Injection Taxonomy Revision Report

**Date:** 2026-07-23
**Rev:** Rev 1 (18 effects) → Rev 2 (12 effects)
**Source:** /home/adhish/Productivity/AMSCUP/docs/vAIlt/noise-injection-design.md
**Implementation:** /home/adhish/Productivity/AMSCUP/repos/K-Radar/datasets/effects/noise_injection.py
**Tests:** /home/adhish/Productivity/AMSCUP/repos/K-Radar/datasets/effects/test_noise_injection.py

---

## Summary

Replaced the 18-effect corruption taxonomy (7 radar + 5 LiDAR + 6 camera) with a streamlined 12-effect taxonomy (4 per modality) based on the canonical sensor-failure types: frame deletion, Gaussian noise / noise-induced shifts, partial loss, complete loss.

---

## What Changed

### Effects Added (new — no prior equivalent)

| Effect | Modality | Notes |
|--------|----------|-------|
| `frame_deletion` | All 3 | Supports deterministic (interval or index-list) and random (per-frame probability) sub-modes. When fired, sets sensor keys to None (radar/LiDAR) or zero-filled normalized tensor (camera). |
| `noise_induced_shifts` | Radar | Cartesian position displacement by sampled noise vectors. Distinct from old `azimuth_jitter` (angular rotation) and old `power_gaussian_noise` (power-only). Parameters: `shift_std`, `distribution`, `clip_radius`. |
| `loss_complete` | All 3 | Full sensor blackout. Sets keys to None (radar/LiDAR) or zero tensor (camera). Explicitly distinct from `loss_partial(fraction=1.0)`. |

### Effects Removed from Active Registry (preserved as legacy)

| Old Effect | Reason for Removal |
|---|---|
| `power_gaussian_noise` (R1) | Not in new radar taxonomy; radar noise effect replaced by `noise_induced_shifts` (coordinate shift, not power noise). |
| `range_attenuation` (R3) | Not in canonical taxonomy. |
| `doppler_corruption` (R4) | Not in canonical taxonomy. |
| `ghost_points` (R5) | Not in canonical taxonomy. |
| `azimuth_jitter` (R6) | Replaced by `noise_induced_shifts` (broader: Cartesian displacement, not angular-only). |
| `power_saturation` (R7) | Not in canonical taxonomy. |
| `lidar_fov_occlusion` (L2) | Not in canonical taxonomy. |
| `lidar_range_dropout` (L4) | Not in canonical taxonomy. |
| `lidar_downsampling` (L5) | Not in canonical taxonomy. |
| `camera_motion_blur` (C2) | Not in canonical taxonomy. |
| `camera_brightness` (C3) | Not in canonical taxonomy. |
| `camera_patch_occlusion` (C4) | Not in canonical taxonomy; replaced by `loss_partial` (single-region zero-out with `fraction` param). |
| `camera_jpeg_compression` (C5) | Not in canonical taxonomy. |
| `camera_gamma_distortion` (C6) | Not in canonical taxonomy. |

### Effects Renamed / Widened

| Old Name | New Name | Change |
|---|---|---|
| `sparse_point_dropout` | `loss_partial` (radar) | Renamed. `rate` param → `fraction`. Same Bernoulli-drop mechanism. |
| `lidar_random_dropout` | `loss_partial` (LiDAR) | Renamed. `rate` param → `fraction`. Same mechanism. |
| `lidar_position_noise` (L3) | `gaussian_noise` (LiDAR) | Widened: now also adds noise to intensity channel via `sigma_intensity` param. |
| `camera_gaussian_noise` (C1) | `gaussian_noise` (camera) | Preserved. Same function. |
| — | `loss_partial` (camera) | New function: single contiguous region zeroed out, parameterized by `fraction`. |

---

## Design Decisions

### Decision 1: Duplicate "Loss Partial" Resolution

The original task specification listed LiDAR as "5 effects" but enumerated only 4 items: frame deletion, Gaussian noise, loss partial, loss complete. The text "loss partial" appeared twice in the source — a confirmed transcription artifact. This report treats Loss Partial as listed **once**, giving LiDAR exactly **4** distinct effects.

The claimed total of "13 effects (5 LiDAR + 4 camera + 4 radar)" is therefore **12** effects. The enumerated lists in the specification are treated as the source of truth; the parenthetical count in the summary was an artifact of the duplication.

### Decision 2: Loss Partial vs Loss Complete — Distinct Explicit Effects

`loss_complete` is implemented as a **separate function**, NOT as `loss_partial(fraction=1.0)`. Rationale:

1. **Semantic distinction:** `loss_partial` models stochastic data loss (each point/region has independent probability of loss). `loss_complete` models a deterministic total sensor blackout. These represent different failure modes.

2. **Implementation divergence for camera:** `loss_partial` zeros a single contiguous region of the image (via rectangular mask). `loss_partial(fraction=1.0)` would need to zero the entire image, but the region-based mechanism doesn't naturally extend to 100% coverage. `loss_complete` uses a direct tensor zero — a distinct code path.

3. **Signal semantics in dict_item:** `loss_partial(fraction=1.0)` on point clouds produces an empty array `shape=(0, N)` — the key is still present. `loss_complete` sets the key to `None`. Downstream code can distinguish these via `_has_key()`, enabling different handling for "frame has no data because every point was dropped" vs "frame has no data because the sensor blacked out."

4. **Metadata clarity:** The `noise_injection` metadata records the effect name. A downstream analysis run can filter by `loss_complete` vs `loss_partial` independently, enabling per-failure-mode metrics.

### Decision 3: Frame Deletion — Per-Sensor Key Clear, Not Frame Skip

Frame deletion does not remove the frame from the evaluation loop entirely. Instead, it clears the affected sensor's data (sets to None or zero tensor). This keeps the frame in the sequence for processing by other sensors' data, which is the correct semantics for multi-sensor evaluation: a LiDAR blackout frame still has radar and camera data.

A `should_skip(frame_index, modality)` pre-check method is provided for eval scripts that want to avoid loading frames for a deleted sensor. The eval script CAN call `should_skip` before `dataset[idx]` to skip wasted I/O, but is NOT required to — if the frame is loaded anyway, `__call__` handles the deletion.

### Decision 4: Noise-Induced Shifts vs Azimuth Jitter

`noise_induced_shifts` uses Cartesian displacement (dX, dY, dZ sampled per point from Gaussian or uniform distribution). Old `azimuth_jitter` rotated points around the sensor origin. The new effect is:
- **More general:** not constrained to spherical coordinates; produces arbitrary displacement
- **More realistic for some failure modes:** multipath can shift a detection laterally without changing range (e.g., off-boresight ghost from a strong reflector)
- **Parameter-compatible:** `shift_std` controls magnitude directly in metres (vs `sigma_deg` which depends on range)

Old `azimuth_jitter` is preserved as legacy for manual import.

---

## Legacy Preservation Strategy

**Non-destructive approach.** All 18 old effect functions are preserved in `noise_injection.py` under a `# LEGACY EFFECTS` section, with full docstrings and function bodies. Legacy registries (`RADAR_EFFECTS_LEGACY`, `LIDAR_EFFECTS_LEGACY`, `CAMERA_EFFECTS_LEGACY`, `ALL_EFFECTS_LEGACY`) are also maintained.

Legacy functions:
- Are NOT loaded into `ALL_EFFECTS` (the active lookup used by `NoiseInjector._resolve`)
- Can still be imported individually: `from noise_injection import power_gaussian_noise`
- Are still callable with the same signature `(dict_item, params, rng) -> dict`
- Will cause `ValueError` if referenced by name in a new-taxonomy `EffectConfig` (designed, not accidental)

---

## Test Results

**103 tests, all PASS, 0 failures.**

| Test Group | Tests | Scope |
|---|---|---|
| Radar effects | 19 | Frame deletion (3 sub-modes), noise-induced shifts (dispersion + clip + power invariance), loss partial (3 fractions + vs-complete distinction), loss complete |
| LiDAR effects | 12 | Frame deletion (3 sub-modes), Gaussian noise (xy/z/intensity params, zero-intensity invariance), loss partial (3 fractions), loss complete |
| Camera effects | 17 | Frame deletion (2 sub-modes), Gaussian noise (sigma=0/sigma>0, multi-camera), loss partial (3 fractions, single-region verification via scipy ndimage), loss complete |
| Registry validation | 17 | Count = 4 per modality, exact name sets, default ordering, legacy-presence checks |
| Injector integration | 22 | End-to-end multi-effect composition, frame deletion via injector, p=0.0 gate, empty config, unknown-effect error, seed determinism, missing keys, should_skip pre-check, legacy name rejection, index-list mode, has_key skip behaviour |

---

## Training Code Verification

Confirmed: no training code paths are touched. Specifically:
- `pipelines/pipeline_detection_v1_0.py` has zero references to `NoiseInjector`, `effects`, `cfg_effect`, or anything under `datasets/effects/`.
- `utils/util_pipeline.py` `build_dataset()` is unmodified (no `**kwargs`).
- The module is eval-time-only.

---

## Amendment 2026-07-24: Camera Gaussian Noise Legacy Resolution

### Finding

`CAMERA_EFFECTS_LEGACY["gaussian_noise"]` and `CAMERA_EFFECTS["gaussian_noise"]` were the **exact same function object** (`camera_gaussian_noise`, defined at line 349). There was no separate legacy copy. This contradicts the claim "all 18 legacy effects were preserved non-destructively and separately" — for camera Gaussian noise, the legacy registry merely aliased the new-taxonomy function.

### Resolution

The duplicate key was **removed** from `CAMERA_EFFECTS_LEGACY` with a comment explaining why: camera Gaussian noise was carried forward into the active taxonomy unchanged, so no separate legacy copy is needed. The function `camera_gaussian_noise` remains accessible at module level and via `CAMERA_EFFECTS["gaussian_noise"]`.

The legacy camera count decreases from 6 to 5 (genuinely distinct legacy effects only). Total legacy effects across all modalities drops from 18 to 17 because camera Gaussian noise was never a separate legacy implementation — it's the same function as the active taxonomy.

Files modified in this amendment:

| File | Change |
|------|--------|
| `/home/adhish/Productivity/AMSCUP/repos/K-Radar/datasets/effects/noise_injection.py` | Removed `"gaussian_noise"` key from `CAMERA_EFFECTS_LEGACY`; added explanatory comment. |
| `/home/adhish/Productivity/AMSCUP/repos/K-Radar/datasets/effects/test_noise_injection.py` | Updated legacy-count check: `== 6` → `== 5`. |
| `/home/adhish/Productivity/AMSCUP/repos/K-Radar/datasets/effects/smoke_test_taxonomy.py` | Updated two legacy-count checks (`6→5`, `18→17`). |
| `/home/adhish/Productivity/AMSCUP/docs/vAIlt/camera-gaussian-noise-resolution.md` | Full investigation record. |

### Test results after amendment

- `test_noise_injection.py`: **103 tests, 103 PASS, 0 FAIL**
- `smoke_test_taxonomy.py`: **89 checks, 89 PASS, 0 FAIL**

---

## Files Modified

| File | Change |
|------|--------|
| `/home/adhish/Productivity/AMSCUP/docs/vAIlt/noise-injection-design.md` | Complete rewrite of Sections 1 (taxonomy), 2 (registries, default ordering), 5 (verification plan). Added Change Log and design-decision sections. |
| `/home/adhish/Productivity/AMSCUP/repos/K-Radar/datasets/effects/noise_injection.py` | Added 12 new effect functions. Added `_frame_deletion_check()`, `_zero_camera_tensor()`, `_set_none()` helpers. Updated registries. Updated `NoiseInjector.__call__` to accept `frame_index` parameter. Added `should_skip` method. Preserved all 18 legacy functions in a `# LEGACY EFFECTS` section with associated legacy registries. |
| `/home/adhish/Productivity/AMSCUP/repos/K-Radar/datasets/effects/test_noise_injection.py` | Complete rewrite: 103 tests covering all 12 new effects (all sub-modes), registry validation, injector integration, legacy compatibility. |
| `/home/adhish/Productivity/AMSCUP/docs/vAIlt/noise-injection-taxonomy-revision-report.md` | This file. Added Amendment 2026-07-24. |
| `/home/adhish/Productivity/AMSCUP/docs/vAIlt/camera-gaussian-noise-resolution.md` | New — investigation record for the camera Gaussian noise legacy resolution. |