# ASF Corruption Study — Alvis (2026-08-11/12)

**Repo:** `repos/K-Radar` (on Alvis: `~/AMSCUP/repos/K-Radar`)
**Results:** `outputs/alvis_smoke/RESULTS.md`, `outputs/alvis_smoke/corruption_summary.csv`
**Gallery:** `outputs/alvis_smoke/gallery/index.html` (clean-vs-corrupted BEV + camera renders, with detected/GT box overlays)

Supersedes [[kradar-effects-audit]] (2026-07-20), which audited an older, non-functional
effects system in `kradar_fusion_v1_0_calib_change.py`. The system actually used here —
`datasets/effects/noise_injection.py` + `datasets/effects/eval_wrapper.py` — is fully
implemented and was exercised end-to-end on Alvis, not just audited. See also
[[asf-training-inputs]] for the sensor→encoder mapping this study perturbs.

## What was done

Ran ASF (A2Fusion) inference on a fixed 6-frame sample (K-Radar seq 1 & 2, 3 densest
frames each) under 9 single-effect conditions — the canonical taxonomy (frame_deletion,
gaussian_noise/noise_induced_shifts, loss_partial) × 3 modalities (radar/lidar/camera) —
plus two `_zeros` conditions (all-zero-but-well-formed frame) as a substitute for the two
blackout conditions that crash the model. Every condition corrupts exactly one modality;
everything else stays clean.

## Headline finding: sensitivity ranking

**LiDAR ≫ radar > camera**, on this 6-frame/19-baseline-detection sample:

| Corruption | Detections (clean=19) |
|---|---|
| LiDAR gaussian_noise (σ_xy=0.5, just above the 0.4m voxel) | 7 (−12) |
| LiDAR all-zero frame | 9 (−10) |
| Radar noise_induced_shifts | 16 (−3) |
| Camera gaussian_noise (σ=40) | 18 (−1) |
| Camera loss_partial (0.3) | 18 (−1) |
| Camera frame_deletion (fully dead) | 19 (+0) |

A fully dead camera costs essentially nothing. For a model marketed as tri-modal, that's
the most interesting result here — worth confirming at larger scale before treating as
general.

## Architecture constraint

Radar/LiDAR `frame_deletion` and `loss_complete` **crash the model**, not just degrade it:
zero points → zero voxels → `RuntimeError: N > 0 assert faild` in the spconv sparse-conv
backbone (`get_indice_pairs_implicit_gemm`). The pipeline's own exception handler then
dies with `UnboundLocalError`, killing the whole job. ASF's `avail_feats` mask
(`a2_fusion.py:167-172`) can't rescue this — it sits downstream of both collate and the
encoder. A dead point-cloud sensor is simply not representable at the data level in this
stack; only camera degrades gracefully (a dead camera is a well-formed black image).

## Two real bugs found and fixed in the noise-injection library

1. **`frame_deletion` silently never fired for LiDAR/camera.** `_get_modality_idx` looked
   up `meta['idx']` using the injector's own modality names, but the dataset writes
   `{'rdr','ldr64','camf',...}`. Only radar coincided. Affected runs reported 6/6
   predictions and looked healthy while being unwitting clean runs — caught only by
   per-frame sensor dumps showing `changed=False`, not by any existing test.
2. **Seeding was not reproducible across processes.** Sub-seeds were derived with Python's
   builtin `hash()` on strings, which CPython salts per-process. `seed: 42` looked fixed
   but silently produced different corruption on every run. Fixed with a blake2b-based
   stable hash; added a subprocess test that varies `PYTHONHASHSEED`.

Both were invisible to the pre-existing 120 unit tests because those tests exercise the
injector against its own conventions, inside a single process. Test suite is now 140
tests and passes both locally and in the `kradarV0.sif` container (Python 3.8 — required
adding `from __future__ import annotations` there too, since PEP 585 generics broke on
that interpreter).

