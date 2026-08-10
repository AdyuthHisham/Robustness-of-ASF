# Noise Injection Module — Inference-Time Robustness Testing

**Date:** 2026-07-23 (Rev 2 — taxonomy revision)
**Status:** Implementation complete
**Scope:** Standalone corruption/injection module for radar + LiDAR + camera at K-Radar evaluation time only.

---

## Change Log (Rev 1 → Rev 2)

| Date | Change | Reason |
|------|--------|--------|
| 2026-07-23 | Replaced 18-effect list with 12-effect taxonomy (4 per modality) | User specification — streamlined to canonical sensor-failure types: frame deletion, Gaussian noise / noise-induced shifts, partial loss, complete loss. |
| 2026-07-23 | Removed 11 old effects: R2 (doppler corruption), R3 (range attenuation), R5 (ghost points), R7 (power saturation), L2 (FOV occlusion), L4 (range dropout), L5 (downsampling), C2 (motion blur), C3 (brightness), C5 (JPEG compression), C6 (gamma distortion) | Not part of the new canonical taxonomy. Preserved in `noise_injection.py` under `# LEGACY EFFECTS` section — not loaded into registries, available for manual import. |
| 2026-07-23 | Renamed "sparse_point_dropout" → "loss_partial" (radar), "random_dropout" → "loss_partial" (LiDAR); unified API with `fraction` param | Standardised naming across modalities. The underlying Bernoulli-drop mechanism is identical. |
| 2026-07-23 | Added `frame_deletion` across all 3 modalities (new) | New requirement: deterministic (interval or index-list) or random (per-frame probability) frame skip. |
| 2026-07-23 | Added `noise_induced_shifts` for radar (new) | Replacement for old azimuth_jitter + new requirement: coordinate/bin shift caused by a noise process, distinct from additive power noise. |
| 2026-07-23 | Added `loss_complete` as a distinct explicit effect (not fraction=1.0 alias) | Sesign decision: see §1.4. |
| 2026-07-23 | LiDAR `gaussian_noise` widened from pure position noise to position + intensity noise | Unified effect per spec: "additive Gaussian noise on point positions/intensity". |
| 2026-07-23 | Camera `loss_partial` uses single-region zero-out with `fraction` param; distinct from old `patch_occlusion` | Per spec requirement: "distinct from generic patch occlusion". |
| 2026-07-23 | Updated registries (`RADAR_EFFECTS`, `LIDAR_EFFECTS`, `CAMERA_EFFECTS`) to reflect exactly the 12-effect taxonomy | Old registries preserved as `RADAR_EFFECTS_LEGACY` etc. |
|| 2026-07-23 | Added `frame_index` optional parameter to `NoiseInjector.__call__()` and `_apply_list()` | Required by deterministic frame_deletion (interval/index-list sub-mode). |
|| 2026-07-28 | Simplified all radar effects to operate ONLY on `rdr_sparse` (+ `rdr_polar_3d` where separately handled). Removed all `pc100p` branches from active and legacy effect functions. | Verified that `pc100p` has zero downstream consumers in the model, loss, or eval pipeline. See [`rdr_sparse-vs-pc100p-explainer.md`](rdr_sparse-vs-pc100p-explainer.md) for full evidence chain. `pc100p` is still loaded and available in `dict_item` but is no longer modified by any noise effect. |

### What maps from old to new

| Old effect | New effect | Mapping |
|---|---|---|
| R1 power_gaussian_noise | — (removed) | Not in new radar taxonomy (replaced by noise_induced_shifts for radar-specific noise). |
| R2 sparse_point_dropout | `loss_partial` (radar) | Same Bernoulli-drop mechanism; param renamed `rate` → `fraction`. |
| R3 range_attenuation | — (removed) | — |
| R4 doppler_corruption | — (removed) | — |
| R5 ghost_points | — (removed) | — |
| R6 azimuth_jitter | `noise_induced_shifts` (partial) | `noise_induced_shifts` is a distinct mechanism (Cartesian displacement vs angular rotation). Old azimuth_jitter preserved as legacy. |
| R7 power_saturation | — (removed) | — |
| L1 random_dropout | `loss_partial` (LiDAR) | Same mechanism; param renamed `rate` → `fraction`. |
| L2 fov_occlusion | — (removed) | — |
| L3 position_noise | `gaussian_noise` (LiDAR, widened) | Now also adds noise to intensity channel. Renamed from `lidar_position_noise`. |
| L4 range_dropout | — (removed) | — |
| L5 downsampling | — (removed) | — |
| C1 gaussian_noise | `gaussian_noise` (camera) | Unchanged. |
| C2 motion_blur | — (removed) | — |
| C3 brightness | — (removed) | — |
| C4 patch_occlusion | — (removed) | Not in new taxonomy. Camera `loss_partial` uses a different mechanism (single region with `fraction` param). Old patch_occlusion preserved as legacy. |
| C5 jpeg_compression | — (removed) | — |
| C6 gamma_distortion | — (removed) | — |

