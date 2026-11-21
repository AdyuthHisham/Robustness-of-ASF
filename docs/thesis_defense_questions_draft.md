# Thesis Defense Questions — "Robustness of Availability-Aware Sensor Fusion Under Synthetic Sensor Corruption"

Every question traces to a specific quote/claim in `thesis_report/Main.md` and, where noted, a `MASTER_AUDIT.md` finding. Each was independently re-verified by a fresh subagent against the source files before inclusion.

---

## Methodology Soundness

**[§4.4 "Why Noises, and Which Ones"; §6.3.1]** "Radar and LiDAR share the same σ schedule by design – 0.1 m (low), 1.0 m (medium), 2.0 m (high)" combined with the Discussion's claim: "Applying an identical noise magnitude to both point-cloud modalities means the gap between how much each degrades reflects the model's dependence on that modality."
**Question.** The K-Radar sensor table gives 4D radar range resolution 0.46 m and a 0.4 m radar-cube voxel grid, versus LiDAR accuracy of ±2.5–8 cm (OS2-64) / ±0.5 cm (OS1-128). At "low" severity (0.1 m), the injected noise is already below radar's own native resolution but 1.25–4× LiDAR's native accuracy; at "medium" (1.0 m) it is still sub-voxel for radar but ~15–40× LiDAR's accuracy. Doesn't an identical σ in metres confound absolute noise magnitude with each sensor's own native measurement precision, undermining the claim that the resulting differential degradation cleanly "reflects the model's dependence on that modality" rather than reflecting how much of that noise each sensor's own resolution already absorbs?
*Why it matters:* this equal-σ choice is never justified against native sensor resolution anywhere in the document — yet it underwrites the thesis's central "LiDAR is uniquely fragile" argument.
*A strong answer would address:* whether severity should have been normalized per-sensor rather than in absolute metres, and whether doing so would still show LiDAR-specific vulnerability or partly explain it away.

**[§4.6 Evaluation Metrics — F1]** "the harmonic mean of precision and recall at a single fixed confidence threshold... rather than swept across recall thresholds."
**Question.** No numeric threshold value is given anywhere, nor whether it was fixed once or re-optimized per condition. Given the Discussion's claim that "corruption in this sweep acts almost entirely on the detector's decide-to-report threshold" (§6.2), an unspecified, unmoved threshold could itself drive part of F1's apparent collapse.
*Why it matters:* F1's cited advantage over AP (calibration sensitivity) is only interpretable if the reader knows what threshold is held fixed.
*A strong answer would address:* the actual threshold value/procedure, and whether a per-condition-optimal threshold changes any headline finding.

**[§4.6 Evaluation Metrics — reliability floor]** "$N>30$, with a softer small-sample ceiling at $N>90$... a fixed threshold chosen to keep sampling noise on a count-based metric acceptably small."
**Question.** No power/variance analysis or citation anywhere justifies 30 (or 90) versus, say, 50 or 100. What quantitative basis supports these specific cutoffs?
*Why it matters:* this floor gates which stratified findings in Chapter 5 count as reliable versus fragile.
*A strong answer would address:* what sampling-noise magnitude at N=30 was estimated acceptable, and sensitivity of the chapter's conclusions to moving the floor.

**[§6.4 Table 6.1, cross-referenced with §5.1.2/Table 5.1]** Table 6.1 attributes a "6–13 percentage point" LiDAR gap between ASF's own branch-exclusion ablation and this thesis's zero-fill results to the difference in absence *mechanism*.
**Question.** Table 5.1 already documents a 3.2–5.6% baseline gap between the two studies' own pipelines "under an otherwise matched evaluation protocol" (candidate cause left unquantified in Future Work), and Table 6.1's discussion never revisits this as a confound. How much of the "6–13 percentage point" gap could be pipeline-baseline noise rather than the branch-exclusion-versus-zero-fill mechanism it's attributed to?
*Why it matters:* this is the thesis's key corroborating evidence for its central "manual declaration does real work" claim.
*A strong answer would address:* whether the baseline gap's magnitude/direction is consistent with explaining away part of the 6–13 point difference.

