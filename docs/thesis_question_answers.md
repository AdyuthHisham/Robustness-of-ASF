# Thesis Defense — Q&A Prep

Format: spoken answer (what to say out loud) → backstage evidence (sources, not spoken) → likely follow-ups → risk flag.

---

## Q1. Shared LiDAR/radar noise severity scale (0.1/1.0/2.0m) despite different sensor resolutions

**Question:** You add the same noise to LiDAR and radar points: 0.1, 1.0 and 2.0 metres. But the two sensors measure at very different scales. The OS1-128 LiDAR is accurate to about 5 mm, while the radar resolves range in 0.46 m steps and its cube is voxelised at 0.4 m. So at low severity, 10 cm is twenty times the LiDAR's own precision and genuinely moves its points, while for the radar the same 10 cm falls inside a single cell and may never show up at all. Did you consider giving each sensor its own severity scale instead of one shared schedule?

### Spoken answer (~60s)
That's a fair point, and no — I didn't give them separate scales, and in hindsight that's a real limitation. I used the same three noise levels, 0.1, 1.0, and 2.0 metres, on both LiDAR and radar points so I could compare "low/medium/high" across sensors on a common axis. But you're right that those numbers don't mean the same thing physically — 10 centimetres is a large perturbation for a LiDAR point that's normally accurate to millimetres, but for radar, which already resolves range in coarser steps, that same 10 centimetres can just get absorbed into the existing measurement uncertainty. So my "low severity" for radar may have been much weaker in real terms than my "low severity" for LiDAR. I didn't recalibrate per-sensor because I wanted one shared, interpretable schedule across all three modalities for the severity trend plots. That's a design tradeoff I'd flag rather than defend as clearly correct.

### Follow-up rebuttal considered
Alternative framing: the design isn't meant to stress-test each sensor's backbone individually, but to study how a fixed real-world distortion magnitude propagates through the whole fusion pipeline. Equal physical displacement is a legitimate independent variable; sensor-specific scaling would be the right choice for a backbone-sensitivity study, not a pipeline-propagation study.

**Code-level check (confirmed):** `radar_gaussian_noise` (`repos/K-Radar/datasets/effects/noise_injection.py:299`) is applied to `dict_item['rdr_sparse']` — a **sparse, continuous-coordinate point list** `(x, y, z, power)`, not a voxelized cube. Verified against actual data dump (seq 48, frame 000006, `radar_gaussian_noise_medium`): `rdr_sparse` shape `(150000, 4) float64`, columns `[x, y, z, power]`; corrupted and clean arrays have identical shape, confirming only xyz values are perturbed in place.

