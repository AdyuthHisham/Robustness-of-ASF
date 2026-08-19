# Robustness metric selection for corruption-robustness evaluation

Evergreen reference for choosing/reporting robustness metrics when there's no
second reference/baseline architecture and no downstream planner — i.e.
exactly AMSCUP's ASF/K-Radar constraint. Full per-paper extraction lives in
`docs/lit_survey/metrics/metrics_audit.md` (checked-in project doc, not this
vault); this note is the durable takeaway, not a duplicate of that audit.

## The central finding: most corruption-robustness metrics need a second model

Surveyed 10 papers (Hendrycks & Dietterich's ImageNet-C/P lineage, RoboBEV,
MSC-Bench, Dong et al.'s 3D-detection corruption benchmark, RobuRCDet, RoHOI,
S2R-Bench, others). Nearly every paper's *headline* metric — mCE (RoboBEV,
Hendrycks), CD (Kamann), RRS (MSC-Bench) — normalizes a model's degradation
against a **second baseline model's** degradation on the same corruption
suite. That's a structural dependency, not a hyperparameter: without a second
architecture evaluated identically, none of these are computable, and there's
no legitimate substitute (ground truth can't fill that role — GT is what
error is measured *against*, not a second degradation data point; see the
"can I use GT as baseline" discussion below).

**Key trap**: RoboBEV's own name is commonly invoked ("RoboBEV-style
retention percentage") for a self-relative, no-baseline metric — but RoboBEV's
actual headline metric (mCE) *is* baseline-dependent. What people usually mean
is RoboBEV's secondary metric, **RR/mRR** (`mean(corrupted_score/clean_score)`
across severities and corruption types) — which needs no baseline. Cite RR/mRR
explicitly, not mCE, if there's no second model in the study design.

## Convergent reinvention — pick one name

RR/mRR (RoboBEV), RS/mRS (MSC-Bench), RCE (Dong et al., inverted convention),
Rb/mRb (Gao et al.) are **the same formula**, independently reinvented four
times. AMSCUP's own `compute_robustness.py` (K-Radar submodule,
`scripts/alvis/`) already implements this — its `Rb^c`/`mRb` is this exact
metric, from Gao et al.'s naming. Worth citing all four as convergent
independent formalization (stronger reviewer argument than one citation
alone), but pick one canonical name for the paper.

## Why GT can't substitute for a baseline model

Asked and answered directly: the baseline model in mCE-style formulas exists
to **normalize away intrinsic corruption difficulty** (fog degrades every
detector more than brightness, independent of architecture) — not to validate
predictions, which GT already does via the AP/mAP numerator. GT-matched
against GT gives a zero-error denominator, not a stand-in degradation
reference. The legitimate no-baseline move is self-relative normalization
(RR/mRR, above), which answers a different — and for a single-model study,
more honest — question: "how much does this model degrade from its own clean
performance," not "how does its degradation compare to some other
architecture's."

## CRI: retention + stability, and its severity-count caveat

RoHOI's CRI = `(retention term) × (variance-discount term across severity
levels)`. It contains RR/mRR inside it, so the two aren't independent
metrics — report the retention number alongside CRI, since CRI's discount can
hide whether a bad CRI score is "consistently mediocre" or "good but erratic."

Concrete caveat for a 3-tier (Low/Med/High) severity design: RoHOI validates
CRI at 5 severity levels. A 3-point sample stdev has only 2 degrees of
freedom, so one noisy severity point (small-sample flukes are real — the
seq46 pilot's own `Rb^c` numbers landed in the noise floor on a single
condition) swings the variance-discount substantially, and 3 points is also
the bare minimum needed to detect nonlinearity (e.g. distinguishing "smooth
degradation" from "flat then cliff at one severity") at all. Not a reason to
drop CRI, but a reason to report it as secondary to RR/mRR with the caveat
disclosed, not as a headline number on its own.

## What each metric family actually answers (use to avoid overlap in reporting)

- **Retention (RR/mRR family)**: single scalar per effect×severity — the
  headline comparison table. Doesn't explain *why* an effect hurts.
- **CRI**: retention + severity-curve stability — catches threshold/cliff
  effects a flat retention number would hide.
- **Absolute AP** (not a ratio): required alongside both of the above — a 90%
  retention on a class with 20% clean AP is a much weaker result than 90%
  retention on a class with 80% clean AP, and ratio-only reporting hides that.
  Stratified breakdowns (distance/class/occlusion/weather) should be computed
  on this absolute table; the ratios above are summaries derived from it.
- **TP-error decomposition (mATE/mAOE/mASE)**: operates *below* AP, on
  matched-object error — the only family that can distinguish *how* an effect
  degrades detections (e.g. noise-induced-shifts → translation error with
  boxes still present, vs. Gaussian noise → scale error / more FN as points
  degrade) rather than just *that* it did. mAVE excluded — K-Radar's label
  schema has no velocity ground truth (confirmed, not assumed). mAAE excluded
  — no semantic attribute labels.
- **Frame-level flip/consistency (adapted from Hendrycks' Flip Rate)**: the
  only family on the temporal axis — operates across a sequence's frames, not
  within one. See [[gt-transition-analysis]] for a related but distinct
  per-object approach to the same general question (whether two nominally
  different effects are empirically distinguishable).

## Related

- [[gt-transition-analysis]] — a per-GT-object churn/retention diagnostic
  (stable / corruption-induced-miss / corruption-induced-recovery /
  baseline-failure), implemented as a companion to the aggregate-AP metrics
  above; answers "which objects did a corruption cost" rather than "how much
  did aggregate accuracy drop," and can distinguish a corrupted run that
  costs N detections cleanly from one that costs N+k and recovers k
  elsewhere — invisible to a pure AP-ratio.
- `docs/lit_survey/metrics/metrics_audit.md` — full per-paper extraction,
  exclusion table, and the open-questions resolution log this note
  summarizes.