### Duplicate "Loss Partial" resolution

The original task specification listed LiDAR as having 5 effects but enumerated only 4 items: frame deletion, Gaussian noise, loss partial, loss complete. The text "loss partial" appeared twice in the source — a transcription artifact. The design treats Loss Partial as a single effect, giving LiDAR exactly **4** effects. The claimed total of "5 LiDAR + 4 camera + 4 radar = 13 effects" is therefore **12** effects. This document uses the enumerated lists as the source of truth.

---

## 1. Corruption Types by Modality

Each entry: short mechanism description and config parameters.

### 1.1 Radar — 4D Imaging Radar (4 effects)

| # | Name | Mechanism | Parameters |
|---|------|-----------|------------|
| R1 | **Frame deletion** | Skip entire radar frame. Deterministic mode: delete every Nth frame (or frames in an explicit index list). Random mode: delete each frame with independent probability p. When fired, sets `rdr_sparse` → `None`, `rdr_polar_3d` → `None`. | `mode` (str, `"deterministic"` or `"random"`, default `"random"`), `interval` (int, every Nth — used when `mode="deterministic"` and no `index_list`), `index_list` (list[int], explicit indices to delete — overrides `interval`), `p` (float, per-frame prob — used when `mode="random"`, default 0.1) |
| R2 | **Noise-induced shifts** | Shift radar detection positions by a noise process. Each point in `rdr_sparse[:, :3]` is displaced by a random vector drawn from a zero-mean Gaussian (or uniform) distribution. This is a _coordinate shift_ effect — distinct from additive power noise. | `shift_std` (float, std dev of displacement in metres, default 1.0), `distribution` (str, `"gaussian"` or `"uniform"`, default `"gaussian"`), `clip_radius` (float, max displacement radius in metres, optional — clips extreme outliers) |
| R3 | **Loss partial** | Remove a fraction of radar detections/points via Bernoulli sampling on `rdr_sparse` rows. Each point independently kept with probability `(1 - fraction)`. | `fraction` (float ∈ [0, 1], fraction of points/returns to remove, default 0.3) |
| R4 | **Loss complete** | Full radar data blackout for this frame. Sets `rdr_sparse` → `None`, `rdr_polar_3d` → `None`. Semantic marker: this frame experienced a total sensor blackout (as opposed to "every point happened to be dropped"). | (none) |

### 1.2 LiDAR — 64-beam Mechanical LiDAR (4 effects)

| # | Name | Mechanism | Parameters |
|---|------|-----------|------------|
| L1 | **Frame deletion** | Skip entire LiDAR frame. Same semantics as radar frame deletion. When fired, sets `ldr64` → `None`. | `mode` (str, `"deterministic"` or `"random"`), `interval` (int), `index_list` (list[int]), `p` (float) |
| L2 | **Gaussian noise** | Add independent `N(0, sigma_xy)` noise to each (x, y) and `N(0, sigma_z)` to z position, plus `N(0, sigma_intensity)` to the intensity channel. | `sigma_xy` (float, m, default 0.1), `sigma_z` (float, m, optional — defaults to sigma_xy), `sigma_intensity` (float, intensity units, default 0.0 — set > 0 to also corrupt intensity) |
| L3 | **Loss partial** | Remove a fraction of LiDAR points via Bernoulli sampling. Each point kept with probability `(1 - fraction)`. | `fraction` (float ∈ [0, 1], default 0.3) |
| L4 | **Loss complete** | Full LiDAR blackout. Sets `ldr64` → `None`. | (none) |

