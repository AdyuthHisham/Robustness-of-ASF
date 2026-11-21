# 01 — Claim audit (CV × thesis × resources)

Path shorthand: `T/` = `/home/adhish/Productivity/AMSCUP/docs/Latex_Report/thesis_report/`; `CV` = `/home/adhish/Documents/Ady_Resume/master/Adyuth_Hisham_CV_Master.tex`; `R/` = `/home/adhish/Documents/Ady_Resume/resources/`; `FIG` = `T/figure/metrics_table.png` (pooled-metrics table, read cell by cell).

Status: **OK** supported · **DERIVED** true but not printed in thesis text, computed from FIG · **WEAK** partly supported · **CONFLICT** sources disagree · **UNSUPPORTED** no document backs it.

Nothing was edited. An earlier run of this task is preserved in `_previous_run/` (it lacked the three PDFs; where it disagrees with this file, trust this file).

---
## A. Headline thesis numbers

| # | Claim | Source | Status / note |
|---|---|---|---|
| T1 | Clean pooled mAP 73.99, F1 0.805, FP 4 900, FN 8 287 | FIG `original`; `T/include/Discussion.tex:37` | OK |
| T2 | LiDAR Gaussian noise medium/high: mAP 18.54 / 17.45, R_b 0.251 / 0.236 → **−74.9 % / −76.4 %** | FIG; `Conclusion.tex:16` | OK |
| T3 | LiDAR complete loss (zero-fill): mAP 44.05, R_b 0.595 → **−40.5 %** | FIG; `Conclusion.tex:16` | OK |
| T4 | Radar noise medium/high: mAP 62.94 / 57.18 → **−14.9 % / −22.7 %** | FIG; `Conclusion.tex:16` | OK |
| T5 | Radar zero-fill: mAP 69.36, R_b 0.937 → **−6.3 %** | FIG only. The only "6.28 %" in text (`Discussion.tex:25`) is a *true-positive-population* change, a different quantity | DERIVED; easy to conflate |
| T6 | Camera zero-fill 72.66 (R_b 0.982, −1.8 %); camera noise high R_b 0.982 | FIG | DERIVED |
| T7 | FN: LiDAR noise high +259.9 % (29 829 vs 8 287), medium +252.5 %, LiDAR zero +131.9 %, radar noise high +77.4 %, medium +51.0 %, radar partial-high +29.9 % | `Discussion.tex:35`; FIG | OK (29 829/8 287 = 3.599 ✓) |
| T8 | FP at LiDAR noise high −82.8 % (842 vs 4 900); largest FP rise anywhere +3.6 % (camera_loss_partial_high 5 078) | `Discussion.tex:33-37`; FIG | OK ✓ |
| T9 | mAP within −8.80 % of baseline for 17 of 22 conditions; five collapse by 14.9–76.4 % | `Conclusion.tex:14` | OK. −8.80 % = radar_loss_partial_high (R_b 0.912). Five = LiDAR noise M/H, LiDAR zero, radar noise M/H |
| T10 | CRI sedan/bus: lidar_gauss 0.106/0.153; radar_gauss 0.272/0.272; camera_gauss 0.915/0.842; camera_partial 0.936/0.929; lidar_partial 0.546/0.383; radar_partial 0.399/0.348 | `Results.tex:450-457` | OK; radar_gauss identical across classes — verify in data before quoting |
| T11 | Baseline vs ASF paper: sedan BEV 77.86/82.5, 3D 74.99/79.3; bus BEV 67.93/70.2, 3D 58.15/60.4 | `Results.tex:30-31` | OK |
| T12 | Frame deletion crashes all 3 modalities; 9 conditions unusable | `Results.tex:480-482` | OK (see D6) |
| T13 | 13 727 frames, 35 456 GT objects, σ = 0.1/1.0/2.0 m, f = 0.1/0.3/0.7, N = 19/5/2, seed 42, p = 1.0 | `Methods.tex:87,420-430`; `Results.tex:15` | OK (see D1) |
| T14 | 36 nominal → 22 evaluable | `Methods.tex:432` | WEAK: 3 modalities × (3 effects × 3 severities + 1 complete) = 30, not 36 |
| T15 | LiDAR average mAP loss over seven conditions = 28 % | not in thesis | DERIVED: mean R_b (0.941, 0.251, 0.236, 1.010, 1.017, 0.959, 0.595) = 0.716 → **28.4 %** |
| T16 | Radar 8 %, camera 1 % | not in thesis | DERIVED: radar 0.924 → 7.6 %; camera 0.986 → 1.4 % (rounds to 1 %, borderline) |

