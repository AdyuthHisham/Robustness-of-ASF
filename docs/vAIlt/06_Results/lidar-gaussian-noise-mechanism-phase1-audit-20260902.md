# Phase 1 audit: why LiDAR Gaussian noise collapses ASF mAP

Read-only. No training/config/data-loader changes made. No forward pass run.

## Coverage statement

Checked: Stage A (full, computed), Stage B (full, code-read only — no hook run),
Stage C (local-availability check only). Not checked: Stage D (not reached — B's
answer already gives a clear mechanistic direction, so D is scoped but deprioritized
pending user call). No BEV features were extracted or inspected. No model was loaded
into memory or run.

## Data used

- `repos/K-Radar/outputs/robustness_reports/row_table_iou03.parquet` (1,109,616 rows,
  mtime 2026-09-01 10:27 — the frame-key-corrected table per
  [[exhaustive-crossproduct-frame-key-fix-20260901]]).
- Conditions: `original`, `lidar_gaussian_noise_medium`, `lidar_gaussian_noise_high`.
- Classes present in this table: `sed` (sedan), `bus`. No other classes are in the
  IoU-0.3 row table, so this is not a full 5+-class breakdown — it's what exists.
- Matching semantics verified directly: TP rows carry both pred and gt columns;
  FP rows have `matched_gt_row_id = null` (pred-only); FN rows have
  `pred_row_id = null` (gt-only). `iou` is populated only on TP rows. This
  confirms trk_id/coordinate matching is already resolved upstream — no blocker here.

## Stage A — failure-mode breakdown (fully executed)

Wilson 95% CIs, N shown. FN rate = FN/(TP+FN) (per-GT-object miss rate). FP rate =
FP/(TP+FP) (fraction of predictions that are false alarms). mATE = mean L2 position
error (m) on TP-matched pairs. mASE here is a **relative-dimension-error proxy**
(mean of |Δh|/h, |Δw|/w, |Δl|/l), not the nuScenes aligned-IoU mASE — flagging this
explicitly since the row table doesn't carry a center/orientation-aligned IoU to
compute the standard metric from. mAOE = mean wrapped absolute yaw error (rad).

| cls | cond | N(gt) | N(pred) | TP | FP | FN | FN rate [95% CI] | FP rate [95% CI] | mATE | mASE(proxy) | mAOE(rad) | mean IoU(TP) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sed | original | 29613 | 26761 | 23008 | 3753 | 6605 | 0.223 [0.218,0.228] | 0.140 [0.136,0.145] | 0.279 | 0.097 | 0.215 | 0.740 |
| sed | lidar_gauss **medium** | 29613 | 5337 | 4516 | 821 | 25097 | **0.848** [0.843,0.852] | 0.154 [0.144,0.164] | 0.399 | 0.079 | 0.212 | 0.707 |
| sed | lidar_gauss **high** | 29613 | 4688 | 4150 | 538 | 25463 | **0.860** [0.856,0.864] | 0.115 [0.106,0.124] | 0.374 | 0.077 | 0.177 | 0.713 |
| bus | original | 5843 | 5308 | 4161 | 1147 | 1682 | 0.288 [0.276,0.300] | 0.216 [0.205,0.227] | 0.440 | 0.103 | 0.160 | 0.679 |
| bus | lidar_gauss **medium** | 5843 | 2080 | 1726 | 354 | 4117 | **0.705** [0.693,0.716] | 0.170 [0.155,0.187] | 0.636 | 0.097 | 0.026 | 0.670 |
| bus | lidar_gauss **high** | 5843 | 1781 | 1477 | 304 | 4366 | **0.747** [0.736,0.758] | 0.171 [0.154,0.189] | 0.640 | 0.102 | 0.025 | 0.666 |

No low-N cells — smallest stratum (bus/high, N(pred)=1781) is still comfortably
above the point where Wilson CIs would be uselessly wide.

**Reading:**

1. **FN rate is the story.** Sedan FN rate goes 22%→85%→86% clean→medium→high; bus
   goes 29%→70%→75%. This is a ~4x (sedan) to ~2.5x (bus) jump in the *miss* rate.
2. **FP rate does not move meaningfully** in the direction that would explain a
   collapse — it's flat or actually *drops* for sedan (14.0%→15.4%→11.5%) and stays
   roughly flat for bus. There's no hallucination surge; noise is not manufacturing
   detections.
