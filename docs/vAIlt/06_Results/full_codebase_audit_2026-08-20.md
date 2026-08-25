# Full Codebase Audit — 2026-08-20

Read-only technical audit of AMSCUP's inference-time robustness pipeline: corruption effects, inference/output handling, `kradar_visibility` parquet, and the metrics stack. Scope and method per the audit brief; coverage notes are in each section and in the final caveat below.

---

## 1. Executive summary

**What exists and is functional:**
- A 14-effect (12 active + 2 disabled/legacy-adjacent) inference-time noise-injection module (`repos/K-Radar/datasets/effects/`) that composes radar/LiDAR/camera corruptions post-`__getitem__`, fully independent of the training pipeline and of the dead `cfg_effect` system. Seeded, tested (120+96+38 checks passing per the fix reports), with a real, previously-shipped RNG-desync bug found and fixed (§3).
- A bypass integration into `main_fusion_eval_0.py` that wraps the dataset with a `NoiseInjector`, sidestepping the non-functional `cfg_effect`/`consider_effects`/`build_dataset(cfg_effect=...)` chain, which was independently audited and confirmed dead (wrong dataset class, no kwarg support, hardcoded `False`).
- A blackout-resolution layer (`eval_wrapper.py`) with three physically-motivated policies (`empty`/`zero_feature`/`last_frame_hold`) for feeding a corrupted-to-`None` modality into ASF's three fixed-arity encoders (no availability mask exists in `FusionBaseIntegrated.forward`).
- A parquet-based ingestion/metrics stack (`scripts/alvis/{ingest,ap_metrics,compute_robustness,run_ap_robustness,gt_transition_analysis,predictions_to_parquet,reconstruct_object_ids}.py`) built to survive Alvis's file-count quota, computing RR/mRR (as `Rb^c`/`mRb`), CRI, a from-scratch 41-point AP reimplementation validated against K-Radar's own KITTI evaluator, and GT-object transition analysis (4-way classification: stable / corruption-induced miss / corruption-induced recovery / baseline failure).
- The `kradar_visibility` CPU pipeline (separate uv project, `test-bed/.../kradar/`), unrelated code path from the corruption/metrics stack, producing one parquet row per (sequence, frame, object) with 7-sensor visibility scores.

**What's stubbed / incomplete:**
- Radar `noise_induced_shifts` (NIS) is fully implemented but explicitly **disabled** (excluded from the active registry) pending an SNR-dial reparameterization; the blocking data-availability issue (`rdr_sparse` has no per-point SNR/RCS field, only CFAR-thresholded `power`) is confirmed directly in code comments and not resolved.
- GT-object identity via K-Radar's own `trk_id` (`reconstruct_object_ids.py`) is implemented but **has not been run on real data** — `ingest.py`'s own docstring states this path is "implemented but unvalidated against real data." The coordinate/IoU-matching fallback is the only path actually exercised.
- mAVE and mAAE are confirmed excluded (no velocity/attribute labels in K-Radar). mATE/mAOE/mASE are specified in the metrics-audit doc as the recommended diagnostic stack but **no code implementing them was found** anywhere in the repo (only AP/RR/CRI/transition-analysis code exists; see §6).
- `primary_sensor_calibrated` and any "piecewise-linear decile mapping" — referenced in this audit's own brief — **do not exist anywhere in the codebase or docs**. Only a plain `primary_sensor` column exists (arg-max over visible-sensor scores, no calibration/versioning). This is a documentation/expectation mismatch, not a code gap (see §5, §7).
- A full IoU-matched flip-rate diagnostic for frame_deletion vs. loss_complete is explicitly out of scope per user direction; only a reduced feasibility check is planned (not found as implemented code).

**Dead code:** `cfg_effect`, `consider_effects`, the `KRadarFusion_v1_0_AffectedSensor` phantom dataset class, and the entire pre-corruption effect system in `kradar_fusion_v1_0_calib_change.py` (camera crack/scratch overlay referencing missing PNGs, LiDAR FOV-occlusion effect) — all confirmed unreachable, superseded by the bypass strategy (§3).

---

## 2. Repo map

```
repos/K-Radar/
├── datasets/
│   └── effects/                              # inference-time corruption module (uv-independent of training)
│       ├── config.py                         # Effect / EffectConfig dataclasses (composable per-modality effect lists)
│       ├── __init__.py                       # public exports: NoiseInjector, EffectConfig, Effect, NoiseInjectedDataset, install_blackout_hooks, load_injector
│       ├── noise_injection.py                # 1236 lines — all 12 active effect fns + NoiseInjector class + 18 legacy effect fns (unused)
│       ├── eval_wrapper.py                    # NoiseInjectedDataset (blackout policy resolution) + install_blackout_hooks (forward-hook BEV zeroing)
│       ├── test_noise_injection.py            # 120 checks
│       ├── smoke_test_taxonomy.py             # 96 checks
│       ├── smoke_test_param_sweep.py          # 109 checks
│       ├── diagnose_loss_partial_zeroout.py   # ad hoc diagnostic script
│       └── visualize_effects*.py (v1/v2/v3)   # gallery renderers for visual inspection
├── scripts/
│   ├── main_fusion_eval_0.py                  # eval entry point; bypass NoiseInjector wiring (§3), dead cfg_effect block
│   ├── main_cond_0_args.py                    # (referenced by cfg_effect grep; not deep-read — condition-based eval variant)
│   ├── smoke_test_integration.py              # 38 checks, integration-level
│   └── alvis/                                 # Alvis-specific sweep driver + metrics/ingestion layer
│       ├── gen_single_effect_configs.py       # generates 30 severity-tier YAMLs + 3 unconditional configs
│       ├── ingest.py                          # canonical row-grain table builder; trk_id backend + coordinate/IoU fallback
│       ├── ap_metrics.py                      # 41-point interpolated AP (verbatim port of eval_revised.py get_thresholds)
│       ├── compute_robustness.py              # parses complete_results.txt → Rb^c, mRb, CRI (dir-based, legacy path)
│       ├── run_ap_robustness.py                # RR/mRR + CRI computed directly from ingest.py's row table (current path)
│       ├── gt_transition_analysis.py          # 4-way GT-object transition classification + stratified aggregation
│       ├── predictions_to_parquet.py          # flattens ~1.1M KITTI txt files → one parquet (Alvis file-quota workaround)
│       └── reconstruct_object_ids.py          # trk_id-based GT/pred identity reconstruction (implemented, unvalidated on real data)
├── utils/kitti_eval/                          # official KITTI evaluator (eval_revised.py) + rotate_iou_cpu.py (pure-NumPy IoU, no GPU/numba dep)
└── datasets/kradar_fusion_v1_0_calib_change.py # training-path dataset class; hosts the dead cfg_effect-driven camera/LiDAR effect code (unreachable)

test-bed/src/Modules/robust_testing/kradar/    # SEPARATE uv project — visibility scoring, not corruption
├── src/kradar_visibility/
│   ├── config.py                              # DATASET_ROOT resolution, sensor specs, OUTPUT_SCHEMA (single source of truth)
│   ├── parser.py                              # label file I/O
│   ├── calibration.py                         # camera calib pickle loading
│   ├── data_loader.py                         # lazy per-frame sensor loading (returns None on missing files)
│   ├── radar_visibility.py                    # SNR-weighted power density score
│   ├── lidar_visibility.py                    # point-in-box count / expected-density ratio
│   ├── camera_visibility.py                   # 8-corner projection → area+centrality score
│   ├── pipeline.py                            # orchestration; compute_visibility_for_frame(), primary_sensor/ghost_flag/occluded derivation
│   └── viewer/                                # FastAPI + static HTML/JS visual-inspection tool
└── tests/{test_smoke,test_verify,test_parallel_smoke}.py, conftest.py

docs/lit_survey/
├── noise_addition/parameter_audit.md          # 14-paper severity-parameter audit (169 lines)
└── metrics/metrics_audit.md                   # 10-paper metrics audit (217 lines)

docs/vAIlt/                                    # project documentation vault, ~140 notes across 00_Inbox…10_Archive
```

---

## 3. Corruption module deep dive

All effect functions live in `repos/K-Radar/datasets/effects/noise_injection.py`. Dispatch, seeding, and probability-gating live in the `NoiseInjector` class (same file, lines 702–908).

### 3.1 Per-effect mechanics

