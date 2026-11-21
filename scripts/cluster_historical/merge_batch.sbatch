#!/bin/bash
#SBATCH -A NAISS2026-4-494
#SBATCH -p alvis
#SBATCH -C NOGPU
#SBATCH -N 1
#SBATCH -c 32
#SBATCH -t 00:30:00
#SBATCH -J merge_batch
#SBATCH -o merge_batch_%j.log
#
# CPU-only merge step for run_batched_sweep.sh -- runs merge_predictions_text.py
# on one of Alvis's NOGPU nodes instead of the login node (which is not meant
# for heavy I/O work, and whose bare python3 is also too old -- 3.6.8, predates
# PEP 563 `from __future__ import annotations` that merge_predictions_text.py
# uses).
#
# Required env vars (set via sbatch --export=ALL,...):
#   PREDS_OUT   path for this batch's merged predictions file
#   GTS_OUT     path for this batch's merged GT file
#   SEQS        comma-separated sequence numbers this batch covers, e.g. "1,2,...,10"
#               -- scopes the merge to exactly this batch (see merge_predictions_text.py's
#               --seqs: without it, any not-yet-deleted raw dumps left over from OTHER
#               sequences/batches get silently folded in too).

set -euo pipefail

: "${PREDS_OUT:?PREDS_OUT must be set}"
: "${GTS_OUT:?GTS_OUT must be set}"
: "${SEQS:?SEQS must be set}"

AM=/cephyr/NOBACKUP/groups/c3se2025-3-18/users/adyuth/AMSCUP/repos/K-Radar
cd "$AM"

module load Python/3.11.3-GCCcore-12.3.0

python3 scripts/alvis/merge_predictions_text.py \
  --outputs-dir outputs \
  --preds-out "$PREDS_OUT" \
  --gts-out "$GTS_OUT" \
  --seqs "$SEQS" \
  --workers 32 \
  --force
