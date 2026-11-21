# 03 — Thesis deep-dive Q&A (48 questions)

Source pointers use the key in 01 (`Meth:L`, `Res:L`, `Disc:L`, `ASF:L`, `Abs`, `Concl`, `Fig:metrics`). **NOT IN THESIS: answer from general knowledge** marks anything the document does not support — say it as general knowledge, not as your result. † = derived from `metrics_table.png` (01 §0).

---

## A. Motivation and framing

**Q1. Why evaluate one model instead of building a better one?**
The scope narrowed from cross-dataset fusion to a focused test of one model's published claim (`Intro:37`). ASF was chosen because it explicitly claims robustness to degradation/failure and comes from the K-Radar group (`Meth:15`). A well-specified falsification test is a cleaner contribution than another architecture. *Cost:* single model, single dataset — external validity is limited (`Disc:103`).

**Q2. What exactly does ASF claim, and what evidence did the paper provide?**
Claim: "robust… under various weather and sensor degradation (or failure) conditions", adapts to sensor combinations without retraining (`Meth:15`). Evidence is narrower (`Meth:19-26`): natural weather only (camera encoder trained only on normal/overcast, confounding); "damaged" tests = LiDAR forward-sector removal + static camera crack overlay, no Gaussian LiDAR noise; availability is a manually supplied dictionary, not triggered; trained/tested only at n=3 sensors (SCL needs 2ⁿ−1 passes).

**Q3. State your three research questions and answers in one breath each.**
(1) General behaviour: claim holds for most but not all conditions — 5 of 21 corrupted conditions collapse, frame deletion crashes (`Concl RQ1`). (2) Noisy vs absent: noisy is worse for LiDAR (−74.9/−76.4% vs −40.5%) and radar (−14.9/−22.7% vs ≈−6%†), not camera (`Concl RQ2`). (3) Where graceful vs collapse: camera/radar graceful, LiDAR noise collapses, frame deletion fails uniformly (`Concl RQ3`).

**Q4. Is "noise worse than zeroing" really a surprise?**
In *presence*-dependence terms no: if the network can't tell the branch is bad, wrong data misleads more than a constant. The thesis stresses this is a different axis from "which sensor the model needs" (`Disc:51`). What's new is the *magnitude* and that ASF's own evaluation did not probe it (`Meth:26`). Don't oversell: the cause is not established (`Disc:107`).

**Q5. Why this reality-gap framing?**
`Intro:5` cites Lambertenghi et al. (simulation-to-real) and extends the idea to benchmark composition (K-Radar test set composition, `Meth:174`). NOT IN THESIS beyond that: it's a motivating analogy, not something your results test.

## B. ASF and fusion architecture

**Q6. Walk me through ASF end to end.**
Frozen encoders (BEVDepth cam, SECOND LiDAR, RTNH radar) → BEV maps with equal H×W, different channels C_s → cut into P_H×P_W patches → UCP: per-sensor LayerNorm→MLP(GeLU)→LayerNorm into a shared C_u (`ASF:70-75`, Eq. UCP) → CASAP: one learned reference query attends over the sensors present at that patch, scaled dot-product softmax over sensors (`ASF:79-84`) → PN: same LN/MLP recipe to equalise statistics regardless of sensor count (`ASF:87-92`) → reshape to BEV grid → unmodified SSD head (`ASF:94,116`).

**Q7. Why is CASAP cheaper than sensor-wise cross-attention?**
SCF attends every query over all sensor×patch pairs: O(N_q N_s N_p). CASAP restricts attention to same-position patches across sensors: O(N_q N_s) per patch (`ASF:22-24, 84`).

**Q8. Why can ASF handle a missing sensor without changing network shape?**
A shared fixed query and softmax over present sensors only; with one sensor the softmax is 1, so CASAP becomes a pass-through (`ASF:84`). DCF concatenation, by contrast, ties input channel width to sensor count (`ASF:21`).

**Q9. What is SCL and why seven passes?**
Sum of cls+reg losses over every non-empty subset of {C, L, R}: 2³−1 = 7 forward/backward passes per batch, missing sensors structurally absent from CASAP's key/value set (not zeroed) (`ASF:98`, Eq. SCL). Scales as 2ⁿ−1, so 15 at four sensors (`Meth:24`).

