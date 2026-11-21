#!/bin/bash
# Scripted driver for the ASF v2.0 corruption sweep, batched by sequence to
# avoid repeating the quota crisis from the first (self-trained-checkpoint)
# sweep: Alvis enforces a per-project FILE COUNT quota, and raw per-frame
# test_kitti/ dumps at 58 sequences x 34 conditions blew well past it,
# silently truncating 8 in-flight jobs before anyone noticed.
#
# Previously this batching (submit ~10 sequences, poll sacct, merge, delete
# raw dumps, repeat) was done BY HAND. This script automates it, and fixes a
# subtlety the manual process didn't have to deal with: merge_predictions_text.py
# is NOT incremental -- it rescans the entire outputs/ tree every time and
# only refuses to shrink the existing output file. If a batch's raw dumps are
# deleted before the *next* batch's merge call, that next call would only see
# the new batch's dumps and get correctly blocked by the shrink-guard -- it
# can never "add on to" data whose raw source is already gone. So each batch
# is first merged into its OWN output file (outputs/batches/all_{preds,gts}_batch<N>.txt,
# kept permanently as a per-batch artifact), which is then APPENDED onto the
# cumulative outputs/all_preds.txt/all_gts.txt -- only after that append
# succeeds are that batch's raw test_kitti/ dumps deleted. Batches never
# overlap in sequence number, so a plain append is safe (no cross-batch GT
# dedup needed -- merge_predictions_text.py already dedups within a batch).
#
# Re-running this script over a range that was already swept will double the
# cumulative files (append, not idempotent) -- delete outputs/all_preds.txt /
# outputs/all_gts.txt first if you intend a clean full restart from batch 1.
#
# Usage:
#   bash scripts/alvis/run_batched_sweep.sh <start_seq> <end_seq> [batch_size]
#
# Example (full sweep, default batch size 10):
#   bash scripts/alvis/run_batched_sweep.sh 1 58
#
# Example (dry run on a small range before trusting the full sweep):
#   bash scripts/alvis/run_batched_sweep.sh 1 2 2
#
# Requires: scripts/alvis/submit_run.sh, scripts/alvis/asf_run.sbatch (this
# session's checkpoint fix already applied -- defaults to the official
# ASF_v2_0_final_10.pt), scripts/alvis/merge_predictions_text.py.
#
# Run the single-sequence 'original' smoke test FIRST (see submit_run.sh) and
# confirm predictions + a sane mAP before running this at any scale -- this
# script has no smoke-test step of its own, by design, so a broken checkpoint
# or config doesn't get discovered only after burning a whole batch's GPU-hours.

set -euo pipefail

# The Alvis login node's bare `python3` is 3.6.8, which predates PEP 563
# (`from __future__ import annotations`, used by merge_predictions_text.py)
# and fails with "SyntaxError: future feature annotations is not defined".
# Per Alvis policy, no host-level pip/conda installs -- load a real Python via
# the module system instead. merge_predictions_text.py is pure stdlib
# (argparse/glob/os/concurrent.futures), so any modern version works.
module load Python/3.11.3-GCCcore-12.3.0 >/dev/null 2>&1 || true
if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 7) else 1)'; then
  echo "FATAL: python3 is still < 3.7 after 'module load Python/3.11.3-GCCcore-12.3.0'" >&2
  echo "(module load failed or the module name changed) -- merge_predictions_text.py needs 3.7+." >&2
  exit 1
fi

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/../.." && pwd)"
SUBMIT="$HERE/submit_run.sh"
MERGE="$HERE/merge_predictions_text.py"
BATCH_DIR="$REPO_ROOT/outputs/batches"
POLL_INTERVAL_S=60

START_SEQ="${1:-}"
END_SEQ="${2:-}"
BATCH_SIZE="${3:-10}"

if [ -z "$START_SEQ" ] || [ -z "$END_SEQ" ]; then
  echo "Usage: $0 <start_seq> <end_seq> [batch_size=10]" >&2
  exit 1
fi

mkdir -p "$BATCH_DIR"

if [ -e "$REPO_ROOT/outputs/all_preds.txt" ] || [ -e "$REPO_ROOT/outputs/all_gts.txt" ]; then
  echo "FATAL: outputs/all_preds.txt and/or outputs/all_gts.txt already exist." >&2
  echo "This script always APPENDS each batch onto them -- re-running over an" >&2
  echo "already-swept range would double-count. Move or delete both files first" >&2
  echo "if you intend a clean full restart from batch 1." >&2
  exit 1
