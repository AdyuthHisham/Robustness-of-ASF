---
title: Exhaustive Cross-Product Analysis — Phase 1 Audit
date: 2026-08-31
status: closed 2026-09-01 — all items resolved against crossproduct_v2/; CRI cross-source dependency remains a standing (non-blocking) limitation
---

# Phase 1 audit: exhaustive cross-product + peer-group anomaly detection

Input confirmed: `repos/K-Radar/outputs/robustness_reports/full_denormalized_table.parquet`
(the only candidate besides an identical-looking copy at
`backups/pre_camgauss_regen_20260831_213750/full_denormalized_table.parquet`,
which is the pre-fix backup — **not** used). Current file: 1,109,616 rows × 33
cols, mtime 2026-08-31 21:38, post camgauss-fix regen per
[[project_crossproduct_regen_20260831]]. Spec quoted 1,109,578 rows — a 38-row
diff, immaterial, consistent with this being a slightly newer regen than
whatever produced the spec's number.

**Important pre-existing context the spec doesn't mention**: a full prior run
of this exact deliverable set already exists at
`repos/K-Radar/outputs/robustness_reports/crossproduct/` — `summary_*.parquet`,
`deltas_*.parquet`, `reports/q1_*.csv` through `q6_*.csv`, `d1`–`d5` anomaly
CSVs, `anomalies.parquet/csv`, `findings.md`, and figures matching this spec's
D-A…D-F / peer-group naming almost exactly. This was very likely built before
the 2026-08-31 camgauss-fix regen. Per [[project_crossproduct_regen_20260831]],
2 vault docs are already known to cite stale numbers from it. **Question 0
below asks whether Phase 2 is a fresh build or a refresh of this existing
output against the new table.**

## Outcome counts (sanity)
TP 648,047 / FP 115,007 / FN 346,562 (sums to 1,109,616 ✓). Matches spec
magnitudes (648,036/114,997/346,545) within the same ~38-row diff.

31 conditions confirmed, exact list matches spec's implied set: 30 corruptions
(camera/lidar/radar × {frame_deletion, gaussian_noise, loss_partial} ×
{low,med,high}) + one `*_loss_complete_zero` per modality (note: spelled
`loss_complete_zero`, not `loss_complete`, in this table — the `ap_robustness_local.json`
side-file inconsistently uses `camera_loss_complete` (no `_zero`) for the same
condition, a naming split to be aware of if cross-referencing that file).
58 sequences, cls = {sed: 916,579 (82.6%), bus: 193,037 (17.4%)} — matches spec.

---

## 1. Unthresholded set?
`row_table_iou03.parquet` has the **same schema as the outcome table** minus
the later-added strata columns (`distance_from_ego_orig`, `n_objs`,
`frame_density`, `distance_bucket`) — it already carries `is_tp`/`is_fp`/`is_fn`
and post-threshold `score`. It is not a raw/unthresholded detection dump; it's
an earlier-stage version of the same fixed-threshold outcome table. I did not
find any raw pre-NMS/pre-threshold prediction dump elsewhere in
`outputs/robustness_reports/`. `ap_robustness_local.json` reports **AP values
per sequence/condition/class already** (`orig_ap_by_cls`, `rb_by_cls` =
robustness ratio), which means AP *was* computed by some upstream process —
but from what input is unclear from this table alone; it isn't reproducible
from `full_denormalized_table.parquet` as given (fixed IoU=0.3, thresholded
score only).
**Verdict: AP/mAP is NOT computable from this table.** Whatever produced
`ap_robustness_local.json` used a different (likely unthresholded, full
score-range) input that isn't in scope here unless you point me to it.

## 2. `matched_gt_row_id` stability
- **Unique within (sequence, frame, condition)**: confirmed, 0 duplicates.
- **NOT globally unique** — it's a small integer (0–2987) reused across
  sequences/frames; it is a per-(sequence, frame) local GT-list index, not a
  persistent object ID.
- **Stable across conditions for a fixed (sequence, frame)**: confirmed by
  direct check — for one fixed (sequence, frame), `matched_gt_row_id=1`
  resolves to identical `gt_loc_x/y/z` (2.67, 0.8, 23.61) across all 28
  conditions present for that frame.
- **Conclusion: churn IS unblocked**, keyed on
  `(sequence, frame_original_or_paired_frame, matched_gt_row_id)` — but see
  Q1 below, because "frame" itself is not consistently keyed across
  conditions (this is the actual blocker for churn/baseline-join, not the ID
  itself).

