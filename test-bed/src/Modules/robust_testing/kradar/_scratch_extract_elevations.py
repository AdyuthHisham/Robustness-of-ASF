"""
Scratch script: Extract real per-channel elevation angles from OS1-128 PCD data.
No source files are modified.
"""
import numpy as np
from pathlib import Path

DATA_ROOT = Path("/home/adhish/Productivity/AMSCUP/repos/K-Radar/data/2/os1-128")
PCD_FILE = DATA_ROOT / "os1-128_00001.pcd"  # First frame

def read_organized_pcd(filepath):
    """Read an ASCII organized PCD file and return points grouped by ring.
    Returns dict: ring -> list of (x, y, z)"""
    rings = {}
    with open(filepath, 'r') as f:
        # Read header
        header_lines = []
        while True:
            line = f.readline().strip()
            header_lines.append(line)
            if line.startswith('DATA'):
                data_type = line.split()[-1]
                break
        
        # Parse header
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
        
        ring_idx = fields.index('ring')
        x_idx = fields.index('x')
        y_idx = fields.index('y')
        z_idx = fields.index('z')
        
        print(f"Fields: {fields}")
        print(f"Width: {width}, Height: {height}")
        print(f"Ring at index: {ring_idx}, x/y/z at: {x_idx},{y_idx},{z_idx}")
        
        if data_type == 'ascii':
            for line_num, line in enumerate(f):
                parts = line.strip().split()
                if len(parts) < len(fields):
                    continue
                x, y, z = float(parts[x_idx]), float(parts[y_idx]), float(parts[z_idx])
                ring = int(parts[ring_idx])
                if ring not in rings:
                    rings[ring] = []
                rings[ring].append((x, y, z))
    
    return rings, width, height

def compute_elevation_angles(rings):
    """For each ring, compute mean elevation angle from x,y,z."""
    results = {}
    for ring in sorted(rings.keys()):
        points = np.array(rings[ring])
        if len(points) == 0:
            results[ring] = None
            continue
        x, y, z = points[:, 0], points[:, 1], points[:, 2]
        range_ = np.sqrt(x**2 + y**2 + z**2)
        # Elevation = arcsin(z / range)
        elev = np.degrees(np.arcsin(z / np.maximum(range_, 1e-10)))
        results[ring] = {
            'mean_elev': float(np.mean(elev)),
            'std_elev': float(np.std(elev)),
            'min_elev': float(np.min(elev)),
            'max_elev': float(np.max(elev)),
            'n_points': len(points),
        }
    return results

# --- Main ---
for pcd_idx in [1, 40, 70, 100, 200]:
    pcd_file = DATA_ROOT / f"os1-128_{pcd_idx:05d}.pcd"
    if not pcd_file.exists():
        print(f"\n=== PCD {pcd_file.name} NOT FOUND ===")
        continue
    print(f"\n{'='*80}")
    print(f"=== PCD {pcd_file.name} ===")
    print(f"{'='*80}")
    rings, w, h = read_organized_pcd(pcd_file)
    angles = compute_elevation_angles(rings)
    
    if not angles:
        print("NO DATA")
        continue
    
    # Print all 128 channel angles
    print(f"\nPer-channel elevation angles (degrees):")
    print(f"{'Chan':>5} {'Mean':>8} {'Std':>8} {'Min':>8} {'Max':>8} {'N':>8}")
    for ring in sorted(angles.keys()):
        a = angles[ring]
        if a is None:
            print(f"{ring:5d} {'NO DATA':>8}")
        else:
            print(f"{ring:5d} {a['mean_elev']:8.3f} {a['std_elev']:8.3f} {a['min_elev']:8.3f} {a['max_elev']:8.3f} {a['n_points']:8d}")
    
    # Summary stats
    means = [angles[r]['mean_elev'] for r in sorted(angles.keys()) if angles[r] is not None]
    n_valid = len(means)
    print(f"\nSummary:")
    print(f"  Valid channels: {n_valid}/{h}")
    print(f"  Min mean elevation: {min(means):.3f} deg")
    print(f"  Max mean elevation: {max(means):.3f} deg")
    print(f"  Range: {max(means) - min(means):.3f} deg")
    
    # Compute the expected range from the assumed model: ±22.25 deg = 44.5 deg
    expected_range = 44.5
    print(f"  Expected VFOV: {expected_range} deg")
    print(f"  Measured VFOV: {max(means) - min(means):.3f} deg")
    
    # Check for systematic offset: is the midpoint around 0 deg or shifted?
    midpoint = (max(means) + min(means)) / 2.0
    print(f"  Midpoint: {midpoint:.3f} deg (expected 0.0 deg for level mount)")
    
    # Count channels above/below certain bands
    above_5 = sum(1 for m in means if m > 5)
    above_2 = sum(1 for m in means if m > 2)
    below_neg2 = sum(1 for m in means if m < -2)
    below_neg5 = sum(1 for m in means if m < -5)
    near_horizon = sum(1 for m in means if -2 <= m <= 2)
    print(f"\n  Bands:")
    print(f"    > +5 deg (sky/tall buildings): {above_5}/{n_valid}")
    print(f"    +2 to +5 deg: {above_2 - above_5}/{n_valid}")
    print(f"    -2 to +2 deg (near horizon): {near_horizon}/{n_valid}")
    print(f"    -5 to -2 deg: {below_neg2 - below_neg5}/{n_valid}")
    print(f"    < -5 deg (ground close): {below_neg5}/{n_valid}")

print("\n\nDONE")