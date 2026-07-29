#!/usr/bin/env python
"""scripts/run_full_sequence.py — Run kradar_visibility pipeline against one FULL real sequence.

Usage
-----
  # Full run (all 462 frames, sequence 2):
  uv run python scripts/run_full_sequence.py

  # Dry-run on first N frames:
  uv run python scripts/run_full_sequence.py --max-frames 3

Note
----
This script does NOT modify pipeline.py, radar_visibility.py, lidar_visibility.py,
or camera_visibility.py.  It is a standalone consumer of the existing public API
that captures current baseline behaviour.
"""

import logging
import sys
import time
import traceback
from pathlib import Path
from typing import Optional

import polars as pl

# ---------------------------------------------------------------------------
# Imports from the pipeline's public surface (same pattern as pipeline.run())
# ---------------------------------------------------------------------------
from kradar_visibility.parser import (
    get_sequence_label_files,
    parse_label_file,
    parse_description_txt,
)
from kradar_visibility.calibration import load_camera_calibration
from kradar_visibility.pipeline import compute_visibility_for_frame
from kradar_visibility.config import DATASET_ROOT, OUTPUT_SCHEMA

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SEQUENCE = "2"                                         # smallest: 462 label files
OUTPUT_PATH = Path("outputs/output_seq2_full.parquet")  # does NOT overwrite output.parquet
ERROR_LOG = Path("outputs/output_seq2_full.errors.log")

# Sequence 2 frame range (discovered empirically)
LABEL_FILES_TOTAL = 462
ANNOTATED_FRAMES = 187
TOTAL_OBJECTS = 222


