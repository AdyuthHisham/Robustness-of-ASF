# 03 — Thesis deep-dive Q&A (44 questions)

Pointers: `M`=`T/include/Methods.tex`, `R`=`Results.tex`, `D`=`Discussion.tex`, `C`=`Conclusion.tex`, `A`=`ASF.tex`, `Th`=`Theory.tex`, `FIG`=`T/figure/metrics_table.png`, with `T/` = `/home/adhish/Productivity/AMSCUP/docs/Latex_Report/thesis_report/`. **NID** = "NOT IN DOCUMENTS: answer from general knowledge" — say it as general knowledge, not as a thesis result.

---
## 1. Framing and design choices

**Q1. Why evaluate a released checkpoint instead of training your own fusion model?**
The question was whether ASF's published claim survives conditions its authors did not test; that needs their weights, unmodified. Training my own would test my model. Scope also excludes new architecture (`M:5`, `Introduction.tex` scope list). The original aim (cross-dataset transfer, unified strategy) narrowed over the project (`Introduction.tex:37`). Cost: single checkpoint, no seed variance (`D:103`).

**Q2. Why ASF?** (a) explicit claim of robustness to degradation and failure; (b) same group as K-Radar, so it is the model best placed to exploit the dataset; (c) only architecture in the surveyed literature that fuses all three modalities and is built on K-Radar (`M:15`, `Th:98`).

**Q3. Why K-Radar rather than nuScenes?** Structured per-sequence weather labels (7 categories), dense 4D radar tensor (64×256×107×37) vs sparse CFAR points; nuScenes records weather in free-text captions, Waymo not at all (`M:9-11,44-82`, `Introduction.tex:33`). Cost: small dataset, imbalance (sedan 37 213 vs bus/truck 7 449 in ASF paper), strata with few sequences.

**Q4. What exactly is your contribution?** A per-sensor inference-time corruption harness plus a metric stack and the measurement of one asymmetry (noise > absence for LiDAR and radar). Not a new model, not a mechanism proof (`C:9`).

