# 04 — CV project and role Q&A

Evidence base: `R/` = `/home/adhish/Documents/Ady_Resume/resources/`. Only **FIDO, smartphone EKF, Crazyflie** have documents. For Sysenso/Siemens, Chalmers Industriteknik, ROS2 and SLURM/Apptainer the folder is empty: every answer is **NOT IN DOCUMENTS** — I give the questions to expect, the general-knowledge frame, and the facts **you must supply**. I have invented nothing about those jobs.

---
## 1. FIDO — EKF navigation (SSY226; `R/SSY226_Fido_article_final.pdf`)

**Facts to know cold (all from the article)**
- Platform: Unitree Go2 EDU (12 DoF, onboard Jetson running the ROS2 stack), added XT-16 LiDAR, GNSS module, Wi-Fi, Bluetooth, conference speakerphone, **custom 3D-printed casing** (§II).
- Localisation done in **2D** "due to time constraints" (§III-A).
- Network RTK via Lantmäteriet **Swepos** over Wi-Fi modem (§III-A1).
- Frame alignment: subtract first GNSS and odometry sample; **Haversine** distance → metres; rotation via **linear regression on GNSS track vs odometry yaw** (method after Leanza et al.) (§III-A2).
- EKF: state x = [x, y, v, φ, ω]ᵀ; **coordinated-turn** (CT) model chosen over constant-velocity because heading is coupled to forward motion in curves; update with RTK-GNSS position and IMU rates; asynchronous measurements; static calibration run to estimate **GNSS covariance**; straight-line initialisation run for frame alignment (§III-A3, §IV-A3).
- Offline verification motion primitives: 5 m radius circle; 10 m straight then 90° turn; odometry used as relative baseline (§III-A5a).
- Numbers: GNSS-vs-odometry RMSE **6.7 m (no RTK) → 1.7 m (RTK)**; STT accuracy **92.7 %**; best response latency **0.485 s** (GPT-4o-mini-tts + librosa), total interaction time 50.612 s; user study 10 subjects × 9 questions, GPT 31.0 vs Gemini 29.5 points; LiDAR–IMU extrinsic t = [0.1710, 0, 0.0908] m, R ≈ I.
- Limits stated by the article: indoor/outdoor not fused; EKF "yet to be validated in a real-time deployment"; RTK vs non-RTK covariance mismatch; weather and obstacles untested.

**What you must not claim:** "sub-meter accuracy" (the measured number is 1.7 m and it is not vs ground truth); "outlier rejection under multipath" (not in the article); "live-tested EKF accuracy" (judged visually).

