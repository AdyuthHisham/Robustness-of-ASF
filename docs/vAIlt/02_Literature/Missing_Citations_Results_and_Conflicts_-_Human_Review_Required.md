---
title: Missing Citations, Results, and Conflicts - Human Review Required
type: literature
source: home/adhish/Productivity/AMSCUP/docs/Latex_Report/FLAGS_REVIEW.md
date: 2026-07-02
tags: [02 Literature]
---
# Missing Citations, Results, and Conflicts - Human Review Required

## [CITE: ...] Flags - Citations Needing Verification

### Theory Chapter
1. **`\cite{lyuCameraLiDARIMU2025}`** - Used extensively. Verify: Lyu et al. 2025 "Camera, LiDAR, and IMU Spatiotemporal Calibration: Methodological Review and Research Perspectives" IEEE T-RO. Check exact title, authors, year.
2. **`\cite{liAutomaticTargetlessLiDAR2023}`** - Li et al. 2023 "Automatic targetless LiDAR–camera calibration: a survey" ISPRS J. Verify exact citation.
3. **`\cite{shiRadarCameraFusion2024}`** - Shi et al. 2024 "Radar and Camera Fusion for Object Detection and Tracking: A Comprehensive Survey" IEEE T-ITS. Verify.
4. **`\cite{multisensor2025}`** - Placeholder citation "A Review of Multi-Sensor Fusion in Autonomous Driving 2025". **NEEDS REAL CITATION** - Find actual paper.
5. **`\cite{paek2022kradar}`** - K-Radar dataset paper. Verify authors: Dong-Hee Paek, Seung-Hyun Kong, Kevin Tirta Wijaya. NeurIPS 2022 Datasets & Benchmarks.
6. **`\cite{paek2025availability}`** - ASF paper. Verify: Paek & Kong 2025 "Availability-Aware Sensor Fusion via Unified Canonical Space" arXiv:2503.07029v2.
7. **`\cite{palladin2024samfusion}`** - Palladin et al. 2024 "SAMFusion: Sensor-Adaptive Multimodal Fusion for 3D Object Detection in Adverse Weather" ECCV 2024 (LNCS). Verify.
8. **`\cite{bijelic2020seeing}`** - Bijelic et al. 2020 "Seeing Through Fog Without Seeing Fog" CVPR 2020. Verify.
9. **`\cite{nuscenes2019}`** - Caesar et al. 2019 nuScenes dataset paper. Verify all authors.
10. **`\cite{Sun_2020_CVPR}`** - Waymo Open Dataset paper. Verify.
11. **`\cite{mai2022perception}`** - Mai et al. 2022 "Perception and sensing for autonomous vehicles under adverse weather conditions: A survey" IEEE T-IV. Verify.
12. **`\cite{kim2015metric}`** - Kim et al. 2015 "A metric for real-time video surveillance systems" Pattern Recognition Letters. Verify.
13. **`\cite{epsm2024}`** - Placeholder "EPSM: A Novel Metric..." **NEEDS REAL CITATION**.
14. **`\cite{sun2024toward}`** - Sun et al. 2024 "Toward Ensuring Safety for Autonomous Driving Perception..." IEEE T-ITS. Verify.
15. **`\cite{hydrafusion}`** - Placeholder **NEEDS REAL CITATION** - Find HydraFusion paper.
16. **`\cite{adafusion}`** - Placeholder **NEEDS REAL CITATION** - Find AdaFusion paper.
17. **`\cite{dgfeg}`** - Placeholder **NEEDS REAL CITATION** - Find DGFEG paper.
18. **`\cite{conformal2023}`** - Conformal prediction survey. Verify.
19. **`\cite{bayesian2022}`** - Gal & Ghahramani 2016 "Dropout as a Bayesian Approximation" ICML. Verify year (2016, not 2022).
20. **`\cite{ewc2017}`** - Kirkpatrick et al. 2017 "Overcoming Catastrophic Forgetting" PNAS. Verify.
21. **`\cite{generative_rehearsal2022}`** - Placeholder **NEEDS REAL CITATION**.
22. **`\cite{tan2020efficientnet}`** - Tan & Le 2019 EfficientNet ICML. Verify year.
23. **`\cite{sparse_radar2023}`** - Placeholder **NEEDS REAL CITATION**.
24. **`\cite{planning_uncertainty2023}`** - Placeholder **NEEDS REAL CITATION**.
25. **`\cite{unified_io2022}`** - Unified-IO paper. Verify.
26. **`\cite{mask2map2023}`** - Mask2Map paper. Verify.
27. **`\cite{clip2021}`** - Radford et al. 2021 CLIP ICML. Verify.
28. **`\cite{sam2023}`** - Kirillov et al. 2023 Segment Anything ICCV. Verify.
29. **`\cite{Van_Brummelen_O'B...}`** - Van Brummelen et al. 2018 Autonomous Vehicle Perception survey. Verify.
30. **`\cite{Raouf_Khan_...}`** - Raouf et al. 2022 Sensor-based PHM survey. Verify.
31. **`\cite{Yan_Liu_...}`** - Yan et al. 2022 OpenCalib. Verify.
32. **`\cite{Liu_Zhang_...}`** - Liu et al. 2025 Awardistill. Verify.
33. **`\cite{Palladin_Dietze_...}`** - Duplicate of palladin2024samfusion. **REMOVE DUPLICATE**.
34. **`\cite{liu2025unilion}`** - UniLION paper. Verify.
35. **`\cite{Nvidia}`** - HuggingFace dataset card. Not a standard citation. Consider removing or citing properly.
36. **`\cite{Chalmers2023}`** - Chalmers website. Not a standard citation. Consider removing.
37. **`\cite{planning_report}`** - Self-citation to planning report. Verify if appropriate.