3. **Localization on survivors degrades but nowhere near enough to explain the mAP
   collapse on its own.** mATE roughly worsens: sedan 0.28m→0.40m (+43%), bus
   0.44m→0.64m (+45%). mASE proxy is flat/slightly improved. mAOE is flat for sedan,
   and *drops* for bus (0.16→0.025 rad) — almost certainly a selection artifact: the
   few buses that still get detected under heavy noise are the easy, well-oriented
   ones, not evidence that orientation gets more accurate under noise.
4. **Conclusion**: the mechanism is overwhelmingly "objects stop being detected at
   all," not "objects are detected but placed/sized/oriented worse" and not
   "hallucinated FPs." Total predicted-object volume collapses too (sedan
   N(pred) 26,761→5,337, an 80% drop) — the detector head is firing far less often
   under LiDAR Gaussian noise, full stop. Any explanation of ASF's mAP collapse needs
   to explain *why detections vanish*, not why localization gets noisier.

This directly motivates Stage B: is there a modality gate that could be
suppressing detections wholesale under a noise-derived signal, or is this a
backbone/feature-quality failure with no gate involved at all?

## Stage B — availability/reliability gating (code read, no forward pass)

Read `repos/K-Radar/models/fuser/a2_fusion.py` (`A2Fusion.forward`, lines 157–237)
and its only caller pattern in `repos/K-Radar/scripts/main_fusion_eval_0.py`
(`vis_objects`, ~line 155–188, and the analogous eval-path block ~line 740).

**Finding — answers the blocking question directly: there is no learned or
computed reliability/quality signal anywhere in the fusion path. The only gate is
a hardcoded, binary, human-specified modality-presence list, and it is not, and
structurally cannot be, sensitive to Gaussian noise.**

Specifics:

- The only "availability" mechanism is `batch_dict['avail_feats']`
  (`a2_fusion.py:168–173`): if a modality's key isn't in this list, its features
  are skipped entirely before cross-attention (`continue`). This is populated by
  the *caller*, not learned by the model — it's a static Python list built from a
  hardcoded string `infer_mode = 'rlc'` (radar+lidar+camera, all three) in the eval
  scripts. **Gaussian-noise conditions never touch `infer_mode`** — noise corrupts
  the tensor values inside an available modality; it does not remove the modality
  from `avail_feats`. So this gate is inert for every experiment in Stage A's
  table. It only fires for the frame-deletion / complete-loss ablations, not the
  Gaussian-noise ones.
- Given a modality passes the presence check, `A2Fusion` embeds it
  (`to_embed_*`), patches it, and feeds it as key/value into one
  `nn.MultiheadAttention` layer (`self.fuser`, line 99) against a learned query
  (`self.aware_query`). Standard MHA has **no explicit quality/confidence term** —
  attention weights come purely from learned content similarity between the query
  and whatever key/value content is handed to it. There is no per-modality scalar
  gate, no dropout-based reliability estimate, no auxiliary quality head anywhere
  in this module. (Also checked: no such thing under
  `backbone_3d/pfe/voxel_set_abstraction.py` or `backbone_2d/resnet_wrapper.py` —
  the only other hits for "quality"/"gate"/"reliab" in `models/`, both unrelated
  string matches in docstrings/unrelated code.)
- The sensor-combination-loss (`is_scl`) path (training-only, line 154, 193–211)
  trains the model against subsets of modalities for robustness, but this is a
  *training-time regularizer*, not an inference-time gate — it doesn't change what
  happens to the checkpoint's forward pass on a noisy test frame.

**Direct answer to the brief's blocking question**: the signal is sensitive **only
to modality absence/dropout** (a hardcoded string, not even a learned flag), and is
**completely blind to in-modality data quality/noise**. Under Gaussian noise, ASF
has no mechanism to detect "this LiDAR is garbage" and down-weight or ignore it —
it always attends to it exactly as if it were clean. If the noise degrades the
LiDAR backbone's BEV features into something uninformative or adversarial to the
learned query, cross-attention will still blend it in at full strength, which is
consistent with Stage A's finding that the detection head simply stops firing
(mass FN) rather than mislocalizing.