fi

# --- helpers -----------------------------------------------------------

# Submit original + full sweep for one sequence; echoes submitted job IDs
# (one per line) to stdout.
submit_sequence() {
  local seq="$1"
  local orig_out orig_id
  orig_out=$(bash "$SUBMIT" "$seq" original)
  orig_id=$(echo "$orig_out" | grep -oE 'Submitted batch job [0-9]+' | grep -oE '[0-9]+$')
  echo "$orig_id"

  local sweep_out
  sweep_out=$(bash "$SUBMIT" "$seq" sweep --confirmed)
  echo "$sweep_out" | grep -oE 'Submitted batch job [0-9]+' | grep -oE '[0-9]+$'
}

# Blocks until every job id passed (space-separated arg) is in a terminal
# sacct state. Prints periodic status.
wait_for_jobs() {
  local job_ids="$1"
  echo "Waiting on jobs: $job_ids"
  while true; do
    local pending=0
    for jid in $job_ids; do
      local state
      state=$(sacct -j "$jid" --format=State --noheader -X 2>/dev/null | head -1 | tr -d ' ')
      case "$state" in
        COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL) ;;
        *) pending=$((pending + 1)) ;;
      esac
    done
    if [ "$pending" -eq 0 ]; then
      echo "All jobs in batch reached a terminal state."
      break
    fi
    echo "  $pending job(s) still running/pending, sleeping ${POLL_INTERVAL_S}s..."
    sleep "$POLL_INTERVAL_S"
  done
}

# Checks every job id for a MIDRUN_CRASH by grepping its sbatch log for the
# Traceback marker (asf_run.sbatch already writes run_stdout.log per
# sequence/condition and distinguishes real crashes from the benign teardown
# segfault -- but that logic runs on the job's OWN log, not something sacct
# reports. Here we just fail loudly if we find the marker anywhere in this
# batch's sequences' run_stdout.log files. Coarser than per-job, but
# sufficient to gate whether it's safe to delete raw dumps.
check_batch_crashes() {
  local seqs="$1"
  local crashed=0
  for seq in $seqs; do
    while IFS= read -r log; do
      if grep -q "Traceback (most recent call last)" "$log"; then
        # Only a crash if the job's own exit also reported CRASHED --
        # cross-check against the "ASF run CRASHED" summary line asf_run.sbatch
        # prints at the end, not just presence of *a* traceback anywhere.
        if grep -q "ASF run CRASHED" "$log"; then
          echo "CRASH detected: $log"
          crashed=1
        fi
      fi
    done < <(find "$REPO_ROOT/outputs/alvis_seq${seq}" -name run_stdout.log 2>/dev/null)
  done
  echo "$crashed"
}

# --- main loop -----------------------------------------------------------

