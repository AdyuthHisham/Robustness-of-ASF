# Thesis Defense Questions — Verified Set

Source: `docs/Latex_Report/thesis_report/Main.md`. Cross-checked against `.agents/MASTER_AUDIT.md` (kradar_visibility code audit).

**Audit intersection result (checked, not assumed):** `MASTER_AUDIT.md` audits `test-bed/src/Modules/robust_testing/kradar/kradar_visibility` — a separate per-object multi-sensor *visibility-scoring* precomputation tool (`config.py`/`OUTPUT_SCHEMA`, `parser.py`, `radar_visible`, `pipeline.py`). The thesis's own evaluated pipeline (Ch. 4: NoiseInjector → ASF forward pass → `dict_datum_to_kitti` → Parquet → AP/retention/CRI/churn) never references kradar_visibility, `OUTPUT_SCHEMA`, `radar_visible`, `parser.py`, or `description.txt` — zero hits on exhaustive grep of Main.md. **No audit finding maps onto the thesis's methodology or results.** Per the task's own instruction not to force a mapping, the Correctness/Internal-consistency category below is built from contradictions internal to the report itself, not from MASTER_AUDIT.

Every question below was independently verified by a fresh subagent against the report text (and, where relevant, the audit) before inclusion. Nine drafted questions were dropped for weak/unconfirmed premises or no real intersection; 12 survive.

---

## 1. Methodology Soundness

**[§4.5] "Radar and LiDAR share the same σ schedule by design – 0.1 m (low), 1.0 m (medium), 2.0 m (high)... camera uses σ=20/50/80"**
→ What determined these specific numeric values, as opposed to any other severity schedule? The only justification given is a *post-hoc* comparison to the ASF sedan anchor box's width, not a derivation of the values themselves, and the Gaussian-noise citations support the corruption *type*, not this specific σ schedule.
*Why it matters:* if the severity levels were chosen to land at convenient fractions of the vehicle width rather than from any independent calibration (real sensor noise characteristics, prior corruption-benchmark schedules), the "low/medium/high" labels risk being circular — chosen to produce a legible narrative rather than representing physically grounded degradation levels. A strong answer states the actual basis for the schedule (prior literature, sensor spec sheets, or an explicit admission it was arbitrary) and defends why that basis is adequate.

**[§4.6] "a fixed ground-truth-object count floor (N>30, with a softer small-sample ceiling at N>90)... a coarser substitute for a formal interval"**
→ Why N=30 specifically, and what does the report's own admission that this "does not communicate the size of the remaining uncertainty above the floor" imply for every stratified claim in Chapter 5 that clears the floor by a small margin?
*Why it matters:* the entire diversity-axis analysis (Ch. 5.2.3) rests on this binary threshold. A defense-level answer needs to justify N=30 is not simply a round number, and address whether a cell at N=35 is meaningfully more trustworthy than one at N=25.

**[§4.6] CRI formula: mean(AP)/AP_clean divided by log(1+pstdev)+1, "following RoHOI's own naming for the same formula"**
→ The report cites RoHOI only for the metric's *name*, not for a derivation of why `log(1+σ)+1` is the correct variance-penalty form. What is the justification for this specific functional form over a simpler alternative (e.g. a linear or coefficient-of-variation penalty), and how sensitive are the CRI rankings in Table 5.5 to that choice?
*Why it matters:* CRI is used to rank effect families against each other (§5.2.4) and underpins headline claims (lidar_gaussian_noise "has, by a wide margin, the lowest CRI"). If the penalty form is not load-bearing to the ranking, that should be shown; if it is, its choice needs defending beyond a naming citation.

**[§4.5] Frame-deletion interval schedule: N=19 (low), N=5 (medium), N=2 (high)**
→ The text justifies frame deletion as an effect *type* ("following the whole-stream dropout precedent of Seeing Through Fog") but gives no basis for these specific interval values. What determined 19/5/2 rather than any other progression?
*Why it matters:* minor relative to the other methodological questions, but the frame-deletion family turns out to be the one that crashes the pipeline entirely (§5.2.5) — a severity schedule that was never empirically exercised deserves at least the same grounding as the others.

---

## 2. Correctness / Internal Consistency

