# Metrics Literature Audit — AMSCUP / ASF Robustness Evaluation

Phase 1, read-only. Audits `docs/lit_survey/metrics/*.pdf` (10 papers) against AMSCUP's constraints: single fused model (ASF), no second reference/baseline architecture, no planner, K-Radar sequential data, 12-effect taxonomy (radar/LiDAR/camera × frame_deletion + modality-specific effects), 3 severity tiers, stratification by distance/class/occlusion/weather-time-env.

---

## 1. Per-paper metric extraction

### 1903.12261 — Hendrycks & Dietterich, "Benchmarking Neural Network Robustness to Common Corruptions and Perturbations" (ICLR 2019)

ImageNet-C/P; defines the CE/mCE/Relative-CE lineage that nearly every later corruption-robustness paper inherits.

| Metric | Formula | Measures | Baseline req. | Computable for AMSCUP? |
|---|---|---|---|---|
| CE (Corruption Error) | `CE_c^f = Σ_s E_{s,c}^f / Σ_s E_{s,c}^AlexNet` | absolute error under corruption c, normalized to a fixed reference model | fixed baseline model (AlexNet) | **No** — normalizer requires a 2nd model |
| mCE | mean of CE over corruption types | single-number absolute robustness | same as CE | **No** |
| Relative CE | `(Σ_s(E_{s,c}^f − E_clean^f)) / (Σ_s(E_{s,c}^AlexNet − E_clean^AlexNet))` | degradation *gap* (corrupted − clean), cross-model normalized | baseline model's clean+corrupted error | **Partial** — numerator (`Σ(E_{s,c}−E_clean)`, self-relative) is usable; denominator (baseline normalization) is not |
| Relative mCE | mean of Relative CE | aggregate degradation-gap | same | **Partial**, same caveat |
| Flip Probability / Rate / mFR | `FP = 1/(m(n−1)) ΣΣ 1[f(x_j)≠f(x_{j-1})]`; FR normalizes by AlexNet's FP | prediction instability across a temporally-correlated perturbation sequence | raw FP: none; FR: baseline model | **Yes (raw FP, adapted)** — redefine as IoU-matched detection-presence flip rate across K-Radar frames/severities. No baseline needed for the raw form. |
| Top-5 Distance / mT5D | permutation-distance over top-5 class rankings across consecutive frames | ranking churn, finer than binary flip | baseline model; top-5 list | **No** — no natural top-k box-ranking analog in 3D detection |
| Subtype robustness | held-out-subtype accuracy after fine-tuning on seen subtypes | OOD generalization, not corruption robustness | seen/unseen taxonomy | **No** — irrelevant, no such taxonomy in K-Radar |

### 1908.05005 — Kamann & Rother, "Benchmarking the Robustness of Semantic Segmentation Models"

Transplants the Hendrycks CE/Relative-CE machinery onto mIoU; architecture-ablation-centric (backbone A vs. backbone B).

| Metric | Formula | Measures | Baseline req. | Computable? |
|---|---|---|---|---|
| Degradation (D) | `D = 1 − mIoU` | task-appropriate error surrogate | none | **Yes**, trivially substitute `D = 1 − mAP` (or `1 − AP@IoU`) |
| Corruption Degradation (CD) | `CD_c^f = Σ_s D_{s,c}^f / Σ_s D_{s,c}^ref` | ratio of model's degradation to a reference architecture's | 2nd reference model (explicitly required — the whole point of the paper) | **No** |
| Relative CD (rCD) | `(Σ_s(D_{s,c}^f−D_clean^f)) / (Σ_s(D_{s,c}^ref−D_clean^ref))` | degradation-gap, cross-model normalized | reference model | **Partial** — numerator alone (self-relative degradation gap) usable, same as Relative CE above |
| SNR corruption-calibration formula | `log2(2^Φc + w_s(N_lum+N_chrom))` | calibrates severity levels of a proposed noise model | n/a (design tool, not eval metric) | Not an evaluation metric — relevant only as prior art for realistic sensor-noise *design*, not scoring |

