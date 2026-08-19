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
