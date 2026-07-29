# ldr128 (Ouster OS2-128 / OS1-128) Usage Audit

**Date:** 2026-07-28
**Scope:** Entire K-Radar repository at `/home/adhish/Productivity/AMSCUP/repos/K-Radar`
**Method:** Exhaustive `grep -rn` (via ripgrep-backed search) for `ldr128`, `LDR128`, `Ldr128` across all file types (.py, .yml, .yaml, .txt, .md, .json, .cfg, .ini); plus targeted searches for `os1-128`, `os2-128`, `get_ldr128`, `def.*ldr128`, and conditional branching on `ldr128`.

---

## 1. Complete Occurrence Table

All 47 occurrences of the string `ldr128` in the repository. Zero case variants (`LDR128`, `Ldr128`) exist.

### 1.1 Config files (.yml/.yaml) — 24 hits, all `False`

| File | Line | Classification | Value | Description |
|------|------|----------------|-------|-------------|
| `configs/ASF_v2_0_original.yml` | 46 | Config key | `False` (commented) | Item enable key, commented out with rest of item dict |
| `configs/ASF_v2_0_final_ADY.yml` | 46 | Config key | `False` | Item enable key |
| `configs/ASF_v2_0_final_wo_SCL.yml` | 46 | Config key | `False` | Item enable key |
| `configs/ASF_v2_0_final.yml` | 46 | Config key | `False` | Item enable key |
| `configs/ASF_v2_0_final_alvis.yml` | 46 | Config key | `False` | Item enable key |
| `configs/ady_conf.yml` | 46 | Config key | `False` | Item enable key |
| `configs/cfg_SpikingRTNH.yml` | 43 | Config key | `False` | Item enable key |
| `configs/cfg_SpikingRTNH_BTI.yml` | 43 | Config key | `False` | Item enable key |
| `configs/cam_minimal.yaml` | 44 | Config key | `False` | Item enable key |
| `configs/cfg_CAMERA_MODEL_Base.yml` | 42 | Config key | `False` | Item enable key |
| `configs/cfg_PVRCNNPP.yml` | 43 | Config key | `False` | Item enable key |
| `configs/cfg_RTNH_wide.yml` | 44 | Config key | `False` | Item enable key |
| `configs/cfg_SECOND.yml` | 42 | Config key | `False` | Item enable key |
| `configs/v1_0/cfg_RTNH.yml` | 41 | Config key | `False` | Item enable key |
| `configs/v1_0/cfg_ASF_final.yml` | 42 | Config key | `False` | Item enable key |
| `configs/v1_0/cfg_A2F_scl_final.yml` | 42 | Config key | `False` | Item enable key |
| `configs/v1_0/cfg_SECOND.yml` | 41 | Config key | `False` | Item enable key |
| `configs/v1_0/cfg_CAMERA_MODEL_Base.yml` | 42 | Config key | `False` | Item enable key |
| `configs/configs/v1_0/cfg_RTNH.yml` | 41 | Config key | `False` | Duplicate of above in nested dir |
| `configs/configs/v1_0/cfg_ASF_final.yml` | 42 | Config key | `False` | Duplicate of above in nested dir |
| `configs/configs/v1_0/cfg_A2F_scl_final.yml` | 42 | Config key | `False` | Duplicate of above in nested dir |
| `configs/configs/v1_0/cfg_SECOND.yml` | 41 | Config key | `False` | Duplicate of above in nested dir |
| `configs/configs/v1_0/cfg_CAMERA_MODEL_Base.yml` | 42 | Config key | `False` | Duplicate of above in nested dir |

**No config in the entire repository ever sets `ldr128` to `True`.**

### 1.2 Dataset loaders (.py) — 14 hits

#### 1.2.1 Item config dict entries (7 hits, all `False`)

| File | Line | Classification | Value | Description |
|------|------|----------------|-------|-------------|
| `datasets/kradar_fusion_v1_0.py` | 67 | Item config key | `False` | Part of `item` dict in `dict_cfg` |
| `datasets/kradar_fusion_v1_0_calib_change.py` | 65 | Item config key | `False` | Same, calibration variant |
| `datasets/kradar_odometry_v1_0.py` | 69 | Item config key | `False` | Part of `item` dict |
| `datasets/kradar_tracking_v1_0.py` | 43 | Item config key | `False` | Part of `item` dict |
| `datasets/kradar_detection_v2_0.py` | 43 | Item config key | `False` | Part of `item` dict |
| `datasets/kradar_detection_v2_1.py` | 55 | Item config key | `False` | Part of `item` dict |
| `tools/get_1st_points/main_get_1st_points.py` | 44 | Item config key | `False` | Part of `item` dict in tool script |

