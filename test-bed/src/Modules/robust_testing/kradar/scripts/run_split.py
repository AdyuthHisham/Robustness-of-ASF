#!/usr/bin/env python
"""scripts/run_split.py — Run kradar_visibility over a K-Radar dataset split
(e.g. resources/split/test.txt) across all its sequences, writing one
combined Parquet.

The split file format is one line per frame: "<sequence_id>,<label_filename>"
(e.g. "1,00182_00150.txt"). It selects a subset of frames *within* each
sequence, not a subset of sequences — every K-Radar sequence contributes
frames to both train and test splits.

Each sequence is processed to its own shard under --shard-dir (resumable:
an existing shard is skipped unless --overwrite is passed, so an interrupted
multi-hour run can be restarted without redoing finished sequences). After
all requested sequences are done, shards are concatenated into one combined
Parquet at --output.

Usage
-----
  # Validate on a couple of sequences first:
  uv run python scripts/run_split.py --sequences 1,2 --workers 4

  # Full test split, all sequences, 6 workers each:
  uv run python scripts/run_split.py --workers 6
"""

import argparse
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, Optional, Set

import polars as pl

from run_full_sequence import run_sequence
from kradar_visibility.config import DATASET_ROOT

# Bundled inside this subproject (copied from K-Radar's resources/split/) so
# a split-aware run needs no dependency on the separate K-Radar git
# submodule being present — only this kradar_visibility subproject needs to
# be transferred to a remote host (e.g. Alvis).
DEFAULT_SPLIT_DIR = Path(__file__).resolve().parent.parent / "resources" / "split"


def parse_split_file(split_path: Path) -> Dict[str, Set[str]]:
    """Parse a K-Radar split file into {sequence_id: {label_filename, ...}}."""
    by_sequence: Dict[str, Set[str]] = defaultdict(set)
    for line in split_path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        seq_id, _, filename = line.partition(",")
        by_sequence[seq_id].add(filename)
    return dict(by_sequence)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dataset-root", type=Path, default=None,
                         help="K-Radar dataset root (default: config.DATASET_ROOT)")
    parser.add_argument("--split-file", type=Path, default=None,
                         help="Split file path (default: bundled resources/split/test.txt in this subproject)")
    parser.add_argument("--sequences", type=str, default=None,
                         help="Comma-separated sequence IDs to restrict to (default: all sequences in the split file)")
    parser.add_argument("--workers", type=int, default=1,
                         help="Worker processes per sequence (default: 1)")
    parser.add_argument("--shard-dir", type=Path, default=Path("outputs/split_shards"),
                         help="Directory for per-sequence shard Parquet/error-log files")
    parser.add_argument("--output", type=Path, default=Path("outputs/kradar_split_full.parquet"),
                         help="Combined output Parquet path")
    parser.add_argument("--overwrite", action="store_true",
                         help="Reprocess sequences even if a shard already exists")
    parser.add_argument("--skip-merge", action="store_true",
                         help="Only produce shards, skip the final concat step")
    args = parser.parse_args()

    dataset_root = args.dataset_root or DATASET_ROOT
    split_file = args.split_file or (DEFAULT_SPLIT_DIR / "test.txt")

    frames_by_sequence = parse_split_file(split_file)
    sequence_ids = sorted(frames_by_sequence.keys(), key=lambda s: int(s) if s.isdigit() else s)
    if args.sequences is not None:
        requested = set(args.sequences.split(","))
        missing = requested - set(sequence_ids)
        if missing:
            print(f"ERROR: sequence(s) not present in split file: {sorted(missing)}", file=sys.stderr)
            sys.exit(1)
        sequence_ids = [s for s in sequence_ids if s in requested]

    args.shard_dir.mkdir(parents=True, exist_ok=True)

    print(f"Split file:      {split_file}")
    print(f"Sequences:       {len(sequence_ids)}  ({', '.join(sequence_ids)})")
    print(f"Total frames:    {sum(len(frames_by_sequence[s]) for s in sequence_ids)}")
    print(f"Workers/seq:     {args.workers}")
    print(f"Shard dir:       {args.shard_dir}")
    print(f"{'=' * 70}\n")

    t_start = time.time()
    shard_paths = []
    for i, seq_id in enumerate(sequence_ids, start=1):
        shard_path = args.shard_dir / f"output_seq{seq_id}.parquet"
        error_log_path = args.shard_dir / f"output_seq{seq_id}.errors.log"
        shard_paths.append(shard_path)

        if shard_path.exists() and not args.overwrite:
            print(f"[{i}/{len(sequence_ids)}] Sequence {seq_id}: shard exists, skipping ({shard_path})\n")
            continue

        print(f"[{i}/{len(sequence_ids)}] Sequence {seq_id}: {len(frames_by_sequence[seq_id])} split frames")
        run_sequence(
            sequence_id=seq_id,
            dataset_root=dataset_root,
            workers=args.workers,
            frame_filter=frames_by_sequence[seq_id],
            output_path=shard_path,
            error_log_path=error_log_path,
        )
        print()

    elapsed = time.time() - t_start
    print(f"{'=' * 70}")
    print(f"All sequences processed in {elapsed:.0f}s ({elapsed / 3600:.2f}h)")

    if args.skip_merge:
        return

    existing_shards = [p for p in shard_paths if p.exists()]
    if not existing_shards:
        print("No shards produced — nothing to merge.")
        return

    print(f"Merging {len(existing_shards)} shard(s) -> {args.output}")
    dfs = [pl.read_parquet(p) for p in existing_shards]
    combined = pl.concat([df for df in dfs if df.height > 0], how="vertical")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    combined.write_parquet(args.output)
    print(f"Combined output: {args.output.resolve()}  ({combined.height} rows)")


if __name__ == "__main__":
    main()
