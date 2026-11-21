# 01 — Claim audit (CV vs thesis)

Read-only audit. Nothing in the CV or thesis was modified. Reviewed: `Adyuth_Hisham_CV_Master.tex`, every live `.tex` under `docs/Latex_Report/thesis_report/` (Abstract, Introduction, Theory, ASF, Methods, Results, Discussion, Conclusion, Nomenclature, GenAIDeclaration, Titlepage, Acknowledgements), `references.bib` entries used for the headline claims, and `figure/metrics_table.png` (the only place the per-condition pooled numbers exist in full).

**Source key.** `Abs`=frontmatter/Abstract.tex, `Intro`, `Theory`, `ASF`, `Meth`=Methods.tex, `Res`=Results.tex, `Disc`=Discussion.tex, `Concl`=Conclusion.tex, `Fig:metrics`=figure/metrics_table.png, `CV`=CV master .tex. Numbers after a colon are line numbers in that file. `Concl` line numbers are approximate (RQ1/RQ2/RQ3 ≈ L14/L16/L18); the Conclusion has no line-numbered sections beyond that, so I cite section names.

**Important:** large parts of Discussion.tex (from ~L148) and Conclusion.tex are commented out with `%`. I treat only uncommented text as "in the thesis". Where a claim's support exists only in commented text, I say so.

---

## 0. Numbers I derived (not stated in the thesis text)

`Fig:metrics` gives pooled mAP per condition; baseline (`original`) = **73.99**, TP = 27,169, FN = 8,287, FP = 4,900 (TP+FN = 35,456 = total GT objects, matches `Res:15`). Retention column Rb and my arithmetic:

| Condition family | Rb values (low/med/high or single) | Pooled mAP loss vs 73.99 |
|---|---|---|
| LiDAR gaussian noise | 0.941 / 0.251 / 0.236 | −5.9% / **−74.9%** / **−76.4%** |
| LiDAR loss_partial | 1.010 / 1.017 / 0.959 | +1.0% / +1.7% / −4.1% |
| LiDAR loss_complete_zero | 0.595 | **−40.5%** |
| Radar gaussian noise | 1.003 / 0.851 / 0.773 | +0.3% / **−14.9%** / **−22.7%** |
| Radar loss_partial | 1.001 / 0.989 / 0.912 | +0.1% / −1.1% / −8.8% |
| Radar loss_complete_zero | 0.937 | **−6.3%** |
| Camera gaussian noise | 0.990 / 0.985 / 0.982 | −1.0% / −1.5% / −1.8% |
| Camera loss_partial | 0.991 / 0.986 / 0.986 | −0.9% / −1.4% / −1.4% |
| Camera loss_complete_zero | 0.982 | −1.8% |

Mean Rb over the seven evaluable conditions per sensor: **LiDAR 0.716 → 28.4% loss; radar 0.924 → 7.6%; camera 0.986 → 1.4%**. These reproduce the CV's "28% / 8% / 1%" — but see claim C7: **the thesis text never states these three averages.**

FN/FP checks (all reproduce): LiDAR noise high FN 29,829 vs 8,287 = **+259.9%** (`Disc:33`); FP 842 vs 4,900 = **−82.8%**; max FP increase 5,078 vs 4,900 = **+3.63%** at camera_loss_partial_high (`Disc:35`). F1 baseline recomputed from TP/FP/FN: precision 0.847, recall 0.766, F1 0.805 = matches table.

Mean-of-class BEV AP (sedan 77.86, bus/truck 67.93 → 72.90) is a *different aggregation* from pooled 73.99. See D1.

---

## A. CV claims

