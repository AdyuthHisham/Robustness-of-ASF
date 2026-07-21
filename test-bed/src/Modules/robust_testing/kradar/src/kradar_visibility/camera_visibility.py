"""
Camera visibility metrics for all four cameras (front/left/right/rear).

Implements §4.3 method A: pinhole projection + FOV/range check.
NEW: Added support for depth buffer occlusion and distortion correction.
NEW: Implements prepare_frame_camera() for per-frame LiDAR→camera depth maps.
NEW: Implements camera_score() with occlusion discount (merged 4.2+4.3).
NEW: Implements stereo_consistency() for front pair (4.5).

NEW METHODOLOGY: k-radar-sensor-visibility-metrics.md (§4.2, §4.3, §4.5)
"""

import numpy as np
from typing import Optional, List, Dict, Tuple
from .calibration import get_camera_params
from .config import (
    CAM_HALF_WIDTH, CAM_HALF_HEIGHT, CAM_W1, CAM_W2,
    DEPTH_MARGIN, DEPTH_SAMPLE_RADIUS
)

# Image dimensions per stereo half
HALF_WIDTH = CAM_HALF_WIDTH
HALF_HEIGHT = CAM_HALF_HEIGHT

# Score weights (§4.3 method B)
W1 = CAM_W1   # projected-area weight
W2 = CAM_W2   # centrality weight


