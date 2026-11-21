#!/bin/bash
# scripts/alvis/regen_sedan_bus.sbatch — one SLURM array task per K-Radar
# sequence, running run_all_sequences.py's Sedan/"Bus or Truck" filtered
# regen for that single sequence to its own shard. Resumable: rerunning
# skips a sequence whose shard already exists (see SKIP check below).
#
# After all array tasks finish, run scripts/alvis/merge_shards.py once to
# concatenate shards into the final output/output_with_env_density.parquet.
#
#SBATCH -A naiss2026-4-494
#SBATCH -p alvis
#SBATCH --gpus-per-node=A40:1
#SBATCH -c 16
#SBATCH -t 04:00:00
#SBATCH --array=1-58%12
#SBATCH -o slurm_logs/regen_sedan_bus_%A_%a.out
#SBATCH -J kradar_vis_sedan_bus

set -euo pipefail

BASE_DIR="${BASE_DIR:-/cephyr/NOBACKUP/groups/c3se2025-3-18/users/adyuth/AMSCUP}"
KRADAR_DIR="$BASE_DIR/test-bed/src/Modules/robust_testing/kradar"
cd "$KRADAR_DIR"
mkdir -p slurm_logs outputs/shards_sedan_bus

module load uv/0.7.13-GCCcore-14.2.0
source "$BASE_DIR/test-bed/.venv/bin/activate"

SEQ="$SLURM_ARRAY_TASK_ID"
SHARD="outputs/shards_sedan_bus/seq_${SEQ}.parquet"

if [ -f "$SHARD" ]; then
  echo "Shard $SHARD already exists, skipping sequence $SEQ."
  exit 0
fi

export KRADAR_DATASET_ROOT="$BASE_DIR/repos/K-Radar"

python scripts/run_all_sequences.py \
  --sequences "$SEQ" \
  --workers 16 \
  --output "$SHARD" \
  --dataset-root "$KRADAR_DATASET_ROOT"
