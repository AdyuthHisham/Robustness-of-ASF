# Task-Conditioned Normalization for Cross-Modal Sensor Contribution Analysis (K-Radar)

## Purpose

This document specifies an implementable pipeline for quantifying how much each sensing modality — LiDAR, 4D radar, camera — contributes to successfully identifying an object in the K-Radar dataset. The output is a per-modality, per-object score on a common scale (probability of correct detection), stratified by range and weather, so that contributions can be compared fairly across modalities that otherwise report incommensurable units (points/m³, tensor power, pixels).

---

## 1. Background and Motivation

### 1.1 Why raw sensor statistics cannot be compared directly

Each modality in K-Radar is a structurally different measurement process:

- **LiDAR** produces a 3D point cloud via time-of-flight ranging. Native unit: points per unit volume.
- **4D Radar** in K-Radar is natively a **dense power tensor** over (Doppler, range, azimuth, elevation) — points are only obtained after a thresholding/detection stage. The dataset's own documentation notes that usable point density is an engineered trade-off (typically 3–10% of measurements retained) against sidelobe noise, meaning radar "density" is detector-threshold-dependent, not a fixed sensor property (Paek, Kong & Lee, *K-Radar*, NeurIPS 2022 Datasets & Benchmarks Track; [arXiv:2206.08171](https://arxiv.org/abs/2206.08171); [GitHub](https://github.com/kaist-avelab/K-Radar)).
- **Camera** produces a 2D projection via the pinhole model. Native unit: pixels, confounded by range and focal length.

A raw value (e.g., "340 LiDAR points" vs. "pixel coverage of 1800 px²") cannot be meaningfully compared because the units, scales, and underlying physical processes differ. **Task-conditioned normalization** solves this by mapping each modality's raw quantity through an empirically fit function onto a shared, meaningful scale: *the probability that an object is correctly detected/identified given that sensor's reading*.

### 1.2 Core idea

Instead of asking "how dense is this object's sensor data," ask: **"empirically, across the dataset, what is the detection success rate at this density level?"** This converts an arbitrary unit into a probability — comparable across modalities by construction — and ties the metric directly to the project's actual objective (identifying objects), rather than to an abstract statistical property of the raw signal.

This is conceptually the same move made implicitly in sensor-fusion ablation literature when arguing that one modality "contributes more" in a given regime (e.g., RadarNet, Yang et al., ECCV 2020; CenterFusion, Nabati & Qi, WACV 2021) — this pipeline makes that argument explicit and quantitative rather than qualitative.

### 1.3 Why stratify by range and weather

K-Radar's defining characteristic, and its primary empirical claim, is that **relative sensor reliability changes systematically with weather** — the original paper demonstrates 4D radar is more robust than LiDAR specifically in adverse conditions (fog, rain, snow) across varied road structures (Paek, Kong & Lee, NeurIPS 2022). A single global calibration curve computed over the whole dataset would average over exactly this effect and erase the signal the dataset was built to expose. Similarly, both LiDAR point density and camera pixel coverage fall off geometrically with range (≈ 1/r² under a Lambertian/uniform angular sampling assumption), so a fixed raw threshold means different things at 10 m versus 80 m. Stratification by `(range_bucket × weather_condition)` is therefore mandatory, not optional.

**Caveat carried over from the geometric correction discussion:** these range-based effects assume Lambertian reflectance and ignore atmospheric attenuation. In fog/rain/snow, the real signal loss includes additional scattering/absorption not captured by simple 1/r² or 1/r⁴ falloff models. Stratifying by weather *category* (rather than trying to model attenuation continuously) is the practical workaround used in this pipeline — see Section 6.

---

## 2. Mathematical Formulation

### 2.1 Per-modality raw quantities

For object $O$, modality $m \in \{\text{lidar, radar, camera}\}$:

