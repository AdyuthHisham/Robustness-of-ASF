import marimo

__generated_with__ = "0.23.9"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    import polars as pl
    from pathlib import Path
    return Path, pl


@app.cell
def _():
    import numpy as np
    import torch
    import open3d as o3d
    from concurrent.futures import ThreadPoolExecutor

    from sensor_data_utils import (
        resolve_input_paths,
        points_in_boxes,
        counts_from_box_idxs,
        SensorCalibrationOffset,
        KRADAR_LIDAR_OFFSET,
        KRADAR_RADAR_OFFSET,
    )

    DEVICE = "cpu"
    return (
        DEVICE,
        KRADAR_LIDAR_OFFSET,
        KRADAR_RADAR_OFFSET,
        SensorCalibrationOffset,
        ThreadPoolExecutor,
        counts_from_box_idxs,
        np,
        o3d,
        points_in_boxes,
        resolve_input_paths,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Paths
    ...
    # Camera image folders (used by the Camera section)
    # Folder mode: discovers all PNG files automatically
    CAM_FRONT_FOLDER  = "/workspace/repos/K-Radar/data/1/cam-front"
    CAM_LEFT_FOLDER   = "/workspace/repos/K-Radar/data/1/cam-left"
    CAM_RIGHT_FOLDER  = "/workspace/repos/K-Radar/data/1/cam-right"
    CAM_REAR_FOLDER   = "/workspace/repos/K-Radar/data/1/cam-rear"

    # Single-image mode: processes only the matching frame
    CAM_FRONT_FOLDER = "/workspace/repos/K-Radar/data/1/cam-front/cam-front_00446.png"
    ...
    """)
    return


@app.cell
def _():
    GT_FOLDER     = "/workspace/repos/K-Radar/data/1/info_label_rev2"
    L1_FOLDER     = "/workspace/repos/K-Radar/data/1/os1-128"
    L2_FOLDER     = "/workspace/repos/K-Radar/data/1/os2-64"
    RADAR_FOLDER  = "/workspace/repos/K-Radar/data/1/radar_zyx_cube"

    CAM_FRONT_FOLDER = "/workspace/repos/K-Radar/data/1/cam-front"
    CAM_LEFT_FOLDER  = "/workspace/repos/K-Radar/data/1/cam-left"
    CAM_RIGHT_FOLDER = "/workspace/repos/K-Radar/data/1/cam-right"
    CAM_REAR_FOLDER  = "/workspace/repos/K-Radar/data/1/cam-rear"

    CAM_CALIB_COMMON_DIR = "/workspace/repos/K-Radar/resources/cam_calib/common"
    CAM_CALIB_T_PARAMS   = "/workspace/repos/K-Radar/resources/cam_calib/T_params_seq/1.pkl"

    return (
        GT_FOLDER, L1_FOLDER, L2_FOLDER, RADAR_FOLDER,
        CAM_FRONT_FOLDER, CAM_LEFT_FOLDER, CAM_RIGHT_FOLDER, CAM_REAR_FOLDER,
        CAM_CALIB_COMMON_DIR, CAM_CALIB_T_PARAMS,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Calibration
    LiDAR and Radar point clouds are already pre-calibrated in the dataset
    pipeline and are reported in the ego (vehicle) frame. **No additional
    calibration transformations are applied** to LiDAR or Radar data.
    """)
    return


@app.cell
def _(KRADAR_LIDAR_OFFSET, KRADAR_RADAR_OFFSET, SensorCalibrationOffset):
    lidar_calibrator = SensorCalibrationOffset(*KRADAR_LIDAR_OFFSET)
    radar_calibrator = SensorCalibrationOffset(*KRADAR_RADAR_OFFSET)
    lidar_calibrator.visualize_offset()
    radar_calibrator.visualize_offset()
    return lidar_calibrator, radar_calibrator


# ... [GT parsing cells unchanged] ...


@app.cell
def _(
    DEVICE, Path, SENSOR_CONFIG, ThreadPoolExecutor,
    counts_from_box_idxs, np, o3d, pl, points_in_boxes, resolve_input_paths,
):
    def _load_pcd_points(pcd_path: Path) -> np.ndarray | None:
        """Load a single PCD file's XYZ points.
        K-Radar LiDAR point clouds are already in the ego frame.
        No additional calibration / frame transformation is applied.
        """
        if not pcd_path.exists():
            print(f"[WARN] PCD not found: {pcd_path}")
            return None
        pcd = o3d.io.read_point_cloud(str(pcd_path))
        points = np.asarray(pcd.points, dtype=np.float32)
        return points  # No transform applied — dataset is pre-calibrated

    def count_lidar_points_in_boxes(...):
        # ... [same structure, uses _load_pcd_points without calibration] ...
        return result

    return (count_lidar_points_in_boxes,)


# ... [Radar cells: radar_zyx_to_pcd and _build_radar_voxel_ego_coords 
#      now build coordinates directly in ego frame without calibration] ...


@app.cell
def _():
    """Camera configuration matching K-Radar PNG file naming convention."""
    CAMERA_CONFIG = {
        "front": {
            "idx_col": "cam_front_idx",
            "prefix": "cam-front",
            "folder": CAM_FRONT_FOLDER,
        },
        "left": {
            "idx_col": "cam_left_idx",
            "prefix": "cam-left",
            "folder": CAM_LEFT_FOLDER,
        },
        "right": {
            "idx_col": "cam_right_idx",
            "prefix": "cam-right",
            "folder": CAM_RIGHT_FOLDER,
        },
        "rear": {
            "idx_col": "cam_rear_idx",
            "prefix": "cam-rear",
            "folder": CAM_REAR_FOLDER,
        },
    }
    return (CAMERA_CONFIG,)


