#!/bin/bash
# scripts/alvis/array_job.sbatch — one SLURM array task per K-Radar sequence.
# Each task processes its sequence's test-split frames (bundled split file,
# resources/split/test.txt) to its own Parquet shard on Mimer. Resumable:
# rerunning skips any sequence whose shard already exists.
#
# Fill in / verify before submitting (see docs/ALVIS_MIGRATION_PLAN.md §9):
#   - #SBATCH -A          : NAISS/C3SE compute project (not yet known)
#   - REMOTE_DIR           : where push_to_alvis.sh deployed this subproject
#   - -c / --workers        : tune after the first few tasks report real timing
#
#SBATCH -A <NAISS_COMPUTE_PROJECT>
#SBATCH -p alvis
#SBATCH -C NOGPU
#SBATCH -c 16
#SBATCH --mem=8G
#SBATCH -t 08:00:00
#SBATCH --array=1-58%12
#SBATCH -o slurm_logs/array_%A_%a.out
#SBATCH -J kradar_vis_split

set -euo pipefail

REMOTE_DIR="${REMOTE_DIR:-$HOME/kradar_visibility}"
cd "$REMOTE_DIR"
mkdir -p slurm_logs

source .venv/bin/activate

SEQ="$SLURM_ARRAY_TASK_ID"

python scripts/run_split.py \
  --sequences "$SEQ" \
  --dataset-root /cephyr/users/adyuth/Alvis/Desktop/cephyr_c3se2025-3-18/datasets/kradar \
  --workers 16 \
  --shard-dir /mimer/NOBACKUP/groups/naiss2025-22-321/projects/AMSCUP/kradar_visibility/shards \
  --skip-merge
