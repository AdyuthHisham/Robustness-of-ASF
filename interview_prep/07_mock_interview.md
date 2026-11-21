# 07 — Mock technical interview (25 questions, escalating)

Model answers use only documented facts; `[YOU]` marks a fact only you can supply. Pointers: `T/`=`/home/adhish/Productivity/AMSCUP/docs/Latex_Report/thesis_report/`, `R/`=`/home/adhish/Documents/Ady_Resume/resources/`. Deeper detail: `03`, `04`, `05`.

## Warm-up (1–5)

**1. Walk me through your CV in 90 seconds.**
Chalmers MSc Systems, Control & Mechatronics (Sep 2024–2026); before that a year at Sysenso on a Siemens site building a LiDAR road-feature annotation tool [YOU: one result]; a summer at Chalmers Industriteknik wiring a Myo EMG band into a Quest 3 prototype; course projects on EKF navigation (FIDO), orientation EKF, Crazyflie LQR; thesis on robustness of a three-sensor fusion detector. Thread: estimation and perception under imperfect sensors.
*Probe:* "Which of these would you redo?" → Crazyflie hardware port (`R/SSY191…pdf` §VIII).

**2. Thesis in 30 seconds.** Use `02_thesis_pitch.md`.
*Probe:* "Isn't that just ablation?" → Ablation removes a sensor; I also corrupt it in place; the finding is the gap between those.

**3. What is sensor fusion and why do it?** Sensors fail under disjoint conditions (camera: light; LiDAR: weather; radar: resolution) so combining them keeps accuracy over more conditions (`Th:9,64`). Levels: early/feature/late (`05` §4).
*Probe:* "Where is ASF?" → feature level.

**4. What is an EKF in one minute?** Linearise f and h at the current estimate; predict mean and covariance, update with Kalman gain K = P⁻Hᵀ(HP⁻Hᵀ+R)⁻¹. Used in FIDO (CT model) and SSY345 (quaternion).
*Probe:* "When does it fail?" → large linearisation error, wrong prior (your phone-on-its-side test), stale covariance.

**5. Your biggest failure?** Crazyflie hardware: sim tracked pulses, hardware oscillated in roll, C-code port not finished, battery issue (`R/SSY191…pdf` §VIII–IX). Lesson: validate the plant model against hardware before tuning the controller.
*Probe:* "What would you check first?" → CoM offset and thrust-ω² constant; then latency; then add integral action.

## Core technical (6–12)

**6. Why does your FIDO EKF use a coordinated-turn model?** Heading and speed are coupled in curves on a quadruped; CV can't represent yaw rate (`R/SSY226…pdf` §III-A3).
*Probe:* "Give me F." → `05` §1.

**7. How accurate was FIDO's localisation?** Measured: GNSS RMSE vs odometry baseline 6.7 m → 1.7 m with RTK. The EKF output itself was judged visually (straight, circle, L-shape); no ground-truth accuracy. Don't say sub-meter.
*Probe:* "So why did the CV say sub-meter?" → Don't defend; correct it: "That line overstated; the measured figure is 1.7 m against odometry, and I'd rewrite it."

**8. Explain your accelerometer and magnetometer gating.** Accelerometer update assumes only gravity, so reject when ‖a‖ deviates from 9.81; magnetometer tracks expected norm with AR(1) and rejects deviations (e.g. near electronics) (`R/SSY345…pdf` Tasks 8, 11).
*Probe:* "Threshold values?" → [YOU] (not in the report; tuned empirically).

**9. Derive discrete LQR and describe your tuning.** `05` §3. Q = diag(2, 0.3, 2, 0.3, 0.5), R = I₄, Ts = 0.01 s, trial and error.
*Probe:* "Is yaw angle controlled?" → No, yaw rate only; the CV line says "yaw stabilization" and should say yaw-rate.

**10. How does ASF handle a missing sensor?** UCP maps each sensor's patch to a common C_u vector; CASAP attends only over present sensors; missing = key absent; output shape fixed; trained over 7 subsets (SCL) (`T/include/ASF.tex:57-103`). Availability is a manual external dictionary.
*Probe:* "Does the network detect failure?" → No (`Methods.tex:23`).

**11. What are AP, F1, retention, CRI?** `03` Q24–27. Quote formulas.
*Probe:* "Critique CRI." → three tiers, log term mixes units, single-tier conditions undefined.

**12. Describe your corruption design.** `03` Q5–6. 4 effects × 3 modalities × 3 severities; σ = 0.1/1.0/2.0 m; f = 0.1/0.3/0.7; N = 19/5/2; seed 42; inference-time between loader and model.
*Probe:* "Why isn't σ sensor-realistic?" → It spans jitter to larger-than-vehicle; stress test.

## Hard (13–19)