## 3. Condition parsing
Regex-safe: `^(camera|lidar|radar)_(frame_deletion|gaussian_noise|loss_partial)_(low|medium|high)$`
for 27 rows, `^(camera|lidar|radar)_loss_complete_zero$` for 3 rows, plus the
literal `original`. Clean, no ambiguity, no edge cases found. Proposed
`(modality, effect, severity)` columns: `effect='loss_complete'`,
`severity='zero'` for the three total-loss rows so they still sort under their
modality's severity ladder without a fake numeric rank.

## 4. Coverage — THIS IS WHERE IT GETS BAD

Rows/sequences per condition (full table in audit script output; highlights):

| condition | n_rows | n_seq |
|---|---|---|
| original | 40,356 | 58 |
| camera_gaussian_noise_* | ~40,300–40,400 | 58 |
| lidar_/radar_* (all effects) | 36,300–40,340 | 58 |
| **camera_frame_deletion_low** | **1,674** | **55** |
| **camera_frame_deletion_medium** | **276** | **47** |
| **camera_frame_deletion_high** | **102** | **31** |

`camera_frame_deletion_*` collapses to 0.25%–4% of baseline row count and
loses up to 27 sequences, while `lidar_frame_deletion_high` /
`radar_frame_deletion_high` retain ~94% of rows at full 58-sequence coverage.
Same nominal effect+severity name, wildly different realized magnitude by
modality. Either:
(a) camera frame-deletion severity is parameterized on a totally different
    scale than lidar/radar (e.g., % of *all* frames dropped vs. % of a
    windowed subset), or
(b) there's a bug specific to camera_frame_deletion — e.g. it's dropping
    frames from the eval join, not just corrupting them, or
(c) camera frame_deletion legitimately removes the camera's contribution to a
    frame's prediction set entirely, and what's left in these rows is only
    the rare surviving camera-only detections in an otherwise multi-sensor
    pipeline (plausible, but then the corresponding fusion/lidar/radar
    contributions in the *same frames* should still show up under `original`
    or other conditions with full coverage, and they don't line up because
    of the frame-ID issue in Q1).

**This is not something I can resolve by inspection — Q2 below.**

Common-sequence intersection: **all conditions except the three
`camera_frame_deletion_*` reach 58/58 sequences**; those three cap coverage at
31/47/55. If restricting to the common intersection across *all* 31
conditions per the spec's coverage rule, every cross-condition comparison
would be capped at whatever sequence set the 31-sequence
`camera_frame_deletion_high` condition covers — that would gut coverage for
every other condition's comparisons for no good reason. **Recommend excluding
`camera_frame_deletion_*` from any global common-intersection requirement and
instead computing per-condition-pair intersections** (spec doesn't currently
allow for this; flagging as a rule change, not deciding unilaterally).

## 5. Nulls and strata — a second real blocker

Null pattern for FN/FP is exactly as documented: FN nulls all pred-side fields
(pred_row_id, height/width/length/loc_*, rotation_y, score, iou) and
`distance_from_ego_orig`, 100% as expected; FP nulls all gt-side fields
(matched_gt_row_id, gt_*) 100% as expected; TP has no nulls in either.
`iou` is additionally null for 100% of FP rows (461,569 = 346,562 FN +
115,007 FP), which the spec doesn't call out explicitly but is a sane design
choice — flag it as an assumption I'm encoding, not something in the caveats.

**`n_objs` and `frame_density` are non-null ONLY for `condition == 'original'`**
(40,356 rows) — **null for all 30 corrupted conditions (1,069,260 rows,
96.36% of the table)**. Both are 1:1 with `(sequence, frame)` in `original`
(verified: 13,727 distinct (sequence, frame) pairs in `original`, 0 with
more than one n_objs/frame_density value), and the spec's own caveat #3 says
`frame_density` is "clean-scene-derived, class-pooled, fixed per frame" —
i.e., it's a property of the (sequence, frame) identity, not of the
condition, so a join-back to corrupted rows should be *possible in principle*.
But — see Q1 — the `frame` string differs in format between `original` and
every corrupted condition, so the join key doesn't currently exist. Until
Q1 is resolved, **`frame_density` is usable only as an `original`-only
covariate, and item 9's "stratum sweep including density" and item 6's
cell-size analysis with density cannot include the 96% of the table that is
corrupted.**