### 2004.08745 — Philion, Kar, Fidler, "Learning to Evaluate Perception Models Using Planner-Centric Metrics" (CVPR 2020)

Proposes PKL, a planner-conditioned KL-divergence metric.

| Metric | Formula | Measures | Baseline req. | Computable? |
|---|---|---|---|---|
| PKL | `Σ_Δ D_KL(p_θ(x_{t+Δ}|o*) ‖ p_θ(x_{t+Δ}|A(s)))` | how much a detector's errors would change a downstream planner's trajectory distribution | trained neural planner, ego-trajectory GT, HD map layers, ≥2s of temporal context | **No** — needs planner + map data K-Radar doesn't have. Categorically out. |
| NDS (reused, not novel here) + mTP error terms | standard nuScenes formula | composite detection quality + per-attribute error | GT-matched detections only | **Yes** — no planner needed for NDS itself, only for PKL |
| FN/FP sensitivity analysis | re-score PKL after removing/injecting boxes | ranks which errors are most planner-dangerous | planner | **No**, same blocker as PKL |

### 2303.11040 — Dong et al., "Benchmarking Robustness of 3D Object Detection to Common Corruptions in Autonomous Driving" (CVPR 2023)

KITTI-C/nuScenes-C/Waymo-C, 27 corruptions, 24 detectors. Self-relative by design — most directly reusable of the batch.

| Metric | Formula | Measures | Baseline req. | Computable? |
|---|---|---|---|---|
| AP_cor | `(1/|C|)Σ_c (1/5)Σ_s AP_{c,s}` | mean detection accuracy across all corruption types/severities | none — same model only | **Yes** |
| RCE (Relative Corruption Error) | per-cell: `(AP_clean−AP_{c,s})/AP_clean`; overall: `(AP_clean−AP_cor)/AP_clean` | % performance drop relative to the model's *own* clean AP | none — self-normalized | **Yes** — structurally identical to the "RoboBEV-style retention" AMSCUP already plans to use |
| Per-category RCE (weather/sensor/motion/object/alignment subsets) | same RCE, subset-averaged | category-level degradation | none | **Yes** |

### 2304.06719 — Gao et al., "Benchmarking Robustness of AI-Enabled Multi-sensor Fusion Systems" (ESEC/FSE 2023)

7 camera+LiDAR fusion systems, 13 corruptions incl. spatial/temporal misalignment.

| Metric | Formula | Measures | Baseline req. | Computable? |
|---|---|---|---|---|
| IOU | standard | box overlap | none | Yes (already standard) |
| AP (R40) | standard | detection accuracy | none | Yes |
| MOTA | `1 − Σ_t(FN+FP+IDSW)/Σ_t GT` | tracking accuracy over time | tracker + consistent-ID GT tracks | **No** — no tracker attached to ASF |
| RMSE (depth completion) | `sqrt((1/m)Σ(d_p−d_g)²)` | dense depth error | dense depth GT | **No** — wrong task (ASF is 3D detection, not depth completion) |
| Rb_c^s | `P_c^s / P_clean` | per-corruption/severity retention ratio, same model | none | **Yes** — same structure as RCE above |
| mRb | mean of Rb_c^s | aggregate retention | none | **Yes** |
| Spatial-misalignment corruption formula | `p_cam = T_velo^cam · p_li` perturbed by ≤2° rotation | corruption *generation*, not a metric | n/a | Relevant as a corruption-design reference for a camera/LiDAR/radar alignment-perturbation effect, not a scoring metric |

### 2306.03454 — Xie et al., "RoboBEV: Towards Robust Bird's Eye View Perception under Corruptions"

The paper AMSCUP's "RoboBEV-style retention percentage" convention is presumably named after. **Critical finding: its headline metric (mCE) needs a second baseline model; its retention metric (RR/mRR) does not.**

