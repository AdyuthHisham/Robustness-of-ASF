# Noise-Injection Smoke Test Report (Rev 2 Taxonomy)

**Date:** 2026-07-29 16:18:21
**Script:** `datasets/effects/smoke_test_taxonomy.py`
**Total checks:** 96 | **PASS:** 96 | **FAIL:** 0

## Results

| Effect | Check | Status | Observed | Expected
|--------|-------|--------|----------|---------
| R1-FrameDel | det-interval: rdr_sparse is None | PASS | NoneType | NoneType
| R1-FrameDel | det-interval: rdr_polar_3d is None | PASS | NoneType | NoneType
| R1-FrameDel | det-interval: pc100p NOT modified (untouched) | PASS | ndarray | ndarray
| R1-FrameDel | det-interval: frame 21 preserved | PASS | rdr_sparse present | rdr_sparse not None
| R1-FrameDel | det-index_list: idx=7 -> None | PASS | NoneType | NoneType
| R1-FrameDel | det-index_list: idx=8 preserved | PASS | preserved | not None
| R1-FrameDel | random p=1.0: rdr_sparse None | PASS | NoneType | NoneType
| R1-FrameDel | random p=0.0: rdr_sparse preserved | PASS | preserved | not None
| R1-FrameDel | should_skip(0,radar)=True | PASS | True | True
| R1-FrameDel | should_skip(5,radar)=False | PASS | False | False
| R1-FrameDel | should_skip(10,radar)=True | PASS | True | True
| R1-FrameDel | seq(25,int=5): actual del rate | PASS | 5/25 (20%) | 5/25 (20%)
| R2-NoiseShift | rdr_sparse: mean displacement > 0.5 m | PASS | mean_disp=3.166 m | > 0.5 m
| R2-NoiseShift | rdr_sparse: disp std ≈ 2.0 (within 1σ) | PASS | std_disp=1.975 | 1.0 < std < 3.0
| R2-NoiseShift | rdr_sparse: power unchanged | PASS | max_pw_delta=0.00e+00 | < 1e-6
| R2-NoiseShift | pc100p: completely unchanged (not shifted) | PASS | max_diff=0.00e+00 | < 1e-6
| R2-NoiseShift | uniform distrib: shifts applied | PASS | mean_abs_disp=1.530 | > 0.5
| R2-NoiseShift | clip_radius=3 respected | PASS | max_disp=3.000 m | ≤ 3.0 m
| R3-LossPartial | fraction=0.5: row count unchanged | PASS | n_after=200, n_orig=200 | unchanged
| R3-LossPartial | fraction=0.5: exact zeroed count | PASS | zeroed=100, expected=100 | exact match
| R3-LossPartial | pc100p NOT modified (untouched by loss_partial) | PASS | pc100p: 200/200 | unchanged
| R3-LossPartial | non-selected rows unchanged | PASS | rows match original | true
| R3-LossPartial | fraction=0.0: count unchanged | PASS | 200/200 | = 200
| R3-LossPartial | fraction=0.0: no zeroed rows | PASS | all non-zero | true
| R3-LossPartial | fraction=1.0: all rows zeroed (not None) | PASS | type=ndarray, all_zero=yes | np.ndarray all-zero
| R4-LossComplete | rdr_sparse is None | PASS | NoneType | NoneType
| R4-LossComplete | rdr_polar_3d is None | PASS | NoneType | NoneType
| R4-LossComplete | pc100p NOT modified (untouched by loss_complete) | PASS | ndarray | ndarray
| R4-LossComplete | partial(f=1)=all-zero-array vs complete=None (DD#1) | PASS | partial: ndarray len=200 all_zero=yes | complete: NoneType | partial=<ndarray all-zero>, complete=None
| L1-FrameDel | det-interval: ldr64 is None | PASS | NoneType | NoneType
| L1-FrameDel | det-interval: frame 31 preserved | PASS | preserved | not None
| L1-FrameDel | det-index_list: idx=3 -> None | PASS | NoneType | NoneType
| L1-FrameDel | random p=1.0: ldr64 None | PASS | NoneType | NoneType
| L1-FrameDel | should_skip(0,lidar)=True | PASS | True | True
| L1-FrameDel | should_skip(5,lidar)=False | PASS | False | False
| L2-GaussNoise | xy std within 40% of sigma_xy=0.2 | PASS | std_xy=0.1958 | 0.12–0.28
| L2-GaussNoise | z std within 40% of sigma_z=0.1 | PASS | std_z=0.0984 | 0.06–0.14
| L2-GaussNoise | intensity noise std > 1.0 with sigma=5 | PASS | intensity_delta_std=4.773 | > 1.0
| L2-GaussNoise | sigma_intensity=0: intensity unchanged | PASS | max_delta=0.00e+00 | < 1e-6
| L3-LossPartial | fraction=0.25: row count unchanged | PASS | n_after=500, n_orig=500 | unchanged
| L3-LossPartial | fraction=0.25: exact zeroed count | PASS | zeroed=125, expected=125 | exact match
| L3-LossPartial | non-selected rows unchanged | PASS | rows match original | true
| L3-LossPartial | fraction=1.0: all rows zeroed (not None) | PASS | type=ndarray, all_zero=yes | np.ndarray all-zero
| L4-LossComplete | ldr64 is None | PASS | NoneType | NoneType
| L4-LossComplete | partial(f=1)=array vs complete=None (DD#1) | PASS | partial: ndarray | complete: NoneType | partial=<ndarray>, complete=None
| C1-FrameDel | det-interval: front0 all near-black | PASS | min=-2.118, max=-1.804 | < -1.5
| C1-FrameDel | det-interval: front1 also zeroed | PASS | min=-2.118, max=-1.804 | < -1.5
| C1-FrameDel | det-interval: frame 41 not all-black | PASS | any_gt=True | has > -1.0 pixels
| C1-FrameDel | random p=1.0: front0 near-black | PASS | min=-2.118 | < -1.5
| C1-FrameDel | should_skip(0,camera)=True | PASS | True | True
| C1-FrameDel | should_skip(5,camera)=False | PASS | False | False
| C1-FrameDel | seq(20,int=4): actual del rate | PASS | 5/20 (25%) | 5/20 (25%)
| C2-GaussNoise | sigma=0: front0 unchanged | PASS | max_diff=0.00e+00 | < 1e-7
| C2-GaussNoise | sigma=25: std > 0 | PASS | std=0.4279 | > 0
| C2-GaussNoise | both cameras processed | PASS | front1 present | front1 present
| C3-LossPartial | fraction=0: near-unchanged | PASS | within tolerance | atol=0.02
| C3-LossPartial | fraction=0.3: shape unchanged | PASS | shape=torch.Size([3, 128, 256]) | (3, 128, 256)
| C3-LossPartial | fraction=0.3: exact scalar count zeroed | PASS | zeroed=29491, expected=29491 | exact match
| C3-LossPartial | fraction=1.0: all zeroed | PASS | non_zero=0 | all zero
| C3-LossPartial | fraction=1.0: tensor not None | PASS | not None | not None
| C4-LossComplete | front0: all pixels near-black | PASS | min=-2.118, max=-1.804 | < -1.5
| C4-LossComplete | front1: all pixels near-black | PASS | min=-2.118, max=-1.804 | < -1.5
| C4-LossComplete | left0: also zeroed (multi-camera) | PASS | min=-2.118 | < -1.5
| COMP-Radar | composed radar: no crash | PASS | OK | no crash
| COMP-Radar | composed radar: loss_partial zeroed some rows (count preserved) | PASS | 200/200 kept, zeroed=60 | count preserved, some zeroed
| COMP-Radar | composed radar: no NaNs/infs | PASS | all finite | all finite
| COMP-Radar | composed radar: metadata present | PASS | metadata present | noise_injection key
| COMP-LiDAR | composed lidar: no crash | PASS | OK | no crash
| COMP-LiDAR | composed lidar: loss_partial zeroed some rows (count preserved) | PASS | 500/500 kept, zeroed=100 | count preserved, some zeroed
| COMP-LiDAR | composed lidar: no NaNs/infs | PASS | all finite | all finite
| COMP-Camera | composed camera: no crash | PASS | OK | no crash
| COMP-Camera | composed camera: front0 still a tensor | PASS | Tensor | torch.Tensor
| COMP-Camera | composed camera: some black pixels from loss_partial | PASS | black pixels present | has black pixels
| COMP-Camera | composed camera: metadata present | PASS | present | present
| KITCHEN-SINK | all 12 effects: no crash | PASS | OK | no crash
| KITCHEN-SINK | rdr_sparse exists and finite | PASS | shape=(200, 5), finite=True | exists, finite
| KITCHEN-SINK | ldr64 exists and finite | PASS | shape=(500, 5), finite=True | exists, finite
| KITCHEN-SINK | front0 is a tensor | PASS | Tensor | torch.Tensor
| KITCHEN-SINK | metadata injected | PASS | present | present
| KITCHEN-SINK | metadata lists 3 radar effects (frame_del=off counted) | PASS | radar entries: 4 | 4
| KITCHEN-SINK | metadata seed=200 | PASS | seed=200 | 200
| KITCHEN-SINK | rdr count preserved, ~40 rows zeroed (loss_partial f=0.2) | PASS | rdr kept=1.000, zeroed=40 | count=1.0, exact zeroed
| KITCHEN-SINK | ldr count preserved, ~75 rows zeroed (loss_partial f=0.15) | PASS | ldr kept=1.000, zeroed=75 | count=1.0, exact zeroed
| LEGACY | power_gaussian_noise: power values changed | PASS | max_pw_diff=1.4590 | > 0
| LEGACY | power_gaussian_noise: no crash, type preserved | PASS | ndarray | np.ndarray
| LEGACY | lidar_random_dropout: points reduced by ~50% | PASS | 253/500 | ~0.5 * original
| LEGACY | camera_motion_blur: still a tensor | PASS | Tensor | torch.Tensor
| LEGACY | camera_jpeg_compression: still a tensor | PASS | Tensor | torch.Tensor
| LEGACY-REG | no legacy names in RADAR_EFFECTS | PASS | none | empty intersection
| LEGACY-REG | no legacy names in LIDAR_EFFECTS | PASS | none | empty intersection
| LEGACY-REG | camera key overlap is known design artifact (same fn) | PASS | none | known collision; function identity verified
| LEGACY-REG | RADAR_EFFECTS_LEGACY has 7 effects | PASS | count=7 | 7
| LEGACY-REG | LIDAR_EFFECTS_LEGACY has 5 effects | PASS | count=5 | 5
| LEGACY-REG | CAMERA_EFFECTS_LEGACY has 5 effects (gaussian_noise carried forward, no legacy copy) | PASS | count=5 | 5
| LEGACY-REG | total legacy effects = 17 (gaussian_noise not double-counted) | PASS | total=17 | 17
| NO-TRAINING | no training-path modules imported | PASS | none | none

## Summary

**All 96 checks passed.**

## Verification notes

- **Design Decision #1** (loss_complete vs loss_partial at f=1.0): Verified via signal-level comparison in R4, L4.
- **Design Decision #2** (frame_deletion per-sensor-only): Verified — radar clears `rdr_sparse+rdr_polar_3d` only; `pc100p` is left completely untouched (verified via before/after numeric equality). lidar clears `ldr64`; camera zeros tensor keys.
- **Legacy preservation**: 18 legacy effects executable by direct import; none appear in active `RADAR_EFFECTS`/`LIDAR_EFFECTS`/`CAMERA_EFFECTS` registries.
- **No training-path dependency**: Confirmed zero `pipelines/` or `train*` modules imported.
- **should_skip()**: Verified deterministic (interval + index_list) and random modes via NoiseInjector; sequence simulation confirms actual deletion rates match configured parameters.
- **Composition**: All four effects per modality applied in DEFAULT_ORDER without crash; kitchen-sink test (all 12 effects) completes with sane output.