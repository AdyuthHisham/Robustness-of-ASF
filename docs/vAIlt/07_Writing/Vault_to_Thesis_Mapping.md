# Vault ↔ Thesis Mapping

Maps vault notes to thesis chapter/section, with status. Verified against the actual `.tex` files (see [[LaTeX_Report_Structure]]), not assumed from the pre-computed outline.

**Additional LaTeX issue found during this verification, not previously flagged**: `include/Theory.tex:223` has `\subsectionSuggested Test-Suite Architecture (Modeling Approach Summary)}` — missing the opening `{` after `\subsection`. This is a genuine LaTeX syntax error (not just a content gap) that will break compilation of the Theory chapter once Results/Discussion/Conclusion are re-enabled and the full document is rebuilt. Report to the user for the submodule; not fixed here per the read-only constraint.

## Chapter 1 — Introduction

| Section | Status | Vault note | Notes |
|---|---|---|---|
| Background | Written | [[Introduction]] | This project's Introduction.md is a K-Radar-scoped companion to the thesis chapter, not a replacement — cites the same background claims (sensor complementarity, weather asymmetry) with this project's own supporting evidence (K-Radar RTNH-vs-PointPillars result) |
| Problem Statement | Written | [[Introduction]] | Thesis version is broader (cross-dataset generalization); this project's version is K-Radar-specific (per-object visibility as the missing signal) |
| Research Questions | Written | [[Introduction]] | This project's 3 RQs sit inside the thesis's 3 RQs, not parallel to them — see explicit cross-reference in [[Introduction]] |
| Scope and Objectives | Written | [[Introduction]] | |
| Thesis Structure | Written | — | Thesis-level document map; not duplicated in the vault |

## Chapter 2 — Theory

| Section | Status | Vault note | Notes |
|---|---|---|---|
| Sensor Principles (Camera; LiDAR; LiDAR Weather-Driven Degradation; Radar; IMU/GPS-RTK) | Written | [[03_Theory/Coordinate_Frames]] (partial — coordinate conventions only) | No vault note covers general sensor *principles* (optics/scanning/FMCW basics) — that content lives only in the thesis chapter; **gap**, not yet in the vault |
| Sensor Noise and Degradation Models (Camera; LiDAR; Radar; Communication-Layer; Temporal; Environmental Summary; Existing Corruption Benchmarks) | Written | [[03_Theory/Sensor_Noise_and_Degradation_Models]] | Close 1:1 match — this vault note's structure mirrors the thesis section headers almost exactly (same source research underlies both) |
| Calibration Theory (Taxonomy; Targetless LiDAR-Camera; IMU-Camera; LiDAR-IMU; Evaluation Metrics) | Written | — | **Gap** — no vault note; this project's own coordinate-frame work ([[03_Theory/Coordinate_Frames]]) documents K-Radar's *existing* calibration, not general calibration theory |
| Sensor Fusion Architectures (Fusion Levels; Advanced Paradigms; Notable Algorithms) | Written | — | **Gap** — not covered by this project's vault notes (out of scope; this project doesn't build a fusion architecture, it builds the test infrastructure to evaluate one) |
| Perception under Adverse Weather (Weather Effects; Mitigation; Relevant Datasets) | Written | [[02_Literature/Literature_Survey]] Theme 4 | Partial overlap via the literature survey's dataset-foundations theme |
| Evaluation Metrics (Detection; Tracking; Calibration; Adverse Weather Robustness) | Written | — | **Gap** — this project's own metrics are visibility scores, not detection/tracking metrics; no direct vault counterpart |
| Summary | Written | — | |
| Visibility Calculation Methods (LiDAR; Camera; Radar; Theoretical Justification) | Written | [[03_Theory/Visibility_Formulas]] | **Confirmed ordering bug**: this section (`Theory.tex:464`) sits *after* "Summary" (`Theory.tex:461`) — structurally it should precede the summary it's meant to be summarized by. Content-wise this is the **closest 1:1 match in the entire mapping** — the thesis section and [[03_Theory/Visibility_Formulas]] describe the same formulas |

## Chapter 3 — Methods

