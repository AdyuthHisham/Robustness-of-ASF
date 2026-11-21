# 08 — Top 10 risks (ranked by likelihood × damage)

Pointers refer to 01 (audit), 03 (thesis Q&A), 06 (consulting). † = derived from `metrics_table.png`.

---

### 1. "Where does '28% / 8% / 1%' come from?"
**Why it hurts:** it's on the CV as a headline, appears nowhere in the thesis text (01 C9), and is an unweighted mean of retention over seven heterogeneous conditions that includes partial-loss values above 1.0.
**Answer:** "It's the mean pooled-mAP loss relative to the 73.99 clean baseline over seven conditions per sensor — noise at three severities, partial loss at three, complete loss — taken from my metrics table: LiDAR 28.4%, radar 7.6%, camera 1.4%†. It's a summary; the result I'd stand behind is the ordering and the worst-case: LiDAR noise −75/−76%, zeroed LiDAR −40%, radar noise −15/−23%, camera ≤2%." **Before the interview:** decide whether to add this definition to the CV or to the thesis.

### 2. "Why does noise hurt more than zeroing — and is it ASF or just the LiDAR backbone?"
**Why it hurts:** it's your central claim and the thesis itself says the cause is not established (`Disc:107`), while the Abstract/Conclusion lean on the availability-flag story and the Conclusion cites a voxelizer hypothesis that isn't in the live Discussion (01 D8).
**Answer:** "Measured: yes. Why: two explanations — the availability flag is never set so a corrupted branch is fused as valid; or a backbone sensitivity to voxel-scale noise independent of fusion. They predict the same result. The discriminating experiment is a LiDAR-only detector under the same noise; I didn't get to run it before cluster access ended. One more clue: false positives fell 83% while false negatives rose 260%, so the model goes quiet rather than hallucinating."

### 3. "Where are your confidence intervals? One seed, one checkpoint?"
**Why it hurts:** true; no CIs, one deterministic noise draw (seed 42), one checkpoint, one dataset (01 D12).
**Answer:** "Correct. The LiDAR-noise effect — mAP 74 to 17.5, FN +260% — is far beyond plausible sampling variation, so I rest conclusions there. I would not rank camera conditions (≤2% differences). The right fix is a cluster bootstrap over sequences with multiple noise seeds; I identified it but ran out of compute access."

### 4. "You applied the same σ to LiDAR and radar. How did you add xyz noise to a dense radar tensor?"
**Why it hurts:** two separate holes — unequal relative severity (LiDAR cm-accurate vs radar 0.46 m range bin) and thesis text never says what radar representation was perturbed (01 D6, D7).
**Answer:** "Equal in metres, not equal in severity — 1 m is ≈2 radar range bins but ≈20–40× LiDAR accuracy, so the LiDAR-vs-radar gap is partly relative perturbation. On the radar representation: [YOU SUPPLY exactly what was perturbed]. If I redid it I'd scale σ to each sensor's resolution." **Do this before the interview:** check the code and know the answer.

### 5. "You didn't train anything. What did you engineer? And how much was AI?"
**Why it hurts:** CV says "Engineered a framework"; thesis is an evaluation of a released checkpoint; GenAI declaration admits AI help with code suggestions.
**Answer:** "No model was trained, by design (`Meth:5`). What I built: the inference-time corruption layer, the per-condition run orchestration on SLURM, the consolidation into a Parquet table, the metric stack (AP, F1, TP-only errors, retention, CRI, churn), and the stratified analysis. [YOU SUPPLY ownership split vs K-Radar/AMSCUP_PLUS code.] AI tools helped with grammar and code suggestions; I reviewed and verified outputs and I can derive each metric myself." Be able to write CRI and AP on a whiteboard.

### 6. "Your own numbers disagree with each other." (D1/D3/D4)
**Why it hurts:** pooled vs mean-of-class (−76.4% vs −70.42%), 21 vs 22 conditions, "17 of 22", FP rose in "6 of 21" (figure: 4), "more than +50% at five other conditions" including +29.9%.
**Answer:** "Two aggregations appear: object-pooled mAP and mean-of-class AP. I quote pooled in the conclusion (76%) and class-averaged in one discussion section (70%); same ranking. Counting: 21 corrupted conditions plus baseline; 5 collapsed, 16 within 8.8%; FP rose in 4 of 21 with a max of +3.6%." Know these cold; they are the cheapest mistakes to avoid.

### 7. "Your baseline is 3–5 points below the paper. Why should I trust the pipeline?"
**Why it hurts:** unresolved; the explanations are in commented-out text while the Conclusion says "ruled out" (01 D10); the text mixes absolute points and relative percent.
**Answer:** "Sedan −4.6 BEV / −4.3 3D, bus −2.3 / −2.3 points. I checked hardware, seed variance and a reported yaw-conversion bug in the K-Radar evaluation code; none is shown sufficient. All robustness metrics are relative to my own baseline, so an absolute offset doesn't change retention conclusions. It remains an open discrepancy." Don't say "ruled out".

### 8. "No telecom/energy/finance, little production experience. Why should we place you?" (06 §5)
**Why it hurts:** consultancy sells breadth and placement flexibility; your depth is automotive perception/estimation.
**Answer:** "My core is method-level: state estimation and fault detection, robustness testing, reproducible data pipelines. At Siemens I was embedded in a client team for a year with regular demos. I'd expect a domain ramp-up and I'd propose automotive-first placement. I won't claim domain knowledge I don't have."

### 9. CV project depth: "How did you measure 'sub-meter'?" / "What's '6-DOF orientation' from accel+gyro?" / "Did the Crazyflie fly?"
**Why it hurts:** the CV gives claims without numbers or references (01 P4–P6); "6-DOF orientation" is technically wrong (3 rotational DOF, yaw unobservable); "establishing a sim-to-hardware framework" overreaches if nothing flew.
**Answer:** [YOU SUPPLY measurement reference and metric for FIDO]; "Orientation is 3-DOF from six sensor axes; yaw drifts without a magnetometer; I estimated roll and pitch well and handled yaw by …"; "Validated in Simulink/Simscape with simulated disturbances; hardware deployment was [YOU SUPPLY]." If no reference existed, say "sub-meter was the filter's own consistent covariance plus loop-closure checks", only if true.

### 10. CV hygiene and language: placeholder title, ROS2 dates, English/Swedish
**Why it hurts:** `[ROLE TITLE]` in the master (CV:7); ROS2 project dated Jul 2023–Jul 2024 in "Gothenburg" while you were at Sysenso, Chennai, and before Chalmers (Sep 2024) (CV:20,48,80); English listed "Intermediate" after an English-taught MSc; Swedish "Beginner" for on-site placements (CV:110).
**Answer:** Fix the CV before sending. State true ROS2 dates/location (e.g. "personal project, [dates], [place]"). Language: give your honest working level and a concrete Swedish plan; ask which client sites need Swedish.

---

## Runner-up risks (not top ten, still prepare)
- **Dataset-split inconsistency** (58 sequences full vs 58-sequence test split, `Theory:25` vs `Meth:87`): know the real split.
- **"Is synthetic Gaussian noise realistic?"** (`Disc:112`): no; ranking is only as realistic as the noise model.
- **CRI critique** (units, variance penalty).
- **LiDAR complete loss "collapse" vs "graceful"** wording conflict (D5): say −40.5%, large but proportionate.
- **Frame-deletion "no predictions"** vs "crash" (D16).
- **Apptainer/Docker/Polars/PyTorch** claims: not in thesis; have an own-experience answer.
