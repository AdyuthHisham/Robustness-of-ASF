#!/home/adhish/Productivity/AMSCUP/test-bed/.venv/bin python3
"""
A metadata compilation tool for NuScenes (Tool 1/2)
This tool gathers and saves:
1.  Scene token
2.  Sample token
3.  Instance token of annotation
4.  Visibility token
5.  No. of LiDAR points
6.  No. of Radar points
7.  Camera visibility (all cameras checked individually)
8.  Which LiDAR sensor
9.  Which camera(s)
10. Which radar sensor(s)
11. Annotation category name & category token
12. Location of Scene
"""
import argparse
import cProfile
import io
import os
import pstats
import sys
import numpy as np
import polars as pl
from pyquaternion import Quaternion
from nuscenes.utils.data_classes import LidarPointCloud, RadarPointCloud, PointCloud
from nuscenes.utils.geometry_utils import points_in_box, transform_matrix
from nuscenes.nuscenes import NuScenes


# ------------------- TRANSFORM FUNCTION -------------------
def transform_pointcloud_to_global(nusc, pointsensor: dict, pc: PointCloud):
    """
    Transform a PointCloud (LiDAR or Radar) from its sensor frame to the global frame.

    Parameters
    ----------
    nusc : NuScenes
        The NuScenes instance (replaces the erroneous 'self' parameter).
    pointsensor : dict
        The record from nusc.get('sample_data', token) for the point sensor
        (must contain 'calibrated_sensor_token' and 'ego_pose_token').
    pc : PointCloud
        The point cloud object (LidarPointCloud or RadarPointCloud).

    Returns
    -------
    pc : PointCloud
        The point cloud transformed **in-place** to global coordinates.
    sensor_to_global : np.ndarray (4x4)
        The final homogeneous transformation matrix (sensor → global).
    """
    # Step 1: Sensor frame → ego vehicle frame
    cs_record = nusc.get("calibrated_sensor", pointsensor["calibrated_sensor_token"])
    sensor_to_ego = transform_matrix(
        cs_record["translation"], Quaternion(cs_record["rotation"]), inverse=False
    )
    pc.rotate(Quaternion(cs_record["rotation"]).rotation_matrix)
    pc.translate(np.array(cs_record["translation"]))

    # Step 2: Ego vehicle frame → global frame
    pose_record = nusc.get("ego_pose", pointsensor["ego_pose_token"])
    ego_to_global = transform_matrix(
        pose_record["translation"], Quaternion(pose_record["rotation"]), inverse=False
    )
    pc.rotate(Quaternion(pose_record["rotation"]).rotation_matrix)
    pc.translate(np.array(pose_record["translation"]))

    sensor_to_global = ego_to_global @ sensor_to_ego
    return pc, sensor_to_global


# ------------------- CAMERA FUNCTION -------------------
def check_camera_visibility(nusc, sample: dict, ann_token: str) -> list[str]:
    """
    Returns which cameras see the annotation in this sample.

    Parameters
    ----------
    nusc       : NuScenes instance
    sample     : sample record dict
    ann_token  : annotation token to check

    Returns
    -------
    list of camera channel names that have the object in frame
    """
    visible_cameras = []
    cams = [
        "CAM_FRONT",
        "CAM_FRONT_LEFT",
        "CAM_FRONT_RIGHT",
        "CAM_BACK",
        "CAM_BACK_LEFT",
        "CAM_BACK_RIGHT",
    ]
    for cam_name in cams:
        cam_token = sample["data"][cam_name]
        _, boxes, _ = nusc.get_sample_data(cam_token, selected_anntokens=[ann_token])
        if len(boxes) > 0:
            visible_cameras.append(cam_name)
    return visible_cameras


