---
title: K-Radar Coordinate Frame Analysis Report
type: literature
source: home/adhish/Productivity/AMSCUP/docs/COORDINATE_FRAME_ANALYSIS.md
date: 2026-07-02
tags: [05 Implementation]
---
# K-Radar Coordinate Frame Analysis Report

## Executive Summary

**K-Radar uses a unified "Radar coordinate frame" as the common reference frame for all sensors and annotations.**

The dataset does **not** use the ego-vehicle frame as the primary coordinate system. Instead:
- **Radar frame** = Primary reference frame (origin at front grill, X forward, Y left, Z up)
- **LiDAR point clouds** are stored in their native sensor frame on disk and **transformed to Radar frame at load time** using `calib_radar_lidar.txt` (translation only)
- **Camera extrinsics** (`radar2camera`, `camera2radar`) are provided per-sequence in `T_params_seq/` pickle files
- **Annotations** (`info_label_rev2`) are in **LiDAR frame** and **transformed to Radar frame at load time** using the same `calib_radar_lidar.txt`
- **No ego frame exists in the runtime pipeline** — the Radar frame serves as the de facto fusion frame

---

## 1. LiDAR (os2-64, os1-128)

### Frame on Disk
**LiDAR sensor frame** (native Ouster coordinate system). The `.pcd` files contain raw points as measured by each LiDAR.

### Transformation Applied?
**Yes — at load time.** The point cloud is translated to the **Radar frame** using calibration values from `info_calib/calib_radar_lidar.txt`.

### Transformation Details

**Calibration File:** `info_calib/calib_radar_lidar.txt` (per sequence)
```
* idx(...)=..., timestamp=...
<frame_diff>, X_offset, Y_offset, Z_offset
```
Example: `0, -2.54, 0.3, 0.7` (frame diff, then X, Y, Z in meters)

**Code Location:** `datasets/kradar_detection_v1_0.py`, `get_pc_lidar()` (lines 514–532)
```python
def get_pc_lidar(self, path_lidar, calib_info=None):
    # ... load PCD ...
    if self.type_coord == 1:  # Radar coordinate
        if calib_info is None:
            raise AttributeError('* Exception error (Dataset): Insert calib info!')
        else:
            pc_lidar = np.array(list(map(lambda x: [
                x[0]+calib_info[0], x[1]+calib_info[1], x[2]+calib_info[2], x[3]
            ], pc_lidar.tolist())))
    return pc_lidar
```

**Same logic in fusion dataset:** `datasets/kradar_fusion_v1_0.py`, `get_ldr64()` (lines 754–780)
```python
if self.ldr64.calib:
    n_pts, _ = pc_lidar.shape
    calib_vals = np.array(dict_item['meta']['calib']).reshape(-1,3).repeat(n_pts, axis=0)
    pc_lidar[:,:3] = pc_lidar[:,:3] + calib_vals
```

### Transformation Matrix
**Translation only (no rotation):**
```
T_lidar2radar = [ I_3×3 | [X_offset, Y_offset, Z_offset]ᵀ ]
                [ 0 0 0 | 1 ]
```
Where `X_offset, Y_offset, Z_offset` come from `calib_radar_lidar.txt` line 2 (values 2–4).

### Notes
- The paper (arXiv:2206.08171, Appendix D.2) states: *"We have not considered the pitch angle difference between 4D Radar and Lidar, since we fix the sensors precisely perpendicular to the ground, resulting in no theoretical difference in the pitch angle."*
- Calibration error reported as **maximum 0.5 cm**
- Both OS2-64 and OS1-128 use the **same calibration** (they share the same roof mount with different heights)

---

## 2. Radar (tesseract / radar_zyx_cube)

### Frame on Disk
**Radar sensor frame** (native FMCW radar coordinate system). The 4D tensor (Doppler × Range × Azimuth × Elevation) and the 3D cube (Z × Y × X Cartesian) are both in the radar's native polar/Cartesian frame.

### Transformation Applied?
**No explicit transformation at load time.** The radar frame **IS the reference frame**.