**Q10. Why does ASF freeze the encoders?**
Avoids backprop through three backbones ×7 and avoids UCP chasing a moving target (`ASF:112`). *Implication for your results:* UCP/CASAP/PN were never trained on noisy-but-present LiDAR features and the encoders were never adapted either.

**Q11. How does ASF decide a sensor is unavailable at inference?**
It does not. A sensor is excluded only if its key is missing from an externally supplied availability dictionary; nothing detects dropout (`Meth:23`). The commented-out Methods text states the eval path for the sweep never sets it; the live text states the conclusion (`Disc:95,144`). *Careful:* the code-trace detail (file names, `avail_feats`) is only in commented text.

**Q12. What do you know about BEVFusion and how does it differ?**
In thesis: BEVFusion fuses camera + LiDAR in a shared BEV space; MV2DFusion fuses at proposal level via cross-modal query attention; both camera+LiDAR only, nuScenes (`Theory:66`). **NOT IN THESIS: answer from general knowledge:** BEVFusion (MIT) lifts camera features with LSS-style depth distribution to BEV, encodes LiDAR to BEV (VoxelNet/SECOND-style), concatenates and runs a conv BEV fusion block; a variant (Liang et al.) differs in architecture; a known weakness is that concatenation couples channel layout to sensor set — the problem ASF's UCP targets.

**Q13. Early vs feature vs late fusion — where does ASF sit?**
Feature-level (mid) fusion on BEV maps. The thesis states this only inside a `\iffalse`'d (not compiled) Theory subsection, so it is **not in the compiled thesis**; treat as general knowledge: early = raw data, late = decision/proposal; feature-level trades some information for modality tolerance.

**Q14. Why is a monocular camera method used on a stereo rig?**
K-Radar's stereo baseline is only 0.12 m, so depth from stereo is weak; paper deliberately uses BEVDepth monocular (`ASF:62`, `Meth:73`).

## C. K-Radar

**Q15. Why K-Radar?**
Dense 4D radar tensor (range×Doppler×azimuth×elevation, 64×256×107×37, ~260–300 MB/frame uncompressed; only 3–10% typically extracted as a point cloud) plus structured per-sequence weather/environment/ToD labels, which nuScenes (text captions) and Waymo (geography axis) lack (`Meth:9-11, 49-56, 82`; `Theory:22`).

**Q16. What is the class set and why only sedan and bus/truck?**
Five classes exist; sedan 37,213 vs bus/truck 7,449 instances dominate; "Benchmark v2.0" evaluates sedan+bus/truck jointly and is what ASF reports (`Theory:37`). Your test split: 29,613 sedan, 5,843 bus/truck (`Res:60-84`).

**Q17. What can you say about the test split and why 13,727 frames?**
`Meth:87`: 58 sequences, 13,727 frames, test split. **But `Theory:25` says K-Radar comprises 58 sequences/35,000 frames** — an internal inconsistency (01 D11). NOT IN THESIS: which is right; check before the interview.

**Q18. How are sensors unified geometrically?**
Everything in the radar frame (front grill, X forward); LiDAR via a translation-only calibration (max error 0.5 cm, pitch neglected), cameras via per-sequence radar→camera 4×4 + intrinsics (`Meth:235-270`).

## D. Corruption design

**Q19. Justify the four corruptions.**
Gaussian noise: sensor-internal signal error (CommonCorruption). Partial loss: partially grounded (laser-beam/scan-layer malfunction; radar reflection loss). Complete loss and frame deletion are methodological endpoints with benchmark precedent, explicitly not claims about a physical cause (`Meth:424-428`; fuller discussion commented). Honest answer: only noise has a direct physical grounding.

**Q20. How did you pick σ = 0.1/1.0/2.0 m?**
Chosen to be interpretable against a sedan: 0.1 m ≈ 5% of its 2.1 m width, 1.0 m ≈ 48%, 2.0 m ≈ car width (`Meth:422`). Same schedule for LiDAR and radar "by design". *Weakness:* it's relative to vehicle size, not to sensor accuracy (D7); σ=2.0 m is slightly *less* than 2.1 m, so "exceeds width outright" is loose.

**Q21. Is equal σ across LiDAR and radar a fair comparison?**
Not equal *severity*: LiDAR accuracy ±2.5–8 cm / ±0.5 cm vs radar range resolution 0.46 m, voxel 0.4 m (`Meth:52,59,65,249`). A 1 m perturbation is ≈2 radar range cells but ≈20–40× LiDAR accuracy. So the LiDAR>radar gap partly reflects relative perturbation, not only model dependence (`Disc:47` over-reads it). Say this before they do.

