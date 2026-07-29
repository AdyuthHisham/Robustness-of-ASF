# ASF Training Inputs Audit

Investigation completed: mapped the exact LiDAR (`ldr64`), Radar (`rdr_sparse`), and Camera (`front0`) inputs consumed during ASF training, traced end-to-end from dataset `__getitem__` through encoders to fuser.

Key findings documented at: `/home/adhish/Productivity/AMSCUP/docs/vAIlt/asf-training-inputs.md`

- LiDAR: pre-calibrated ldr64 point cloud, 5 cols [x,y,z,intensity,ring], voxelized → SECONDNet → `spatial_features_2d` (512ch)
- Radar: pre-sampled rdr_sparse points, 4 cols [x,y,z,power], voxelized + PointNet → sparse 3D backbone → `bev_feat` (768ch)
- Camera: single front0, 704×256, ImageNet normalized, Swin-S + LSS BEV pooling → `cam_bev_feat` (256ch)
- No availability-dropout during training (inference only)
- Depth labels, obj masks, pc100p, rdr_polar_3d: NOT loaded during ASF training
- Training config: `configs/v1_0/cfg_A2F_scl_final.yml`