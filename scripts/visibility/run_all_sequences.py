#!/usr/bin/env python
"""scripts/run_all_sequences.py — Regenerate output_with_env_density.parquet
for every K-Radar sequence, annotated frames only.

Unannotated label files produce zero output rows (compute_visibility_for_frame
returns [] when objects is empty) but still pay the full sensor-load cost
(~16s/frame single-threaded), so this script pre-filters each sequence's
label files to annotated-only before dispatching work — cutting total work
roughly in proportion to the annotated/total frame ratio while producing an
identical set of output rows to a full (unfiltered) run.

Usage
-----
  uv run python scripts/run_all_sequences.py --workers 8
"""

from amscup_paths import VISIBILITY_DIR  # noqa: E402
import argparse
import logging
import os
import sys
import time
import traceback
from pathlib import Path
from typing import Optional

for _env_var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_env_var, "1")

import polars as pl

from kradar_visibility.parser import (
    get_sequence_label_files,
    parse_label_file,
    parse_description_txt,
)
from kradar_visibility.calibration import load_camera_calibration
from kradar_visibility.pipeline import compute_visibility_for_frame
from kradar_visibility.config import DATASET_ROOT, ALLOWED_WEATHER

log = logging.getLogger(__name__)

SEQUENCE_IDS = [str(i) for i in range(1, 59)]
OUTPUT_PATH = (VISIBILITY_DIR / "output_with_env_density.parquet")
ERROR_LOG = (VISIBILITY_DIR / "output_with_env_density.errors.log")
PROGRESS_LOG = (VISIBILITY_DIR / "output_with_env_density.progress.log")

# K-Radar info_label_rev2 class strings (exact, case-sensitive) for "sedans
# or buses" — the dataset labels buses/trucks jointly as "Bus or Truck",
# there is no separate "Bus" class.
TARGET_CLASSES = {"Sedan", "Bus or Truck"}


