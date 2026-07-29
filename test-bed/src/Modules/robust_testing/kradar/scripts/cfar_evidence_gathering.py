#!/usr/bin/env python3
"""Evidence-gathering: numerical equivalence, benchmarks, per-object scores on real K-Radar data.

This is a standalone evidence-gathering script, NOT a test. It does NOT
modify radar_visibility.py or any other source file.
"""

import time
import numpy as np
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from kradar_visibility.radar_visibility import (
    prepare_frame_radar,
    _prepare_frame_radar_loop_reference,
    compute_radar_sparsity_score,
    DB_HEADROOM,
    RADAR_GUARD_CELLS,
    RADAR_TRAINING_CELLS,
)
from kradar_visibility.data_loader import load_radar_cube
from kradar_visibility.pipeline import _bbox_voxels_from_annotation
from kradar_visibility.parser import parse_label_file

DATASET_ROOT = Path("/home/adhish/Productivity/AMSCUP/repos/K-Radar")
D, H, W = 150, 400, 250

# ===========================================================================
# Helper: parse all objects from a frame's label files
# ===========================================================================
def get_objects_for_frame(seq_id, frame_str):
    """Return list of (obj_annotation, bbox_voxels) for a frame."""
    label_dir = DATASET_ROOT / "data" / seq_id / "info_label_rev2"
    results = []
    for f in sorted(label_dir.iterdir()):
        if not f.name.endswith(".txt"):
            continue
        # File naming: FRAME_TRACKINGID.txt — match the frame part
        parts = f.stem.split("_")
        if parts[0] != frame_str:
            continue
        try:
            header, objects = parse_label_file(f)
        except Exception as e:
            print(f"  WARNING: parse error in {f.name}: {e}", file=sys.stderr)
            continue
        for obj in objects:
            vox = _bbox_voxels_from_annotation(obj)
            results.append((obj, vox))
    return results


# ===========================================================================
# EQUIVALENCE CHECK on 2 REAL FRAMES (sub-cube for loop-reference speed)
# ===========================================================================
print("=" * 72)
print("ITEM 4: NUMERICAL EQUIVALENCE — loop reference vs vectorized")
print("         on REAL DATA sub-cubes (20x40x40)")
print("=" * 72)

# Use sub-cube approach like verify_cfar_fix.py: loop ref on full cube is 430s
# Sub-cube of 20x40x40 = 32K cells is < 1s in the loop
test_frames_equiv = ["00135", "00140"]
z_span = (60, 80)
y_span = (180, 220)
x_span = (20, 60)

for frame_str in test_frames_equiv:
    print(f"\n--- Frame {frame_str} ---")
    cube = load_radar_cube("2", frame_str, DATASET_ROOT)
    sub_cube = cube[z_span[0]:z_span[1], y_span[0]:y_span[1], x_span[0]:x_span[1]].copy()

    # Vectorized
    t0 = time.perf_counter()
    nf_vec = prepare_frame_radar(sub_cube)
    t_vec = time.perf_counter() - t0

    # Loop reference
    t0 = time.perf_counter()
    nf_loop = _prepare_frame_radar_loop_reference(sub_cube)
    t_loop = time.perf_counter() - t0

    # Compare only valid cells (> -100)
    valid = (sub_cube > 0)
    diff = np.abs(nf_vec[valid] - nf_loop[valid])
    max_abs = diff.max()
    mean_abs = diff.mean()
    n_valid = valid.sum()

    print(f"  Sub-cube shape: {sub_cube.shape} ({sub_cube.size:,} cells, {n_valid:,} valid)")
    print(f"  Vectorized:     {t_vec:.4f}s")
    print(f"  Loop reference: {t_loop:.4f}s")
    print(f"  Max abs diff:   {max_abs:.6e}")
    print(f"  Mean abs diff:  {mean_abs:.6e}")
    print(f"  Bit-identical:  {max_abs == 0.0}")

    if max_abs != 0.0:
        print(f"  WARNING: non-zero diff! Check the mismatched cells.")
        # Show where the differences are
        mismatches = np.where(diff > 0)
        print(f"  Mismatch count: {len(mismatches[0])}")
        if len(mismatches[0]) > 0:
            print(f"  First 5 mismatch locations and values:")
            for i in range(min(5, len(mismatches[0]))):
                zi, yi, xi = mismatches[0][i], mismatches[1][i], mismatches[2][i]
                print(f"    ({zi},{yi},{xi}): loop={nf_loop[zi,yi,xi]:.10e} vec={nf_vec[zi,yi,xi]:.10e}")