**Q5. Why only Gaussian noise, partial loss, complete loss, frame deletion?** Taxonomy follows prior benchmarks (Gao 2023: 14 patterns; Dong 2023; Yu 2022; Bijelic's whole-stream dropout). Only Gaussian noise has a direct physical grounding (sensor-internal noise, CommonCorruption); complete loss and frame deletion are "methodological conveniences" I do not claim model a specific hardware fault (`M:420-428`, commented rationale `M:377-418`). Cost: no weather simulation, miscalibration, misalignment, or joint corruption.

**Q6. Why σ = 0.1 / 1.0 / 2.0 m?** Same schedule for radar and LiDAR so the comparison isolates model dependence; scaled against ASF's sedan anchor 4.2×2.1×2.0 m: 0.1 m ≈ 5 % of width, 1.0 m ≈ 48 %, 2.0 m > width (`M:422`). Honest: high severity is a stress test; older notes flag it as ~10× above literature LiDAR noise (`defense_questions.md`, unverified in `.tex`). A finer sweep between 0.1 and 1.0 m was not run (`C:69`).

**Q7. Is 'the same σ for radar and LiDAR' fair?** It equalises metres, not information content or voxel scale. Radar grid voxel is 0.4 m (`M:249`) and LiDAR voxel size is ASF-config specific (NOT IN DOCUMENTS: SECOND typical 0.05–0.1 m — general knowledge). So the same σ is relatively "bigger" for LiDAR's voxels — a confound for the LiDAR-vs-radar ranking. State it.

**Q8. Why corrupt at inference only?** Question is the released model's behaviour; no corrupted training data exists in this study (`M:436`). Result is therefore "what a clean-trained model does", not "what is achievable with robust training".

## 2. ASF and BEVFusion architecture

**Q9. Walk me through ASF.** Encoders (BEVDepth, SECOND, RTNH) → BEV maps, same H×W, different channels C_s → patchify → UCP per-sensor MLP (LN → GeLU-MLP → LN) to common C_u → CASAP: one learned reference query attends over the available sensors' vectors at each patch (score = Q·F/√C_u; softmax across sensors) → PN → reshape to grid → unmodified SSD head. Training: SCL over 2³−1 = 7 subsets; encoders frozen (`A:57-116`).

**Q10. Why is CASAP cheaper than sensor-wise cross-attention?** SCF attends every query over all sensors × all patches: O(N_q N_s N_p). CASAP restricts to same-position patches: O(N_q N_s) per patch (`A:22-24,84`).

**Q11. What happens when only one sensor is present?** Softmax over one key = 1; CASAP is pass-through, so output shape is unchanged — the structural reason a missing sensor needs no retrain; PN then renormalises the different statistics (`A:84-88`).

**Q12. Is ASF's availability awareness automatic?** No. Excludes a sensor only if its key is absent from an externally supplied availability dictionary; the network has no run-time dropout detector (`M:23`). The sweep path never sets it (commented-out code trace `M:34-36`; stated in `C:18`, `D:95`). So in my sweep every branch is always in the attention set — including the zeroed one.

**Q13. So is your 'complete loss' really a sensor loss?** No: it is zero-fill through the encoder. The network's biases/BN can map all-zeros to a non-zero constant (plausible, unverified; `D:109`). ASF's own branch-exclusion is cleaner; compare: LiDAR −28.8 % (sedan) clean exclusion vs −41.4 % zero-fill; −36.5 % vs −43.1 % bus; radar −3.9 % vs −6.7 %, −12.0 % vs −10.4 %; camera −0.8 % vs −3.1 %, −1.0 % vs −0.8 % (`D:80-91`). Careful: each relative to its own study's baseline.

**Q14. BEVFusion vs ASF?** BEVFusion fuses camera + LiDAR BEV features in a shared BEV space (feature-level); ASF adds radar and replaces concatenation with patchwise attention, enabling any subset. MV2DFusion is proposal-level. Neither BEVFusion nor MV2DFusion was evaluated; they only motivated the choice (`Th:66`). Anything deeper on BEVFusion (e.g. LSS view transform, BEV pooling kernel) is **NID**.

**Q15. Early/mid/late fusion — where is ASF?** Feature-level (mid). Data-level and decision-level definitions are in a commented-out block (`Th:42-49`); definitions are standard — **NID** beyond that.

**Q16. Why are encoders frozen, and does that matter for your result?** Frozen to avoid backprop through three backbones × 7 passes and a moving UCP target (`A:112`). Consequence: LiDAR noise sensitivity likely lives partly in SECOND's frozen voxelisation/sparse conv, which is why a backbone-level explanation is "equally consistent" (`D:107`).

**Q17. Camera encoder trained only on normal/overcast — relevance?** Plausible reason fused output depends little on camera and why camera is weak in adverse weather in ASF's paper; not proven for synthetic noise (`D:65`, `C:54`).

## 3. K-Radar and data

**Q18. Describe the sensor setup.** RETINA-4ST 4D radar (77–81 GHz, 118 m, 107° az, 37° el, 10 Hz); OS2-64 and OS1-128 LiDARs; four ZED2i stereo pairs; RTK-GPS. All annotations in radar frame (X forward). LiDAR→radar translation only (e.g. −2.54, 0.30, 0.70 m) (`M:44-80,235-246`).

**Q19. Why is radar 'dense'?** The tensor keeps the full range–azimuth–elevation–Doppler power distribution (~260–300 MB/frame); only 3–10 % is usually extracted as points (`M:82`).

**Q20. What are the benchmark conventions?** v2.0: sedan + bus/truck, IoU 0.3, AP_BEV and AP_3D, 41-point recall interpolation (`Th:37`, `M:448-452`).

**Q21. Is your baseline reproducing the paper?** No: 4.6/4.3 points below on sedan (BEV/3D), 2.3/2.3 on bus/truck. Same checkpoint, same code, same IoU, so unresolved. Seed variance ruled out (paper's 10-seed std small), software/hardware difference "checked and ruled out" (commented text), candidate: KITTI-yaw π/2 conversion issue (K-Radar GitHub #81), unquantified (`R:36`, `C:63`). Impact: all R_b ratios share a denominator that is itself offset; ratios are less affected than absolute AP but not immune.

**Q22. How balanced is the test data?** Weather: normal 5 415 frames, sleet 2 206, heavy snow 1 720, fog 1 445, rain 1 424, light snow 1 103, overcast 414. Day 9 196 / night 4 531. Urban 4 764, highway 4 308 … (`M:148-156,165`). Fog bus/truck N = 0/5; overcast two sequences (`R:61-77`). So the minority strata are statistically fragile — flagged, not hidden.

**Q23. Why does bus/truck collapse in rain (AP 7.9)?** Observed in both the paper (8.0) and your regeneration (7.89); only 120 objects, 5–12 sequences. Cause not investigated (`R:131`, commented table). Don't theorise beyond that.

## 4. Metrics

**Q24. Define AP as you used it.** 41-point interpolated AP at IoU 0.3: precision at recalls {0, 0.025 … 1}, p_interp(r) = max_{r̃≥r} p(r̃); TP/FP/FN pooled over the evaluation set (`M:448-452`).

**Q25. Why also F1?** Single operating point; more sensitive to confidence-calibration shift than AP (`M:454-458`). Baseline F1 0.805 (precision 0.847, recall 0.766); at LiDAR noise high 0.268.

**Q26. Define retention.** R_b = metric(condition, severity) / metric(clean, same stratum), after Gao et al.; RR/mRR (RoboBEV), RS/mRS (MSC-Bench) are equivalent under other names. Needs no second baseline model (`M:484-488`).

**Q27. Define CRI and critique it.** CRI = [mean(AP_L, AP_M, AP_H)/AP_clean] / [log(1 + pstdev(AP_L, AP_M, AP_H)) + 1] (RoHOI naming). Population std because three tiers are the complete set; std on raw AP not on the retention ratio (`M:490-494`). Critique (your own, from older notes): with three tiers the variance term is weak; CRI is secondary to retention; undefined for single-tier complete loss. Also the formula mixes units: AP in raw points inside a log vs a ratio in the numerator — any change of AP scale (0–1 vs 0–100) changes the penalty. NID for the original RoHOI derivation.

**Q28. Why does mASE/mAOE 'improve' under heavy corruption?** Computed on matched TPs only; at LiDAR noise high pooled TP falls 79.3 % so survivors are easy cases — survivorship bias, not accuracy gain (`D:23`; FIG mASE 0.203 vs 0.239, mAOE 0.137 vs 0.207).

**Q29. What is churn?** Per-object transition vs clean: stable / corruption-induced miss / recovery / baseline failure. LiDAR noise high: net retention 0.207, churn 0.609 (`M:472-482`; FIG).

**Q30. Why isn't there a confidence interval?** Fixed N>30 floor (soft ceiling N>90) and a <10-sequence flag instead; coarser than CI and says nothing about uncertainty above the floor (`M:446`). Cleanest honest answer: "frames within a sequence are correlated, so a naive frame-level CI would be too narrow; a sequence-level bootstrap is the right tool and I did not run it" (bootstrap = **NID**, general knowledge).

## 5. Findings

**Q31. Headline numbers?** See `01_claim_audit.md` T2–T9.

**Q32. Why does noise hurt more than zeroing?** *Measured:* LiDAR −74.9/−76.4 % vs −40.5 %; radar −14.9/−22.7 % vs −6.3 %; camera neither. *Hypotheses (not discriminated):* (H1) the corrupted branch is never gated: a zeroed input yields a near-constant, structured feature, while noise yields confidently wrong geometry that the attention weights cannot reject, and the detection head then suppresses output (FN up, FP down). (H2) backbone-level: voxelisation + sparse conv are sensitive to voxel-scale displacement independent of fusion (`D:107`); a candidate sub-mechanism — SECOND discarding noise-displaced points at the ROI boundary — was *not* verified and doesn't explain near-field collapse (`C:50`). (H3, general knowledge, not tested): noisy points redistribute into many occupied voxels, destroying the sparsity pattern the sparse conv relies on, whereas zero points simply remove input. Say H3 is NID.

**Q33. Why FN up and FP down rather than hallucinations?** Corrupted LiDAR leaves no coherent object-shaped cluster, so confidence scores fall below the report threshold: the detector 'abstains'. FP −82.8 %, FN +259.9 %; largest FP increase +3.6 % (`D:33-39`). The inference that confidence shrinks is consistent with this but the score distributions were not inspected in the thesis (NID for the score histogram).

**Q34. Is ASF robust or not?** 16 of 21 corrupted conditions within −8.8 %; the collapse is concentrated in a named minority; but the one failing regime (present-but-corrupted LiDAR) is exactly the one with no health signal (`D:27,142-144`).

**Q35. Camera barely matters — is camera robust?** No. It means fused output barely depends on camera, so camera corruption barely moves it. Camera-only detectors are "extremely vulnerable" (Dong 2023). Camera L+R config vs C+L+R: only 2.0 AP3D points for sedan, 0.5 bus (commented ablation `D:226`).

**Q36. Radar vs LiDAR?** Radar sits between: CRI 0.272 vs 0.106/0.153 for LiDAR vs 0.84–0.94 camera. Radar's collapse conditions (noise M/H, partial-high) = three of the six FN-heavy conditions (`D:56`).

**Q37. Class divergence?** In normal weather bus/truck retains R_b 0.456 vs sedan 0.143 at LiDAR noise high; in Urban 0.789 vs 0.227. Interpretation deferred, unexplained (`R:292,329`). Candidate (general knowledge, untested): larger objects have more points so survive noise better.

**Q38. Frame deletion?** Crashes all 3 modalities (RuntimeError on zero-voxel sparse-conv input; camera None crashes too); excluded from CRI and strata (`R:480-482`). Caveat D6 in audit.

## 6. Statistical validity, threats, hindsight

**Q39. Statistical validity?** Pooled N = 35 456 GT objects; single seed 42; deterministic p = 1.0, so each condition is one sample of the noise realisation. Mitigation: five LiDAR-noise strata agree. Missing: multi-seed noise draws, sequence-level bootstrap, multiple checkpoints.

**Q40. Threats to validity?** Construct: synthetic ≠ real faults. Internal: reproduction gap, aggregation choice (pooled vs class-mean), zero-fill ≠ exclusion, seed. External: one model, one dataset, one weather-skewed split. Conclusion: causal claim not supported.

**Q41. What would you do differently?** (1) run the LiDAR-only (non-fused) detector under identical noise, (2) multiple noise seeds + sequence bootstrap, (3) finer σ grid 0.05–1.0 m with voxel-size-relative σ, (4) populate the availability flag in an "oracle exclusion" run to bound the gating effect, (5) log score distributions to prove 'abstention', (6) joint corruptions. Items 1 and 4 are exactly what would discriminate H1/H2.

**Q42. Does your result generalise to production?** No claim. Same asymmetry in other availability-aware architectures is an open question (`D:134`).

**Q43. How does this relate to safety standards?** Discussion cites Sun et al. 2024 on safety standardisation calling for characterisation of degraded states (`D:144`). Details of ISO 26262/SOTIF/UL 4600 are **NID**.

**Q44. Compute and reproducibility?** Alvis, A40 (48 GB), SLURM array, one job per sequence, partition `alvis`; seed 42; KITTI-format outputs → single Parquet; metrics from one canonical loader (`M:511-529`). Number of jobs/GPU-hours: **NOT IN DOCUMENTS** — don't quote one. Apptainer: not in the thesis; answer only from your own experience.

---
## Likely probes to rehearse (one line each)
- "Your −75 % depends on σ — what's the break-even σ?" → unknown between 0.1 (−5.9 %) and 1.0 m (−74.9 %); that's the finer-sweep gap.
- "Does the collapse start at voxel size?" → conclusion text frames "at or above voxel resolution" in old notes; not tested in current `.tex`.
- "Could a sanity filter (statistical outlier removal) fix it?" → untested, NID; plausible but would be a *different* system.
