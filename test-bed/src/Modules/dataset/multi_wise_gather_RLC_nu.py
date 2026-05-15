#!/home/adhish/Productivity/AMSCUP/test-bed/.venv/bin python3
"""
A metadata compilation tool for NuScenes (Tool 1/2)  —  MULTITHREADED VERSION
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

Parallelism strategy
--------------------
  Outer pool  (--workers N) : one task per annotation — N annotations processed in parallel.
  Inner pool  (3 threads)   : camera / radar / lidar checks run concurrently per annotation.

NuScenes look-ups are read-only dict accesses and file reads, so sharing the single
nusc object across threads is safe.
"""
import argparse
import cProfile
import io
import os
import pstats
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import polars as pl
from pyquaternion import Quaternion

from nuscenes.utils.data_classes import LidarPointCloud, RadarPointCloud, PointCloud
from nuscenes.utils.geometry_utils import points_in_box, transform_matrix
from nuscenes.nuscenes import NuScenes

try:
    from tqdm import tqdm

    _TQDM = True
except ImportError:
    _TQDM = False


# ------------------- PROGRESS HELPER -------------------
class _Progress:
    """Minimal thread-safe progress counter used when tqdm is unavailable."""

    def __init__(self, total: int):
        self._total = total
        self._done = 0
        self._lock = threading.Lock()

    def update(self):
        with self._lock:
            self._done += 1
            if self._done % max(1, self._total // 20) == 0 or self._done == self._total:
                pct = 100 * self._done / self._total
                print(
                    f"  Progress: {self._done}/{self._total}  ({pct:.0f}%)", flush=True
                )


# ------------------- TRANSFORM FUNCTION -------------------
def transform_pointcloud_to_global(nusc, pointsensor: dict, pc: PointCloud):
    """
    Transform a PointCloud (LiDAR or Radar) from its sensor frame to the global frame.

    Parameters
    ----------
    nusc : NuScenes
        The NuScenes instance.
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
    Returns {radar_sensor_name: point_count} for points inside the annotation box.
    Only non-zero entries are included.
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
    Returns (lidar_point_count, lidar_sensor_name) for points inside the annotation box.
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


# ------------------- PER-ANNOTATION WORKER -------------------
def process_annotation(
    nusc,
    scene_token: str,
    scene_name: str,
    location: str,
    sample_token: str,
    ann_token: str,
) -> dict:
    """
    Process a single annotation and return its metadata record.

    The three sensor checks (camera / radar / lidar) are run concurrently
    using a small inner thread pool (3 threads).
    """
    sample = nusc.get("sample", sample_token)
    ann = nusc.get("sample_annotation", ann_token)

    instance_token = ann["instance_token"]
    category_name = ann["category_name"]
    inst_rec = nusc.get("instance", ann["instance_token"])
    category_token = nusc.get("category", inst_rec["category_token"])
    visibility_token = ann.get("visibility_token", "")

    # ---- Run the three sensor checks concurrently (inner pool) ----
    with ThreadPoolExecutor(max_workers=3) as inner_pool:
        cam_fut = inner_pool.submit(check_camera_visibility, nusc, sample, ann_token)
        radar_fut = inner_pool.submit(count_radar_points, nusc, sample, ann_token)
        lidar_fut = inner_pool.submit(count_lidar_points, nusc, sample, ann_token)

        visible_cams = cam_fut.result()
        radar_counts = radar_fut.result()
        lidar_count, lidar_sensor = lidar_fut.result()

    total_radar_pts = sum(radar_counts.values())
    active_radars = list(radar_counts.keys())

    return {
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
        "radar_points_per_sensor": str(radar_counts),  # stored as string for parquet
        "visible_cameras": str(visible_cams),  # stored as string for parquet
        # Scene metadata
        "location": location,
    }


# ------------------- MAIN PROCESSING LOOP -------------------
def process_dataset(nusc: NuScenes, max_workers: int = 8) -> list[dict]:
    """
    Collect all work items (one per annotation) then process them in parallel.

    Parameters
    ----------
    nusc        : NuScenes instance (shared read-only across threads)
    max_workers : size of the outer thread pool

    Returns
    -------
    list of record dicts (order not guaranteed)
    """

    # ---- Pass 1: enumerate all work items (fast, no I/O) ----
    work_items: list[tuple] = []

    for scene in nusc.scene:
        scene_token = scene["token"]
        scene_name = scene["name"]
        log_record = nusc.get("log", scene["log_token"])
        location = log_record["location"]

        sample_token = scene["first_sample_token"]
        while sample_token != "":
            sample = nusc.get("sample", sample_token)
            for ann_token in sample["anns"]:
                work_items.append(
                    (scene_token, scene_name, location, sample_token, ann_token)
                )
            sample_token = sample["next"]

    total = len(work_items)
    print(
        f"\nDispatching {total} annotation tasks across {max_workers} outer threads "
        f"(+3 inner threads each for sensor checks)…"
    )

    # ---- Pass 2: process in parallel ----
    records: list[dict] = []
    errors: int = 0

    if _TQDM:
        progress = tqdm(total=total, unit="ann", dynamic_ncols=True)
    else:
        progress = _Progress(total)

    with ThreadPoolExecutor(max_workers=max_workers) as outer_pool:
        futures = {
            outer_pool.submit(process_annotation, nusc, *item): item
            for item in work_items
        }

        for future in as_completed(futures):
            try:
                records.append(future.result())
            except Exception as exc:
                errors += 1
                item = futures[future]
                print(
                    f"\n  [ERROR] ann_token={item[4]}  scene={item[1]}  — {exc}",
                    file=sys.stderr,
                )

            if _TQDM:
                progress.update(1)
            else:
                progress.update()

    if _TQDM:
        progress.close()

    if errors:
        print(
            f"\n  ⚠  {errors} annotation(s) failed and were skipped.", file=sys.stderr
        )

    return records


# ------------------- ENTRY POINT -------------------
if __name__ == "__main__":
    print("Python version:")
    print(sys.version)
    print(
        f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )

    # ---- Argument Parsing ----
    parser = argparse.ArgumentParser(
        description="Metadata Compilation (1/2) — multithreaded"
    )

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
        default="multi_nuscenes_metadata.parquet",
        help="Output path for the Parquet file (default: nuscenes_metadata.parquet)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=8,
        help="Number of outer worker threads (one per annotation). Default: 8. "
        "Rule of thumb: set to the number of logical CPU cores.",
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
    print(f"Outer worker threads    : {args.workers}")
    print(f"Profiling enabled       : {args.profile}")

    # ---- Run (with optional cProfile) ----
    if args.profile:
        profiler = cProfile.Profile()
        profiler.enable()

    records = process_dataset(nusc, max_workers=args.workers)

    if args.profile:
        profiler.disable()

        stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stream)
        stats.strip_dirs()
        stats.sort_stats(pstats.SortKey.CUMULATIVE)
        stats.print_stats(args.profile_lines)

        print("\n\n========== cPROFILE REPORT ==========")
        print(stream.getvalue())

        prof_path = os.path.splitext(args.output)[0] + ".prof"
        profiler.dump_stats(prof_path)
        print(f"Full profile saved to : {prof_path}")
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
    print(f"Metadata saved to : {args.output}")
    print(df.schema)
    print(df.head())
