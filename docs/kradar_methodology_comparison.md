# KRADAR Visibility Analysis Methodology Comparison

## Executive Summary
The KRADAR visibility analysis pipeline determines whether each annotated 3D object in a frame is detectable by radar, LiDAR, and camera sensors, producing binary visibility flags and continuous visibility scores. The original methodology relied on raw point counts and simple geometric checks, lacking normalization for range, occlusion, and sensor-specific noise. The new methodology introduces per‑frame precomputation (noise‑floor maps, range images, depth maps) and merges geometric and occlusion factors into a unified, range‑invariant score, while adding cross‑sensor sanity checks (e.g., radar‑ghost flags). This improves robustness to weather, occlusion, and sensor noise while staying within CPU‑only, memory‑efficient constraints.

## Methodology Overview (ELI15)
### What is KRADAR visibility analysis and why does it matter?
KRADAR is a dataset for autonomous driving that includes synchronized radar, LiDAR (64‑ and 128‑beam), and multi‑camera data with 3D bounding box labels. Visibility analysis answers the question: *“For each labeled object, can each sensor actually see it, and how well?”* This is crucial for sensor fusion—if a sensor reports an object that it cannot truly see (e.g., a radar ghost), the fusion algorithm may be misled. Visibility scores help weight sensor contributions, filter false positives, and diagnose sensor performance under adverse weather (rain, fog, snow) where raw point counts become misleading.

### Old Methodology (Summary from `01_original_methodology_summary.md` and `04_visibility_methodology.md`)
- **Goal**: Produce per‑sensor visibility flags and scores using existing infrastructure with minimal new code.
- **Radar**: Used a simple SNR‑weighted power density (Section 4.1 of `04_visibility_methodology.md`) – sum of excess power above a per‑frame noise floor inside the object’s oriented bounding box, divided by box volume.
- **LiDAR**: Reused the existing GPU‑accelerated `points_in_boxes_gpu` (OpenPCDet) to get raw point counts inside the oriented box, then normalized by an expected‑density model based on sensor geometry (Section 4.2). Visibility was `count > 0` and within FOV/range.
- **Camera**: Projected the 3D bounding box’s 8 corners into each camera image, computed the clipped 2D area and centrality, and combined them into a score (Section 4.3). No explicit occlusion handling.
- **Constraints**: CPU‑only, no loading of the full 4D radar tensor (radar_tesseract), lazy loading, vectorized across objects, graceful degradation to `(visible=False, score=0.0)` on missing data.

### New Methodology (Summary from `k-radar-recommended-pipeline-summary.md` and `k-radar-sensor-visibility-metrics.md`)
- **Core Idea**: Decouple per‑frame expensive precomputation from per‑object scoring. Compute once per frame:
  - Radar: CFAR‑style noise‑floor map over `radar_zyx_cube`.
  - LiDAR (each beam): range image (nearest hit per azimuth/elevation bin).
  - Camera: Sparse depth maps by projecting the full LiDAR point cloud into each camera view.
- **Per‑object scoring** (vectorized across all objects):
  - **Radar**: Same SNR‑weighted excess power, now using the precomputed noise floor; optional Doppler‑coherence gating.
  - **LiDAR**: Combines **density ratio** (actual points / expected points from geometry) and **occlusion fraction** (ratio of rays that hit something nearer than the object) → `score = density_ratio × (1 − occluded_fraction)`. Visibility requires both terms to exceed thresholds.
  - **Camera**: Same 8‑corner area/centrality base score, now multiplied by a LiDAR depth‑buffer occlusion discount (fraction of sampled pixels where LiDAR sees a closer surface).
- **Cross‑sensor sanity check**: Flag probable radar ghosts when `radar_visible=True` and all other sensors report `visible=False` (free, no extra compute).
- **Benefits**: Range‑invariant scores, explicit occlusion handling, robustness to weather‑induced noise floor changes, and minimal per‑object cost (O(1) after per‑frame O(N) precomputation).

## Old vs. New Methodology — Pros and Cons

