# K-Radar Sensor Effects System — Audit

**Date:** 2026-07-20
**Scope:** `kradar_fusion_v1_0_calib_change.py` and supporting infrastructure
**Context:** Inference-time robustness testing only — not used during training.

---

## 1. Verified Starting Points

All four claimed locations were verified against the live codebase at commit state 2026-07-20 with line numbers that match exactly. No drift from the reported positions.

### 1a. Camera crack/scratch overlay — `get_camera_img()` (line 570-580)

**File:** `datasets/kradar_fusion_v1_0_calib_change.py`

```python
# L570-L580
if self.cfg_effect is not None:
    if self.cfg_effect.cam.effect is not None:
        img_effect = Image.open(self.cfg_effect.cam.path_cropped.get(self.cfg_effect.cam.effect))
        img_np = np.array(img)
        img_effect_np = np.array(img_effect)
        thr = self.cfg_effect.cam.thr
        img_np[img_effect_np>thr] = img_effect_np[img_effect_np>thr]
        img = Image.fromarray(img_np)
        img_np = None
        img_effect_np = None
        img_effect = None
```

**Mechanism:** An overlay image (crack or scratch PNG) is loaded, converted to numpy, and its pixel values are alpha-blended by threshold. Pixels in the base image where `overlay > thr` are replaced by the corresponding overlay pixel. `thr` defaults to 100 (grayscale threshold — the overlay images appear to be grayscale/binary masks with artifacts).

**Important:** The effect images referenced by `cfg_effect.cam.path_cropped` (e.g. `./resources/imgs/img_crack_cropped.png`) DO NOT EXIST in the repo at `resources/imgs/`. That directory contains only example/screenshot PNGs. The camera effect will raise `FileNotFoundError` if activated.

**Order in `__getitem__`:** Applied inside `get_camera_img()` which is called at step 5 of the `__getitem__` pipeline. Only affects `img_load==0` (cropped images) — the `img_load==1` (undistorted) and `img_load==2` (raw cv2) code paths have no effect hooks.

### 1b. LiDAR FOV occlusion "missed" — `get_ldr64()` (line 775-784)

**File:** `datasets/kradar_fusion_v1_0_calib_change.py`

```python
# L775-L784
if self.cfg_effect is not None:
    if self.cfg_effect.lid.effect == 'missed':
        deg2rad = np.pi/180.
        min_angle, max_angle = self.cfg_effect.lid.angle
        min_rad = min_angle*deg2rad
        max_rad = max_angle*deg2rad
        azi_lidar = np.arctan2(pc_lidar[:,1],pc_lidar[:,0])
        ind_valid = np.where(((azi_lidar<min_rad) & (azi_lidar>-np.pi)) | \
                                ((azi_lidar>max_rad) & (azi_lidar<np.pi)))[0]
        pc_lidar = pc_lidar[ind_valid,:]
```

**Mechanism:** Computes azimuth for each LiDAR point via `arctan2(y, x)`, then keeps only points OUTSIDE the `[min_angle, max_angle]` sector. Points whose azimuth falls in the configurable angular gap (default `[-10, 53]` degrees) are dropped entirely — this simulates a sensor that "misses" that FOV region.

**Important:** Applied AFTER calibration offset addition (line 770-773) and BEFORE the `cfg_calib_change` translation/rotation block (line 786-804). This order matters: calibration brings points into radar-ref frame, then occlusion removes some, then calibration-change shifts/rotates the survivors.

### 1c. `consider_effects` flag — `scripts/main_fusion_eval_0.py` line ~75 and `tools/asf_visualization/main_get_videos.py` line ~65

**File:** `scripts/main_fusion_eval_0.py` (line 75)