### Methods Chapter
38. **`\cite{lyuCameraLiDARIMU2025}`** - Temporal calibration method reference. OK.
39. **`\cite{paek2025availability}`** - ASF reference. OK.

### Results Chapter
40. **`\cite{liu2022bevfusion}`** - BEVFusion results. Verify NDS numbers match paper.
41. **`\cite{wang2024mv2dfusion}`** - MV2DFusion results. Verify 76.7% NDS / 74.5% mAP.
42. **`\cite{yin2023ea}`** - EA-LSS results. Verify 74.4% NDS.
43. **`\cite{chen2023hvdetfusion}`** - HVDetFusion results. Verify 67.4% NDS.
44. **`\cite{zhang2023echofusion}`** - EchoFusion results. Verify ~51.4%.
45. **`\cite{paek2025availability}`** - ASF 87.2% mAP claim. Verify.

### Discussion Chapter
46. **All citations above** - Cross-check all references in Discussion.

---

## [RESULT NEEDED] Flags - Experimental Results Requiring Verification

### K-Radar Results (Section 4.1)
| Metric | Reported Value | Source | Verification Needed |
|--------|---------------|--------|---------------------|
| Overall mAP (Car, IoU=0.3) | 79.26% | aggregated_data.md | **VERIFY**: Run evaluation on K-Radar test set |
| Day NDS | 81.43% | aggregated_data.md | **VERIFY** |
| Night NDS | 74.85% | aggregated_data.md | **VERIFY** |
| Fog mAP | 93.70% | aggregated_data.md | **VERIFY** - Seems high, check if correct split |
| Heavy Snow mAP | 65.83% | aggregated_data.md | **VERIFY** |
| Clear mAP | 81.22% | aggregated_data.md | **VERIFY** |
| Overcast mAP | 87.58% | aggregated_data.md | **VERIFY** - Higher than clear? Check |
| Rain mAP | 72.90% | aggregated_data.md | **VERIFY** |

### nuScenes Results (Section 4.2)
| Metric | Reported Value | Source | Verification Needed |
|--------|---------------|--------|---------------------|
| Camera-Radar NDS | 67.4% | aggregated_data.md | **VERIFY** - Matches HVDetFusion claim |
| Full Suite NDS | 72.1% | aggregated_data.md | **VERIFY** |
| Full Suite mAP | 69.7% | aggregated_data.md | **VERIFY** |
| Latency (RTX 4090) | 103 ms | Methods | **VERIFY** - Profile actual model |
| Latency (Jetson Orin) | 156 ms | Methods | **VERIFY** - Deploy and measure |

### Ablation Studies (Section 4.3)
| Configuration | NDS | mAP | Source | Verification Needed |
|--------------|-----|-----|--------|---------------------|
| Base Early Fusion | 62.1% | 58.3% | aggregated_data.md | **VERIFY** |
| + Mid-level | 64.8% | 61.2% | aggregated_data.md | **VERIFY** |
| + Availability | 68.0% | 64.8% | aggregated_data.md | **VERIFY** |
| + Online Calib | 69.5% | 66.4% | aggregated_data.md | **VERIFY** |
| + Weather Proc | 70.2% | 67.1% | aggregated_data.md | **VERIFY** |
| Full Proposed | 72.1% | 69.7% | aggregated_data.md | **VERIFY** |

