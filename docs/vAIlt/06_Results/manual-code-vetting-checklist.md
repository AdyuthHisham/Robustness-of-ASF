# Manual code-vetting checklist — robustness pipeline (Phase 1 audit, read-only)

Generated 2026-08-31. Scope correction from the task brief: the actual corruption →
inference → merge pipeline lives in `repos/K-Radar/` (submodule), not
`test-bed/src/Modules/robust_testing/kradar/` — that testbed module is the separate
per-object visibility-scoring subproject. Only Stage 4 (`master_metrics_table.py`)
lives in the testbed. All other paths below are relative to `repos/K-Radar/` unless
marked `[testbed]`.

Read in the order below — each stage's checklist assumes you already understand the
previous stage's data contract.

---

## BLOCKING QUESTIONS — resolved 2026-08-31 (see below); original 5 questions kept for record

1. **Deployment gate — RESOLVED.** `asf_run.sbatch` L86 confirms the
   `pipeline_detection_v1_0.py` bind-mount was added 2026-08-26 (same day the gap was
   found); the `dict_out = dict_datum` fix is present in source (L549, L830 of
   `pipelines/pipeline_detection_v1_0.py`). Cross-referenced against
   `alvis-wipe-audit-2026-08-28.md`: the full ASF corruption sweep ran **2026-08-27**
   — after the fix landed — and `all_preds.txt`/`all_gts.txt`/batch files are dated
   2026-08-27. **Current data reflects the fixed frame-identifier code.** Residual
   caveat, unrelated to the frame-id fix: 144 `camera_frame_deletion_new_{low,medium,high}`
   runs crashed mid-run (container exit 134, only 1 partial prediction file written) —
   decide whether that condition/severity combo still needs a rerun before trusting
   it in any final table.
2. Trk_id backend — **dropped per user**, not used, not planned to be validated;
   `ingest.py` runs the coordinate/IoU fallback in practice.
3. **Merge duplicate-row risk — RESOLVED, no bug found.**
   `scripts/alvis/merge_predictions_text.py` (L34–39, L66–97) actively guards this:
   only reads `all/preds` (not the 4x road/time/weather-duplicated subdirs written by
   `pipeline_detection_v1_0.py`), and when multiple `exp_*` reruns exist for one
   `(sequence, condition)` reads only the **lexicographically-latest** one (L70–73,
   exp dir names embed `YYMMDD_HHMMSS` so string-max == most recent) — prevents
   double-counted reruns. GT dedup is `(sequence, frame)`, first-occurrence-wins
   (L86–97). The `--seqs` comma-truncation bug that caused real data loss
   (see `official-checkpoint-rerun-2026-08-26.md`) was a separate, already-fixed
   issue in the batch driver, not in this dedup logic.
4. **Cross-check between metric paths — CONFIRMED GAP.** `compare_smoke.py` and
   `compare_parquets.py` are *not* a cross-check between `master_metrics_table.py`
   and `compute_robustness.py` — the former compares clean-vs-noisy displacement on
   6-frame smoke data, the latter diffs two checkpoint-era row-tables (self-trained
   vs. official checkpoint). The only real cross-check on record is in
   `official-checkpoint-rerun-2026-08-26.md`: AP computed independently via
   `ap_metrics.py`/`ingest.py` vs. K-Radar's own `eval_revised.py` agrees to ~0.01,
   but only for AP, only on the `original` (clean) baseline, one time. **RCE, mRR,
   and CRI have never been cross-checked between the row-table path and the
   complete_results.txt path.** Worth a manual spot-check on at least one corrupted
   condition before relying on either for the thesis.
5. `mFR` omission — **dropped per user**, not used/reported.

---

## Stage 1 — Noise injection

### `datasets/effects/noise_injection.py` (~1270 lines)

