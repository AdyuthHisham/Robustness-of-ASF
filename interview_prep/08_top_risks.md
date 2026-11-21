# 08 — Top 10 risks (ranked by likelihood × damage)

Ranking logic: an interviewer reads the CV, opens one claim, and checks it. Items 1–5 are claims your own PDFs contradict. Pointers in `01_claim_audit.md` (C = CV claim, D = discrepancy, T = thesis number). Nothing was edited; rewording suggestions below are proposals for you to apply or not.

### 1. "FIDO: sub-meter accuracy in live tests — how did you measure it?" (C10)
**Why it hurts:** the article reports GNSS-vs-odometry RMSE 6.7 → **1.7 m**; no EKF-vs-ground-truth number exists (`R/SSY226_Fido_article_final.pdf` abstract, §IV-A1, §III-A5a).
**Answer:** "That line on my CV overstates it. What I measured: RTK reduced the RMSE of GNSS against the robot's odometry from 6.7 m to 1.7 m across trials. Odometry isn't ground truth, and I didn't evaluate the EKF output against surveyed points; I judged it on straight, circle and L-shaped runs. The next step would be a surveyed reference and NEES/NIS." 
**CV fix:** "Reduced GNSS position RMSE (vs odometry baseline) from 6.7 m to 1.7 m with network RTK; fused with odometry in a coordinated-turn EKF."

### 2. "Show me the outlier rejection in the FIDO EKF / what about multipath?" (C11)
**Why:** the article has no outlier gate and never mentions multipath.
**Answer:** "In FIDO the weighting came from calibrated GNSS covariance; I did not implement a gate, and I identified stale covariance after an RTK drop as a weakness. The gating work I can derive and show is in my orientation-filter project: accelerometer-norm and AR(1) magnetometer-norm gates. For FIDO I'd add a chi-square innovation gate, χ²₂(0.99) = 9.21." (Only say "I did not implement" if true — [YOU] check your code.)
**CV fix:** move gating to the SSY345 bullet; delete the multipath clause.

### 3. "Smartphone EKF: 6-DOF? benchmarked against Google? what was the optimum?" (C13–C14)
**Why:** filter used gyro + accelerometer + **magnetometer**; reference = "app's" estimate; RMSE up to 2.71 rad; report says quantification was difficult (`R/SSY345_Project_Group_37.pdf` Task 12).
**Answer:** "Orientation is three-DOF; the filter is a 4-state quaternion EKF with gyro as input and accelerometer and magnetometer updates, each gated. I compared sensor combinations against the phone app's own orientation output. The comparison was qualitative: initial orientations differed, so RMSE wasn't a clean metric. Findings: accelerometer+magnetometer without gyro can't track motion; the magnetometer bounds yaw drift but is disturbed by electronics, which is why I added the AR(1) norm gate."
**CV fix:** "Quaternion EKF (gyro input; gated accelerometer and magnetometer updates) for smartphone orientation; compared sensor combinations against the phone's built-in estimate."

### 4. "Crazyflie: 'sim-to-hardware deployment framework'? 'yaw stabilization'?" (C16, C19)
**Why:** the report says hardware did not match, code port not completed, validation limited to simulation; yaw rate only.
**Answer:** "I designed and simulated the controller and flashed it for a hover test; the hardware oscillated in roll, and we couldn't finish the Embedded-Coder port. So I wouldn't call it a deployment framework; what I have is a validated simulation plus a documented failure analysis. States were roll, pitch and their rates plus yaw rate."
**CV fix:** "Discrete LQR for roll/pitch (and yaw-rate) with complementary-filter attitude estimate in Simscape; hardware test showed sim-to-real gap (battery CoM offset; code port unfinished)."

### 5. "Why is noisy LiDAR worse than no LiDAR? Prove the mechanism." (D7)
**Why:** your own thesis says cause not established; one decisive experiment not run and can't be (access lost).
**Answer:** "I measured it; I didn't prove why. Two explanations fit and predict the same outcome: the corrupted branch never gets gated because availability is a manual flag, or SECOND's voxel backbone is itself sensitive to voxel-scale noise. Evidence leaning toward gating mattering: zero-fill costs LiDAR 6–13 points more than ASF's own clean exclusion. The experiment that separates them is a LiDAR-only detector under identical noise."

### 6. "Your baseline doesn't match the paper." (D3, T11)
**Answer:** "2.3–4.6 AP points below, same checkpoint, code, IoU. Seed variance and software mismatch I checked and ruled out as sufficient; a KITTI yaw-conversion issue in the K-Radar repo is a candidate I didn't quantify. Retention is a ratio on the same pipeline, so a constant offset cancels, though condition-dependent offsets wouldn't." Don't say 'the paper is wrong'.

### 7. "One seed, no confidence intervals, a synthetic σ larger than the car." (D8, D9)
**Answer:** "Agreed, those are the limits. What I have: 35 456 objects, five strata and both classes all pointing at LiDAR noise as worst, and a reliability floor and sequence-confounding flag. What I'd add: multiple noise seeds, sequence-level bootstrap, and a finer σ sweep between 0.1 and 1.0 m, where the collapse begins (−5.9 % at 0.1 m, −74.9 % at 1.0 m)."

### 8. "Show me the Apptainer / SLURM script. How much compute?" (C2)
**Why:** Apptainer isn't in the thesis; no job counts/GPU-hours in any document; the folder has no scripts.
**Answer:** [YOU] open your actual job script. If you can't: "SLURM array, one job per sequence on Alvis A40s; containers for the ASF environment [only if true]; I don't have the GPU-hour total to hand." Never quote a number you can't produce.

### 9. "Sysenso/Siemens and Industriteknik: details and numbers?" (C6–C8)
**Why:** zero documents; the CV says "validated" and "effectively extracting" with no metrics. Also the ROS2 project's Jul–Aug 2023 dates overlap the Sysenso job and its location differs.
**Answer:** prepare per `04` §4–§6: algorithm, data scale, measure of success, failure cases, your share. If a number doesn't exist, say "I didn't measure that" and describe how you judged it (client acceptance in demos). Resolve the ROS2 date line before someone asks ("personal project over a few weeks alongside work" only if true).

### 10. "How much of the thesis/code did AI write?" and "Are you a consultant or a researcher?" (D11)
**Answer (AI):** "The declaration says AI helped with phrasing and code suggestions, not with content; I can walk through any function and any figure from raw data, e.g. recompute FN +259.9 % from 29 829 vs 8 287." Then do it.
**Answer (consultant):** "My strengths are measuring a system honestly and communicating the boundary of a claim. I lack domain experience in telecom, energy and finance and would pair with the client's domain owner early; the method transfers, the vocabulary I'd learn." (`06` §4.)

---
## Safe rewording summary for CV lines (proposals only)
| CV line | Proposal |
|---|---|
| FIDO "sub-meter … live tests" | "RTK reduced GNSS RMSE (vs odometry) from 6.7 m to 1.7 m" |
| FIDO "outlier rejection … multipath" | delete or replace with "covariance-weighted updates from calibrated GNSS noise" |
| SSY345 "6-DOF … accelerometer/gyroscope … Google" | quaternion EKF, gyro + gated accelerometer + magnetometer; compared against phone's estimate |
| SSY191 "roll, pitch and yaw … deployment framework" | roll/pitch + yaw-rate LQR; simulated, hardware test showed gap |
| Thesis "Apptainer" | keep only if you can show the image/def file |
| Thesis "28 % / 8 % / 1 %" | keep; say "mean retention over seven conditions per sensor, pooled mAP" and be ready to show FIG |