**Q22. How was Gaussian noise applied to a dense radar tensor?**
**NOT IN THESIS** — `Meth:422` says per-coordinate on "radar/LiDAR point xyz", while `ASF:66` says RTNH ingests a dense tensor. I must state which representation the sweep perturbed. General knowledge: perturbing a 4D tensor by xyz noise requires either re-binning displaced points or perturbing the point extraction preceding RTNH.

**Q23. Why zero-fill for complete loss? Is that a realistic dropout?**
It's a stress-test endpoint, "equivalent to loss_partial at f=1.0", not a failure model (`Meth:426`). In this pipeline a zeroed branch is still fed through encoder+fusion (`Disc:109`), so it measures "ASF with an undeclared all-zero sensor", not "ASF with branch removed". ASF's own branch exclusion is a better baseline for true absence (`Disc:76-95`, Table).

**Q24. What does the branch-exclusion vs zero-fill comparison show?**
Relative BEV AP drop from C+L+R when LiDAR is lost: paper −28.8% sedan / −36.5% bus vs this thesis −41.37% / −43.06%; radar −3.9/−12.0 vs −6.67/−10.36; camera −0.8/−1.0 vs −3.06/−0.81 (`Disc:86-88`). LiDAR zero-fill costs 6–13 pts more than clean exclusion. *Caveat:* different baselines (paper vs regenerated, 3–5 pt gap) and different pooling, so treat as indicative.

**Q25. Why does frame deletion crash and is it a finding?**
For radar/LiDAR the `None` frame becomes an empty point cloud and ASF's sparse-conv backbone raises a RuntimeError on zero voxels; for camera the frame is dropped and the pipeline also crashes (`Res:482`). It yields no metrics for 9 conditions. It's a robustness-engineering finding (no empty-input guard), not a statement about detection under temporal loss. Your abstract's "producing no predictions" is looser than "crashed" (D16).

**Q26. Why inference-time only?**
No training was done in the thesis; the checkpoint is the officially released one, weights unmodified (`Meth:5,436`). So findings are about a model never exposed to these corruptions. A retrained-with-augmentation model could behave differently — untested.

**Q27. Is partial loss on camera realistic?**
No: per-pixel colour-channel dropout (`Meth:424`), not occlusion or contamination. It's closer to salt noise; the flat camera result must be read with `Disc:65` (branch contributes little).

## E. Metrics

**Q28. Define AP as you computed it.**
41-point recall-interpolated AP at IoU 0.3 (K-Radar convention), TP/FP/FN pooled across the set; precision at 41 recall levels r∈{0,0.025,…,1}, interpolated as max over r̃≥r (`Meth:448-450`). IoU 0.3 is lenient vs typical 0.5/0.7 — NOT IN THESIS beyond "matches K-Radar official". Whether the pooled "mAP" column is BEV or 3D is not stated (D2).

**Q29. Why F1 in addition to AP?**
F1 is a single operating point at a fixed confidence threshold, so it is more sensitive to calibration shifts than threshold-swept AP (`Meth:458`). Baseline F1 0.805 → 0.268 at LiDAR noise high† . Check: TP 27,169, FP 4,900, FN 8,287 → P 0.847, R 0.766.

**Q30. What are mATE/mASE/mAOE and why do they "improve" in collapsed conditions?**
ATE = ground-plane centre distance; ASE = 1−IoU after aligning translation and rotation; AOE = wrapped yaw difference (`Meth:460-470`). Computed only over matched TPs, so when TPs drop 79.3% (LiDAR noise high) the survivors are the easy cases — survivorship bias (`Disc:13-23`). Do not read mASE/mAOE improvements as gains.

**Q31. Define retention. Why not mCE?**
Rb = metric(condition,severity)/metric(clean, same stratum) following Gao et al. (`Meth:484-488`). Self-relative, no second baseline model needed, unlike mCE. Equivalent to RoboBEV RR/mRR, MSC-Bench RS/mRS.