Strata distinct values: `weather` = {fog, normal, overcast, rain, sleet} (5,
matches spec), `time_of_day` = {day, night} (2, matches), `environment` = 8
values {alleyway, countryside, highway, mountain, parkinglots, shoulder,
university, urban} (matches spec's count of 8).

## 6. Cell sizes

`(condition × cls × weather × time_of_day)`: 540 cells, 62 with N<30 (11.5%),
115 with N<100 (21.3%).
`(... × environment)`: 1,316 cells, 300 with N<30 (22.8%), 524 with N<100
(39.8%).
Adding environment roughly doubles cell count and roughly doubles the
unreliable fraction. **Recommend: environment as drill-down only, not a
primary stratum** — it's usable for D-C/D-D breakdowns and flat-except-one
detection at fixed (condition, cls), but a primary 5-way group_by
(condition×cls×weather×tod×environment) would have ~40% of cells below a
reasonable reliability floor. Proposed floor: N≥30 for "reliable" (Wilson CI
still fairly wide there, but tighter floors gut coverage further — this is a
judgment call, flagging as a recommendation not a decision).

## 7. `frame_density` binning — BLOCKED

Cannot report a real distribution or propose bin edges: the field is null for
96.36% of rows (see item 5), and even within `original` it's an `n_objs`-style
integer count (1–16, mean 4.07, median 4) per the describe() output, not a
continuous density needing quantile binning necessarily — but I can't assess
skew or propose edges responsibly against 3.6% of the target rows and zero
corrupted-condition rows. **Open project item per spec instruction — not
deciding.**

## 8. Metric feasibility

| Metric | Status | Notes |
|---|---|---|
| P/R/F1 | **Supported** | is_tp/fp/fn are exact per-row outcomes at IoU 0.3, fixed threshold. |
| AP/mAP | **Impossible from this table** | No unthresholded score range available here (see item 1). `ap_robustness_local.json` has AP already computed by an out-of-scope process. |
| mRR/RS, RCE | **Supported** | RCE is just retention ratio math on P/R/F1/mATE etc. from this table's own baseline join — contingent on the item-1/Q1 frame-key fix for the `original` join. |
| mATE/mASE/mAOE | **Supported, TP-only** | loc_x/y/z, height/width/length, rotation_y both pred- and gt-side present on every TP row. `rotation_y` units not documented in schema — need to confirm radians vs degrees and the wrap convention (±π vs [0,2π)) before computing mAOE; I have not verified this yet (Q3). |
| mFR | **Supported** | derivable from FN rate per stratum, same caveats as P/R/F1. |
| CRI | **Located**, not yet formula-checked | `cri_by_effect` appears in `ap_robustness_local.json`, computed per (sequence, effect) — but that's AP-based CRI from the out-of-scope AP source, not something I can independently recompute from this table without AP. If CRI is wanted from *this* table's F1/precision/recall instead, I haven't located a reference formula in-repo to check against — need the paper/spec reference (Q4). |
| Churn | **Supported, conditionally** | ID pairing itself works (item 2); blocked on the `frame` join key mismatch (Q1) for tying corrupted rows back to their `original` counterpart frame. |

## 9. Peer-group feasibility (preliminary, pending Q1/Q2)

Using the 540-cell (condition×cls×weather×tod) grouping as a proxy:
- **(a) sibling conditions at fixed (cls, weather, tod)**: 27 non-original,
  non-loss_complete_zero conditions group into 9 (modality,effect) families ×
  3 severities; at fixed (cls,weather,tod) each family gives a 3-member
  severity ladder — thin (spec wants ≥4 for scoring, these max at 3 plus
  original as an implicit 4th reference point). Workable if `original` counts
  as the 4th member.
- **(b) severity ladders**: same 3-per-family structure, same caveat.
- **(c) stratum sweep at fixed (condition,cls)**: weather(5)×tod(2) = 10 cells
  per condition — well above 4, but ~20% fall under N=30 per item 6, so
  "reliable" membership will vary a lot by condition; camera_frame_deletion_*
  conditions will be mostly `insufficient` given item 4.
- **(d) modality parity at fixed (effect,severity,stratum)**: only 3 members
  (camera/lidar/radar) per group — below the spec's own ≥4 threshold. This
  group type **cannot meet the stated minimum**; either lower the floor for
  this one group type or drop it. Flagging, not deciding.
- **(e) cross-stratum at fixed everything-but-one**: not fully sized yet,
  deferred to Phase 2 since it needs the full group_by table built.

## 10. Dispersion baseline — not computed
Requires the full summary table (2.1) to compute MAD per group type
meaningfully; doing it by hand pre-Phase-2 on a proxy grouping would produce
numbers I'd have to redo anyway. Deferring to Phase 2, first deliverable out
of the group_by.

---

## Blocking questions — STOP, awaiting answers

**Q0.** A prior full run of this exact deliverable set exists at
`outputs/robustness_reports/crossproduct/` (summary/deltas parquets, q1–q6
CSVs, d1/d3/d5 anomaly CSVs, findings.md, figures), apparently pre-dating the
2026-08-31 camgauss-fix regen. Is Phase 2 a **fresh rebuild** overwriting this
directory, or a **refresh** that should diff against and explain what changed
from the prior run? This changes deliverable scope materially (a diff-report
step vs. not).

**Q1 (hard blocker — affects items 1/5/7/9, deliverables 2.2, D-E, D-F density
cuts).** `frame` is formatted as a plain zero-padded index (`"000000"`) under
`condition == 'original'` but as `"XXXXX-YYYYY"` (two 5-digit numbers) under
every corrupted condition — verified 0% overlap in frame strings between
`original` and `camera_gaussian_noise_low` for the same sequence, and by
extension likely all corrupted conditions. This means:
- there is currently **no key to join a corrupted row back to its `original`
  baseline** for the same physical frame (needed for 2.2 baseline deltas, D-E
  churn, and the `frame_density`/`n_objs` backfill in item 5/7).
- I don't know what the two numbers in `"XXXXX-YYYYY"` represent (candidate
  guesses: paired sensor-frame indices for a desync/resample corruption, or a
  {corrupted_frame_idx}-{nearest_original_frame_idx} pairing where the second
  number IS the join key — if so this is trivially fixable by parsing).
