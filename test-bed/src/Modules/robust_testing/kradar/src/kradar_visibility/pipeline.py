"""Pipeline: parse labels -> compute visibility -> output Parquet.

Changes vs. original:
  ISSUE-01: LiDAR calls updated for new single-sensor calculate_lidar_visibility()
            signature — called once for OS2-64, once for OS1-128.
  ISSUE-02: cam_*_proj_x/y explicitly set to None when cam_*_visible=False.
  ISSUE-03: _bbox_voxels_from_annotation() now uses rotated 8-corner AABB
            (via _obj_corners()) instead of axis-aligned half-extents.
  ISSUE-04: Radar grid constants documented with verification snippet; a
            runtime shape assertion guards against a mismatched .mat file.
  ISSUE-05: Handled inside lidar_visibility.py (center-point FOV check).
  ISSUE-06: Handled inside camera_visibility.py (clip removed from projection).
  ISSUE-07: Calibration load wrapped per-sequence; failures log a warning and
            disable camera metrics for that sequence rather than crashing.
  ISSUE-08: Guard added before pl.DataFrame() for the empty-rows case.
"""

from pathlib import Path
from typing import Optional, List
import math
import logging

import numpy as np
import polars as pl

from .parser import parse_label_file, get_sequence_label_files
from .data_loader import load_radar_cube, load_lidar_points
from .calibration import get_camera_params, load_camera_calibration
from .radar_visibility import compute_radar_sparsity_score
from .lidar_visibility import calculate_lidar_visibility
from .camera_visibility import calculate_camera_visibility, project_point_to_image
from .config import (
    RADAR_FOV_AZIMUTH_DEG, RADAR_FOV_ELEVATION_DEG, RADAR_MAX_RANGE_M,
    OS2_64_CHANNELS, OS2_64_VFOV_DEG, OS2_64_HRES_DEG,
    OS1_128_CHANNELS, OS1_128_VFOV_DEG, OS1_128_HRES_DEG,
)

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Radar zyx_cube grid parameters
# ISSUE-04: Document assumed values here.  Verify by running:
#   import scipy.io
#   mat = scipy.io.loadmat("<dataset>/data/1/radar_zyx_cube/cube_00001.mat")
#   key = [k for k in mat if not k.startswith("__")][0]
#   print(mat[key].shape)   # must print (RADAR_GRID_Z, RADAR_GRID_Y, RADAR_GRID_X)
# Update the six constants below if the shape differs.
# ---------------------------------------------------------------------------
RADAR_Z_MIN, RADAR_Z_MAX = -30.0, 30.0   # meters
RADAR_Y_MIN, RADAR_Y_MAX = -80.0, 80.0   # meters
RADAR_X_MIN, RADAR_X_MAX = 0.0, 100.0    # meters
RADAR_GRID_Z, RADAR_GRID_Y, RADAR_GRID_X = 150, 400, 250

# ---------------------------------------------------------------------------
# LiDAR expected-density constants (§4.2 method B)
# Approximate theoretical point count that would strike a 1-m² surface at
# the given sensor's angular resolution — used to normalise raw counts into
# a 0-1 sparsity score.
# ---------------------------------------------------------------------------
_EXPECTED_OS2 = (OS2_64_CHANNELS * OS2_64_VFOV_DEG / 360.0) * (360.0 / OS2_64_HRES_DEG)
_EXPECTED_OS1 = (OS1_128_CHANNELS * OS1_128_VFOV_DEG / 360.0) * (360.0 / OS1_128_HRES_DEG)