| Metric | Formula | Measures | Baseline req. | Computable? |
|---|---|---|---|---|
| CE_i / mCE | `CE_i = Σ_l(1−NDS_{i,l}) / Σ_l(1−NDS_{i,l}^baseline)`; mCE = mean over i | candidate model's degradation *relative to a fixed baseline model's* degradation | **explicit 2nd baseline model** (DETR3D in the paper) evaluated identically | **No** |
| RR_i / mRR | `RR_i = Σ_l NDS_{i,l} / (3·NDS_clean)`; mRR = mean over i | retained fraction of the model's *own* clean performance under corruption | none — self-relative | **Yes** — this is the metric AMSCUP should actually mean by "RoboBEV-style retention" |
| NDS + mATE/mASE/mAOE/mAVE/mAAE | standard nuScenes formula | composite score + per-attribute TP error | GT-matched detections | **Yes**, with caveat: mAVE needs consecutive-frame velocity GT (check K-Radar), mAAE needs semantic attribute labels (likely absent from K-Radar) |
| Corruption severity remap (ImageNet-C 1–5 → Easy/Mod/Hard 3-tier) | per-corruption table | severity-tier design convention | n/a | Precedent for AMSCUP's 3-tier design, not a metric |
| Camera Crash / Frame Lost (temporal corruption types) | persistent camera-set drop / per-frame independent drop at `p=severity/6` | novel *corruption types*, not metrics | sequential multi-view data | Directly relevant as corruption-design precedent for `frame_deletion`-family effects (see §4 discussion below) |

### 2501.01037 — MSC-Bench, "Benchmarking and Analyzing Multi-Sensor Corruption for Driving Perception"

16 camera+LiDAR corruptions, 6 detectors, 4 HD-map constructors. This *is* essentially the RoboBEV-lineage self-relative framework, formalized cleanly.

| Metric | Formula | Measures | Baseline req. | Computable? |
|---|---|---|---|---|
| RS / mRS | `RS_i = Σ_l Acc_{i,l} / (3·Acc_clean)`; mRS = mean over i | same-model retention across corruption types/severities | none | **Yes** — mathematically identical to RoboBEV's RR/mRR |
| RRS / mRRS | `RRS_i = Σ_l Acc_{i,l}/Σ_l Acc_{i,l}^base − 1` | candidate-vs-baseline relative degradation | 2nd baseline model | **No** |

### 2502.13071 — RobuRCDet, "Enhancing Robustness of Radar-Camera Fusion in Bird's Eye View" (ICLR 2025)

Proposes a robust radar-camera detector; not primarily a metrics paper, but has the most rigorous **radar-specific corruption formulas** of any paper surveyed — directly relevant since ASF ingests 4D radar.

| Metric/formula | Formula | Measures | Baseline req. | Computable? |
|---|---|---|---|---|
| NDS, mAP, mATE/mASE/mAOE/mAVE/mAAE | standard | task accuracy + TP error decomposition | GT-matched detections | Yes / Partial (mAVE, mAAE — same K-Radar-annotation caveat as above) |
| No novel corruption-robustness metric proposed | Table 2 just reports raw NDS/mAP per condition | — | — | n/a |
| Radar corruption formulas: key-point missing, spurious points (`p_n = p ∪ p′, p′~N(δ,σ), σ~U(1,50)`), point-shifting, non-positional (RCS/velocity) disturbance | explicit stochastic formulas | corruption *generation*, not evaluation | n/a | Reference for designing ASF's radar `gaussian_noise`/`noise_induced_shifts`/`loss_partial` effects; not a scoring metric |

### 2507.09111 — RoHOI, "Robustness Benchmark for Human-Object Interaction Detection"

Not a 3D-detection paper, but its two metrics are architecture-agnostic and were explicitly designed under the same no-baseline-model constraint AMSCUP has.

| Metric | Formula | Measures | Baseline req. | Computable? |
|---|---|---|---|---|
| MRI (Mean Robustness Index) | `(1/C)Σ_c (1/L_c)Σ_l M_{c,l}` | plain mean task metric across corruptions/severities, **no clean normalization** | none | **Yes** — but weaker than RS/mRR since not clean-normalized |
| CRI (Composite Robustness Index) | `(1/C)Σ_c [(M̄_c/M_clean) × 1/(log(1+σ_c)+1)]` | clean-normalized retention, **discounted by cross-severity instability** (σ_c = std of per-severity scores) | none — self-relative, but needs ≥2 severity levels per corruption for σ_c to be meaningful (paper uses 5) | **Yes** — the most informative single-model metric surveyed: rewards models that degrade both *little* and *consistently* |

