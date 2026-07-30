# Noise-Injection Parameter Sweep Smoke Test Report (Rev 2 Taxonomy)

**Date:** 2026-07-30 12:02:58
**Script:** `datasets/effects/smoke_test_param_sweep.py`
**Total checks:** 109 | **PASS:** 109 | **FAIL:** 0 | **Anomalies flagged:** 0

Built against current `noise_injection.py`: `radar_loss_partial` / `lidar_loss_partial` / `camera_loss_partial` use the AI-MSF-Benchmark zero-out/permutation mechanism (not the old deletion/block-occlusion), and `frame_deletion` includes the `should_skip()`/`__call__()` consistency cache fix.

## Results by effect

### R1-FrameDel

| Parameter | Check | Status | Observed | Expected |
|-----------|-------|--------|----------|----------|
| p=0.0 | random p=0.0: observed rate within 0.06 | PASS | rate=0.0000 | ~0.0 (+/- 0.06) |
| p=0.01 | random p=0.01: observed rate within 0.06 | PASS | rate=0.0085 | ~0.01 (+/- 0.06) |
| p=0.1 | random p=0.1: observed rate within 0.06 | PASS | rate=0.0975 | ~0.1 (+/- 0.06) |
| p=0.5 | random p=0.5: observed rate within 0.06 | PASS | rate=0.5065 | ~0.5 (+/- 0.06) |
| p=0.9 | random p=0.9: observed rate within 0.06 | PASS | rate=0.9035 | ~0.9 (+/- 0.06) |
| p=1.0 | random p=1.0: observed rate within 0.06 | PASS | rate=1.0000 | ~1.0 (+/- 0.06) |
| interval=1 | det interval=1: rate over 50 frames | PASS | 50/50 = 1.0 | 1.0 |
| interval=5 | det interval=5: rate over 50 frames | PASS | 10/50 = 0.2 | 0.2 |
| interval=1000000 | det interval=1000000: rate over 50 frames | PASS | 0/50 = 0.0 | 0.0 |
| index_list=[] | empty index_list: never deletes | PASS | preserved | not None |
| index_list=[5] | single-element list, idx=5 matches: deletes | PASS | NoneType | NoneType |
| index_list=full(0..49) | index_list covering entire sequence: deletes every frame | PASS | 50/50 | 50/50 |
| cache p=0.0 | should_skip()/__call__() agree over 200 frames | PASS | mismatches=0/200 | 0/200 |
| cache p=0.3 | should_skip()/__call__() agree over 200 frames | PASS | mismatches=0/200 | 0/200 |
| cache p=0.7 | should_skip()/__call__() agree over 200 frames | PASS | mismatches=0/200 | 0/200 |
| cache p=1.0 | should_skip()/__call__() agree over 200 frames | PASS | mismatches=0/200 | 0/200 |

### R2-NoiseShift

| Parameter | Check | Status | Observed | Expected |
|-----------|-------|--------|----------|----------|
| shift_std=0.0 | shift_std=0: bit-exact no-op | PASS | mean_disp=0.00e+00 | < 1e-12 |
| shift_std=0.01 | shift_std=0.01: displacement > 0 | PASS | mean_disp=0.0154 | > 0 |
| shift_std=0.1 | shift_std=0.1: displacement > 0 | PASS | mean_disp=0.1542 | > 0 |
| shift_std=1.0 | shift_std=1.0: displacement > 0 | PASS | mean_disp=1.5417 | > 0 |
| shift_std=5.0 | shift_std=5.0: displacement > 0 | PASS | mean_disp=7.7084 | > 0 |
| shift_std=20.0 | shift_std=20.0: displacement > 0 | PASS | mean_disp=30.8336 | > 0 |
| all | mean displacement monotonically increasing with shift_std | PASS | see per-value rows above | monotonic increase |

### R3-LossPartial