**[§5.2.5 vs. §4.5/§6.5.1] Frame deletion crashes; loss_complete_zero does not — same zero-fill mechanism, opposite outcome, never reconciled**
→ "For radar and LiDAR, the `None` frame is zero-filled into an empty point cloud, and ASF's sparse-convolution backbone raises a `RuntimeError`" (§5.2.5) — yet `loss_complete_zero`, which also "zero-fills the entire modality's input for the frame" (§4.5), produces clean, usable metrics (pooled AP 42.2 for LiDAR cited in the Discussion). The report notes these are different in kind ("rather than replacing it with zeros the way `loss_complete_zero` does") but never explains what differs at the tensor/shape level that causes one zero-fill to crash and the other not to.
*Why it matters:* this isn't cosmetic — `frame_deletion` is excluded wholesale from CRI and the diversity-axis analysis on the strength of this crash, and RQ3's claim that "frame deletion fails all three [modalities] uniformly" rests on it. A defense-level answer needs to name the actual mechanical difference (shape mismatch vs. valid-but-degenerate tensor, e.g.) rather than just asserting the two are "not the same."

**[Future Work vs. §6.5.1] "Seed variance... checked and ruled out" vs. "a differently-trained ASF checkpoint... was not tested"**
→ §7 states "Seed variance and a software/hardware mismatch were both checked and ruled out as sufficient explanations" for the 3.2–5.6% baseline gap, while §6.5.1 (Limitations) states this thesis evaluates only a single checkpoint and explicitly that "whether the specific findings... would hold for a differently-trained ASF checkpoint (e.g. a different random seed...) was not tested."
*Why it matters:* these read as contradictory unless "seed variance... checked" refers to something other than re-running ASF under different seeds (e.g., reading off ASF's own published seed-variance table, referenced elsewhere for the Sleet/Heavy-Snow discussion) — but the report never states that inline at either location. A strong answer clarifies precisely what analysis "checked and ruled out" seed variance, given no second checkpoint was ever run.

**[§5.1.2 vs. §5.3/§7] Baseline gap stated as both "3–5 AP points" and "3.2–5.6%" with no stated unit distinction**
→ §5.1.2 reports the gap as "consistently 3–5 AP points below," while the Chapter 5 Summary and §7 both report "3.2–5.6%." These are compatible (absolute points vs. relative percentage on a ~70–80 AP base) but the report never states this explicitly anywhere the two figures co-occur.
*Why it matters:* a reader skimming only the Summary or Conclusion could reasonably take "3.2–5.6%" as a second, independent measurement rather than the same figure in different units. Worth asking the author to confirm on the record that no second discrepancy exists.

**[§6.3.2] Restricted radar breakdown given for sedan; no equivalent for bus/truck**
→ "Restricted to sedan's reliably-supported categories... radar's own weakest points all fall under `radar_gaussian_noise_high`" — this per-class restricted breakdown exists only for sedan. No equivalent bus/truck-restricted radar breakdown appears anywhere in the document, beyond the general small-N caveat repeated elsewhere.
*Why it matters:* §6.3.2's claim that "radar's fragility is not confined to a single edge case" is argued largely from the sedan-only breakdown. Since bus/truck is shown elsewhere in the thesis to diverge sharply from sedan under corruption (e.g., the weather/environment class-divergence discussed in §6 itself), omitting the equivalent bus/truck view leaves the generality of the radar-fragility claim asymmetrically supported.

---

## 3. Validity of Evaluation

**[§6.5.2 / Conclusion "New Findings"] Voxelizer-drop hypothesis "was not verified by directly counting dropped points" — but is this actually blocked by lost Alvis access?**
→ The report explicitly ties the *undischargeable* experiment (a LiDAR-only, non-fused detector under the same noise) to lost Alvis compute ("cannot be run now that Alvis compute access is lost," §6.5.2). But the weaker, cheaper check — directly counting how many noise-displaced points SECOND's voxelizer drops near its ROI boundary — is stated as simply "not verified," with no compute-access caveat attached anywhere in the text, and is plausibly computable from already-retrieved local data (point coordinates + the voxelizer's own known bounds) without re-running inference.
*Why it matters:* if this check is in fact locally feasible, its absence is a validity gap that predates the loss of Alvis access, not a casualty of it — the report should distinguish "couldn't do this" from "didn't do this yet." A strong answer states whether the point-count check remains feasible from existing local artifacts and, if so, why it wasn't run before the thesis was finalized.

