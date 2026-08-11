# ASF Training Inputs: LiDAR, Radar, and Camera Data Keys

> **Scope**: Training pipeline only. Read-only investigation of the K-Radar repository at `/home/adhish/Productivity/AMSCUP/repos/K-Radar`. Does **not** cover eval-time noise injection (see `kradar-effects-audit.md`, `noise-injection-design.md`, `rdr_sparse-vs-pc100p-explainer.md`).

## 1. Training Entry Point

**Script**: `scripts/main_train_0_args.py` (line 26)
```python
pline = PipelineDetection_v1_0(path_cfg=PATH_CONFIG, mode='train')
pline.train_network()
```

**Pipeline**: `pipelines/pipeline_detection_v1_0.py`, class `PipelineDetection_v1_0` (line 36).

**Config used for ASF training**: `configs/v1_0/cfg_A2F_scl_final.yml` — specified via `--config ./configs/ASF_v2_0_final.yml` but the actual v1_0 config at `configs/v1_0/cfg_A2F_scl_final.yml` is the resolved reference.

**Model skeleton**: `FusionBaseIntegrated` at `models/skeletons/fusion_base_integrated.py` (line 9). This wraps three frozen pretrained encoders (CamBase, SECONDNet, RadarBase) + A2Fusion fuser + AnchorHeadSingleIntegrated head.

**Training loop**: `PipelineDetection_v1_0.train_network()` (line 268 of pipeline file). At each iteration it calls:
```python
dict_net = self.network(dict_datum)                          # line 305
loss = self.network.head.loss(dict_net)                      # line 310 (get_loss_from='detector')
```
or during SCL:
```python
loss = self.network.loss(dict_net)                           # line 171 of fusion_base_integrated.py
```

---

## 2. Per-Modality Trace

### 2.1 LiDAR (`ldr64`)

#### Config section (`cfg_A2F_scl_final.yml`, lines 39-45, 82-90)
```yaml
item: {
    'ldr64': True,
    ...
}
ldr64: {
    'processed': True,
    'dir': '/media/donghee/HDD_3/processed_lpc_calib_roi',
    'skip_line': 13,
    'n_attr': 9,
    'n_used': 5,
    'inside_ldr64': True,
    'calib': True,
}
roi: {
    'filter': True,
    'xyz': [0.,-6.4,-2.,72.,6.4,6.0],
    'keys': [],             # <-- EMPTY — dataset filter_roi does NOTHING
    'voxel_size': [0.4, 0.4, 0.4],
}
```

#### Step 1: Dataset `__getitem__` (`datasets/kradar_fusion_v1_0.py`, line 1123)
```python
dict_item = self.get_ldr64(dict_item) if self.item['ldr64'] else dict_item
```

#### Step 2: `get_ldr64` (lines 766-794)
Since `ldr64.processed=True`:
- Loads pre-processed npy from `{dir}/{seq}/lpc_{ldr_idx}.npy` (line 774)
- Returns shape `(N, 9)` — 9 attributes per point: x, y, z, intensity, ring, time, range, ... (n_attr=9)
- Already pre-calibrated and ROI-filtered at preprocessing time

Raw PCD path fallback (lines 776-790) — NOT used during ASF training because `processed=True`.

#### Step 3: `filter_roi` (line 1101-1114)
`roi.keys` is `[]` (line 101 of config), so the for loop at line 1104 iterates over nothing. **No ROI filtering happens at the dataset level during training.** Clipping occurs only inside SECONDNet's voxelizer.

#### Step 4: `collate_fn` v2_1 (lines 1278-1397)
- `rdr_sparse` and `ldr64` are treated as sparse keys (line 1289 — `list_sparse_keys`)
- Points are concatenated across batch: `dict_batch['ldr64']` becomes shape `(total_N, 9)`
- Batch index array created: `dict_batch['batch_indices_ldr64']` shape `(total_N,)`

#### Step 5: FusionBaseIntegrated.forward → SECONDNet (fusion_base_integrated.py, line 155)
```python
batch_dict = self.ldr(batch_dict)
```
The `self.ldr` encoder is a SECONDNet instance with its head replaced by `nn.Identity()` (line 100).

