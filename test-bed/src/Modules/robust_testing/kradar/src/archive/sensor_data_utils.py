"""
sensor_data_utils.py

Shared helper functions for the K-Radar sensor-fusion processing pipeline.

This module centralizes logic that is duplicated between the LiDAR and Radar
processing paths:

  * Path resolution: accept either a single file or a directory and return a
    deterministic, sorted list of files to process.
  * Validation: raise clear, actionable errors for missing paths, wrong file
    types, and empty directories.
  * Device-agnostic "points in boxes" computation: a NumPy/CPU implementation
    of the same operation provided on GPU by
    `pcdet.ops.roiaware_pool3d.roiaware_pool3d_utils.points_in_boxes_gpu`,
    plus a thin dispatcher that picks GPU or CPU based on a `device` flag.

These helpers are imported by both the GPU notebook (sensor_data.py /
sensor_data_gpu.py) and the CPU notebook (sensor_data_cpu.py).
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import numpy as np


# ---------------------------------------------------------------------------
# Path resolution / discovery
# ---------------------------------------------------------------------------

def resolve_input_paths(
    input_path: str | Path,
    suffixes: Sequence[str],
    recursive: bool = False,
) -> list[Path]:
    """Resolve a user-supplied path into a sorted list of files to process.

    Accepts either:
      * A path to a single file matching one of `suffixes` -> returns
        `[that_file]`.
      * A path to a directory -> returns all files within it whose suffix is
        in `suffixes`, sorted by name for deterministic ordering. Set
        `recursive=True` to search subdirectories as well.

    Args:
        input_path: File or directory path (str or Path).
        suffixes: Iterable of accepted file extensions, e.g. (".pcd",) or
            (".mat",). Matching is case-insensitive and tolerant of
            extensions given with or without a leading dot.
        recursive: If True and `input_path` is a directory, search
            subdirectories recursively (`rglob`) instead of only the
            top level (`glob`).

    Returns:
        A sorted list of `Path` objects to process. Always non-empty.

    Raises:
        FileNotFoundError: If `input_path` does not exist, or if a directory
            contains no files matching `suffixes`.
        NotADirectoryError: If `input_path` is neither a file nor a directory
            (e.g. a broken symlink or special file).
        ValueError: If a single-file `input_path` does not have a suffix in
            `suffixes`.
    """
    input_path = Path(input_path)

    # Normalize suffixes to lowercase, dot-prefixed strings, e.g. ".pcd"
    normalized_suffixes = {
        s.lower() if s.startswith(".") else f".{s.lower()}" for s in suffixes
    }

    if not input_path.exists():
        raise FileNotFoundError(f"Path not found: {input_path}")

    if input_path.is_file():
        if input_path.suffix.lower() not in normalized_suffixes:
            raise ValueError(
                f"Unsupported file type: '{input_path.suffix}' for "
                f"{input_path}. Expected one of: "
                f"{sorted(normalized_suffixes)}"
            )
        return [input_path]

    if input_path.is_dir():
        glob_fn = input_path.rglob if recursive else input_path.glob
        matches: list[Path] = []
        for suffix in sorted(normalized_suffixes):
            matches.extend(glob_fn(f"*{suffix}"))

        # De-duplicate (in case a file matches multiple suffix patterns) and
        # sort for a deterministic processing order.
        files = sorted(set(f for f in matches if f.is_file()))

        if not files:
            mode = "recursively " if recursive else ""
            raise FileNotFoundError(
                f"No files {mode}matching {sorted(normalized_suffixes)} "
                f"found in directory: {input_path}"
            )
        return files

    raise NotADirectoryError(
        f"Path exists but is neither a regular file nor a directory: "
        f"{input_path}"
    )


# ---------------------------------------------------------------------------
# Device-agnostic points-in-boxes
# ---------------------------------------------------------------------------

def points_in_boxes_cpu(points: np.ndarray, boxes: np.ndarray) -> np.ndarray:
    """Pure-NumPy CPU equivalent of `points_in_boxes_gpu`.

    For each point, determines which (rotated) 3D box it falls inside, if
    any. Mirrors the semantics of OpenPCDet's
    `points_in_boxes_gpu(points, boxes)`:

        - points: (N, 3) array of (x, y, z) coordinates.
        - boxes:  (M, 7) array of (cx, cy, cz, dx, dy, dz, heading), where
          dx/dy/dz are full box dimensions (length, width, height) and
          heading is the rotation around the z-axis in radians.

    Returns:
        (N,) int64 array where each entry is the index `m` (0..M-1) of the
        box the point falls inside, or -1 if the point is not inside any
        box. If a point lies inside multiple boxes, the first matching box
        (lowest index) wins -- matching the typical GPU kernel behaviour.

    Notes:
        This implementation is O(N * M) and intended for the moderate
        per-frame object counts typical of K-Radar annotations (tens of
        boxes). For very large M, consider spatial pre-filtering (e.g. an
        axis-aligned bounding-box check) before the rotated-box test.
    """
    points = np.asarray(points, dtype=np.float64)
    boxes = np.asarray(boxes, dtype=np.float64)

    n_points = points.shape[0]
    n_boxes = boxes.shape[0]

    box_idxs = np.full(n_points, -1, dtype=np.int64)
    if n_points == 0 or n_boxes == 0:
        return box_idxs

    for m in range(n_boxes):
        cx, cy, cz, dx, dy, dz, heading = boxes[m]

        # Translate points into the box's local frame.
        local = points - np.array([cx, cy, cz])

        # Rotate by -heading around the z-axis to align with axes.
        cos_h, sin_h = np.cos(-heading), np.sin(-heading)
        x_rot = local[:, 0] * cos_h - local[:, 1] * sin_h
        y_rot = local[:, 0] * sin_h + local[:, 1] * cos_h
        z_rot = local[:, 2]

        half_dx, half_dy, half_dz = dx / 2.0, dy / 2.0, dz / 2.0

        inside = (
            (np.abs(x_rot) <= half_dx)
            & (np.abs(y_rot) <= half_dy)
            & (np.abs(z_rot) <= half_dz)
        )

        # Only assign points that haven't already been claimed by an earlier
        # (lower-index) box, matching "first match wins" semantics.
        unclaimed = box_idxs == -1
        assign = inside & unclaimed
        box_idxs[assign] = m

    return box_idxs


def points_in_boxes(points, boxes, device: str = "cpu"):
    """Dispatch points-in-boxes computation to GPU or CPU.

    Args:
        points: For `device="cuda"`, a `(1, N, 3)` torch.Tensor on the GPU
            (matching `points_in_boxes_gpu`'s expected shape). For
            `device="cpu"`, an `(N, 3)` array-like (NumPy array or anything
            convertible via `np.asarray`).
        boxes: For `device="cuda"`, a `(1, M, 7)` torch.Tensor on the GPU.
            For `device="cpu"`, an `(M, 7)` array-like.
        device: Either "cpu" or "cuda". Selects the implementation used.

    Returns:
        - `device="cuda"`: a `(N,)` torch.Tensor of box indices (as returned
          by `points_in_boxes_gpu(...).squeeze(0)`), still on the GPU.
        - `device="cpu"`: a `(N,)` NumPy int64 array of box indices.

    Raises:
        ValueError: If `device` is not "cpu" or "cuda".
        ImportError: If `device="cuda"` but the OpenPCDet CUDA op is not
            importable.
    """
    if device == "cpu":
        return points_in_boxes_cpu(np.asarray(points), np.asarray(boxes))

    if device == "cuda":
        # Imported lazily so this module (and the CPU pipeline) can be used
        # on machines without the compiled CUDA extension.
        from pcdet.ops.roiaware_pool3d.roiaware_pool3d_utils import (
            points_in_boxes_gpu,
        )

        return points_in_boxes_gpu(points, boxes).squeeze(0)

    raise ValueError(f"Unsupported device: {device!r}. Expected 'cpu' or 'cuda'.")


# ---------------------------------------------------------------------------
# Misc small helpers
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Sensor calibration offsets (sensor frame -> ego/vehicle frame)
# ---------------------------------------------------------------------------

class SensorCalibrationOffset:
    """Applies a fixed translation offset between a sensor frame and the ego frame.

    K-Radar's ground-truth annotations (object centers, headings) are given
    in the vehicle's ego frame, with origin at the vehicle reference point.
    Raw LiDAR and Radar point clouds are reported in their own sensor
    frames, each translated from the ego origin by a fixed mounting offset.
    This class converts points between those frames.

    Args:
        offset_x, offset_y, offset_z: Translation (in meters) from the ego
            origin to the sensor's mounting position, expressed in the ego
            frame's axes (x: forward, y: left/right, z: up/down -- sign
            convention follows the K-Radar dataset).
    """

    def __init__(self, offset_x: float, offset_y: float, offset_z: float):
        self.offset = np.array([offset_x, offset_y, offset_z], dtype=np.float64)

        # Vehicle reference point (ego frame origin).
        self.vehicle_center = np.array([0.0, 0.0, 0.0])

        # Sensor mounting position relative to the vehicle center.
        self.sensor_antenna_position = self.vehicle_center + self.offset

    def sensor_to_ego(self, sensor_point: np.ndarray) -> np.ndarray:
        """Transform a single `(3,)` point from sensor frame to ego frame."""
        return np.asarray(sensor_point, dtype=np.float64) + self.offset

    def ego_to_sensor(self, ego_point: np.ndarray) -> np.ndarray:
        """Transform a single `(3,)` point from ego frame to sensor frame."""
        return np.asarray(ego_point, dtype=np.float64) - self.offset

    def transform_point_cloud(self, sensor_points: np.ndarray) -> np.ndarray:
        """Transform an `(N, 3)` point cloud from sensor frame to ego frame.

        Args:
            sensor_points: `(N, 3)` array of points in the sensor frame.

        Returns:
            `(N, 3)` array of points in the ego frame, same dtype as input.
        """
        sensor_points = np.asarray(sensor_points)
        return sensor_points + self.offset[np.newaxis, :].astype(sensor_points.dtype)

    def visualize_offset(self) -> None:
        """Print a human-readable summary of the calibration offset."""
        print("=" * 70)
        print("CALIBRATION OFFSET VISUALIZATION")
        print("=" * 70)

        print(f"\nVehicle Center (Ego Frame Origin): {self.vehicle_center}")
        print(f"Sensor Antenna Position: {self.sensor_antenna_position}")
        print(f"Calibration Offset: {self.offset}")

        print("\nInterpretation:")
        print(
            f"  X-axis: {'+' if self.offset[0] > 0 else ''}{self.offset[0]:.2f}m "
            f"{'FORWARD' if self.offset[0] > 0 else 'BACKWARD'}"
        )
        print(
            f"  Y-axis: {'+' if self.offset[1] > 0 else ''}{self.offset[1]:.2f}m "
            f"{'RIGHT' if self.offset[1] > 0 else 'LEFT'}"
        )
        print(
            f"  Z-axis: {'+' if self.offset[2] > 0 else ''}{self.offset[2]:.2f}m "
            f"{'UP' if self.offset[2] > 0 else 'DOWN'}"
        )

        print("\n" + "=" * 70)


# K-Radar sensor mounting offsets, in meters, relative to the ego/vehicle
# reference point (see K-Radar dataset documentation / calibration files).
KRADAR_LIDAR_OFFSET = (-2.54, 0.3, 0.7)
KRADAR_RADAR_OFFSET = (-0.18, -0.12, 0.19)


def counts_from_box_idxs(box_idxs: np.ndarray, num_boxes: int) -> np.ndarray:
    """Convert per-point box assignments into a per-box point count.

    Args:
        box_idxs: (N,) array of box indices in [-1, num_boxes - 1], as
            returned by `points_in_boxes` / `points_in_boxes_cpu`.
        num_boxes: Total number of boxes `M` for this frame.

    Returns:
        (M,) int64 array where entry `i` is the number of points assigned
        to box `i`. Points with index -1 (no box) are excluded.
    """
    box_idxs = np.asarray(box_idxs)
    shifted = box_idxs + 1  # -1 -> 0 (bin for "no box")
    counts = np.bincount(shifted, minlength=num_boxes + 1)[1:]
    # Ensure exactly `num_boxes` entries even if some trailing boxes got 0.
    if counts.shape[0] < num_boxes:
        counts = np.pad(counts, (0, num_boxes - counts.shape[0]))
    return counts.astype(np.int64)