**Q&A**
1. *What did you personally build?* **NOT IN DOCUMENTS** (article lists 5 authors, you first). Decide in advance which of: EKF, heading alignment, RTK, covariance calibration, ROS2 integration, you owned. Say only that.
2. *Write the EKF.* Predict: x⁻ = f(x, Δt) with CT model: x += v cosφ Δt, y += v sinφ Δt, φ += ω Δt, v, ω ≈ constant + process noise; P⁻ = F P Fᵀ + Q with F = ∂f/∂x. Update: y = [x_gnss, y_gnss] (+ ω from IMU); S = H P⁻ Hᵀ + R; K = P⁻ Hᵀ S⁻¹; x = x⁻ + K(y − h(x⁻)); P = (I−KH)P⁻. (Model class from the article; explicit equations written here are standard — general knowledge.)
3. *Why CT, not CV?* Curved maneuvers couple heading and speed on a quadruped; CV can't represent yaw rate (§III-A3).
4. *Why does RTK help, quantitatively?* 6.7 → 1.7 m RMSE vs odometry baseline across trials (§IV-A1). Odometry has scale error, so absolute radius is not trusted (§IV-A1).
5. *Is 1.7 m good enough for sidewalks?* The article itself says meter-level is insufficient for sidewalk following (§I) and that RTK gives "cm-level in favourable conditions"; the 1.7 m is therefore an unresolved gap (likely RTK float vs fixed, covariance, or the odometry baseline's own error — **hypotheses only**, not in the article).
6. *How did you weight GNSS vs odometry?* From measured static GNSS covariance at start of run; weakness: if RTK drops mid-run the covariance is stale; proposal: re-measure and keep separate covariance levels for GNSS vs RTK (§V-C1).
7. *How do you handle outliers?* Honest answer from the article: no explicit gate; weighting via covariance. If asked for design: chi-square gate on innovation, d² = νᵀS⁻¹ν > χ²₂(0.99)=9.21 → reject (general knowledge). Do not say it was implemented unless you did it and can show the code.
8. *Failure modes:* GNSS multipath / loss of RTK fix (urban canyon, trees); heading misalignment (error grows with distance); LiDAR SLAM drift in corridors (mitigated by tightly-coupled LIO per article); stale covariance; time-sync of asynchronous sensors; 2D assumption on slopes.
9. *Why tightly-coupled LIO?* Fuses high-rate IMU with deskewed point clouds; keeps map straight in feature-poor corridors (no ghosting, Fig. 6, qualitative) (§III-A4, §IV-A4).
10. *How was LiDAR extrinsic obtained?* Mechanical measurement, rotation assumed identity ("small residual misalignment may exist") (§III-A4). Trade-off: no calibration optimisation.
11. *LLM agent architecture?* VIM (full-duplex, barge-in) → FIDO Mind (Brain model emits JSON {response, actions}; Reviewer prompt checks rules) → high-level state machine (behaviour selection, indoor/campus navigation) over ROS2 (§III-B). Choice GPT-4.1: best navigation/misleading-question scores and fastest.
12. *Could you evaluate localisation better?* Yes: RTK-fixed static reference points / total station, report EKF RMSE & 95 % CEP vs surveyed truth, NEES/NIS consistency checks (general knowledge).

## 2. Smartphone orientation EKF (SSY345; `R/SSY345_Project_Group_37.pdf`, 2 authors)

**Facts to know cold**
- State = unit quaternion q (4 states), **gyro as input** (u = ω). Rationale: modern gyros are low-noise/high-rate; avoids 7-state [q ω]; faster, easier to tune. Cost: gyro noise enters only via process noise; no bias state → drift (Task 1).
- Process model (Task 3–4): q̇ = ½S(ω+v)q → F(ω) = I + (Δt/2)S(ω), G(q̂) = (Δt/2)S(q̂); x⁺ = F x; P⁺ = F P Fᵀ + G R_ω Gᵀ; renormalise q. First-order Euler of e^{AΔt}.
- Accelerometer update (Task 6): yᵃ = Qᵀ(q)(g₀ + fᵃ) + e; H = ∂[Q(q)g₀]/∂q; assumes **fᵃ = 0**.
- Violation → jerks during horizontal acceleration; fix = gate when ‖a‖ ≠ 9.81 within a threshold (Task 8).
- Magnetometer update (Task 9–11): m₀ = [0, √(mx²+my²), mz]ᵀ; yaw drifts near electronics; fix = AR(1) tracker L̂ₖ = (1−α)L̂ₖ₋₁ + α‖mₖ‖ with threshold; α and threshold tuned by trial and error.
- Empirical sensor stats (Task 2): µ_acc = [0.0286, −0.0547, 9.854]; gyro mean ~10⁻³ rad/s scale, magnetometer µ = [−28.4, −15.4, −63.7] (units as in report, µT presumably — **units not stated**).
- Initial prior x = [1 0 0 0]ᵀ (flat, face up); starting on its side → filter can't recover (initial pose must be right) (Task 5).
- Task 12 RMSE vs app reference (rad), angle1/2/3: all sensors 2.71/0.40/0.34; acc+gyro 2.43/0.39/0.29; gyro+mag 1.14/0.39/0.34; acc+mag 3.51/0.19/0.25 → acc+mag "effectively unusable" for motion. Initial orientations mismatch ⇒ "difficult to directly quantify".

**Q&A**
1. *Derive the discrete quaternion propagation.* q(t_k) = e^{AΔt}q(t_{k−1}), A = ½S(ω); e^{AΔt} ≈ I + AΔt; use S(v)q = S(q)v to move noise; linearise S(q) at q̂ (Task 3).
2. *Why normalise?* The linearisation doesn't preserve ‖q‖ = 1; project back after each update (Task 4, `mu_normalizeQ`). Covariance of a 4-state, 3-DOF rotation is rank-deficient — a standard weakness (general knowledge: MEKF uses a 3-state error).
3. *Why does the accelerometer give only roll/pitch?* Gravity is the only observed direction; yaw rotates about it (general knowledge) — which is why the magnetometer is needed.
4. *Explain your outlier gate.* Accelerometer: accept if ‖a‖ within a band around 9.81 (threshold value **NOT IN DOCUMENTS**). Magnetometer: AR(1) low-pass of ‖m‖ is the expected norm; reject measurements whose norm deviates beyond threshold. Both protect the "no external field/force" assumption — **not** random-spike rejection.
5. *Why is the Angle 1 RMSE 2.7 rad?* The report doesn't diagnose. Candidates (general knowledge): angle-wrap ±π, Euler-convention mismatch or yaw offset vs app reference; initial-orientation offset (report's own explanation). Do not claim the filter is wrong or right — say the comparison was inconclusive.
6. *Did you beat Google's algorithm?* No; the report doesn't claim it. The reference is "the app's" orientation; both struggled. Say "qualitative sensor-combination study".
7. *Why not include gyro bias in state?* Trade-off in Task 1: 7→ bigger state, but better long-term; I chose simplicity. A bias state (3 more) would be the first extension.
8. *EKF vs complementary filter?* EKF gives covariance-weighted, time-varying gain and a principled place for gating; complementary has a fixed gain γ; EKF costs Jacobians and tuning R/Q (general knowledge).
9. *Tuning?* Q/R from measured sensor covariances (Task 2), thresholds by trial and error.

