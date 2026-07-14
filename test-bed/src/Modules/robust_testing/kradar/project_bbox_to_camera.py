#!/usr/bin/env python3
"""
K-Radar 3D Bounding Box to Camera Image Projection

Projects 3D bounding boxes from K-Radar annotations onto camera images.
Uses existing calibration and parser utilities from the kradar_visibility package.
"""

import argparse
import math
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any
import numpy as np
import cv2

# Import from existing kradar_visibility modules
from src.kradar_visibility.parser import (
    parse_label_file,
    get_sequence_label_files,
    HeaderInfo,
    ObjectAnnotation,
)
from src.kradar_visibility.calibration import (
    load_camera_calibration,
    get_camera_params,
    CAMERA_MAP,
)
from src.kradar_visibility.data_loader import (
    load_camera_image,
    get_camera_image_path,
)

# Class colors for visualization (BGR format for OpenCV)
CLASS_COLORS = {
    'Sedan': (0, 255, 0),        # Green
    'Bus or Truck': (255, 0, 0), # Blue
    'Motorcycle': (0, 0, 255),   # Red
    'Bicycle': (0, 255, 255),    # Yellow
    'Pedestrian': (255, 0, 255), # Magenta
    'Unknown': (128, 128, 128),  # Gray
}


def get_class_color(obj_class: str) -> Tuple[int, int, int]:
    """Get BGR color for object class."""
    return CLASS_COLORS.get(obj_class, CLASS_COLORS['Unknown'])


def compute_3d_corners(obj: ObjectAnnotation) -> np.ndarray:
    """
    Compute 8 corners of 3D bounding box in radar/LiDAR coordinate frame.

    Args:
        obj: ObjectAnnotation with center, half-dimensions, and heading

    Returns:
        (8, 3) array of corner coordinates [X, Y, Z]
    """
    cx, cy, cz = obj.x, obj.y, obj.z
    hl, hw, hh = obj.length_half, obj.width_half, obj.height_half

    # Local corners (before rotation): all combinations of ±hl, ±hw, ±hh
    # Order matches the pipeline's _obj_corners for consistency
    local = np.array([
        [-hl, -hw, -hh], [-hl, -hw,  hh], [-hl,  hw, -hh], [-hl,  hw,  hh],
        [ hl, -hw, -hh], [ hl, -hw,  hh], [ hl,  hw, -hh], [ hl,  hw,  hh],
    ], dtype=np.float64)

    # Rotation around Z-axis by theta (heading in radians)
    cos_t, sin_t = math.cos(obj.theta), math.sin(obj.theta)
    R = np.array([
        [cos_t, -sin_t, 0],
        [sin_t,  cos_t, 0],
        [0,      0,     1],
    ], dtype=np.float64)

    # Rotate and translate
    corners = (R @ local.T).T + np.array([cx, cy, cz])
    return corners