| Modality | Effect | Function : lines | Mechanism |
|---|---|---|---|
| Radar | frame_deletion | `radar_frame_deletion` L180–189 | `_frame_deletion_check` (L137–165) decides fire; on fire, sets `rdr_sparse`/`rdr_polar_3d` → `None`. Deterministic mode reads `dict_item['meta']['idx']['rdr']` via `_get_modality_idx` (L114–129), which fixed a modality-key mismatch bug (dataset uses `rdr`/`ldr64`/`camf` etc., not `radar`/`lidar`/`camera`). |
| Radar | gaussian_noise | `radar_gaussian_noise` L299–328 | Isotropic `N(0, σ²)` added independently to x,y,z of every `rdr_sparse` row. Does not touch `power`. Deliberately distinct from NIS (SNR-independent). |
| Radar | loss_partial | `radar_loss_partial` L331–358 | Exact-count permutation selection: `loss_num = int(n*fraction)`, `index = rng.permutation(n)[:loss_num]`, `arr[index] = 0`. Row count preserved (zero-out, not deletion). Extrapolated from AI-MSF-Benchmark's LiDAR operator (radar has no native AI-MSF analog). |
| Radar | loss_complete | `radar_loss_complete` L361–371 | Unconditional `_set_none(["rdr_sparse","rdr_polar_3d"])`. |
| Radar | loss_complete_zero | `radar_loss_complete_zero` L374–389 | Unconditional `np.zeros_like` in place — sensor present, all-zero, no `None`/blackout-policy indirection. |
| Radar | noise_induced_shifts (NIS) | `radar_noise_induced_shifts` L244–296 | **DISABLED** — excluded from `RADAR_EFFECTS`/`DEFAULT_ORDER_RADAR`. Implemented as flat isotropic Cartesian displacement (gaussian or uniform, optional clip radius). See §3.3 for the blocker. |
| LiDAR | frame_deletion | `lidar_frame_deletion` L397–406 | Same mechanism as radar; sets `ldr64` → `None`. |
| LiDAR | gaussian_noise | `lidar_gaussian_noise` L409–445 | Isotropic `N(0,σ²)` on x,y,z (single σ, anisotropic xy/z split dropped 2026-08-17); optional intensity noise (col 3, default off). |
| LiDAR | loss_partial | `lidar_loss_partial` L448–473 | Same permutation zero-out mechanism as radar, ported directly from AI-MSF-Benchmark `corruption/operator/lidar_operator.py:29-34`. |
| LiDAR | loss_complete | `lidar_loss_complete` L476–484 | `_set_none(["ldr64"])`. |
| LiDAR | loss_complete_zero | `lidar_loss_complete_zero` L487–497 | `np.zeros_like` in place. |
| Camera | frame_deletion | `camera_frame_deletion` L542–553 | On fire, all camera keys replaced with `_zero_camera_tensor` (normalized-space black, computed as `(0-mean)/std`, ≈(-2.12,-2.04,-1.80) per channel) — never `None` (image tensors can't be `None` downstream). |
| Camera | gaussian_noise | `camera_gaussian_noise` L556–571 | Additive noise, σ in 0–255 pixel units, converted to normalized-tensor space via `sigma/255/0.229` (single approximate std-channel divisor across all 3 channels, not per-channel std). |
| Camera | loss_partial | `camera_loss_partial` L574–618 | Flattens (H,W,3) uint8 to 1D, zeroes an exact-count random subset via permutation — **R/G/B channels of the same pixel can be zeroed independently** (confirmed property, ported from AI-MSF-Benchmark `image_operator.py:126-134`), not block/rectangle occlusion. |
| Camera | loss_complete | `camera_loss_complete` L621–630 | Same `_zero_camera_tensor` as frame_deletion — no separate `_zero` variant needed since camera was always zero-tensor-based. |

18 Rev-1 legacy effects (`power_gaussian_noise`, `sparse_point_dropout`, `range_attenuation`, `doppler_corruption`, `ghost_points`, `azimuth_jitter`, `power_saturation`, `lidar_random_dropout`, `lidar_fov_occlusion`, `lidar_position_noise`, `lidar_range_dropout`, `lidar_downsampling`, `camera_motion_blur`, `camera_brightness`, `camera_patch_occlusion`, `camera_jpeg_compression`, `camera_gamma_distortion`) remain in the file (L925–1237) under `ALL_EFFECTS_LEGACY`, importable by name but not registered in `ALL_EFFECTS`/dispatched by `NoiseInjector`.

### 3.2 Severity tiers — implemented vs. documented

Source: `scripts/alvis/gen_single_effect_configs.py` `SEVERITY_EFFECTS`/`FRAME_DELETION_PARAMS` (L83–133), cross-checked against `docs/lit_survey/noise_addition/parameter_audit.md` §0.

| Effect | Low | Medium | High | Doc match |
|---|---|---|---|---|
| `{radar,lidar,camera}_frame_deletion` | `mode: deterministic, interval: 19` (~5%) | `interval: 5` (~20%) | `interval: 2` (~50%) | Matches §0's 2026-08-18 decision (switched from `random p=0.1/0.5/0.9` to deterministic interval; frame 0 always deleted since `frame_index % interval == 0`). |
| `radar_gaussian_noise` (σ, m) | 0.1 | 1.0 | 2.0 | Matches §0 exactly (Kumar et al. 2025 endpoints, medium = user-chosen linear midpoint, not paper-labeled). |
| `lidar_gaussian_noise` (σ, m, isotropic) | 0.1 | 1.0 | 2.0 | Matches §0's 2026-08-18 decision to mirror radar's values (was 0.04/0.08/0.12, CommonCorruption `gaussian_rad` levels 1/3/5 — superseded per generator comment L25–35). **Caveat carried in both code comment and doc**: CommonCorruption's own scale perturbs spherical-radial r on KITTI/Velodyne data, not isotropic Cartesian xyz on K-Radar's Ouster os2-64/os1-128 — matching radar trades one unanchored ladder for a different one, not a strictly better-justified choice. |
| `{radar,lidar,camera}_loss_partial` (fraction) | 0.1 | 0.3 | 0.7 | Matches §0's approved decision (High lowered from 0.8→0.7; no paper tests partial loss past ~75%). |
| `camera_gaussian_noise` (σ, 0–255) | 20.0 | 50.0 | 80.0 | Matches §0 exactly (Morales & Habiti 2025 validated 0–100 range; evenly spaced, not their exact 30/60/100 figure checkpoints — a deliberate, disclosed choice). |
| `{radar,lidar}_loss_complete_zero` | — (unconditional, no severity) | | | Matches doc (no severity axis in literature for complete loss; treated as a qualitatively distinct terminal state, not a 4th severity point on `loss_partial`'s axis). |
| `camera_loss_complete` | — (unconditional) | | | Matches doc. |
| `radar_noise_induced_shifts` | — (disabled) | | | Matches doc's superseded note: original 0.01/1.0/5.0 m sweep abandoned; replacement (N=30/60/100% SNR dial) never implemented in code — the disabled function still contains only the old flat-meter logic (§3.3). |

No drift found between the generator's implemented parameters and the parameter_audit.md's §0 "approved, post-audit" decisions table — the generator's inline comments explicitly cite the same decision dates (2026-08-17, 2026-08-18) as the doc.

### 3.3 Known issues

**RNG desync bug (fixed).** `NoiseInjector.should_skip()` (pre-check for I/O avoidance) and `__call__()`/`_apply_list()` both drew independently from the same per-effect `sub_rng` for random-mode `frame_deletion`, so calling both for the same frame (the documented usage pattern) consumed two draws for one logical decision and could disagree — reproduced empirically at 5–7/30 mismatches (seed=7, p=0.2). Fixed 2026-07-30 via a `self._skip_cache: dict[(modality, frame_index), bool]` that `should_skip()` populates and `_apply_list()` replays via `_apply_cached_frame_deletion()` (noise_injection.py L774–827), avoiding a second rng draw on a cache hit. Confirmed in code: the cache exists exactly as described, `clear_skip_cache()` is present (L734–748), and the fix report's before/after test counts (113→120 checks passing) are consistent with the current `test_noise_injection.py`. The switch to deterministic `frame_deletion` mode (§3.2, 2026-08-18) makes this bug's random-mode trigger path currently unused in the generated severity configs, though the fix remains live code for any random-mode config.

**Stable-hash fix.** A related, adjacent fix: `_stable_hash()` (L56–65) replaces Python's builtin `hash()` for sub-seed derivation, because builtin `hash()` on strings is process-salted unless `PYTHONHASHSEED` is fixed — the original implementation silently produced different corruption across runs of the "same" seeded config. Uses `blake2b` truncated to 8 bytes, masked to 32 bits. Confirmed present at both `_sub_rng` (L68–79, currently unused by `NoiseInjector._resolve`, which uses its own inline `_stable_hash` call at L770) and `NoiseInjector._resolve` (L750–773).

**frame_deletion vs. loss_complete redundancy.** Confirmed explicitly redundant for radar/lidar and documented as such: both call `_set_none()` unconditionally when fired, on the same key sets (`_RADAR_FRAME_DELETION_KEYS`/`_LIDAR_FRAME_DELETION_KEYS`, shared constants at L176–177). `gen_single_effect_configs.py`'s header comment (L37–46) states this was confirmed by a prior empirical 2026-08-11 sweep where the two effects "aborted identically." Consequently `loss_complete` (the `None`-setting variant) is deliberately **not emitted** by the config generator — only `frame_deletion` and `loss_complete_zero` (the all-zero-array variant, which is *not* redundant, since it avoids the `None`/blackout-policy indirection entirely) appear in the generated sweep. Camera has no `loss_complete_zero` analog since camera's `loss_complete` was always zero-tensor-based.

### 3.4 Dead-code postmortem — `cfg_effect` / `consider_effects`

Confirmed via direct grep and reading `main_fusion_eval_0.py` (L103–156) and the independent audit `docs/vAIlt/06_Results/kradar-effects-audit.md` / `kradar-effects-verification.md`:

- `consider_effects = False` is hardcoded in `main_fusion_eval_0.py:126` (also independently confirmed hardcoded in `tools/asf_visualization/main_get_videos.py:65`). The `else` branch building `self.cfg_effect` (camera crack/scratch dict, LiDAR "missed"-angle dict, radar `effect=None`) is unreachable dead code — even if flipped, it would fail downstream.
- `build_dataset(self, split='test', cfg_effect=self.cfg_effect)` (L156) passes a kwarg `build_dataset()` doesn't accept: `utils/util_pipeline.py`'s signature is `def build_dataset(p_pline, split='train')`, no `**kwargs`, single-line body with no injection point — confirmed by the verification table (kradar-effects-verification.md item #5) as a `TypeError` if `consider_effects` were ever flipped to `True`.
- `self.cfg.DATASET.NAME = 'KRadarFusion_v1_0_AffectedSensor'` (L67) references a dataset class that doesn't exist in `datasets/__init__.py`'s registry (only `KRadarDetection_v1_0/v1_1/v2_0` and `KRadarFusion_v1_0` are registered) — a phantom class name, confirmed dead by the verification table (item #6).
- Radar itself has **zero** `cfg_effect`-hook implementation anywhere in `kradar_fusion_v1_0_calib_change.py` — `get_rdr_sparse()`, `get_rdr_polar_3d()`, `get_rpcs()`, `get_cube_polar()` all load and return with no effect guards (verification table item #4). Camera's crack/scratch overlay (L570–580 of that file) and LiDAR's angle-based "missed" occlusion (L775–784) do have code, but their referenced resource PNGs don't exist on disk (verification item #1).

**Bypass mechanism (what actually runs).** `main_fusion_eval_0.py` builds a `NoiseInjector` independently of `cfg_effect`/`build_dataset`, wraps the loaded `dataset[idx_frame]` dict directly after it's fetched (L163–165: `if self._noise_injector is not None: dict_item = self._noise_injector(dict_item, frame_index=idx_frame)`), and feeds the corrupted dict into `dataset.collate_fn`. This requires no change to `build_dataset`, no new dataset class, and no flip of `consider_effects` — it operates entirely as a post-`__getitem__` transform, confirmed by the "37/37 integration checks pass" report (`noise-injection-integration-report.md`) and matching the code read directly above. The Alvis sweep driver (`eval_wrapper.py`'s `NoiseInjectedDataset`) is a more fully-featured version of the same pattern (adds blackout-policy resolution and per-frame dump/logging), used for the actual 300+-job sweep rather than the single-frame `main_fusion_eval_0.py` visualization script.

---

## 4. Inference & output pipeline

**Trigger point relative to forward pass.** Corruption is applied strictly between dataset `__getitem__` and `collate_fn`/model forward — confirmed in both `main_fusion_eval_0.py` (`_NoiseInjectedDataset.__getitem__`, L52–54, and the class-level `ResultVis.vis_objects` loop) and `eval_wrapper.py`'s `NoiseInjectedDataset.__getitem__` (L183–243). The model itself never sees an uncorrupted-then-corrupted transition; `install_blackout_hooks()` (eval_wrapper.py L337–368) additionally registers forward hooks on the `cam`/`ldr`/`rdr` encoder submodules of `FusionBaseIntegrated` to zero that branch's BEV feature post-encoder, for the `zero_feature` blackout policy specifically — this is the one place corruption effects reach past the dataset layer into the model's forward pass, and only as a zeroing hook, never a code change to the encoders/fuser themselves.

**Output format.** K-Radar's own `dict_datum_to_kitti` (`utils/util_pipeline.py`, not deep-read but referenced consistently across `predictions_to_parquet.py`/`ingest.py`/`gt_transition_analysis.py`) writes native-sensor-frame values into KITTI's field slots (no camera-frame transform — confirmed by comment in `predictions_to_parquet.py` L21–25). Two per-run outputs: `all_preds.txt` (KITTI 16-token lines tagged `{seq}_{frame}_{condition} ...`) and `all_gts.txt` (15-token, tagged `{seq}_{frame} ...`, no score/condition). K-Radar's own placeholder for "zero predictions this frame" is a `dummy ...` line with an all-zero box and `score=0` — parses successfully as a spurious FP if not explicitly filtered (confirmed: 47,307 such rows in `all_preds.txt` as of 2026-08-20; `ingest.py:_parse_preds_txt` L76–84 filters these out by checking `rest.split(" ",1)[0] == "dummy"`).

`reconstruct_object_ids.py` additionally produces `all_gts_with_trkid.txt` / `all_preds_with_trkid.txt` / `all_fn.txt` / `all_gts_ambiguous.txt`, rejoining K-Radar's own persistent `trk_id` (present upstream in the UWIPL-refined label tree but discarded by `dict_datum_to_kitti`). **This backend is implemented but confirmed not yet run against real data** (`ingest.py` module docstring, L18–19: "NOT present as of this writing, so this path is implemented but unvalidated against real data").

`predictions_to_parquet.py` flattens the entire multi-condition sweep's `all/{preds,gts}/*.txt` files (excluding redundant road/time/weather duplicate subdirs) into one `all_predictions.parquet`, motivated by Alvis's per-project **file-count** quota (not just byte-size), confirmed hit empirically ("Disk quota exceeded" at 26% filesystem fill).

**Ingestion abstraction boundary.** `ingest.py`'s `load_prediction_rows()` is the single canonical entry point every downstream metric consumes (`ap_metrics.compute_ap_grouped`, `run_ap_robustness.py`, `gt_transition_analysis.build_match_table_from_ingest`) — it genuinely isolates format-specific parsing (KITTI-line regex, `dummy`-row filtering, trk_id-vs-coordinate backend selection) behind a single typed schema (`is_tp`/`is_fp`/`is_fn`/`score`/`gt_*` columns). No format-specific logic (KITTI-line parsing, tag-splitting) leaks into `ap_metrics.py`, `compute_robustness.py` (which is a distinct legacy path parsing `complete_results.txt` directly, not `ingest.py`'s row table — see below), or `gt_transition_analysis.py`'s aggregation functions — those all operate on the abstracted row/match tables only. The one exception: `gt_transition_analysis.py` itself contains the actual BEV-IoU matcher (`match_frame_pairs`) that `ingest.py`'s coordinate-fallback backend imports and calls — matching logic lives in the transition-analysis module, not ingest, a modularity choice (not a leak) that is explicitly flagged in both files' docstrings to avoid a circular import.

**Two independent robustness-computation paths coexist**, not consolidated: `compute_robustness.py` (parses `complete_results.txt` per-run-directory, confirmed by its own docstring to be **unusable for the actual sweep** because per-run directories get cleaned up after merging into `all_preds.txt`/`all_gts.txt` — "no alvis_seq*/original/ dir has an all/preds/ subdir... for any of the 10 sequences") vs. `run_ap_robustness.py` (computes AP directly from `ingest.py`'s row table, the actually-usable path). Both implement the same `compute_cri` function — `run_ap_robustness.py` imports it directly from `compute_robustness.py` rather than duplicating it, so this is partial reuse, not full duplication, but `compute_robustness.py`'s own AP-parsing path (`parse_complete_results`) is dead weight for the real sweep per its own admission.

---

## 5. Visibility parquet & occlusion proxy

Schema is `kradar_visibility.config.OUTPUT_SCHEMA` (config.py L110–161), one row per (sequence, frame, tracked object), built in `pipeline.py`'s `compute_visibility_for_frame()`.

**Geometry / identity:**
`sequence_id`, `frame_idx`, `timestamp`, `obj_tracking_id`, `obj_class`, `obj_x/y/z`, `obj_theta`, `obj_length/width/height`, `obj_distance_ego`, `sensor_identify` (the raw K-Radar label's own sensor-identity flag, distinct from this pipeline's derived `primary_sensor`).

**Per-sensor visibility (radar, ×2 LiDAR, ×4 camera):**
`radar_visible`, `radar_fov_in`, `radar_range_in`, `radar_sparsity_score`; `lidar{64,128}_visible`, `lidar{64,128}_visible_confirmed`, `lidar{64,128}_points_count`, `lidar{64,128}_sparsity_score`; `cam_{front,left,right,rear}_visible`, `cam_{front,left,right,rear}_proj_x/y`, `cam_{front,left,right,rear}_visibility_score`.

**Cross-sensor aggregates:** `num_sensors_visible` (count of visible-sensor tuples), `primary_sensor` (arg-max sensor by score among visible sensors — see pipeline.py L444–464: `visible_sensors` list of `(name, score)` tuples built conditionally per sensor, `primary_sensor = max(visible_sensors, key=lambda x: x[1])[0] if num_sensors_visible > 0 else None`).

**Scene context:** `weather`, `environment`, `time_of_day`, `frame_object_count`.

**Occlusion proxy:** `ghost_flag` and `occluded` (pipeline.py L515–521):
```python
'ghost_flag': radar_visible and not lidar64_visible and not lidar128_visible
              and not (cam_front_visible or cam_left_visible or cam_right_visible or cam_rear_visible),
'occluded': radar_fov_in and radar_range_in and num_sensors_visible == 0,
```
`ghost_flag` = radar-only detection (a plausible false-positive/ghost-target signature). `occluded` = object sits within the geometric radar FOV+range envelope ("should be observable" proxy) but *no* sensor confirms it — distinct from out-of-range. **This is the occlusion proxy derivation** — implemented as a boolean geometric-availability check, not a depth-buffer-based true occlusion test (a separate `DEPTH_MARGIN`/`DEPTH_SAMPLE_RADIUS`-based camera depth-buffer mechanism exists in `config.py` L61–63 and is used inside `camera_visibility.py`'s per-camera scoring, but `occluded` itself at the row level is the coarser radar-FOV-based proxy, not a per-sensor depth check).

**`primary_sensor_calibrated` / piecewise-linear decile mapping — not found.** Grepped exhaustively (`primary_sensor_calibrated`, `decile`) across the entire repo: no such column, function, or design doc exists. `OUTPUT_SCHEMA` has exactly one `primary_sensor` field, and `pipeline.py` computes it once, with no versioned/calibrated variant, no decile binning, and no separate calibration pass. This is a genuine gap between the audit brief's expectation and the actual codebase — flagged here rather than silently fabricated (see §7, §8).

---

## 6. Metrics pipeline

| Metric | Status | Location | Notes |
|---|---|---|---|
| mRR / RS (retention) | **Complete** | `scripts/alvis/compute_robustness.py` (`_rb`, `compute_condition_report`, L110–179); `run_ap_robustness.py` (row-table-based path, L60–107) | Two independent implementations of the same `Rb^c = corrupted_AP/original_AP` formula, aligned to metrics_audit.md §5.1's finding that `mRb` (Gao et al. naming) is mathematically RoboBEV's RR/mRR — the audit explicitly notes this is convergent re-naming, not a design choice made fresh. `run_ap_robustness.py` is the actually-usable path since per-run `complete_results.txt` files don't survive the sweep's directory cleanup. |
| CRI | **Complete** | `compute_robustness.py:compute_cri` (L119–139), reused by `run_ap_robustness.py` | `CRI = mean(Rb) - stdev(Rb)` over the 2–3 available severity tiers per effect; requires ≥2 tiers (returns `None` otherwise, explicit design choice against silently treating a 1-tier effect as "perfectly stable"). Matches the metrics_audit.md's RoHOI-derived formula, with the n=3-tiers-vs-paper's-n=5 caveat explicitly documented in both the metrics audit (§5.3) and the code's own docstring. |
| RCE | **Not separately implemented** | — | Metrics audit identifies RCE (Dong et al.) as structurally identical to Rb/RR under an inverted sign convention (`1-Rb` vs `Rb`); no dedicated RCE function exists, but it is trivially derivable from the existing `Rb^c`/`mean_rb` outputs — not implemented as a named metric anywhere. |
| mATE / mASE / mAOE (TP-error decomposition) | **Not implemented** | — | Recommended explicitly in `metrics_audit.md` §3 ("Diagnostic — TP-error decomposition") as the analytical lever to distinguish NIS-type translation error from Gaussian-noise-type scale/FP-FN error, and flagged as computable (K-Radar labels include `l,w,h` for mASE; no velocity/attribute data blocks mAVE/mAAE). No code in `scripts/alvis/` or elsewhere implements ATE/ASE/AOE computation — `ap_metrics.py` computes AP only, not per-attribute TP error. This is a genuine implementation gap, not merely a disabled/legacy path. |
| mFR (flip rate) | **Not implemented** (explicitly out of scope, reduced to a feasibility check) | `metrics_audit.md` §5.4 defines a reduced-scope re-analysis plan (compare frame_deletion's model-abort behavior against loss_complete_zero's non-abort behavior on already-existing sweep frames) | No code implementing this reduced check, or the full IoU-matched flip-rate diagnostic, was found — this remains a documented plan only. |
| GT-object transition analysis | **Complete** (matching backend partially unvalidated) | `scripts/alvis/gt_transition_analysis.py` | 4-way classification via `classify_transition()` (L312–325): `stable` (clean=1,corr=1), `corruption_induced_miss` (1,0), `corruption_induced_recovery` (0,1), `baseline_failure` (0,0). Derived per-(sequence, frame, gt_obj_idx) via `build_transition_table()` (L328–380), a full outer join between clean and corrupted match tables, with unmatched-on-one-side rows explicitly reported as `missing_one_side` rather than silently dropped or force-classified. `aggregate_transition_rates()` computes `corruption_induced_miss_rate`, `stable_detection_rate`, `corruption_induced_recovery_rate`, `churn`/`churn_rate`, and `net_retention` (the last one explicitly documented as not bounded in [0,1] — numerator/denominator populations differ by construction, not a bug), plus a hard `assert` sanity check that the four transition counts sum to the per-cell total. |

**GT-object spatial matching (predictions → GT via K-Radar `object_id`/`trk_id`): partial.** Two backends:
1. **Coordinate/IoU fallback** (`match_frame_pairs` in `gt_transition_analysis.py` L155–192): greedy, class-conditioned, single-IoU-threshold, highest-score-first BEV matching using `rotate_iou_gpu_eval` (a pure-NumPy Sutherland-Hodgman polygon-clip implementation, `utils/kitti_eval/rotate_iou_cpu.py`, no GPU/numba dependency). **This is the only backend actually exercised** — confirmed both files are present locally and used for dev/iteration.
2. **`trk_id` backend** (`reconstruct_object_ids.py` + `ingest.py:_load_via_trkid`): rejoins K-Radar's own persistent per-object `trk_id` from the UWIPL-refined label tree (discarded by `dict_datum_to_kitti` on the way to KITTI-format text), giving genuine object identity rather than IoU-based re-matching. **Implemented but confirmed not run on real data** — requires Alvis (torch/open3d/cv2 + real dataset paths), explicitly noted as "NOT present as of this writing" in `ingest.py`'s own docstring.

The module explicitly documents its own matching protocol is **not** the official KITTI AP protocol (`eval_revised.py`) — no ignored-region/DontCare/difficulty handling — so its match counts should not be compared numerically against `complete_results.txt`'s AP figures; they answer a different question (per-object identity/fate vs. precision-recall-integrated accuracy).

---

## 7. Documentation cross-check

| Design decision (doc) | Code match? | Notes |
|---|---|---|
| Severity tier values (parameter_audit.md §0) | **Match** | Generator (`gen_single_effect_configs.py`) parameters match the audit's approved decisions exactly, including inline comments citing the same rationale/dates. |
| `loss_complete` redundant with `frame_deletion(p=1.0)` for radar/lidar; not emitted by generator (Noise_Taxonomy.md, parameter_audit §3) | **Match** | Confirmed both in code (`gen_single_effect_configs.py` UNCONDITIONAL_EFFECTS excludes plain `loss_complete`) and the shared `_set_none` call sites. |
| `loss_complete_zero` distinct regime, not redundant (parameter_audit §3, literature-supported) | **Match** | Confirmed by mechanism (zero-fill vs. None) and by the doc's own citation of BenchmarkingRobustness's catastrophic-vs-graceful loss finding. |
| Frame-deletion RNG desync bug fixed (frame-deletion-rng-desync-fix-report.md) | **Match** | `self._skip_cache`, `clear_skip_cache()`, `_apply_cached_frame_deletion()` all present exactly as described; test counts (113→120) consistent. |
| `cfg_effect`/`consider_effects` confirmed dead (kradar-effects-audit.md, kradar-effects-verification.md) | **Match** | All 6 verification-table claims independently reconfirmed directly against current `main_fusion_eval_0.py` source in this audit. |
| Radar NIS reparameterization to SNR dial N=30/60/100% (parameter_audit.md §0, §0a) | **Contradiction — decided but not implemented.** | The doc presents this as an "approved, post-audit" decision, but the code's `radar_noise_induced_shifts` function (noise_injection.py L192–296) is unchanged from the old flat-meter implementation and remains fully DISABLED — the code's own TODO comment (L192–243) independently confirms the reparameterization was never carried out and cites the exact blocker (`rdr_sparse` lacks a per-point SNR/RCS field). The doc and code agree on *why* it's blocked but the doc's decision-table framing ("approved... supersedes") could read as if the change already landed; it has not. |
| `primary_sensor_calibrated` / decile-mapping (implied by this audit's own brief, not found in any vAIlt doc either) | **No corresponding doc or code found.** | Neither the codebase nor the ~140-file `docs/vAIlt/` vault contains this concept. `Output_Schema.md` (04_Design/) documents the schema as-is, including plain `primary_sensor`, with no calibrated/versioned variant mentioned. This appears to be based on a misunderstanding rather than a stale doc — there is nothing in the vault to be stale relative to. |
| Radar has no native AI-MSF `loss_partial` analog; extrapolated (Noise_Taxonomy.md, code docstring) | **Match** | Both the design doc and the function docstring (`radar_loss_partial` L331-344) state this identically. |
| GT-object identity stable across corruption conditions since GT doesn't change (gt_transition_analysis.py docstring, robustness-metric-implementation-plan.md) | **Match** | `_canonical_gt()` implementation (L206-236) directly implements this: picks one condition's GT per (sequence,frame), preferring "original". |
| trk_id backend "not present as of this writing" (ingest.py docstring) vs. robustness-metric-implementation-plan.md's §2.5 design | **Match, both flag the same gap** | Doc and code docstring both explicitly state the trk_id path is unvalidated; consistent, not contradictory. |
| Distance/weather enrichment from `kradar_test_split_full.parquet` planned (ingest.py docstring L32-34) | **Confirmed not wired in** | Code docstring states explicitly: "is NOT yet wired in here." No contradiction — doc and code agree on the gap. |

No cases were found where a vAIlt doc claims something is *implemented* that the code contradicts, other than the NIS reparameterization framing noted above — the vault's own internal convention (re-verify docs against live code before trusting historical implementation-log claims, per `Verification_Report.md`'s explicit methodology) appears to have been followed consistently; most of what could have been stale documentation has already been caught and corrected by the vault's own prior audit passes (e.g., `Verification_Report.md`'s merge of 6 near-duplicate audit reports, `Dedup_Map.md`'s dedup pass).

---

## 8. Open gaps / blockers

- **Radar NIS SNR-dial reparameterization**: blocked. Confirmed directly in code (`noise_injection.py` L192-243 TODO) and doc (parameter_audit.md §0a): `rdr_sparse` as loaded carries only `[x, y, z, power]` — no per-point SNR or RCS field. `power` is CFAR-thresholded raw linear power; the local noise-floor convolution CFAR computes at detection time is used only for thresholding and discarded, never persisted to the saved `.npy`. Three options are documented as considered (power-as-SNR-proxy; live per-sample CFAR recompute, rejected as violating the no-training-pipeline-changes constraint; offline noise-floor persistence via a preprocessing re-run) — none implemented. Effect remains DISABLED.
- **`trk_id`-based GT-object matching**: implemented, not run on real data. Requires Alvis (torch/open3d/cv2, real dataset paths, sbatch submission — never login-node/host-level installs per project convention). Coordinate/IoU fallback is the only validated path.
- **mATE/mASE/mAOE**: specified as the recommended diagnostic in `metrics_audit.md` but no implementing code found anywhere in the repo.
- **mFR / flip-rate diagnostic for frame_deletion vs. loss_complete**: reduced-scope feasibility check is documented as planned; no implementing code found. The full diagnostic is explicitly out of scope per user direction (metrics_audit.md §5.4).
- **Distance/weather/occlusion-proxy enrichment of the prediction row table**: not wired in — `ingest.py`'s own docstring states the `tesseract_idx ↔ kitti_frame_number` mapping needed to join `kradar_test_split_full.parquet` context columns onto prediction rows is "a different problem... still open at the time of writing."
- **`primary_sensor_calibrated`/decile mapping**: does not exist in code or docs (see §5, §7) — not a blocked/in-progress item, simply absent.
- **CRI's n=3-severity-tier estimator noise**: explicitly documented (metrics_audit.md §5.3) as a disclosed limitation of the sample-stdev term in `compute_cri`, not resolved (RoHOI's own validation used n=5 tiers).
- **RCE as a named, separate metric**: not implemented; trivially derivable from existing `Rb^c` output but no dedicated function exists.

---

## 9. Appendix: key code excerpts

**1. Bypass entry point — `main_fusion_eval_0.py` L103–166** (dead `cfg_effect` sits alongside the live bypass):
```python
consider_effects = False
if not consider_effects:
    self.cfg_effect = None
else:
    self.cfg_effect = dict(cam=dict(...), lid=dict(...), rad=dict(effect=None, angle=[]))
...
def vis_objects(self, indices=..., conf_thr=0.0):
    dataset = build_dataset(self, split='test', cfg_effect=self.cfg_effect)  # dead kwarg, ignored
    ...
    dict_item = dataset[idx_frame]
    if self._noise_injector is not None:                                    # bypass — actually runs
        dict_item = self._noise_injector(dict_item, frame_index=idx_frame)
    batch_dict = dataset.collate_fn([dict_item])
```

**2. Deterministic frame-deletion modality-key fix — `noise_injection.py` L94–129**:
```python
_MODALITY_IDX_KEYS: dict[str, tuple[str, ...]] = {
    "rdr": ("rdr", "radar"), "radar": ("rdr", "radar"),
    "ldr": ("ldr64", "ldr", "ldr128", "lidar"), "lidar": (...),
    "cam": ("camf", "cam", "camr", "camera"), "camera": (...),
}
```
Fixes a bug where deterministic frame_deletion silently never fired for lidar/camera because `dict_item['meta']['idx']` is keyed by the dataset's own sensor names (`rdr`/`ldr64`/`camf`), not the injector's modality names.

**3. RNG-desync fix — cache-and-replay — `noise_injection.py` L793–827**:
```python
if name == "frame_deletion" and modality is not None and frame_index is not None:
    cache_key = (modality, frame_index)
    if cache_key in self._skip_cache:
        deleted = self._skip_cache.pop(cache_key)
        if deleted:
            d = self._apply_cached_frame_deletion(modality, d)
        continue          # <- no fresh rng draw; should_skip()'s decision is replayed
```

**4. Blackout policy resolution — `eval_wrapper.py` L302–317** (`empty` policy shown):
```python
def _resolve_point_blackout(self, item, keys, saved):
    for k in keys:
        if k not in item or item[k] is not None:
            continue
        if self._policy == "zero_feature":
            item[k] = saved.get(k) or _empty_like(None)
        elif self._policy == "last_frame_hold":
            item[k] = self._prev_clean.get(k) or _empty_like(saved.get(k))
        else:  # 'empty'
            item[k] = _empty_like(saved.get(k))
```

**5. NIS blocker — `noise_injection.py` L208-214** (comment, verbatim):
```
LIMITATION (why this is blocked): rdr_sparse as loaded here carries only
[x, y, z, power] -- no per-point SNR or RCS field. `power` is CFAR-
thresholded raw linear power; the local noise floor CFAR computes at
detection time... is used only for thresholding and is discarded --
never written to the saved sprdr_*.npy.
```

**6. `primary_sensor` derivation — `pipeline.py` L444–464**:
```python
visible_sensors = []
if radar_visible: visible_sensors.append(('radar', radar_score))
if lidar64_visible: visible_sensors.append(('lidar64', lidar64_score))
... (lidar128, cam_front/left/right/rear similarly)
num_sensors_visible = len(visible_sensors)
primary_sensor = (max(visible_sensors, key=lambda x: x[1])[0]
                  if num_sensors_visible > 0 else None)
```
No calibration or decile-mapping variant exists anywhere in this file or `config.py`.

**7. Occlusion proxy — `pipeline.py` L515–521**:
```python
'ghost_flag': radar_visible and not lidar64_visible and not lidar128_visible
              and not (cam_front_visible or cam_left_visible or cam_right_visible or cam_rear_visible),
'occluded': radar_fov_in and radar_range_in and num_sensors_visible == 0,
```

**8. GT-object transition classification — `gt_transition_analysis.py` L312–325**:
```python
def classify_transition(m_clean: int, m_corr: int) -> str:
    if m_clean == 1 and m_corr == 1: return "stable"
    if m_clean == 1 and m_corr == 0: return "corruption_induced_miss"
    if m_clean == 0 and m_corr == 1: return "corruption_induced_recovery"
    return "baseline_failure"
```

**9. CRI (variance-penalized retention) — `compute_robustness.py` L119–139**:
```python
def compute_cri(rb_by_severity: dict[str, float]) -> float | None:
    values = [v for k, v in rb_by_severity.items() if k in _SEVERITY_TIERS and v is not None]
    if len(values) < 2:
        return None
    return statistics.mean(values) - statistics.stdev(values)
```

**10. 41-point AP threshold sampling (verbatim port of K-Radar's own evaluator) — `ap_metrics.py` L40–57**:
```python
def _get_thresholds(tp_scores, num_gt, num_sample_pts=41):
    scores = np.sort(tp_scores)[::-1]
    current_recall = 0.0
    thresholds = []
    for i, score in enumerate(scores):
        l_recall = (i + 1) / num_gt
        r_recall = (i + 2) / num_gt if i < (len(scores) - 1) else l_recall
        if ((r_recall - current_recall) < (current_recall - l_recall)) and (i < (len(scores) - 1)):
            continue
        thresholds.append(float(score))
        current_recall += 1.0 / (num_sample_pts - 1.0)
    return thresholds
```

**11. `dummy`-row filtering (silent-FP bug fix) — `ingest.py` L76–84**:
```python
if rest.split(" ", 1)[0] == "dummy":
    # K-Radar's own placeholder for "zero predictions this frame" --
    # 47307 such rows in all_preds.txt as of 2026-08-20, all silently
    # counted as FP before this fix.
    continue
```

**12. Canonical GT selection across corruption conditions — `gt_transition_analysis.py` L206–236** (`_canonical_gt`):
```python
chosen_condition = (
    gt.select("sequence", "frame", "condition").unique()
    .with_columns(pl.when(pl.col("condition") == "original").then(0).otherwise(1).alias("_priority"))
    .sort(["sequence", "frame", "_priority", "condition"])
    .group_by(["sequence", "frame"], maintain_order=True).first()
    .select("sequence", "frame", "condition")
)
```

---

## Coverage caveats

- All `.py` files under `repos/K-Radar/datasets/effects/`, `repos/K-Radar/scripts/alvis/`, `repos/K-Radar/scripts/main_fusion_eval_0.py`, and `test-bed/.../kradar/src/kradar_visibility/` were read in full or near-full (config.py, pipeline.py's relevant sections, noise_injection.py end-to-end, eval_wrapper.py end-to-end, all 8 alvis metrics/ingestion scripts end-to-end).
- `docs/vAIlt/` (148 markdown files, including 10_Archive duplicates — close to the brief's stated 151) was surveyed via full headers/opening context for every file plus full reads of the highest-load-bearing implementation/results notes (Noise_Taxonomy area, frame-deletion fix/verification reports, kradar-effects audit/verification, robustness-metric-implementation-plan, parameter/metrics audits' source documents). Files not read in full body (mostly `02_Literature/` per-paper annotation notes, `07_Writing/` thesis-mapping notes, and `10_Archive/` byte-identical dedup copies) were confirmed via header/opening-paragraph content to be either literature-summary notes with no code-facing claims to cross-check, or archived duplicates of files already read.
- `repos/K-Radar/` beyond the effects/scripts/alvis code was read only insofar as referenced (annotation/`trk_id` format via `reconstruct_object_ids.py`'s docstring, `rdr_sparse` structure via `noise_injection.py`'s module docstring and the NIS TODO) — no full audit of the wider K-Radar training/model code was performed, per scope.
- `docs/lit_survey/noise_addition/parameter_audit.md` (169 lines) and `docs/lit_survey/metrics/metrics_audit.md` (217 lines) were read in full; the `.html` counterpart of parameter_audit exists but was not diffed against the `.md` (not flagged as necessary — no indication in the vault that the two have diverged).

This second pass extends coverage to everything the original scope explicitly excluded: the `nuscenes`/`example` sibling modules under `robust_testing/`, the rest of `test-bed/`, the `AMSCUP_PLUS` and `AI-MSF-Benchmark` submodules, `tools/data_transfer_kradar/`, top-level scratch scripts, and the two non-code directories.

---

## 10. NuScenes module (`test-bed/src/Modules/robust_testing/nuscenes/`)

5 `.py` files, all read in full.

| File | Lines | What it is |
|---|---|---|
| `__init__.py` | 0 (empty) | No package exports — not wired into anything importable as a module. |
| `Dataset_Module.py` | ~500 (marimo notebook) | A `marimo` reactive notebook (`app.cell` decorators, `marimo.App`), not a plain script. Interactive exploration of the nuScenes mini split via `nuscenes-devkit`: lists scenes, renders LiDAR/radar/camera sample data, finds an "adverse" (night+rain) scene, plots sensor extrinsic positions in BEV, computes per-object radar/LiDAR point-in-box counts for one hand-picked annotation, and a TF-IDF-over-scene-descriptions experiment (writes `tfidf.parquet`). Roughly two-thirds of the file (from the SBERT/UMAP/HDBSCAN scene-clustering pipeline onward) is commented-out draft code, never executed. Explicitly imports `from example.sample import hello` (§11) as a cross-module smoke-test of the sibling `example` package. |
| `wise_gather_RLC_nu.py` | 366 | Standalone CLI script (not integrated with `Dataset_Module.py`). "Metadata compilation tool 1/2": iterates every scene→sample→annotation in a nuScenes split and, per annotation, computes camera visibility (`nusc.get_sample_data` box-projection check per of 6 cameras), radar point-in-box counts per of 5 radar sensors, and LiDAR point-in-box count — writes one row per annotation to a polars parquet. Single-threaded, `cProfile`-instrumentable via `--profile`. |
| `multi_wise_gather_RLC_nu.py` | 433 | Multithreaded variant of the same tool: outer `ThreadPoolExecutor` (one task per annotation, `--workers`, default 8) plus an inner 3-thread pool per annotation (camera/radar/lidar checks concurrently) — parallelism is safe because `NuScenes` object access is read-only dict/file I/O, explicitly justified in the module docstring. Produces the identical schema/output as `wise_gather_RLC_nu.py`. |
| `compare_paraquet.py` | 388 | Generic two-parquet diff tool (schema, row count, sort-and-align by key, column-by-column value comparison, colored pass/fail summary) — written to validate that the single-threaded and multithreaded gatherers above produce identical output (default `--sort-key ann_token`, matching the two gatherers' schema). Not nuScenes-specific in its logic, just used here for that purpose. Filename has a typo (`paraquet`, not `parquet`) baked into the file name itself. |

**Maturity relative to `kradar_visibility`:** far less mature. This is a per-annotation *metadata gathering* tool (visibility booleans/point-counts as flat columns) with no scoring/formula layer (no radar SNR-weighted score, no LiDAR expected-density ratio, no camera area+centrality score — just raw counts and boolean "is this object in this camera's frustum"), no config module, no tests, no CLI entry-point conventions matching `kradar_visibility`'s `pipeline.run()`. There is **no corruption-effects code and no metrics code** in this directory — it implements neither the noise-injection taxonomy (§3) nor the AP/RR/CRI/transition-analysis stack (§6); it is visibility-adjacent (point-in-box counts, camera-frustum checks) but a much shallower version of what `kradar_visibility` does for K-Radar.

**Shared code/abstractions with `kradar_visibility`:** none found. No imports between the two directories, no shared config/schema module, no common parquet schema (this module's implicit schema — `scene_token, sample_token, ann_token, instance_token, category_name, category_token, visibility_token, lidar_sensor, lidar_points, radar_points_total, radar_sensors, radar_points_per_sensor, visible_cameras, location` — bears no column-name resemblance to `kradar_visibility.config.OUTPUT_SCHEMA`, §5). The two are fully independent implementations against different dataset devkits (`nuscenes-devkit` vs. hand-rolled K-Radar label/calibration parsing).

**Active vs. stub:** the two gatherer scripts (`wise_gather_RLC_nu.py`, `multi_wise_gather_RLC_nu.py`) and the diff tool are complete, runnable CLI programs with argument parsing, profiling hooks, and (for the multithreaded one) progress reporting — not stubs. `Dataset_Module.py` is genuinely exploratory/notebook-grade: real working cells interleaved with large blocks of commented-out, never-run clustering-pipeline code (three near-duplicate draft implementations of a scene-embedding/UMAP/HDBSCAN pipeline, each superseding the last in comments, none executed). No evidence in the file listing or content of this module being invoked from any driver script, CI, or the Alvis sweep tooling in `repos/K-Radar/scripts/alvis/` — it appears to be a standalone, actively-authored-but-not-integrated exploration track, parallel to but not feeding into the K-Radar corruption/metrics work that is this project's main line.

## 11. Example template module (`test-bed/src/Modules/robust_testing/example/`)

One file, `sample.py`, read in full (9 lines):

```python
def hello(arg1, arg2):
    print(arg1 - arg2)


if __name__ == "__main__":
    x = 1
    y = 2
    hello(x, y)
```

Trivial placeholder — subtracts two numbers and prints the result. Its only observed use is as an import target from `nuscenes/Dataset_Module.py` (`from example.sample import hello`, called as `hello(5, 7)`), which reads as a smoke test confirming that `test-bed`'s package/module layout resolves cross-module imports correctly (`Modules/robust_testing/example` importable from `Modules/robust_testing/nuscenes`), not as a demonstration of any dataset-module pattern. Given `robust_testing/`'s other two directories are named after datasets (`kradar/`, `nuscenes/`), `example/` most likely exists as a placeholder/reference slot for "how a new dataset module directory is structured" — but as written, it contains no scaffold (no config.py, no pipeline.py, no expected function signatures) that a new module would actually copy from. It is a stub in the literal sense: present, importable, unrelated in content to what a real dataset module (`kradar_visibility` or the `nuscenes` gatherers) does.

## 12. `test-bed/` top level

`test-bed/main.py` is the package's nominal entry point and is exactly the uv-scaffold default: a two-line `def main(): print("Hello from test-bed!")`, unrelated to any of the actual pipelines documented above (K-Radar visibility, nuScenes gathering) — those are invoked directly (`uv run uvicorn ...`, `python scripts/...`), not through `main.py`. `pyproject.toml` declares `test-bed` as `requires-python = ">=3.10"` (looser than the `kradar_visibility` sub-project's own `pyproject.toml`/lock, consistent with `kradar_visibility` being treated as a separate nested uv project per CLAUDE.md) with top-level dependencies `hdbscan`, `marimo`, `numpy<2.0.0`, `nuscenes-devkit`, `pandas`, `polars`, `pyarrow`, `python-lsp-server`, `ruff`, `sentence-transformers`, `umap-learn`, `visidata` — i.e., this top-level project's own dependency set is oriented around the nuScenes/marimo exploration track (§10) and general tabular/notebook tooling, not around K-Radar (`kradar_visibility` pins its own separate lock file for that). `src/` contains only `Modules/` (housing `robust_testing/`) plus a `test_bed.egg-info/` build artifact and a `README.md`; no other top-level source directories exist. One stray artifact, `test-bed/tRttP5MW.zip.part`, sits at the project root (a partial/incomplete zip download, name suggests a temp-download artifact rather than anything version-controlled or referenced by code) — not investigated further as out of scope for a source audit.

## 13. AMSCUP_PLUS submodule (`repos/AMSCUP_PLUS/`)

Git submodule, own `CLAUDE.md`/`AGENTS.md`/`README.md`/`HOWTO.md`/`FIXES.md`/`MIGRATION_STATE.md`. Role (per its own README, first line): "a self contained working area for running the detection and fusion models and producing their predictions" for four models — **ASF** (tri-modal, K-Radar-only, needs the 4D radar tensor nuScenes lacks), **BEVFusion**, **CMT**, **MV2DFusion** (the latter three run on both nuScenes and K-Radar) — without ever modifying the upstream model repos in place.

**Structure** (from directory listing + READMEs, not deep-read given size/non-Python-audit scope):

| Directory/file | Role |
|---|---|
| `code/` | The four model repos with fixes applied (copies, not the upstream originals) |
| `containers/` | Container `.def` files + build/pack `.sbatch` scripts (MV2DFusion-specific containers confirmed present: `mv2dfusion.def`, `build_mv2dfusion.sbatch`, `build_mv2dfusion_ops.sbatch`, `build_mv2dfusion_base.sbatch`, `pack_mv2dfusion.sbatch`, `test_sandbox_exec.sbatch`) |
| `weights/` | Model checkpoints (not enumerated — large binary artifacts) |
| `runs/` | Job scripts, adapters, frame selectors; `runs/scale/` = full-dataset array-task scripts + resubmit/status helpers |
| `results/` | Raw predictions per `<model>__<dataset>` folder — nuScenes (val 6019 frames + train 28130 frames, per README) and K-Radar (all 58 sequences, 34,994 labeled frames) |
| `sensi_transform/` (also duplicated under `code/sensi_transform/`) | Converts `results/` → `sensi_candidates/` parquet. Files: `sensi_common.py` (schema/class maps/alignment math), `convert_kradar.py`, `convert_nuscenes.py`, `asf_align.py`, `extract_pkl.py`, `run_transform.py`, `run_all_transform.sh`, `run_extract.sh`, `make_asf_sidecars.py`. Per its own `CLAUDE.md`: outputs one parquet per (dataset, model, recording) — 2782 files total, 14-column schema (`recording_id, frame_idx, track_id, source, class_name, x, y, z, yaw, length, width, height, confidence, visibility`), ego frame REP-103 convention. This is a **separate, independently-designed candidate-detection schema** from both `kradar_visibility.config.OUTPUT_SCHEMA` (§5) and the `all_preds.txt`/parquet ingestion schema in `scripts/alvis/ingest.py` (§4/§6) — no shared column names, no code-level connection between this submodule's schema and the main-repo corruption/metrics pipeline. |
| `sensi_asf_sidecars/` | ~58 per-sequence JSON sidecar files (`asf_sidecar_seq{N}.json` + `_summary.json`) used by `asf_align.py` for ASF frame-alignment during the parquet conversion |
| `sensi_rigtest/` | Ad hoc calibration/rig comparison scripts — `validate_calib.py`, `cmp_intr.py`, `compare.py`, `analyze_z.py`, `inspect_pkl.py`, plus two camera-rig "variant" builder scripts (`builder_variantA_4cam.py`, `builder_variantB_frontonly.py`) and CMT/MV2DFusion A/B comparison `.sbatch` jobs |
| `migration_scripts/` | Arrhenius-cluster-migration build/test artifacts (`kradar.def`, `build_kradar_container.sh`, `test_asf_container.sbatch`, `populate_asf_workspace.sh`, `smoke_test.py`, plus split/manifest text files) |
| `logs/` | Command-output/diagnostic dumps copied back from cluster runs |
| Top-level `*.sbatch` (`asf.sbatch` 16 lines, `asf_sidecar.sbatch` 18, `extract.sbatch` 8, `sensi_env_test.sbatch` 9, `transform.sbatch` 8) | Small one-off job scripts for setup/conversion steps, not the full-scale `runs/scale/` array jobs |
| `replay_verify.py` (41 lines, read in full), `replay_test.py` (37), `replay_test2.py` (36) | Small standalone diagnostic scripts checking that K-Radar frame ordering in the ASF prediction output (`test_kitti/.../all/gts`) matches the raw `info_label_rev2` label files. `replay_verify.py`: reads the sequence's radar-lidar calibration offset, filters GT label centroids by ROI + azimuth + class (`Sedan`, `Bus or Truck` — the same two-class scope as this project's overall study), computes per-stem nearest-neighbor distance between the ASF-emitted GT centroids and the recomputed label centroids at spot-check indices `[0,1,100,300,500,542]`, and reports the worst mean-NN distance as a frame-alignment sanity check. |

**Migration context (from `MIGRATION_STATE.md`, `CLAUDE.md`):** this submodule is simultaneously mid-migration from the Alvis cluster to a new cluster, Arrhenius (aarch64/GH200 GPU nodes vs. Alvis's x86_64) — `MIGRATION_STATE.md` tracks confirmed environment facts (module availability, storage quotas, container portability) as of 2026-07-20 through 2026-07-27, with the ASF container confirmed building/running on Arrhenius (job 631358) but `datasets/`/`revise_label/`/`pretrained/`/`preprocessed/` data directories not yet migrated as of the last logged entry. This migration effort is a separate concern from the model-running/`sensi_transform` work and is not part of the corruption/metrics pipeline audited in §1–9.

No import or code-level dependency was found between `AMSCUP_PLUS` and the main repo's `repos/K-Radar/datasets/effects/` or `scripts/alvis/` code (different schema, different purpose — candidate-detection export across 4 models/2 datasets vs. this project's single-model ASF corruption-robustness sweep). The two do share underlying data (K-Radar sequences, ASF as one of the four models) but operate as parallel, non-integrated efforts.

## 14. AI-MSF-Benchmark integration status (`repos/AI-MSF-Benchmark/`)

Vendored third-party repo (own `.git`), top-level structure: `corruption/` (`operator/`, `simulation/`, `3rd_parts/`, `example/`), `system/` (per-model subdirectories: `CLOCs`, `TWISE`, `EPNet`, `FConv`, `DFMOT`, `MDANet`, `JMODT`), `src/`, `utils/`, `tools/`, `document/`. Not line-by-line audited, per scope (vendored code).

**Actual integration: zero code-level dependency.** Grepped for `AI-MSF-Benchmark`/`AI_MSF`/`ai_msf` and for any import path referencing this submodule across `test-bed/` and `repos/K-Radar/` — every hit is a **docstring or comment**, not an import statement or `sys.path` reference:

- `noise_injection.py` (radar/LiDAR/camera `loss_partial` functions, L332–339, L449–455, L575–580, L591, L603): cites `corruption/operator/lidar_operator.py:29-34` and `corruption/operator/image_operator.py:126-134` as the mechanism source (exact-count permutation zero-out) that was **re-implemented from scratch** in K-Radar's own module — no `import` of anything under `repos/AI-MSF-Benchmark/`.
- `smoke_test_param_sweep.py`, `smoke_test_taxonomy.py`, `test_noise_injection.py`, `visualize_effects_v2.py`: all reference "AI-MSF-Benchmark" only in comments/docstrings explaining the same loss_partial provenance, confirming the mechanism match rather than importing code.

This matches what `docs/vAIlt/06_Results/aimsf-benchmark-comparison.md`'s own scope statement says (headers surveyed in the original pass, §1): a **direct code comparison** document explicitly scoped to reading both codebases side-by-side to verify the K-Radar port matches the mechanism, not a statement that K-Radar imports AI-MSF-Benchmark code at runtime.

**Role: reference implementation only, not an integrated dependency.** AI-MSF-Benchmark functions as a citation/provenance source for two of the twelve active corruption effects' mechanics (loss_partial's permutation-based zero-out, ported independently into `noise_injection.py` for radar/LiDAR/camera) and is explicitly *not* vendored-as-a-library — no `sys.path` insertion, no `pip`/`uv` dependency entry, no `import` anywhere in the grepped set points at `repos/AI-MSF-Benchmark/`. Nothing in this pass found evidence it is more integrated than that "reference/provenance" characterization — the port is a clean-room re-implementation against the same algorithm, not a call-through.

## 15. Data transfer tooling (`tools/data_transfer_kradar/`)

6 files: `phase1_mapper.py`, `phase2_rsync.py`, `phase3_verify.py`, `quick_check.py`, `run_pipeline.sh`, `sync_manifest.json`. A 3-phase pipeline (headers read, not deep-audited — out of the corruption/metrics/visibility scope, brief summary per instructions) for moving K-Radar sensor data between machines, driven from an Excel manifest:

| File | Role |
|---|---|
| `phase1_mapper.py` | `RadarFileMapper` — reads one Excel workbook with 58 sheets (one per K-Radar sequence), builds a manifest mapping each sheet's rows to sequence folders; own docstring lists 3 "FIXES" (leading-zero stripping in `tesseract_to_cube_stem()`, configurable `output_dir`, constructor accepting `output_dir`), i.e. this is a patched second iteration of the script, not first-draft. |
| `phase2_rsync.py` | `RsyncOrchestrator` — generates per-sequence rsync commands/batches from the phase-1 manifest; same "(Fixed)" iteration marker in its docstring (manifest path no longer hardcoded, path validated, configurable batch-dir output). |
| `phase3_verify.py` | `TransferVerifier` — validates transferred files against the manifest via remote MD5 checksum comparison. |
| `quick_check.py` | Explicitly labeled "one-off diagnostic" with hardcoded `XLSX_FILE`/`BASE_DIR` paths under the file's own `# CONFIGURE THESE PATHS` comment — a manual pre-flight sanity check meant to be edited before each run, not a maintained CLI. |
| `run_pipeline.sh` | Shell wrapper chaining the three phases. |
| `sync_manifest.json` | Generated/tracked manifest artifact from a prior run. |

Overall: a maintained (fix-iterated, not scratch) 3-phase data-migration pipeline, distinct in purpose from both the corruption/metrics code (§1–9) and `AMSCUP_PLUS`'s cluster-migration tooling (§13) — this one is about the raw sensor-data transfer/verification step (mapping which local files correspond to which sequence, rsyncing them, checksum-verifying the copy), not about corruption injection or model execution.

## 16. Top-level scratch scripts

| File | One-liner |
|---|---|
| `aggregate_doc.py` | Reads Org-mode thesis notes (`/home/adhish/Documents/my_org_docs/thesis/`) plus the Obsidian vault and writes a consolidated `docs/aggregated_data.md`, with cross-reference index generation. Hardcoded absolute paths outside the repo (`~/Documents/my_org_docs/...`) — a personal, machine-specific one-off, not portable/maintained tooling. |
| `aggregate_script.py` | Near-duplicate purpose to `aggregate_doc.py` (same thesis-dir/obsidian-vault inputs, same hardcoded personal paths) — appears to be an earlier or alternate iteration of the same aggregation idea rather than a distinct maintained tool; the two were not diffed line-by-line (out of scope), but the header variable names/paths overlap almost exactly. |
| `extract_phases.py` | Parses `obsidianVault/Canvas.canvas` (an Obsidian JSON canvas file), extracting node/edge/group structure — one-off canvas-data extraction script. |
| `extract_sf.py` | Same `Canvas.canvas` input, near-identical `inside_group()` helper to `extract_phases.py` — a second one-off extraction script against the same source, not obviously merged with the first. |
| `update_xref.py` | Cross-reference/term-index builder — regex-extracts alphanumeric terms from content and tracks first-occurrence snippets, presumably feeding into the aggregation scripts' cross-reference index. |
| `main.py` | Empty file (0 bytes) — present at repo root but contains nothing. |
| `verification_report.md` | A **stale, abandoned-mid-run** QA report: every row of its verification table reads "UNVERIFIED (awaiting subagent result)" — the delegated verification subagents it was waiting on never completed or were never merged back in. Distinct from `docs/vAIlt/06_Results/Verification_Report.md` (§1's audited vault doc), which is a completed, re-verified synthesis — this top-level file is an earlier, never-finished attempt, per the vault's own `Dedup_Map.md`/`Verification_Report.md` framing (excluded from that merge as a different-topic false match, not because content overlapped). |
| `notes.txt` | Informal dated journal entries (`# 13/March` header, "Doubts"/"Status" sections) — personal working notes, not maintained documentation. |
| `commit_message.txt` | A single staged/drafted commit message ("Added comprehensive README.md for AMSCUP repository") — a scratch file for composing a commit message outside `git commit -m`, not a tracked log. |

All ten items in this section read as one-off/scratch artifacts from earlier working sessions — none carry the "single source of truth" framing that `kradar_visibility/config.py` or the `docs/vAIlt/` vault explicitly claim for themselves, and none are referenced by any of the corruption/metrics/visibility code audited in §1–9.

## 17. Non-code directories

- **`groupL/`** — 5 files, all binary reference documents: `ppts/Final_Presentation.pptx`, `ppts/Mid-term presentation.pptx`, `pdfs/Poster.pdf`, `pdfs/Initial Planning Report.pdf`, `pdfs/TME180_Project_Report (1).pdf`. Confirmed non-code per CLAUDE.md's characterization ("reference papers/slides") — a course/group deliverables archive, not consulted further.
- **`flowcharts/`** — 4 files, all Excalidraw diagram sources: `flowchart.excalidraw`, `phases_combined.excalidraw`, `dataflow.excalidraw`, `sensor_fusion.excalidraw`. Confirmed non-code diagram files, not read in detail (JSON-based drawing format, no executable content).

Neither directory was deep-read; file listing and CLAUDE.md's own description were sufficient to confirm both are out-of-scope reference/diagram material with no code-facing content to audit.
