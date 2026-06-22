#!/usr/bin/env python
"""scripts/run_pipeline.py — CLI entry point for the kradar_visibility pipeline.

Usage examples
--------------
# Toy subset (default): sequences 1+2, 20 annotated frames each
uv run python scripts/run_pipeline.py

# Custom sequences and frame limit
uv run python scripts/run_pipeline.py --sequences 1 2 3 --frame-limit 50

# Full run (future scope — slow on CPU)
uv run python scripts/run_pipeline.py --sequences $(seq 1 58 | tr '\n' ' ') --no-frame-limit

# Custom output path
uv run python scripts/run_pipeline.py --output outputs/my_run.parquet

# Skip verification report generation
uv run python scripts/run_pipeline.py --no-report
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import polars as pl

# ---------------------------------------------------------------------------
# Defaults (match smoke test toy-scale spec)
# ---------------------------------------------------------------------------
DEFAULT_SEQUENCES = ["1", "2"]
DEFAULT_FRAME_LIMIT = 20
DEFAULT_OUTPUT = Path("outputs/visibility_output.parquet")
DEFAULT_REPORT = Path("outputs/verification_report.md")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the K-Radar visibility pipeline and produce a Parquet output.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--sequences",
        nargs="+",
        default=DEFAULT_SEQUENCES,
        metavar="SEQ",
        help=f"Sequence IDs to process (default: {DEFAULT_SEQUENCES})",
    )
    parser.add_argument(
        "--frame-limit",
        type=int,
        default=DEFAULT_FRAME_LIMIT,
        metavar="N",
        help=f"Max annotated frames per sequence (default: {DEFAULT_FRAME_LIMIT}). "
             "Use 0 for no limit.",
    )
    parser.add_argument(
        "--no-frame-limit",
        action="store_true",
        help="Process all frames (overrides --frame-limit). Full-dataset, future scope.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        metavar="PATH",
        help=f"Parquet output path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--dataset-root",
        type=Path,
        default=None,
        metavar="PATH",
        help="K-Radar dataset root (default: value from config.py)",
    )
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Skip verification report generation after pipeline run.",
    )
    parser.add_argument(
        "--report-output",
        type=Path,
        default=DEFAULT_REPORT,
        metavar="PATH",
        help=f"Verification report output path (default: {DEFAULT_REPORT})",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Terminal summary
# ---------------------------------------------------------------------------

def print_summary(df: pl.DataFrame, elapsed: float):
    """Print a compact summary table of the pipeline output."""
    sep = "─" * 60
    print()
    print(sep)
    print("  PIPELINE SUMMARY")
    print(sep)
    print(f"  Total rows (object-frames):  {df.height}")
    print(f"  Sequences:                   {sorted(df['sequence_id'].unique().to_list())}")
    print(f"  Frames:                      {df['frame_idx'].n_unique()}")
    print(f"  Unique objects:              {df['obj_tracking_id'].n_unique()}")
    print(f"  Object classes:              {sorted(df['obj_class'].unique().to_list())}")
    print(f"  Elapsed:                     {elapsed:.1f}s")
    print(sep)

    # Sensor visibility rates
    sensor_cols = [
        ("radar",     "radar_visible"),
        ("lidar64",   "lidar64_visible"),
        ("lidar128",  "lidar128_visible"),
        ("cam_front", "cam_front_visible"),
        ("cam_left",  "cam_left_visible"),
        ("cam_right", "cam_right_visible"),
        ("cam_rear",  "cam_rear_visible"),
    ]
    print()
    print("  SENSOR VISIBILITY RATES")
    print(f"  {'Sensor':<12} {'Visible':>8}  {'Rate':>8}")
    print(f"  {'──────':<12} {'───────':>8}  {'────':>8}")
    for label, col in sensor_cols:
        n_visible = df[col].sum()
        rate = n_visible / df.height * 100
        print(f"  {label:<12} {n_visible:>8}  {rate:>7.1f}%")

    # Score stats
    print()
    print("  SCORE STATISTICS (non-zero rows)")
    score_cols = [
        ("radar_sparsity_score",        "Radar sparsity"),
        ("lidar64_sparsity_score",       "LiDAR64 sparsity"),
        ("lidar128_sparsity_score",      "LiDAR128 sparsity"),
        ("cam_front_visibility_score",   "Cam front vis"),
    ]
    print(f"  {'Metric':<26} {'Mean':>8}  {'Median':>8}  {'Max':>8}")
    print(f"  {'──────':<26} {'────':>8}  {'──────':>8}  {'───':>8}")
    for col, label in score_cols:
        nz = df.filter(pl.col(col) > 0)[col]
        if nz.len() == 0:
            print(f"  {label:<26} {'—':>8}  {'—':>8}  {'—':>8}")
        else:
            print(f"  {label:<26} {nz.mean():>8.4f}  {nz.median():>8.4f}  {nz.max():>8.4f}")

    # Primary sensor distribution
    print()
    print("  PRIMARY SENSOR DISTRIBUTION")
    ps = (
        df.group_by("primary_sensor")
        .len()
        .sort("len", descending=True)
    )
    for row in ps.iter_rows(named=True):
        sensor = row["primary_sensor"] or "none"
        count = row["len"]
        pct = count / df.height * 100
        print(f"  {sensor:<16} {count:>6}  ({pct:.1f}%)")

    print(sep)
    print()


# ---------------------------------------------------------------------------
# Verification report
# ---------------------------------------------------------------------------

def generate_verification_report(parquet_path: Path, report_path: Path):
    """Run pytest on test_verify.py with --json-report and emit a markdown report."""
    print("Generating verification report...")

    json_report_path = report_path.parent / ".ver_report_tmp.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        [
            "uv", "run", "pytest",
            "tests/test_verify.py",
            "-v",
            "-m", "not optional",
            f"--json-report",
            f"--json-report-file={json_report_path}",
            "--tb=no",
            "-q",
        ],
        capture_output=True,
        text=True,
    )

    # Parse JSON report
    if not json_report_path.exists():
        print("  Warning: pytest JSON report not found. Is pytest-json-report installed?")
        print("  Install with: uv add pytest-json-report")
        _write_fallback_report(report_path, result)
        return

    with open(json_report_path) as f:
        report = json.load(f)

    json_report_path.unlink(missing_ok=True)

    # Build markdown
    lines = [
        "# Verification Report",
        "",
        f"**Parquet:** `{parquet_path}`  ",
        f"**Generated:** {_now()}  ",
        f"**Mode:** CPU-only / toy-scale  ",
        "",
        "| VER ID | Test | Status | Notes |",
        "|--------|------|--------|-------|",
    ]

    summary = report.get("summary", {})
    tests = report.get("tests", [])

    for t in tests:
        node = t["nodeid"]
        # Extract VER-XX id from test name
        name = node.split("::")[-1]
        ver_id = _extract_ver_id(name)
        outcome = t["outcome"]

        if outcome == "passed":
            status = "✅ PASSED"
        elif outcome == "failed":
            status = "❌ FAILED"
        elif outcome == "skipped":
            reason = t.get("setup", {}).get("longrepr", "") or t.get("call", {}).get("longrepr", "")
            status = f"⏭️ SKIPPED"
        else:
            status = outcome.upper()

        # Extract failure message if any
        notes = ""
        if outcome == "failed":
            call = t.get("call", {})
            longrepr = call.get("longrepr", "")
            # Take just the last line of the traceback
            if longrepr:
                notes = longrepr.strip().split("\n")[-1][:80]
        elif outcome == "skipped":
            call = t.get("setup", {}) or t.get("call", {})
            notes = "Insufficient data at toy scale"

        lines.append(f"| {ver_id} | `{name}` | {status} | {notes} |")

    # Summary counts
    passed = summary.get("passed", 0)
    failed = summary.get("failed", 0)
    skipped = summary.get("skipped", 0)
    total = passed + failed + skipped

    lines += [
        "",
        "## Summary",
        "",
        f"| | Count |",
        f"|---|---|",
        f"| ✅ Passed  | {passed} |",
        f"| ❌ Failed  | {failed} |",
        f"| ⏭️ Skipped | {skipped} |",
        f"| **Total**  | **{total}** |",
        "",
        "## Notes",
        "",
        "- Skipped tests require more data than the toy-scale subset provides.",
        "- VER-25/26 (weather impact) are optional and require weather labels wired into the pipeline.",
        "- Full-dataset verification is future scope.",
    ]

    report_path.write_text("\n".join(lines))
    print(f"  Verification report written to {report_path}")
    print(f"  Result: {passed} passed, {failed} failed, {skipped} skipped / {total} total")


def _write_fallback_report(report_path: Path, result: subprocess.CompletedProcess):
    """Fallback: write raw pytest stdout if JSON report unavailable."""
    lines = [
        "# Verification Report",
        "",
        "> **Note:** `pytest-json-report` not installed. Raw pytest output below.",
        "> Install with: `uv add pytest-json-report`",
        "",
        "```",
        result.stdout,
        result.stderr,
        "```",
    ]
    report_path.write_text("\n".join(lines))
    print(f"  Fallback report written to {report_path}")


def _extract_ver_id(test_name: str) -> str:
    """Extract VER-XX from test name like test_ver01_foo or test_smk02_bar."""
    import re
    m = re.search(r'(ver\d+|smk\d+)', test_name, re.IGNORECASE)
    if m:
        raw = m.group(1).upper()
        num = re.search(r'\d+', raw).group()
        prefix = "VER" if raw.startswith("VER") else "SMK"
        return f"{prefix}-{int(num):02d}"
    return "—"


def _now() -> str:
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = parse_args()

    # Resolve frame limit
    frame_limit = None if args.no_frame_limit else (args.frame_limit or None)

    print()
    print("K-Radar Visibility Pipeline")
    print("=" * 40)
    print(f"  Sequences:    {args.sequences}")
    print(f"  Frame limit:  {frame_limit if frame_limit else 'none (all frames)'}")
    print(f"  Output:       {args.output}")
    print(f"  Dataset root: {args.dataset_root or 'from config.py'}")
    print()

    # Import here so import errors surface cleanly
    try:
        from kradar_visibility.pipeline import run
    except ImportError as e:
        print(f"Error: could not import kradar_visibility: {e}")
        print("Make sure you're running from the kradar/ project root with: uv run python scripts/run_pipeline.py")
        sys.exit(1)

    # Run pipeline
    t0 = time.time()
    df = run(
        sequence_ids=args.sequences,
        frame_limit=frame_limit,
        dataset_root=args.dataset_root,
        output_path=args.output,
    )
    elapsed = time.time() - t0

    if df.is_empty():
        print("Pipeline produced no rows. Check --sequences and --dataset-root.")
        sys.exit(1)

    # Terminal summary
    print_summary(df, elapsed)

    # Verification report
    if not args.no_report:
        generate_verification_report(args.output, args.report_output)

    print(f"Done. Parquet: {args.output}")


if __name__ == "__main__":
    main()