### Code Evidence

**Tensor loading:** `datasets/kradar_detection_v1_0.py`, `get_tesseract()` (lines 417–441)
```python
def get_tesseract(self, path_tesseract, is_in_DRAE=True, is_in_3d=False, is_in_log=False):
    arr_tesseract = loadmat(path_tesseract)['arrDREA']
    if is_in_DRAE:
        arr_tesseract = np.transpose(arr_tesseract, (0, 1, 3, 2))  # DRAE ordering
    return arr_tesseract
```

**Cube loading:** `get_cube()` (lines 443–497)
```python
def get_cube(self, path_cube, is_in_log=False, mode=0):
    arr_cube = np.flip(loadmat(path_cube)['arr_zyx'], axis=0)  # z-axis flipped
    # ... ROI cropping, normalization ...
    return arr_cube
```

**Coordinate mapping:** The radar cube uses a fixed Cartesian grid defined in the dataset class:
```python
self.arr_z_cb = np.arange(-30, 30, 0.4)   # Z: -30 to 30 m
self.arr_y_cb = np.arange(-80, 80, 0.4)   # Y: -80 to 80 m
self.arr_x_cb = np.arange(0, 100, 0.4)    # X: 0 to 100 m (forward only)
```

### Radar FOV / Range (from config & paper)
- **Azimuth:** ±53.5° (107° total) — forward only
- **Elevation:** ±18.5° (37° total)
- **Range:** 0–118 m (paper: "longitudinal radius of 120m")

### Notes
- The radar is mounted at the **front grill** (paper Figure 3)
- Radar frame: Origin at radar, X forward, Y left, Z up
- **All other sensors are transformed TO this frame**

---

## 3. Camera (cam-front, cam-left, cam-rear, cam-right)

### Frame on Disk
**Camera sensor frame** (ZED2i stereo pairs). Images are raw (distorted) PNGs, 2560×720 stitched (left/right 1280×720 each).

### Transformation Applied?
**Yes — at load time for projection.** Two sets of extrinsics are provided:

| Transform | Source | Description |
|-----------|--------|-------------|
| `radar2camera` (4×4) | `T_params_seq/{seq}/` pickle | Radar → Camera frame |
| `camera2radar` (4×4) | `T_params_seq/{seq}/` pickle | Camera → Radar frame (inverse) |
| `camera_intrinsics` (4×4) | `T_params_seq/{seq}/` pickle | K matrix embedded in top-left 3×3 |

### Projection Pipeline

**For 3D → 2D projection (labels → image):**
```
P_radar (3D bbox in radar frame)
    → T_radar2camera @ P_radar (to camera frame)
    → K @ P_camera (to pixel coordinates)
```

**Code Location:** `datasets/kradar_fusion_v1_0.py`, `collate_fn` (lines 1326–1330)
```python
temp_dict_t_params = self.dict_t_params[seq][k]
list_intrinsics.append(torch.tensor(temp_dict_t_params['camera_intrinsics'], dtype=torch.float32))
list_cam2sensor.append(torch.tensor(temp_dict_t_params['camera2'+self.ref_sensor], dtype=torch.float32))
list_sensor2img.append(torch.tensor(temp_dict_t_params[self.ref_sensor+'2image'], dtype=torch.float32))
```

Where `self.ref_sensor = 'radar'` (from config `t_params.ref_sensor`)

**Camera→Radar extrinsics are used directly** — no intermediate ego frame.

### Undistortion
**Yes — pre-computed offline.** Two sets of images are provided:
- `undistorted/` — lens distortion corrected
- `cropped/` — further cropped/resized for training

**Code:** `kradar_fusion_v1_0.py` lines 179–190, 578–618
```python
if self.cam_dir.load == 'cropped':
    self.img_load = 0
    self.img_dir = self.cam_dir.cropped
elif self.cam_dir.load == 'undistorted':
    self.img_load = 1
    self.img_dir = self.cam_dir.undistorted
```