| ID | CV claim (CV line) | Thesis evidence (source) | Status |
|---|---|---|---|
| C1 | "finishing an M.Sc. … (Sep 2026)" (CV:16, CV:80) | GenAI declaration dated "Gothenburg, September 2026"; Titlepage lists supervisors Amin Assadi, Jordanka Kovaceva, examiner Jonas Bärgman (Titlepage:125-127) | Supported. Today is Oct 2026: be able to state precisely whether you have graduated / thesis approved. |
| C2 | Thesis "evaluates multi-modal 3D object detection robustness using large-scale HPC experimentation" (CV:16) | Alvis, A40 GPUs, SLURM array jobs one per sequence (`Meth:511`); "on the order of a million text files" (`Meth:526`) | Supported qualitatively. **No job count, GPU-hours, or wall-clock in thesis** — you cannot quantify "large-scale" from the document. |
| C3 | "Engineered a framework for stress-testing multi-modal 3D detectors, corrupting camera, LiDAR and radar inputs independently…" (CV:40) | Independent per-modality corruption (`Meth:420`); `NoiseInjector` wraps sensor dict after loading (`Meth:523`); no ASF code change | Supported, but "framework" is generous: tested on **one** model, one checkpoint, one dataset (`Disc:103`). Thesis never calls it a framework. Authorship of the injector/eval wrapper is not stated in the thesis (commented text names `datasets/effects/eval_wrapper.py`, `compute_robustness.py`, `configs/noise/single/*.yml`) — be ready to say exactly which parts you wrote vs reused from K-Radar/AMSCUP_PLUS. |
| C4 | Metrics "AP, F1 … position, size, orientation … retention, composite robustness index" (CV:40) | AP `Meth:448`, F1 `Meth:454`, mATE/mASE/mAOE `Meth:460`, retention `Meth:484`, CRI `Meth:490` | Supported. (Churn is also in the thesis; not on CV.) |
| C5 | "run … on an HPC cluster with SLURM and Apptainer" (CV:40, CV:105) | SLURM: `Meth:511`. **Apptainer: not mentioned anywhere in the thesis.** Docker also listed in CV:105, not in thesis. Polars/PyTorch (CV:43, CV:106) also absent from thesis text (Parquet is mentioned `Meth:526`). | SLURM supported. **Apptainer/Docker/Polars/PyTorch: NOT IN THESIS.** Fine if true, but be able to answer from your own experience; the document will not back you up. |
| C6 | ASF is "a camera/LiDAR/radar 3D detector, on the K-Radar dataset" (CV:41) | `Abs:12`, `ASF:7` | Supported. |
| C7 | "At medium and high noise, a noisy sensor hurt more than a zeroed one, for both LiDAR and radar" (CV:41) | LiDAR −74.9/−76.4 vs −40.5 (`Concl RQ2`; `Fig:metrics`). Radar −14.9/−22.7 (`Concl RQ2`) vs zeroed −6.3 (`Fig:metrics` Rb 0.937 only; per-class BEV −6.67/−10.36 `Disc:86`) | Supported. The "6.3%" appears nowhere in text; it comes from the figure (1−0.937). |
| C8 | "radar pooled mAP fell 14.9% to 22.7% under noise versus 6.3% zeroed" (CV:41) | As above | Supported, but "14.9% to 22.7%" is **medium → high**, not a range over all noise levels (low is +0.3%). Say "14.9% at medium, 22.7% at high". |
| C9 | "LiDAR … losing 28% of mAP on average across seven conditions, versus 8% radar and 1% camera" (CV:41) | **Not in thesis text.** Derived by me from `Fig:metrics` Rb: 28.4 / 7.6 / 1.4 | **Reproducible but unsourced aggregate.** Seven = 3 noise + 3 partial + 1 complete (frame deletion excluded). It is an unweighted mean over heterogeneous conditions, includes partial-loss values >1 (apparent improvements), and mixes severities. Defensible only if you can state exactly this definition. Camera 1.4% → "1%" is fine; do not claim ordering among camera conditions (differences are ≤0.9 pt, single noise draw). |
| C10 | "LiDAR's losses came from missed detections (false negatives up to +260%)" (CV:41) | `Disc:33,35`: +259.9% | Supported. |
| C11 | "false positives rose at most 3.6% in any condition" (CV:41) | `Disc:35`: +3.63% at **camera**_loss_partial_high | Supported, **but sentence placement implies LiDAR**. LiDAR FP actually *fell* 82.8% at noise high. The 3.6% max is a camera condition. Phrase: "across all 21 conditions, the largest FP increase was 3.6%, and it was on camera". |
| C12 | Skills: "LiDAR-based road-feature extraction … SLAM-adjacent techniques … Docker" (CV:102-105) | Not thesis topics | "SLAM-adjacent" is vague; expect "what exactly?". |

## B. CV items with no thesis counterpart (project/role claims)

