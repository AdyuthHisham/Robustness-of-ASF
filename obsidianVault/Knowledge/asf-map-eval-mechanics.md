# ASF / K-Radar mAP Evaluation Mechanics

How the mAP number reported by the ASF (A2Fusion) sweep is actually computed, traced end-to-end
from a live inference pass through to the final scalar. Complements [[asf-training-inputs]]
(what goes into the model) and [[robustness-metric-selection]] (what's built on top of this AP,
i.e. Rb^c/mRb). Full code-referenced walkthrough is in this session's transcript; key facts below.

## Code path

`pipelines/pipeline_detection_v1_0.py:validate_kitti` → per-conf-threshold KITTI text dump →
`utils/kitti_eval/eval_revised.py:get_official_eval_result_revised` (called via
`do_eval_v3`/`eval_class`/`compute_statistics_jit`). This is a from-scratch reimplementation of
the KITTI devkit's 41-point AP, not the OpenPCDet/mmdet3d one.

## Step 1 — inference → NMS'd boxes (per frame)

`models/head/rdr_spcube_head_multi_cls.py:get_nms_pred_boxes_for_single_sample`:
dense per-cell class softmax + box regression → keep cells where `argmax != background` and
`max_softmax_prob > conf_thr` → decode `(x,y,z,l,w,h,θ)` (θ via atan2 of two regressed
components) → rotated-box NMS. `conf_thr` is swept as a *hard pre-filter* (loop in
`validate_kitti`, separate dump per threshold) — distinct from the 41 PR-curve thresholds
computed later inside the AP calc itself.

## Step 2 — dump to KITTI-format text

`utils/util_pipeline.py:dict_datum_to_kitti`. **The 2D image bbox field is a hardcoded dummy
(`50 50 150 150`) for both GT and predictions** — never derived from real geometry. This means
KITTI's difficulty-tier height/occlusion/truncation filters in `clean_data` are a structural
no-op in this pipeline (height=100 always clears every MIN_HEIGHT threshold), so easy/normal/hard
AP splits collapse to identical results here. Empty predictions get one `dummy -1 -1 0 0...0`
line rather than an empty file — the presence/absence of this line is what the survivorship-bias
ingest bug (see [[asf-corruption-study-alvis]], 2026-08-20 update) hinged on.

## Step 3 — parse back to arrays

`utils/kitti_eval/kitti_common.get_label_annos` re-reads the per-frame text files into
`gt_annos`/`dt_annos` (list of dicts, one per frame: name/bbox/dimensions/location/rotation_y/
score). **This parsed text is the actual input to the AP computation** — not the network, not
raw sensor data.

## Step 4 — TP/FP/FN assignment (per class × difficulty × IoU threshold)

`compute_statistics_jit`: greedy one-to-one matching, one GT box → highest-scoring qualifying
detection with rotated BEV/3D IoU > `min_overlap` (0.3/0.5/0.7 = easy/mod/hard, per-class
matrix). TP = matched pair; FN = unmatched valid GT; FP = unmatched non-ignored detection above
current score cutoff. Class mismatch / dummy lines / (structurally-inert) difficulty filtering →
`ignore`, excluded from all three counts. **Counts are pooled across every frame in the dataset
before computing precision** (`fused_compute_statistics`) — not averaged per-frame. This pooling
is exactly the mechanism the frame_deletion survivorship-bias bug exploited: a condition with
99% missing prediction files shrinks the pool to an easy surviving 1%, looking better than
baseline unless FN rows are synthesized for the missing frames.

## Step 5 — 41-point PR curve → AP → mAP

`get_thresholds`: harvest every TP's score from the whole dataset, pick 41 cutoffs spaced by
recall (not by score). Rerun matching at each cutoff, pool TP/FP/FN dataset-wide →
`precision[i] = TP/(TP+FP)`, then monotonic max from the tail. `AP = mean(41 precision points) *
100` (`get_mAP_v2`) — arithmetic mean, not an integral. `mAP` = whatever the caller averages over
class/difficulty/IoU afterward (repo convention: IoU=0.3, per [[asf-corruption-study-alvis]]'s
2026-08-20 correction to match official K-Radar BEV methodology).