## 3. Crazyflie LQR (SSY191; `R/Project_Report_SSY191_Group_7.pdf`, 4 authors)

**Facts to know cold**
- Crazyflie 2.1: 27 g, 92×92×29 mm, BMI088 IMU, BMP388 pressure.
- Complementary filter: roll φ = atan2(a_y, a_z), pitch θ = atan2(−a_x, √(a_y²+a_z²)); θ_k = (1−γ)θ_acc,k + γ(θ_{k−1} + h·ω_gyro,k), **γ = 0.9**, γ = α/(h+α). With h = 0.01 s ⇒ α = γh/(1−γ) = 0.09 s (**my arithmetic**, not in report; crossover ≈ 1/(2πα) ≈ 1.8 Hz).
- Plant in Simscape: Newton–Euler; T_i = bω_i²; torques with d·cos(π/4) lever arms; gyroscopic term ω×Jω; drag term F_d.
- Linearised about hover (T_Bi = mg/4); states x = [φ, φ̇, θ, θ̇, ψ̇] (**yaw rate only**); inputs ΔT₁..₄.
- Discretisation: A_d = e^{A Ts}, B_d = ∫e^{Aτ}B dτ, **Ts = 0.01 s**; `dlqr(A,B,Q,R)`; K = R⁻¹BᵀP form for continuous; ARE shown.
- Tuned (trial and error): **Q = diag(2, 0.3, 2, 0.3, 0.5), R = I₄**; K rows magnitude ~0.0284, 0.0112, 0.0420, 0.0166, 0.0701.
- Sim: pulse reference on roll/pitch tracked with minimal oscillation; thrust changes small.
- Hardware: roll oscillation, yaw/pitch deviated from zero; suspected battery weight asymmetry; Simulink→C (Embedded Coder / `code.c`) could not be completed; battery depleted unusually fast. **Conclusion in report: sim performance did not transfer; real-world testing not possible.**

**Q&A**
1. *Derive LQR.* min J = ∫(xᵀQx + uᵀRu)dt; u = −Kx, K = R⁻¹BᵀP, AᵀP + PA − PBR⁻¹BᵀP + Q = 0. Discrete: P = AᵀPA − AᵀPB(R + BᵀPB)⁻¹BᵀPA + Q, K = (R + BᵀPB)⁻¹BᵀPA (general knowledge; `dlqr` used).
2. *Effect of Q↑ / R↑?* Q↑ aggressive tracking, risk oscillation; R↑ smoother thrust, sluggish (report §VI).
3. *Why linearise at hover, and where does it break?* Small-angle validity; gradually worse away from operating point (§V).
4. *Is the system controllable?* **NOT IN DOCUMENTS** (not checked in the report). Quick check: rank [B AB A²B …] = 5 — general knowledge. Note A has zero rows; yaw angle not a state.
5. *Why didn't it work on hardware?* Report's own list: battery mass off-centre, unmodelled hardware, couldn't finish C-code port. Add as lessons (general knowledge, mark as such): model mismatch (motor dynamics, thrust-ω² constant, latency), no integral action/trim, sensor bias, sampling jitter.
6. *Robustness claim?* Only reference-pulse/disturbance tests in one simulation; no gain/phase margins, no uncertainty sweep — be honest.
7. *Complementary filter limits?* No yaw correction; gains fixed; fails under sustained acceleration (accelerometer sees specific force not gravity).