| ID | Claim | Issue |
|---|---|---|
| P1 | Sysenso/Siemens LiDAR annotation tool (CV:22-23) | No numbers on the CV (accuracy, recall of zebra/lane detection, speed-up, frame counts). **Missing information — see 04.** |
| P2 | Myo+Quest 3 pipeline (CV:29-30) | Honest scoping ("orientation and gesture fidelity scoped as next-stage"). No latency/sample-rate numbers on CV. |
| P3 | ROS2 pipelines (CV:48-52) | Dated Jul 2023–Jul 2024 and located "Gothenburg, Sweden" — but CV:20 puts you at Sysenso, **Chennai**, Jul 2023–Jul 2024, and Chalmers starts Sep 2024 (CV:80). Location/date inconsistency an interviewer can see. |
| P4 | FIDO EKF "sub-meter positional accuracy in live tests" (CV:58) | Number not in any document I was given; how it was measured (ground truth? RTK reference? CEP/RMSE?) is the first question. "Stable under GPS multipath" is a claim, not a measurement. |
| P5 | Smartphone IMU EKF "6-DOF orientation" (CV:65) | Accelerometer+gyro give **3-DOF orientation** (roll/pitch observable via gravity; yaw unobservable without a magnetometer). "6-DOF" is a terminology trap (6 sensor axes ≠ 6-DOF pose). Also "benchmarked against Google's proprietary algorithm" — you need the metric and result. |
| P6 | Crazyflie "establishing a simulation-to-hardware deployment framework" (CV:73) | "Establishing" overstates if nothing was flown. Say exactly what was simulated vs on hardware. |
| P7 | CV header `\cvroletitle{[ROLE TITLE]}` (CV:7) | Unfilled placeholder in the master. Make sure it never reaches a submitted PDF. |
| P8 | Languages: English "Intermediate", Swedish "Beginner" (CV:110) | Consultancy places people on-site at clients; English-Intermediate on a CV for someone who completed an English-taught MSc invites doubt; Swedish-Beginner is a real placement constraint. Decide your honest line (see 06). |
| P9 | Hackathon "LUNAR FINTECH Challenge" first prize (CV:86-88) | Only finance-adjacent evidence you have; no further detail on CV. |

---

## C. Headline thesis numbers (for the Q&A — verified where I could)

| ID | Number | Source | Check |
|---|---|---|---|
| T1 | 58 sequences / 13,727 frames / 35,456 GT objects (sedan 29,613, bus/truck 5,843) | `Meth:87`, `Res:15`, `Res:60-84` | Object counts sum correctly across weather and ToD axes. |
| T2 | Baseline BEV AP sedan 77.86 / bus-truck 67.93; 3D AP 74.99 / 58.15 vs paper 82.5/70.2 (BEV), 79.3/60.4 (3D) | `Res:30-31` | Gaps: sedan −4.64/−4.31 pts; bus −2.27/−2.25 pts. See D10. |
| T3 | Pooled baseline mAP 73.99, F1 0.805, FP 4,900, FN 8,287; TP 27,169 | `Fig:metrics`, `Disc:23` | Self-consistent. |
| T4 | LiDAR noise med/high pooled mAP 18.54 / 17.45 (Rb 0.251/0.236); FN 29,214/29,829; FP 1,175/842; F1 0.291/0.268; churn 0.594/0.609; net retention 0.230/0.207 | `Fig:metrics` | Churn/net-retention appear only in the figure and commented text. |
| T5 | LiDAR complete zero: mAP 44.05, Rb 0.595, FN 19,215 (+131.9%), F1 0.586 | `Fig:metrics`, `Disc:35` | |
| T6 | Radar noise med/high: mAP 62.94/57.18, FN +51.0%/+77.4% | `Fig:metrics`, `Disc:35` | |
| T7 | Max non-collapse loss −8.80% (radar_loss_partial_high 67.48) | `Concl RQ1`, `Fig:metrics` | Concl says "17 of 22 graded conditions"; figure supports **16 of 21 corrupted** (+baseline = 17 of 22). See D3. |
| T8 | CRI sedan/bus: cam_partial 0.936/0.929; cam_noise 0.915/0.842; lidar_partial 0.546/0.383; radar_partial 0.399/0.348; radar_noise 0.272/0.272; lidar_noise 0.106/0.153 | `Res:451-456` | My pooled recompute (AP in 0–100 points): lidar noise 0.112, radar noise 0.284, radar partial 0.405 — consistent. Camera noise pooled 0.811 vs reported 0.915/0.842 — I cannot reproduce from pooled values; per-class AP per tier not in the document. |
| T9 | Per-axis worst cells (`Res:420-429`): e.g. sedan weather 0.143 LiDAR noise high (normal); sedan parking-lots 0.003 | `Res:412-432` | Many cells on tiny N/few sequences; flagged by the thesis itself. |
| T10 | Noise σ 0.1/1.0/2.0 m (radar+LiDAR), 20/50/80 (camera, 0–255); partial 0.1/0.3/0.7; frame deletion every 19/5/2; p=1.0; seed 42 | `Meth:422-430` | σ relative to sedan width 2.1 m: 4.8%/47.6%/95%. ("exceeds the vehicle's width outright" at 2.0 m is a slight overstatement: 2.0 < 2.1.) Camera 2σ: 40/100/160 = 15.7%/39.2%/62.7% — matches. |
| T11 | AP: 41-point interpolated, IoU 0.3; precision envelope max over r̃≥r | `Meth:448-450` | Note: formula as written averages 41 points over r∈{0,0.025,…,1} = 41 values ✓. |
| T12 | ASF: UCP→CASAP→PN, SCL over 2³−1=7 subsets, CASAP cost O(N_q N_s) vs SCF O(N_q N_s N_p); encoders BEVDepth/SECOND/RTNH frozen; camera trained only on normal/overcast (seq 1–20) | `ASF:7-24,57-66,98,110`, `Disc:65` | |
| T13 | Compute: 4×A40 (48 GB)/node, 85 nodes cluster-wide; one SLURM job per sequence | `Meth:511` | |