# ===========================================================================
# BENCHMARK (vectorized only) on 3 full REAL frames
# ===========================================================================
print("\n" + "=" * 72)
print("ITEM 5: PER-FRAME BENCHMARK — vectorized on 3 full REAL frames (150x400x250)")
print("=" * 72)

bench_frames = ["00135", "00140", "00152"]
bench_times = []
for frame_str in bench_frames:
    cube = load_radar_cube("2", frame_str, DATASET_ROOT)
    assert cube.shape == (D, H, W), f"Unexpected shape: {cube.shape}"

    t0 = time.perf_counter()
    nf = prepare_frame_radar(cube)
    t = time.perf_counter() - t0
    bench_times.append(t)

    valid = cube > 0
    nf_valid = nf[valid]
    print(f"  Frame {frame_str}: {t:.4f}s  (valid: {valid.sum():,}/{cube.size:,}, "
          f"NF range: [{nf_valid.min():.2f}, {nf_valid.max():.2f}] dB)")

mean_t = float(np.mean(bench_times))
std_t = float(np.std(bench_times))
min_t = float(np.min(bench_times))
max_t = float(np.max(bench_times))
print(f"\n  Mean:   {mean_t:.4f}s")
print(f"  Std:    {std_t:.4f}s")
print(f"  Range:  {min_t:.4f} – {max_t:.4f}s")
print(f"  vs. original ~430s:  speedup = {430.0 / mean_t:.0f}×")
print(f"  400-frame projection: {400 * mean_t / 60:.1f} min ({400 * mean_t / 3600:.3f} hr)")
print(f"  vs 430s/frame original: 400 frames = 47.8 hr")


# ===========================================================================
# PER-OBJECT SCORE TABLE — real frames with ≥2 objects
# ===========================================================================
print("\n" + "=" * 72)
print("ITEM 6: PER-OBJECT SCORE TABLE — real frames with ≥2 objects")
print("=" * 72)

# Find frames in sequence 2 that have ≥2 objects AND have a radar cube
label_dir = DATASET_ROOT / "data" / "2" / "info_label_rev2"
cube_dir = DATASET_ROOT / "data" / "2" / "radar_zyx_cube"

multi_obj_frames = []
all_label_files = sorted(label_dir.glob("*.txt"))

# Group by frame number and count objects per frame
from collections import defaultdict
frame_objects = defaultdict(list)
for f in all_label_files:
    frame_str = f.stem.split("_")[0]
    try:
        _, objs = parse_label_file(f)
    except Exception:
        continue
    frame_objects[frame_str].extend(objs)

# Filter to frames with ≥2 objects
candidate_frames = []
for frame_str, objs in frame_objects.items():
    if len(objs) >= 2:
        # Check cube exists
        cube_file = cube_dir / f"cube_{frame_str}.mat"
        if cube_file.exists():
            candidate_frames.append((frame_str, objs))

print(f"  Found {len(candidate_frames)} frames with ≥2 objects in sequence 2")
print(f"  Using up to 7 frames for per-object scoring\n")

# Take up to 7 frames
test_multi_frames = candidate_frames[:7]

all_scores = []  # list of dicts
frame_cfar_times = []

