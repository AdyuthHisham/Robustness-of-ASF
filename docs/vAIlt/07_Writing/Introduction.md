# Introduction

## Background

Autonomous-vehicle perception depends on fusing complementary sensor modalities — camera, LiDAR, and radar — each with a distinct failure profile. Cameras carry rich semantic information but degrade under poor lighting, glare, and precipitation. LiDAR delivers precise 3D geometry but is attenuated by fog, rain, and snow, and can return false positives from precipitation particles. Radar is comparatively weather-robust (it operates at a wavelength, ~4mm at 77–81GHz, that largely passes through rain, fog, and snow rather than scattering off them) but provides much lower spatial resolution than the other two. No single modality is sufficient on its own; effective fusion is what makes robust perception possible.

The gap this project sits in is that **most published fusion benchmarks evaluate under favorable conditions** — clear weather, daytime, uncrowded roads — and report performance under exactly those conditions. The K-Radar dataset was built specifically to break that pattern: 35K frames across fog, rain, sleet, and snow, with 4D radar tensors, dual LiDAR (OS2-64/OS1-128), four-camera stereo coverage, and RTK-GPS, collected partly in Gangwon-do, Korea's highest-snowfall province (see [[02_Literature/KRadar_Dataset_Paper]]). Its own baseline comparison — radar-based detection holding steady while LiDAR-based detection drops 22–30 AP points under sleet and heavy snow, on the *same* scenes and objects — is the empirical anchor this entire project's premise rests on: sensor robustness under weather is not a marginal effect, it is large enough to change which sensor should be trusted when.

## Problem Statement

Knowing *that* sensors fail differently under weather is not the same as being able to say, for a specific object in a specific frame, *which* sensor to trust. K-Radar ships per-frame weather labels and per-sequence sensor data, but no continuous, per-object measure of how visible a given annotated object actually was to each sensor — that has to be computed. This project's first deliverable, the `kradar_visibility` pipeline, exists to close that gap: for every annotated object in every frame, it produces a physics-grounded visibility score per sensor (SNR-weighted power density for radar, point-density ratio for LiDAR, projected-area × centrality for camera — see [[03_Theory/Visibility_Formulas]]), not just a binary present/absent flag.

That per-object visibility signal is the foundation for the second, larger problem: **building a robust test set**. A sensor-fusion model's clean-data accuracy says nothing about how it degrades when a sensor is noisy, partially lost, or entirely absent — and the failure modes documented across this project's literature survey (see [[02_Literature/Literature_Survey]]) show that fusion architectures do not degrade gracefully by default. Complete LiDAR loss crashes naive fusion systems outright; naive camera-LiDAR fusion can perform *worse* than camera alone under dense fog, because the implicit "the other sensor will cover for me" assumption breaks under asymmetric sensor failure. Quantifying this for K-Radar specifically — not just citing that it happens elsewhere — is the problem this project's noise-injection and evaluation work addresses.

## Research Questions

1. **How visible is a given annotated object to each sensor, as a continuous physics-grounded score rather than a binary flag** — and does that score behave as the underlying sensor physics predicts (e.g. radar score staying stable while LiDAR score drops under adverse weather, for the same object)?
2. **How does synthetic, parameterized sensor corruption (frame deletion, Gaussian/coordinate-shift noise, partial signal loss) affect downstream inference**, and does the effect track what real-world weather degradation in K-Radar already shows for LiDAR vs. radar?
3. **Can a robust test-set methodology built on visibility-stratified, corruption-injected K-Radar data reveal fusion-model failure modes** that clean-data evaluation on the same dataset would not surface?

These sit inside, and motivate, the broader thesis-level research questions on cross-dataset generalization and sensor-fusion robustness under adverse conditions (`docs/Latex_Report/thesis_report/include/Introduction.tex`) — this project is the K-Radar-specific empirical arm of that broader investigation, not a separate undertaking.

## Scope and Objectives

**In scope**: a CPU-only, toy-scale-validated visibility pipeline for K-Radar (radar/LiDAR-64/LiDAR-128/4×camera, one Parquet row per annotated object per frame); a parameterized noise-injection suite for LiDAR/camera/radar (frame deletion, Gaussian/coordinate-shift noise, partial/complete loss — see [[04_Design/Noise_Taxonomy]]) drawn from and cross-checked against the surveyed corruption-benchmark literature; the battle-plan methodology of baseline inference → visibility-based robust test-set construction → noise injection → comparative inference → metrics (`Small_Brown_Book.md`).

**Explicitly out of scope for this arm of the project** (per `test-bed/.../kradar/README.md` and `kradar_task_brief.md`): GPU-accelerated point-in-box testing; full 58-sequence, full-dataset runs (current validation is 1–2 sequences, ≤20 annotated frames); the full 4DRT radar tensor (the pipeline uses the pre-processed `radar_zyx_cube`, never the 64M-cell/frame tesseract); Doppler-coherence radar gating (K-Radar provides no RTK-GPS/INS stream to make this feasible); camera temporal consistency (the pipeline is deliberately per-frame and stateless).

## Document Structure (this project's arm of the vault)

`02_Literature` surveys the 12 papers this project's noise taxonomy and robustness-testing methodology draw from, organized by theme with an explicit account of where they disagree. `03_Theory` covers the visibility-scoring formulas, K-Radar's radar-frame coordinate convention, and the literature-derived sensor noise/degradation model. `04_Design` covers the corruption taxonomy actually selected for implementation, system architecture, API contracts, and output schema. `05_Implementation` holds the pipeline module and config documentation. `06_Results` holds the merged verification-report audit trail and the rendered noise-visual-inspection gallery with exact severity parameters. `07_Writing` (this section) maps this project's work back onto the broader thesis structure (see [[Vault_to_Thesis_Mapping]] and [[LaTeX_Report_Structure]]).

## Source

- `test-bed/src/Modules/robust_testing/kradar/README.md`
- `docs/Small_Brown_Book.md` (battle plan)
- `docs/kradar_task_brief.md` (master task brief)
- `docs/Latex_Report/thesis_report/include/Introduction.tex` (broader thesis framing — read-only)
