# 05 — Fundamentals refresher (whiteboard-level)

All **GENERAL KNOWLEDGE** unless a thesis pointer is given. Verify any constant before quoting it as authoritative.

---

## 1. Extended Kalman Filter

**Model.** x_k = f(x_{k−1}, u_k) + w, w~N(0,Q); z_k = h(x_k) + v, v~N(0,R).

**Predict.**
x̂⁻ = f(x̂, u)
P⁻ = F P Fᵀ + Q, F = ∂f/∂x |_{x̂}   (and Q mapped through noise Jacobian L Qc Lᵀ if noise enters non-additively)

**Update.**
ν = z − h(x̂⁻) (innovation)
S = H P⁻ Hᵀ + R, H = ∂h/∂x |_{x̂⁻}
K = P⁻ Hᵀ S⁻¹
x̂ = x̂⁻ + Kν
P = (I − KH)P⁻ — prefer Joseph form P = (I−KH)P⁻(I−KH)ᵀ + KRKᵀ for numerical symmetry/PSD.

**Why "extended".** KF is optimal only for linear-Gaussian. EKF linearises around the current estimate; error grows when nonlinearity is strong or the estimate is far off (inconsistency, divergence). UKF uses sigma points (no Jacobians, 2nd-order accurate mean); Iterated EKF re-linearises in the update.

**Jacobian examples.**
- Unicycle: x=[px,py,θ,v]; f: px+=v cosθ dt, py+=v sinθ dt → F has ∂px/∂θ = −v sinθ dt, ∂px/∂v = cosθ dt, ∂py/∂θ = v cosθ dt, ∂py/∂v = sinθ dt.
- GNSS position update: h(x)=[px,py] → H=[I₂ 0].
- Accelerometer gravity update for quaternion q: h(q) = R(q)ᵀ g; H = ∂h/∂δθ (error-state form).

**Outlier gating.** NIS = νᵀS⁻¹ν ~ χ²_m (m = measurement dimension). Reject if NIS > threshold. χ² 99%: m=1 → 6.63, m=2 → 9.21, m=3 → 11.34; 95%: 3.84 / 5.99 / 7.81. Failure mode: rejecting everything after divergence — fix with covariance inflation, forced reset after N consecutive rejections, or robust (Huber) weighting instead of hard gate.

**Consistency checks.** NEES (needs ground truth) and NIS averaged over time should sit inside χ² bounds; innovations should be zero-mean white. Tune Q by raising it when NIS is chronically high.

**Observability.** Yaw not observable from gravity or position-only updates at standstill; position biases not observable without references. Unobservable states' covariance grows without bound.

**Typical pitfalls.** Wrong angle wraparound in innovations; quaternion normalisation; asynchronous measurements (use timestamps; propagate to measurement time); delayed GNSS; non-positive-definite P.

## 2. Complementary filter

Low-pass accel-derived tilt + high-pass integrated gyro:
θ̂_k = α(θ̂_{k−1} + ω_k Δt) + (1−α) θ_acc,k, α = τ/(τ+Δt).
τ = crossover time constant (e.g. 0.5–2 s). Accel only gives roll/pitch; yaw drifts unless magnetometer/other reference. No covariance, no gating (add a ‖a‖≈g check). Madgwick/Mahony are gradient-descent / PI-on-error nonlinear complementary filters on quaternions. Versus EKF: cheaper, fewer tuning knobs, no uncertainty; EKF handles time-varying noise and multiple sensor types more rigorously.

## 3. Discrete LQR

