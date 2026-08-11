# Common Corruption Robustness of Point Cloud Detectors

#ReferPaper #corruption/lidar/benchmark #important

Li, Wang, Juefei-Xu, Guo, Li, Ma (U. Alberta / Kyushu U. / NTU / NYU). ~2022.

## Contribution

First large-scale physical-aware robustness benchmark for LiDAR 3D object detectors against common real-world corruption: **1,122,150 examples, 7,481 scenes, 25 corruption types, 6 severity levels (0=clean, 1–5)**, evaluated on 8 detectors (PVRCNN, PointRCNN, SECOND, BtcDet, VoTr-SSD, VoTr-TSD, SE-SSD, Centerpoint). Built on KITTI.

## Exact parameters — source paper for this project's Gaussian Noise AND Loss/Partial implementations

**Scene-level radial noise** (spherical coords, noise on radial coordinate r):
- `uniform_rad`: bounds ±{0, 0.04, 0.08, 0.12, 0.16, 0.2} m (severity 0–5)
- `gaussian_rad`: σ = {0, 0.04, 0.06, 0.08, 0.10, 0.12} m
- `impulse_rad`: ±0.2 m deterministic perturbation on portion {0, N/30, N/25, N/20, N/15, N/10} of points

**Object-level Cartesian noise:**
- `uniform_obj`: bounds ±{0, 0.02, 0.04, 0.06, 0.08, 0.10} m
- `gaussian_obj`: σ = {0, 0.02, 0.03, 0.04, 0.05, 0.06} m
- `impulse_obj`: ±0.1 m bias on portion {0, N/30...N/10}

**Loss/density corruptions (the "partial loss" family):**
- `cutout` (scene): KNN-erase around selected centers, (portion, neighbors) = {(0,0), (N/2000,100)...(N/600,100)}
- `local_dec` (scene): delete 75% of points in a spatial neighborhood, (portion, neighbors) = {(0,0), (N/300,100)...(N/100,100)}
- `beam_del`: delete portion {0, N/100, N/30, N/10, N/5, N/3} of points
- `layer_del`: bin polar angle θ into 64 layers (matches KITTI's 64-beam LiDAR), delete {0,3,7,11,15,19} random bins
- `background`: add uniform random noise points, count {0, N/45...N/20}

**Weather** (physics-based simulators, not generic noise): rain/snow via LISA simulator, rainfall {0,5,15,50,150,500} mm/hr, snow {0,0.5,1.5,5,15,50} mm/hr; fog via LFS simulator, attenuation α = {0,0.005,0.01,0.02,0.05,0.1}.

**Transformation:** shear, FFD (free-form deformation, 5×5×5 control points), scale (±20%), rotation (up to 10°), translation (up to ~1m).

## Key findings

- Average mCE_AP = 11.01% (Car) across all detectors/corruptions. **Worst: snow (45.64%), shear (39.71%), FFD (34.93%), rain (26.45%).** Fog surprisingly mild (1.88%) — mostly attenuates points that are already zero-intensity in clean KITTI, so the marginal effect is small.
- Rain's error stays ~flat (~26%) across all 5 severities — an anomalous non-monotonic trend attributed to sparse rain-droplet noise saturating quickly.
- Voxel-based detectors more robust than point-based; one-stage generally more robust than two-stage, **except** under cutout/local_dec/beam_del/layer_del and shape transforms, where two-stage wins.
- Existing robustness enhancements are largely ineffective: Part-Aware Data Augmentation barely helps (mCE_AP 11.01%→10.85%); KNN-based outlier removal actually **worsens** Car-detection robustness (→13.60%) though it modestly helps Pedestrian.

## Relevance to AMSCUP

This is the direct numeric-parameter source for this project's LiDAR Gaussian Noise and Loss Partial corruptions (see [[04_Design/Noise_Taxonomy]]) — the σ sweeps and portion-of-points formulas above are the template this project's own severity ladder (`severity_parameters.yaml`, [[06_Results/Noise_Visual_Inspection]]) should be checked against for consistency of scale.

## Source

- `docs/lit_survey/noise_addition/markdown/CommonCorruption.md` (784 L)