- **LiDAR:** $\rho_{\text{lidar}}(O) = N_{\text{pts}}(O) / V_{\text{box}}(O)$ — points per m³ within the 3D box.
- **Radar:** $E_{\text{radar}}(O) = \int_{\mathcal{R}_{\text{obj}}} P(d, r, \theta, \phi)\, dd\, dr\, d\theta\, d\phi$ — power integral over the 4D tensor region corresponding to the projected box. (Secondary/derived: point count after CFAR/threshold $\tau$.)
- **Camera:** $\tilde\rho_{\text{cam}}(O) = \dfrac{N_{\text{px}}(O)}{|\mathcal{A}_{\text{img}}(O)|} \cdot r(O)^2$ — range-normalized pixel density on the projected box region.

### 2.2 Detection outcome label

For each annotated ground-truth object $O$, define a binary (or graded) outcome from a trained detector's predictions, using standard IoU-based matching (as in KITTI/nuScenes evaluation protocols):

$$
y(O) = \mathbb{1}\big[\exists\, \hat{O} : \text{IoU}_{3D}(O, \hat{O}) \ge \tau_{\text{IoU}}\ \wedge\ \text{class}(\hat O) = \text{class}(O)\big]
$$

Graded alternative: use the matched prediction's confidence score $s(\hat O) \in [0,1]$ instead of a hard 0/1 label, if you want a continuous outcome rather than success/failure.

### 2.3 Calibration function (the core object being estimated)

For modality $m$ and stratum $z = (\text{range\_bucket}, \text{weather})$, fit a monotonic function:

$$
g_{m,z}: v_m \mapsto \hat{P}(y = 1 \mid V_m = v_m,\ Z = z)
$$

i.e., the empirical probability of successful detection given that modality's raw reading, within stratum $z$. This is a 1D calibration/regression problem — isotonic regression or binned empirical frequency are both appropriate (see Section 4).

### 2.4 Normalized contribution score

The task-conditioned score for object $O$, modality $m$:

$$
\hat{c}_m(O) = g_{m,\,z(O)}\big(v_m(O)\big) \in [0,1]
$$

All three modalities' scores now live on the same scale — "implied probability of correct detection" — and are directly comparable, summable, or usable as fusion-gating weights.

### 2.5 Aggregate contribution metrics

Over a stratum $z$ or the full dataset $\mathcal{D}$:

- **Mean contribution:** $\bar{c}_m(z) = \frac{1}{|\mathcal{D}_z|}\sum_{O \in \mathcal{D}_z} \hat{c}_m(O)$
- **Relative contribution share** (normalize across modalities so they sum to 1, useful for stacked-bar visualization):
$$
w_m(O) = \frac{\hat{c}_m(O)}{\sum_{m' \in \{\text{lidar,radar,camera}\}} \hat{c}_{m'}(O)}
$$
- **Marginal contribution (ablation-based, complementary check):** $\Delta_m = \text{AP}_{\text{full}} - \text{AP}_{\setminus m}$, i.e., AP drop when modality $m$ is removed from a fusion model. This is the standard ablation metric used in BEVFusion (Liu et al., ICRA 2023) and RadarNet (Yang et al., ECCV 2020); it should be computed alongside $\hat c_m$ as a sanity check, since it answers a related but distinct question (marginal value to a *specific fusion architecture* vs. intrinsic informativeness of the raw signal).

---

## 3. Literature Review — Implementation-Relevant Sources

