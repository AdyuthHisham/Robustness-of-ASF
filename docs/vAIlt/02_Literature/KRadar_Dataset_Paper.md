# K-Radar: 4D Radar Object Detection for Autonomous Driving in Various Weather Conditions

#ReferPaper #corruption/radar/dataset #important

Paek, Wijaya, Kong (KAIST). The dataset paper this entire project is built on.

## Contribution

First large-scale 4D Radar Tensor (4DRT)-based 3D object detection dataset — **35K frames, 93.3K 3D bbox labels**, 58 sequences (1–20 Daejeon urban, 21–58 Gangwon-do, Korea's highest-snowfall province), across fog/rain/sleet/light-snow/heavy-snow/overcast/normal, paired with LiDAR (OS2-64 + OS1-128), 4×stereo camera (ZED2i, 360° coverage), RTK-GPS. Two baseline networks (RTNH with height info, RTN without) demonstrate that (1) height information in the 4DRT is critical and (2) 4D-radar detection is far more weather-robust than LiDAR detection.

## The central empirical result this whole project rests on

RTNH (radar) vs. PointPillars (LiDAR), AP_3D across weather:
- **Normal**: PointPillars 52.3%, RTNH 49.9% — comparable.
- **Sleet**: PointPillars drops to 22.7% (**−29.6pp**); RTNH holds at 41.5% (actually *higher* than its own normal-weather AP_BEV).
- **Heavy snow**: PointPillars drops to 29.7% (**−22.6pp**); RTNH holds at 44.5%.

Mechanistically: sleet freezes onto the LiDAR housing forming a frost layer that blocks the beam entirely; heavy snow (>1cm/hr) physically accumulates on LiDAR/camera surfaces within ~5 minutes of driving, largely blinding both; radar (λ≈4mm, 77–81GHz) passes through precipitation largely unaffected. This is the physical justification behind [[03_Theory/Sensor_Noise_and_Degradation_Models]]'s claim that radar is comparatively weather-robust, now grounded in a controlled same-scene, same-object A/B comparison rather than separate studies on different data.

## Sensor suite (canonical reference — cross-check against [[03_Theory/Visibility_Formulas]] constants)

| Sensor | Spec |
|---|---|
| 4D Radar (RETINA-4ST) | 64×256 tensor, 107° az × 37° el FOV, 118 m range, 0.46 m range res, 1° angular res, 10 FPS, front-grill mounted |
| LiDAR OS2-64 | 131,072 pts/frame, 360°×22.5° FOV, 240 m range, 10 FPS |
| LiDAR OS1-128 | 262,144 pts/frame, 360°×45° FOV, 120 m range, 10 FPS |
| 4× stereo camera (ZED2i) | 1280×720 per half, 110°×70° FOV, 30 FPS, front/rear/left/right |
| RTK-GPS | 0.025m+1ppm CEP, 1 FPS |

Weather operational definitions (Appendix C): light snow = ≤~1cm/hr; heavy snow = >1cm/hr; fog = distant objects dimly visible through omni-directional fog; day ≈6:00–16:00, night ≈20:00–4:00. These are the exact category boundaries K-Radar's `description.txt` weather field encodes — the ground truth [[04_Design/Output_Schema]]'s `weather` column is built from.

## Coordinate frame / calibration

Confirms [[03_Theory/Coordinate_Frames]]: labels annotated in LiDAR frame (since the raw 4DRT power map is "unintuitive to human" annotators), transformed to radar frame via calibration; pitch difference assumed zero (sensors mounted perpendicular to ground); calibration error ≤0.5cm.

## Explicit limitations the paper states (worth carrying into this project's own Limitations section)

- **4DRT is forward-only, 107° azimuth** (not 360° like LiDAR/camera) — a deliberate scope cut, since dense 360° 4D tensor storage would push the already-large ~12TB dataset far higher.
- Authors explicitly warn K-Radar should **not** be expected to transfer well as pretraining for other radar-tensor datasets (e.g., RADIATE) — different hardware → different power-measurement distributions, different range resolution (K-Radar 0.46m vs. RADIATE 0.175m), and geographic/driving-side distribution shift (Korea right-hand traffic).
- Authors explicitly do **not** claim RTNH is architecturally superior to PointPillars — the radar-vs-LiDAR comparison is meant only to demonstrate sensor robustness, not network design quality. This project's own visibility-scoring work should be careful about the same distinction: a low LiDAR visibility score reflects sensor physics under weather, not detector quality.

## Source

- `docs/lit_survey/noise_addition/markdown/kradar.md` (536 L)
- K-Radar paper (arXiv:2206.08171) — also the primary source for [[03_Theory/Coordinate_Frames]]
