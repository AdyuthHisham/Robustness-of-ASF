#!/usr/bin/env python3
"""Part 2: Per-object scoring on real multi-object frames (sequence 2)."""
from amscup_paths import KRADAR_ROOT  # noqa: E402
import sys, time, numpy as np
from pathlib import Path
from collections import defaultdict

from kradar_visibility.data_loader import load_radar_cube
from kradar_visibility.radar_visibility import (
    prepare_frame_radar,
    compute_radar_sparsity_score,
)
from kradar_visibility.pipeline import _bbox_voxels_from_annotation
from kradar_visibility.parser import parse_label_file

DATASET_ROOT = KRADAR_ROOT

# Find frames with >=2 objects
label_dir = DATASET_ROOT / "data" / "2" / "info_label_rev2"
cube_dir = DATASET_ROOT / "data" / "2" / "radar_zyx_cube"

frame_objs = defaultdict(list)
for f in sorted(label_dir.glob("*.txt")):
    frame_str = f.stem.split("_")[0]
    try:
        _, objs = parse_label_file(f)
    except:
        continue
    frame_objs[frame_str].extend(objs)

# Filter cubes that exist
candidates = sorted((fs, objs) for fs, objs in frame_objs.items() if len(objs) >= 2 and (cube_dir / f"cube_{fs}.mat").exists())
print(f"Found {len(candidates)} frames with >=2 objects in seq 2")
for fs, objs in candidates[:15]:
    print(f"  Frame {fs}: {len(objs)} objects")

# Use first 7
use_frames = candidates[:7]
print(f"\nUsing {len(use_frames)} frames")

# We'll store cubes in a proper dict
cubes = {}
all_scores = []

for frame_str, objs in use_frames:
    print(f"\nLoading frame {frame_str} ({len(objs)} objects)...")
    t0 = time.perf_counter()
    cube = load_radar_cube("2", frame_str, DATASET_ROOT)
    t_load = time.perf_counter() - t0
    print(f"  Loaded in {t_load:.1f}s")

    valid = cube > 0
    cube_db = np.full(cube.shape, -100.0, dtype=np.float64)
    cube_db[valid] = 10.0 * np.log10(cube[valid])

    t0 = time.perf_counter()
    noise_map = prepare_frame_radar(cube)
    t_cfar = time.perf_counter() - t0
    print(f"  CFAR: {t_cfar:.4f}s")

    for obj in objs:
        bbox = _bbox_voxels_from_annotation(obj)

        score_cfar = compute_radar_sparsity_score(
            cube, bbox, noise_floor_db=noise_map,
            cube_db=cube_db, valid_mask=valid,
        )
        score_global = compute_radar_sparsity_score(
            cube, bbox, noise_floor_db=None,
            cube_db=cube_db, valid_mask=valid,
        )

        nf_subset = noise_map[bbox['z_min']:bbox['z_max'],
                              bbox['y_min']:bbox['y_max'],
                              bbox['x_min']:bbox['x_max']]
        local_nf = float(np.median(nf_subset[nf_subset > -100.0])) if np.any(nf_subset > -100.0) else -100.0

        all_scores.append({
            'frame': frame_str,
            'tracking_id': obj.tracking_id,
            'class': obj.obj_class,
            'distance': obj.distance_ego,
            'score_cfar': score_cfar,
            'score_global': score_global,
            'diff': score_cfar - score_global,
            'local_nf': local_nf,
        })

# ========== Print results ==========
print("\n" + "=" * 96)
print("PER-OBJECT SCORE TABLE")
print("=" * 96)
print(f"{'Frame':<8} {'TrkID':<8} {'Class':<18} {'Dist(m)':<10} {'Score_CFAR':<12} {'Score_Glb':<12} {'Diff':<10} {'Loc_NF':<8}")
print("-" * 96)
for r in all_scores:
    print(f"{r['frame']:<8} {r['tracking_id']:<8} {r['class']:<18} {r['distance']:<10.2f} "
          f"{r['score_cfar']:<12.6f} {r['score_global']:<12.6f} {r['diff']:<+10.6f} {r['local_nf']:<8.2f}")

scores_cfar = np.array([r['score_cfar'] for r in all_scores])
print(f"\nTotal: {len(all_scores)} objects across {len(use_frames)} frames")
print(f"CFAR all in [0,1]: {bool((scores_cfar >= -1e-12).all() and (scores_cfar <= 1.0+1e-12).all())}")
print(f"CFAR: min={scores_cfar.min():.6f} max={scores_cfar.max():.6f} mean={scores_cfar.mean():.6f} std={scores_cfar.std():.6f}")

print("\nPer-frame score spread:")
for frame_str, objs in use_frames:
    f_scores = [r['score_cfar'] for r in all_scores if r['frame'] == frame_str]
    if len(f_scores) >= 2:
        print(f"  {frame_str}: [{min(f_scores):.4f}, {max(f_scores):.4f}] spread={max(f_scores)-min(f_scores):.4f}")

print("\nLocal adaptivity (NF→score correlation per frame):")
for frame_str, objs in use_frames:
    f_entries = [r for r in all_scores if r['frame'] == frame_str]
    nf_vals = [r['local_nf'] for r in f_entries]
    sc_vals = [r['score_cfar'] for r in f_entries]
    if len(f_entries) >= 2 and len(set(nf_vals)) >= 2:
        corr = float(np.corrcoef(nf_vals, sc_vals)[0, 1])
        print(f"  {frame_str} ({len(f_entries)} objects): r(NF, score) = {corr:+.4f}")
    else:
        print(f"  {frame_str} ({len(f_entries)} objects): insufficient variation (nf_distinct={len(set(nf_vals))})")

print("\nDone.")