| | |
|---|---|
| **Logic** | `NoiseInjector` class L733–939; dispatch via `_apply_list`/`__call__`/`should_skip` L824–930; registries `RADAR_EFFECTS`/`LIDAR_EFFECTS`/`CAMERA_EFFECTS` L666–690 |
| **What it does** | Applies configured per-modality corruption effects to a sample dict, with seeded per-effect sub-RNGs for reproducibility |
| **Verify** | (a) `_stable_hash`/`_sub_rng` (L56–79) — re-run the same config+seed twice, confirm byte-identical corrupted output (this is the fix for Python's salted `hash()` breaking cross-process reproducibility — exactly the RNG-desync failure class you've hit before). (b) `_resolve` (L801) derives seed from `blake2b(seed\|modality\|name\|i)` where `i` is the effect's **list index** — confirm reordering effects in a YAML is understood to shift every subsequent effect's seed stream (implicit contract, not a bug, but confirm it's not surprising you). (c) `_get_modality_idx`/`_MODALITY_IDX_KEYS` (L94–129) — this is the fix for the previously-documented bug where `frame_deletion` silently never fired for lidar/camera due to key-name mismatch; trace that `dict_item['meta']['idx']` is actually populated with `rdr`/`ldr64`/`camf` keys at the real call site in `datasets/kradar_detection_v2_1.py`, not just in tests. |
| **Why it matters** | If reproducibility fails silently, every seeded corruption run is uncontrolled and thesis results aren't reproducible. If `frame_deletion` still doesn't fire per-modality, entire ablation conditions are silently no-ops. |

| | |
|---|---|
| **Logic** | `DEFAULT_ORDER_RADAR`/`_LIDAR`/`_CAMERA` constants L701–725 vs. actual execution order in `_apply_list` |
| **What it does** | Documents an intended effect ordering (blackout last) that is **not enforced in code** |
| **Verify** | Grep every YAML under `configs/noise/` for effect list ordering; confirm `loss_complete`/`loss_complete_zero` is listed last in every config that combines it with an in-place effect (`gaussian_noise`, `loss_partial`) in the same modality. |
| **Why it matters** | A misordered config would run an in-place noise effect on data that's about to be blacked out (harmless — wasted work) — or worse, blackout could run before an in-place effect that a downstream fallback branch needs pristine (see next entry). This is unenforced-by-code, so a future config change won't fail loudly. |
| **Suspicious** | This is a real gap: constants exist that *look* like they enforce ordering but don't. Flag explicitly rather than trusting the comment. |

### `datasets/effects/eval_wrapper.py` (369 lines)

| | |
|---|---|
| **Logic** | `NoiseInjectedDataset.__getitem__` L183–243; `install_blackout_hooks` L337–369 |
| **What it does** | Glues `NoiseInjector` into the eval loop; saves "pre-injection" sensor references before corruption for use by `zero_feature`/`last_frame_hold` blackout policies' encoder-input fallback |
| **Verify — highest priority in Stage 1** | The "pristine" reference saved at L188–199 is only actually pristine for **rebinding** effects (blackout sets the key to `None`) — **in-place** effects (`gaussian_noise`, `loss_partial`) mutate the array the reference points to (docstring admits this at L199–202). Pick a real `configs/noise/*.yml` that combines a blackout effect with an in-place effect on the *same modality*, and hand-trace whether the "clean" fallback array used by `zero_feature`'s encoder input (L306–310) has actually been corrupted by the in-place effect that ran first. |
| **Why it matters** | If this leaks, the `zero_feature` blackout condition — meant to represent "sensor completely absent" — is silently contaminated with noise instead of testing a true zero-input branch. This would invalidate any ablation conclusion drawn from that condition. |

| | |
|---|---|
| **Logic** | `should_skip()` / `_skip_cache` L758–763, 891–930 |
| **What it does** | `should_skip()` is called before frame I/O to decide whether to skip loading; the boolean decision is cached and *replayed* (not redrawn) when `__call__()` runs later for the same frame |
| **Verify** | Confirm every call site that calls `should_skip()` for a given frame always subsequently calls `__call__()` for that exact frame (unbounded cache growth risk is documented in the class's own docstring caveat, L774–778 — check it hasn't become a real memory issue on long Alvis runs). Reading suggests this is internally consistent (re-verified during audit: idempotent under repeated `should_skip()` calls, different cache keys per modality), but do one integration-test trace since it's the second-most RNG-sensitive part of Stage 1. |
| **Why it matters** | If `should_skip()`'s cached decision and `__call__()`'s applied decision ever diverge, a frame could be I/O-skipped as "corrupted-away" but not actually corrupted in the label/metric path (or vice versa) — silent mismatch between what was skipped and what was scored. |

### Dead code / suspicious, no fix needed

- `# LEGACY EFFECTS` block, L942–1268 (~330 lines, 18 functions) — not in `ALL_EFFECTS`, not registry-reachable, only invocable via manual import by name. **Verify with one grep**: `grep -rn <function names>` across `scripts/` and `configs/` to confirm nothing references these — if clean, treat as confirmed dead.
- `radar_noise_induced_shifts` (L244–296) — defined but excluded from `RADAR_EFFECTS`/`DEFAULT_ORDER_RADAR` since 2026-08-17 pending SNR reparameterization. Grep `configs/noise/*.yml` for `noise_induced_shifts` — if present it'll raise `ValueError` at resolve time (loud failure, low risk), but confirm no stale config references it.

---

## Stage 2 — Inference

| | |
|---|---|
| **Live entry point** | `scripts/alvis/asf_run.sbatch` (+ `asf_official_benchmark*.sbatch`, `asf_smoke.sbatch`) → `scripts/main_fusion_eval_0.py` → `pipelines/pipeline_detection_v1_0.py` (`validate()`/`test()`) |
| **What it does** | Runs ASF model forward passes over corrupted samples produced by Stage 1 |
| **Verify** | 1. Confirm the sbatch `BINDS` list actually mounts the fixed `pipeline_detection_v1_0.py` and `main_fusion_eval_0.py` into the container — this is BLOCKING QUESTION 1 above; do this check before reading anything downstream. 2. Confirm the `except: dict_out = dict_datum` fix (from the frame-identifier-bug fix report) is present in whatever copy is actually executed, not just in git source. |
| **Why it matters** | This is the single highest-leverage check in the whole audit: if the container runs a stale copy, every downstream join keyed on frame identity (Stage 3, Stage 4's GT-transition analysis) inherits silently-wrong frame labels — the exact failure mode that already produced a false 0% mAP result on bus/university sequences before being caught. |

---

## Stage 3 — Merging inference data

Read `reconstruct_object_ids.py` before `ingest.py` — the latter conditionally
depends on the former's output files.

### `scripts/alvis/reconstruct_object_ids.py` (508 lines)

| | |
|---|---|
| **Logic** | Whole file — builds trk_id-based GT/pred matching, writes `all_gts_with_trkid.txt` / `all_preds_with_trkid.txt` / `all_fn.txt` |
| **What it does** | Preferred (higher-fidelity) backend for associating predictions with ground-truth objects by tracker id rather than by coordinate/IoU matching |
| **Verify** | Per `ingest.py`'s own docstring, this backend is "implemented but unvalidated against real data" — confirm current validation status (BLOCKING QUESTION 2). If validated, spot-check that `trk_id` is unique within a `(sequence, frame)` — no such uniqueness assertion exists in the consuming join (see below); a duplicate trk_id in one frame would silently fan out. |
| **Why it matters** | This determines which of two matching backends is actually producing your row table — a materially different question from "is the row table correct," since the two backends use different matching logic entirely. |

### `scripts/alvis/ingest.py` (566 lines)

| | |
|---|---|
| **Logic** | `load_prediction_rows()` L492 (entry point); `_parse_preds_txt` L166–203; `_match_via_coordinates` L231–322 (fallback, calls `gt_transition_analysis.match_frame_pairs`); `_load_via_trkid` L429–481 |
| **What it does** | Canonical row-table builder. Auto-selects the trk_id backend if all three trkid files exist, else falls back to coordinate/IoU matching. Row grain is `(sequence, frame, condition, prediction)` for TP/FP plus one synthesized FN row per unmatched GT object (stated explicitly L29–31). |
| **Verify — join-key uniqueness (your specific concern)** | No explicit uniqueness assertion exists anywhere in this file for the row grain. Three separate places rely on unstated invariants: (1) real prediction rows assume each parsed line in `all_preds.txt` is unique per `(seq, frame, condition)` — confirmed only if `merge_predictions_text.py` guarantees single-write (BLOCKING QUESTION 3, not yet traced); (2) trk_id join (L429–445) joins on `(sequence, frame, trk_id)` assuming `trk_id` non-null and unique per `(sequence, frame)` in `gt_df` — unchecked; (3) FN join in the trk_id backend (L447–481) matches on `gt_line_idx`, relying on **positional-order equivalence** between `all_gts.txt`'s per-frame block order and the trk_id file's per-frame row order — this is a second frame-identity-adjacent positional-alignment assumption, same failure class as the Stage 2 frame-identifier bug. Spot-check a few `(seq, frame)` blocks where `gt_line_idx == N` in both files to confirm they point at the same physical object. |
| **Verify — silent condition drop/rename** | `_use_new_camera_frame_deletion` (L64–75) silently drops rows for the known-buggy `camera_frame_deletion_{low,medium,high}` condition and renames `camera_frame_deletion_new_*` down to the plain name. Confirm this transform is applied at all three call sites consistently (pred parsing, trk_id pred_df, fn_df) — if a 4th ingestion path exists that bypasses it, row counts for that condition would silently include the buggy run's near-zero-coverage data. |
| **Verify — dummy-frame handling** | L149–203 (esp. L159–164): confirm the current code correctly separates `dummy`-marker lines (K-Radar's "zero real predictions" placeholder) from real FP rows — a prior version of this logic miscounted ~47,307 dummy rows as real FPs (fixed as of 2026-08-20 per prior notes). Confirm you're reading the fixed version, and that dummy-frame GT objects still correctly synthesize FN rows via `_frame_groups()` L262–266. |
| **Why it matters** | Any fan-out here silently multiplies FP/FN counts feeding every downstream metric (mAP, mRR, CRI). A dropped/mis-renamed condition silently changes what condition's numbers you think you're reporting. |

---

## Stage 4 — Generating metrics

Read `gt_transition_analysis.py` before `ap_metrics.py` (the latter's matching reuses
the former's threshold), and read both before the two metrics-table scripts below.

### `scripts/alvis/gt_transition_analysis.py` (541 lines)

| | |
|---|---|
| **Logic** | `match_frame_pairs` L155–192 (BEV-IoU greedy matcher); `DEFAULT_IOU_THRESHOLD = 0.5` L104; `build_match_table` |
| **What it does** | The actual IoU-matching logic reused by both `ingest.py`'s coordinate-fallback backend and this module's own GT-object-transition analysis |
| **Verify — threshold source-of-truth (your specific concern)** | `DEFAULT_IOU_THRESHOLD` here is one hardcoded `0.5` literal; `ingest.py`'s `load_prediction_rows(..., iou_threshold: float = 0.5)` (L498) is an **independent second hardcoded `0.5`**, not imported from this constant. They currently agree by coincidence, not by construction. If you ever tune the IoU threshold, you must change both — confirm this before any threshold-sensitivity analysis in the thesis, and consider whether to flag/fix this duplication before Phase 2. |
| **Why it matters** | A silently-diverged threshold between the matcher used for row-table construction and the one used for GT-transition analysis would make the two analyses inconsistent with each other without any error. |

### `scripts/alvis/ap_metrics.py` (128 lines)

| | |
|---|---|
| **Logic** | `compute_ap`/`compute_ap_grouped`, whole file |
| **What it does** | Ports K-Radar's own official evaluator's (`eval_revised.py`) thresholding logic verbatim, for comparability with `complete_results.txt` |
| **Verify** | Confirms it deliberately does **not** reimplement difficulty stratification, reasoning that K-Radar's KITTI writer hardcodes a dummy 2D bbox (`util_pipeline.py:339`), making difficulty strata degenerate. Verify that hardcoded-bbox claim still holds in the currently-deployed (bind-mounted) pipeline copy — same deployment-gate risk as Stage 2. |
| **Why it matters** | If the KITTI writer's hardcoded bbox assumption changes upstream, this module's simplification becomes silently wrong (would compute AP without real difficulty stratification while believing it's equivalent to the official evaluator). |

### `test-bed/src/Modules/robust_testing/kradar/scripts/analysis/master_metrics_table.py` [testbed]

| | |
|---|---|
| **Logic** | `METRIC_COLUMNS = ["mAP", "mATE", "mASE", "mAOE", "RCE", "mRR"]` L78; `compute_rb` L171 |
| **What it does** | Row-table-based metrics aggregation, consumes `ingest.py`'s output. `mRR` computed as corrupted/original ratio (RoboBEV-style Rb metric). |
| **Verify** | `mFR` is absent from `METRIC_COLUMNS` — read the full module docstring (L1–20, truncated during audit) for the stated reason and confirm it matches what the thesis claims to report. If `mFR` appears in any results table elsewhere in the repo, that's a live inconsistency to resolve. |
| **Why it matters** | A metric silently missing from the canonical table, if also expected in the thesis, means you're either missing analysis or computing mFR from a different (uncross-checked) path. |

### `scripts/alvis/compute_robustness.py` (341 lines)

| | |
|---|---|
| **Logic** | `compute_cri` L120 (cites RoHOI Wen et al. arXiv:2507.09111v3 Eq. 2); whole file |
| **What it does** | A **second, independent** metrics path — parses `complete_results.txt` (K-Radar's own evaluator's text output) directly, rather than consuming `ingest.py`'s row table |
| **Verify — cross-check (your specific concern)** | Confirm whether this path's numbers are ever cross-checked against `master_metrics_table.py`'s row-table-based numbers for overlapping metrics. `compare_smoke.py`/`compare_parquets.py` exist in `scripts/alvis/` suggesting this was done at least once — find and read those results, and confirm the thesis doesn't unknowingly mix numbers computed via two different pipelines for what's presented as one consistent metric. |
| **Why it matters** | Two independently-implemented paths computing "the same" metric is a classic source of silent divergence — if they disagree, one is wrong (or the frame-identifier bug from Stage 2 propagated differently into each), and the thesis needs to know which. |

---

## Formula verification against source papers (2026-08-31)

Per your follow-up: (a) `camera_frame_deletion_new` is to be ignored/dropped entirely
(no rerun), and (b) verified whether mATE/mASE/mAOE/RCE/mRR/CRI in
`master_metrics_table.py` [testbed] and `compute_robustness.py` match the formulas
in their cited source papers. Checked against: nuScenes devkit detection README
(mATE/mASE/mAOE), Dong et al. CVPR 2023 "Benchmarking Robustness of 3D Object
Detection to Common Corruptions" (RCE, via a robustness survey that quotes it
directly — arxiv 2401.06542), RoboBEV/MSC-Bench/Gao et al. convention (mRR/Rb, per
this repo's own `robustness-metric-selection.md`), and RoHOI (Wen et al., arXiv
2507.09111, Eq. 2, for CRI).

### CONFIRMED BUG — RCE sign is inverted relative to Dong et al.'s definition

`compute_rce_by` (`master_metrics_table.py` L112–125) computes:
```
RCE = (ap - orig_ap) / orig_ap * 100        # i.e. Rb - 1, as a percentage
```
Dong et al.'s actual published RCE (confirmed via a survey paper that quotes it
directly, `RCE = (AP_clean - AP_corrupted) / AP_clean`, tables labeled `RCE(%)↓` —
lower is better, positive RCE = degradation) is:
```
RCE = (orig_ap - ap) / orig_ap * 100        # i.e. 1 - Rb, as a percentage
```
**These are exact negations of each other, not just a scaling difference.** Under
the code's current formula, a corrupted run that performs *worse* than clean
produces a **negative** RCE; under Dong et al.'s convention (and this repo's own
`robustness-metric-selection.md`, which explicitly describes RCE as "Dong et al.,
inverted convention" of the Rb retention formula — i.e. `1 - Rb`, not `Rb - 1`), a
worse-performing corrupted run should produce a **positive** RCE, with lower/negative
being better. The code's RCE is literally `Rb - 1`, not the paper's `1 - Rb`.
**This is not a rounding or edge-case issue — every RCE value currently in any
generated table has the opposite sign from what the cited literature (and this
project's own metric-selection note) defines.** If reported as "RCE" in the thesis
with a citation to Dong et al. or compared against any external RCE table, the sign
will read backwards. Fix is a one-line change (`(orig_ap - ap) / orig_ap * 100`) —
flagging per Phase 1 scope (no code changes made).

### CONFIRMED BUG — mASE does not compute nuScenes' `1 - IoU`

nuScenes defines ASE as `1 - IoU` "after aligning centers and orientation" — i.e.
true 3D intersection-over-union of the two boxes once translation/rotation are
factored out. `compute_ate_ase_aoe_by` (`master_metrics_table.py` L138–152, reused
from `heatmaps.py`) instead computes:
```
ase = 1 - (min(w,gt_w)*min(l,gt_l)*min(h,gt_h)) / (max(w,gt_w)*max(l,gt_l)*max(h,gt_h))
```
This is a per-axis min/max volume ratio, **not** true IoU — the denominator should
be the union volume (`vol1 + vol2 - intersection`), not `max(w)·max(l)·max(h)`.
These coincide only when the two boxes' dimensions are proportional along every
axis (e.g. isotropic scaling); they diverge for anisotropic size errors. Concrete
counter-example: box A = (4,1,1), box B = (1,4,1) (same volume, different aspect
ratio) — true `1-IoU` (centered/aligned) = 1 − 1/7 ≈ **0.857**; the code's formula
gives 1 − 1/16 ≈ **0.9375** — a ~9-point absolute difference for two boxes that are
symmetric permutations of each other and should score identically either way (both
formulas are at least symmetric under that permutation, but they disagree with each
other on the actual value). Values will be numerically wrong wherever predicted/GT
box aspect ratios diverge, which is exactly the regime `mASE` exists to catch (shape
distortion under corruption) — this is precisely the failure mode most likely to be
misreported. Needs a fix (true union-volume denominator) before mASE numbers are
citable as "nuScenes-style ASE."

### Simplification, not a bug, but a real deviation — mATE/mASE/mAOE averaging protocol

nuScenes' TP metrics are computed as "the average of the cumulative mean at each
achieved recall level above 10%," with all TP errors for a class set to 1 if 10%
recall isn't reached — a confidence-threshold-integrated protocol. This codebase's
`compute_ate_ase_aoe_by` instead takes a flat mean over all `is_tp` rows at
whatever single confidence threshold the row table was built at (`iou03` in the
current parquet name). This is a legitimate simplification given a single fixed
operating point rather than a full PR-curve sweep, but it means the numbers are not
directly comparable to a paper reporting true nuScenes-protocol mATE/mASE/mAOE —
worth a footnote in the thesis rather than a claim of exact NDS-style equivalence.

### CONFIRMED MATCH — CRI (RoHOI, Eq. 2)

`compute_cri` (`repos/K-Radar/scripts/alvis/compute_robustness.py` L120–150) computes
`(mean_M_c / M_clean) / (log(1 + sigma_c) + 1)`, which matches RoHOI's published
Eq. 2 `CRI_c = (M̄_c/M_clean) · 1/(log(1+σ_c)+1)` exactly, including the log-stability
term and the clean-normalization placement (confirmed this is *not* accidentally
computed from pre-normalized Rb ratios — the code's own docstring explains why that
would be wrong, and the implementation takes raw AP values as the paper does). One
open ambiguity: the paper doesn't explicitly state population vs. sample stdev for
σ_c; the code deliberately uses population stdev (`statistics.pstdev`) with a
documented justification (severity tiers are a fixed complete set, and it degrades
gracefully to σ=0 for the 1-tier edge case). This is a defensible reading of an
underspecified paper detail, not a confirmed deviation — flagging only because it
is a judgment call, not something to silently assume matches the paper's own
(possibly sample-stdev) implementation if you ever diff against their reference
code.

### CONFIRMED MATCH — mRR / Rb

`compute_rb` in both `master_metrics_table.py` (L171–178) and
`heatmaps.py` computes `corrupted_value / original_value` against the single global
clean baseline — matches the convergent RR/mRR (RoboBEV) / RS/mRS (MSC-Bench) /
Rb/mRb (Gao et al.) formula family exactly, as this repo's own
`robustness-metric-selection.md` already documents. No deviation found.

### `camera_frame_deletion_new` — excluded per your instruction

Confirmed excluded from `master_metrics_table.py`'s condition set already (it's not
in `SENSORS`/`EFFECTS`/`SEVERITIES`-derived `CORRUPTED_CONDITIONS`, L64–73 — only
`gaussian_noise`/`loss_partial`/`loss_complete_zero` per sensor are included; camera
frame-deletion variants were never in this table's scope to begin with). No
action needed there. The 144 crashed runs from the wipe-audit note concern a
different table (`compute_robustness.py`'s complete_results.txt path / raw sweep
logs) — since you've said to ignore this condition family entirely, no rerun or
further tracing needed on either path.

## Summary of flagged issues (no fix — for your review only)

1. Stage 2 deployment gate unresolved — highest priority, gates everything downstream.
2. Stage 1: blackout-vs-in-place-effect ordering is documented but unenforced in code; possible clean-fallback contamination.
3. Stage 3: no join-key uniqueness assertions anywhere (pred rows, trk_id join, FN positional join) — all rely on unchecked upstream invariants.
4. Stage 4: IoU threshold 0.5 duplicated as two independent hardcoded literals instead of one imported constant.
5. Stage 4: two independent metric-computation paths exist with no enforced (only ad hoc) cross-check.
6. Stage 1: ~330 lines of legacy dead effect code, plus one disabled effect (`radar_noise_induced_shifts`) — believed dead, not exhaustively grep-confirmed in this pass.
7. Stage 3: `merge_predictions_text.py` not yet traced — needed to close out blocking question 3.

## Blocking questions (repeated from top for visibility)

See "BLOCKING QUESTIONS" section above — 5 items, all require your input, not resolvable by reading alone.

---

**STOP — Phase 1 complete. Do not proceed to Phase 2 without explicit approval.**
