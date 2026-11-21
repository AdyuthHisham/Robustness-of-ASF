# 04 — CV project and role Q&A

**Basis and limits.** The only document I have for these projects is the CV (a few bullets each). There is no report, code or data for them in the inputs. So:
- Facts below come from the CV. Anything else is labelled **GENERAL KNOWLEDGE** (correct engineering, not your experience) or **[YOU SUPPLY]** (a fact only you know).
- **Numbers you should know cold: the CV contains exactly one** — "sub-meter positional accuracy" (FIDO). For every other project the CV has no metric. Before the interview, write down for each: dataset/size, metric, result, your contribution. I have not invented any.
- Answer template for anything numeric: *what was measured → against what reference → how many trials → result → what it does not show.*

---

## 1. Sysenso Systems → Siemens client site (Jul 2023–Jul 2024) — LiDAR road-feature annotation tool

**CV claims (CV:20-25):** semi-automatic road-feature annotation tool; zebra crossings, ground planes, lane markings from 3D LiDAR point clouds using geometric/analytical methods; regular client demos; Python, C++, PCL.

**Numbers to know cold [YOU SUPPLY — none on CV]:** points per frame / sensor model; detection recall/precision per feature (or manual-correction rate); annotation time per km or per frame before vs after; frames/km processed; latency per frame.

**Likely questions and model answers**

1. *Walk me through the pipeline.* Template (**GENERAL KNOWLEDGE**; edit to what you did): load cloud → crop ROI → ground segmentation (RANSAC plane fit or progressive morphological/grid-based) → intensity thresholding on ground points (retro-reflective paint has higher intensity) → clustering/connected components → geometric fit (parallel stripes of known width/spacing for zebra; polyline fitting for lanes) → export to map format → human review ("semi-automatic").
2. *Why geometric methods and not a learned model?* Defensible reasons: no labelled data at the start, interpretability, deterministic behaviour for annotation QA, client acceptance. Cost: brittle to worn paint, rain/wet reflectivity, sparse returns at range, slopes. [YOU SUPPLY: what you actually decided.]
3. *Ground plane in a non-flat road?* Single global RANSAC plane fails on crowns/slopes/ramps; use local/grid plane fits or piecewise models (**GENERAL KNOWLEDGE**).
4. *Failure modes.* Faded/occluded paint, other vehicles occluding the ground, intensity differences between sensors/range, motion distortion without deskewing, sparse far-range points, wet roads reducing reflectance, mis-calibration between LiDAR and ego frame. Mitigation = intensity normalisation by range, accumulate multiple scans with pose, review UI.
5. *How did you validate it?* [YOU SUPPLY: against what ground truth? manual labels? how many frames?]. If no formal validation, say so and say how client feedback served as acceptance.
6. *What does "semi-automatic" mean?* Automatic proposals + human correction; the measure of success is reduction in human effort, not raw precision. [YOU SUPPLY the effort reduction.]
7. *Client demos — what feedback changed the design?* [YOU SUPPLY one concrete example.] Consulting relevance: this is the closest evidence you have of working inside a client team (secondment).
8. *C++ vs Python split?* [YOU SUPPLY.] Typical: PCL in C++ for heavy geometry, Python for glue/visualisation.
9. *Trade-offs you made.* Speed vs accuracy; tuning thresholds per scene vs generalising; false positives cost review time, false negatives cost missing map features.

**Weak spot:** CV says "effectively extracting map-relevant road features" with no evidence. Prepare one concrete before/after.

---

## 2. Chalmers Industriteknik (Jun–Aug 2025) — Myo EMG band + Meta Quest 3

**CV claims (CV:27-32):** integrated Myo EMG armband with Quest 3, real-time sensor-data pipeline for a virtual prosthetic-rehabilitation prototype; hand-pose mapping in Unity; "core sensor-to-headset pipeline completed and validated, orientation and gesture fidelity scoped as next-stage."

**Facts I can state about Myo (GENERAL KNOWLEDGE, verify):** 8-channel surface EMG, ~200 Hz, plus a 9-axis IMU (~50 Hz); onboard gesture classifier for five poses; Bluetooth LE; the Myo was discontinued by Thalmic/North and has no official SDK support — a real risk for any product. [YOU SUPPLY how you actually received data: SDK/bridge/phone/PC.]

**Numbers to know cold [YOU SUPPLY]:** sample rate, end-to-end latency (EMG → headset display), packet loss, number of gestures, accuracy of "validated".