---

## Correctness / Internal Consistency

**[§4.6 ASE correction claim; §4.7 "cross-product anomaly analysis"]** "An earlier implementation of this project's metrics code computed ASE from an incorrect per-axis min/max approximation rather than true box-overlap IoU... this was identified and corrected in the pipeline before any of the figures reported in this chapter were computed."
**Question.** `MASTER_AUDIT.md` **A-3-01** documents that `crossproduct.py`'s `_tp_error_metrics` — part of the cross-product analysis stage §4.7 names as this thesis's own — still uses the old min/max-volume ASE approximation, diverging from the corrected true-IoU formula used in sibling `master_metrics_table.py`/`heatmaps.py` (repro: 0.667 vs. 0.75 for the same box pair). Does the "corrected before any figures" claim hold for whatever feeds the "anomaly-detection method used elsewhere in this chapter" (§5.2.3), or could that step draw on the uncorrected formula?
*Why it matters:* the thesis makes a blanket correctness claim the codebase doesn't uniformly satisfy, with no way for the reader to tell which figures are covered.
*A strong answer would address:* which script computed which reported number, and confirmation the anomaly-flagging path avoids the uncorrected formula.

**[§4.7 "cross-product anomaly analysis"]**
**Question.** `MASTER_AUDIT.md` **A-7-01** documents that `crossproduct.py`/`run_analysis.py`/`plots.py` still hardcode the superseded `crossproduct/` directory (frozen since 2026-08-31) while the project's own current docs treat `crossproduct_v2/` as canonical, with no code updated. Which output tree did the cross-product analysis actually read from for Chapter 5/6's results, and does that match what's currently called authoritative?
*Why it matters:* Main.md names this stage as part of "this thesis's own pipeline" without enough detail to confirm which artifact tree backs it.
*A strong answer would address:* a direct statement of which directory/run was actually used, checked against the codebase's current state.

**[§4.7 pipeline stages 5–6]** "flattened into a single Parquet table... all downstream metrics... computed from this one ingested table."
**Question.** `MASTER_AUDIT.md` **B-5-01** found `row_table_iou03.parquet` was silently rewritten after a prior integrity audit certified it (same row count, +~200 KB, no explanation on record). Since the row count is unchanged this is minor — what's the likely explanation for the byte-size change, and can it be confirmed no reported statistic was affected?
*Why it matters (minor):* process-hygiene gap, not a challenge to the results' correctness given the unchanged row count.

**[§4.5 "Why Noises, and Which Ones" vs. §5.1.1 "Scope and Verification" vs. Discussion §6.1/§6.2]** §4.5 (methodology) states: "of which 22 are evaluable at full or near-full sequence coverage; the nine `frame_deletion` conditions and **the two** complete-loss conditions are treated separately." §5.1.1 (Results) states instead: "at **22** evaluable conditions (**including the three** `loss_complete_zero` conditions) plus the `frame_deletion` conditions discussed separately." Every citation of this figure in the Discussion chapter (§6.1 line ~1225, §6.2 line ~1239, and again at line ~1373) instead says "**21** evaluable... conditions."
**Question.** Arithmetically, gaussian_noise (3 sensors × 3 severities = 9) + loss_partial (3×3 = 9) + loss_complete_zero (3 sensors × 1 single tier = 3) sums to 21, matching the Discussion chapter's own repeated figure — not the 22 stated in §5.1.1, which contradicts its own arithmetic in the same sentence. Separately, §4.5 says there are "two" complete-loss conditions treated as excluded (grouped with `frame_deletion`), while §5.1.1 and the rest of the document (e.g. the CRI section's "the three `loss_complete_zero` conditions") consistently treat it as three conditions that ARE included in the evaluable set. Which is correct — 21 or 22 evaluable conditions, two or three complete-loss conditions, and are they included in or excluded from that count — and how did §5.1.1's own stated total end up inconsistent with both its own arithmetic and every place in the thesis that cites it?
*Why it matters:* this is the denominator behind several headline claims (e.g. "17 of 22 evaluable conditions," Conclusion RQ1; "20 of 21 evaluable conditions," Conclusion "New Findings") — the two different totals used in different chapters mean at least one of those headline fractions is stated against the wrong base.
*A strong answer would address:* which count (21 or 22) is the intended, correct one; whether §4.5's "two"/excluded characterization of complete-loss is simply an editing error left over from an earlier version of the taxonomy; and a confirmation that every fraction/percentage reported against "the evaluable conditions" elsewhere in the thesis uses the corrected denominator consistently.

