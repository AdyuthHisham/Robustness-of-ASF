# 4D mmWave Radar in Adverse Environments for Autonomous Driving: A Survey

#ReferPaper #corruption/radar/survey #important

Peng, Tang, Sun, Servadei, Wille (TU Munich / Infineon / China University of Geosciences). arXiv preprint, ~2025.

## Contribution

First survey focused specifically on 4D mmWave radar performance under adverse environments (rain, snow, fog, smoke, poor lighting) for autonomous driving. Catalogs ~20 public weather-inclusive 4D radar datasets and the methods applied to each adverse-condition category (general strategies; rain/snow-specific; fog/smoke-specific), then lists open challenges.

## Relevance to K-Radar / AMSCUP

**K-Radar is profiled directly in the survey's dataset table**: 35K frames of 4D radar tensors (Doppler×range×azimuth×elevation) + point clouds, calibrated with LiDAR/stereo cameras/IMU/RTK-GPS, covering fog/rain/snow/gloom(overcast)/night, ~120 m detection range — described as "the first large-scale 4D mmWave radar dataset specifically focused on adverse weather scenarios," noted as demonstrating radar's superior robustness vs. LiDAR in adverse weather but **lacking long-range point clouds**.

Comparator datasets worth citing against K-Radar: TJ4DRadSet (7.8K frames), aiMotive (26.5K, 200m range), Dual Radar (50K), MAN TruckScenes (30K, 230m), OmniHD-Scenes (450K frames — largest), WaterScenes (54K, broadest weather coverage: fog+rain+snow+gloom+night+glare+low-light).

## Corruption/simulation methods cited (directly relevant to this project's noise taxonomy)

- **Snow simulation on LiDAR** (Hähner et al., reused across multiple datasets): modeled as three operations — adding points, losing points, and information shift.
- **Fog simulation** (Hähner et al.): applied at multiple severity levels to LiDAR point clouds (used in VoD-Fog); 4D radar points left unmodified in that dataset — i.e., fog was treated as LiDAR-only in that prior work, a gap K-Radar's *real* fog sequences instead fill natively.
- **Smoke simulation**: crudely modeled by deleting LiDAR scans in certain sequences — much coarser than the fog/snow point-perturbation models.
- **CA-CFAR + sidelobe filtering** used as radar-side denoising for rain/snow/sleet/fog during point-cloud generation.
- Physical rationale given for why fog/smoke affect radar less than rain/snow: mmWave wavelength vs. fog/smoke particle size gives minimal Rayleigh scattering, whereas rain/snow cause genuine attenuation and backscatter (waterdrops absorb signal and create clutter).

## Open challenges the paper flags (useful for framing this project's gaps)

- Noise/sparsity handling remains unresolved — radar's inherent sparsity produces many empty voxels/pillars.
- Real-world adverse-condition collection is hard, pushing toward simulation, but **simulation methodology is inconsistent across the field** — no shared standard (a gap this project's own taxonomy work sits inside).
- Domain shift across weather/road types is "often overlooked" by existing methods.

## Source

- `docs/lit_survey/noise_addition/markdown/4DmmwaveSurvey.md` (255 L)