Plant x_{k+1} = A x_k + B u_k. Minimise J = Σ (xᵀQx + uᵀRu) (Q ⪰ 0, R ≻ 0).
Solve DARE: P = Q + AᵀPA − AᵀPB(R + BᵀPB)⁻¹BᵀPA.
Gain K = (R + BᵀPB)⁻¹ BᵀPA, u_k = −K x_k.
Requirements: (A,B) stabilisable, (Q^{1/2},A) detectable. Discretise continuous model with ZOH: A_d = e^{AT}, B_d = ∫e^{Aτ}dτ B. Q/R selection: Bryson's rule Q_ii = 1/(max x_i)², R_jj = 1/(max u_j)².
Practicalities: LQR has no integral action → augment with ∫(r−y) (LQI); use anti-windup with saturation; with estimator in the loop the separation principle holds for LQG in the linear case but margins can collapse; delay/actuator lag erode the ideal-LQR margins.

## 4. Sensor fusion levels

| Level | What is fused | Pros | Cons |
|---|---|---|---|
| Early (data) | raw data (points to image pixels, etc.) | max information | requires tight calibration/time sync; sensitive to any sensor failure; heavy |
| Feature (mid) | learned features (e.g. BEV maps) | good accuracy/cost, can handle some missing modalities by design | architecture couples to sensor set unless designed otherwise (ASF's UCP/CASAP) |
| Late (decision/track) | per-sensor detections/tracks | modular, fault-tolerant, interpretable (Kalman + association) | loses cross-modal cues; association errors |

Thesis tie-in: ASF = feature-level; BEVFusion = feature-level BEV; MV2DFusion = proposal-level (`Theory:66`; taxonomy text in `Theory` is inside `\iffalse`, so not in the compiled thesis).

## 5. Sensor failure modes

| Sensor | Typical failures |
|---|---|
| Camera | low light/night, glare, fog/rain/lens droplets, motion blur, rolling shutter, exposure saturation, loss of depth scale (monocular); semantic strength, weak geometry |
| LiDAR | rain/snow/fog scattering and false returns, low-reflectivity surfaces, range-dependent sparsity, cross-talk, motion distortion, window contamination; precise geometry, weather-sensitive (`Theory:76`) |
| Radar | low angular resolution, multipath/ghost targets, clutter, limited elevation (4D radar improves), RCS-dependent detection, Doppler ambiguity; robust to weather and light (`Theory:17,76`) |
| IMU | bias drift, scale error, vibration, temperature; integration drift quadratic in position |
| GNSS | multipath, urban canyons, ionospheric/tropospheric error, RTK fixed↔float transitions, jamming/spoofing |

K-Radar facts you can cite: 4D radar RETINA-4ST 77–81 GHz, range 118 m @ 0.46 m, 107° azimuth × 37° elevation (`Meth:50-57`).

## 6. Point cloud processing

- **Voxel-grid downsampling:** bin points into cubes, keep centroid → uniform density, speeds later steps.
- **Ground segmentation:** RANSAC plane (sample 3 points, count inliers within τ; N ≈ log(1−p)/log(1−w³) iterations); for non-planar roads, grid/ring-wise local fits or Patchwork-style methods.
- **Clustering:** Euclidean (KD-tree), DBSCAN (ε, minPts), connected components on a range image.
- **Registration:** ICP (point-to-point / point-to-plane), requires good initialisation; NDT is smoother; local minima.
- **Intensity:** retro-reflective markings stand out → thresholding on ground points for lane/zebra extraction (needs range/incidence normalisation).
- **Representations for learning:** point-based (PointNet++), voxel + sparse 3D conv (SECOND, used for ASF's LiDAR `ASF:64`), pillar (PointPillars), range-image. Sparse conv skips empty voxels; empty input breaks it (thesis frame-deletion crash `Res:482`).
- **Noise sensitivity:** σ ≳ voxel size scatters points across voxels, destroying local structure (thesis cites registration loss under σ=0.05 m, `Disc:107`).

## 7. ROS2 concepts

- **Node:** process-level unit; communicates via DDS. **Topics** (pub/sub streaming), **services** (sync RPC, short), **actions** (goal/feedback/result, cancellable; built on topics+services), **parameters** (per-node runtime config), **launch files** (Python/XML/YAML composition), **ament** build (ament_cmake/ament_python via `colcon`).
- **QoS:** reliability (reliable/best-effort), durability (volatile/transient-local), history (keep-last N/keep-all), depth, deadline/lifespan/liveliness. Publisher/subscriber must be *compatible* (a reliable subscriber won't connect to a best-effort publisher). `SensorDataQoS` = best-effort, volatile, small depth.
- **Executors & callback groups:** single-threaded executor serialises callbacks (long callback blocks timers); multi-threaded executor + `MutuallyExclusive`/`Reentrant` groups.
- **Composition / intra-process comms:** nodes in one process pass pointers; avoids serialization.
- **Time:** `use_sim_time`, clock topics; `message_filters` ExactTime/ApproximateTime for sync (slop).
- **tf2:** transform tree with timestamps.
- **Lifecycle nodes:** unconfigured→inactive→active, deterministic bring-up.

## 8. SLURM and containers

- `sbatch` (batch), `srun` (launch step), `salloc` (interactive), `squeue/sacct/scancel`.
- Resources: `--gpus-per-node=A40:1`, `--cpus-per-task`, `--mem`, `--time`, `--partition`, `-A project`.
- **Job arrays:** `--array=0-57%10` one task per index (`$SLURM_ARRAY_TASK_ID`), `%10` caps concurrency. Thesis: one job per sequence (`Meth:511`).
- Dependencies: `--dependency=afterok:<id>`.
- **Apptainer (ex-Singularity):** rootless container as a single SIF file; `apptainer exec --nv image.sif cmd` exposes host NVIDIA GPU libs; `--bind /data:/data`; build from Docker image; reproducible but SIF images are immutable. Docker typically unavailable on shared HPC due to daemon/root.
- I/O: avoid millions of small files on the parallel FS; use node-local `$TMPDIR`, archive, or Parquet (thesis consolidated ~1M text files into one Parquet table, `Meth:526`).

## 9. Detection metrics

- **IoU** = |A∩B|/|A∪B| (3D box IoU or BEV IoU). A prediction is TP if IoU ≥ threshold and class matches and GT not already matched; else FP; unmatched GT = FN.
- **Precision** = TP/(TP+FP); **Recall** = TP/(TP+FN); **F1** = 2PR/(P+R).
- **AP** = area under the precision–recall curve; this thesis: 41-point interpolated, IoU 0.3 (`Meth:448-450`). VOC uses 11/all points; COCO 101 points over IoU 0.5:0.95. **mAP** = mean over classes (the thesis's pooled "mAP" is object-pooled, see 01 D1/D2).
- **nuScenes-style TP errors:** ATE (centre distance), ASE (1−IoU after aligning centre/orientation), AOE (yaw error, wrapped); computed over TPs only → survivorship bias (`Disc:13-23`).
- **Retention** Rb = metric_corrupted / metric_clean; **mCE/RCE** baseline-relative forms.
- **Why IoU 0.3?** K-Radar's official convention (`Meth:448`); lenient vs 0.5/0.7.
- Calibration: AP is threshold-free; F1 is operating-point-dependent.

## 10. Quick derivations to practise on a whiteboard
1. EKF update from the minimum-variance argument: K = P Hᵀ (H P Hᵀ + R)⁻¹.
2. Discrete LQR via DP: V_k(x) = xᵀP_k x ⇒ Riccati recursion → DARE as k→∞.
3. Complementary filter α from time constant.
4. Mahalanobis gate from χ² quantiles.
5. CRI on pooled LiDAR noise: mean AP (69.59,18.54,17.45) = 35.19; /73.99 = 0.476; pstdev ≈ 24.3; ln(1+24.3)+1 = 4.23; CRI ≈ 0.112.
6. F1 from TP/FP/FN: 27,169 / 4,900 / 8,287 → P 0.847, R 0.766, F1 0.805.
