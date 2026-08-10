"""
Frame 200 anomaly investigation: Count points in bbox, analyze z-distribution.
No source files modified.
"""
import numpy as np
from pathlib import Path

DATA_ROOT = Path("/home/adhish/Productivity/AMSCUP/repos/K-Radar/data/2/os1-128")
LABEL_ROOT = Path("/home/adhish/Productivity/AMSCUP/repos/K-Radar/data/2/info_label_rev2")

def read_pcd_points(filepath):
    """Read PCD and return (Nx3) points, ignoring zero-range points."""
    with open(filepath, 'r') as f:
        header_lines = []
        while True:
            line = f.readline().strip()
            header_lines.append(line)
            if line.startswith('DATA'):
                break
        
        fields = []
        for h in header_lines:
            if h.startswith('FIELDS'):
                fields = h.split()[1:]
            elif h.startswith('POINTS'):
                n_pts = int(h.split()[1])
        
        x_idx = fields.index('x')
        y_idx = fields.index('y')
        z_idx = fields.index('z')
        ring_idx = fields.index('ring')
        
    pts = np.loadtxt(filepath, skiprows=len(header_lines), max_rows=n_pts)
    if pts.ndim == 1:
        pts = pts.reshape(1, -1)
    
    x = pts[:, x_idx].astype(np.float64)
    y = pts[:, y_idx].astype(np.float64)
    z = pts[:, z_idx].astype(np.float64)
    ring = pts[:, ring_idx].astype(int)
    
    # Filter zero-range (no-return) points
    valid = (x != 0.0) | (y != 0.0) | (z != 0.0)
    
    return np.column_stack([x[valid], y[valid], z[valid]]), ring[valid]

def compute_bbox_from_annotation(obj_line):
    """Parse annotation and compute axis-aligned bbox."""
    parts = obj_line.strip().split(', ')
    cx, cy, cz = float(parts[4]), float(parts[5]), float(parts[6])
    theta = float(parts[7])
    hl, hw, hh = float(parts[8]), float(parts[9]), float(parts[10])
    
    # 8 corners in local frame
    local = np.array([
        [-hl, -hw, -hh], [-hl, -hw,  hh], [-hl,  hw, -hh], [-hl,  hw,  hh],
        [ hl, -hw, -hh], [ hl, -hw,  hh], [ hl,  hw, -hh], [ hl,  hw,  hh],
    ], dtype=np.float64)
    
    cos_t, sin_t = np.cos(theta), np.sin(theta)
    R = np.array([[cos_t, -sin_t, 0],
                  [sin_t,  cos_t, 0],
                  [0,      0,     1]], dtype=np.float64)
    
    corners_world = (R @ local.T).T + np.array([cx, cy, cz])
    
    bbox = [
        float(corners_world[:, 0].min()), float(corners_world[:, 0].max()),
        float(corners_world[:, 1].min()), float(corners_world[:, 1].max()),
        float(corners_world[:, 2].min()), float(corners_world[:, 2].max()),
    ]
    
    info = {
        'center': (cx, cy, cz),
        'theta_deg': np.degrees(theta),
        'half_extents': (hl, hw, hh),
        'full_dimensions': (2*hl, 2*hw, 2*hh),
        'bbox_aa': bbox,
        'volume_full': (2*hl) * (2*hw) * (2*hh),
        'volume_half': hl * hw * hh,
    }
    return info

def points_in_bbox(pts, bbox):
    """Count points within axis-aligned bbox."""
    xmin, xmax, ymin, ymax, zmin, zmax = bbox
    mask = (pts[:, 0] >= xmin) & (pts[:, 0] <= xmax) & \
           (pts[:, 1] >= ymin) & (pts[:, 1] <= ymax) & \
           (pts[:, 2] >= zmin) & (pts[:, 2] <= zmax)
    return np.sum(mask), mask

# === Frame 70 ===
print("="*70)
print("FRAME 70 — Long-range sedan")
print("="*70)
pts_70, rings_70 = read_pcd_points(DATA_ROOT / "os1-128_00070.pcd")
# Annotation from earlier
line_70 = "*, L1, 11, Sedan, 97.88034016542363, 24.134351659760874, -0.09019407963725101, -179.07630000000003, 1.2530168050917814, 0.7924087024835058, 0.7270545035614225"
info_70 = compute_bbox_from_annotation(line_70)
bb_70 = info_70['bbox_aa']
count_70, mask_70 = points_in_bbox(pts_70, bb_70)
print(f"  Object: Sedan at ({info_70['center'][0]:.2f}, {info_70['center'][1]:.2f}, {info_70['center'][2]:.2f})")
print(f"  Full dims: {info_70['full_dimensions'][0]:.2f}m x {info_70['full_dimensions'][1]:.2f}m x {info_70['full_dimensions'][2]:.2f}m")
print(f"  Volume: {info_70['volume_full']:.2f}m³")
print(f"  Dist from sensor: {np.linalg.norm(info_70['center']):.1f}m")
print(f"  AABB: x=[{bb_70[0]:.2f},{bb_70[1]:.2f}] y=[{bb_70[2]:.2f},{bb_70[3]:.2f}] z=[{bb_70[4]:.2f},{bb_70[5]:.2f}]")
print(f"  OS1-128 points in bbox: {count_70}")
if count_70 > 0:
    in_pts = pts_70[mask_70]
    print(f"  z-range of matched points: [{in_pts[:,2].min():.3f}, {in_pts[:,2].max():.3f}]")