### Old Methodology
**Pros**
- Reused existing, well‑tested GPU‑accelerated point‑in‑box kernels (`points_in_boxes_gpu`) for LiDAR (01_original_methodology_summary.md, line 16‑19).
- Simple to implement and reason about (direct counts, basic projections).
- Low per‑object computational cost (no per‑frame precomputation needed).

**Cons**
- **Radar**: SNR‑weighted power density still required a per‑frame noise‑floor estimate; the original implementation did not precompute and reuse it, leading to redundant computation (04_gap_analysis.md, Gap 11‑16).
- **LiDAR**: Raw point count is not normalized for range or occlusion; a sparse far object and a dense near occluded object could yield similar counts, making the score not a true visibility measure (04_visibility_methodology.md, lines 103‑105).
- **Camera**: No occlusion handling; an object fully hidden behind another still receives a high score based solely on projection area and centrality (04_visibility_methodology.md, lines 169‑171).
- **Missing cross‑sensor validation**: No automatic flagging of radar‑ghost or inconsistent sensor agreements (04_gap_analysis.md, Gap 25‑30).
- **Scalability**: Per‑object loops over raw points (if not using GPU kernel) would become prohibitive; the original plan relied on GPU kernels unavailable in the CPU‑only validation build (00_orchestrator_kickoff_prompt.md, lines 31‑34).

### New Methodology
**Pros**
- **Radar**: Precomputed noise‑floor map amortizes the cost across all objects; optional Doppler coherence refines ghost rejection without loading the full 4DRT (k-radar-sensor-visibility-metrics.md, lines 12‑13, 78‑87).
- **LiDAR**: The merged density × (1‑occlusion) score separates range effects from true occlusion, yielding a range‑invariant visibility metric (k-radar-recommended-pipeline-summary.md, lines 36‑52; k-radar-sensor-visibility-metrics.md, lines 115‑122).
- **Camera**: Depth‑buffer discount provides a principled occlusion penalty that is cheap because the LiDAR→camera projection is done once per frame (k-sensor-visibility-metrics.md, lines 172‑194).
- **Cross‑sensor ghost flag**: Free sanity check that helps identify radar multipath artifacts (k-radar-recommended-pipeline-summary.md, lines 11‑12).
- **CPU‑only & memory‑efficient**: No full 4DRT loading; per‑frame O(N) precomputation scales with points/cells, not with number of objects (04_visibility_methodology.md, lines 21‑36).
- **Vectorized**: Per‑object scoring uses precomputed maps, enabling NumPy broadcasting across all objects in a frame (04_visibility_methodology.md, lines 27‑30).

**Cons**
- **Implementation complexity**: Requires adding precomputation steps and modifying the pipeline to pass shared data (06_upgrade_roadmap.md, Phase 1‑3).
- **Parameter tuning**: New thresholds (e.g., `tau_density`, `MIN_RAYS_FOR_OCCLUSION_CHECK`) and CFAR guard/training cell sizes need tuning (k-radar-sensor-visibility-metrics.md, lines 115‑130).
- **Approximation errors**: The LiDAR occlusion fraction assumes a perfect range image; sparse LiDAR at long range can make the occlusion ratio noisy (mitigated by a minimum‑ray guard) (k-radar-sensor-visibility-metrics.md, lines 54‑57).
- **CPU cost of precomputation**: Though amortized, building range images and depth maps adds per‑frame overhead; however, the roadmap shows this overhead is expected to be <20% (06_upgrade_roadmap.md, lines 149‑158).