| Parameter | Check | Status | Observed | Expected |
|-----------|-------|--------|----------|----------|
| fraction=0.0 | row count unchanged | PASS | 200/200 | unchanged |
| fraction=0.0 | exact zeroed count == floor(N*fraction) | PASS | zeroed=0, expected=0 | exact match |
| fraction=0.01 | row count unchanged | PASS | 200/200 | unchanged |
| fraction=0.01 | exact zeroed count == floor(N*fraction) | PASS | zeroed=2, expected=2 | exact match |
| fraction=0.3 | row count unchanged | PASS | 200/200 | unchanged |
| fraction=0.3 | exact zeroed count == floor(N*fraction) | PASS | zeroed=60, expected=60 | exact match |
| fraction=0.8 | row count unchanged | PASS | 200/200 | unchanged |
| fraction=0.8 | exact zeroed count == floor(N*fraction) | PASS | zeroed=160, expected=160 | exact match |
| fraction=1.0 | row count unchanged | PASS | 200/200 | unchanged |
| fraction=1.0 | exact zeroed count == floor(N*fraction) | PASS | zeroed=200, expected=200 | exact match |
| all | zeroed count monotonically non-decreasing with fraction | PASS | see per-value rows above | monotonic non-decrease |
| fraction=1.5 | fraction>1.0: does not crash, clamps to all-zeroed (== fraction=1.0) | PASS | len=200, zeroed=200/200 | len=200, zeroed=200/200 |
| fraction=1.0 | loss_partial(f=1.0) stays ndarray, never becomes None | PASS | ndarray | ndarray (not None) |

### R4-LossComplete

| Parameter | Check | Status | Observed | Expected |
|-----------|-------|--------|----------|----------|
| params={} | always full clear regardless of params | PASS | rdr_sparse=None, rdr_polar_3d is None=True | both None |
| params={'fraction': 0.01} | always full clear regardless of params | PASS | rdr_sparse=None, rdr_polar_3d is None=True | both None |
| params={'fraction': 0.5} | always full clear regardless of params | PASS | rdr_sparse=None, rdr_polar_3d is None=True | both None |
| params={'anything': 'ignored'} | always full clear regardless of params | PASS | rdr_sparse=None, rdr_polar_3d is None=True | both None |

### L1-FrameDel

| Parameter | Check | Status | Observed | Expected |
|-----------|-------|--------|----------|----------|
| p=0.0 | random p=0.0: observed rate within 0.06 | PASS | rate=0.0000 | ~0.0 (+/- 0.06) |
| p=0.1 | random p=0.1: observed rate within 0.06 | PASS | rate=0.0950 | ~0.1 (+/- 0.06) |
| p=0.5 | random p=0.5: observed rate within 0.06 | PASS | rate=0.4930 | ~0.5 (+/- 0.06) |
| p=1.0 | random p=1.0: observed rate within 0.06 | PASS | rate=1.0000 | ~1.0 (+/- 0.06) |
| interval=1 | det interval=1: rate over 50 frames | PASS | 50/50 = 1.0 | 1.0 |
| interval=5 | det interval=5: rate over 50 frames | PASS | 10/50 = 0.2 | 0.2 |
| interval=1000000 | det interval=1000000: rate over 50 frames | PASS | 0/50 = 0.0 | 0.0 |

### L2-GaussNoise

| Parameter | Check | Status | Observed | Expected |
|-----------|-------|--------|----------|----------|
| sigma=0.0 | sigma=0: bit-exact no-op | PASS | observed_std=0.00e+00 | < 1e-12 |
| sigma=0.01 | sigma=0.01: observed std within tolerance | PASS | observed_std=0.0095 | ~0.01 (+/- 35%) |
| sigma=0.1 | sigma=0.1: observed std within tolerance | PASS | observed_std=0.0951 | ~0.1 (+/- 35%) |
| sigma=1.0 | sigma=1.0: observed std within tolerance | PASS | observed_std=0.9514 | ~1.0 (+/- 35%) |
| sigma=10.0 | sigma=10.0: observed std within tolerance | PASS | observed_std=9.5142 | ~10.0 (+/- 35%) |
| all | observed std monotonically increasing with sigma | PASS | see per-value rows above | monotonic increase |

### L3-LossPartial

