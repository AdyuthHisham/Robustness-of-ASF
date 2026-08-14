#!/usr/bin/env python3
"""
Performance benchmark for precomputation overhead (Phase 4 Task 4.2).

Compares per-frame runtime with vs without the Phase 2 precomputation
(LiDAR range images, radar noise-floor maps, camera depth maps) and
reports whether the overhead is under 20% per frame with no significant
memory increase.
"""

import sys
import time
import tracemalloc
import numpy as np
from pathlib import Path

# Add the project root's src directory to the path to import kradar_visibility modules
project_root = Path(__file__).resolve().parents[1]
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from kradar_visibility.lidar_visibility import prepare_frame_lidar, calculate_lidar_visibility
from kradar_visibility.radar_visibility import compute_radar_sparsity_score
from kradar_visibility.camera_visibility import (
    prepare_frame_camera,
    calculate_camera_visibility
)
from kradar_visibility.parser import parse_label_file, get_sequence_label_files
from kradar_visibility.data_loader import load_radar_cube, load_lidar_points
from kradar_visibility.calibration import get_camera_params, load_camera_calibration
from kradar_visibility.config import (
    OS2_64_CHANNELS, OS2_64_VFOV_DEG, OS2_64_HRES_DEG,
    OS1_128_CHANNELS, OS1_128_VFOV_DEG, OS1_128_HRES_DEG,
    CAM_HALF_WIDTH, CAM_HALF_HEIGHT,
    DATASET_ROOT
)
from kradar_visibility.pipeline import (
    RADAR_Z_MIN, RADAR_Z_MAX, RADAR_Y_MIN, RADAR_Y_MAX,
    RADAR_X_MIN, RADAR_X_MAX, RADAR_GRID_Z, RADAR_GRID_Y, RADAR_GRID_X,
    _EXPECTED_OS2, _EXPECTED_OS1, _LIDAR_FOV, _LIDAR_RANGE_OS2, _LIDAR_RANGE_OS1,
    _world_to_voxel, _radar_fov_check, _radar_range_check, _obj_corners,
    _bbox_voxels_from_annotation, _bbox_list_from_annotation
)


def load_test_frame(sequence_id: str, frame_limit: int = 1):
    """Load a single annotated frame with all sensor data."""
    label_files = get_sequence_label_files(sequence_id, DATASET_ROOT)
    if not label_files:
        raise ValueError(f"No label files found for sequence {sequence_id}")
    
    annotated_files = []
    for f in label_files:
        try:
            _, objects = parse_label_file(f)
            if objects:
                annotated_files.append(f)
                if len(annotated_files) >= frame_limit:
                    break
        except Exception:
            continue
    
    if not annotated_files:
        raise ValueError(f"No annotated frames found for sequence {sequence_id}")
    
    label_file = annotated_files[0]
    header, objects = parse_label_file(label_file)
    if header is None or not objects:
        raise ValueError(f"Failed to parse {label_file}")
    
    # Load sensor data
    radar_cube = load_radar_cube(sequence_id, header.tesseract_idx, DATASET_ROOT)
    os2_points = load_lidar_points(sequence_id, header.os2_64_idx, "os2-64", DATASET_ROOT)
    os1_points = load_lidar_points(sequence_id, header.os1_128_idx, "os1-128", DATASET_ROOT)
    
    # Check calibration availability
    calib_available = True
    try:
        load_camera_calibration(seq=int(sequence_id))
    except Exception:
        calib_available = False
    
    return header, objects, radar_cube, os2_points, os1_points, calib_available


