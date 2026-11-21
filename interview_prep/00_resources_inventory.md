# 00 — Resources inventory

Scope: `/home/adhish/Documents/Ady_Resume/resources` listed recursively (`find -type f`). **Three files total.** No subfolders, no code, no READMEs, no certificates, no job descriptions, no past applications, no Cleeven material. Nothing in the three files contains instruction-like text aimed at the reader (checked: all are plain course reports/articles).

| Path | Type | Pages | Contents (1 line) | Supports |
|---|---|---|---|---|
| `resources/Project_Report_SSY191_Group_7.pdf` | PDF, IEEE two-col, text-extractable | 7 | SSY191 (Model-Based Dev. of Cyber-Physical Systems) report: Crazyflie 2.1 Simscape plant, complementary filter (γ=0.9), linearisation, discrete LQR (Ts=0.01 s), simulation vs. failed hardware test. 4 authors (you = 2nd). | CV "Modeling and Control of a Crazyflie Quadrotor" |
| `resources/SSY226_Fido_article_final.pdf` | PDF, IEEE two-col, text-extractable | 8 | SSY226 design project "FIDO": Unitree Go2 tour-guide robot; RTK-GNSS + odometry + IMU EKF (coordinated-turn model), LiDAR-inertial SLAM, LLM-as-agent interaction (STT 92.7 %, latency 0.485 s). 5 authors (you = 1st). | CV "FIDO, EKF Navigation for an Autonomous Robot Dog" |
| `resources/SSY345_Project_Group_37.pdf` | PDF, LaTeX report, text-extractable | 14 | SSY345 (Sensor Fusion & Nonlinear Filtering) report: quaternion EKF (gyro-as-input, accel + magnetometer updates, outlier gating), MATLAB listings, RMSE vs. phone-app reference. 2 authors (you + a partner). | CV "Real-Time Orientation Estimation from Smartphone IMU" |

Text extracted with `pdftotext -layout`; all three read in full. Figures inside the PDFs were not OCR'd (captions and surrounding text only).

## Unmatched / unreadable
- Unreadable: none.
- Resource files with no CV entry: none (all three map to a project).
- **CV entries with NO file in resources** (so every answer on them is "NOT IN DOCUMENTS"):
  - Sysenso Systems / Siemens client-site LiDAR annotation tool (Jul 2023–Jul 2024)
  - Chalmers Industriteknik Myo EMG / Meta Quest 3 / Unity internship (Jun–Aug 2025)
  - ROS2 camera perception & robotics learning pipelines (personal project)
  - SLURM/Apptainer HPC (partially supported by thesis Methods §"Experiment Setup", `Methods.tex:508-531`, but no job scripts, containers or logs)
  - Hackathon (LUNAR FINTECH / Noctis Bank), extracurriculars
- Also missing from resources: any Cleeven job description, any past application, any certificate.

## Other files read (outside resources, for cross-checking)
- CV: `/home/adhish/Documents/Ady_Resume/master/Adyuth_Hisham_CV_Master.tex`
- Thesis: `docs/Latex_Report/thesis_report/Main.tex` + `include/{Introduction,Theory,ASF,Methods,Results,Discussion,Conclusion}.tex`, `frontmatter/*.tex`, `backmatter/radar_tables.tex`, `figure/metrics_table.png` (image inspected), plus `adyuth_thesis_defense_details.md` and `defense_questions.md` (older-draft notes; used only as secondary cross-check, **they cite an older `report.md` and some numbers differ from the current `.tex`**).
- Not read in full: `Discussion.tex` lines 148–488 (entirely commented-out legacy text; non-comment lines after 267 = none), `references.bib` entries, the PNG/PDF figures other than `metrics_table.png`, `References.tex`.
