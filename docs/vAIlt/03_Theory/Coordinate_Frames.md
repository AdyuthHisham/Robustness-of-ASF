# Coordinate Frames

K-Radar uses the **radar sensor frame** as the canonical fusion frame — not an ego-vehicle frame. Origin at the front grill, X forward, Y left, Z up. All other sensors and annotations are transformed to it at load time; **no ego-frame transform exists anywhere in the pipeline**.

## Per-sensor frame and transform

| Sensor | Native frame (on disk) | Transform to radar frame | Applied where |
|---|---|---|---|
| Radar (tesseract / `radar_zyx_cube`) | Radar (already canonical) | Identity | N/A |
| LiDAR (OS2-64, OS1-128) | LiDAR (native Ouster frame) | **Translation only**, from `info_calib/calib_radar_lidar.txt` | `get_pc_lidar()` / `get_ldr64()` |
| Annotations (`info_label_rev2`) | LiDAR (same as LiDAR points — see proof below) | Same translation as LiDAR | `get_tuple_object()` / `get_label()` |
| Cameras (ZED2i ×4, stereo) | Camera | `radar2camera` (4×4), per-sequence from `T_params_seq/{seq}/` pickle | Projection only, not stored-data mutation |

The LiDAR→radar transform is translation-only (no rotation) — the K-Radar paper (Appendix D.2) states sensors are mounted "precisely perpendicular to the ground," so pitch difference is assumed zero. Reported calibration error: max 0.5 cm. **Both** OS2-64 and OS1-128 use the same calibration file despite being at different roof heights (flagged below).

## Proof that annotations are natively in LiDAR frame, not radar frame

This matters for anyone hand-rolling a new sensor into the pipeline — it's not obvious from the parquet output alone, which is already in radar frame.

1. Code comment, `kradar_detection_v1_0.py`: *"labels are represented on Ldr coordinate"*.
2. The transform is conditional on `type_coord`: `type_coord==1` (radar) applies the `calib_radar_lidar.txt` translation to labels; `type_coord==2` (LiDAR) applies none — proving the native label frame is LiDAR.
3. The calibration file is literally named `calib_radar_lidar.txt` and its docstring direction is LiDAR→Radar.
4. Paper: *"3D bounding boxes can be easily transformed from the Lidar to the Radar coordinate frame..."* — direction stated explicitly.
5. Annotation workflow: annotators drew boxes on **LiDAR point-cloud visualizations** (the 4DRT tensor is described as "unintuitive to human"), so boxes are LiDAR-frame by construction.

## Radar cube grid (defines the pipeline's voxel mapping)

```
arr_x_cb = [0, 100) m, step 0.4    (forward only)
arr_y_cb = [-80, 80) m, step 0.4   (left/right)
arr_z_cb = [-30, 30) m, step 0.4   (up/down)
```
FOV: azimuth ±53.5° (107° total), elevation ±18.5° (37° total), range 0–118 m. This grid is what [[Visibility_Formulas]]'s radar voxelization maps world coordinates onto.

## Annotation label format

```
*, R, 1, Sedan, 47.391, -2.104, -0.425, -0.340, 1.641, 0.807, 0.710
```
Fields: `*`, sensor_identify, tracking_id, class, **X, Y, Z, Theta(deg), half_length, half_width, half_height** — meters and degrees, half-dimensions (code correctly doubles them for `obj_length/width/height`, no discrepancy there). Only objects with positive X (forward of ego) are annotated; range 120 m longitudinal × 80 m lateral.

## Flagged inconsistencies (not resolved in the dataset, worth carrying into Limitations)

- **LiDAR height calibration**: the same `calib_radar_lidar.txt` translation is applied to both OS2-64 and OS1-128 despite the paper stating they sit at different roof heights — code has no sensor-specific Z-offset. Possible systematic Z-error for one of the two LiDARs.
- **Camera extrinsic consistency unverified**: `T_params_seq` supplies `radar2camera` directly, while `util_calib.py` independently computes `T_ldr2cam` (LiDAR→camera). Since LiDAR→radar is translation-only, `radar2camera` should equal `ldr2cam @ inverse(radar2ldr)` — this has not been numerically cross-checked against the dataset's actual stored matrices.
- **No ego frame**: downstream tasks needing a vehicle-centered frame (motion prediction, planning) get no transform from this dataset. The radar frame is vehicle-fixed but offset ~2–3 m forward of a typical ego origin (rear-axle center).

## Source

- `docs/COORDINATE_FRAME_ANALYSIS.md` (373 L, canonical — full code citations with line numbers for every transform, open-questions table, K-Radar paper cross-references)
- `docs/vAIlt/05_Implementation/K-Radar_Coordinate_Frame_Analysis_Report.md` (earlier vault import of the same source — folded in here)
- K-Radar paper (arXiv:2206.08171), Appendix D.1–D.2
- `repos/K-Radar/datasets/kradar_detection_v1_0.py`, `kradar_fusion_v1_0.py`, `utils/util_calib.py`
