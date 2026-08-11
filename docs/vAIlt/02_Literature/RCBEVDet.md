# RCBEVDet: Radar-Camera Fusion in Bird's Eye View for 3D Object Detection

#ReferPaper #corruption/fusion/radar-camera

Lin, Liu, Xia, Wang, Wang, Qi, Dong, Dong, Zhang, Zhu (Peking University / UESTC / Changan Automobile).

## Contribution

Radar-camera BEV fusion detector: **RadarBEVNet** (dual-stream point+transformer radar backbone with an RCS-aware BEV encoder — scatters each point's feature over a radius proportional to its RCS value rather than a single pixel, using RCS as an object-size prior) + **CAMF** (deformable cross-attention fusion between radar and camera BEV features). SOTA radar-camera accuracy on nuScenes/VoD at 21–28 FPS.

## Robustness result (the part relevant to this project)

Follows CRN's sensor-dropout protocol: randomly drop 0/1/3/all camera views, or drop radar entirely, evaluate Car-class mAP.

| Config | Drop=0 | 1-view drop | 3-view drop | All-views drop |
|---|---|---|---|---|
| Camera-only (BEVDepth) | 49.4 | 41.1 | 24.2 | 0 |
| Radar-only (CenterPoint) | 30.6 | 25.3 | 14.9 | 0 |
| CRN (fusion) | 68.8 | 62.4/64.3 | 48.9/57.0 | 12.8/43.8 |
| **RCBEVDet (fusion)** | **72.5** | **66.9/71.6** | **53.5/66.1** | **16.5/62.1** |

Under **radar** failure specifically, CRN drops 4.5/11.8/25.0 points across the three severities while RCBEVDet drops only 0.9/6.4/10.4 — attributed to the cross-attention fusion producing more robust BEV features via dynamic alignment rather than fixed-weight concatenation.

## Relevance to AMSCUP

The camera-vs-radar failure asymmetry (camera-only crashes to 0 under full drop; radar-only likewise) mirrors K-Radar's own multi-sensor visibility premise — this is architecture-level evidence that *how* sensors are fused (not just which sensors are present) determines robustness to the exact single/multi-sensor-failure scenarios this project's `num_sensors_visible`/`primary_sensor` columns are designed to characterize (see [[04_Design/Output_Schema]]). Note this paper tests only **complete sensor dropout**, not graded noise/weather corruption — it doesn't overlap with the parameter-level corruption papers in this survey ([[CommonCorruption_PointCloud_Benchmark]], [[LiRTest]]).

## Source

- `docs/lit_survey/noise_addition/markdown/RCBEVDet.md` (326 L)
