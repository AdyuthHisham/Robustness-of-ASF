# Generating Realistic and Diverse Tests for LiDAR-Based Perception Systems

#ReferPaper #corruption/lidar/mutationtesting

Christian, Woodlief (University of Virginia). ~2023. Code: `github.com/less-lab-uva/semLidarFuzz`.

## Contribution

Semantic **entity-level mutation testing** for LiDAR semantic segmentation, starting from real labeled point clouds (SemanticKITTI) rather than synthetic corruption. Eight mutation operations (Add, Remove, Rotate, Mirror, Adjust Intensity, Deform, Adjust Scale, Class-Preserving Swap) composed into 7 test-generating compositions, each gated by parameterized "realism invariants" that abort a mutation if it would produce an unrealistic scene (e.g., floating object, overlap with existing entity).

## Explicitly positions itself against noise-injection approaches

The paper's related-work critique is directly relevant to this project's own design choices: it argues that **weather-simulation noise injection is realistic but low-diversity** (doesn't change the semantic label, so can't surface classification failures) while **generic data-augmentation noise is diversity-increasing but not realism-verified**. Its own entity-level approach targets a third axis — compositional/semantic mutation — deliberately positioned as *orthogonal to*, not a replacement for, sensor-noise corruption.

## Methodology and oracle design (reusable idea for this project)

- 5 SemanticKITTI-leaderboard models tested: Cylinder3D, SPVNAS, JS3C-Net, SalsaNext, SqueezeSegV3.
- **Relative-success oracle**: corrects for cases where the mutation itself changes ground-truth class composition (rather than comparing raw accuracy naively).
- **Jaccard Index (class-averaged IoU)** used alongside plain Accuracy — found far more sensitive to small/rare-class failures. Example: an Add-Rotate mutation (inserting a bicyclist) caused only a 0.03% Accuracy drop in Cylinder3D but a 7.6% Jaccard drop, because the model split "bicyclist" into separate "bicycle" + "person" detections — a safety-relevant class-splitting error invisible to whole-scene accuracy.
- False-positive control via **voting across the diverse SUT set** (a test flagged as unrealistic/invalid if ≥3 of 5 models fail on it) — avoids needing human judgment on LiDAR point clouds, which the authors note is largely infeasible at scale.

## Key finding

At the highest severity, JS3C-Net was the most brittle of the 5 models (e.g., 21.9% Accuracy drop under a Vehicle Scale mutation with error cascading into an unrelated fence/building region) — despite being competitively ranked on the standard SemanticKITTI leaderboard, underscoring that leaderboard rank doesn't predict mutation robustness.

## Relevance to AMSCUP

Not a source for any of this project's implemented corruptions (it explicitly avoids weather/noise injection), but its **Jaccard-over-Accuracy** argument is directly applicable if this project ever needs a rare-class-sensitive metric for evaluating corrupted-vs-clean K-Radar inference — plain mAP/accuracy could mask exactly the kind of small-object failure this paper flags as most safety-relevant.

## Source

- `docs/lit_survey/noise_addition/markdown/Generating_Realistic_and_Diverse_Tests_for_LiDAR-Based_Perception_Systems.md` (379 L)
