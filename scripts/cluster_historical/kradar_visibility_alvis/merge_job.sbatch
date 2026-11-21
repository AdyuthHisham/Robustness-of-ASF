#!/bin/bash
# scripts/alvis/merge_job.sbatch — submit with:
#   sbatch --dependency=afterok:<array_job_id> scripts/alvis/merge_job.sbatch
# Runs after every array task in the job it depends on has exited 0. Calling
# run_split.py without --sequences processes the full split (58 sequences);
# every sequence's shard already exists from the array job, so each is
# skipped instantly and this just concatenates them into the final Parquet.
#
#SBATCH -A naiss2026-4-494
#SBATCH -p alvis
#SBATCH --gpus-per-node=A40:1
#SBATCH -c 1
#SBATCH -t 00:30:00
#SBATCH -o slurm_logs/merge_%j.out
#SBATCH -J kradar_vis_merge

set -euo pipefail

BASE_DIR="${BASE_DIR:-/cephyr/NOBACKUP/groups/c3se2025-3-18/users/adyuth/AMSCUP}"
KRADAR_DIR="$BASE_DIR/test-bed/src/Modules/robust_testing/kradar"
cd "$KRADAR_DIR"
mkdir -p slurm_logs

module load uv/0.7.13-GCCcore-14.2.0
# kradar is a uv workspace member of test-bed (see test-bed/pyproject.toml),
# so `uv sync` resolves the shared venv at the workspace root, not here.
source "$BASE_DIR/test-bed/.venv/bin/activate"

python scripts/run_split.py \
  --dataset-root "$BASE_DIR/repos/K-Radar" \
  --shard-dir outputs/shards \
  --output outputs/kradar_test_split_full.parquet
