# LiRTest: Augmenting LiDAR Point Clouds for Automated Testing of Autonomous Driving Systems

#ReferPaper #corruption/lidar/metamorphic #important

Guo, Feng, Chen (Nanjing University). ISSTA '22.

## Contribution

First automated LiDAR-based ADS testing tool using metamorphic testing with two transform families — **affine** (translation, rotation, scale, symmetry) and **physics-based weather** (rain, snow, fog) — applied to LiDAR point clouds from KITTI, tested against PointPillars, SECOND, Part-A², PV-RCNN.

## Metamorphic relations and exact parameters

**Affine family** (4 operators, label transforms with the point cloud since they're not label-preserving in general): Translation `p(x,y,z)→p(x+tx,y+ty,z+tz)`, tx∈{±2,±4,±6,±8}, ty∈{±1,±2,±3,±4}; Rotation about z-axis, q∈{−π/4,−π/6,−π/8,π/8,π/6,π/4}; Scale, factor 1.05–1.25 step 0.05; Symmetry (mirror about XOZ plane), no params.

**Weather family** (3 operators, physics-based attenuation model, label-preserving — this is the key methodological difference from the affine family):
- Shared model: relative sensor power `P_n = P_r/C_s` as a function of weather strength `W` and empirical coefficients `a, b`, giving a fractional intensity-reduction `λ` at distance `m`.
- **Rain**: `a=0.01, b=0.6`, W swept 2–20 (step 2). Range-measurement noise deliberately **not** modeled (cited literature puts it <2% error, judged negligible).
- **Snow**: `a=0.005, b=0.5`, W swept 2–20; **plus** synthetic noise points added via N(σ) sampled over X/Y/Z, concentrated near the vehicle and decreasing with distance, σ=8 in experiments; noise-ratio parameter swept 5–50 (step 5).
- **Fog**: `a=0.015, b=0.7`, W swept 2–20; additionally modeled as a cylindrical density region around the vehicle (radius R=1.35 in experiments), density positively correlated with a fog-concentration parameter swept 10–100 (step 10).

## Key findings

- Weather transforms consistently drop AP more than affine transforms. Overall drop by class: Car −7.59%, Pedestrian −11.41%, Cyclist −14.27%.
- Worst single case: **PointPillars under Snow — AP drops 44.53 points** (64.25→19.72 mAP), the largest degradation across all model×transform combinations. Snow also produces the highest neuron-coverage perturbation (mean Jaccard distance to seed 0.47, vs. 0.10–0.30 for other transforms) — the internal-activation signal agrees with the output-level finding.
- Retraining with 10% mixed transformed data recovers 0.3–15.4pp AP depending on model/class; Cyclist benefits most (+8.4% avg), Car least (+4.1% avg) — consistent with cyclists being the sparsest, most weather-sensitive class.

## Relevance to AMSCUP

Direct methodological precedent for radar/LiDAR-side noise injection with physically-parameterized severity sweeps. The explicit choice to **not** model rain-induced range noise (judged negligible) is a useful counter-data-point if this project's own radar `noise_induced_shifts` corruption (see [[04_Design/Noise_Taxonomy]]) needs to justify why it *does* model coordinate shift as the primary radar corruption mechanism rather than intensity noise — LiRTest and this project make different modeling choices for a similar physical effect, worth reconciling explicitly rather than silently diverging.

## Limitations the paper acknowledges

Physics-based weather models "cannot cover all factors that may influence LiDAR performance" (e.g., no EMI modeling); parameters (σ=8, R=1.35, a/b coefficients) are empirically chosen, not exhaustively validated against real sensor data; scope limited to the 3D-detection subtask, not full-pipeline (tracking/fusion/planning) robustness.

## Source

- `docs/lit_survey/noise_addition/markdown/LiRTest.md` (434 L)