This may be related to, or a residual of, the known
[[project_kradar_frame_identifier_bug]] (marked fixed 2026-08-26, "metrics
unaffected but re-sweep/regen pending") — worth checking whether this regen
predates or postdates that fix actually landing in the frame-writing code
path, since the mismatch looks structural rather than a value error.
**I will not guess which half of `"XXXXX-YYYYY"` is the join key. Need either
a pointer to the code that writes this field, or confirmation to treat the
second number as the original-frame index.**

**Q2.** `camera_frame_deletion_{low,medium,high}` retain 4.1%/0.7%/0.25% of
baseline row count and lose 3/11/27 of 58 sequences, while
`lidar_frame_deletion_high` and `radar_frame_deletion_high` retain ~94% at
full sequence coverage for the nominally same effect+severity semantics. Is
this expected (camera frame-deletion parameterized on a different scale, or
architecturally different from lidar/radar because camera predictions vanish
entirely without fallback fusion) or a bug in how camera frame-deletion
severity was applied / how those rows were joined into the eval? This
determines whether `camera_frame_deletion_*` gets included in cross-modality
comparisons (peer group (d)) at all, or is footnoted out.

**Q3.** `rotation_y`/`gt_rotation_y` units and wrap convention for mAOE —
radians or degrees, and is 0 aligned to ego-forward with wrap at ±π or
[0, 2π)? Not verifiable from the parquet alone; need the labeling convention
from K-Radar's label spec or the code that writes `rotation_y` into this
table.

**Q4.** CRI formula: the paper reference to check `cri_by_effect` (present in
`ap_robustness_local.json`, AP-based) against — which paper/section, and do
you want CRI recomputed from this table's F1 (since AP isn't available here,
per item 1) using the same formula shape, or is AP-based CRI from the JSON
file acceptable as an input to Phase 2 (which would mean Phase 2 isn't purely
derived from `full_denormalized_table.parquet` as the spec states)?

**Q5.** Reliability floor for item 6 — I proposed N≥30 as "reliable." Confirm
or override before it's baked into every deliverable's reliable/unreliable
split.

Waiting on Q0–Q5 before any Phase 2 implementation, per spec instruction.

---

## Addendum 2026-08-31 (later same day): full pipeline rerun against the fixed table

