# Noise Injection Module — Inference-Time Robustness Testing

**Date:** 2026-07-21
**Status:** Design proposal (pre-implementation)
**Scope:** Standalone corruption/injection module for radar + LiDAR + camera at K-Radar evaluation time only.

---

## 1. Corruption Types by Modality

Each entry: short mechanism description, well-known sensor-corruption origin, and config parameters.

### 1.1 Radar — 4D Imaging Radar (7 types)

| # | Name | Mechanism | Origin / Standard | Parameters |
|---|------|-----------|------------------|------------|
| R1 | **Power Gaussian noise** | Additive Gaussian noise to per-bin power values (`rdr_sparse[:,3]` RCS, `rdr_polar_3d[0]` power plane, `pc100p` power channels). Noise is independent per bin. | Standard sensor-noise model — thermal noise in receiver chain. | `std` (float, noise sigma), `clip_min` (float, floor dB) |
| R2 | **Sparse-point dropout** | Randomly drop rows from `rdr_sparse` (the N×4 or N×5 point cloud) by Bernoulli sampling. Each point kept with probability `1 - rate`. Equivalent to reduced probability-of-detection. | Common radar detection dropout — target RCS below noise floor causes missed detections. | `rate` (float ∈ [0,1], fraction dropped) |
| R3 | **Range attenuation** | Scale power values by `exp(-alpha * (r - r0)+)` where `r` is range from sensor origin. Simulates increased path loss or atmospheric absorption beyond a range threshold. | Free-space path loss + atmospheric attenuation (ITU-R P.676). | `alpha` (float, dB/m), `r0` (float, start range in m) |
| R4 | **Doppler corruption** | Add noise to or zero out the doppler channel (`rdr_polar_3d[1]` or cube doppler plane). Simulates velocity ambiguity or micro-Doppler smearing. | Doppler ambiguity / micro-Doppler spread from vibration or rotation. | `mode` (enum: `gaussian`|`zero`|`mask`), `std` (float, gaussian sigma) |
| R5 | **Ghost point injection** | Inject N random false-positive radar points into `rdr_sparse`. Positions uniformly sampled from the sensor FOV; power values sampled from the observed power distribution. | Multipath reflections or sidelobe detections create phantom targets. | `num` (int, points per frame), `power_bounds` (tuple [min, max] dB) |
| R6 | **Azimuth/elevation jitter** | Add angular noise to point positions before Cartesian conversion (equivalent to perturbing `theta` in `rdr_polar_3d` bin assignment). Rotates each point around the sensor origin by `N(0, sigma_deg)` degrees. | Angle estimation noise from monopulse processing / beamwidth limits. | `sigma_deg` (float, angular std dev), `per_axis` (bool, independent azimuth/elevation) |
| R7 | **Power saturation / clipping** | Clamp power values above a configurable ceiling. Simulates ADC saturation near strong reflectors. | ADC saturation (common in close-range high-RCS targets). | `ceiling` (float, max dB), `floor` (float, min dB, default -inf) |

### 1.2 LiDAR — 64-beam Mechanical LiDAR (5 types)

| # | Name | Mechanism | Origin / Standard | Parameters |
|---|------|-----------|------------------|------------|
| L1 | **Random point dropout** | Uniform-random removal of N% of points from `ldr64` point cloud. Simulates reduced reflectivity or return loss. | Standard dropout — reduced surface reflectivity / incidence angle. | `rate` (float ∈ [0,1]) |
| L2 | **FOV occlusion (azimuth sector)** | Keep only points whose azimuth falls outside `[min_deg, max_deg]` (same mechanism as existing `missed` effect, now parameterized here). | Physical FOV blockage (vehicle body, debris, weather). | `min_deg`, `max_deg` (float, degrees), `invert` (bool, keep *inside* instead) |
| L3 | **Gaussian position noise** | Add independent `N(0, sigma)` noise to each (x,y,z) coordinate in `ldr64`. Simulates ranging jitter. | Standard range-measurement noise (time-of-flight jitter). | `sigma_xy` (float, m), `sigma_z` (float, m, optional — defaults to `sigma_xy`) |
| L4 | **Range-limited dropout** | Drop points outside `[r_min, r_max]`. Simulates minimum-range blind spot and maximum-range attenuation. | LiDAR minimum range / maximum unambiguous range. | `r_min` (float, m, default 0), `r_max` (float, m, default 200) |
| L5 | **Downsampling** | Keep every Nth point (uniform stride). Simulates reduced angular resolution (fewer beams or lower rotation rate). | Reduced beam count or angular resolution. | `stride` (int, keep every Nth point) |