## Gallery: verified, not just rendered

`build_gallery.py` overlays predicted (solid, class-colored) and ground-truth (dashed
cyan) boxes on every radar/LiDAR BEV render and, via real 3D→2D projection using the
pipeline's own `resources/cam_calib/T_params_seq` calibration, on the camera frames too.

Verification performed (not assumed):
- **Local-density test**: points inside a predicted box vs. a same-size box shifted
  laterally at the same range — 13/15 boxes show 2×–20× enclosure, confirming boxes sit
  on real clusters rather than merely being centroid-close to GT.
- **Polygon check**: shoelace area of every box equals `l×w` exactly (no self-intersecting
  corners).
- **Camera projection**: edge-gradient strength inside projected boxes is 6.2×–8.5× the
  frame average — real object edges, not empty road.
- Initially claimed camera boxes were impossible (the KITTI file's own 2D bbox column is
  a placeholder) — wrong; the real projection matrices were sitting in the repo the whole
  time, just not in the file I'd checked.

Each frame also carries a sensor-status line (`Radar: clean | LiDAR: CORRUPTED (...) |
Camera: clean`) rather than attributing any box to one sensor — ASF fuses all three
branches on every frame, so no detection is "identified by" a single sensor; the honest
statement is which sensor's *input* was corrupted for that condition.

## Caveats (original 6-frame smoke study)

6 frames, one severity per effect, one seed. Not AP — detection-count deltas only. See
`RESULTS.md` for the full write-up.

---

# Update 2026-08-14/17: sequence-46/1 pilot, then full 10-sequence sweep

## Sequence-46 pilot (2026-08-14)

Built a SEQ-generic Alvis driver (`scripts/alvis/asf_run.sbatch` + `submit_run.sh`,
generalized from a one-off `asf_seq46.sbatch`) and ran full-sequence (not 6-frame) AP-based
inference: sequence 46 (598 raw labels → 300 after class/ROI/`remove_0_obj` filtering) and
sequence 1 (597 raw → 299), original baseline + one corrupted condition
(camera `gaussian_noise`, σ=40).

**Bug found and fixed**: the sbatch script had inherited `export KRADAR_EVAL_GPU_IOU=1`
verbatim from the smoke-study template. That env var opts into a numba `@cuda.jit`
rotated-IoU kernel (`nms_gpu.py`) that SIGSEGVs on driver mismatch —
`utils/kitti_eval/eval_revised.py:13-19` documents this and defaults to a CPU fallback when
unset. The smoke template's own header claimed "CPU rotated-IoU fallback" as a fix while
setting the exact opposite. Removing the export fixed it; predictions were already
correctly written before the crash in both cases (segfault happens during the *later*
AP-eval step), so no data was lost, just the AP summary.