### Sensor Dropout (Section 4.5)
| Config | NDS | Source | Verification Needed |
|--------|-----|--------|---------------------|
| C+L+R | 72.1% | aggregated_data.md | **VERIFY** |
| L+R | 65.7% | aggregated_data.md | **VERIFY** |
| C+R | 62.1% | aggregated_data.md | **VERIFY** |
| C+L | 68.9% | aggregated_data.md | **VERIFY** |
| Camera only | 50.1% | aggregated_data.md | **VERIFY** |

### Calibration Robustness (Section 4.3.3)
| Initial Error | Fixed Fusion NDS | +Online NDS | Improvement | Verification Needed |
|--------------|-----------------|-------------|-------------|---------------------|
| 5 cm / 1° | 71.8% | 71.9% | +0.1% | **VERIFY** |
| 10 cm / 2° | 70.2% | 71.5% | +1.3% | **VERIFY** |
| 20 cm / 5° | 65.4% | 70.8% | +5.4% | **VERIFY** |
| 50 cm / 10° | 52.1% | 68.3% | +16.2% | **VERIFY** |

### Noise Injection (Section 4.5.1)
| Noise Level | Proposed NDS | Source | Verification Needed |
|------------|-------------|--------|---------------------|
| σ=0 | 72.1% | aggregated_data.md | **VERIFY** |
| σ=0.05 | 71.2% | aggregated_data.md | **VERIFY** |
| σ=0.1 | 69.3% | aggregated_data.md | **VERIFY** |
| σ=0.2 | 64.7% | aggregated_data.md | **VERIFY** |

---

## [CONFLICT: ...] Flags - Conflicting Information

### 1. K-Radar Weather Performance Conflict
**Conflict**: Fog mAP (93.70%) > Clear mAP (81.22%) > Overcast mAP (87.58%)
**Source**: aggregated_data.md Table C.1
**Issue**: Fog performance exceeding clear weather is counterintuitive. Possible explanations:
- Fog test set has easier scenes (fewer objects, simpler scenarios)
- Radar dominates and the evaluation metric favors radar-detectable objects
- Data split issue (fog scenes from different locations)
**Action**: Investigate fog test set composition; verify evaluation protocol; consider reporting per-condition breakdowns with scene complexity metrics.

### 2. Overcast vs Clear Performance
**Conflict**: Overcast (87.58%) > Clear (81.22%) mAP
**Possible**: Diffuse lighting reduces shadows/glare, improving camera performance
**Action**: Verify with qualitative examples; if real, emphasize as finding.

### 3. ASF vs Proposed K-Radar Results
**Conflict**: ASF paper claims 87.2% mAP on K-Radar; Proposed claims 79.26%
**Source**: aggregated_data.md vs paek2025availability
**Possible**: Different evaluation protocols (class subset, IoU threshold, train/test split, Car vs all classes)
**Action**: Check ASF paper's exact evaluation setup; ensure fair comparison.

### 4. nuScenes Camera-Radar NDS
**Conflict**: Proposed claims 67.4% NDS matching HVDetFusion
**Source**: aggregated_data.md Table 4
**Issue**: HVDetFusion paper reports 67.4% NDS on camera-radar track. Need to verify proposed method actually achieves this.
**Action**: Run nuScenes camera-radar evaluation.

### 5. Ablation Cumulative vs Individual
**Conflict**: Ablation shows +3.2% (availability) +1.5% (calib) +0.7% (weather) = +5.4% total, but full method shows 72.1% vs base 62.1% = +10%
**Source**: aggregated_data.md ablation table
**Issue**: Non-additive effects (interactions between components). The table shows cumulative, not isolated.
**Action**: Clarify in text that ablations are cumulative; add isolated component ablations if possible.

### 6. Latency Numbers
**Conflict**: Methods chapter says 103 ms (RTX 4090), Results table says 103 ms, but component breakdown sums to 45+18+35+5=103 ms ✓
**However**: Jetson Orin 156 ms - is this with TensorRT FP16? Batch size 1?
**Action**: Document exact measurement conditions (batch size, precision, warmup runs).

