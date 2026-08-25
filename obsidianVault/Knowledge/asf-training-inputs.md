# ASF Training Inputs Audit

Investigation completed: mapped the exact LiDAR (`ldr64`), Radar (`rdr_sparse`), and Camera (`front0`) inputs consumed during ASF training, traced end-to-end from dataset `__getitem__` through encoders to fuser.

Key findings documented at: `/home/adhish/Productivity/AMSCUP/docs/vAIlt/asf-training-inputs.md`

- LiDAR: pre-calibrated ldr64 point cloud, 5 cols [x,y,z,intensity,ring], voxelized → SECONDNet → `spatial_features_2d` (512ch)
- Radar: pre-sampled rdr_sparse points, 4 cols [x,y,z,power], voxelized + PointNet → sparse 3D backbone → `bev_feat` (768ch)
- Camera: single front0, 704×256, ImageNet normalized, Swin-S + LSS BEV pooling → `cam_bev_feat` (256ch)
- No availability-dropout during training (inference only)
- Depth labels, obj masks, pc100p, rdr_polar_3d: NOT loaded during ASF training
- Training config: `configs/v1_0/cfg_A2F_scl_final.yml`

## Cons / limitations (self-acknowledged + inferred)

- Camera branch is trained only on normal/overcast sequences (1–20) — the model essentially learns to discount camera in bad weather rather than being weather-invariant on camera features. This matters for camera corruption experiments: baseline camera reliability is already capped low, so corruption effects there may show a floor effect.
- The paper explicitly flags the camera backbone as the weakest link — camera features remain "separated" in the t-SNE space (Fig. 2c) even after CASAP, unlike LiDAR/radar which converge well.
- Benchmarked almost exclusively on K-Radar itself — no cross-dataset validation, so generalizability of the "availability-aware" claims outside K-Radar's specific sensor suite/geography is unverified.
- SCL trains over only 7 discrete sensor combinations (binary presence/absence) — it doesn't model partial degradation directly (e.g. NIS-style graded radar noise, [[robustness-metric-selection|reparameterized severity tiers]]). This is exactly the gap the inference-time corruption study fills: ASF's own training doesn't cover graded severities, so the robustness curves are genuinely novel evidence, not a re-derivation of something ASF already tested.
- Monocular camera baseline (BEVDepth) vs. stereo (DSGN++) showed negligible difference once fused (Table 8) — suggesting the fusion mechanism itself, not encoder quality, may be masking camera degradation effects. Worth keeping in mind when interpreting camera-corruption RCE results as "ASF's camera robustness" vs. "ASF's tendency to just ignore camera."