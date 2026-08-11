# Seeing Through Fog Without Seeing Fog

#ReferPaper #corruption/fusion/weather #important

Bijelic, Gruber, Mannan, Kraus, Ritter, Dietmayer, Heide (Mercedes-Benz / Algolux / Ulm / Princeton). CVPR 2020.

## Contribution

(1) A real-world multimodal adverse-weather dataset — camera, LiDAR (×2), radar, gated NIR, FIR; >10,000 km driven across Germany/Sweden/Denmark/Finland; ~100K labels — deliberately capturing rare fog/snow/rain scenes rather than filtering them out (a direct contrast to KITTI, see [[KITTI_Vision_Benchmark_Suite]]). (2) An entropy-steered adaptive deep-fusion detector, trained **only on clear-weather data**, that generalizes to unseen real adverse weather at test time.

## The central experimental result

All degradation is **real**, not synthetic — driven in actual fog/snow/rain and in a controlled fog chamber (visibility set precisely to 30/40/50 m).

- **LiDAR-only detector AP drops 45.38% relative** between clear and dense-fog conditions (pulsed LiDAR restricted to <20–25m effective range in fog due to backscatter).
- Naive camera-LiDAR fusion baselines (AVOD-FPN, Concat SSD, Fusion SSD) **degrade below image-only performance in dense fog** — their implicit "learned redundancy" assumption breaks when one modality fails asymmetrically. AVOD-FPN's dense-fog AP (33.95) is far below plain image-only SSD's (87.89) at the same difficulty level.
- The proposed entropy-gated fusion (per-stream Shannon-entropy mask, computed on 16×16 pixel patches, gating cross-sensor feature concatenation) improves 9.69% AP over its own non-gated "Deep Fusion" ablation in dense fog, and the paper reports >8% AP improvement over prior fusion methods in hard scenarios *independent of weather condition*.
- Radar-only detection appears to improve slightly in adverse weather — the authors explicitly flag this as **likely a confound from simpler scenes** (fewer/farther vehicles visible in fog), not genuine radar robustness, a self-acknowledged artifact worth noting since it's the kind of spurious correlation this project's own weather-column analysis should guard against.

## Training-time robustness technique (methodologically relevant)

Random per-stream dropout (p=0.5, entropy set to zero) used as **training-time regularization**, not evaluation corruption — forces the fusion network not to over-rely on any single modality. Distinct from, but philosophically related to, this project's evaluation-time corruption/dropout testing.

## Relevance to AMSCUP

The closest real-data analog to K-Radar's own approach (both reject synthetic weather simulation in favor of real driven adverse-weather sequences) — a strong precedent for why K-Radar's own real fog/rain/sleet/snow sequences are more trustworthy ground truth than any of this survey's synthetic corruption models ([[LiRTest]], [[CommonCorruption_PointCloud_Benchmark]]) for validating *whether* a synthetic corruption model is realistic. The radar-improves-in-fog confound is a direct methodological warning for this project's own weather-stratified visibility analysis.

## Limitations acknowledged

Adverse weather is statistically rare even in fog-prone regions (dense fog with <50m visibility cited at up to only ~15 occurrences/year) — meaning even this large real-world dataset can't provide enough adverse-weather data for direct supervised training, which is why the paper trains only on clear data and relies on generalization rather than more data collection.

## Source

- `docs/lit_survey/noise_addition/markdown/SeeingThroughFog.md` (257 L)
