# AI-MSF-Benchmark vs. K-Radar noise_injection.py — Direct Code Comparison

**Date:** 2026-07-29
**Scope:** Gaussian noise and loss-partial implementations only. No paper or other repo analysis.
**Source files compared:**
- AI-MSF-Benchmark: `corruption/operator/lidar_operator.py`, `corruption/operator/image_operator.py`
- K-Radar: `datasets/effects/noise_injection.py`

---

## 1. Gaussian Noise — LiDAR/Point Cloud

### AI-MSF-Benchmark

**File:** `corruption/operator/lidar_operator.py`, lines 37-42

```python
@staticmethod
def gaussian_noise(pointcloud, severity=1):
    N, C = pointcloud.shape
    c = [0.02, 0.04, 0.06, 0.08, 0.1][severity - 1]
    jitter = np.random.normal(size=(N, C)) * c
    new_pc = (pointcloud + jitter).astype('float32')
    return new_pc
```

**Data format:** (N, 4) float32 numpy array — KITTI velodyne format: `[x, y, z, reflectance]`.

### K-Radar

**File:** `datasets/effects/noise_injection.py`, lines 227-260 (`lidar_gaussian_noise`)

```python
def lidar_gaussian_noise(dict_item: dict, params: dict, rng: np.random.Generator) -> dict:
    sigma_xy = params.get("sigma_xy", 0.1)
    sigma_z = params.get("sigma_z", sigma_xy)
    sigma_intensity = params.get("sigma_intensity", 0.0)
    if _has_key(dict_item, "ldr64"):
        pc = dict_item["ldr64"]
        n = len(pc)
        noise_xy = rng.normal(0.0, sigma_xy, size=(n, 2))
        noise_z = rng.normal(0.0, sigma_z, size=n)
        pc[:, 0] += noise_xy[:, 0]
        pc[:, 1] += noise_xy[:, 1]
        pc[:, 2] += noise_z
        if sigma_intensity > 0.0 and pc.shape[1] >= 4:
            noise_intensity = rng.normal(0.0, sigma_intensity, size=n)
            pc[:, 3] += noise_intensity
    return dict_item
```

**Data format:** `dict_item['ldr64']` — (N, M) numpy where M >= 3: `[x, y, z, intensity, ring, ...]`. M is typically 5 (x,y,z,intensity,ring) for K-Radar lidar.

### Comparison Table — LiDAR Gaussian Noise

| Aspect | AI-MSF-Benchmark | K-Radar |
|---|---|---|
| Channels affected | ALL columns (x,y,z,reflectance) isotropically | Per-axis: x,y together, z separately, intensity optionally |
| Noise distribution | N(0, c) same std per channel | N(0, sigma_xy) on x,y; N(0, sigma_z) on z; N(0, sigma_intensity) on col 3 |
| Parameterization | Severity 1-5 maps to fixed std array; same std for all C columns | Named params `sigma_xy`, `sigma_z`, `sigma_intensity` (metres/unit); defaults: 0.1, same, 0.0 |
| Isotropic vs. per-axis | Isotropic (same sigma for ALL columns including reflectance) | Per-axis anisotropic — x/y vs z can differ; intensity noise is opt-in and independent |
| Clipping | None | None |
| Modality | LiDAR only (no radar operator) | LiDAR-specific function; radar gets `noise_induced_shifts` (position displacement) instead |
| Return style | Returns **new array** (does not mutate input) | Mutates **in-place** within dict_item, returns dict_item reference |
| Severity granularity | 5 discrete levels | Continuous via param dict |

---

## 2. Gaussian Noise — Camera/Image

### AI-MSF-Benchmark

**File:** `corruption/operator/image_operator.py`, lines 59-63

```python
@staticmethod
def gaussian_noise(image, severity=1):
    x = image.copy()
    c = [.08, .12, 0.18, 0.26, 0.38][severity - 1]
    x = np.array(x) / 255.
    return np.uint8(np.clip(x + np.random.normal(size=x.shape, scale=c), 0, 1) * 255)
```

**Data format:** (H, W, 3) uint8 numpy — standard RGB image plane (HWC).

### K-Radar

**File:** `datasets/effects/noise_injection.py`, lines 348-363 (`camera_gaussian_noise`)

```python
def camera_gaussian_noise(dict_item: dict, params: dict, rng: np.random.Generator) -> dict:
    sigma = params.get("sigma", 10.0)
    sigma_norm = sigma / 255.0 / 0.229  # approximate — using mean std across channels
    for k in _camera_keys(dict_item):
        img = dict_item[k]
        noise = torch.randn_like(img) * sigma_norm
        dict_item[k] = img + noise
    return dict_item
```

**Data format:** `dict_item['front0']` (or other camera key) — (3, H, W) **normalized torch.Tensor**. The image is already normalized by ImageNet mean/std (mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225]).