# LiDAR FOV limits [x_min, x_max, y_min, y_max] in meters (center-point check)
_LIDAR_FOV = [-200.0, 200.0, -200.0, 200.0]  # effectively no FOV cutoff
_LIDAR_RANGE = [0.0, 120.0]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _world_to_voxel(x: float, y: float, z: float):
    """Convert world (meter) coords to radar zyx_cube integer voxel indices."""
    vx = int((x - RADAR_X_MIN) / (RADAR_X_MAX - RADAR_X_MIN) * (RADAR_GRID_X - 1))
    vy = int((y - RADAR_Y_MIN) / (RADAR_Y_MAX - RADAR_Y_MIN) * (RADAR_GRID_Y - 1))
    vz = int((z - RADAR_Z_MIN) / (RADAR_Z_MAX - RADAR_Z_MIN) * (RADAR_GRID_Z - 1))
    vx = max(0, min(RADAR_GRID_X - 1, vx))
    vy = max(0, min(RADAR_GRID_Y - 1, vy))
    vz = max(0, min(RADAR_GRID_Z - 1, vz))
    return vz, vy, vx


def _radar_fov_check(x: float, y: float, z: float) -> bool:
    """True if (x, y, z) is inside the radar's azimuth/elevation cone."""
    range_xy = math.sqrt(x**2 + y**2)
    if range_xy < 1e-6:
        return True
    azimuth = math.degrees(math.atan2(y, x))
    elevation = math.degrees(math.atan2(z, range_xy))
    return (abs(azimuth) <= RADAR_FOV_AZIMUTH_DEG / 2.0 and
            abs(elevation) <= RADAR_FOV_ELEVATION_DEG / 2.0)


def _radar_range_check(x: float, y: float, z: float) -> bool:
    """True if (x, y, z) is within 0–118 m of the radar origin."""
    return math.sqrt(x**2 + y**2 + z**2) <= RADAR_MAX_RANGE_M


def _obj_corners(obj) -> np.ndarray:
    """Return the 8 world-frame corners of a rotated 3D bbox as (8, 3)."""
    cx, cy, cz = obj.x, obj.y, obj.z
    hl, hw, hh = obj.length_half, obj.width_half, obj.height_half

    local = np.array([
        [-hl, -hw, -hh], [-hl, -hw,  hh], [-hl,  hw, -hh], [-hl,  hw,  hh],
        [ hl, -hw, -hh], [ hl, -hw,  hh], [ hl,  hw, -hh], [ hl,  hw,  hh],
    ], dtype=np.float64)

    cos_t, sin_t = math.cos(obj.theta), math.sin(obj.theta)
    R = np.array([[cos_t, -sin_t, 0],
                  [sin_t,  cos_t, 0],
                  [0,      0,     1]], dtype=np.float64)

    return (R @ local.T).T + np.array([cx, cy, cz])


def _bbox_voxels_from_annotation(obj) -> dict:
    """AABB of a rotated bbox in voxel space.

    FIX ISSUE-03: Uses all 8 rotated world-frame corners to compute the
    axis-aligned bounding box, then converts to voxel indices.  The original
    code expanded the bbox axis-aligned using raw half-extents, which is only
    correct when theta==0.
    """
    corners = _obj_corners(obj)
    voxels = [_world_to_voxel(float(c[0]), float(c[1]), float(c[2])) for c in corners]
    vz = [v[0] for v in voxels]
    vy = [v[1] for v in voxels]
    vx = [v[2] for v in voxels]
    return {
        'z_min': min(vz), 'z_max': max(vz),
        'y_min': min(vy), 'y_max': max(vy),
        'x_min': min(vx), 'x_max': max(vx),
    }


def _bbox_list_from_annotation(obj) -> list:
    """Axis-aligned bbox as [xmin, xmax, ymin, ymax, zmin, zmax] in meters."""
    corners = _obj_corners(obj)
    return [
        float(corners[:, 0].min()), float(corners[:, 0].max()),
        float(corners[:, 1].min()), float(corners[:, 1].max()),
        float(corners[:, 2].min()), float(corners[:, 2].max()),
    ]


def _assert_radar_cube_shape(cube: np.ndarray):
    """ISSUE-04: Runtime guard — warn loudly if the .mat shape doesn't match constants."""
    expected = (RADAR_GRID_Z, RADAR_GRID_Y, RADAR_GRID_X)
    if cube.shape != expected:
        log.warning(
            "radar_zyx_cube shape %s does not match expected %s. "
            "Update RADAR_GRID_Z/Y/X and RADAR_*_MIN/MAX constants in pipeline.py.",
            cube.shape, expected,
        )