```python
# L75-L102
consider_effects = False
if not consider_effects:
    self.cfg_effect = None
else:
    self.cfg_effect = dict(
        cam = dict(
            path_ori = dict(
                crack = './resources/imgs/img_crack.png',
                light_scratch = './resources/imgs/img_light_scratch.png',
                severe_scratch = './resources/imgs/img_severe_scratch.png',
            ),
            path_cropped = dict(
                crack = './resources/imgs/img_crack_cropped.png',
                light_scratch = './resources/imgs/img_light_scratch_cropped.png',
                severe_scratch = './resources/imgs/img_severe_scratch_cropped.png',
            ),
            effect='crack',
            thr=100,
        ),
        lid = dict(
            effect='missed',
            angle=[-10,53], # [deg]
        ),
        rad = dict(
            effect=None,
            angle=[]
        ),
    )
```

Both scripts (`main_fusion_eval_0.py` and `main_get_videos.py`) have the same pattern: hardcoded `consider_effects = False`, and `self.cfg_effect = None` is the only live path. The effect dict is dead code.

### 1d. `cfg_effect` dict structure

The dict has three top-level keys:

| Key   | Sub-keys                 | Status        |
|-------|--------------------------|---------------|
| `cam` | `effect`, `thr`, `path_ori`, `path_cropped` | Implemented via threshold overlay |
| `lid` | `effect`, `angle`        | Implemented via azimuth masking  |
| `rad` | `effect`, `angle`        | **Placeholder only** — `effect=None`, no code reads `cfg_effect.rad` anywhere |

---

## 2. Full Execution Flow

### 2a. `build_dataset()` — the factory

**File:** `utils/util_pipeline.py` (line 56)

```python
def build_dataset(p_pline, split='train'):
    return datasets.__all__[p_pline.cfg.DATASET.NAME](cfg = p_pline.cfg, split=split)
```

**Critical finding:** `build_dataset()` does NOT accept `**kwargs`. Passing `cfg_effect=self.cfg_effect` as a keyword argument (as the visualization scripts do at line 105-106) will raise `TypeError: build_dataset() got an unexpected keyword argument 'cfg_effect'`. The effect system is **not activatable through the standard `build_dataset()` factory**.

The only way to activate effects is to construct `KRadarFusion_v1_0_CalibChange` directly and pass `cfg_effect` via `**kwargs`, which is what the raw constructor handles:

```python
# datasets/kradar_fusion_v1_0_calib_change.py line 248-250
self.cfg_effect = kwargs.get('cfg_effect', None)
if self.cfg_effect is not None:
    self.cfg_effect = EasyDict(self.cfg_effect)
```

### 2b. `__init__` (line 86)

The `__init__` stores `cfg_effect` as `EasyDict(self.cfg_effect)` (line 250). It also stores `cfg_calib_change` at line 252-254. Neither affects dataset metadata loading, split selection, label loading, or physical value computation.

### 2c. `__getitem__` (line 1144)

Order of operations (effects in **bold**):

```
Step  1. get_label(dict_item)                         — parses label files, no effects
Step  2. get_ldr64(dict_item)                         — loads LiDAR point cloud
           -> **LiDAR FOV occlusion effect** applied here (lines 775-784)
Step  3. get_rdr_polar_3d(dict_item)                  — loads radar polar cube (no effect)
Step  4. get_rdr_sparse(dict_item)                    — loads radar sparse points (no effect)
Step  5. get_camera_img(dict_item)                    — loads camera images
           -> **Camera crack/scratch overlay effect** applied here (lines 570-580)
Step  6. get_rpcs(dict_item)                          — loads radar point clouds (no effect)
Step  7. filter_roi(dict_item)                        — spatial ROI filter
Step  8. get_description(dict_item)                   — metadata enrichment
Step  9. get_depth_labels(dict_item)                  — depth label loading
Step 10. get_obj_mask(dict_item)                      — object mask loading
```

**Key observation:** Radar data (steps 3, 4, 6) has NO effect hook anywhere in this pipeline.

### 2d. `collate_fn()` (line 1244)

Two versions (`v2_0` and `v2_1`). Both handle `rdr_sparse`, `ldr64`, and `pc100p`/`pc*` as sparse point keys. The collate function does:
- Extracts labels and GT boxes from `meta`
- Converts sparse point clouds to batched tensors with batch indices
- Optionally shuffles points (controlled by `shuffle_points` config, default `False`)
- Stacks camera intrinsics/extrinsics from `dict_t_params`
- Produces `dict_batch` with keys: `camera_imgs`, `ldr64`, `rdr_sparse`, `gt_boxes`, `label`, etc.

