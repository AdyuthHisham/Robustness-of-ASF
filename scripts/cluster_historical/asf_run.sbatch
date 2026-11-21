#!/bin/bash
#SBATCH -A NAISS2026-4-494
#SBATCH -p alvis
#SBATCH -N 1
#SBATCH --gpus-per-node=A40:1
#SBATCH -t 01:30:00
#SBATCH -J asf_run
#SBATCH -o asf_run_%j.log
#
# NOTE: #SBATCH directives are parsed before SEQ/OUT_NAME are known, so -J/-o
# are generic here. submit_run.sh passes --job-name/-o with the real
# sequence+condition name via the sbatch CLI, which override these.

# ASF (A2Fusion, tri-modal) original-vs-corrupted run on a full K-Radar
# sequence on Alvis. Sequence-generic: SEQ selects both the dataset config
# (configs/ASF_v2_0_seq${SEQ}_alvis.yml) and the output tree
# (outputs/alvis_seq${SEQ}/$OUT_NAME). Generalized from asf_seq46.sbatch,
# which stays in place, untouched, as the record of the sequence-46 pilot.
#
# One job = one (sequence, condition) pair, selected entirely by the env
# vars below.
#
# Required env vars (set by submit_run.sh, or export before `sbatch --export=...`):
#   SEQ               sequence number, e.g. 46 or 1 -- must have a matching
#                      configs/ASF_v2_0_seq${SEQ}_alvis.yml
#   OUT_NAME          result subdir name, e.g. original / camera_gaussian_noise_high
# Optional:
#   NOISE_CFG         noise YAML under configs/noise/, e.g. single/camera_gaussian_noise_high.yml
#                      (omit/empty for the original/baseline run)
#   BLACKOUT_POLICY   empty (default) | zero_feature | last_frame_hold
#                      only meaningful when NOISE_CFG sets a blackout effect
#
# Carries the three Alvis fixes proven on the full 17.5k-frame ASF run (see
# scripts/main_cond_0_args.py / utils/kitti_eval/eval.py history): no eager
# GPU-NMS import at startup, CPU rotated-IoU fallback, KITTI split clamped for
# small N.

set -e

: "${SEQ:?SEQ must be set (see scripts/alvis/submit_run.sh)}"
: "${OUT_NAME:?OUT_NAME must be set (see scripts/alvis/submit_run.sh)}"
NOISE_CFG="${NOISE_CFG:-}"
BLACKOUT_POLICY="${BLACKOUT_POLICY:-empty}"

AM=/cephyr/NOBACKUP/groups/c3se2025-3-18/users/adyuth/AMSCUP/repos/K-Radar
SIF=/mimer/NOBACKUP/groups/naiss2025-22-321/users/adyuth/containers/kradarV0.sif

KRADAR_DATA=/cephyr/NOBACKUP/groups/c3se2025-3-18/datasets/kradar
PRE=/cephyr/NOBACKUP/groups/c3se2025-3-18/datasets/kradar_pre/processed
TRAINED=/cephyr/NOBACKUP/groups/c3se2025-3-18/datasets/kradar_pre/trained

# Defaults to the OFFICIAL published ASF v2.0 checkpoint (matches the
# label_version: v2_0 / KRadar_refined_label_by_UWIPL labels already baked
# into these per-sequence configs -- see docs/sensor_fusion.md's Benchmark
# v2.0 row). The self-trained checkpoint used by the first corruption sweep
# (exp_260506_135737_A2FUSION_.../models/model_10.pt, MD5 805ac29a...,
# undocumented provenance, does NOT match docs/sensor_fusion.md's published
# numbers) is still reachable via MODEL_CKPT=... if ever needed again.
CKPT="${MODEL_CKPT:-$AM/pretrained/ASF_v2_0_final_10.pt}"
CONFIG=./configs/ASF_v2_0_seq${SEQ}_alvis.yml

if [ ! -f "$CKPT" ]; then
  echo "FATAL: $CKPT does not exist -- no checkpoint at MODEL_CKPT/default path" >&2
  exit 1
fi

if [ ! -f "$AM/$CONFIG" ]; then
  echo "FATAL: $AM/$CONFIG does not exist -- no dataset config for sequence $SEQ" >&2
  exit 1
fi

OUT=$AM/outputs/alvis_seq${SEQ}/$OUT_NAME
mkdir -p "$OUT"
export TMPDIR=$OUT/tmp
mkdir -p "$TMPDIR"