Voxelization happens **later, inside the model** (`models/pre_processor/rdr_sparse_processor.py`, `RadarSparseProcessor.forward()`, via spconv's `PointToVoxel`), not at injection time. `PointToVoxel` retains up to 4 raw points per voxel (with continuous coordinates) as feature input to a linear/pointnet layer — it does not collapse to binary occupancy. So a 0.1m shift that doesn't move a point across a voxel boundary still changes the coordinate values the network actually sees; the noise is not simply discarded by quantization.

**Net effect on the rebuttal:** strengthens it. The "gets absorbed into a single cell and never shows up" concern is weaker than originally assumed, because injection precedes voxelization and per-point continuous data survives into the model's input features.

**Still unverified / open:** actual configured value of `RDR_SP_CUBE.GRID_SIZE` (or `roi.grid_size`) for the ASF run; whether `is_with_simplified_pointnet` pooling (`max` vs `mean`) at that layer washes out small per-point differences after voxel aggregation. Worth checking before relying on this in the room.

### Backstage evidence
- Severity values identical across LiDAR/radar: Methods.tex:422 (thesis text); code confirms both use the same 3-tier sigma table (`noise_injection.py:299` radar, `:409` LiDAR).
- Sensor specs (LiDAR ±5mm, radar 0.46m range res, 0.4m cube voxel) — Methods.tex sensor table, lines 44-79.
- No LiDAR/radar-specific severity recalibration documented anywhere in Methods.tex or vAIlt severity-design docs.
- Radar's SNR-dB-based `noise_induced_shifts` effect (sensor-appropriate alternative, from Morales & Habibi arXiv 2505.00584) exists in code but is **disabled** (`noise_injection.py:244`), excluded pending a reparameterization decision.
- `rdr_sparse` shape verified directly from data: `(150000, 4)`, `[x,y,z,power]`, no doppler column present in this dump despite module docstring mentioning an optional 5-column variant.
- Confidence: SUPPORTED (design choice + code-level verification); voxel-pooling caveat UNVERIFIABLE without checking config + spconv aggregation behavior directly.

### Likely follow-ups
- "So is your radar 'high severity' condition actually testing anything?" — radar_gaussian_noise CRI (0.272 both classes) is far higher (more robust) than lidar_gaussian_noise (0.106/0.153); could reflect genuine radar robustness or under-perturbation — can't fully separate without the pooling-mode check.
- "Did you verify the noise survives past the voxel-pooling layer?" — honest answer: not yet: `is_with_simplified_pointnet` pooling mode (max/mean) at that layer is unchecked.
- "Why not use the disabled `noise_induced_shifts` effect?" — left disabled pending an unresolved SNR-dial reparameterization decision; natural future work.

### Risk flag
This gap is not currently listed in the thesis's stated limitations (single-checkpoint, cause-not-established, synthetic-not-real, minority-strata fragility, no-further-data). Practice owning it plainly. The voxel-pooling follow-up is the one place the examiner's original concern could still partially hold — check the config/pooling mode before the defense if time allows.

---

## Q2. Restriction to sedan/bus classes; expectation of earlier collapse for smaller targets

**Question:** You score cars and buses or trucks, following K-Radar's standard benchmark. But the dataset also labels pedestrians, bicycles and motorcycles, and those are much smaller targets, so the laser returns far fewer points from each one. A car has to have its points scattered by about a metre before the model loses it. A pedestrian starts with far less to lose. Do you expect the collapse to arrive sooner for them, and would that be worth a line in the limitations?

### Spoken answer (~55s)
I only scored sedans and buses or trucks, because that's the standard K-Radar benchmark convention, and it's also what ASF's own published results report on, so my baseline numbers are directly comparable to theirs. K-Radar does label pedestrians, bicycles, and motorcycles too, but I didn't evaluate on them. Your intuition is right, though — I'd expect the collapse to happen sooner for smaller, sparser-point targets. If a car needs its points scattered by roughly a metre before the model starts losing it, a pedestrian, with far fewer LiDAR returns to begin with, has much less margin before it disappears entirely. I haven't tested that, so I can't put a number on it, but it's a reasonable hypothesis and I agree it deserves an explicit line in my limitations — right now it isn't there, and it should be.

### Backstage evidence
- Class restriction confirmed: thesis evaluates only sedan and bus/truck throughout (Results.tex N_gt tables, Methods.tex). ASF's own published tables are also sedan/bus-only (ASF.tex lines 26-50) — matching benchmark convention, VERIFIED.
- No pedestrian/bicycle/motorcycle evaluation anywhere in thesis, code (dataset row_table schema confirmed only `sed`/`bus` classes present), or presentation deck.
- "Sooner collapse for smaller targets" is a hypothesis, not tested. Existing density-vs-AP analysis (item2_binned_recall.csv) is over sedan/bus GT-count-per-frame bins, not object-class size — not directly transferable evidence.
- Confidence: VERIFIED for "thesis doesn't evaluate these classes"; UNVERIFIABLE for the collapse-timing prediction (no pedestrian-scale data exists to check against).

### Likely follow-ups
- "Does K-Radar have enough pedestrian instances to test this?" — unknown, would need to check K-Radar's class distribution before the defense.
- "Isn't this the same limitation as ASF's own paper?" — yes, the class restriction inherits directly from ASF's own evaluation scope; a shared limitation, not unique to this thesis.

### Risk flag
Real gap in the stated limitations list. Worth adding a sentence on class-size sensitivity as future work before the defense, since the examiner raised it explicitly.

---

## Q3. Bus/truck rain baseline (7.9 AP) near-exact match to ASF paper (8.0 AP) despite overall 3–5 point gap elsewhere

**Question:** Before any corruption is applied, your baseline scores 7.9 AP on buses and trucks in rain, against 81.7 in overcast weather, on a similar number of objects: 120 against 151. ASF's own paper reports 8.0 for the same class in the same weather, so this is one of the few numbers you reproduce almost exactly, while the rest of your baseline sits 2 to 5 points low. Any idea what is happening there?

### Spoken answer (~65s)
That's a striking coincidence and I don't have a confirmed explanation for it. Across the board, my baseline numbers sit about 3 to 5 points below ASF's published figures, and I discuss three possible reasons in the thesis — random seed differences, some software or hardware mismatch, and a possible yaw-angle conversion issue that's actually a known open issue in the K-Radar codebase. None of those fully explains the gap on its own. But this one cell, buses and trucks in rain, comes out at about 8 AP for me versus 8.0 in their paper — almost exact. My honest read is that this is more likely a small-sample coincidence than evidence the model is fine there. There are only about 120 to 150 objects in that bucket, so the AP estimate has a lot of variance, and a near-perfect match on one small, noisy stratum isn't strong evidence about what's causing the 3-to-5-point gap everywhere else. I wouldn't read too much into it without a confidence interval.

### Backstage evidence
- Thesis numbers: bus/truck rain baseline AP = 7.9 (Discussion.tex:131), N_gt rain=120, overcast=151 (Results.tex baseline_ngt_by_axis). ASF paper: bus/truck rain = 8.0 AP (ASF.tex table). VERIFIED, both direct from thesis text.
- Overall baseline gap: sedan BEV 77.86 vs 82.5 (-4.64), sedan 3D 74.99 vs 79.3 (-4.31), bus BEV 67.93 vs 70.2 (-2.27), bus 3D 58.15 vs 60.4 (-2.25) — thesis's own "3.2-5.6%" framing (Results.tex:36, 485).
- Root-cause discussion (seed variance / software-hardware mismatch / yaw-conversion bug, citing K-Radar GitHub issue #81) exists only in a **commented-out** section of Discussion.tex (lines 140-151) — not in the compiled document. Be aware this reasoning is not literally present in the submitted PDF, only in draft material.
- N=120 is well below the thesis's own reliability floor (N>30 soft, N>90 preferred) — this cell is exactly the kind of low-N stratum the thesis itself flags as statistically fragile (Methods.tex:446, Discussion.tex:106-107).
- Confidence: SUPPORTED for the numbers; "likely coincidence" interpretation is defensible reasoning, not a thesis claim.

### Likely follow-ups
- "Can you put a confidence interval on that 7.9?" — not computed in the thesis for baseline AP cells; would bootstrap if pushed, N=120 implies a wide interval.
- "Doesn't a good match undermine your seed-variance explanation?" — no, high variance can produce a lucky match as easily as a mismatch.
- "Why isn't this discussion in your compiled thesis?" — be ready to say it was cut from the final draft as an unresolved open item, restated briefly in Future Work.

### Risk flag
Root-cause discussion for the baseline gap exists only in commented-out draft text, not the compiled thesis. If the examiner has read the PDF closely, they may note the gap is acknowledged but under-explained in the final document.

---

## Q4. Should the detection model self-diagnose sensor failure, or should something else in the vehicle?

**Question:** You suggest the model should look at its own inputs and spot a sensor that has gone bad. But a car already runs other software that watches its hardware. Should the detection model be the one to catch this, or should something else in the car do it?

### Spoken answer (~70s)
I think that's the right question, and my honest answer is: probably not the detection model, or at least not it alone. In the thesis I point out that ASF's own availability-awareness mechanism doesn't actually look at the data and decide a sensor is degraded — it relies on a flag that's supplied to it externally, telling it which sensors are available. My corruption experiments never set that flag, even for a fully zeroed-out sensor, which is part of why I can't fully separate "the model reacts badly because it wasn't told" from "the model reacts badly regardless." In a real vehicle, sensor health monitoring already exists at a lower level — signal quality checks, hardware watchdogs, diagnostic software that's simpler, faster, and easier to certify for safety than a large perception network. So I'd lean towards that layer being responsible for detecting failure, and the perception model's job being to respond well once it's told, or to degrade gracefully if it's not told in time. What I haven't tested is whether giving the model a better internal signal, so it could infer degradation from the data itself, would close some of the gap I found. That's future work, not something my results speak to directly.

### Backstage evidence
- Confirmed in code: ASF's availability signal (`avail_feats`) is a manually-supplied dictionary set before inference, never inferred automatically from data (Methods.tex:22-24, Discussion.tex "Cause Not Established" §98). Corruption sweep never populates it for any condition, including zero-filled complete loss.
- Open Question #2 explicitly listed in Discussion.tex:122-129: "would a stronger content-derived availability signal close the gap" — genuinely open, unresolved in the thesis.
- The "external hardware diagnostics vs. model self-diagnosis" framing is defensible engineering judgment, not a thesis claim — be clear in the room this is reasoning beyond what's written.
- Confidence: mechanism claim VERIFIED; "who should own this" recommendation UNVERIFIABLE as a thesis claim (your own synthesis).

### Likely follow-ups
- "Isn't that exactly what ASIL/functional-safety architecture already does in production ADAS stacks?" — reasonable to agree and connect to existing safety-monitor patterns (separate diagnostic ECUs).
- "Could you test a content-derived signal with your existing data?" — no, Alvis compute is gone; would need a new inference run against a modified availability-inference mechanism.
- "If the flag was never set, does that undermine your zero-fill vs. branch-exclusion comparison in Chapter 6?" — strong follow-up: Discussion.tex's `complete_loss_mechanism_comparison` table explicitly frames zero-fill retention as *not* an unqualified robustness measure precisely because the flag isn't set (limitation #2) — connects back to a stated limitation, not a new hole.

### Risk flag
Touches the thesis's most explicitly unresolved limitation (cause-not-established, Discussion.tex §97-101). Good opportunity to show command of the material — keep the position as "open question," not a firm claim.

---

## Q5. LiDAR Gaussian noise more harmful than complete LiDAR loss — backbone or fusion, and how to separate experimentally?

**Question:** Your results show that LiDAR Gaussian noise is much more harmful than complete LiDAR loss. Do you think this mainly comes from the LiDAR backbone itself, or from ASF continuing to fuse corrupted LiDAR features? Is there any method to separate these two effects experimentally?

### Spoken answer (~65s)
I can't fully separate those two causes from my results, and I say so directly in the thesis. There are two candidate explanations. One is that the LiDAR backbone itself is sensitive to small positional noise — there's prior work showing that kind of registration error hurts detection even outside a fusion setting. The other is that ASF keeps trusting and fusing the corrupted LiDAR features instead of down-weighting them, because it was never told that sensor had degraded — its availability signal is a flag that's set externally, and my experiments never set it, even when a sensor is fully noised out. My best guess is it's a mix of both, but I can't prove that split with the data I have. The clean way to separate them would be running a LiDAR-only, non-fused detector under the exact same noise and comparing its degradation curve to ASF's — if a standalone detector collapses just as sharply, that points to the backbone; if it degrades much more gently, that points to the fusion mechanism continuing to trust bad features. I didn't run that comparison, mainly because I lost compute access before I could.

### Backstage evidence
- Thesis explicitly frames this as unresolved: Discussion.tex "Cause Not Established" §97-101 — two candidate explanations (fusion-gating absence vs. backbone-level sensitivity to voxel-scale noise independent of fusion), citing `zeng2025ugp` (KITTI registration accuracy loss under Gaussian point noise, independent of fusion) as precedent for the backbone-intrinsic explanation.
- Confirmed in code: `avail_feats` is manually supplied, never inferred from data (Methods.tex:22-24); corruption sweep never sets it for any condition.
- Thesis states plainly the discriminating experiment "was not run and cannot be run now that Alvis compute access is lost."
- Proposed separation method (non-fused LiDAR-only detector under same noise) is my own synthesis, consistent with the thesis's framing but not literally proposed there.
- Confidence: SUPPORTED (thesis's own stated position); the proposed experimental design is reasoning, not a thesis claim.

### Likely follow-ups
- "Could you at least ablate ASF's own LiDAR-only branch, if one exists?" — worth checking whether ASF's architecture exposes an unfused single-modality output path before answering "no" outright.
- "Wouldn't setting avail_feats=False for noisy-but-present LiDAR be a cheaper test?" — yes, close to what Discussion.tex's Open Question #2 already asks; flag as the most immediately actionable follow-up experiment.

### Risk flag
This is the thesis's single most exposed open question — expect it to come up in some form regardless of phrasing. The honest "I don't know, here's how I'd find out" answer is the right one; don't overclaim a mechanism.

---

## Q6. Should ASF be extended to reliability-aware fusion, and with what signal?

**Question:** The ASF can handle a sensor when it is explicitly marked as unavailable, but it cannot automatically recognize a degraded sensor that is still producing data. Do you think ASF should be extended to reliability-aware fusion, and what signal could be used to estimate sensor reliability?

### Spoken answer (~60s)
I think that's a reasonable direction, yes. Right now ASF only handles the case where a sensor is explicitly marked unavailable — it has no way to notice, on its own, that a sensor is still producing data but that data has gone bad. My results actually show why that matters: a noisy-but-present LiDAR sensor hurt the model more than a completely absent one, which suggests the model would benefit from knowing "this input looks unreliable" even when nothing external tells it so. As for what signal could drive that, I'd look at things like point count and density per frame compared to what's normal for that sensor, statistical spread of the returned points, and for radar specifically, signal power or SNR-style statistics. Cross-checking sensors against each other is another option — if LiDAR and radar disagree sharply about what's in front of the car, that's itself a signal something's wrong. I haven't implemented or tested any of this, it's a natural next step rather than a result of my thesis.

### Backstage evidence
- Directly answers Discussion.tex Open Question #2 (Discussion.tex:122-129): "would a stronger content-derived availability signal close the gap" — genuinely open in the thesis.
- Candidate signals (point density/count, statistical spread, radar power/SNR, cross-sensor consistency) are my own proposal, not stated in the thesis.
- Radar's `power` column exists in `rdr_sparse` (verified from data: shape `(150000,4)`, columns `[x,y,z,power]`) — a concrete, already-available signal that could seed an SNR-based reliability estimate without new data collection.
- Confidence: "what's missing" framing VERIFIED (Methods.tex/Discussion.tex); candidate-signal list UNVERIFIABLE as a thesis claim (own synthesis).

### Likely follow-ups
- "Wouldn't a learned reliability signal just reproduce whatever the backbone already implicitly does?" — fair challenge; honest answer is you don't know, ties back to the Q5 "cause not established" ambiguity.
- "Isn't this the same idea as NIS (noise-induced shifts), which you disabled?" — distinguish clearly: `noise_induced_shifts` (radar, SNR-dB-based) is a corruption *model*, not a reliability *detector* — related concept, opposite direction.

### Risk flag
Low — this is future-work territory the thesis already gestures at. Main risk is conflating "signal for injecting realistic noise" with "signal for detecting unreliable data" if pressed quickly.

---

## Q7. Frame deletion crashes the pipeline — gap between model-level and system-level availability awareness?

**Question:** ASF is designed to handle sensor unavailability, but I noticed frame deletion also causes the whole inference pipeline to crash. Does this reveal a gap between model-level availability awareness and system-level robustness, and how could this be addressed?

### Spoken answer (~75s)
Yes, and that's actually one of my clearer findings. ASF can gracefully handle a sensor it's explicitly told is missing, but frame deletion isn't that — it deletes a frame's data without telling the model anything, and the pipeline doesn't just perform worse, it crashes outright, for all three sensors, with no prediction produced at all. For radar and LiDAR specifically, the missing frame gets zero-filled into an empty point cloud, and ASF's sparse-convolution backbone throws a runtime error on that zero-voxel input — it's not built to accept a legitimately empty scan. So yes, this is exactly the gap you're describing: model-level availability-awareness assumes a clean, external signal tells it what's missing, but it has no tolerance for malformed or unexpectedly empty raw input arriving on its own. In a real vehicle I don't think you'd want the perception model to be the thing that catches this — you'd want a validation layer in front of it that either flags a degenerate frame properly through the same availability mechanism, or holds the last good frame, before anything reaches the backbone at all.

### Backstage evidence
- Thesis's exact mechanism (Results.tex §5.2.5, "Frame Deletion: Uniform, Non-Graceful Failure Across All Three Sensors"): *"For radar and LiDAR, the None frame is zero-filled into an empty point cloud, and ASF's sparse-convolution backbone raises a RuntimeError on that zero-voxel input. For camera, the frame is dropped rather than zero-filled, and this also crashes the pipeline."* VERIFIED, direct quote from compiled thesis text.
- Frame_deletion excluded entirely from CRI and diversity-axis analysis "for all three modalities, not only camera" per this section — matches Methods.tex:442.
- **Discrepancy found, flag before using this in the room**: a separate engineering audit (`docs/vAIlt/06_Results/row-table-integrity-audit-2026-08-31.md`, same date range as the thesis's own analysis) documents that `lidar_frame_deletion_*` and `radar_frame_deletion_*` conditions were **rerun and fixed** between an earlier backup and the current build — row counts jumped from 10-300 rows (crashed) to 37,892-40,113 rows (near-full coverage), explicitly logged as "crashed→fixed rerun." Only `camera_frame_deletion_*` remains genuinely broken in that audit (144 `camera_frame_deletion_new` Alvis jobs crashed with container exit=134, "only 1 partial prediction file written before abort"). The 22-condition analysis scope excludes frame_deletion uniformly across all three modalities per a 2026-08-25 policy decision — which **predates** the lidar/radar fix — so it's unclear whether this exclusion was ever revisited after lidar/radar started producing usable data, or whether the "fix" only affected ingest-side row merging rather than the underlying RuntimeError itself. **Not resolved from documentation alone.**
- Confidence: RuntimeError mechanism VERIFIED (direct thesis quote); "still crashes for all three modalities" framing SUPPORTED but has a documented internal inconsistency worth checking before stating it flatly.

### Likely follow-ups
- "So does frame_deletion actually still crash for LiDAR and radar, or was that fixed?" — honest answer if asked directly: "The thesis treats it as crashing uniformly across all three sensors and excludes it entirely for consistency; there's an engineering log suggesting LiDAR and radar were later rerun successfully, but I haven't reconciled whether that changes the crash finding or just fixed a data-merging step downstream of it. I'd want to check that before revising the claim."
- "Why does a zero-voxel input crash a sparse-conv backbone — isn't that a basic edge case to handle?" — agree, this is a legitimate input-validation gap in the model implementation, not a subtle robustness finding.
- "How would you fix this at the system level?" — input-validation layer ahead of the model that catches degenerate frames and either raises the proper availability flag or holds the last valid frame, plus a watchdog/fallback so an inference-time exception doesn't take down the whole pipeline (ties to Q4's hardware-level health monitoring answer).

### Risk flag
The lidar/radar "fixed rerun" discrepancy is a genuine, unresolved finding that could contradict a flat "crashes for all three modalities" statement if the examiner has independently looked at the row-level data. Recommend checking this before the defense — either confirm the fix only touched data-merging (crash claim stands) or confirm the RuntimeError was actually resolved (claim needs updating in how confidently you state it).