### Comparison Table
| Aspect                | Old Methodology                                          | New Methodology                                                                 |
|-----------------------|----------------------------------------------------------|---------------------------------------------------------------------------------|
| **Radar score**       | SNR‑weighted excess power; noise floor computed per object (redundant) | Same formula, but noise‑floor map precomputed once per frame; optional Doppler coherence |
| **LiDAR score**       | Raw point count → expected‑density ratio (range‑invariant only via expectation) | Density ratio × (1 − occlusion fraction); occlusion measured via per‑frame range image |
| **Camera score**      | 8‑corner projection → area/centrality (no occlusion)     | Same base score × LiDAR depth‑buffer occlusion discount (sparse depth map precomputed per frame) |
| **Cross‑sensor check**| None                                                     | Radar‑ghost flag: `radar_visible ∧ ¬lidar_visible ∧ ¬camera_visible` |
| **Per‑frame cost**    | Low (no shared precomputation) but redundant noise‑floor/range image LiDAR→camera per object | Moderate: one noise‑floor map, one range image per LiDAR, four depth maps per frame; amortized over objects |
| **Per‑object cost**   | O(1) after point‑in‑box (GPU) or O(N points) if CPU      | O(1) – simple table lookups and arithmetic using precomputed maps               |
| **Weather robustness**| Moderate (radar SNR adapts, but LiDAR/camera lack explicit noise handling) | High: radar noise floor adapts per frame; LiDAR occlusion unaffected by reflectivity; camera depth buffer unaffected by illumination |
| **Occlusion handling**| Implicit via density ratio for LiDAR; none for camera    | Explicit ray‑occlusion for LiDAR; depth‑buffer discount for camera               |
| **Implementation effort**| Low (reuse existing kernels)                           | Medium (add precomputation, modify pipeline, add ghost flag)                    |

### Code Snippets Illustrating Differences
**Old LiDAR scoring (pseudo‑code from 04_visibility_methodology.md lines 95‑104):**
```python
lidar_points_count = points_in_boxes_gpu(points, bbox)   # GPU kernel
lidar_score = lidar_points_count / expected_count(bbox)  # expected from geometry
visible = lidar_points_count > 0 and in_fov_and_range(bbox)
```

**New LiDAR scoring (k-radar-sensor-visibility-metrics.md lines 115‑159):**
```python
# Precomputed once per frame: range_image[channel, azimuth] = nearest hit range
N_actual = count_points_in_box(points, box)
N_expected = projected_silhouette_area(box, sensor_origin) / (r^2 * d_az * d_el)
density_ratio = min(1.0, N_actual / max(N_expected, eps))

ray_channels, ray_az_bins = angular_footprint(box, sensor_origin, channel_lut)
if len(ray_channels) >= MIN_RAYS:
    hits = range_image[ray_channels, ray_az_bins]
    reaching = (hits >= r_near) & (hits <= r_far)
    occluded_fraction = 1.0 - reaching.sum() / len(ray_channels)
else:
    occluded_fraction = 0.0   # too few rays, fall back to density only

score = density_ratio * (1.0 - occluded_fraction)
visible = (density_ratio > tau_density) and (occluded_fraction < 1.0)
```

**Old Camera scoring (04_visibility_methodology.md lines 159‑166):**
```python
# Project 8 corners, compute clipped area and centrality
score = w1 * (clipped_area / image_area) + w2 * (1 - normalized_dist_to_center)
visible = clipped_area > 0 and z_cam > 0
```

**New Camera scoring (k-radar-sensor-visibility-metrics.md lines 192‑222):**
```python
# Same base score...
base_score = (A_clip / max(A_full, 1e-6)) * centrality
# Depth‑buffer discount using precomputed sparse depth map
z_obj = expected_surface_depth(corners_3d, extrinsics)
sample_uv = sample_pixels(clipped, n_samples=64)
d_local = local_depth_lookup(depth_map, sample_uv, radius=3)
occluded_px = sum(d_local < (z_obj - DEPTH_MARGIN))
occlusion_discount = 1.0 - occluded_px / max(len(sample_uv), 1.0)
score = base_score * occlusion_discount
return {"visible": True, "score": float(score)}
```

## Per‑Sensor Deep Dive

### Radar (64‑beam, 4D → collapsed to zyx cube)
- **Old Methodology**:  
  - Used `radar_zyx_cube` (Doppler‑collapsed cube).  
  - Score = sum of `max(0, power - noise_floor)` inside oriented bbox, divided by box volume.  
  - Noise floor estimated per‑object (or globally) – not shared across objects, causing redundant computation.  
  - No explicit Doppler consistency check; multipath ghosts could inflate score.  
  - Pros: Simple, one pass over cube, vectorizable across objects if noise floor precomputed.  
  - Cons: Noise‑floor redundancy; vulnerable to non‑stationary weather‑induced background changes.