#### Step 6: SECONDNet `pre_processor` (`models/skeletons/second_net.py`, lines 163-201)
Reads from batch_dict:
- `batch_dict['ldr64']` — raw point cloud (line 168)
- `batch_dict['batch_indices_ldr64']` — batch membership (line 169)

For each batch item, selects first `n_used=5` columns (x, y, z, intensity, ring) (line 175):
```python
temp_points = batched_ldr64[..., :self.num_point_features]
```

Creates:
- `batch_dict['points']` — `(total_N, 6)` [batch_idx, x, y, z, intensity, ring] (line 195)
- `batch_dict['voxels']` — voxelized features (line 196)
- `batch_dict['voxel_coords']` — coordinates in bzyx format (line 197)
- `batch_dict['voxel_num_points']` — points per voxel (line 198)

Voxelization uses `voxel_size=[0.4, 0.4, 0.4]` and `point_cloud_range=[0., -6.4, -2., 72., 6.4, 6.0]` (from SECONDNet config, lines 65-71 of cfg_SECOND.yml), giving a BEV grid of 180×32×20 (x×y×z).

#### Step 7: SECONDNet forward (line 203-212)
Processes through VFE → 3D SparseCNN → HeightCompression → BaseBEVBackbone → outputs `spatial_features_2d` as the LiDAR BEV feature map.

#### Step 8: FusionBaseIntegrated writes the key mapping (fusion_base_integrated.py, line 107)
```python
setattr(self, type+'_key', encoder_cfg.KEY)  # 'spatial_features_2d'
```
This key is retrieved in `forward()` as `batch_dict['spatial_features_2d']`.

---

### 2.2 Radar (`rdr_sparse`)

#### Config section (`cfg_A2F_scl_final.yml`, lines 39-45, 94-97)
```yaml
item: {
    'rdr_sparse': True,
    ...
}
rdr_sparse: {
    'processed': True,
    'dir': '/media/donghee/kradar/rdr_sparse_data/rtnh_wider_1p_1'
}
roi: {
    'grid_size': 0.4,
    'voxel_size': [0.4, 0.4, 0.4],
}
```

#### Step 1: Dataset `__getitem__` (line 1125)
```python
dict_item = self.get_rdr_sparse(dict_item) if self.item['rdr_sparse'] else dict_item
```

#### Step 2: `get_rdr_sparse` (lines 921-938)
Since `rdr_sparse.processed=True`:
- Loads from `{dir}/{seq}/sprdr_{rdr_idx}.npy` (line 927)
- Shape `(N, 4)` — columns: x, y, z, power (line 928)
- These are pre-sampled 4D radar sparse points (approximately 1% of full cube, hence the naming convention `_1p_1` in the directory)

The fallback path (lines 930-937) loads from an older format — not used during ASF training.

#### Step 3: `filter_roi` — NOT applied for radar
`roi.keys` is `[]`, so `rdr_sparse` points are not filtered at the dataset level.

#### Step 4: `collate_fn` v2_1 (same sparse-keys logic as LiDAR)
- `dict_batch['rdr_sparse']` — concatenated points, shape `(total_N, 4)`
- `dict_batch['batch_indices_rdr_sparse']` — shape `(total_N,)`

#### Step 5: FusionBaseIntegrated.forward → RadarBase (fusion_base_integrated.py, line 156)
```python
batch_dict = self.rdr(batch_dict)
```
The `self.rdr` encoder is a RadarBase instance with its head stripped (lines 102-103):
```python
encoder.head = nn.Identity()
encoder.list_modules = encoder.list_modules[:-1]
```
So the radar encoder produces only BEV features, not detection outputs.

#### Step 6: RadarBase.forward (rdr_base.py, lines 55-58)
Delegates to modules in order: `pre_processor` → `backbone`.

#### Step 7: RadarSparseProcessor (`models/pre_processor/rdr_sparse_processor.py`, lines 65-100)
Reads from batch_dict:
- `dict_item['rdr_sparse']` — shape `(N, 4)` points (line 67)
- `dict_item['batch_indices_rdr_sparse']` — (line 68)