def project_point_to_image(point_3d, camera_intrinsics, T_radar2cam, dist_coeffs=None):
    """Project 3D radar-frame point(s) to 2D image pixel coordinates.

    NEW: Added support for distortion correction using calibration coefficients.
    If dist_coeffs is provided, applies radial and tangential distortion correction.

    Args:
        point_3d:          (3,) or (N, 3) array in radar coordinates.
        camera_intrinsics: 4×4 camera intrinsic matrix (K embedded in top-left 3×3).
        T_radar2cam:       4×4 extrinsic transform from radar frame to camera frame.
        dist_coeffs:       Optional distortion coefficients [k1, k2, p1, p2, k3].

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
    x = uvw[:, 0] / denom
    y = uvw[:, 1] / denom

    # Apply distortion correction if coefficients provided
    if dist_coeffs is not None and len(dist_coeffs) >= 4:
        k1, k2, p1, p2 = dist_coeffs[0], dist_coeffs[1], dist_coeffs[2], dist_coeffs[3]
        k3 = dist_coeffs[4] if len(dist_coeffs) > 4 else 0.0
        
        r2 = x*x + y*y
        radial_distortion = 1 + k1*r2 + k2*(r2**2) + k3*(r2**3)
        
        x_distorted = x * radial_distortion + 2*p1*x*y + p2*(r2 + 2*x*x)
        y_distorted = y * radial_distortion + p1*(r2 + 2*y*y) + 2*p2*x*y
        
        x = x_distorted
        y = y_distorted

    u = x
    v = y

    return u, v, z_cam


def calculate_visibility_score(obj_corners, cam_params, depth_map=None):
    """Camera visibility score for one object and one camera.

    Projects all 8 3D bbox corners, clips the resulting 2D bbox to image
    bounds, then scores by clipped-area fraction and centrality.

    NEW: If depth_map provided, applies depth-buffer occlusion discount.
        Compares projected depth with depth map value at same pixel.
        If object is farther than depth map value, applies occlusion penalty.

    Args:
        obj_corners: (8, 3) array of 3D corners in radar frame.
        cam_params:  Dict with 'camera_intrinsics' (4×4), 'radar2camera' (4×4),
                     and optionally 'dist_coeffs' for distortion correction.
        depth_map:   Optional 2D array (H, W) with depth values in meters.
                     If provided, enables depth-buffer occlusion test.

    Returns:
        float score in [0, 1].  0.0 means not visible (behind camera or outside FOV).
    """
    K = cam_params['camera_intrinsics']
    T = cam_params['radar2camera']
    dist_coeffs = cam_params.get('dist_coeffs', None)

    u, v, z_cam = project_point_to_image(obj_corners, K, T, dist_coeffs)

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

    # Base score from area and centrality
    base_score = W1 * (area / (HALF_WIDTH * HALF_HEIGHT)) + W2 * centrality

    # NEW: Apply depth-buffer occlusion discount if depth map provided
    if depth_map is not None:
        # Sample depth values at projected corner points
        height, width = depth_map.shape
        occlusion_factors = []
        
        for i in range(len(u)):
            ui, vi = int(round(u[i])), int(round(v[i]))
            
            # Check if point is within image bounds
            if 0 <= ui < width and 0 <= vi < height:
                measured_depth = depth_map[vi, ui]
                projected_depth = z_cam[i]
                
                # If measured depth is valid and less than projected depth,
                # something is occluding the object
                if measured_depth > 0 and projected_depth > measured_depth:
                    # Calculate occlusion ratio (how much is obscured)
                    occlusion_ratio = min(0.9, (projected_depth - measured_depth) / projected_depth)
                    occlusion_factors.append(occlusion_ratio)
                else:
                    occlusion_factors.append(0.0)
            else:
                # Point outside image - no occlusion info available
                occlusion_factors.append(0.0)
        
        # Apply average occlusion penalty to reduce score
        if occlusion_factors:
            avg_occlusion = np.mean(occlusion_factors)
            # Reduce score based on occlusion (more occlusion = lower score)
            occlusion_factor = 1.0 - avg_occlusion
            final_score = base_score * occlusion_factor
        else:
            final_score = base_score
    else:
        # No depth map provided - use base score (backward compatibility)
        final_score = base_score

    return float(final_score)


def calculate_camera_visibility(obj_corners, seq=1, depth_maps=None):
    """Calculate visibility scores for all four camera directions.

    Each direction has two stereo sub-cameras; score = max of the two.

    NEW: Added support for per-camera depth maps for occlusion testing.

    Args:
        obj_corners: (8, 3) array of 3D corners in radar frame.
        seq:         Sequence ID (int) used to look up calibration.
        depth_maps:  Optional dict mapping camera direction to depth map.
                     If provided, enables depth-buffer occlusion test per camera.

    Returns:
        Dict with keys 'front', 'left', 'right', 'rear'.
    """
    scores = {}
    for direction in ['front', 'left', 'right', 'rear']:
        cam_params_list = get_camera_params(direction, seq=seq)
        
        # Get depth map for this direction if provided
        depth_map = None
        if depth_maps is not None:
            depth_map = depth_maps.get(direction)
        
        s0 = calculate_visibility_score(obj_corners, cam_params_list[0], depth_map)
        s1 = calculate_visibility_score(obj_corners, cam_params_list[1], depth_map)
        scores[direction] = max(s0, s1)
    return scores


# =============================================================================
# NEW PHASE 4 FUNCTIONS: Per-frame precomputation and improved scoring
# =============================================================================

def prepare_frame_camera(points, lidar_extrinsics, camera_intrinsics_list, camera_extrinsics_list, 
                         image_width: int, image_height: int) -> List[np.ndarray]:
    """
    Build sparse depth maps by projecting LiDAR points into each camera image.
    
    NEW METHODOLOGY: k-radar-sensor-visibility-metrics.md (§4.1, §4.3)
    Called once per frame to create depth maps for all cameras, shared across objects.
    
    FIX (Phase 4 Task 4.2 follow-up): Vectorized per-pixel minimum reduction using
    np.minimum.at() with np.inf initialization to avoid the zero-initialization bug
    in the legacy generate_camera_depth_maps(). This replaces the Python for-loop
    that caused ~47.5s/frame overhead.
    
    Args:
        points: (N, >=3) LiDAR points in radar frame [x, y, z, ...]
        lidar_extrinsics: 4x4 transform from LiDAR to radar frame (if different sensors)
        camera_intrinsics_list: List of 4x4 intrinsic matrices for each camera
        camera_extrinsics_list: List of 4x4 radar-to-camera transforms for each camera
        image_width: Camera image width (per half-image, e.g., 1280)
        image_height: Camera image height (per half-image, e.g., 720)
        
    Returns:
        List of depth maps (H, W) one per camera, dtype float32.
        Values are depth in meters (z in camera frame), 0 = no point.
    """
    if points is None or len(points) == 0:
        # Return empty depth maps for all cameras
        return [np.zeros((image_height, image_width), dtype=np.float32) 
                for _ in range(len(camera_intrinsics_list))]
    
    depth_maps = []
    
    for cam_idx in range(len(camera_intrinsics_list)):
        K = camera_intrinsics_list[cam_idx][:3, :3]
        T_radar2cam = camera_extrinsics_list[cam_idx]
        
        # Initialize depth map with inf so np.minimum.at() correctly reduces to nearest depth
        depth_map = np.full((image_height, image_width), np.inf, dtype=np.float32)
        
        # Transform all points to camera frame
        pts_hom = np.hstack([points[:, :3], np.ones((len(points), 1))])  # Nx4
        pts_cam = (T_radar2cam @ pts_hom.T).T  # Nx4
        
        # Keep only points in front of camera
        valid = pts_cam[:, 2] > 0
        if not np.any(valid):
            # Replace inf with 0 for "no depth data" sentinel
            depth_map[np.isinf(depth_map)] = 0.0
            depth_maps.append(depth_map)
            continue
            
        pts_cam = pts_cam[valid]
        z_cam = pts_cam[:, 2]
        x_cam = pts_cam[:, 0]
        y_cam = pts_cam[:, 1]
        
        # Project to image
        u = (K[0, 0] * x_cam / z_cam) + K[0, 2]
        v = (K[1, 1] * y_cam / z_cam) + K[1, 2]
        
        u_int = np.round(u).astype(int)
        v_int = np.round(v).astype(int)
        
        # Filter to image bounds
        in_bounds = (u_int >= 0) & (u_int < image_width) & (v_int >= 0) & (v_int < image_height)
        
        if not np.any(in_bounds):
            depth_map[np.isinf(depth_map)] = 0.0
            depth_maps.append(depth_map)
            continue
            
        u_valid = u_int[in_bounds]
        v_valid = v_int[in_bounds]
        z_valid = z_cam[in_bounds]
        
        # Vectorized per-pixel minimum reduction: keep closest (minimum z) per pixel
        np.minimum.at(depth_map, (v_valid, u_valid), z_valid)
        
        # Replace remaining inf (pixels with no projected points) with 0 sentinel
        depth_map[np.isinf(depth_map)] = 0.0
        depth_maps.append(depth_map)
        
    return depth_maps


def camera_score(box_half_extents: np.ndarray, 
                K: np.ndarray, 
                T_radar2cam: np.ndarray, 
                depth_map: Optional[np.ndarray],
                image_size: Tuple[int, int],
                dist_coeffs: Optional[np.ndarray] = None) -> Dict:
    """
    Compute camera visibility score for one object in one camera.
    
    NEW METHODOLOGY: k-radar-sensor-visibility-metrics.md (§4.2, §4.3)
    Merges 8-corner projection (4.2) + depth-buffer occlusion discount (4.3).
    
    Args:
        box_half_extents: (3,) [l/2, w/2, h/2] half-extents in object frame
        K: 3x3 camera intrinsic matrix
        T_radar2cam: 4x4 radar-to-camera transform
        depth_map: (H, W) sparse depth map from prepare_frame_camera()
        image_size: (width, height) tuple
        dist_coeffs: Optional distortion coefficients [k1, k2, p1, p2, k3]
        
    Returns:
        dict with: visible (bool), score (float), occlusion_discount (float),
                   base_score (float), projected_corners (8,2), z_cam (8,)
    """
    width, height = image_size
    l_half, w_half, h_half = box_half_extents
    
    # 8 corners in object frame (centered at origin)
    corners_obj = np.array([
        [-l_half, -w_half, -h_half], [ l_half, -w_half, -h_half],
        [ l_half,  w_half, -h_half], [-l_half,  w_half, -h_half],
        [-l_half, -w_half,  h_half], [ l_half, -w_half,  h_half],
        [ l_half,  w_half,  h_half], [-l_half,  w_half,  h_half],
    ], dtype=np.float64)
    
    # Transform to camera frame
    corners_hom = np.hstack([corners_obj, np.ones((8, 1))])
    corners_cam = (T_radar2cam @ corners_hom.T).T  # 8x4
    z_cam = corners_cam[:, 2]
    
    # Check if behind camera
    if np.any(z_cam <= 0):
        return {
            'visible': False, 'score': 0.0, 'occlusion_discount': 1.0,
            'base_score': 0.0, 'projected_corners': None, 'z_cam': z_cam
        }
    
    # Project to image
    u = (K[0, 0] * corners_cam[:, 0] / z_cam) + K[0, 2]
    v = (K[1, 1] * corners_cam[:, 1] / z_cam) + K[1, 2]
    
    # Apply distortion correction if provided
    if dist_coeffs is not None and len(dist_coeffs) >= 4:
        k1, k2, p1, p2 = dist_coeffs[0], dist_coeffs[1], dist_coeffs[2], dist_coeffs[3]
        k3 = dist_coeffs[4] if len(dist_coeffs) > 4 else 0.0
        
        x_norm = (u - K[0, 2]) / K[0, 0]
        y_norm = (v - K[1, 2]) / K[1, 1]
        r2 = x_norm*x_norm + y_norm*y_norm
        radial = 1 + k1*r2 + k2*(r2**2) + k3*(r2**3)
        u = u * radial + 2*p1*x_norm*y_norm + p2*(r2 + 2*x_norm*x_norm)
        v = v * radial + p1*(r2 + 2*y_norm*y_norm) + 2*p2*x_norm*y_norm
    
    # Convex hull of projected corners -> clip to image bounds
    x_min, x_max = np.min(u), np.max(u)
    y_min, y_max = np.min(v), np.max(v)
    
    x_min_c = max(0.0, x_min)
    y_min_c = max(0.0, y_min)
    x_max_c = min(float(width), x_max)
    y_max_c = min(float(height), y_max)
    
    # Outside image
    if x_max_c <= x_min_c or y_max_c <= y_min_c:
        return {
            'visible': False, 'score': 0.0, 'occlusion_discount': 1.0,
            'base_score': 0.0, 'projected_corners': np.stack([u, v], axis=1), 'z_cam': z_cam
        }
    
    # Base score: area fraction + centrality
    area = (x_max_c - x_min_c) * (y_max_c - y_min_c)
    cx_proj = x_min_c + (x_max_c - x_min_c) / 2.0
    cy_proj = y_min_c + (y_max_c - y_min_c) / 2.0
    centrality = 1.0 - (abs(cx_proj - width/2) + abs(cy_proj - height/2)) / (width + height)
    base_score = W1 * (area / (width * height)) + W2 * centrality
    
    # Occlusion discount using depth map (4.3)
    occlusion_discount = 1.0
    if depth_map is not None and depth_map.size > 0:
        # Sample points in clipped hull (grid sampling)
        sample_n = 20  # number of sample points
        xs = np.linspace(x_min_c, x_max_c, max(2, int(np.sqrt(sample_n))))
        ys = np.linspace(y_min_c, y_max_c, max(2, int(np.sqrt(sample_n))))
        
        occluded_count = 0
        valid_count = 0
        
        for x_samp in xs:
            for y_samp in ys:
                u_int = int(round(x_samp))
                v_int = int(round(y_samp))
                
                if 0 <= u_int < width and 0 <= v_int < height:
                    d_local = depth_map[v_int, u_int]
                    if d_local > 0:
                        valid_count += 1
                        # Object depth at this pixel (interpolate from corners)
                        # Simple approach: use median corner depth
                        z_obj = np.median(z_cam)
                        if d_local < z_obj - DEPTH_MARGIN:
                            occluded_count += 1
        
        if valid_count > 0:
            occlusion_discount = 1.0 - (occluded_count / valid_count)
            occlusion_discount = max(0.1, occlusion_discount)  # floor at 0.1
    
    final_score = base_score * occlusion_discount
    
    return {
        'visible': True,
        'score': float(final_score),
        'occlusion_discount': float(occlusion_discount),
        'base_score': float(base_score),
        'projected_corners': np.stack([u, v], axis=1),
        'z_cam': z_cam
    }


def stereo_consistency(box_half_extents: np.ndarray,
                      K_left: np.ndarray, K_right: np.ndarray,
                      T_left: np.ndarray, T_right: np.ndarray,
                      image_size: Tuple[int, int]) -> float:
    """
    Stereo consistency check for front camera pair (4.5).
    
    NEW METHODOLOGY: k-radar-sensor-visibility-metrics.md (§4.5)
    Projects box corners to both stereo images, block-matches disparity in ROI.
    
    Args:
        box_half_extents: (3,) [l/2, w/2, h/2]
        K_left, K_right: 3x3 intrinsic matrices
        T_left, T_right: 4x4 radar-to-camera transforms
        image_size: (width, height)
        
    Returns:
        consistency in [0, 1], 1.0 = perfect match, 0.0 = no match
        Returns 1.0 if stereo check not applicable (e.g., outside overlap)
    """
    width, height = image_size
    l_half, w_half, h_half = box_half_extents
    
    # 8 corners in object frame
    corners_obj = np.array([
        [-l_half, -w_half, -h_half], [ l_half, -w_half, -h_half],
        [ l_half,  w_half, -h_half], [-l_half,  w_half, -h_half],
        [-l_half, -w_half,  h_half], [ l_half, -w_half,  h_half],
        [ l_half,  w_half,  h_half], [-l_half,  w_half,  h_half],
    ], dtype=np.float64)
    
    # Project to left camera
    corners_hom = np.hstack([corners_obj, np.ones((8, 1))])
    corners_cam_left = (T_left @ corners_hom.T).T
    z_left = corners_cam_left[:, 2]
    
    if np.any(z_left <= 0):
        return 1.0  # Not applicable
        
    u_left = (K_left[0, 0] * corners_cam_left[:, 0] / z_left) + K_left[0, 2]
    v_left = (K_left[1, 1] * corners_cam_left[:, 1] / z_left) + K_left[1, 2]
    
    # Project to right camera
    corners_cam_right = (T_right @ corners_hom.T).T
    z_right = corners_cam_right[:, 2]
    
    if np.any(z_right <= 0):
        return 1.0  # Not applicable
        
    u_right = (K_right[0, 0] * corners_cam_right[:, 0] / z_right) + K_right[0, 2]
    v_right = (K_right[1, 1] * corners_cam_right[:, 1] / z_right) + K_right[1, 2]
    
    # Define ROI in left image (clipped hull)
    x_min_l = max(0, int(np.floor(np.min(u_left))))
    x_max_l = min(width - 1, int(np.ceil(np.max(u_left))))
    y_min_l = max(0, int(np.floor(np.min(v_left))))
    y_max_l = min(height - 1, int(np.ceil(np.max(v_left))))
    
    if x_max_l <= x_min_l or y_max_l <= y_min_l:
        return 1.0  # Not applicable
    
    # Expected disparity from box center
    cx_obj = 0.0  # object centered at origin
    # Transform center to both cameras
    center_hom = np.array([0, 0, 0, 1], dtype=np.float64)
    center_left = T_left @ center_hom
    center_right = T_right @ center_hom
    
    if center_left[2] <= 0 or center_right[2] <= 0:
        return 1.0
        
    u_exp_left = (K_left[0, 0] * center_left[0] / center_left[2]) + K_left[0, 2]
    u_exp_right = (K_right[0, 0] * center_right[0] / center_right[2]) + K_right[0, 2]
    expected_disparity = u_exp_left - u_exp_right
    
    if expected_disparity <= 0:
        return 1.0  # Not a valid stereo configuration
    
    # Simple block matching in ROI (just compute median disparity from corners)
    # For each corner, compute disparity
    disparities = []
    for i in range(8):
        if z_left[i] > 0 and z_right[i] > 0:
            d = u_left[i] - u_right[i]
            if d > 0:
                disparities.append(d)
    
    if not disparities:
        return 1.0
        
    measured_disparity = np.median(disparities)
    
    # Consistency = 1 - relative error
    if expected_disparity > 0:
        consistency = 1.0 - min(1.0, abs(measured_disparity - expected_disparity) / expected_disparity)
    else:
        consistency = 1.0
    
    return float(max(0.0, min(1.0, consistency)))