## B. CV claims

| # | CV line | Claim | Source | Status |
|---|---|---|---|---|
| C1 | CV:37-43 | Thesis Jan–Sep 2026; supervisors Assadi & Kovaceva | `T/include/frontmatter/Titlepage.tex:125-127`, `Preface.tex` | OK |
| C2 | CV:40 | Framework, independent per-modality corruption; AP/F1/localisation/retention/CRI; SLURM **and Apptainer** | `Methods.tex:420-430,441-494,511` | SLURM OK. **Apptainer/Docker appear nowhere in the thesis** and no resource backs them |
| C3 | CV:41 | numbers | T2–T9, T15–T16 | OK / DERIVED |
| C4 | CV:41 | noisy worse than zeroed for LiDAR and radar at medium/high | T2–T5 | OK (radar low noise: R_b 1.003, no harm; CV already says "medium and high") |
| C5 | CV:41 | LiDAR losses from missed detections, FP ≤ 3.6 % | T7, T8 | OK; the *cause* of noise>zero is **not established** (`Discussion.tex:106-109`) |
| C6 | CV:20-25 | Sysenso/Siemens LiDAR annotation tool | none | UNSUPPORTED (CV only) |
| C7 | CV:27-32 | Myo EMG + Quest 3 + Unity; "validated" | none | UNSUPPORTED; be ready to define "validated" |
| C8 | CV:48-54 | ROS2 camera/action pipelines | none | UNSUPPORTED. Date: Jul–Aug 2023 overlaps the Sysenso job (Jul 2023–Jul 2024, Chennai) but is listed "Gothenburg, Sweden" (your MSc starts Sep 2024) → expect "when/where?" |
| C9 | CV:58 | FIDO EKF fuses GNSS/RTK + IMU | `R/SSY226_Fido_article_final.pdf` §III-A3: state [x,y,v,φ,ω], coordinated-turn model; update with RTK-GNSS position and IMU rates; also fuses **odometry** | OK; odometry is the main high-rate input and is missing from CV |
| C10 | CV:58 | "**sub-meter** positional accuracy in live tests" | same PDF, abstract + §IV-A1: GNSS-vs-odometry-baseline RMSE **6.7 → 1.7 m** with RTK; odometry "not an absolute ground truth" (§III-A5a); no EKF accuracy number (EKF judged visually, Fig. 5) | **CONFLICT.** 1.7 m ≠ sub-meter; it is raw-GNSS RMSE vs. odometry, not EKF vs. ground truth. Highest-risk CV line |
| C11 | CV:59 | "outlier rejection in the EKF measurement-update … under GPS multipath" | same PDF: "outlier" 0 hits, "multipath" 0 hits; only covariance-weighted updates (static GNSS covariance calibration; §V-C1 lists RTK/non-RTK covariance mismatch as a *limitation*) | **UNSUPPORTED.** Outlier gating is in SSY345, not FIDO |
| C12 | CV:56-59 | "live tests on a campus robot dog" | same PDF §V-A: indoor/outdoor "not fused"; module "has yet to be validated in a real-time deployment" | WEAK |
| C13 | CV:65 | EKF "6-DOF orientation from accelerometer/gyroscope" + outlier handling for "noise spikes" | `R/SSY345_Project_Group_37.pdf` Tasks 6–11: gyro as input + accelerometer **+ magnetometer**; 4-state unit quaternion; gating = ‖a‖≠9.81 (external force) and AR(1) magnetic-norm tracker (disturbance) | **CONFLICT:** magnetometer omitted; orientation is 3 DOF; "noise spikes" mislabels the gating purpose |
| C14 | CV:66 | "Benchmarked against Google's proprietary algorithm across configurations to identify optimal combinations" | same PDF Task 12: reference = "orientation data streamed from the smartphone"/"the app's algorithm" (Google never named). RMSE up to 2.71 rad (angle 1, all sensors), 2.43 (acc+gyro), 1.14 (gyro+mag), 3.51 (acc+mag). Report: initial orientations differ → "difficult to directly quantify"; "both our filter and the app's … struggle" | **OVERSTATEMENT.** Qualitative comparison only; no optimum is identified; "Google" is not in the document |
| C15 | CV:65 | "real-time" | report is MATLAB with streamed data (`filterTemplate.m`); real-time not demonstrated | WEAK |
| C16 | CV:72 | LQR "for roll, pitch and **yaw** stabilization" | `R/Project_Report_SSY191_Group_7.pdf` §V: x = [φ, φ̇, θ, θ̇, ψ̇]; "specific emphasis on … roll and pitch"; yaw **rate** only | **OVERSTATEMENT** |
| C17 | CV:72 | complementary filter from raw IMU | same PDF §III: γ = 0.9, θ_k = (1−γ)θ_acc,k + γ(θ_{k−1} + h·ω_k); roll/pitch only | OK |
| C18 | CV:73 | "validated robustness against simulated disturbances" | same PDF §VII: reference pulses on roll/pitch, thrust changes small (Figs 5–6) | WEAK: one simulation, no parameter-uncertainty test |
| C19 | CV:73 | "establishing a simulation-to-hardware deployment framework" | same PDF abstract: "validation is limited to a closed simulation"; §VIII–IX: hardware oscillated, "efficiency seen in simulations is not translated well", C-code generation "could not be completed", "proper testing … was not possible" | **CONTRADICTED** |
| C20 | CV:102-106 | PyTorch, Docker, Bash, "SLAM-adjacent" | none for PyTorch/Docker/Bash; SLAM only as FIDO LIO (your share unclear) | WEAK |
| C21 | CV:86-88 | Hackathon 1st prize | none | UNSUPPORTED (non-technical) |