For each batch item:
1. Filters to current batch index (line 73)
2. Voxelizes with `grid_size=0.4`, `point_cloud_range=[0.,-6.4,-2.,72.,6.4,6.0]`, max 4 points per voxel (line 41-48)
3. If simplified PointNet enabled (it is, per RTNH config line 100-103): applies `nn.Linear(4→32)` → max pooling → writes `sp_features` (lines 86-93)
4. Writes `batch_dict['sp_indices']` — voxel coordinates (line 100)

**Input dimension**: The config at `cfg_RTNH.yml` line 98 says `INPUT_DIM: 4`. Combined with `SIMPLIFIED_POINTNET: IS_WITH_SIMPLIFIED_POINTNET: True`, `OUT_CHANNEL: 32`, the 4-column sparse radar points [x, y, z, power] are linearly projected to 32 channels then max-pooled per voxel.

#### Step 8: RadarSparseBackbone (3D SparseCNN, cfg_RTNH.yml lines 105-117)
Processes through encoding channels [64, 128, 256] with stride [1, 2, 2], then to-BEV with channels [256, 256, 256] with kernel sizes [3, 6, 12]. Outputs `batch_dict['bev_feat']` with 768 channels.

#### Step 9: FusionBaseIntegrated writes the key mapping (fusion_base_integrated.py, line 107)
```python
setattr(self, type+'_key', encoder_cfg.KEY)  # 'bev_feat'
```

---

### 2.3 Camera (`front0`)

#### Config section (`cfg_A2F_scl_final.yml`, lines 39-69)
```yaml
item: {
    'cam': True,
}
cam: {
    'front0': True,
    'front1': False,
    'left0': False,
    'left1': False,
    'right0': False,
    'right1': False,
    'rear0': False,
    'rear1': False,
}
cam_dir: {
    'load': 'cropped',
    'cropped': '/media/donghee/HDD_2/kradar_imgs_all/cropped',
}
cam_process: {
    'ori_shape': [1280, 720],
    'resize': 0.7,
    'crop': [96, 170, 800, 426],
    'mean': [0.303, 0.303, 0.307],
    'std': [0.113, 0.119, 0.107],
    'is_use_imgnet_mean_std': True,
}
t_params: {
    'load': True,
    'dir': './resources/cam_calib/T_params_seq',
    'ref_sensor': 'radar',
}
depth_labels: { 'load': False }
obj_mask: { 'load': False }
```

**Key**: Only `front0` is enabled. All other cameras are disabled.

#### Camera preprocessing flow

1. **Pre-cropped images** (not done at runtime): Original 1280×720 images are resized by 0.7 → 896×504, then cropped to [96:800, 170:426] → 704×256. These are stored and loaded from `cam_dir.cropped`.

2. **Dataset __getitem__** (line 1126):
```python
dict_item = self.get_camera_img(dict_item) if self.item['cam'] else dict_item
```

3. **`get_camera_img`** (lines 592-632, `img_load=0` path):
   - Loads `{cropped_dir}/{seq}/{cam_key}/{cam_idx}.png` via PIL.Image.open
   - Applies `self.compose_img(img)` (defined at lines 208-213)
   ```python
   self.compose_img = torchvision.transforms.Compose([
       torchvision.transforms.ToTensor(),
       torchvision.transforms.Normalize(mean=rgb_mean, std=rgb_std),
   ])
   ```
   - Since `is_use_imgnet_mean_std: True` (line 69 of config): uses ImageNet stats
     - `rgb_mean = [0.485, 0.456, 0.406]`
     - `rgb_std  = [0.229, 0.224, 0.225]`
   - Output tensor stored as `dict_item['front0']`: shape `(3, 256, 704)`, float32, normalized