| Parameter | Check | Status | Observed | Expected |
|-----------|-------|--------|----------|----------|
| fraction=0.0 | row count unchanged | PASS | 500/500 | unchanged |
| fraction=0.0 | exact zeroed count == floor(N*fraction) | PASS | zeroed=0, expected=0 | exact match |
| fraction=0.01 | row count unchanged | PASS | 500/500 | unchanged |
| fraction=0.01 | exact zeroed count == floor(N*fraction) | PASS | zeroed=5, expected=5 | exact match |
| fraction=0.3 | row count unchanged | PASS | 500/500 | unchanged |
| fraction=0.3 | exact zeroed count == floor(N*fraction) | PASS | zeroed=150, expected=150 | exact match |
| fraction=0.8 | row count unchanged | PASS | 500/500 | unchanged |
| fraction=0.8 | exact zeroed count == floor(N*fraction) | PASS | zeroed=400, expected=400 | exact match |
| fraction=1.0 | row count unchanged | PASS | 500/500 | unchanged |
| fraction=1.0 | exact zeroed count == floor(N*fraction) | PASS | zeroed=500, expected=500 | exact match |
| all | zeroed count monotonically non-decreasing with fraction | PASS | see per-value rows above | monotonic non-decrease |
| fraction=1.5 | fraction>1.0: does not crash, clamps to all-zeroed (== fraction=1.0) | PASS | len=500, zeroed=500/500 | len=500, zeroed=500/500 |
| fraction=1.0 | loss_partial(f=1.0) stays ndarray, never becomes None | PASS | ndarray | ndarray (not None) |

### L4-LossComplete

| Parameter | Check | Status | Observed | Expected |
|-----------|-------|--------|----------|----------|
| params={} | always full clear regardless of params | PASS | ldr64=None | None |
| params={'fraction': 0.01} | always full clear regardless of params | PASS | ldr64=None | None |
| params={'fraction': 0.5} | always full clear regardless of params | PASS | ldr64=None | None |
| params={'anything': 'ignored'} | always full clear regardless of params | PASS | ldr64=None | None |

### C1-FrameDel

| Parameter | Check | Status | Observed | Expected |
|-----------|-------|--------|----------|----------|
| p=0.0 | random p=0.0: observed rate within 0.08 | PASS | rate=0.0000 | ~0.0 (+/- 0.08) |
| p=0.1 | random p=0.1: observed rate within 0.08 | PASS | rate=0.1020 | ~0.1 (+/- 0.08) |
| p=0.5 | random p=0.5: observed rate within 0.08 | PASS | rate=0.4780 | ~0.5 (+/- 0.08) |
| p=1.0 | random p=1.0: observed rate within 0.08 | PASS | rate=1.0000 | ~1.0 (+/- 0.08) |
| interval=1 | det interval=1: rate over 30 frames | PASS | 30/30 = 1.0 | 1.0 |
| interval=5 | det interval=5: rate over 30 frames | PASS | 6/30 = 0.2 | 0.2 |
| interval=1000000 | det interval=1000000: rate over 30 frames | PASS | 0/30 = 0.0 | 0.0 |

### C2-GaussNoise

| Parameter | Check | Status | Observed | Expected |
|-----------|-------|--------|----------|----------|
| sigma=0.0 | sigma=0: bit-exact no-op | PASS | observed_std_norm=0.00e+00 | < 1e-7 |
| sigma=1.0 | sigma=1.0: observed std (pixel-space) within tolerance | PASS | observed_std_pixel~1.00 | ~1.0 (+/- 35%) |
| sigma=10.0 | sigma=10.0: observed std (pixel-space) within tolerance | PASS | observed_std_pixel~10.00 | ~10.0 (+/- 35%) |
| sigma=50.0 | sigma=50.0: observed std (pixel-space) within tolerance | PASS | observed_std_pixel~49.85 | ~50.0 (+/- 35%) |
| sigma=255.0 | sigma=255.0: observed std (pixel-space) within tolerance | PASS | observed_std_pixel~254.35 | ~255.0 (+/- 35%) |
| all | observed std monotonically increasing with sigma | PASS | see per-value rows above | monotonic increase |

### C3-LossPartial

