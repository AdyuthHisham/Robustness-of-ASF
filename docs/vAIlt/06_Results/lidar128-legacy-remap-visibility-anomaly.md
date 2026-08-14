# LiDAR128 Legacy-Remap Visibility Anomaly

#kradar_visibility #diagnostic

## Finding

`lidar128_visible=True` with `lidar128_points_count=0` and `lidar128_sparsity_score=0.0`
occurs whenever `sensor_identify='L'` (the legacy combined-LiDAR label, vs. the
per-sensor `L1`/`L2` labels). This is **not** a bug in the per-sensor scoring
formula — `lidar_visibility.py`'s own gating (`visible = in_fov and in_range
and count > 0 and final_score > 0.0`) is correct in isolation.

## Root cause

`pipeline.py` (`compute_visibility_for_frame`), the legacy-label remap:

```python
if obj.sensor_identify == 'L':
    lidar64_original = lidar64_visible
    lidar128_original = lidar128_visible
    lidar64_visible = lidar64_original or lidar128_original
    lidar128_visible = lidar64_original or lidar128_original
```

For `'L'`-labeled objects, `lidar128_visible` gets OR'd with `lidar64_visible`
regardless of whether OS1-128 itself detected anything. So a `'L'` object seen
only by OS2-64 (e.g. 12 points) gets `lidar128_visible=True` even though OS1-128
independently saw zero points and scored 0.0. A consumer filtering rows on
`lidar128_visible` alone (without also checking `points_count`/`score`) will
silently include detections OS1-128 never actually confirmed.

## Data evidence

**351-row sample** (`output/output_with_env_density.parquet`, sequences
1/9/13/23/38): 8 affected rows.

| sequence_id | frame_idx | obj_tracking_id |
|---|---|---|
| 9 | 28 | 7 |
| 9 | 35 | 12 |
| 9 | 36 | 12 |
| 13 | 40 | 105 |
| 13 | 43 | 108 |
| 13 | 44 | 108 |
| 13 | 45 | 109 |
| 13 | 46 | 109 |

**Full sequence 9 alone** (1672 rows, all frames, not just the 20-frame-limited
sample): **58 affected rows** — confirms this scales roughly linearly with
row count and is a real, dataset-wide pattern, not sample-specific noise.
Avoid trusting `lidar128_visible` in isolation for `sensor_identify='L'`
objects when doing full-dataset analysis; always cross-check
`lidar128_points_count > 0` or the new confirmed column below.

## Fix applied

Added `lidar64_visible_confirmed` / `lidar128_visible_confirmed` columns
(`pipeline.py`, `config.OUTPUT_SCHEMA`) — capture each sensor's own
pre-remap visibility verdict, so `lidar128_visible_confirmed=False` while
`lidar128_visible=True` flags exactly this case. Verified against the full
sequence-9 run: all 58 affected rows correctly show
`lidar128_visible_confirmed=False`, `lidar128_points_count=0`.

**Schema change**: two new columns added to `config.OUTPUT_SCHEMA` — existing
`primary_sensor`/`num_sensors_visible`/`ghost_flag` computations were left
using the original (remapped) `lidar64_visible`/`lidar128_visible` for
backward compatibility; only the new `_confirmed` columns change behavior.

**Not yet done**: `output_with_env_density.parquet` has not been
regenerated with the new columns — this fix has only been verified via an
in-memory run of sequence 9, not written to disk.

## Related fix: LiDAR sensor-spec dimension errors (same investigation)

While tracing the expected-density constants that feed `lidar*_sparsity_score`,
found the OS2-64/OS1-128 VFOV and range constants didn't match the K-Radar
dataset paper (`docs/lit_survey/noise_addition/kradar.pdf`, p.12, Appendix B,
Table 7 "Sensor suite details"):

| constant | was | paper (Table 7) | fixed to |
|---|---|---|---|
| `OS2_64_VFOV_DEG` (elevation FOV) | 33.2° | 22.5° | 22.5° |
| `OS1_128_VFOV_DEG` (elevation FOV) | 44.5° | 45° | 45.0° |
| `OS2_64_HRES_DEG` (azimuth res) | 0.35° | 0.18° | 0.18° |
| `OS1_128_HRES_DEG` (azimuth res) | 0.17° | 0.18° | 0.18° |
| OS2-64 max range | 120m (shared `_LIDAR_RANGE`) | 240m | `OS2_64_MAX_RANGE_M=240.0` |
| OS1-128 max range | 120m (shared `_LIDAR_RANGE`) | 120m | `OS1_128_MAX_RANGE_M=120.0` (unchanged) |

Table 7's resolution row is `[0.1cm range res, 0.18° azimuth res, 0.35°
elevation res]`, **identical for both LiDARs**. Confirmed 0.35° = elevation
res via `VFOV/channels`: `22.5/64 ≈ 0.35°` and `45/128 ≈ 0.35°`, both land on
the same value — so the *actual* per-sensor azimuth resolution (what
`HRES_DEG` is used for in code: `azimuth_bins = 360/HRES_DEG`) is 0.18° for
both sensors, not the previous 0.35°/0.17° (which were wrong on both value
and per-sensor-difference — the paper gives one shared azimuth-res number).

Applied in `config.py` (new `OS2_64_MAX_RANGE_M`/`OS1_128_MAX_RANGE_M`
constants, corrected `VFOV_DEG` and `HRES_DEG` values) and `pipeline.py`
(`_LIDAR_RANGE` split into `_LIDAR_RANGE_OS2`/`_LIDAR_RANGE_OS1`, passed to
the respective `calculate_lidar_visibility()` calls). All active
(non-archived) vault docs referencing these constants updated to match:
`Visibility_Formulas.md`, `Config_Reference.md`, `KRadar_configpy_Reference.md`,
`K-Radar_Multi-Sensor_Visibility_Calculation_Formulas_and_Methodologies.md`,
`Sensor_Sparsity_and_Noise_Injection.md`. `scripts/benchmark_precomputation.py`
updated to match (dev-only script, not part of the test suite). Full
`pytest` suite (48 passed, 19 skipped — skips are pre-existing/unrelated)
still green after both rounds of changes.

**This changes computed values, not just gating**: `_EXPECTED_OS2` ends at
≈8,000 points/m³ (was ≈6,074 before either fix; dipped to ≈4,114 after the
VFOV-only fix, now corrected further by the HRES fix), `_EXPECTED_OS1` ends
at ≈32,000 points/m³ (was ≈33,459). Net effect on `lidar64_sparsity_score`
vs. the original pre-fix code is a modest *decrease* (higher expected
density than originally coded), not the large increase the VFOV-only
interim fix implied — the two fixes partially offset each other. OS2-64
objects between 120–240m — previously marked `in_range=False` and zeroed
out — will now be scored regardless. **`output_with_env_density.parquet`
(and any other existing output) is stale relative to this fix and should be
regenerated before
further analysis relies on `lidar64_sparsity_score` or far-range OS2-64
visibility.**

## Related fix: `config.OUTPUT_SCHEMA` column-order drift

Found while re-verifying: `OUTPUT_SCHEMA` in `config.py` listed columns in a
different order than `pipeline.py`'s row dict actually builds them —
`obj_theta` was out of position relative to `obj_length/width/height`, and
`weather`/`environment`/`time_of_day`/`frame_object_count` were listed near
the top (right after `sensor_identify`) but the row dict actually appends
them at the very end (after `primary_sensor`, before `ghost_flag`). This
predates all the fixes above — not introduced by this session's earlier
changes (confirmed via `git diff`).

Harmless in practice (`polars.DataFrame(list[dict])` keys columns by name,
not list position, so actual Parquet output was never affected), but
`OUTPUT_SCHEMA` is meant to be the single source of truth for the schema
per `CLAUDE.md`, so it should match reality. Reordered `OUTPUT_SCHEMA` to
match the row dict exactly — verified programmatically (49/49 columns,
position-for-position match). `pytest`: 48 passed / 19 skipped, unchanged.

## Related fix: mirrored occlusion-check corners (real correctness bug)

Found while explaining `occluded_fraction`/`confidence` in detail:
`_compute_occlusion_fraction_from_range_image` (`lidar_visibility.py`) built
its 8 bbox corners as `[-xmin, -ymin, -zmin], ...` instead of
`[xmin, ymin, zmin], ...`. The docstring/comment claimed this was valid
because "the bbox is centered at origin," but `bbox` is the object's actual
**world-frame** AABB (`_bbox_list_from_annotation()` in `pipeline.py`) —
negating the mins only reconstructs the true corners when `xmin == -xmax`
(box symmetric about the world origin), which is never true for a real
K-Radar object sitting tens of meters from the sensor. The corrupted corners
point in roughly the opposite direction from the sensor, so the
azimuth/elevation lookup samples the wrong bin of the per-frame range image
entirely — silently producing wrong occlusion verdicts for essentially
every real object.

**Confirmed with a real object** (sequence 9, first label file,
`bbox ≈ [x: 10.5–15.2, y: -11.9–-9.7, z: -1.49–-0.14]`): buggy corners gave
`occluded_fraction=0.0, confidence=0.375`; corrected corners gave
`occluded_fraction=0.167, confidence=0.75` — same object, same range image,
different (correct) bins sampled.

**Why existing tests (VER-27/28) didn't catch it**: both use a toy bbox
`[4.5, 5.5, -0.5, 0.5, -0.5, 0.5]` where `ymin=-ymax` and `zmin=-zmax` are
symmetric about zero by construction, coincidentally masking most of the
bug; the tests also only assert the final score lands in `[0,1]` and moves
in the expected relative direction, not that the underlying geometry is
correct.

**Fix**: corners now built directly from `xmin/xmax/ymin/ymax/zmin/zmax`,
no negation. Added `VER-33`
(`test_ver33_occlusion_corners_not_mirrored_for_off_origin_bbox` in
`test_verify.py`) — places a bbox far from the origin, puts a close occluder
in the *correct* forward direction, and asserts the score is actually
discounted; this fails against the pre-fix code (confirmed) and passes
against the fix. Full `pytest`: 49 passed (48 + new test) / 19 skipped, no
regressions.

**Impact**: this affects the occlusion term of `lidar64_sparsity_score` /
`lidar128_sparsity_score` for any row where `occluded_fraction`/`confidence`
were nonzero — i.e. most real objects, not an edge case. Distinct from (and
larger than) the VFOV/HRES/range constant fixes above, since it corrupts
the occlusion computation itself rather than a scaling constant feeding it.
`output_with_env_density.parquet` was already flagged stale by the earlier
fixes; this compounds that — regenerate before further analysis.

## Related

- [[Verification_Report]] — original venue where a different LiDAR128 bug
  (range-image zero-bin misread as occluded) was documented; that bug is
  confirmed already fixed in the current codebase (`lidar_visibility.py`
  excludes `range_samples > 0.0` from `valid_samples`).
