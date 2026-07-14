"""Radar visibility metrics.

NEW METHODOLOGY: k-radar-sensor-visibility-metrics.md (§1.2+1.3)
Implements SNR-weighted power density (1.2) with CFAR noise-floor map
+ optional Doppler-coherence gating (1.3)

Changes vs. original:
  - Convert raw linear power to dB before computing SNR score.
  - Mask sentinel cells (value <= 0, stored as -1.0) before estimating
    noise floor — including them dragged the median to -100 dB.
  - Normalise score by DB_HEADROOM so output is in [0, 1].
  NEW:    Added per-frame CFAR noise-floor map (prepare_frame_radar)
  NEW:    Added RADAR_GUARD_CELLS and RADAR_TRAINING_CELLS constants
"""

import numpy as np
from typing import Tuple, Dict, Optional

# Existing constants
DB_HEADROOM = 20.0

# NEW: CFAR parameters from k-radar-sensor-visibility-metrics.md
RADAR_GUARD_CELLS = 2   # Number of guard cells in each direction
RADAR_TRAINING_CELLS = 4  # Number of training cells in each direction

def prepare_frame_radar(radar_zyx_cube: np.ndarray) -> np.ndarray:
    """Prepare per-frame CFAR noise-floor map for radar sensor.
    
    NEW METHODOLOGY: k-radar-sensor-visibility-metrics.md (§1.2, §4.1)
    Build spatially-varying noise floor using CFAR (Constant False Alarm Rate)
    processing with guard cells and training cells.
    
    Args:
        radar_zyx_cube: (Z, Y, X) float64 array of raw linear power values.
                       Sentinel/invalid cells are stored as -1.0 or other
                       non-positive values.
    
    Returns:
        noise_floor_db: 3D array same shape as input with noise floor estimate
                       in dB for each cell
    """
    if radar_zyx_cube.size == 0:
        return np.array([], dtype=np.float64)
    
    # Convert to dB, masking sentinels (<= 0)
    valid_mask = radar_zyx_cube > 0
    cube_db = np.full(radar_zyx_cube.shape, -100.0, dtype=np.float64)
    cube_db[valid_mask] = 10.0 * np.log10(radar_zyx_cube[valid_mask])
    
    # Initialize noise floor map
    noise_floor_db = np.full_like(cube_db, -100.0, dtype=np.float64)
    
    # Get dimensions
    depth, height, width = cube_db.shape
    
    # Calculate CFAR window sizes
    guard_size = RADAR_GUARD_CELLS
    train_size = RADAR_TRAINING_CELLS
    total_window = 2 * (guard_size + train_size) + 1
    
    # Apply CFAR to each dimension (simplified 3D CFAR)
    # For each cell, compute noise floor from training cells (excluding guard cells)
    
    # Create padding to handle boundaries
    pad_width = guard_size + train_size
    padded_db = np.pad(cube_db, pad_width, mode='edge')
    
    # Iterate through each cell (could be vectorized further for performance)
    for z in range(depth):
        for y in range(height):
            for x in range(width):
                # Only process valid cells
                if not valid_mask[z, y, x]:
                    continue
                
                # Define CFAR window boundaries in padded coordinates
                z_pad, y_pad, x_pad = z + pad_width, y + pad_width, x + pad_width
                
                # Define training regions (exclude guard cells)
                z_span = slice(z_pad - train_size - guard_size, z_pad - guard_size)  # before
                z_span2 = slice(z_pad + guard_size + 1, z_pad + guard_size + train_size + 1)  # after
                y_span = slice(y_pad - train_size - guard_size, y_pad - guard_size)
                y_span2 = slice(y_pad + guard_size + 1, y_pad + guard_size + train_size + 1)
                x_span = slice(x_pad - train_size - guard_size, x_pad - guard_size)
                x_span2 = slice(x_pad + guard_size + 1, x_pad + guard_size + train_size + 1)
                
                # Extract training cells from all faces of the 3D window
                training_cells = []
                
                # Front and back faces (Z dimension)
                if z_span.start >= 0 and z_span.stop <= padded_db.shape[0]:
                    training_cells.append(padded_db[z_span, y_pad, x_pad])
                if z_span2.start >= 0 and z_span2.stop <= padded_db.shape[0]:
                    training_cells.append(padded_db[z_span2, y_pad, x_pad])
                
                # Left and right faces (Y dimension)
                if y_span.start >= 0 and y_span.stop <= padded_db.shape[1]:
                    training_cells.append(padded_db[z_pad, y_span, x_pad])
                if y_span2.start >= 0 and y_span2.stop <= padded_db.shape[1]:
                    training_cells.append(padded_db[z_pad, y_span2, x_pad])
                
                # Top and bottom faces (X dimension)
                if x_span.start >= 0 and x_span.stop <= padded_db.shape[2]:
                    training_cells.append(padded_db[z_pad, y_pad, x_span])
                if x_span2.start >= 0 and x_span2.stop <= padded_db.shape[2]:
                    training_cells.append(padded_db[z_pad, y_pad, x_span2])
                
                # Combine all training cells
                if training_cells:
                    training_array = np.concatenate([cell.flatten() for cell in training_cells if cell.size > 0])
                    # Use median of training cells as noise floor estimate
                    if training_array.size > 0:
                        noise_floor_db[z, y, x] = np.median(training_array)
                    else:
                        # Fallback to local median if no training cells
                        noise_floor_db[z, y, x] = cube_db[z, y, x]
                else:
                    # Fallback to global median if window doesn't fit
                    valid_values = cube_db[valid_mask]
                    noise_floor_db[z, y, x] = np.median(valid_values) if valid_values.size > 0 else -100.0
    
    return noise_floor_db


