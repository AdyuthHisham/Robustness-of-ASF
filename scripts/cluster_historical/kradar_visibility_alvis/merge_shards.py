#!/usr/bin/env python
"""scripts/alvis/merge_shards.py — Concatenate per-sequence shard Parquets
(produced by regen_sedan_bus.sbatch, one per sequence under
outputs/shards_sedan_bus/) into the final output/output_with_env_density.parquet.

Usage
-----
  uv run python scripts/alvis/merge_shards.py \
      --shard-dir outputs/shards_sedan_bus \
      --output output/output_with_env_density.parquet \
      --expect 58
"""

from amscup_paths import FIGURES_DIR  # noqa: E402
import argparse
from pathlib import Path

import polars as pl


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shard-dir", type=Path, default=Path("outputs/shards_sedan_bus"))
    parser.add_argument("--output", type=Path, default=(FIGURES_DIR / "output_with_env_density.parquet"))
    parser.add_argument("--expect", type=int, default=58, help="Expected shard count; warns if fewer found.")
    args = parser.parse_args()

    shards = sorted(args.shard_dir.glob("seq_*.parquet"))
    print(f"Found {len(shards)} shard(s) in {args.shard_dir} (expected {args.expect}).")
    if len(shards) < args.expect:
        missing = args.expect - len(shards)
        print(f"WARNING: {missing} shard(s) missing — merging what's available. "
              f"Re-run the sbatch array for missing sequences before treating this as final.")

    if not shards:
        print("No shards found. Nothing to merge.")
        return

    dfs = [pl.read_parquet(s) for s in shards]
    df = pl.concat(dfs, how="vertical")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(args.output)

    print(f"Merged {df.height} rows from {len(shards)} shard(s) -> {args.output.resolve()}")
    print(f"Sequences present: {sorted(df['sequence_id'].unique().to_list(), key=lambda x: int(x) if x.isdigit() else 0)}")


if __name__ == "__main__":
    main()
