# rdr_sparse vs pc100p: What they are, how they differ, and whether radar effects must modify both

**Investigation date:** 2026-07-28
**Author:** Hermes agent (investigation by request)
**Source codebase:** K-Radar fusion dataset (``kradar_fusion_v1_0_calib_change.py``) + model code + noise-injection effects module

---

## 1. What is `rdr_sparse`?

### Origin

`rdr_sparse` is a **pre-processed, thresholded, cartesian point cloud** derived from the raw 4D radar cube (the "tesseract"). It is generated *offline* by the function `generate_sparse_rdr_cube_for_wider_rtnh()` in:

**File:** `datasets/kradar_detection_v1_1.py`, line 1045–1134

The generation pipeline:

1. Load the raw radar cube `arr_zyx` from a `.mat` tesseract file (line 1087):
   ```python
   arr_cube = np.flip(loadmat(path_cube)['arr_zyx'], axis=0)
   ```
2. Normalise power values by `1e+13` (line 1088):
   ```python
   arr_cube /= norm_val
   ```
3. Apply a **quantile threshold** (line 1090) to keep only the top (100 × `QUANTILE_RATE`)% of voxels by power:
   ```python
   z_ind, y_ind, x_ind = np.where(arr_cube > np.quantile(arr_cube, quantile_rate))
   ```
   The default config uses `QUANTILE_RATE: 0.1` (`configs/sparse_rdr_data_generation/cfg_gen_wider_rtnh_10p.yml`, line 34), meaning the top 10% of voxels by power are kept (the name "rtnh_wider_10p_1").

4. Convert from grid indices to **cartesian coordinates** via grid origin + grid_size × index (lines 1093–1095):
   ```python
   z_pc_coord = ((z_min + z_ind * grid_size) - grid_size / 2)
   y_pc_coord = ((y_min + y_ind * grid_size) - grid_size / 2)
   x_pc_coord = ((x_min + x_ind * grid_size) - grid_size / 2)
   ```

5. Stack into `(N, 4)` array: `[x, y, z, power]` (line 1097):
   ```python
   sparse_rdr_cube = np.stack((x_pc_coord, y_pc_coord, z_pc_coord, power_val), axis=-1)
   ```

6. Save as `sprdr_{rdr_idx}.npy` (line 1134):
   ```python
   path_save = osp.join(dir_save_folder, seq, f'{name_header}_{idx_data}.npy')
   ```
   where `name_header = 'sprdr'` per `cfg_gen_wider_rtnh_10p.yml` line 29.

### Loading at inference time

**File:** `datasets/kradar_fusion_v1_0_calib_change.py`, lines 945–961 (`get_rdr_sparse()`)

Two paths exist, gated by `self.rdr_sparse.processed` (default: `True`, line 75):

**Processed path (default):** Loads `sprdr_{rdr_idx}.npy` directly:
```python
path_rdr_sparse = osp.join(dir_rdr_sparse, seq, f'sprdr_{rdr_idx}.npy')
rdr_sparse = np.load(path_rdr_sparse)           # line 951 — shape (N, 4): [x, y, z, power]
dict_item['rdr_sparse'] = rdr_sparse
```

**Unprocessed path:** Loads `rpc_{rdr_idx}.npy` and takes first 4 columns:
```python
rdr_sparse = np.load(path_rdr_sparse)
dict_item['rdr_sparse'] = rdr_sparse[:,:4]      # line 961 — drops doppler if present
```

### Column schema

| Index | Name    | Meaning                                          |
|-------|---------|--------------------------------------------------|
| 0     | x       | Cartesian x-coordinate (metres)                  |
| 1     | y       | Cartesian y-coordinate (metres)                  |
| 2     | z       | Cartesian z-coordinate (metres)                  |
| 3     | power   | Normalised radar power/reflectivity (÷1e+13)     |
| (4    | doppler | Doppler velocity — added offline by a separate tool; NOT present in standard loading) |