- **New Methodology**:  
  - Precomputes per‑frame CFAR‑style noise‑floor map (`prepare_frame_radar`) once and reuses it for all objects.  
  - Optional Doppler‑coherence gating: for each object, crop a small sub‑tensor across Doppler bins, compare measured vs. expected Doppler, weight excess power by coherence.  
  - Pros: Noise‑floor adaptation to frame‑specific conditions (rain/fog/snow) reduces false positives; Doppler gating helps reject moving‑object ghosts.  
  - Cons: Requires tuning of CFAR guard/training cells; Doppler gating adds small per‑object overhead (still O(1) because sub‑tensor size bounded).  
  - **Source**: `k-radar-sensor-visibility-metrics.md` lines 78‑87 (recommendation), 165‑186 (implementation).

### LiDAR‑64 (OS2‑64) and LiDAR‑128 (OS1‑128)
- **Old Methodology**:  
  - Leveraged existing GPU kernel `points_in_boxes_gpu` to get raw point count inside oriented bbox.  
  - Derived `lidar*_sparsity_score` = `count / expected_count` where `expected_count` modeled from sensor geometry (vertical/horizontal resolution, range).  
  - Visibility = `count > 0` and bbox center within documented FOV/range.  
  - Pros: Reused well‑tested GPU code; expected‑density normalization made score roughly range‑invariant.  
  - Cons: Could not distinguish a genuinely sparse far object from a nearby occluded object with similar expected count; no explicit occlusion term.  

- **New Methodology**:  
  - Builds per‑frame range image (`prepare_frame_lidar`) – nearest hit per (channel, azimuth bin).  
  - Computes both density ratio (same as old) **and** occlusion fraction: fraction of rays aimed at the box that hit something nearer than the box’s near range.  
  - Final score = `density_ratio × (1 − occluded_fraction)`.  
  - Visibility requires both density ratio > τ and occlusion fraction < 1.0 (with a minimum‑ray guard to avoid noisy ratios at long range).  
  - Pros: Separates geometric sparsity from occlusion; robust to weather (rain/snow reduces returns but affects both actual and expected similarly); occlusion term penalizes objects hidden behind closer surfaces.  
  - Cons: At very long range, few rays intersect the box → occlusion fraction noisy; mitigated by `MIN_RAYS_FOR_OCCLUSION_CHECK` fallback to density‑only.  
  - **Source**: `k-radar-sensor-visibility-metrics.md` lines 115‑159 (LiDAR scoring function), `k-radar-recommended-pipeline-summary.md` lines 18‑21 (precompute), 36‑52 (theory).

### Camera (×4: front‑left, front‑right, rear‑left, rear‑right)
- **Old Methodology**:  
  - Projected 8 corners of the oriented bbox into each camera image using intrinsics/extrinsics.  
  - Computed clipped 2D convex hull area and centroid distance from image center.  
  - Score = weighted sum of normalized area and centrality (e.g., 0.7*area + 0.3*centrality).  
  - Visibility = clipped area > 0 and depth in front of camera (`z_cam > 0`).  
  - Pros: Extremely cheap (8 matrix‑vector multiplies per object per camera); gave a continuous size‑ and position‑aware signal.  
  - Cons: No occlusion handling – an object fully hidden behind another vehicle still scored high if its bounding box projected visible.

- **New Methodology**:  
  - Same base area/centrality score.  
  - Adds LiDAR depth‑buffer occlusion discount: compute expected surface depth of the object, sample pixels inside the projected hull, compare LiDAR depth (from precomputed sparse depth map) to object depth; discount score by fraction of samples where LiDAR sees a closer surface.  
  - Pros: Explicitly penalizes occluded objects; cheap because depth map is computed once per frame by projecting the full LiDAR point cloud (reuse across all objects and cameras).  
  - Cons: Relies on accurate LiDAR‑to‑camera extrinsic calibration; sparse LiDAR may miss surfaces, causing false‑negative occlusion (depth map holes); adds small per‑object sampling cost (configurable number of samples).  
  - **Source**: `k-radar-sensor-visibility-metrics.md` lines 172‑194 (recommendation), 192‑222 (implementation); `k-radar-recommended-pipeline-summary.md` lines 19‑22 (precompute), 23‑27 (per‑object scoring).

