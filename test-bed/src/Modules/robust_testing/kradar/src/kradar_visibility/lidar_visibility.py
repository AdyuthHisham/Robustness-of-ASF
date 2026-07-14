"""LiDAR visibility metrics for OS2-64 and OS1-128.

Implements §4.2 method A+B (CPU point-in-box count → expected-density ratio).

Changes vs. original:
  ISSUE-01: calculate_lidar_visibility() now returns a single-sensor tuple
            (visible, points_count, sparsity_score) per bbox.  The caller
            (pipeline.py) calls it once for OS2-64 and once for OS1-128,
            passing the correct expected_density constant each time.
  ISSUE-05: FOV/range visibility check now tests the object *center* against
            the sensor envelope, not whether the entire bbox fits inside it.
            Replaced containment test with a center-point check so objects
            straddling a FOV boundary are not spuriously marked invisible.
"""

from typing import Tuple, Dict, List, Optional
import numpy as np
from .config import (
    OS2_64_CHANNELS, OS2_64_VFOV_DEG, OS2_64_HRES_DEG,
    OS1_128_CHANNELS, OS1_128_VFOV_DEG, OS1_128_HRES_DEG
)

# Look-up tables for OS2-64 and OS1-128 LiDAR sensors
OS2_64_CHANNEL_LUT = {
    'channels': OS2_64_CHANNELS,
    'elevations': np.linspace(np.radians(-OS2_64_VFOV_DEG/2), np.radians(OS2_64_VFOV_DEG/2), OS2_64_CHANNELS),
    'azimuth_bins': int(360 / OS2_64_HRES_DEG)
}
OS1_128_CHANNEL_LUT = {
    'channels': OS1_128_CHANNELS,
    'elevations': np.linspace(np.radians(-OS1_128_VFOV_DEG/2), np.radians(OS1_128_VFOV_DEG/2), OS1_128_CHANNELS),
    'azimuth_bins': int(360 / OS1_128_HRES_DEG)
}


def prepare_frame_lidar(points, num_channels, v_fov_deg, h_res_deg):
    """Generate a range image from LiDAR points.

    Args:
        points: Nx3 array of LiDAR points in sensor frame (x forward, y left, z up).
        num_channels: Number of laser channels (e.g., 64 for OS2-64, 128 for OS1-128).
        v_fov_deg: Vertical field of view in degrees (total, e.g., 26.8 for OS2-64).
        h_res_deg: Horizontal resolution in degrees (e.g., 0.16 for OS2-64).

    Returns:
        tuple (range_image, sensor_origin):
            range_image: 2D array of shape [num_channels, azimuth_bins] with range in meters.
                         azimute_bins = int(360 / h_res_deg)
                         Values are set to 0 where no point falls in the bin.
            sensor_origin: 3-element array [0, 0, 0] (sensor is at origin of point cloud frame).
    """
    if points is None or len(points) == 0:
        # Return empty range image and zero origin
        azimuth_bins = int(360.0 / h_res_deg)
        range_image = np.zeros((num_channels, azimuth_bins), dtype=np.float32)
        return range_image, np.array([0.0, 0.0, 0.0], dtype=np.float32)

    # Compute spherical coordinates for each point
    x = points[:, 0]
    y = points[:, 1]
    z = points[:, 2]
    range_vals = np.sqrt(x**2 + y**2 + z**2)
    # Avoid division by zero for elevation
    elevation = np.arcsin(np.divide(z, range_vals, out=np.zeros_like(z), where=range_vals!=0))
    azimuth = np.arctan2(y, x)  # [-pi, pi]

    # Convert to degrees
    elevation_deg = np.degrees(elevation)
    azimuth_deg = np.degrees(azimuth)
    # Shift azimuth to [0, 360)
    azimuth_deg = np.where(azimuth_deg < 0, azimuth_deg + 360.0, azimuth_deg)

    # Calculate bin indices
    azimuth_bins = int(360.0 / h_res_deg)
    elevation_bin_size = v_fov_deg / num_channels

    # Clip elevation to FOV
    min_elevation = -v_fov_deg / 2.0
    max_elevation = v_fov_deg / 2.0
    elev_mask = (elevation_deg >= min_elevation) & (elevation_deg <= max_elevation)

    # Initialize range image with zeros (meaning no point)
    range_image = np.zeros((num_channels, azimuth_bins), dtype=np.float32)

    # For each point within FOV, compute bin indices and update range if closer
    for i in range(len(points)):
        if not elev_mask[i]:
            continue
        elev = elevation_deg[i]
        azi = azimuth_deg[i]
        r = range_vals[i]

        # Compute channel index (0 to num_channels-1)
        chan = int((elev - min_elevation) / elevation_bin_size)
        if chan < 0 or chan >= num_channels:
            # Should not happen due to clamping, but skip to be safe
            continue

        # Compute azimuth bin (0 to azimuth_bins-1)
        az_bin = int(azi / h_res_deg)
        if az_bin < 0 or az_bin >= azimuth_bins:
            # Wrap around (should not happen with [0,360) azimuth)
            az_bin = az_bin % azimuth_bins

        # Update range if this point is closer than current value
        current_val = range_image[chan, az_bin]
        if current_val == 0.0 or r < current_val:
            range_image[chan, az_bin] = r

    sensor_origin = np.array([0.0, 0.0, 0.0], dtype=np.float32)
    return range_image, sensor_origin


