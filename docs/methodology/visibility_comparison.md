# Visibility Metrics Comparison (ELI15)

This document compares how we measure *visibility* for three different sensors used in the K‑Radar project: **camera**, **LiDAR**, and **radar**.  The goal is to explain the chosen method for each sensor in simple language (like you would explain to a 15‑year‑old), why we picked that method, and why we didn’t use the other options.

---

## 1. Radar – `radar_sparsity_score`

### How we measure it (Method B – SNR‑weighted power density)
- Radar data comes as a 3‑D cube (`radar_zyx_cube`) that stores the power of the radar return at each point in space.
- For each object we look at the *oriented bounding box* (the 3‑D box that fits the object) and sum the **extra** power inside that box **above the background noise**.
- The background noise is estimated for each frame by looking at the quiet parts of the cube (the median power outside any objects).
- The final score is:
```
score = sum(max(0, power - noise_floor) for all cells inside the box) / box_volume
```
- The score is a continuous number; a higher score means the object is “brighter” to the radar.

### Why we chose this method
- **Adapts to distance:** Radar noise changes with range, so estimating the noise floor per‑frame makes the score fair for near and far objects.
- **Runs on the CPU:** It only needs one pass through the cube, which fits the project’s *CPU‑only* constraint.
- **Vectorizable:** The same operation can be applied to many objects in parallel, keeping it fast.

### Why we rejected the other ideas
- **Method A – Binary cell‑count:** It just counts cells above a fixed threshold. That threshold is the same for every frame, so far objects get a score of zero even if they are visible.
- **Method C – Full 4‑DRT integration:** This would load the entire 4‑D radar tensor (64 M cells) for every frame, breaking the *memory‑efficiency* sub‑goal and making the program too heavy for a CPU‑only run.

---

## 2. LiDAR – `lidar*_sparsity_score`

### How we measure it (Method A + B)
1. **Raw point count (Method A)** – We count how many LiDAR points fall inside the object’s bounding box. This uses a CPU‑based `points_in_boxes` routine (a lightweight version of the existing GPU kernel).
2. **Expected‑density normalization (Method B)** – We compute how many points we would *expect* to see in that box based on the LiDAR sensor’s specs (number of laser channels, angular resolution, and the box’s size and distance). Then:
```
score = actual_count / expected_count   (clamped to 0‑1)
```
- The score is a 0‑1 value; 1 means the object is fully visible, 0 means it is hidden.

### Why we chose this combo
- **Re‑uses existing code:** The point‑in‑box routine is already available, so we don’t need to write a new algorithm.
- **Gives a normalized score:** By dividing by the expected count we get a metric that works for both the 64‑channel and 128‑channel LiDARs and automatically penalises far objects.
- **Cheap on CPU:** Both steps are simple array operations, staying within the CPU‑only budget.

### Why we didn’t pick the other option
- **Method C – Voxel occupancy ratio:** Voxelising every box adds an extra pass and a new hyper‑parameter (voxel size). The benefit (capturing point clustering) is small compared to the dominant effect of weather on LiDAR sparsity, so the extra cost isn’t justified.

---

## 3. Camera – `cam_*_visibility_score`

### How we measure it (Method B – 8‑corner projection)
- For each object we take the 8 corners of its 3‑D bounding box and project them into the camera image using the camera matrix `K[R|t]`.
- From the projected corners we compute a 2‑D bounding box, clip it to the image borders, and measure two things:
  1. **Area fraction:** How much of the image the object occupies (`clipped_area / image_area`).
  2. **Centrality:** How close the object’s centre is to the image centre (objects near the centre get a higher bonus).
- The final score is a weighted sum, e.g. `0.7*area + 0.3*(1‑norm_dist_to_center)`.

### Why we chose this method
- **Fast and cheap:** Only eight matrix multiplications per object, plus a tiny 2‑D bbox computation.
- **Continuous score:** Gives a smooth value that reflects both size and position, satisfying the requirement that “bigger / more central objects are more visible”.
- **Works on CPU:** No need for expensive depth‑testing or GPU rendering.

### Why we left out the other ideas
- **Method A – Center‑point only:** This only tells us *whether* the centre of the object is inside the image, not *how much* of the object we can see – not enough for a continuous visibility score.
- **Method C – Projection + LiDAR depth‑buffer occlusion:** Adding a depth‑buffer check would require projecting the LiDAR point cloud into the camera each frame, which is considerably more work. While it would improve accuracy (by discounting occluded objects), it is not required to pass the smoke tests and would exceed the CPU‑only budget for full‑dataset runs. We keep it as an optional flag for future experiments.

---

## 4. Summary Table

| Sensor | Chosen Score | Core Idea | Why Chosen | Rejected Alternatives |
|--------|--------------|-----------|------------|-----------------------|
| Radar  | `radar_sparsity_score` (Method B) | SNR‑weighted power density on `radar_zyx_cube` | Adapts to range‑dependent noise, CPU‑only, vectorizable | Binary count (A) – fixed threshold; Full 4‑DRT (C) – too memory‑heavy |
| LiDAR  | `lidar*_sparsity_score` (Method A + B) | Point‑in‑box count + expected‑density normalization | Re‑uses point‑in‑box code, gives normalized 0‑1 score, cheap | Voxel occupancy (C) – extra cost, little benefit |
| Camera | `cam_*_visibility_score` (Method B) | 8‑corner projection → 2‑D bbox area + centrality | Fast, continuous, CPU‑only, meets tests | Center‑point only (A) – Boolean; Projection + LiDAR occlusion (C) – heavy, optional |

---

### What this means for the pipeline
- All three scores are **continuous** numbers (0‑1 style) that can be written directly into the output Parquet table.
- The methods respect the project’s *memory‑efficiency* and *CPU‑only* sub‑goals, so the full dataset can be processed on a typical workstation.
- Optional, higher‑accuracy upgrades (radar full‑tesseract, camera occlusion) are kept behind configuration flags for future research without breaking the baseline workflow.

*Prepared by the Hermes‑Architect based on the visibility methodology document (04_visibility_methodology.md) and the project’s architecture notes.*
