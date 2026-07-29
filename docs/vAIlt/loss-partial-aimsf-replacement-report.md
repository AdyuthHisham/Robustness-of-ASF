# AI-MSF-Benchmark Loss Partial Replacement Report

**Date:** 2026-07-29
**Scope:** Full replacement of K-Radar's `radar_loss_partial`, `lidar_loss_partial`, `camera_loss_partial` with AI-MSF-Benchmark's zero-out mechanism.
**Source:** `datasets/effects/noise_injection.py`
**Verified findings doc:** `docs/vAIlt/aimsf-benchmark-comparison.md`

---

## 1. Summary

All three loss_partial implementations were ported from Bernoulli deletion / rectangular block-occlusion to exact-count permutation selection with zero-out. The new mechanism is:

- **LiDAR:** Direct port from `corruption/operator/lidar_operator.py:29-34`
- **Camera:** Direct port from `corruption/operator/image_operator.py:126-134`
- **Radar:** Extrapolated from AI-MSF-Benchmark's LiDAR mechanism (no radar source exists)

---

## 2. Mechanism Comparison

### 2.1 LiDAR (`lidar_loss_partial`)

| Aspect | Old (Bernoulli Deletion) | New (AI-MSF-Benchmark Zero-Out) |
|--------|--------------------------|----------------------------------|
| Selection | `rng.uniform(size=n) >= fraction` (Bernoulli, stochastic count) | `rng.permutation(n)[:int(n * fraction)]` (exact count) |
| Action | Boolean indexing removes rows: `arr[keep]` | Zeroes selected rows: `arr[index] = 0` |
| Row count | Changes (shrinks) | Preserved |
| Zero value | `np.zeros(C)` generalized (C = arr.shape[1]) | Same — already correct |
| RNG | `rng.uniform()` | `rng.permutation()` |

**Code diff (key lines):**

Old:
```python
keep = rng.uniform(size=n) >= fraction
dict_item["ldr64"] = dict_item["ldr64"][keep]
```

New:
```python
loss_num = int(n * fraction)
index = rng.permutation(n)[:loss_num]
arr[index] = np.zeros(c, dtype=arr.dtype)
```

### 2.2 Radar (`radar_loss_partial`)

Same change as LiDAR, with explicit in-code comment:

> NOTE: AI-MSF-Benchmark does not define a radar operator. This implementation
> extrapolates the same zero-out-via-permutation principle used by
> AI-MSF-Benchmark's LiDAR operator onto radar's column format. Not a direct port.

### 2.3 Camera (`camera_loss_partial`)

| Aspect | Old (Rectangular Occlusion) | New (Flatten-Permute-Zero) |
|--------|------------------------------|----------------------------|
| Spatial structure | Single contiguous rectangular region | Salt-and-pepper per-pixel dropout |
| Selection | `rng.integers(y0, y0+ph, x0, x0+pw)` within (H,W) bounds | `rng.permutation(H*W*3)[:int(H*W*3*fraction)]` on flattened array |
| Channel coupling | All 3 channels of each pixel in region zeroed together | Individual scalar zeroing — R/G/B of same pixel can drop independently |
| fraction clipping | `fraction >= 1.0` → clipped to 0.99 (area sqrt degeneracy) | No clipping — flatten-permute works cleanly at all fractions |
| Shape | Preserved | Preserved |

**Code diff (key lines):**

Old:
```python
target_area = fraction * H * W
side = int(np.sqrt(target_area))
ph = min(max(1, side), H)
pw = min(max(1, side), W)
...
img_np[y0: y0 + ph, x0: x0 + pw] = 0
```

New:
```python
flat = img_np.flatten()
n_total = len(flat)
loss_num = int(n_total * fraction)
index = rng.permutation(n_total)[:loss_num]
flat[index] = 0
dict_item[k] = _from_nhwc(flat.reshape(shape))
```

---

## 3. Preserved Properties

### 3.1 Camera cross-channel dropout (confirmed from AI-MSF-Benchmark source)

The new `camera_loss_partial` flattens the full `(H, W, 3)` array before selecting indices, meaning individual colour channels of the same pixel can be dropped independently (R zeroed, G/B intact). This is a **confirmed property of the source mechanism** (`image_operator.py:126-134`) and is explicitly preserved — not "fixed" during porting.

The test `test_camera_loss_partial_cross_channel_independence()` confirms this by:
1. Creating a uniform mid-gray image with all 3 channels != 0
2. Applying `camera_loss_partial` with fraction=0.4
3. Verifying that some pixels have 1 or 2 channels zeroed (not all 3)

