# 05 — Fundamentals refresher (whiteboard-level)

Priority order = what your documents show you actually did: **1 EKF + gating, 2 detection metrics/fusion, 3 complementary filter + LQR, 4 point clouds / sensor failure modes, 5 SLURM/containers, 6 ROS2.** This file is general theory (standard textbook results); it is not claimed to come from your documents unless a pointer says so. `R/` = `/home/adhish/Documents/Ady_Resume/resources/`.

Key: `M:`=Methods.tex, `Th:`=Theory.tex under `/home/adhish/Productivity/AMSCUP/docs/Latex_Report/thesis_report/include/`.

## 1. EKF (you did this three times: FIDO, SSY345; LQG appears in FIDO control)

**Model:** xₖ = f(xₖ₋₁, uₖ) + wₖ, wₖ ~ N(0, Q); yₖ = h(xₖ) + eₖ, eₖ ~ N(0, R).

**Predict**
x̂⁻ = f(x̂ₖ₋₁, uₖ);  F = ∂f/∂x |x̂ₖ₋₁;  P⁻ = F P Fᵀ + Q (or G Q Gᵀ if noise enters through G).

**Update**
H = ∂h/∂x |x̂⁻;  ν = y − h(x̂⁻);  S = H P⁻ Hᵀ + R;  K = P⁻ Hᵀ S⁻¹;  x̂ = x̂⁻ + Kν;  P = P⁻ − K S Kᵀ  (Joseph form (I−KH)P(I−KH)ᵀ + KRKᵀ is numerically safer).

**Your Jacobians**
- FIDO CT model, x = [x, y, v, φ, ω]: f = [x + vcosφΔt, y + vsinφΔt, v, φ + ωΔt, ω]. F = I + Δt·[[0,0,cosφ,−v sinφ,0],[0,0,sinφ,v cosφ,0],[0,0,0,0,0],[0,0,0,0,1],[0,0,0,0,0]]. GNSS update: H = [[1,0,0,0,0],[0,1,0,0,0]]. (Model per `R/SSY226…pdf` §III-A3; matrices are my derivation.)
- SSY345 quaternion: F = I + (Δt/2)S(ω), G = (Δt/2)S(q̂); accel H = ∂(Q(q)g₀)/∂q (3×4), mag same with m₀ (`R/SSY345…pdf` Tasks 3, 6, 9). Renormalise q after every step.

**Gating / outliers**
- Innovation gate (Mahalanobis): d² = νᵀS⁻¹ν; reject if d² > χ²_m(p) (m = dim y; m=2, 99 % → 9.21; m=3, 99 % → 11.34).
- Physical-consistency gates (what you actually did, SSY345): accel norm ≈ g; magnetometer norm vs AR(1) tracker L̂ₖ = (1−α)L̂ₖ₋₁ + α‖mₖ‖.
- Robust alternatives: inflate R with innovation (adaptive), Huber/Student-t weighting.

**Consistency tests:** NIS = νᵀS⁻¹ν ~ χ²(m); NEES = (x−x̂)ᵀP⁻¹(x−x̂) ~ χ²(n). Over/under-confident P shows up here.

**Failure modes:** linearisation error (large initial uncertainty — SSY345 wrong initial pose), unmodelled bias (gyro), filter divergence from too-small Q, stale covariance (FIDO RTK drop), asynchronous measurements (apply updates in timestamp order, predict to each timestamp), unobservable states (yaw without magnetometer), non-normalised quaternions.

**EKF vs UKF vs particle:** EKF = first-order, needs Jacobians; UKF = sigma points, no Jacobians, better for strong nonlinearity at ~same cost; PF handles multimodality but costs N particles.

**Whiteboard question:** "derive the Kalman gain" — minimise trace(P⁺) over K: P⁺ = (I−KH)P⁻(I−KH)ᵀ + KRKᵀ; ∂tr/∂K = 0 ⇒ K = P⁻Hᵀ(HP⁻Hᵀ+R)⁻¹.

## 2. Complementary filter (SSY191)
Continuous: θ̂ = LP(s)·θ_acc + HP(s)·∫ω, LP = 1/(αs+1), HP = αs/(αs+1) (sums to 1). Discrete: θₖ = (1−γ)θ_acc,ₖ + γ(θₖ₋₁ + hωₖ), γ = α/(h+α). Your γ = 0.9, h = 0.01 s ⇒ α = 0.09 s (my arithmetic). Large γ trusts the gyro. Limits: accel measures specific force, so sustained linear acceleration corrupts it; no yaw; fixed gain. Relation to Kalman: steady-state Kalman filter for a 1-state angle model with gyro input has the same structure with gain set by Q/R.

## 3. Discrete LQR (SSY191)
x_{k+1} = A_d x_k + B_d u_k, A_d = e^{ATs}, B_d = ∫₀^{Ts}e^{Aτ}B dτ (zero-order hold). Minimise Σ(xᵀQx + uᵀRu). DARE: P = AᵀPA − AᵀPB(R + BᵀPB)⁻¹BᵀPA + Q; K = (R + BᵀPB)⁻¹BᵀPA; u = −Kx. Needs (A,B) stabilisable, (Q^{1/2},A) detectable. Guarantees (continuous LQR): ≥ 60° phase margin, infinite gain margin upward (state feedback only; lost with an observer — LQG has no guaranteed margins). Tuning: Bryson's rule Qᵢᵢ = 1/(max xᵢ)², Rⱼⱼ = 1/(max uⱼ)². Tracking: add integral state or feedforward N̄. Your values: Q = diag(2, 0.3, 2, 0.3, 0.5), R = I₄, Ts = 0.01 s (`R/SSY191…pdf` §VI).
Why hardware failed (report + general): CoM offset from battery, unmodelled actuator dynamics/latency, no integral trim.