| Section | Status | Vault note | Notes |
|---|---|---|---|
| System Architecture Overview | Written | [[04_Design/System_Architecture]] | Close match — thesis section is broader (whole-system), vault note is `kradar_visibility`-pipeline-specific |
| Sensor Specifications and Configuration (K-Radar Sensor Suite; Coordinate Frame Conventions; Visibility Calculation Methods; nuScenes Sensor Suite) | Written | [[02_Literature/KRadar_Dataset_Paper]] (sensor suite table), [[03_Theory/Coordinate_Frames]] | No nuScenes coverage in this project's vault work — **gap**, this project is K-Radar-only |
| Data Synchronization (Hardware; Software Timestamp Alignment) | Written | — | **Gap** |
| Calibration Procedure (Initial Target-based; Online Targetless Refinement; Temporal) | Written | — | **Gap** — beyond what [[03_Theory/Coordinate_Frames]] documents (which is K-Radar's *existing* calibration, not a procedure this project performs) |
| Feature Extraction (Image; LiDAR; Radar) | Written | — | **Gap** — out of scope; this project computes visibility scores, not detector input features |
| Fusion Strategy (Availability-Aware Fusion; Fusion Levels Implemented) | Written | — | **Gap** — this is the thesis's own fusion-architecture contribution, a separate deliverable from this project's visibility/noise-injection work |
| Availability-Aware Detection Head | Written | — | **Gap** |
| Handling Adverse Conditions (Radar/LiDAR/Camera Preprocessing; Adaptive Fusion under Degradation) | Written | [[04_Design/Noise_Taxonomy]] (inverse relationship — this project *injects* the degradation this section presumably *handles*) | Not a direct match; complementary |
| Implementation Details (Software Architecture; Hardware) | Written | [[04_Design/System_Architecture]], [[04_Design/API_Contracts]] | Strong match for the visibility-pipeline slice specifically |
| Experimental Setup (Datasets; Training Details; Data Flow of the Robust Test Suite) | Written | [[06_Results/Noise_Visual_Inspection]] (data-flow adjacent), [[04_Design/Noise_Taxonomy]] | "Data Flow of the Robust Test Suite" (`Methods.tex:524`) is the thesis-level description of exactly what this project's noise-injection pipeline implements — closest match in this chapter after Visibility Calculation Methods |
| Summary | Written | — | |

## Chapters 4–6 — Results, Discussion, Conclusion (excluded from build)

Fully written in `.tex` but `\input` commented out in `Main.tex` (commit `41f2e2c`, "results doesn't reflect current status"). Per-section status:

| Chapter | Sections | Vault coverage |
|---|---|---|
| Ch.4 Results | Quantitative Results; Ablation Studies; Sensor Degradation Analysis (Controlled Noise Injection; Complete Sensor Dropout); Qualitative Analysis; Computational Performance; Summary | [[06_Results/Verification_Report]] and [[06_Results/Noise_Visual_Inspection]] are this project's *own* results notes, not populated versions of the thesis's placeholder figures — the thesis's `fig:noise_sensitivity` and `fig:kradar_weather` placeholders are exactly what this project's noise-injection gallery could fill (see ready-to-paste snippets below) |
| Ch.5 Discussion | Interpretation; Comparison with SOTA (BEVFusion, SAMFusion, ASF); Limitations; Implications; Open Questions; Summary | No vault equivalent — this project's own limitations are documented per-note (e.g. [[03_Theory/Visibility_Formulas]] discrepancy notes, [[06_Results/Verification_Report]] cleanup debt), not consolidated into a thesis-level discussion |
| Ch.6 Conclusion | Conclusions; Future Work; Final Remarks | No vault equivalent |

## Ready-to-paste figure snippets

Paths relative to `thesis_report/` — the user copies the actual PNG into the submodule's `figure/` directory themselves; this vault is not written to.

**`fig:noise_sensitivity`** (`Results.tex:243`, currently `% \includegraphics[width=0.9\linewidth]{figure/noise_sensitivity.pdf}`) — candidate source: a severity-ladder comparison from [[06_Results/Noise_Visual_Inspection]], e.g.:
```latex
\includegraphics[width=0.9\linewidth]{figure/noise_sensitivity.png}
% source candidate: docs/vAIlt/_assets/noise_visual_inspection/frame_seq001_rdr033/lidar/lidar_gaussian_noise_{low,medium,high}.png (composite)
```

**`fig:kradar_weather`** (`Results.tex:57`, currently `% \includegraphics[width=0.9\linewidth]{figure/kradar_weather_mAP.pdf}`) — this is a per-weather AP comparison plot, not currently produced by this project's own pipeline (which outputs per-object visibility scores, not model AP). Candidate source: the RTNH-vs-PointPillars weather table in [[02_Literature/KRadar_Dataset_Paper]], re-plotted:
```latex
\includegraphics[width=0.9\linewidth]{figure/kradar_weather_mAP.png}
% source candidate: K-Radar paper's own per-weather AP table (see 02_Literature/KRadar_Dataset_Paper.md),
% re-plotted as a bar chart -- not yet generated by this project
```

## Bib keys in use (for `09_References/`)

`lyuCameraLiDARIMU2025`, `liAutomaticTargetlessLiDAR2023`, `multisensor2025`, `mai2022perception`, `paek2025availability`, `planning_report` — all currently render as `[?]` since bibliography output is disabled (see [[LaTeX_Report_Structure]]).

## Source

- `docs/Latex_Report/thesis_report/include/{Theory,Methods,Results,Introduction}.tex` (section headers verified via grep against actual files)
- [[LaTeX_Report_Structure]]