### 1.3 Camera — Multi-view RGB (4 effects)

| # | Name | Mechanism | Parameters |
|---|------|-----------|------------|
| C1 | **Frame deletion** | Skip entire camera frame. Same semantics as radar/LiDAR. When fired, all camera-image keys found in the dict_item are set to a zero-filled normalized tensor. | `mode` (str), `interval` (int), `index_list` (list[int]), `p` (float) |
| C2 | **Gaussian noise** | Additive `N(0, sigma)` per pixel per channel in normalized tensor space. | `sigma` (float, pixel value std in 0–255 units, default 10) |
| C3 | **Loss partial** | Zero out a single contiguous rectangular region covering approximately `fraction` of the image area. Region is randomly positioned. Distinct from multi-patch occlusion — this is the canonical "partial data loss" corruption. | `fraction` (float ∈ [0, 1], fraction of image area to zero, default 0.2) |
| C4 | **Loss complete** | Full image blackout. All camera keys replaced with a zero-filled normalized tensor (pixel values ≈ -mean/std). | (none) |

### 1.4 Design Decision: Loss Partial vs Loss Complete

**Decision: Distinct explicit effects.** `loss_complete` is a separate effect function, NOT `loss_partial(fraction=1.0)`.

Rationale:
1. **Semantic difference:** `loss_partial` models a stochastic data-loss process (each point/region has independent probability of being lost). `loss_complete` models a deterministic total sensor blackout. The two represent different failure modes for robustness testing.
2. **Camera mechanism divergence:** For camera, `loss_partial(fraction=0.3)` blacks out a region of the image (30% area). `loss_partial(fraction=1.0)` would need to black out the entire image, but the contiguous-region mechanism doesn't naturally extend to covering 100% of the image without being a qualitatively different operation (it would need to draw a region larger than the image). `loss_complete` is implemented as setting the entire tensor to zero — a distinct code path.
3. **Metadata clarity:** Downstream consumers (evaluation scripts, metrics, visualization) can distinguish "frame had a total sensor blackout" from "frame had extreme partial loss" by the effect name in the metadata. This matters for per-failure-mode analysis.
4. **Edge-case determinism:** `loss_partial(fraction=1.0)` on point clouds (LiDAR/radar) produces an empty array — which is the same as `loss_complete`. But `loss_complete` sets the key to `None` (allowing downstream `_has_key` to correctly report "this sensor has no data"), whereas `loss_partial` leaves an empty array `shape=(0, N)`. Using `None` vs empty array is a cleaner signal for downstream code.

---

## 2. Module Structure

### 2.1 File layout

```
datasets/effects/
    __init__.py             # exports NoiseInjector + config schema
    noise_injection.py      # NoiseInjector class + per-effect functions
    config.py               # EffectConfig dataclass schema
    test_noise_injection.py # Unit tests
```

### 2.2 Core class

```python
class NoiseInjector:
    """
    Standalone inference-time corruption module for K-Radar.
    Operates on post-__getitem__ dict_item; no dependency on cfg_effect.
    """
    def __init__(self, config: EffectConfig):
        self.config = config
        self.rng = np.random.default_rng(config.seed)
        # Resolve effect lists from config
        ...

    def should_skip(self, frame_index: int, modality: str) -> bool:
        """
        Pre-check for frame_deletion effects. Called by the eval script
        BEFORE fetching the frame to avoid wasted data loading.
        Returns True if this frame_index should be skipped for the
        given modality based on frame_deletion config.
        """
        ...

    def __call__(self, dict_item: dict, frame_index: int | None = None) -> dict:
        """
        Apply all configured corruptions to one sample's dict_item.
        Deterministic frame_deletion (interval / index_list) is driven
        solely by dict_item['meta']['idx'][modality], populated by the
        caller/dataset — NOT by this frame_index argument, which the
        effect functions do not read for that decision (see
        frame-deletion-rng-desync-fix-report.md, Discrepancy #1). This
        argument's only current effect is keying should_skip()'s decision
        cache so should_skip() and __call__() agree for the same frame.
        When frame_deletion fires, the affected sensor keys are set to
        None and subsequent effects skip them via _has_key().
        Order: radar -> LiDAR -> camera.
        """
        ...
        dict_item['meta']['noise_injection'] = self._metadata()
        return dict_item
```

