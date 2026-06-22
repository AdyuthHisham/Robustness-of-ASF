"""Radar visibility metrics.

Implements §4.1 method B: SNR-weighted power density on radar_zyx_cube.

Changes vs. original:
  - Convert raw linear power to dB before computing SNR score.
  - Mask sentinel cells (value <= 0, stored as -1.0) before estimating
    noise floor — including them dragged the median to -100 dB.
  - Normalise score by DB_HEADROOM so output is in [0, 1].
"""

import numpy as np

# Normalisation headroom: a bbox with average SNR of this many dB above
# the noise floor scores 1.0. Objects above this are clipped to 1.0.
DB_HEADROOM = 20.0


def compute_radar_sparsity_score(radar_zyx_cube: np.ndarray, bbox: dict) -> float:
    """SNR-weighted power density score for one bbox, normalised to [0, 1].

    Args:
        radar_zyx_cube: (Z, Y, X) float64 array of raw linear power values.
                        Sentinel/invalid cells are stored as -1.0 or other
                        non-positive values.
        bbox:           Dict with z_min/z_max/y_min/y_max/x_min/x_max
                        (integer voxel indices, exclusive upper bound).

    Returns:
        float in [0, 1].  0.0 means no signal above noise; 1.0 means
        average SNR >= DB_HEADROOM dB above noise floor.
    """
    # --- Convert to dB, masking sentinels ---
    valid_mask = radar_zyx_cube > 0
    cube_db = np.full(radar_zyx_cube.shape, -100.0, dtype=np.float64)
    cube_db[valid_mask] = 10.0 * np.log10(radar_zyx_cube[valid_mask])

    # --- Per-frame noise floor from valid cells only ---
    valid_values = cube_db[valid_mask]
    if valid_values.size == 0:
        return 0.0
    noise_floor_db = float(np.median(valid_values))

    # --- Extract bbox subset ---
    subset = cube_db[
        bbox['z_min']:bbox['z_max'],
        bbox['y_min']:bbox['y_max'],
        bbox['x_min']:bbox['x_max'],
    ]
    if subset.size == 0:
        return 0.0

    # --- SNR-weighted score, normalised to [0, 1] ---
    snr = np.maximum(0.0, subset - noise_floor_db)
    raw_score = float(np.mean(snr))
    return float(np.clip(raw_score / DB_HEADROOM, 0.0, 1.0))


def radar_visibility(radar_zyx_cube: np.ndarray, object_bboxes: list) -> list:
    """Compute radar sparsity scores for multiple bboxes."""
    return [compute_radar_sparsity_score(radar_zyx_cube, bbox) for bbox in object_bboxes]

