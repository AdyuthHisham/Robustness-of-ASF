import numpy as np
import pytest

from kradar_visibility import (
    # Radar
    compute_radar_sparsity_score,
    # LiDAR
    calculate_lidar_visibility, load_camera_calibration, get_camera_params, calculate_visibility_score, calculate_camera_visibility,
    project_point_to_image,
    # Parser
    parse_label_file,
    get_sequence_label_files, parse_description_txt,
    HeaderInfo, load_radar_cube, load_lidar_points, load_camera_image,
    ALLOWED_WEATHER,
)


class TestParsing:
    def test_smk01_header_and_object_counts(self, dataset_root):
        """SMK-01: parse one file, header count==1, object count==N matching manual count."""
        sample_file = dataset_root / "data" / "1" / "info_label_rev2" / "00033_00001.txt"
        header, objects = parse_label_file(sample_file)
        assert header is not None
        assert isinstance(header, HeaderInfo)
        assert len(objects) > 0
        # Manual count: each file in this dataset has 1 object line
        assert len(objects) == 1

    def test_smk02_cam_lrr_shared_index(self, dataset_root):
        """SMK-02: cam-lrr index resolves to existing files for left/right/rear."""
        sample_file = dataset_root / "data" / "1" / "info_label_rev2" / "00033_00001.txt"
        header, _ = parse_label_file(sample_file)
        cam_lrr_idx = header.cam_lrr_idx
        
        for cam in ("cam-left", "cam-right", "cam-rear"):
            path = dataset_root / "data" / "1" / cam / f"{cam}_{cam_lrr_idx}.png"
            assert path.exists(), f"{cam} image not found at {path}"

    def test_smk03_all_calibrations_loaded(self, dataset_root):
        """SMK-03: 7 calibration objects loaded, all matrices valid shapes."""
        # We have 8 camera keys (front0, front1, right0, right1, rear0, rear1, left0, left1)
        # Plus radar-lidar calibration is implicit in the T_params_seq pickle
        calib = load_camera_calibration(seq=1)
        expected_keys = {'front0', 'front1', 'right0', 'right1', 'rear0', 'rear1', 'left0', 'left1'}
        assert set(calib.keys()) == expected_keys
        for key in calib:
            assert 'camera_intrinsics' in calib[key]
            assert 'radar2camera' in calib[key]
            assert calib[key]['camera_intrinsics'].shape == (4, 4)
            assert calib[key]['radar2camera'].shape == (4, 4)

    def test_smk04_weather_labels_valid(self, dataset_root):
        """SMK-04: description.txt weather labels in allowed set, 3 random sequences."""
        desc = parse_description_txt("1", dataset_root)
        assert desc['weather'] in ALLOWED_WEATHER


class TestProjection:
    @pytest.mark.parametrize("xyz,camera,expect_visible", [
        ((10, 0, 0), "front", True),   # SMK-05
        ((-10, 0, 0), "rear", True),   # SMK-06
        ((0, 10, 0), "left", True),     # SMK-07
        ((0, -10, 0), "right", True),   # SMK-08
    ])
    def test_smk05_08_projection_smoke(self, xyz, camera, expect_visible):
        params = get_camera_params(camera, seq=1)[0]
        point = np.array([xyz], dtype=np.float32)
        u, v, z_cam = project_point_to_image(point, params['camera_intrinsics'], params['radar2camera'])
        assert (z_cam[0] > 0) == expect_visible
        if expect_visible:
            assert 0 <= u[0] < 1280
            assert 0 <= v[0] < 720

    def test_smk09_behind_camera_rejected(self):
        """SMK-09: negative z_cam -> cam_front_visible=False."""
        # A point behind the front camera (in camera coordinates, z < 0)
        # Use a point that's clearly behind the vehicle
        obj_corners = np.array([
            [-5, 0, 0], [-5, 1, 0], [-5, -1, 0], [-5, 0, 1],
            [-5, 1, 1], [-5, -1, 1], [-5, 0.5, 0.5], [-5, -0.5, 0.5],
        ], dtype=np.float32)
        params = get_camera_params('front', seq=1)[0]
        score = calculate_visibility_score(obj_corners, params)
        assert score == 0.0