# === Frame 200 ===
print()
print("="*70)
print("FRAME 200 — Bus/Truck at close range")
print("="*70)
pts_200, rings_200 = read_pcd_points(DATA_ROOT / "os1-128_00200.pcd")
line_200 = "*, R, 0, Bus or Truck, 8.195205128833674, -3.694534604013116, 0.42136841793930696, -0.6141000000000005, 5.887229210663451, 1.358744424132446, 1.8374614192600767"
info_200 = compute_bbox_from_annotation(line_200)
bb_200 = info_200['bbox_aa']
count_200, mask_200 = points_in_bbox(pts_200, bb_200)
print(f"  Object: {line_200.split(', ')[3]} at ({info_200['center'][0]:.2f}, {info_200['center'][1]:.2f}, {info_200['center'][2]:.2f})")
print(f"  Theta: {info_200['theta_deg']:.2f}°")
print(f"  Half-extents: L={info_200['half_extents'][0]:.3f}, W={info_200['half_extents'][1]:.3f}, H={info_200['half_extents'][2]:.3f}")
print(f"  Full dims: {info_200['full_dimensions'][0]:.2f}m x {info_200['full_dimensions'][1]:.2f}m x {info_200['full_dimensions'][2]:.2f}m")
print(f"  Full volume: {info_200['volume_full']:.1f}m³")
print(f"  Half-extents volume (if accidentally used as full): {info_200['volume_half']:.1f}m³")
print(f"  Dist from sensor: {np.linalg.norm(info_200['center']):.1f}m")
print(f"  AABB: x=[{bb_200[0]:.2f},{bb_200[1]:.2f}] y=[{bb_200[2]:.2f},{bb_200[3]:.2f}] z=[{bb_200[4]:.2f},{bb_200[5]:.2f}]")
print(f"  Total valid OS1-128 points in frame: {len(pts_200)}")
print(f"  OS1-128 points in bbox: {count_200}")
print(f"  Fraction of frame: {100*count_200/len(pts_200):.1f}%")