# ------------------- RADAR FUNCTION -------------------
def count_radar_points(nusc, sample: dict, ann_token: str) -> dict[str, int]:
    """
    Returns a dict of {radar_sensor_name: point_count} for points inside the annotation box.

    Parameters
    ----------
    nusc      : NuScenes instance
    sample    : sample record dict
    ann_token : annotation token

    Returns
    -------
    dict mapping radar channel name → number of points inside the box (only non-zero entries)
    """
    radar_counts: dict[str, int] = {}
    ann_box = nusc.get_box(ann_token)

    radar_sensors = [
        "RADAR_FRONT",
        "RADAR_FRONT_LEFT",
        "RADAR_FRONT_RIGHT",
        "RADAR_BACK_LEFT",
        "RADAR_BACK_RIGHT",
    ]
    for radar_name in radar_sensors:
        radar_token = sample["data"][radar_name]
        sd_rec = nusc.get("sample_data", radar_token)
        pcl_path = os.path.join(nusc.dataroot, sd_rec["filename"])

        pc = RadarPointCloud.from_file(pcl_path)
        pc, _ = transform_pointcloud_to_global(nusc, sd_rec, pc)

        points = pc.points[:3, :].copy()
        inside = points_in_box(ann_box, points)
        count = int(np.sum(inside))
        if count > 0:
            radar_counts[radar_name] = count
    return radar_counts


# ------------------- LIDAR FUNCTION -------------------
def count_lidar_points(nusc, sample: dict, ann_token: str) -> tuple[int, str]:
    """
    Returns the number of LiDAR points inside the annotation box, and the sensor name.

    Parameters
    ----------
    nusc      : NuScenes instance
    sample    : sample record dict
    ann_token : annotation token

    Returns
    -------
    (point_count, lidar_sensor_name)
    """
    lidar_sensor_name = "LIDAR_TOP"
    ann_box = nusc.get_box(ann_token)

    lidar_token = sample["data"][lidar_sensor_name]
    lidar_sd = nusc.get("sample_data", lidar_token)
    pcl_path = os.path.join(nusc.dataroot, lidar_sd["filename"])

    pc = LidarPointCloud.from_file(pcl_path)
    pc, _ = transform_pointcloud_to_global(nusc, lidar_sd, pc)

    points = pc.points[:3, :].copy()
    inside = points_in_box(ann_box, points)
    return int(np.sum(inside)), lidar_sensor_name


# ------------------- MAIN PROCESSING LOOP -------------------
def process_dataset(nusc: NuScenes) -> list[dict]:
    """
    Iterate over all scenes → samples → annotations and collect metadata records.

    Returns
    -------
    list of dicts, one per annotation, containing all requested fields.
    """
    records: list[dict] = []

    for scene in nusc.scene:
        scene_token = scene["token"]
        scene_name = scene["name"]

        # Resolve location via the log record
        log_record = nusc.get("log", scene["log_token"])
        location = log_record["location"]

        print(
            f"\n================ SCENE: {scene_name}  [{scene_token}] ================"
        )
        print(f"  Location: {location}")

        sample_token = scene["first_sample_token"]

        while sample_token != "":
            sample = nusc.get("sample", sample_token)
            # print(f"\n  ----- SAMPLE: {sample_token} -----")

            for ann_token in sample["anns"]:
                ann = nusc.get("sample_annotation", ann_token)

                instance_token = ann["instance_token"]
                category_name = ann["category_name"]
                inst_rec = nusc.get("instance", ann["instance_token"])
                category_token = nusc.get("category", inst_rec["category_token"])
                visibility_token = ann.get("visibility_token", "")

                # print(f"\n    Annotation : {ann_token}")
                # print(f"    Instance   : {instance_token}")
                # print(f"    Category   : {category_name}  (token: {category_token})")
                # print(f"    Visibility : {visibility_token}")

                # ---- Camera ----
                visible_cams = check_camera_visibility(nusc, sample, ann_token)
                # print(f"    Cameras    : {visible_cams}")

                # ---- Radar ----
                radar_counts = count_radar_points(nusc, sample, ann_token)
                total_radar_pts = sum(radar_counts.values())
                active_radars = list(radar_counts.keys())
                # print(f"    Radar pts  : {radar_counts}")

                # ---- LiDAR ----
                lidar_count, lidar_sensor = count_lidar_points(nusc, sample, ann_token)
                # print(f"    LiDAR pts  : {lidar_count}  ({lidar_sensor})")

                # ---- Build record ----
                record = {
                    # Identifiers
                    "scene_token": scene_token,
                    "scene_name": scene_name,
                    "sample_token": sample_token,
                    "ann_token": ann_token,
                    "instance_token": instance_token,
                    # Annotation metadata
                    "category_name": category_name,
                    "category_token": category_token,
                    "visibility_token": visibility_token,
                    # Sensor data
                    "lidar_sensor": lidar_sensor,
                    "lidar_points": lidar_count,
                    "radar_points_total": total_radar_pts,
                    "radar_sensors": str(active_radars),  # stored as string for parquet
                    "radar_points_per_sensor": str(
                        radar_counts
                    ),  # stored as string for parquet
                    "visible_cameras": str(
                        visible_cams
                    ),  # stored as string for parquet
                    # Scene metadata
                    "location": location,
                }
                records.append(record)

            sample_token = sample["next"]

    return records


