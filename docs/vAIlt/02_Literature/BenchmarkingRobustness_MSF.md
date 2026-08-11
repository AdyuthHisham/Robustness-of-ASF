# Benchmarking Robustness of AI-Enabled Multi-Sensor Fusion Systems

#ReferPaper #corruption/fusion #important

Gao, Wang, Feng, Ma, Chen, Xu (Nanjing University / U. Alberta / U. Tokyo). ESEC/FSE '23.

## Contribution

First public benchmark of AI-enabled camera-LiDAR multi-sensor-fusion (MSF) perception (detection, tracking, depth completion). Builds **14 corruption patterns** into KITTI-C and evaluates 7 MSF systems (EPNet, FConv, CLOCs, JMODT, DFMOT, TWISE, MDANet) spanning deep/late/weak fusion architectures.

## Corruption taxonomy (source paper for this project's Gaussian Noise corruption)

Three categories: **Weather** (rain, fog, brightness — physics-based models, consistent across sensors, validated at 98%+ classifier accuracy against real rain/fog data), **Sensor Corruption** (distortion, motion blur, defocus blur — camera only; **Gaussian Noise** and **Impulse Noise**, each defined separately for camera pixels and LiDAR point coordinates), **Sensor Misalignment** (spatial — rotation ±0.5°/1°/2° per axis; temporal — 0.1–0.5s delay).

**Gaussian Noise definition (§3.2.2, exact wording)**: "applies Gaussian distributed noise to each point's coordinate in a point cloud or each pixel's value in an image." No numeric σ given in this paper — for exact parameter values, cross-reference [[CommonCorruption_PointCloud_Benchmark]], which specifies σ per severity level.

## Key findings

- Robustness score (avg over 7 systems, [0,1]): **Fog worst (0.29)** — depth-completion systems drop to 0.14; Rain 0.72; camera Gaussian noise (0.74) hurts more than LiDAR Gaussian noise (0.88) — **camera noise is consistently more damaging than LiDAR noise** for these fusion architectures.
- **Complete LiDAR loss crashes all 7 systems (Rb=0).** Complete camera loss crashes 3/7; MDANet uniquely survives complete camera loss but crashes under *partial* (50–75%) loss — a counterintuitive non-monotonic failure mode worth flagging.
- Spatial misalignment: Y-axis 2° rotation crashes 5/7 systems; X/Z rotations far milder. Temporal misalignment: 0.3s LiDAR delay drops tracking robustness ~60%; camera delay only 10–20% at the same lag — **LiDAR-camera fusion is far more temporal-sync-sensitive on the LiDAR side.**
- Deep-fusion systems (EPNet, JMODT, TWISE) are consistently more robust to blur/noise/partial camera loss than late/weak fusion — repair strategies (adding a LiDAR→fusion shortcut for CLOCs, an extra 2D-projected-point-cloud guidance branch for FConv) nearly fully recover performance under complete camera loss (Rb 0→0.94/0.99).

## Relevance to AMSCUP

Direct precedent for testing K-Radar-based fusion under **complete sensor loss** (this project's `loss_complete`/frame-deletion corruptions) and **partial signal loss** (`loss_partial`) — the MDANet non-monotonic-loss finding is a concrete reason to test intermediate severities, not just clean-vs-complete-loss endpoints. Also the direct methodological ancestor for the spatial/temporal misalignment testing this project has not yet implemented (see [[04_Design/Noise_Taxonomy]] open questions).

## Source

- `docs/lit_survey/noise_addition/markdown/BenchmarkingRobustness.md` (475 L)