**Calibration YAMLs** (`resources/cam_calib/common/*.yml`) contain distortion coefficients (k1–k5) and the `T_ldr2cam` (LiDAR→Camera) transform used to generate undistorted images offline via `util_calib.py::save_calibration_matrix_in_npy()`.

### Camera Extrinsics Format (from `util_calib.py`)
```python
# L to C (LiDAR to Camera)
r_ldr2cam = R.from_euler('zyx', [yaw, pitch, roll], degrees=True).as_matrix()
T_ldr2cam = np.concatenate([r_ldr2cam, [x, y, z].reshape(-1,1)], axis=1)  # 3×4
# Then padded to 4×4
```

**Note:** The calibration is **LiDAR→Camera**, but since LiDAR is already transformed to Radar frame at load time, the effective transform chain is:
```
Radar → (inverse of calib_radar_lidar) → LiDAR → T_ldr2cam → Camera
```
Or directly: `radar2camera` from `T_params_seq`.

---

## 4. Annotations / Labels (`info_label_rev2`)

### Frame on Disk
**LiDAR frame** (same as the raw LiDAR point clouds).

**Evidence from paper (Appendix D.1):**
> "We utilize the calibrated LPC [LiDAR point cloud] with a maximum calibration error of 0.5cm to enable accurate 3D bounding box annotations."

> "The 3D bounding boxes can be easily transformed from the Lidar to the Radar coordinate frame since we provide both spatial and temporal calibration parameters..."

### Transformation Applied at Load Time
**Yes — LiDAR frame → Radar frame** using the same `calib_radar_lidar.txt` translation.

**Code:** `datasets/kradar_detection_v1_0.py`, `get_tuple_object()` (lines 306–395)
```python
def get_tuple_object(self, line, calib_info, is_heading_in_rad=True, path_label=None):
    # ... parse x, y, z, theta, l, w, h from line ...
    
    if self.type_coord == 1:  # Radar coordinate
        x = x + calib_info[0]
        y = y + calib_info[1]
        z = z + calib_info[2]
    
    return (cls_name, idx_cls, [x, y, z, theta, l, w, h], idx_obj)
```

**Same in fusion dataset:** `kradar_fusion_v1_0.py`, `get_label()` (lines 426–436)
```python
if self.label.calib:
    dx, dy, dz = dict_item['meta']['calib']
    for obj in list_tuple_objs:
        cls_name, (x, y, z, th, l, w, h), trk, avail = obj
        x = x + dx
        y = y + dy
        z = z + dz
        list_temp.append((cls_name, (x, y, z, th, l, w, h), trk, avail))
```

### Label Format (from `info_label_rev2/*.txt`)
```
*, R, 1, Sedan, 47.391, -2.104, -0.425, -0.340, 1.641, 0.807, 0.710
```
Fields: `*`, sensor_identify, tracking_id, class, **X, Y, Z, Theta (deg), half_length, half_width, half_height**

**Units:** Meters, degrees (heading), half-dimensions

### Notes
- Heading `Theta` is **yaw angle in degrees** (converted to radians in code)
- Only objects with **positive X (forward of ego)** are annotated (paper: "we only annotate objects that appear in the positive longitudinal axis")
- Annotation range: **120m longitudinal, 80m lateral** from ego

### Definitive Proof That Labels Are in LiDAR Frame

#### 1. Explicit Developer Comment in Code
`datasets/kradar_detection_v1_0.py`, line 287:
```python
def get_calib_info(self, path_calib, is_z_offset_from_cfg=True):
    if not (self.type_coord == 1):  # not Radar coordinate (labels are represented on Ldr coordinate)
        return None
```
**Direct quote:** `"labels are represented on Ldr coordinate"`

#### 2. `type_coord` Conditional Transform
The transform is **only applied when leaving LiDAR frame**:
- `type_coord == 1` (Radar): applies translation from `calib_radar_lidar.txt`
- `type_coord == 2` (LiDAR): **no transform applied** — labels used as-is
This proves the native label frame = LiDAR frame.

