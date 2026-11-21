# 02 — Thesis pitch (spoken)

Numbers marked † are from `metrics_table.png` / my arithmetic (see 01 §0). Say them only if you can state the definition: *pooled-object mAP at IoU 0.3, loss relative to the clean baseline of 73.99*.

---

## 30 seconds

"My thesis tests a claim. ASF is a camera–LiDAR–4D-radar 3D detector that says it keeps working when sensors degrade or fail. I took the released checkpoint, trained nothing, and corrupted each sensor independently on the K-Radar test set — noise, partial loss, complete loss — then measured the damage. The headline: for LiDAR and radar, a sensor that is *noisy but present* hurts far more than one that is *completely gone*. LiDAR noise cost about 75% of mAP†; zeroing LiDAR cost about 40%†. Camera barely mattered. And the damage was missed detections, not false alarms."

## 2 minutes

"Fusion benchmarks are mostly clear-weather, daytime, uncrowded, so reported accuracy says little about what happens when a sensor degrades. ASF — from the group that built K-Radar — is designed for exactly that: it projects each sensor's bird's-eye-view features into a shared space and fuses them with a light cross-attention, and it's trained on every sensor subset so one network handles missing sensors.

Reading the paper closely, the evidence is narrower than the claim. Weather robustness is natural weather. The 'damaged sensor' tests are one LiDAR sector removal and one camera crack overlay. And availability is a flag you set before inference — the network doesn't detect a sensor going offline.

So I built an inference-time corruption pipeline: Gaussian noise, partial loss, complete loss, frame deletion, each applied to one modality at low, medium, high severity, run on 58 sequences — 13,727 frames, 35,456 objects — on Chalmers' Alvis cluster as one SLURM job per sequence. Metrics: AP and F1, translation/size/orientation error, retention against the clean baseline, a composite robustness index, and per-object churn.

Findings: of 21 corrupted conditions, 5 collapsed — LiDAR noise medium and high, LiDAR zeroed, radar noise medium and high — and 16 stayed within 9% of baseline. LiDAR noise cost 75–76%†; zeroed LiDAR 40%†. Radar noise cost 15% and 23%†; zeroed radar 6%†. Camera was within 2% everywhere†. False negatives rose up to 260%; the largest false-positive increase anywhere was 3.6%. So it's suppression, not hallucination. Frame deletion crashed the pipeline for all three sensors.

What I can't claim: why. The availability flag was never set in my runs, which is consistent with the asymmetry, but a backbone sensitivity to voxel-scale noise explains it equally well, and the discriminating experiment — a LiDAR-only detector under the same noise — wasn't run before I lost cluster access."

## 5 minutes

**Problem (45 s).** "Perception models are validated on benchmarks that under-represent bad conditions. That's a reality gap. A fusion model doubly so: three sensors fail in different ways, and a summary mAP hides which failure breaks it. I wanted a method that answers three things: how robust is the model, where does it fail, which sensor does it lean on."

**The model under test (45 s).** "ASF uses frozen per-sensor encoders — BEVDepth for camera, SECOND for LiDAR, RTNH for radar. Their BEV maps are cut into patches, mapped by a learned projection to a common channel size, and fused per patch by a single cross-attention whose query is shared and whose key/value set is just the sensors present at that patch — so cost scales with the number of sensors, not patches. It's trained on all seven non-empty sensor subsets. The key detail for my study: excluding a sensor happens only if its key is absent from a dictionary supplied before inference. Nothing in the network notices a sensor going bad."

**The method (60 s).** "Four corruptions, per modality, applied after data loading and before the encoders — the model is untouched. Noise σ of 0.1, 1.0, 2.0 metres on LiDAR and radar points; for scale, 1 m is about half a car's width. Partial loss drops 10, 30, 70% of points. Complete loss zero-fills. Frame deletion removes every 19th, 5th, 2nd frame. Seed fixed, deterministic. Metrics at IoU 0.3, K-Radar's convention. Retention is condition metric over clean metric. CRI is retention divided by a penalty on severity variance. Churn classifies every object as stable, newly missed, newly recovered, or missed in both. Everything is stratified by weather, environment, time of day, distance, density — with a minimum of 30 objects per cell and a flag when a stratum comes from under ten sequences."

**Results (75 s).** "Five conditions collapsed. LiDAR noise: mAP 74 → 18.5 at medium, 17.5 at high, with false negatives 8.3 thousand → 29.8 thousand and false positives down 83%. Zeroed LiDAR: 44, so the same sensor is *twice as harmful noisy as absent*. Radar mirrors it more mildly. Camera is flat — consistent with the paper's own ablation, where dropping camera by clean branch exclusion costs only 0.8% (sedan) and 1.0% (bus/truck) of BEV AP. CRI ranks LiDAR noise worst at 0.11 to 0.15, radar noise 0.27, camera 0.84 to 0.94. Mechanically, mATE, mASE, mAOE look better in the collapsed conditions — that's survivorship, they're computed only over the matched true positives. Across 21 conditions, FN rose in nearly all and FP rose in only four."

**Limits and honesty (45 s).** "One checkpoint, one dataset, synthetic faults, one noise draw per condition, no confidence intervals. The 3–5 point gap to the paper's baseline is unresolved. Equal σ on LiDAR and radar is not equal severity — LiDAR is centimetre-accurate, radar's range cell is 0.46 m. And I don't know why noise beats zeroing in harm: two explanations fit, I could test neither."

**Close (30 s).** "The takeaway is methodological: report robustness per failure mode, not per sensor, because 'works when the sensor is declared absent' says little about 'works when the sensor is lying'."

---

## "So what" for an industry audience

1. **Validate on failure *modes*, not failure *events*.** A system that handles a known-absent sensor can still collapse on a degraded-but-present one. Safety cases (the thesis cites Sun et al. 2024 on perception safety standardisation) need characterisation across degraded conditions.
2. **Silent failure is the expensive failure.** Nothing flagged the LiDAR collapse. A deployed stack needs a data-derived health signal per sensor (voxel occupancy, point count, SNR) *before* fusion. This is a proposed direction in the thesis, **not tested**.
3. **Cheap, reusable method.** Inference-time injection requires no retraining and no model changes; one SLURM array job per sequence; results in one Parquet table. Transferable to any perception model with a loader and a prediction format.
4. **Aggregate metrics hide the story.** Pooled mAP, FN-vs-FP split, and per-object churn together tell you *what* broke and *how*; single-number robustness scores (CRI) are useful for ranking but need their assumptions stated.
5. **Camera's flatness is not camera robustness.** The fused output barely depends on camera, so camera corruption is invisible. Dependency analysis ≠ sensor quality analysis.
6. **Consulting framing:** it's a risk-assessment exercise — take a vendor's claim, find where the evidence stops, design the cheapest experiment that probes beyond it, report effect sizes with caveats.