## 4. Sensor fusion levels
| Level | What is combined | Pros | Cons | Example |
|---|---|---|---|---|
| Early (data) | raw points/pixels | max information | needs tight calibration/sync; one bad sensor contaminates | LiDAR points painted with image features |
| Feature / mid | per-sensor feature maps (BEV) | learned, balanced cost | head input shape tied to sensor count (DCF) unless attention-based | BEVFusion, **ASF** (UCP+CASAP) |
| Late (decision) | per-sensor detections | modular, fault-tolerant | discards cross-modal cues, association needed | Kalman/JPDA tracking of detections |
Your thesis: ASF is feature-level (`T/include/ASF.tex`); availability handling = key absent from attention.

## 5. Sensor failure modes
- **Camera:** low light, glare, saturation, motion blur, lens contamination/crack, rain on lens; no direct depth. (Thesis simulates intensity noise σ = 20/50/80, pixel dropout, blackout.)
- **LiDAR:** rain/snow/fog backscatter and attenuation, dust, specular/dark surfaces (low return), sparse at range, window contamination, mutual interference; near-IR, so weather-limited. (Thesis simulates point jitter σ, point dropout, all-zero.)
- **Radar:** low angular resolution (4D improves), multipath/ghost targets, clutter from rain, CFAR thresholding discards information, interference. K-Radar: radar accuracy largely unaffected normal→adverse weather (`Th:76`).
- **GNSS:** multipath, canopy, urban canyon, RTK fix → float → single loss, corrections link drop (FIDO).
- **IMU:** bias drift, scale error, vibration, magnetometer disturbance (SSY345).
- **System-level:** timestamp skew, extrinsic drift, dropped frames (thesis: frame deletion crash).

## 6. Point-cloud processing (Sysenso background; thesis voxelisation)
Downsample (voxel grid) → crop → ground removal (RANSAC plane fit: sample 3 pts, count inliers within τ, N ≥ log(1−p)/log(1−wⁿ)) → clustering (Euclidean/DBSCAN, KD-tree) → feature extraction (PCA normals/extent, intensity). Registration: ICP (point-to-point/plane) converges only from a good initial guess. Detection backbones: voxelisation + sparse 3D conv (SECOND) → collapse height into channels → BEV; PointPillars alternative. Noise: statistical outlier removal (mean k-NN distance > µ + nσ) — a plausible *mitigation* for the thesis's LiDAR-noise finding, untested (**NID**). Library: PCL (CV).

## 7. ROS2 concepts
- **Node** = process unit; **topics** (pub/sub, many-to-many, async), **services** (sync request/response), **actions** (goal/feedback/result, cancellable, long-running — your C++ server/client), **parameters**, **launch files**, `tf2` transforms, ament/colcon build.
- **DDS** middleware (default Fast DDS/Cyclone); discovery over multicast.
- **QoS:** Reliability (RELIABLE vs BEST_EFFORT), Durability (VOLATILE vs TRANSIENT_LOCAL — late joiners get last sample, e.g. static transforms/maps), History (KEEP_LAST depth N), Deadline, Liveliness. Publisher/subscriber must be *compatible* (a RELIABLE sub won't connect to a BEST_EFFORT pub). Sensor streams → `SensorDataQoS` (best-effort, small depth).
- **Multi-camera sync:** hardware trigger best; else `message_filters::ApproximateTimeSynchronizer` with slop; measure skew.
- **Executors/callback groups:** single-threaded default blocks on long callbacks; MultiThreaded + separate callback groups for action servers.
- **Latency measurement:** stamp at capture, compare at consumer; your OpenCV standalone benchmark isolated middleware overhead (CV:52).
(FIDO ran its stack on ROS2 on a Jetson: `R/SSY226…pdf` §II-A.)

## 8. SLURM and containers
- **SLURM:** `sbatch` script with `#SBATCH --array=0-N`, `--gpus-per-node`, `--time`, `--cpus-per-task`, `--mem`; `$SLURM_ARRAY_TASK_ID` selects work item; `squeue`, `scancel`, `sacct`, `seff`; dependencies `--dependency=afterok`. Thesis: one job per sequence on Alvis A40s (`M:511`).
- **Apptainer:** rootless `.sif` images; `apptainer build x.sif def`; `exec --nv` for GPU; `--bind src:dst` for datasets; image immutable ⇒ reproducibility; why not Docker on shared HPC (root daemon).
- **Pipeline design lessons from the thesis:** emit one record per frame, consolidate into Parquet, compute all metrics from one canonical loader (`M:526-527`); crash isolation per task.

## 9. Detection metrics
- IoU = |A∩B|/|A∪B|; TP if IoU ≥ τ (thesis τ = 0.3, K-Radar convention) and class matches, each GT used once, detections sorted by score.
- Precision = TP/(TP+FP); recall = TP/(TP+FN); AP = area under interpolated PR curve (thesis: 41 recall points, `M:448-452`); mAP = mean over classes; nuScenes uses centre-distance matching + mATE/mASE/mAOE/mAVE/mAAE + NDS.
- F1 = 2PR/(P+R) at a fixed score threshold; threshold-dependent unlike AP.
- **Robustness:** retention R = metric_corrupt/metric_clean; mCE (needs reference model); RCE = (clean − corrupt)/clean; CRI as in `M:490-494`.
- **Traps:** TP-only metrics suffer survivorship bias when the TP set shrinks; pooled vs class-mean mAP differ; AP at IoU 0.3 is lenient vs 0.5/0.7 (K-Radar benchmark choice), so don't compare to KITTI numbers.