#### 3. Calibration File Name & Content
File: `info_calib/calib_radar_lidar.txt`
```
frame difference,x,y
32,-2.54,0.3
```
Contains **LiDAR→Radar** translation offsets (X, Y). Z-offset comes from config. The code reads this and adds it to labels when Radar frame is requested.

#### 4. Paper States Transform Direction
> "The 3D bounding boxes can be easily transformed **from** the Lidar **to** the Radar coordinate frame..."
Source = LiDAR frame, Target = Radar frame.

#### 5. Annotation Workflow
Paper Section 3.3: *"Since the 4DRT high-dimensional representation is unintuitive to human, we leverage the high-resolution LPC so that the annotators can accurately label the 3D bounding boxes of objects on the road in the visualized point clouds."*
Annotators **look at LiDAR point clouds** to draw boxes → labels are in LiDAR frame by construction.

#### 6. If Labels Were Already in Radar Frame
- No transform would be needed for `type_coord == 1`
- `calib_radar_lidar.txt` would not be read for labels
- Paper would not say "transformed **from** Lidar **to** Radar"

**All evidence chains converge: Labels on disk = LiDAR frame.**

---

## 5. Unified Frame for Fusion

### Common Reference Frame
**Radar coordinate frame** (origin at front grill, X forward, Y left, Z up).

### How Multi-Sensor Alignment is Achieved

| Sensor | Native Frame | Runtime Transform to Radar-Frame Transform | When Applied |
|--------|-------------|----------------------|--------------|
| Radar (tesseract/cube) | Radar | Identity (none) | N/A |
| LiDAR (os2-64/os1-128) | LiDAR | Translation from `calib_radar_lidar.txt` | `__getitem__` / `get_pc_lidar()` |
| Cameras | Camera | `radar2camera` from `T_params_seq` | `__getitem__` / `collate_fn` |
| Annotations | LiDAR | Same translation as LiDAR | `__getitem__` / `get_label_bboxes()` |

### Fusion in Network Input

**Detection datasets** (`kradar_detection_v1_0.py`): Single-sensor or pre-voxelized BEV — fusion happens in the network (e.g., RTNH uses 4DRT as primary input).

**Fusion dataset** (`kradar_fusion_v1_0.py`): Returns all sensors in radar frame:
```python
def __getitem__(self, idx):
    dict_item = self.list_dict_item[idx]
    dict_item = self.get_ldr64(dict_item)        # LiDAR → radar frame
    dict_item = self.get_rdr_polar_3d(dict_item) # Radar polar → radar Cartesian
    dict_item = self.get_rdr_sparse(dict_item)   # Radar sparse points
    dict_item = self.get_camera_img(dict_item)   # Images + intrinsics/extrinsics
    dict_item = self.filter_roi(dict_item)       # ROI filtering in radar frame
    return dict_item
```

**Collate function** (`collate_fn`, lines 1264–1360) builds batched tensors with:
- `camera_intrinsics`: [B, N_cam, 4, 4]
- `camera2radar`: [B, N_cam, 4, 4]  (extrinsics)
- `radar2image`: [B, N_cam, 4, 4]   (projection matrix)
- `radar_aug_matrix`: [B, 4, 4] (identity by default)

**No ego-frame transformation exists in the training pipeline.** The radar frame serves as the de facto "ego" frame because the radar is mounted at the front center of the vehicle.

---

## 6. Code Citations Summary