## Implementation & Practical Context

### Upgrade Path (from `06_upgrade_roadmap.md`)
The upgrade follows a **phased approach**:
1. **Phase 1 – Foundation (Sensor Module Updates)**  
   - Update `lidar_visibility.py`, `radar_visibility.py`, `camera_visibility.py` to accept precomputed inputs (range image, noise floor, depth maps) and implement the new scoring formulas.  
   - Changes are backward compatible (can fall back to old behavior if precomputed data missing).  
2. **Phase 2 – Integration (Pipeline Updates)**  
   - Modify `pipeline.py` to call the precomputation functions once per frame, pass the results to the sensor modules, and compute the cross‑sensor ghost flag.  
3. **Phase 3 – Validation & Performance**  
   - Run smoke and verification tests on a subset of sequences.  
   - Benchmark precomputation overhead (target <20% per‑frame increase).  
   - Update documentation.  
- See `06_upgrade_roadmap.md` lines 3‑182 for detailed task breakdown and effort estimates.

### Gaps Between Old and New Systems (from `04_gap_analysis.md`)
The gap analysis identified four **critical gaps** that the new methodology addresses:
1. **Missing per‑frame LiDAR range‑image precomputation** – LiDAR scores were not occlusion‑aware.  
2. **Missing per‑frame radar noise‑floor map** – Radar scores less robust to weather‑induced background changes.  
3. **Missing per‑frame LiDAR→camera projection for depth‑buffer occlusion** – Camera scores lacked explicit occlusion handling.  
4. **Missing fusion‑level ghost flag** – No automatic flagging of radar‑ghost/multipath cases.  

Additionally, several **non‑critical gaps** and **enhancements** were noted (e.g., distortion‑corrected camera projection, Doppler‑coherence gating, voxel occupancy ratio as offline audit). These are optional extensions that can be gated behind feature flags.

### Dependency Management (from `05_dependency_analysis.md`)
The upgrade respects a clear dependency order to enable incremental deployment:
```
pipeline.py
├── lidar_visibility.py
├── radar_visibility.py
└── camera_visibility.py
```
- **lidar_visibility.py**, **radar_visibility.py**, and **camera_visibility.py** can be updated independently (backward‑compatible).  
- **pipeline.py** must be updated last, as it depends on all three sensor modules to pass precomputed data and compute the ghost flag.  
- See `05_dependency_analysis.md` lines 1‑12 for the full dependency graph and upgrade order.

## Key Takeaways
- **Why the change?** The old method produced visibility scores that conflated range, occlusion, and sensor noise, leading to misleading fusion inputs, especially in adverse weather. The new method decouples these factors using per‑frame precomputation, yielding more physically meaningful scores.
- **What you gain**:  
  - Range‑invariant, occlusion‑aware LiDAR scores.  
  - Weather‑adaptive radar scores with optional Doppler ghost rejection.  
  - Occlusion‑sensitive camera scores via lightweight depth‑buffer discount.  
  - Free cross‑sensor sanity check for radar ghosts.  
  - All within CPU‑only, memory‑efficient constraints suitable for validation and debugging.
- **What you pay**: Moderate increase in implementation complexity and per‑frame precomputation overhead (expected <20%). Requires tuning of new parameters (CFAR cells, ray‑count thresholds, sampling densities).
- **Adoption path**: Follow the phased upgrade roadmap – update sensor modules first (independent), then the pipeline. Dependencies are linear and backward‑compatible, allowing incremental rollout.
- **Verification**: Existing smoke and verification tests (based on Parquet output) should continue to pass; the new methods were selected specifically to satisfy those criteria (see `04_visibility_methodology.md` goal alignment).

This concludes the ELI15‑style comparison of the KRADAR visibility analysis methodologies.