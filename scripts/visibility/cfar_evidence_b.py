#!/usr/bin/env python3
"""Benchmark: load one cube, run all CFAR operations on it fresh each time.
"""
from amscup_paths import KRADAR_ROOT  # noqa: E402
import sys, time, numpy as np
from pathlib import Path

from kradar_visibility.data_loader import load_radar_cube
from kradar_visibility.radar_visibility import (
    prepare_frame_radar,
    _prepare_frame_radar_loop_reference,
    compute_radar_sparsity_score,
    DB_HEADROOM,
)

DATASET_ROOT = KRADAR_ROOT

# ============================================================
# 1. BENCHMARK: vectorized on 3 pre-loaded frames
# ============================================================
print("Loading frame 00135...")
t0 = time.perf_counter()
cube_135 = load_radar_cube("2", "00135", DATASET_ROOT)
print(f"  Loaded in {time.perf_counter()-t0:.1f}s, shape={cube_135.shape}")

print("Loading frame 00140...")
t0 = time.perf_counter()
cube_140 = load_radar_cube("2", "00140", DATASET_ROOT)
print(f"  Loaded in {time.perf_counter()-t0:.1f}s")

print("Loading frame 00152...")
t0 = time.perf_counter()
cube_152 = load_radar_cube("2", "00152", DATASET_ROOT)
print(f"  Loaded in {time.perf_counter()-t0:.1f}s")

# Benchmark vectorized on each (fresh load, so CFAR time excludes load)
print("\n=== ITEM 4+5: Numerical equivalence + Benchmarks ===")
frames_data = [("00135", cube_135), ("00140", cube_140), ("00152", cube_152)]

bench_times = []
for fname, cube in frames_data:
    valid = cube > 0
    t0 = time.perf_counter()
    nf = prepare_frame_radar(cube)
    t = time.perf_counter() - t0
    bench_times.append(t)
    nf_valid = nf[valid]
    print(f"  {fname} vectorized: {t:.4f}s  valid={valid.sum():,}/{cube.size:,}  "
          f"NF [{nf_valid.min():.2f}, {nf_valid.max():.2f}] dB")

mean_t = np.mean(bench_times)
std_t = np.std(bench_times)
print(f"\n  Mean: {mean_t:.4f}s  Std: {std_t:.4f}s  Range: {min(bench_times):.4f} - {max(bench_times):.4f}s")
print(f"  Speedup vs 430s: {430.0/mean_t:.0f}x")
print(f"  400 frames (CFAR + load): ~{400*(mean_t+100)/60:.1f} min ({(mean_t+100)*400:.0f}s CFAR+load)")
print(f"  400 frames (CFAR only): {400*mean_t/60:.1f} min")

# ============================================================
# 2. EQUIVALENCE: full-frame on 2 frames (each ~7min in loop)
#    We'll use a sub-cube approach for practicality
# ============================================================
print("\n=== Numerical equivalence on SUB-CUBES ===")
for fname, cube in [("00135", cube_135), ("00140", cube_140)]:
    z0, z1, y0, y1, x0, x1 = 60, 80, 180, 220, 20, 60
    sc = cube[z0:z1, y0:y1, x0:x1].copy()
    print(f"  {fname} sub-cube {sc.shape} ({sc.size:,} cells):")
    
    t0 = time.perf_counter()
    nf_loop = _prepare_frame_radar_loop_reference(sc)
    t_loop = time.perf_counter() - t0
    
    t0 = time.perf_counter()
    nf_vec = prepare_frame_radar(sc)
    t_vec = time.perf_counter() - t0
    
    valid_sc = sc > 0
    diff = np.abs(nf_vec[valid_sc] - nf_loop[valid_sc])
    print(f"    Loop: {t_loop:.4f}s  Vec: {t_vec:.4f}s")
    print(f"    Max abs diff: {diff.max():.6e}  Mean abs diff: {diff.mean():.6e}")
    print(f"    Bit-identical: {diff.max() == 0.0}")

# ============================================================
# 3. CFAR on sub-cube with np.mean to test the alternative
# ============================================================
print("\n=== Quick check: mean vs median in original loop ===")
sc = cube_135[60:80, 180:220, 20:60].copy()
valid_sc = sc > 0
cube_db_sc = np.full(sc.shape, -100.0, dtype=np.float64)
cube_db_sc[valid_sc] = 10.0 * np.log10(sc[valid_sc])
print(f"  Global median of valid cells: {np.median(cube_db_sc[valid_sc]):.2f} dB")
print(f"  Global mean of valid cells:   {np.mean(cube_db_sc[valid_sc]):.2f} dB")

# Check what the loop reference uses (line 216):
# noise_floor_db[z, y, x] = np.median(training_array)
print(f"  Original loop reduction: np.median (line 216 of radar_visibility.py)")

