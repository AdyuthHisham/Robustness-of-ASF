# Visibility Formulas

Per-sensor visibility scoring methodology implemented in `kradar_visibility` (`test-bed/src/Modules/robust_testing/kradar/src/kradar_visibility/`). Covers radar, LiDAR (×2), and camera (×4), plus the (implicit) fusion aggregation. All formulas below are transcribed from the pipeline code, not the earlier design doc — see **Discrepancy Notes** for where the two disagree.

## LiDAR — count / expected-density ratio

**Raw point count:**
```
N_points = Σᵢ [Pᵢ ∈ bbox]
```
`bbox` is the axis-aligned bounding box (AABB) enclosing the 8 rotated corners of the object annotation — the rotated box is reduced to its AABB before the point-in-box test, which over-counts near corners when `theta ≠ 0`.

**Expected density** (fixed per sensor, not per-object extent). VFOV and
HRES values corrected to match the K-Radar dataset paper
(`docs/lit_survey/noise_addition/kradar.pdf`, p.12, Table 7) — see
[[../06_Results/lidar128-legacy-remap-visibility-anomaly|LiDAR128 Legacy-Remap Visibility Anomaly]]
for the discrepancies this fixed:
- OS2-64 VFOV was 33.2°, paper says 22.5°; OS1-128 was 44.5°, paper says 45°.
- OS2-64/OS1-128 HRES (azimuth resolution) was 0.35°/0.17° respectively —
  wrong on both counts. Table 7's resolution row is `[0.1cm range res,
  0.18° azimuth res, 0.35° elevation res]`, **identical for both sensors**.
  0.35° is the elevation resolution (confirmed via `VFOV/channels`: both
  `22.5/64` and `45/128` ≈ 0.35°), not OS2-64's azimuth res. Correct azimuth
  res for both sensors is 0.18°.
```
E_OS2  = (64  × 22.5 / 360) × (360 / 0.18) ≈ 8,000   points/m³
E_OS1  = (128 × 45.0 / 360) × (360 / 0.18) ≈ 32,000  points/m³
```

**Sparsity score:**
```
S_lidar = clip(N_points / (E × V_bbox), 0, 1)
```

**Gating:** `visible = True` iff `N_points > 0` AND center within range (FOV limit `[-200,200]×[-200,200]` m is effectively unbounded). Range cutoff is **per-sensor**, matching Table 7: `[0, 240]` m for OS2-64, `[0, 120]` m for OS1-128 (previously both shared a single `[0, 120]` m cutoff, under-counting OS2-64 detections beyond 120m). The pipeline runs this twice per frame — once for OS2-64, once for OS1-128 — producing independent `lidar64_*` / `lidar128_*` columns. **No occlusion handling**: the point-in-box test counts all points geometrically inside the bbox regardless of whether they belong to an occluder.

## Camera — 8-corner projection → area × centrality

**Projection:** `P_image = K · (T_radar2camera · P_radar)[0:3] / Z`, applied to all 8 rotated bbox corners, per camera direction (front/left/right/rear), per stereo half (1280×720 each).

**Clipped area fraction and centrality:**
```
A_clipped = max(0, u_max_c − u_min_c) × max(0, v_max_c − v_min_c)     (clipped to image bounds)
d_norm    = (|u_c − 640| + |v_c − 360|) / 2000
C         = 1 − d_norm
V_camera  = 0.7 × (A_clipped / 921600) + 0.3 × C
```
Weights `w₁=0.7` (area), `w₂=0.3` (centrality) — `config.py`. **Stereo handling:** each direction has two sub-cameras; the pipeline takes the **max** score across the pair. **Gating:** `visible=True` iff all 8 corners have `z_cam > 0` (in front of camera) AND `A_clipped > 0`. No occlusion handling in the default build (an optional LiDAR depth-buffer check exists but is flag-gated off).

## Radar — SNR-weighted power density on `radar_zyx_cube`

```
P_dB      = 10·log₁₀(P_linear)                  (P_linear > 0; sentinel −100 dB otherwise)
N_dB      = median(P_dB[all valid cells in cube])
V_radar   = clip( mean_{c∈bbox}( max(0, P_dB(c) − N_dB) ) / 20.0 , 0, 1 )
```
`DB_HEADROOM = 20 dB` — mean SNR ≥ 20 dB above the per-frame noise floor scores 1.0. Uses `radar_zyx_cube/` (Doppler-collapsed 3D cube), **never** the full 4DRT tesseract (64M cells/frame — out of budget for the CPU-only pipeline; see [[04_Design/System_Architecture|System Architecture]]).

**Gating (independent of score):**
```
radar_fov_in   = |azimuth| ≤ 53.5° AND |elevation| ≤ 18.5°     (107° × 37° cone)
radar_range_in = √(x²+y²+z²) ≤ 118 m
```

## Fusion — implicit, no explicit fused score

There is **no fused visibility column** in the output schema. The pipeline exposes:
```
num_sensors_visible = Σ I(sensor_visible)
primary_sensor       = argmax_{s: visible}(sensor_score[s])
```
Selection is raw-score comparison with **no explicit sensor weighting** — LiDAR 128 tends to win at close range (highest point density), radar at long range (LiDAR sparse, radar SNR adapts), side cameras for lateral objects. A missing sensor file degrades to `visible=False, score=0.0` (logged, never raises) and is automatically excluded from `primary_sensor`.

## Selected vs. rejected methods

| Sensor | Selected | Rejected alternatives | Why rejected |
|---|---|---|---|
| Radar | B: SNR-weighted density | A: binary cell-count threshold; C: full 4DRT | A fails monotonic-distance-decrease (fixed threshold ignores range-dependent noise floor); C violates the 64M-cell/frame memory budget |
| LiDAR | B: count/expected-density ratio | A: raw point count (kept only as the `*_points_count` column); C: voxel occupancy ratio | C's extra voxelization pass wasn't justified — weather dominates sparsity variance more than spatial-coverage resolution would capture |
| Camera | B: 8-corner area+centrality | A: center-point projection only; C: B + LiDAR depth-buffer occlusion | A can't produce a continuous score; C adds real per-frame cost (sparse LiDAR projection + z-test) not required to pass the test suite |

## Discrepancy notes (design doc vs. implementation — code is authoritative)

1. **LiDAR expected density**: design doc describes a per-object angular-extent formula; the implementation uses a **fixed constant** per sensor type (`E_OS2`, `E_OS1` above), described in code comments as an approximation for "a 1 m² surface."
2. **Radar noise floor**: design doc says median of cells *outside* annotated bboxes; implementation uses median of **all valid cells including inside bboxes** — simpler, no per-frame bbox-union needed.
3. **Camera stereo**: design doc implies one camera per direction; implementation has two stereo sub-cameras per direction, max-scored — a practical addition not in the original spec.

## Source

- `docs/VISIBILITY_FORMULAS_AND_METHODS.md` (514 L, canonical — full formula derivations, methodology comparison table, threshold reference table, verification test cross-references)
- `test-bed/src/Modules/robust_testing/kradar/src/kradar_visibility/{radar,lidar,camera}_visibility.py`, `pipeline.py`, `config.py` (ground truth for all formulas above)
- `docs/vAIlt/05_Implementation/K-Radar_Multi-Sensor_Visibility_Calculation_Formulas_and_Methodologies.md` (earlier vault import of the same source — content folded in here, not separately maintained)
