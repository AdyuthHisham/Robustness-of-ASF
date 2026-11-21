# ASF is availability-*told*, not availability-*aware*

Root-cause investigation into a paradox in the corruption sweep: LiDAR fed
Gaussian noise at/above voxel scale degrades ASF far more catastrophically
than LiDAR zeroed out completely, which is the opposite of what an
"availability-aware" architecture should produce (a garbage-but-present
signal should be recoverable-or-worse-than-absent, not enormously worse).
See [[asf-corruption-study-alvis]] and [[robustness-radar-charts]] for the
underlying sweep this was investigated from, and the
[[ASF_KRadar_Adversarial_Review|adversarial review]] this sharpens (critique
#3: robustness tested only via simulated blackout).

## The numbers (pooled, IoU=0.3, clean sed AP=75.55, mAP=69.27)

| Condition | sed AP | mAP retention | mATE | n_TP | net_retention |
|---|---|---|---|---|---|
| `lidar_loss_complete_zero` (sensor absent) | 43.38 | 58.2% | 0.440 | 15,499 | 0.579 |
| `lidar_gaussian_noise_medium` (σ=0.5, ≈ voxel size) | 11.07 | 25.6% | 0.544 | 4,132 | 0.154 |
| `lidar_gaussian_noise_high` (σ=1.0) | 11.23 | 22.7% | 0.520 | 3,431 | 0.128 |

Same qualitative pattern for radar (milder): `radar_loss_complete_zero` 95.8%
retention vs `radar_gaussian_noise_high` 80.3%. Camera shows no asymmetry
either way because camera is marginal to the fusion regardless of input
state (see [[asf-training-inputs]]).

## Root cause, traced in code

ASF's only availability-aware mechanism is `a2_fusion.py:166-173`
(`AwareFuser.forward`): a branch is skipped from the cross-attention query
set iff its key is absent from `batch_dict['avail_feats']` — a plain
membership check, not a learned or content-derived signal.

`avail_feats` is populated in exactly two places, both hand-run
demo/visualization paths, not the eval pipeline:
`main_fusion_eval_0.py`'s `vis_objects()` (line 171) and a conditional-eval
helper (line 740), plus `tools/asf_visualization/main_get_videos.py`. Both
set it from a **fixed, externally-chosen `infer_mode` string** (e.g.
`'rlc'`, `'rl'`) applied uniformly across an entire run — exactly the
paper's own Table 3 methodology (pick a sensor combination up front, evaluate
the whole set under it). It is never derived per-frame and never derived
from sensor content.

**`pipelines/pipeline_detection_v1_0.py`'s `test()`/`validate()` — the
functions the entire 58-sequence corruption sweep actually runs through —
never reference `avail_feats` at all** (confirmed by grep, zero hits). Every
AP number in this repo's sweep, including `*_loss_complete_zero`, runs with
all three branches always present in the fuser's query. `loss_complete_zero`
doesn't hit the `continue` skip above; per `eval_wrapper.py`'s own
docstring, it zero-fills the raw point array pre-voxelization because
"the ASF stack cannot consume `None`... there is no availability mask and no
`None` path" in this code path. The LiDAR encoder still runs on the zeroed
array; the fuser still attends to whatever comes out.

## What this means mechanistically

Neither zero-ablation nor noise-injection in this repo's sweep — nor,
apparently, anything but the paper's own hand-set-`infer_mode` Table 3 runs —
exercises real availability masking. Both are testing how the *ordinary,
always-three-branch* fused attention reacts to a corrupted encoder output;
the difference is only what kind of corruption:

- **All-zero points** → voxelizes to a near-empty/degenerate occupancy grid,
  structurally similar to sparse real scenes (e.g. distant frames) the
  backbone has already learned to weight lightly. Degradation is mild
  because the *shape* of the bad signal resembles a known low-information
  case.
- **Gaussian noise ≥ voxel scale** (σ=0.5-1.0m vs 0.4m voxels) → scatters
  real points into a dense, spatially-plausible-looking but semantically
  wrong occupancy pattern. Nothing in CASAP can distinguish "genuinely dense
  real return" from "noise-scattered garbage that happens to be dense," so
  it gets trusted at full weight, actively injecting wrong spatial
  information into the fused representation instead of being ignored.

Sed/bus asymmetry (sed AP collapses harder than bus at medium/high severity)
is consistent with this: sedans have thinner point support to begin with, so
voxel-scale noise destroys proportionally more of it.

## Why this sharpens the adversarial review's critique #3