# ============================================================
# 4. Per-object scoring on multi-object frames
# ============================================================
print("\n=== ITEM 6: Per-object scores on real multi-object frames ===")
from kradar_visibility.pipeline import _bbox_voxels_from_annotation
from kradar_visibility.parser import parse_label_file

# Reuse cubes already loaded. We need frames with ≥2 objects.
# From earlier analysis: frames 00135, 00140, 00152 have 2 objects each.
# Let's load a couple more.
for extra in ["00155", "00160", "00213"]:
    print(f"  Loading frame {extra}...")
    t0 = time.perf_counter()
    locals()[f"cube_{extra}"] = load_radar_cube("2", extra, DATASET_ROOT)
    print(f"    Done in {time.perf_counter()-t0:.1f}s")

multi_frames = ["00135", "00140", "00152", "00155", "00160", "00213"]
all_scores = []

for fname in multi_frames:
    cube = locals()[f"cube_{fname}"]
    valid = cube > 0
    cube_db = np.full(cube.shape, -100.0, dtype=np.float64)
    cube_db[valid] = 10.0 * np.log10(cube[valid])
    
    # Parse objects
    label_dir = DATASET_ROOT / "data" / "2" / "info_label_rev2"
    objs = []
    for f in sorted(label_dir.glob("*.txt")):
        if f.stem.split("_")[0] == fname:
            _, parsed_objs = parse_label_file(f)
            objs.extend(parsed_objs)
    
    print(f"  Frame {fname}: {len(objs)} objects")
    
    if len(objs) < 2:
        print(f"    SKIP: only {len(objs)} objects")
        continue
    
    t0 = time.perf_counter()
    noise_map = prepare_frame_radar(cube)
    t_cfar = time.perf_counter() - t0
    print(f"    CFAR: {t_cfar:.4f}s")
    
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
            'frame': fname,
            'tracking_id': obj.tracking_id,
            'class': obj.obj_class,
            'distance': obj.distance_ego,
            'score_cfar': score_cfar,
            'score_global': score_global,
            'diff': score_cfar - score_global,
            'local_nf': local_nf,
        })

print(f"\n{'Frame':<8} {'TrkID':<8} {'Class':<18} {'Dist(m)':<10} {'Score_CFAR':<12} {'Score_Glob':<12} {'Diff':<10} {'Loc_NF':<8}")
print("-" * 96)
for r in all_scores:
    print(f"{r['frame']:<8} {r['tracking_id']:<8} {r['class']:<18} {r['distance']:<10.2f} "
          f"{r['score_cfar']:<12.6f} {r['score_global']:<12.6f} {r['diff']:<+10.6f} {r['local_nf']:<8.2f}")

scores_cfar = np.array([r['score_cfar'] for r in all_scores])
print(f"\nTotal: {len(all_scores)} objects across {len(multi_frames)} frames")
print(f"CFAR all in [0,1]: {bool((scores_cfar >= 0).all() and (scores_cfar <= 1).all())}")
print(f"CFAR scores: min={scores_cfar.min():.6f} max={scores_cfar.max():.6f} mean={scores_cfar.mean():.6f} std={scores_cfar.std():.6f}")

print("\nPer-frame score spread:")
for fname in multi_frames:
    f_scores = [r['score_cfar'] for r in all_scores if r['frame'] == fname]
    if len(f_scores) >= 2:
        print(f"  {fname}: range [{min(f_scores):.4f}, {max(f_scores):.4f}] spread={max(f_scores)-min(f_scores):.4f}")
    elif len(f_scores) == 1:
        print(f"  {fname}: single score = {f_scores[0]:.6f}")
    else:
        print(f"  {fname}: no objects")

# Local adaptivity: correlation
print("\nLocal adaptivity (NF→score correlation per frame):")
for fname in multi_frames:
    f_entries = [r for r in all_scores if r['frame'] == fname]
    if len(f_entries) >= 2:
        nf_vals = [r['local_nf'] for r in f_entries]
        sc_vals = [r['score_cfar'] for r in f_entries]
        corr = float(np.corrcoef(nf_vals, sc_vals)[0, 1])
        print(f"  {fname} ({len(f_entries)} objects): r(NF, score) = {corr:.4f}")
    else:
        print(f"  {fname}: insufficient objects ({len(f_entries)})")

# Also check: # of real (non-synthetic) frames the prior benchmark was run on
# and whether the summary claim was benchmark-only or total time.
print(f"\nNOTE: Cube loading takes ~100s per file. The 10.6s/figure in the summary is CFAR-only.")
print(f"Total frame time with loading: ~{100+mean_t:.1f}s per frame. For 400 frames: {400*(100+mean_t)/3600:.2f} hrs")
print(f"(The summary's 430s estimate was loop-body-only; total would be ~530s)")

print("\nDone.")