def run_sequence(
    sequence_id: str = SEQUENCE,
    dataset_root: Optional[Path] = None,
    max_frames: Optional[int] = None,
    annotated_first: bool = False,
) -> pl.DataFrame:
    """Run the pipeline on *every* frame of one sequence with per-frame progress.

    Parameters
    ----------
    sequence_id : str
        K-Radar sequence folder name.
    dataset_root : Path or None
        Root of the K-Radar dataset.  Defaults to config.DATASET_ROOT.
    max_frames : int or None
        If set, process at most this many label files (for dry-run testing).

    Returns
    -------
    pl.DataFrame
    """
    if dataset_root is None:
        dataset_root = DATASET_ROOT

    dataset_root = Path(dataset_root)
    output_path = OUTPUT_PATH
    error_log_path = ERROR_LOG

    # ------------------------------------------------------------------ #
    # Calibration availability  (same logic as pipeline.run())
    # ------------------------------------------------------------------ #
    calib_available = True
    try:
        load_camera_calibration(seq=int(sequence_id) if sequence_id.isdigit() else 1)
    except Exception as exc:
        log.warning(
            "Calibration unavailable for sequence %s (%s). Camera metrics zeroed.",
            sequence_id, exc,
        )
        calib_available = False

    # ------------------------------------------------------------------ #
    # Weather label
    # ------------------------------------------------------------------ #
    weather_info = parse_description_txt(sequence_id, dataset_root)
    weather_raw = weather_info.get("weather", "").strip()
    from kradar_visibility.config import ALLOWED_WEATHER

    if weather_raw and weather_raw in ALLOWED_WEATHER:
        weather_label = weather_raw
    else:
        weather_label = "normal"

    # ------------------------------------------------------------------ #
    # Label file list (identical to pipeline.run() with frame_limit=None)
    # ------------------------------------------------------------------ #
    label_files = get_sequence_label_files(sequence_id, dataset_root)

    if annotated_first and max_frames is not None:
        # Skip empty frames to get a quick dry-run with real output
        annotated = []
        for f in label_files:
            if len(annotated) >= max_frames:
                break
            try:
                _, objects = parse_label_file(f)
                if objects:
                    annotated.append(f)
            except Exception:
                continue
        label_files = annotated
        max_frames = None  # already capped

    n_total = len(label_files)

    if max_frames is not None:
        label_files = label_files[:max_frames]
        n_total = len(label_files)

    print(f"Sequence:        {sequence_id}")
    print(f"Dataset root:    {dataset_root}")
    print(f"Label files:     {n_total}  (total available: {len(get_sequence_label_files(sequence_id, dataset_root))})")
    print(f"Weather:         {weather_label}")
    print(f"Calibration:     {'available' if calib_available else 'UNAVAILABLE (camera zeroed)'}")
    print(f"Output:          {output_path}")
    print(f"Error log:       {error_log_path}")
    print(f"\n{'=' * 60}")
    print(f"{'FRAME':>10}  {'FILES':>6}  {'ELAPSED':>10}  {'ETA':>10}  {'STATUS'}")
    print(f"{'─' * 10}  {'─' * 6}  {'─' * 10}  {'─' * 10}  {'─' * 20}")

    # ------------------------------------------------------------------ #
    # Main loop with per-frame progress
    # ------------------------------------------------------------------ #
    all_rows: list[dict] = []
    errors: list[str] = []
    t_start = time.time()

    for idx, label_file in enumerate(label_files):
        t_frame = time.time()
        frame_name = label_file.stem
        frame_success = True
        frame_error_msg = ""

        try:
            header, objects = parse_label_file(label_file)
            rows = compute_visibility_for_frame(
                sequence_id, header, objects, dataset_root,
                calib_available=calib_available,
                weather_label=weather_label,
            )
            all_rows.extend(rows)
        except Exception as exc:
            frame_success = False
            frame_error_msg = f"{type(exc).__name__}: {exc}"
            tb = traceback.format_exc()
            errors.append(
                f"[FRAME {idx + 1:>4d} / {n_total}] {frame_name}\n"
                f"  File:     {label_file}\n"
                f"  Error:    {frame_error_msg}\n"
                f"  Traceback:\n"
                f"{'    ' + tb.replace(chr(10), chr(10) + '    ').rstrip()}"
            )

        elapsed = time.time() - t_start
        frame_duration = time.time() - t_frame

        # ETA estimate based on per-frame average so far
        frames_done = idx + 1
        if frames_done > 2:
            avg_per_frame = elapsed / frames_done
            eta_remaining = avg_per_frame * (n_total - frames_done)
            eta_str = f"{eta_remaining:>8.0f}s" if eta_remaining < 3600 else f"{eta_remaining / 3600:>7.1f}h"
        else:
            eta_str = "  warming…"

        frame_count_str = f"{idx + 1:>4d}/{n_total}"
        status = "OK" if frame_success else "ERR"
        print(
            f"{frame_name:>10}  {frame_count_str:>6}  {elapsed:>8.0f}s  {eta_str:>10}  {status}"
        )

    # ------------------------------------------------------------------ #
    # Write errors log
    # ------------------------------------------------------------------ #
    error_log_path.parent.mkdir(parents=True, exist_ok=True)
    if errors:
        error_log_path.write_text(
            f"# Sequence {sequence_id} — per-frame error log\n"
            f"# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"# Total frames processed: {n_total}\n"
            f"# Frames with errors: {len(errors)}\n"
            f"\n"
            + "\n---\n".join(errors)
            + "\n"
        )
        print(f"\n⚠ {len(errors)} frame(s) had errors — see {error_log_path}")
    else:
        error_log_path.write_text(
            f"# Sequence {sequence_id} — per-frame error log\n"
            f"# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"# Total frames processed: {n_total}\n"
            f"# Frames with errors: 0\n"
            f"# No errors.\n"
        )

    # ------------------------------------------------------------------ #
    # Build DataFrame and write Parquet
    # ------------------------------------------------------------------ #
    elapsed_total = time.time() - t_start

    if not all_rows:
        print("\n⚠ Pipeline produced no rows for this sequence.")
        print(f"Total frames processed: {n_total}")
        print(f"Total wall-clock time: {elapsed_total:.0f}s")
        return pl.DataFrame()

    df = pl.DataFrame(all_rows, schema_overrides={
        "cam_front_proj_x": pl.Float64,
        "cam_front_proj_y": pl.Float64,
        "cam_left_proj_x": pl.Float64,
        "cam_left_proj_y": pl.Float64,
        "cam_right_proj_x": pl.Float64,
        "cam_right_proj_y": pl.Float64,
        "cam_rear_proj_x": pl.Float64,
        "cam_rear_proj_y": pl.Float64,
    })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(output_path)

    # ------------------------------------------------------------------ #
    # Summary
    # ------------------------------------------------------------------ #
    n_errors = len(errors)
    print(f"\n{'=' * 60}")
    print(f"  COMPLETE — Sequence {sequence_id}")
    print(f"  Total frames processed:  {n_total}")
    print(f"  Frames with errors:      {n_errors}")
    print(f"  Rows produced:           {df.height}")
    print(f"  Total wall-clock time:   {elapsed_total:.0f}s")
    if elapsed_total > 0:
        print(f"  Per-frame average:       {elapsed_total / n_total:.1f}s")
        print(f"  Throughput:              {n_total / elapsed_total:.2f} frames/s")
    print(f"  Output:                  {output_path.resolve()}")
    print(f"  Errors log:              {error_log_path.resolve()}")
    print(f"{'=' * 60}")

    return df


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Run kradar_visibility pipeline on one full sequence.",
    )
    parser.add_argument(
        "--sequence",
        default=SEQUENCE,
        help=f"Sequence ID (default: {SEQUENCE})",
    )
    parser.add_argument(
        "--dataset-root",
        type=Path,
        default=None,
        help="K-Radar dataset root (default: config.DATASET_ROOT)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Parquet output path (default: outputs/output_seq2_full.parquet)",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=None,
        help="Process at most N frames (for dry-run testing; default: all)",
    )
    parser.add_argument(
        "--annotated-first",
        action="store_true",
        help="Skip empty frames and process the first N annotated frames (for quick dry-run). "
             "Implies --max-frames N.",
    )
    parser.add_argument(
        "--error-log",
        type=Path,
        default=None,
        help="Error log path (default: outputs/output_seq2_full.errors.log)",
    )

    args = parser.parse_args()

    # Override paths via globals  (safe: these are module-scope Path objects)
    global OUTPUT_PATH, ERROR_LOG
    if args.output is not None:
        OUTPUT_PATH = args.output
    if args.error_log is not None:
        ERROR_LOG = args.error_log

    run_sequence(
        sequence_id=args.sequence,
        dataset_root=args.dataset_root,
        max_frames=args.max_frames,
        annotated_first=args.annotated_first,
    )


if __name__ == "__main__":
    main()