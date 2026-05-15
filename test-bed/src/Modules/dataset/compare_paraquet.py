#!/usr/bin/env python3
"""
compare_parquet.py
------------------
Compares two Parquet files and reports whether they are identical,
and if not, exactly where and how they differ.

Comparison stages (in order):
  1. Schema         — column names and dtypes must match
  2. Row count      — both files must have the same number of rows
  3. Sort & align   — rows are sorted by a canonical key before value comparison
                      (necessary because multithreading produces non-deterministic order)
  4. Column values  — every column is compared element-wise
  5. Summary report — pass/fail per stage, mismatch samples printed

Usage:
  python compare_parquet.py file_a.parquet file_b.parquet
  python compare_parquet.py file_a.parquet file_b.parquet --sort-key ann_token
  python compare_parquet.py file_a.parquet file_b.parquet --show-diffs 20 --no-color
"""

import argparse
import sys
from dataclasses import dataclass, field

import polars as pl


# ------------------------------------------------------------------ #
#  Colour helpers                                                      #
# ------------------------------------------------------------------ #

USE_COLOR = True  # flipped to False by --no-color


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text


def green(t):
    return _c("32", t)


def red(t):
    return _c("31", t)


def yellow(t):
    return _c("33", t)


def bold(t):
    return _c("1", t)


def cyan(t):
    return _c("36", t)


# ------------------------------------------------------------------ #
#  Result container                                                    #
# ------------------------------------------------------------------ #


@dataclass
class CompareResult:
    passed: bool = True
    messages: list[str] = field(default_factory=list)

    def fail(self, msg: str):
        self.passed = False
        self.messages.append(red("  ✗  ") + msg)

    def ok(self, msg: str):
        self.messages.append(green("  ✓  ") + msg)

    def info(self, msg: str):
        self.messages.append(cyan("  ·  ") + msg)

    def warn(self, msg: str):
        self.messages.append(yellow("  !  ") + msg)


# ------------------------------------------------------------------ #
#  Stage 1 — Schema                                                    #
# ------------------------------------------------------------------ #


def compare_schema(df_a: pl.DataFrame, df_b: pl.DataFrame, result: CompareResult):
    print(bold("\n── Stage 1: Schema ──────────────────────────────────────"))

    cols_a = set(df_a.columns)
    cols_b = set(df_b.columns)

    only_in_a = cols_a - cols_b
    only_in_b = cols_b - cols_a

    if only_in_a:
        result.fail(f"Columns only in A: {sorted(only_in_a)}")
    if only_in_b:
        result.fail(f"Columns only in B: {sorted(only_in_b)}")

    # Compare dtypes for shared columns
    shared_cols = sorted(cols_a & cols_b)
    dtype_mismatches = []
    for col in shared_cols:
        ta = df_a[col].dtype
        tb = df_b[col].dtype
        if ta != tb:
            dtype_mismatches.append((col, ta, tb))

    if dtype_mismatches:
        for col, ta, tb in dtype_mismatches:
            result.fail(f"Column '{col}': dtype A={ta}  B={tb}")
    else:
        if not only_in_a and not only_in_b:
            result.ok(
                f"Schemas identical  ({len(shared_cols)} columns, all dtypes match)"
            )

    # Print full schema side-by-side for reference
    result.info("Full schema (A):")
    for col in df_a.columns:
        marker = "" if col in cols_b else yellow("  ← missing in B")
        result.info(f"    {col:<40} {str(df_a[col].dtype)}{marker}")

    for msg in result.messages:
        print(msg)
    result.messages.clear()


# ------------------------------------------------------------------ #
#  Stage 2 — Row count                                                 #
# ------------------------------------------------------------------ #


def compare_row_count(df_a: pl.DataFrame, df_b: pl.DataFrame, result: CompareResult):
    print(bold("\n── Stage 2: Row Count ───────────────────────────────────"))

    ra, rb = len(df_a), len(df_b)
    if ra == rb:
        result.ok(f"Row counts match: {ra:,} rows")
    else:
        result.fail(
            f"Row counts differ: A has {ra:,}, B has {rb:,}  (delta = {abs(ra-rb):,})"
        )

    for msg in result.messages:
        print(msg)
    result.messages.clear()

    return ra == rb