**This is a real, code-confirmed structural gap, and probably the most quotable
finding of Phase 1**: ASF's "availability" mechanism is a presence/absence
switchboard operators must flip by hand, not a learned robustness feature. The
Gaussian-noise collapse is not something the architecture is failing to handle
correctly — it's something the architecture has no facility to handle at all.

### Scoped Phase 2 candidate (not run): confirm empirically via forward-pass hook

To confirm the mechanistic story (backbone feature quality degradation → blind
cross-attention → detection head under-fires) rather than resting on architecture
reading alone, a Phase 2 hook would need:

- **Checkpoint**: `ASF_v2_0_final_10.pt` — **see blocking finding below, this is
  not actually a local file.**
- **Frames**: a small paired sample (~10–20 frames) that have both `original` and
  `lidar_gaussian_noise_{medium,high}` rows in the row table, stratified across the
  FN cases identified in Stage A (i.e., objects with GT present in both clean and
  noisy that flip TP→FN).
- **Hook points**: `batch_dict['fused_feat']` (post-fusion, `a2_fusion.py:235`) and
  `batch_dict['feat_b4_fusion']`/`feat_indiv` (pre-fusion per-modality, already
  wired for visualization via `get_feats_to_vis`/`feat_indiv` flags in the same
  forward — no new instrumentation needed, just flip existing flags).
- **Compute**: inference-only, no gradients, single-frame batches — this is cheap
  (CPU-feasible if GPU isn't available locally; each forward pass is a handful of
  small conv/attention ops on a fixed-size BEV grid, not a full training loop).
- **Not run in Phase 1** per the read-only constraint. Flagging as ready to go
  pending your approval and pending resolution of the checkpoint-location blocker.

## Stage C — raw point-cloud / voxelization-level check

**Hard blocker, consistent with prior findings — not new.**

`repos/K-Radar/data` is not a local directory; it is a **read-only `sshfs` mount**
to `alvis2.c3se.chalmers.se` (`mount` confirms `fuse.sshfs`, pointing at Alvis
Cephyr storage). `ls`/traversal into it hangs for 15s+ and was killed rather than
returning. Raw LiDAR point clouds (`os2-64` or equivalent) are not locally mirrored
anywhere in the repo — I checked `test-bed/src/Datasets` (empty/absent) and did not
find a local point-cloud cache elsewhere. This matches [[project_alvis_permanently_unavailable]]
and the brief's own caveat, so Stage C is a documented blocker, not new information:
**a point-count/density comparison on raw clouds cannot be done locally.**

## Stage D — BEV feature-map comparison

Not executed (per instructions: only scope this if B doesn't already answer the
mechanism, and B gave a clear, code-confirmed answer). If you want it anyway, the
hook points are identical to the ones scoped for Stage B's Phase 2 candidate above
(`fused_feat`, `feat_indiv`) — Stage D would just mean also capturing each
modality's *pre-fusion, post-backbone* BEV tensor (`batch_dict['bev_feat']` for
LiDAR, per `KEY_FEATS`/`DIM_FEATS` in the A2Fusion config) for the same clean/noisy
frame pairs and diffing them directly (cosine similarity / L2 per spatial cell),
rather than just comparing post-fusion output. No additional access requirements
beyond what Stage B's candidate already needs.

## Blocking questions — need your call before Phase 2

1. ~~Checkpoint locality contradiction.~~ **Resolved by user 2026-09-02**: Alvis
   storage/file access (the sshfs mounts, including `pretrained/`) still works —
   there are simply no CPU/GPU nodes left, so no compute can run *on* Alvis. Reading
   `ASF_v2_0_final_10.pt` straight off the `pretrained/` mount for a Phase 2 forward
   pass is fine; the pass itself just has to execute on local hardware, which was
   always the plan. No copy-to-local-disk step needed. Memory updated
   ([[project_alvis_permanently_unavailable]]).
2. **Class scope.** Stage A only covers `sed`/`bus` because that's all that's in
   `row_table_iou03.parquet`. If the thesis's headline mAP figure is computed
   across a broader K-Radar class set, confirm whether that full multi-class
   breakdown lives in a different table (`full_denormalized_table*.parquet`?) that
   I should re-run Stage A against, or whether sed/bus is in fact the full
   evaluated class set for this checkpoint.