Session context: the `weather`/`environment`/`time_of_day` regression this
audit doesn't mention (it postdates the audit — a concurrent 22:45 "original
reingest" run silently degraded these to `normal`/null) was fixed separately
by rejoining sequence-level metadata from a known-good backup, then
`build_denormalized_table.py` was rerun. `full_denormalized_table.parquet` is
now 1,109,578 rows × 34 cols, 0% null on `weather`/`environment`/
`time_of_day`/`frame_density`/`n_objs`, and `frame` is `"{radar_idx}-{lidar_idx}"`
for **both** `original` and every corrupted condition (Q1's format mismatch
resolved).

`scripts/analysis/crossproduct/run_analysis.py` was rerun end-to-end against
this table from `test-bed/src/Modules/robust_testing/kradar/`. Stale
pre-rerun output was backed up to
`backups/pre_crossproduct_rerun_20260831_230859/` before overwriting.

**Q0 (fresh vs. refresh)** — resolved as: refresh in place, overwrite
`outputs/robustness_reports/crossproduct/`, backup taken first. No separate
diff-report was produced as its own deliverable, but the diffs below serve
that purpose.

**Q1 (frame-key mismatch) — RESOLVED.** Confirmed by direct effect on
output: `summary_full_density.parquet` (the density×distance-bucket
marginalization) had **zero** `n_total` rows attributed to any non-`original`
condition in the stale run (100% of density-stratified data was
`original`-only, exactly per audit item 5/7's blocker). Post-fix, corrupted
conditions contribute 832,358 of the table's rows into density-stratified
cells (722,035 of those in `reliable` cells) — the frame-key backfill join
now works as designed. Direct downstream confirmation:
`anomaly_coverage.csv`'s `stratum_sweep` peer-group row (the group type keyed
on frame_density/distance_bucket at fixed condition×cls) went from 2 scored
group-instances per metric to 44, 100% scored either way — a 22x expansion,
present identically across all 7 metrics. No other peer-group type's
`n_group_instances` changed (cross_stratum_tod/weather, sibling_conditions,
modality_parity, severity_ladder — all identical row-for-row to the stale
run), which is the expected signature of a fix that's specific to the
frame_density join and touches nothing else.

**Q2 (camera_frame_deletion_* coverage collapse) — RESOLVED BY DECISION:
`camera_frame_deletion_*` is to be ignored.** User decision 2026-08-31 (later
same day, after this addendum was first written): treat all three
`camera_frame_deletion_{low,medium,high}` conditions as out of scope
entirely, not just for the crossproduct pipeline (which already excluded
`frame_deletion` conditions by design, per `crossproduct.py:17`) but as a
standing project-level decision — no further investigation into whether the
coverage collapse is a parameterization difference or an upstream bug.
Superseded, not open.

**Q3 (rotation_y units) — RESOLVED.** Verified directly from
`full_denormalized_table.parquet`: `rotation_y` (pred) ranges [0.79, 7.07] ≈
[0, 2π), `gt_rotation_y` ranges [-3.34, 3.44] ≈ [-π, π] — both radians, not
degrees. Raw K-Radar label files (`info_label_rev2/*.txt`) store degrees
(confirmed in `datasets/kradar_detection_v1_0.py:341`, values like `177.0`,
`179.9237`); converted via `theta * pi/180` when `is_heading_in_rad=True`.
`crossproduct/metrics.py`'s `angle_error` already wraps the pred-minus-gt
difference correctly via mod-2π to `[-π, π]`
(`np.abs((diff + pi) % (2*pi) - pi)`), and its docstring confirms this is a
genuine heading (not axis-symmetric) because K-Radar's own AOS similarity
`(1+cos(gt-pred))/2` scores a 180°-flipped box 0 (worst). No code change
needed — this was already implemented correctly during the Phase 2 build;
the audit item was a documentation gap, not a pipeline bug.

