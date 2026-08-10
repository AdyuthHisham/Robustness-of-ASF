"""
V2: Filter zero-range (no-return) points before computing elevations.
Also: compute the actual beam angle from geometry -- for channels hitting the
ground, the elevation should equal the beam angle (for a flat ground plane).
"""
import numpy as np
from pathlib import Path

DATA_ROOT = Path("/home/adhish/Productivity/AMSCUP/repos/K-Radar/data/2/os1-128")

def read_organized_pcd_raw(filepath):
    """Read organized PCD and return all points as structured array."""
    with open(filepath, 'r') as f:
        header_lines = []
        while True:
            line = f.readline().strip()
            header_lines.append(line)
            if line.startswith('DATA'):
                data_type = line.split()[-1]
                break
        
        fields = []
        width = 0
        height = 0
        for h in header_lines:
            if h.startswith('FIELDS'):
                fields = h.split()[1:]
            elif h.startswith('WIDTH'):
                width = int(h.split()[1])
            elif h.startswith('HEIGHT'):
                height = int(h.split()[1])
        
        if data_type != 'ascii':
            raise ValueError("Expected ASCII PCD")
        
        ring_idx = fields.index('ring')
        x_idx = fields.index('x')
        y_idx = fields.index('y')
        z_idx = fields.index('z')
        
        # Read all points
        all_points = []
        for line in f:
            parts = line.strip().split()
            if len(parts) >= len(fields):
                x, y, z = float(parts[x_idx]), float(parts[y_idx]), float(parts[z_idx])
                ring = int(parts[ring_idx])
                all_points.append((ring, x, y, z))
    
    return np.array(all_points, dtype=[('ring', 'i4'), ('x', 'f4'), ('y', 'f4'), ('z', 'f4')]), width, height, fields


for pcd_idx in [1, 40, 70, 71, 100, 200]:
    pcd_file = DATA_ROOT / f"os1-128_{pcd_idx:05d}.pcd"
    if not pcd_file.exists():
        continue
    
    print(f"\n{'='*80}")
    print(f"PCD {pcd_file.name}")
    print(f"{'='*80}")
    
    pts, w, h, fields = read_organized_pcd_raw(pcd_file)
    
    # Filter valid points (not zero-range)
    valid_mask = (pts['x'] != 0.0) | (pts['y'] != 0.0) | (pts['z'] != 0.0)
    valid = pts[valid_mask]
    
    # Filter invalid (zero-range = no return)
    nos_return = pts[~valid_mask]
    
    print(f"  Total points: {len(pts)}")
    print(f"  Valid returns: {len(valid)} ({100*len(valid)/len(pts):.1f}%)")
    print(f"  No-return (0,0,0): {len(nos_return)} ({100*len(nos_return)/len(pts):.1f}%)")
    print(f"  Organization: {h} channels x {w} azimuth bins")
    print()
    
    # Per-channel analysis
    print(f"{'Chan':>5} {'Valid':>7} {'Valid%':>8} {'Elev_Mean':>10} {'Elev_Min':>9} {'Elev_Max':>9} {'Rng_Mean':>9}")
    print("-" * 60)
    
    for ring in range(h):
        ring_pts = valid[valid['ring'] == ring]
        n_valid = len(ring_pts)
        pct = 100.0 * n_valid / w
        
        if n_valid > 0:
            x = ring_pts['x']
            y = ring_pts['y']
            z = ring_pts['z']
            r = np.sqrt(x**2 + y**2 + z**2)
            elev = np.degrees(np.arcsin(z / np.maximum(r, 1e-10)))
            
            # Sort by range and only consider points at non-trivial range (>1m) for elevation
            # This filters out noise points very close to the sensor
            far_mask = r > 1.0
            if np.any(far_mask):
                elev_far = elev[far_mask]
                r_far = r[far_mask]
                print(f"{ring:5d} {n_valid:7d} {pct:7.1f}% {np.mean(elev_far):9.3f}° {np.min(elev):8.3f}° {np.max(elev):8.3f}° {np.mean(r_far):8.2f}m")
            else:
                print(f"{ring:5d} {n_valid:7d} {pct:7.1f}% {'N/A':>10} {'N/A':>9} {'N/A':>9} {'N/A':>9}")
        else:
            print(f"{ring:5d} {0:7d} {'0.0%':>8} {'—':>10} {'—':>9} {'—':>9} {'—':>9}")
    
    # Summary
    print(f"\n  CHANNEL SUMMARY (valid returns only, range>1m):")
    all_elevs = []
    for ring in range(h):
        ring_pts = valid[valid['ring'] == ring]
        if len(ring_pts) > 0:
            x, y, z = ring_pts['x'], ring_pts['y'], ring_pts['z']
            r = np.sqrt(x**2 + y**2 + z**2)
            far = r > 1.0
            if np.any(far):
                elev = np.degrees(np.arcsin(z[far] / np.maximum(r[far], 1e-10)))
                all_elevs.extend(elev)
    
    all_elevs = np.array(all_elevs)
    if len(all_elevs) > 0:
        print(f"  All valid-point elevations: mean={np.mean(all_elevs):.3f}° min={np.min(all_elevs):.3f}° max={np.max(all_elevs):.3f}°")
    
    # Count valid returns per channel band
    print(f"\n  VALID RETURN RATE BY BAND:")
    bands = [(0, 19, "Ch 0-19 (top)"),
             (20, 49, "Ch 20-49"),
             (50, 65, "Ch 50-65 (horizon band)"),
             (66, 99, "Ch 66-99"),
             (100, 127, "Ch 100-127 (bottom)")]
    for lo, hi, label in bands:
        ring_pts_total = sum(len(valid[valid['ring'] == r]) for r in range(lo, hi+1))
        expected = (hi - lo + 1) * w
        pct = 100.0 * ring_pts_total / expected
        print(f"  {label}: {ring_pts_total}/{expected} = {pct:.1f}% valid")
    
    # For the horizon channels (50-65): what fraction hit objects > 30m?
    print(f"\n  LONG-RANGE (>30m) COVERAGE BY BAND:")
    for lo, hi, label in bands:
        ring_pts = valid[(valid['ring'] >= lo) & (valid['ring'] <= hi)]
        if len(ring_pts) > 0:
            r = np.sqrt(ring_pts['x']**2 + ring_pts['y']**2 + ring_pts['z']**2)
            far = np.sum(r > 30.0)
            very_far = np.sum(r > 80.0)
            print(f"  {label}: {far} >30m, {very_far} >80m")


print("\n\nDONE")