**Notable exclusion:** `kradar_detection_v1_0.py` and `kradar_detection_v1_1.py` do NOT have an `ldr128` key in their item config dicts at all — the key was added starting from v2_0 dataset versions.

#### 1.2.2 Filename index destructuring (7 hits)

Every dataset loader and the 3 tool scripts that parse label file headers contain the following pattern:

```python
rdr, ldr64, camf, ldr128, camr = temp_idx.split('=')[1].split('_')
```

| File | Line | Classification | Description |
|------|------|----------------|-------------|
| `datasets/kradar_fusion_v1_0.py` | 367 | Filename index variable | Destructures `idx(tesseract_os2-64_cam-front_os1-128_cam-lrr)=...` header |
| `datasets/kradar_fusion_v1_0.py` | 370 | Dict key | `'ldr128': ldr128` stores the string index |
| `datasets/kradar_fusion_v1_0_calib_change.py` | 358,361 | Filename index variable | Same pattern |
| `datasets/kradar_odometry_v1_0.py` | 360,363 | Filename index variable | Same pattern |
| `datasets/kradar_tracking_v1_0.py` | 199,202 | Filename index variable | Same pattern |
| `datasets/kradar_detection_v2_0.py` | 152,155 | Filename index variable | Same pattern |
| `datasets/kradar_detection_v2_1.py` | 261,264 | Filename index variable | Same pattern |
| `tools/get_1st_points/main_get_1st_points.py` | 202,205 | Filename index variable | Same pattern |
| `tools/get_doppler_for_rdr_sparse/main_get_doppler_points_for_rdr_sparse.py` | 141,144 | Filename index variable | Same pattern |
| `tools/eval_checker/check_evaluation_with_label.py` | 229 | Filename index variable | Same pattern |

**Critical:** This variable holds a STRING TIMESTAMP INDEX from the label file header (e.g. `"0003"`), NOT LiDAR point cloud data. It is the frame-sync index, not a data-processing operation. There is zero functional processing of ldr128 data at any of these sites.

**Notable exclusion:** `kradar_detection_v1_0.py` and `kradar_detection_v1_1.py` do NOT contain this index parsing pattern — they use a different label header format from the v1_0/v1_1 era.

### 1.3 `__getitem__` conditional branching

Every dataset loader's `__getitem__` was inspected. None branches on `self.item['ldr128']`. The conditional chains only check:

| Dataset | Checks in `__getitem__` |
|---------|------------------------|
| `kradar_fusion_v1_0.py` | `ldr64`, `rdr_polar_3d`, `rdr_sparse`, `cam`, `rpcs`, `roi` |
| `kradar_fusion_v1_0_calib_change.py` | (same as fusion) |
| `kradar_odometry_v1_0.py` | `ldr64`, `rdr_polar_3d`, `rdr_sparse`, `cam` |
| `kradar_tracking_v1_0.py` | `ldr64`, `rdr_sparse` |
| `kradar_detection_v2_0.py` | `ldr64`, `rdr_sparse`, `roi` |
| `kradar_detection_v2_1.py` | `ldr64`, `rdr_sparse`, `cam`, `rdr_polar_3d`, `roi` |
| `kradar_detection_v1_0.py` | no ldr128 at all |
| `kradar_detection_v1_1.py` | no ldr128 at all |

**No dataset has branching logic for `ldr128`.**

---

## 2. Broader search: 128-beam sensor references

### 2.1 No `get_ldr128()` function exists

Searched all `.py` files for `def.*128` and `get_ldr`. All results map to `get_ldr64()` or `get_ldr64_from_path()`. No `get_ldr128()` or equivalent function exists in the entire repository.

### 2.2 Commented-out `os1-128` path (v1_0/v1_1 only)

In `kradar_detection_v1_0.py:869` and `kradar_detection_v1_1.py:869`:

```python
# path_lidar_pc_128 = '/'+os.path.join(*path_header, 'os1-128', 'os1-128_'+lidar_idx+'.pcd')
```

Marked with `### Currently not used`. References the older Ouster OS1-128 sensor (predecessor to OS2-128). This is commented-out code in the oldest dataset version; no functional equivalent exists in v2_0/v2_1 loaders.