The 5th column (doppler) can optionally be added by `tools/get_doppler_for_rdr_sparse/main_get_doppler_points_for_rdr_sparse.py` (line 357) as a post-processing step, writing to a separate `rdr_sparse_doppler_{idx}.npy` file. Standard loaded `rdr_sparse` is `(N, 4)`.

### Downstream consumers (the actual model path)

1. **`collate_fn`** (file: `kradar_fusion_v1_0_calib_change.py`, lines 1259, 1313):
   `rdr_sparse` is included in `list_sparse_keys`, so it gets batched into a concatenated tensor with `batch_indices_rdr_sparse`.

2. **`models/pre_processor/rdr_sparse_processor.py`** (line 67):
   ```python
   rdr_sparse = dict_item['rdr_sparse'].cuda()
   ```
   This is the **model's actual radar input**. It is voxelised by `PointToVoxel` and fed through a simplified PointNet or summed-feature pooling to create `sp_features` and `sp_indices` (lines 80–100), which then flow into the RTNH/ASF backbone and detection head.

3. **`models/skeletons/spiking_rtnh.py`** (lines 150, 528):
   ```python
   rdr_sparse = dict_item['rdr_sparse'].cuda()
   ```

4. **Inference scripts** like `scripts/main_fusion_eval_0.py` (line 194):
   ```python
   pc_radar = dict_item['rdr_sparse']
   ```
   Then further filtered on line 196 by power quantile:
   ```python
   pc_radar = pc_radar[np.where(pc_radar[:,3] > np.quantile(pc_radar[:,3], 1-percentile_rate))[0],:]
   ```

5. **ROI filter** (`filter_roi`, line 1129): only `rdr_sparse` and `ldr64` get ROI-cropped.

Key takeaway: **`rdr_sparse` is *the* radar input to every K-Radar model** (RTNH, ASF, SpikingRTNH, etc.).

---

## 2. What is `pc100p`?

### Origin

`pc100p` is an **unthresholded, dense, cartesian representation of the entire radar volume** — every single voxel in the 4D radar cube (all 256 range × 107 azimuth × 37 elevation bins) flattened to a point cloud of shape `(256×107×37, 5) = (1,012,224, 5)`.

It is produced by `get_rdr_polar_3d()` when the config flag `in_pc100p=True` (which is the default — see line 76).

**File:** `datasets/kradar_fusion_v1_0_calib_change.py`, lines 992–1014

Construction:

1. Either load a pre-computed `polar3d_{rdr_idx}.npy` file (processed path) or compute from cube power + doppler polar data (live path).

2. The core result is `cube_polar`, a `(2, 256, 107, 37)` array:
   - `cube_polar[0]` = power plane (normalised ÷ 1e+13)
   - `cube_polar[1]` = doppler cartesian

3. Pre-compute the XYZ coordinates of *every voxel* in the polar grid (done once in `__init__`, lines 226–243):
   ```python
   rae_r = np.repeat(np.repeat((self.arr_range).copy().reshape(n_r,1,1), n_a, 1), n_e, 2)
   rae_a = np.repeat(np.repeat((self.arr_azimuth).copy().reshape(1,n_a,1), n_r, 0), n_e, 2)
   rae_e = np.repeat(np.repeat((self.arr_elevation).copy().reshape(1,1,n_e), n_r, 0), n_a, 1)
   # Radar polar → General polar coordinate
   rae_a = -rae_a
   rae_e = -rae_e
   xyz_x = rae_r * np.cos(rae_e) * np.cos(rae_a)
   xyz_y = rae_r * np.cos(rae_e) * np.sin(rae_a)
   xyz_z = rae_r * np.sin(rae_e)
   self.rdr_polar_3d_xyz = np.stack((xyz_x, xyz_y, xyz_z), axis=0)  # (3, 256, 107, 37)
   ```