### 1.3 Camera — Multi-view RGB (6 types)

| # | Name | Mechanism | Origin / Standard | Parameters |
|---|------|-----------|------------------|------------|
| C1 | **Gaussian noise** | Additive `N(0, sigma)` per pixel per channel. | Standard sensor read noise. | `sigma` (float, pixel value std, 0–255 range) |
| C2 | **Motion blur** | Convolve image with a directional box/gaussian kernel. Simulates camera motion during exposure. | Standard motion blur — camera platform vibration / ego-motion. | `kernel_size` (int, odd), `angle_deg` (float, blur direction), `intensity` (float, blur weight) |
| C3 | **Brightness adjustment** | Multiply all pixel values by `factor` and clip to [0, 255]. | Exposure variation / auto-exposure instability. | `factor` (float, multiplier), `per_channel` (bool, default false) |
| C4 | **Random patch occlusion** | Overlay N random rectangular patches (size `[h,w]`) filled with a fixed color or noise on the image. | Physical debris, raindrops on lens, sensor dead pixels. | `num_patches` (int), `max_size` (tuple [h,w] fraction of image), `fill` (enum: `black`|`white`|`mean`|`random`) |
| C5 | **JPEG compression** | Encode/decode through cv2 JPEG at a configurable quality level. | Standard compression artifacts in transmitted video. | `quality` (int, 1–100, lower = more artifacts) |
| C6 | **Histogram / gamma distortion** | Apply `gamma` correction (power-law). | Camera gamma / tone-mapping variation. | `gamma` (float, typical 0.5–2.0) |

**Note on existing camera crack/scratch overlay:** The existing overlay mechanism at L570–580 is replaced by the more general C4 (patch occlusion). If crack/scratch overlay is specifically desired it can be implemented as a special case of C4 with pre-defined mask patterns — but the existing PNG-based approach is skipped because the referenced files do not exist and reproducing them is scope creep.

**Note on existing LiDAR "missed" effect:** L2 subsumes the existing mechanism. The new module reimplements it rather than calling the existing inline code, so the dependency on `cfg_effect.lid.effect == 'missed'` string matching is eliminated.

---

## 2. Module Structure

### 2.1 File layout

```
datasets/effects/           # NEW standalone directory
    __init__.py             # exports NoiseInjector + config schema
    noise_injection.py      # NoiseInjector class + per-effect functions
    config.py               # EffectConfig dataclass schema
```

**Rationale for `datasets/effects/` over `utils/effects/`:** The module operates on the dict_item format produced by the dataset's `__getitem__()`, which is a data-pipeline concern. Colocating it under `datasets/` keeps the data-pipeline logic together and mirrors where `kradar_fusion_v1_0_calib_change.py` lives (which is the file that currently contains inline effect code).

### 2.2 Core class

```python
class NoiseInjector:
    """
    Standalone inference-time corruption module for K-Radar.
    Operates on post-__getitem__ dict_item; no dependency on cfg_effect.
    """
    def __init__(self, config: EffectConfig):
        """
        config: EffectConfig dataclass with per-modality effect lists.
        Sets up the per-effect random seeds and state machines.
        """
        self.config = config
        self.rng = np.random.default_rng(config.seed)

    def __call__(self, dict_item: dict) -> dict:
        """
        Apply all configured corruptions to one sample's dict_item.
        Called once per frame after dataset.__getitem__().
        Modifies dict_item in-place and returns it.
        Order: radar -> LiDAR -> camera (by increasing data size;
               camera last because images are largest and least disruptive
               to reorder if point-cloud effects change the point count).
        """
        if self.config.radar:
            dict_item = self._apply_radar(dict_item)
        if self.config.lidar:
            dict_item = self._apply_lidar(dict_item)
        if self.config.camera:
            dict_item = self._apply_camera(dict_item)
        # Tag the dict to record what was applied
        dict_item['meta']['noise_injection'] = self._metadata()
        return dict_item
```

### 2.3 Per-modality dispatch methods

```python
def _apply_radar(self, d: dict) -> dict:
    """Applies each configured radar effect in order. Each effect called
    only if its probability gate [0,1] < p(seed_draw)."""
    for eff in self.config.radar:
        if self.rng.uniform() < eff.p:
            d = eff.fn(d, eff.params, self.rng)
    return d

def _apply_lidar(self, d: dict) -> dict: ...
def _apply_camera(self, d: dict) -> dict: ...
```

Each effect is a pure function with signature:

