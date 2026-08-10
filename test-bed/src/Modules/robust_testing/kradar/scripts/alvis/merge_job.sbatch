#!/bin/bash
# scripts/alvis/merge_job.sbatch — submit with:
#   sbatch --dependency=afterok:<array_job_id> scripts/alvis/merge_job.sbatch
# Runs after every array task in the job it depends on has exited 0. Calling
# run_split.py without --sequences processes the full split (58 sequences);
# every sequence's shard already exists from the array job, so each is
# skipped instantly and this just concatenates them into the final Parquet.
#
#SBATCH -A <NAISS_COMPUTE_PROJECT>
#SBATCH -p alvis
#SBATCH -C NOGPU
#SBATCH -c 1
#SBATCH --mem=4G
#SBATCH -t 00:30:00
#SBATCH -o slurm_logs/merge_%j.out
#SBATCH -J kradar_vis_merge

set -euo pipefail

REMOTE_DIR="${REMOTE_DIR:-$HOME/kradar_visibility}"
cd "$REMOTE_DIR"
mkdir -p slurm_logs

source .venv/bin/activate

python scripts/run_split.py \
  --dataset-root /cephyr/users/adyuth/Alvis/Desktop/cephyr_c3se2025-3-18/datasets/kradar \
  --shard-dir /mimer/NOBACKUP/groups/naiss2025-22-321/projects/AMSCUP/kradar_visibility/shards \
  --output /mimer/NOBACKUP/groups/naiss2025-22-321/projects/AMSCUP/kradar_visibility/kradar_test_split_full.parquet