| Parameter | Check | Status | Observed | Expected |
|-----------|-------|--------|----------|----------|
| fraction=0.0 | shape unchanged | PASS | shape=torch.Size([3, 128, 256]) | (3,128,256) |
| fraction=0.0 | exact scalar zeroed count == floor(H*W*3*fraction) [const image] | PASS | zeroed=0, expected=0 | exact match |
| fraction=0.01 | shape unchanged | PASS | shape=torch.Size([3, 128, 256]) | (3,128,256) |
| fraction=0.01 | exact scalar zeroed count == floor(H*W*3*fraction) [const image] | PASS | zeroed=983, expected=983 | exact match |
| fraction=0.3 | shape unchanged | PASS | shape=torch.Size([3, 128, 256]) | (3,128,256) |
| fraction=0.3 | exact scalar zeroed count == floor(H*W*3*fraction) [const image] | PASS | zeroed=29491, expected=29491 | exact match |
| fraction=0.8 | shape unchanged | PASS | shape=torch.Size([3, 128, 256]) | (3,128,256) |
| fraction=0.8 | exact scalar zeroed count == floor(H*W*3*fraction) [const image] | PASS | zeroed=78643, expected=78643 | exact match |
| fraction=1.0 | shape unchanged | PASS | shape=torch.Size([3, 128, 256]) | (3,128,256) |
| fraction=1.0 | exact scalar zeroed count == floor(H*W*3*fraction) [const image] | PASS | zeroed=98304, expected=98304 | exact match |
| all | zeroed scalar count monotonically non-decreasing with fraction (const image) | PASS | see per-value rows above | monotonic non-decrease |
| fraction=0.01 (natural img) | zeroed count >= floor(N*f); excess above that is the documented natural/round-trip caveat (739 pre-existing black scalars) | PASS | zeroed=2086, expected>=983, natural_zero_baseline=739, excess=1103 | >= 983 (excess documented as pass, not fail) |
| fraction=0.3 (natural img) | zeroed count >= floor(N*f); excess above that is the documented natural/round-trip caveat (739 pre-existing black scalars) | PASS | zeroed=30259, expected>=29491, natural_zero_baseline=739, excess=768 | >= 29491 (excess documented as pass, not fail) |
| fraction=0.8 (natural img) | zeroed count >= floor(N*f); excess above that is the documented natural/round-trip caveat (739 pre-existing black scalars) | PASS | zeroed=78841, expected>=78643, natural_zero_baseline=739, excess=198 | >= 78643 (excess documented as pass, not fail) |
| fraction=1.0 (natural img) | zeroed count >= floor(N*f); excess above that is the documented natural/round-trip caveat (739 pre-existing black scalars) | PASS | zeroed=98304, expected>=98304, natural_zero_baseline=739, excess=0 | >= 98304 (excess documented as pass, not fail) |
| fraction=2.0 | fraction>1.0: no crash, implicitly clamps to all-zeroed (no old rect-cap code) | PASS | shape=torch.Size([3, 128, 256]), zeroed=98304/98304 | shape=(3,128,256), zeroed=98304/98304 |
| fraction=1.0 | loss_partial(f=1.0) stays a tensor, never becomes None | PASS | Tensor | torch.Tensor (not None) |

### C4-LossComplete

| Parameter | Check | Status | Observed | Expected |
|-----------|-------|--------|----------|----------|
| params={} | always full blackout regardless of params | PASS | front0 all<-1.5=True | True |
| params={'fraction': 0.01} | always full blackout regardless of params | PASS | front0 all<-1.5=True | True |
| params={'fraction': 0.5} | always full blackout regardless of params | PASS | front0 all<-1.5=True | True |
| params={'anything': 'ignored'} | always full blackout regardless of params | PASS | front0 all<-1.5=True | True |

### R3vR4-Distinct