```python
def gaussian_noise_radar(dict_item: dict, params: dict, rng: np.random.Generator) -> dict
def sparse_point_dropout(dict_item: dict, params: dict, rng: np.random.Generator) -> dict
# ... one function per effect listed in §1
```

### 2.4 Config schema (dataclass)

```python
@dataclass
class EffectConfig:
    """Top-level config for the noise injection module."""
    seed: int = 42           # Master seed; each effect derives a sub-seed
    radar: list[Effect] | None = None
    lidar: list[Effect] | None = None
    camera: list[Effect] | None = None

@dataclass
class Effect:
    """One effect instance (compositional — multiple per modality)."""
    name: str                # Effect name, e.g. 'power_gaussian_noise'
    p: float = 1.0           # Per-frame probability of applying this effect
    params: dict = field(default_factory=dict)  # Effect-specific parameters
```

**Composability:** Multiple Effect entries per modality — e.g. `radar=[Effect('power_gaussian_noise', p=0.8, params={'std': 0.1}), Effect('ghost_points', p=0.3, params={'num': 5})]` applies power noise on 80% of frames and ghost points on 30% of frames, independently per frame. If both fire on the same frame, they apply in list order.

### 2.5 Effect registry

A dict mapping effect name → function, loaded at module import time:

```python
RADAR_EFFECTS: dict[str, Callable] = {
    'power_gaussian_noise':     gaussian_noise_radar,
    'sparse_point_dropout':     sparse_point_dropout,
    'range_attenuation':        range_attenuation,
    'doppler_corruption':       doppler_corruption,
    'ghost_points':             ghost_points,
    'azimuth_jitter':           azimuth_jitter,
    'power_saturation':         power_saturation,
}
LIDAR_EFFECTS: dict[str, Callable] = { ... }
CAMERA_EFFECTS: dict[str, Callable] = { ... }
```

---

## 3. Bypass vs Fix Decision

### Decision: Bypass (Option b) — build an independent entry point

The new module is called **after** `dataset.__getitem__()` returns, as a post-processing wrapper. It does not depend on `cfg_effect`, `consider_effects`, `build_dataset`, or any of the four broken links in the existing chain.

### Three blockers + phantom class: how each is handled