**Effects are invisible to collate** — they've already been baked into the sensor data in `__getitem__`. The collate function sees only the already-corrupted data.

### 2e. Model input

The model (`build_network()` call in the pipeline or eval script) receives `dict_batch` from `collate_fn`. It reads:
- `dict_batch['camera_imgs']` — already overlaid with crack/scratch if effect active
- `dict_batch['ldr64']` — already missing points in the occluded azimuth range
- `dict_batch['rdr_sparse']` — **never modified by effects**
- `dict_batch['pc100p']` / other radar PC keys — **never modified**

---

## 3. Implementation Status by Modality

### Camera — ✅ Fully implemented

| Aspect | Detail |
|--------|--------|
| **Mechanism** | Pixel-level threshold compositing of overlay PNG onto cropped camera image |
| **Effect types** | `crack`, `light_scratch`, `severe_scratch` (by image selection) |
| **Configured via** | `cfg_effect.cam.effect` (string key into `path_cropped` dict) |
| **Parameter** | `cfg_effect.cam.thr` (integer threshold, default 100) |
| **Code location** | `get_camera_img()` lines 570-580 |
| **Blocking issue** | Effect images do not exist in `resources/imgs/` — would crash with `FileNotFoundError` |
| **Only affects** `img_load==0` | Cropped image path only — undistorted and raw cv2 paths have no effect hook |

### LiDAR — ✅ Fully implemented

| Aspect | Detail |
|--------|--------|
| **Mechanism** | Azimuth-based point removal outside a configurable angular sector |
| **Effect type** | `missed` only (hardcoded string comparison) |
| **Configured via** | `cfg_effect.lid.effect` (must equal `'missed'`) |
| **Parameters** | `cfg_effect.lid.angle = [min_deg, max_deg]` |
| **Code location** | `get_ldr64()` lines 775-784 |
| **Applied after** | Calibration translation (line 773) |
| **Applied before** | `cfg_calib_change` rotation/translation (line 786) |

### Radar — ❌ Not implemented

| Aspect | Detail |
|--------|--------|
| **Status** | `rad.effect` is always `None` in all reference scripts |
| **Code** | No file in the repo reads `cfg_effect.rad` — zero lines of effect logic exists |
| **`get_rdr_sparse()`** (line 945) | Loads `.npy` file, returns immediately — no effect hook |
| **`get_rdr_polar_3d()`** (line 992) | Loads `.npy` or computes from tesseract — no effect hook |
| **`get_rpcs()`** (line 1109) | Loads radial PC files — no effect hook |
| **`get_cube_polar()`** (line 878) | Derives power/Doppler cubes — no effect hook |

---

## 4. Randomization / Probability / Composability

### Deterministic — no randomness

There is **zero** randomization or probability logic in the effect system:

- **No stochastic application:** Effects are applied with 100% probability when `cfg_effect` is not `None`. There is no roll, no `np.random`, no `random.random()` gate.
- **No effect selection randomness:** The effect type is hardcoded per-sensor in `cfg_effect.cam.effect` and `cfg_effect.lid.effect`. There is no random pick from a pool.
- **No parameter randomization:** `thr` and `angle` are static config values. No jitter, no distribution sampling.
- **Per-sensor singleton only:** Each sensor can only have one active effect at a time. `cam.effect` is a single string key; `lid.effect` is a single string. There is no composition (e.g. no way to apply both a crack AND a scratch to the same image, or both FOV occlusion AND point jitter to LiDAR).

### No effect batch diversity

Because `cfg_effect` is set once at dataset construction time and shared by all samples, every frame in the dataset gets exactly the same corruption. There is no per-frame or per-batch randomization.

---

## 5. Files Required to Touch for a New Radar Effect