### s41597-025-06255-3 — S2R-Bench, "A Sim-to-Real Evaluation Benchmark for Autonomous Driving" (Scientific Data 2025)

Not a metrics paper — a dataset descriptor validating sim-corruption-toolkit fidelity against real corrupted data.

| Metric | Formula | Measures | Baseline req. | Computable? |
|---|---|---|---|---|
| 3D AP, BEV AP | standard KITTI-style, IoU=0.5, moderate difficulty | detection accuracy | GT boxes only | **Yes** (confirms standard AP is the norm; nothing novel) |
| Percent gap / "30% satisfactory simulation" threshold | `(AP_real−AP_sim)/AP_real` narrated per-cell; ad hoc 30% cutoff | sim-vs-real fidelity, **not** model robustness | paired real-corrupted + sim-corrupted datasets for the same scenario | **No** — answers a different question (sim fidelity) than AMSCUP's (robustness under corruption); do not conflate despite superficially similar arithmetic |

---

## 2. Source conflicts

1. **"RoboBEV-style retention percentage" is ambiguous and, read literally, points at the wrong metric.** RoboBEV's headline metric is **mCE**, which requires a second baseline model (DETR3D) — not computable for AMSCUP. The metric that actually matches AMSCUP's stated convention is RoboBEV's **secondary** metric, **RR/mRR**, which is self-relative. AMSCUP's write-up should cite RR/mRR explicitly and note the disambiguation, so a reviewer familiar with RoboBEV doesn't assume mCE is being computed without a baseline.

2. **The same self-relative retention formula has been independently reinvented under five names with no cross-citation reconciling them**: RoboBEV's RR/mRR (2306.03454), MSC-Bench's RS/mRS (2501.01037), Dong et al.'s RCE (2303.11040, inverse convention — reports the drop, not the retained fraction), Gao et al.'s Rb/mRb (2304.06719). All four compute `mean over corruptions/severities of (corrupted_metric / clean_metric)`, differing only in whether they report the ratio or `1 − ratio`, and in which base task-metric (NDS vs. AP vs. IOU-derived) plugs in. This is not a genuine disagreement — it's convergent independent formalization of the same quantity — but AMSCUP should pick one canonical name+formula and cite the convergence explicitly (defensible as "multiple independent works converge on this formulation," a stronger reviewer argument than citing one paper alone).

3. **CE-style (baseline-normalized) formulas are structurally consistent but all inapplicable**: Hendrycks' CE (top-1 error), Kamann's CD (`1−mIoU`), RoboBEV's CE_i (`1−NDS`) all require a fixed reference/baseline model in the denominator. No conflict in definition — just confirms the baseline-dependency blocker is universal across this metric family, not paper-specific.

---

## 3. Recommended metric stack