---

## D. Discrepancies, overstatements, ambiguities (report only — nothing fixed)

**D1 — Two different "pooled" conventions are mixed.**
Conclusion/CV use *pooled-object mAP* from `Fig:metrics` (LiDAR noise high **−76.4%**; complete **−40.5%**; radar partial high **−8.8%**). Discussion `L72` and the summary `L146` use *mean-of-class BEV AP* (**−70.42%**, **−42.16%**, **−11.80%**; "pooled AP 23.7 and 21.6", "42.2"). Check: (77.86→16.06, 67.93→27.07) mean 72.90→21.56 = −70.4%. Same condition, two numbers, both labelled "pooled". *Safe phrasing:* "On pooled-object mAP the drop is 76%; averaging per-class AP it's 70%. Same conclusion, different weighting; sedan is 83% of the objects, so pooling is sedan-dominated."

**D2 — Pooled "mAP" is undefined as BEV or 3D.** `Meth:448` states AP at IoU 0.3 without BEV/3D. Baseline table gives both. 73.99 matches neither count-weighted BEV (76.2) nor 3D (72.2) exactly (pooled AP is not a weighted mean). Also "mAP" is a misnomer for object-pooled AP. *Phrase:* "pooled AP at IoU 0.3 over both classes; I'd have to check the repo whether the column is BEV or 3D" — **better: find out before the interview.**

**D3 — Condition counts are inconsistent.** `Res:15` "22 evaluable conditions (including three loss_complete_zero)"; `Disc` "21 evaluable corrupted conditions" and "22-condition sweep" (`Disc:35`); `Meth:432` "36 nominal, of which 22 evaluable" (arithmetic: 3 modalities × 3 effects × 3 severities = 27 + 3 single-tier complete-loss = 21 corrupted, +1 baseline = 22 rows in the table; the 36 counts complete loss at three tiers and frame deletion at nine). `Concl RQ1` "17 of 22 graded conditions within −8.80%": figure supports **16 of 21 corrupted** (five collapse: LiDAR noise med/high/complete, radar noise med/high). Safe: "21 corrupted conditions plus a clean baseline; 5 collapsed, 16 stayed within 8.8%."

**D4 — FN/FP counts differ between text and figure.** `Disc:37` "FP increases in only 6 of 21 … remaining 15 fall". `Fig:metrics`: FP > 4,900 in only **4** conditions (camera noise med 4,913, noise high 4,933, partial med 4,920, partial high 5,078); 17 fall. `Disc:37` "FN rise in 19 of 21" vs `Concl` "missed detections rather than fabricated ones in 20 of 21". `Disc:35` "by more than +50% at five other conditions" lists radar_loss_partial_high at **+29.9%**. Use the figure; quote "FP rose in 4 of 21, max +3.6%".

**D5 — LiDAR complete loss: "collapse" vs "graceful".** `Concl RQ3` calls LiDAR "collapses abruptly under Gaussian noise **and complete loss**"; `Disc:146` calls complete-loss "graceful degradation ASF already shows (pooled AP 42.2)"; `Disc:142` says ASF "survives the loss of an entire sensor". −40.5% mAP (F1 0.805→0.586, FN +131.9%) is not graceful by most standards. *Safe:* "Zeroing LiDAR costs 40%; noise costs 75%. The first is large but proportionate to LiDAR's role; the second is a collapse."

**D6 — Radar corruption mechanics under-specified.** `ASF:66`: RTNH consumes a dense range/azimuth/elevation/Doppler tensor; `Meth:422`: Gaussian noise is added to "radar/LiDAR point xyz (metres)" with σ up to 2 m; `Meth:436` "radar cube/point cloud, depending on modality". The thesis never says what radar representation was perturbed or how xyz noise is applied to a dense tensor in the sweep. Expect "how do you add 1 m noise to a tensor?" — NOT IN THESIS.