| Component | File | Key Functions/Lines |
|-----------|------|---------------------|
| LiDAR loading + transform | `datasets/kradar_detection_v1_0.py` | `get_pc_lidar()` (514–532) |
| LiDAR loading (fusion) | `datasets/kradar_fusion_v1_0.py` | `get_ldr64()` (754–780), `get_ldr64_from_path()` (782–799) |
| Label loading + transform | `datasets/kradar_detection_v1_0.py` | `get_tuple_object()` (306–395), `get_label_bboxes()` (397–412) |
| Label loading (fusion) | `datasets/kradar_fusion_v1_0.py` | `get_label()` (330–458) |
| Radar tensor loading | `datasets/kradar_detection_v1_0.py` | `get_tesseract()` (417–441) |
| Radar cube loading | `datasets/kradar_detection_v1_0.py` | `get_cube()` (443–497) |
| Camera calibration loading | `utils/util_calib.py` | `get_matrices_from_dict_calib()` (56–80), `save_calibration_matrix_in_npy()` (138–163) |
| Camera params (T_params) | `datasets/kradar_fusion_v1_0.py` | `get_t_params_all_seqs()` (539–552) |
| Camera projection matrices | `datasets/kradar_fusion_v1_0.py` | `collate_fn()` lines 1326–1330 |
| Calibration file format | `info_calib/calib_radar_lidar.txt` | Line 2: `frame_diff, X, Y, Z` |
| Config reference sensor | `datasets/kradar_fusion_v1_0.py` | Line 74: `t_params.ref_sensor = 'radar'` |

---

## 7. Open Questions / Ambiguities

| Question | Status | Notes |
|----------|--------|-------|
| Is there **any** ego-frame used in evaluation metrics (KITTI eval)? | **Unclear** | `utils/kitti_eval/` exists but not fully traced. KITTI uses camera frame. |
| Does `calib_radar_lidar.txt` Z-offset account for LiDAR height difference (OS2-64 vs OS1-128)? | **Likely yes for OS2-64** | Paper says OS2-64 is "lower height", OS1-128 "higher height" on roof. Same calib file used for both in code. |
| Are camera images used in training **distorted** or **undistorted**? | **Undistorted (cropped)** | Config `cam_dir.load = 'cropped'` loads pre-undistorted images. |
| Is there a **LiDAR→Radar rotation** (not just translation)? | **No** | Paper Appendix D.2: "no theoretical difference in pitch angle"; code only applies translation. |
| What is the **exact radar frame origin**? | **Front grill center** | Paper Fig 3: "4D Radar is attached to the front grill" |
| Does the **radar cube grid** align with radar frame axes? | **Yes** | `arr_x_cb = [0, 100]` (forward), `arr_y_cb = [-80, 80]` (left/right), `arr_z_cb = [-30, 30]` (up/down) |

---

## 8. Critical Inconsistencies Flagged

### ⚠️ LiDAR Height Calibration (OS2-64 vs OS1-128)
The code applies **the same `calib_radar_lidar.txt` translation** to both LiDARs (see `get_ldr64()` — no sensor-specific calib). But the paper states they are at **different heights** on the roof. This could introduce a systematic Z-offset error for OS1-128.

### ⚠️ Camera Extrinsic Reference
`T_params_seq` provides `radar2camera` directly. But `util_calib.py` computes `T_ldr2cam` (LiDAR→Camera). Since LiDAR→Radar is translation-only, these should be consistent:
```
radar2camera = ldr2cam @ inverse(radar2ldr)
```
This should be verified for calibration consistency.

### ⚠️ No Ego Frame in Pipeline
If downstream tasks (e.g., motion prediction, tracking in world coordinates) need ego/world frame, **no transformation is provided in the dataset**. The radar frame is vehicle-fixed but **not at the vehicle center** (it's at the front grill). This is a ~2-3m forward offset from typical ego origin (rear axle center).

---

## 9. Conclusion

**K-Radar uses the Radar sensor frame as the canonical coordinate system.** All sensor data and annotations are transformed to this frame at load time:

1. **Radar data** — already in radar frame (no transform)
2. **LiDAR point clouds** — stored in LiDAR frame, translated to radar frame using `calib_radar_lidar.txt` (translation only)
3. **Annotations** — stored in LiDAR frame, same translation to radar frame
4. **Camera images** — raw distorted on disk; undistorted+cropped versions pre-computed. Extrinsics (`radar2camera`) provided per-sequence for projection.

**No ego-vehicle frame transformation occurs in the training/inference pipeline.** The radar frame (front grill, X forward) serves as the fusion reference frame. For applications requiring a centered ego frame, an additional fixed transform would be needed.