4. **Collate_fn** v2_1 (lines 1335-1361):
   - `front0` is in `list_cams` (from `list_dealt_cams`, built at line 194)
   - Stacked along camera dimension: `dict_batch['camera_imgs']` shape `(B, N=1, 3, 256, 704)`
   - Calibration matrices also stacked: `sensor2image` (line 1405, shape `(B, 1, 4, 4)` — radar→front0 projection)
   - The `ref_sensor` is `'radar'` (line 77 of config)

#### Step 5: FusionBaseIntegrated.forward → CamBase (fusion_base_integrated.py, line 154)
```python
batch_dict = self.cam(batch_dict)
```
The `self.cam` encoder is a CamBase instance with its head replaced by `nn.Identity()` (line 98).

#### Step 6: CamBase.forward (`models/skeletons/cam_base.py`, lines 269-324)
Reads from batch_dict:
- `batch_dict['camera_imgs'][:,0,:,:,:]` — front0 images only, shape `(B, 3, 256, 704)` (line 270)
- `batch_dict['sensor2image']` — radar→camera projection matrix, shape `(B, 1, 4, 4)` (line 310)

Processing:
1. Swin-S backbone extracts multi-scale features (line 272)
2. FPN neck (LSSFPN) produces `batch_dict['image_fpn']` (line 274)
3. LSS depth estimation network -> depth + context features (lines 301-305)
4. BEV pooling using `sensor2image` geometry (lines 310-316)
5. Downsample + permute
6. Output: `batch_dict['cam_bev_feat']` — shape `(B, 256, H, W)` (line 319)

#### Step 7: FusionBaseIntegrated writes the key mapping (fusion_base_integrated.py, line 107)
```python
setattr(self, type+'_key', encoder_cfg.KEY)  # 'cam_bev_feat'
```

---

## 3. The Fuser and Head

### A2Fusion fuser (`models/fuser/a2_fusion.py`, lines 166-184)
Reads from `batch_dict`:
- `batch_dict['cam_bev_feat']` — Camera BEV (channel 256)
- `batch_dict['spatial_features_2d']` — LiDAR BEV (channel 512)
- `batch_dict['bev_feat']` — Radar BEV (channel 768)

These are projected to common dimension (256), patched, and fused via multi-head attention with learned queries. Output: `batch_dict['fused_feat']`.

### AnchorHeadSingleIntegrated (`models/head/anchor_head_integrated.py`, lines 364-394)
Reads `data_dict['fused_feat']` (from config key `KEY_FEATURES: 'fused_feat'`, line 203 of config).

Also reads `data_dict['gt_boxes']` during training for target assignment.

---

## 4. Availability Mechanism During Training

**None.** Despite the model name "Availability-aware Sensor Fusion," the training pipeline has **no sensor dropout, masking, availability-flag logic, or simulated sensor absence**.

The A2Fusion fuser does have an availability check at lines 168-173 of `a2_fusion.py`:
```python
### Adjusting availability ###
if not self.training:
    if 'avail_feats' in batch_dict.keys():
        if temp_key not in batch_dict['avail_feats']:
            continue
### Adjusting availability ###
```

This is **gated by `if not self.training:`** — it only activates during evaluation/inference. During training, all three sensor branches always execute and all three feature maps are always fused.

No training code in `pipelines/pipeline_detection_v1_0.py` or `models/skeletons/fusion_base_integrated.py` ever populates an `avail_feats` key. The variable `batch_dict['avail_feats']` only appears in the eval-time noise-injection path (`scripts/main_fusion_eval_0.py`), not in training.

**Verdict**: The "availability" awareness is an inference-only feature. The model is trained exclusively on complete, all-sensors-present data.

---

## 5. Keys Loaded by Dataset But NOT Consumed During Training

| Key | Config setting | Why not used |
|-----|---------------|--------------|
| `rdr_polar_3d` | Not in `item` dict (defaults to False) | Not loaded |
| `pc100p`, `pc10p`, `pc1p`, etc. | `item.rpcs` is False (not in config) | Not loaded |
| `rdr` (full cube) | `item.rdr: False` | Not loaded |
| `ldr128` | `item.ldr128: False` | Not loaded |
| `depth_labels` | `depth_labels.load: False` | Not loaded |
| `obj_mask` | No `obj_mask` section in config | Not loaded |
| `front1`, `left0`, `right0`, etc. | All `False` | Not loaded |
| Front/left/right/rear raw images | `cam_dir.load: 'cropped'` (not `img_load=2`) | Pre-cropped path only |