Assuming the pattern established by camera/LiDAR (effect applied inside the sensor's `get_*` method based on `cfg_effect`), adding a radar corruption requires changes in:

### Required (always)

| # | File | What to change |
|---|------|----------------|
| 1 | `datasets/kradar_fusion_v1_0_calib_change.py` | **Add effect code** to `get_rdr_sparse()` (line 945) and/or `get_rdr_polar_3d()` (line 992) after the data loading section. Pattern: guard `if self.cfg_effect is not None and self.cfg_effect.rad.effect == '<your_effect>':` then modify `dict_item['rdr_sparse']` / `dict_item['rdr_polar_3d']` / `dict_item['pc100p']` in place. If the effect needs to run after multiple radar data sources are loaded, add a new dedicated method (e.g. `apply_rdr_effect()`) and call it from `__getitem__` after steps 3,4,6 but before step 7 (ROI filter). |
| 2 | `scripts/main_fusion_eval_0.py` (or the eval entry point) | Set `cfg_effect.rad.effect` to a non-None string, add any effect-specific parameters. |
| 3 | (Optional but recommended) `utils/util_pipeline.py` | Update `build_dataset()` to accept `**kwargs` and pass them to the constructor. Otherwise the effect is only activatable via direct constructor calls. |

### Required if using `build_dataset()` factory

| # | File | What to change |
|---|------|----------------|
| 4 | `datasets/__init__.py` | Add `KRadarFusion_v1_0_CalibChange` to `__all__` dict with a name string (e.g. `'KRadarFusion_v1_0_CalibChange'`). Currently it is NOT registered, so `build_dataset()` cannot instantiate it. |
| 5 | `utils/util_pipeline.py` | `build_dataset()` needs to accept `**kwargs` and pass them: `datasets.__all__[name](cfg=p_pline.cfg, split=split, **kwargs)` |

### Not required (no training path changes)

- `pipelines/pipeline_detection_v1_0.py` — training pipeline calls `build_dataset(self, split='train')` with no effect kwargs. No changes needed — the new radar effect code is behind `if self.cfg_effect is not None` guards, so it's a no-op during training.
- Config YAML files — unless you want to drive effects from config rather than programmatic dicts.

---

## 6. Additional Findings

### 6a. `KRadarFusion_v1_0_AffectedSensor` is a phantom class

`scripts/main_fusion_eval_0.py` sets:
```python
self.cfg.DATASET.NAME = 'KRadarFusion_v1_0_AffectedSensor'
```

This class name does not exist in `datasets/__init__.py`'s `__all__` dict. If `build_dataset()` were called with this name (and if `build_dataset` actually worked with a `cfg_effect` kwarg), it would raise a `KeyError`. The script works in practice because `consider_effects` is hardcoded to `False`, so this line is never reached meaningfully.

### 6b. Only `KRadarFusion_v1_0_CalibChange` has effects code

No other dataset class in the repo (`KRadarDetection_v1_0`, `KRadarFusion_v1_0`, etc.) contains `cfg_effect` handling. Effects are exclusively in `kradar_fusion_v1_0_calib_change.py`.

### 6c. The effects system is dead code

Because:
1. `build_dataset()` doesn't forward `cfg_effect` kwargs
2. The effect images don't exist on disk
3. The dataset class name in the eval script doesn't match the registry
4. `consider_effects=False` is hardcoded in both reference scripts

The effect system has never been executed (or if it was, it was manually constructed outside `build_dataset`).

### 6d. Camera effect only works on `img_load==0` (cropped)

The `img_load==1` (undistorted) and `img_load==2` (raw) code paths in `get_camera_img()` bypass the effect block entirely. If the dataset config uses a non-cropped image source, setting a camera effect has no visible effect.

### 6e. No effect metadata is preserved

Once effects are applied, there is no flag, tensor, or key in `dict_item` or `dict_batch` indicating that corruption was applied. Downstream evaluation code cannot distinguish corrupted from clean samples without external bookkeeping.

### 6f. The LiDAR effect is hardcoded to `'missed'`

```python
if self.cfg_effect.lid.effect == 'missed':
```

Only the string `'missed'` is handled. Any other value is silently ignored. There is no `else` or `else`-`if` chain for other LiDAR effect types.