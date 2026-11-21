# RR/mRR heatmap session summary

For an agent doing data analysis on the 4 heatmaps in this directory. Source
data, formula, and reliability conventions below — read before interpreting
any cell value.

## Source data

`repos/K-Radar/outputs/robustness_reports/crossproduct_v2/summary_full_density.parquet`
— 42,240 rows, granularity: one row per (condition, cls, weather, time_of_day,
environment, distance_bucket, frame_density). `condition="original"` rows are
the clean baseline; all other conditions are `{modality}_{effect}_{severity}`
(21 conditions: 3 modalities × {gaussian_noise, loss_partial} × 3 severities,
+ 3 modalities × loss_complete_zero with no severity).

Metric used: `ap_restricted_range` (AP-style precision metric, 0–100 range,
null when a stratum has zero ground-truth objects for that class).

## Formula (RoboBEV RR/mRR, self-relative, no second baseline model)

```
ratio      = corrupted.ap_restricted_range / clean.ap_restricted_range   (clean = same stratum, condition="original")
RR_delta   = ratio − 1        # 0 = same as clean, negative = worse, positive = better
mRR_delta  = mean_over_severities(ratio) − 1   # RoboBEV RR_i = (1/L) Σ_l ratio_l
```

All cell values in every heatmap are `_delta` form: **a raw ratio, not a
percentage** (no ×100). Read −0.5 as "50% lower than clean," not "−0.5%."

Per-class values are combined into one cell via `num_gt`-weighted mean across
`cls` (sed, bus) — weight is the corrupted row's `num_gt`, not clean's.

Full derivation/citation chain (RoboBEV vs. MSC-Bench RS/mRS vs. Dong et al.
RCE vs. Gao et al. Rb/mRb — convergent reinventions of the same formula) is in
`obsidianVault/Knowledge/robustness-metric-selection.md`.

## Reliability rule (N_FLOOR = 30)

A cell/row is "reliable" only if **both** the corrupted-side and clean-side
summed `n_total` (post any marginalization/severity-merge) are ≥30. This is
recomputed after aggregation, not inherited from the parquet's per-fine-row
`reliable` flag — inheriting it caused a bug (see Known issues below) where
marginalized rows were nearly all falsely flagged unreliable.

- **Hatched cell** (`////` pattern): value is shown but rests on ≥1
  unreliable sub-component. Treat as directionally suggestive, not
  statistically solid.
- **Dropped row**: a Y-axis row is removed entirely (not left blank) if
  *none* of its cells across all X columns are reliable. Reported as
  `N dropped` in each figure's title.
- **Blank/grey cell** (`#F3F4F6`, `set_bad`): no data at all (null AP on one
  side, usually zero ground-truth objects in that stratum for that class) —
  distinct from unreliable-but-present.
- **Colorbar clip colors** (dark blue over / dark red under, `extend="both"`
  arrows): cell value exceeds the fixed ±1.2 display range — still real data,
  just off-scale, rendered in a color not used elsewhere on the map so it
  isn't misread as an ordinary extreme green/red.

## The 4 heatmaps

| File | Y-axis | X-axis | Severity |
|---|---|---|---|
| `rr_heatmap.png` | 106 full (weather\|tod\|env\|distbucket\|density) strata | 21 individual conditions | not merged |
| `mrr_heatmap.png` | same 106 strata | 9 (modality×effect) groups | merged via mRR |
| `mrr_heatmap_marginal.png` | 22 single-dimension marginal rows (5 weather + 2 tod + 8 env + 4 distbucket + 3 density values, each averaged over the other 4 dims + cls) | 9 (modality×effect) groups | merged via mRR |
| `rr_heatmap_marginal.png` | same 22 marginal rows | 21 individual conditions | not merged |

Generating scripts: `generate_rr_heatmap.py`, `generate_mrr_heatmap.py`,
`generate_mrr_heatmap_marginal.py`, `generate_rr_heatmap_marginal.py` (each
independent, none overwrites another's output). Run via:

```bash
uv run --project test-bed/src/Modules/robust_testing/kradar python docs/crossproduct_figures/<script>.py
```

Each script prints a verification line (`verification OK`) that cross-checks
one plotted cell against a manual re-aggregation straight from the source
parquet — re-run and check that line if you doubt a value.

## Known issues / caveats to carry forward

- 21 of 1920 `original`-condition rows have `ap_clean == 0`; those strata are
  excluded from RR entirely (division-by-zero guard), not shown as RR=0.
- `ap_restricted_range` is null for ~87% of fine-grained (cls, stratum) cells
  in the `original` baseline (sparse cross-product, most combos have no GT
  objects for one class) — this is why the marginal (collapsed) heatmaps have
  far better coverage/reliability than the full 106/170-stratum ones.
- RoboBEV's canonical `mRR` averages `NDS` (a composite detection score), not
  raw AP. Here `M = ap_restricted_range`, an explicit substitution — flag this
  if citing the numbers as literal RoboBEV mRR in a report.
- `mFR` is deliberately excluded from the metrics stack (2026-09-01 decision,
  see `obsidianVault` project memory) — do not add it without checking that
  decision first.
