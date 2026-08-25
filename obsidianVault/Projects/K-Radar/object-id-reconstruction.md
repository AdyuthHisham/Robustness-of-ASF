# Object-ID reconstruction for ASF predictions (2026-08-19)

**Code:** `repos/K-Radar/scripts/alvis/reconstruct_object_ids.py`, `render_recon_review.py`
**Review gallery:** `repos/K-Radar/outputs/object_id_recon/review_gallery/index.html`

## What it does

`all_gts.txt`/`all_preds.txt` carry no object identity — `dict_datum_to_kitti()`
(`utils/util_pipeline.py`) discards it. Traced upstream: `datasets/kradar_fusion_v1_0.py`'s
`collate_fn` names the discarded field `trk_id` — a persistent cross-frame track ID, sourced
from the UWIPL-refined v2.0 label tree. Two-stage read-only reconstruction, both instantiate
the real `KRadarFusion_v1_0(cfg, split='test')` class rather than replaying its
filename/split/class-filter logic by hand (avoids the replication-risk failure mode):

- **Stage A** — rejoins each GT line to its `trk_id` by float-tolerance equality (same source
  values, just rounded/permuted by `dict_datum_to_kitti`).
- **Stage B** — greedy per-class BEV-IoU matching (reusing `utils/kitti_eval/eval.py`) between
  predictions and that frame's `trk_id`-tagged GT. Unmatched preds flagged FP, unmatched GT
  flagged FN — nothing dropped.

Validated on sequence 32 (dry run, both on Alvis and locally — see below): 21/21 frames
indexed correctly, 2/21 unmatched GT, 531 preds / 65 FP / 6 FN at IoU>0.5.

## ⚠️ Known flaw — trk_id matching is not yet trustworthy, needs more work

Confirmed via the review gallery (`fn_32_000019_lidar_loss_complete_zero`): a GT object and a
low-confidence prediction (score 0.43) sat ~1.8m apart in `loc_z` — close enough to plausibly
be the same object, far enough to miss the 0.5 IoU threshold. This is a **near-miss classified
as both FP and FN**, which is defensible under strict IoU matching but means:

- The current FP/FN counts likely overstate true miss/spurious-detection rates whenever a
  detector is *degraded but not absent* — exactly what corruption conditions are expected to
  produce. A softer secondary metric (center-distance fallback, or reporting near-misses
  separately) is probably needed before these counts are used for headline robustness numbers.
- Two GT lines per sequence (seq32: 2/21) fail even the *exact* Stage A rejoin (rounding
  tolerance 5e-3) — rare, but not zero, and not yet root-caused (candidate: revised-label
  rounding edge case, or a genuine duplicate-object situation Stage A's ambiguity check should
  have caught but didn't).
- The review-gallery renders always show the **clean, uncorrupted LiDAR point cloud** as visual
  context, never the actual corrupted sensor input the model saw at inference — so a FN under a
  LiDAR-corruption condition can look like "there was plenty of data, why did it miss" when the
  model actually had zeroed/degraded LiDAR. Don't read gallery point-cloud density as ground
  truth for what the model received.

**Next steps before trusting this for real robustness analysis:** (1) scale past the seq32 dry
run and check if the near-miss/unmatched rates hold across sequences, (2) decide on a
near-miss-aware metric instead of strict binary FP/FN, (3) root-cause the 2 unmatched-GT lines.

## Local (non-Alvis) execution path

Confirmed this pipeline runs off-Alvis given a Python 3.8 venv (`uv python install 3.8.20`;
`torch`/`torchvision`-cpu/`open3d`/`numba`/`opencv` etc. all have working py3.8 wheels) plus
three path workarounds:
- `configs/ASF_v2_0_seq{N}_local.yml` — `/opt/K-Radar/...` container paths rewritten to local.
- `tools/revise_label_local/` — the mounted `tools/revise_label/` only has sequence 1
  extracted; pull other sequences from `kradar_revised_label_v2_0.zip` (all 58 seqs present).
- A staged cwd symlinking `resources/` and `tools/revise_label/.../{seq}` — two hardcoded
  relative paths in `kradar_fusion_v1_0.py` (`./tools/revise_label/...`, `./resources/info_arr.mat`)
  ignore the cfg-driven paths entirely.

This is CPU-only work — the Alvis `--gres=gpu:A40:1` flag in the sbatch scripts is only there
because the `alvis` partition rejects zero-GPU jobs, not because anything here uses a GPU.