**Q32. Define CRI and its flaws.**
CRI_c = [mean(AP_L,AP_M,AP_H)/AP_clean] / [ln(1+pstdev(AP_L,AP_M,AP_H)) + 1], population σ on raw AP (`Meth:490-494`). Flaws: (i) log term depends on AP units (0–100 here); (ii) penalises any severity gradient — radar_loss_partial has mean Rb ≈0.97 yet CRI 0.399; (iii) three tiers = tiny sample for a σ; (iv) undefined for single-tier loss_complete; (v) borrowed from RoHOI (HOI detection), unvalidated for 3D detection. Whiteboard: pooled LiDAR noise: mean AP 35.19/73.99 = 0.476; pstdev 24.3; ln(25.3)+1 = 4.23; CRI ≈ 0.112 vs reported 0.106 (sedan)/0.153 (bus).

**Q33. What is churn?**
Per GT object: stable (detected both), corruption-induced miss (clean yes, corrupted no), recovery (clean no, corrupted yes), baseline failure (both missed) (`Meth:472-482`). Churn rate = fraction of *all* objects changing status either way; net retention = of clean-detected objects, how many still detected, credited for recoveries, can exceed 1 (`Res:202-207`). Values: LiDAR noise high churn 0.609, net retention 0.207†.

**Q34. How do you define a detection match for FP/FN counts?**
**NOT IN THESIS beyond** IoU 0.3 threshold and pooled TP/FP/FN. General knowledge: greedy matching of score-sorted predictions to GT by IoU, one-to-one; confidence threshold for F1 not stated in thesis.

**Q35. What is the 'N>30' rule and is it statistically meaningful?**
A fixed GT-object floor (N>30, soft ceiling N>90), plus a flag for cells from <10 sequences, instead of per-cell CIs (`Meth:446`). It is binary and doesn't tell uncertainty above the floor. Frames/objects within a sequence are not independent, so effective N is closer to the number of sequences. A cluster bootstrap over sequences would be the right tool — NOT DONE.

## F. Results and mechanism

**Q36. Why does noise hurt more than zeroing? (give the full answer)**
Observed: LiDAR −74.9/−76.4% (noise med/high) vs −40.5% (zero); radar −14.9/−22.7% vs −6.3%†; camera both ≈ −1–2%†. Thesis hypotheses, both unverified (`Disc:107-109`): (1) The availability mechanism is never invoked, so a corrupted-but-present branch is fused as if valid; zeroed input maps through BN/conv biases to a roughly constant feature, which CASAP/PN may handle more benignly than structured-but-wrong geometry. (2) Backbone-level sensitivity to voxel-scale point noise, independent of fusion (cites Zeng et al. registration degradation under σ=0.05 m). They predict the same outcome; the LiDAR-only test would discriminate and was not run. **NOT IN THESIS: general knowledge:** sparse 3D convs learn local geometric patterns; noise at ≥ voxel size scatters one point per voxel across many voxels, destroying neighbourhood structure and pushing activations out of distribution; an all-zero input is a degenerate but *constant* input, whereas noise yields structured-looking but wrong features. Note ASF trains with sensors structurally *absent*, never zeroed or noisy, so neither case was seen in training. Evidence that features become low-confidence rather than confidently wrong: FP falls −82.8% while FN +260%.

**Q37. FP fell by 83% — does that fit a "confidently wrong features" story?**
No. Confidently wrong features would give hallucinations. The data show suppression: the detector stops reporting (`Disc:35,39`). That fits an out-of-distribution feature map whose scores fall below the report threshold.