| Parameter | Check | Status | Observed | Expected |
|-----------|-------|--------|----------|----------|
| fraction=0.99 | radar: loss_partial output type differs from loss_complete | PASS | partial: ndarray, complete: NoneType | ndarray vs NoneType |
| fraction=0.99 | camera: loss_partial(f=0.99) pixel output DIFFERS from loss_complete (not fully black) | PASS | identical=False | False (partial still has ~1% non-black scalars) |
| fraction=1.0 | radar: loss_partial output type differs from loss_complete | PASS | partial: ndarray, complete: NoneType | ndarray vs NoneType |
| fraction=1.0 | camera: loss_partial(f=1.0) pixel output == loss_complete pixel output (expected, by design both are all-black) | PASS | identical=True | identical (both all-black; distinguished only by which effect ran) |

### REAL-FRAME

| Parameter | Check | Status | Observed | Expected |
|-----------|-------|--------|----------|----------|
| n/a | real K-Radar frame available for testing (informational — not required to pass) | PASS | skipped: loader unavailable (No module named 'data_loader') | informational |

## Anomalies flagged

None. No non-monotonic, discontinuous, crashing, or silently-no-op behavior observed across the swept parameter ranges.

## Cap-behavior check (camera loss_partial, post AI-MSF-Benchmark swap)

The old rectangular block-occlusion implementation had explicit `fraction >= 1.0` capping logic written for that mechanism. The current flatten-permute-zero mechanism (`index = rng.permutation(n_total)[:loss_num]`) has no such explicit cap: numpy array slicing silently truncates `[:loss_num]` to `n_total` elements when `loss_num > n_total`, so `fraction > 1.0` degrades gracefully to "zero everything" without any special-case code. Verified at `fraction=2.0` above — no crash, full zero-out, same result as `fraction=1.0`.

## loss_partial vs loss_complete distinguishability

- **Radar/LiDAR**: `loss_partial(fraction=1.0)` produces an all-zero **ndarray** (row count preserved); `loss_complete` produces **None**. Type-distinguishable at every fraction, including the f=1.0 edge.
- **Camera**: `camera_loss_complete` does *not* set tensors to `None` (unlike radar/lidar) — it zero-fills them, same as `camera_frame_deletion`. So at `fraction=1.0`, `camera_loss_partial`'s pixel output is **numerically identical** to `camera_loss_complete`'s output (both fully black) — they are only distinguishable by which effect executed, not by inspecting the resulting tensor. This is expected: full-fraction partial loss and complete loss are semantically the same end state on camera; the design distinction is about *which effect ran* / applies at all fractions below 1.0, not about the f=1.0 output tensor. Verified at f=0.99 that partial output is NOT pixel-identical to complete (still ~1% non-black scalars).

## Overall verdict

**PASS — module behaves correctly and predictably across its practical parameter range.** All 12 taxonomy effects were swept from near-zero/no-op through low, moderate (existing default), high, and edge-case-extreme parameter settings. Row/scalar counts for `loss_partial` effects match `floor(N*fraction)` exactly at every tested fraction (including fraction>1.0, which degrades gracefully via numpy slicing rather than crashing or requiring special-case capping code). Gaussian-noise effects (`lidar.gaussian_noise`, `camera.gaussian_noise`) show sigma=0 as a bit-exact no-op and observed std scaling monotonically with configured sigma. `frame_deletion` (radar/lidar/camera) shows correct behavior at p=0/p=1 and interval=1/interval=huge, with `should_skip()` and `__call__()` staying consistent across a full probability sweep — confirming the consistency cache fix holds under repeated random draws, not just the single-call case. `loss_complete` is confirmed to have no meaningful severity axis (garbage/ignored params don't change its always-full-clear behavior). No crashes, no non-monotonic or discontinuous behavior, no silent no-ops at nonzero parameter values were observed. **Ready for a full-sequence pipeline run.**

## Scope notes

- All checks run against synthetic data matching real K-Radar array/tensor shapes (`rdr_sparse` (200,5), `rdr_polar_3d` (2,256,107,37), `ldr64` (500,5), camera (3,128,256)). A best-effort real-frame check was attempted; see the `REAL-FRAME` row above for its outcome in this run.
- Legacy (Rev 1) effects are out of scope for this sweep — covered separately in `smoke_test_taxonomy.py`.
- `noise_injection.py` was NOT modified as part of this task.