---

## 6. Summary Table

| Modality | Dataset key | Shape (per sample) | Preprocessing | Config location | Encoder model | Dict key consumed by fuser |
|----------|-------------|-------------------|---------------|----------------|---------------|---------------------------|
| **LiDAR** | `ldr64` | `(N, 9)` → `n_used=5` cols: [x, y, z, intensity, ring] + calib offset | Pre-processed npy (calibrated + ROI-filtered offline); SECONDNet voxelizer clips to point_cloud_range | `cfg_A2F_scl_final.yml` lines 39-45, 82-90, 98-106; `cfg_SECOND.yml` lines 65-72 | `SECONDNet` (`second_net.py`) | `spatial_features_2d` (512 ch) |
| **Radar** | `rdr_sparse` | `(N, 4)` cols: [x, y, z, power] | Pre-processed 1% sparse points from `rtnh_wider_1p_1`; voxelized to grid_size=0.4; PointNet-projected (4→32) | `cfg_A2F_scl_final.yml` lines 39-45, 94-97; `cfg_RTNH.yml` lines 96-103 | `RadarBase`→`RadarSparseProcessor` + `RadarSparseBackbone` (`rdr_base.py`, `rdr_sparse_processor.py`) | `bev_feat` (768 ch) |
| **Camera** | `front0` | `(3, 256, 704)` | Pre-cropped 704×256; ToTensor (0-1) + ImageNet normalize `mean=[0.485,0.456,0.406]`, `std=[0.229,0.224,0.225]` | `cfg_A2F_scl_final.yml` lines 47-69; `cfg_CAMERA_MODEL_Base.yml` lines 147-170 | `CamBase`→Swin-S + LSSFPN + BEVPool (`cam_base.py`) | `cam_bev_feat` (256 ch) |

---

## 7. Plain-English Verdict

> **What are the actual LiDAR, Radar, and Camera inputs to ASF training?**

**LiDAR**: A pre-calibrated 64-channel Ouster OS2-64 point cloud (`ldr64`), loaded as an (N × 9) array but only the first 5 columns (x, y, z, intensity, ring) are consumed by the SECONDNet backbone. The raw points are voxelized into 0.4 m cubes spanning [0 to 72 m in x, −6.4 to 6.4 m in y, −2 to 6 m in z], then processed through VFE + 3D sparse convolutions + BEV compression to produce a 512-channel LiDAR BEV feature map.

**Radar**: Pre-sampled sparse 4D radar points (`rdr_sparse`), loaded as an (N × 4) array of [x, y, z, power] — approximately 1% density of the full radar cube (sourced from the `rtnh_wider_1p_1` preprocessed dataset). These are voxelized at 0.4 m, projected through a lightweight PointNet (linear 4→32 → max pooling), then processed through 3D submanifold sparse convolutions to produce a 768-channel radar BEV feature map.

**Camera**: A single front-facing camera image (`front0`), pre-cropped to 704 × 256 pixels, normalized to [0, 1] via ToTensor, then standardized with ImageNet channel statistics (mean [0.485, 0.456, 0.406], std [0.229, 0.224, 0.225]). This is run through a Swin-S backbone, LSS-FPN neck, and LSS BEV pooling (using radar-to-camera projection geometry) to produce a 256-channel camera BEV feature map.

**All three modalities are always present during training.** The "Availability-aware" name refers strictly to an inference-time capability: at test time, the A2Fusion fuser can skip a sensor branch if its feature key is absent from `batch_dict['avail_feats']`. No such logic operates during training — the model is trained exclusively on complete sensor triplets (LiDAR + Radar + Camera), with no sensor dropout, masking, or simulated unavailability. The dataset loads six additional data types (`rdr_polar_3d`, `pc100p`, `depth_labels`, `obj_mask`, etc.) that are completely unused by the ASF training pipeline.