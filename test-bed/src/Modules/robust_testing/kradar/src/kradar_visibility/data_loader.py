"""Lazy data loaders for all sensor types."""
from pathlib import Path
from typing import Optional, Tuple
import numpy as np
import scipy.io
import cv2


def load_radar_cube(sequence_id: str, frame_idx: str, dataset_root: Optional[Path] = None) -> Optional[np.ndarray]:
    """Load radar_zyx_cube .mat file for a given frame."""
    if dataset_root is None:
        dataset_root = Path("/home/adhish/Productivity/AMSCUP/repos/K-Radar")
    
    # Try cube_XXXXX.mat naming
    cube_dir = dataset_root / "data" / sequence_id / "radar_zyx_cube"
    mat_file = cube_dir / f"cube_{frame_idx}.mat"
    
    if not mat_file.exists():
        return None
    
    mat_data = scipy.io.loadmat(str(mat_file))
    data_keys = [k for k in mat_data.keys() if not k.startswith('__')]
    if not data_keys:
        return None
    
    return mat_data[data_keys[0]]


def read_pcd_file(filepath: Path) -> np.ndarray:
    """Read a PCD file and return points as Nx3 numpy array."""
    with open(filepath, 'rb') as f:
        header = []
        while True:
            line = f.readline()
            if not line:
                break
            line = line.decode('utf-8', errors='ignore').strip()
            header.append(line)
            if line.startswith('DATA'):
                data_type = line.split()[-1]
                break
        
        num_points = None
        for h in header:
            if h.startswith('POINTS'):
                num_points = int(h.split()[-1])
        
        if data_type == 'ascii':
            points = []
            for line in f:
                coords = line.decode('utf-8', errors='ignore').strip().split()
                if len(coords) >= 3:
                    points.append([float(coords[0]), float(coords[1]), float(coords[2])])
            return np.array(points, dtype=np.float32)
        else:
            data = np.fromfile(f, dtype=np.float32)
            if len(data) >= num_points * 3:
                return data[:num_points * 3].reshape(-1, 3)
            return np.empty((0, 3), dtype=np.float32)
    
    return np.empty((0, 3), dtype=np.float32)


def load_lidar_points(sequence_id: str, frame_idx: str, sensor: str = "os2-64", dataset_root: Optional[Path] = None) -> Optional[np.ndarray]:
    """Load LiDAR point cloud for a given frame.
    
    sensor: 'os2-64' or 'os1-128'
    """
    if dataset_root is None:
        dataset_root = Path("/home/adhish/Productivity/AMSCUP/repos/K-Radar")
    
    pcd_file = dataset_root / "data" / sequence_id / sensor / f"{sensor}_{frame_idx}.pcd"
    if not pcd_file.exists():
        return None
    
    return read_pcd_file(pcd_file)


def load_camera_image(sequence_id: str, frame_idx: str, camera: str, dataset_root: Optional[Path] = None) -> Optional[np.ndarray]:
    """Load camera image for a given frame.
    
    camera: 'cam-front', 'cam-left', 'cam-right', 'cam-rear'
    """
    if dataset_root is None:
        dataset_root = Path("/home/adhish/Productivity/AMSCUP/repos/K-Radar")
    
    img_file = dataset_root / "data" / sequence_id / camera / f"{camera}_{frame_idx}.png"
    if not img_file.exists():
        return None
    
    img = cv2.imread(str(img_file))
    if img is None:
        return None
    
    return img


def get_camera_image_path(sequence_id: str, frame_idx: str, camera: str, dataset_root: Optional[Path] = None) -> Optional[Path]:
    """Get path to camera image without loading it."""
    if dataset_root is None:
        dataset_root = Path("/home/adhish/Productivity/AMSCUP/repos/K-Radar")
    
    img_file = dataset_root / "data" / sequence_id / camera / f"{camera}_{frame_idx}.png"
    return img_file if img_file.exists() else None