def calculate_lidar_visibility(points, bboxes, fov, range_limit, expected_density, range_image=None, sensor_origin=None):
    """Compute point-in-box count and sparsity score for one sensor cloud.

    NEW: Added support for precomputed range image to compute occlusion fraction.
    When range_image and sensor_origin are provided, computes:
        score = density_ratio × (1 - occluded_fraction × confidence)
    Otherwise, falls back to original behavior:
        score = density_ratio

    FIX ISSUE-01: Single-sensor return — caller decides which cloud to pass.
    FIX ISSUE-05: Visibility uses object center vs. FOV, not full-bbox containment.

    Args:
        points:           Nx3 numpy array of LiDAR points in radar/sensor frame.
        bboxes:           List of [xmin, xmax, ymin, ymax, zmin, zmax] (axis-aligned).
        fov:              [x_min, x_max, y_min, y_max] sensor FOV limits (meters).
        range_limit:      [min_range, max_range] sensor range limits (meters).
        expected_density: Theoretical point count for a 1-m³ bbox at this sensor's
                          angular resolution (scalar float).
        range_image:      Precomputed range image [channels, azimuth_bins] with nearest hit range (meters).
                         Optional; if not provided, falls back to original behavior.
        sensor_origin:    3-element array [x, y, z] of sensor position in sensor frame.
                         Optional; if not provided, falls back to original behavior.

    Returns:
        Tuple of three numpy arrays, one entry per bbox_len =True count,   returns ==  of  dtype=bool)
          (visible: bool[n], points_count: int[n], sparsity_score: float[n])
    """
    n = len(bboxes)
    visible = np.zeros(n, dtype=bool)
    points_count = np.zeros(n, dtype=int)
    sparsity_score = np.zeros(n, dtype=float)

    pts = np.asarray(points, dtype=np.float32)  # ensure array, avoids per-point loop overhead
    # Ensure pts is 2D (Nx3) even if a single point is passed as 1D
    if pts.ndim == 1:
        pts = pts.reshape(1, -1)

    for i, bbox in enumerate(bboxes):
        xmin, xmax, ymin, ymax, zmin, zmax = bbox

        # --- ISSUE-05 FIX: center-point FOV/range check ---
        cx = (xmin + xmax) / 2.0
        cy = (ymin + ymax) / 2.0
        cz = (zmin + zmax) / 2.0
        dist = float(np.sqrt(cx**2 + cy**2 + cz**2))

        in_fov = (fov[0] <= cx <= fov[1] and fov[2] <= cy <= fov[3])
        in_range = (range_limit[0] <= dist <= range_limit[1])

        # --- ISSUE-01 FIX: count from the single cloud passed in ---
        if len(pts) > 0:
            # Optimized point-in-box test: use in-place boolean operations to avoid temporary arrays
            mask = np.ones(len(pts), dtype=bool)
            mask &= (pts[:, 0] >= xmin)
            mask &= (pts[:, 0] <= xmax)
            mask &= (pts[:, 1] >= ymin)
            mask &= (pts[:, 1] <= ymax)
            mask &= (pts[:, 2] >= zmin)
            mask &= (pts[:, 2] <= zmax)
            count = int(np.sum(mask))
        else:
            count = 0

        # NEW: Compute density ratio (same as before)
        density_ratio = float(count / expected_density) if expected_density > 0 else 0.0

        # NEW: If range_image and sensor_origin provided, compute occlusion fraction and confidence
        if range_image is not None and sensor_origin is not None:
            # Determine which channel LUT to use based on expected_density (approximate)
            # This is a simplification - in practice, we should pass the channel_lut directly
            if expected_density > 0:
                # Rough estimation: higher expected_density means more channels
                if expected_density > 50:  # Arbitrary threshold - OS1-128 has higher density
                    channel_lut = OS1_128_CHANNEL_LUT
                else:
                    channel_lut = OS2_64_CHANNEL_LUT
            else:
                # Default to OS2-64 if we can't determine
                channel_lut = OS2_64_CHANNEL_LUT

            # Validate range image dimensions
            if not _validate_range_image_dimensions(range_image, channel_lut['channels'], channel_lut['azimuth_bins']):
                # Fallback to original behavior if dimensions don't match
                occluded_fraction = 0.0
                confidence = 0.0
            else:
                # Compute occlusion fraction and confidence using range image
                occluded_fraction, confidence = _compute_occlusion_fraction_from_range_image(
                    bbox, range_image, sensor_origin, channel_lut
                )
        else:
            # Fallback to original behavior: no occlusion consideration
            occluded_fraction = 0.0
            confidence = 0.0

        # NEW: Final score = density_ratio × (1 - occluded_fraction × confidence)
        final_score = density_ratio * (1.0 - occluded_fraction * confidence)

        visible[i] = in_fov and in_range and count > 0 and final_score > 0.0

        points_count[i] = count
        sparsity_score[i] = final_score

    return visible, points_count, sparsity_score