### Comparison Table — Camera Gaussian Noise

| Aspect | AI-MSF-Benchmark | K-Radar |
|---|---|---|
| Format | (H, W, 3) uint8 numpy | (3, H, W) normalized torch.Tensor |
| Normalization | [0,1] float (ephemeral, only during computation) | Normalized to ImageNet statistics (permanent, the tensor lives in this space) |
| Noise application | Per-pixel, per-channel, same std | Per-pixel, per-channel, same std |
| Parameterization | Severity 1-5: c ∈ [0.08, 0.12, 0.18, 0.26, 0.38] (in [0,1] pixel space) | sigma in [0,255] pixel space, converted via `sigma/255.0/0.229` |
| Clipping | Clip to [0,1] then *255 → uint8 | None (noise in normalized space can push values outside ImageNet range) |
| Channels | All 3 channels same sigma | All 3 channels same sigma |
| Dependency | numpy, skimage (for other ops) | torch only |

**⚠️ K-Radar's normalization conversion:**
`sigma_norm = sigma / 255.0 / 0.229` is approximate — it uses the ImageNet std of channel 0 (0.229) for all channels. The actual channel stds are [0.229, 0.224, 0.225], so the green/blue channels get a slightly different effective sigma. This is a minor inconsistency but probably negligible in practice.

---

## 3. Loss Partial — LiDAR/Point Cloud

### AI-MSF-Benchmark

**File:** `corruption/operator/lidar_operator.py`, lines 29-34

```python
@staticmethod
def loss_partial(pointcloud, severity=1):
    params = [0.1, 0.25, 0.5, 0.75, 0.9][severity - 1]
    N, C = pointcloud.shape
    index = np.random.permutation(N)[:int(N * params)]
    pointcloud[index] = [0, 0, 0, 0]
    return pointcloud
```

**Mechanism:** **ZEROES OUT** selected points in-place. Array shape (N, 4) is preserved — points are sent to the origin with zero reflectance. This is the critical distinction.

### K-Radar

**File:** `datasets/effects/noise_injection.py`, lines 176-194 (`radar_loss_partial`) and 263-278 (`lidar_loss_partial`)

```python
# Radar version (lines 176-194):
def radar_loss_partial(dict_item: dict, params: dict, rng: np.random.Generator) -> dict:
    fraction = params.get("fraction", 0.3)
    for key in ["rdr_sparse"]:
        if _has_key(dict_item, key):
            arr = dict_item[key]
            n = len(arr)
            keep = rng.uniform(size=n) >= fraction
            dict_item[key] = arr[keep]
    return dict_item

# LiDAR version (lines 263-278):
def lidar_loss_partial(dict_item: dict, params: dict, rng: np.random.Generator) -> dict:
    fraction = params.get("fraction", 0.3)
    if _has_key(dict_item, "ldr64"):
        n = len(dict_item["ldr64"])
        keep = rng.uniform(size=n) >= fraction
        dict_item["ldr64"] = dict_item["ldr64"][keep]
    return dict_item
```

**Mechanism:** **BERNOULLI REMOVAL** — each point is independently kept with probability `1-fraction`. Removed points are actually **deleted** from the array (boolean indexing). The array shrinks from N to ~N*(1-fraction).

### Comparison Table — LiDAR/Point Cloud Loss Partial

| Aspect | AI-MSF-Benchmark | K-Radar |
|---|---|---|
| Removal mechanism | **Zero-out** — sets selected rows to [0,0,0,0]; array shape preserved | **Bernoulli deletion** — removes rows via boolean indexing; array shrinks |
| Selection method | Random permutation → first `int(N*frac)` indices (deterministic count) | Independent Bernoulli per point (binomial count, variance ~ N*frac*(1-frac)) |
| Severity parameter | [0.1, 0.25, 0.5, 0.75, 0.9] (5 discrete levels) | Continuous `fraction` float (default 0.3) |
| Number of points dropped | Exactly `floor(N * fraction)` | Stochastic — average `N * fraction`, but actual count varies |
| Data format | (N, 4) KITTI velodyne — [x,y,z,reflectance] | `rdr_sparse`: (N, 4+) [x,y,z,power,...]; `ldr64`: (N, M) [x,y,z,intensity,ring,...] |
| Mutability | Mutates input, returns same array object | Creates new array via boolean indexing (new memory allocation) |
| Applicable modalities | LiDAR only in AI-MSF-Benchmark | Radar (`rdr_sparse`) and LiDAR (`ldr64`) independently |
| RNG source | `np.random` global state | Deterministic sub-generator from master `np.random.Generator` |

### Critical Functional Difference — Zero-out vs. Deletion

This is the most important finding in this report. The two mechanisms produce qualitatively different corrupted data:

1. **Zero-out (AI-MSF-Benchmark):** Points at (0,0,0) will be:
   - Filtered out by any range-gating preprocessor (typical threshold: `r > epsilon`)
   - Collapsed into the sensor origin — creates spurious "returns" at the sensor location
   - Merged into the first voxel by voxelization (if voxel size > 0) — polluting the origin voxel with N/fraction points
   - Treated as a sensor-self return by BEVFusion-style BEV encoders

2. **Deletion (K-Radar):** Points are simply gone — no spurious geometry introduced.
   - Batch padding may need to be handled downstream (variable-size point clouds)
   - Number of points per frame changes, which some models handle better than others
   - No sensor-origin artifacts

**Bottom line:** These are NOT drop-in replacements. Porting AI-MSF-Benchmark's zero-out approach to K-Radar would require different downstream handling and produces different evaluation results.

---

## 4. Loss Partial — Camera/Image

### AI-MSF-Benchmark

**File:** `corruption/operator/image_operator.py`, lines 126-134

```python
@staticmethod
def loss_partial(image, severity=1):
    params = [0.1, 0.25, 0.5, 0.75, 0.9][severity - 1]
    img_shape = image.shape
    arr = image.copy().flatten()
    loss_num = int(len(arr) * params)
    index = np.random.permutation(len(arr))[:loss_num]
    arr[index] = 0
    image = arr.reshape(img_shape).astype("uint8")
    return image
```

**Mechanism:** Per-pixel dropout. Flattens the entire image (all channels), selects `floor(N * fraction)` random pixels (by linear index), sets them to zero. This is salt-and-pepper style dropout at pixel granularity, NOT a contiguous region.

### K-Radar

**File:** `datasets/effects/noise_injection.py`, lines 366-417 (`camera_loss_partial`)

```python
def camera_loss_partial(dict_item: dict, params: dict, rng: np.random.Generator) -> dict:
    fraction = params.get("fraction", 0.2)
    ...
    for k in _camera_keys(dict_item):
        img_np = _to_nhwc(dict_item[k])  # (H, W, 3) uint8
        H, W = img_np.shape[:2]
        target_area = fraction * H * W
        side = int(np.sqrt(target_area))
        ph = min(max(1, side), H)
        pw = min(max(1, side), W)
        ...
        y0 = rng.integers(0, H - ph + 1) if H > ph else 0
        x0 = rng.integers(0, W - pw + 1) if W > pw else 0
        img_np[y0: y0 + ph, x0: x0 + pw] = 0
        dict_item[k] = _from_nhwc(img_np)
    return dict_item
```

**Mechanism:** Single rectangular region zero-out. Computes a square-ish region covering approximately `fraction` of the image area, positions it randomly, and zeros out that contiguous block.

### Comparison Table — Camera Loss Partial

| Aspect | AI-MSF-Benchmark | K-Radar |
|---|---|---|
| Mechanism | **Per-pixel dropout** — random individual pixels set to 0 | **Rectangular occlusion** — single contiguous region zeroed out |
| Spatial structure | Salt-and-pepper (independent pixel loss) | Block occlusion (structured missing region) |
| Fraction semantics | `fraction` of total pixels individually dropped | `fraction` of image area covered by one rectangle |
| Determinism | Exactly `floor(N * fraction)` pixels dropped (permutation-based) | Approximate area (region size adjusted to hit target fraction) |
| Data format | (H, W, 3) uint8 numpy (HWC) | (3, H, W) normalized torch.Tensor → converted to (H,W,3) uint8 → back |
| Round-trip | No conversion needed | Round-trips through `_to_nhwc` → `_from_nhwc` (numpy ↔ torch, pixel ↔ normalized) |

**These are fundamentally different corruptions** — per-pixel dropout and block occlusion affect different spatial frequency bands and test different failure modes.

---

## 5. Summary Table — All 4 Variants

| Corruption | Modality | AI-MSF-Benchmark Mechanism | K-Radar Mechanism | Drop-in? |
|---|---|---|---|---|
| Gaussian noise | LiDAR | Isotropic N(0,c) on ALL 4 channels; (N,4) KITTI; returns new array | Per-axis: xy vs z vs intensity; (N,M) dict_item; in-place mutation | **No** (different channels, different params, different data format) |
| Gaussian noise | Camera | (H,W,3) uint8; N(0,c) in [0,1]; clipped | (3,H,W) torch normalized; sigma in pixel space converted; no clipping | **No** (different tensor format, normalization path) |
| Loss partial | LiDAR | Zero-out selected rows to [0,0,0,0]; shape preserved | Bernoulli deletion (remove rows); shape shrinks | **No** (opposite semantics for downstream models) |
| Loss partial | Camera | Per-pixel dropout flattened; salt-and-pepper | Single rectangular occlusion; contiguous block | **No** (completely different corruption structure) |

