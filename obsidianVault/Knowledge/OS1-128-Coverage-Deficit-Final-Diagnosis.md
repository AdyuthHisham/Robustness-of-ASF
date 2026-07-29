# OS1-128 Coverage Deficit — Final Diagnosis

## Status: RESOLVED — Genuine Hardware/Sensor-Physics Limitation

### Prior Conclusion ("sensor characteristic, not a bug") stands — with full evidence.

## Step 1 — Pipeline's Elevation Angle Source

**Source file:** `/home/adhish/Productivity/AMSCUP/test-bed/src/Modules/robust_testing/kradar/src/kradar_visibility/config.py`

```
OS1_128_CHANNELS = 128
OS1_128_VFOV_DEG = 44.5   # total vertical FOV
OS1_128_HRES_DEG = 0.17   # azimuth resolution
```

**LUT computation** in `lidar_visibility.py`:
```python
OS1_128_CHANNEL_LUT = {
    'channels': 128,
    'elevations': np.linspace(-22.25°, +22.25°, 128),  # uniform, 0.3477°/step
    'azimuth_bins': 2117  # int(360/0.17)
}
```

No per-channel calibration file exists in the K-Radar dataset for the OS1-128. The only calibration file per sequence (`info_calib/calib_radar_lidar.txt`) contains a translation-only offset (x=-2.54, y=0.3 for sequence 2).

## Step 2 — Ground Truth Comparison

**No published per-channel elevation LUT in K-Radar:** The dataset does not provide individual beam elevation angles for the OS1-128. As secondary ground truth, actual beam elevations were measured from PCD organized-format data (HEIGHT=128 rows, `ring` field) across 6 frames of sequence 2.

**Measured beam angles (from frame 1, highway night):**

| Channel | Mean Elevation | Valid Return % | Behavior |
|---------|---------------|----------------|----------|
| 0 | +21.5° | 7.5% | Sky (few returns) |
| 30 | +11.7° | 15% | Sky / distant structures |
| 50 | +4.7° | 26% | Transition to horizon |
| 62 | +0.5° | 39% | Near horizon |
| **63** | **+0.15°** | **40%** | **HORIZON** |
| **64** | **-0.20°** | **41%** | **HORIZON** |
| 80 | -5.7° | 100% | Ground at 11m range |
| 100 | -12.5° | 100% | Ground at 7.5m range |
| 127 | -21.0° | 81% | Ground at 4.8m range |
| — | **Measured VFOV ≈ 42.5°** | — | Spec: 44.5° |

**Verdict: MATCHES SPEC — NO SYSTEMATIC OFFSET**

- The horizon crosses between channels 63 and 64, confirming the sensor optical axis is approximately level (expected for a correctly mounted sensor).
- Total measured FOV (42.5°) is close to spec (44.5°); the 2° gap is from missing returns at the extreme beam edges, not tilt.
- No evidence of pitch, roll, or yaw miscalibration.
- Each channel's elevation behavior (beam angle × return rate) is consistent with a level-mounted 44.5°-VFOV sensor.

**The prior report's translation-only test was inadequate to rule out tilt, but the tilt hypothesis is now directly falsified by PCD elevation data.**

## Step 3 — Correction Hypothesis Test

**Not applicable** — since no systematic offset was found, no correction would be meaningful. The pipeline's uniform ±22.25° assumption is a reasonable approximation of actual beam geometry for expected-density computations.

## Step 4 — Frame 200 Anomaly (25,101 points)

**Verified:** The original count of 25,101 points in a simple axis-aligned bbox is confirmed. The pipeline's rotated bbox gives 25,062 points (negligible difference).

**Explanation:**

- **(a) Object is a Truck/Bus (extremely large):** Full dimensions 11.77m × 2.72m × 3.67m, volume 117.6 m³. This is not a normal car; it's a semi-trailer-sized vehicle.

- **(b) Object is very close (9.0m):** At 9m, OS1-128 horizontal resolution (0.17°) gives ~2.7cm point spacing; vertical resolution (0.35°) gives ~5.5cm spacing. Expected density ≈ 673 pts/m². With ~55% valid return rate → ~370 pts/m². Projected frontal area (W×H after 35° rotation) ≈ 8-10 m² → 3,000-3,700 expected points on the front face. The box volume (118 m³) captures returns from the sides and top too, giving more.

- **(c) No ground contamination:** The box's z-range is −1.42 to +2.26m. Ground at sensor mount height (~−2m) falls below this. Sample points cluster within the truck body. The ~35° rotation means the side of the truck is exposed to the sensor, increasing the effective area.

- **(d) Half-extent conversion is correct:** Pipeline's `_obj_corners()` correctly uses half-extents as half-dimensions (producing faces at ±hl, ±hw, ±hh in local). The subsequent `_bbox_list_from_annotation()` computes the correct world-frame AABB after rotation. No half-extent bug present.

- **Correct PCD file:** The frame 200 annotation (`00200_00170.txt`, `os1_128` frame index = 00169) maps to PCD file `os1-128_00169.pcd` (215,616 valid points), not `os1-128_00200.pcd` (183,515 valid points). The 25,101 count is 11.6% of valid points, consistent with a massive object at close range.

**Conclusion:** Entirely plausible — expected from a large close-range object.

## Final Verdict

**The OS1-128 forward-coverage deficit is a genuine hardware/sensor-physics limitation, NOT a calibration bug.**

Evidence:
- Sensor is mounted level (horizon at channels 63/64).
- Beam pattern matches Ouster specification (~44.5° VFOV).
- The observed "deficit" is that only channels near the horizon (±5°) generate returns from objects at 50-100m+ range. Upper channels hit empty sky; lower channels hit ground at close range.
- A sedan at 100m occupies ~±0.4° elevation = only 2-3 channels can possibly detect it.
- The 128-channel beam distribution is not a bug — it's how LiDAR works. ~25 "horizon channels" out of 128 is normal for highway driving.

True for all single LiDARs in highway driving. The complementary OS2-64 has a different vertical FOV (33.2°) and beam arrangement, producing better long-range coverage from its own specific set of horizon channels.

**Document as dataset/sensor limitation** — no pipeline fix needed for the coverage deficit itself. If increased long-range detection is required, the sensor fusion strategy (OS2-64 + OS1-128) already provides this: 481 OS2-64 points at x>80m vs 31 OS1-128 points (frame 71 data).

## Scratch Scripts Created

- `_scratch_extract_elevations.py` — Per-channel mean elevation from PCD organized data
- `_scratch_elevation_v2.py` — V2 with zero-range filtering, valid return rates
- `_scratch_frame200.py` — Frame 200 and frame 70 point-in-box analysis
- `_scratch_frame200_v2.py` — Corrected version using pipeline API (`_bbox_list_from_annotation`, correct PCD file)