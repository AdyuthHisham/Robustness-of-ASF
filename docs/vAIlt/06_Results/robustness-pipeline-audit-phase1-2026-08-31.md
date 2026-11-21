# Robustness pipeline audit — Phase 1 (2026-08-31)

Read-only. Scope: noise injection RNG handling, AP, mRR/Rb, RCE, mATE/mASE/mAOE, mFR, CRI, GT-transition
analysis, and the row-table join/merge stages that feed them. ASF training code untouched (out of scope).

Files read in full: `repos/K-Radar/datasets/effects/noise_injection.py`,
`repos/K-Radar/scripts/alvis/ap_metrics.py`, `repos/K-Radar/scripts/alvis/compute_robustness.py`,
`repos/K-Radar/scripts/alvis/gt_transition_analysis.py`, `repos/K-Radar/scripts/alvis/ingest.py`
(`_load_via_trkid` + `load_prediction_rows`), `test-bed/.../scripts/analysis/master_metrics_table.py`,
`test-bed/.../scripts/analysis/heatmaps.py` (signatures), `test-bed/.../scripts/analysis/crossproduct/metrics.py`.
Cross-checked against `obsidianVault/Knowledge/robustness-metric-selection.md`.

---

## 1. CONFIRMED BUGS ONLY (at-a-glance)

1. **RCE sign inversion between master table and context-breakdown tables** —
   `test-bed/src/Modules/robust_testing/kradar/scripts/analysis/master_metrics_table.py:124` vs `:234`.
   `compute_rce_by()` (feeds `master_metrics_table.csv/.md`) computes `(orig_ap - ap)/orig_ap*100` (degradation
   positive, matches the documented Dong-et-al.-inverted convention). `build_context_table()`'s inline RCE
   (feeds `master_metrics_table_by_{weather,time_of_day,environment}.csv/.md`) computes `(ap - orig_ap)/orig_ap*100`
   — the opposite sign, under the identical column header "RCE". Contaminates: all three
   `master_metrics_table_by_*.csv/.md` files' RCE columns, and any figure/table built from them (any reader who
   reads "RCE" per the module's own documented convention, or per the master table's convention, will read
   corruption-improves-detection where the data means corruption-hurts, and vice versa).

That's the only bug meeting the CONFIRMED bar from this pass. See §2 for everything checked, including two
items flagged for verification rather than confirmed (unproven, not dismissed).

---

## 2. Stage-by-stage detail

### 2.1 Noise injection (`repos/K-Radar/datasets/effects/noise_injection.py`)

**RNG/seed handling.** Master RNG seeded from `config.seed`; each `(modality, name, i)` effect gets its own
sub-generator via `_stable_hash(f"{seed}|{modality}|{name}|{i}") & 0xFFFFFFFF` fed through `np.random.default_rng`.
`_stable_hash` uses `hashlib.blake2b`, not Python's salted `hash()`. This is a **fix already landed** (module
docstring/comments explicitly describe and reference the prior bug where builtin `hash()` desynced sub-seeds
across processes — this matches the class of bug the audit brief calls out from a past review, and the fix here
reads correct: blake2b is deterministic across processes/runs given the same input string). Verdict: **CORRECT**
(as fixed).

**should_skip() / __call__() cache consistency.** `_skip_cache` keyed by `(modality, frame_index)`, written by
`should_skip()`, popped-and-replayed by `_apply_list()` so the pre-load skip decision and the actual apply
decision can't diverge and can't double-consume the sub-rng stream. Verified by reading both methods together —
logic is internally consistent: `should_skip()` draws from `sub_rng` exactly once when `frame_deletion` is
configured, caches the boolean: `_apply_list()` checks the cache first and, if present, replays without drawing.
No frame_deletion effect after the first one in a modality's list is `frame_deletion` (`_apply_list` iterates
over all effects on a name check, would replay for each `name=="frame_deletion"` entry — but only one
`frame_deletion` entry per modality's registry can exist since it's a single dict key), so no double-pop risk.
Verdict: **CORRECT**.

**Frame-index resolution across sensor key spellings.** `_MODALITY_IDX_KEYS` maps injector modality names
(`rdr`/`ldr`/`cam`) and long names to the actual keys the dataset's `meta['idx']` dict uses. Module docstring
records this as the fix for the earlier bug class (deterministic frame_deletion silently never firing for
lidar/camera because the short/long name mismatch made `_get_modality_idx` return `None`). Re-derived
independently by reading `_get_modality_idx` and the dict: logic is correct — first matching key wins, coerces
str→int, returns `None` (declines to delete) only if no candidate key present. Verdict: **CORRECT**.