## 4. Sysenso Systems → Siemens client site (Jul 2023–Jul 2024) — **NOT IN DOCUMENTS**
CV facts only: semi-automatic road-feature annotation tool; zebra crossings, ground planes, lane markings from 3D LiDAR; "geometric and analytical methods"; Python/C++/PCL/Git/Linux; regular client demos.
**You must prepare, with real numbers:** point-cloud size and sensor; ground-plane method (RANSAC? gradient? — what did you actually use?); how zebra crossings were found (intensity thresholding → clustering → pattern fit?); precision/recall or time saved vs manual annotation; how "semi-automatic" (human correction loop); failure cases (wet road, worn paint, occlusion, slopes); languages split Python vs C++; your role vs team; the Siemens team/project; what shipped.
**General-knowledge frame (label as such):** ground = RANSAC plane or progressive morphological/grid min-height; markings = high-reflectivity (intensity) points on ground; zebra = periodic stripes → cluster, PCA, spacing check; trade-offs: intensity calibration varies with range/angle/sensor; accuracy vs recall; annotation-tool value = review time, not model accuracy.
**Questions to expect:** "How did you evaluate it?", "What broke most?", "What would you do with ML now?", "What was the hardest client feedback?", "Why geometric rather than learned?"
Red flag: CV says you were "client-seconded" — expect "what did Siemens own vs Sysenso?" Prepare confidentiality-safe wording.

## 5. Chalmers Industriteknik — Myo + Meta Quest 3 (Jun–Aug 2025) — **NOT IN DOCUMENTS**
CV facts only: Myo EMG band integrated with Quest 3; "functional real-time sensor-data pipeline"; Unity/C#/Meta XR SDK; hand-pose mapping extended; "core pipeline completed and validated"; orientation and gesture fidelity left as next stage.
**Prepare:** how Myo data reached Unity (Bluetooth LE → PC/phone bridge? SDK?) — Myo is discontinued, so SDK/driver hurdles; sample rate (Myo: 8-channel sEMG ~200 Hz, IMU ~50 Hz — *general knowledge, verify*); latency measured?; what "validated" meant (unit check? user trial?); gesture classification used or not; supervisor named on CV (Morten Kristoffersen) — be ready for reference check; the exact scope of "hand-pose mapping" done.
**Failure modes (general):** EMG electrode shift/skin impedance, sweat, calibration per user, cross-talk, IMU drift limiting orientation fidelity (matches CV's "orientation fidelity next-stage"), BLE packet loss/jitter, clock sync between Myo and Quest.

## 6. ROS2 pipelines (Jul–Aug 2023, personal) — **NOT IN DOCUMENTS**
CV facts only: dual-camera synchronized capture nodes (C++/Python), ament packages + launch files, custom msg/srv, **action server/client in C++** with feedback and cancellation, OpenCV standalone benchmarks isolating pipeline vs middleware overhead.
**Prepare:** which cameras; how you synchronised (hardware trigger vs `message_filters::ApproximateTime`); measured numbers (fps, latency per stage, ROS2 overhead %); DDS/QoS settings used; repo link (github.com/AdyuthHisham on CV) — interviewers will open it; resolve the date/location overlap with Sysenso (audit C8). See `05_fundamentals_refresher.md` §ROS2.

## 7. SLURM / Apptainer HPC (thesis infrastructure)
**In documents:** Alvis, A40 ×4 per node (48 GB), 2×32-core Xeon Gold 6338, 256 GiB; SLURM array jobs on `alvis` partition, **one job per sequence**; ~10⁶ output text files → Parquet; metrics computed locally (`M:511-531`); access lost after sweep (`D:118`).
**NOT IN DOCUMENTS:** Apptainer image definition, bind mounts, job script, array size, walltime, GPU-hours, failed-job handling, dependency pinning.
**General frame:** Apptainer (ex-Singularity) = rootless HPC containers from a `.sif`; `apptainer exec --nv` exposes the NVIDIA driver; bind `/mimer` data paths; why not Docker: no root daemon on shared clusters. SLURM: `#SBATCH --array=0-57`, `--gpus-per-node=A40:1`, `--time`, `%A_%a` logs; check with `sacct`, `seff`. Trade-offs: many small jobs → scheduling overhead vs simple fault isolation (a crash on one sequence — e.g. the frame-deletion RuntimeError — kills one task not the sweep). Prepare your real script before the interview.
