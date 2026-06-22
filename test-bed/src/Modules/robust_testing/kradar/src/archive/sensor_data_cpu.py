import marimo

__generated_with = "0.23.9"
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

    # Shared helpers: input-path resolution (file-or-directory), a
    # device-agnostic points-in-boxes implementation (CPU/NumPy here,
    # GPU/CUDA available via the same dispatcher in sensor_data_gpu.py),
    # and sensor-to-ego calibration offsets.
    from sensor_data_utils import (
        resolve_input_paths,
        points_in_boxes,
        counts_from_box_idxs,
        SensorCalibrationOffset,
        KRADAR_LIDAR_OFFSET,
        KRADAR_RADAR_OFFSET,
    )

    # This notebook is the CPU-only pipeline: force device="cpu" everywhere.
    # Changing this single constant is all that's needed to keep the
    # GPU notebook and this one in sync via sensor_data_utils.
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

    `GT_FOLDER`, `L1_FOLDER`, and `L2_FOLDER` may each point to either:

    * A **directory** containing many files (the original behaviour), or
    * A **single file** to process in isolation.

    Both forms are handled automatically by `resolve_input_paths` in the
    processing cells below -- no other configuration changes are required.

    Examples:

    ```python
    # Directory of ground-truth label files (original behaviour)
    GT_FOLDER = "/workspace/repos/K-Radar/data/1/info_label_rev2"

    # A single ground-truth label file
    GT_FOLDER = "/workspace/repos/K-Radar/data/1/info_label_rev2/00033.txt"

    # Directory of os1-128 LiDAR PCDs (original behaviour)
    L1_FOLDER = "/workspace/repos/K-Radar/data/1/os1-128"

    # A single os1-128 LiDAR PCD
    L1_FOLDER = "/workspace/repos/K-Radar/data/1/os1-128/os1-128_00033.pcd"

    # Directory of os2-64 LiDAR PCDs (original behaviour)
    L2_FOLDER = "/workspace/repos/K-Radar/data/1/os2-64"

    # A single os2-64 LiDAR PCD
    L2_FOLDER = "/workspace/repos/K-Radar/data/1/os2-64/os2-64_00033.pcd"

    # Directory of radar zyx cubes (used by the Radar section)
    RADAR_FOLDER = "/workspace/repos/K-Radar/data/1/radar_zyx_cube"

    # A single radar zyx cube (.mat)
    RADAR_FOLDER = "/workspace/repos/K-Radar/data/1/radar_zyx_cube/cube_00033.mat"

    # Camera image folders (used by the Camera section)
    CAM_FRONT_FOLDER  = "/workspace/repos/K-Radar/data/1/cam_front"
    CAM_LEFT_FOLDER   = "/workspace/repos/K-Radar/data/1/cam_left"
    CAM_RIGHT_FOLDER  = "/workspace/repos/K-Radar/data/1/cam_right"
    CAM_REAR_FOLDER   = "/workspace/repos/K-Radar/data/1/cam_rear"

    # Camera calibration
    CAM_CALIB_COMMON_DIR = "/workspace/repos/K-Radar/resources/cam_calib/common"
    CAM_CALIB_T_PARAMS   = "/workspace/repos/K-Radar/resources/cam_calib/T_params_seq/1.pkl"
    ```
    """)
    return


@app.cell
def _():
    GT_FOLDER     = "/workspace/repos/K-Radar/data/1/info_label_rev2"
    L1_FOLDER     = "/workspace/repos/K-Radar/data/1/os1-128"
    L2_FOLDER     = "/workspace/repos/K-Radar/data/1/os2-64"
    RADAR_FOLDER  = "/workspace/repos/K-Radar/data/1/radar_zyx_cube"

    # Camera image directories (one per camera)
    CAM_FRONT_FOLDER = "/workspace/repos/K-Radar/data/1/cam_front"
    CAM_LEFT_FOLDER  = "/workspace/repos/K-Radar/data/1/cam_left"
    CAM_RIGHT_FOLDER = "/workspace/repos/K-Radar/data/1/cam_right"
    CAM_REAR_FOLDER  = "/workspace/repos/K-Radar/data/1/cam_rear"

    # Camera calibration directories / files
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

    LiDAR and Radar point clouds are reported in their own sensor frames,
    each offset from the vehicle's ego frame (the frame used by the GT
    annotations) by a fixed mounting translation. `SensorCalibrationOffset`
    (in `sensor_data_utils.py`) applies that translation so points line up
    with the GT object boxes.

    `KRADAR_LIDAR_OFFSET` and `KRADAR_RADAR_OFFSET` hold the K-Radar
    mounting offsets `(x, y, z)` in meters. Both LiDAR sensors (os1-128 and
    os2-64) share the same offset in this dataset.
    """)
    return


@app.cell
def _(KRADAR_LIDAR_OFFSET, KRADAR_RADAR_OFFSET, SensorCalibrationOffset):
    # Calibrators that map points from each sensor's frame into the ego
    # (vehicle) frame used by the GT annotations.
    lidar_calibrator = SensorCalibrationOffset(*KRADAR_LIDAR_OFFSET)
    radar_calibrator = SensorCalibrationOffset(*KRADAR_RADAR_OFFSET)

    lidar_calibrator.visualize_offset()
    radar_calibrator.visualize_offset()
    return lidar_calibrator, radar_calibrator


@app.cell
def _(Path, pl, resolve_input_paths):
    def parse_gt_file(filepath: Path) -> tuple[dict, list[dict]]:
        """Parse a single GT annotation file.

        Args:
            filepath: Path to a `*.txt` ground-truth label file.

        Returns:
            A `(header, objects)` tuple where `header` is a dict describing
            the frame (sensor indices, timestamp, filename) and `objects`
            is a list of per-object annotation dicts.
        """
        header = {}
        objects = []

        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                if line.startswith("* idx("):
                    # Parse header line
                    parts = line.split("=", 1)[1].split(",")[0].split("_")
                    header = {
                        "file": filepath.name,
                        "radar_idx": parts[0],
                        "lidar64_idx": parts[1],
                        "cam_front_idx": parts[2],
                        "lidar128_idx": parts[3],
                        "cam_lrr_idx": parts[4],
                        "timestamp": float(line.split("timestamp=")[1]),
                    }

                elif line.startswith("*,"):
                    # Parse object annotation line
                    fields = [f.strip() for f in line.split(",")]
                    objects.append(
                        {
                            "file": filepath.name,
                            "sensor": fields[1],
                            "tracking_id": fields[2],
                            "class_name": fields[3],
                            "x_center": float(fields[4]),
                            "y_center": float(fields[5]),
                            "z_center": float(fields[6]),
                            "azimuth": float(fields[7]),
                            "half_length": float(fields[8]),
                            "half_width": float(fields[9]),
                            "half_height": float(fields[10]),
                        }
                    )

        return header, objects

    def load_gt_folder(
        path: str | Path, recursive: bool = False
    ) -> tuple[pl.DataFrame, pl.DataFrame]:
        """Load ground-truth annotations from a file or directory.

        Args:
            path: Either a single `*.txt` ground-truth file, or a directory
                containing one or more `*.txt` files. Directory contents are
                processed in sorted (deterministic) order.
            recursive: If `path` is a directory, search subdirectories too.

        Returns:
            `(headers_df, objects_df)` -- one row per frame and one row per
            annotated object, respectively, each with a leading numeric ID
            column (`frame_id` / `object_id`).

        Raises:
            FileNotFoundError: If `path` doesn't exist, or a directory
                contains no `*.txt` files.
            ValueError: If `path` is a single file that isn't `.txt`.
            NotADirectoryError: If `path` is neither a file nor a directory.
        """
        gt_files = resolve_input_paths(path, suffixes=[".txt"], recursive=recursive)

        all_headers = []
        all_objects = []
        for fp in gt_files:
            header, objects = parse_gt_file(fp)
            if header:
                all_headers.append(header)
            all_objects.extend(objects)

        headers_df = (
            pl.DataFrame(all_headers)
            .with_columns(pl.int_range(pl.len(), dtype=pl.Int32).alias("frame_id"))
            .select(["frame_id", pl.all().exclude("frame_id")])
        )

        objects_df = (
            pl.DataFrame(all_objects)
            .with_columns(pl.int_range(pl.len(), dtype=pl.Int32).alias("object_id"))
            .select(["object_id", pl.all().exclude("object_id")])
        )

        return headers_df, objects_df

    return (load_gt_folder,)