---

## 6. AI-MSF-Benchmark's Image Loss Partial — Important Note on Semantics

AI-MSF-Benchmark's `ImageOperator.loss_partial` does **not** operate as a spatial occlusion. It flattens the 3D (H,W,3) array into 1D, randomly selects pixels by linear index, and zeros them. This means the three color channels of a given pixel are NOT zeroed together — a pixel at (y, x) may have only its R channel zeroed while G and B remain intact, because the flattening interleaves channels.

Contrast this with K-Radar's `camera_loss_partial`, which zeros a **contiguous (H, W, 3) sub-volume** — all three channels of each pixel in the region are set to black. This is a physically plausible occlusion. AI-MSF-Benchmark's per-pixel dropout is an unlikely real-world corruption for cameras (more like salt-and-pepper sensor noise).

---

## 7. Portability Assessment

### What would need to change to port AI-MSF-Benchmark's loss_partial into K-Radar's noise_injection.py

#### For LiDAR (`lidar_loss_partial`):

1. **Mechanism change** — K-Radar currently uses Bernoulli deletion. To match AI-MSF-Benchmark's zero-out:
   - Replace `keep = rng.uniform(size=n) >= fraction` / `arr[keep]` with `index = rng.permutation(N)[:int(N*frac)]` / `arr[index] = 0`
   - Array shape is preserved (no size reduction downstream)

2. **Selection determinism** — AI-MSF-Benchmark uses permutation (exact count), K-Radar uses Bernoulli (stochastic count). Porting would switch from binomial to exact count.

3. **Data format** — AI-MSF-Benchmark assumes exactly (N, 4) (KITTI velodyne). K-Radar's `ldr64` can have more columns (5+), and `rdr_sparse` can have 4+ or 5+ columns. The zero-out `[0, 0, 0, 0]` hardcodes 4 columns — need to generalize to `np.zeros(C)` where C = `pointcloud.shape[1]`.

4. **RNG** — AI-MSF-Benchmark uses global `np.random`. K-Radar uses deterministic sub-generators from a master `np.random.Generator` — easy to adapt (already uses `rng.permutation()` pattern elsewhere).

5. **Severity** — AI-MSF-Benchmark uses 5 discrete levels. K-Radar uses continuous `fraction`. Keep continuous for flexibility, or offer both.

#### For Camera (`camera_loss_partial`):

Porting is **not recommended** — the mechanisms are semantically different. AI-MSF-Benchmark's per-pixel dropout on flattened array is an unusual corruption for cameras. If you must port:

1. Replace region logic with flat array permutation
2. Operate on `_to_nhwc()` output (uint8 HWC) — like AI-MSF-Benchmark does
3. Return via `_from_nhwc()` — already in K-Radar's toolchain
4. But note: per-pixel dropout breaks the color channel correlation (R/G/B of the same pixel may not all be zeroed together)

#### For Radar:

AI-MSF-Benchmark has **no radar operator** at all. No porting is possible.

### Dependencies

| Dependency | AI-MSF-Benchmark | K-Radar | Porting Concern |
|---|---|---|---|
| numpy | ✓ (global RNG) | ✓ (Generator RNG) | None — both use numpy, just RNG style differs |
| torch | ✗ | ✓ | AI-MSF-Benchmark camera ops work on numpy; K-Radar camera ops work on torch tensors |
| opencv-python | ✓ (image ops) | ✓ (already imported) | None — K-Radar already uses cv2 |
| skimage | ✓ (image ops) | ✗ | K-Radar doesn't use skimage for camera noise/loss ops — not needed for these specific functions |
| wand | ✓ (motion_blur only) | ✗ | Not needed for gaussian_noise or loss_partial |
| natsort, tqdm, fire | ✓ (simulation infra) | ✗ | Not needed — these are CLI/pipeline tools, not core to the noise functions |

### Verdict

**Demand 2 (replace K-Radar's loss_partial with AI-MSF-Benchmark's version) must be carefully reconsidered.** The two implementations produce meaningfully different corruptions:

- Zero-out (AI-MSF-Benchmark) sends points to (0,0,0,0), creating sensor-origin artifacts that most models will filter out differently than missing points.
- Deletion (K-Radar) simply removes points, changing the point count and requiring downstream batch-handling logic.

If the goal is to reproduce AI-MSF-Benchmark's evaluation protocol on K-Radar data, you need the **zero-out** approach. If the goal is a more physically realistic partial sensor failure, the **deletion** approach is arguably better (a real sensor dropout drops returns, it doesn't move them to the origin).

**Recommendation:** Add zero-out as a separate parameterized mode (`mode='zero'`) in the existing loss_partial functions, rather than replacing the current implementation. This preserves compatibility with existing experiments while enabling AI-MSF-Benchmark-compatible evaluation.