## C. Thesis-internal discrepancies you would struggle to defend

| # | Issue | Where | Safe phrasing |
|---|---|---|---|
| D1 | "58-sequence test split" yet K-Radar "comprises 58 sequences (35 000 frames)": whole dataset and test split cannot both be 58. Also N_gt table/pie include LightSnow and HeavySnow, while commented-out legacy text in `Discussion.tex` says the test split has none | `Theory.tex:25`, `Methods.tex:87,148`, `Abstract.tex:12`, `Results.tex:66-67` | "13 727 frames of the released test partition (58 sequences in my label set)"; verify counts before the interview |
| D2 | Two AP aggregations: FIG/Conclusion use **pooled** mAP (LiDAR noise high 17.45; zero 44.05). `Discussion.tex:146` says "pooled AP 23.7 and 21.6 (medium/high) … 42.2 (zero)" — these are class-mean (sedan 16.06, bus 27.07 → 21.6). `Discussion.tex:72` −42.16 % (class-mean) vs `Conclusion.tex:16` −40.5 % (pooled) | as listed | Always name the aggregation: "pooled mAP 17.45" vs "class-mean 21.6" |
| D3 | Baseline gap "3–5 AP points" (`Results.tex:36`) and "3.2–5.6 %" (`Results.tex:485`): points vs relative. Actual: 4.64 / 4.31 / 2.27 / 2.25 points = 5.6 / 5.4 / 3.2 / 3.7 % | `Results.tex:30-36,485` | "2–5 AP points (3–6 % relative) below the paper; cause unresolved" |
| D4 | FIG has 21 corrupted rows (7 per modality) + baseline = 22 rows, so `Conclusion.tex:14` "17 of 22" = 16 corrupted + baseline; `Results.tex:15` "22 evaluable conditions" also includes the baseline. Condition counts: 36 nominal, 22 evaluable, "21 evaluable corrupted" (`Discussion.tex:37`), 3 complete-loss vs "two complete-loss" (`Methods.tex:432`) | | "21 corrupted conditions + clean baseline = 22 rows; 9 frame-deletion crashed" |
| D5 | Tone: Abstract "ASF's claims hold only within narrower conditions" vs `Discussion.tex:142` "ASF is mostly robust … a genuine step toward robustness" | | "17/22 conditions robust; one realistic regime not" |
| D6 | Abstract: frame deletion "producing no predictions"; Results: **RuntimeError** in sparse conv on zero-voxel input, camera frame dropped crashes pipeline. A crash is partly a harness/code-path artefact | `Abstract.tex:14` vs `Results.tex:480-482` | "non-graceful failure of the released code path; not an accuracy number" |
| D7 | Cause of noise>absence is hypothesis ("consistent with, but not proof of", `Conclusion.tex:18`); discriminating experiment (LiDAR-only detector under same noise) not run, Alvis access lost (`Discussion.tex:107,118`); zero-fill goes through encoder, not branch exclusion | | "I measured X; two hypotheses fit; could not discriminate" |
| D8 | σ up to 2.0 m exceeds vehicle width (1 m ≈ 48 % of 2.1 m, `Methods.tex:422`); realism conceded (`Discussion.tex:112`) | | stress test, not a sensor model |
| D9 | Seed 42 only, no CIs, N>30 floor instead (`Methods.tex:430,446`), single checkpoint, single dataset (`Discussion.tex:103`) | | concede; cite scale (35 456 objects) and consistency across strata |
| D10 | Only single-modality corruption; joint corruption is future work (`Conclusion.tex:69`) | | |
| D11 | GenAI declaration (`GenAIDeclaration.tex`): LLMs for phrasing and "suggest code improvements, support documentation" → expect "how much code did AI write?" | | be precise |
| D12 | Old `defense_questions.md` quotes σ literature range 0.02–0.12 m and §-numbers from an older `report.md`; current `.tex` doesn't cite that range | `docs/Latex_Report/defense_questions.md` | don't quote it unless re-verified in `references.bib` |