@app.cell
def _(GT_FOLDER, load_gt_folder, pl):
    pl.Config.set_tbl_width_chars(200)
    pl.Config.set_fmt_str_lengths(50)
    pl.Config.set_tbl_cols(-1)

    headers_df, objects_df = load_gt_folder(GT_FOLDER)

    print(f"Loaded {len(headers_df)} frames, {len(objects_df)} objects\n")
    print(headers_df.head())
    print(objects_df.head())
    return headers_df, objects_df


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # N# of points by sensor

    The cell below implements the CPU pipeline. It accepts either a
    directory of `.pcd` files or a single `.pcd` file via
    `resolve_input_paths`, and uses `points_in_boxes(..., device="cpu")`
    (a pure-NumPy implementation in `sensor_data_utils.py`) instead of the
    CUDA kernel `points_in_boxes_gpu`. No `.cuda()` / `.pin_memory()` calls
    are used anywhere in this pipeline.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Lidar
    """)
    return


@app.cell
def _():
    SENSOR_CONFIG = {
        "os1-128": {
            "idx_col": "lidar128_idx",
            "prefix": "os1-128",
            "out_col": "os1_point_count",
        },
        "os2-64": {
            "idx_col": "lidar64_idx",
            "prefix": "os2-64",
            "out_col": "os2_point_count",
        },
    }
    return (SENSOR_CONFIG,)


@app.cell
def _(
    DEVICE,
    Path,
    SENSOR_CONFIG,
    ThreadPoolExecutor,
    counts_from_box_idxs,
    lidar_calibrator,
    np,
    o3d,
    pl,
    points_in_boxes,
    resolve_input_paths,
):
    def _load_pcd_points(pcd_path: Path) -> np.ndarray | None:
        """Load a single PCD file's XYZ points, transformed into the ego frame.

        Points are read in the LiDAR sensor frame and then shifted into the
        ego (vehicle) frame via `lidar_calibrator`, so they align with the
        GT object boxes (which are defined in the ego frame).
        """
        if not pcd_path.exists():
            print(f"[WARN] PCD not found: {pcd_path}")
            return None
        pcd = o3d.io.read_point_cloud(str(pcd_path))
        points = np.asarray(pcd.points, dtype=np.float32)
        return lidar_calibrator.transform_point_cloud(points).astype(np.float32)


    def count_lidar_points_in_boxes(
        lidar_path: str | Path,
        headers_df: pl.DataFrame,
        objects_df: pl.DataFrame,
        sensor: str = "os1-128",  # "os1-128" or "os2-64"
        device: str = DEVICE,
        recursive: bool = False,
    ) -> pl.DataFrame:
        """Count, per annotated object, how many LiDAR points fall inside its box.

        Also computes `lidar_point_density` = point_count / box_volume, where
        box_volume = length * width * height. This quantifies how well the
        LiDAR sensor covers each object relative to its physical size.

        Args:
            lidar_path: Either a directory containing the sensor's `.pcd`
                files (original behaviour), or a path to a single `.pcd`
                file. When a single file is given, only frames whose
                `{idx_col}` matches that file's index are updated; all other
                frames retain their previous (or default 0) count.
            headers_df: Per-frame metadata, including the LiDAR index column
                named in `SENSOR_CONFIG[sensor]["idx_col"]`.
            objects_df: Per-object annotations to be augmented with point
                count and density columns.
            sensor: Which LiDAR sensor config to use ("os1-128" or "os2-64").
            device: "cpu" (default for this notebook) or "cuda". Controls
                which `points_in_boxes` implementation is used.
            recursive: If `lidar_path` is a directory, search subdirectories
                for `.pcd` files as well.

        Returns:
            `objects_df` with added/updated columns:
              - `{out_col}` (Int32): LiDAR point count per object box.
              - `{out_col}_density` (Float32): points per cubic meter.

        Raises:
            FileNotFoundError: If `lidar_path` doesn't exist, or a directory
                contains no `.pcd` files.
            ValueError: If `lidar_path` is a single file that isn't `.pcd`.
        """
        cfg = SENSOR_CONFIG[sensor]
        idx_col = cfg["idx_col"]
        prefix = cfg["prefix"]
        out_col = cfg["out_col"]
        density_col = f"{out_col}_density"

        pcd_files = resolve_input_paths(
            lidar_path, suffixes=[".pcd"], recursive=recursive
        )
        # Map each discovered PCD file back to its frame index (the part of
        # the filename after the sensor prefix, e.g. "os1-128_00033.pcd" ->
        # "00033"), so a single-file input only updates the matching frame.
        available_idxs = {
            fp.stem[len(prefix) + 1 :]: fp
            for fp in pcd_files
            if fp.stem.startswith(f"{prefix}_")
        }

        all_counts: dict[tuple[str, str], int] = {}
        rows = list(headers_df.iter_rows(named=True))

        def load_frame(header):
            idx = header[idx_col]
            pcd_path = available_idxs.get(idx)
            if pcd_path is None:
                return header, None
            pts = _load_pcd_points(pcd_path)
            return header, pts

        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = [pool.submit(load_frame, row) for row in rows]

            for future in futures:
                header, points = future.result()
                if points is None:
                    continue

                file_name = header["file"]
                frame_objs = objects_df.filter(pl.col("file") == file_name)
                if frame_objs.is_empty():
                    continue

                boxes_np = (
                    frame_objs.select(
                        [
                            "x_center",
                            "y_center",
                            "z_center",
                            pl.col("half_length") * 2,
                            pl.col("half_width") * 2,
                            pl.col("half_height") * 2,
                            "azimuth",
                        ]
                    )
                    .to_numpy()
                    .astype(np.float32)
                )

                box_idxs = points_in_boxes(points, boxes_np, device=device)
                if device != "cpu":
                    box_idxs = box_idxs.cpu().numpy()

                M = boxes_np.shape[0]
                counts = counts_from_box_idxs(box_idxs, M)

                for i, tid in enumerate(frame_objs["tracking_id"].to_list()):
                    all_counts[(file_name, tid)] = int(counts[i])

        counts_col = [
            all_counts.get((row["file"], row["tracking_id"]), 0)
            for row in objects_df.iter_rows(named=True)
        ]

        # Compute per-object box volume = length * width * height.
        # The GT stores half-extents, so full dimensions are 2 * half_*.
        # Density = point_count / volume  (points per cubic meter).
        result = objects_df.with_columns(
            pl.Series(out_col, counts_col, dtype=pl.Int32)
        )

        volumes = (
            result["half_length"] * 2 * result["half_width"] * 2 * result["half_height"] * 2
        )
        densities = [
            float(c) / float(v) if float(v) > 0.0 else 0.0
            for c, v in zip(result[out_col].to_list(), volumes.to_list())
        ]
        result = result.with_columns(
            pl.Series(density_col, densities, dtype=pl.Float32)
        )

        return result

    return (count_lidar_points_in_boxes,)


@app.cell
def _(L1_FOLDER, count_lidar_points_in_boxes, headers_df, objects_df):
    # Example: directories of PCDs (original behaviour, now CPU-only).
    # objects_with_counts = count_lidar_points_in_boxes(
    #     L1_FOLDER, headers_df, objects_df, sensor="os1-128"
    # )
    # print(objects_with_counts.head())

    # objects_with_counts = count_lidar_points_in_boxes(
    #     L2_FOLDER, headers_df, objects_df, sensor="os2-64"
    # )
    # print(objects_with_counts.head())

    # Example: a single PCD file instead of a directory.
    single_pcd = f"{L1_FOLDER}/os1-128_00033.pcd"
    objects_with_counts = count_lidar_points_in_boxes(
        single_pcd, headers_df, objects_df, sensor="os1-128"
    )

    print(objects_with_counts.head())
    return (objects_with_counts,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Radar
    """)
    return