# ------------------- ENTRY POINT -------------------
if __name__ == "__main__":
    print("Python version:")
    print(sys.version)
    print(
        f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )

    # ---- Argument Parsing ----
    parser = argparse.ArgumentParser(description="Metadata Compilation (1/2)")

    parser.add_argument(
        "--version",
        type=str,
        default="v1.0-mini",
        help="nuScenes dataset version (default: v1.0-mini)",
    )
    parser.add_argument(
        "--dataroot",
        type=str,
        default="/home/adhish/Productivity/AMSCUP/test-bed/src/Datasets/nuscenes",
        help="Path to the root directory of the nuScenes dataset",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose output from NuScenes"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="nuscenes_metadata.parquet",
        help="Output path for the Parquet file (default: nuscenes_metadata.parquet)",
    )
    parser.add_argument(
        "--profile",
        action="store_true",
        help="Enable cProfile profiling of the main processing loop",
    )
    parser.add_argument(
        "--profile-lines",
        type=int,
        default=30,
        help="Number of top lines to show in profiling report (default: 30)",
    )

    args = parser.parse_args()

    # ---- NuScenes Init ----
    nusc = NuScenes(
        version=args.version,
        dataroot=args.dataroot,
        verbose=args.verbose,
    )
    print(f"\nLoaded nuScenes version : {args.version}")
    print(f"Data root               : {args.dataroot}")
    print(f"Verbose mode            : {args.verbose}")
    print(f"Output file             : {args.output}")
    print(f"Profiling enabled       : {args.profile}")

    # ---- Run (with optional cProfile) ----
    if args.profile:
        profiler = cProfile.Profile()
        profiler.enable()

    records = process_dataset(nusc)

    if args.profile:
        profiler.disable()

        # #Print profiling report to stdout
        stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stream)
        stats.strip_dirs()
        stats.sort_stats(pstats.SortKey.CUMULATIVE)
        stats.print_stats(args.profile_lines)

        print("\n\n========== cPROFILE REPORT ==========")
        print(stream.getvalue())

        # Also save the full profile to a .prof file alongside the parquet
        prof_path = os.path.splitext(args.output)[0] + ".prof"
        profiler.dump_stats(prof_path)
        print(f"Full profile saved to: {prof_path}")
        print("  (Tip: visualise with `snakeviz` or `tuna`)")

    # ---- Save to Parquet ----
    print(f"\nCollected {len(records)} annotation records.")

    df = pl.DataFrame(records).with_columns(
        [
            pl.col("lidar_points").cast(pl.Int32),
            pl.col("radar_points_total").cast(pl.Int32),
        ]
    )

    df.write_parquet(args.output, compression="snappy")
    print(f"Metadata saved to: {args.output}")
    print(df.schema)
    print(df.head())