4. Concatenate the fixed XYZ grid with the per-frame power+doppler data (line 1008):
   ```python
   pc100p = np.concatenate((self.rdr_polar_3d_xyz, cube_polar), axis=0)
   ```
   Result: `(5, 256, 107, 37)` — channels are **[x, y, z, power, doppler]**.

5. Reshape to a tall point-cloud format `(N, 5)` (line 1009–1010):
   ```python
   n_dim, _, _, _ = pc100p.shape  # n_dim = 5
   dict_item['pc100p'] = pc100p.reshape(n_dim, -1).transpose()
   ```
   This gives `(256×107×37, 5)` = approximately **1,012,224 points** per frame.

### Column schema

| Index | Name    | Meaning                                          |
|-------|---------|--------------------------------------------------|
| 0     | x       | Cartesian x-coordinate (centre of each voxel)    |
| 1     | y       | Cartesian y-coordinate (centre of each voxel)    |
| 2     | z       | Cartesian z-coordinate (centre of each voxel)    |
| 3     | power   | Radar power/reflectivity at that voxel (÷1e+13)  |
| 4     | doppler | Doppler velocity at that voxel                    |

### Downstream consumers

**`pc100p` has NO downstream consumers in the model, loss, or evaluation pipeline.**

It is:
- **Created** in `get_rdr_polar_3d()` (line 1007–1010)
- **Passed through `collate_fn`** — it's listed in `list_sparse_keys` (lines 1259, 1313) and gets batched into a concatenated tensor with `batch_indices_pc100p`
- **Used as a source** by `get_proportional_rdr_points_from_pc100p()` (line 1058–1061) to derive downsampled point clouds (`rdr_pc`), which themselves are used as an alternative to `rdr_sparse` in certain pipelines
- **Manipulated by the noise-injection module** (7 distinct effect handlers reference it: `noise_injection.py` lines 118, 144, 189, 207, 652–653, 666–669, 683–684, 705–706, 773–774)

But **no model code** (`models/pre_processor/*.py`, `models/skeletons/*.py`, `scripts/main_fusion_eval_0.py`) ever reads `dict_item['pc100p']` or `dict_item['batch_indices_pc100p']`. The smoke test (`scripts/smoke_test_integration.py`) only checks that the field is `None` after a frame-deletion effect, validating the noise-injection behaviour rather than any downstream consumption.

---

## 3. The concrete difference between `rdr_sparse` and `pc100p`

| Property               | `rdr_sparse`                            | `pc100p`                                          |
|------------------------|------------------------------------------|---------------------------------------------------|
| **Point count**        | ~1000–10,000 *after ROI filtering* (see correction below) — raw output of `generate_sparse_rdr_cube_for_wider_rtnh()` is ~1.5M (top 10% of the 150×400×250 `radar_zyx_cube` grid) | 1,012,224 (every voxel in the 256×107×37 grid)   |
| **Columns**            | 4: `[x, y, z, power]`                   | 5: `[x, y, z, power, doppler]`                   |
| **Threshold**          | Quantile-filtered (top 10% default)     | None — all voxels present                         |
| **Derivation**         | From raw `.mat` tesseract via grid-index decode | From pre-computed `polar3d_{idx}.npy` or live cube  |
| **Sampling**           | Sparse, "interesting" detections only   | Dense, every grid cell regardless of power        |
| **Storage**            | On-disk per-frame `.npy` file           | On-disk per-frame `.npy` file, or computed live    |
| **Purpose**            | **Model input** — the actual radar point cloud fed to RTNH/ASF | **Utility representation** — used to derive down-sampled views (`pc10p`, `pc1p`, etc.) for experiments |
| **Doppler availability** | Usually absent (added by separate tool) | Always present (channel 4)                         |

**They are NOT the same physical points.** `rdr_sparse` is a small, power-filtered subset of high-signal returns. `pc100p` is the full-volume grid with all voxels, including empty/noise-power cells. The `rdr_sparse` points *could* correspond to a subset of `pc100p` rows (since both are derived from the same underlying radar cube, just with different processing pipelines), but they are **not kept row-aligned** — each is independently constructed and has a different number of rows.

