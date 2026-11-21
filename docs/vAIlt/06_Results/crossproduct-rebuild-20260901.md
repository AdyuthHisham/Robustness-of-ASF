# Crossproduct Rebuild from Corrected Data — 2026-09-01

## Task

Regenerate the entire `crossproduct/` deliverable tree from the frame-key-corrected
`full_denormalized_table.parquet` / `full_denormalized_table_22cond.parquet`
(see [[exhaustive-crossproduct-frame-key-fix-20260901]],
[[frame-key-derivation-kradar]]), and resume the blocked Phase 1 audit
(`docs/vAIlt/06_Results/exhaustive-crossproduct-phase1-audit-20260831.md`)
against the new tree.

## Step 0 — verified before touching anything

The three corrected tables were **not** at the path the task brief named
(`repos/K-Radar/outputs/*.parquet`) — they live under
`repos/K-Radar/outputs/robustness_reports/*.parquet`. Once located:

- `row_table_iou03.parquet` / `full_denormalized_table.parquet`: 1,109,616 rows,
  `full_denormalized_table_22cond.parquet`: 872,745 rows. mtime 2026-09-01 10:27,
  newer than both backups.
- Zero nulls in `weather`/`environment`/`time_of_day`/`frame_density`/`n_objs` across
  all three.
- `frame_key_int` format (`XXXXX-YYYYY`) confirmed identical between `original` and
  every corrupted condition.
- camgauss recompute from the corrected table: **TP=80,335 / FP=14,698 / FN=26,033** —
  exact match to the claimed figures.
- Both backup dirs (`pre_camgauss_original_merge_backup_20260901/`,
  `robustness_reports/pre_original_reingest_backup_20260831/`) intact and untouched.

Step 0 passed; proceeded to rebuild.

## Step 1 — decisions applied

Surfaced as blocking questions, resolved before rebuilding:

- **Q0 (build scope)**: fresh `crossproduct_v2/` directory, not an in-place refresh
  of `crossproduct/` — approved by user. Rationale: keeps the old tree available for
  side-by-side diffing and avoids silently changing numbers already cited elsewhere
  (vault, thesis) before those citations are updated.
- **rotation_y / mAOE convention**: radians, wrapped mod 2π to [-π, π] then `abs()`
  (`metrics.py:61-67`, `angle_error()`) — matches K-Radar's own AOS
  `(1+cos(gt-pred))/2` full-heading formula, not axis-symmetric mod π. Already
  correctly implemented and documented (Phase 1 decision 4,
  [[exhaustive-crossproduct-phase1-audit]]); no code change needed, no ambiguity found.
