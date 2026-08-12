# Sensor Sparsity Scoring and Noise-Injection Mechanics

**Date:** 2026-08-11
**Status:** Reference note — consolidates existing code behavior, no new design decisions.
**Scope:** (1) how `kradar_visibility` scores per-sensor sparsity, (2) how AI-MSF-Benchmark's corruption code perturbs data and what hardware failure each corruption emulates, (3) status of the `kradar_visibility` pipeline as of this commit.

Related: [[04_Design/noise-injection-design.md]], [[04_Design/Output_Schema]], [[04_Design/Noise_Taxonomy]], [[04_Design/System_Architecture]]

---

## Part 1 — Sparsity scoring per sensor

Source: `test-bed/src/Modules/robust_testing/kradar/src/kradar_visibility/{radar,lidar,camera}_visibility.py`

### Radar — CFAR-based SNR-weighted power density

File: `radar_visibility.py`. Two-stage: per-frame noise-floor map (`prepare_frame_radar`), then per-bbox score (`compute_radar_sparsity_score`).

**Noise floor (1D-cross CFAR, `prepare_frame_radar`, lines 90–143):**
1. Raw linear power cube `(Z, Y, X)` → dB: `cube_db = 10*log10(power)` for cells `>0`; sentinel/invalid cells (≤0) set to a fixed **-100.0 dB** floor (`valid_mask = radar_zyx_cube > 0`).
2. `RADAR_GUARD_CELLS = 2`, `RADAR_TRAINING_CELLS = 4` (`config.py`). For each cell under test, the noise floor is the **median of 24 training cells**: 6 rays (± along Z, Y, X), each ray 4 cells long, offset by the 2-cell guard band from the center (`_build_arm_offsets`, lines 54–83). This is a **1D-cross CFAR**, not a full 3D neighborhood CFAR — only cells sharing two of three axis coordinates with the cell under test are used as training data, which is cheaper than a volumetric CFAR window but blind to diagonal clutter structure.
3. Vectorized implementation pads the dB cube by `P = guard+training = 6` cells (`np.pad(..., mode='edge')`), then per Z-plane extracts the 24 arm slices as views and does one `np.median(stacked, axis=0)` reduction — replaces the original triple-nested Python loop, verified numerically equivalent to <1e-14 max abs diff (docstring lines 14-17, reference loop kept as `_prepare_frame_radar_loop_reference`). Notably `scipy.ndimage.median_filter` was tried and rejected — it silently includes the center cell in the median even with a zero at the footprint center, which breaks guard-band exclusion (lines 33-37).
4. Invalid cells are forced back to -100.0 dB in the output noise-floor map after the vectorized pass (`noise_floor_db[~valid_mask] = -100.0`).

**Per-bbox score (`compute_radar_sparsity_score`, lines 228–300):**
- Noise floor for the bbox = **median of the CFAR noise-floor map values inside the bbox voxel range** (not per-cell local noise floor — a single scalar per object, `np.median(nf_subset)`). Falls back to a supplied scalar (`noise_floor_val`) or, if neither is given, the **global median of all valid dB cells** in the frame.
- SNR per cell: `snr = max(0, subset_db - noise_floor_db_val)` (clipped at 0, so cells below the local noise floor contribute 0, not negative).
- `raw_score = mean(snr)` over the bbox voxels.
- **Normalization**: `score = clip(raw_score / DB_HEADROOM, 0, 1)`, `DB_HEADROOM = 20.0` dB (`config.py`). So a bbox averaging ≥20 dB above its local CFAR noise floor saturates at 1.0; 0 dB above floor → 0.0. This 20 dB headroom is a fixed constant, not derived from the data — it is the single most consequential undocumented tuning knob in the radar score (see note below).
- **Output column: `radar_sparsity_score`, float, range [0, 1]** (exact per docstring: "0.0 means no signal above noise; 1.0 means average SNR ≥ DB_HEADROOM dB above noise floor").

### LiDAR (OS2-64 and OS1-128) — expected-density-ratio method