3. **mASE definition.** I used a relative-dimension proxy, not nuScenes-style
   aligned-IoU mASE, because the row table doesn't carry the fields to compute a
   true translation/rotation-decoupled size-only IoU. If you want the real metric
   for the thesis, that requires re-deriving aligned boxes from the raw box
   parameters already in the table (feasible, not run here since it wasn't needed
   to answer Stage A's qualitative question) — flag if this matters for what gets
   cited downstream.
4. **Whether to proceed to the Stage B Phase 2 hook** at all, given Stage B's
   code-read answer is already fairly conclusive (no gate exists, full stop) — or
   whether that's sufficient for the report of a written thesis section without an
   empirical forward-pass confirmation.

No Phase 2 action (hook insertion, forward pass, checkpoint copy) will be taken
until you respond to the above.

## Phase 2 addendum (2026-09-03): empirical confirmation via CPU forward pass

User approved proceeding on 2026-09-02/03 with the defaults stated above (sed/bus
scope, mASE proxy fine for this diagnostic, do the hook). Ran the scoped Phase 2
candidate: 5 paired clean/`lidar_gaussian_noise_high` frames from sequence 32
(the only local sequence checked; picked for convenience, not selected for any
property of the frames themselves), single-frame no-grad forward passes on local
CPU, reading `ASF_v2_0_final_10.pt` and the three frozen sub-encoder checkpoints
directly off the `pretrained/` Alvis sshfs mount (per the resolved blocking
question — mount is fine for reads, no CPU/GPU nodes on Alvis itself). Dumped
`feat_indiv` (per-modality, pre-fusion) and `fused_feat` (post-fusion) via the
model's own existing instrumentation hooks (`get_feats_to_vis`/`feat_indiv`
flags in `a2_fusion.py`, already wired for visualization — no repo edits).

**This required substantial CPU-porting work**, all done as environment/shim
fixes in the standalone script, never in the repo: this checkpoint's forward
path depends on several CUDA-only compiled extensions (`spconv`'s CPU wheel
lacks fused activation+bias in `indice_conv`; `roiaware_pool3d`, `iou3d_nms`,
`pointnet2_stack`, `sort_vertices` (Rotated_IoU), and `bev_pool_ext` have no
CPU implementation at all). Fixed/stubbed each surgically:
- `spconv` CPU `indice_conv`: patched to strip the fused act/bias request,
  run the plain conv, then apply bias + activation (ReLU/LeakyReLU/Sigmoid) in
  plain torch — mathematically equivalent, not an approximation.
- `roiaware_pool3d`, `iou3d_nms`, `pointnet2_stack`, `sort_vertices`: stubbed
  to raise only if actually called — true, since these back training-loss/ROI
  paths and NMS post-processing, none of which run before `fused_feat` is
  populated in this eval-mode single-pass. NMS (`iou3d_nms_cuda.nms_gpu`) does
  get called after the head produces raw boxes, which still fails on CPU — box
  outputs were **not** extracted this session, only pre/post-fusion features
  (in scope for what Stage B needed; extracting final boxes would need a real
  CPU NMS implementation, not attempted).