batch_num=0
seq=$START_SEQ
while [ "$seq" -le "$END_SEQ" ]; do
  batch_num=$((batch_num + 1))
  batch_start=$seq
  batch_end=$((seq + BATCH_SIZE - 1))
  if [ "$batch_end" -gt "$END_SEQ" ]; then
    batch_end=$END_SEQ
  fi
  batch_seqs=$(seq "$batch_start" "$batch_end")

  echo "=== Batch $batch_num: sequences $batch_start-$batch_end ==="

  all_job_ids=""
  for s in $batch_seqs; do
    ids=$(submit_sequence "$s")
    all_job_ids="$all_job_ids $ids"
  done

  wait_for_jobs "$all_job_ids"

  crashed=$(check_batch_crashes "$batch_seqs")
  if [ "$crashed" -eq 1 ]; then
    echo "FATAL: batch $batch_num (sequences $batch_start-$batch_end) had a mid-run crash." >&2
    echo "Not merging or deleting raw dumps for this batch -- inspect run_stdout.log files under" >&2
    echo "outputs/alvis_seq{$batch_start..$batch_end}/*/exp_*/run_stdout.log before re-running." >&2
    exit 1
  fi

  # Batch-scoped merge -- see header comment for why this can't target the
  # final all_preds.txt/all_gts.txt directly. Runs as a CPU-only Slurm job
  # (merge_batch.sbatch, -C NOGPU) rather than on the login node: heavy I/O
  # across dozens of sequence dirs doesn't belong on the login node, and its
  # bare python3 (3.6.8) can't run this script anyway. --seqs scopes the scan
  # to exactly this batch's sequences, so any not-yet-deleted raw dumps left
  # over from other sequences/batches don't get silently folded in.
  preds_batch="$BATCH_DIR/all_preds_batch${batch_num}.txt"
  gts_batch="$BATCH_DIR/all_gts_batch${batch_num}.txt"
  # '+' delimiter, NOT comma: SEQS is passed through `sbatch --export`, whose
  # OWN syntax uses commas to separate NAME=VALUE pairs -- a comma-separated
  # value here gets silently truncated at the first comma by sbatch itself.
  # This exact bug caused a real data-loss incident on 2026-08-26: the merge
  # silently processed only sequence 1 of a 10-sequence batch, and this
  # script deleted all 10 sequences' raw dumps believing the merge had
  # covered all of them. merge_predictions_text.py now refuses outright if
  # --seqs contains a comma, as a second line of defense.
  n_batch_seqs=$(echo "$batch_seqs" | wc -l)
  seqs_plus=$(echo "$batch_seqs" | paste -sd+)
  echo "Submitting merge job for batch $batch_num (seqs $seqs_plus) -> $preds_batch / $gts_batch"
  merge_sbatch_out=$(sbatch \
    --job-name="merge_batch${batch_num}" \
    --output="merge_batch${batch_num}_%j.log" \
    --export="ALL,PREDS_OUT=${preds_batch},GTS_OUT=${gts_batch},SEQS=${seqs_plus}" \
    "$HERE/merge_batch.sbatch")
  merge_job_id=$(echo "$merge_sbatch_out" | grep -oE 'Submitted batch job [0-9]+' | grep -oE '[0-9]+$')
  wait_for_jobs "$merge_job_id"

  merge_state=$(sacct -j "$merge_job_id" --format=State --noheader -X 2>/dev/null | head -1 | tr -d ' ')
  merge_log="merge_batch${batch_num}_${merge_job_id}.log"
  if [ "$merge_state" != "COMPLETED" ]; then
    echo "FATAL: merge job $merge_job_id for batch $batch_num ended in state $merge_state, not COMPLETED." >&2
    echo "Not appending or deleting raw dumps for this batch -- inspect $merge_log" >&2
    exit 1
  fi

  if [ ! -s "$preds_batch" ]; then
    echo "FATAL: batch $batch_num merge produced an empty $preds_batch -- refusing to delete raw dumps." >&2
    exit 1
  fi

  # Hard gate, independent of merge_predictions_text.py's own comma-refusal:
  # confirm the merge log actually reports processing every sequence in this
  # batch before any raw dump is deleted. "Found N sequence directories"
  # must equal the batch's sequence count exactly.
  found_line=$(grep -oE '^Found [0-9]+ sequence directories' "$REPO_ROOT/$merge_log" || true)
  found_n=$(echo "$found_line" | grep -oE '[0-9]+' | head -1)
  if [ -z "$found_n" ] || [ "$found_n" -ne "$n_batch_seqs" ]; then
    echo "FATAL: merge log $merge_log reports '$found_line' but this batch has $n_batch_seqs sequences." >&2
    echo "Refusing to append or delete raw dumps -- the merge did not cover the full batch." >&2
    exit 1
  fi

  echo "Appending batch $batch_num into outputs/all_preds.txt / outputs/all_gts.txt"
  cat "$preds_batch" >> "$REPO_ROOT/outputs/all_preds.txt"
  cat "$gts_batch" >> "$REPO_ROOT/outputs/all_gts.txt"

  echo "Deleting raw test_kitti/ dumps for sequences $batch_start-$batch_end"
  for s in $batch_seqs; do
    find "$REPO_ROOT/outputs/alvis_seq${s}" -type d -name test_kitti -exec rm -rf {} +
  done

  echo "=== Batch $batch_num complete ==="
  seq=$((batch_end + 1))
done

echo "All batches complete. outputs/all_preds.txt / outputs/all_gts.txt built incrementally, one append per batch."
echo "Per-batch files kept under $BATCH_DIR as the durable intermediate artifact."
echo "Next: python scripts/alvis/ingest.py --outputs-dir outputs --iou-threshold 0.5 --out outputs/robustness_reports/row_table_iou03.parquet"