File: `lidar_visibility.py`. Same code path (`calculate_lidar_visibility`) called twice by the pipeline, once per sensor, with sensor-specific `expected_density` and channel LUT constants (`OS2_64_CHANNELS=64, OS2_64_VFOV_DEG=33.2, OS2_64_HRES_DEG=0.35`; `OS1_128_CHANNELS=128, OS1_128_VFOV_DEG=44.5, OS1_128_HRES_DEG=0.17` — `config.py`).

**Range image (`prepare_frame_lidar`, lines 36–113):**
- Convert Nx3 points to spherical: `range = sqrt(x²+y²+z²)`, `elevation = arcsin(z/range)`, `azimuth = atan2(y,x)` shifted to `[0,360)`.
- Bin into `(num_channels, azimuth_bins)` where `azimuth_bins = int(360/h_res_deg)` and channel index = `(elevation_deg - min_elev) / (v_fov_deg/num_channels)`.
- Out-of-FOV or out-of-channel-range points dropped (matches old loop's `continue`).
- Per bin, keep the **nearest** point (`np.minimum.at` seeded with `+inf`, converted to `0.0` sentinel for empty bins) — a proper range image, not just an occupancy grid.
- A documented precision landmine (lines 84-91): binning must promote `elevation_deg`/`azimuth_deg` to float64 before the divide, because float32-array-vs-python-float division stays float32 and can truncate into the wrong bin at boundaries — this bit them once already (comment explicitly calls out the numpy promotion-rule gotcha).

**Score (`calculate_lidar_visibility`, lines 116–220):**
- FOV/range check uses the **bbox center only** (not full-bbox containment) — `in_fov`/`in_range` against sensor FOV and range_limit (documented fix, ISSUE-05, avoids spuriously marking boundary-straddling objects invisible).
- `count` = number of points with all 3 coords inside `[xmin,xmax]×[ymin,ymax]×[zmin,zmax]` (vectorized boolean AND, not per-point loop).
- `density_ratio = count / expected_density` (expected_density: theoretical point count for a reference 1 m³ box at this sensor's angular resolution — computed from channel count/VFOV/HRES upstream, passed in as `expected_density`).
- **Occlusion discount** (optional, when `range_image`/`sensor_origin` given): projects the 8 bbox corners into spherical, looks up channel/azimuth-bin range-image values via nearest elevation match (`np.argmin` over channel LUT elevations) and bin-width azimuth division, then `occluded_fraction = mean(range_image_range < corner_range)` over valid samples, `confidence = fraction of samples with a valid (finite, non-NaN) hit`.
- **Final score**: `density_ratio * (1 - occluded_fraction * confidence)`. When no range image is supplied, `occluded_fraction=confidence=0` so the discount is a no-op and score reduces to plain `density_ratio`.
- `visible = in_fov and in_range and count>0 and final_score>0.0`.
- **Note**: `density_ratio` is **not clipped to [0,1]** anywhere in this function — if `count > expected_density` (denser-than-theoretical return, e.g. from a very close/reflective object), the score can exceed 1.0. This is a real gap vs. the radar and camera scores, which are explicitly clamped.
- **Output columns: `lidar64_sparsity_score` / `lidar128_sparsity_score`, float, nominal range [0, 1] but unclamped above** (`lidar64_points_count`/`lidar128_points_count` int, `lidar64_visible`/`lidar128_visible` bool).

### Camera (×4: front/left/right/rear) — projected-area + centrality, occlusion-discounted

File: `camera_visibility.py`. Two live entry points: legacy `calculate_visibility_score`/`calculate_camera_visibility` and the newer `camera_score`/`prepare_frame_camera` (Phase 4, merges §4.2+§4.3 of the methodology doc). Pipeline uses the newer path; both are described since both remain in the module.

**Depth map (`prepare_frame_camera`, lines 222–304):** projects all LiDAR points into each camera image, keeps nearest depth per pixel via `np.minimum.at` seeded at `+inf` (same pattern as the LiDAR range image), 0.0 sentinel for empty pixels. Comment flags this as a deliberate fix for a "zero-initialization bug" in a legacy loop-based version that cost ~47.5 s/frame.

**Score (`camera_score`, lines 307–436):**
- 8 object corners (half-extents in object frame) → homogeneous transform to camera frame via `T_radar2cam` → any corner with `z_cam <= 0` (behind camera) ⇒ `visible=False, score=0.0`.
- Pinhole projection `u,v` from `K`, optional radial+tangential distortion correction applied in **normalized** image coordinates (explicit code comment: applying distortion directly to pixel coords blows up `r²` to ~1e6 instead of ~4 — this was a fixed bug, not a hypothetical one, per the same pattern also present in the older `project_point_to_image`).
- Clip projected 2D bbox to image bounds `(width=CAM_HALF_WIDTH=1280, height=CAM_HALF_HEIGHT=720)` — these are per-stereo-half dimensions.
- `area = clipped_w * clipped_h`; `centrality = 1 - (|cx_proj - width/2| + |cy_proj - height/2|) / (width+height)` (L1, not L2/Euclidean, centrality — so a purely-x offset and a purely-y offset of the same magnitude discount centrality identically).
- `base_score = W1*(area/(width*height)) + W2*centrality`, **`CAM_W1=0.7` (area weight), `CAM_W2=0.3` (centrality weight)** (`config.py`) — area dominates by more than 2:1.
- **Occlusion discount**: grid-samples up to `sample_n=20` points (`int(sqrt(20))≈4` per axis → up to 16 actual samples) inside the clipped hull, compares each sample's `depth_map` value to `z_obj = median(z_cam over 8 corners)`. A sample counts occluded if `d_local < z_obj - DEPTH_MARGIN` (`DEPTH_MARGIN = 0.1` m). `occlusion_discount = 1 - occluded_count/valid_count`, **floored at 0.1** (never fully zeroes the score from occlusion alone). `DEPTH_SAMPLE_RADIUS = 3` px is defined in `config.py` but is **not referenced anywhere in `camera_score`** — the actual sampling is a coarse grid over the whole clipped hull, not a radius-3 neighborhood lookup per corner; this constant appears to be dead/aspirational config.
- `final_score = base_score * occlusion_discount`.
- `calculate_camera_visibility` picks `max(score_left_half, score_right_half)` per direction — each of the 4 directions is itself a stereo pair, and the reported score is the better of the two lenses, not an average or a consistency-weighted blend. `stereo_consistency()` (lines 439–537) exists as a separate front-pair disparity check but is not folded into `camera_score`'s occlusion discount — it's a standalone function; whether the pipeline actually calls it needs checking against `pipeline.py` (not confirmed here).
- **Output columns: `cam_front_visibility_score`, `cam_left_visibility_score`, `cam_right_visibility_score`, `cam_rear_visibility_score`, float** — nominal [0,1] since `base_score` components (area fraction, centrality) are both bounded in [0,1] and `occlusion_discount ∈ [0.1, 1.0]`, but **not explicitly clipped** in code, so a centrality/area edge case could in principle push `base_score` slightly outside [0,1] (e.g. object bbox larger than the image, area fraction >1 is prevented by clipping to `width*height`, but centrality's L1 formula can't exceed 1 either — in practice this stays in range, unlike the LiDAR score).

### Output schema (from `config.OUTPUT_SCHEMA`, `config.py`)

Full column list, one row per (sequence, frame, object): `sequence_id, frame_idx, timestamp, obj_tracking_id, obj_class, obj_x, obj_y, obj_z, obj_length, obj_width, obj_height, obj_theta, obj_distance_ego, sensor_identify, weather, radar_visible, radar_fov_in, radar_range_in, radar_sparsity_score, lidar64_visible, lidar64_points_count, lidar64_sparsity_score, lidar128_visible, lidar128_points_count, lidar128_sparsity_score, cam_front_visible, cam_front_proj_x, cam_front_proj_y, cam_front_visibility_score, cam_left_*, cam_right_*, cam_rear_*, num_sensors_visible, primary_sensor, ghost_flag`.

---

## Part 2 — Noise injection mechanics and hardware parallel

Source: `repos/AI-MSF-Benchmark/corruption/` — `main.py`, `simulation/*.py` (orchestration/IO), `operator/*.py` (actual math). This code is **entirely separate** from `kradar_visibility` — it operates on flat KITTI-format directories (`image_2/`, `velodyne/`, `calib/`), not on the K-Radar Parquet output.

**Scoping constraints (as given, not re-derived):**
- (a) Noise injection targets the **train split only** — corrupting images/point clouds doesn't alter ground-truth labels, so corrupted train data can be reused with the original labels; this is intentional project scope, not a limitation of the corruption code itself.
- (b) **Full-frame-loss corruption is out of scope** — a separate frame-delete mechanism elsewhere in the project already covers that case. The corruption code below does contain `loss_complete` operators for image and LiDAR (`ImageOperator.loss_complete`, `LidarOperator.loss_complete`) — these zero out the entire frame/cloud. Per the stated scope decision, **these are unused for this project's methodology** — noted here for completeness only, not recommended for adoption.

### Severity scaling — general pattern

Every operator uses a **fixed 5-element (or 3-element) Python list indexed by `severity-1`**, i.e. a **lookup table per level**, not a continuous/parametric function. `assert sev in range(1,6)` (image/lidar/delay/weather) or `range(1,4)` for calib (3 levels only — rotation-based calib corruption caps at severity 3, `CalibSimulation.simulation`, line 29). There is no interpolation between levels and no formula deriving level *n* from level 1 — each severity's parameter value was hand-picked (visible directly in each list literal below). This is worth flagging: severity is **not** linear in general (e.g. image `gaussian_noise` scale goes `.08, .12, .18, .26, .38` — roughly but not exactly geometric; `impulse_noise` goes `.03, .06, .09, .17, .27` — a clear nonlinear jump between level 3→4).

### Camera / image (`operator/image_operator.py`, driven by `main.py:simulate_image` → `ImageSimulation`)

| Corruption | Mechanism | Severity LUT (1–5) | Hardware parallel |
|---|---|---|---|
| `gaussian_noise` | Additive `np.random.normal(scale=c)` on image normalized to [0,1], reclip+rescale to uint8 | c = .08,.12,.18,.26,.38 | Sensor read noise / low-light thermal noise |
| `impulse_noise` | `skimage.util.random_noise(mode='s&p', amount=c)` — salt-and-pepper | c = .03,.06,.09,.17,.27 | Dead/stuck pixels, bit-flip errors in the sensor readout or bus |
| `brightness` | Convert to HSV, add `c` to V channel, clip [0,1] | c = .1,.2,.3,.4,.5 | Overexposure / strong ambient light, auto-exposure failure |
| `darkness` | Same as brightness but subtract `c` from V | c = .1,.2,.3,.4,.5 | Underexposure, low-light/nighttime driving, lens contamination |
| `defocus_blur` | Disk-kernel convolution (`cv2.filter2D` per channel) with `(radius, alias_blur)` pairs | (3,.1),(4,.5),(6,.5),(8,.5),(10,.5) | Out-of-focus lens, incorrect autofocus, condensation |
| `motion_blur` | ImageMagick (`wand`) `MagickMotionBlurImage` with `(radius, sigma)`, random angle `U(-45°,45°)` per call | (10,3),(15,5),(15,8),(15,12),(20,15) | Vehicle vibration, high angular velocity vs. exposure time |
| `distortion` | `albumentations.OpticalDistortion(distort_limit, shift_limit)`, both params equal per level | (0.5,0.5)…(1.5,1.5) | Lens defect, thermal lens deformation, mounting stress |
| `loss_partial` | Flatten image, randomly zero a `params` fraction of **all pixel values** (not spatial patches — a flat random index permutation over the raveled array) | .1,.25,.5,.75,.9 | Sensor dropout / corrupted rows-columns in readout, not physically a "patch" occlusion (contrast with `Noise_Taxonomy.md`'s dirt/patch-occlusion concept — this is uniformly scattered, not contiguous) |
| `loss_complete` | Returns an all-zero image, ignores severity | n/a | Full camera failure — **out of scope per constraint (b)**, unused |

### LiDAR (`operator/lidar_operator.py`, driven by `main.py:simulate_lidar` → `LidarSimulation`)

Operates on raw `.bin` point clouds loaded as `Nx4` (`x,y,z,intensity`) float32.

| Corruption | Mechanism | Severity LUT | Hardware parallel |
|---|---|---|---|
| `gaussian_noise` | Additive `np.random.normal(size=(N,4)) * c` on **all 4 channels including intensity** | c = .02,.04,.06,.08,.1 | Range/intensity measurement jitter, beam-steering error, atmospheric scattering |
| `impulse_noise` | Pick `c` random points (`N//30 … N//5`, i.e. count scales with cloud size not a fixed number), shift each by `±0.2` random sign per (x,y,z,intensity) dim | c = N/30, N/20, N/10, N/7, N/5 | Multipath reflections / spurious returns (ghost points), not modeled as new points but as position perturbation of existing ones |
| `loss_partial` | Randomly zero out `params` fraction of points (all 4 fields → `[0,0,0,0]`), same Bernoulli-drop mechanism as image `loss_partial` | .1,.25,.5,.75,.9 | Beam dropout, low-reflectivity surface non-return, rain/fog attenuation causing partial point loss |
| `loss_complete` | Zero out **all** points | n/a | Full LiDAR failure — **out of scope per constraint (b)**, unused |

### Delay (`operator/delay_operator.py`, driven by `main.py:simulate_delay` → `DelaySimulation`)

`delay(inputbasedir, outputbasedir, severity, copy_mode)`: severity → integer frame-shift `t ∈ {1,2,3,4,5}` (direct index, not a LUT of distinct values — `t = severity`). Builds output sequence as `[first_frame]*t + input_frames[:-t]` — i.e. **repeats the first frame t times**, then time-shifts the rest by t, via symlink (`copy_mode=0`) or file copy (`copy_mode=1`). Mechanically this is a pure temporal shift/hold-last(-first), not a jitter or randomized delay distribution. **Hardware parallel:** sensor bus latency / processing pipeline lag causing one modality's data stream to desync from the others — e.g. LiDAR spin completing late relative to camera trigger, or a slow perception-stack ingestion queue. Directly emulates temporal misalignment between sensor streams in a multi-sensor fusion pipeline.

### Calibration / extrinsics (`operator/calib_operator.py`, driven by `main.py:simulate_calib` → `CalibSimulation`)

`rotation_x/y/z(V2C, severity)`: severity → rotation magnitude `num ∈ {0.5°, 1°, 2°}` (**only 3 levels**, `range(1,4)` asserted in `CalibSimulation.simulation`), applied to a single axis. Mechanism (`extrinsic_mutaion`): decompose the 3×3 rotation block of the velo-to-cam extrinsic matrix into Euler angles (`rotationMatrixToEulerAngles`), add `theta` (in radians) to the axis under test, reconstitute the rotation matrix (`eulerAnglesToRotationMatrix`), leave translation untouched (dead/commented-out translation-noise code exists at lines 50-64 but is not wired into `rotation()` — only rotational drift is actually injected). **Hardware parallel:** extrinsic calibration drift from vehicle vibration, thermal expansion of sensor mounts, or a bump/collision that shifts sensor orientation without a full recalibration — a well-documented real AV failure mode (calibration goes stale between calibration cycles). Note the severity cap at 3 levels (not 5) is a real constraint baked into `assert sev in range(1,4)` — attempting severity 4-5 here will raise, unlike every other corruption type.

### Weather (`operator/weather_operator.py`, driven by `main.py:simulate_weather` → `WeatherSimulation`)

Not a self-contained numeric transform — both `rain` and `fog` **shell out** (`os.system`) to external third-party tools under `corruption/3rd_parts/{camera,lidar}/main.py` (physically-based rain/fog rendering pipelines, not vendored/reviewed here). 
- `rain`: severity → `rainfall ∈ {10,25,50,75,100}` mm/hr (5 levels), passed as `--intensity` to both camera and lidar external simulators.
- `fog`: severity → `level ∈ {strong, moderate, low}` — **note the inverted ordering**: `severity=1 → "strong"`, `severity=3 → "low"`, i.e. increasing severity index maps to *decreasing* fog intensity label, opposite of every other corruption's convention where higher severity = worse. Capped at 3 levels (`assert severity <= 3`). This is a real inconsistency in the codebase worth flagging if weather corruption is ever wired into this project's pipeline.
**Hardware parallel:** atmospheric attenuation — rain/fog scatter and absorb both visible light (camera) and LiDAR beams (905nm/1550nm), reducing effective range and adding backscatter noise/false near-range returns. This is the standard "weather corruption" category in AV robustness literature (cf. `docs/vAIlt/02_Literature/SeeingThroughFog.md`).

---

## Part 3 — kradar_visibility project status

Source: `git log --oneline -30` (repo root), `test-bed/src/Modules/robust_testing/kradar/{PHASE1_ANALYSIS.md, PHASE2_ROADMAP.md, AGENTS.md, architecture.md}`.

### Done / implemented and working

- **Core pipeline**: `parser.py` → `data_loader.py` → `calibration.py` → `{radar,lidar,camera}_visibility.py` → `pipeline.compute_visibility_for_frame()` → Polars DataFrame → Parquet, per `AGENTS.md`/`architecture.md`.
- **Radar CFAR noise-floor map**: implemented and vectorized (`prepare_frame_radar`), including a documented ~1000× speedup over the original triple-nested loop with the loop kept as a numerically-verified reference (`5b3cb29` — "Vectorize lidar build_range_image per-point loop, 86x speedup on real data" is a separate, later LiDAR-side vectorization commit; radar CFAR vectorization is documented in the module docstring dated July 2026).
- **LiDAR range-image precompute + occlusion-aware score**: `prepare_frame_lidar` + occlusion discount in `calculate_lidar_visibility`, vectorized bin assignment (commit `5b3cb29`, 86× speedup on real data).
- **Camera depth-buffer occlusion discount**: `prepare_frame_camera` + `camera_score`, default-on per Phase 1 gap-analysis priority #5, with a documented fix for a zero-initialization bug that cost ~47.5s/frame in the legacy loop version.
- **Output schema** (`config.OUTPUT_SCHEMA`) includes `weather`, `ghost_flag`, `num_sensors_visible`, `primary_sensor` — i.e. the "ghost flag" and "weather column" items flagged as gaps in `PHASE1_ANALYSIS.md` (#7, #9) are present in the schema as currently checked in, though this note cannot confirm the ghost-flag *logic* in `pipeline.py` is fully implemented (not read in this pass) versus just reserved as a column.
- **Viewer**: FastAPI + static HTML/JS at `src/kradar_visibility/viewer/`, reuses `config.py`/`data_loader.py`/`calibration.py`/`pipeline.compute_visibility_for_frame()`.
- **Test scaffolding**: `tests/test_smoke.py` (SMK-01..17) and `tests/test_verify.py` (VER-01..26) exist per `AGENTS.md`; smoke-test-first workflow documented.
- **Noise-injection module** (separate from kradar_visibility, in the AI-MSF-Benchmark submodule): per `docs/vAIlt/04_Design/noise-injection-design.md`, status "Implementation complete" as of 2026-07-23 rev 2 — 12-effect canonical taxonomy (4 per modality: radar/LiDAR/camera), replacing an earlier 18-effect list; `frame_deletion` and `noise_induced_shifts` added; radar effects simplified in a later 2026-07-28 change to operate only on `rdr_sparse` (not `pc100p`, confirmed zero downstream consumers).

### In progress

- **Schema additions for environment/time-of-day/object-density and noise-corruption evaluation metrics** — being worked on in a **separate, parallel task right now**; not yet landed in `config.OUTPUT_SCHEMA` as read for this note. Do not treat as done.
- Per `PHASE1_ANALYSIS.md`'s prioritized gap list, several items are plausibly mid-flight but not verifiable as complete from static file inspection alone: **Doppler-coherence gating (§1.3, radar)**, **stereo consistency wiring into the main camera score** (the `stereo_consistency()` function exists in `camera_visibility.py` but nothing read here confirms `pipeline.py` calls it), **inter-object occlusion graph**, **class-shape-prior occlusion check**, **cross-camera consistency**.

### Planned / not started (per PHASE1_ANALYSIS.md gap list, unconfirmed as started)

- Offline audit hooks for full-4DRT radar & instance-mask camera on sampled frames (gap #14).
- Config-driven per-sensor enable/disable toggles for ablation studies (gap #20).
- Range-image-based `N_expected` computation for LiDAR (replacing the current analytic-formula `expected_density`) — gap #17, would remove the LiDAR score's unclamped-above-1.0 behavior noted in Part 1 only incidentally, not as its primary purpose.

---

## Non-obvious findings worth surfacing

1. **LiDAR `sparsity_score` is not clamped to [0,1]** (`lidar_visibility.py:213`, `final_score = density_ratio * (1 - occluded_fraction*confidence)`) — unlike radar (`np.clip(..., 0, 1)`) and camera (bounded by construction). A very dense return (count > expected_density) produces a score >1, which downstream consumers treating this column as a probability/confidence would silently mishandle.
2. **`DEPTH_SAMPLE_RADIUS` (config.py) is defined but never referenced in `camera_visibility.py`** — the occlusion discount actually grid-samples the whole clipped projection hull (~16 points), not a radius-3 neighborhood per corner as the constant's name implies. Looks like a leftover from an earlier design.
3. **Weather corruption's `fog` severity is inverted relative to every other corruption**: `severity=1 → "strong"` fog, `severity=3 → "low"` fog (`weather_operator.py:49`) — opposite of rain, image, and LiDAR corruptions where higher severity number means worse corruption. A latent bug if fog is ever swept alongside other corruptions assuming monotonic severity.
4. **Calibration corruption caps at 3 severity levels, not 5** (`assert sev in range(1,4)`, `calib_simulation.py:29`), and only injects rotational drift — a commented-out translation-noise path (`calib_operator.py:58-64`) was written but never wired into `rotation()`. If translational extrinsic drift is wanted for the calibration hardware-failure story, it needs to be added, not just uncommented (the API shape suggests it was scaffolded and abandoned).
5. Radar's `DB_HEADROOM = 20.0` dB normalization constant is a fixed, seemingly hand-picked value with no derivation visible in the code — worth checking against the methodology doc (`k-radar-sensor-visibility-metrics.md`, referenced but not read in this pass) for justification before citing it as principled.
6. `LidarOperator.impulse_noise`'s corrupted-point count scales with cloud size (`N//30 … N//5`) rather than being a fixed count or fraction expressed as a percentage list like every other severity LUT in the codebase — inconsistent parameterization style, though not obviously wrong.

## Fixed bug — `obj.theta` degrees/radians mismatch (2026-08-11)

**Status: fixed**, `pipeline.py:128` (`_obj_corners`).

**Root cause**: K-Radar's raw `info_label_rev2/*.txt` label files store the object heading (`theta`, column 8 of an object line) in **degrees** — confirmed directly from a real label line, `..., Sedan, 25.885, -27.680, -0.453, 106.390, ...`, where `106.39` is only sensible as degrees (nobody encodes headings past 2π ≈ 6.28 rad). `parser.py:97` parses this value verbatim into `ObjectAnnotation.theta` with no unit conversion, and `pipeline.py:460` (output column `obj_theta`) correctly passes it straight through as degrees — that part was never wrong, and explains why `obj_theta` legitimately ranges outside a naive [-180, 180] wrap (see Part 1's schema notes / Q2 range analysis).

The bug was in `_obj_corners()`, which builds the object's 8 world-frame bounding-box corners for LiDAR point-in-box counting and radar voxel/FOV checks:

```python
cos_t, sin_t = math.cos(obj.theta), math.sin(obj.theta)   # BEFORE — obj.theta is degrees, math.cos/sin expect radians
```

Python's `math.cos`/`math.sin` expect radians; feeding a degrees value straight in silently produces a nonsense rotation (`cos(106.39 rad)` ≈ 17 full turns past the intended angle, not `cos(106.39°)`). This corrupted the rotated bbox used for **radar CFAR sampling and LiDAR point-in-box counting** for every object whose heading wasn't near a multiple of ~57.3° (1 rad expressed in degrees — the coincidental case where the wrong computation could still look plausible).

**Fix**:
```python
theta_rad = math.radians(obj.theta)
cos_t, sin_t = math.cos(theta_rad), math.sin(theta_rad)
```
Confirmed via `grep` that `obj.theta` is used in exactly two places codebase-wide: this rotation (now fixed) and the raw output-column passthrough (correct, untouched).

**Measured impact** (5-sequence, 15-frame-per-sequence rerun, 351 object-rows, before vs. after, `output_with_env_density_BEFORE_theta_fix.parquet` vs. `output_with_env_density.parquet`):

| column | rows changed | max abs Δ | mean abs Δ |
|---|---|---|---|
| `radar_visible` (bool) | 0 / 351 | — | — |
| `radar_sparsity_score` | 314 / 351 (89%) | 0.936 | 0.016 |
| `lidar64_points_count` | 227 / 351 (65%) | — | — |
| `lidar64_sparsity_score` | 227 / 351 (65%) | 0.277 | 0.008 |
| `lidar128_points_count` | 299 / 351 (85%) | — | — |
| `lidar128_sparsity_score` | 320 / 351 (91%) | 0.077 | 0.005 |

`radar_visible` is untouched because that flag is a coarse azimuth/elevation/range check on the object's *center point* — independent of rotation. Every score that actually depends on the rotated bbox footprint changed in the large majority of rows; one object's radar score swung by 0.936 (effectively 0→1 or the reverse), consistent with the old code placing the CFAR sampling region somewhere unrelated to the object's real footprint. Mean deltas are small (0.5–1.6%) because most objects in this sample have near-axis-aligned headings where the corruption happened to be mild — the 65–91% row-change rate is the number that matters, not the mean.

Camera scores are **also** affected — `pipeline.py:387` calls the same `_obj_corners(obj)` before passing corners into `calculate_camera_visibility`, so the fix propagates there too:

| column | rows changed |
|---|---|
| `cam_front_visibility_score` | 342 / 351 (97%) |
| `cam_left_visibility_score` | 27 / 351 (8%) |
| `cam_right_visibility_score` | 15 / 351 (4%) |
| `cam_rear_visibility_score` | 0 / 351 (rear camera had no visible objects in this sample either way — see Q2 note) |
| `cam_front_proj_x` / `cam_front_proj_y` | 0 / 351 (unchanged) |

Note the asymmetry: front-camera *scores* change in 97% of rows, but front-camera *projected pixel coordinates* (`proj_x`/`proj_y`) don't change at all. This is because `proj_x`/`proj_y` are computed by projecting the object **center** point (`pipeline.py` center-point projection block, separate from `corners`), which never depended on `_obj_corners()` — only the visibility *score* (area/centrality/occlusion, which needs the full rotated 8-corner hull) went through the buggy rotation. Left/right cameras changed far less often simply because fewer objects in this sample were within their FOV at all.

**Implication**: any prior evaluation run against `kradar_visibility` output predates this fix and scored a large majority of non-axis-aligned objects against a geometrically wrong bounding box for **radar, LiDAR, and front-camera** visibility — not just radar/LiDAR as initially assessed. Re-running affected analyses against post-fix output is recommended before drawing conclusions from any sparsity/visibility score in this dataset. Only the center-point pixel-projection columns (`cam_*_proj_x/y`) and the coarse geometric `radar_visible`/`radar_fov_in`/`radar_range_in` flags were untouched by this bug.

`uv run pytest tests/test_smoke.py`: 20/20 pass, both before and after the fix (smoke tests don't currently assert on absolute score values for rotated objects, which is why this bug wasn't caught by the existing suite — worth a follow-up test case with a non-trivial `theta`).