**Q4 (CRI formula reference) — RESOLVED.** Located in
`repos/K-Radar/scripts/alvis/compute_robustness.py:120`
(`compute_cri`, well-commented): RoHOI (Wen et al., arXiv:2507.09111v3, Eq.
2), `CRI_c = (M̄_c/M_clean) × 1/(log(1+σ_c)+1)`, where `σ_c` is the
**population** stdev (not sample) of raw AP across severity tiers, `M̄_c` the
mean raw AP across tiers, `M_clean` the clean-baseline AP for the same
(conf_thr, cls, view, iou) cell. Deliberately computed from raw AP, not from
retention ratios (`Rb`) — the docstring explains why: stdev isn't
scale-invariant under division, so computing σ from `Rb = M/M_clean` instead
of raw `M` silently rescales the variance penalty. `docs/lit_survey/metrics/
metrics_audit.md` §5.3 already covers the n=3-severity-tier caveat (RoHOI
validates with 5 tiers) as a disclosed limitation: report CRI as
secondary/diagnostic alongside RR/mRR, footnote the tier-count caveat, don't
treat it as a blocker. **Caveat carried forward**: CRI is AP-based, and per
item 1/Q1 of the original audit, AP is not computable from
`full_denormalized_table.parquet` alone — CRI in the crossproduct
deliverable would need to source AP from `ap_robustness_local.json` /
`compute_robustness.py`'s own output, a genuine cross-source dependency, not
something resolvable purely within this table.

**Q5 (N≥30 reliability floor) — CONFIRMED, kept as-is.** Rationale: Wilson CI
half-width for a proportion near 0.5 is still ±~18pp at N=30 (e.g. precision
0.50 → CI [0.33, 0.67]), wide enough that most real effects won't be
CI-significant at this floor, but large enough that point estimates stop
being dominated by single-detection noise (the standard Np≥5, N(1-p)≥5 rule
of thumb for the normal approximation Wilson relies on). Raising to N≥100
would flip ~21.3% of (condition×cls×weather×tod) cells to unreliable (vs.
11.5% at N≥30, per audit item 6) — disproportionately hitting rare
weather×class combinations (bus+sleet, etc.) that are often exactly the
cells peer-group anomaly detection is trying to catch, not noise to be
filtered out. N≥30 stays the floor baked into every reliable/unreliable tag
in `crossproduct.py`/`anomaly.py`.

### Rerun sanity checks
- All 7 marginalization-level summary parquets and 3 deltas parquets have
  identical row/col shapes to the stale run (expected — condition/cls/
  weather/tod/env cardinality is fixed by the schema, not by data
  availability; only null patterns and aggregate values inside cells should
  differ, which they do — see below).
- `reports/anomalies.parquet`: **1,421 total flags** (348 real / 1,073
  small-N artifact / 0 suspected-bug) vs. stale **1,042** (325 real / 717
  small-N / 0 suspected-bug) — materially different, as expected from the
  stratum_sweep expansion above (more scored groups → more candidates for
  both real and small-N flags).
- `q1_significant.csv`: same row count (41) as stale, values shifted only in
  the 5th decimal place — consistent with a correct backfill changing which
  exact frame-level rows get joined/aggregated without moving the
  already-large aggregate metrics much, not a red flag.
- `d1_monotonicity_violations.csv`: 173 rows vs. stale 184 — different
  underlying member set (spot-checked: several stale camera_gaussian_noise
  rows for `sed/fog/day` etc. no longer appear, others do) — a real content
  change, not just a rename/reorder.
- No exceptions in the run log; all expected output files (7 summaries, 3
  deltas, `findings.md`, 20 report CSVs, `anomalies.{csv,parquet}`,
  `anomaly_coverage.csv`, 4 D-figures, 3 anomaly-figures) were freshly
  written with post-rerun mtimes.

Full numeric comparison and file list: see this session's summary in
[[exhaustive-crossproduct-phase2-progress]] and the Daily note for
2026-08-31.

---

## Addendum 2026-09-01: audit checklist closed against `crossproduct_v2/`

Context: the 8/31 fix above was itself built on a table that still had a residual
frame-key defect (see [[exhaustive-crossproduct-frame-key-fix-20260901]]) — fixed
again same day, `crossproduct_v2/` rebuilt from the doubly-corrected table with
`RELIABILITY_FLOOR` also corrected back to 30 (had silently drifted to 100 with no
git history to explain it) and `SMALL_N_CEILING` rescaled 300→90 to preserve the
3x-floor ratio. Full detail: [[crossproduct-rebuild-20260901]].

Closing the remaining checklist items against the actual `crossproduct_v2/` output:

