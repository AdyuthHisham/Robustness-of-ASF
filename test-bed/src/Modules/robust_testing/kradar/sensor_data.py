import marimo  # noqa

__generated_with = "0.23.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo  # noqa

    return (mo,)


@app.cell
def _():
    import polars as pl
    from pathlib import Path

    return Path, pl


@app.cell
def _():
    KRADAR_REPO = "/home/adhish/Productivity/AMSCUP/repos/K-Radar"
    return (KRADAR_REPO,)


@app.cell
def _():
    import numpy as np
    import torch
    import open3d as o3d
    from pcdet.ops.roiaware_pool3d.roiaware_pool3d_utils import points_in_boxes_gpu
    from concurrent.futures import ThreadPoolExecutor

    return ThreadPoolExecutor, np, o3d, points_in_boxes_gpu, torch


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Paths
    """
    )
    return


@app.cell
def _():
    GT_FOLDER = "/workspace/repos/K-Radar/data/1/info_label_rev2"
    L1_FOLDER = "/workspace/repos/K-Radar/data/1/os1-128"
    L2_FOLDER = "/workspace/repos/K-Radar/data/1/os2-64"
    # R_FOLDER = "/workspace/repos/K-Radar/data/1/os2-64"
    ## Cameras can be recursive based on folder name
    # CF_FOLDER = "/workspace/repos/K-Radar/data/1/os2-64"
    # L2_FOLDER = "/workspace/repos/K-Radar/data/1/os2-64"
    return GT_FOLDER, L1_FOLDER, L2_FOLDER


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # Parse info files
    """
    )
    return


@app.cell
def _(Path, pl):
    def parse_gt_file(filepath: Path) -> tuple[dict, list[dict]]:
        """Parse a single GT annotation file."""
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

    def load_gt_folder(folder: str | Path) -> tuple[pl.DataFrame, pl.DataFrame]:
        folder = Path(folder)
        if not folder.exists():
            raise FileNotFoundError(f"Folder not found: {folder}")
        if not folder.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {folder}")
        gt_files = sorted(folder.glob("*.txt"))
        if not gt_files:
            raise FileNotFoundError(f"No .txt files found in: {folder}")

        all_headers = []
        all_objects = []
        for fp in gt_files:
            if not fp.is_file():
                continue
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
    mo.md(
        r"""
    # N# of points by sensor
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Lidar
    """
    )
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
    Path,
    SENSOR_CONFIG,
    ThreadPoolExecutor,
    np,
    o3d,
    pl,
    points_in_boxes_gpu,
    torch,
):
    def count_lidar_points_in_boxes(
        lidar_dir: Path,
        headers_df: pl.DataFrame,
        objects_df: pl.DataFrame,
        sensor: str = "os1-128",  # "os1-128" or "os2-64"
    ) -> pl.DataFrame:
        lidar_dir = Path(lidar_dir)
        cfg = SENSOR_CONFIG[sensor]
        idx_col = cfg["idx_col"]
        prefix = cfg["prefix"]
        out_col = cfg["out_col"]

        all_counts = {}
        rows = list(headers_df.iter_rows(named=True))

        def load_frame(header):
            pcd_path = lidar_dir / f"{prefix}_{header[idx_col]}.pcd"
            if not pcd_path.exists():
                print(f"[WARN] PCD not found: {pcd_path}")
                return header, None
            pcd = o3d.io.read_point_cloud(str(pcd_path))
            points = np.asarray(pcd.points, dtype=np.float32)
            return header, torch.from_numpy(points).pin_memory()

        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = [pool.submit(load_frame, row) for row in rows]

            for future in futures:
                header, points_cpu = future.result()
                if points_cpu is None:
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

                points_gpu = points_cpu.unsqueeze(0).cuda(non_blocking=True)
                boxes_gpu = torch.from_numpy(boxes_np).unsqueeze(0).cuda()
                box_idxs = points_in_boxes_gpu(points_gpu, boxes_gpu).squeeze(0)

                M = boxes_gpu.shape[1]
                shifted = box_idxs + 1
                counts = torch.bincount(shifted, minlength=M + 1)[1:].cpu().numpy()

                for i, tid in enumerate(frame_objs["tracking_id"].to_list()):
                    all_counts[(file_name, tid)] = int(counts[i])

        counts_col = [
            all_counts.get((row["file"], row["tracking_id"]), 0)
            for row in objects_df.iter_rows(named=True)
        ]
        return objects_df.with_columns(pl.Series(out_col, counts_col, dtype=pl.Int32))

    return (count_lidar_points_in_boxes,)


@app.cell
def _(
    L1_FOLDER,
    L2_FOLDER,
    count_lidar_points_in_boxes,
    headers_df,
    objects_df,
):
    objects_with_counts = count_lidar_points_in_boxes(
        L1_FOLDER, headers_df, objects_df, sensor="os1-128"
    )
    print(objects_with_counts.head())

    objects_with_counts = count_lidar_points_in_boxes(
        L2_FOLDER, headers_df, objects_df, sensor="os2-64"
    )
    print(objects_with_counts.head())
    return (objects_with_counts,)


@app.cell
def _(objects_with_counts):
    print(objects_with_counts.shape)

    print(objects_with_counts.head())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Radar
    """
    )
    return


@app.cell
def _(np):
    import scipy.io as sio

    mat = sio.loadmat("/workspace/repos/K-Radar/data/1/radar_zyx_cube/cube_00033.mat")
    arr = mat["arr_zyx"]

    print("Shape:", arr.shape)  # expect (Z, Y, X)
    print("Dtype:", arr.dtype)
    print("Min/Max:", arr.min(), arr.max())
    print("Non-zero cells:", np.count_nonzero(arr))
    return (sio,)


@app.cell
def _(Path, np, sio):
    def radar_zyx_to_pcd(mat_path: Path, power_threshold: float = 0.0):
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

        points = np.stack([x, y, z], axis=1)
        print(
            f"  {mat_path.name}: {len(points)} points above threshold {power_threshold}"
        )
        return points, power_db

    def save_pcd_with_intensity(
        out_path: Path, points: np.ndarray, intensity: np.ndarray
    ):
        """
        Write a PCD file with XYZI fields.
        points:    (N, 3) float32
        intensity: (N,)   float32  ← scalar field, stored as 'intensity'
        """
        N = len(points)
        out_path = Path(out_path)

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

    return radar_zyx_to_pcd, save_pcd_with_intensity


@app.cell
def _(Path, radar_zyx_to_pcd, save_pcd_with_intensity):
    mat_path = Path("/workspace/repos/K-Radar/data/1/radar_zyx_cube/cube_00033.mat")
    out_path = Path("test-bed/src/Modules/robust_testing/outputs") / "cube_00033.pcd"

    points, power_db = radar_zyx_to_pcd(mat_path, power_threshold=0.0)
    save_pcd_with_intensity(out_path, points, power_db)
    return


if __name__ == "__main__":
    app.run()