# ------------------------------------------------------------------ #
#  Stage 3 — Sort & align                                              #
# ------------------------------------------------------------------ #


def sort_and_align(
    df_a: pl.DataFrame,
    df_b: pl.DataFrame,
    sort_key: list[str],
    result: CompareResult,
) -> tuple[pl.DataFrame, pl.DataFrame]:
    print(bold("\n── Stage 3: Sort & Align ────────────────────────────────"))

    # Validate sort key columns exist in both
    valid_key = []
    for col in sort_key:
        if col in df_a.columns and col in df_b.columns:
            valid_key.append(col)
        else:
            result.warn(
                f"Sort key column '{col}' missing from one or both files — skipping it"
            )

    if not valid_key:
        result.warn(
            "No valid sort key columns — comparing in file order (rows may not align!)"
        )
        for msg in result.messages:
            print(msg)
        result.messages.clear()
        return df_a, df_b

    result.info(f"Sorting both files by: {valid_key}")
    df_a_sorted = df_a.sort(valid_key)
    df_b_sorted = df_b.sort(valid_key)

    # Check that sort keys are unique (warn if not — alignment may be ambiguous)
    dupes_a = df_a_sorted.filter(pl.struct(valid_key).is_duplicated()).height
    dupes_b = df_b_sorted.filter(pl.struct(valid_key).is_duplicated()).height
    if dupes_a or dupes_b:
        result.warn(
            f"Sort key is not unique!  A: {dupes_a} duplicate keys,  B: {dupes_b} duplicate keys"
        )
        result.warn("Row alignment may be ambiguous for duplicate-key rows")
    else:
        result.ok("Sort keys are unique — rows are unambiguously aligned")

    for msg in result.messages:
        print(msg)
    result.messages.clear()
    return df_a_sorted, df_b_sorted


# ------------------------------------------------------------------ #
#  Stage 4 — Column-by-column value comparison                         #
# ------------------------------------------------------------------ #


def compare_values(
    df_a: pl.DataFrame,
    df_b: pl.DataFrame,
    result: CompareResult,
    show_diffs: int,
) -> dict[str, int]:
    """
    Compares every shared column element-wise.
    Returns {column_name: mismatch_count} for all columns that had mismatches.
    """
    print(bold("\n── Stage 4: Column Values ───────────────────────────────"))

    shared_cols = [c for c in df_a.columns if c in df_b.columns]
    mismatch_counts: dict[str, int] = {}

    for col in shared_cols:
        series_a = df_a[col]
        series_b = df_b[col]

        # Use series equality; handle nulls explicitly
        null_mask_a = series_a.is_null()
        null_mask_b = series_b.is_null()

        # Rows where both are null → equal; one null, one not → different
        both_null = null_mask_a & null_mask_b

        # For non-null rows, compare values
        # Cast to string for universal comparison (handles nested/struct types safely)
        try:
            eq_mask = series_a.cast(pl.Utf8) == series_b.cast(pl.Utf8)
        except Exception:
            eq_mask = series_a == series_b

        # A row is equal if: both null, OR (neither null AND values equal)
        equal_mask = both_null | (eq_mask & ~null_mask_a & ~null_mask_b)
        n_mismatch = int((~equal_mask).sum())

        if n_mismatch == 0:
            print(green(f"  ✓  {col:<45} all {len(series_a):,} rows match"))
        else:
            mismatch_counts[col] = n_mismatch
            result.fail(f"{col:<45} {n_mismatch:,} / {len(series_a):,} rows differ")
            print(result.messages.pop())

            # Print a sample of mismatched rows
            if show_diffs > 0:
                mismatch_idx = (~equal_mask).arg_true()[:show_diffs]
                sample = pl.DataFrame(
                    {
                        "row": mismatch_idx,
                        "A": series_a[mismatch_idx].cast(pl.Utf8),
                        "B": series_b[mismatch_idx].cast(pl.Utf8),
                    }
                )
                print(
                    yellow(
                        f"      First {min(show_diffs, n_mismatch)} mismatched rows for '{col}':"
                    )
                )
                print("      " + str(sample).replace("\n", "\n      "))

    return mismatch_counts