def _process_one_frame(
    label_file: Path,
    sequence_id: str,
    dataset_root: Path,
    calib_available: bool,
    weather_label: str,
    environment_label: Optional[str],
    time_of_day_label: Optional[str],
) -> tuple[str, list[dict], Optional[str]]:
    frame_name = label_file.stem
    try:
        header, objects = parse_label_file(label_file)
        objects = [o for o in objects if o.obj_class in TARGET_CLASSES]
        rows = compute_visibility_for_frame(
            sequence_id, header, objects, dataset_root,
            calib_available=calib_available,
            weather_label=weather_label,
            environment_label=environment_label,
            time_of_day_label=time_of_day_label,
        )
        return frame_name, rows, None
    except Exception:
        return frame_name, [], traceback.format_exc()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--sequences", nargs="+", default=SEQUENCE_IDS)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--dataset-root", type=Path, default=None)
    args = parser.parse_args()

    dataset_root = args.dataset_root or DATASET_ROOT
    output_path = args.output

    # Derive log paths from --output so parallel invocations (e.g. one SLURM
    # array task per sequence, each with its own --output shard) don't clobber
    # a single shared progress/error log.
    progress_log = output_path.with_suffix(".progress.log")
    error_log = output_path.with_suffix(".errors.log")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    progress = open(progress_log, "w", buffering=1)

    def plog(msg: str):
        line = f"[{time.strftime('%H:%M:%S')}] {msg}"
        print(line, flush=True)
        progress.write(line + "\n")

    # ---- Build annotated-only frame worklist across all sequences ----
    seq_meta = {}
    all_tasks: list[tuple[Path, str]] = []
    for seq_id in args.sequences:
        calib_available = True
        try:
            load_camera_calibration(seq=int(seq_id) if seq_id.isdigit() else 1)
        except Exception as exc:
            plog(f"seq {seq_id}: calibration unavailable ({exc}); camera metrics zeroed")
            calib_available = False

        weather_info = parse_description_txt(seq_id, dataset_root)
        weather_raw = weather_info.get("weather", "").strip()
        weather_label = weather_raw if weather_raw in ALLOWED_WEATHER else "normal"
        environment_label = weather_info.get("location", "").strip() or None
        time_of_day_label = weather_info.get("time", "").strip() or None

        seq_meta[seq_id] = (calib_available, weather_label, environment_label, time_of_day_label)

        label_files = get_sequence_label_files(seq_id, dataset_root)
        n_total = len(label_files)
        annotated = []
        for f in label_files:
            try:
                _, objects = parse_label_file(f)
                if any(o.obj_class in TARGET_CLASSES for o in objects):
                    annotated.append(f)
            except Exception:
                continue
        plog(f"seq {seq_id}: {len(annotated)}/{n_total} frames with Sedan/Bus-or-Truck queued")
        all_tasks.extend((f, seq_id) for f in annotated)

    n_total_tasks = len(all_tasks)
    plog(f"TOTAL: {n_total_tasks} annotated frames across {len(args.sequences)} sequences")

    # ---- Process ----
    all_rows: list[dict] = []
    errors: list[str] = []
    t_start = time.time()

    if args.workers <= 1:
        for idx, (label_file, seq_id) in enumerate(all_tasks):
            calib_available, weather_label, environment_label, time_of_day_label = seq_meta[seq_id]
            frame_name, rows, error = _process_one_frame(
                label_file, seq_id, dataset_root, calib_available,
                weather_label, environment_label, time_of_day_label,
            )
            if error is None:
                all_rows.extend(rows)
            else:
                errors.append(f"[seq {seq_id} / {frame_name}]\n{error}")
            if (idx + 1) % 25 == 0 or (idx + 1) == n_total_tasks:
                elapsed = time.time() - t_start
                rate = (idx + 1) / elapsed
                eta = (n_total_tasks - idx - 1) / rate if rate > 0 else float("inf")
                plog(f"{idx + 1}/{n_total_tasks} frames  elapsed={elapsed:.0f}s  eta={eta:.0f}s  rows_so_far={len(all_rows)}")
    else:
        from concurrent.futures import ProcessPoolExecutor, as_completed

        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            futures = {}
            for label_file, seq_id in all_tasks:
                calib_available, weather_label, environment_label, time_of_day_label = seq_meta[seq_id]
                fut = pool.submit(
                    _process_one_frame,
                    label_file, seq_id, dataset_root, calib_available,
                    weather_label, environment_label, time_of_day_label,
                )
                futures[fut] = seq_id
            done = 0
            for fut in as_completed(futures):
                seq_id = futures[fut]
                frame_name, rows, error = fut.result()
                done += 1
                if error is None:
                    all_rows.extend(rows)
                else:
                    errors.append(f"[seq {seq_id} / {frame_name}]\n{error}")
                if done % 25 == 0 or done == n_total_tasks:
                    elapsed = time.time() - t_start
                    rate = done / elapsed
                    eta = (n_total_tasks - done) / rate if rate > 0 else float("inf")
                    plog(f"{done}/{n_total_tasks} frames  elapsed={elapsed:.0f}s  eta={eta:.0f}s  rows_so_far={len(all_rows)}")

    elapsed_total = time.time() - t_start

    if errors:
        error_log.write_text(
            f"# Full regeneration — per-frame error log\n"
            f"# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"# Frames with errors: {len(errors)}\n\n" + "\n---\n".join(errors) + "\n"
        )
        plog(f"{len(errors)} frame(s) had errors — see {error_log}")
    else:
        error_log.write_text("# No errors.\n")

    if not all_rows:
        plog("Pipeline produced no rows. Aborting write.")
        sys.exit(1)

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

    plog(f"COMPLETE: {df.height} rows, {n_total_tasks} frames, {len(errors)} errors, "
         f"{elapsed_total:.0f}s total -> {output_path.resolve()}")


if __name__ == "__main__":
    main()
