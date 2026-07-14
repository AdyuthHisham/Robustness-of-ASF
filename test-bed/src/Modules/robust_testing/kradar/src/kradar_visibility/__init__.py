from .radar_visibility import radar_visibility, compute_radar_sparsity_score
from .lidar_visibility import calculate_lidar_visibility
from .calibration import (
    load_camera_calibration, get_camera_params, get_T_radar2cam,
    get_camera_intrinsics, CAMERA_MAP
)
from .camera_visibility import (
    calculate_visibility_score, calculate_camera_visibility,
    project_point_to_image
)
from .config import *
from .parser import (
    parse_header, parse_object_line, parse_label_file,
    get_sequence_label_files, parse_description_txt,
    HeaderInfo, ObjectAnnotation
)
from .data_loader import (
    load_radar_cube, load_lidar_points, load_camera_image,
    get_camera_image_path, read_pcd_file
)
from .pipeline import run, compute_visibility_for_frame

def main() -> None:
    print("Hello from kradar-visibility!")
