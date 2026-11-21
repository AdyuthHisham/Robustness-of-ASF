# 02 — Thesis pitch (spoken)

Numbers: pooled mAP, clean = 73.99 (`T/figure/metrics_table.png`). T = `/home/adhish/Productivity/AMSCUP/docs/Latex_Report/thesis_report/`. Say "pooled mAP" when you quote these (see audit D2).

## 30 seconds
"My thesis tests whether a camera–LiDAR–4D-radar fusion detector, ASF, is as robust as its authors claim. I did not train anything: I took the released checkpoint, injected synthetic faults into each sensor separately — Gaussian noise, partial loss, complete loss, frame deletion — and ran 21 conditions over 13 727 K-Radar frames on a SLURM cluster. The main result: LiDAR with Gaussian noise cuts pooled mAP by about 75 %, far worse than losing LiDAR entirely at about 40 %, and it happens through missed detections, not false alarms. So 'robust to sensor failure' held for a sensor that disappears, but not for one that keeps reporting wrong data."

## 2 minutes
1. **Problem (20 s).** Fusion benchmarks mostly report clean-weather accuracy, so reported performance overstates robustness. ASF explicitly claims to work 'under various weather and sensor degradation or failure', which makes it a testable claim (`T/include/Methods.tex:15-26`).
2. **What ASF's own evidence covers (15 s).** Natural weather; complete sensor loss; one narrow damage test — LiDAR forward-sector removal and a camera crack overlay. No Gaussian-noise LiDAR test. And availability is a flag someone must set before inference; the network does not detect a dead sensor itself (`Methods.tex:19-26`).
3. **Method (30 s).** Four corruption types × three modalities × three severities, applied inference-time between data loader and model. Noise σ = 0.1 / 1.0 / 2.0 m for LiDAR and radar. Metrics: AP at IoU 0.3, F1, mATE/mASE/mAOE, retention, churn, and a Composite Robustness Index. Run as SLURM array jobs on Chalmers Alvis A40s, one job per sequence; about a million prediction text files consolidated into one Parquet table (`Methods.tex:420-430,511,526`).
4. **Results (40 s).** Of the 21 corrupted conditions in the pooled table, 16 stay within −8.8 % of baseline (the thesis writes '17 of 22', which only works if the clean baseline is counted as the 22nd). Five collapse: LiDAR noise medium/high (−74.9 % / −76.4 %), LiDAR zeroed (−40.5 %), radar noise medium/high (−14.9 % / −22.7 %). Camera is essentially irrelevant: worst case −1.8 %. LiDAR failures are false negatives: FN +259.9 %, FP −82.8 %, and the largest FP increase anywhere is +3.6 % (`Conclusion.tex:14-16`, `Discussion.tex:33-37`).
5. **Caveat and implication (15 s).** I measured the asymmetry; I did not establish the cause. Two explanations fit — ungated corrupted branch, or backbone sensitivity to voxel-scale noise — and the experiment that separates them is not run (`Discussion.tex:106-107`).

## 5 minutes (add these blocks to the 2-minute version)
**Why K-Radar and why ASF (45 s).** K-Radar has structured per-sequence weather labels and a dense 4D radar tensor, not a sparse CFAR point list; nuScenes and Waymo don't annotate weather as a field. ASF comes from the same group as K-Radar and claims graceful degradation, so the claim is checkable (`Methods.tex:7-15`).

**How ASF works (60 s).** Three frozen pretrained encoders (BEVDepth camera, SECOND LiDAR, RTNH radar) produce BEV maps. UCP projects each patch to a common vector; CASAP does single-query cross-attention across sensors at each patch position, so cost is O(N_q·N_s) rather than O(N_q·N_s·N_p); PN renormalises. Training uses Sensor Combination Loss over all 7 non-empty sensor subsets. Missing sensor = key absent from attention; output shape unchanged (`T/include/ASF.tex:57-103`).

**Dataset and reliability (30 s).** Weather, environment, time, distance and point-density strata; N>30 object floor; flag strata from <10 sequences as sequence-confounded. Some 'easy' weather scores (fog, light snow) rest on 2–7 sequences, so I don't read them as easier (`Methods.tex:446`, `Results.tex:124`).

**Metrics subtlety (30 s).** mATE/mASE/mAOE only cover matched true positives. At LiDAR noise high the TP population shrinks 79.3 %, so mASE/mAOE look better — survivorship bias, not a gain (`Discussion.tex:23`).

**Noise vs absence (45 s).** Same mechanism-agnostic question: is a present-but-wrong sensor worse than an absent one? For LiDAR yes: −75 % vs −40 %. Relative to ASF's own clean branch-exclusion ablation, my zero-fill costs 6–13 points more for LiDAR (−41.4 % vs −28.8 % sedan; −43.1 % vs −36.5 % bus) — evidence that declaring absence helps (`Discussion.tex:76-95`). This is the 'silent failure' point: nothing in the pipeline flags a corrupted-but-present LiDAR.

**Limits and what next (45 s).** One checkpoint, one dataset, seed 42, synthetic faults, σ up to 2 m (bigger than the car), no joint corruption; baseline 2–5 AP points below the paper, cause unresolved; Alvis access ended so no more runs. Next: LiDAR-only detector under same noise (discriminating experiment); content-derived per-branch reliability (voxel occupancy, SNR) feeding the availability gate (`Discussion.tex:103-118,130-146`).

## 'So what' for an industry audience
- **Validation claim hygiene**: "robust to sensor failure" is under-specified. Test (a) sensor absent-and-known, (b) sensor absent-and-unknown, (c) sensor present-but-wrong. Only (a) is what availability flags cover.
- **Silent degradation is the risk**: no health signal fired in the corrupted-LiDAR case. Production stacks need an input-side sensor-health monitor, independent of the fusion network, and a fallback path.
- **Cheap, reusable method**: inference-time fault injection on a released checkpoint, per-sensor, with retention and FN/FP decomposition. No retraining, so it fits audit/acceptance testing of third-party models. That is directly consulting-shaped work.
- **Don't over-sell**: synthetic noise is not a sensor model; the number to take away is the *asymmetry and its mechanism class (misses, not hallucinations)*, not '−75 %'.
- **Transfer to other domains** (say only as analogy, no claims): redundant-sensor monitoring in telecom/energy (fault models: absent, stale, noisy) — your thesis does not cover these domains.
