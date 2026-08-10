# Where to inject radar corruption: post-threshold `.npy` vs pre-threshold `.mat` cube

**Investigation date:** 2026-07-30
**Scope:** Investigation only. No code changed in `repos/K-Radar`, `repos/AMSCUP_PLUS`, or `test-bed/src/Modules/robust_testing/kradar`.

Builds on `docs/vAIlt/rdr_sparse-vs-pc100p-explainer.md`, which already established that `rdr_sparse` (the model's actual radar input) is a pre-thresholded `.npy` derivative, and that the current noise-injection module operates on it post-hoc. This report determines exactly which raw `.mat` directory it's derived from, whether re-deriving it per-frame is feasible, and where corruption should be injected.

---

## 1. Raw file inspection

Loaded with `scipy.io.loadmat` (scipy 1.17.1, available in the `kradar_visibility` uv env at `test-bed/src/Modules/robust_testing/kradar`; no scipy install needed).

### `radar_tesseract/tesseract_00033.mat` (293 MB on disk)

- Dict key: `arrDREA` (Doppler-Range-Elevation-Azimuth)
- Shape: `(64, 256, 37, 107)`, dtype `float64`
- Value range: min `818.16`, max `1.395e18`, mean `3.645e12`
- Physical quantity: raw 4D tesseract power/ADC values across (64 Doppler bins x 256 range bins x 37 elevation bins x 107 azimuth bins) -- **not yet projected to cartesian space**.
- `loadmat()` wall-clock: **31.4 s** for a single file (single measurement).

### `radar_zyx_cube/cube_00033.mat` (58 MB on disk)

- Dict key: `arr_zyx`
- Shape: `(150, 400, 250)`, dtype `float64` -- corresponds to z (150 bins x 0.4 m = 60 m span, -30 to 30), y (400 bins x 0.4 m = 160 m span, -80 to 80), x (250 bins x 0.4 m = 100 m span, 0 to 100), matching the `arr_z_cb`/`arr_y_cb`/`arr_x_cb` grids hardcoded in `generate_sparse_rdr_cube_for_wider_rtnh` (`kradar_detection_v1_1.py:1061-1063`).
- Value range: min `-1.0`, max `2.973e14`, mean `5.636e10`
- Physical quantity: power already projected onto a cartesian z-y-x voxel grid -- this is the "zyx cube," a cartesian-projected but still dense/unthresholded representation, one processing step downstream of the raw tesseract.
- `loadmat()` wall-clock, repeated 3x: **4.99 s, 4.63 s, 4.74 s** -- consistent across repeats regardless of OS page-cache warmth, indicating the cost is dominated by scipy's MAT-file parsing/decompression (CPU-bound), not raw disk I/O.

---

## 2. Exact derivation chain

Read the full `generate_sparse_rdr_cube_for_wider_rtnh()` (`datasets/kradar_detection_v1_1.py:1045-1134`), not just the excerpt in the prior explainer.

**`path_cube` construction** -- traced back through `dict_item['meta']['path']`, populated by `get_path_data_from_path_label()`:

```python
# kradar_detection_v1_1.py:851-852
path_radar_tesseract = '/'+os.path.join(*path_header, 'radar_tesseract', 'tesseract_'+radar_idx+'.mat')
path_radar_cube      = '/'+os.path.join(*path_header, 'radar_zyx_cube', 'cube_'+radar_idx+'.mat')
...
# kradar_detection_v1_1.py:871-874
dict_path = {
    'rdr_sparse_cube'   : path_radar_sparse_cube,
    'rdr_tesseract'     : path_radar_tesseract,
    'rdr_cube'          : path_radar_cube,      # <- this is the key generate_sparse_rdr_cube_for_wider_rtnh reads
    ...
}
```

```python
# kradar_detection_v1_1.py:1084-1087
dict_path = dict_item['meta']['path']
path_cube = dict_path['rdr_cube']               # <- resolves to radar_zyx_cube/cube_*.mat
arr_cube = np.flip(loadmat(path_cube)['arr_zyx'], axis=0) # z-axis is flipped
```

**Definitive answer: `rdr_sparse` is derived from `radar_zyx_cube/`, not `radar_tesseract/`.** The tesseract (raw range-doppler-angle cube, `arrDREA`) is loaded elsewhere in the codebase (`rdr_tesseract` key, used by `get_cube_doppler` and doppler-related tooling) but never touched by `generate_sparse_rdr_cube_for_wider_rtnh`. The prior explainer's phrase "raw 4D tesseract" for the source of `rdr_sparse` is imprecise -- it's actually one step downstream: the tesseract has already been range-doppler-angle -> cartesian projected into `radar_zyx_cube` by an earlier (undocumented-here, likely MATLAB/vendor) processing stage before this Python function ever runs. So there are effectively three tiers: raw tesseract -> zyx cube (dense cartesian) -> sparse point cloud (thresholded cartesian).

**`noise_injection.py` confirmation** (`repos/K-Radar/datasets/effects/noise_injection.py`): grepped for `.mat`, `loadmat`, and `generate_sparse_rdr_cube_for_wider_rtnh` -- zero hits. The module's only imports are `cv2`, `numpy`, `torch`, and its own `EffectConfig`. All effect handlers operate on `dict_item["rdr_sparse"]` and `dict_item["pc100p"]` (lines 117, 143, 194, 215, 654-759 region) -- in-memory numpy arrays already loaded from `.npy`/precomputed sources by the time any effect runs. **Confirmed: it never touches `.mat` files and never calls the raw-cube generation function.**

It's also worth noting `noise_injection.py` is not currently wired into the training dataset loader (`kradar_fusion_v1_0_calib_change.py` has zero references to it) -- it's consumed only by `scripts/smoke_test_integration.py`, `test_noise_injection.py`, and `visualize_effects.py`, i.e. it's a standalone robustness-testing harness applied to an already-loaded `dict_item`, not baked into `__getitem__` for training.

---

## 3. One-time vs re-runnable

`generate_sparse_rdr_cube_for_wider_rtnh()` is unambiguously a **one-time offline batch script**, not something designed for per-frame invocation at eval/train time:

```python
# kradar_detection_v1_1.py:1048-1055
dir_save_folder = osp.join(cfg_sparse_data.SAVE_FOLDER, name_sparse_cfar)
os.makedirs(dir_save_folder, exist_ok=True)
for idx in range(58):
    os.makedirs(osp.join(dir_save_folder, f'{idx+1}'), exist_ok=True)   # pre-creates all 58 sequence dirs
len_total_data = self.__len__()
```

```python
# kradar_detection_v1_1.py:1068
for idx in tqdm(range(len_total_data)):   # tqdm progress bar over the ENTIRE split
```

```python
# kradar_detection_v1_1.py:1137-1156  (__main__ block)
if __name__ == '__main__':
    ...
    dataset = KRadarDetection_v1_1(cfg=cfg, split='test')
    dataset.generate_sparse_rdr_cube_for_wider_rtnh(vis_for_check=False, vis_in_sampled_sphere=False)
```

No CLI args for a single sequence/frame subset, no early-exit if the output file already exists (would just overwrite), no multiprocessing pool inside the function itself (single-threaded `for` loop) -- but it's clearly meant to be launched once per split (train/test) as an offline preprocessing job producing the `sprdr_*.npy` corpus that the fusion dataset loader (`get_rdr_sparse()`) then reads at training/eval time. There is no code path anywhere that calls this function inside `__getitem__` or any per-batch/per-epoch loading logic.

---

## 4. Real timing

Replicated the function's core logic verbatim (load -> normalize -> quantile threshold -> grid-index-to-cartesian conversion) as a scratch script in `/tmp/radar_investigation`, using the real file `radar_zyx_cube/cube_00033.mat` and the exact constants from the source (`grid_size=0.4`, `norm_val=1e13`, `quantile_rate=0.9` i.e. top `QUANTILE_RATE=0.1`). This is a reimplementation of the logic, not a direct call to `generate_sparse_rdr_cube_for_wider_rtnh()` itself -- the original method requires a fully constructed `KRadarDetection_v1_1` dataset object (config, label parsing, calib loading) which is out of scope to instantiate for a timing probe; the isolated numeric core is what actually costs time (I/O + threshold), so this reproduces the real cost profile.

Measured breakdown, single frame:

| Stage | Time (s) |
|---|---|
| `loadmat()` I/O + parse | 4.553 |
| normalize (`/= 1e13`) | 0.131 |
| `np.quantile` + `np.where` (top 10%) | 0.848 |
| grid-index -> cartesian + `np.stack` | 0.166 |
| **Total** | **5.698** |

Output: `(1,500,000, 4)` array -- top 10% of `150x400x250 = 15,000,000` voxels = exactly 1.5M rows. **Note:** this contradicts the earlier explainer's claim that `rdr_sparse` is "~1000-10,000" points. That smaller figure is the count *after* the fusion loader's ROI filter (`filter_roi`, `kradar_fusion_v1_0_calib_change.py:1125-1138`) crops to the detection region -- the raw output of `generate_sparse_rdr_cube_for_wider_rtnh()` itself is 1.5M points per frame, two orders of magnitude larger than what ends up feeding the model. Worth flagging as a correction to the prior doc if it matters downstream.

**Extrapolation to a 30-50 frame sequence** (sequential, single process): 30 x 5.70 s ~= **171 s (2.85 min)**; 50 x 5.70 s ~= **285 s (4.75 min)**.

I/O vs compute: `loadmat()` is **80%** of per-frame cost (4.55 / 5.70 s) and is CPU-bound MAT-file parsing, not raw disk read (confirmed by repeated loads showing no speedup from OS page cache). This means it is **process-parallelizable near-linearly with core count** -- an 8-worker multiprocessing pool (the same pattern the original codebase already uses elsewhere, e.g. `tqdm` loops over datasets) could process 50 frames in roughly 50/8 x 5.70 s ~= **36 s**. This matches the one-time-batch design already established in Task 3: the existing pipeline is built to amortize this cost once, not per-epoch.

---

## 5. Corruption injection point: tradeoff and recommendation

**Corrupting `rdr_sparse` (current, post-threshold `.npy`):**
- Pro: instant, in-memory, per-`__getitem__` cost is negligible (microseconds on arrays of a few thousand rows post-ROI-filter).
- Con: cannot simulate threshold-boundary effects -- e.g. "corruption drops a voxel's power below the quantile cutoff so it never survives thresholding" is structurally impossible to model once you only see the post-threshold survivors. Any corruption that should plausibly change *which* voxels clear the top-10% bar (attenuation, added noise floor, jamming) can only be approximated by ad-hoc row-dropping heuristics on the already-selected point set, not derived from the actual power field.

**Corrupting the raw `.mat` cube pre-threshold (new path):**
- Pro: physically correct -- corruption is applied to the dense power field before quantile selection, so threshold-boundary effects (a corrupted voxel falling out of/into the top 10%) are captured naturally, and doppler-cube analogues can share the same approach.
- Con: **5.70 s/frame single-process** measured cost, dominated by `loadmat()` parsing of a 58 MB file, not something a training-time `__getitem__` can absorb per-sample per-epoch. This is strictly an offline/batch regeneration cost, matching the granularity of the existing `generate_sparse_rdr_cube_for_wider_rtnh` design (one-time pass writing a new `.npy` corpus), not a live corruption hook.

**Recommendation: (c) -- support both via a config flag for corruption stage, but implement the pre-threshold path as an offline batch regeneration step (mirroring the existing `generate_sparse_rdr_cube_for_wider_rtnh` script/`__main__` pattern), never as a per-`__getitem__` live call.**

Rationale directly from the timing data: 5.70 s/frame single-process (171-285 s for 30-50 frames) is two to three orders of magnitude too slow for live corruption inside a training/eval loop that needs sub-millisecond per-sample cost, but entirely reasonable as a one-time (or per-corruption-config) offline pass -- especially parallelized, where 50 frames drops to ~36 s across 8 workers. Given the raw cube is CPU-bound (not I/O-bound) to load, this parallelizes cleanly using the same multiprocessing pattern the codebase already applies elsewhere for batch preprocessing. Keeping `rdr_sparse`-level corruption (option a) as the sole path forecloses an entire class of physically realistic corruptions (threshold-boundary effects); building only the raw-cube path (option b) with no fallback would remove the current fast, cheap post-threshold corruptions that don't need physical threshold fidelity (e.g. dropout, coordinate jitter) and force every corruption experiment through a multi-minute-per-sequence regeneration step even when unnecessary. A config flag choosing corruption stage per-effect gets the cheap effects staying fast and the physically-sensitive effects (anything touching the power field near the quantile boundary) routed through an offline regeneration pass.

---

**This is a recommendation only. No code was changed in this investigation. Adyuth must decide before any implementation proceeds.**

---

## 6. Decision (2026-07-30)

**Decision: keep radar corruption injection on `rdr_sparse` only.** The offline batch raw-cube (`radar_zyx_cube`) regeneration path described in Section 5 is **deferred, not rejected**.

Rationale: the measured cost of the pre-threshold path is **5.70 s/frame single-process** (Section 4), two to three orders of magnitude too slow for live per-frame use in a training/eval loop that needs sub-millisecond per-sample cost. `rdr_sparse`-only corruption stays in-memory, post-threshold, and effectively free per `__getitem__` (microseconds), matching how `noise_injection.py` already operates today (Section 2).

This forecloses threshold-boundary corruption effects (Section 5's Con for option a) as a known, accepted limitation — not an oversight. If physically-realistic threshold-boundary corruption (a corrupted voxel falling out of/into the top-10% quantile cut) becomes necessary later, the raw-cube offline path is already scoped: single-threaded cost, parallelization strategy (~36 s for 50 frames across 8 workers), and integration point (mirroring `generate_sparse_rdr_cube_for_wider_rtnh`'s existing offline-batch pattern) are all specified in Section 5 above. This report is the spec to pick back up if that work is ever prioritized — no new investigation should be needed to start it.

No code was changed as part of making this decision.