**Questions**

1. *What did "validated" mean?* [YOU SUPPLY. Be precise: functional test vs measured latency vs user test.] Do not imply clinical validation.
2. *Latency budget?* GENERAL KNOWLEDGE: for VR, motion-to-photon below ~20 ms is the comfort target; EMG itself leads movement by ~30–100 ms electromechanical delay; BLE adds 7.5–30 ms+ connection interval. Know where yours sat.
3. *Why was orientation fidelity left for later?* Myo IMU orientation drifts in yaw (no absolute heading reference without calibration); mapping to Quest's world frame needs alignment/calibration (**GENERAL KNOWLEDGE**). Honest framing: you scoped risk, shipped the core.
4. *EMG failure modes.* Electrode shift, sweat/impedance drift, fatigue, arm-position dependence of classification, crosstalk, motion artefacts; need per-user calibration.
5. *Unity/C# threading.* Sensor callbacks vs main thread; use thread-safe queues; avoid blocking `Update`. [YOU SUPPLY what you did.]
6. *What would you do next?* Calibration routine, filtering/EMG feature extraction (RMS, MAV, etc.), sensor-fusion of IMU + Quest hand tracking, user testing.

---

## 3. ROS2 camera perception & robotics learning pipelines (personal)

**CV claims (CV:48-54):** synchronised dual-camera capture nodes (C++/Python), ament packages + launch files, custom msg/srv interfaces, action server/client with feedback and cancellation, OpenCV C++ programs for capture and processing-time benchmarking isolating pipeline cost from ROS2 overhead.

**Inconsistency to resolve first:** the CV dates this Jul 2023–Jul 2024 and locates it in Gothenburg, but the same dates put you at Sysenso in Chennai; Chalmers starts Sep 2024. Decide the true dates/location and fix the CV. Be ready: "Was this one project or several? Where were you?"

**Numbers to know cold [YOU SUPPLY]:** camera model(s), resolution, fps, measured sync error between the two cameras, processing time per frame (standalone OpenCV vs via ROS2), ROS2 distro (Humble/Iron/…).

**Questions**

1. *How did you synchronise two cameras?* Options: hardware trigger (best, µs), software timestamp matching with `message_filters` (`ApproximateTimeSynchronizer`, tolerance `slop`), or a single node capturing both (shared clock). [YOU SUPPLY which.] Know the failure: approximate sync hides skew; with moving scenes it matters.
2. *What did your benchmark show about ROS2 overhead?* [YOU SUPPLY the numbers.] GENERAL KNOWLEDGE: overhead comes from serialization/copies and DDS; large images over default QoS and without intra-process comms cost copies; use `image_transport`, composable nodes with intra-process comms, loaned messages, and shared-memory DDS to cut it.
3. *Topic vs service vs action?* Topic = streaming, many-to-many; service = synchronous request/reply, short; action = long-running goal with feedback, result and cancellation (built on topics+services).
4. *Why an action for your task?* Asynchronous, preemptible, with progress feedback; a service would block. [YOU SUPPLY the task.]
5. *QoS choices?* Sensor data: `SensorDataQoS` (best-effort, volatile, small depth) so a slow subscriber doesn't stall; commands/state: reliable. Mismatched QoS (reliable subscriber to best-effort publisher) = no connection.
6. *Executors/callback groups?* Single-threaded executor serialises callbacks; a long image callback blocks timers; use multi-threaded executor + separate callback groups (`MutuallyExclusive` vs `Reentrant`).
7. *Why C++ over Python for the capture node?* Lower per-frame overhead, no GIL, deterministic timing; Python fine for prototyping.
8. *What does this not show?* No robot deployment is stated on the CV; it's a pipeline/learning project.

---

## 4. FIDO — EKF for an autonomous robot dog (course design project)

**CV claims (CV:56-61):** EKF fusing GNSS/RTK + IMU, "sub-meter positional accuracy in live tests on a campus robot dog", outlier rejection in the measurement-update step, "stable localization under GPS multipath".

**Numbers to know cold [YOU SUPPLY]:** state vector and dimension, IMU rate, GNSS rate, RTK fix type availability (fixed vs float), test route length, reference used to claim "sub-meter" (RTK ground truth? surveyed points? loop closure error?), the metric (RMSE? CEP? max error?), the gating threshold, process/measurement noise values, number of runs.