# ---------------------------------------------------------------------------
# Per-frame visibility computation
# ---------------------------------------------------------------------------

def compute_visibility_for_frame(sequence_id, header, objects, dataset_root,
                                  calib_available: bool = True):
    """Compute all visibility metrics for every object in one frame.

    Args:
        sequence_id:       Sequence folder name (string).
        header:            HeaderInfo from parser.
        objects:           List of ObjectAnnotation from parser.
        dataset_root:      Path to K-Radar dataset root.
        calib_available:   Set to False when calibration failed to load for
                           this sequence; camera metrics will be zeroed out.

    Returns:
        List of row dicts (one per object).
    """
    rows = []

    # --- Load sensor data for this frame ---
    radar_cube = load_radar_cube(sequence_id, header.tesseract_idx, dataset_root)
    os2_points = load_lidar_points(sequence_id, header.os2_64_idx, "os2-64", dataset_root)
    os1_points = load_lidar_points(sequence_id, header.os1_128_idx, "os1-128", dataset_root)

    # ISSUE-04: validate radar cube shape once per frame (only when file exists)
    if radar_cube is not None:
        _assert_radar_cube_shape(radar_cube)

    seq_int = int(sequence_id) if sequence_id.isdigit() else 1

    for obj in objects:
        # ------------------------------------------------------------------ #
        # Radar                                                                #
        # ------------------------------------------------------------------ #
        radar_fov_in = _radar_fov_check(obj.x, obj.y, obj.z)
        radar_range_in = _radar_range_check(obj.x, obj.y, obj.z)
        radar_visible = radar_fov_in and radar_range_in

        radar_score = 0.0
        if radar_visible and radar_cube is not None:
            try:
                bbox = _bbox_voxels_from_annotation(obj)
                if (bbox['z_max'] > bbox['z_min'] and
                        bbox['y_max'] > bbox['y_min'] and
                        bbox['x_max'] > bbox['x_min']):
                    radar_score = float(compute_radar_sparsity_score(radar_cube, bbox))
            except Exception as exc:
                log.debug("radar score failed for obj %s: %s", obj.tracking_id, exc)
                radar_score = 0.0

        # ------------------------------------------------------------------ #
        # LiDAR                                                                #
        # ISSUE-01: call calculate_lidar_visibility once per cloud, read       #
        #           only [0][0], [1][0], [2][0] from each result.              #
        # ------------------------------------------------------------------ #
        bbox_list = [_bbox_list_from_annotation(obj)]

        lidar64_visible = False
        lidar64_points = 0
        lidar64_score = 0.0
        if os2_points is not None and len(os2_points) > 0:
            try:
                vis, cnt, sco = calculate_lidar_visibility(
                    os2_points, bbox_list,
                    fov=_LIDAR_FOV, range_limit=_LIDAR_RANGE,
                    expected_density=_EXPECTED_OS2,
                )
                lidar64_visible = bool(vis[0])
                lidar64_points = int(cnt[0])
                lidar64_score = float(sco[0])
            except Exception as exc:
                log.debug("lidar64 failed for obj %s: %s", obj.tracking_id, exc)

        lidar128_visible = False
        lidar128_points = 0
        lidar128_score = 0.0
        if os1_points is not None and len(os1_points) > 0:
            try:
                vis, cnt, sco = calculate_lidar_visibility(
                    os1_points, bbox_list,
                    fov=_LIDAR_FOV, range_limit=_LIDAR_RANGE,
                    expected_density=_EXPECTED_OS1,
                )
                lidar128_visible = bool(vis[0])
                lidar128_points = int(cnt[0])
                lidar128_score = float(sco[0])
            except Exception as exc:
                log.debug("lidar128 failed for obj %s: %s", obj.tracking_id, exc)

        # ------------------------------------------------------------------ #
        # Camera                                                               #
        # ISSUE-07: skip gracefully when calibration unavailable.              #
        # ------------------------------------------------------------------ #
        cam_front_visible = False
        cam_left_visible = False
        cam_right_visible = False
        cam_rear_visible = False
        cam_front_proj_x: Optional[float] = None
        cam_front_proj_y: Optional[float] = None
        cam_left_proj_x: Optional[float] = None
        cam_left_proj_y: Optional[float] = None
        cam_right_proj_x: Optional[float] = None
        cam_right_proj_y: Optional[float] = None
        cam_rear_proj_x: Optional[float] = None
        cam_rear_proj_y: Optional[float] = None
        cam_scores = {'front': 0.0, 'left': 0.0, 'right': 0.0, 'rear': 0.0}

        if calib_available:
            corners = _obj_corners(obj)
            try:
                cam_scores = calculate_camera_visibility(corners, seq=seq_int)
            except Exception as exc:
                log.debug("camera visibility failed for obj %s: %s", obj.tracking_id, exc)

            cam_front_visible = cam_scores['front'] > 0
            cam_left_visible = cam_scores['left'] > 0
            cam_right_visible = cam_scores['right'] > 0
            cam_rear_visible = cam_scores['rear'] > 0

            # Project object center for proj_x/y columns
            center_point = np.array([[obj.x, obj.y, obj.z]], dtype=np.float64)
            for direction in ['front', 'left', 'right', 'rear']:
                # Only store projection when the direction is actually visible
                dir_visible = cam_scores[direction] > 0
                if not dir_visible:
                    continue
                try:
                    params_list = get_camera_params(direction, seq=seq_int)
                    params = params_list[0]  # use first stereo sub-camera for projection
                    u, v, z_cam = project_point_to_image(
                        center_point,
                        params['camera_intrinsics'],
                        params['radar2camera'],
                    )
                    if z_cam[0] > 0:
                        u_val, v_val = float(u[0]), float(v[0])
                        # ISSUE-02: only store if visible (already guarded above)
                        if direction == 'front':
                            cam_front_proj_x, cam_front_proj_y = u_val, v_val
                        elif direction == 'left':
                            cam_left_proj_x, cam_left_proj_y = u_val, v_val
                        elif direction == 'right':
                            cam_right_proj_x, cam_right_proj_y = u_val, v_val
                        elif direction == 'rear':
                            cam_rear_proj_x, cam_rear_proj_y = u_val, v_val
                except Exception as exc:
                    log.debug("projection failed for %s obj %s: %s",
                              direction, obj.tracking_id, exc)

        # ------------------------------------------------------------------ #
        # Primary sensor / sensor count                                        #
        # ------------------------------------------------------------------ #
        visible_sensors = []
        if radar_visible:
            visible_sensors.append(('radar', radar_score))
        if lidar64_visible:
            visible_sensors.append(('lidar64', lidar64_score))
        if lidar128_visible:
            visible_sensors.append(('lidar128', lidar128_score))
        if cam_front_visible:
            visible_sensors.append(('cam_front', cam_scores['front']))
        if cam_left_visible:
            visible_sensors.append(('cam_left', cam_scores['left']))
        if cam_right_visible:
            visible_sensors.append(('cam_right', cam_scores['right']))
        if cam_rear_visible:
            visible_sensors.append(('cam_rear', cam_scores['rear']))

        num_sensors_visible = len(visible_sensors)
        primary_sensor = (
            max(visible_sensors, key=lambda x: x[1])[0]
            if num_sensors_visible > 0 else None
        )

        rows.append({
            'sequence_id': sequence_id,
            'frame_idx': int(header.tesseract_idx),
            'timestamp': header.timestamp,
            'obj_tracking_id': obj.tracking_id,
            'obj_class': obj.obj_class,
            'obj_x': obj.x,
            'obj_y': obj.y,
            'obj_z': obj.z,
            'obj_theta': obj.theta,
            'obj_length': obj.length,
            'obj_width': obj.width,
            'obj_height': obj.height,
            'obj_distance_ego': obj.distance_ego,
            'sensor_identify': obj.sensor_identify,
            'radar_visible': radar_visible,
            'radar_fov_in': radar_fov_in,
            'radar_range_in': radar_range_in,
            'radar_sparsity_score': radar_score,
            'lidar64_visible': lidar64_visible,
            'lidar64_points_count': lidar64_points,
            'lidar64_sparsity_score': lidar64_score,
            'lidar128_visible': lidar128_visible,
            'lidar128_points_count': lidar128_points,
            'lidar128_sparsity_score': lidar128_score,
            'cam_front_visible': cam_front_visible,
            'cam_front_proj_x': cam_front_proj_x,
            'cam_front_proj_y': cam_front_proj_y,
            'cam_front_visibility_score': cam_scores['front'],
            'cam_left_visible': cam_left_visible,
            'cam_left_proj_x': cam_left_proj_x,
            'cam_left_proj_y': cam_left_proj_y,
            'cam_left_visibility_score': cam_scores['left'],
            'cam_right_visible': cam_right_visible,
            'cam_right_proj_x': cam_right_proj_x,
            'cam_right_proj_y': cam_right_proj_y,
            'cam_right_visibility_score': cam_scores['right'],
            'cam_rear_visible': cam_rear_visible,
            'cam_rear_proj_x': cam_rear_proj_x,
            'cam_rear_proj_y': cam_rear_proj_y,
            'cam_rear_visibility_score': cam_scores['rear'],
            'num_sensors_visible': num_sensors_visible,
            'primary_sensor': primary_sensor,
        })

    return rows


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run(
    sequence_ids: List[str],
    frame_limit: Optional[int] = None,
    dataset_root: Optional[Path] = None,
    output_path: Optional[Path] = None,
) -> pl.DataFrame:
    """Run the full visibility pipeline.

    Args:
        sequence_ids: Sequence folder names to process (e.g. ["1", "2"]).
        frame_limit:  Max label files per sequence; None = all.
        dataset_root: K-Radar dataset root.  Defaults to config value.
        output_path:  If provided, write the result as Parquet here.

    Returns:
        Polars DataFrame with one row per (frame, object).
    """
    from .config import DATASET_ROOT  # import here to allow override via arg

    if dataset_root is None:
        dataset_root = DATASET_ROOT

    all_rows: List[dict] = []

    for seq_id in sequence_ids:
        # ISSUE-07: pre-check calibration availability for this sequence
        calib_available = True
        try:
            load_camera_calibration(seq=int(seq_id) if seq_id.isdigit() else 1)
        except Exception as exc:
            log.warning("Calibration unavailable for sequence %s (%s). "
                        "Camera metrics will be zeroed.", seq_id, exc)
            calib_available = False

        label_files = get_sequence_label_files(seq_id, dataset_root)
        if frame_limit:
            annotated = []
            for f in label_files:
                if len(annotated) >= frame_limit:
                    break
                try:
                    _, objects = parse_label_file(f)
                    if objects:
                        annotated.append(f)
                except Exception:
                    continue
            label_files = annotated

        for label_file in label_files:
            try:
                header, objects = parse_label_file(label_file)
                rows = compute_visibility_for_frame(
                    seq_id, header, objects, dataset_root,
                    calib_available=calib_available,
                )
                all_rows.extend(rows)
            except Exception as exc:
                log.warning("Skipping %s: %s", label_file, exc)

    # ISSUE-08: guard against empty result
    if not all_rows:
        log.warning("No rows produced. Check dataset_root and sequence_ids.")
        return pl.DataFrame()

    df = pl.DataFrame(all_rows, schema_overrides={
        'cam_front_proj_x': pl.Float64,
        'cam_front_proj_y': pl.Float64,
        'cam_left_proj_x':  pl.Float64,
        'cam_left_proj_y':  pl.Float64,
        'cam_right_proj_x': pl.Float64,
        'cam_right_proj_y': pl.Float64,
        'cam_rear_proj_x':  pl.Float64,
        'cam_rear_proj_y':  pl.Float64,
    })

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.write_parquet(output_path)
        log.info("Wrote %d rows to %s", df.height, output_path)
        print(f"Wrote {df.height} rows to {output_path}")

    return df