| Blocker | Existing broken path | Bypass approach |
|---------|---------------------|-----------------|
| **#1** `build_dataset()` has no `**kwargs` (util_pipeline.py:56) | Cannot forward `cfg_effect` to dataset constructor | Not touched. The module gets data *after* the dataset produces it — no constructor injection needed. |
| **#2** Camera overlay PNGs don't exist (resources/imgs/) | `FileNotFoundError` on first camera frame | Not touched. Camera corruptions use procedural generation (C4 patches, C1 noise, C2 blur) — no external image assets. |
| **#3** `consider_effects = False` hardcoded (main_fusion_eval_0.py:75) | Dead code branch unreachable | Not touched. The eval script imports `NoiseInjector` directly and never touches the `consider_effects` / `cfg_effect` block. The old dead code can be left in place or pruned — it's inert either way. |
| **Phantom class** `KRadarFusion_v1_0_AffectedSensor` not in `__all__` | `KeyError` if ever reached | Not touched. The eval script uses `build_dataset(self, split='test')` with the standard dataset name from the config YAML — unaffected by the phantom string at line 39 (which is overridden when `build_dataset` resolves `p_pline.cfg.DATASET.NAME` from the yaml config, not line 39's override). |

### What IS touched: exactly one file

| File | Change |
|------|--------|
| `scripts/main_fusion_eval_0.py` | Add 3–4 lines: import `NoiseInjector`, construct it with a config dict, call it on each `dict_item` after `dataset[idx_frame]`. |

That is the **only** integration point in the entire main codebase. All corruption logic lives in `datasets/effects/`.

### Tradeoffs of the rejected option (fix the chain)

**Option (a) Fix the existing system** would require touching:

1. `utils/util_pipeline.py` — add `**kwargs` to `build_dataset()` signature and pass them to the constructor
2. `datasets/__init__.py` — register either `KRadarFusion_v1_0_CalibChange` or the phantom class name
3. `scripts/main_fusion_eval_0.py` — fix the class name string, flip `consider_effects = True`
4. `datasets/kradar_fusion_v1_0_calib_change.py` — add radar effect hooks inline in `get_rdr_sparse()`, `get_rdr_polar_3d()`, `get_rpcs()`
5. `resources/imgs/` — generate crack/scratch PNGs (or modify the code to skip missing files)

**Risks:**
- `build_dataset()` is used by the training pipeline (`pipeline_detection_v1_0.py:55-56`). Adding `**kwargs` to it is safe in Python (backward-compatible), but it creates a new code path through dataset construction that could interact with config loading. Every change to shared infrastructure carries regression risk to training.
- The eval script line 39 sets `self.cfg.DATASET.NAME = 'KRadarFusion_v1_0_AffectedSensor'` — if this is the *only* name the script works with and it doesn't match the real class, the eval script must change regardless. Once you're changing the eval script anyway, the bypass approach costs the same touch-point but with zero risk to training.
- Adding radar effects inline means scattering effect logic across 4 separate methods in a 1600+ line file, making the dataset harder to read and test.
- The existing mechanism lacks randomization, composition, and metadata-tagging — retrofitting those would require restructuring the inline code anyway.

**Verdict:** Bypass is lower risk (zero regression on training, zero regression on existing eval if the module is disabled), cleaner separation of concerns, and gives all three modalities first-class compositional support from day one.

---

## 4. Integration Points

### 4.1 Eval script — `scripts/main_fusion_eval_0.py`

The only file that changes. Approximate diffs:

```python
# === NEW: at top of file ===
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from datasets.effects.noise_injection import NoiseInjector
from datasets.effects.config import EffectConfig, Effect

# === NEW: inside ResultVis.__init__, after line 102 (end of cfg_effect dead block) ===
self.injector = NoiseInjector(EffectConfig(
    seed=42,
    radar=[
        Effect('power_gaussian_noise', p=0.8, params={'std': 0.05}),
    ],
    lidar=[
        Effect('random_dropout', p=1.0, params={'rate': 0.2}),
    ],
    camera=[
        Effect('gaussian_noise', p=0.5, params={'sigma': 10}),
        Effect('motion_blur', p=0.3, params={'kernel_size': 5, 'angle_deg': 45, 'intensity': 1.0}),
    ],
))

# === NEW: inside vis_objects() line 111, after `dict_item = dataset[idx_frame]` ===
dict_item = self.injector(dict_item)
```

That is the full extent of integration. The script's `collate_fn`, network forward pass, visualization code, and metric collection handle corrupted data identically to clean data (because the data shape does not change for most effect types — the exceptions, like dropout, reduce point count but the collate_fn already handles variable-length point clouds).

### 4.2 Training pipeline — `pipelines/pipeline_detection_v1_0.py`

**Zero changes.** The training script never imports or references `NoiseInjector`. The `build_dataset()` calls at lines 55–56 pass no corruption config. The dataset's `__getitem__` is unmodified. Training data is never corrupted.

### 4.3 Visualization script — `tools/asf_visualization/main_get_videos.py`

Optionally updated if visualization of corrupted data is desired. Same pattern: instantiate `NoiseInjector` and call on each `dict_item` after `__getitem__`. Not required for the core robustness-testing use case.

---

## 5. Verification Plan

### 5.1 Unit-level: per-effect function correctness

For each effect function in §1:

| Effect | How to verify | Acceptance |
|--------|---------------|------------|
| R1 Power Gaussian | Load a frame's `rdr_sparse`, apply effect with `std=0.5`, check `hist(new[:,3] - old[:,3])` approximates `N(0, 0.5)` | KS test p > 0.05 or visual histogram inspection |
| R2 Sparse-point dropout | `rate=0.5`, check `len(new_rdr) ≈ 0.5 * len(old_rdr)` | Within ±5% of expected count |
| R3 Range attenuation | Compute range of each point, confirm power decays beyond `r0` | Power at `r > r0` strictly lower than power at `r <= r0` for same RCS |
| R4 Doppler corruption | `mode='zero'` → check doppler channel is all zeros; `mode='gaussian'` → check noise added | Zero mode: `all(new_dop == 0)`. Gaussian: std matches param |
| R5 Ghost points | `num=10`, check `len(new_rdr) - len(old_rdr) == 10` (unless combined with dropout) | Point count delta matches `num` |
| R6 Azimuth jitter | Compute azimuth before/after, check distribution of delta approximates `N(0, sigma_deg)` | Std of angular delta within 10% of `sigma_deg` |
| R7 Power saturation | `ceiling=100`, check `all(new_power <= 100)` | All values ≤ ceiling |
| L1 Random dropout | `rate=0.3`, check point count | Within ±5% of expected |
| L2 FOV occlusion | `min_deg=-30, max_deg=30`, compute azimuth of all kept points | No point has azimuth in [-30, 30] degrees |
| L3 Position noise | `sigma_xy=0.1`, check `mean(norm(new_xyz - old_xyz)) ≈ 0.1*sqrt(3)` for 3D or `≈ 0.1*sqrt(2)` for xy-only | Mean error within 20% of expected |
| L4 Range dropout | `r_min=5, r_max=50`, check range of all kept points | All kept: `r ∈ [5, 50]` |
| L5 Downsampling | `stride=4`, check `len(new_ldr) ≈ len(old_ldr)/4` | Count within ±5% of expected |
| C1 Gaussian noise | Per-pixel diff vs original approximates `N(0, sigma)` | Mean pixel diff ≈ 0, std ≈ `sigma` |
| C2 Motion blur | Check image is visibly blurred (visual); check kernel applied correctly (unit test on known pattern) | Convolution produces expected output on test pattern |
| C3 Brightness | `factor=1.5`, check `mean(new_img) ≈ 1.5 * mean(old_img)` (within clipping tolerance) | Ratio within 5% before clipping |
| C4 Patch occlusion | `num_patches=3, fill='black'`, check N rectangular regions have all-zero pixel values | Exactly N zero blocks found |
| C5 JPEG | `quality=10`, check file-size-like metric differs from original | PSNR vs original < 30 dB |
| C6 Gamma | `gamma=2.0`, check power-law relationship | Mean reponse error < 5% |

### 5.2 Integration-level: bypass strategy works end-to-end

1. **Dry-run without injector:** Run `scripts/main_fusion_eval_0.py` with `injector` = identity pass-through. Confirm eval produces same results as current baseline (no regression).
2. **Dry-run with injector enabled but zero-corruption config** (all `p=0.0` or empty effect lists). Confirm numerical bit-exact output to the baseline for at least one frame.
3. **Run with one effect per modality at `p=1.0`:** Confirm the script completes without errors for the full sequence. Check output metrics differ from clean baseline.
4. **Phantom class avoidance:** Confirm the eval script never references `KRadarFusion_v1_0_AffectedSensor` — only the config YAML's dataset name is used via `build_dataset(self, split='test')` at line 105.

### 5.3 Regression: training pipeline is untouched

1. Confirm `pipelines/pipeline_detection_v1_0.py` has zero lines referencing `NoiseInjector`, `effects`, `cfg_effect`, or any file under `datasets/effects/`.
2. Confirm `utils/util_pipeline.py` `build_dataset()` is unmodified (still no `**kwargs`).
3. Run one training epoch on a single sequence (seq '10', 62 frames) with batch_size=1 to confirm no import error or data-path change.

### 5.4 Metadata verification

1. After injection, confirm `dict_item['meta']['noise_injection']` is a dict listing every effect that was drawn (name, parameter values, `p` threshold, seed sub-branch).
2. In the eval output log, print this metadata for each frame to allow per-sample audit.

---

## Appendix A: Effect ordering within a modality

Within each modality, effects are applied in the order listed in the `EffectConfig` list. The default order (and the recommended one) is:

**Radar:** R6 (jitter) → R7 (saturation) → R1 (power noise) → R4 (doppler) → R3 (attenuation) → R2 (dropout) → R5 (ghosts)

Rationale: geometrical perturbation first (jitter), then signal-domain changes (saturation, noise, doppler, attenuation), then structural changes (dropout removes points, ghosts adds them last so they survive).

**LiDAR:** L4 (range limit) → L2 (FOV occlusion) → L3 (position noise) → L1 (dropout) → L5 (downsample)

Rationale: clipping first (range, FOV), then noise, then subsampling.

**Camera:** C3 (brightness) → C6 (gamma) → C1 (noise) → C2 (blur) → C4 (occlusion) → C5 (JPEG)

Rationale: radiometric transforms first, then additive noise, then blur (which would smooth other artifacts), then structural patches, then compression.

---

## Appendix B: Relationship to existing code

| File | Existing role | New role | Conflict? |
|------|--------------|----------|-----------|
| `datasets/effects/` (NEW) | — | All corruption logic | No |
| `datasets/kradar_fusion_v1_0_calib_change.py` | Contains inline camera/LiDAR effects (dead code) | Unchanged; inline effects remain inert behind `cfg_effect` guard | No |
| `scripts/main_fusion_eval_0.py` | Eval script with dead effect block | Add `NoiseInjector` call (3 lines) | No |
| `utils/util_pipeline.py` | `build_dataset()` factory | Unchanged | No |
| `datasets/__init__.py` | Dataset registry | Unchanged | No |
| `pipelines/pipeline_detection_v1_0.py` | Training pipeline | Unchanged | No |
| `tools/asf_visualization/main_get_videos.py` | Visualization | Unchanged (optional later) | No |