**Primary — Retention metric (self-relative, no baseline needed):**
`RR_i = (1/L)Σ_l M_{i,l} / M_clean`, aggregated to mRR (or `1 − RR_i` if reporting as degradation). Use RoboBEV's RR/mRR naming (most field-recognized), cite MSC-Bench RS/mRS, Dong et al. RCE, and Gao et al. Rb/mRb as convergent independent formulations (addresses conflict #2 above), and explicitly disambiguate from RoboBEV's mCE (conflict #1). `M` = whatever composite/AP metric ASF already reports (mAP@IoU or an NDS-style composite if the true-positive error terms below are adopted).

**Secondary — Composite Robustness Index (RoHOI, 2507.09111):**
`CRI = (1/C)Σ_c [(M̄_c/M_clean) × 1/(log(1+σ_c)+1)]`. Adds a variance penalty across the 3 severity tiers on top of RR/mRR. This is the one metric in the survey that distinguishes "degrades a little but reliably" from "degrades unpredictably" — directly useful given AMSCUP's 3-tier severity design, since an effect with high retention-mean but high cross-severity variance (e.g., erratic behavior at Medium relative to Low/High) would be flagged by CRI but invisible to RR/mRR alone. Caveat: RoHOI validates this with 5 severity levels; with only 3, σ_c is a noisier estimate — worth a footnote acknowledging this, not a blocker.

**Tertiary — Raw/absolute reporting (both required alongside the above, not standalone):**
`AP_cor` (Dong et al.) or plain per-corruption/per-severity `1 − mAP` tables (Kamann's D, generalized). Absolute performance must be reported alongside retention %, because a high retention percentage on a task the model was already bad at (or a low retention percentage on a task near ceiling) is not informative alone — this is the same reasoning Hendrycks & Dietterich give for reporting both CE and Relative CE.

**Diagnostic — TP-error decomposition (NDS-style: mATE, mAOE, mASE):**
Translation and orientation error terms computed on GT-matched detections — no planner, no baseline, no tracker needed. This is the metric most likely to **distinguish NIS from Gaussian noise**: noise-induced shifts should manifest primarily as translation error (mATE) with detections still present, while Gaussian noise on radar/LiDAR returns is more likely to inflate false-positive/false-negative rates and scale error (mASE) as spurious/degraded points corrupt box regression. Report these per-effect, not just aggregated — this is exactly the analytical lever the taxonomy needs to justify NIS and Gaussian-noise as distinct rather than redundant effects.
- **mASE (scale error)**: usable — K-Radar labels include box dimensions (`l, w, h`), so this is computable from GT-matched detections with no additional dependency.
- **mAVE (velocity error)**: **excluded** — K-Radar's label schema has no velocity data (confirmed, §5.2). Do not approximate via finite differences across frames without separately validating that a frame-to-frame position-derivative estimate is reliable enough to serve as ground truth; that validation is out of scope here.
- **mAAE (attribute error)**: excluded — K-Radar likely lacks the semantic attribute labels (moving/parked, sitting/standing-style) this requires; unconfirmed but treated as unavailable pending a schema check, consistent with §4.

**Diagnostic — frame_deletion vs. loss_complete: basic feasibility check, not a full flip-rate diagnostic (see §5.4):**
A full IoU-matched detection-presence flip-rate metric across complete, unsampled sequences (adapted from Hendrycks' Flip Rate, 1903.12261) remains the methodologically correct way to test whether these two effects have distinguishable temporal signatures, but is out of scope for now per your direction. §5.4 below defines a reduced-scope, re-analysis-only check using the sweep data that already exists on Alvis — explicitly a directional/feasibility signal, not a statistically powered result.

**Stratification:** all of the above (RR/mRR, CRI, raw AP, TP-error decomposition) should be computed per stratum (distance bin, object class, occlusion proxy, weather/time/environment) as well as globally — none of the recommended metrics have a structural dependency that blocks stratified computation, since they're all single-model, GT-matched, per-frame/per-object quantities that aggregate cleanly by subgroup.

---

## 4. Excluded metrics

| Metric | Source | Missing dependency |
|---|---|---|
| mCE, CE_i (RoboBEV) | 2306.03454 | 2nd baseline model (DETR3D in original paper) |
| CE, mCE, Relative CE, Relative mCE (fully normalized) | 1903.12261 | fixed reference model (AlexNet) for normalization |
| CD, rCD (fully normalized) | 1908.05005 | 2nd reference architecture — explicit point of the paper |
| RRS, mRRS | 2501.01037 | 2nd baseline model |
| PKL | 2004.08745 | trained neural planner + HD map layers + ego-trajectory GT — none exist for ASF/K-Radar |
| FN/FP sensitivity analysis (PKL-based) | 2004.08745 | same planner dependency |
| MOTA | 2304.06719 | tracker module + consistent-ID GT tracks — ASF has no tracker |
| RMSE (depth completion) | 2304.06719 | wrong task (dense depth, not 3D detection) |
| Top-5 Distance / mT5D | 1903.12261 | no top-k class-ranking analog for 3D boxes |
| Subtype robustness | 1903.12261 | requires a seen/unseen subtype taxonomy, irrelevant to sensor corruption |
| mAAE | 2306.03454, 2502.13071 | semantic attribute labels (moving/parked etc.), likely absent from K-Radar — verify before final exclusion |
| mAVE | 2306.03454, 2502.13071 | per-object velocity ground truth — confirmed absent from K-Radar's label schema (§5.2) |
| Percent-gap / "30% satisfactory simulation" | s41597-025-06255-3 | paired real-corrupted + sim-corrupted datasets for the same scenario — answers sim-fidelity, not robustness |

---

## 5. Blocking questions — resolved

### 5.1 Base task metric — RESOLVED

Analyzed the existing Alvis inference outputs and the tooling already built around them (`repos/K-Radar/scripts/alvis/compute_robustness.py`, parsing `complete_results.txt` as written by `pipelines/pipeline_detection_v1_0.py:validate_kitti_conditional`). This settles the question empirically rather than by new design choice:

**The base metric is already fixed by the existing pipeline**: standard K-Radar KITTI-style AP, reported per `(conf_thr, condition, class)` block, with:
- **View**: both BEV and 3D (`bev`/`3d` rows)
- **IoU thresholds**: `{0.7, 0.5, 0.3}`, all three always reported per block
- **Class**: per-class (`sed`, i.e. sedan, etc. — not pre-averaged)
- **Confidence threshold**: swept (multiple `Conf thr:` blocks per file)
- **`Rb^c` is already implemented** on top of this exact grid: `Rb^c = corrupted_AP / original_AP`, computed per (conf_thr, condition, class, view, iou) cell, aligned by matching IoU value (not index) between the original and corrupted runs' block lists — see `compute_robustness.py:110-153`.

No new metric needs to be defined. **RR/mRR and CRI (§3) should be built as an aggregation layer directly on top of this existing per-cell `Rb^c` output**, not as a parallel metric computed from scratch — i.e., `RR_i` = mean of `Rb^c` over severities within corruption type `i` (already the shape `compute_condition_report` produces per condition; `mRb` in the existing code is in fact already RR/mRR's formula, just under Gao et al.'s naming rather than RoboBEV's — reinforcing the naming-conflict note in §2.2). CRI's variance term (`σ_c`) is the one addition not yet present: computed as the stdev of `Rb^c` across the severity triple (low/medium/high) within a condition, per cell, before the `1/(log(1+σ_c)+1)` discount is applied.

One open implementation detail carried into this: whether RR/CRI report at the **per-class, per-view, per-IoU granularity** (matching what `compute_robustness.py` already emits, maximally informative but a large table) or a **pre-aggregated single number per corruption/severity** (mean over class/view/IoU, matching the mRb summary `compute_robustness.py` currently prints). Recommend keeping both: full per-cell table for the stratified analysis (§3, distance/class/occlusion/weather breakdowns need the per-class granularity anyway), single aggregate number for headline reporting — this is not a blocker, just a reporting-layout decision for Phase 2.

### 5.2 mAVE — RESOLVED, excluded

Confirmed: K-Radar's label schema has no velocity data. mAVE is dropped from the TP-error diagnostic entirely — not "conditionally usable pending verification" as originally hedged in §1/§3, but excluded outright. The TP-error decomposition is limited to translation (mATE-equivalent) and orientation error; scale error (mASE-equivalent) — box dimension mismatch — remains available since K-Radar labels include `l, w, h`. Table in §4 updated accordingly.

### 5.3 CRI severity-count sensitivity — explained in depth

RoHOI's CRI formula is `CRI = (1/C) Σ_c [(M̄_c/M_clean) × 1/(log(1+σ_c)+1)]`, where `σ_c` is the standard deviation of the per-severity scores `{M_{c,1}, ..., M_{c,L_c}}` for corruption type `c`. The concern is that `σ_c` is a sample standard deviation estimated from only `L_c` points, and AMSCUP's `L_c = 3` (low/medium/high) against RoHOI's validated `L_c = 5`.

Why this matters concretely:
- **Degrees of freedom**: sample stdev from n=3 has 2 degrees of freedom. It's a legitimate unbiased estimator, but its own sampling variance is large — with only 3 points, a single unusually noisy severity level (e.g. a fluky Rb^c from a small evaluation sample, which the seq46 pilot's own notes already flag — "mean Rb^c = 1.025... no clear degradation signal... noise floor at this sample size, not a real finding") can swing `σ_c` substantially, and that swing propagates directly into the CRI discount factor for that corruption type. With n=5, one noisy point is diluted across more measurements and has proportionally less leverage on the estimate.
- **Shape assumption**: `σ_c` alone doesn't distinguish "monotonically degrading, evenly spaced" (Low→Med→High = 0.9→0.6→0.3, σ≈0.24) from "flat then cliff" (0.95→0.90→0.30, σ≈0.30) — both get penalized similarly by CRI's variance term despite very different practical failure modes (the second is arguably worse — a threshold effect rather than graceful degradation, which is exactly the kind of thing a reviewer would want distinguished for something like the frame_deletion/loss_complete question). With only 3 points this ambiguity is worse, since there's no way to see whether the trend between Low-Med and Med-High is consistent or not — a 3rd data point is the minimum needed to detect nonlinearity at all, and AMSCUP's severity design sits exactly at that minimum, not comfortably above it.
- **What doesn't change**: the retention term `M̄_c/M_clean` (the RR/mRR-equivalent numerator) is unaffected by severity count — its estimate quality depends on per-frame sample size (frames × sequences), not on the number of severity tiers. Only the variance-penalty half of CRI is severity-count-sensitive.

Practical resolution: keep CRI in the stack but **report it as a secondary/diagnostic number alongside RR/mRR, not as the headline metric**, and note the n=3 caveat explicitly wherever CRI is reported (a one-line footnote is sufficient — this is a defensible, disclosed limitation, not a fatal flaw). If a specific corruption type's CRI ranking looks surprising relative to its RR/mRR ranking, treat that as a signal to inspect the raw 3-point Low/Med/High curve directly rather than trusting the summary number — which is exactly the kind of qualitative check the frame_deletion/loss_complete diagnostic below already involves.

### 5.4 frame_deletion vs. loss_complete diagnostic — scope reduced per your direction

Agreed: a full flip-rate diagnostic (§3's original proposal — IoU-matched detection-presence flip rate computed across every frame of full, unsampled sequences, for both effects, at matched severities) is out of scope for now. Revised to a **basic feasibility check**, not a full diagnostic:

1. From the already-run 10-sequence sweep (`obsidianVault/Projects/K-Radar/asf-corruption-study-alvis.md`, "Full sweep infrastructure" §), identify which sequences retained enough consecutive surviving (post-filter) frames to support a same-sequence before/after comparison — each sequence run there is capped at 10 surviving frames via `max_per_seq: 10, frame_select: 'first'`, so consecutivity within that cap needs to be checked per sequence rather than assumed.
2. For those sequences, compare `frame_deletion` (radar/LiDAR, which the notes confirm **crashes the model** at medium/high severity — the spconv backbone aborting on a near/fully-empty point cloud, 40 of the 300 sweep jobs failing this exact way) against the already-flagged-redundant `loss_complete`/`loss_complete_zero` pair on whatever frames both conditions produced usable output for (i.e., `frame_deletion` at low severity only, since medium/high abort before reaching eval — this itself is already informative: `loss_complete_zero` zero-fills and so *doesn't* crash, meaning the two effects' abort behavior alone already diverges at the pipeline level even before considering detection output).
3. Report this explicitly as a **feasibility/directional check, not a statistically powered diagnostic** — the caveats already logged for the sweep (10 frames/sequence, one seed, `Rb^c` not yet computed across the full 300-job sweep as of the 2026-08-17 note) apply here too, and n=1 seed at 3 severities is not enough to support a claim like "these two effects are/aren't distinguishable," only "on this sample, they did/didn't look different."

This does not require any new inference runs — it's a re-analysis of sweep outputs that already exist on Alvis, which keeps it consistent with this being a read-only audit task. If the basic check surfaces something suggestive, that's the justification for later investing in the full flip-rate diagnostic; if not, it can be dropped from Phase 2 scope without having spent the sequence-level re-run cost.

---

Stopping here per instructions — no implementation, no Phase 2 scaffolding until you've reviewed this.