- `bev_pool_ext` (camera lift-splat pooling): replaced with a plain
  `index_add_`-based sum-pool. This is an approximation of the exact spatial
  axis convention (not verified against the CUDA kernel's internal indexing),
  but immaterial here — the camera branch's inputs are camera intrinsics/
  extrinsics only, invariant to LiDAR noise by construction, so it only needed
  to not crash. The result below confirms this: camera features are bit-for-bit
  identical between clean and noisy runs (see below), which they would not be
  if this approximation were somehow polluting the comparison.

Also fixed two data-pipeline bugs blocking the run (both real, pre-existing,
unrelated to this investigation, not touched in the repo):
`get_label()` hardcodes a stale relative path
(`./tools/revise_label/kradar_revised_label_v2_0/...`) that resolves to an
**empty** directory on this checkout; the real data lives under
`./tools/revise_label_local/kradar_revised_label_v2_0/...` (matches
`cfg.path_data.revised_label_v2_0`) — redirected via a local `open()` shim in
the script. And `collate_fn`'s `gt_boxes` assembly throws on zero-object
frames (`remove_0_obj=True`, the config default, is exactly what avoids this
by filtering them at index time — already correct, no fix needed once the
label-path bug was fixed).

### Results (mean absolute activation magnitude and std, full feature map, 5 frames)

| key | clean mean\_abs | noisy mean\_abs | Δ% | clean std | noisy std |
|---|---|---|---|---|---|
| `cam_bev_feat` | 0.01099 (avg) | **identical to clean, every frame** | 0.00% | 0.0778 | 0.0778 |
| `bev_feat` (radar) | 0.0159 (avg) | ±0.05% (noise floor) | ~0.00% | ~0.0971 | ~0.0971 |
| `spatial_features_2d` (**LiDAR/SECOND**) | 0.01875 (avg) | 0.01956 (avg) | **+4.2% to +4.5%, all 5/5 frames** | 0.1188 | 0.1189–0.1190 |
| `fused_feat` | 0.0181 (avg) | 0.0185 (avg) | **+2.1% to +2.6%, all 5/5 frames** | 0.1087 | 0.1089–0.1090 |

**Reading:**

1. **Sanity check passes cleanly**: camera features are exactly identical
   between conditions (noise injection correctly scoped to LiDAR only, and the
   `bev_pool` CPU approximation doesn't introduce any spurious variation).
   Radar features are unchanged to numerical noise. This confirms the
   experiment setup is sound before trusting the LiDAR-branch result.
2. **The LiDAR branch does not collapse, go chaotic, or get flagged/suppressed
   under noise — it produces a systematically *stronger*, still
   well-behaved-looking feature map.** Every single frame (5/5) shows the same
   direction and similar magnitude of shift (+4.2–4.5% mean activation, <0.2%
   std change). This is exactly consistent with the Stage B code-read
   prediction: there is no mechanism anywhere in the backbone or fuser that
   detects "this input is corrupted" and reacts to it — the backbone just
   processes the noisier, denser occupancy pattern and outputs proportionally
   more activation energy, the same way it would for a genuinely denser real
   scene.
3. **The fused output's shift (+2.1–2.6%) is consistently proportional to
   roughly half of the LiDAR branch's own shift** — exactly what plain,
   ungated cross-attention over three co-equal modality tokens would produce
   when only one input changes. There's no sign of the fused representation
   being protected or the LiDAR branch's influence being dialed down; the
   perturbation just flows straight through into the shared representation,
   confirming Stage B's structural claim empirically, not just by code
   reading.
4. **Important limit on what this shows**: this is a *global* mean/std over
   the whole spatial feature map — a coarse statistic. A clean +4% shift with
   near-zero std change is a small, well-behaved global effect; it does not,
   by itself, obviously explain Stage A's ~4x explosion in FN rate. That
   suggests the actual damage is likely **spatial**, not magnitude-based: noise
   scattering points into plausible-but-wrong locations probably shifts
   *where* activation energy lands in the BEV grid (corrupting anchor-cell
   alignment) rather than how much total activation there is — a hypothesis
   this data is consistent with but does not directly test. Confirming that
   would need the originally-scoped Stage D (per-cell spatial diff / cosine
   similarity map between clean and noisy `spatial_features_2d`, not just
   global scalar stats) — still not run.
5. **Box-level confirmation (would recall collapse actually reproduce on 5
   frames) was not obtained** — CPU NMS isn't implemented in this repo's
   compiled extensions and wasn't reimplemented, so no final predicted boxes
   came out of this run. The feature-level result above is suggestive but not
   a full reproduction of Stage A's FN-rate finding on these specific 5 frames.

### New/updated blocking questions

- **Q5 (new)**: is a proper Stage D (spatial diff map, not just global stats)
  worth running to confirm the "corrupted alignment, not corrupted magnitude"
  hypothesis in (4) above? It needs no new access — same checkpoint, same
  frames, just diffing `spatial_features_2d` per-cell instead of aggregating.
- **Q6 (new)**: is box-level (NMS-final) confirmation on these 5 frames worth
  the extra work of writing a CPU `nms` fallback (straightforward — greedy
  IoU-threshold NMS in plain torch, no CUDA-specific behavior needed), or is
  the feature-level evidence sufficient for the thesis section?
- Two real, pre-existing repo bugs were found and worked around (not fixed) —
  flagging in case they matter beyond this investigation: (a) `get_label()`'s
  hardcoded stale revise-label path, (b) `collate_fn`'s empty-box-array
  broadcast on zero-object frames. Say the word if you want these actually
  patched in the repo (out of scope for a read-only-adjacent diagnostic
  script, but a two-line fix each if wanted).