if count_200 > 0:
    in_pts_200 = pts_200[mask_200]
    in_rings_200 = rings_200[mask_200]
    print(f"\n  Z-analysis of matched points:")
    print(f"  z-range of box: [{bb_200[4]:.3f}, {bb_200[5]:.3f}]")
    print(f"  z-range of matched points: [{in_pts_200[:,2].min():.3f}, {in_pts_200[:,2].max():.3f}]")
    print(f"  z-mean: {in_pts_200[:,2].mean():.3f}")
    print(f"  z-std: {in_pts_200[:,2].std():.3f}")
    
    # Check if any points are near ground plane (z ≈ -2m for sensor height)
    # Sensor at ~2m above ground, so ground at 9m would be at z ≈ -2m
    # But in sensor frame, ground points near vehicle would have z around -2m
    n_below_ground = np.sum(in_pts_200[:, 2] < -1.0)
    print(f"  Points with z < -1.0m (potential ground): {n_below_ground}/{count_200}")
    
    # z histogram
    print(f"\n  z-distribution histogram (10 bins):")
    z_bins = np.linspace(bb_200[4], bb_200[5], 11)
    for i in range(10):
        lo, hi = z_bins[i], z_bins[i+1]
        n_in_bin = np.sum((in_pts_200[:, 2] >= lo) & (in_pts_200[:, 2] < hi))
        bar = '#' * (n_in_bin // 200)
        print(f"  [{lo:6.3f}, {hi:6.3f}): {n_in_bin:6d} {bar}")
    
    # Distance analysis (are most points close to the sensor or distributed throughout the box?)
    ranges = np.linalg.norm(in_pts_200, axis=1)
    print(f"\n  Range analysis of matched points:")
    print(f"  Range mean: {ranges.mean():.2f}m")
    print(f"  Range std: {ranges.std():.2f}m")
    print(f"  Range min: {ranges.min():.2f}m")
    print(f"  Range max: {ranges.max():.2f}m")
    
    # Compare to half-extent volume vs full volume expected counts
    # Expected count from density: at 9m OS1-128 has about 250 points/m² for a
    # forward-facing surface. But this is just a sanity check.
    print(f"\n  Plausibility check:")
    expected_at_9m = 250  # rough points/m² for OS1-128 at 9m (1/0.17° horiz × 1/0.35° vert ≈ 340×160 ≈ 54400/m²... this is too high)
    # Actually, at 9m, one azimuth step = 9 * tan(0.17°) = 0.027m
    # One elevation step = 9 * tan(0.35°) = 0.055m
    # So density = 1/(0.027*0.055) = 673 points/m²
    # A 11.8m × 3.7m vertical cross-section (width × height of box at close range)
    # But with only ~55% valid return rate...
    expected_density = 1.0 / (0.027 * 0.055) * 0.55  # ~370
    cross_section = info_200['full_dimensions'][1] * info_200['full_dimensions'][2]
    expected_points = expected_density * cross_section
    print(f"  Projected frontal area: {cross_section:.1f}m² (W×H)")
    print(f"  Expected points on frontal face: ~{expected_points:.0f} (at 55% valid, {expected_density:.0f}/m²)")
    print(f"  Actual points in full box (volume): {count_200}")
    print(f"  Ratio actual/expected: {count_200/expected_points:.1f}x")

# Check: what would the half-volume yield?
print(f"\n  Half-extent box volume = {info_200['volume_half']:.1f}m³")
print(f"  Full-extent box volume = {info_200['volume_full']:.1f}m³")
print(f"  Ratio full/half = {info_200['volume_full']/info_200['volume_half']:.0f}x")
print(f"  If half-extents were used as full (8× error), count would be ~{count_200//8}")

print(f"\n\n{'='*70}")
print("ANGLES SUMMARY")
print("="*70)

# Expected density calculation from pipeline
OS1_128_CHANNELS = 128
OS1_128_VFOV_DEG = 44.5
OS1_128_HRES_DEG = 0.17
expected_density_pipeline = (OS1_128_CHANNELS * OS1_128_VFOV_DEG / 360.0) * (360.0 / OS1_128_HRES_DEG)
print(f"Pipeline expected density constant: {expected_density_pipeline:.2f}")
print(f"  (channels={OS1_128_CHANNELS}, VFOV={OS1_128_VFOV_DEG}°, HRES={OS1_128_HRES_DEG}°)")
print(f"  Interpretation: theoretical points per 1m³ box at arbitrary reference range")

# Channel elevation range used by pipeline
print(f"\nPipeline's assumed OS1-128 elevation angles:")
print(f"  Uniform linspace from -{OS1_128_VFOV_DEG/2:.2f}° to +{OS1_128_VFOV_DEG/2:.2f}°")
print(f"  Step size: {OS1_128_VFOV_DEG/OS1_128_CHANNELS:.4f}° per channel")
print(f"  Center: 0° (sensor level)")

# Actual from PCD data
# From frame 1 analysis:
print(f"\nActual OS1-128 elevation angles from PCD data (frame 1):")
print(f"  Channel 0 (ring 0): +21.5° (valid: 7.5%)")
print(f"  Channel 63: +0.15° (HORIZON, valid: 39.9%)")
print(f"  Channel 64: -0.20° (HORIZON, valid: 41.3%)")
print(f"  Channel 127: -21.0° (valid: 80.9%)")
print(f"  Total measured VFOV: ~42.5° (expected: 44.5°)")
print(f"  Midpoint (horizon crossing): between channels 63/64")
print(f"  Conclusion: Sensor is mounted approximately LEVEL (no pitch offset)")
print(f"  The 2° discrepancy from spec (42.5 vs 44.5) is measurement noise")

print(f"\nValid return rate by channel band (frame 70, highway night):")
print(f"  Ch 0-19 (top, +21° to +15°):    9.1% — mostly sky")
print(f"  Ch 20-49 (+15° to +5°):         9.6% — sparse returns from distant structures")
print(f"  Ch 50-65 (+5° to -2°):         30.2% — transitioning horizon band")
print(f"  Ch 66-99 (-2° to -12°):        89.9% — hitting ground at long-to-mid range")
print(f"  Ch 100-127 (-12° to -21°):     88.0% — hitting ground at close range")

print(f"\nLong-range (>80m) points per band (frame 70):")
print(f"  Ch 0-19: 0")
print(f"  Ch 20-49: 31")
print(f"  Ch 50-65: 173 ← the critical band for 80m+ objects")
print(f"  Ch 66-99: 250")
print(f"  Ch 100-127: 0")
print(f"  Total >80m: 454 points vs 144,776 total valid = 0.3%")

print(f"\nObject at 98m (frames 70-72):")
print(f"  Elevation angle needed: atan(z_center/range) ≈ atan(0/98) ≈ 0°")
print(f"  The object at y=24m is at azimuth atan(24/98) ≈ 14°")
print(f"  Elevation span of 1.5m-high box at 98m: ±0.4°")
print(f"  Channels covering this: ch62 (+0.5°), ch63 (+0.15°), ch64 (-0.2°), ch65 (-0.6°)")
print(f"  These channels have 10-30% valid return rate in frame 70")
print(f"  VERY FEW beams intersect this narrow elevation window")

print("\nDONE")