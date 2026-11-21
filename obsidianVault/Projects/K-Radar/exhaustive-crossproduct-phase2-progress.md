---
name: exhaustive-crossproduct-phase2-progress
description: Phase 2 implementation progress for the exhaustive cross-product analysis module (metrics.py/crossproduct.py/queries.py) over full_denormalized_table.parquet -- what's built and verified, what's deferred
metadata:
  type: project
---

# Phase 2 implementation progress (2026-08-31)

Following [[exhaustive-crossproduct-phase1-audit]]'s resolved blockers, built
the reusable module at
`test-bed/src/Modules/robust_testing/kradar/scripts/analysis/crossproduct/`.

## Built and verified this session

- **`metrics.py`**: `wilson_ci`, `precision_recall_f1`, `angle_error` (mod-2π
  wrap per Phase 1 decision 4), `reliability_tag` (reliable/unreliable/
  no_data per Phase 1 decision 5, floor=100), `retention_ratio`/`absolute_delta`.
- **`crossproduct.py`**: `build_summary` at 6 marginalization levels (full
  grain down to per-condition), each cross-joining the FULL domain of every
  key column (not just observed combos) so `no_data` cells are explicit
  rows, not silently absent. Joins in TP-only mATE/mASE/mAOE and
  restricted-range AP (via K-Radar's own `compute_ap_grouped`, reused not
  reimplemented) separately since AP requires per-group score sorting, not a
  simple sum-aggregate. `add_baseline_deltas` joins every corrupted cell to
  `original` on non-condition keys, computes delta+retention, flags
  `baseline_reliable`.
  - Verified: `summary_full` = 14,080 rows (1,318 reliable / 2,184 unreliable
    / 10,578 no_data). `summary_cond_cls_weather_tod_env` = 3,520 rows
    (620 reliable / 359 unreliable / 2,541 no_data) — 620+359=979 matches
    Phase 1's audit count exactly.
  - Sanity check: `lidar_gaussian_noise_high` shows f1_delta=-0.536,
    AP retention=0.296 (largest collapse) — matches
    [[full-denormalized-exploratory-pass]]'s independently-found headline #1.
    `lidar_loss_complete_zero` AP retention=0.578 vs. `radar`'s 0.66 vs.
    `camera`'s ~1.0 (camera zero-ablation barely registers) — plausible,
    matches sensor-importance priors for this fusion stack.
