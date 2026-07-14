---
title: Sensor Visibility & Identification Metrics for K-Radar
type: literature
source: home/adhish/Downloads/k-radar-sensor-visibility-metrics.md
date: 2026-07-02
tags: [02 Literature]
---
# Sensor Visibility & Identification Metrics for K-Radar
### Theoretical Reference Document — Radar / LiDAR-64 / LiDAR-128 / Camera×4

**Scope:** For every annotated 3D object per frame, define a boolean `*_visible` and continuous `*_score` per sensor, under CPU-only, lazy-loading, vectorized constraints. K-Radar bboxes are `(x,y,z,θ,l,w,h)` with **half-extents**; convert to full extents (`2l, 2w, 2h`) before any volumetric computation — this is the single most common bug source and is flagged explicitly in every formula below.

---

## 0. Shared Conventions

- Object frame: box center `c=(x,y,z)`, yaw `θ` about z, full dimensions `L=2l, W=2w, H=2h`.
- Point-in-box test (any sensor): rotate point into box frame, `R(-θ)(p-c)`, then check `|Δx|≤L/2, |Δy|≤W/2, |Δz|≤H/2`. This is O(N) per object, O(N·M) per frame for N points, M objects — vectorize via broadcasting (N×M) rather than looping, and pre-filter with an axis-aligned bounding box (AABB) or KD-tree/range query to keep it CPU-tractable (KITTI devkit and OpenPCDet's `points_in_boxes_cpu` use exactly this two-stage filter, Geiger et al. 2012; OpenPCDet, Team OpenPCDet 2020).
- Degrade gracefully: if a sensor file is missing/unreadable, set `visible=False, score=0.0` and log — never raise.

---

## 1. Radar Visibility Methods

### 1.1 Binary Cell-Count Density (Baseline A)
**Source:** standard CFAR-thresholding practice in automotive radar (Rohling 1983, CA-CFAR; adapted in nuScenes/RadarScenes-style radar point generation).
**Formula:**
```
visible = (count{cells in bbox : P(cell) > τ}) > 0
score   = count{cells in bbox : P(cell) > τ} / V_box,  V_box = L·W·H
```
**Input:** `radar_zyx_cube` (Doppler-collapsed power cube), a global or per-frame threshold τ.
**Occlusion handling:** none — radar penetrates most non-metallic occluders and diffracts around others, so cell counts don't degrade cleanly with occlusion the way LiDAR/camera do. No augmentation is strictly required, but front-object shadowing (metal panel occlusion) is not modeled.
**Complexity:** O(cells in box) per object ≈ O(k) with k~ tens–hundreds; memory O(1) beyond the cube itself.
**Pros:** trivial, fast, no per-frame noise-floor estimation needed.
**Cons:** ignores relative signal strength; a single hot pixel from clutter can flip `visible=True`; not robust to sidelobe leakage; τ tuning is brittle across weather.
**K-Radar suitability:** Poor as sole score — heavy rain/snow raises broadband noise floor, so a fixed τ either over- or under-fires; only useful as a fast pre-filter/gate before method 1.2.

### 1.2 SNR-Weighted Power Density (Baseline B — currently selected)
**Source:** adapted from CFAR excess-power aggregation, cf. Richards, *Fundamentals of Radar Signal Processing* (2014); similar excess-power-in-ROI scoring used in View-of-Delft radar analysis (Palffy et al. 2022) and RADIal (Rebut et al. 2022).
**Formula:**
```
N_local(cell) = median or mean power in a guard-banded ring around cell (per-frame CFAR noise floor)
excess(cell)  = max(0, P(cell) - N_local(cell))
visible = Σ_{cell∈box} excess(cell) > ε
score   = Σ_{cell∈box} excess(cell) / V_box
```
**Input:** `radar_zyx_cube`, cell resolution (Δaz, Δel, Δr) to compute V_box in cell units, guard/training-cell geometry for CFAR.
**Occlusion handling:** partial — a fully radar-shadowed object (rare, e.g., large flat metal truck directly in front) shows depressed excess power; not explicitly modeled, could add a ray-based shadow check (see §4).
**Complexity:** O(k) per object for the box sum + O(cube size) once per frame for the noise-floor map (can be precomputed frame-globally, amortized). Memory: reuses the already-loaded collapsed cube, no extra tensor.
**Pros:** normalizes for per-frame/weather noise floor (critical in K-Radar's rain/fog/snow splits); differentiable-friendly; already selected and validated in your pipeline.
**Cons:** sensitive to guard-cell/training-cell window size; azimuth/elevation resolution is coarse (107°/37° FOV over limited bins) so small or distant objects (motorcycle, pedestrian) may span very few cells → noisy score; multipath ghosts near large metal vehicles (buses/trucks) inflate excess power outside the true object footprint.
**K-Radar suitability:** best available compromise given CPU-only + no full 4DRT; recommended as core radar score.

### 1.3 Doppler-Coherence Gating (Novel Alternative)
**Source:** motion-compensated Doppler consistency, cf. moving-target indication (MTI) literature (Skolnik, *Radar Handbook*, 2008) and dynamic-object radar filtering in RadarScenes (Schumann et al. 2021).
**Formula:**
```
For a moving ego + moving/static object, expected Doppler v_exp is computable from
ego-motion + object velocity prior (if tracked) via v_exp = -(v_ego · r̂) [+ v_obj·r̂]
coherence(cell) = 1 - |v(cell) - v_exp| / v_tol
visible = max_cell coherence(cell) > 0
score   = Σ_{cell∈box, coherence>0} excess(cell)·coherence(cell) / V_box
```
**Input:** requires the (currently CPU-avoided) Doppler dimension per cell — i.e., a Doppler-resolved slice, not the fully collapsed cube. Needs ego pose (RTK-GPS, already in K-Radar) and, ideally, a velocity prior (finite-difference from consecutive-frame tracks/`sensor_identify` history).
**Occlusion handling:** none directly, but strongly rejects multipath ghosts (§4.1) since ghost returns typically show incoherent/aliased Doppler.
**Complexity:** O(k) per object if you slice only the box's Doppler bins rather than materializing the full 4DRT (i.e., index a bounding sub-tensor `[r_min:r_max, az_min:az_max, el_min:el_max, :]` — memory O(k·D) where D=64 Doppler bins, still far smaller than 64M cells/frame).
**Pros:** meaningfully improves precision by rejecting clutter/ghost false positives that 1.2 cannot; principled use of the one radar-unique dimension you're otherwise discarding.
**Cons:** breaks down for stationary objects with `v_exp≈0` near the ego (Doppler resolution floor); needs velocity priors that don't exist for a first-pass detection (chicken-and-egg with tracking); implementation complexity is materially higher than 1.1/1.2.
**K-Radar suitability:** High long-term value (K-Radar retains full RAED without dimensionality loss), but should be flag-gated (like Method C) since it partially reintroduces the memory/complexity you're trying to avoid — mitigate by slicing per-object sub-volumes instead of the full tensor.

### 1.4 Full 4DRT Integration (Baseline C — memory-prohibitive default-off)
**Source:** direct volumetric integration, as used in dense-tensor detection baselines (RTNH network in the K-Radar paper, Paek et al. 2022, NeurIPS D&B).
**Formula:** `score = Σ_{r,az,el,d ∈ box} P(r,az,el,d) / V_box·D` (D = Doppler bins), `visible = score > ε`.
**Occlusion handling:** none inherent.
**Complexity/memory:** O(64×256×107×37) ≈ 64M cells/frame if materialized; must instead crop to a padded per-object AABB in tensor-index space before loading — even then, keep flag-gated.
**Pros:** ground-truth-faithful, most information-preserving.
**Cons:** the reason it's gated — CPU RAM/time cost scales with number of objects × crop volume; I/O-bound if 4DRT isn't cached.
**K-Radar suitability:** use only for offline validation/audits of 1.2's scores on a sampled subset, not per-frame production.

---

## 2 / 3. LiDAR-64 (OS2-64) and LiDAR-128 (OS1-128) Visibility Methods
*(Same method family applies to both; differences are angular resolution and therefore the expected-density normalization constant. Treat as one section, parametrized by channel count `C∈{64,128}`.)*

### 2.1 Raw Point-in-Box Count (Baseline A)
**Source:** standard practice, KITTI `num_points_in_gt` (Geiger et al. 2012), used ubiquitously (OpenPCDet, mmdetection3d).
**Formula:** `visible = count>0`; `score = count` (unnormalized) or `count/V_box`.
**Occlusion handling:** none.
**Complexity:** O(N) per object with AABB pre-filter, fully vectorizable (numpy broadcasting or KD-tree query per box).
**Pros:** trivial, universal, comparable across the whole community's literature.
**Cons:** heavily range- and size-biased — same object at 10m vs 80m yields wildly different counts, making cross-distance comparison meaningless without normalization; this is precisely why 2.2 was selected.
**K-Radar suitability:** fine as a raw feature input into 2.2, weak as standalone score.

### 2.2 Expected-Density Normalization (Baseline B — currently selected)
**Source:** angular-resolution-based expected point count, a technique formalized for LiDAR "visibility levels" in nuScenes (`visibility` token 1: 0–40%, 2: 40–60%, 3: 60–80%, 4: 80–100% of a box's LiDAR+camera footprint; Caesar et al. 2020) and in the Waymo Open Dataset's `num_lidar_points_in_box` combined with range-based expected sampling density (Sun et al. 2020).
**Formula:**
```
N_expected(box) ≈ (Δθ_h · Δθ_v)^-1 · A_visible(box, sensor_origin) / r²   [solid-angle projected-area model]
   where Δθ_h, Δθ_v are the sensor's angular resolutions (horizontal from rotation rate/points-per-rev,
   vertical from the fixed channel LUT, e.g., 64 or 128 beam elevation table),
   A_visible = projected silhouette area of the box facing the sensor, r = range to box center
score   = min(1, N_actual / N_expected)
visible = score > τ_density  (e.g., 0.05–0.1)
```
**Input:** point cloud, sensor extrinsics/origin, per-channel elevation LUT (OS2-64 vs OS1-128 differ here — this is the parametrization point), box pose.
**Occlusion handling:** partial and implicit — if another object occludes the box, `N_actual` drops below `N_expected` and score correctly falls, *without* needing to know the occluder exists. This is actually a strength: expected-density normalization is occlusion-*sensitive* even though it isn't occlusion-*aware* (it can't distinguish "occluded" from "sensor malfunction" or "highly absorptive surface," e.g., a black car).
**Complexity:** O(N) for the count + O(1) analytic solid-angle term per box; fully vectorizable across boxes.
**Pros:** range-invariant, so distance degradation is graceful and comparable across the whole 0–118 m range in K-Radar; already selected — recommended to keep as core LiDAR score.
**Cons:** the projected-area model `A_visible` is itself an approximation (planar-facing-area assumption breaks for highly oriented boxes near the sensor, or when the box is only partially in FOV); dark/absorptive surfaces (rubber tires, black paint) legitimately return fewer photons and get penalized despite being "visible" in the geometric sense — a known LiDAR intensity artifact (Ouster OS-series datasheets; Levinson & Thrun 2010 on LiDAR reflectivity calibration).
**K-Radar suitability:** Strong; the two LiDAR channel counts (64 vs 128) enter cleanly via the elevation LUT resolution term, giving directly comparable normalized scores across the two sensors — useful for cross-sensor redundancy analysis.

### 2.3 Ray-Casting Occupancy / Frustum Visibility (Novel Alternative)
**Source:** ray-casting visibility reasoning from sensor origin, as used for amodal/occlusion-aware 3D detection labels in Waymo Open Dataset's occlusion heuristics (Sun et al. 2020) and in "ScanComplete"/frustum-occupancy style reasoning for indoor scenes (Dai et al. 2018), adapted to automotive LiDAR occlusion in FreeSpace/occupancy-grid literature (e.g., Hoermann et al. 2018, dynamic occupancy grids).
**Formula:**
```
For each of the C·(360/Δaz_pts) LiDAR rays intersecting the box's angular footprint:
  find first-return range r_hit along that ray
  ray "reaches" the box if r_hit ∈ [r_near(box), r_far(box)] ± ε  (i.e., the return actually
    terminates on/near the box surface rather than short of it, which implies an occluder)
occluded_fraction = 1 - (#rays reaching box surface) / (#rays whose angular footprint overlaps box)
visible = occluded_fraction < 1
score   = (1 - occluded_fraction) · (N_actual / N_expected)   [combine with 2.2]
```
**Input:** full point cloud with per-point range (not just points inside the box — need the *entire* ray set, so must query along the box's subtended angular window and check first-hit range, not just points already inside the box), sensor origin, box geometry.
**Occlusion handling:** explicit and directional — distinguishes "no return because occluded by a nearer object" from "no return because self-occlusion (only the near face of the box was ever visible) or beyond max range."
**Complexity:** O(rays subtending the box angular window), which is small (box angular footprint is a tiny fraction of the 360° sweep) — implementable as a 2D range-image lookup if you rasterize the LiDAR sweep to a (channel × azimuth-bin) range image first (O(1) amortized per ray after O(N) rasterization once per frame). This range-image approach is exactly how KITTI-style and Waymo occlusion computations are made CPU-tractable.
**Pros:** the only method here that cleanly separates "sensor limitation" from "occlusion by another tracked object," directly answering the brief's occlusion-awareness ask; reuses infrastructure (range image) that's cheap to build once per frame and reusable across all objects.
**Cons:** requires building a range image (modest one-time cost, ~C×1024 bins, tiny), and self-occlusion vs. inter-object occlusion still need a second pass against other boxes' angular footprints to be separated cleanly (see §4).
**K-Radar suitability:** Recommended as an *occlusion-aware upgrade path* over 2.2, particularly valuable in K-Radar's alley/urban scenes with high object density and mutual occlusion; low incremental CPU cost given K-Radar's already-large per-frame point count.

### 2.4 Voxel Occupancy Ratio (Baseline C — rejected)
**Source:** voxel-grid occupancy scoring, as in VoxelNet-style preprocessing (Zhou & Tuzel 2018) and SECOND (Yan et al. 2018).
**Formula:** `score = (#occupied voxels in box) / (#voxels in box)`, voxel size v.
**Occlusion handling:** none beyond what 2.1 already gives.
**Complexity/memory:** requires materializing a voxel grid per object or a shared fine grid per frame; rejected per your spec for cost — correctly so, since 2.2 gives comparable occlusion-*sensitivity* at O(1) extra cost and 2.3 gives true occlusion-*awareness* at modest extra cost, making 2.4 strictly dominated for this use case.
**K-Radar suitability:** not recommended; retained here only for completeness/comparison.

---

## 4. Camera Visibility Methods (×4: front, left, right, rear)

### 4.1 Center-Point Projection Only (Baseline A)
**Source:** minimal viability check, common in early monocular 3D detection pipelines (e.g., early KITTI baselines).
**Formula:** project `c` via `K[R|t]`; `visible = (0≤u<W) ∧ (0≤v<H) ∧ z_cam>0`. No continuous score.
**Occlusion handling:** none.
**Complexity:** O(1) per object.
**Pros:** trivial, useful as a fast reject.
**Cons:** binary only, ignores partial-frame truncation and occlusion entirely; a fully occluded object with a visible center pixel (rare but possible with thin occluders) is misclassified.
**K-Radar suitability:** pre-filter only.

### 4.2 8-Corner Projection → 2D BBox → Area/Centrality Score (Baseline B — currently selected)
**Source:** standard 3D→2D projection + KITTI-style 2D bbox area/truncation heuristics (Geiger et al. 2012 devkit truncation field); centrality weighting is a common design choice in modern amodal-visibility scoring, e.g., FCOS3D-style centerness (Wang et al. 2021) repurposed for a visibility score.
**Formula:**
```
project 8 box corners → 2D convex hull → clipped to image → (u_min,v_min,u_max,v_max)
A_clip = clipped area, A_full = unclipped projected hull area
centrality = 1 - ||p_center_2d - p_image_center|| / (image_diag/2)
score = (A_clip / A_full) · max(0, centrality)
visible = A_clip > 0
```
**Input:** 8 corners in ego frame, camera intrinsics K and extrinsics per one of 4 cameras.
**Occlusion handling:** none inherent — a fully unoccluded-but-truncated box and a fully in-frame-but-occluded box can get the same score, which is the acknowledged gap addressed by 4.3/C.
**Complexity:** O(1) per object per camera (8 matrix-vector products + 2D hull), trivially vectorizable across all 4 cameras × all objects.
**Pros:** cheap, deterministic, no learned model dependency (important for reproducibility as an annotation-quality metric rather than a perception-model output); already selected.
**Cons:** conflates truncation and occlusion; centrality term is a crude proxy for lens distortion / fisheye effects that stereo wide-FOV rigs often have — should verify K-Radar's cameras' distortion model is applied before projection, not just a pinhole K.
**K-Radar suitability:** Reasonable default; recommend explicitly applying the stereo cameras' distortion coefficients (if provided in calibration files) before the corner projection, since 1280×720 wide-baseline stereo rigs commonly have non-trivial radial distortion that a naive pinhole projection will mis-locate corners for, especially near image edges.

### 4.3 Depth-Buffer / LiDAR Z-Buffer Occlusion Discount (Baseline C — flag-gated)
**Source:** Z-buffer occlusion reasoning using an auxiliary depth sensor, standard in nuScenes' construction of the `visibility` attribute (Caesar et al. 2020) and in KITTI's occlusion levels (0=fully visible,1=partly,2=largely,3=unknown; Geiger et al. 2012).
**Formula:**
```
project LiDAR points into the camera image → sparse depth map D(u,v)
for each pixel in the object's projected 2D bbox, compare object's expected depth z_obj(u,v)
  (from the 3D box surface) against nearest sparse D(u,v):
occluded_px = count{ D(u,v) < z_obj(u,v) - δ }
score = 4.2's score · (1 - occluded_px / total_px_sampled)
```
**Occlusion handling:** explicit, the intended purpose.
**Complexity:** O(points projected once per frame, shared across all objects/cameras) + O(pixels sampled per box) — the per-frame LiDAR→image projection is the expensive part but is amortizable across all objects sharing that camera.
**Pros:** directly answers occlusion; reuses LiDAR data already loaded for §2/3, so marginal cost is mostly the projection step.
**Cons:** sparse LiDAR depth leaves gaps (especially at range or on thin structures), so `D(u,v)` needs a local-neighborhood or splatted lookup rather than exact pixel match, adding complexity; still susceptible to LiDAR-camera calibration/sync error, which is compounded across 3 sensors' calibrations.
**K-Radar suitability:** valuable, keep flag-gated as specified given the added projection cost across 4 cameras.

### 4.4 Instance-Segmentation-Mask Overlap (Novel Alternative)
**Source:** comparing projected 3D box footprint against a 2D instance segmentation/panoptic mask, a technique used for amodal vs. modal visibility separation, e.g., in the amodal completion literature (Zhu et al. 2017, "Semantic Amodal Segmentation"; Qi et al. 2019 on amodal 3D detection) and practically in nuScenes-style visibility derivation pipelines that use 2D detections/masks as a cross-check.
**Formula:**
```
run (or use precomputed) 2D instance mask M for the object's class in the projected region
modal_area   = |M ∩ projected_hull|
amodal_area  = |projected_hull| (i.e., 4.2's A_clip)
score = modal_area / amodal_area   (this is literally the "modal/amodal ratio" used to define
        occlusion level in amodal-perception benchmarks)
visible = modal_area > 0
```
**Input:** a 2D instance segmentation model's output (or ground-truth panoptic masks, if K-Radar/derived toolchains provide any) per camera frame.
**Occlusion handling:** the most direct and standard formalization of occlusion (modal vs. amodal area ratio) in the computer vision literature.
**Complexity:** dominated by the segmentation model's inference cost — if using a learned model, this is the first method in this catalog with non-trivial per-frame compute, and on CPU-only a lightweight model (e.g., a MobileNet-backboned instance segmenter) would still likely dominate the whole per-frame budget across all sensors combined.
**Pros:** best occlusion fidelity of the camera methods; class-consistency check as a side benefit (mask class should match annotation class — mismatches flag possible mis-projection or mis-calibration).
**Cons:** CPU-only inference cost is the primary blocker — explicitly conflicts with the "no GPU kernels" constraint's spirit even if technically runnable on CPU; introduces a learned-model dependency (versioning, reproducibility, domain gap in fog/snow where segmentation models trained on clear-weather data degrade); the constraint document doesn't mention model files as an available input, so this should be treated as future work, not baseline.
**K-Radar suitability:** highest theoretical accuracy, worst practical fit to the stated CPU-only lazy-loading constraint; recommend only as an *offline audit tool* run on a sampled subset (analogous to Radar method 1.4), not in the production per-frame pipeline.

### 4.5 Optical-Flow / Multi-View Stereo Consistency (Novel Alternative)
**Source:** occlusion boundary detection via flow discontinuities (Sun et al. 2010, "Secrets of Optical Flow Estimation"), and consistency checks across K-Radar's stereo pairs specifically — since K-Radar cameras are stereo, left/right disparity consistency at the object's projected region is a free occlusion/verification signal (standard stereo literature, Scharstein & Szeliski 2002).
**Formula:**
```
For a stereo pair covering the same FOV (if any of the 4 cameras are paired):
  compute disparity d(u,v) in the projected bbox region (block matching or SGM)
  expected disparity d_exp = f·baseline / z_obj
  consistency = 1 - mean(|d(u,v) - d_exp|) / d_exp   (clipped to [0,1])
score = 4.2's score · consistency
```
**Occlusion handling:** indirect — disparity outliers within the box region typically indicate a foreground occluder or background bleed-through at box edges (a classic stereo occlusion artifact), not full amodal/modal reasoning like 4.4 but cheaper than running a segmentation net.
**Complexity:** stereo matching (block matching, not full SGM, to stay CPU-feasible) over a small ROI is fast, O(ROI size × disparity search range); much cheaper than 4.4.
**Pros:** uses sensor data K-Radar already provides (stereo rig) rather than requiring an external model; classical CV, deterministic, reproducible.
**Cons:** only meaningful if two of the 4 cameras genuinely form a stereo pair with sufficient overlap for the object in question (need to confirm K-Radar's front/left/right/rear rig geometry — if they're a single-baseline front stereo pair rather than 4 independent monocular views, this only applies to front-view objects); degrades in low-texture regions and adverse weather (rain streaks/fog reduce stereo matching quality, a known limitation, Hirschmuller 2008).
**K-Radar suitability:** worth implementing for the front stereo pair specifically as a low-cost occlusion cross-check, but should not be assumed to generalize to left/right/rear without confirming rig overlap in K-Radar's calibration files.

---

## 5. Comparative Decision Matrix

| Sensor | Method | Accuracy | Weather Robust | Distance Invariant | Occlusion Aware | CPU Feasible | Implementation Ease |
|---|---|---|---|---|---|---|---|
| Radar | 1.1 Binary cell-count | Low | Medium | Low | None | High | High |
| Radar | 1.2 SNR-weighted power (selected) | Medium-High | High | Medium | Low | High | Medium |
| Radar | 1.3 Doppler-coherence gating | High | High | Medium | Low-Medium (rejects ghosts) | Medium | Low |
| Radar | 1.4 Full 4DRT integration | Highest | High | Medium | None | Low (gated) | Low |
| LiDAR 64/128 | 2.1 Raw point count | Low | Medium-High | Low | None | High | High |
| LiDAR 64/128 | 2.2 Expected-density norm (selected) | Medium-High | Medium-High | High | Medium (implicit) | High | Medium |
| LiDAR 64/128 | 2.3 Ray-casting/frustum occupancy | High | Medium-High | High | High (explicit) | Medium-High | Medium |
| LiDAR 64/128 | 2.4 Voxel occupancy ratio | Medium | Medium-High | Medium | Low | Low (rejected) | Medium |
| Camera×4 | 4.1 Center-point only | Low | Low-Medium | Medium | None | High | High |
| Camera×4 | 4.2 8-corner area/centrality (selected) | Medium | Low-Medium | Medium | None | High | Medium |
| Camera×4 | 4.3 Depth-buffer discount | High | Medium | Medium | High | Medium (gated) | Medium |
| Camera×4 | 4.4 Instance-mask overlap | Highest | Low (weather-sensitive model) | Medium | Highest | Low | Low |
| Camera×4 | 4.5 Stereo/optical-flow consistency | Medium-High | Low-Medium | Medium | Medium | Medium-High | Medium |

*(Weather robustness for camera methods is inherently capped "Low-Medium" relative to radar/LiDAR, reflecting K-Radar's own stated motivation for including 4D radar — camera degrades most in fog/rain/snow regardless of scoring method.)*

---

## 6. Occlusion-Aware Extensions (Deep Dive)

### 6.1 Radar: Multipath / Ghosting
Ghost targets arise from indirect (reflected) propagation paths, typically off large flat metal surfaces (guardrails, trucks, walls) common in K-Radar's highway/urban/alley scenes. Two complementary discriminators:
- **Doppler-coherence gating (1.3):** ghosts often show Doppler inconsistent with a physically plausible object at that range/azimuth given ego-motion, since the ghost's apparent range is the *sum* of direct and reflected path lengths, but its Doppler still reflects the real object's velocity — a detectable range/velocity mismatch (cf. multipath ghost suppression literature, e.g., Kellner et al. 2013 "Instantaneous Ego-Motion Estimation using Doppler Radar," and multipath mitigation surveys in automotive radar, Bilik et al. 2019).
- **Symmetry/mirror check:** true objects and their multipath ghosts often appear at ranges related by reflection geometry off a known planar surface (if road-boundary/wall geometry is estimable from LiDAR); a ghost candidate whose range/azimuth is consistent with a mirror-image of a stronger nearby detection across a plausible reflecting surface can be down-weighted. This is a heavier lift (needs a per-frame plane estimate, e.g., from LiDAR ground/wall segmentation) and should be flag-gated, analogous to 1.4.
- **Practical recommendation:** for a first pass, use 1.2 with a conservative τ and cross-validate radar-only detections against LiDAR/camera co-visibility — if `radar_visible=True` but both LiDAR and camera scores are ~0 at a *plausible* mirrored position rather than the annotated position, flag as a probable-ghost artifact rather than silently trusting the radar score.

### 6.2 LiDAR: Occlusion Beyond Point Counts
Three escalating techniques, in order of cost:
1. **Expected-density normalization (2.2)** — implicit occlusion sensitivity, free.
2. **Ray-casting/frustum occupancy (2.3)** — explicit, distinguishes occluder-caused misses from self-occlusion/range-limit misses, moderate cost via range-image rasterization.
3. **Inter-object occlusion attribution** — once 2.3 flags `occluded_fraction>0`, determine *which* other annotated box is the occluder by checking whether the failing rays' angular footprint overlaps another box's angular footprint at a *nearer* range: `occluder = argmin_j{ r_j : ray_angle ∈ footprint(box_j) ∧ r_j < r(box_i) }`. This gives an explicit occlusion graph per frame (who occludes whom), useful both as a `*_score` input and as a rich debugging/QA artifact for the annotation pipeline itself. Cost is O(M²) box-pair angular overlap checks per frame in the worst case, but M (objects per frame) is small (tens), so this is cheap in absolute terms.
4. **"Complete object" shape-prior comparison** — compare the observed partial point cloud's fitted extent against a class-conditional expected extent (e.g., median L/W/H per class from the K-Radar training-set annotations), and treat large shortfalls not explained by range/angular resolution as occlusion evidence. This is essentially a nonparametric version of amodal shape completion (cf. Yuan et al. 2018, "PCN: Point Completion Network," for the general amodal-completion idea) but implemented as a lightweight lookup table rather than a learned model, keeping it CPU-cheap. Recommended as a good middle ground between 2.3's rigor and full learned amodal completion's cost.

### 6.3 Camera: Beyond Depth-Buffer
- **Amodal completion (learned):** as in 4.4, predicts the object's full extent even where occluded; highest fidelity, highest cost — treat as offline-audit only per the CPU constraint.
- **Learned visibility classifiers:** a lightweight classifier trained on (crop, projected-box-metadata) → visibility-level, similar in spirit to nuScenes' human-annotated visibility bins but automated; still a learned-model dependency, same caveats as 4.4 regarding weather-domain shift.
- **Mask overlap (4.4)** and **stereo/flow consistency (4.5)** as detailed above — the two most CPU-tractable "beyond depth-buffer" options.
- **Cross-camera consistency (novel, cheap):** K-Radar's 4 cameras have overlapping FOV at boundaries; an object visible in only 1 of 2 cameras that should both see it (given its 3D position and each camera's known FOV) is informative of occlusion specific to one viewpoint — a free byproduct of running 4.2 across all 4 cameras and comparing scores, requiring no new sensor processing at all.

---

## 7. Recommended Pipeline (Theoretical Optimal, CPU-Only)

Given the constraints (CPU-only, no full-4DRT default, vectorizable per-frame, half-extent-aware, graceful degradation), the recommended production combination is:

1. **Radar:** keep **1.2 (SNR-weighted power density)** as the default score. Add **1.3 (Doppler-coherence gating)** as an optional refinement restricted to a per-object cropped Doppler sub-volume (not the full 4DRT) — this keeps memory bounded while substantially improving precision against multipath ghosts, which is otherwise the largest unaddressed error source in the current baseline. Reserve **1.4** strictly for offline validation on a sampled subset (e.g., 1–2% of frames) to periodically calibrate 1.2's τ and confirm no systematic score drift across weather splits.

2. **LiDAR (both 64 and 128):** keep **2.2 (expected-density normalization)** as the default score, parametrized separately per sensor via each unit's channel/elevation LUT. Upgrade to **2.3 (ray-casting/frustum occupancy)** as the standard occlusion-aware augmentation — its marginal cost (one range-image rasterization per frame, reused across all objects) is low relative to its correctness gain, and it directly satisfies the brief's explicit ask for LiDAR occlusion reasoning. Add the **inter-object occlusion graph (§6.2.3)** as a cheap O(M²) by-product for QA/debugging and as an optional feature for downstream fusion.

3. **Camera (×4):** keep **4.2 (8-corner projection area/centrality)** as the default score, with distortion-corrected corner projection. Enable **4.3 (LiDAR depth-buffer occlusion discount)** by default rather than purely flag-gated — since the LiDAR point cloud is already loaded for step 2, the marginal cost of projecting it into each camera's frame once (shared across all objects in that camera) is modest, and this most directly closes the "occlusion beyond area/centrality" gap the baseline explicitly lacks. Add **4.5 (stereo consistency)** specifically for the front camera pair if K-Radar's rig confirms genuine stereo overlap there. Treat **4.4 (instance-mask overlap)** as an offline-only audit method, consistent with the LiDAR/radar pattern of gating the most expensive/highest-fidelity method behind an explicit flag.

4. **Fusion-level sanity check:** compute all three sensors' `*_visible` per object and flag `radar_visible=True ∧ lidar_visible=False ∧ camera_visible=False` as a probable radar-ghost/multipath case (§6.1) for manual review or automatic down-weighting — this cross-sensor consistency check costs nothing beyond values already computed and is the highest-leverage "free" quality signal available given K-Radar's tri-modal setup.

**Why this combination is optimal under the stated constraints:** every default-on method is O(1)–O(N) per object with shared per-frame amortized precomputation (radar noise-floor map once; LiDAR range-image once; LiDAR→camera projection once per camera) — so total per-frame cost stays roughly O(N_points + N_radar_cells + M·const) rather than scaling with M×(expensive-op), which is what would happen if amodal segmentation or full-4DRT integration were made default. Every gated/offline method is reserved specifically for periodic calibration/audit rather than production scoring, matching the brief's memory and CPU constraints while still providing a path to higher-fidelity ground truth when needed.

---

## 8. Bibliography

- Paek, D.-H., Kong, S.-H., Wijaya, K.T. (2022). *K-Radar: 4D Radar Object Detection Dataset and Benchmark for Autonomous Driving in Various Weather Conditions.* NeurIPS Datasets & Benchmarks. arXiv:2206.08171.
- Geiger, A., Lenz, P., Urtasun, R. (2012). *Are we ready for Autonomous Driving? The KITTI Vision Benchmark Suite.* CVPR.
- Caesar, H. et al. (2020). *nuScenes: A Multimodal Dataset for Autonomous Driving.* CVPR.
- Sun, P. et al. (2020). *Scalability in Perception for Autonomous Driving: Waymo Open Dataset.* CVPR.
- Team OpenPCDet (2020–). *OpenPCDet: An Open-source Toolbox for 3D Object Detection from Point Clouds.* GitHub.
- Zhou, Y., Tuzel, O. (2018). *VoxelNet: End-to-End Learning for Point Cloud Based 3D Object Detection.* CVPR.
- Yan, Y., Mao, Y., Li, B. (2018). *SECOND: Sparsely Embedded Convolutional Detection.* Sensors.
- Wang, T. et al. (2021). *FCOS3D: Fully Convolutional One-Stage Monocular 3D Object Detection.* ICCV Workshops.
- Rohling, H. (1983). *Radar CFAR Thresholding in Clutter and Multiple Target Situations.* IEEE Trans. Aerospace and Electronic Systems.
- Richards, M.A. (2014). *Fundamentals of Radar Signal Processing*, 2nd ed. McGraw-Hill.
- Skolnik, M. (2008). *Radar Handbook*, 3rd ed. McGraw-Hill.
- Palffy, A. et al. (2022). *View-of-Delft: A Multi-Class RGB-D-Radar Dataset.* IEEE RA-L.
- Rebut, J. et al. (2022). *RADIal: Raw Levels of Radar Imaging for Automotive Perception.* CVPR.
- Schumann, O. et al. (2021). *RadarScenes: A Real-World Radar Point Cloud Data Set for Automotive Applications.* IEEE FUSION.
- Kellner, D. et al. (2013). *Instantaneous Ego-Motion Estimation using Doppler Radar.* IEEE ITSC.
- Bilik, I. et al. (2019). *The Rise of Radar for Autonomous Vehicles: Signal Processing Solutions and Future Research Directions.* IEEE Signal Processing Magazine.
- Levinson, J., Thrun, S. (2010). *Robust Vehicle Localization in Urban Environments Using Probabilistic Maps* (LiDAR intensity calibration discussion). ICRA.
- Hoermann, S., Bach, M., Dietmayer, K. (2018). *Dynamic Occupancy Grid Prediction for Urban Autonomous Driving.* ICRA.
- Dai, A. et al. (2018). *ScanComplete: Large-Scale Scene Completion and Semantic Segmentation for 3D Scans.* CVPR.
- Yuan, W. et al. (2018). *PCN: Point Completion Network.* 3DV.
- Zhu, Y. et al. (2017). *Semantic Amodal Segmentation.* CVPR.
- Qi, S. et al. (2019). *3D Amodal Instance Segmentation.* related amodal-3D literature.
- Sun, D., Roth, S., Black, M. (2010). *Secrets of Optical Flow Estimation and Their Principles.* CVPR.
- Scharstein, D., Szeliski, R. (2002). *A Taxonomy and Evaluation of Dense Two-Frame Stereo Correspondence Algorithms.* IJCV.
- Hirschmuller, H. (2008). *Stereo Processing by Semi-Global Matching and Mutual Information.* IEEE TPAMI.
- ISO 26262-1:2018. *Road vehicles — Functional safety* (sensor visibility/perception-reliability definitions referenced for terminology only, not a technical formula source).

---

*Notes on implementation caution: every formula above assumes box dimensions have already been converted from K-Radar's stored half-extents to full extents; every volumetric/area normalization (`V_box`, `A_full`) will silently be off by 8× (2³) or 4× (2²) if this conversion is skipped. Recommend adding a unit test that asserts `V_box` for a canonical annotation matches an independently hand-computed value.*
