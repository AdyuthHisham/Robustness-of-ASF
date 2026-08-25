# Robustness visualization plan (ASF / K-Radar)

Maps the metrics stack (mRR/RS, RCE, mATE/mASE/mAOE, mFR, GT-transition
matrix) and the planned denormalized analysis table onto specific graphs and
their data dependencies. Not implementation — a specification for what to
build once the underlying metrics/matching pipeline (see
`robustness-metric-implementation-plan.md`) produces the needed tables.

## 1. mAP of everything

| Graph | Data needed |
|---|---|
| Grouped bar chart: mAP per (effect × severity), one panel per modality | Per-run mAP values from clean + all corrupted runs; effect/severity/modality as grouping keys |
| Line plot: mAP vs. severity (Low/Med/High), one line per effect | Same, with severity as ordinal x-axis — better than bars for showing degradation *trend* |

Line plot is more useful than bar for the thesis narrative since severity is
ordinal — trend slope is the story, not just magnitude.

## 2. Performance vs. object count in frame

| Graph | Data needed |
|---|---|
| Scatter/binned line: mAP (or per-frame RCE) vs. #objects-in-frame, clean vs. corrupted overlaid | Per-frame object count (derivable from GT annotations per frame_idx), per-frame detection outcome |
| Box plot: per-frame AP distribution, binned by object-count tercile (low/med/high density) | Same, bucketed — box plot shows variance which matters if density affects consistency, not just mean |

This needs a **per-frame** granularity metric, not just per-run mAP — frame-level
AP or at minimum frame-level TP/FP/FN counts.

## 3. Best/worst corruption per sensor × class

| Graph | Data needed |
|---|---|
| Heatmap: rows = 12 effects, columns = {car, bus} × {radar, LiDAR, camera}, cell = RCE (or mAP retention %) | RCE per (effect, modality, class) — most information-dense option for 12×2×3 = 72 cells |
| Ranked horizontal bar (per modality, faceted): effects sorted by mean RCE across classes | Same data, alternate view for write-up prose ("top-3 / bottom-3 most damaging effects") |

Heatmap is the right primary choice — too many combinations for bars to stay
legible. Use a diverging colormap centered at RCE=0.

## 4. FPs and FNs

| Graph | Data needed |
|---|---|
| Stacked bar: FP count and FN count per effect/severity, clean baseline as reference line | Per-run confusion counts — needs matched detections (GT-ID matching module), not just raw pred/GT counts |
| Precision-Recall curves overlaid (clean vs. each severity tier) | Confidence scores per prediction + matched TP/FP/FN — richer than scalar FP/FN, shows where on the operating curve corruption hurts |

FP/FN counts alone conflate confidence-threshold effects with true
degradation — PR curves separate these. Worth doing since the pipeline
retains confidence scores (present in ASF's KITTI-format output).

## 5. Does frame_deletion affect detection

| Graph | Data needed |
|---|---|
| Line plot: mAP/mFR over frame index within a sequence, with deleted frames marked (e.g., shaded/dashed) | Per-frame detection results + which frames were deleted, per sequence |
| Before/after comparison: mFR for frame_deletion vs. loss_complete side by side | Directly tests whether the two flagged-as-possibly-redundant effects are empirically distinguishable |

Since `frame_deletion` vs `loss_complete` was flagged as a possible design
redundancy, a direct RCE/mFR comparison between them (not just each vs.
clean) is worth its own figure — it either confirms redundancy (supports
merging) or reveals a difference (justifies keeping both).

## 6. Churn statistics (noisy vs. original)

Maps directly onto the GT-object transition analysis module
(`gt_transition_analysis.py`).

| Graph | Data needed |
|---|---|
| Alluvial/Sankey diagram: GT objects flowing between {stable detection, corruption-induced miss, corruption-induced recovery, baseline failure} states, clean → corrupted | The transition matrix itself, per effect/severity |
| Stacked bar: proportion of GT objects in each of the 4 categories, per effect/severity | Same data, more compact — better for many-effect comparison; Sankey better for a single highlighted effect in the main text |
| Line plot: churn rate vs. severity, one line per effect | Derived churn rate metric across severity tiers |

Sankey for 1-2 illustrative effects in the main narrative, stacked bar for
the full sweep in an appendix — avoids a wall of Sankeys nobody can compare.

## 7. Zero-value ablation across sensors

Frame explicitly as *retention relative to full-sensor baseline*, not
"robustness" — zeroing a sensor input is not a neutral no-signal condition
(BatchNorm/conv-bias make zero non-neutral to the network).

| Graph | Data needed |
|---|---|
| Grouped bar: mAP retention % when {radar=0, LiDAR=0, camera=0} vs. full-sensor baseline, per class | Three additional inference runs with each modality zeroed independently |
| Radar/spider chart: retention % across the three zeroed-sensor conditions, per class | Same data — makes relative sensor-importance ranking visually immediate, but only pair with a raw-numbers table since spider charts distort magnitude perception |

Default to grouped bar as primary; skip the radar chart unless a presentation
specifically needs the "at a glance" framing.

## 8. mATE, mASE

| Graph | Data needed |
|---|---|
| Grouped bar: mATE and mASE per effect/severity, clean baseline as horizontal reference line, separate panels for translation vs. scale error | Matched TP boxes (pred vs. GT) with position/dimension deltas — depends on the GT-ID matching module |
| Scatter: mATE vs. mASE per condition, colored by effect, to see if translation and scale errors move together or diverge | Same — useful for the NIS-vs-Gaussian mechanistic distinction, since NIS (range/RCS-correlated) may show a different ATE/ASE signature than uniform Gaussian noise |

The scatter is the strongest tool for the NIS-vs-Gaussian methodological
argument — if NIS and Gaussian noise cluster in different regions of
ATE/ASE space, that's direct empirical support for keeping them as separate
effects.

---

## Stratification factors (distance, weather, time-of-day, environment)

Not separate graphs — **facet/slice dimensions** applied to any of the
above, which is exactly what the denormalized analysis table is for.

| Factor | Recommended treatment | Data needed |
|---|---|---|
| **Distance from ego** | Line plot: RCE vs. distance bin (near/mid/far), one line per effect, faceted by modality | Distance-bin field (`obj_distance_ego` in `kradar_test_split_full.parquet`, once the frame-index enrichment join is wired in) |
| **Weather** | Grouped bar: mAP retention by weather category × effect | Scene context field (`weather` in the same parquet) |
| **Time of day** | Same as weather, or a paired box plot (day vs. night) per effect | Scene context field |
| **Environment** | Same pattern as weather | Scene context field |
| **Occlusion** | Line plot: RCE vs. occlusion-proxy bin, once the derivation methodology is settled | Blocked — no real occlusion signal exists anywhere in the pipeline (K-Radar hardcodes `occ=0`); this graph cannot be built until/unless that upstream gap is resolved |

Practically: build one denormalized table (prediction outcome + all
stratification fields), then generate distance/weather/time/environment
breakdowns as faceted small-multiples of the primary mAP and RCE plots
rather than bespoke graph types per factor — single-sourced analysis
pipeline, not duplicated join logic per factor.

## Open dependency

Items 3, 4, 6, and 8 all require the GT-object spatial matching module to be
finalized first (matched TP/FP/FN with identity linkage) — that is the
current bottleneck upstream of most of this visualization work. See
`robustness-metric-implementation-plan.md` for matcher status (coordinate
backend validated on real data; trk_id backend still flagged as flawed and
excluded pending a fix to `reconstruct_object_ids.py`'s Stage B box-format
bug).