## D. Evidence in resources NOT on the CV
1. **FIDO scale/ownership**: you are first author of a 5-person article; Unitree Go2 + XT-16 LiDAR + RTK GNSS + Jetson + ROS2 + LLM agent. Numbers: RMSE 6.7→1.7 m; STT 92.7 %; best latency 0.485 s (total T = 50.612 s); user study 10 subjects, 9 questions, GPT 31.0 vs Gemini 29.5. Technical depth not on CV: LiDAR–IMU extrinsic t = [0.1710, 0, 0.0908] m, tightly-coupled LIO, heading alignment by linear regression of GNSS track vs odometry yaw, static GNSS covariance calibration, Haversine, coordinated-turn model.
2. **FIDO honest limits** (turn into strengths): 2-D only; indoor/outdoor not fused; RTK covariance mismatch identified with a fix proposed (§V-C1).
3. **SSY345**: derived discrete quaternion process model (F = I + (Δt/2)S(ω), G = (Δt/2)S(q̂)), measurement Jacobians d/dq[Q(q)g₀], two gating schemes, empirical covariances (µ_acc,z = 9.854 m/s²), failure analysis (wrong prior unobservable; acc+mag without gyro unusable). All whiteboard-ready.
4. **SSY191**: Newton–Euler → linearised A/B → discretised (Ts = 0.01 s) → tuned Q = diag(2, 0.3, 2, 0.3, 0.5), R = I₄; hardware failure analysis.
5. **Thesis not on CV**: survivorship bias in mATE/mASE/mAOE (TP population −79.3 % at LiDAR noise high); reproduction gap vs paper; N>30 floor and sequence-confounding flag; ~1 M text files consolidated to one Parquet table (`Methods.tex:526`); critique that ASF availability is manually declared and its camera encoder trained only on normal/overcast.

## E. Contradicted / unbacked CV claims (summary)
Contradicted: C10, C11, C13, C14, C16, C19. Unbacked: C2 (Apptainer), C6–C8, C20. Suggested safe rewording: `08_top_risks.md`.