Not just "robustness is tested via simulated blackout, not real faults" —
more specifically: **ASF has no failure *detector*, only a failure
*declarer***. The one mechanism for handling a bad sensor requires an
external oracle (a human or an eval harness) to already know which sensor
died and manually exclude it, before any inference happens. A real
automotive fault (miscalibration, partial occlusion, EMI, stuck-at-noise
ADC) doesn't announce itself by vanishing from a config dict — it looks like
`gaussian_noise`, the exact regime this data shows ASF has no defense for.
"Robust under sensor degradation and failure" (the paper's phrasing)
collapses two mechanically opposite outcomes into one word: mild loss under
clean absence (which requires knowing it happened) vs. near-total collapse
under noisy presence (the realistic case). They are not the same claim, and
this repo's own sweep shows only the easier one holds.

## Caveat

This is a code-reading-based mechanistic account (voxel occupancy behavior
under zero vs. noise input), not a direct instrumented measurement of
per-branch attention weights or voxel counts under each condition — a
worthwhile follow-up would be to dump CASAP's attention weights for the
LiDAR branch under `loss_complete_zero` vs `gaussian_noise_high` and confirm
they're both non-negligible (expected, if this account is right) rather than
the noise condition actually being auto-downweighted and something else
explaining the AP collapse.

## Addendum 2026-09-02: independently re-derived, FN breakdown adds the missing piece

Re-ran the Stage A/B split of this same question from scratch (fresh Phase 1 audit,
`row_table_iou03.parquet` post frame-key-fix) without first reading this note —
landed on the exact same `a2_fusion.py:168-173` mechanism and the same
`infer_mode`/`avail_feats` code path independently, which is a good cross-check.
New pieces this pass adds:

- **Failure-mode breakdown**: the AP collapse under `lidar_gaussian_noise_{medium,high}`
  is almost entirely FN-driven, not localization- or FP-driven. FN rate: sed
  22%→85%→86%, bus 29%→70%→75% (clean→medium→high). FP rate is flat or *drops*
  slightly (no hallucination surge). mATE on survivors worsens only ~40-45%
  (nowhere near enough to explain the AP collapse alone). Predicted-object volume
  itself collapses (sed preds 26,761→5,337, -80%) — the detection head is simply
  firing far less, consistent with "noise-scattered occupancy gets attended to at
  full weight and actively corrupts the fused representation" rather than "objects
  get detected but placed worse." mATE/FN numbers here are per-class on the
  frame-key-corrected table and don't exactly match the pooled clean-AP=75.55
  figures above — expected, different table vintage — but the qualitative pattern
  (small mATE shift, dominant FN swing) is the reinforcing new fact.
- **Checkpoint/mount finding, worth flagging separately**: `repos/K-Radar/pretrained/`
  (where `ASF_v2_0_final_10.pt` lives) is itself a read-only `sshfs` mount to
  `alvis2.c3se.chalmers.se`, same as `repos/K-Radar/data`. Unlike `data` (which hung
  on traversal), `pretrained` was actually reachable and readable (`dd`'d 20MB in
  ~1.6s) during this session — meaning the checkpoint isn't genuinely local either,
  it just happens to still be served over a live mount. Contradicts the strong form
  of [[project_alvis_permanently_unavailable]] for passive file access specifically
  (compute/sbatch is still assumed dead) — worth copying the checkpoint to true
  local disk before any Phase 2 forward-pass work depends on it staying reachable.

Full writeup: `docs/vAIlt/06_Results/lidar-gaussian-noise-mechanism-phase1-audit-20260902.md`.

## Addendum 2026-09-03: empirically confirmed via CPU forward pass (5 frames, seq 32)

Ran the Phase 2 candidate scoped above — actual forward passes (no grad, CPU,
reading the checkpoint off the `pretrained/` Alvis mount), dumping `feat_indiv`/
`fused_feat` clean vs `lidar_gaussian_noise_high`. Required substantial CPU-porting
(spconv's CPU `indice_conv` lacks fused act+bias, several CUDA-only ops
stubbed/reimplemented — see the audit doc's Phase 2 addendum for the full list),
all done in a standalone script, no repo edits.

**Result, 5/5 frames, fully consistent**: camera features identical
clean-vs-noisy (sanity check — camera is LiDAR-noise-invariant by construction,
confirms setup is sound); radar features unchanged to numerical noise;
`spatial_features_2d` (LiDAR/SECOND) shows a small, consistent **+4.2–4.5%**
increase in mean activation magnitude with std essentially unchanged (no chaos,
no collapse — a systematically *stronger*, still well-behaved feature map);
`fused_feat` shows **+2.1–2.6%**, roughly half the LiDAR shift — exactly what
plain ungated cross-attention over 3 co-equal tokens produces when only one
input changes. Empirically confirms the code-read claim: nothing anywhere
detects the corrupted input or dials down its influence.

**Caveat that matters**: this is a coarse global mean/std, and a clean +4%
shift doesn't obviously explain Stage A's ~4x FN-rate explosion by itself — the
real damage is more likely spatial (noise-scattered points shifting *where*
activation lands in the BEV grid, misaligning anchor cells) than magnitude-based.
A per-cell spatial diff map (scoped, not run) would confirm this directly.
Box-level (post-NMS) confirmation also not obtained — CPU NMS isn't implemented
here and wasn't added.