@app.cell
def _(RADAR_FOLDER, np, resolve_input_paths):
    import scipy.io as sio

    # Resolve either a directory of radar cubes or a single .mat file; pick
    # the first cube for the inline shape/stats preview below.
    radar_files = resolve_input_paths(RADAR_FOLDER, suffixes=[".mat"])
    first_radar_file = radar_files[0]

    mat = sio.loadmat(str(first_radar_file))
    arr = mat["arr_zyx"]

    print(f"Preview file: {first_radar_file.name}")
    print("Shape:", arr.shape)  # expect (Z, Y, X)
    print("Dtype:", arr.dtype)
    print("Min/Max:", arr.min(), arr.max())
    print("Non-zero cells:", np.count_nonzero(arr))
    return (sio,)


@app.cell
def _(Path, np, radar_calibrator, resolve_input_paths, sio):
    def radar_zyx_to_pcd(mat_path: Path, power_threshold: float = 0.0):
        """Convert a single radar zyx power cube into XYZ points + dB intensity.

        Points are computed in the radar sensor frame and then transformed
        into the ego (vehicle) frame via `radar_calibrator`, so they align
        with the GT object boxes (which are defined in the ego frame).

        Args:
            mat_path: Path to a `.mat` file containing an `arr_zyx` array.
            power_threshold: Cells with power <= this value are dropped.

        Returns:
            `(points, power_db)`: an `(N, 3)` float32 array of (x, y, z)
            coordinates in the ego frame, and an `(N,)` float32 array of
            the corresponding power in dB.
        """
        mat = sio.loadmat(str(mat_path))
        arr = mat["arr_zyx"]

        Z, Y, X = arr.shape
        x_coords_axis = np.linspace(0, 100, X)
        y_coords_axis = np.linspace(-80, 80, Y)
        z_coords_axis = np.linspace(-30, 30, Z)

        mask = arr > power_threshold
        z_idx, y_idx, x_idx = np.where(mask)

        x = x_coords_axis[x_idx].astype(np.float32)
        y = y_coords_axis[y_idx].astype(np.float32)
        z = z_coords_axis[z_idx].astype(np.float32)
        power = arr[z_idx, y_idx, x_idx].astype(np.float32)

        # Convert to dB for a usable scalar range
        power_db = 10 * np.log10(power + 1e-10).astype(np.float32)

        points_sensor = np.stack([x, y, z], axis=1)
        points = radar_calibrator.transform_point_cloud(points_sensor).astype(
            np.float32
        )
        print(
            f"  {mat_path.name}: {len(points)} points above threshold {power_threshold}"
        )
        return points, power_db

    def save_pcd_with_intensity(
        out_path: Path, points: np.ndarray, intensity: np.ndarray
    ):
        """Write a PCD file with XYZI fields.

        Args:
            out_path: Destination `.pcd` path. Parent directories are
                created if they don't exist.
            points: `(N, 3)` float32 array of (x, y, z) coordinates.
            intensity: `(N,)` float32 array stored as the 'intensity' field.
        """
        N = len(points)
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        with open(out_path, "w") as f:
            f.write("# .PCD v0.7 - Point Cloud Data\n")
            f.write("VERSION 0.7\n")
            f.write("FIELDS x y z intensity\n")
            f.write("SIZE 4 4 4 4\n")
            f.write("TYPE F F F F\n")
            f.write("COUNT 1 1 1 1\n")
            f.write(f"WIDTH {N}\n")
            f.write("HEIGHT 1\n")
            f.write("VIEWPOINT 0 0 0 1 0 0 0\n")
            f.write(f"POINTS {N}\n")
            f.write("DATA ascii\n")
            for i in range(N):
                f.write(
                    f"{points[i,0]:.4f} {points[i,1]:.4f} {points[i,2]:.4f} {intensity[i]:.4f}\n"
                )

    def process_radar_cubes(
        radar_path: str | Path,
        out_dir: str | Path,
        power_threshold: float = 0.0,
        recursive: bool = False,
    ) -> list[Path]:
        """Convert one or more radar zyx cubes to PCD files.

        Args:
            radar_path: Either a directory of `.mat` radar cubes, or a path
                to a single `.mat` file.
            out_dir: Directory to write the resulting `.pcd` files into. One
                output file is produced per input cube, named after the
                input file's stem (e.g. `cube_00033.mat` -> `cube_00033.pcd`).
            power_threshold: Forwarded to `radar_zyx_to_pcd`.
            recursive: If `radar_path` is a directory, search subdirectories
                for `.mat` files as well.

        Returns:
            A sorted list of the output `.pcd` file paths that were written.

        Raises:
            FileNotFoundError: If `radar_path` doesn't exist, or a directory
                contains no `.mat` files.
            ValueError: If `radar_path` is a single file that isn't `.mat`.
        """
        mat_files = resolve_input_paths(
            radar_path, suffixes=[".mat"], recursive=recursive
        )
        out_dir = Path(out_dir)

        written: list[Path] = []
        for mat_path in mat_files:
            points, power_db = radar_zyx_to_pcd(mat_path, power_threshold=power_threshold)
            out_path = out_dir / f"{mat_path.stem}.pcd"
            save_pcd_with_intensity(out_path, points, power_db)
            written.append(out_path)

        return written

    return (process_radar_cubes,)