### 3.2 Continuous fraction parameter

The `fraction` parameter retains continuous semantics (K-Radar's existing style) rather than switching to AI-MSF-Benchmark's 5-level discrete severity. This is a conscious design choice:
- Continuous is a superset of discrete
- Preserves compatibility with existing configs' parameter name
- The underlying mechanism change (Bernoulli → permutation) is independent of parameter granularity

### 3.3 Function signature and registry

All function signatures `fn(dict_item, params, rng) -> dict_item` are preserved. Same function names, same registry entries. No changes to `NoiseInjector`, `EffectConfig`, or integration scripts were needed beyond test updates.

---

## 4. Config Impact (Task 7)

`configs/noise_injection_smoke_test.yml` uses:
- `lidar: loss_partial(fraction=0.3)` — The practical effect at fraction=0.3 changes from "30% of rows deleted" to "30% of rows zeroed". For the smoke test integration, the config parameter value does not need to change — the test assertions were updated to match the new behavior.

No config files needed parameter re-tuning for visible corruption at the same values. The corruption degree (30% of points affected) is identical; only the type of corruption (zeroed vs deleted) differs.

---

## 5. loss_partial vs loss_complete Distinction (Task 11)

At `fraction=1.0`, the two effects are now **structurally closer** than before, but remain clearly distinct:

| Modality | loss_partial(f=1.0) | loss_complete | Distinct? |
|----------|---------------------|---------------|-----------|
| Radar | `rdr_sparse` → all-zero (N,5) ndarray | `rdr_sparse` → None | **Yes** (array vs None) |
| LiDAR | `ldr64` → all-zero (N,5) ndarray | `ldr64` → None | **Yes** (array vs None) |
| Camera | `front0` → black tensor via flatten-zero-roundtrip | `front0` → black tensor via `_zero_camera_tensor` | **Mechanically distinct** but pixel-identical |

For radar and LiDAR, the distinction is clear-cut: `loss_partial` preserves the array (sentinel = all-zero values), while `loss_complete` sets the key to `None` (sentinel = missing data). Downstream consumers that check `is None` will still see them as different.

For camera, both produce pixel-identical black tensors at fraction=1.0, but the code paths are different (`loss_partial` goes through the uint8 round-trip; `loss_complete` goes through `_zero_camera_tensor`). The distinction is documentational rather than data-level.

---

## 6. Test Results

### test_noise_injection.py

| Metric | Before | After |
|--------|--------|-------|
| Total tests | 113 | 113 |
| PASS | 103 (estimated — 10 old Bernoulli tests silently wrong) | **113** |
| FAIL | 0 (silent — `_check` prints but doesn't raise) | **0** |

### smoke_test_taxonomy.py

| Metric | Before | After |
|--------|--------|-------|
| Total checks | 96 | 96 |
| PASS | 90 (estimated — 6 old-deletion checks failing) | **96** |
| FAIL | 6 (silent) | **0** |

### smoke_test_integration.py

| Metric | Before | After |
|--------|--------|-------|
| Total checks | 37 | 38 |
| PASS | 36 | **38** |
| FAIL | 1 (`ldr64 count reduced` check) | **0** |

### Files modified

| File | Changes |
|------|---------|
| `datasets/effects/noise_injection.py` | Rewritten `camera_loss_partial` (flatten-permute-zero). `radar_loss_partial` + `lidar_loss_partial` were already updated to new mechanism. |
| `datasets/effects/test_noise_injection.py` | Rewritten all 4 loss_partial tests (radar, lidar, camera, camera-cross-channel). Updated injector test. |
| `datasets/effects/smoke_test_taxonomy.py` | Rewritten all 3 loss_partial effect tests + 2 composition tests + 2 kitchen-sink checks. |
| `scripts/smoke_test_integration.py` | Updated L3 check (count preserved + exact zeroed count). |

Files NOT touched: `frame_deletion`, `loss_complete`, `gaussian_noise`, `noise_induced_shifts`, training code paths, config schema, `NoiseInjector` class.

---

## 7. Files Not Modified

As specified:
- `frame_deletion` (R1, L1, C1) — not touched
- `loss_complete` (R4, L4, C4) — not touched
- `gaussian_noise` (L2, C2) — not touched
- `noise_induced_shifts` (R2) — not touched
- Any training-path code — not touched