**`radar_noise_induced_shifts` (NIS).** Confirmed DISABLED — excluded from `RADAR_EFFECTS`/`DEFAULT_ORDER_RADAR`
(grep-verified: not present in either dict/list at lines 668-676 and 703-711). Function body left in place is
inert dead code, clearly marked. Not a bug (not reachable), but flag for the audit's purpose: if anything
outside this module directly imports `radar_noise_induced_shifts` and dispatches it manually, it would run the
flat-meter (not SNR-dial) implementation the docstring says is deliberately not finished. No such import found in
`repos/K-Radar/scripts/alvis/*.py` (grep for `noise_induced_shifts` outside this file: none). Verdict:
**SIMPLIFICATION / non-issue** given current call sites.

**`camera_gaussian_noise` sigma conversion.** `sigma_norm = sigma / 255.0 / 0.229` — approximates pixel-space
sigma→normalized-tensor-space sigma using a single channel's std (0.229, the R channel) for all three channels,
despite the true per-channel std being `(0.229, 0.224, 0.225)`. Docstring calls this out explicitly as
"approximate — using mean std across channels" (misleading comment: 0.229 is not the mean of the three, it's the
R-channel value; the true mean is 0.2263). This under- or over-states injected noise magnitude per channel by up
to ~1.6% (0.229 vs 0.225) — small, but the comment claiming "mean std" is itself inaccurate. Verdict:
**SIMPLIFICATION** (magnitude of the discrepancy is below what would change severity-tier ordering, but the
docstring's characterization of what it's doing is wrong — flagging so it isn't cited as "uses the true per-channel
mean" in the writeup).

**Legacy effects.** Fully quarantined (`ALL_EFFECTS_LEGACY`, never merged into `ALL_EFFECTS`, no call site
found). Not part of the active sweep. Not audited further (explicitly out of the active taxonomy; would only
matter if some script directly imports one, and none do per grep).

### 2.2 mAP (`repos/K-Radar/scripts/alvis/ap_metrics.py`)

**Ground truth.** K-Radar's official evaluator (`utils/kitti_eval/eval_revised.py`) implements KITTI-style
41-point recall-interpolated AP: sample 41 score thresholds spaced evenly in recall from the sorted TP scores
(`get_thresholds`), compute precision at each threshold over the full TP+FP set, take the monotonic-decreasing
envelope, average, ×100.

**Code.** `_get_thresholds` is described as (and, read line-by-line, is) a verbatim port of
`eval_revised.py:get_thresholds`'s recall-spacing logic — same `l_recall`/`r_recall`/`continue` skip condition,
same `current_recall += 1/(num_sample_pts-1)` accumulator. `compute_ap` then sweeps precision at each threshold
over `cum_tp`/`cum_fp` (all TP+FP, score-sorted), applies the same backward monotonic max envelope KITTI uses,
sums and divides by `num_sample_pts` (41), ×100. `num_gt = is_tp.sum() + is_fn.sum()` (not a separate GT count
column) — self-consistent with the row-table's is_tp/is_fn/is_fp booleans as the single source of truth for
what counts as GT.

**Difficulty stratification.** Explicitly and correctly *not* reimplemented — module docstring gives a specific,
checkable reason (K-Radar's KITTI writer hardcodes every 2D bbox to `50 50 150 150` and occluded=0/truncated=0.00
for every object, so every difficulty tier's cutoff is trivially satisfied identically; there is no real
difficulty signal in this data to stratify on). This is a documented simplification with a verifiable basis, not
an unexamined shortcut.

Verdict: **CORRECT** (faithful re-implementation of K-Radar's own evaluator, difficulty-stratification omission
justified and stated).

### 2.3 mRR / Rb (`repos/K-Radar/scripts/alvis/compute_robustness.py`, `master_metrics_table.py`)

**Ground truth (vault convention, `obsidianVault/Knowledge/robustness-metric-selection.md:31-39`).**
RR/mRR (RoboBEV), RS/mRS (MSC-Bench), Rb/mRb (Gao et al.) are the same formula: corrupted-metric / clean-metric
(retention ratio, "higher is better", 1.0 = no degradation).

**Code.** `compute_robustness.py:_rb`: `corrupted_val / original_val`, guarded against `original_val == 0`
(returns `None`, not `inf`/`0`). `master_metrics_table.py:compute_rb`: `val / orig` for every condition against
the single `original` baseline value, same zero/`None` guard. Both match the vault's stated convention exactly.
`master_metrics_table.py:build_master_table` sets `mRR=1.0` for `original` itself (correct: retention against
itself is 1 by definition, not left `None`/computed-and-coincidentally-1).

Verdict: **CORRECT**, in both implementations, and mutually consistent with each other.

### 2.4 RCE (`master_metrics_table.py`)

**Ground truth (vault, `robustness-metric-selection.md:33`; module's own docstring,
`master_metrics_table.py:112-116`).** RCE = Dong et al.'s convention, described in-repo as "inverted" relative to
the RR/Rb family — i.e. `(AP_clean - AP_corrupted) / AP_clean`, positive = degradation, "lower is better" (the
mirror image of the retention-ratio family, not the same formula with a different name).

**Code — two independent implementations, disagreeing:**
- `compute_rce_by` (`:112-125`, used by `build_master_table` → `master_metrics_table.csv/.md`):
  `(orig_ap - ap) / orig_ap * 100.0` — matches the stated convention.
- `build_context_table` (`:209-264`, used for the three `master_metrics_table_by_*` files), inline at `:234`:
  `(ap - orig_ap) / orig_ap * 100.0` — **sign-flipped** relative to `compute_rce_by` and relative to the
  module's own docstring.

**Worked example.** Take a bucket where `orig_ap = 70.0`, `corrupted_ap = 50.0` (a real 20-point AP drop under
corruption — clearly "bad", should read RCE > 0 per the documented convention). `compute_rce_by` (master table):
`(70-50)/70*100 = +28.57` — correctly signals degradation. `build_context_table`'s inline formula for the exact
same numbers in a context bucket: `(50-70)/70*100 = -28.57` — reads as *improvement* under the same "RCE, lower
is better" header. A reader (or a script auto-flagging "conditions with RCE > threshold as concerning") pulling
from the by-weather/by-time_of_day/by-environment tables will get the opposite conclusion from the master table
for the same underlying degradation.

**Downstream contamination:** `master_metrics_table_by_weather.csv/.md`, `master_metrics_table_by_time_of_day.csv/.md`,
`master_metrics_table_by_environment.csv/.md` (all three, all RCE columns) and any figure/table generated from
them. The master table itself and its RCE column are unaffected (uses `compute_rce_by`, the correct-signed path).

Verdict: **CONFIRMED BUG** (file: `test-bed/src/Modules/robust_testing/kradar/scripts/analysis/master_metrics_table.py`,
line 234; correct line should read `(orig_ap - ap) / orig_ap * 100.0`, or better, `build_context_table` should
call the shared `compute_rce_by` instead of duplicating the formula inline).

### 2.5 mATE / mASE / mAOE (`master_metrics_table.py:compute_ate_ase_aoe_by`)

**Ground truth (nuScenes convention, which K-Radar/ASF defer to per project convention).** ATE = 2D Euclidean
center distance in the ground (BEV) plane between matched pred/GT boxes. ASE = `1 - IoU` of the two boxes'
*axis-aligned same-centered* volumes (i.e., dimension-only overlap — rotation and position error factored out,
isolating scale/dimension error). AOE = smallest angular difference between predicted and GT yaw, in radians,
wrapped to `[-π, π]` before taking magnitude.

**Code.**
- ATE (`:136`): `sqrt((loc_x-gt_loc_x)^2 + (loc_z-gt_loc_z)^2)`. `loc_x`/`loc_z` are the same two columns
  `gt_transition_analysis.py` documents as the BEV plane (matches `eval_revised.py`'s `bev_axes=[0,2]` convention
  cited there). Matches nuScenes ATE.
- ASE (`:138-148`): `intersection = min(w,gt_w)*min(l,gt_l)*min(h,gt_h)`, `union = w*l*h + gt_w*gt_l*gt_h -
  intersection`, `ase = 1 - intersection/union`. This is exactly the same-centered-box volume IoU nuScenes ASE
  uses (dimensions only, no position/rotation term) — correct formula, correctly ignoring rotation_y for this
  metric specifically (as it should).
- AOE (`:149-151`): `wrapped = (raw_diff + π) mod 2π - π`, then `abs()`. Standard signed-angle wrap into
  `[-π, π]`; verified algebraically correct (e.g. raw_diff = 350° → wrapped = -10°, |wrapped| = 10°, matching the
  module's own stated example of a 170/-170 pair reading as 20°, not 340°).

Pooling is over `is_tp` rows only (both classes pooled, per the docstring) — correct population for
ATE/ASE/AOE, which are conventionally computed only on matched (TP) pairs, not FP/FN.

Verdict: **CORRECT**, all three, matches nuScenes convention as K-Radar/ASF defer to it.

### 2.6 mFR

Grepped for any frame-level flip/consistency computation across `test-bed/src/Modules/robust_testing/kradar/`
and `repos/K-Radar/scripts/alvis/`: none exists. `master_metrics_table.py`'s own docstring (`:10-13`) states this
directly and explains the 2026-08-28 decision to omit the column entirely rather than fill it with a placeholder.
Verified true by absence — not computed anywhere, not silently wrong. Verdict: **not implemented, correctly
not silently faked** (no bug — nothing to be wrong).

### 2.7 CRI (`repos/K-Radar/scripts/alvis/compute_robustness.py:compute_cri`)

**Ground truth (RoHOI, Wen et al., cited in the code):** `CRI_c = (mean(M_severity) / M_clean) * 1/(log(1+σ_c)+1)`,
population stdev of raw AP values across severity tiers of one effect, not of the retention ratios.

**Code.** `compute_cri` takes `ap_by_severity` (raw AP per tier) and `clean_ap` separately, computes
`statistics.mean(values)`, `statistics.pstdev(values)` (population, not sample — matches "fixed complete tier
set" framing), and returns `(mean_m/clean_ap) / (log(1+sigma_c)+1)`. The docstring includes a specific worked
numeric argument for *why* it takes raw AP rather than pre-divided Rb ratios (computing σ from Rb instead of raw
AP silently rescales the variance penalty by `1/M_clean` before the log stabilizer — verified algebraically
correct: `pstdev(x/k) = pstdev(x)/k` for constant `k`, so an `Rb`-based σ would indeed be `σ_raw/M_clean`,
producing a weaker penalty exactly as the comment describes). Requires ≥2 tiers and nonzero `clean_ap`, returns
`None` otherwise (no silent 0/1 fallback). Grouping by effect (`condition_name` with trailing `_low/_medium/_high`
stripped) in `main()` correctly separates severity tiers into `ap_by_severity` per-effect groups before calling
`compute_cri`, using `mean_corrupted_ap`/`mean_original_ap` (means of AP over the (conf_thr, cls, view, iou) rows
that matched between original and corrupted blocks) as the raw AP inputs.

Verdict: **CORRECT**, matches the cited paper's formula, and the choice of raw-AP-not-Rb input is specifically
justified with a checked-out numeric argument rather than asserted.

### 2.8 GT-object transition analysis (`repos/K-Radar/scripts/alvis/gt_transition_analysis.py`)

**Matching.** Own greedy, class-conditioned, single-IoU-threshold BEV matcher (`match_frame_pairs`), explicitly
documented as distinct from the official KITTI multi-threshold sweep — correct scope statement, not conflated
with AP anywhere in the file or in `master_metrics_table.py`'s usage.

**BEV box construction.** `[loc_x, loc_z, length, width, rotation_y]` — the docstring traces this back to
`eval_revised.py:calculate_iou_partly`'s BEV branch column selection (`bev_axes=[0,2]` after KITTI's h/w/l→l/h/w
reindex) and states the reasoning for reusing exactly that convention rather than re-deriving. Consistent with
the BEV axes used elsewhere (`master_metrics_table.py`'s ATE, same `loc_x`/`loc_z` pair).

**GT object identity across conditions.** `_canonical_gt` picks one condition's GT per `(sequence, frame)`
("original" preferred, else alphabetically-first present), assigns `gt_obj_idx` by within-frame row order, and
matches every condition's predictions against this single canonical table — correctly avoiding the trap of
treating GT as if it could differ per condition (it can't; only sensor input differs) while still giving a stable
key. `build_transition_table`'s join uses `how="full"` and explicitly reports (not silently drops) rows present
in only one condition (`missing_one_side`) — correct handling of the fan-in-fan-out risk a `full` join usually
carries; the join key `(sequence, frame, gt_obj_idx)` is 1:1 on both sides by construction (`gt_obj_idx` assigned
once per canonical frame, both `clean`/`corr` filtered from the same `match_table` keyed the same way), so no
row-count fan-out.

**`classify_transition` four-way split.** `stable`/`corruption_induced_miss`/`corruption_induced_recovery`/
`baseline_failure` — exhaustive and mutually exclusive over the 2×2 `(m_clean, m_corr)` space, matches the
docstring's spec exactly, and is checked with a runtime assertion in `aggregate_transition_rates` (counts must
sum to the per-cell total) rather than assumed.

**`net_retention` — documented non-standard denominator.** `(n_stable + n_recover) / (n_stable + n_miss)`. The
denominator (`stable+miss` = clean-detected population) is *not* the same population as the numerator's second
term (`recover`, drawn from the clean-*missed* population) — the module's own comment (`:467-472`) states this
explicitly and notes the ratio is therefore not bounded to `[0,1]` and can exceed 1 when recoveries outnumber the
clean-miss population. Re-derived independently: this is correct as literally specified (it is a variant, not
the standard "retention" fraction bounded in [0,1]) — flagging per audit instructions since a metric can exceed
its intuitive bound, but the code matches its own documented (if unusual) spec, not a spec violation. Verdict:
**SIMPLIFICATION / caveat, not a bug** — the formula does what it says, but "retention" naming invites a reader
to assume `[0,1]` boundedness that doesn't hold; worth flagging in any figure caption that uses this column.

Verdict overall: **CORRECT** (matching protocol, join safety, four-way classification, assertion-checked
aggregation), with the `net_retention` naming/boundedness caveat noted above (not a bug).

### 2.9 Merge / join stages (`repos/K-Radar/scripts/alvis/ingest.py:_load_via_trkid`)

**Pred↔GT join.** `pred_df.join(gt_for_join, on=["sequence","frame","trk_id"], how="left")` (`:445`). Row-count
safety of a left join here depends on `(sequence, frame, trk_id)` being unique in `gt_for_join` — not
independently re-verified in this pass (would require reading `reconstruct_object_ids.py`'s `trk_id` assignment,
out of the file set actually read this session). **Flagged for follow-up, not confirmed either way**: if
`reconstruct_object_ids.py` ever assigns the same `trk_id` to two GT objects in the same `(sequence, frame)`,
this join silently fans out predictions matched to that `trk_id` into duplicate rows, inflating `is_tp` counts
and downstream AP/ATE/ASE/AOE for whatever `(condition, cls)` cells contain that frame. No evidence found either
way in the files read; do not treat as confirmed.

**FN↔GT join via `gt_line_idx`.** `:468-471`, joins on `["sequence","frame","gt_line_idx"]` where `gt_line_idx`
is assigned as `pl.int_range(pl.len()).over(["sequence","frame"])` on `gt_df`'s file-read row order (`:452`) —
structurally unique per `(sequence, frame)` by construction (a fresh 0..N-1 range per group), so this join key is
safe by construction, no fan-out risk. Comment at `:447-451` gives the ordering assumption this depends on (both
`all_gts.txt` and `all_fn.txt`'s `gt_line_idx` numbering must originate from the same per-frame row order) —
plausible given both are stated to derive from `reconstruct_object_ids.py`'s shared parse, but, like the trk_id
join above, this cross-file ordering invariant was not independently verified against `reconstruct_object_ids.py`
itself in this pass.

Verdict: `gt_line_idx` join — **CORRECT** (unique by construction). `trk_id` join — **UNVERIFIED, not confirmed
bug or correct** (uniqueness assumption not checked against its source file this session).

---

## Findings summary

- CONFIRMED BUG: 1 (RCE sign inversion, `master_metrics_table.py:234` vs `:124` — §2.4)
- SIMPLIFICATION (documented, deliberate, not incorrect): 4 — AP difficulty-stratification omission (§2.2),
  camera_gaussian_noise sigma "mean std" comment inaccuracy (§2.1), `net_retention`'s non-[0,1] denominator
  naming caveat (§2.8), radar NIS left disabled/dead-but-inert (§2.1)
- CORRECT (formula matches paper/nuScenes/vault convention, verified against code): 9 — RNG sub-seeding
  (§2.1), should_skip/__call__ cache consistency (§2.1), modality-key frame-index resolution (§2.1), mAP/41-pt
  interpolation (§2.2), mRR/Rb (§2.3), mATE (§2.5), mASE (§2.5), mAOE (§2.5), CRI (§2.7), GT-transition
  matching+join+classification (§2.8)
- RESOLVED (§2.10): `ingest.py:445` trk_id join uniqueness — **CORRECT by construction, with one unenforced
  data-quality assumption flagged** (see below; no longer UNVERIFIED)
- Not implemented, correctly not faked: mFR (§2.6)

---

## Follow-up: trk_id join-key uniqueness verification

**File read in full:** `repos/K-Radar/scripts/alvis/reconstruct_object_ids.py`. Cross-checked against
`ingest.py:429-445`.

**Ground truth (what the join needs).** `ingest.py:445`'s `pred_df.join(gt_for_join, on=["sequence","frame","trk_id"], how="left")`
is safe (no row fan-out) iff `trk_id` is unique within every `(sequence, frame)` group of `gt_for_join`
(`gt_df` filtered/renamed, `ingest.py:433-437`).

**How `trk_id` is actually assigned (`reconstruct_object_ids.py:stage_a_rejoin_sequence`, `:207-273`).** Three
disjoint cases per GT line, all within one `(seq, frame)`:

1. **Unique Stage-A match** (`:248-251`): `gl.trk_id = candidates[i]["trk_id"]`, `used[i] = True` — copies the
   dataset's own per-object `trk_id` field (`dict_item["meta"]["label"]`'s 3rd tuple element), marks that
   candidate consumed so no other GT line in the same frame can reuse it.
2. **Ambiguous match, `len(matches) > 1`** (`:252-257`): same assignment, `matches[0]` picked, `used[i] = True` —
   still marks the chosen candidate consumed, so a second ambiguous GT line can't independently pick the same
   candidate index. Flagged via `gl.ambiguous = True` / `all_gts_ambiguous.txt`, not silently resolved.
3. **No Stage-A match** (`:258-271`): `gl.trk_id = -(gl.line_idx + 1)` — negative, and `line_idx` (assigned at
   `parse_gts_file:146`, `idx = len(by_frame[key])`) is a fresh per-`(seq,frame)` 0..N-1 counter, so this
   sentinel is unique within the frame by construction and, per the code comment (`:264-269`) and observed
   dataset convention (`info_label_rev2/*.txt`), real `trk_id`s are always non-negative — no collision range
   overlap with case 1/2.

**The `used[]` array is the actual uniqueness enforcement mechanism**, not the values of `trk_id` themselves:
two different `GtLine`s in the same frame can never be assigned the same `candidates[i]` index, because `used[i]`
is checked in the match-list comprehension (`:237, "not used[i]"`) and set immediately after every assignment
(cases 1 and 2 both set it). So even in the ambiguous case, the code cannot double-assign one dataset object's
identity to two different GT lines.

**What is NOT verified by this code (residual, unenforced assumption).** The `used[]` guard prevents the
*reconstruction script* from creating a duplicate — but it does not check whether the raw dataset itself
already contains two *distinct* candidate objects in `dataset_objs` (`:221-232`) that happen to carry the same
real, non-negative `trk_id` value at the source (i.e. an upstream labeling data-quality issue in
`info_label_rev2/*.txt`, not a reconstruction bug). If that were true, two different GT lines could each match a
different candidate index (`used[]` correctly keeps them separate) yet those two candidates' `trk_id` values
would collide, and `gt_for_join` would carry two rows with the same `(sequence, frame, trk_id)` — reproducing
exactly the fan-out risk the audit flagged. **No assertion or dedup check exists anywhere in
`reconstruct_object_ids.py` or `ingest.py` to catch this case if it occurred** — it would fail silently as a
duplicated-row fan-out in the pred_df join, inflating `is_tp` counts for whatever frame(s) it touched.

**Verdict:** `trk_id` uniqueness within a frame is **CORRECT given the reasonable and stated assumption that
the source dataset's per-object `trk_id` field ("this codebase's own convention already treats it as a
persistent cross-frame identity", docstring `:11-14`) is itself unique per object within a frame** — which is
what "persistent object identity" should mean by definition, and is consistent with every failure mode this
script explicitly guards against (ambiguous rounding matches, unmatched GT) being handled by index-based
mechanisms, not trk_id-based ones. Not a CONFIRMED BUG: no code path was found that can *create* a trk_id
collision, and no evidence (data or code) was found of the dataset itself containing one. However, this is a
**data-quality assumption resting entirely on the upstream label files, unverified by any runtime check** —
recommend adding a cheap defensive assertion in `stage_a_rejoin_sequence` (e.g. `assert len({c["trk_id"] for c
in candidates}) == len(candidates)` before matching, or a post-hoc `gt_for_join`-side duplicate check in
`ingest.py` before the join at `:445`) so a real-data violation would raise loudly instead of silently
fanning-out rows. This was not run against actual `all_gts_with_trkid.txt` output (not present in this
environment — reconstruction only runs on Alvis) so it remains an untested-on-real-data assumption, just no
longer an unexamined one.
