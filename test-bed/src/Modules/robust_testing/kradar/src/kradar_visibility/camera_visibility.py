"""Camera visibility metrics for all four cameras (front/left/right/rear).

Implements §4.3 method B: 8-corner projection → 2D bbox → area/centrality score.

Changes vs. original:
  ISSUE-06: Removed np.clip() from project_point_to_image().  Raw projected
            (u, v) values are now returned as-is so the pipeline can store
            true pixel coordinates as cam_*_proj_x/y.  Clipping for the area
            calculation still happens inside calculate_visibility_score(), which
            is the correct place.
"""

import numpy as np
from .calibration import get_camera_params, CAMERA_MAP

# Image dimensions per stereo half
HALF_WIDTH = 1280
HALF_HEIGHT = 720

# Score weights (§4.3 method B)
W1 = 0.7   # projected-area weight
W2 = 0.3   # centrality weight


def project_point_to_image(point_3d, camera_intrinsics, T_radar2cam):
    """Project 3D radar-frame point(s) to 2D image pixel coordinates.

    FIX ISSUE-06: np.clip() removed.  Returns raw (u, v) so out-of-bounds
    projections are preserved — callers must not assume values are in-bounds.
    Use z_cam > 0 to gate on-camera checks; use the clipped area logic inside
    calculate_visibility_score() for score computation.

    Args:
        point_3d:          (3,) or (N, 3) array in radar coordinates.
        camera_intrinsics: 4×4 camera intrinsic matrix (K embedded in top-left 3×3).
        T_radar2cam:       4×4 extrinsic transform from radar frame to camera frame.

    Returns:
        u (N,), v (N,): raw pixel coordinates (may be outside image bounds).
        z_cam (N,):     depth in camera frame — positive means in front of camera.
    """
    pts = np.atleast_2d(point_3d).astype(np.float64)
    ones = np.ones((pts.shape[0], 1))
    pts_hom = np.hstack([pts, ones])           # N×4

    pts_cam = (T_radar2cam @ pts_hom.T).T      # N×4
    z_cam = pts_cam[:, 2]

    K = camera_intrinsics[:3, :3]
    uvw = (K @ pts_cam[:, :3].T).T            # N×3
    # Avoid division by zero for points exactly on the image plane
    denom = np.where(np.abs(uvw[:, 2]) > 1e-8, uvw[:, 2], 1e-8)
    u = uvw[:, 0] / denom
    v = uvw[:, 1] / denom

    return u, v, z_cam


def calculate_visibility_score(obj_corners, cam_params):
    """Camera visibility score for one object and one camera.

    Projects all 8 3D bbox corners, clips the resulting 2D bbox to image
    bounds, then scores by clipped-area fraction and centrality.

    Args:
        obj_corners: (8, 3) array of 3D corners in radar frame.
        cam_params:  Dict with 'camera_intrinsics' (4×4) and 'radar2camera' (4×4).

    Returns:
        float score in [0, 1].  0.0 means not visible (behind camera or outside FOV).
    """
    K = cam_params['camera_intrinsics']
    T = cam_params['radar2camera']

    u, v, z_cam = project_point_to_image(obj_corners, K, T)

    # Any corner behind camera → object not visible from this camera
    if np.any(z_cam <= 0):
        return 0.0

    # 2D projection bbox (raw, unclipped)
    x_min = float(np.min(u))
    x_max = float(np.max(u))
    y_min = float(np.min(v))
    y_max = float(np.max(v))

    # Clip to image bounds for area calculation
    x_min_c = max(0.0, x_min)
    y_min_c = max(0.0, y_min)
    x_max_c = min(float(HALF_WIDTH), x_max)
    y_max_c = min(float(HALF_HEIGHT), y_max)

    # Object projects completely outside the image
    if x_max_c <= x_min_c or y_max_c <= y_min_c:
        return 0.0

    area = (x_max_c - x_min_c) * (y_max_c - y_min_c)
    cx_proj = x_min_c + (x_max_c - x_min_c) / 2.0
    cy_proj = y_min_c + (y_max_c - y_min_c) / 2.0
    centrality = 1.0 - (
        abs(cx_proj - HALF_WIDTH / 2.0) + abs(cy_proj - HALF_HEIGHT / 2.0)
    ) / (HALF_WIDTH + HALF_HEIGHT)

    score = W1 * (area / (HALF_WIDTH * HALF_HEIGHT)) + W2 * centrality
    return float(score)


def calculate_camera_visibility(obj_corners, seq=1):
    """Calculate visibility scores for all four camera directions.

    Each direction has two stereo sub-cameras; score = max of the two.
    Returns a dict mapping direction → score.  A score > 0 means visible.

    Args:
        obj_corners: (8, 3) array of 3D corners in radar frame.
        seq:         Sequence ID (int) used to look up calibration.

    Returns:
        Dict with keys 'front', 'left', 'right', 'rear'.
    """
    scores = {}
    for direction in ['front', 'left', 'right', 'rear']:
        cam_params_list = get_camera_params(direction, seq=seq)
        s0 = calculate_visibility_score(obj_corners, cam_params_list[0])
        s1 = calculate_visibility_score(obj_corners, cam_params_list[1])
        scores[direction] = max(s0, s1)
    return scores