**"Sub-meter" is the first question.** Without an independent reference, "sub-meter" can only be a consistency claim (filter covariance), not accuracy. Decide what you can honestly claim.

**Questions**

1. *State vector & models.* Typical: position (N,E[,D]), velocity, heading (and biases). Prediction by IMU integration (strapdown or simplified unicycle/kinematic model); update by GNSS position (and velocity/heading if available). [YOU SUPPLY yours.]
2. *Why EKF not KF/UKF?* Non-linear process (heading enters through rotation); EKF linearises via Jacobian F = ∂f/∂x. UKF avoids Jacobians, costs more; for mild nonlinearity EKF is adequate (details in 05).
3. *How did your outlier rejection work?* Mahalanobis gating on the innovation: d² = νᵀS⁻¹ν, S = HPHᵀ+R; reject if d² > χ²_{k,α} (e.g. k=2, α=0.99 → 9.21). [YOU SUPPLY threshold and what you did with rejected fixes.] Failure mode: filter divergence → covariance shrinks, valid fixes get gated out forever; mitigation = inflate P / reset after N consecutive rejections.
4. *Why does multipath hurt?* Reflected signals bias pseudo-range/carrier phase → jumps of metres, usually positively correlated over seconds; gating handles jumps, not slow bias. RTK float vs fixed status flags indicate quality.
5. *How did you tune Q and R?* Use sensor datasheets for R and IMU noise densities for Q; check innovation whiteness and NIS/NEES consistency. [YOU SUPPLY what you did.]
6. *Observability.* Heading is weakly observable at standstill from position-only updates; yaw drift without magnetometer/motion. 
7. *Timing and latency.* GNSS measurement delay vs IMU timestamps; handle out-of-sequence measurements or buffer/rewind.
8. *What fails on a legged robot?* Vibration/gait noise on IMU, foot-slip not modelled; leg odometry would help (**GENERAL KNOWLEDGE**). [YOU SUPPLY if used.]
9. *Language/runtime.* Python; real-time constraints? [YOU SUPPLY rate achieved.]

---

## 5. Real-time orientation from smartphone IMU (course)

**CV claims (CV:63-68):** EKF for "6-DOF orientation" from accelerometer + gyroscope with outlier handling; benchmarked vs Google's proprietary fusion across sensor configurations.

**Correct the framing before they do:** accel+gyro yield 3-DOF *orientation* (roll, pitch, yaw). Yaw is unobservable from gravity alone → drifts. "6-DOF" may mean the six sensor axes; say "orientation (3 rotational DOF) from 6 sensor axes".

**Numbers to know cold [YOU SUPPLY]:** device model, sample rates, metrics vs Google (angle RMSE? relative to what reference?), configurations compared (e.g., gyro only, accel+gyro, +magnetometer), best configuration.

**Questions**

1. *State and error representation.* Quaternion state with multiplicative error (3-parameter error state) avoids singular covariance of the 4-dim quaternion; renormalise after update (**GENERAL KNOWLEDGE**). [YOU SUPPLY yours.]
2. *Measurement model for accel.* In quasi-static conditions accel ≈ gravity in body frame: h(q) = Rᵀ(q)·[0,0,g]ᵀ; linear acceleration violates it → gate or inflate R when |‖a‖−g| is large (outlier handling).
3. *Why does yaw drift and what fixes it?* No absolute heading; add magnetometer (distorted indoors) or visual/other references.
4. *Gyro bias.* Estimate as states; stationary detection helps.
5. *How did you benchmark vs Google's?* Android rotation-vector sensor fuses accel/gyro/mag proprietary; metric and reference needed. [YOU SUPPLY]. Pitfall: comparing to a proprietary output as "truth" measures agreement, not accuracy.
6. *Outlier handling — what spikes?* Linear acceleration during motion, shocks, gyro saturation.
7. *EKF vs complementary filter vs Madgwick/Mahony?* Complementary: fixed-gain, cheap, easy tuning, no covariance. EKF: time-varying gain, uncertainty, principled gating, cost and tuning burden. (05)

---

## 6. Crazyflie quadrotor — modelling and control (course)

**CV claims (CV:70-75):** discrete-time LQR for roll/pitch/yaw, complementary filter for attitude from raw IMU, full dynamics in Simscape/Simulink, validated robustness against simulated disturbances, "establishing a simulation-to-hardware deployment framework."

