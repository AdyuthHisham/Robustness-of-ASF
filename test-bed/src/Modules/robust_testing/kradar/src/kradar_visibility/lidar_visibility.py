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

import numpy as np


def read_pcd_file(filepath):
    """Read a PCD file and return points as Nx3 numpy array."""
    with open(filepath, 'rb') as f:
        header = []
        while True:
            line = f.readline()
            if not line:
                break
            line = line.decode('utf-8', errors='ignore').strip()
            header.append(line)
            if line.startswith('DATA'):
                data_type = line.split()[-1]
                break

        num_points = None
        for h in header:
            if h.startswith('POINTS'):
                num_points = int(h.split()[-1])

        if data_type == 'ascii':
            points = []
            for line in f:
                coords = line.decode('utf-8', errors='ignore').strip().split()
                if len(coords) >= 3:
                    points.append([float(coords[0]), float(coords[1]), float(coords[2])])
            return np.array(points, dtype=np.float32)
        else:
            data = np.fromfile(f, dtype=np.float32)
            if num_points is not None and len(data) >= num_points * 3:
                return data[:num_points * 3].reshape(-1, 3)
            return np.empty((0, 3), dtype=np.float32)

    return np.empty((0, 3), dtype=np.float32)


def calculate_lidar_visibility(points, bboxes, fov, range_limit, expected_density):
    """Compute point-in-box count and sparsity score for one sensor cloud.

    FIX ISSUE-01: Single-sensor return — caller decides which cloud to pass.
    FIX ISSUE-05: Visibility uses object center vs. FOV, not full-bbox containment.

    Args:
        points:           Nx3 numpy array of LiDAR points in radar/sensor frame.
        bboxes:           List of [xmin, xmax, ymin, ymax, zmin, zmax] (axis-aligned).
        fov:              [x_min, x_max, y_min, y_max] sensor FOV limits (meters).
        range_limit:      [min_range, max_range] sensor range limits (meters).
        expected_density: Theoretical point count for a 1-m³ bbox at this sensor's
                          angular resolution (scalar float).

    Returns:
        Tuple of three numpy arrays, one entry per bbox:
          (visible: bool[n], points_count: int[n], sparsity_score: float[n])
    """
    n = len(bboxes)
    visible = np.zeros(n, dtype=bool)
    points_count = np.zeros(n, dtype=int)
    sparsity_score = np.zeros(n, dtype=float)

    pts = np.asarray(points, dtype=np.float32)  # ensure array, avoids per-point loop overhead

    for i, bbox in enumerate(bboxes):
        xmin, xmax, ymin, ymax, zmin, zmax = bbox

        # --- ISSUE-05 FIX: center-point FOV/range check ---
        cx = (xmin + xmax) / 2.0
        cy = (ymin + ymax) / 2.0
        cz = (zmin + zmax) / 2.0
        dist = float(np.sqrt(cx**2 + cy**2 + cz**2))

        in_fov = (fov[0] <= cx <= fov[1] and fov[2] <= cy <= fov[3])
        in_range = (range_limit[0] <= dist <= range_limit[1])
        visible[i] = in_fov and in_range and count > 0

        # --- ISSUE-01 FIX: count from the single cloud passed in ---
        if len(pts) > 0:
            mask = (
                (pts[:, 0] >= xmin) & (pts[:, 0] <= xmax) &
                (pts[:, 1] >= ymin) & (pts[:, 1] <= ymax) &
                (pts[:, 2] >= zmin) & (pts[:, 2] <= zmax)
            )
            count = int(np.sum(mask))
        else:
            count = 0

        points_count[i] = count
        sparsity_score[i] = float(count / expected_density) if expected_density > 0 else 0.0

    return visible, points_count, sparsity_score
