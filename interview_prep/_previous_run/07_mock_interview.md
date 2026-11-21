# 07 — Mock interview (25 questions, escalating)

Model answers use only thesis/CV facts or are tagged **GK** (general knowledge) / **[YOU SUPPLY]**. † = derived from `metrics_table.png` (01 §0). Each question has the follow-up probes an interviewer would use.

---

## Level 1 — Warm-up

**1. Tell me about yourself in under 90 seconds.**
M.Sc. Systems, Control and Mechatronics at Chalmers, finishing Sep 2026; before that a year as a client-seconded engineer at Sysenso on a Siemens site building a LiDAR road-feature annotation tool in C++/Python/PCL; thesis on robustness of a camera–LiDAR–4D-radar detector under synthetic corruption, run on an HPC cluster; side work in EKF state estimation and ROS2.
*Probes:* Why Sweden? Why consulting rather than a product company? What do you want to be doing in three years?

**2. Why a consultancy?**
Variety and client exposure: the Siemens secondment showed I work well embedded in someone else's team and enjoy demo-and-feedback cycles. [YOU SUPPLY the personal reason.]
*Probes:* Are you comfortable not owning the product? How do you feel about a client's decisions you disagree with?

**3. Summarise your thesis in 30 seconds.** (See 02.)
*Probes:* Was it your idea? Who wrote the code? Did you train anything?

**4. What was your contribution versus existing code?**
The thesis evaluates the officially released ASF checkpoint; the corruption wrapper, run orchestration, metric computation and analysis are the contribution (`Meth:5,436,523`). [YOU SUPPLY the exact split between your code and K-Radar/AMSCUP_PLUS tooling.] AI tools were used for grammar/clarity and code suggestions (GenAI declaration).
*Probes:* How much was AI-assisted? How did you verify it? Show me a piece of code you're proud of.

## Level 2 — Core technical

**5. What is sensor fusion and why not just use LiDAR?**
Sensors fail under different conditions: camera in poor light, LiDAR in rain/snow/fog, radar has low resolution but is weather-robust (`Theory:9,76`). Fusion buys redundancy.
*Probes:* Which fusion level? What does radar add over LiDAR? Does fusion always beat the best single sensor? (GK: no; poorly designed fusion can be worse and fail jointly — Gao et al. found tight coupling.)

**6. Explain what ASF does.**
Frozen per-sensor encoders → BEV patches → per-sensor projection to common channels → cross-attention per patch over present sensors → normalisation → detection head; trained on all 7 sensor subsets (`ASF:57-103`).
*Probes:* Why a shared query? Complexity? What happens with one sensor?

**7. What did you find?**
5 of 21 conditions collapsed; LiDAR noise −75%/−76%†, zero −40.5%†; radar noise −15%/−23%†, zero −6%†; camera ≤2%†; FN up to +260%, max FP +3.6% (`Disc:35`).
*Probes:* Which of these numbers is pooled vs per-class? (D1.) Where are the error bars? (None.)

**8. Define AP and F1 and why you used both.**
AP: 41-point interpolated area under P–R at IoU 0.3 (`Meth:448`). F1: fixed-threshold harmonic mean, more calibration-sensitive (`Meth:458`).
*Probes:* Why IoU 0.3? (K-Radar convention.) What threshold for F1? (**Not stated in thesis.**)

**9. What does the EKF do in your FIDO project and what's the state?**
Fuses GNSS/RTK and IMU for localisation; predict with IMU kinematics, update with GNSS; Mahalanobis gating to reject outliers. [YOU SUPPLY state vector, thresholds.]
*Probes:* Jacobian of your process model? How did you tune Q/R? How did you get "sub-meter"?

**10. What is the difference between a complementary filter and an EKF?**
Fixed-gain frequency split vs time-varying optimal gain with covariance and gating; CF cheap and simple, EKF principled but costlier to tune (05 §1–2).
*Probes:* When would you choose each? What does a complementary filter do with yaw?

## Level 3 — Probing

**11. Why does noise hurt more than zeroing?**
Observed, not explained: two hypotheses (unused availability flag so corrupted branch fused as valid; backbone voxel-scale sensitivity) predict the same outcome; the LiDAR-only experiment wasn't run (`Disc:107`). Added evidence: FP fell 83% → suppression, not hallucination.
*Probes:* How would you test it? What does the zero-fill case actually feed the network? (Points set to zero, branch still processed, `Disc:109`.)

**12. Is that finding generalisable?**
No evidence beyond ASF/K-Radar: single checkpoint, single dataset, synthetic faults (`Disc:103,112`). Plausibly general for tightly coupled fusion (Gao et al., Yu et al.), but untested here.
*Probes:* What would convince you it generalises? (A second availability-aware architecture; another radar dataset.)

**13. You applied the same σ to LiDAR and radar. Fair?**
Equal in metres, unequal relative to the sensor: LiDAR accuracy centimetres vs radar range resolution 0.46 m (`Meth:52,59`). So the gap is partly relative perturbation, not only model reliance.
*Probes:* How would you equalise severity? (Scale σ to resolution/accuracy, or match to a degradation in task metric.)