- **N≥30 reliability floor**: initially found `metrics.py:20` set to
  `RELIABILITY_FLOOR = 100` and asked the user whether to keep that or use the task
  brief's "N≥30" — user said keep N≥100. **Then found the actual Phase 1 audit doc's
  own 2026-08-31 addendum**
  (`docs/vAIlt/06_Results/exhaustive-crossproduct-phase1-audit-20260831.md`,
  "Q5 (N≥30 reliability floor) — CONFIRMED, kept as-is") had explicitly resolved and
  documented **N≥30** with rationale: Wilson CI half-width at N=30 is still wide
  enough (~±18pp near p=0.5) that single-detection noise doesn't dominate, while
  N≥100 would flip ~21.3% of (condition×cls×weather×tod) cells to unreliable
  vs. 11.5% at N≥30 — disproportionately hitting rare weather×class combinations
  (bus+sleet etc.) that peer-group anomaly detection specifically targets. The
  in-code `RELIABILITY_FLOOR=100` contradicted this resolved decision, with no git
  history to explain the change (`scripts/analysis/` in `kradar_visibility` is
  untracked for this file). Re-surfaced to the user with this new information;
  user confirmed **N≥30 is correct**, superseding the earlier "keep 100" answer.
  Changed `metrics.py:20` `RELIABILITY_FLOOR = 100` → `30` (and the module
  docstring's `N<100` → `N<30`), and reran the full rebuild.
- **camera_frame_deletion_\***: carried forward as excluded (9 of 31 `frame_deletion`
  conditions dropped from the 22-condition scope, `master_metrics_table.CONDITIONS`)
  — not re-litigated, per standing instruction.

## Step 2 — rebuild

Ran the existing pipeline (`crossproduct.py` / `queries.py` / `anomaly.py` /
`detectors.py` / `plots.py` / `anomaly_plots.py` / `run_analysis.py`) unmodified,
via a thin wrapper script that redirects every output path to
`repos/K-Radar/outputs/robustness_reports/crossproduct_v2/` while reading from the
already-corrected `full_denormalized_table.parquet` (the pipeline's `ROW_TABLE_PATH`
already pointed at the right file — no source-path change needed, only output
redirection). No changes made to the analysis code itself.

Full deliverable set regenerated and confirmed present:

- 7 `summary_*.parquet` (condition, cond_cls, cond_cls_weather, cond_cls_weather_tod,
  cond_cls_weather_tod_env, full, full_density)
- 3 `deltas_*.parquet` (condition, cond_cls, cond_cls_weather_tod) — note
  `deltas_cond_cls_weather.parquet` was not part of the original script's write list
  either (only `condition`/`cond_cls`/`cond_cls_weather_tod` levels get delta files
  written by `run_analysis.py`; matches the old tree's set exactly)
- All Q1–Q6 CSVs, `anomalies.csv/.parquet`, `anomaly_coverage.csv`,
  `d1_monotonicity_violations.csv`, `d3_modality_divergence.csv`,
  `d5_cross_metric_inconsistency.csv`, `findings.md`
- All 4 top-level figures + 3 anomaly-addendum figures

## Step 3 — sanity check against pre-fix `crossproduct/`

**Internal consistency**: `summary_condition.parquet`'s camgauss TP/FP/FN
(80,335/14,698/26,033) reconciles exactly with the Step 0 raw recompute and with
`findings.md`. Confirmed.

**Diff vs. the existing `crossproduct/` tree — smaller than expected.** The task
brief anticipated large deltas (citing "96.36% null frame_density" and "0 joined
rows" pre-fix). The actual measured diff was much smaller:

- `summary_condition.parquet`: `n_total` per condition differs by 1–18 rows out of
  ~40,000 (rounding/matching-order noise); `f1`/`ap_restricted_range`/`mATE`/`mAOE`
  agree to 3–4 decimal places.
- `summary_full_density.parquet`: 407 of 42,240 cells changed `n_total`, total
  absolute diff = 652 rows out of 872,745 (0.07%). `reliable` cell count unchanged
  (1,841 in both).
- `deltas_condition.parquet` / `deltas_cond_cls.parquet` /
  `deltas_cond_cls_weather_tod.parquet`: identical row counts and identical
  `baseline_reliable` counts (21/21, 42/42, 315/420) between old and new.
- `q5_max_churn.csv`: **byte-identical** old vs. new — churn is read from a cached
  JSON (`queries.CHURN_DIR`, `_load_churn_json`) that this frame-key fix never
  touched.

**Conclusion**: the existing `outputs/robustness_reports/crossproduct/` tree
(mtime 2026-08-31 23:10) was *not* built on the severely-broken data the task brief
described. It must already have absorbed most of the frame-key correction before
this session — consistent with the `pre_original_reingest_backup_20260831/` backup
being dated earlier the same day, implying an intermediate re-ingestion/fix already
happened before 23:10 on 2026-08-31. The dramatic "96% null" / "0 joined rows" state
applies to an even earlier snapshot than the `crossproduct/` tree that was sitting
on disk at the start of this task, not to what this rebuild actually superseded.

This does **not** mean the rebuild was unnecessary — `crossproduct_v2/` is now
verified to derive from the exact, freshly-reconfirmed corrected source (Step 0),
which the old tree's provenance could not be verified against without doing this
work. But readers should not expect the headline numbers to have moved
substantially; they didn't, because the corruption this rebuild is guarding against
had already been mostly fixed upstream of the old tree.

## Post-floor-correction rebuild results (N≥30)

Rebuilt again after correcting `RELIABILITY_FLOOR` to 30. camgauss TP/FP/FN still
reconciles exactly (80,335/14,698/26,033) — the floor only changes which cells are
tagged `reliable`/`unreliable`, not the underlying counts. Effect of the floor
correction:

- **Reliable cells in `summary_full_density.parquet`**: 3,267/42,240 at N≥30, vs.
  1,841/42,240 at the (incorrect) N≥100 — matches the audit doc's predicted
  direction (loosening the floor recovers rare-cell coverage).
- **Anomaly flags**: 2,395 total (353 real / 2,040 small-N artifact / **2 suspected
  bug**) at N≥30, vs. 1,433 total (362 real / 1,071 small-N / 0 suspected bug) at
  N≥100. More cells clearing the reliability floor means more peer-group
  comparisons are scored, which surfaces more candidates in every category.
- **The 2 new `suspected_bug` flags**: both `lidar_gaussian_noise_*` × sleet ×
  `precision=1.0`, `n_sequences=1` (single sequence backing the cell), robust
  z ≈ 19.1 and 5.9 against a peer median ≈ 0.84–0.86. Plausibly a genuine
  single-sequence perfect-precision outlier newly admitted by the loosened floor,
  not a pipeline defect — but flagged here for manual audit per the pipeline's own
  `category` labeling, not dismissed unilaterally.
- D1 monotonicity violations: 222 (vs. 173 in the audit doc's own N≥30 rerun from
  Aug 31, vs. 184 in that day's stale N≥30 run before the frame-key fix — all three
  numbers use the same floor, so the Aug-31→Sep-1 change reflects the frame-key
  correction's effect on `original`-joined severity ladders, not a floor artifact).

This is now the deliverable set that matches every resolved Phase 1 audit decision:
frame-key-corrected source data, N≥30 floor, mod-2π mAOE wrap, `camera_frame_deletion_*`
excluded.

## Follow-up: deep dive on the 2 `suspected_bug` anomaly flags

Both flags: `condition=lidar_gaussian_noise_{low,high}, cls=sed, environment=highway,
distance_bucket=far_40_60, time_of_day=day`, member=`sleet`, `metric=precision`,
`value=1.0`, `n_sequences=1`.

**Root cause, traced to raw rows**: this exact stratum has data from exactly 1
sequence (`53`) under `sleet` (sleet itself is the rarest weather overall — 12/58
sequences dataset-wide). In `original` (baseline) for this cell: `n_tp=12, n_fp=2,
n_fn=37`. The 2 FP predictions are both low-confidence (scores 0.31, 0.32) and near
the `far_40_60` bucket boundary (44m, 58m). Under all three `lidar_gaussian_noise_*`
severities, both FPs vanish (`n_fp=0` at low/medium/high) while TP count degrades
monotonically with severity (12→4→1) — the expected pattern for noise suppressing
low-confidence detections generally, catching the two marginal FPs along with
weaker TPs. Precision hits exactly 1.0 simply because `n_fp` hit exactly 0.

**Verdict: not a data or pipeline bug.** A real, mechanistically coherent value that
happens to be statistically extreme (robust z ≈ 19.1, 5.9) because it rests on a
single sequence — exactly the failure mode `n_sequences` was added to flag.

**Real bug found while explaining it**: `anomaly.classify_anomaly()`
(`anomaly.py:213-250`) checks for a near-perfect value (`value >= 0.999 and
n_total < 200` for precision/recall/f1) **before** checking `n_sequences <=
SEQUENCE_CONFOUND_CEILING`. Both branches return immediately, so the
sequence-confound check — which the function's own docstring says exists precisely
to catch "a cell rests on <=2 distinct sequences" — is unreachable for any
near-perfect score. Confirmed empirically: **100% of the table's `suspected_bug`
flags (2/2) have `n_sequences=1`** and would reclassify to `small_n_artifact` if the
sequence check ran first. This is a check-ordering bug in the classifier, not a data
issue — **not fixed**, since reordering it is a real behavior change to the
anomaly-detection design (arguably perfect scores should always get manual-audit
priority regardless of cause) that needs a decision, not a silent patch.

## Follow-up: broader sweep of `crossproduct/` scripts for other silent drift

Grepped every module-level `UPPER_CASE = ` constant across `crossproduct.py`,
`metrics.py`, `anomaly.py`, `detectors.py`, `queries.py`, `plots.py`,
`anomaly_plots.py`, `run_analysis.py`, and the sibling `scripts/analysis/*.py`
(none outside `crossproduct/` reference the reliability floor at all). Findings:

- **`anomaly.py:46` `RELIABLE_FLOOR = 100` — dead code.** Grepped: never referenced
  anywhere in the file or imported elsewhere. The floor actually gating output is
  `metrics.RELIABILITY_FLOOR` (now 30), consumed via the `reliable` boolean column
  `anomaly.py` reads at line ~136. This is a second, differently-named copy of the
  same concept sitting at the same wrong value (100) the real constant had drifted
  to — annotated in place as dead code, not deleted or wired in (a human call:
  either remove it, or someone once intended it to do something and never finished
  the wiring).
- **3 stale comments citing "N>=100"** (`crossproduct.py:96`, `queries.py:89`,
  `queries.py:162`, `anomaly.py:91` empirical counts) — all leftover documentation
  from when the floor really was 100. Fixed to N>=30; the `anomaly.py:91` one also
  had its empirical group-counts re-verified against the corrected floor (max
  weather co-occurrence per fixed stratum is still 3, confirmed structural not
  floor-sensitive — 1,062/318/154 groups top out at 1/2/3 members respectively,
  vs. the stale comment's 829/177/45).
- **`SMALL_N_CEILING = 300`** — this was set as roughly 3x the (buggy) 100 floor as
  a "soft second tier." Not rescaled when the floor was corrected to 30 — flagged
  in a code comment for a human decision (keep at 300 flat, or rescale to preserve
  the 3x ratio, e.g. ~90) rather than changed unilaterally, since I don't know if
  300 was chosen as a ratio or as an absolute row-count judgment independent of the
  floor.
- Everything else checked (`MAD_SCALE`, `ROBUST_Z_THRESHOLD`, `MIN_MEMBERS`,
  `SEQUENCE_CONFOUND_CEILING`, `MAD_FLOOR` per metric, `PEER_GROUPS` `min_members`
  overrides, `CROSS_METRIC_PATTERNS` thresholds in `detectors.py`,
  `CONDITIONS`/`CLEAN_CONDITION` in `master_metrics_table.py`) — no other reference
  to the reliability floor, no other constant that looked stale or inconsistent
  with its own docstring/rationale.

All edits from this follow-up were comments and one dead-code annotation only — no
functional/output change, confirmed by reimporting all touched modules cleanly.
`crossproduct_v2/` from the prior rebuild remains valid; no rebuild needed for this
pass.

## Decisions on the two follow-up questions (user, 2026-09-01)

- **`classify_anomaly()` check order**: left as-is. A near-perfect value
  (`value>=0.999, n_total<200`) is always tagged `suspected_bug` regardless of
  `n_sequences`, even when the sequence-confound explanation is already known. User
  decision: perfect scores warrant manual-audit priority unconditionally. The 2
  existing flags (both `n_sequences=1`) remain `suspected_bug`, not reclassified.
- **`SMALL_N_CEILING`**: rescaled from 300 to **90**, preserving the original 3x
  reliability-floor ratio (was 3x100, now 3x30) rather than leaving a now-10x-floor
  gap. This is a real behavior change (affects `small_n_artifact` vs `real`
  classification for cells between N=30 and N=90), so `crossproduct_v2/` was rebuilt.

## Rebuild #3 (post-SMALL_N_CEILING correction)

camgauss TP/FP/FN reconciles exactly again (80,335/14,698/26,033) — the ceiling
change only affects anomaly-classification labels, not the underlying counts.

- Anomaly flags: **2,395 total** (unchanged count) — `real` 353→**438** (+85),
  `small_n_artifact` 2,040→**1,955** (−85), `suspected_bug` **2→2** (unchanged, as
  expected: both flags have `value=1.0` which trips the unconditional
  near-perfect-score branch before `SMALL_N_CEILING` is ever consulted).
- The 85-cell shift is exactly the cells with N between 90 and 300 that were
  previously given the soft "still could be noise" caveat and are now treated as
  fully reliable `real` findings — the expected effect of tightening the ceiling
  from 10x-floor back to 3x-floor.

This is now the deliverable set reflecting every resolved decision: frame-key-
corrected source data, N≥30 floor, N≥90 small-N soft ceiling, mod-2π mAOE wrap,
`camera_frame_deletion_*` excluded, unconditional suspected_bug priority for
near-perfect scores.

## Output location

`repos/K-Radar/outputs/robustness_reports/crossproduct_v2/` is now the current
deliverable tree. `crossproduct/` (old) is left in place, untouched, for reference —
not deleted per [[feedback_batch_deletion_sync_gate]] discipline (never delete
without an explicit decision to do so).

Any downstream reference (vault notes, thesis) that cites `crossproduct/` paths
should be updated to `crossproduct_v2/` when next touched; not done in this pass
since Q0 was scoped as "produce the new tree," not "update every downstream
citation."

## Standing constraint

Per [[project_alvis_permanently_unavailable]]: Alvis compute is gone for good. The
locally rebuilt `all_preds.txt`/`all_gts.txt` and the three corrected parquets are
the permanent source of truth for this project going forward — this rebuild is not
provisional pending any future resync.

## Next

Resume the Phase 1 audit checklist
(`docs/vAIlt/06_Results/exhaustive-crossproduct-phase1-audit-20260831.md`) against
`crossproduct_v2/`, since it was previously blocked by the bug this rebuild fixed.
