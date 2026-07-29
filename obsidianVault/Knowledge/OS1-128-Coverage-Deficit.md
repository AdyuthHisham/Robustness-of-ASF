# OS1-128 Long-Range Coverage Deficit

## Root Cause of lidar128_visible=False at Score=0.0

Investigation performed on sequence 2, frames 00069-00072 and 5 additional frames (100, 200, 300, 400, 450). Full analysis: 10 frames checked, 4 with objects.

### Finding

The OS1-128 point cloud (Ouster OS1-128, 128-channel) has **fundamentally sparse long-range forward coverage**. This is a sensor/data characteristic, not a code processing bug.

**Key data point**: frame 00071 (os1-128_00040.pcd) has only **31 points with x>80m** forward direction, with **max y-coverage of 18.2m**. The object at (95.6, 24.1, 0.07) has y=24.1, which is outside the OS1-128's forward y-coverage by ~6m.

### Evidence

| Metric | OS1-128 | OS2-64 |
|--------|---------|--------|
| Valid points per frame | 144,776 | 80,388 |
| Points within 10m | 85,554 (59%) | 26,482 (33%) |
| Points within 30m | 133,259 (92%) | 60,698 (76%) |
| **Points with x>80m** | **31** | **481** |
| Max y of x>80m points | 18.2m | 81.4m |
| Points in bbox at (95.6,24.1) | 0 | 8 |

Cross-cloud analysis: **70% of OS2-64 points have an OS1-128 neighbor within 0.5m** — frames ARE aligned, no coordinate mismatch.

Archive calibration offset `KRADAR_LIDAR_OFFSET=(-2.54, 0.3, 0.7)` makes no difference when applied (0→0 points in bbox).

Ring-by-ring analysis: OS1-128 channels 0-49 point mostly at sky (very few returns), channels 50-65 cover forward horizon (~15 of 128 channels), channels 66-127 point at ground (near-range only). Result: only ~12% of channels contribute to long-range forward detection.

### Affected frames and objects

| Frame | Object Range | OS1 pts in bbox | OS2 pts in bbox |
|-------|-------------|-----------------|-----------------|
| 70 | 100.8m (y=24.1) | 0 | 8 |
| 71 | 98.6m (y=24.1) | 0 | 8 |
| 72 | 96.0m (y=24.3) | 0 | 7 |
| 100 | 33.2m (y=24.8) | **6** | 94 |
| 200 | 9.0m (y=-3.7) | **25101** | 17512 |

**Bug is OS1-128 specific**: OS2-64 has 15x more long-range forward points per frame. Same sensor parameters code path, same scoring function — the difference is purely in the raw data density at long range.

### Channels/rings breakdown

Detailed ring-by-ring analysis shows a clear pattern of valid-return distribution across the 128 channels.

See `_diagnose_lidar128.py` output for ring-level details.

## Final Diagnosis (2026-07-28)

**Verdict: GENUINE HARDWARE/SENSOR-PHYSICS LIMITATION — not a calibration bug.**

The full tilt/pitch hypothesis was investigated and falsified. The sensor is mounted level (horizon at channels 63-64) and the beam distribution matches Ouster OS1-128 specification. The coverage deficit is a fundamental consequence of LiDAR geometry in highway environments — see [[OS1-128-Coverage-Deficit-Final-Diagnosis]] for the complete evidence, including:
- Per-channel elevation angle extraction from PCD organized data
- Valid return rate by channel band (0-19: 9%, 20-49: 10%, 50-65: 30%, 66-99: 90%, 100-127: 88%)
- Frame 200 anomaly (25,101 points) explained: large truck at 9m range
- Ground-truth angle comparison: MATCHES SPEC, no systematic offset found