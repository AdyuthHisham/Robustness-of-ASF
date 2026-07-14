#!/usr/bin/env python3
"""
Validation script for the visibility output Parquet file.

Given a path to a Parquet file, this script checks:
  a. The file opens as valid Parquet (via polars).
  b. Every column in the expected_cols list is present.
  c. sequence_id, frame_idx, and obj_tracking_id contain no nulls.
  d. ghost_flag column has boolean dtype.
  e. All columns ending in "_score" have values within [0.0, 1.0], ignoring nulls.

Usage:
    uv run python scripts/validate_output.py /path/to/output.parquet
"""

import sys
from pathlib import Path

import polars as pl


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path_to_parquet_file>")
        sys.exit(1)

    parquet_path = Path(sys.argv[1])
    if not parquet_path.is_file():
        print(f"ERROR: File not found: {parquet_path}")
        sys.exit(1)

    # Expected columns from tests/test_smoke.py::test_smk17_full_pipeline_two_sequences
    expected_cols = [
        'sequence_id', 'frame_idx', 'obj_tracking_id', 'obj_class',
        'radar_visible', 'radar_sparsity_score',
        'lidar64_visible', 'lidar64_points_count', 'lidar64_sparsity_score',
        'lidar128_visible', 'lidar128_points_count', 'lidar128_sparsity_score',
        'cam_front_visible', 'cam_front_visibility_score',
        'cam_left_visible', 'cam_left_visibility_score',
        'cam_right_visible', 'cam_right_visibility_score',
        'cam_rear_visible', 'cam_rear_visibility_score',
        'ghost_flag'
    ]

    all_passed = True

    # a. Check that the file opens as valid Parquet
    try:
        df = pl.read_parquet(parquet_path)
        print("PASS: File opens as valid Parquet")
    except Exception as e:
        print(f"FAIL: Failed to read Parquet file: {e}")
        sys.exit(1)

    # b. Check that every expected column is present
    missing_cols = [col for col in expected_cols if col not in df.columns]
    if missing_cols:
        print(f"FAIL: Missing columns: {missing_cols}")
        all_passed = False
    else:
        print("PASS: All expected columns present")

    # c. Check that sequence_id, frame_idx, and obj_tracking_id contain no nulls
    for col in ['sequence_id', 'frame_idx', 'obj_tracking_id']:
        null_count = df[col].null_count()
        if null_count > 0:
            print(f"FAIL: Column '{col}' contains {null_count} null(s)")
            all_passed = False
        else:
            print(f"PASS: Column '{col}' contains no nulls")

    # d. Check that ghost_flag column has boolean dtype
    if 'ghost_flag' in df.columns:
        if df['ghost_flag'].dtype == pl.Boolean:
            print("PASS: ghost_flag column has boolean dtype")
        else:
            print(f"FAIL: ghost_flag column has dtype {df['ghost_flag'].dtype}, expected Boolean")
            all_passed = False
    else:
        # This case should have been caught by the column presence check, but just in case
        print("FAIL: ghost_flag column not found")
        all_passed = False

    # e. Check that all columns ending in "_score" have values within [0.0, 1.0], ignoring nulls
    score_cols = [col for col in df.columns if col.endswith('_score')]
    for col in score_cols:
        # Drop nulls for the range check
        non_null = df[col].drop_nulls()
        if non_null.is_empty():
            print(f"INFO: Column '{col}' contains only nulls; skipping range check")
            continue
        min_val = non_null.min()
        max_val = non_null.max()
        # min_val and max_val are scalars; they should not be None because non_null is not empty
        if min_val is None or max_val is None:
            # This should not happen, but guard anyway
            print(f"INFO: Column '{col}' has no non-null values; skipping range check")
            continue
        if min_val < 0.0 or max_val > 1.0:
            print(f"FAIL: Column '{col}' has values outside [0.0, 1.0]: min={min_val}, max={max_val}")
            all_passed = False
        else:
            print(f"PASS: Column '{col}' values within [0.0, 1.0] (min={min_val}, max={max_val})")

    if all_passed:
        print("\nAll checks passed.")
        sys.exit(0)
    else:
        print("\nOne or more checks failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()