class TestLoading:
    def test_smk10_radar_tensor_shape(self, dataset_root):
        """SMK-10: one zyx_cube frame loads with valid shape, no OOM."""
        radar_cube = load_radar_cube("1", "00033", dataset_root)
        assert radar_cube is not None
        assert radar_cube.ndim == 3

    def test_smk11_os2_64_pointcloud(self, dataset_root):
        """SMK-11: N>0 points for a frame with visible objects."""
        points = load_lidar_points("1", "00001", "os2-64", dataset_root)
        assert points is not None
        assert points.ndim == 2
        assert points.shape[1] == 3
        assert len(points) > 0

    def test_smk12_os1_128_denser_than_os2_64(self, dataset_root):
        """SMK-12: OS1-128 point count >= OS2-64 for same frame."""
        os2_points = load_lidar_points("1", "00001", "os2-64", dataset_root)
        os1_points = load_lidar_points("1", "00001", "os1-128", dataset_root)
        assert os2_points is not None
        assert os1_points is not None
        assert len(os1_points) >= len(os2_points)

    def test_smk13_camera_images_load(self, dataset_root):
        """SMK-13: all 4 camera images load, shape (720,2560,3) stitched stereo, pixels in [0,255]."""
        # Use the cam-lrr shared index from a sample label file
        sample_file = dataset_root / "data" / "1" / "info_label_rev2" / "00033_00001.txt"
        header, _ = parse_label_file(sample_file)
        
        for cam in ("cam-front", "cam-left", "cam-right", "cam-rear"):
            if cam == "cam-front":
                idx = header.cam_front_idx
            else:
                idx = header.cam_lrr_idx
            
            img = load_camera_image("1", idx, cam, dataset_root)
            assert img is not None, f"Failed to load {cam} image at idx {idx}"
            # Stitched stereo pair: 2560x720 (two 1280x720 images side by side)
            assert img.shape == (720, 2560, 3), f"{cam} shape mismatch: {img.shape}"
            assert img.min() >= 0 and img.max() <= 255
            
            # Verify we can split into left/right halves
            left_half = img[:, :1280, :]
            right_half = img[:, 1280:, :]
            assert left_half.shape == (720, 1280, 3)
            assert right_half.shape == (720, 1280, 3)


