# configs/

| Path | What |
|---|---|
| `asf/ASF_v2_0_seq<N>_alvis.yml` (N = 1 to 58) | **The configs the corruption sweep ran.** `scripts/cluster_historical/asf_run.sbatch` loads `configs/ASF_v2_0_seq${SEQ}_alvis.yml`, one per test sequence. Seq 1 and seq 2 differ only in their header comment and the `portion` block; the file header says the same holds against seq 46. Each runs the official checkpoint `pretrained/ASF_v2_0_final_10.pt` (the sbatch default; `MODEL_CKPT` can override it). The checkpoint is not in this repo. |
| `asf/ASF_v2_0_final.yml` | Base ASF config. Differs from the per-sequence files in `PATH_EXP`, `START_EP`, `INTERVAL_EPOCH_UTIL` and an empty `portion` (all sequences). Not the file the sweep loaded. |
| `asf/TRAINING_cfg_A2F_scl_final.yml` | Training config for the ASF variant (reference; the thesis uses the released checkpoint, not a retrained one). |
| `noise/single/<sensor>_<effect>_<severity>.yml` | One file per corruption condition: `{camera, lidar, radar}` x `{gaussian_noise, loss_partial, frame_deletion}` x `{low, medium, high}`, plus `<sensor>_loss_complete_zero.yml` (single tier). 30 files. Selected with `NOISE_CFG` in the sbatch script. |
| `noise/*.yml` | Combined and diagnostic effects (`blackout`, `camera_dead`, `lidar_dead`, `radar_dead`, `*_zeros`, `shape_preserving`). Not part of the swept conditions. |
| `cam_calib/` | Camera calibration for the visibility pipeline (`common/` YAML, `T_params_seq/`, `T_npy/`, zipped per-sequence calibration). |
| `split/test.txt`, `split/train.txt` | K-Radar frame lists (17,535 and 17,457 lines). The sweep used the 58-sequence test split. |

Corruption semantics are defined in `src/effects/` (`config.py` for the schema, `noise_injection.py` for the effects).
