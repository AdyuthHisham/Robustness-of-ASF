# ASF robustness visualization results (2026-08-20)

Executes `robustness-visualization-plan.md` items 1–8 against current data.
Occlusion stratification is out of scope (K-Radar hardcodes `occ=0`
dataset-wide, see bottom of doc) — item 7 (zero-sensor ablation) turned out
to **not** need a new inference run and is built in §7 below (an earlier
pass of this doc incorrectly called it out of scope; corrected same day).

**Standardized on IoU=0.3 throughout** — matches K-Radar's official BEV
methodology (pooled AP at 0.3 lands within noise of `complete_results.txt`'s
published Sedan/Bus numbers; see `robustness-metric-implementation-plan.md`
S6). An earlier pass of this analysis used IoU=0.5 for the mAP/RCE items,
matching a stale baseline number in the original task brief — corrected.

## 0. Data freshness and a real bug found and fixed mid-session

`repos/K-Radar/outputs/all_preds.txt` is 748,981 lines as of this run (grew
from the 743K+ referenced when the task was scoped), so all artifacts here
were **rebuilt from scratch**.

**Bug found and fixed in `ingest.py`** (this session, not previously known):
`_match_via_coordinates` grouped exclusively over `preds` (post dummy-line
filtering) to decide which frames to score. A frame where the model
genuinely detected **zero objects** produces only a `dummy` placeholder line
in `all_preds.txt` — correctly filtered out as not-a-real-prediction — but
since filtering removed it from `preds` entirely, that frame's group
disappeared from the matcher's iteration and its GT objects never got FN
rows synthesized. The frame silently vanished from the row table instead of
correctly scoring as "0 recall, all-FN," which **inflated mAP for exactly
the conditions this pipeline exists to catch** (confirmed empirically:
`lidar_gaussian_noise_high` mAP was 33.5 before the fix, 15.7 after — the
"before" number was computed from only the ~2–8% of frames that happened to
have a real detection, ignoring the ~92–98% that had none).

Fix (`ingest.py:67-116`, `:149-241`, `:243-297`, `:440-444`):
`_parse_preds_txt` now returns a second frame of `(sequence, frame,
condition)` triples for dummy-only frames; `_match_via_coordinates`
iterates over the union of real-prediction groups and these, synthesizing a
full-miss FN row for every GT object in a dummy frame. This is distinct
from — and does not touch — the separate, genuine "frame absent from
`all_preds.txt` entirely" case (crashed job, see §1), which correctly
remains unscored since that frame was never evaluated at all.

Verification: `radar/lidar_gaussian_noise_*` frame-pair coverage went from
28–97% (apparent "missing data") to **100%** post-fix — because those
frames were never actually missing, just all-dummy. `frame_deletion`
conditions' coverage was unaffected by the fix (0.2–4.1%, unchanged) — that
one really is missing raw data, confirmed by grepping `all_preds.txt`
directly (e.g. seq28 `radar_frame_deletion_high` has exactly 1 line total
in the raw file, vs. 299 for `lidar_gaussian_noise_high`, which is ~99% real
`dummy` lines that the old pipeline silently dropped).

Rebuilt artifacts (`repos/K-Radar/scripts/alvis/outputs/robustness_reports/`):
- `row_table_iou03.parquet` — 994,552 rows: 595,851 TP / 105,813 FP /
  292,888 FN (FN count jumped +92,497 vs. the pre-fix build, all from
  correctly-scored dummy frames).
- `row_table_iou05.parquet` — kept for reference, not used in this report.
- Dummy-tag count: 47,317 unique `(sequence,frame,condition)` triples
  (close to the previously-cited 47,307 raw dummy *lines*; small difference
  is line-count vs. deduplicated-triple-count, not a discrepancy).