### 7. Citation Year Mismatch
**Conflict**: `\cite{bayesian2022}` references Gal & Ghahramani 2016 paper
**Action**: Fix citation key to `bayesian2016` or update year.

### 8. Duplicate Reference
**Conflict**: `Palladin_Dietze_Narayanan_Bijelic_Heide_2024` and `palladin2024samfusion` appear to be the same paper
**Action**: Remove duplicate; keep one consistent citation key.

### 9. Missing Paper Titles in References
**Conflict**: Several references have placeholder titles ("Authors et al.")
**Items**: multisensor2025, hydrafusion, adafusion, dgfeg, generative_rehearsal2022, sparse_radar2023, planning_uncertainty2023, unified_io2022, mask2map2023
**Action**: Find actual papers and replace placeholders.

---

## Additional Review Items

### Figure References
All figure `\includegraphics` commands currently reference placeholder paths. Need to:
1. Copy images from Obsidian vault to thesis_report/figure/
2. Convert Excalidraw to PDF/PNG
3. Generate missing plots from experimental data
4. Update all figure paths in .tex files

### Table References
All tables use `[H]` placement specifier (requires `float` package - already in Settings.tex ✓). Verify tables render correctly.

### Cross-References
- `\ref{fig:system_architecture}` - Figure not yet created
- `\ref{fig:fusion_pipeline}` - Figure not yet created
- `\ref{tab:kradar_sensors}` - Table exists in Methods.tex ✓
- `\ref{tab:nuscenes_sensors}` - Table exists in Methods.tex ✓
- `\ref{tab:kradar_overview}` - Table exists in Results.tex ✓
- etc. - Verify all labels match references

### Acronyms
Acronyms.tex updated with comprehensive list. Verify all acronyms used in text are defined (4D, ADAS, AMOTA, ASF, AV, BEV, CADC, CAN, CFAR, CLIP, CMOS, CNN, CPU, CVPR, D-S, DNN, DOF, EKF, EPSM, FOV, FPN, FPS, GAN, GNSS, GPU, GPS, HPC, ICP, ICRA, IMU, IoU, IROS, K-Radar, KL, LDS, LiDAR, LSS, LSTM, mAP, mAAE, mASE, mATE, mAVE, mAOE, ML, MLP, mmWave, NDS, NMS, NN, NRIQA, OD, ORB, PnP, PKL, RANSAC, ReLU, RGB, RL, ROI, ROS, RTK, SAM, SfM, SIFT, SLAM, SNR, SOTA, SOTIF, SVD, TTC, TTCE, VIO, VRU).

### Bibliography Style
Main.tex uses `\bibliographystyle{IEEEtrakn}` but References.tex uses manual `thebibliography` environment. **Conflict**: Choose one approach.
**Recommendation**: Keep manual thebibliography for precise control; remove `\bibliographystyle` and `\bibliography` commands from Main.tex, or switch to BibTeX with .bib file.

### Compilation Checklist
Before final submission:
- [ ] Run `pdflatex Main.tex` → `bibtex Main` (if using BibTeX) → `pdflatex Main.tex` × 2
- [ ] Check all citations resolve (no [?] in output)
- [ ] Check all cross-references resolve (no ?? in output)
- [ ] Verify all figures/tables appear
- [ ] Check page limits (if any)
- [ ] Verify Chalmers template compliance (title page, abstract, etc.)

---

## Priority Order for Human Review

### Critical (Block Compilation/Validity)
1. Fix bibliography approach (thebibliography vs BibTeX)
2. Resolve duplicate reference (Palladin)
3. Fix citation year mismatch (bayesian2016 vs 2022)
4. Verify all [CITE: ...] items have real papers
5. Replace placeholder references (multisensor2025, hydrafusion, adafusion, dgfeg, etc.)

### High (Result Validity)
6. Verify K-Radar fog mAP > clear mAP anomaly
7. Verify ASF vs Proposed comparison fairness
8. Verify all ablation numbers from actual experiments
9. Verify Jetson Orin latency measurement conditions

### Medium (Completeness)
10. Generate/create all missing figures
11. Copy and convert Obsidian images
12. Add missing acronyms if any used in text
13. Verify all cross-references

### Low (Polish)
14. Clarify cumulative vs isolated ablation in text
15. Add scene complexity metrics to weather results
16. Document evaluation protocols precisely