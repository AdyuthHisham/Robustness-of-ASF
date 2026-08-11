# TMVA4D — 4D Radar Semantic Segmentation of People in Field Conditions

#ReferPaper #corruption/radar/realworld

Skog, Kotlyar, Kubelka, Magnusson (Örebro University AASS). Preprint, ~2025.

## Contribution

TMVA4D: CNN/ConvLSTM + ASPP architecture family for semantic segmentation of people from 4D imaging radar, using five 2D heatmap projections (elevation-azimuth, elevation-Doppler, elevation-range, range-azimuth, Doppler-azimuth — the elevation views are the novel addition vs. prior multi-view radar segmentation work). Also contributes a multimodal radar+thermal dataset collected in field-robotics conditions (mine, car wash, construction tent, forest) with **real, physically induced** dust, water spray, and smoke — not synthetic corruption.

## Method (brief)

Sensrad Hugin A3 4D solid-state radar (42 m range) + FLIR AX5 thermal camera; YOLOv8x-seg trained on 4.8% manually annotated frames used as an auto-annotator to label the remaining ~95% for training. Best model (TMVA4D-IntConvLSTM 'Medium', soft-Dice loss): **Dice 75.9%, IoU 61.2%** for the person class. ASPP removal collapses performance (Dice 73.2%→37.1%) — the single largest ablation effect in the paper.

## Directly relevant finding: radar robustness under real degraded visibility

Table IV compares "Clear" vs. "Dust" conditions within the same environment: Dice 73.2%→71.3%, IoU 57.8%→55.4% — a small drop, supporting the paper's conclusion that **airborne particulate has little impact on radar-based person detection**. This is an empirical, real-world (not simulated) data point for the "radar is weather-robust" claim this project's own [[03_Theory/Sensor_Noise_and_Degradation_Models|noise model note]] makes on theoretical grounds.

**Caveat for citing this finding**: the degradation here is dust/smoke/water-spray in industrial/field settings, not the rain/fog/snow that dominates K-Radar and the rest of this literature set — different physical mechanism (particulate scattering vs. precipitation attenuation), so the robustness magnitude shouldn't be assumed to transfer directly to K-Radar's weather categories.

## Method limitation worth noting for this project

No systematic severity parameterization — conditions are categorical (clear/dust, mine/surface) from real physical setup, not a swept synthetic parameter. Contrast with this project's own approach ([[04_Design/Noise_Taxonomy]]), which does define explicit severity levels (low/medium/high) for its corruption effects — a design choice this paper doesn't need to make because its degradation is real rather than injected.

## Source

- `docs/lit_survey/noise_addition/markdown/4dradarsemanticsegmentation.md` (326 L)