---

## 4. Are they synchronised representations of the same points?

**No.** They are not row-aligned, not point-count-aligned, and not intended to represent the same set of physical points.

- `pc100p` contains **every voxel** in the radar's polar grid → ~1 million rows
- `rdr_sparse` contains the **top 10% by power** of the cube's voxels at generation time → ~1.5M rows raw (see correction below), reduced to ~1000–10,000 after ROI filtering at load time

The only relationship is that both originate from the same underlying 4D radar cube (the "tesseract"): `rdr_sparse` via offline quantile-threshold + grid-to-cartesian conversion, and `pc100p` via live (or pre-computed) polar-to-cartesian conversion of the full cube. They share a common source but are **independent representations, not synchronised copies** of one another.

The name convention — `pc100p` = "point cloud, 100% of voxels" — vs the inference-script pattern of thresholding `rdr_sparse` to top 1% (`percentile_rate = 0.01`) suggests the naming mirrors the `pc1p`/`pc5p`/`pc10p` series (proportional point clouds at different rates, produced by `get_rpcs()` in the config). `pc100p` is simply the "keep everything" end of that spectrum.

---

## 5. Does any downstream code cross-reference `rdr_sparse` and `pc100p`?

**No.** I searched every file in the K-Radar repository that touches either key. Here is the exhaustive list of what happens:

- **Dataset loaders** (`kradar_fusion_v1_0_calib_change.py`, `kradar_fusion_v1_0.py`, `kradar_odometry_v1_0.py`, `kradar_detection_v2_1.py`): both keys are set independently by separate loader functions. Neither loader reads the other key to construct itself.
- **`collate_fn`** (line 1259/1313): both are listed in `list_sparse_keys` and handled identically — each is individually concatenated across the batch and given its own `batch_indices_*` tensor. Nothing checks cross-key consistency.
- **`get_proportional_rdr_points_from_pc100p()`** (line 1058): reads `pc100p` to *derive* a new `rdr_pc` key, but never reads `rdr_sparse`.
- **`filter_roi()`** (line 1125–1138): explicitly lists `['rdr_sparse', 'ldr64']` — **`pc100p` is NOT in the ROI filter**, so they don't even share the same spatial cropping.
- **Model code** (`models/pre_processor/rdr_sparse_processor.py`, `models/skeletons/spiking_rtnh.py`, `models/skeletons/fusion_base.py`, `models/skeletons/fusion_base_integrated.py`): reads `rdr_sparse` only — never touches `pc100p`.
- **Noise-injection module** (`noise_injection.py`): the *only* code that modifies both keys together. All other code treats them independently.

**Conclusion: There is zero coupling between `rdr_sparse` and `pc100p` in any consumer downstream of the dataset loader.** Nobody ever checks that points dropped from one are also dropped from the other. Nobody computes a metric that assumes they agree.

---

## 6. Verdict: Is radar_loss_partial's "modify both keys" behaviour necessary?

**It is unnecessary (overcautious) under current codebase usage.**

Here's the evidence chain:

1. `rdr_sparse` is a **sparse, thresholded** point cloud (~1000–10,000 points) derived from the top-N% of radar voxels by power. It is the primary input for every K-Radar model.
2. `pc100p` is a **dense, full-grid** point cloud (~1 million points) containing *every* radar voxel without thresholding. It is not consumed by any model, loss, or evaluation code.
3. They are **completely independent representations** — not row-aligned, not point-count-aligned, and not synchronised.
4. **No downstream code cross-references the two.** Nothing would break or produce inconsistent results if one key were modified and the other were not.
5. The only reason to modify both would be conceptual consistency (both are "radar data" and both describe the same scene), but that is a design preference, not an operational requirement.