**D7 — "Same σ" is not "same severity".** `Disc:47` reads the LiDAR–radar gap as model dependence, but σ=1 m is 20–40× LiDAR's stated accuracy (±2.5–8 cm / ±0.5 cm, `Meth:59,65`) while radar range resolution is 0.46 m and radar cube voxels are 0.4 m (`Meth:52,249`). Equal absolute σ = very unequal perceptual severity; this confounds the claim that the gap "reflects the model's dependence".

**D8 — Cause of noise>zero is claimed in some places, disclaimed in others.** `Abs`/`Concl` frame it via the never-populated availability flag; `Disc:107` says cause "not established", backbone-level voxel sensitivity "equally consistent", discriminating experiment (LiDAR-only detector under same noise) not run and cannot be (Alvis access lost, `Disc:118`). `Concl` "New Findings" also cites a **voxelizer hypothesis ("SECOND's voxelizer silently discarding noise-displaced points near its ROI boundary")** pointing to §lidar_sensitivity, which does **not** contain it in the live Discussion text. Do not present the voxelizer story as a thesis result.

**D9 — Abstract vs Discussion tone.** `Abs:16` "published robustness claims hold only within narrower validation conditions"; `Disc:142` "ASF is mostly robust … a genuine step toward robustness". Both are defensible together; prepare the one-line reconciliation: "mostly robust, one failure regime, and the paper's claim is broader than its evidence."

**D10 — Baseline gap stated in mixed units; explanations missing.** `Res:36` "3–5 AP points below … both classes" — bus gaps are 2.27/2.25 pts. `Res:485` "3.2–5.6%" is **relative**. The three candidate explanations (seed variance, hardware/software, yaw π/2 conversion bug, K-Radar issue #81) exist only in **commented-out** Discussion; `Concl` Future Work still says they were "checked and ruled out". All robustness numbers are relative to your own regenerated baseline, so the gap does not invalidate them, but you cannot cite the "ruled out" analysis from the compiled thesis.

**D11 — Dataset-split ambiguity.** `Theory:25`: K-Radar "comprises 58 sequences (35,000 frames total)"; `Meth:87,522`: "58-sequence, 13,727-frame **test split**, not the full 35,000-frame dataset". Both cannot be literally true. I do not know the official split sizes — NOT IN THESIS. Be ready to state which is right.

**D12 — No uncertainty quantification.** One deterministic noise realization per condition (seed 42, p=1.0, `Meth:430`), single checkpoint, no CIs; reliability handled by N>30 floor and sequence-count flag only (`Meth:446`). Effect sizes at LiDAR noise (−75%) dwarf any plausible variance; camera differences (≤1.8%, mutual differences <1 pt) cannot be ranked.

**D13 — CRI properties.** CRI = (mean AP/AP_clean)/(ln(1+pstdev(AP))+1) with AP in 0–100 points (`Meth:492`): the log term is **unit-dependent** (on a 0–1 scale it ≈ 0 and CRI → mean retention). It punishes any severity gradient (radar_loss_partial: mean retention ≈0.967 but CRI 0.399, lower than lidar_loss_partial 0.546). Borrowed from RoHOI (a human–object-interaction benchmark, `references.bib` rohoi2025), not a validated 3D-detection metric. Ranking by CRI vs by Rb mean can disagree.

**D14 — Class imbalance.** Sedan 29,613 vs bus/truck 5,843; bus/truck rain N=120, fog N=0/5. Pooled results are sedan-dominated; per-axis bus/truck findings often rest on 5–12 sequences.

**D15 — Camera partial loss is pixel-channel dropout**, not occlusion (`Meth:424`) — low realism; camera "robustness" partly reflects that the camera branch contributes little (`Disc:65`).

**D16 — Frame deletion is a harness/model failure, not a perception result.** `Abs:14` says it produces "no predictions"; `Res:482` says it crashes the pipeline (zero-voxel RuntimeError in the sparse-conv backbone for radar/LiDAR; cause for camera not explained). Nine conditions yield no metrics. My inference (NOT IN THESIS): loss_complete_zero keeps N points set to zero (row count preserved, `Meth:424`) while frame deletion produces an empty cloud — which is why one runs and the other crashes.

**D17 — GenAI declaration** (`GenAIDeclaration.tex`): AI used for grammar/clarity and "to suggest code improvements, support documentation". Expect "what did the AI write?" in connection with CV:40 "Engineered". Have a precise answer.

**D18 — Thesis content with no CV mention that interviewers may raise:** frame-deletion crash, baseline reproduction gap, churn metric, dataset characterisation.