**The task brief's precomputed-artifact paths (`scripts/alvis/outputs/...`
at repo root) don't exist** — actual location is
`repos/K-Radar/scripts/alvis/outputs/robustness_reports/` (nested submodule
path). **The task brief's headline (baseline mAP=55.41 at IoU=0.5) is not
reproducible** with current data — pooled baseline at IoU=0.3 (this
report's standard) is **69.27**. Different data snapshot, not a regression.

## 1. mAP of everything

**Coverage rule**: any condition below 90% frame-pair coverage vs.
`original` (13,727 pairs) is excluded from headline comparisons and marked
`low_coverage=true` / `x` marker. Post-fix, **only `frame_deletion`
conditions fail this** — all radar/lidar `frame_deletion_{low,medium,high}`
(0.2–4.1% coverage: genuinely crashed/never-run frames, confirmed against
raw `all_preds.txt`). Every other condition, including all `gaussian_noise`
tiers, now has **100% coverage** (13,727/13,727 frame-pairs).

![mAP vs severity](robustness_figures/item1_map_vs_severity.png)

*IoU=0.3, coordinate backend, pooled across 58 sequences and both classes.
`x` markers = low coverage (frame_deletion only), not comparable to
baseline. Data: `item1_map_by_condition.csv`.*

**Headline finding**: camera corruptions are flat (68.7–69.7 vs. 69.27
baseline, ≤1% relative) at every severity. **LiDAR gaussian_noise is
catastrophic** and this is now a high-confidence number (100% coverage,
not survivorship-biased): mAP 65.1 (low) → 17.7 (medium) → 15.7 (high), a
77% relative drop at high severity — the clearest, strongest finding in
this dataset. Radar gaussian_noise degrades more gently and linearly: 70.4
→ 60.4 → 55.9 (−19% at high). `lidar_loss_complete_zero` also substantial:
40.3 (−42%). `frame_deletion`'s true effect remains **unmeasurable** — its
raw coverage is too sparse (0.2–4.1% of frames) regardless of the ingest
fix, since those frames were never run at all, not merely mis-scored. A
re-run that survives high-severity frame_deletion is needed to close that
question.

## 2. Performance vs. object count in frame

GT counts derived directly from `all_gts.txt` (58-sequence, full coverage).
13,727 frames counted, median 2 objects/frame. Metric: per-frame recall
(TP/(TP+FN)) at IoU=0.3, `original` vs. three representative medium-severity
gaussian-noise conditions (one per sensor).

![Recall vs density](robustness_figures/item2_recall_vs_density_line.png)
![Recall by tercile](robustness_figures/item2_recall_boxplot_tercile.png)

Data: `item2_per_frame_recall.csv`, `item2_binned_recall.csv`. Coverage:
100% of `original`'s 13,727 frames for all four conditions shown.

## 3. Best/worst corruption per sensor × class

12 effects × {sed, bus}. Cell = RCE% vs. `original`, highest-severity tier
with adequate coverage per cell (only `frame_deletion` cells ever fall back
to a lower severity now).

![RCE heatmap](robustness_figures/item3_rce_heatmap.png)

Data: `item3_rce_picked.csv`. Sharpest reliable finding:
`lidar_gaussian_noise_high` bus RCE = **−68.0%**, `radar_frame_deletion_high`
bus shows −70.3% but is a low-coverage cell (29 frame-pairs, 13 GT bus
objects total) — not trustworthy on its own, though directionally
consistent with lidar/radar being the sensitive modalities.

## 4. FPs and FNs

Stacked FP/FN counts (coverage ≥90% conditions only, IoU=0.3) and PR curves
(`original` vs. severity tiers of one representative effect per sensor).

![FP/FN stacked](robustness_figures/item4_fp_fn_stacked.png)
![PR curves](robustness_figures/item4_pr_curves.png)

Data: `item4_fp_fn_by_condition.csv`. IoU=0.3, coordinate backend.

## 5. Does frame_deletion affect detection differently from loss_complete?

**Still inconclusive** — the ingest fix doesn't help here, since
`frame_deletion`'s problem is missing raw data (crashed jobs), not
mis-scored dummy frames. What can be said, with the same survivorship
caveat as before: on the tiny surviving sample, `frame_deletion` miss rates
(19.3–27.5%) are lower than `loss_complete_zero`'s (28.9% radar, 56.3%
lidar, both well-covered). **Do not cite this section's numbers as
resolving the redundancy question** — needs a frame_deletion re-run with
full coverage first. Data: `item5_frame_deletion_vs_loss_complete.csv`.

