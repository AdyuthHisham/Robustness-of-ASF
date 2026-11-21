# AMSCUP K-Radar Robustness Pipeline — Phase 1 Adversarial Code Review (2026-08-31)

Read-only audit. No files modified. Scope: noise injection → inference → merge → mAP/mRR/RCE/CRI/mFR/transition analysis. Pipeline code: `test-bed/src/Modules/robust_testing/kradar/`; supporting scripts under `repos/K-Radar/` (`datasets/effects/noise_injection.py`, `scripts/alvis/*`, `outputs/robustness_reports/*`, `gt_transition_analysis.py`, `kitti_boxes.py`, gallery/review renderers). mATE/mASE/mAOE searched for exhaustively — **not implemented anywhere in the codebase**, treated as N/A.

**Phase 2 status (2026-08-31): all 4 confirmed bugs fixed, see [Outcome](#3-phase-2-outcome-2026-08-31) below.**

## 1. CONFIRMED BUGS (ranked, terse)

1. **`camera_gaussian_noise` ignores the seeded RNG — uses PyTorch's global RNG instead.**
   `repos/K-Radar/datasets/effects/noise_injection.py:582-597`. Accepts `rng: np.random.Generator` but never uses it; draws via `torch.randn_like(img) * sigma_norm` (global, unseeded, per-DataLoader-worker-independent torch RNG). Contradicts the module's seedable docstring and `EffectConfig.seed`'s reproducibility contract. Worse under `DataLoader(num_workers>0)` (`main_fusion_eval_0.py:643`) — each worker gets an independent torch seed.
   **Impact**: all `camera_gaussian_noise` severities are non-reproducible run-to-run; every downstream Rb/RCE/CRI/churn number for this specific effect is unverifiable. No other effect in the active registry has this defect (verified line-by-line).

2. **`reconstruct_object_ids` / `ingest.py` trk_id backend silently drops Stage-A-unmatched GT objects from transition analysis.**
   `reconstruct_object_ids.py:112, 234-259` (unmatched GT kept with `trk_id=None` instead of flagged/removed) → `ingest.py:439-441,445` (`is_tp = ~is_fp & trk_id.is_not_null()`; join `on=["sequence","frame","trk_id"]` treats `None` as joinable) → `gt_transition_analysis.py:299-309` (`build_match_table_from_ingest` filters on `is_tp`/`is_fn`, both false for these rows; final `.filter(gt_obj_idx.is_not_null())` strips them). ~9.5% of GT lines affected in the one real test run (seq32).
   **Not yet live**: this backend has only run on one sequence; current published churn numbers use the coordinate-fallback backend (unaffected). But it's the backend the project's own plan calls "preferred" — will silently understate denominators/TP/FN counts once run at scale.

3. **`build_figures.py:110` — third RCE implementation missing the zero/null guard the other two copies have.**
   `(pl.col("ap") - pl.col("orig_ap")) / pl.col("orig_ap") * 100`, no `orig_ap == 0` guard (unlike `compute_robustness.py`'s `_rb` and `run_ap_robustness.py:86`). Not triggered in current 58-sequence pooled data, but a live landmine (`inf`/`NaN` → `item3_rce_heatmap.png` color scale) for any future run scoped to a class/sequence subset missing a rare class.

4. **`render_recon_review.py:48` — GT box color B/R channels swapped vs. source-of-truth; GT boxes render cyan instead of yellow.**
   `_GT_COLOR = (230, 230, 0)` vs. `kitti_boxes.py:167`'s correct `(0, 230, 230)` (OpenCV BGR → yellow), which also matches this file's own legend text/swatch `#e6e600`. Redefined locally instead of importing from `kitti_boxes.py`. Cosmetic only, but corrupts visual GT/pred judgment during manual object-ID-reconstruction review.

**Already caught/fixed by the user's team (record only)**: IoU-threshold default mismatch (0.5 vs. pipeline-standard 0.3) in churn scripts, fixed 2026-08-28 (`obsidianVault/Projects/K-Radar/full-denormalized-exploratory-pass.md:60-73`) — same bug class this audit targeted.

**Prior `frame_deletion` RNG-desync bug**: confirmed fixed (`_skip_cache` present) and now structurally unreachable (`mode: deterministic` for all configs since 2026-08-18). Dormant footgun: `_apply_list`'s outer gate and `_frame_deletion_check`'s inner gate still both consult `sub_rng` under unused `mode="random"` — reintroduced if any future config sets that mode.

**Prior `cfg_effect`/`consider_effects` dead-code blockers**: still present, unchanged (`main_fusion_eval_0.py:126-128`, `tools/asf_visualization/main_get_videos.py:65-67` hard-set `consider_effects = False`).

## 2. Stage-by-stage detail

### Noise injection / RNG
All active-registry effects except `camera_gaussian_noise` correctly thread the seeded `rng` through (`rng.normal`/`rng.permutation`/`rng.integers`). `_apply_list`'s outer per-effect gate (`sub_rng.uniform() < p`) fires exactly once per effect per frame regardless of data content — the structural invariant preventing cross-effect/frame desync; holds for every registry entry.

### Ingest / merge
- Frame-identifier bug: confirmed fixed at source (`main_fusion_eval_0.py:772`); all consumers parse the corrected tag consistently.
- Coordinate-fallback join/FN-synthesis (`ingest.py:149-322`): correct, no double-counting, ambiguous trk_id matches logged not silently resolved.
- Dedup-by-latest-experiment-dir and anti-regression guard: sound.
- Risk (not confirmed bug): `reconstruct_object_ids.py`'s `ProcessPoolExecutor` uses default fork after importing torch/open3d/cv2 — same fork-after-init hazard `ingest.py` hit (44-min hang) and fixed via `spawn` elsewhere; not mitigated here.
- Risk: `ingest.py`'s `_use_new_camera_frame_deletion` is an unguarded permanent string patch with no version check.

### Config generation / coverage
Config generation: 33 configs, no duplicates/gaps; no clean/`original` baseline config generated (downstream-assumption trap, not a bug). Coverage script's arithmetic and parsing correct; no pass/fail exit code (usage caveat, not a bug).

### KITTI box conversion (`kitti_boxes.py`)
Column-inverse mapping and 8-corner/rotation formula cross-checked against `util_pipeline.py:dict_datum_to_kitti` and `util_geometry.py:Object3D` — **no axis-swap/sign bug found**. Clean.

### mAP
Ground truth (`eval_revised.py:get_mAP_v2`): 41-point sampled recall, monotonic-envelope precision, `sum(precision[:41])/41*100`. `ap_metrics.py:92-106` reproduces this verbatim — **empirically bit-exact** against the official evaluator on a tested (seq, class, view, IoU) cell. **CORRECT.**
Dead 11-point `get_mAP` in `eval_revised.py`, never wired in — doc trap, not live bug.
Matching is BEV-IoU (KITTI convention), not nuScenes center-distance — deliberate, vault-documented.
**Open risk (SIMPLIFICATION, under-validated)**: `ap_metrics.py` sweeps score thresholds over one fixed global greedy TP/FP labeling; the official evaluator re-derives TP/FP independently at each of the 41 thresholds with different selection rules. Equivalence unproven in general, validated on one cell only — not stress-tested on crowded-detection frames.

### mATE / mASE / mAOE
Not implemented anywhere. Referenced only in a future-tense planning doc.

### mRR / Rb / mRb
`Rb^c = AP_corrupted/AP_clean` (`compute_robustness.py:_rb`, `run_ap_robustness.py:79-107`), correctly zero-guarded. Genuine mean-of-ratios (matches RoboBEV/vault convention), not ratio-of-pooled-means. **CORRECT.**
Documented simplifications (self-disclosed in vault, not hidden): `mean_rb` unweighted across sequences regardless of GT count; per-condition class set can differ since `ap=None` classes are omitted rather than zero-filled.

### RCE
Vault convention: signed `%`-change of AP, `(AP_corrupt-AP_clean)/AP_clean*100` — a deliberate local naming overload of literature RCE, not the bug class being hunted. Two of three implementations guard div-by-zero; the third does not (bug #3).

### CRI
`(mean_AP/clean_AP) × 1/(log(1+σ)+1)`, raw-AP-based (a prior variance-penalty rescaling bug already fixed and verified absent at both call sites). Correctly guards `<2` tiers / null `clean_ap`. **CORRECT** against its own documented formula — cannot independently verify the cited RoHOI source equation from training-knowledge recall (low confidence), treating code's own docstring as spec.
Unreconciled dual implementation: `compute_robustness.py` pools across class×view×IoU per severity tier; `run_ap_robustness.py` pools only across class — numbers not comparable side-by-side even on identical predictions.

### mFR / "flip rate"
No metric literally named `mFR` exists. Closest analog is `gt_transition_analysis.py`'s 4-way per-GT-object churn classification (stable/corruption_induced_miss/corruption_induced_recovery/baseline_failure) — uses a stable, condition-independent GT object index correctly. `net_retention` can exceed 1.0 by design (different-population numerator/denominator) — documented, not a bug. Naming gap if any downstream code expects a literal `mFR` scalar.

### GT-object transition analysis
Pairwise clean-vs-corrupted only, no severity-sequence ordering to get wrong.
Missing-row handling (`build_transition_table`, full outer join + `missing_one_side` warning) correct — but doesn't cover rows already dropped upstream by bug #2.
IoU-threshold mismatch (0.5 vs 0.3): fixed 2026-08-28, current output threshold-aligned.
**Unverified assumption (flagged, not confirmed either way)**: GT boxes assumed bit-identical across compared conditions — asserted only in comments, never checked in code. Highest-value next check given this repo's history of exactly this bug class.
Second, fully-implemented IoU matcher (`build_match_table`/`_canonical_gt`) in the same file is dead code — audit trap since the module's docstring invites using it as a library.

### Data currency
Published churn/transition numbers use the coordinate-fallback backend on data postdating both the frame-identifier fix and IoU-threshold fix — **current**. The trk_id backend (preferred per project plan) is dry-run on one sequence only and carries bug #2 unexercised at scale.

## 3. Phase 2 outcome (2026-08-31)

All 4 confirmed bugs fixed in place, no regressions elsewhere touched. `repos/K-Radar` is a submodule with a large amount of pre-existing unrelated uncommitted work (config deletions, sbatch edits, other `ingest.py`/`merge_predictions_text.py`/`main_fusion_eval_0.py` changes); none of that was staged or committed — only the 4 files below were edited, and nothing was committed per standing instruction to only commit when asked.

| # | Bug | File | Fix | Status |
|---|-----|------|-----|--------|
| 1 | `camera_gaussian_noise` ignores seeded RNG | `datasets/effects/noise_injection.py:590-598` | Noise now drawn via `rng.normal(...)` (seeded numpy Generator) instead of `torch.randn_like` (global torch RNG) | fixed |
| 2 | trk_id backend silently drops Stage-A-unmatched GT | `scripts/alvis/reconstruct_object_ids.py` (`stage_a_rejoin_sequence`, unmatched branch) | Unmatched GT lines get a unique negative sentinel `trk_id = -(line_idx+1)` instead of `None`; survives `is_not_null()` filters in `ingest.py`/`gt_transition_analysis.py` as an FN instead of vanishing. Verified real dataset trk_ids are always non-negative (`info_label_rev2/*.txt`), so no collision risk with real ids or across other unmatched objects in the same frame | fixed |
| 3 | Third RCE implementation missing zero-guard | `scripts/alvis/outputs/robustness_reports/build_figures.py:110` | `pl.when(orig_ap == 0).then(None).otherwise(...)`, matching the guard already in `compute_robustness.py`/`run_ap_robustness.py` | fixed |
| 4 | GT box color B/R channel swap | `scripts/alvis/render_recon_review.py` | Removed the locally-redefined (backwards) `_GT_COLOR`; now imports the correct tuple from `kitti_boxes.py` | fixed |

All 4 edited files pass `python3 -m py_compile`.

### What needs regenerating

- **Bug #1 (camera_gaussian_noise) — regen required, and it's live.** `camera_gaussian_noise` appears in the current published 58-sequence pooled results (`item3_rce_picked.csv` and others). Every number derived from it — noise-injected frames, inference outputs, merged predictions, and every downstream metric (per-severity AP, Rb, RCE, CRI, transition/churn) for this one effect specifically — was produced under a non-reproducible, DataLoader-worker-dependent RNG and should be treated as unverified until rerun. Full chain rerun needed for `camera_gaussian_noise` (all 3 severities) only: noise injection → inference → merge → `ap_metrics`/`compute_robustness`/`run_ap_robustness`/`build_figures` → any `gt_transition_analysis` cells that include it. No other effect is affected — every other registry entry was verified to thread the seeded RNG correctly, so nothing else needs rerunning on account of this bug.

- **Bug #2 (trk_id-backend GT drop) — no regen needed yet, nothing published uses this path.** Current published churn/transition numbers use the coordinate-fallback backend, which never had this bug. The trk_id backend has only been dry-run on one sequence (seq32); worth re-running that same dry run to confirm the fix (expect the previously-observed ~9.5%-of-GT-lines unmatched count to now show up as `is_fn=True` rows in the transition table instead of silently vanishing) before trusting it at full 58-sequence scale.

- **Bug #3 (RCE zero-guard) — no regen needed.** Dormant: no class in the current 58-sequence pooled data hits `orig_ap == 0`, so `item3_rce_heatmap.png` and `item3_rce_picked.csv` are numerically unchanged by this fix. Only matters for a future run scoped to a class/sequence subset missing a rare class.

- **Bug #4 (GT color swap) — re-render only, not a data recompute.** Any already-generated `render_recon_review.py` gallery images (used for the manual object-ID-reconstruction review, see `docs/vAIlt/06_Results/manual-code-vetting-checklist.md`) have GT boxes rendered cyan instead of yellow and should be re-rendered before further manual vetting sessions — cheap, no upstream recompute needed since it's a visualization-only bug.

**Net regen scope**: one targeted rerun of the `camera_gaussian_noise` chain (3 severities) through to metrics/figures, plus a cheap re-render of any existing recon-review galleries. Everything else in the current published results is unaffected by these fixes.

## 4. camera_gaussian_noise regen — done (2026-08-31)

Executed on Alvis (`/cephyr/NOBACKUP/groups/c3se2025-3-18/users/adyuth/AMSCUP/repos/K-Radar`). Full chain:

1. **Fix synced**: rsynced the corrected `noise_injection.py` to Alvis (login-checkout was otherwise current; only the RNG fix line differed).
2. **Inference rerun**: 174 jobs (58 sequences × 3 severities), submitted in 6 batches of ~30 via `submit_run.sh <SEQ> camera_gaussian_noise_{low,medium,high} --confirmed`. All COMPLETED, exit 0:0; prediction counts matched pre-fix frame counts (no crashes, no truncation). New timestamped `exp_*` dirs written alongside the old (buggy) ones.
3. **Merge — required a correction mid-flight.** `outputs/all_preds.txt`/`all_gts.txt` on Alvis turned out to already be stale/partial (only `original` condition — the true durable full-sweep data lives in `outputs/batches/all_{preds,gts}_batch{1..11}.txt`, built incrementally by `run_batched_sweep.sh` with raw per-sequence dumps deleted after each batch's merge, per that script's documented workflow). A naive full rescan of currently-existing raw dumps would have silently dropped the other ~29 conditions (their raw dumps no longer exist on disk, only their already-consolidated batch-file rows do). Corrected approach: concatenated all 11 batch files, filtered out stale `camera_gaussian_noise_*` rows, spliced in the fresh rows from step 2's rescan. Line-count arithmetic checked exactly (824,922 old total − 97,475 stale − 97,499 fresh = 824,946 new total, confirmed). Backups of every intermediate state kept under `outputs/backups/` on Alvis.
4. **Metrics regen**: `run_ap_robustness.sbatch` (ingest.py + ap_metrics.py over the corrected merge) — 30/31 conditions × 9 effects with CRI per sequence, ~10.5 min. `camera_gaussian_noise_{low,medium,high}` mean_rb now ≈0.97–1.02 (sane, monotonic-ish with severity, consistent with a mild camera-only-modality effect in a fusion model — contrast with e.g. `camera_frame_deletion_high`'s Rb≈0.09 collapse).
5. **row_table_iou03.parquet regen**: full-sweep `ingest.py` (IoU 0.3, coordinate backend) on Alvis, 1.1M rows, ~1 min (well under the 3h budget the script's own comments worried about at this scale). Synced back to the local repo (old copy backed up as `row_table_iou03_pre_camgauss_fix_backup.parquet`).
6. **Figures/CSVs regen**: ran `build_figures.py` locally via `uv run --with polars --with matplotlib --with numpy --with pyarrow --with pandas`. Items 1, 3, 4, 5, 6, 8 all regenerated successfully. **Item 7 (`item7_zero_ablation`) failed** — pre-existing, unrelated bug: it filters for a condition literally named `camera_loss_complete`, which doesn't exist in the data (only `camera_loss_complete_zero` does). Not touched — out of scope for this fix, flagged here for a future pass.

Net result: `camera_gaussian_noise` numbers in `item3_rce_picked.csv` and related outputs now reflect reproducible, correctly-seeded noise. No pre-fix snapshot of `item3_rce_picked.csv` was preserved before the regen overwrote it in place, so an exact before/after diff isn't available — only the post-fix values, which are sane and internally consistent with `ap_robustness.json`'s Rb figures.
