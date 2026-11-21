# Full-granularity denormalized exploratory pass (2026-08-28)

Task: build one prediction/GT-outcome-grain denormalized table joining the
22-condition robustness sweep to context (distance/density/environment/
weather/time_of_day), compute all 7 in-scope metrics (mAP, mATE, mASE, mAOE,
mRR, FN rate, FP rate — mFR omitted, no frame-level flip computation exists)
plus churn, and run a 4-pass exploratory analysis (condition main effects,
context main effects, condition×context interaction, continuous-stratifier
charts) to surface thesis-candidate findings rather than pre-deciding final
figures.

## Where things live

- Code: `test-bed/src/Modules/robust_testing/kradar/scripts/analysis/`
  - `build_denormalized_table.py` — the table itself
  - `exploratory_passes.py` — Pass 1–3 (reuses `master_metrics_table.py`'s
    and `fpfn_table.py`'s group_cols-generic machinery verbatim, no
    modification needed — both already took arbitrary group_cols)
  - `pass4_stratifier_charts.py` — Pass 4 charts (36 PNGs, N-encoded markers)
  - `run_churn_context.py` — context-stratified churn (see gotcha below)
  - `merge_churn.py` — merges churn into Pass 1/3 output
- Data: `repos/K-Radar/outputs/robustness_reports/full_denormalized_table.parquet`
  (1,109,578 rows, ALL 31 conditions incl. the 9 crashed-coverage
  `frame_deletion` ones — a documented superset, use this only if you
  specifically need those) and `full_denormalized_table_22cond.parquet`
  (872,713 rows, the 22-condition analysis scope, added 2026-08-28 after an
  audit caught the superset issue — use this one for anything matching the
  rest of this project's condition scope), plus `.../exploratory/` (Pass 1–4
  outputs, all built by filtering the superset to 22 conditions independently,
  before the scoped file existed — audited and confirmed no numbers were
  computed from the superset)
- Findings writeup: `docs/trend_candidates.md` (project doc, not this vault
  — see CLAUDE.md's split between `docs/vAIlt/` and `obsidianVault/`)

## Key infrastructure findings (would save time next time)

- `row_table_iou03.parquet` already has `distance_from_ego`/`weather`/
  `environment`/`time_of_day` joined — no rejoin needed. But
  `distance_from_ego` is **null for every FN row** (346,545/1,109,578, 31%)
  because it's only computed from prediction location — FN rows have no
  prediction. Fixed by falling back to GT-coordinate distance for FN rows
  only (`build_denormalized_table.py`).
- `frame_density` already existed (`bar_charts.py`) as GT sed+bus count per
  frame from `original`, binned 1/2-3/4+ — confirmed with user this (not a
  sensor point-count proxy) is the intended definition.
- GT-object spatial matching for mATE/mASE/mAOE was **not** a blocker —
  already implemented and used by `master_metrics_table.py` via
  `heatmaps.py`'s coordinate-fallback greedy IoU matcher.
- Churn (`gt_transition_analysis.py`, written 2026-08-19) was implemented
  and unit-tested but **never run against real sweep data** before this
  session — this was the first real invocation. Its own transition table
  does NOT carry weather/time_of_day/environment (confirmed via
  `ColumnNotFoundError` when the CLI's `--group-by weather` was tried
  directly) — those must be left-joined by the caller onto
  `build_transition_table`'s output before calling
  `aggregate_transition_rates`, exactly as that function's docstring says.
  `run_churn_context.py` does this join once and aggregates 3x from the
  same in-memory transition table rather than rerunning the matcher per
  dimension.
- **IoU threshold bug, caught and fixed 2026-08-28**: `gt_transition_analysis.py`'s
  `load_prediction_rows(iou_threshold=...)` has a library default of 0.5
  (`gta.DEFAULT_IOU_THRESHOLD`). All three churn scripts (the original CLI
  run and both `run_churn_context.py`/`run_churn_pass4.py`) initially passed
  that default through without checking its value, silently computing churn
  at IoU=0.5 while every other metric in this pass (mAP/mATE/mASE/mAOE/FN/FP,
  from `row_table_iou03.parquet`) is at IoU=0.3. Caught when the user asked
  "was IoU 0.5 or 0.3 used?" — re-ran all three churn scripts with an
  explicit `IOU_THRESHOLD = 0.3` constant instead of the library default.
  Every finding's ranking/conclusion held; magnitudes shifted by ~1-6 points
  (mostly downward — the looser 0.3 threshold classifies more borderline
  matches as "stable" rather than miss/recover). Lesson: never pass a
  library default through unchecked when a specific value is load-bearing
  elsewhere in the same analysis — check what it actually resolves to.

## Gotcha: memory

A single combined `corrupted_condition × weather × time_of_day ×
environment` churn run (21 conditions' worth of coordinate-fallback greedy
BEV IoU matching, pure NumPy Sutherland-Hodgman, no numba/GPU) drove this
machine (7.6GB RAM) into severe swap thrashing — 6.3GB swap used, matcher
process stuck in D-state (disk-sleep) for 25 min, had to be killed. A retry
via `run_churn_context.py` (context joined once, aggregated 3x separately
rather than one 4-way cross) completed but still pushed the system to <150MB
free RAM / 7.7GB swap before finishing (~19 min wall). If repeating this on
similar hardware: prefer per-dimension runs over combining stratification
dimensions in one matcher pass, even though that means 3x the matching cost.

## Headline candidate findings (see `docs/trend_candidates.md` for full writeup)

1. LiDAR Gaussian noise causes a step-function mAP collapse (low severity
   ~harmless, medium/high ~70% collapse), not a graded one.
2. Corruption failure mode is dominated by missed detections — FP rate
   stays flat or even *drops* under heavy corruption, never spikes.
3. mAOE/mATE/mASE barely move even as mAP collapses — corruption mostly
   kills detections outright rather than degrading survivors' localization.
4. Scene context (environment/weather) baseline effects are larger than
   most corruption effects — up to 68 mAP points from context alone
   (`alleyway`/`university`/`rain` hard; `shoulder`/`urban`/`fog` easy).
5. `lidar_gaussian_noise_high`'s collapse is context-modulated — confirmed
   independently by both mAP double-difference and churn_rate: `shoulder`/
   `alleyway` (baseline-extreme environments) both churn far less
   (0.22–0.35) than mid-difficulty environments (>0.60).
6. `lidar_loss_partial_medium` is the cleanest example of "mAP-stable but
   high churn" in this sweep: mRR≈1.00 yet 6% of GT objects still flip
   TP↔FN underneath.

## Not done this pass

- Churn vs. distance_from_ego / frame_density (Pass 4's continuous
  stratifiers) — deferred, flagged in `docs/trend_candidates.md`.
- Pass 3's `mAP_delta_from_main_effect` column conflates the context main
  effect with the true interaction; findings that needed the true
  interaction used a manually-computed double-difference instead (not
  precomputed in the CSVs).