**[Ch. 4/5, general] No significance testing or variance estimate on the corruption sweep itself**
→ The corruption sweep was run once, deterministically (p=1.0, fixed seed=42, §4.5: "All effects were applied with per-frame probability p=1.0... under a fixed master seed (42)"). Every reported AP/retention/CRI drop is a point estimate with no confidence interval, bootstrap, or repeated-trial variance measure computed on the sweep's own conditions — the N>30 floor addresses sample-size reliability of a stratum's ground truth count, not the run-to-run variance of the corruption injection or inference itself.
*Why it matters:* claims like "AP collapses non-gradually" (§6, Summary) and specific percentage drops (e.g. "−259.9%" FN rise) are treated as exact findings rather than estimates with uncertainty. A defense-level answer should address whether single-seed, single-run point estimates are sufficient to support claims of a "sharp, non-linear decline" versus gradual degradation, or whether that shape claim itself needs a repeated-trial check to rule out single-run noise.

---

## 4. Generalization / Limitations

**[§6.5.1] Single-checkpoint constraint vs. reliance on ASF's own seed-variance table to challenge ASF's headline results**
→ The Conclusion's "New Findings" leans on ASF's *own* seed-variance table (its Table 7) to argue ASF's most-emphasized published numbers (Sleet, Heavy Snow) "sit on... the least statistically stable numbers" — using a cross-seed variance argument against ASF's paper — while this thesis's own results derive from exactly one checkpoint/seed with no equivalent variance characterization of its own findings.
*Why it matters:* this is not a contradiction but an asymmetry worth defending explicitly: the thesis critiques ASF's paper for not flagging seed instability while its own headline findings (the LiDAR-noise collapse) carry no analogous seed-stability characterization. A strong answer explains why this asymmetry doesn't undercut the thesis's own confidence in its single-seed findings, or acknowledges it as an open limitation.

**[Conclusion, New Findings] ASF's Table 7 claim asserted without supporting detail**
→ "ASF's own most-emphasised published results (Sleet, Heavy Snow... 'particularly remarkable') sit on the same seed-variance table's least statistically stable numbers, a tension the paper itself never flags (its Table 7, )" — Main.md gives no numbers, no description of what "least statistically stable" means quantitatively, and no other detail about Table 7 anywhere in the document; this is the only mention of it.
*Why it matters:* this is one of the thesis's more pointed "Contested/New Findings" claims against ASF's own paper, but as written a reader cannot verify it without going to the external source. A defense-level answer should be prepared to state the actual Table 7 numbers and the specific instability measure referenced, on the record.

---

## 5. Presentation Gaps

**[Nomenclature vs. §4.6] N≥30 vs. N>30 — inconsistent floor definition**
→ The Nomenclature table (Corruption Parameters) defines the reliability floor as "N≥30," while §4.6's body text states "N>30" (strictly greater than 30). These are literally different thresholds (a stratum with exactly N=30 is reliable under one definition and unreliable under the other).
*Why it matters:* small, but every reliability judgment made throughout Chapter 5 depends on which of these two thresholds is actually implemented in the analysis code. Should be resolved to one canonical definition before submission.

**[§3.2.2 UCP / §3.2.4 PN] Model hyperparameters n_u, n_n, C_u defined only symbolically, never given numeric values**
→ UCP and PN's equations reference n_u/n_n (how many times the Proj block is applied) and C_u (the shared per-patch vector length), but no numeric value for any of the three appears anywhere in the document, including in the complexity-analysis discussion (O(N_q N_s N_p) etc., where N_q, N_s, N_p, C_u are likewise never instantiated numerically).
*Why it matters:* this is architecture description, not original contribution, so it's a minor completeness gap rather than a methodological flaw — but a reader cannot assess how large ASF's fusion module actually is (parameter count, patch resolution) from the text as written. Worth being able to state these values from memory in the defense even if they're not added to the final text.

---

## Notes on rejected candidates

Dropped after verification: two questions attempting to tie MASTER_AUDIT findings (radar_visible gating, OUTPUT_SCHEMA drift, crossproduct path ambiguity, weather/environment description.txt gap) to the thesis's methodology — confirmed by independent subagent check that **no textual or methodological overlap exists**; the audit covers a disjoint subsystem (`kradar_visibility`) the thesis never references. Forcing these would have violated the task's own anti-hallucination constraint.