**13. Present your headline result with numbers.** LiDAR noise medium/high −74.9 %/−76.4 % vs LiDAR zero −40.5 %; radar noise −14.9 %/−22.7 % vs zero −6.3 %; camera ≤ −1.8 % in all; FN +259.9 %, FP −82.8 %; largest FP rise +3.6 % (`C:14-16`, FIG).
*Probe:* "Pooled or class-mean?" → pooled mAP; class-mean LiDAR-high is 21.6 (`D:146`), different aggregation.

**14. Why does noise hurt more than zeroing?** Measured, not explained. H1: ungated corrupted branch; H2: backbone voxel-scale sensitivity; discriminating run (LiDAR-only detector) not done and cannot be (access lost) (`D:106-107,118`).
*Probe:* "Which do you believe?" → "I lean H1+H2 jointly, but I have no evidence to pick; zero-fill vs clean exclusion shows gating matters for LiDAR (−41.4 % vs −28.8 % sedan), which supports H1 partially."

**15. Your baseline is 2–5 AP below the paper. Why trust your retention?** Retention is a ratio on the same pipeline; a constant multiplicative offset cancels, an offset that varies by condition would not. Cause unresolved: seed and software ruled out in my notes; KITTI yaw-conversion issue candidate, unquantified (`R:36`, `C:63`).
*Probe:* "Did you test the yaw fix?" → No.

**16. Statistical validity?** One seed, no CIs; N>30 floor; <10-sequence flag; 35 456 objects pooled; five strata agree on LiDAR-noise as worst. Proper fix: sequence-level bootstrap and multiple noise seeds (`M:446`).
*Probe:* "Why sequence-level?" → frames within a sequence are correlated; frame-level CIs too narrow (general knowledge).

**17. Why did mASE and mAOE improve under the worst corruption?** Survivorship: TP population −79.3 %; survivors are easy (`D:23`).
*Probe:* "How would you fix the metric?" → evaluate on the fixed set of objects detected in both clean and corrupted runs (paired TP subset).

**18. What happens in the Kalman update if the innovation covariance S is near singular?** K blows up / numerical failure; use Cholesky solve, Joseph form, regularise R. (General knowledge.)
*Probe:* "In your quaternion filter?" → state has rank-deficient covariance (4 states, 3 DOF) — normalisation hides it; MEKF would use 3-state error.

**19. FIDO: how would you add outlier rejection?** Chi-square gate on innovation d² = νᵀS⁻¹ν vs χ²₂(0.99) = 9.21; consider separate R for RTK-fixed vs float; track fix-type flag. (General; not implemented in the article.)
*Probe:* "Did you implement it?" → [YOU] answer truthfully; documents say no.

## Expert / curveball (20–25)

**20. Design a fix for the LiDAR-noise collapse.** Per-branch health statistic computed from input before CASAP (voxel occupancy, point-count, range-image roughness, SNR) → drop branch from attention below threshold; train with noise augmentation across SCL subsets; evaluate with the same sweep plus oracle-exclusion control. Untested (`D:146`, `D:135`).
*Probe:* "What false-alarm cost?" → dropping a good LiDAR loses ≈ −29 to −41 % mAP in the exclusion/zero cases (`D:80-91`) — threshold must be tuned on ROC for health detection.

**21. Is your result a statement about LiDAR or about ASF?** About one released ASF checkpoint on K-Radar. Prior benchmarks (Yu 2022, Gao 2023) find LiDAR dependence in other models, so the *direction* is not unique; the *noise-vs-absence magnitude* is ASF-specific until replicated (`D:49-51,103`).

**22. A client asks: "Is this model safe to deploy?" Reply.** My evidence addresses one failure class on one dataset with synthetic faults; it shows a silent, non-graceful regime. Safe-to-deploy needs operational-domain coverage, real fault data, runtime monitors, and a safety case; I can scope the missing tests.

**23. How would you test detector robustness to timing faults?** Frame delay/skew and stale-frame replay (not frame deletion → crash); the thesis' wrapper had a `last_frame_hold` option not used (commented, `M:32`). Metrics: retention vs delay; temporal consistency.
*Probe:* "Why did frame deletion crash?" → `None`→empty cloud→zero-voxel input → sparse-conv RuntimeError.

**24. You're placed at a client with an unfamiliar telecom data problem. First week?** `06` §3: decision, inventory, baseline, cheap experiments, hypothesis vs measurement, one-pager, handover. Honest: no telecom domain knowledge.
*Probe:* "What if the client resists your finding?" → show the raw table, ask them to name the experiment that would change my mind.

**25. What is wrong with your CV?** Answer (see `08`): FIDO "sub-meter" and outlier line, SSY345 "6-DOF/Google", Crazyflie "yaw/hardware framework". "I've re-read my reports against the CV; here are the lines I'd correct."
*Probe:* silence — the interviewer will wait; don't pad.