| Source | Relevance to this pipeline |
|---|---|
| **Paek, Kong & Lee, "K-Radar," NeurIPS 2022** ([arXiv:2206.08171](https://arxiv.org/abs/2206.08171)) | Defines the dataset's native radar tensor representation, weather/road metadata needed for stratification, and the baseline detector (RTNH) usable as the detector in Section 2.2. |
| **Geiger et al., "KITTI," CVPR 2012** | Source of the standard 3D IoU-based matching protocol used in Eq. 2.2; also defines the calibration chain for projecting boxes to compute camera pixel coverage. |
| **Caesar et al., "nuScenes," CVPR 2020** | Defines range-stratified and visibility-stratified AP evaluation (nuScenes Detection Score), the closest existing precedent for the `(range × weather)` stratification proposed here. |
| **Lang et al., "PointPillars," CVPR 2019** | Source of the pillar/voxel point-density framing for $\rho_{\text{lidar}}$; useful baseline detector architecture for generating $y(O)$ from LiDAR-only input. |
| **Yin, Zhou & Krähenbühl, "CenterPoint," CVPR 2021** | Center-based detection head; recommended as the common detector head across modality-specific baselines so that $y(O)$ is computed consistently regardless of which modality is the input. |
| **Yang et al., "RadarNet," ECCV 2020** | Precedent for radar-LiDAR fusion ablations and marginal-contribution (Δ AP) analysis (Section 2.5). |
| **Nabati & Qi, "CenterFusion," WACV 2021** | Precedent for associating radar returns to camera-detected object centers; relevant if extending this pipeline to frustum-based cross-modal association. |
| **Liu et al., "BEVFusion," ICRA 2023** | Standard architecture for modality-ablation studies; the $\Delta_m$ metric in Section 2.5 mirrors BEVFusion's reported per-modality ablations. |
| **Zadrozny & Elkan, "Transforming Classifier Scores into Accurate Multiclass Probability Estimates," KDD 2002** | Foundational reference for isotonic regression as a calibration method — directly applicable to fitting $g_{m,z}$ in Section 2.3. |
| **Platt, "Probabilistic Outputs for Support Vector Machines," 1999** | Alternative parametric calibration method (logistic/Platt scaling) if isotonic regression is too data-hungry per stratum. |
| **Guo, Pleiss, Sun & Weinberger, "On Calibration of Modern Neural Networks," ICML 2017** | Background on reliability diagrams and calibration evaluation (ECE) — useful for validating that $g_{m,z}$ is well-calibrated, not just monotonic. |

---

## 4. Implementation Pipeline

### Step 1 — Compute raw per-object quantities

For every annotated object $O$ in every frame:
1. Extract $\rho_{\text{lidar}}(O)$ from the synchronized LiDAR sweep within the 3D box.
2. Extract $E_{\text{radar}}(O)$ from the 4DRT cube using the projected 3D box region into (Doppler, range, azimuth, elevation) index space.
3. Project the 3D box into each camera (standard $P = K[R|t]$ pipeline) and compute $\tilde\rho_{\text{cam}}(O)$ per visible camera.
4. Tag each object with metadata: `range_bucket` (e.g., 0–20m, 20–40m, 40–60m, 60m+), `weather` (clear/fog/rain/snow, from K-Radar's recorded condition labels), `road_type` (urban/suburban/highway/alleyway), `class` (sedan/bus-truck/pedestrian/bicycle).

### Step 2 — Generate detection outcomes

Train (or use a provided baseline) a single-modality detector per modality:
- LiDAR-only detector (e.g., PointPillars or CenterPoint backbone).
- Radar-only detector (e.g., K-Radar's RTNH baseline operating on 4DRT).
- Camera-only detector (e.g., monocular or multi-view 3D detector such as a PETR/DETR3D-style head, acknowledging the inherent depth ambiguity — see caveats).

Run each on a held-out evaluation split, match predictions to ground truth via 3D IoU (Eq. 2.2), and record $y(O)$ (or $s(\hat O)$) per object per modality.

> **Important:** Use the *same* matching threshold $\tau_{\text{IoU}}$ and the *same* evaluation split across all three modality-specific detectors so that $y(O)$ is comparable across modalities — otherwise differences in $g_{m,z}$ partly reflect detector/threshold differences rather than sensor informativeness.

### Step 3 — Stratify

Partition the evaluation set into strata $z = (\text{range\_bucket}, \text{weather})$. Use a coarse grid initially (e.g., 4 range buckets × 4 weather categories = 16 strata) to keep per-stratum sample counts viable; refine only where data density allows.

### Step 4 — Fit the calibration function $g_{m,z}$

For each `(modality, stratum)` pair:
1. Collect all $(v_m(O), y(O))$ pairs for objects $O \in \mathcal{D}_z$.
2. Fit $g_{m,z}$ via **isotonic regression** (monotonic, non-parametric, no shape assumption — appropriate here since we expect "more signal → higher detection probability" but not necessarily a specific functional form). Use `sklearn.isotonic.IsotonicRegression`.
3. If a stratum has too few samples for stable isotonic fitting (common for rare combinations like "bicycle + snow + 60m+"), fall back to:
   - A simpler **binned empirical frequency** estimator (fixed-width or fixed-count bins on $v_m$, plot mean $y$ per bin), or
   - **Platt scaling** (1-parameter logistic fit) for low-data strata, accepting the added shape assumption.
4. Validate calibration quality via a **reliability diagram** and **Expected Calibration Error (ECE)** per `(modality, stratum)` pair (Guo et al., ICML 2017), reporting ECE alongside results so consumers of this analysis know how trustworthy each stratum's curve is.

### Step 5 — Score and aggregate

1. Apply $\hat c_m(O) = g_{m, z(O)}(v_m(O))$ to every object in the full dataset (not just the calibration split — use cross-validation or a held-out calibration set vs. scoring set to avoid overfitting the calibration curve to itself).
2. Compute aggregate metrics from Section 2.5: mean contribution per modality per stratum, relative contribution shares, and (as a cross-check) ablation-based $\Delta_m$ from a jointly-trained fusion model.
3. Visualize: heatmap of $\bar c_m(z)$ over the `(range × weather)` grid, one per modality — this is the primary deliverable, directly showing where/when each sensor's signal translates into actual identification capability.

### Step 6 — Cross-validation / robustness checks

- **K-fold over scenes** (not frames) to avoid temporal leakage between calibration and scoring sets, since adjacent frames in a driving sequence are highly correlated.
- **Sensitivity to $\tau_{\text{IoU}}$:** repeat Step 2 at two or three IoU thresholds (e.g., 0.25, 0.5, 0.7) and confirm relative modality rankings are stable — if rankings flip with threshold choice, report this explicitly rather than picking one threshold silently.
- **Sensitivity to detector choice:** where feasible, repeat Step 2 with a second architecture per modality to check that $g_{m,z}$ reflects the sensor's informativeness rather than one specific detector's idiosyncrasies.

---

## 5. Suggested Repository Structure

```
contribution_analysis/
├── extract_raw_quantities.py      # Step 1: rho_lidar, E_radar, rho_cam per object
├── run_modality_detectors.py      # Step 2: single-modality detection + IoU matching
├── stratify.py                    # Step 3: range/weather bucket assignment
├── fit_calibration.py             # Step 4: isotonic regression / binning per (m, z)
├── score_objects.py               # Step 5: apply g_{m,z}, compute c_m(O)
├── aggregate_and_plot.py          # Step 5: heatmaps, bar charts, summary tables
├── robustness_checks.py           # Step 6: k-fold, IoU sensitivity, detector sensitivity
└── configs/
    ├── range_buckets.yaml
    ├── weather_categories.yaml
    └── iou_thresholds.yaml
```

---

## 6. Limitations (carry-over caveats relevant to this specific strategy)

- **Detector dependence:** $y(O)$ depends on the choice of single-modality detector architecture and training; a weak radar-only baseline will understate radar's true informativeness regardless of how good the underlying signal is. Mitigate via Step 6's detector-sensitivity check.
- **Weather as a discrete category, not a continuous attenuation model:** stratifying by weather *label* (clear/fog/rain/snow) sidesteps — rather than solves — the open problem of modeling continuous atmospheric attenuation ($\propto e^{-\alpha r}$, with $\alpha$ varying by fog/rain intensity). This is an intentional simplification: it is tractable with the labels K-Radar provides, but it will blur within-category variation (e.g., light fog vs. dense fog are both just "fog").
- **Sample sparsity in rare strata:** combinations like rare class × extreme weather × long range will have few samples, producing noisy or unreliable $g_{m,z}$ — flag low-sample strata explicitly (e.g., grey out or annotate with sample count on heatmaps) rather than silently reporting an unreliable number.
- **IoU-matching threshold is itself a modeling choice**, not a ground truth — different thresholds can shift which modality "looks better," so report sensitivity (Step 6) rather than a single threshold's results as definitive.
- **Camera-only detection's depth ambiguity** (Section 2.4, Step 5 of the projection pipeline in the broader project) means a camera-only detector's $y(O)$ partly reflects how well the *depth estimation* sub-component works, not purely 2D visual informativeness — worth noting when interpreting low camera contribution scores.