### 2.3 Per-effect function signature

Each effect is a pure function:

```python
def effect_name(dict_item: dict, params: dict, rng: np.random.Generator) -> dict
```

The function modifies dict_item in-place and returns it. Effects that fire (probability gate passed) may set sensor keys to `None` (for deletion/blackout effects) or modify data in-place.

### 2.4 Config schema

Unchanged from Rev 1 — `EffectConfig` and `Effect` dataclasses remain the same. The `Effect.params` dict carries effect-specific parameters per the tables in §1.

### 2.5 Effect registries

```python
RADAR_EFFECTS: dict[str, Callable] = {
    'frame_deletion':       radar_frame_deletion,
    'noise_induced_shifts': radar_noise_induced_shifts,
    'loss_partial':         radar_loss_partial,
    'loss_complete':        radar_loss_complete,
}

LIDAR_EFFECTS: dict[str, Callable] = {
    'frame_deletion':       lidar_frame_deletion,
    'gaussian_noise':       lidar_gaussian_noise,
    'loss_partial':         lidar_loss_partial,
    'loss_complete':        lidar_loss_complete,
}

CAMERA_EFFECTS: dict[str, Callable] = {
    'frame_deletion':       camera_frame_deletion,
    'gaussian_noise':       camera_gaussian_noise,
    'loss_partial':         camera_loss_partial,
    'loss_complete':        camera_loss_complete,
}
```

Legacy effect registries (`RADAR_EFFECTS_LEGACY`, etc.) are maintained in the source file for backward compatibility but are NOT loaded into `ALL_EFFECTS` and NOT used by `NoiseInjector`.

---

## 3. Integration Points

Unchanged from Rev 1. The module is called as a post-processing step after `dataset.__getitem__()`. Only `scripts/main_fusion_eval_0.py` imports `NoiseInjector` (3–4 lines). Training pipeline (`pipelines/pipeline_detection_v1_0.py`) has zero references.

### Frame deletion integration

When frame_deletion is configured, the eval script SHOULD call `injector.should_skip(idx, modality)` before loading each frame to avoid wasted I/O. If `should_skip` is not called and the frame is loaded anyway, `__call__` handles it by setting sensor keys to `None` — the frame is still returned but the affected modality's data is empty.

---

## 4. Verification Plan

### 4.1 Per-effect verification

| Effect | How to verify | Acceptance |
|--------|---------------|------------|
| Frame deletion (deterministic) | `interval=10, frame_index=20` → sensor key set to `None` | Key is `None` |
| Frame deletion (random) | `p=1.0` → sensor key set to `None` | Key is `None` |
| Radar noise_induced_shifts | Compute position delta before/after; check `std(delta) ≈ shift_std` | Mean of `std(delta)` within 30% of `shift_std` |
| Loss partial (all modalities) | `fraction=0.5`, check point count ~50% of original | Count within ±5% of expected |
| Loss complete (all modalities) | Sensor key is `None` after effect | Key is `None` |
| LiDAR Gaussian noise | Std of position delta ≈ param | Within 30% of sigma_xy/sigma_z |
| Camera Gaussian noise | Std of pixel delta > 0 when sigma > 0 | Pixel std > 0 |
| Camera loss partial | Exactly one contiguous zeroed region found | 1 region detected; area ~ fraction × total |

### 4.2 Integration

- All 12 effects can be composed in any order via `EffectConfig`
- Frame deletion runs before other effects in _apply_list (pre-check) so deleted data is not unnecessarily processed
- Metadata injection works with all effect combinations

---

## 5. Relationship to existing code

| File | Existing role | New role | Conflict? |
|------|--------------|----------|-----------|
| `datasets/effects/` | All corruption logic | Same — taxonomy narrowed from 18 → 12 effects | No |
| `datasets/effects/noise_injection.py` | 18-effect implementation | 12-effect implementation + legacy section | No — backward-compatible via legacy registries |
| `datasets/kradar_fusion_v1_0_calib_change.py` | Inline camera/LiDAR effects (dead code) | Unchanged | No |
| `scripts/main_fusion_eval_0.py` | Eval script with dead effect block | Add `NoiseInjector` call | No |
| Training pipeline | — | Zero changes | No |