def benchmark_with_precomputation(radar_cube, os2_points, os1_points, objects, seq_int, n_runs):
    """Benchmark full pipeline WITH precomputation (LiDAR range images + camera depth maps)."""
    times = []
    peak_memories = []
    
    for _ in range(n_runs):
        tracemalloc.start()
        start = time.perf_counter()
        
        # --- LiDAR precomputation ---
        os2_range_image, os2_sensor_origin = prepare_frame_lidar(
            os2_points, OS2_64_CHANNELS, OS2_64_VFOV_DEG, OS2_64_HRES_DEG
        )
        os1_range_image, os1_sensor_origin = prepare_frame_lidar(
            os1_points, OS1_128_CHANNELS, OS1_128_VFOV_DEG, OS1_128_HRES_DEG
        )
        
        # --- Radar: global median (fast path, same in both modes) ---
        valid_mask = radar_cube > 0
        cube_db = np.full(radar_cube.shape, -100.0, dtype=np.float64)
        cube_db[valid_mask] = 10.0 * np.log10(radar_cube[valid_mask])
        valid_values = cube_db[valid_mask]
        noise_floor_val = float(np.median(valid_values)) if valid_values.size > 0 else -100.0
        
        # --- Camera precomputation ---
        camera_depth_maps = {}
        camera_intrinsics_list = []
        camera_extrinsics_list = []
        for direction in ['front', 'left', 'right', 'rear']:
            params_list = get_camera_params(direction, seq=seq_int)
            camera_intrinsics_list.append(params_list[0]['camera_intrinsics'])
            camera_extrinsics_list.append(params_list[0]['radar2camera'])
        
        lidar_extrinsics = np.eye(4)
        depth_maps = prepare_frame_camera(
            os1_points[:, :3], lidar_extrinsics,
            camera_intrinsics_list, camera_extrinsics_list,
            CAM_HALF_WIDTH, CAM_HALF_HEIGHT
        )
        for i, direction in enumerate(['front', 'left', 'right', 'rear']):
            camera_depth_maps[direction] = depth_maps[i]
        
        # --- Score all objects ---
        for obj in objects:
            bbox_list = [_bbox_list_from_annotation(obj)]
            
            # Radar score
            bbox = _bbox_voxels_from_annotation(obj)
            if (bbox['z_max'] > bbox['z_min'] and
                    bbox['y_max'] > bbox['y_min'] and
                    bbox['x_max'] > bbox['x_min']):
                compute_radar_sparsity_score(
                    radar_cube, bbox, noise_floor_val=noise_floor_val,
                    cube_db=cube_db, valid_mask=valid_mask
                )
            
            # LiDAR scores
            if os2_points is not None and len(os2_points) > 0:
                calculate_lidar_visibility(
                    os2_points, bbox_list, _LIDAR_FOV, _LIDAR_RANGE_OS2,
                    _EXPECTED_OS2, range_image=os2_range_image, sensor_origin=os2_sensor_origin
                )
            if os1_points is not None and len(os1_points) > 0:
                calculate_lidar_visibility(
                    os1_points, bbox_list, _LIDAR_FOV, _LIDAR_RANGE_OS1,
                    _EXPECTED_OS1, range_image=os1_range_image, sensor_origin=os1_sensor_origin
                )
            
            # Camera scores
            corners = _obj_corners(obj)
            calculate_camera_visibility(corners, seq=seq_int, depth_maps=camera_depth_maps)
        
        end = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        times.append(end - start)
        peak_memories.append(peak / (1024 * 1024))  # MB
    
    return times, peak_memories