@app.cell
def _(np, Path):
    import yaml
    import pickle
    from PIL import Image as PILImage

    def load_image(path: str | Path) -> np.ndarray:
        """Load a PNG image and return it as a NumPy array."""
        with PILImage.open(path) as img:
            return np.array(img)

    def load_camera_calibration(
        calib_common_dir: str,
        t_params_pkl: str,
        camera_folders: dict[str, str | Path] | None = None,
    ) -> dict:
        """Load K-Radar camera calibration.
        
        Image width and height are inferred at runtime from actual PNG files
        when camera_folders is provided. No hard-coded dimensions.
        """
        cam_names = ["cam_front", "cam_left", "cam_right", "cam_rear"]
        calib_dir = Path(calib_common_dir)
        
        with open(t_params_pkl, "rb") as f:
            t_params = pickle.load(f)

        calib = {}
        for cam in cam_names:
            yaml_path = calib_dir / f"{cam}.yaml"
            if not yaml_path.exists():
                continue
            with open(yaml_path, "r") as f:
                y = yaml.safe_load(f)

            # ... [parse intrinsics, distortion, rotation, translation] ...
            
            # Infer dimensions from first available PNG at runtime
            width, height = 0, 0
            if camera_folders is not None and cam in camera_folders:
                cam_folder = Path(camera_folders[cam])
                png_candidates = resolve_input_paths(
                    cam_folder, suffixes=[".png"], recursive=False
                )
                if png_candidates:
                    with PILImage.open(png_candidates[0]) as img:
                        width, height = img.size  # Runtime inference!

            calib[cam] = {
                "fx": fx, "fy": fy, "px": px, "py": py,
                "k1": k1, "k2": k2, "k3": k3, "k4": k4, "k5": k5,
                "R": R, "t": t_vec,
                "width": width, "height": height,
            }
        return calib

    return (load_camera_calibration, load_image, yaml, pickle, PILImage)


@app.cell
def _(CAM_CALIB_COMMON_DIR, CAM_CALIB_T_PARAMS, CAMERA_CONFIG, load_camera_calibration):
    camera_folders_for_calib = {
        f"cam_{name}": cfg["folder"] for name, cfg in CAMERA_CONFIG.items()
    }
    cam_calib = load_camera_calibration(
        CAM_CALIB_COMMON_DIR, CAM_CALIB_T_PARAMS,
        camera_folders=camera_folders_for_calib,
    )
    # ... [print dimensions — now dynamically inferred] ...
    return (cam_calib,)


@app.cell
def _(np):
    def compute_camera_visibility(
        box: np.ndarray,
        cam_calib_entry: dict,
        n_samples: int = 500,
    ) -> dict:
        W = cam_calib_entry["width"]
        H = cam_calib_entry["height"]
        
        if W <= 0 or H <= 0:
            return {"is_visible": False, "visibility_percentage": 0.0}
        
        # ... [rest of projection logic uses W, H from calib_entry] ...


@app.cell
def _(
    Path, CAMERA_CONFIG, cam_calib, compute_camera_visibility,
    count_lidar_points_in_boxes, count_radar_voxels_in_boxes,
    np, pl, points_in_boxes, counts_from_box_idxs, o3d,
    resolve_input_paths, sio, DEVICE, SENSOR_CONFIG, ThreadPoolExecutor,
):
    def compute_multimodal_observability(
        gt_path, lidar_path, radar_path, camera_folders,
        cam_calib, headers_df, objects_df,
        lidar_sensor="os1-128",
        radar_high_power_percentile=95.0,
        camera_n_samples=500,
        output_dir=".",
        recursive=False,
    ):
        # ... [LiDAR and Radar parts unchanged] ...
        
        # Camera visibility with PNG discovery via CAMERA_CONFIG
        cam_available = {}
        for cam_name, cam_cfg in CAMERA_CONFIG.items():
            cam_path = camera_folders.get(cam_name, "")
            if not cam_path:
                cam_available[cam_name] = {}
                continue
            
            png_files = resolve_input_paths(
                cam_path, suffixes=[".png"], recursive=recursive
            )
            prefix = cam_cfg["prefix"]
            cam_available[cam_name] = {
                fp.stem[len(prefix) + 1:]: fp
                for fp in png_files
                if fp.stem.startswith(f"{prefix}_")
            }
        
        # ... [visibility computation per object, using cam_calib W/H] ...
        
        return result

    return (compute_multimodal_observability,)


@app.cell
def _(
    GT_FOLDER, L1_FOLDER, RADAR_FOLDER,
    CAM_FRONT_FOLDER, CAM_LEFT_FOLDER, CAM_RIGHT_FOLDER, CAM_REAR_FOLDER,
    cam_calib, compute_multimodal_observability, headers_df, objects_df, pl,
):
    camera_folders = {
        "front": CAM_FRONT_FOLDER,
        "left":  CAM_LEFT_FOLDER,
        "right": CAM_RIGHT_FOLDER,
        "rear":  CAM_REAR_FOLDER,
    }
    multimodal_df = compute_multimodal_observability(
        gt_path=GT_FOLDER,
        lidar_path=L1_FOLDER,
        radar_path=RADAR_FOLDER,
        camera_folders=camera_folders,
        cam_calib=cam_calib,
        headers_df=headers_df,
        objects_df=objects_df,
        lidar_sensor="os1-128",
        radar_high_power_percentile=95.0,
        camera_n_samples=500,
        output_dir="outputs",
    )
    print(multimodal_df.head(10))
    return (multimodal_df,)


if __name__ == "__main__":
    app.run()