**14. How did you apply noise to radar?**
**NOT IN THESIS** — the Methods text says xyz noise on points while ASF's radar encoder takes a dense tensor. Say plainly which representation you perturbed [YOU SUPPLY].
*Probes:* What does σ=2 m do to a 0.46 m range-bin tensor?

**15. Walk me through CRI and criticise it.**
Formula (`Meth:492`); criticisms: AP-unit dependence of ln(1+σ), over-penalises gradients (radar_loss_partial 0.399 with mean Rb 0.97), 3-point σ, borrowed from HOI detection (D13).
*Probes:* Compute CRI for me. (LiDAR noise pooled ≈ 0.11.) Would you use it in a safety argument? (No; use per-severity Rb with CIs.)

**16. Your baseline is below the paper. Why?**
Sedan −4.6 BEV/−4.3 3D pts; bus −2.3/−2.3 pts (`Res:30-31`). Unresolved: candidates (hardware, seed variance, K-Radar yaw-conversion issue) were investigated in material that is not in the compiled thesis. Relative robustness metrics are unaffected by an absolute offset.
*Probes:* Did you contact the authors? Could the yaw bug change your robustness conclusions? (Unlikely in direction: it applies to both clean and corrupted runs; magnitude unquantified.)

**17. Frame deletion crashed. Is that a result?**
It's an engineering finding: no empty-input guard in the sparse-conv path (`Res:482`). It says nothing about how ASF would handle a missing frame if guarded. Don't call it "complete failure to detect".
*Probes:* How would you fix it? (Return empty predictions or hold-last with a staleness flag; GK.)

**18. Statistical validity?**
No CIs; single seed; N>30 floor; effective sample ≈ sequences, not frames (`Meth:446`). Large effects survive; small contrasts don't.
*Probes:* Design the CI procedure. (Cluster bootstrap over sequences × multiple noise seeds.)

## Level 4 — Hard

**19. A client says "our model is robust because it handles sensor dropout." What do you do?**
Ask what "dropout" means in their tests (declared absence vs silent degradation vs partial); replicate my thesis ladder: absence, partial loss, noise, at graded severities; separate FN from FP; report retention per stratum with CIs; check where the claim's evidence stops (`Meth:19-26`).
*Probes:* What if they have no budget for new experiments? (Use existing logs/field data to find natural degradations; rank conditions by exposure.)

**20. How would you make ASF detect a degraded-but-present sensor?**
Proposal in thesis (untested): a content-derived per-branch statistic (voxel occupancy, point count, SNR) before CASAP that withholds a branch's key/value pair (`Disc:146`). GK: train with noisy-branch augmentation, add reliability head, uncertainty-aware fusion.
*Probes:* Risks? (False gating reduces redundancy; thresholds drift; adversarial/edge cases; needs validation on real faults.)

**21. Design a test for a LiDAR failure mode you haven't simulated.**
Pick a mechanism (e.g. window contamination → intensity/range attenuation + dropout by sector; EMI → burst noise), parameterise severity against physical units, apply inference-time, report retention and FN/FP, and tie to a hazard (SOTIF-style). Note the thesis's own limit: real faults may resemble neither noise nor absence (`Disc:112`).
*Probes:* How would you validate the simulator against reality?

**22. Derive the discrete LQR gain.**
Cost-to-go V=xᵀPx; minimise over u: u=−(R+BᵀPB)⁻¹BᵀPA x; substitute → DARE (05 §3).
*Probes:* What if there's delay? Integral action? Why might the gain be poor on hardware? (Unmodelled actuators, saturation, noise.)

**23. EKF diverges on your robot after a GPS jump. Diagnose.**
Check innovation/NIS trace; if gating rejects all subsequent fixes the covariance has collapsed → inflate P or reset after N rejections; check angle wraparound, timestamp alignment, units; log innovations. (05 §1.)
*Probes:* What if it only diverges at standstill? (Heading unobservable.)

## Level 5 — Stress and consulting

**24. You have no telecom/energy/finance experience. Why should we place you there?**
I'd say: "You shouldn't place me cold. My transferable core is state estimation, fault detection, robustness testing and data pipelines; I'd expect a ramp-up and I'd show evidence of fast ramp-up: [Myo/Quest, thesis]. I'd rather be useful sooner in automotive and expand." (06 §5)
*Probes:* Give me an example of learning a domain fast. What happens if the client domain expert distrusts you?

**25. Convince a sceptical manager that your 28% / 8% / 1% figures mean something.**
Say what they are: average pooled-mAP loss relative to the clean baseline over seven conditions per sensor (noise ×3, partial loss ×3, complete loss) — my summary of the table, not a number in the thesis text (†). The headline is the ordering and the noise-vs-zero contrast, which hold regardless of averaging. Don't defend the exact figures as precise.
*Probes:* Why not weight by severity or by exposure? Does including partial loss (≈0%) dilute the result? (Yes; the worst-case ordering is the robust statement.)

---

## Scoring guide for yourself
- Claims backed with a pointer: good. Claims with "I think" where the thesis has a statement: study that spot.
- Any time you say a number, also say its definition (pooled vs per-class; relative to clean).
- If asked something outside the thesis, say "that's not in my thesis — from general knowledge…" (the 03/04 convention).
