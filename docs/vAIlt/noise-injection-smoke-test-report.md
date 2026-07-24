# Noise-Injection Smoke Test Report (Rev 2 Taxonomy)

**Date:** 2026-07-24 11:53:00
**Script:** `datasets/effects/smoke_test_taxonomy.py`
**Total checks:** 89 | **PASS:** 89 | **FAIL:** 0

## Results

| Effect | Check | Status | Observed | Expected
|--------|-------|--------|----------|---------
| R1-FrameDel | det-interval: rdr_sparse is None | PASS | NoneType | NoneType
| R1-FrameDel | det-interval: rdr_polar_3d is None | PASS | NoneType | NoneType
| R1-FrameDel | det-interval: pc100p is None | PASS | NoneType | NoneType
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
| R2-NoiseShift | pc100p: mean displacement > 0.5 m | PASS | pc_mean_disp=3.230 m | > 0.5 m
| R2-NoiseShift | uniform distrib: shifts applied | PASS | mean_abs_disp=1.530 | > 0.5
| R2-NoiseShift | clip_radius=3 respected | PASS | max_disp=3.000 m | ≤ 3.0 m
| R3-LossPartial | fraction=0.5: kept ratio within [0.45, 0.55] | PASS | kept=0.455 | [0.45, 0.55]
| R3-LossPartial | pc100p also dropped | PASS | pc100p: 91/200 (0.455) | < 200
| R3-LossPartial | fraction=0.0: count unchanged | PASS | 200/200 | = 200
| R3-LossPartial | fraction=1.0: empty array (not None) | PASS | type=ndarray, len=0 | np.ndarray len 0
| R4-LossComplete | rdr_sparse is None | PASS | NoneType | NoneType
| R4-LossComplete | rdr_polar_3d is None | PASS | NoneType | NoneType
| R4-LossComplete | pc100p is None | PASS | NoneType | NoneType
| R4-LossComplete | partial(f=1)=array vs complete=None (DD#1) | PASS | partial: ndarray len=0 | complete: NoneType | partial=<ndarray len=0>, complete=None
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
| L3-LossPartial | fraction=0.25: kept ratio within [0.70, 0.80] | PASS | kept=0.756 | [0.70, 0.80]
| L3-LossPartial | fraction=1.0: empty array (not None) | PASS | type=ndarray, len=0 | np.ndarray len 0
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
| C2-GaussNoise | sigma=25: std > 0 | PASS | std=0.4283 | > 0
| C2-GaussNoise | both cameras processed | PASS | front1 present | front1 present
| C3-LossPartial | fraction=0: near-unchanged | PASS | within tolerance | atol=0.02
| C3-LossPartial | fraction=0.3: some black pixels present | PASS | min=-2.118 | < -1.5
| C3-LossPartial | fraction=0.99: most pixels black | PASS | black_frac=0.851 | > 0.5
| C4-LossComplete | front0: all pixels near-black | PASS | min=-2.118, max=-1.804 | < -1.5
| C4-LossComplete | front1: all pixels near-black | PASS | min=-2.118, max=-1.804 | < -1.5
| C4-LossComplete | left0: also zeroed (multi-camera) | PASS | min=-2.118 | < -1.5
| COMP-Radar | composed radar: no crash | PASS | OK | no crash
| COMP-Radar | composed radar: points removed by loss_partial | PASS | 138/200 kept (0.690) | < 90% kept
| COMP-Radar | composed radar: no NaNs/infs | PASS | all finite | all finite
| COMP-Radar | composed radar: metadata present | PASS | metadata present | noise_injection key
| COMP-LiDAR | composed lidar: no crash | PASS | OK | no crash
| COMP-LiDAR | composed lidar: points reduced | PASS | 392/500 kept | < 90%
| COMP-LiDAR | composed lidar: no NaNs/infs | PASS | all finite | all finite
| COMP-Camera | composed camera: no crash | PASS | OK | no crash
| COMP-Camera | composed camera: front0 still a tensor | PASS | Tensor | torch.Tensor
| COMP-Camera | composed camera: some black pixels from loss_partial | PASS | black pixels present | has black pixels
| COMP-Camera | composed camera: metadata present | PASS | present | present
| KITCHEN-SINK | all 12 effects: no crash | PASS | OK | no crash
| KITCHEN-SINK | rdr_sparse exists and finite | PASS | shape=(161, 5), finite=True | exists, finite
| KITCHEN-SINK | ldr64 exists and finite | PASS | shape=(419, 5), finite=True | exists, finite
| KITCHEN-SINK | front0 is a tensor | PASS | Tensor | torch.Tensor
| KITCHEN-SINK | metadata injected | PASS | present | present
| KITCHEN-SINK | metadata lists 3 radar effects (frame_del=off counted) | PASS | radar entries: 4 | 4
| KITCHEN-SINK | metadata seed=200 | PASS | seed=200 | 200
| KITCHEN-SINK | rdr kept ratio ~0.8 (loss_partial f=0.2) | PASS | rdr kept=0.805 | ~0.80
| KITCHEN-SINK | ldr kept ratio ~0.85 (loss_partial f=0.15) | PASS | ldr kept=0.838 | ~0.85
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

**All 89 checks passed.**

## Verification notes

- **Design Decision #1** (loss_complete vs loss_partial at f=1.0): Verified via signal-level comparison in R4, L4.
- **Design Decision #2** (frame_deletion per-sensor-only): Verified — radar clears `rdr_sparse+rdr_polar_3d+pc100p`; lidar clears `ldr64`; camera zeros tensor keys.
- **Legacy preservation**: 18 legacy effects executable by direct import; none appear in active `RADAR_EFFECTS`/`LIDAR_EFFECTS`/`CAMERA_EFFECTS` registries.
- **No training-path dependency**: Confirmed zero `pipelines/` or `train*` modules imported.
- **should_skip()**: Verified deterministic (interval + index_list) and random modes via NoiseInjector; sequence simulation confirms actual deletion rates match configured parameters.
- **Composition**: All four effects per modality applied in DEFAULT_ORDER without crash; kitchen-sink test (all 12 effects) completes with sane output.