**New effect added**: `loss_complete_zero` (radar/LiDAR) — zero-fills the sensor array in
place at injection time, distinct from the existing `loss_complete` (sets the key to
`None`, resolved later by `NoiseInjectedDataset`'s `blackout_policy`). Camera's own
`loss_complete` was already zero-tensor based, so no camera analogue was needed. Added with
150 passing unit tests (up from 140).

**Robustness metric implemented**: Rb^c = corrupted-AP / original-AP, mRb = mean(Rb^c),
from *Benchmarking Robustness of AI-Enabled Multi-sensor Fusion Systems* §3.3
(`docs/lit_survey/noise_addition/markdown/BenchmarkingRobustness.md`). Camera
gaussian_noise (σ=40) on sequence 46: mean Rb^c = 1.025, min 0.793 (Bus/Truck 3D @IoU 0.7),
max 1.631 (Sedan BEV @IoU 0.7) — no clear degradation signal on this single condition/seed,
flagged explicitly as inconclusive rather than "robust," since most Rb^c values sit at or
above 1.0 (noise floor at this sample size, not a real finding).

**Gallery built and verified**: radar/LiDAR/camera original-vs-corrupted panels with real
prediction/GT box overlays, using the same `render_bev`/`draw_boxes`/`draw_camera_boxes`
pipeline as the original smoke gallery. Confirmed the camera sensor is genuinely
**mono, not stereo**: `front0`/`front1` are the left/right halves of a single 2560×720
stereo image (`datasets/kradar_fusion_v1_0.py:690-691`), but every `ASF_v2_0_seq*_alvis.yml`
config sets `cam: {front0: True, front1: False, ...}` — confirmed empirically by zero
`front1` files ever appearing in a `--dump-sensors` dump.

## Full sweep infrastructure (2026-08-17)

Generalized everything into a repeatable multi-sequence, multi-severity study:

- `scripts/alvis/gen_single_effect_configs.py` rewritten to emit a **low/medium/high**
  severity triple per effect (29 configs: 9 effects × 3 severities + radar/LiDAR
  `loss_complete_zero` unconditional × 2), sourced from
  `docs/vAIlt/06_Results/noise-visual-inspection-severity-levels-report.md`'s severity
  table (not the older single-value `effect_parameters.yaml`, which disagrees on several
  effects). `loss_complete` (the None-setting variant) stays excluded — a prior generator
  finding (2026-08-11 sweep) showed it's redundant with `frame_deletion(p=1.0)` for
  radar/LiDAR, both aborting identically.

  | Effect | Low | Medium | High |
  |---|---|---|---|
  | frame_deletion (all 3 modalities), p | 0.1 | 0.5 | 0.9 |
  | radar noise_induced_shifts, shift_std | 0.01 | 1.0 | 5.0 |
  | lidar gaussian_noise, sigma_xy/sigma_z | 0.01 | 0.5/0.2 | 1.0 |
  | camera gaussian_noise, sigma | 1.0 | 40.0 | 50.0 |
  | loss_partial (all 3 modalities), fraction | 0.1 | 0.3 | 0.8 |
  | loss_complete_zero (radar/lidar) | unconditional, no severity levels |

- 10 sequence configs added (`ASF_v2_0_seq{2,7,8,9,15,16,18,41,48,55}_alvis.yml`) — randomly
  selected (seed 42) from the 58 available K-Radar sequences, each capped to the first 10
  *surviving* (post-filter) frames via `max_per_seq: 10, frame_select: 'first'`.
- `submit_run.sh` extended with a `sweep` mode looping over all 29 configs, gated behind
  `--confirmed` (same as a single named condition) given the cost of discovering a broken
  baseline after burning dozens of corrupted-job GPU-hours.
- `scripts/alvis/compute_robustness.py`: first parser in the repo for
  `complete_results.txt`'s output format (previously only writers existed). Handles the
  format's asymmetric label spacing (`'bev: '` vs `'3d  :'`) via key-prefix matching, not
  literal string match. Validated against the seq46 pilot's real numbers — exact match.
- `scripts/alvis/build_sequence_full_gallery.py` / `build_random_sample_gallery.py`:
  promote the pilot's ad hoc gallery script into reusable, parameterized ones. Original
  panels are rendered once per frame and shared across every condition section (not
  re-rendered per condition) — sourced from any one corrupted condition's pre-injection
  `_clean` backup, since the `original` run itself has no `--dump-sensors` dump.

**Ran the full sweep**: 10 sequences × (1 original + 29 corrupted) = 300 SLURM jobs, all
finished — 260 OK, 40 failed (exactly `lidar`/`radar frame_deletion` at medium+high severity,
10 sequences each — the sparse-conv backbone aborting on a near/fully-empty point cloud,
consistent with the smoke study's documented crash mode; zero segfaults, zero unexpected
failures).

## Gallery-rendering lessons (worth remembering for next time)

1. **`render_bev`'s point-drawing loop is O(n) Python-level overhead** (`cv2.circle` +
   a Python colormap call per point, up to ~150k radar points/frame) — fine for a handful
   of renders, not for hundreds. Fixed by subsampling (cap 20k points) at the *call site* in
   the new gallery scripts, not by touching the shared `render_bev` itself (used by other
   galleries too).
