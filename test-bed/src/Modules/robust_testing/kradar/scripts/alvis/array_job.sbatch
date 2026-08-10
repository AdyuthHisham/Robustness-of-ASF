#!/bin/bash
# scripts/alvis/array_job.sbatch — one SLURM array task per K-Radar sequence.
# Each task processes its sequence's test-split frames (bundled split file,
# resources/split/test.txt) to its own Parquet shard. Resumable: rerunning
# skips any sequence whose shard already exists.
#
# Deployment: this repo is deployed via git clone to
#   /cephyr/NOBACKUP/groups/c3se2025-3-18/users/adyuth/AMSCUP
# --dataset-root points at repos/K-Radar, which has data/, preprocessed/,
# pretrained/, revise_label/ symlinked in to the real dataset locations
# (/cephyr/NOBACKUP/groups/c3se2025-3-18/datasets/kradar and kradar_pre/,
# and the Mimer refined-label path) — this makes the on-cluster layout
# identical to local dev, just with DATASET_ROOT overridden via --dataset-root
# since config.py's default is hardcoded to the local dev machine's path.
#
# Fill in / verify before submitting (see docs/ALVIS_MIGRATION_PLAN.md):
#   - #SBATCH -A          : naiss2026-4-494 (confirmed via sacctmgr)
#   - -c / --workers        : tune after the first few tasks report real timing
#
#SBATCH -A naiss2026-4-494
#SBATCH -p alvis
#SBATCH -C NOGPU
#SBATCH -c 16
#SBATCH --mem=8G
#SBATCH -t 08:00:00
#SBATCH --array=1-58%12
#SBATCH -o slurm_logs/array_%A_%a.out
#SBATCH -J kradar_vis_split

set -euo pipefail

BASE_DIR="${BASE_DIR:-/cephyr/NOBACKUP/groups/c3se2025-3-18/users/adyuth/AMSCUP}"
KRADAR_DIR="$BASE_DIR/test-bed/src/Modules/robust_testing/kradar"
cd "$KRADAR_DIR"
mkdir -p slurm_logs outputs/shards

module load uv/0.7.13-GCCcore-14.2.0
source .venv/bin/activate

SEQ="$SLURM_ARRAY_TASK_ID"

python scripts/run_split.py \
  --sequences "$SEQ" \
  --dataset-root "$BASE_DIR/repos/K-Radar" \
  --workers 16 \
  --shard-dir outputs/shards \
  --skip-merge