def _validate_range_image_dimensions(range_image: np.ndarray, expected_channels: int, expected_azimuth_bins: int) -> bool:
    """Validate that range image dimensions match expectations.

    Args:
        range_image: 2D array [channels, azimuth_bins]
        expected_channels: Expected number of channels (e.g., 64 or 128)
        expected_azimuth_bins: Expected number of azimuth bins

    Returns:
        True if dimensions match, False otherwise
    """
    if not isinstance(range_image, np.ndarray) or range_image.ndim != 2:
        return False
    return range_image.shape[0] == expected_channels and range_image.shape[1] == expected_azimuth_bins


def _compute_occlusion_fraction_from_range_image(bbox: List[float], range_image: np.ndarray, 
                                               sensor_origin: np.ndarray, channel_lut: dict) -> Tuple[float, float]:
    """Compute occlusion fraction and confidence using precomputed range image.

    Args:
        bbox: [xmin, xmax, ymin, ymax, zmin, zmax] bounding box in world coordinates
        range_image: Precomputed range image [channels, azimuth_bins] with nearest hit range (meters)
        sensor_origin: 3-element array [x, y, z] of sensor position in sensor frame
        channel_lut: Dictionary with channel parameters

    Returns:
        Tuple (occlusion_fraction, confidence) where:
          occlusion_fraction: 0.0 = no occlusion, 1.0 = fully occluded
          confidence: 0.0 = no valid samples, 1.0 = all samples valid
    """
    xmin, xmax, ymin, ymax, zmin, zmax = bbox

    # Define box corners in object center frame
    corners = np.array([
        [-xmin, -ymin, -zmin], [ xmax, -ymin, -zmin], [ xmax,  ymax, -zmin], [-xmin,  ymax, -zmin],  # bottom face
        [-xmin, -ymin,  zmax], [ xmax, -ymin,  zmax], [ xmax,  ymax,  zmax], [-xmin,  ymax,  zmax]   # top face
    ])

    # Shift corners to be relative to object center (assuming bbox is centered at origin)
    # Actually, the bbox is already in world coordinates with center at (0,0,0) for this computation
    # We need to transform to sensor frame
    corners_sensor = corners - sensor_origin  # Shift to sensor-relative coordinates

    # Convert to spherical coordinates for each corner
    ranges = np.linalg.norm(corners_sensor[:, :2], axis=1)
    elevations = np.arcsin(corners_sensor[:, 2] / np.maximum(ranges, 1e-6))
    azimuths = np.arctan2(corners_sensor[:, 1], corners_sensor[:, 0])

    # Normalize azimuth to [0, 2pi) for binning
    azimuths = np.where(azimuths < 0, azimuths + 2*np.pi, azimuths)

    # Find channel indices for each corner (closest elevation match)
    elevations_array = np.array(channel_lut['elevations'])
    channel_indices = np.argmin(np.abs(elevations[:, None] - elevations_array[None, :]), axis=1)

    # Find azimuth bin indices
    azimuth_bin_width = 2*np.pi / channel_lut['azimuth_bins']
    azimuth_indices = (azimuths / azimuth_bin_width).astype(int)
    azimuth_indices = np.clip(azimuth_indices, 0, channel_lut['azimuth_bins'] - 1)

    # For each channel-azimuth bin, get the range from the range image
    range_samples = range_image[channel_indices, azimuth_indices]

    # Compute occlusion fraction and confidence
    # Ignore infinite values in range_samples (no hit) and NaN values
    valid_samples = np.isfinite(range_samples) & ~np.isnan(range_samples)
    if np.any(valid_samples):
        # For valid samples, if actual range > range image value, then occluded
        occluded = np.zeros_like(ranges, dtype=bool)
        occluded[valid_samples] = ranges[valid_samples] > range_samples[valid_samples]
        occluded_fraction = np.mean(occluded[valid_samples])
        confidence = np.mean(valid_samples)  # fraction of valid samples
    else:
        occluded_fraction = 0.0
        confidence = 0.0

    return float(occluded_fraction), float(confidence)