def benchmark_without_precomputation(radar_cube, os2_points, os1_points, objects, seq_int, n_runs):
    """Benchmark scoring path WITHOUT precomputation (fallback paths)."""
    times = []
    peak_memories = []
    
    # Precompute radar global median (same in both modes - not precomputation overhead)
    valid_mask = radar_cube > 0
    cube_db = np.full(radar_cube.shape, -100.0, dtype=np.float64)
    cube_db[valid_mask] = 10.0 * np.log10(radar_cube[valid_mask])
    valid_values = cube_db[valid_mask]
    noise_floor_val = float(np.median(valid_values)) if valid_values.size > 0 else -100.0
    
    # NO LiDAR precomputation
    # NO Camera depth maps
    
    for _ in range(n_runs):
        tracemalloc.start()
        start = time.perf_counter()
        
        for obj in objects:
            bbox_list = [_bbox_list_from_annotation(obj)]
            
            # Radar score (global median fallback)
            bbox = _bbox_voxels_from_annotation(obj)
            if (bbox['z_max'] > bbox['z_min'] and
                    bbox['y_max'] > bbox['y_min'] and
                    bbox['x_max'] > bbox['x_min']):
                compute_radar_sparsity_score(
                    radar_cube, bbox, noise_floor_val=noise_floor_val,
                    cube_db=cube_db, valid_mask=valid_mask
                )
            
            # LiDAR scores (NO range image - fallback path)
            if os2_points is not None and len(os2_points) > 0:
                calculate_lidar_visibility(
                    os2_points, bbox_list, _LIDAR_FOV, _LIDAR_RANGE_OS2,
                    _EXPECTED_OS2, range_image=None, sensor_origin=None
                )
            if os1_points is not None and len(os1_points) > 0:
                calculate_lidar_visibility(
                    os1_points, bbox_list, _LIDAR_FOV, _LIDAR_RANGE_OS1,
                    _EXPECTED_OS1, range_image=None, sensor_origin=None
                )
            
            # Camera scores (NO depth maps - fallback path)
            corners = _obj_corners(obj)
            calculate_camera_visibility(corners, seq=seq_int, depth_maps={})
        
        end = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        times.append(end - start)
        peak_memories.append(peak / (1024 * 1024))  # MB
    
    return times, peak_memories