@app.cell
def _(RADAR_FOLDER, process_radar_cubes):
    # Example: a directory of radar cubes -> a directory of PCDs.
    out_dir = "test-bed/src/Modules/robust_testing/outputs"
    # written_files = process_radar_cubes(RADAR_FOLDER, out_dir, power_threshold=0.0)
    # print(f"Wrote {len(written_files)} PCD file(s) to {out_dir}")

    # Example: a single radar cube file instead of a directory.
    single_cube = f"{RADAR_FOLDER}/cube_00033.mat"
    written_files = process_radar_cubes(single_cube, out_dir, power_threshold=0.0)
    return


# ---------------------------------------------------------------------------
# Part 2: Radar Voxel Occupancy Analysis
# ---------------------------------------------------------------------------

@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Radar Voxel Occupancy Analysis

    Instead of projecting the radar cube into a sparse point cloud and then
    testing points-in-boxes, we operate directly on the dense `arr_zyx`
    tensor. This preserves zero-power voxels and enables aggregation of
    raw power statistics per object.

    For every annotated object the following are computed:
    - `radar_voxel_count` – number of voxel centres inside the 3-D box.
    - `radar_mean_power` – mean power value (linear) of those voxels.
    - `radar_max_power` – peak power of those voxels.
    - `radar_high_power_voxel_count` – voxels whose power exceeds the
      95th-percentile of the whole frame.
    - `radar_occupancy_score` – fraction of in-box voxels that are
      "high power" (`high_power_voxel_count / max(voxel_count, 1)`).
    """)
    return


@app.cell
def _(np, pl, points_in_boxes, radar_calibrator, resolve_input_paths, sio):
    def _build_radar_voxel_ego_coords(arr_zyx: np.ndarray) -> np.ndarray:
        """Build an (N_voxels, 3) array of voxel-centre coordinates in the ego frame.

        The radar cube axes map to spatial dimensions as follows
        (matching `radar_zyx_to_pcd`):

            X: linspace(0,   100, X)  – range, pointing forward
            Y: linspace(-80,  80, Y)  – lateral / azimuth
            Z: linspace(-30,  30, Z)  – elevation

        All voxel centres are first expressed in the radar sensor frame and
        then translated to the ego frame via `radar_calibrator.transform_point_cloud`.

        Args:
            arr_zyx: (Z, Y, X) radar power cube.

        Returns:
            (Z*Y*X, 3) float64 array of (x, y, z) coordinates in the ego
            frame, in row-major (z, y, x) order matching `arr_zyx.ravel()`.
        """
        Z, Y, X = arr_zyx.shape

        # Build 1-D coordinate axes in the sensor frame (same as radar_zyx_to_pcd)
        x_axis = np.linspace(0,   100, X, dtype=np.float64)
        y_axis = np.linspace(-80,  80, Y, dtype=np.float64)
        z_axis = np.linspace(-30,  30, Z, dtype=np.float64)

        # Meshgrid in (z, y, x) order so flattening matches arr_zyx.ravel()
        zz, yy, xx = np.meshgrid(z_axis, y_axis, x_axis, indexing="ij")  # each (Z,Y,X)
        points_sensor = np.stack(
            [xx.ravel(), yy.ravel(), zz.ravel()], axis=1
        )  # (Z*Y*X, 3) in sensor frame

        # Apply the radar mounting offset: sensor frame -> ego frame
        return radar_calibrator.transform_point_cloud(points_sensor)  # (Z*Y*X, 3)


    def count_radar_voxels_in_boxes(
        radar_path: str,
        headers_df: pl.DataFrame,
        objects_df: pl.DataFrame,
        high_power_percentile: float = 95.0,
        recursive: bool = False,
    ) -> pl.DataFrame:
        """Compute per-object radar voxel occupancy metrics from raw zyx cubes.

        For each frame the full `arr_zyx` tensor is loaded.  All voxel centres
        are transformed to the ego frame and then tested against every GT
        bounding box using the same `points_in_boxes` dispatcher used for LiDAR.
        This gives us both geometric occupancy (how many voxels are inside the
        box) and power statistics (mean/max/high-power) without any information
        loss from sparse-cloud thresholding.

        The `radar_occupancy_score` is:
            high_power_voxel_count / max(voxel_count, 1)
        It equals 0 when no voxels are inside the box, and approaches 1 when
        most in-box voxels are high-power detections.

        Args:
            radar_path: Directory of `.mat` radar cubes, or path to a single
                `.mat` file. The stem must follow the `cube_XXXXX` convention
                so the frame index can be extracted (e.g. "cube_00033" -> "00033").
            headers_df: Per-frame metadata including the "radar_idx" column.
            objects_df: Per-object annotation DataFrame to be augmented.
            high_power_percentile: Percentile threshold (0-100) used to
                classify voxels as "high power" within each frame.  Default
                is the 95th percentile of all non-zero voxel values in the frame.
            recursive: Whether to search `radar_path` subdirectories.

        Returns:
            `objects_df` extended with:
              - radar_voxel_count          (Int32)
              - radar_mean_power           (Float32)
              - radar_max_power            (Float32)
              - radar_high_power_voxel_count (Int32)
              - radar_occupancy_score      (Float32)
        """
        mat_files = resolve_input_paths(radar_path, suffixes=[".mat"], recursive=recursive)

        # Map "00033" -> Path("cube_00033.mat") for O(1) per-frame lookup.
        # The stem convention is "cube_XXXXX"; we strip the leading "cube_" prefix.
        available_cubes: dict[str, object] = {}
        for fp in mat_files:
            stem = fp.stem  # e.g. "cube_00033"
            if stem.startswith("cube_"):
                available_cubes[stem[len("cube_"):]] = fp

        # Per-object result dicts keyed by (file, tracking_id)
        voxel_results: dict[tuple[str, str], dict] = {}

        for header in headers_df.iter_rows(named=True):
            radar_idx = header["radar_idx"]
            mat_path = available_cubes.get(radar_idx)
            if mat_path is None:
                continue

            file_name = header["file"]
            frame_objs = objects_df.filter(pl.col("file") == file_name)
            if frame_objs.is_empty():
                continue

            # ----------------------------------------------------------------
            # Load the raw power cube and build voxel-centre coordinates
            # in the ego frame.
            # arr_zyx shape: (Z, Y, X); powers are linear (not dB here).
            # ----------------------------------------------------------------
            mat_data = sio.loadmat(str(mat_path))
            arr_zyx = mat_data["arr_zyx"].astype(np.float64)  # (Z, Y, X)

            # Flat power values (Z*Y*X,) matching the row order of voxel_coords
            power_flat = arr_zyx.ravel()

            # Ego-frame coordinates for every voxel centre: (Z*Y*X, 3)
            voxel_coords_ego = _build_radar_voxel_ego_coords(arr_zyx)

            # 95th-percentile power threshold for the whole frame.
            # Computed over ALL voxels (including zeros) so it is a stable,
            # per-frame reference that does not shift with sparse detections.
            frame_power_threshold = float(
                np.percentile(power_flat, high_power_percentile)
            )

            # ----------------------------------------------------------------
            # Build boxes array (M, 7) in the standard points_in_boxes format:
            # [cx, cy, cz, length, width, height, yaw]
            # ----------------------------------------------------------------
            boxes_np = (
                frame_objs.select(
                    [
                        "x_center",
                        "y_center",
                        "z_center",
                        pl.col("half_length") * 2,
                        pl.col("half_width") * 2,
                        pl.col("half_height") * 2,
                        "azimuth",
                    ]
                )
                .to_numpy()
                .astype(np.float64)
            )

            # Assign each voxel centre to a box (CPU implementation).
            # voxel_box_idxs: (N_voxels,) int64, -1 = no box.
            voxel_box_idxs = points_in_boxes(
                voxel_coords_ego.astype(np.float32),
                boxes_np.astype(np.float32),
                device="cpu",
            )

            M = boxes_np.shape[0]
            tracking_ids = frame_objs["tracking_id"].to_list()

            for box_i, tid in enumerate(tracking_ids):
                # Boolean mask selecting voxels inside this specific box
                in_box_mask = voxel_box_idxs == box_i

                voxel_count = int(in_box_mask.sum())
                in_box_powers = power_flat[in_box_mask]

                if voxel_count == 0:
                    voxel_results[(file_name, tid)] = {
                        "radar_voxel_count": 0,
                        "radar_mean_power": 0.0,
                        "radar_max_power": 0.0,
                        "radar_high_power_voxel_count": 0,
                        "radar_occupancy_score": 0.0,
                    }
                else:
                    mean_power = float(in_box_powers.mean())
                    max_power  = float(in_box_powers.max())
                    # "High power" = power strictly above the frame's
                    # high_power_percentile value.
                    high_power_count = int((in_box_powers > frame_power_threshold).sum())
                    occupancy_score  = high_power_count / max(voxel_count, 1)

                    voxel_results[(file_name, tid)] = {
                        "radar_voxel_count": voxel_count,
                        "radar_mean_power": mean_power,
                        "radar_max_power": max_power,
                        "radar_high_power_voxel_count": high_power_count,
                        "radar_occupancy_score": occupancy_score,
                    }

        # Materialise per-object columns (default = zeros for unmatched objects)
        _defaults = {
            "radar_voxel_count": 0,
            "radar_mean_power": 0.0,
            "radar_max_power": 0.0,
            "radar_high_power_voxel_count": 0,
            "radar_occupancy_score": 0.0,
        }

        col_data: dict[str, list] = {k: [] for k in _defaults}
        for row in objects_df.iter_rows(named=True):
            r = voxel_results.get((row["file"], row["tracking_id"]), _defaults)
            for k in _defaults:
                col_data[k].append(r[k])

        return objects_df.with_columns([
            pl.Series("radar_voxel_count",           col_data["radar_voxel_count"],           dtype=pl.Int32),
            pl.Series("radar_mean_power",             col_data["radar_mean_power"],             dtype=pl.Float32),
            pl.Series("radar_max_power",              col_data["radar_max_power"],              dtype=pl.Float32),
            pl.Series("radar_high_power_voxel_count", col_data["radar_high_power_voxel_count"], dtype=pl.Int32),
            pl.Series("radar_occupancy_score",        col_data["radar_occupancy_score"],        dtype=pl.Float32),
        ])

    return (count_radar_voxels_in_boxes,)


@app.cell
def _(RADAR_FOLDER, count_radar_voxels_in_boxes, headers_df, objects_df):
    objects_with_radar = count_radar_voxels_in_boxes(
        RADAR_FOLDER, headers_df, objects_df
    )
    print(objects_with_radar.select([
        "object_id", "tracking_id",
        "radar_voxel_count", "radar_mean_power", "radar_max_power",
        "radar_high_power_voxel_count", "radar_occupancy_score",
    ]).head())
    return (objects_with_radar,)


# ---------------------------------------------------------------------------
# Part 3: Camera Visibility Analysis
# ---------------------------------------------------------------------------

@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Camera Visibility Analysis

    For each annotated object we determine whether (and how much of) it is
    visible in each of the four K-Radar cameras:
    `cam_front`, `cam_left`, `cam_right`, `cam_rear`.

    ### Projection chain

    GT boxes are in the ego frame.  For each camera we have:
    - **Extrinsics** `R` (3×3 rotation) and `t` (3,) translation that
      transform a point from the ego frame to the camera frame:
          `P_cam = R @ P_ego + t`
    - **Intrinsics** `fx, fy, px, py` (focal lengths and principal point):
          `u = fx * P_cam[0]/P_cam[2] + px`
          `v = fy * P_cam[1]/P_cam[2] + py`

    A point is visible if `depth = P_cam[2] > 0` and
    `0 <= u < W, 0 <= v < H`.

    ### Visibility percentage

    We sample ≥500 uniformly distributed points inside each 3-D box, project
    them into the camera, and report the fraction that satisfy the visibility
    conditions.  This is a Monte-Carlo approximation of the fraction of the
    object volume that the camera can observe.
    """)
    return


