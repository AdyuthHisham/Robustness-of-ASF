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

## Caveats

6 frames, one severity per effect, one seed. Not AP — detection-count deltas only. See
`RESULTS.md` for the full write-up.
