"""Debug: Use pipeline's own methods to compute frame 200 bbox & point count."""
import sys, numpy as np
from pathlib import Path

# Add the source to path
sys.path.insert(0, str(Path("/home/adhish/Productivity/AMSCUP/test-bed/src/Modules/robust_testing/kradar/src")))
from kradar_visibility.data_loader import read_pcd_file
from kradar_visibility.parser import parse_label_file

DATA = Path("/home/adhish/Productivity/AMSCUP/repos/K-Radar")
SEQ = "2"
FRAME = 200

# --- Get annotation directly ---
label_file = DATA / "data" / SEQ / "info_label_rev2" / "00200_00170.txt"
header, objects = parse_label_file(label_file)
obj = objects[0]

print(f"Object annotation:")
print(f"  Class: {obj.obj_class}")
print(f"  Tracking ID: {obj.tracking_id}")
print(f"  Center: ({obj.x:.3f}, {obj.y:.3f}, {obj.z:.3f})")
print(f"  Theta: {obj.theta:.4f} rad = {np.degrees(obj.theta):.2f}°")
print(f"  Half extents: L={obj.length_half:.3f}, W={obj.width_half:.3f}, H={obj.height_half:.3f}")
print(f"  Full dims: L={obj.length:.3f}, W={obj.width:.3f}, H={obj.height:.3f}")
print(f"  Distance: {obj.distance_ego:.2f}m")

# --- Build bbox using pipeline's method ---
from kradar_visibility.pipeline import _bbox_list_from_annotation
bbox = _bbox_list_from_annotation(obj)
print(f"\nPipeline bbox: x=[{bbox[0]:.3f},{bbox[1]:.3f}] y=[{bbox[2]:.3f},{bbox[3]:.3f}] z=[{bbox[4]:.3f},{bbox[5]:.3f}]")

# Also compute simple half-extent bbox (axis-aligned, no rotation)
hbbox = [
    obj.x - obj.length_half, obj.x + obj.length_half,
    obj.y - obj.width_half, obj.y + obj.width_half,
    obj.z - obj.height_half, obj.z + obj.height_half,
]
print(f"Simple AABB: x=[{hbbox[0]:.3f},{hbbox[1]:.3f}] y=[{hbbox[2]:.3f},{hbbox[3]:.3f}] z=[{hbbox[4]:.3f},{hbbox[5]:.3f}]")

# --- Load OS1-128 points ---
os1_file = DATA / "data" / SEQ / "os1-128" / f"os1-128_{header.os1_128_idx}.pcd"
print(f"\nLoading: {os1_file}")
pts = read_pcd_file(os1_file)
print(f"Points shape: {pts.shape}")
print(f"Point range: x=[{pts[:,0].min():.3f},{pts[:,0].max():.3f}] y=[{pts[:,1].min():.3f},{pts[:,1].max():.3f}] z=[{pts[:,2].min():.3f},{pts[:,2].max():.3f}]")

# Remove zero-range points
valid = (pts[:,0]!=0)|(pts[:,1]!=0)|(pts[:,2]!=0)
pts_f = pts[valid]
print(f"Valid (non-zero) points: {len(pts_f)}/{len(pts)}")
print(f"Valid range: x=[{pts_f[:,0].min():.3f},{pts_f[:,0].max():.3f}] y=[{pts_f[:,1].min():.3f},{pts_f[:,1].max():.3f}] z=[{pts_f[:,2].min():.3f},{pts_f[:,2].max():.3f}]")

# Print some sample points near where box should be
near = (pts_f[:,0] > 2) & (pts_f[:,0] < 15) & (pts_f[:,1] > -10) & (pts_f[:,1] < 5) & (pts_f[:,2] > -3) & (pts_f[:,2] < 4)
nearby = pts_f[near]
print(f"\nPoints near box region (x=2..15, y=-10..5, z=-3..4): {len(nearby)}")
if len(nearby) > 0:
    print(f"First 20 sample points in region:")
    for i in range(min(20, len(nearby))):
        print(f"  ({nearby[i,0]:.3f}, {nearby[i,1]:.3f}, {nearby[i,2]:.3f})")
    
# --- Count using pipeline bbox ---
xmin,xmax,ymin,ymax,zmin,zmax = bbox
mask = (pts_f[:,0]>=xmin)&(pts_f[:,0]<=xmax)&(pts_f[:,1]>=ymin)&(pts_f[:,1]<=ymax)&(pts_f[:,2]>=zmin)&(pts_f[:,2]<=zmax)
count_pipeline = int(np.sum(mask))
print(f"\n--- FINAL RESULT ---")
print(f"Points in pipeline bbox: {count_pipeline}/{len(pts_f)} ({100*count_pipeline/len(pts_f):.2f}%)")

# Also count in simple AABB
xmin,xmax,ymin,ymax,zmin,zmax = hbbox
mask2 = (pts_f[:,0]>=xmin)&(pts_f[:,0]<=xmax)&(pts_f[:,1]>=ymin)&(pts_f[:,1]<=ymax)&(pts_f[:,2]>=zmin)&(pts_f[:,2]<=zmax)
count_simple = int(np.sum(mask2))
print(f"Points in simple AABB: {count_simple}/{len(pts_f)} ({100*count_simple/len(pts_f):.2f}%)")