@app.cell
def _(np, Path):
    import yaml
    import pickle

    def load_camera_calibration(
        calib_common_dir: str,
        t_params_pkl: str,
    ) -> dict:
        """Load K-Radar camera calibration for all four cameras.

        K-Radar stores calibration data in two places:
          1. `resources/cam_calib/common/*.yaml` – one YAML per camera,
             containing intrinsics (fx, fy, px, py, distortion) and the
             rotation matrix R.
          2. `resources/cam_calib/T_params_seq/*.pkl` – per-sequence pickle
             containing the translation vectors `t` for each camera.

        This function merges both sources into a single dict keyed by camera
        name ("cam_front", "cam_left", "cam_right", "cam_rear").

        Args:
            calib_common_dir: Path to the directory containing the per-camera
                YAML files (e.g. "cam_front.yaml", etc.).
            t_params_pkl: Path to the sequence-specific T_params pickle file.

        Returns:
            Dict mapping camera name -> calibration sub-dict with keys:
              - "fx", "fy", "px", "py"      – intrinsic scalars
              - "k1".."k5"                  – distortion coefficients (may be 0)
              - "R"  (3×3 ndarray)          – rotation ego->camera
              - "t"  (3,  ndarray)          – translation ego->camera
              - "width", "height"           – image dimensions (int)
        """
        cam_names = ["cam_front", "cam_left", "cam_right", "cam_rear"]
        calib_dir = Path(calib_common_dir)

        # ----------------------------------------------------------------
        # 1. Load per-sequence translation vectors from the pickle file.
        #    The pickle is expected to be a dict of the form:
        #      { "cam_front": {"t": [tx, ty, tz]}, ... }
        #    (Actual key structure may vary; we handle both flat and nested.)
        # ----------------------------------------------------------------
        with open(t_params_pkl, "rb") as f:
            t_params = pickle.load(f)

        # ----------------------------------------------------------------
        # 2. Load intrinsics + rotation from per-camera YAML files.
        # ----------------------------------------------------------------
        calib = {}
        for cam in cam_names:
            yaml_path = calib_dir / f"{cam}.yaml"
            if not yaml_path.exists():
                print(f"[WARN] Calibration YAML not found: {yaml_path}")
                continue

            with open(yaml_path, "r") as f:
                y = yaml.safe_load(f)

            # --- Intrinsics ---
            # Typical K-Radar YAML layout (adapt key names if needed):
            #   camera_matrix:
            #     data: [fx, 0, px, 0, fy, py, 0, 0, 1]
            #   distortion_coefficients:
            #     data: [k1, k2, p1, p2, k3]
            #   image_width: 1280
            #   image_height: 720
            #   rectification_matrix / rotation_matrix:
            #     data: [r11, r12, ..., r33]   (row-major 3×3)
            cam_mat_data = y.get("camera_matrix", {}).get("data", [1, 0, 0, 0, 1, 0, 0, 0, 1])
            dist_data    = y.get("distortion_coefficients", {}).get("data", [0, 0, 0, 0, 0])
            rot_data     = y.get("rotation_matrix", y.get("rectification_matrix", {})).get(
                "data", [1, 0, 0, 0, 1, 0, 0, 0, 1]
            )
            width  = int(y.get("image_width",  1280))
            height = int(y.get("image_height", 720))

            fx = float(cam_mat_data[0])
            fy = float(cam_mat_data[4])
            px = float(cam_mat_data[2])
            py = float(cam_mat_data[5])

            k1 = float(dist_data[0]) if len(dist_data) > 0 else 0.0
            k2 = float(dist_data[1]) if len(dist_data) > 1 else 0.0
            k3 = float(dist_data[4]) if len(dist_data) > 4 else 0.0
            k4 = float(dist_data[5]) if len(dist_data) > 5 else 0.0
            k5 = float(dist_data[6]) if len(dist_data) > 6 else 0.0

            R = np.array(rot_data, dtype=np.float64).reshape(3, 3)

            # ----------------------------------------------------------------
            # 3. Merge the translation from the T_params pickle.
            #    Accept both dict-of-dict and direct array layouts.
            # ----------------------------------------------------------------
            if cam in t_params:
                t_entry = t_params[cam]
                if isinstance(t_entry, dict):
                    t_vec = np.array(t_entry.get("t", [0, 0, 0]), dtype=np.float64).ravel()
                else:
                    t_vec = np.array(t_entry, dtype=np.float64).ravel()
            else:
                print(f"[WARN] No translation found for {cam} in {t_params_pkl}")
                t_vec = np.zeros(3, dtype=np.float64)

            calib[cam] = {
                "fx": fx, "fy": fy, "px": px, "py": py,
                "k1": k1, "k2": k2, "k3": k3, "k4": k4, "k5": k5,
                "R": R,
                "t": t_vec,
                "width":  width,
                "height": height,
            }

        return calib

    return (load_camera_calibration, yaml, pickle)