## 6. Churn statistics (GT-object transitions, clean → corrupted)

Via `gt_transition_analysis.py`, coverage-≥90% conditions only — now **24
of 30** corrupted conditions qualify (up from 20 pre-fix, since
`gaussian_noise` conditions are no longer misclassified as low-coverage).

![Churn stacked bar](robustness_figures/item6_churn_stacked_bar.png)

Data: `item6_churn_by_condition.csv`. Worst churn among newly-included
conditions: `lidar_gaussian_noise_high`/`_medium` — check the CSV directly,
now correctly reflecting the full-coverage catastrophic-miss picture from
§1 rather than a partial sample.

## 7. Zero-sensor ablation

**Correction**: an earlier pass of this doc called this out of scope,
reasoning it needed new inference runs. Wrong — `radar_loss_complete_zero`
/ `lidar_loss_complete_zero` (`noise_injection.py:374,487`) zero-fill that
sensor's array in place, and `camera_loss_complete`
(`noise_injection.py:621-629`) zero-fills the camera tensors — leaving the
other sensors clean in every case. That's exactly the ablation this item
asks for, and it's already in the sweep at 100% coverage.

![Zero-sensor ablation](robustness_figures/item7_zero_ablation_bar.png)

Data: `item7_zero_ablation.csv`. Retention % vs. full-sensor baseline
(mean across classes): **camera=0 → 100.7%** (no measurable loss — camera
is essentially redundant for this fusion model), **radar=0 → 94.2%**
(small loss), **lidar=0 → 58.3%** (major loss). This sharpens and confirms
§1's headline: the model is lidar-load-bearing, radar-secondary, and
barely uses camera at all. Per-class breakdown in the CSV (bus sedan
retention diverges slightly more than sed, e.g. lidar=0: sed 57.4% vs. bus
59.2%, but both tell the same story).

Framing caveat carried from the original plan doc: report this as
*retention relative to full-sensor baseline*, not "robustness" — a zeroed
tensor still passes through BatchNorm/conv-bias and is not a neutral
no-signal input to the network, so this measures the model's reliance on
each sensor under this specific ablation mechanism, not a general
sensor-dropout robustness guarantee.

## 8. mATE, mASE

TP-only, IoU=0.3. TP rows are unaffected by the dummy-frame fix (only FN
synthesis changed), so these numbers are unchanged from the earlier pass.

![mATE/mASE bars](robustness_figures/item8_ate_ase_bars.png)
![mATE vs mASE scatter](robustness_figures/item8_ate_vs_ase_scatter.png)

Data: `item8_ate_ase_by_condition.csv`. Baseline mATE≈0.326m, mASE≈0.241.
Among ≥90%-coverage conditions, both are mostly flat (0.31–0.35m,
0.24–0.27) **except** `lidar_gaussian_noise_{high,medium}`: mATE jumps to
0.52–0.54m. Combined with §1's mAP collapse, this says lidar gaussian noise
degrades ASF two ways simultaneously — it misses most objects outright
*and* mislocalizes the few it still finds.

## Occlusion stratification — dead end, not built

K-Radar's KITTI GT writer hardcodes `occ=0` for every object
(`repos/K-Radar/utils/util_pipeline.py:339`).

## Distance/weather/time-of-day/environment stratification — blocked

Frame-index join (`tesseract_idx` ↔ KITTI frame number) remains unresolved.

## Reproducing this report

```
cd repos/K-Radar/scripts/alvis/outputs/robustness_reports
uv run --with polars --with numpy python ../../ingest.py --outputs-dir ../../../outputs \
    --iou-threshold 0.3 --force-backend coordinate --workers 8 --out row_table_iou03.parquet
uv run --with polars --with numpy --with matplotlib --with pyarrow python build_figures.py
uv run --with polars --with numpy --with matplotlib --with pyarrow python build_item2_density.py
```

PNGs copied into `docs/vAIlt/06_Results/robustness_figures/` for stable
embedding here.