2. **A detached SSH command isn't actually killed when the local `timeout` expires** — an
   early attempt left two duplicate gallery-render processes running concurrently on Alvis,
   racing on the same output files. Always verify a background remote process is the one
   you think it is (`ps aux` by PID) before trusting a "still running" assumption.
3. **Alvis has no CPU-only nodes** — even a non-GPU rendering job needs
   `--gpus-per-node=A40:1` to be schedulable on the `alvis` partition.
4. **Passing a multi-argument command string through `sbatch --export=...` across
   local-shell → ssh → remote-shell → sbatch is fragile** — nested quoting silently
   truncated `--out` off the end of a real command on first attempt. Fixed by writing the
   command to a small shell script and passing its *path* via `--export`, executed as
   `bash $GALLERY_SCRIPT` inside the sbatch job instead.
5. **`cv2.imwrite`/`PIL.save` default to near-lossless JPEG quality (~95)** when only the
   file extension is changed from `.png` to `.jpg` with no explicit quality parameter — a
   569.5 MB PNG gallery only shrank to 378.3 MB this way, far short of the expected 5-10×;
   an explicit lower quality (~75-80) is needed for a real size win, not yet applied.

## Terminology note

User preference, applied throughout all new writing this session: label uncorrupted
data/runs **"original"**, not "clean" — but existing on-disk identifiers already named
`clean` (e.g. `outputs/alvis_seq46/clean/`, the earlier pilot's `out_name`) are left as
literal names, described with "original" in surrounding prose rather than renamed.

## Caveats (sweep)

10 sequences, 10 frames/sequence (post-filter, not literally the first 10 raw frames), one
seed. Robustness numbers (Rb^c/mRb) are computed by `compute_robustness.py` but have not
yet been run across the full 300-job sweep as of this writeup — only the seq46 pilot's
single-condition Rb^c has been computed and reported so far.

---

# Update 2026-08-19: metrics literature audit + GT-object transition analysis

Metrics literature audit (`docs/lit_survey/metrics/metrics_audit.md`) recommends a stack
built on top of the existing `Rb^c`/`mRb` output — see [[robustness-metric-selection]] for
the full writeup (RoboBEV naming trap, convergent-reinvention note, CRI's severity-count
caveat at n=3).

Added a companion per-object diagnostic, `scripts/alvis/gt_transition_analysis.py`: churn
classification (stable / corruption_induced_miss / corruption_induced_recovery /
baseline_failure) per GT object across a clean/corrupted pair, reusing this repo's own BEV
box convention and `rotate_iou_cpu.py`. Read-only, operates on `all_predictions.parquet`.
Unit-verified, not yet run against real sweep output. Full detail in
[[gt-transition-analysis]].

---

# Update 2026-08-19/20: full 58-sequence sweep completed, quota saga, two silent-truncation bugs found and fixed

## File-count quota crisis and the pivot away from parquet

Resuming the sweep from the 10-sequence pilot, discovered the Alvis project quota
(`c3se2026-1-2`) was at **99% of its 5M file cap** (a per-project quota shared with other
users, not size-based — confirmed the filesystem itself was only 26% full by bytes).
Root cause: `test_kitti/**` writes 4× the file count it needs (once under `all/`, three
more times under redundant road/time/weather condition subdirs), and a `--dump-meta-only`
flag added earlier (writes only `meta.txt`, not full sensor arrays) didn't touch this.

Original plan was a Parquet consolidation (`predictions_to_parquet.py`); pivoted mid-session
to a simpler flat-text format instead — two merged files (`outputs/all_preds.txt`,
`outputs/all_gts.txt`), each line tagged `<sequence>_<frame>_<condition> <kitti_line>`, GT
deduplicated to one entry per `(sequence, frame)` since ground truth doesn't vary by
corruption condition. `scripts/alvis/merge_predictions_text.py` only reads `all/preds` +
`all/gts` (skips the 4× road/time/weather duplicates) and only the **lexicographically-latest
`exp_*` dir per (sequence, condition)** — needed after finding 128 pairs with two successful
`exp_*` runs (an 08-17 and an 08-18 attempt both succeeding), which were double-counting
predictions before this fix.

**Performance note**: the initial single-threaded `glob.glob()` walk over ~280K nested paths
on CephFS never finished in 45+ minutes (MDS round-trip latency, not CPU-bound). Parallelizing
the walk with a `ThreadPoolExecutor` — one thread per sequence directory, glob+read
concurrently, single writer thread only — cut this to under a minute. GIL releases during I/O
syscalls, so this is a real win despite Python's GIL; only ever one thread touches the output
file handles, so no interleaving/corruption risk.

**Reclaimed ~1.22M files** (99%→75% project quota) by deleting the 128 duplicate `exp_*` dirs
and then every `test_kitti/` subtree once its predictions were consolidated into the flat
files — `outputs/` went from 1,221,927 files to 60,220.

## Bug: merge script blindly overwrote consolidated data (near-miss, recovered)

Once source `test_kitti/` starts getting deleted after a merge, a from-scratch rerun of the
merge script can only see whatever raw data remains — for already-merged, already-deleted
sequences that's nothing, so a naive rerun silently truncates them back to 0 lines. Hit this
for real (would have dropped 274,551 lines to 164,324) before it overwrote anything, caught
by inspecting the log's line counts. Fixed the script itself: writes to `.tmp` first, refuses
to replace the real output if the new run produced fewer lines than what's already there
(`--force` to override), so the failure mode is now "refuse and leave `.tmp` for manual
inspection" instead of "silently regress." Manual merge in that case: `cat old + new.tmp`,
verify GT-tag overlap via `comm -13` (expect 0 new — corrupted-condition GT is always a
subset of `original`'s), verify zero exact-duplicate lines via `sort | uniq -d`, replace,
scp, md5-verify. Used this pattern for every subsequent batch merge (4 batches of ~10
sequences each, resubmitting the 40 sequences that turned out to have zero corrupted-condition
data — see below).

## Root cause of the original 40-sequence gap: quota exhaustion, not a code bug

The 10-sequence pilot's later full-sweep resubmission (08-18) succeeded for sequences 1-12,
then every job from sequence 13 onward failed **instantly** (2-second runtime, exit `0:53`)
starting at exactly 13:27:26 UTC — the same file-count quota wall documented above, just hit
mid-sweep. 40 sequences ended up with only their `original` baseline and zero corrupted
conditions; resubmitted all 40 in 4 batches of ~10 once quota was reclaimed, verified each
batch's `sacct` state (all failures within the expected `frame_deletion`/`loss_complete_zero`
sparse-conv-crash family) before merging.

One real cluster **node failure** encountered along the way: 4 jobs for sequence 50 (3
`radar_gaussian_noise_*` + `radar_loss_complete_zero`) all died together at exactly 10:02
runtime on node `alvis9-12` (`NODE_FAIL` state) — confirmed via `sacct -o NodeList` that all
4 shared the same node. Retried individually; node had recovered.

## Bug: seq46 and 6 other sequences had non-full historical pilot data hiding as "complete"

seq46 was the very first pilot (2026-08-14, `submit_seq46.sh`, hand-written, predates the
generalized sweep tooling) — only ever had `original` + one legacy-named `camera_gaussian_high`
condition (not `camera_gaussian_noise_high`). Never flagged as "missing" by the earlier
zero-corrupted-conditions check since it technically had *some* corrupted data. Submitted the
full 29-condition sweep for it, then removed the two legacy-named singleton lines
(`clean`, `camera_gaussian_high` — 516 lines) once the full sweep confirmed them redundant.

Six more sequences (**15, 16, 18, 41, 48, 55**) had the same class of problem in a subtler
form: their `original` baseline was full-sequence (run later, mature tooling, 08-18), but
every corrupted condition came from an **08-17 "spot-check" batch** — a small, deliberately
frame-limited manual validation run (confirmed via job log:
`Test (Total): 100%|██████████| 10/10`, i.e. the dataloader itself only exposed 10 samples for
that run) that predates the current no-cap sequence configs. These jobs `COMPLETED` cleanly
(exit `0:0`) so never surfaced as failures, and produced nonzero output so never tripped the
"zero corrupted conditions" check either — invisible to both existing verification passes.
Root-caused by comparing GT frame count against corrupted-condition frame count per sequence
(ratio ~0.04-0.09 vs. the normal 0.4-1.5 range) and reading the actual job log. Resubmitted
the full sweep for all 6; merging required stripping the *old* stale lines for these
sequences first (not just concatenating) since the old spot-check predictions and the new
full-run predictions share identical tags for their overlapping frames and are — being fully
deterministic (fixed `seed: 42`) — byte-identical, so a naive concat produced 1,980 exact
duplicate lines. Deleted the 174 now-genuinely-superseded old `exp_*` dirs afterward, but
preserved the 18 `radar_noise_induced_shifts_*` dirs among them — that effect is currently
disabled from the active sweep config (pending an SNR-dial rework) so those runs are not
actually superseded by anything newer.

**Human-in-the-loop mistake, caught and fixed**: the strip-and-replace fix above used an
overly broad `grep -vE "^(15|16|18|41|48|55)_"` that deleted **every** line for these 6
sequences from the merged file, including their legitimate `original` baseline (which the new
sweep never touches, since `sweep` mode doesn't resubmit `original`). Caught immediately via
a routine original/GT-ratio sanity check showing all 6 sequences suddenly at ratio 0.000.
`original`'s raw `test_kitti` data was already deleted from Alvis by that point (part of the
very first big quota-reclaim cleanup) — the only surviving copy was a stale local `.bak` file
(`all_preds.txt.pre_shift_removal.bak`, kept before an unrelated manual cleanup pass), from
which the 4,122 `original` lines for these 6 sequences were extracted and re-merged. Lesson:
**never keep exactly one working copy of a large derived artifact once its raw source has
been deleted** — the local `.bak` (kept for an unrelated reason) was the only thing that made
this recoverable.

## Bug: `asf_run.sbatch` cannot detect a mid-run crash — 8 jobs silently truncated

Sequence 12's 5 LiDAR conditions (`gaussian_noise_low`, `loss_complete_zero`,
`loss_partial_{high,low,medium}`) showed partial frame coverage (31-98% of the 444-frame GT)
despite `sacct` reporting clean `COMPLETED`/exit `0:0` states. Root cause, found in the raw
job log: `OSError: [Errno 122] Disk quota exceeded` mid-run (frame 136/444 for the worst
case), immediately followed by `Fatal Python error: Aborted` — the same file-count quota wall
documented above, this time crashing individual jobs mid-write rather than failing them
outright. **`asf_run.sbatch` counts however many prediction files exist after the python
process exits as success** (`ASF run OK (seq N, cond): <n> prediction files written.`) with
no check against the expected frame count, so a partial crash is indistinguishable from a
real completion at the SLURM/log level. Grepped all 2,392 job logs on Alvis for the literal
`Disk quota exceeded` string — found exactly 8 affected jobs total across the *entire* sweep,
all in sequence 12 (3 `radar_gaussian_noise_*`, already independently fixed earlier this
session; the 5 LiDAR ones above). Retried all 5; this time 4-5 minute runtimes (vs. the
original 52s-80s truncated ones) and 444/444 frames each, confirmed via job log
`prediction files written` counts. Cross-verified with an independent statistical audit
(frame-count-vs-GT ratio across every sequence×condition in the merged file, not just the
log grep) — confirmed no other silent truncation exists anywhere in the dataset outside the
well-understood, stochastic `frame_deletion`/`loss_complete_zero` crash family. **This sbatch
success-check gap should be fixed at the source** (compare written-frame-count against
expected frame-count, not just "process exited") before any future large sweep, rather than
relying on this kind of post-hoc audit again.