@app.cell
def _(CAM_CALIB_COMMON_DIR, CAM_CALIB_T_PARAMS, load_camera_calibration):
    cam_calib = load_camera_calibration(CAM_CALIB_COMMON_DIR, CAM_CALIB_T_PARAMS)
    for _cam_name, _cam_data in cam_calib.items():
        print(f"{_cam_name}: {_cam_data['width']}x{_cam_data['height']}, "
              f"fx={_cam_data['fx']:.1f}, fy={_cam_data['fy']:.1f}")
    return (cam_calib,)


@app.cell
def _(np):
    def _build_box_corners(box: np.ndarray) -> np.ndarray:
        """Return the 8 corners of a 3-D bounding box in the ego frame.

        The box is parameterised as [cx, cy, cz, length, width, height, yaw]
        (the same 7-element format used by `points_in_boxes`).

        The 8 corners are the ±half-extent vertices of the axis-aligned box
        rotated by `yaw` around the z-axis and translated to the box centre.

        Args:
            box: (7,) array [cx, cy, cz, length, width, height, yaw].

        Returns:
            (8, 3) float64 array of corner coordinates in the ego frame.
        """
        cx, cy, cz, dx, dy, dz, yaw = box.astype(np.float64)
        hl, hw, hh = dx / 2, dy / 2, dz / 2

        # 8 corners in the box's local (axis-aligned) frame
        local_corners = np.array([
            [ hl,  hw,  hh],
            [ hl,  hw, -hh],
            [ hl, -hw,  hh],
            [ hl, -hw, -hh],
            [-hl,  hw,  hh],
            [-hl,  hw, -hh],
            [-hl, -hw,  hh],
            [-hl, -hw, -hh],
        ], dtype=np.float64)  # (8, 3)

        # Rotation matrix around z-axis by `yaw`
        cos_y, sin_y = np.cos(yaw), np.sin(yaw)
        R_yaw = np.array([
            [cos_y, -sin_y, 0],
            [sin_y,  cos_y, 0],
            [0,      0,     1],
        ], dtype=np.float64)

        # Rotate and translate to ego frame
        return (R_yaw @ local_corners.T).T + np.array([cx, cy, cz])


    def _project_ego_points_to_camera(
        points_ego: np.ndarray,
        cam_calib_entry: dict,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Project ego-frame 3-D points into a single camera image plane.

        Transformation chain:
            P_cam = R @ P_ego + t          (rigid body: ego -> camera frame)
            u = fx * (P_cam_x / P_cam_z) + px
            v = fy * (P_cam_y / P_cam_z) + py

        Distortion is intentionally omitted for this visibility check: the
        goal is a fast geometric in/out-of-frustum test, not sub-pixel accuracy.
        For corner-case objects near the image boundary, the small distortion
        error is tolerable.

        Args:
            points_ego: (N, 3) array of 3-D points in the ego frame.
            cam_calib_entry: Calibration dict for one camera (from
                `load_camera_calibration`).

        Returns:
            Tuple `(u, v, depth)` each of shape (N,):
              - u, v: pixel coordinates (may be outside [0,W) × [0,H)).
              - depth: z-coordinate in the camera frame (positive = in front).
        """
        R   = cam_calib_entry["R"]    # (3, 3)
        t   = cam_calib_entry["t"]    # (3,)
        fx  = cam_calib_entry["fx"]
        fy  = cam_calib_entry["fy"]
        px  = cam_calib_entry["px"]
        py  = cam_calib_entry["py"]

        # Transform to camera frame: P_cam = R @ P_ego^T + t  (broadcast t)
        P_cam = (R @ points_ego.T).T + t   # (N, 3)

        depth = P_cam[:, 2]                # z in camera frame; >0 = visible

        # Avoid division by zero; masked out when depth<=0 anyway
        safe_depth = np.where(depth > 0, depth, 1e-9)

        u = fx * (P_cam[:, 0] / safe_depth) + px
        v = fy * (P_cam[:, 1] / safe_depth) + py

        return u, v, depth


    def project_box_to_camera(
        box: np.ndarray,
        cam_calib_entry: dict,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Project the 8 corners of a 3-D GT box into a camera image.

        Args:
            box: (7,) array [cx, cy, cz, length, width, height, yaw] in ego frame.
            cam_calib_entry: Calibration dict for one camera.

        Returns:
            Tuple `(u, v, depth)` each of shape (8,), one entry per corner.
        """
        corners_ego = _build_box_corners(box)         # (8, 3)
        return _project_ego_points_to_camera(corners_ego, cam_calib_entry)


    def compute_camera_visibility(
        box: np.ndarray,
        cam_calib_entry: dict,
        n_samples: int = 500,
    ) -> dict:
        """Estimate what fraction of a 3-D box is visible in a single camera.

        ### Algorithm

        1. Project all 8 box corners to determine a coarse visibility flag
           (Condition 1: at least one corner with depth>0 inside the image, or
           Condition 2: the 2-D bounding rectangle of all corners intersects the
           image rectangle).
        2. If the coarse check passes, sample `n_samples` points uniformly at
           random inside the 3-D box (in its local frame, then rotated to ego),
           project them into the camera, and compute the fraction with
           depth>0 and pixel coords inside the image.

        Args:
            box: (7,) array [cx, cy, cz, length, width, height, yaw].
            cam_calib_entry: Calibration dict for the target camera.
            n_samples: Number of random interior points for the Monte-Carlo
                fraction estimate.  Must be >= 1; 500 is the default.

        Returns:
            Dict with keys:
              - "is_visible"           (bool): coarse visibility flag.
              - "visibility_percentage" (float): fraction in [0, 1].
        """
        W = cam_calib_entry["width"]
        H = cam_calib_entry["height"]

        # ------------------------------------------------------------------
        # Step 1: Coarse check via 8 box corners
        # ------------------------------------------------------------------
        u_corners, v_corners, depth_corners = project_box_to_camera(box, cam_calib_entry)

        # Condition 1: at least one corner is fully inside the image with depth>0
        in_image = (
            (depth_corners > 0)
            & (u_corners >= 0) & (u_corners < W)
            & (v_corners >= 0) & (v_corners < H)
        )

        # Condition 2: the 2-D axis-aligned bounding rectangle of all corners
        # (regardless of depth) overlaps the image rectangle.
        # This catches large objects whose corners may project outside the frame
        # but whose interior still fills part of the image.
        valid_depth = depth_corners > 0
        if valid_depth.any():
            u_min = float(u_corners[valid_depth].min())
            u_max = float(u_corners[valid_depth].max())
            v_min = float(v_corners[valid_depth].min())
            v_max = float(v_corners[valid_depth].max())
            # AABB overlap: two rectangles overlap iff neither is fully outside
            overlap = (u_max >= 0) and (u_min < W) and (v_max >= 0) and (v_min < H)
        else:
            overlap = False

        is_visible_coarse = bool(in_image.any()) or overlap

        if not is_visible_coarse:
            return {"is_visible": False, "visibility_percentage": 0.0}

        # ------------------------------------------------------------------
        # Step 2: Monte-Carlo interior sampling for the fine visibility fraction
        # ------------------------------------------------------------------
        cx, cy, cz, dx, dy, dz, yaw = box.astype(np.float64)

        # Sample uniformly in the box's local (axis-aligned) coordinate frame
        rng = np.random.default_rng(seed=42)  # deterministic for reproducibility
        local_samples = rng.uniform(
            low  =[-dx / 2, -dy / 2, -dz / 2],
            high =[ dx / 2,  dy / 2,  dz / 2],
            size =(n_samples, 3),
        )  # (n_samples, 3)

        # Rotate samples by the box yaw angle to align with the ego frame
        cos_y, sin_y = np.cos(yaw), np.sin(yaw)
        R_yaw = np.array([
            [cos_y, -sin_y, 0.0],
            [sin_y,  cos_y, 0.0],
            [0.0,    0.0,   1.0],
        ])
        samples_ego = (R_yaw @ local_samples.T).T + np.array([cx, cy, cz])

        # Project samples into the camera
        u_s, v_s, d_s = _project_ego_points_to_camera(samples_ego, cam_calib_entry)

        visible_mask = (
            (d_s > 0)
            & (u_s >= 0) & (u_s < W)
            & (v_s >= 0) & (v_s < H)
        )
        visibility_pct = float(visible_mask.sum()) / n_samples

        return {
            "is_visible":            bool(visible_mask.any()),
            "visibility_percentage": visibility_pct,
        }

    return (
        _build_box_corners,
        _project_ego_points_to_camera,
        compute_camera_visibility,
        project_box_to_camera,
    )


# ---------------------------------------------------------------------------
# Part 4: Unified Multi-Modal Observability
# ---------------------------------------------------------------------------

@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Unified Multi-Modal Observability

    `compute_multimodal_observability` iterates over every annotated object
    and merges LiDAR, Radar, and Camera metrics into a single row per object.

    The output Polars DataFrame is exported as both `.parquet` and `.csv`.
    """)
    return


@app.cell
def _(
    Path,
    cam_calib,
    compute_camera_visibility,
    count_lidar_points_in_boxes,
    count_radar_voxels_in_boxes,
    np,
    pl,
    points_in_boxes,
    counts_from_box_idxs,
    lidar_calibrator,
    o3d,
    resolve_input_paths,
    sio,
    DEVICE,
    SENSOR_CONFIG,
    ThreadPoolExecutor,
):
    def compute_multimodal_observability(
        gt_path: str | Path,
        lidar_path: str | Path,
        radar_path: str | Path,
        camera_folders: dict[str, str | Path],
        cam_calib: dict,
        headers_df: pl.DataFrame,
        objects_df: pl.DataFrame,
        lidar_sensor: str = "os1-128",
        radar_high_power_percentile: float = 95.0,
        camera_n_samples: int = 500,
        output_dir: str | Path = ".",
        recursive: bool = False,
    ) -> pl.DataFrame:
        """Produce a unified multi-modal observability DataFrame for all GT objects.

        This is the top-level orchestrator.  It:
        1. Runs LiDAR point counting + density (Part 1).
        2. Runs Radar voxel occupancy analysis (Part 2).
        3. Runs per-camera visibility analysis (Part 3) for all four cameras.
        4. Joins everything on (file, tracking_id) into a single wide DataFrame.
        5. Exports to `{output_dir}/multi_modal_visibility.parquet` and `.csv`.

        Args:
            gt_path: Ground-truth label file or directory.
            lidar_path: LiDAR PCD file or directory for the chosen sensor.
            radar_path: Radar `.mat` cube file or directory.
            camera_folders: Dict mapping camera name to image folder path,
                e.g. {"cam_front": "/data/cam_front", ...}.  Image paths are
                not directly used here; the dict is present for future
                per-image loading extensions.
            cam_calib: Calibration dict as returned by `load_camera_calibration`.
            headers_df: Per-frame metadata DataFrame.
            objects_df: Per-object annotation DataFrame.
            lidar_sensor: "os1-128" or "os2-64".
            radar_high_power_percentile: Percentile threshold for high-power
                radar voxel classification.
            camera_n_samples: Number of Monte-Carlo samples per object per camera
                for visibility percentage estimation.
            output_dir: Directory where output files are written.
            recursive: Passed to path-resolution helpers.

        Returns:
            Wide Polars DataFrame with one row per annotated object and
            columns as specified in Part 4 of the task specification.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # ------------------------------------------------------------------
        # Part 1: LiDAR
        # ------------------------------------------------------------------
        print("[1/3] Computing LiDAR point counts and densities ...")
        cfg = SENSOR_CONFIG[lidar_sensor]
        out_col     = cfg["out_col"]
        density_col = f"{out_col}_density"

        df = count_lidar_points_in_boxes(
            lidar_path, headers_df, objects_df,
            sensor=lidar_sensor, device=DEVICE, recursive=recursive,
        )

        # Rename to canonical names expected by the output schema
        df = df.rename({out_col: "lidar_point_count", density_col: "lidar_point_density"})

        # ------------------------------------------------------------------
        # Part 2: Radar voxel occupancy
        # ------------------------------------------------------------------
        print("[2/3] Computing Radar voxel occupancy ...")
        df = count_radar_voxels_in_boxes(
            radar_path, headers_df, df,
            high_power_percentile=radar_high_power_percentile,
            recursive=recursive,
        )

        # ------------------------------------------------------------------
        # Part 3: Camera visibility (all four cameras)
        # ------------------------------------------------------------------
        print("[3/3] Computing Camera visibility ...")

        cam_order = ["cam_front", "cam_left", "cam_right", "cam_rear"]

        # Build per-object camera results.
        # We iterate over objects grouped by frame to avoid re-building the
        # boxes array for every single object.
        cam_cols: dict[str, list] = {
            "visible_front":  [],
            "visible_left":   [],
            "visible_right":  [],
            "visible_rear":   [],
            "best_camera":    [],
            "max_visibility_percentage": [],
        }

        for row in df.iter_rows(named=True):
            # Build the (7,) box array for this object
            box = np.array([
                row["x_center"],
                row["y_center"],
                row["z_center"],
                row["half_length"] * 2,
                row["half_width"]  * 2,
                row["half_height"] * 2,
                row["azimuth"],
            ], dtype=np.float64)

            vis_results: dict[str, dict] = {}
            for cam_name in cam_order:
                if cam_name not in cam_calib:
                    # Calibration not available – treat as not visible
                    vis_results[cam_name] = {
                        "is_visible": False,
                        "visibility_percentage": 0.0,
                    }
                else:
                    vis_results[cam_name] = compute_camera_visibility(
                        box, cam_calib[cam_name], n_samples=camera_n_samples
                    )

            cam_cols["visible_front"].append(vis_results["cam_front"]["is_visible"])
            cam_cols["visible_left"].append(vis_results["cam_left"]["is_visible"])
            cam_cols["visible_right"].append(vis_results["cam_right"]["is_visible"])
            cam_cols["visible_rear"].append(vis_results["cam_rear"]["is_visible"])

            # Determine best camera (highest visibility percentage)
            best_cam  = max(cam_order, key=lambda c: vis_results[c]["visibility_percentage"])
            max_vis   = vis_results[best_cam]["visibility_percentage"]
            best_name = best_cam if max_vis > 0.0 else "none"

            cam_cols["best_camera"].append(best_name)
            cam_cols["max_visibility_percentage"].append(float(max_vis))

        df = df.with_columns([
            pl.Series("visible_front",              cam_cols["visible_front"],              dtype=pl.Boolean),
            pl.Series("visible_left",               cam_cols["visible_left"],               dtype=pl.Boolean),
            pl.Series("visible_right",              cam_cols["visible_right"],              dtype=pl.Boolean),
            pl.Series("visible_rear",               cam_cols["visible_rear"],               dtype=pl.Boolean),
            pl.Series("best_camera",                cam_cols["best_camera"],                dtype=pl.Utf8),
            pl.Series("max_visibility_percentage",  cam_cols["max_visibility_percentage"],  dtype=pl.Float32),
        ])

        # ------------------------------------------------------------------
        # Select and order the final output columns
        # ------------------------------------------------------------------
        output_cols = [
            "object_id",
            "tracking_id",
            "lidar_point_count",
            "lidar_point_density",
            "radar_voxel_count",
            "radar_mean_power",
            "radar_max_power",
            "radar_high_power_voxel_count",
            "radar_occupancy_score",
            "visible_front",
            "visible_left",
            "visible_right",
            "visible_rear",
            "best_camera",
            "max_visibility_percentage",
        ]
        result = df.select(output_cols)

        # ------------------------------------------------------------------
        # Export
        # ------------------------------------------------------------------
        parquet_path = output_dir / "multi_modal_visibility.parquet"
        csv_path     = output_dir / "multi_modal_visibility.csv"

        result.write_parquet(str(parquet_path))
        result.write_csv(str(csv_path))

        print(f"Saved {len(result)} rows -> {parquet_path}")
        print(f"Saved {len(result)} rows -> {csv_path}")

        return result

    return (compute_multimodal_observability,)


@app.cell
def _(
    GT_FOLDER,
    L1_FOLDER,
    RADAR_FOLDER,
    CAM_FRONT_FOLDER,
    CAM_LEFT_FOLDER,
    CAM_RIGHT_FOLDER,
    CAM_REAR_FOLDER,
    cam_calib,
    compute_multimodal_observability,
    headers_df,
    objects_df,
    pl,
):
    camera_folders = {
        "cam_front": CAM_FRONT_FOLDER,
        "cam_left":  CAM_LEFT_FOLDER,
        "cam_right": CAM_RIGHT_FOLDER,
        "cam_rear":  CAM_REAR_FOLDER,
    }

    multimodal_df = compute_multimodal_observability(
        gt_path        = GT_FOLDER,
        lidar_path     = L1_FOLDER,
        radar_path     = RADAR_FOLDER,
        camera_folders = camera_folders,
        cam_calib      = cam_calib,
        headers_df     = headers_df,
        objects_df     = objects_df,
        lidar_sensor               = "os1-128",
        radar_high_power_percentile= 95.0,
        camera_n_samples           = 500,
        output_dir     = "outputs",
    )

    pl.Config.set_tbl_width_chars(300)
    pl.Config.set_tbl_cols(-1)
    print(multimodal_df.head(10))
    return (multimodal_df,)


if __name__ == "__main__":
    app.run()