for frame_str, objs in test_multi_frames:
    # Load cube and compute noise floor ONCE
    cube = load_radar_cube("2", frame_str, DATASET_ROOT)
    valid_mask = cube > 0
    cube_db = np.full(cube.shape, -100.0, dtype=np.float64)
    cube_db[valid_mask] = 10.0 * np.log10(cube[valid_mask])

    t0 = time.perf_counter()
    noise_map = prepare_frame_radar(cube)
    t_cfar = time.perf_counter() - t0
    frame_cfar_times.append(t_cfar)

    print(f"  Frame {frame_str}: {len(objs)} objects, CFAR {t_cfar:.4f}s")

    for obj in objs:
        bbox = _bbox_voxels_from_annotation(obj)

        # Score with CFAR
        score_cfar = compute_radar_sparsity_score(
            cube, bbox, noise_floor_db=noise_map,
            cube_db=cube_db, valid_mask=valid_mask,
        )

        # Score with global median (no CFAR)
        score_global = compute_radar_sparsity_score(
            cube, bbox, noise_floor_db=None,
            cube_db=cube_db, valid_mask=valid_mask,
        )

        # Local noise floor in bbox
        nf_subset = noise_map[bbox['z_min']:bbox['z_max'],
                              bbox['y_min']:bbox['y_max'],
                              bbox['x_min']:bbox['x_max']]
        local_nf = float(np.median(nf_subset[nf_subset > -100.0])) if np.any(nf_subset > -100.0) else -100.0

        all_scores.append({
            'frame': frame_str,
            'tracking_id': obj.tracking_id,
            'obj_class': obj.obj_class,
            'distance': obj.distance_ego,
            'score_cfar': score_cfar,
            'score_global': score_global,
            'diff': score_cfar - score_global,
            'local_nf': local_nf,
        })

# Print the table
print(f"\n{'Frame':<8} {'TrkID':<8} {'Class':<18} {'Dist(m)':<10} {'Score_CFAR':<12} {'Score_Global':<14} {'Diff':<10} {'Loc_NF(dB)':<12}")
print("-" * 100)

for r in all_scores:
    print(f"{r['frame']:<8} {r['tracking_id']:<8} {r['obj_class']:<18} {r['distance']:<10.2f} "
          f"{r['score_cfar']:<12.6f} {r['score_global']:<14.6f} {r['diff']:<+10.6f} {r['local_nf']:<12.2f}")

# Summary
scores_cfar = np.array([r['score_cfar'] for r in all_scores])
scores_global = np.array([r['score_global'] for r in all_scores])
print(f"\nTotal objects: {len(all_scores)} across {len(test_multi_frames)} frames")
print(f"All scores in [0,1]: {all(0.0 <= r['score_cfar'] <= 1.0 for r in all_scores)}")
print(f"CFAR   — min: {scores_cfar.min():.6f}, max: {scores_cfar.max():.6f}, "
      f"mean: {scores_cfar.mean():.6f}, std: {scores_cfar.std():.6f}")
print(f"Global — min: {scores_global.min():.6f}, max: {scores_global.max():.6f}, "
      f"mean: {scores_global.mean():.6f}, std: {scores_global.std():.6f}")

# Per-frame spread
print(f"\nPer-frame score spread:")
for frame_str, objs in test_multi_frames:
    f_scores = [r['score_cfar'] for r in all_scores if r['frame'] == frame_str]
    if len(f_scores) >= 2:
        print(f"  Frame {frame_str}: {len(f_scores)} objects, range [{min(f_scores):.4f}, {max(f_scores):.4f}], "
              f"spread = {max(f_scores) - min(f_scores):.4f}")
    else:
        print(f"  Frame {frame_str}: {len(f_scores)} object(s), score = {f_scores[0]:.6f}")

# Local adaptivity check: correlation between noise floor and score
print(f"\nLocal adaptivity (NF→score correlation):")
for frame_str, objs in test_multi_frames:
    f_entries = [r for r in all_scores if r['frame'] == frame_str]
    if len(f_entries) >= 3:
        nf_vals = [r['local_nf'] for r in f_entries]
        sc_vals = [r['score_cfar'] for r in f_entries]
        corr = float(np.corrcoef(nf_vals, sc_vals)[0, 1])
        print(f"  Frame {frame_str}: r(NF, score) = {corr:.4f}  ({len(f_entries)} objects)")
    else:
        nf_vals = [r['local_nf'] for r in f_entries]
        sc_vals = [r['score_cfar'] for r in f_entries]
        if len(f_entries) == 2 and nf_vals[0] != nf_vals[1]:
            # Manual calculation for 2 points
            nf_arr = np.array(nf_vals)
            sc_arr = np.array(sc_vals)
            corr = float(np.corrcoef(nf_arr, sc_arr)[0, 1])
            print(f"  Frame {frame_str}: r(NF, score) = {corr:.4f}  ({len(f_entries)} objects)")
        else:
            print(f"  Frame {frame_str}: insufficient variation ({len(f_entries)} objects)")

print("\nDone.")