**Q38. Why is the LiDAR collapse "non-gradual"?**
Rb 0.941 (σ=0.1) → 0.251 (σ=1.0) → 0.236 (σ=2.0)† — a step between low and medium, then saturation. With three severity tiers I cannot localise the knee (future work: finer σ sweep, `Concl`). The knee likely sits near voxel size — NOT IN THESIS (the voxel size isn't given in live text).

**Q39. Why is camera flat? Is camera robust?**
Not robust — the fused output barely depends on it: camera CRI 0.842–0.936 (`Res:451-452`), paper's own camera-exclusion drop is 0.8–1.0%. Contributing, unproven: camera encoder trained only on normal/overcast sequences (`ASF:110`, `Disc:65`). Camera-only detectors are "extremely vulnerable" (Dong et al.) — different quantity (`Disc:67`).

**Q40. Where is the single most severe cell and should anyone trust it?**
Sedan, parking lots, LiDAR noise medium, Rb 0.003 (`Res:331`, `Res:422`); parking lots sedan N=653. It's a small-sample stratum; thesis says not to read it as a stable environment effect.

**Q41. Why does bus/truck retain more than sedan under LiDAR noise in normal weather (0.456 vs 0.143)?**
Stated as genuine (19 and 18 sequences) but **interpretation deferred / unexplained** (`Res:292`). NOT IN THESIS: general speculation — larger objects have more points, so after noise some structure may remain; unverified.

**Q42. Radar dips harder at medium than high in rain/sleet — explanation?**
Rain N=120 consistent with sample noise; sleet N=1,132 too large for that; reported as unexplained (`Res:296`).

**Q43. Compare the three corruption types.**
By worst case: noise > complete loss > partial loss (`Disc:72`): −70.42% (mean-of-class), −42.16%, −11.80%; on pooled-object mAP: −76.4, −40.5, −8.8†. Literature support is indirect (Gao: misalignment crashes fusion; MSC-Bench: absence-type faults barely move RS).

## G. Statistics, validity, threats, limits

**Q44. What are the threats to validity?**
Internal: single noise realization/seed (`Meth:430`); pooling dominated by sedan; baseline reproduces 2.3–4.6 pt below paper (`Res:30`); aggregation inconsistencies (D1,D3,D4). Construct: σ not matched to sensor accuracy; zero-fill ≠ absence; camera loss is pixel dropout; synthetic faults only (`Disc:112`). External: one checkpoint, one dataset, 58 sequences with 2–7 sequences in many strata (`Disc:103,115`). Conclusion: effect sizes at LiDAR noise are large enough to survive these; fine-grained rankings are not.

**Q45. Is the finding statistically valid? Where are the CIs?**
There are none. The LiDAR-noise effect (pooled mAP 74→17.5; FN +260%) is far larger than plausible sampling variation, but small contrasts (camera conditions, 1–2%) cannot be ranked. Proper fix: bootstrap over sequences, multiple noise seeds, multiple checkpoints — NOT DONE (Alvis access lost, `Disc:118`).

**Q46. Your baseline is 3–5 points below the paper. Why should I trust the rest?**
Gaps: sedan −4.64 BEV/−4.31 3D; bus −2.27/−2.25 pts (relative 3.2–5.6%) (`Res:30-36,485`). All robustness metrics are *relative to my own baseline*, so the gap affects absolute numbers, not retention. Candidate causes (seed variance, hardware, K-Radar issue #81 yaw π/2 conversion) were investigated in commented-out Discussion; none shown sufficient. Honest: unresolved. Do not say "ruled out" without that text.

**Q47. What does the weather-stratified result say?**
Normal weather has 19 sequences — the only reliable anchor; sedan fog/light-snow high scores are small-sample artefacts; bus/truck rain AP 7.9 matches the paper's 8.0 (`Res:124-131`; `Disc` commented comparison). LiDAR noise is worst or second worst in every stratum of every axis, both classes, except bus/truck in urban where radar noise high (0.453) and radar zero (0.570) are worse (`Res:255-256,333`).

**Q48. What would you do differently?**
(1) Run the LiDAR-only (non-fused) detector under the same noise to discriminate fusion vs backbone causes (`Disc:107`). (2) Finer σ sweep around 0.1–1.0 m to find the knee. (3) Calibrate noise to each sensor's resolution (equal relative severity). (4) Multiple seeds + sequence-level bootstrap CIs. (5) Test the availability-declared version: set the dictionary under zero-fill to measure what declaration buys. (6) Combined multi-sensor corruptions. (7) Test a content-derived gate (occupancy/SNR) — proposed, never implemented (`Disc:146`). (8) Cross-architecture replication (`Disc:134`).

---

### Bonus rapid-fire (no pointer needed)
- Total GT objects: 35,456; TP 27,169; FN 8,287; FP 4,900 (`Disc:23,37`).
- LiDAR noise high: FN 29,829 (+259.9%), FP 842 (−82.8%), TP −79.3%.
- Biggest FP rise: +3.63% camera_loss_partial_high.
- Sensor suite: RETINA-4ST 77–81 GHz, 118 m, 0.46 m range res, 107°×37°; Ouster OS2-64 and OS1-128; ZED2i ×4; RTK-GPS (`Meth:44-80`).
- Compute: A40 48 GB, 4/node, 85 nodes, `alvis` partition, one SLURM job per sequence.