# Overlay only the fixed/new files over the baked repo (keeps the baked v2_0 labels).
BINDS=""
BINDS="$BINDS,$AM/scripts/main_cond_0_args.py:/opt/K-Radar/scripts/main_cond_0_args.py"
# Gap found 2026-08-26: this file was NEVER bind-mounted, so every run up to
# and including the full 58-sequence 'original' baseline silently used the
# container's stale baked-in copy (positional zfill(6) idx_name), completely
# no-op'ing this session's frame-identifier fix (idx_name = f"{rdr}-{ldr64}").
# Does not corrupt AP/TP/FP correctness (matching stays internally consistent
# per index either way) but does corrupt per-frame identity/cross-referencing.
BINDS="$BINDS,$AM/pipelines/pipeline_detection_v1_0.py:/opt/K-Radar/pipelines/pipeline_detection_v1_0.py"
BINDS="$BINDS,$AM/datasets/kradar_fusion_v1_0.py:/opt/K-Radar/datasets/kradar_fusion_v1_0.py"
BINDS="$BINDS,$AM/datasets/effects:/opt/K-Radar/datasets/effects"
BINDS="$BINDS,$AM/$CONFIG:/opt/K-Radar/$CONFIG"
BINDS="$BINDS,$AM/configs/noise:/opt/K-Radar/configs/noise"
BINDS="$BINDS,$AM/utils/kitti_eval/eval.py:/opt/K-Radar/utils/kitti_eval/eval.py"
BINDS="$BINDS,$AM/utils/kitti_eval/eval_revised.py:/opt/K-Radar/utils/kitti_eval/eval_revised.py"
BINDS="$BINDS,$AM/utils/kitti_eval/rotate_iou_cpu.py:/opt/K-Radar/utils/kitti_eval/rotate_iou_cpu.py"
BINDS="$BINDS,$KRADAR_DATA:/opt/K-Radar/kradar_dataset"
BINDS="$BINDS,$PRE/processed_lpc_calib_roi:/opt/K-Radar/pre_processed/processed_lpc_calib_roi"
BINDS="$BINDS,$PRE/rdr_sparse_data:/opt/K-Radar/pre_processed/rdr_sparse_data"
BINDS="$BINDS,$PRE/kradar_imgs:/opt/K-Radar/pre_processed/kradar_imgs"
BINDS="$BINDS,$TRAINED/CAMERA_MODEL_10.pt:/opt/K-Radar/pretrained/CAMERA_MODEL_10.pt"
BINDS="$BINDS,$TRAINED/SECOND_10.pt:/opt/K-Radar/pretrained/SECOND_10.pt"
BINDS="$BINDS,$TRAINED/RTNH_wide_10.pt:/opt/K-Radar/pretrained/RTNH_wide_10.pt"
BINDS="$BINDS,$CKPT:/opt/K-Radar/run_ckpt.pt"
BINDS="$BINDS,$OUT:/opt/K-Radar/logs"
BINDS="${BINDS#,}"

NOISE_ARGS=""
if [ -n "$NOISE_CFG" ]; then
  # Sensor dumps land next to the predictions. --dump-meta-only: at full-sequence
  # x 58-sequence x 29-condition scale, writing every frame's actual sensor
  # arrays (.npy/.png) would be a real disk-space risk -- only the per-frame
  # meta.txt (changed=True/False per modality, frame/seq/sensor indices) is
  # kept. Drop this flag for a small ad hoc run where you want the full
  # arrays for a gallery (e.g. the earlier 10-sequence test, or build_seq_gallery.py).
  NOISE_ARGS="--noise-config /opt/K-Radar/configs/noise/$NOISE_CFG"
  NOISE_ARGS="$NOISE_ARGS --blackout-policy $BLACKOUT_POLICY"
  NOISE_ARGS="$NOISE_ARGS --dump-sensors /opt/K-Radar/logs/sensor_dump"
  NOISE_ARGS="$NOISE_ARGS --dump-meta-only"
fi

echo "=== sequence: $SEQ  condition: $OUT_NAME  noise-config: ${NOISE_CFG:-<none, original run>}  blackout-policy: $BLACKOUT_POLICY ==="