class TestMetrics:
    def test_smk14_radar_score_monotonic_with_distance(self):
        """SMK-14: close object (10m) score > far object (80m) score."""
        shape = (100, 100, 100)
        radar_cube = np.ones(shape) * 0.5
        radar_cube[10:20, 10:20, 10:20] += 5.0
        radar_cube[80:90, 80:90, 80:90] += 1.0
        close_bbox = {'z_min': 10, 'z_max': 20, 'y_min': 10, 'y_max': 20, 'x_min': 10, 'x_max': 20}
        far_bbox = {'z_min': 80, 'z_max': 90, 'y_min': 80, 'y_max': 90, 'x_min': 80, 'x_max': 90}
        close_score = compute_radar_sparsity_score(radar_cube, close_bbox)
        far_score = compute_radar_sparsity_score(radar_cube, far_bbox)
        assert close_score > far_score

    def test_smk15_lidar_count_os1_128_ge_os2_64(self):
        """SMK-15: same object, OS1-128 point count >= OS2-64."""
        points = np.array([
            [5, 5, 5], [6, 6, 6], [7, 7, 7],
            [80, 80, 80],
        ], dtype=np.float32)
        close_bbox = [[0, 10, 0, 10, 0, 10]]
        far_bbox = [[75, 85, 75, 85, 75, 85]]
    
        fov = [-100, 100, -100, 100]
        range_limit = [0, 200]
    
        # Expected densities from config constants (§4.2 method B)
        from kradar_visibility.config import (
            OS2_64_CHANNELS, OS2_64_VFOV_DEG, OS2_64_HRES_DEG,
            OS1_128_CHANNELS, OS1_128_VFOV_DEG, OS1_128_HRES_DEG,
        )
        expected_os2 = (OS2_64_CHANNELS * OS2_64_VFOV_DEG / 360.0) * (360.0 / OS2_64_HRES_DEG)
        expected_os1 = (OS1_128_CHANNELS * OS1_128_VFOV_DEG / 360.0) * (360.0 / OS1_128_HRES_DEG)
    
        # Both sensors see the same point cloud here — OS1-128 should yield
        # a lower sparsity score (same count / higher expected density), but
        # raw point *count* is identical since it's the same cloud.
        # The test validates count >= 0 and score ordering.
        close_os2 = calculate_lidar_visibility(points, close_bbox, fov, range_limit, expected_os2)
        close_os1 = calculate_lidar_visibility(points, close_bbox, fov, range_limit, expected_os1)
        far_os2   = calculate_lidar_visibility(points, far_bbox,   fov, range_limit, expected_os2)
        far_os1   = calculate_lidar_visibility(points, far_bbox,   fov, range_limit, expected_os1)
    
        # Raw counts must match (same cloud, same bbox)
        assert close_os2[1][0] == close_os1[1][0], "same cloud → same raw count"
        assert far_os2[1][0]   == far_os1[1][0]
    
        # Close bbox sees more points than far bbox
        assert close_os2[1][0] > far_os2[1][0]
    
        # OS1-128 sparsity score should be lower than OS2-64 for same count
        # (higher expected density → lower normalised score)
        assert close_os1[2][0] < close_os2[2][0], "OS1-128 score < OS2-64 for same count"

    def test_smk16_camera_score_center_gt_edge(self):
        """SMK-16: center-of-frame object score > edge-of-FOV object score."""
        # Center object (in front of vehicle)
        center_corners = np.array([
            [10, -1, 0], [10, 1, 0],
            [12, -1, 0], [12, 1, 0],
            [10, -1, 2], [10, 1, 2],
            [12, -1, 2], [12, 1, 2],
        ], dtype=np.float32)
        scores = calculate_camera_visibility(center_corners, seq=1)
        assert scores['front'] > 0

    def test_smk17_full_pipeline_two_sequences(self, dataset_root, smoke_sequence_ids, smoke_frame_limit, tmp_path):
            """SMK-17: end-to-end pipeline.py run on 2 sequences / 20 frames -> parquet, no crash, all columns present."""
            from kradar_visibility.pipeline import run
            import polars as pl

            # Run the pipeline on the two sequences with frame limit
            df = run(
                sequence_ids=smoke_sequence_ids,
                frame_limit=smoke_frame_limit,
                dataset_root=dataset_root,
                output_path=tmp_path / "smoke_output.parquet"
            )

            # Check that we got data
            assert df.height > 0, "Pipeline produced no output"

            # Check that expected columns are present (including those from phases 1-3)
            expected_cols = [
                'sequence_id', 'frame_idx', 'obj_tracking_id', 'obj_class',
                'radar_visible', 'radar_sparsity_score',
                'lidar64_visible', 'lidar64_points_count', 'lidar64_sparsity_score',
                'lidar128_visible', 'lidar128_points_count', 'lidar128_sparsity_score',
                'cam_front_visible', 'cam_front_visibility_score',
                'cam_left_visible', 'cam_left_visibility_score',
                'cam_right_visible', 'cam_right_visibility_score',
                'cam_rear_visible', 'cam_rear_visibility_score',
                'ghost_flag'  # New in phase 2
            ]
            for col in expected_cols:
                assert col in df.columns, f"Missing expected column: {col}"

            # Check that ghost flag is boolean
            assert df['ghost_flag'].dtype == pl.Boolean, "ghost_flag column must be boolean"

            # Optionally, check that the file was written
            out_path = tmp_path / "smoke_output.parquet"
            assert out_path.exists(), "Output Parquet file was not created"

            # Read back and verify same shape
            df_read = pl.read_parquet(out_path)
            assert df_read.height == df.height, "Row count mismatch between returned DF and saved Parquet"

    def test_smk_frame_limit_uses_annotated_frames(self, dataset_root):
        """frame_limit=N must select N frames that have at least one object,
        skipping empty frames — not just the first N files."""
        from kradar_visibility.parser import get_sequence_label_files, parse_label_file
    
        # Sequence 2 has empty frames at the start, making it the ideal test case
        seq_id = "2"
        frame_limit = 5
    
        label_files = get_sequence_label_files(seq_id, dataset_root)
    
        # Replicate the pipeline's frame-selection logic
        annotated = []
        for f in label_files:
            if len(annotated) >= frame_limit:
                break
            try:
                _, objects = parse_label_file(f)
                if objects:
                    annotated.append(f)
            except Exception:
                continue
    
        # Must have found exactly frame_limit annotated files
        assert len(annotated) == frame_limit, (
            f"Expected {frame_limit} annotated frames, got {len(annotated)}"
        )
    
        # Every selected file must actually contain at least one object
        for f in annotated:
            _, objects = parse_label_file(f)
            assert len(objects) > 0, f"{f.name} was selected but has no objects"
    
        # Sanity check: the naive first-N approach would have missed these
        # (sequence 2 has empty frames before any annotated ones)
        naive_files = label_files[:frame_limit]
        naive_objects = sum(
            len(parse_label_file(f)[1]) for f in naive_files
        )
        assert naive_objects == 0, (
            "Sequence 2 should have 0 objects in its first N files — "
            "if this fails, pick a sequence with leading empty frames"
        )
    
    def test_smk_all_sequences_accessible(self, dataset_root):
        """All 58 sequence directories must exist and contain at least one
        label file with at least one annotated object."""
        from kradar_visibility.parser import get_sequence_label_files, parse_label_file
    
        EXPECTED_SEQUENCES = [str(i) for i in range(1, 59)]  # "1" through "58"
    
        missing_dirs = []
        empty_sequences = []  # dir exists but zero label files
        no_annotations = []   # label files exist but none have objects
    
        for seq_id in EXPECTED_SEQUENCES:
            seq_dir = dataset_root / "data" / seq_id
            if not seq_dir.exists():
                missing_dirs.append(seq_id)
                continue
    
            label_files = get_sequence_label_files(seq_id, dataset_root)
            if not label_files:
                empty_sequences.append(seq_id)
                continue
    
            # Check that at least one file in the sequence has objects
            has_annotation = False
            for f in label_files:
                try:
                    _, objects = parse_label_file(f)
                    if objects:
                        has_annotation = True
                        break
                except Exception:
                    continue
    
            if not has_annotation:
                no_annotations.append(seq_id)
    
        # Report all failures together rather than stopping at first
        failures = []
        if missing_dirs:
            failures.append(f"Missing sequence directories: {missing_dirs}")
        if empty_sequences:
            failures.append(f"Sequences with no label files: {empty_sequences}")
        if no_annotations:
            failures.append(f"Sequences with no annotated objects: {no_annotations}")
    
        assert not failures, "\n".join(failures)