# ------------------------------------------------------------------ #
#  Final summary                                                       #
# ------------------------------------------------------------------ #


def print_summary(
    result: CompareResult, mismatch_counts: dict[str, int], path_a: str, path_b: str
):
    print(bold("\n══════════════════════════════════════════════════════════"))
    print(bold("  SUMMARY"))
    print(bold("══════════════════════════════════════════════════════════"))
    print(f"  File A : {path_a}")
    print(f"  File B : {path_b}")
    print()

    if result.passed and not mismatch_counts:
        print(green(bold("  ✓  FILES ARE IDENTICAL")))
    else:
        print(red(bold("  ✗  FILES DIFFER")))
        if mismatch_counts:
            print()
            print(yellow("  Columns with mismatches:"))
            for col, count in sorted(mismatch_counts.items(), key=lambda x: -x[1]):
                print(yellow(f"    {col:<45} {count:,} rows"))

    print(bold("══════════════════════════════════════════════════════════\n"))


# ------------------------------------------------------------------ #
#  Entry point                                                         #
# ------------------------------------------------------------------ #

DEFAULT_SORT_KEY = ["ann_token"]  # unique per row in NuScenes metadata output


def main():
    global USE_COLOR

    parser = argparse.ArgumentParser(
        description="Compare two Parquet files for equality.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("file_a", help="Path to first Parquet file")
    parser.add_argument("file_b", help="Path to second Parquet file")
    parser.add_argument(
        "--sort-key",
        nargs="+",
        default=DEFAULT_SORT_KEY,
        metavar="COL",
        help=f"Column(s) to sort by before comparing rows. "
        f"Default: {DEFAULT_SORT_KEY}. "
        f"Use multiple columns for a composite key: --sort-key scene_token sample_token ann_token",
    )
    parser.add_argument(
        "--show-diffs",
        type=int,
        default=5,
        metavar="N",
        help="Number of mismatched rows to print per column (default: 5, 0 to disable)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI colour output",
    )
    args = parser.parse_args()

    if args.no_color:
        USE_COLOR = False

    # ---- Load files ----
    print(bold("\n══════════════════════════════════════════════════════════"))
    print(bold("  PARQUET COMPARISON TOOL"))
    print(bold("══════════════════════════════════════════════════════════"))

    try:
        print(f"\nLoading  A : {args.file_a}")
        df_a = pl.read_parquet(args.file_a)
        print(f"  → {len(df_a):,} rows,  {len(df_a.columns)} columns")

        print(f"Loading  B : {args.file_b}")
        df_b = pl.read_parquet(args.file_b)
        print(f"  → {len(df_b):,} rows,  {len(df_b.columns)} columns")
    except Exception as e:
        print(red(f"\n[FATAL] Could not load file: {e}"))
        sys.exit(1)

    result = CompareResult()
    mismatch_counts: dict[str, int] = {}

    # ---- Run stages ----
    compare_schema(df_a, df_b, result)

    rows_match = compare_row_count(df_a, df_b, result)
    if not rows_match:
        # Can't do row-level comparison if counts differ — stop here
        print(yellow("\n  Skipping value comparison: row counts differ."))
        print_summary(result, {}, args.file_a, args.file_b)
        sys.exit(1 if not result.passed else 0)

    df_a, df_b = sort_and_align(df_a, df_b, args.sort_key, result)

    mismatch_counts = compare_values(df_a, df_b, result, args.show_diffs)

    print_summary(result, mismatch_counts, args.file_a, args.file_b)

    sys.exit(0 if result.passed and not mismatch_counts else 1)


if __name__ == "__main__":
    main()
