---
title: §4 Visibility Metric Methodology — Recommendations
type: concept
source: home/adhish/Downloads/04_visibility_methodology.md
date: 2026-07-02
tags: [05 Implementation]
---
# §4 Visibility Metric Methodology — Recommendations

> **Execution Mode: CPU-Only / Validation-Only**
>
> All recommended methods below are chosen to be runnable on CPU with
> minimal memory.  GPU-specific paths (e.g. `points_in_boxes_gpu`) are
> noted as **future-scope**; the current build uses CPU equivalents.
> Full-dataset and GPU-accelerated variants are explicitly out of scope.


> Companion doc to `kradar_visibility_analysis_prompt.md`. Intended as an
> orchestrator-consumable spec: each section ends in a single concrete
> recommendation an implementing agent can build against without further
> design decisions.

## Goal alignment (from §5)

Every method below is selected to satisfy these constraints from §5/§8 before
accuracy is optimized further:

- **Sub-Goal 2 / §8.1 memory efficiency**: never load the full 4DRT
  (64×256×107×37 ≈ 64M cells/frame) per object. Use `radar_zyx_cube/` and
  frame-level lazy loading.
- **Sub-Goal 3**: all metrics reuse a single oriented-bbox-in-frame primitive
  (rotate by `theta`, translate by `(x,y,z)`, half-extents `L/2,W/2,H/2`) so
  radar/LiDAR/camera all consume the same transform code, not bespoke ones.
- **Sub-Goal 4 / §8.1 parallelization**: per-object score computation must be
  vectorizable across all objects in a frame (no per-object Python loops over
  raw points where avoidable) — this rules out per-object KD-tree builds as a
  *default* path.
- **Reuse existing infra**: the GPU `points_in_boxes_gpu` kernel is not
  available in this CPU-only build.  Use a lightweight CPU point-in-box
  implementation (e.g. NumPy-based frustum test or Open3D) for the
  validation phase.  GPU acceleration is future scope.
- **Error handling (§8.1)**: every method must degrade to `visible=False,
  score=0.0` cleanly when the underlying sensor file is missing, not raise.

---

## 4.1 Radar — `radar_sparsity_score`

### Candidate methods

**A. Binary cell-count density**
Threshold `radar_zyx_cube` at a fixed power floor, count cells inside the
oriented bbox above threshold, divide by bbox volume.
- Input: `radar_zyx_cube/` (already Doppler-collapsed).
- Formula: `score = count(cell.power > P_thresh AND cell in bbox) / bbox_volume_m3`
- Pros: cheap, one pass, easy to vectorize across all objects in a frame
  (compute occupancy mask once, then index per-bbox).
- Cons: a single global threshold ignores range-dependent noise floor —
  far objects get unfairly zeroed out.

**B. SNR-weighted power density**
Per-frame estimate a noise floor (e.g. median power of cells outside any
annotated bbox, or bottom decile), then sum *excess* power inside the bbox
rather than counting binary hits.
- Input: `radar_zyx_cube/`.
- Formula: `score = sum(max(0, power_db - noise_floor_db) for cell in bbox) / bbox_volume_m3`
- Pros: range-adaptive (noise floor estimated per-frame), continuous (not
  threshold-sensitive), still one pass over the cube.
- Cons: noise floor estimation adds a cheap but non-trivial per-frame step;
  slightly more sensitive to multipath/clutter than (A).

**C. Full 4DRT range-Doppler-azimuth-elevation integration**
Use `radar_tesseract/` directly, integrate power across the Doppler axis
inside the bbox's angular/range extent.
- Input: `radar_tesseract/` (full 64M-cell tensor).
- Pros: most physically complete (Doppler retained, could later support a
  motion-consistency check).
- Cons: violates the §8.1 memory-efficiency constraint directly — loading
  the full tensor per frame for thousands of objects is the explicitly
  called-out cost risk. Reject as primary path; keep as an optional
  `--full-tesseract` flag for research use only.

### Recommendation

Implement **B (SNR-weighted power density on `radar_zyx_cube`)** as
`radar_sparsity_score`, with **A's binary count** retained as a free
secondary diagnostic column if cheap to compute alongside (no schema entry
required, can live in a debug sidecar). Rationale: B satisfies SMK-14's
monotonic-decrease-with-distance check more robustly than A because the
per-frame noise floor adapts, and it stays within the zyx-cube memory
budget. `radar_fov_in` / `radar_range_in` are pure geometry (azimuth/
elevation angle of bbox center vs. 107°/37° cone, range vs. 0–118 m) and are
computed independently of A/B/C, gating `radar_visible` to `fov_in AND
range_in`.

---

## 4.2 LiDAR — `lidar64_sparsity_score`, `lidar128_sparsity_score`

### Candidate methods

**A. Raw point count in oriented bbox**
Direct reuse of the existing `points_in_boxes_gpu` (OpenPCDet) pipeline
already built for this codebase.
- Input: `os2-64/`, `os1-128/` point clouds, oriented bbox.
- Formula: `lidar*_points_count = points_in_boxes_gpu(points, bbox)`
- Pros: zero new code — directly reuses existing GPU-accelerated,
  prefetched/pinned-memory pipeline from prior K-Radar work; fast,
  well-tested.