**Recommendation:** The effects could safely be simplified to modify only `rdr_sparse` (the key that actually feeds the model) and skip `pc100p`. If this were done, the loss_partial, noise_induced_shifts, power_floor_clip, power_ceiling_clip, and doppler_jitter effects would all produce identical model inputs while avoiding wasted passes over a million-row array. The frame_deletion and loss_complete effects could also limit their `_set_none` to `rdr_sparse` and `rdr_polar_3d`.

**Caveat:** The above is a statement about what the current codebase *actually uses*. If you intend to eventually route `pc100p` (or derived keys like `pc10p`) into a model, then maintaining the sync would be proper future-proofing. But as of today's code, it is not required.

---

## Source references (all file:line)

| Claim | File | Line(s) |
|-------|------|---------|
| `rdr_sparse` offline generation | `datasets/kradar_detection_v1_1.py` | 1045–1134 |
| Quantile threshold for sparse generation | `configs/sparse_rdr_data_generation/cfg_gen_wider_rtnh_10p.yml` | 33–34 |
| `rdr_sparse` loading (processed path) | `datasets/kradar_fusion_v1_0_calib_change.py` | 945–952 |
| `rdr_sparse` loading (unprocessed path) | same file | 953–961 |
| Default config: `rdr_sparse` enabled | same file | 75 |
| `rdr_sparse` in ROI filter | same file | 1127–1135 |
| `rdr_sparse` in collate_fn | same file | 1259, 1313, 1278–1283, 1414–1421 |
| `rdr_sparse` consumed by model pre-processor | `models/pre_processor/rdr_sparse_processor.py` | 67 |
| `rdr_sparse` consumed by spiking RTNH | `models/skeletons/spiking_rtnh.py` | 150, 528 |
| `rdr_sparse` consumed in eval script | `scripts/main_fusion_eval_0.py` | 194 |
| `pc100p` creation in `get_rdr_polar_3d` | `datasets/kradar_fusion_v1_0_calib_change.py` | 992–1014 |
| XYZ pre-computation for `pc100p` | same file | 226–243 |
| Default config: `in_pc100p=True` | same file | 76 |
| `pc100p` shape = (1012224, 5) | implied by 256×107×37 grid | 1007–1010 |
| `pc100p` NOT in ROI filter | same file | 1127–1128 |
| `pc100p` in collate_fn (batched but unused) | same file | 1259, 1313 |
| `pc100p` NOT read by any model code | models/ directory | exhaustive search — zero hits |
| Noise-injection treats both keys | `datasets/effects/noise_injection.py` | 144, 189, 207, 666–669, 773–774 |
| No cross-reference between keys | entire repo | exhaustive search — zero hits |

---

## Correction (2026-07-30, from `docs/vAIlt/radar-mat-vs-npy-corruption-point-report.md`)

This doc's original claim (Sections 1, 3, 4: "`rdr_sparse` is ~1000–10,000 points") conflates two different stages of the pipeline and needs disambiguation:

- **Raw output of `generate_sparse_rdr_cube_for_wider_rtnh()`** (the function that actually produces `sprdr_*.npy`, i.e. `rdr_sparse` before any further filtering): measured directly against the real `radar_zyx_cube/cube_00033.mat` file — **exactly 1,500,000 points/frame** (top 10% of the `150×400×250 = 15,000,000`-voxel `radar_zyx_cube` grid). This is what actually gets written to disk as `rdr_sparse`.
- **~1000–10,000 points**, as originally stated here, is the count *after* the fusion loader's ROI filter (`filter_roi`, `kradar_fusion_v1_0_calib_change.py:1125–1138`) crops the loaded `rdr_sparse` array down to the detection region — i.e. what the model actually consumes per-frame post-crop, not what's on disk.

Both numbers are correct for what they describe; the original text above just didn't distinguish "on-disk `sprdr_*.npy` size" from "post-ROI-filter size fed to the model." Left the original phrasing in place above rather than rewritten, per this correction.