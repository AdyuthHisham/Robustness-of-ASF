# Sensor Noise and Degradation Models

Literature-derived failure-mode taxonomy for camera, LiDAR, and radar, organized as physical degradation vs. communication/transmission failure, plus cross-cutting temporal and environmental factors. This is the theoretical basis for [[04_Design/Noise_Taxonomy|the noise taxonomy]] actually implemented in the pipeline — this note covers the broader literature survey; the design note covers what was selected and why.

## Camera

**Physical degradation:**
- **Thermal (dark current) noise** — signal-independent noise floor from heat, roughly doubling per 6–8°C rise; automotive cabin housings can exceed 60°C. Modeled as additive Gaussian/Poisson-Gaussian noise scaled by an Arrhenius temperature factor and exposure time, plus a fixed-pattern (DSNU) and temporal (read noise) component.
- **Photon shot noise / PRNU** — Poisson photon-arrival variation plus fixed per-pixel gain variation; dominant source in adequate lighting.
- **Row/column power-supply-coupled noise** — column-parallel CMOS readout converts supply ripple into structured row noise; sensor-model-specific (two production automotive sensors showed very different susceptibility to identical supply noise).
- **Lens/optical degradation** — a 30-factor automotive camera noise taxonomy singles out lens obstruction (dirt/dust/condensation/insects) and windshield distortion as "omnipresent and independent." **Key finding: combining multiple simultaneous noise factors produces accuracy loss that is not simply additive** — motivates testing combined, not only isolated, conditions.

**Communication/transmission:**
- Frame drops/delayed frames under bus congestion.
- Compression artifacts (H.264/H.265 blockiness, ringing, color bleeding).
- Pixel/row corruption — one study's injected fault ranges give concrete calibration targets: missing row/column pixels → 34–100% output deviation; pixel-shift faults → 0.3–10%; color-loss faults → 0.3–2.9%.

## LiDAR

**Physical degradation:**
- **Ranging noise** — Gaussian on point position, either isotropic (σ≈1.6mm x/y, ≈10mm z at close range) or decomposed into time-of-flight uncertainty + beam-divergence term (grows near-grazing incidence). Registration studies sweep σ up to values producing 3.3–6.5% recall drop at 30–40m for σ=0.05m.
- **Ray-drop / point dropout** — probabilistic per-beam drop, or structured "dead channel" dropout (entire vertical channel missing). Graph-based reconstruction of dropped beams achieves ~12cm RMSE on KITTI-derived dropout tests — indicates the scale of information loss.
- **Mirror contamination / laser aging** — slow monotonic drift (max range, point density) over service life, not frame-to-frame noise.
- **Weather-driven degradation** — controlled study ordering: light rain < weak fog < intense rain < thick fog for detection-performance drop. Under intense rain/thick fog, retroreflective targets retained ≥74% of clear-weather point count while aluminum/steel targets became undetectable at 20–30m. Rain = discrete scattering dropouts; fog = continuous-medium scattering with a sharp distance-dependent range ceiling — physically distinct mechanisms, not interchangeable in a simulator.

**Communication/transmission:** dropped frames/full outages (test both transient single-frame and sustained multi-second — fusion tolerates brief gaps via prediction but not sustained ones); bursty packet loss (Gilbert-Elliott/Fritchman Markov chain fits real automotive-network burst statistics better than independent per-packet loss); bit-flip/timestamp corruption; latency (LiDAR's 10–20Hz scan rate makes it comparatively latency-sensitive vs. 30+Hz camera).

## Radar

**Physical degradation:**
- **Antenna misalignment** — vibration/shock-driven mounting drift; small vertical tilt materially degrades detection given radio directionality. Slow, cumulative, vibration-exposure-tied.
- **RF component aging / I-Q mismatch** — a 24GHz CMOS receiver study found ~1.0–1.5dB / 10–24° uncorrected mismatch measurably degrades signal quality; passive down-converter chains can reach ~20dB noise figure, well above automotive tolerance.
- **Clutter / multipath ghost targets** — road-surface or flat-structure reflections create delayed spurious detections at wrong apparent ranges. CFAR thresholding (cell-averaging, ordered-statistics, clutter-map variants) is the standard mitigation, trading detection probability against clutter-edge sensitivity.
- **Transmitter power degradation** — gradually shrinks usable-range envelope.

**Communication/transmission:** full/partial sensor failure (stopped or stale-value reporting); detection dropout even while nominally online; Doppler/velocity noise under low SNR or multipath; track loss + re-acquisition delay (stresses fusion-layer track management more than raw noise does); data-rate reduction under bus congestion.

## Cross-cutting

**Temporal patterns** (for test-suite design):

| Pattern | Examples | Test-suite treatment |
|---|---|---|
| Sudden onset | sensor outage, dead LiDAR channel, radar fault, network burst | Step-function; measure fusion recovery time |
| Gradual/progressive | lens fogging, laser decay, antenna misalignment, RF aging | Slowly increasing severity over simulated mission duration |
| Intermittent/bursty | packet loss, detection dropout, track loss | Markov-chain (good/bad state) rather than independent per-frame probability |
| Environmental, reversible | rain/fog LiDAR loss, glare blooming, thermal noise | Tie to an underlying variable (precip rate, temp, visibility) that ramps up/down within a scenario |

**Cross-sensor correlation**: combining multiple simultaneous camera noise factors produces non-additive accuracy loss (same finding as the camera-specific note above, generalized), and heavy rain/fog degrades LiDAR and camera simultaneously while radar stays comparatively unaffected — motivates correlated multi-sensor degradation scenarios (e.g. "heavy rain: LiDAR point-count drop + camera blur + unaffected radar"), not only single-sensor fault injection.

**Reference corruption benchmarks used as calibration baselines** (see also [[02_Literature/Literature_Survey]]): MultiCorrupt (10 corruption types for LiDAR-camera fusion, open-source generation code); a 14-corruption-pattern multi-sensor-fusion robustness catalog; FADE (system-level, not just perception-level, fault-injection testing on the Baidu Apollo stack — tests planning/control deviation and recovery time, not just detection accuracy).

## Source

- `docs/sensor_noise_modeling_research.md` (169 L, canonical — full numbered reference list with DOIs/arXiv IDs for every claim above)
- `docs/vAIlt/05_Implementation/Sensor_Noise_Modeling_for_Object_Detection_Sensor_Fusion_Test_Suites.md` (earlier vault import of the same source — folded in here)
