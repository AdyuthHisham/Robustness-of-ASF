# Are We Ready for Autonomous Driving? The KITTI Vision Benchmark Suite

#ReferPaper #corruption/benchmark/foundational

Geiger, Lenz, Urtasun (Karlsruhe Institute of Technology / Toyota Technological Institute at Chicago). CVPR 2012.

## Contribution

The foundational real-world autonomous-driving benchmark: stereo matching, optical flow, visual odometry/SLAM, and 3D object detection/orientation, from a real driving platform (2 color + 2 grayscale cameras, Velodyne HDL-64E, OXTS RT3003 GPS/IMU). Central finding: methods that rank highly on lab benchmarks (Middlebury) perform substantially worse on this more realistic real-world data — establishing the "lab-to-real generalization gap" as a first-class benchmark-design concern, which every corruption-benchmark paper in this survey inherits as a premise.

## Why it matters to AMSCUP despite predating radar/weather robustness work entirely

KITTI is not about noise injection or weather at all — and that absence is itself the useful data point. The stereo/optical-flow benchmark subset was explicitly **curated to exclude bad-illumination scenes** ("as, e.g., tunnels") during the diversity-maximizing k-means sample selection. **Adverse conditions were filtered out, not targeted.** This is the direct historical contrast that motivates every adverse-weather dataset in this survey ([[KRadar_Dataset_Paper]], [[SeeingThroughFog]]) — K-Radar and Seeing-Through-Fog exist specifically to fill the gap KITTI's own curation choice created.

## Benchmark-design methodology reused across this project's downstream sources

- Diversity-maximizing sampling: k-means (k=400) on 144-dim descriptors for stereo/flow pairs; greedy entropy-maximizing sampling over orientation bins for 3D object detection — both are examples of "don't just collect more data, collect *diverse* data," a principle worth citing when justifying this project's own sequence/scenario selection for the K-Radar-based robust test set.
- Calibrated multi-sensor ground truth pipeline (automatic camera-camera, semi-automatic Velodyne-camera, automatic GPS/IMU-Velodyne via hand-eye calibration) — the direct methodological ancestor of K-Radar's own multi-stage calibration (see [[03_Theory/Coordinate_Frames]]).
- Introduced **Average Orientation Similarity (AOS)**, combining detection recall with cosine-based orientation similarity — a metric-design precedent worth considering if this project ever needs an orientation-aware (not just presence/absence) visibility or detection metric.

## Limitations acknowledged (relevant precedent for scoping honestly)

Ground-truth density for stereo/flow only ~50% (occlusion-limited); Velodyne-camera calibration only semi-automatic (manual correspondence selection required — "fully automatic techniques were not accurate enough" at the time); 3D detection evaluation restricted to non-occluded/weakly-occluded, non-truncated, ≥40px objects; explicitly scoped as an evolving benchmark ("gradually increase difficulty over time").

## Source

- `docs/lit_survey/noise_addition/markdown/Are_we_ready_for_autonomous_driving_The_KITTI_vision_benchmark_suite.md` (268 L)