### 2.3 `os2-128` paths in radar_film tools (external data cache)

Two scripts in `tools/radar_film/` reference `os2-128` directory paths:

| File | Line | Description |
|------|------|-------------|
| `tools/radar_film/get_pw_dist.py` | 227 | `path_lpc = osp.join(self.ldr_dir, seq_name, 'os2-128', f'os2-128_{ldr_idx}.pcd')` — constructs path to 128-beam PCD files in a user-specific external directory. Data loaded from this path is fed to `get_ldr64()` (line 277). |
| `tools/radar_film/get_objs_from_lidar.py` | 23 | `FOLDER_PCD = '/media/donghee/HDD_0/Radar_Film/gen_files/44/os2-128'` — hardcoded path to a user-specific external directory. Also uses `get_ldr64()` to load. |

These are **standalone research utilities** that process OS2-128 sensor data by loading it with standard `get_ldr64()` PCD parsing. They use the `ldr64` processing path, not a dedicated `ldr128` pipeline. Both reference user-specific external mount points (not part of the training dataset structure).

### 2.4 UI calibration utility comment

`uis/ui_calibration.py:1335` contains a comment:
```python
# get tesseract, os2-64, cam-front, os1-128, and cam-lrr
```
This is a code comment describing the label file header format. Not a functional reference.

### 2.5 Label matcher filename format

`tools/label_matcher/label_matcher.py:114` constructs a label file header containing `os1-128` in the descriptive sensor-name string. This is metadata formatting only (the sensor name string embedded in the label file header), not data processing.

---

## 3. Effects / noise-injection module

`datasets/effects/` — zero references to `ldr128`. All LiDAR effects target only `ldr64`.

---

## 4. scripts/ directory

Zero references to `ldr128`.

---

## 5. Sensor specification (for reference)

If ldr128 loading logic were to exist, the K-Radar dataset's 128-beam LiDAR data comes from:

- **Sensor:** Ouster OS2-128 (later sequences) / Ouster OS1-128 (earlier sequences)
- **Data format:** `.pcd` files in an `os2-128/` or `os1-128/` subdirectory per sequence
- **Naming convention:** `os2-128_{5-digit-index}.pcd`
- **Structure:** Standard Ouster PCD format with per-point fields (x, y, z, intensity, ring, time, etc.)
- **Point attributes:** Typically 5+ attributes per point (x, y, z, intensity, ring) — same as ldr64 PCD files
- **Key difference from ldr64:** 128 vertical channels vs 64, so the PCD will have roughly 2x the point count per frame at the same horizontal resolution. The raw file format (text PCD with header lines) is similar, but the `n_attr` and `skip_line` values would differ if processed with dedicated logic.

No dedicated loading logic exists in the repository; the `tools/radar_film/` scripts load these PCD files through the generic `get_ldr64()` function, applying 64-beam attribute counts and skip lines to 128-beam data.

---

## 6. Verdict

**ldr128 is entirely dormant / unused across the entire K-Radar codebase.**

Every occurrence falls into exactly one of two categories:

1. **A config boolean set to `False`** — every training/inference config (24/24 .yml files, 7/7 Python `item` dicts) has `'ldr128': False`. **Not a single config ever enables it.**

2. **A filename-index destructuring variable** — the string `rdr, ldr64, camf, ldr128, camr = ...` parses the frame-sync index from a label file header. The `ldr128` variable here is a string timestamp index (e.g. `"0003"`), not LiDAR data. Never checked, never branched on, never passed to any processing function.

There is:
- **No** `get_ldr128()` function anywhere
- **No** `if self.item['ldr128']` conditional in any `__getitem__`
- **No** code path that loads, transforms, or consumes 128-beam LiDAR point cloud data through the standard dataset pipeline
- **No** visualization or tooling that processes ldr128 via its config key
- **No** noise-injection effect that touches ldr128

The only code touching physical `os2-128` files (`tools/radar_film/get_pw_dist.py` and `tools/radar_film/get_objs_from_lidar.py`) loads them through the `get_ldr64()` function, applies 64-beam attribute counts, and has no awareness of the `ldr128` config key whatsoever — these are standalone research scripts on user-local mount points, not part of the model/training pipeline.

**Bottom line:** The Ouster OS2-128 / OS1-128 sensor data exists on disk in the K-Radar dataset but the repository has no code that processes it through its own pipeline. Adding ldr128 support would require writing the data loader, integration into the `item` config semantics, and training/inference plumbing from scratch.