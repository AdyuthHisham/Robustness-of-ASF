import pickle

# Camera mapping: direction -> (cam_number, cam_key)
# front: 1,2 | right: 3,4 | rear: 5,6 | left: 7,8
CAMERA_MAP = {
    'front': [(1, 'front0'), (2, 'front1')],
    'right': [(3, 'right0'), (4, 'right1')],
    'rear': [(5, 'rear0'), (6, 'rear1')],
    'left': [(7, 'left0'), (8, 'left1')],
}

def load_camera_calibration(seq=1):
    """Load T_params_seq pickle for a given sequence. Returns dict of cam_key -> params."""
    filepath = f'/home/adhish/Productivity/AMSCUP/repos/K-Radar/resources/cam_calib/T_params_seq/{seq}'
    with open(filepath, 'rb') as f:
        data = pickle.load(f)
    return data

def get_camera_params(direction, seq=1):
    """Get camera params for a direction (front/right/rear/left). Returns list of (cam_number, params)."""
    calib_data = load_camera_calibration(seq)
    result = []
    for cam_number, cam_key in CAMERA_MAP[direction]:
        params = calib_data[cam_key]
        result.append({
            'cam_number': cam_number,
            'cam_key': cam_key,
            'camera_intrinsics': params['camera_intrinsics'],  # 4x4
            'radar2camera': params['radar2camera'],            # 4x4
            'camera2radar': params['camera2radar'],            # 4x4
        })
    return result

def get_T_radar2cam(cam_number, seq=1):
    """Get the 4x4 T_radar2camera matrix for a specific camera number."""
    calib_data = load_camera_calibration(seq)
    for direction, cams in CAMERA_MAP.items():
        for cn, ck in cams:
            if cn == cam_number:
                return calib_data[ck]['radar2camera']
    raise ValueError(f"Camera number {cam_number} not found")

def get_camera_intrinsics(cam_number, seq=1):
    """Get the 4x4 camera intrinsics matrix for a specific camera number."""
    calib_data = load_camera_calibration(seq)
    for direction, cams in CAMERA_MAP.items():
        for cn, ck in cams:
            if cn == cam_number:
                return calib_data[ck]['camera_intrinsics']
    raise ValueError(f"Camera number {cam_number} not found")

def load_calibration(data_path):
    """
    Load calibration data for the K-Radar dataset.
    This is a placeholder function for the web visualization tool.
    In a real implementation, this would load the calibration data from the given path.
    For now, we return an empty dictionary.
    """
    return {}