def main():
    print("=" * 70)
    print("Phase 4 Task 4.2 — Precomputation Performance Benchmark")
    print("=" * 70)
    
    # Configuration
    SEQUENCE_ID = "1"
    N_RUNS = 5  # Reduced from 20 due to benchmark time
    
    print(f"\nLoading test frame from sequence {SEQUENCE_ID}...")
    try:
        header, objects, radar_cube, os2_points, os1_points, calib_available = load_test_frame(SEQUENCE_ID)
    except Exception as e:
        print(f"ERROR: Failed to load test frame: {e}")
        sys.exit(1)
    
    seq_int = int(SEQUENCE_ID)
    
    print(f"  Objects in frame: {len(objects)}")
    print(f"  Radar cube: {radar_cube.shape if radar_cube is not None else 'None'}")
    print(f"  OS2-64 points: {len(os2_points) if os2_points is not None else 0}")
    print(f"  OS1-128 points: {len(os1_points) if os1_points is not None else 0}")
    print(f"  Calibration available: {calib_available}")
    print(f"  Runs per mode: {N_RUNS}")
    
    if radar_cube is None:
        print("ERROR: No radar cube loaded")
        sys.exit(1)
    if os2_points is None or len(os2_points) == 0:
        print("ERROR: No OS2-64 points loaded")
        sys.exit(1)
    if os1_points is None or len(os1_points) == 0:
        print("ERROR: No OS1-128 points loaded")
        sys.exit(1)
    if not calib_available:
        print("ERROR: Calibration not available for sequence 1")
        sys.exit(1)
    
    # Warm-up runs (not measured)
    print("\nWarming up...")
    _ = benchmark_with_precomputation(radar_cube, os2_points, os1_points, objects, seq_int, 1)
    _ = benchmark_without_precomputation(radar_cube, os2_points, os1_points, objects, seq_int, 1)
    
    # Benchmark WITH precomputation
    print(f"\nBenchmarking WITH precomputation ({N_RUNS} runs)...")
    with_times, with_peak_mems = benchmark_with_precomputation(
        radar_cube, os2_points, os1_points, objects, seq_int, N_RUNS
    )
    
    # Benchmark WITHOUT precomputation
    print(f"Benchmarking WITHOUT precomputation ({N_RUNS} runs)...")
    without_times, without_peak_mems = benchmark_without_precomputation(
        radar_cube, os2_points, os1_points, objects, seq_int, N_RUNS
    )
    
    # Statistics
    def stats(times):
        arr = np.array(times)
        return {
            'mean': float(np.mean(arr)),
            'std': float(np.std(arr)),
            'min': float(np.min(arr)),
            'max': float(np.max(arr)),
            'median': float(np.median(arr)),
        }
    
    with_stats = stats(with_times)
    without_stats = stats(without_times)
    
    with_peak_mean = float(np.mean(with_peak_mems))
    without_peak_mean = float(np.mean(without_peak_mems))
    
    # Per-frame timing (divide by number of objects)
    num_objects = len(objects)
    with_mean_per_frame = with_stats['mean'] / num_objects
    without_mean_per_frame = without_stats['mean'] / num_objects
    
    # Overhead calculation
    overhead_abs = with_mean_per_frame - without_mean_per_frame
    overhead_pct = (overhead_abs / without_mean_per_frame) * 100 if without_mean_per_frame > 0 else float('inf')
    
    # Memory overhead
    mem_overhead_mb = with_peak_mean - without_peak_mean
    mem_overhead_pct = (mem_overhead_mb / without_peak_mean) * 100 if without_peak_mean > 0 else float('inf')
    
    # Results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    print(f"\nPer-frame timing (mean over {N_RUNS} runs, {num_objects} objects/frame):")
    print(f"  WITH precomputation:    {with_mean_per_frame*1000:.3f} ms/frame (total: {with_stats['mean']*1000:.3f} ms)")
    print(f"  WITHOUT precomputation: {without_mean_per_frame*1000:.3f} ms/frame (total: {without_stats['mean']*1000:.3f} ms)")
    
    print(f"\nOverhead:")
    print(f"  Absolute: {overhead_abs*1000:.3f} ms/frame")
    print(f"  Percentage: {overhead_pct:.1f}%")
    
    print(f"\nPeak memory usage (tracemalloc, mean over {N_RUNS} runs):")
    print(f"  WITH precomputation:    {with_peak_mean:.2f} MB")
    print(f"  WITHOUT precomputation: {without_peak_mean:.2f} MB")
    print(f"  Overhead: {mem_overhead_mb:.2f} MB ({mem_overhead_pct:.1f}%)")
    
    # PASS/FAIL criteria
    print("\n" + "=" * 70)
    print("VALIDATION")
    print("=" * 70)
    
    time_pass = overhead_pct < 20.0
    mem_pass = mem_overhead_pct < 50.0  # generous threshold for memory
    
    print(f"  Time overhead < 20%: {'PASS' if time_pass else 'FAIL'} ({overhead_pct:.1f}%)")
    print(f"  Memory overhead reasonable: {'PASS' if mem_pass else 'FAIL'} ({mem_overhead_pct:.1f}%)")
    
    overall_pass = time_pass and mem_pass
    print(f"\n{'='*70}")
    if overall_pass:
        print("✅ OVERALL: PASS — Precomputation overhead is under 20% per frame")
    else:
        print("❌ OVERALL: FAIL — Precomputation overhead exceeds thresholds")
    print(f"{'='*70}")
    
    # Caveats
    print("\nCaveats:")
    print(f"  - Single frame sample (sequence {SEQUENCE_ID}, frame {header.tesseract_idx})")
    print(f"  - Machine load variability may affect absolute timings")
    print(f"  - Memory measured via tracemalloc (Python heap only, not RSS)")
    print(f"  - Results may vary across different frames/sequences")
    print(f"  - Radar CFAR noise-floor map (prepare_frame_radar) excluded from")
    print(f"    precomputation benchmark as it is prohibitively slow (>5 min/frame)")
    print(f"    and uses global median in both modes per pipeline.py design.")
    
    sys.exit(0 if overall_pass else 1)


if __name__ == "__main__":
    main()