# Run manifest: written before inference so it exists even if the job aborts.
# Records what this run actually is, independent of stdout log parsing.
GIT_SHA=$(cd "$AM" && git rev-parse HEAD)
NOISE_CFG_CONTENT="null"
if [ -n "$NOISE_CFG" ] && [ -f "$AM/configs/noise/$NOISE_CFG" ]; then
  NOISE_CFG_CONTENT=$(python3 -c "
import json, sys
try:
    import yaml
    print(json.dumps(yaml.safe_load(open('$AM/configs/noise/$NOISE_CFG'))))
except Exception as e:
    print(json.dumps({'error': str(e)}))
" 2>/dev/null || echo "null")
fi
cat > "$OUT/run_manifest.json" <<MANIFEST
{
  "out_name": "$OUT_NAME",
  "sequence": "$SEQ",
  "config": "$CONFIG",
  "noise_config_path": "${NOISE_CFG:-null}",
  "noise_config_content": $NOISE_CFG_CONTENT,
  "blackout_policy": "$BLACKOUT_POLICY",
  "checkpoint": "$CKPT",
  "git_sha": "$GIT_SHA",
  "slurm_job_id": "${SLURM_JOB_ID:-unknown}",
  "submitted_at_utc": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
MANIFEST
echo "--- run manifest written: $OUT/run_manifest.json ---"
cat "$OUT/run_manifest.json"

cd "$AM"
# The inference + dump finish first; the process can still abort with a
# "free(): invalid pointer" during teardown (a tensorboard/torch cleanup
# segfault on exit), which happens after the preds are on disk -- that alone
# should not fail the job.
#
# BUT (found 2026-08-25, camera_frame_deletion_new sweep): a real Python
# exception mid-run (e.g. collate_fn choking on a None camera tensor) also
# produces a nonzero exit + a "free(): invalid pointer" abort during the
# crash unwind, and previously this script could not tell the two apart --
# it judged success purely on "any predictions written at all", so a run
# that crashed after processing only the first few batches was reported
# "ASF run OK" with a silently truncated prediction set. Some conditions
# (radar/lidar frame_deletion at high severity, both loss_complete_zero
# variants) ARE expected to abort the model in the sparse-conv backbone on
# zero-point input -- that's still a legitimate result, but it must be
# reported as a crash with a partial count, not silently folded into "OK".
#
# Fix: capture the container's own exit code (via PIPESTATUS, since output
# is teed) and grep the captured output for a real Python "Traceback" --
# the benign post-completion teardown segfault has no Python traceback
# (segfaults during interpreter teardown, not during a Python frame), so
# this reliably distinguishes "crashed mid-run, exception in Python code"
# from "finished the loop, then hit the known-benign teardown segfault".
RUN_LOG="$OUT/run_stdout.log"
set +e
apptainer exec --nv --bind "$BINDS" "$SIF" bash -c "
  cd /opt/K-Radar
  export PYTHONPATH=/opt/K-Radar:\$PYTHONPATH
  export TMPDIR=/opt/K-Radar/logs/tmp
  mkdir -p \$TMPDIR
  # Do NOT set KRADAR_EVAL_GPU_IOU=1: that opts into a numba @cuda.jit
  # rotated-IoU kernel in nms_gpu.py which SIGSEGVs on driver mismatch
  # (see utils/kitti_eval/eval_revised.py:13-19). Leave unset -> CPU fallback.
  python scripts/main_cond_0_args.py \
    --config $CONFIG \
    --model /opt/K-Radar/run_ckpt.pt \
    --conf_thr 0.3 \
    $NOISE_ARGS
" 2>&1 | tee "$RUN_LOG"
APPTAINER_RC=${PIPESTATUS[0]}
set -e

echo '--- prediction files written ---'
NPRED=$(find "$OUT" -path '*all/preds/*.txt' | wc -l)
echo "--- count: $NPRED (no baked-in expectation -- sequence $SEQ's post-filter frame count is read from this number, not assumed) ---"
echo "--- sensor dump: $(find "$OUT/sensor_dump" -type f 2>/dev/null | wc -l) file(s) ---"
echo '--- AP results ---'
find "$OUT" -name 'complete_results.txt' -exec echo {} \; -exec cat {} \;

MIDRUN_CRASH=0
if [ "$APPTAINER_RC" -ne 0 ] && grep -q "Traceback (most recent call last)" "$RUN_LOG"; then
  MIDRUN_CRASH=1
fi

if [ "$MIDRUN_CRASH" -eq 1 ]; then
  echo "ASF run CRASHED (seq $SEQ, $OUT_NAME): mid-run Python exception (container exit=$APPTAINER_RC), only $NPRED partial prediction files written before abort -- NOT a complete sequence, do not treat as OK."
  exit 1
elif [ "$NPRED" -gt 0 ]; then
  echo "ASF run OK (seq $SEQ, $OUT_NAME): $NPRED prediction files written."
  exit 0
else
  echo "ASF run FAILED (seq $SEQ, $OUT_NAME): no predictions written."
  exit 1
fi