- Cons: raw count alone isn't a normalized "visibility" score — a count of
  5 means different things at 10 m vs. 80 m.

**B. Count normalized by theoretical expected density**
Model expected point count from channel count, angular resolution, and
range (a LiDAR's vertical/horizontal angular resolution implies an expected
number of beam returns striking a bbox of known size at a given distance),
then score = actual / expected.
- Input: same point-in-box counts from (A), plus sensor angular-resolution
  constants (64 vs. 128 channel, known horizontal scan rate) and bbox
  geometry.
- Formula (approx.): `expected ≈ (vertical_channels × vertical_extent_angle / total_vertical_fov) × (horizontal_extent_angle / horizontal_angular_resolution)`,
  `score = clip(actual_count / expected, 0, 1)`
- Pros: range- and channel-invariant — a sparse-but-expected far object and
  a sparse-and-anomalous near object are distinguishable, which is the
  actual definition of "visibility" rather than raw density.
- Cons: the expected-count model is an approximation (ignores partial
  occlusion by other objects, ground strikes); needs a documented formula
  and a couple of sanity checks against SMK-15.

**C. Voxel occupancy ratio**
Voxelize the bbox interior at a fixed resolution (e.g. 0.1–0.2 m), compute
fraction of occupied voxels.
- Pros: captures spatial coverage, not just count (a clustered burst of 50
  points in one corner vs. 50 points spread over the surface).
- Cons: extra voxelization pass per object; resolution choice is another
  hyperparameter; marginal benefit over (B) for this use case given weather
  is the dominant noise source, not point clustering.

### Recommendation

Use **A** to populate `lidar*_points_count` with a CPU-based point-in-box
implementation (lightweight, no GPU required), and **B** to derive
`lidar*_sparsity_score` from it via the expected-density normalization.
This is the cheapest path that still yields a real 0–1 "visibility" number
satisfying VER-06/VER-07 (decreases with distance) without re-deriving it —
distance is already implicit in the expected/actual ratio. Reject C: the
added voxelization cost isn't justified given weather (VER-25) dominates
sparsity variance far more than within-bbox point clustering does.
`lidar*_visible` = `points_count > 0 AND bbox center within sensor's
documented FOV/range`.

---

## 4.3 Camera — `cam_*_visibility_score`

### Candidate methods

**A. Center-point projection only**
Project bbox center via `K[R|t]`, check if pixel falls in `[0,1280)×[0,720)`
and `z_cam > 0`.
- Pros: trivial, one matrix-vector op per object per camera.
- Cons: no notion of "how visible" beyond a boolean — fails the stated goal
  of a continuous score, and gives no signal for SMK-16 (center vs. edge
  object should differ).

**B. 8-corner projection → 2D bbox → area/centrality score**
Project all 8 3D bbox corners into each camera, take the 2D convex hull /
axis-aligned bbox, clip to image bounds, then score from clipped area
fraction and distance-from-image-center.
- Input: bbox corners, camera `K, R, t`.
- Formula: `score = w1 * (clipped_area / image_area) + w2 * (1 - normalized_dist_to_center)`,
  weights e.g. `w1=0.7, w2=0.3`; `cam_*_proj_x/y` = projected center.
- Pros: cheap (8 matmuls + 2D hull), gives a genuinely continuous, size- and
  centrality-aware score; satisfies SMK-16 directly (larger/more-central
  projection → higher score).
- Cons: no occlusion handling — an object fully hidden behind a closer
  vehicle still scores high.

**C. B + LiDAR depth-buffer occlusion check**
Same as B, plus: project the relevant LiDAR point cloud into the same
camera, build a sparse depth buffer, and discount the score by the fraction
of the object's projected footprint where LiDAR returns indicate a closer
surface than the object's own depth.
- Pros: handles real occlusion, which B cannot — meaningfully different
  answer for "in FOV" vs. "actually visible."
- Cons: adds a per-camera, per-frame LiDAR projection + sparse z-test; more
  expensive, and depth-buffer sparsity itself can produce false negatives
  (gaps in LiDAR coverage misread as "nothing occluding").

### Recommendation

Implement **B as the primary `cam_*_visibility_score`** (projection +
area + centrality), since it's cheap, fully vectorizable per frame, and
directly satisfies the stated smoke/verification criteria (SMK-05–09,
SMK-16, VER-10–15) without depending on LiDAR cross-registration succeeding.
Add **C's occlusion discount as an optional second pass**, gated behind a
config flag (`enable_occlusion_check=True`), since it strictly improves
accuracy but isn't required to pass the defined test suite and adds
real cost at full-dataset scale (Sub-Goal 1 overarching goal: "passes all
smoke/verification tests" — B alone already clears that bar).
`cam_*_visible` = `z_cam > 0 AND clipped_area > 0`.

---

## Summary table

| Sensor | Score basis | Reused existing infra? | Optional upgrade |
|---|---|---|---|
| Radar | SNR-weighted power density (zyx_cube) | No — new, but zyx_cube only | Full 4DRT Doppler integration (flag-gated) |
| LiDAR 64/128 | CPU point-in-box count → expected-density ratio | No — CPU implementation required | Voxel occupancy ratio (future) |
| Camera ×4 | 8-corner projection → area × centrality | No — new, but cheap | LiDAR depth-buffer occlusion discount |