**Item 1 (unthresholded set / AP feasibility) — VERDICT REVERSED.** The original
audit concluded "AP/mAP is NOT computable from this table." This was wrong, or at
least overtaken by the Phase 2 build: `ap_metrics.compute_ap_grouped()`
(`repos/K-Radar/scripts/alvis/ap_metrics.py:113`) computes a **restricted-range** AP
per group directly from `full_denormalized_table.parquet`'s per-row `score`/`iou`
columns (groups with `num_gt==0` omitted, not zero-filled). This is the
`ap_restricted_range` column populated in every `summary_*.parquet` — e.g.
`camera_gaussian_noise_high` = 71.18. Caveat carried forward in `findings.md`:
restricted-range AP matches K-Radar's own official-benchmark convention exactly, it
is not the same as an unbounded/full-range AP, and CRI (item 8, below) still can't
be derived from it without the separate `ap_robustness_local.json` source.

**Item 4 (camera_frame_deletion coverage collapse) — closed by decision**, not
investigated further: excluded from the 22-condition scope per user decision
2026-08-31, carried forward unchanged into `crossproduct_v2/`
(`master_metrics_table.CONDITIONS`, `crossproduct.py:17` docstring).

**Item 5 (nulls in `frame_density`/`n_objs`) — closed.** Zero nulls confirmed in
`crossproduct_v2/`'s source table (Step 0 of the 9/1 rebuild) — the frame-key defect
that caused this is fixed, verified twice (8/31 addendum, then again 9/1 after a
residual recurrence).

**Item 6 (cell sizes / reliability floor) — closed at N≥30.** In
`summary_full_density.parquet`: 3,267 `reliable` / 3,499 `unreliable` / 35,474
`no_data` cells (42,240 total). Matches the audit's own 8/31-addendum rationale for
N≥30 (Wilson CI width, avoiding disproportionate exclusion of rare weather×class
cells) — re-confirmed by the user a second time on 9/1 after the floor had silently
regressed to 100 mid-session and was caught and reverted.

**Item 7 (`frame_density` binning) — closed by the existing 3-bin scheme.**
`anomaly.py`'s module docstring records this as resolved audit decision A2: keep
`{1, 2-3, 4+}` rather than re-bin. No blocker remains now that item 5's null issue
is fixed — all three bins are populated for every non-excluded condition.

**Item 8 (metric feasibility table) — closed, with one standing cross-source
caveat.** P/R/F1, AP (restricted-range, see item 1 reversal above), mRR/RS/RCE,
mATE/mASE/mAOE (radians, mod-2π wrap, resolved 8/31 Q3), mFR, and churn are all
implemented and populated in `crossproduct_v2/`. **CRI remains the one item not
fully closed**: it requires raw (non-restricted-range) AP across severity tiers per
the RoHOI formula (resolved 8/31 Q4, `compute_robustness.py:120`), which lives in
`ap_robustness_local.json`, a source outside `full_denormalized_table.parquet`.
Not attempted in `crossproduct_v2/` — would need an explicit decision to either
pull that file in as a second input (breaking the "everything derived from the one
table" property) or skip CRI as a deliverable and only report it as documented in
`docs/lit_survey/metrics/metrics_audit.md` §5.3.

**Item 9 (peer-group feasibility) — closed, moved from preliminary to actual.**
All 6 peer-group types (`sibling_conditions`, `modality_parity`, `severity_ladder`,
`stratum_sweep`, `cross_stratum_tod`, `cross_stratum_weather`) are implemented and
scored in `crossproduct_v2/reports/anomaly_coverage.csv` with real per-metric
scored/insufficient counts, e.g. `stratum_sweep` scores 44/44 (100%) across every
metric, `cross_stratum_weather` scores as low as 9.7% for mAOE (expected — this is
the thinnest peer group, capped at 3 members per audit item 9(a)'s original
analysis, re-verified 9/1 under the corrected floor). 2,395 total anomaly flags
(438 real / 1,955 small-N artifact / 2 suspected-bug, the latter root-caused and
resolved as a single-sequence artifact, not a data bug — see
[[crossproduct-rebuild-20260901]]).

**Item 10 (dispersion baseline) — closed.** `anomaly.py`'s peer-group scoring
computes median/scaled-MAD (`MAD_SCALE=1.4826`, Iglewicz & Hoaglin convention) per
group as its center/spread baseline for every peer-group×metric combination — this
*is* the dispersion baseline the original audit deferred to "first deliverable out
of the group_by." No separate computation needed; it's already the mechanism behind
every anomaly flag in `anomalies.parquet`.

**Status: Phase 1 audit checklist is now fully closed** against `crossproduct_v2/`.
One residual open item (not a blocker): CRI's cross-source dependency (item 8) is a
standing limitation, not something further audit work resolves — it needs a project
decision on scope, not more investigation.