---

## Validity of Evaluation

**[§6.1 "Survivorship Bias Beyond the Worst Conditions"]** the 15 non-defaulting conditions' true-positive population moves "no more than −6.28%... to +1.66%... negligible in practice."
**Question.** Elsewhere in the same chapter, comparable single-digit-percent changes (e.g., the largest FP increase in the whole sweep, +3.6%, §6.2; CRI gaps like 0.915 vs. 0.842, §5.2.4) are treated as meaningful. What quantitative threshold — not a qualitative judgment call — distinguishes "negligible" from "meaningful" at this same order of magnitude?
*Why it matters:* the dismissal of survivorship bias outside the six worst conditions isn't held to the same standard applied elsewhere in the same analysis.
*A strong answer would address:* a stated, consistently-applied tolerance for population-shift-driven metric comparability.

---

## Generalization / Limitations

**[§5.2.3.1 Weather; §6.3.3]** ASF's camera encoder trains "only on normal or overcast scenes"; yet the thesis's own weather breakdown shows camera staying flat across untrained categories (Fog/Rain/Sleet) with its one dip in a *trained* category (Overcast, attributed to sample noise).
**Question.** Does this run counter to using the training-coverage gap to explain camera's low corruption sensitivity, or is synthetic corruption simply incomparable to natural weather here?
*Why it matters:* the training-gap explanation is offered without testing it against the thesis's own weather-stratified data, which appears to point the other way.
*A strong answer would address:* whether the explanation should be weakened/dropped, and what fits the data better.

**[Conclusion "New Findings"]** the SECOND-voxelizer boundary-discard hypothesis for LiDAR's vulnerability, conceded to "not... explain why near-field points... degrade almost as severely."
**Question (presentation).** This mechanism is introduced only in the Conclusion and never developed in §6.3.1, the Discussion section it belongs to. Why place a mechanism-level claim only in the summary?
**Question (substantive).** Given the admitted gap, what would be needed to actually test the hypothesis and to find a near-field explanation it doesn't cover?

**[Future Work, baseline discrepancy]** an unconfirmed KITTI yaw-conversion bug "flagged as a plausible contributing factor" to the baseline gap, "unquantified," raised only once.
**Question.** Since Gaussian noise perturbs point positions (and derived orientation), could this bug interact non-uniformly with corrupted conditions — e.g. contaminating mAOE or retention ratios — rather than cancelling as a constant offset? Was this checked?
*Why it matters:* if magnitude-dependent, it wouldn't cancel out of $R_b^c$ the way a flat baseline offset would.

---

## Presentation Gaps

**[§5.1.2 vs. Table 5.1 vs. Conclusion]** §5.1.2 calls the regeneration gap "consistently 3–5 AP points," but two of Table 5.1's four deltas are ~2.25–2.27 points — below that range. The Conclusion's "3.2–5.6%" does match the table exactly as a relative figure.
**Question.** Is "3–5 AP points" accurate against the table's own numbers, or should the earlier text use the relative "3.2–5.6%" figure instead?
*Why it matters:* this is the thesis's headline reproducibility number, stated inconsistently in two places.

**[§3.3 Inference — "the unmodified SSD detection head"]** "SSD" is used but absent from the List of Acronyms, which otherwise defines 40+ terms including narrower ones (CASAP, UCP, RTNH).
**Question.** What does SSD stand for here, and why was it omitted from the acronym list?