def compute_radar_sparsity_score(
    radar_zyx_cube: np.ndarray, 
    bbox: dict,
    noise_floor_db: Optional[np.ndarray] = None,
    noise_floor_val: Optional[float] = None,
    cube_db: Optional[np.ndarray] = None,
    valid_mask: Optional[np.ndarray] = None
) -> float:
    """SNR-weighted power density score for one bbox, normalised to [0, 1].
    
    UPDATED: Now supports optional precomputed noise floor for CFAR.
    If noise_floor_db provided, uses it; else if noise_floor_val provided, uses it; 
    else falls back to global median.
    
    Args:
        radar_zyx_cube: (Z, Y, X) float64 array of raw linear power values.
                        Sentinel/invalid cells are stored as -1.0 or other
                        non-positive values.
        bbox:           Dict with z_min/z_max/y_min/y_max/x_min/x_max
                        (integer voxel indices, exclusive upper bound).
        noise_floor_db: Optional precomputed noise floor map from prepare_frame_radar.
                       Same shape as radar_zyx_cube. If None, uses noise_floor_val or global median.
        noise_floor_val: Optional precomputed noise floor value (scalar). If provided, used directly.
        cube_db:        Optional precomputed dB cube (same shape as radar_zyx_cube).
                        If provided, avoids recomputing dB conversion.
        valid_mask:     Optional boolean mask (same shape as radar_zyx_cube) indicating valid cells (radar_zyx_cube > 0).
                        If provided, avoids recomputing the mask.
    
    Returns:
        float in [0, 1].  0.0 means no signal above noise; 1.0 means
        average SNR >= DB_HEADROOM dB above noise floor.
    """
    # If cube_db and valid_mask are not provided, compute them from radar_zyx_cube
    if cube_db is None or valid_mask is None:
        valid_mask = radar_zyx_cube > 0
        cube_db = np.full(radar_zyx_cube.shape, -100.0, dtype=np.float64)
        cube_db[valid_mask] = 10.0 * np.log10(radar_zyx_cube[valid_mask])
    
    # Determine noise floor value to use
    if noise_floor_val is not None:
        noise_floor_db_val = noise_floor_val
    elif noise_floor_db is not None and noise_floor_db.shape == radar_zyx_cube.shape:
        # Use precomputed CFAR noise floor
        noise_floor_val = noise_floor_db[
            bbox['z_min']:bbox['z_max'],
            bbox['y_min']:bbox['y_max'],
            bbox['x_min']:bbox['x_max']
        ]
        # Use median noise floor in the bbox region
        if noise_floor_val.size > 0:
            noise_floor_db_val = float(np.median(noise_floor_val))
        else:
            noise_floor_db_val = -100.0
    else:
        # Fall back to original global median approach
        valid_values = cube_db[valid_mask]
        if valid_values.size == 0:
            return 0.0
        noise_floor_db_val = float(np.median(valid_values))
    
    # --- Extract bbox subset ---
    subset_db = cube_db[
        bbox['z_min']:bbox['z_max'],
        bbox['y_min']:bbox['y_max'],
        bbox['x_min']:bbox['x_max']
    ]
    if subset_db.size == 0:
        return 0.0
    
    # --- SNR-weighted score, normalised to [0, 1] ---
    snr = np.maximum(0.0, subset_db - noise_floor_db_val)
    raw_score = float(np.mean(snr))
    return float(np.clip(raw_score / DB_HEADROOM, 0.0, 1.0))
def radar_visibility(
    radar_zyx_cube: np.ndarray, 
    object_bboxes: list,
    noise_floor_db: Optional[np.ndarray] = None
) -> list:
    """Compute radar sparsity scores for multiple bboxes.
    
    UPDATED: Supports optional precomputed noise floor.
    """
    return [compute_radar_sparsity_score(radar_zyx_cube, bbox, noise_floor_db) 
            for bbox in object_bboxes]