**Numbers to know cold [YOU SUPPLY]:** sample time, state vector, Q/R weights and rationale, step-response metrics (rise time, overshoot, settling), disturbance magnitude and recovery, complementary filter gain/time constant, whether anything flew.

**Be precise on "framework":** if no flight took place, say "I built the model, controller and a path to deployment; it was validated in simulation." The CV's "establishing" invites "did it fly?".

**Questions**

1. *Why LQR?* Multi-state optimal feedback, systematic trade of state error vs control effort, guaranteed stability margins for the ideal linear model (continuous LQR: ≥60° phase margin, infinite gain margin upwards; **not guaranteed for discrete, delayed, or estimated-state systems**).
2. *Linearisation point.* Hover; attitude small-angle dynamics decouple roll/pitch/yaw rate loops. Validity breaks at large angles.
3. *How did you pick Q and R?* Bryson's rule (1/max-acceptable²); iterate by simulation. [YOU SUPPLY.]
4. *Discretisation.* Zero-order hold; solve the DARE for P, K = (R+BᵀPB)⁻¹BᵀPA. Sample rate vs unmodelled actuator delay.
5. *Complementary filter vs attitude from raw IMU.* Gyro integrated (high-pass) + accel tilt (low-pass): θ̂ = α(θ̂+ω dt) + (1−α)θ_acc; α = τ/(τ+dt). Accel only constrains roll/pitch; yaw drifts.
6. *Simulation-to-hardware gaps.* Motor dynamics/saturation, battery sag, latency, IMU noise/bias, unmodelled aerodynamics (ground effect, blade flapping), actuator limits (anti-windup).
7. *Integral action?* LQR as stated is a regulator; steady-state error from model mismatch needs integral augmentation (LQI).
8. *Disturbance test design.* [YOU SUPPLY.]

---

## 7. SLURM / Apptainer HPC (thesis infrastructure; CV:40, CV:105)

**What the thesis supports:** SLURM array jobs, one job per sequence, A40 GPUs (4/node, 48 GB), Alvis `alvis` partition, ~1M text output files consolidated into Parquet before leaving the cluster (`Meth:511,526`). **Apptainer is not in the thesis** — you must answer from experience. **Numbers [YOU SUPPLY]:** jobs submitted, wall-clock per job, GPU-hours, failure/resubmission rate.

**Questions**

1. *Why one job per sequence?* Embarrassingly parallel across sequences, bounded runtime per job, fault isolation (a crash loses one sequence), fits the scheduler. Downside: scheduler overhead for tiny jobs, I/O contention.
2. *Why Apptainer?* Reproducible environment, no root, works on HPC where Docker daemon isn't allowed; `apptainer exec --nv` exposes the host NVIDIA driver; bind mounts for datasets (**GENERAL KNOWLEDGE**).
3. *Million small files — problem?* Parallel file systems handle metadata poorly; you consolidated to Parquet (thesis says so) — good. Avoid writing to home; use node-local scratch (`$TMPDIR`) and copy out.
4. *How did you handle failures?* Sequences with crashes (frame deletion) → excluded conditions. Job arrays make resubmission selective: `sbatch --array=<failed ids>`.
5. *Reproducibility.* Fixed seed 42, deterministic wrapper, fixed checkpoint. Hardware differs from the paper's (RTX 3090 vs A40) — GPU nondeterminism magnitude not measured (commented text).
6. *Resource requests.* `--gpus-per-node`, `--time`, `--cpus-per-task`; over-requesting hurts queue priority; profile first.
7. *What happened when you lost access?* No further experiments possible (`Disc:118`) — own it; local copies of predictions were kept for analysis.

---

## 8. Roles and extracurriculars (likely behavioural)

- **Hackathon, first prize, Noctis Bank (CV:86-88).** Know: team size, your role, stack, how "gamified sustainable spending" worked, what you shipped in the time box. Prototype, not a product. This is your only finance-adjacent item; be ready to talk about it for 2 minutes.
- **CIRC International Student Guide 2025; TEDxPSGTech Tech Coordinator 2021; Rotary Club chair 2021** — prepare one concrete story each (conflict, deadline, ownership). Consultants are screened for stakeholder handling.
- **Skills section:** "SLAM-adjacent", "Docker", "PyTorch": expect "which SLAM? did you train a model?". The honest answer for PyTorch from the thesis: inference only with the released ASF code; no training (`Meth:5`).