- **`queries.py`**: all 7 questions now implemented.
  - Q1 (beats-baseline, significant/noise split), Q2 (top/bottom-N per
    metric at 4 levels), Q3 (FP count vs. rate divergence), Q4 (FP/FN joint
    worst offenders) — all split reliable from unreliable/no_data, never
    merged.
  - Q5 (churn): reuses the prior pass's cached
    `churn_by_condition*.json` (already computed at `iou_threshold=0.3`)
    instead of rerunning the matcher — avoids the documented memory
    blowup entirely. Pooled over classes (cached output has no per-class
    split) — flagged, not silently assumed done. Verified:
    `lidar_gaussian_noise_high` = 60.9% churn (highest), matches Q2's AP
    ranking independently. 13/21 conditions show recovery rate ≥ miss
    rate — flagged as suspicious per spec, not reported as robustness.
  - Q6 (loss_complete_zero): camera retention 0.988, radar 0.898, lidar
    0.500 — camera-loss is nearly invisible to this model, lidar-loss is
    catastrophic. Off-distribution-BEV caveat included verbatim in every
    output.
  - Q7 (anomaly finder): non-monotonic-severity check + group-median
    (MAD-based) deviation check. **Caught and fixed a real bug mid-build**:
    the deviation check's first version grouped by `(modality, effect,
    cls)`, pooling all three severity tiers into one reference median —
    this trivially flagged every high-severity cell as an "outlier" purely
    because low-severity cells (which barely move) dragged the median up.
    Fixed to group by `(condition, cls)` instead, comparing only across
    weather×tod within a fixed condition. Post-fix output is coherent:
    rain/sleet+night cells recur across multiple independent conditions in
    the outlier list — a real compounding-difficulty signal, not an
    artifact. NOT covered: sign-flip-vs-baseline detection, full
    weather-interaction double-difference (clean-baseline-gap vs.
    corrupted-minus-clean-delta) — flagged as still-open.
- **`plots.py`**: 4 figures built (severity-monotonicity lines,
  condition×weather retention heatmap, FP-vs-FN scatter, churn ranking
  bars). Visually verified severity-monotonicity and heatmap. Known gap:
  heatmap y-axis uses full condition strings, not the two-letter codes the
  spec asked for (`radar_charts.CONDITION_CODE` only keys `(sensor,
  effect)` tuples, not full condition-with-severity strings) — cosmetic,
  not correctness. No N-per-bin bars or bootstrap CI ribbons yet.
- **`run_analysis.py`**: orchestrates build→deltas→all 7 queries→CSV
  exports→markdown findings report→figures. Runs end-to-end without error.

## Known limitation, flagged not hidden

Q1's "significant" flag is CI-based (Wilson lower bound excludes the
original point estimate) ONLY for precision/recall, since those are the only
metrics with a CI implemented. For f1/mATE/mASE/mAOE/AP, "significant" only
means "both the corrupted and baseline cells clear N≥100" — a weaker bar,
marked via a `ci_based` column so it's never mistaken for the same standard.
Building a proper F1/AP confidence interval (e.g. bootstrap) was judged out
of scope for this pass; flagging here so it isn't silently assumed done.

## Not yet built (as of end of this session)

- Q7's sign-flip-vs-baseline detection and the full weather-interaction
  double-difference (corrupted-minus-clean delta vs. clean per-weather
  baseline gap, to separate compounding difficulty from inherited
  difficulty).
- Per-class churn (Q5) — would require rerunning
  `gt_transition_analysis.py`'s matcher with `cls` added to the group-by,
  which risks the documented memory blowup; not attempted.
- Bootstrap CI for F1/AP/error metrics (Q1's significance test is weaker
  for these than for precision/recall).
- Two-letter condition codes on the heatmap; N-per-bin bar charts;
  bootstrap CI ribbons on any figure.
- Q2 output only exported to CSV at the `condition` level in
  `run_analysis.py`'s default run — `queries.q2_all_levels` supports
  `cond_cls`/`cond_cls_weather`/`cond_cls_weather_tod` but those aren't
  wired into the orchestrator's CSV export yet.

## Anomaly-addendum session (2026-08-31, same day) — peer-group detection mode

Separate from everything above: the addendum reframed Q7 from
baseline-relative to PEER-relative detection (a cell measured against the
other cells expected to behave like it, not against `original`). Ran its own
Phase-1-style audit first (A1 peer-group viability, A2 frame_density
binning, A3 dispersion baseline, A4 CI-detectability), got explicit user
decisions on all 4, then implemented. Full audit + decisions:
[[exhaustive-crossproduct-anomaly-addendum]].

Resolved decisions: A2 keeps the existing 3-bin frame_density scheme;
detection gate is SINGLE (robust z primary, CI-overlap recorded not
filtering — A4 found 78%/52% of precision/recall cells have a CI too wide
for a double-gate to ever fire); the dead `cross_stratum_weather` peer group
(0% viable at 4+ members) was redefined to pool frame_density too, then
found empirically to cap at 3 co-occurring members even after loosening —
`min_members` set to 3, not 4, documented as the real achievable ceiling
rather than an arbitrary choice; severity-ladder (49% viable) and
cross-stratum-by-tod (5% viable) both run anyway with exclusions reported.

Built `anomaly.py` (6 peer-group definitions, median/scaled-MAD center+spread
with a MAD==0 floor fallback, robust z, three-way real/small-N/suspected-bug
classifier) and `detectors.py` (D1 monotonicity, D2 flat-except-one, D3
modality-ordering divergence, D4 median-polish interaction residual, D5
cross-metric inconsistency) plus `anomaly_plots.py`. Wired into
`run_analysis.py`; `queries.q7_anomalies` now raises `NotImplementedError`
pointing here (superseded, not duplicated, per the addendum's explicit
instruction).

**Two real bugs caught and fixed during this build, not just at review**:
1. `flag_anomalies` crashed on an all-`insufficient` peer group (`abs()` on
   an all-null column) — a real edge case (`cross_stratum_weather` before
   the min_members fix), not a hypothetical.
2. `pl.DataFrame(list_of_dicts)`'s default 100-row schema inference saw only
   `None` in `ci_overlaps_median` for the first 100 rows (only
   precision/recall carry a CI) then choked on a real `bool` later — fixed
   with `infer_schema_length=None`.
3. The bug-classifier's first version flagged precision/recall `<=0.0` as
   `suspected_bug` — which misclassified a REAL finding
   (`lidar_loss_complete_zero` + rare `bus` class + rain/night genuinely
   producing 0 detections) as a pipeline bug. Fixed to only flag
   suspiciously-PERFECT (~1.0) low-N scores — 0.0 under total sensor loss on
   a rare class is mechanistically expected, not suspicious.

**Verified output** (`anomalies.csv`, 1,421 flags: 389 real / 1,032
small-N / 0 suspected-bug): top-ranked flag is `bus + sleet + day +
lidar_gaussian_noise_high` precision collapsing to 0.50 against a
sibling-conditions peer median of 0.90 (robust z=-43.9, tight 22-member
peer group) — exactly the addendum's target pattern (one member breaking
from an otherwise-tight cluster). D4's median-polish heatmap (condition x
weather, `sed`, fit quality 0.84) shows lidar-corruption residuals flipping
sign between fog (positive) and normal/overcast (negative), and radar
conditions showing a consistent negative residual specifically in sleet —
a genuinely new interaction-level finding not visible in any
baseline-relative table built earlier in this project.

**Documented as legitimate null results, not bugs**: D2 (flat-except-one)
found zero qualifying groups — every real anomaly in this dataset comes
from already-scattered groups, not tight ones. `cross_stratum_tod` (2-member
groups) can mathematically never produce a robust-z flag (median=mean, MAD
symmetric, z≡0.674) — its zero flags are a property of the math, not
evidence of no anomaly; this is called out explicitly in `run_analysis.py`'s
findings report so it isn't misread as a clean result.

## Where things live

- Code: `test-bed/src/Modules/robust_testing/kradar/scripts/analysis/crossproduct/`
  (`anomaly.py`, `detectors.py`, `anomaly_plots.py` added this session)
- Output: `repos/K-Radar/outputs/robustness_reports/crossproduct/summary_*.parquet`,
  `deltas_*.parquet`, `reports/anomalies.{csv,parquet}`,
  `reports/anomaly_coverage.csv`, `figures/anomaly/*.png`

## 2026-08-31, later same day — frame-key fix attempt, new blocker found

Attempted to fix the Phase-1-audit-flagged frame-key mismatch
(`build_denormalized_table.py`'s `_add_frame_density` join silently failing
for 96.36% of rows). Rigorously derived and validated a per-sequence
tesseract_idx-offset join key (see [[frame-key-derivation-kradar]] for the
full method and validation against `seq32_frame_index_map.txt`), implemented
as `_add_frame_key` in `build_denormalized_table.py`.

Before this could matter in practice, discovered the upstream
`row_table_iou03.parquet` had been independently regenerated (by a
concurrent process, not this session) at 22:45, which already fixed the
frame-format bug at the source — `original` and corrupted conditions now
share one uniform `"tess-lidar"` frame format, 100% joinable directly. Made
`_add_frame_key` detect this and skip the derived-offset path when it's not
needed (kept as a validated fallback, not deleted, in case the format
regresses again).

Reran `build_denormalized_table.py` against the current (22:45) source:
`full_denormalized_table.parquet` now 1,109,578 rows (now matches the task
spec exactly), `frame_density`/`n_objs` null count **0** (was 1,069,260 /
96.36%). Backed up to `backups/pre_framekey_fix_20260831/`.

**Blocked the planned full crossproduct rerun**: the same 22:45 upstream
regen has `environment` and `time_of_day` 100% null (only `weather`
survived) — broke `crossproduct.build_summary`'s join immediately
(`time_of_day` dtype mismatch, empty-vs-string). This is a new regression in
someone else's concurrent work, not caused by this session. Per
project convention (never guess/patch silently), did **not** attempt to
backfill or guess `environment`/`time_of_day` values, and did **not** rerun
the crossproduct pipeline against this broken table — `crossproduct/`
outputs (summary/deltas parquets, `reports/`, `figures/`) are left at their
pre-session (21:39) state, now stale relative to the newly-fixed
`full_denormalized_table.parquet` but not corrupted by a bad rerun either.

**Next steps for whoever picks this up**: (1) find/fix whatever regenerated
`row_table_iou03.parquet` at 22:45 so `environment`/`time_of_day` are
populated again (check `ingest.py`'s `_sequence_metadata`/description.txt
join — that's the most likely place this broke); (2) once fixed, rerun
`build_denormalized_table.py` again (frame-key logic in this session's fix
is already correct and needs no further change) and then the full
crossproduct pipeline; (3) items 5–7 of the original task spec (camera
frame_deletion coverage re-check, fresh Phase-1-v2 audit doc, trend-doc
updates) were not attempted this session — still open.

## 2026-08-31, later same day: weather/env/tod fix + full pipeline rerun

The `environment`/`time_of_day` regression flagged above (a concurrent
22:45 "original reingest" run had no access to `description.txt` on this
machine and silently degraded `weather`/`environment`/`time_of_day` to
`normal`/null) was fixed by a separate session: rejoined sequence-level
metadata (`sequence`, `weather`, `environment`, `time_of_day` — per-sequence
constants) from `pre_original_reingest_backup_20260831/row_table_iou03.parquet`
(known-good, cross-verified against a second independent source, 0
mismatches across 58 sequences), then reran `build_denormalized_table.py`.
`full_denormalized_table.parquet` is now 1,109,578 rows × 34 cols, 0% null
on `weather`/`environment`/`time_of_day`/`frame_density`/`n_objs`, and
`frame` format is consistent (`"{radar_idx}-{lidar_idx}"`) between
`original` and every corrupted condition — this also resolves the Phase-1
audit's Q1 frame-key blocker, since that mismatch was a symptom of the same
underlying join issue.

Ran `scripts/analysis/crossproduct/run_analysis.py` end-to-end against the
fixed table (backup of stale output at
`backups/pre_crossproduct_rerun_20260831_230859/`). Materially changed vs.
the stale (pre-fix) run:

- `summary_full_density.parquet`: corrupted-condition rows went from 0 to
  832,358 (`n_total` sum) — the frame_density stratification was previously
  `original`-only (96% of the table was starved of this join), now works
  across all conditions.
- `anomaly_coverage.csv`'s `stratum_sweep` peer group: 2 → 44 scored group
  instances per metric (22x), only peer group affected — confirms the fix is
  specific to the density join, isolated correctly.
- `anomalies.parquet`: 1,042 → 1,421 total flags (325→348 real, 717→1,073
  small-N artifact, 0→0 suspected-bug).
- `d1_monotonicity_violations.csv`: 184 → 173 rows, different member set
  (not just a count change).
- Q1-Q6 headline numbers (findings.md) largely stable in magnitude — small
  decimal-place shifts consistent with corrected backfill, not large swings.

`camera_frame_deletion_*` coverage collapse (Phase-1 audit item 4/Q2):
**confirmed out of scope for this pipeline** — `crossproduct.py` restricts
input to the 22-condition scope and excludes all `frame_deletion`
conditions by design (pre-existing decision, code comment at
`crossproduct.py:17`, unrelated to today's fixes). The underlying
data-quality question (is camera frame-deletion's severity scale different
from lidar/radar's, or a real bug) was **not investigated this session** and
remains open — it doesn't feed this deliverable.

Full detail: [[exhaustive-crossproduct-phase1-audit-20260831]] addendum
(same date, appended at end of that file).

**Still open**: Q2 camera_frame_deletion upstream question, Q3 rotation_y
units, Q4 CRI formula reference, Q5 N≥30 floor (unchanged/not revisited).
Item 5-7 doc updates (`docs/crossproduct_trends_and_anomalies.md`,
`docs/trend_candidates.md`) done this session too — see Daily note.