## Final state (2026-08-20)

All 58 sequences now have uniform, verified full-sequence corrupted-condition coverage
(except `radar_noise_induced_shifts_*`, currently disabled dataset-wide pending the SNR-dial
rework). `outputs/all_preds.txt` (711,348 lines) and `outputs/all_gts.txt` (35,456 lines,
13,727 unique sequence/frame entries) are the canonical merged dataset — md5-verified synced
between Alvis and local `repos/K-Radar/outputs/`. Raw per-frame `test_kitti/**` files have
been deleted project-wide now that this consolidation exists as the sole record.

## Visualization suite built (2026-08-20, later same day)

Full write-up: [[docs/vAIlt/06_Results/robustness-visualization-results-2026-08-20]]
(project-doc vault, not this one — see CLAUDE.md's vault split).

Built the 8-category visualization suite against `all_preds.txt` at its
now-current 748,981 lines (grew from 711,348 since the "final state" note
above — a real re-run happened between these two sessions, not yet logged
here in detail). Rebuilt `row_table_iou03.parquet`/`row_table_iou05.parquet`
and both `ap_robustness_local*.json` from scratch since the precomputed
artifacts referenced by the task brief didn't exist at their stated path.

**Key correction to the study's running headline**: pooled baseline mAP is
61.60 (IoU=0.5), not the previously-cited 55.41 — different data snapshot,
not a pipeline regression. More importantly, confirmed quantitatively what
this note's "well-understood, stochastic crash family" line already
qualitatively flagged: `radar/lidar_frame_deletion_{low,medium,high}`
predictions cover only **0.2–4.0%** of frames (2–509 of 12,788 pairs).
Naive pooled AP over that tiny surviving (easy) sample gives mAP *above*
baseline (up to 82.2) — the opposite of "catastrophic." This is a
survivorship-bias artifact of `ingest.py`'s FN-synthesis only firing for
frames present in a condition's own output; it does not mean frame_deletion
is actually benign. **Verdict: frame_deletion's true effect on mAP is
unmeasurable with the current sweep** — needs a re-run that survives
high-severity frame_deletion before this question can be closed either way.
Reliable-coverage (≥90% of baseline frames) worst performers instead:
`lidar_gaussian_noise_medium` (mAP 30.6, −50%), `lidar_gaussian_noise_high`
(33.5, −46%), `lidar_loss_complete_zero` (36.0, −42%).

**Correction, same day**: the above "reliable-coverage" framing for
gaussian_noise was itself wrong, for a different reason than frame_deletion.
Found a real bug in `ingest.py`: `_match_via_coordinates` grouped only over
`preds` *after* dummy-line filtering, so a frame where the model genuinely
detected zero objects (a real `dummy` line, correctly filtered as "not a
prediction") vanished from the matcher's iteration entirely — its GT never
got FN rows synthesized, so the frame silently dropped out of AP instead of
scoring as a full miss. This is NOT the same failure as frame_deletion's
crashed/never-run frames (verified via raw grep: `radar_frame_deletion_high`
seq28 has exactly 1 line total in `all_preds.txt`, vs. `lidar_gaussian_noise_high`
seq28 having 299/299 lines, ~99% of them real `dummy`). Fixed by tracking
dummy-only frames separately and synthesizing full-FN rows for them. Effect:
`lidar_gaussian_noise_high` mAP corrected from 33.5 (survivorship-biased,
computed from the ~2% of frames that had any real detection) to **15.7**
(IoU=0.3, full 100% coverage) — a 77% relative drop, now the dataset's
clearest and most confident finding. Standardized the whole report on
IoU=0.3 (matches official K-Radar BEV methodology) while at it, replacing
the earlier IoU=0.5 pass. New baseline: mAP=69.27. Full corrected write-up:
[[docs/vAIlt/06_Results/robustness-visualization-results-2026-08-20]].

**Second correction, same day**: initially called the plan's item 7
(zero-sensor ablation) out of scope, reasoning it needed new inference
runs. Wrong — `radar_loss_complete_zero`/`lidar_loss_complete_zero`
(`datasets/effects/noise_injection.py:374,487`) and `camera_loss_complete`
(`:621-629`) already zero-fill exactly one sensor's tensor(s) in place
while leaving the others clean — precisely the ablation mechanism item 7
asks for, already in the sweep at 100% coverage. Built it: **camera=0 →
100.7% mAP retention** (essentially no loss — camera is redundant for this
fusion model), **radar=0 → 94.2%**, **lidar=0 → 58.3%** (major loss). This
sharpens the same lidar-dominant conclusion from a second, independent
angle (direct ablation vs. noise-injection degradation curves).

**Not yet done**: `compute_robustness.py` has still only ever been run on the single seq46
pilot condition, never across the full 58-sequence merged dataset.

---

# Update 2026-08-25: checkpoint provenance — locally-trained, not the official weights

The ASF checkpoint this whole sweep runs against —
`exp_260506_135737_A2FUSION_rlc_l1d256_l2p2t32d256g_l2g_scl_mha16/models/model_10.pt`
(hardcoded `CKPT` in `repos/K-Radar/scripts/alvis/asf_run.sbatch`, `asf_smoke.sbatch`,
`asf_seq46.sbatch`) is **locally/self-trained**, not the officially published
`pretrained/ASF_v2_0_final_10.pt` (KAIST weights, downloaded via the Google Drive link in
`docs/sensor_fusion.md`). Same architecture/epoch count (both are epoch-10 checkpoints
of an `OPTIMIZER.MAX_EPOCH: 11` run, `INTERVAL_EPOCH_MODEL: 1`), confirmed different
weights — same file size, different MD5 (self-trained `805ac29a...` vs. official
`2ae9105d...`, per `asf_official_benchmark.sbatch`'s header comment).

Searched exhaustively for the training job that produced it — not found. No training
sbatch/script exists in `repos/K-Radar` or `repos/AMSCUP_PLUS` git history; no commit
message in either repo documents it; the vault and `docs/vAIlt/` have no prior mention.
`AMSCUP_PLUS/FIXES.md:118-119` treats the two checkpoints as interchangeable ("work the
same way") without explaining why the self-trained one was chosen. Conclusion: it was
trained outside both repos' tracked tooling (a manual/untracked Alvis run), and the
reasoning behind that choice is not recoverable from the codebase — tribal knowledge only.

**Practical consequence**: every AP/mAP number in this sweep (e.g. `original` mAP=69.27
above) reflects this self-trained checkpoint, not the paper's published benchmark
checkpoint. Don't compare sweep numbers directly against `docs/sensor_fusion.md`'s
official table (Sedan 79.3/Bus 60.4 AP3D@0.3) without accounting for this — the gap is
checkpoint identity, not eval methodology (both use the same `eval_revised.py` code path).
See [[robustness-metrics-tables]] for the three-way comparison (official / self-trained
sweep / `exp_260820_155158_A2FUSION` official-checkpoint rerun).

**2026-08-26 update:** re-ran the full 58-sequence baseline (`original` condition only) with the
official checkpoint, plus fixed the batch-sweep infrastructure (and found/fixed a real data-loss
bug in it along the way). Full writeup: [[official-checkpoint-rerun-2026-08-26]]. The
33-condition corruption sweep itself with the official checkpoint has not been re-run yet —
deferred by a mid-session plan change in favor of validating the clean baseline first.