def project_corners_to_image(
    corners_3d: np.ndarray,
    camera_intrinsics: np.ndarray,
    T_radar2cam: np.ndarray,
    apply_distortion: bool = False,
    dist_coeffs: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Project 3D corners from radar frame to 2D image plane.

    Args:
        corners_3d: (8, 3) array of 3D corners in radar frame
        camera_intrinsics: 4x4 camera intrinsic matrix (K in top-left 3x3)
        T_radar2cam: 4x4 extrinsic transform from radar to camera frame
        apply_distortion: Whether to apply lens distortion (requires dist_coeffs)
        dist_coeffs: Distortion coefficients [k1, k2, p1, p2, k3] if available

    Returns:
        u: (8,) array of pixel x coordinates
        v: (8,) array of pixel y coordinates
        z_cam: (8,) array of depths in camera frame
    """
    pts = corners_3d.astype(np.float64)
    ones = np.ones((pts.shape[0], 1))
    pts_hom = np.hstack([pts, ones])  # N x 4

    # Transform to camera frame
    pts_cam = (T_radar2cam @ pts_hom.T).T  # N x 4
    z_cam = pts_cam[:, 2]

    # Project using intrinsic matrix
    K = camera_intrinsics[:3, :3]
    uvw = (K @ pts_cam[:, :3].T).T  # N x 3

    # Avoid division by zero
    denom = np.where(np.abs(uvw[:, 2]) > 1e-8, uvw[:, 2], 1e-8)
    u = uvw[:, 0] / denom
    v = uvw[:, 1] / denom

    if apply_distortion and dist_coeffs is not None:
        # Use OpenCV's projectPoints for distortion
        # Need to convert to format expected by cv2.projectPoints
        rvec = np.zeros((3, 1), dtype=np.float64)  # No additional rotation
        tvec = np.zeros((3, 1), dtype=np.float64)  # Already in camera frame
        # cv2.projectPoints expects object points in world frame, we pass camera-frame points
        # So we use identity rotation and zero translation
        obj_pts = pts_cam[:, :3].reshape(-1, 1, 3).astype(np.float64)
        img_pts, _ = cv2.projectPoints(
            obj_pts, rvec, tvec, K.astype(np.float64), dist_coeffs.astype(np.float64)
        )
        u = img_pts[:, 0, 0]
        v = img_pts[:, 0, 1]

    return u, v, z_cam


def draw_3d_box(
    img: np.ndarray,
    u: np.ndarray,
    v: np.ndarray,
    z_cam: np.ndarray,
    color: Tuple[int, int, int],
    obj_class: str,
    tracking_id: int,
    line_thickness: int = 2,
    corner_radius: int = 4,
) -> np.ndarray:
    """
    Draw 3D bounding box wireframe on image.

    Args:
        img: Input image (BGR)
        u, v: (8,) arrays of projected pixel coordinates
        z_cam: (8,) depths in camera frame
        color: BGR color tuple
        obj_class: Object class name for label
        tracking_id: Object tracking ID
        line_thickness: Thickness of box edges
        corner_radius: Radius of corner circles

    Returns:
        Annotated image
    """
    # Only draw corners that are in front of the camera
    valid = z_cam > 0
    if not np.any(valid):
        return img

    u_valid = u[valid].astype(int)
    v_valid = v[valid].astype(int)

    # Edge connectivity for 3D box (using corner order from compute_3d_corners)
    # Corners indices:
    # 0: -l, -w, -h    1: -l, -w, +h    2: -l, +w, -h    3: -l, +w, +h
    # 4: +l, -w, -h    5: +l, -w, +h    6: +l, +w, -h    7: +l, +w, +h
    edges = [
        (0, 1), (1, 3), (3, 2), (2, 0),  # rear face (-l)
        (4, 5), (5, 7), (7, 6), (6, 4),  # front face (+l)
        (0, 4), (1, 5), (2, 6), (3, 7),  # vertical edges
    ]

    # Draw edges
    for i, j in edges:
        if valid[i] and valid[j]:
            pt1 = (u_valid[np.where(valid)[0].tolist().index(i)],
                   v_valid[np.where(valid)[0].tolist().index(j)])
            # Need to map back to original indices
            # Simpler: use the original arrays and check valid
            pt1 = (int(u[i]), int(v[i]))
            pt2 = (int(u[j]), int(v[j]))
            cv2.line(img, pt1, pt2, color, line_thickness, cv2.LINE_AA)

    # Draw corners
    for i in range(8):
        if valid[i]:
            cv2.circle(img, (int(u[i]), int(v[i])), corner_radius, color, -1, cv2.LINE_AA)

    # Draw label near the top-front corner (corner 5 = +l, -w, +h)
    if valid[5]:
        label_x = int(u[5])
        label_y = int(v[5]) - 10
        label_text = f"{obj_class} ID:{tracking_id}"
        cv2.putText(img, label_text, (label_x, label_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)

    return img


def process_frame(
    sequence_id: str,
    label_file: Path,
    camera: str = 'cam-front',
    output_dir: Optional[Path] = None,
    dataset_root: Optional[Path] = None,
    seq_int: Optional[int] = None,
    verbose: bool = False,
) -> Optional[Path]:
    """
    Process a single label file and project boxes onto camera image.
    Handles stereo camera pairs (left/right images side by side).

    Args:
        sequence_id: Sequence folder name (e.g., "1")
        label_file: Path to annotation .txt file
        camera: Camera name ('cam-front', 'cam-left', 'cam-right', 'cam-rear')
        output_dir: Directory to save annotated images
        dataset_root: K-Radar dataset root
        seq_int: Sequence ID as integer for calibration lookup
        verbose: Print detailed info

    Returns:
        Path to saved annotated image, or None if failed
    """
    if dataset_root is None:
        dataset_root = Path("/home/adhish/Productivity/AMSCUP/repos/K-Radar")

    if seq_int is None:
        seq_int = int(sequence_id) if sequence_id.isdigit() else 1

    # Parse annotations
    header, objects = parse_label_file(label_file)

    if verbose:
        print(f"\nProcessing: {label_file.name}")
        print(f"  Header: cam-front_idx={header.cam_front_idx}, timestamp={header.timestamp}")
        print(f"  Objects: {len(objects)}")

    # Determine camera direction from camera name
    cam_direction_map = {
        'cam-front': 'front',
        'cam-left': 'left',
        'cam-right': 'right',
        'cam-rear': 'rear',
    }
    direction = cam_direction_map.get(camera, 'front')

    # Load calibration for both stereo cameras
    try:
        cam_params_list = get_camera_params(direction, seq=seq_int)
        # cam_params_list[0] = left stereo (e.g., front0), [1] = right stereo (e.g., front1)
        cam_params_left = cam_params_list[0]
        cam_params_right = cam_params_list[1]
        K_left = cam_params_left['camera_intrinsics']
        K_right = cam_params_right['camera_intrinsics']
        T_left = cam_params_left['radar2camera']
        T_right = cam_params_right['radar2camera']
    except Exception as e:
        print(f"  ERROR: Failed to load calibration for {direction}: {e}")
        return None

    # Load camera image (full stereo pair: 2560x720 = 2x 1280x720)
    # Use cam_front_idx for cam-front, but find nearest available for other cameras
    cam_frame_idx = header.cam_front_idx if camera == 'cam-front' else header.cam_front_idx
    img = load_camera_image(sequence_id, cam_frame_idx, camera, dataset_root)
    if img is None:
        # Try to find the nearest available frame for this camera
        img_path = get_camera_image_path(sequence_id, cam_frame_idx, camera, dataset_root)
        if img_path is None:
            # Find nearest available frame
            cam_dir = dataset_root / "data" / sequence_id / camera
            if cam_dir.exists():
                available_frames = []
                for f in cam_dir.glob(f"{camera}_*.png"):
                    try:
                        frame_num = int(f.stem.split('_')[1])
                        available_frames.append(frame_num)
                    except:
                        pass
                if available_frames:
                    target = int(cam_frame_idx)
                    nearest = min(available_frames, key=lambda x: abs(x - target))
                    cam_frame_idx = f"{nearest:05d}"
                    img = load_camera_image(sequence_id, cam_frame_idx, camera, dataset_root)
                    if verbose:
                        print(f"  Using nearest frame {cam_frame_idx} for {camera} (target was {target})")
    if img is None:
        img_path = get_camera_image_path(sequence_id, cam_frame_idx, camera, dataset_root)
        if img_path is None:
            print(f"  ERROR: Camera image not found: {camera}_{cam_frame_idx}.png")
            return None
        img = cv2.imread(str(img_path))
        if img is None:
            print(f"  ERROR: Failed to load image: {img_path}")
            return None

    img_h, img_w = img.shape[:2]
    half_w = img_w // 2  # 1280 for stereo pair
    if verbose:
        print(f"  Image size: {img_w}x{img_h} (half={half_w}x{img_h})")

    # Split image into left and right stereo halves
    img_left = img[:, :half_w].copy()
    img_right = img[:, half_w:].copy()

    # Process each object
    num_projected = 0
    num_behind = 0
    num_outside = 0

    for obj in objects:
        # Compute 3D corners in radar frame
        corners_3d = compute_3d_corners(obj)

        if verbose and obj.tracking_id == objects[0].tracking_id:
            print(f"\n  Object {obj.tracking_id} ({obj.obj_class}):")
            print(f"    Center: ({obj.x:.3f}, {obj.y:.3f}, {obj.z:.3f})")
            print(f"    Half-dims: l={obj.length_half:.3f}, w={obj.width_half:.3f}, h={obj.height_half:.3f}")
            print(f"    Theta: {obj.theta:.3f} rad ({math.degrees(obj.theta):.1f} deg)")
            print(f"    3D Corners (radar frame):")
            for i, c in enumerate(corners_3d):
                print(f"      {i}: ({c[0]:.3f}, {c[1]:.3f}, {c[2]:.3f})")

        # Project to LEFT stereo camera
        u_l, v_l, z_l = project_corners_to_image(corners_3d, K_left, T_left)

        # Project to RIGHT stereo camera
        u_r, v_r, z_r = project_corners_to_image(corners_3d, K_right, T_right)

        if verbose and obj.tracking_id == objects[0].tracking_id:
            print(f"    LEFT camera coords (Z): {z_l}")
            print(f"    LEFT projected (u,v):")
            for i in range(8):
                status = "BEHIND" if z_l[i] <= 0 else "OK"
                print(f"      {i}: ({u_l[i]:.1f}, {v_l[i]:.1f}) Z={z_l[i]:.3f} {status}")
            print(f"    RIGHT camera coords (Z): {z_r}")
            print(f"    RIGHT projected (u,v):")
            for i in range(8):
                status = "BEHIND" if z_r[i] <= 0 else "OK"
                print(f"      {i}: ({u_r[i]:.1f}, {v_r[i]:.1f}) Z={z_r[i]:.3f} {status}")

        # Check visibility for left camera
        left_visible = np.all(z_l > 0) and np.any((u_l >= 0) & (u_l < half_w) & (v_l >= 0) & (v_l < img_h))
        right_visible = np.all(z_r > 0) and np.any((u_r >= 0) & (u_r < half_w) & (v_r >= 0) & (v_r < img_h))

        if not left_visible and not right_visible:
            if np.any(z_l <= 0) or np.any(z_r <= 0):
                num_behind += 1
                if verbose:
                    print(f"    Object {obj.tracking_id}: Behind camera")
            else:
                num_outside += 1
                if verbose:
                    print(f"    Object {obj.tracking_id}: Outside both camera FOVs")
        else:
            num_projected += 1
            color = get_class_color(obj.obj_class)
            # Draw on left half
            if left_visible:
                img_left = draw_3d_box(img_left, u_l, v_l, z_l, color, obj.obj_class, obj.tracking_id)
            # Draw on right half
            if right_visible:
                img_right = draw_3d_box(img_right, u_r, v_r, z_r, color, obj.obj_class, obj.tracking_id)

    # Recombine stereo image
    img = np.hstack([img_left, img_right])

    if verbose:
        print(f"  Summary: {num_projected} projected, {num_behind} behind camera, {num_outside} outside FOV")

    # Save annotated image
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        output_name = f"seq_{sequence_id}_{camera}_frame_{cam_frame_idx}_projected.png"
        output_path = output_dir / output_name
        cv2.imwrite(str(output_path), img)
        if verbose:
            print(f"  Saved: {output_path}")
        return output_path

    return None


def main():
    parser = argparse.ArgumentParser(
        description="Project K-Radar 3D bounding boxes onto camera images"
    )
    parser.add_argument(
        '--sequence', '-s', type=str, default='1',
        help='Sequence ID (folder name in data/)'
    )
    parser.add_argument(
        '--camera', '-c', type=str, default='cam-front',
        choices=['cam-front', 'cam-left', 'cam-right', 'cam-rear', 'all'],
        help='Camera to project onto (use "all" for all 4 cameras)'
    )
    parser.add_argument(
        '--frames', '-f', type=int, default=3,
        help='Number of frames to process (from start of sequence)'
    )
    parser.add_argument(
        '--output-dir', '-o', type=str, default='output/projections',
        help='Output directory for annotated images'
    )
    parser.add_argument(
        '--dataset-root', '-d', type=str,
        default='/home/adhish/Productivity/AMSCUP/repos/K-Radar',
        help='K-Radar dataset root'
    )
    parser.add_argument(
        '--verbose', '-v', action='store_true',
        help='Print detailed projection info for first object'
    )
    parser.add_argument(
        '--specific-frame', type=str,
        help='Process a specific frame (e.g., "00132_00100") instead of first N frames'
    )

    args = parser.parse_args()

    dataset_root = Path(args.dataset_root)
    output_dir = Path(args.output_dir)
    seq_id = args.sequence

    # Determine which cameras to process
    all_cameras = ['cam-front', 'cam-left', 'cam-right', 'cam-rear']
    if args.camera == 'all':
        cameras = all_cameras
    else:
        cameras = [args.camera]

    # Get label files
    label_files = get_sequence_label_files(seq_id, dataset_root)
    if not label_files:
        print(f"No label files found for sequence {seq_id}")
        return

    # Filter to specific frame if requested
    if args.specific_frame:
        label_files = [f for f in label_files if args.specific_frame in f.name]
        if not label_files:
            print(f"Frame {args.specific_frame} not found in sequence {seq_id}")
            return

    # Limit number of frames
    label_files = label_files[:args.frames]

    print(f"Processing {len(label_files)} frame(s) from sequence {seq_id}")
    print(f"Cameras: {cameras}")
    print(f"Output: {output_dir}")

    for label_file in label_files:
        for camera in cameras:
            process_frame(
                sequence_id=seq_id,
                label_file=label_file,
                camera=camera,
                output_dir=output_dir,
                dataset_root=dataset_root,
                verbose=args.verbose,
            )

    print("Done!")


if __name__ == '__main__':
    main()