---
title: §6 Smoke Test Scaffold
type: decision
source: home/adhish/Downloads/06_smoke_tests_scaffold.md
date: 2026-07-02
tags: [05 Implementation]
---
# §6 Smoke Test Scaffold

> **Execution Mode: CPU-Only / Validation-Only**
>
> These smoke tests are designed to run on a **toy-scale subset** (1–2
> sequences, ≤20 frames) in under 5 minutes on CPU.  They validate
> correctness, not performance.  Full-dataset smoke tests and GPU
> execution are future scope.


> Maps SMK-01..17 to concrete pytest stubs. Fixtures assume the package
> layout from §8 (`kradar_visibility/`). All bodies are `TODO` — this is
> structure, not implementation. Built against the methodology choices in
> `04_visibility_methodology.md` (radar=B, lidar=A+B, camera=B).

## Fixtures (`tests/conftest.py`)

```python
import polars as pl
import pytest
from pathlib import Path

@pytest.fixture(scope="session")
def dataset_root() -> Path:
    """Root containing sequence folders 1..58. TODO: read from config.py / env var KRADAR_ROOT."""
    raise NotImplementedError

@pytest.fixture(scope="session")
def smoke_sequence_ids() -> list[str]:
    """1-2 sequences for smoke testing. TODO: pick sequences covering >=2 weather conditions."""
    return ["1", "2"]

@pytest.fixture(scope="session")
def smoke_frame_limit() -> int:
    return 20  # 10-20 frames per §6 intro

@pytest.fixture(scope="session")
def calib_loader(dataset_root):
    """TODO: from calibration.py, returns loaded calibration for all 7 sensors."""
    raise NotImplementedError

@pytest.fixture
def sample_label_file(dataset_root, smoke_sequence_ids):
    """TODO: path to one info_label_rev2/*.txt for sequence smoke_sequence_ids[0]."""
    raise NotImplementedError
```

## 6.1 Data Parsing (`test_smoke.py::TestParsing`)

```python
class TestParsing:
    def test_smk01_header_and_object_counts(self, sample_label_file):
        """SMK-01: parse one file, header count==1, object count==N matching manual count."""
        # TODO: from parser.py import parse_label_file
        # header, objects = parse_label_file(sample_label_file)
        # assert header is not None
        # assert len(objects) == EXPECTED_N  # fill in after manual inspection
        raise NotImplementedError

    def test_smk02_cam_lrr_shared_index(self, dataset_root, sample_label_file):
        """SMK-02: cam-lrr index resolves to existing files for left/right/rear."""
        # TODO: header = parse_header(sample_label_file)
        # for cam in ("cam-left", "cam-right", "cam-rear"):
        #     path = build_camera_path(dataset_root, cam, header.cam_lrr_idx)
        #     assert path.exists()
        raise NotImplementedError

    def test_smk03_all_calibrations_loaded(self, calib_loader):
        """SMK-03: 7 calibration objects loaded, all matrices valid shapes."""
        # TODO: assert set(calib_loader.keys()) == {"R","L1","L2","CF","CL","CR","CRE"}
        # for sensor, calib in calib_loader.items():
        #     assert calib.K.shape == (3,3) if sensor.startswith("C") else True
        raise NotImplementedError

    def test_smk04_weather_labels_valid(self, dataset_root):
        """SMK-04: description.txt weather labels in allowed set, 3 random sequences."""
        ALLOWED = {"clear", "overcast", "fog", "rain", "sleet", "snow"}
        # TODO: sample 3 sequences, parse description.txt, assert label in ALLOWED
        raise NotImplementedError
```

## 6.2 Coordinate Transforms (`test_smoke.py::TestProjection`)

```python
class TestProjection:
    @pytest.mark.parametrize("xyz,camera,expect_visible", [
        ((10, 0, 0), "cam-front", True),   # SMK-05: center of image (~640,360) +-50px
        ((-10, 0, 0), "cam-rear", True),   # SMK-06
        ((0, 10, 0), "cam-left", True),    # SMK-07: 0<=u<1280, 0<=v<720
        ((0, -10, 0), "cam-right", True),  # SMK-08
    ])
    def test_projection_smoke(self, calib_loader, xyz, camera, expect_visible):
        # TODO: from camera_visibility.py import project_point
        # u, v, z = project_point(xyz, calib_loader[camera])
        # assert (z > 0) == expect_visible
        # if expect_visible: assert 0 <= u < 1280 and 0 <= v < 720
        raise NotImplementedError

    def test_smk09_behind_camera_rejected(self, calib_loader):
        """SMK-09: negative z_cam -> cam_front_visible=False."""
        # TODO: project a point known to be behind front camera, assert visible=False
        raise NotImplementedError
```

## 6.3 Sensor Data Loading (`test_smoke.py::TestLoading`)

```python
class TestLoading:
    def test_smk10_radar_tensor_shape(self, dataset_root, smoke_sequence_ids):
        """SMK-10: one zyx_cube (or 4DRT) frame loads with valid shape, no OOM."""
        # TODO: from data_loader.py import load_radar_cube
        raise NotImplementedError

    def test_smk11_os2_64_pointcloud(self, dataset_root, smoke_sequence_ids):
        """SMK-11: N>0 points for a frame with visible objects."""
        raise NotImplementedError

    def test_smk12_os1_128_denser_than_os2_64(self, dataset_root, smoke_sequence_ids):
        """SMK-12: OS1-128 point count >= OS2-64 for same frame (CPU point-in-box)."""
        raise NotImplementedError

    def test_smk13_camera_images_load(self, dataset_root, smoke_sequence_ids):
        """SMK-13: all 4 camera images load, shape (720,1280,3), pixels in [0,255]."""
        raise NotImplementedError
```

## 6.4 Visibility Metrics (`test_smoke.py::TestMetrics`)

```python
class TestMetrics:
    def test_smk14_radar_score_monotonic_with_distance(self):
        """SMK-14: close object (10m) score > far object (80m) score. Tests method B from §4.1."""
        # TODO: from radar_visibility.py import compute_radar_sparsity_score
        raise NotImplementedError

    def test_smk15_lidar_count_os1_128_ge_os2_64(self):
        """SMK-15: same object, OS1-128 point count >= OS2-64. Tests CPU method A from §4.2."""
        raise NotImplementedError

    def test_smk16_camera_score_center_gt_edge(self):
        """SMK-16: center-of-frame object score > edge-of-FOV object score. Tests method B from §4.3."""
        raise NotImplementedError

    def test_smk17_full_pipeline_two_sequences(self, dataset_root, smoke_sequence_ids, smoke_frame_limit, tmp_path):
        """SMK-17: end-to-end pipeline.py run on 2 sequences / 20 frames -> parquet, no crash, all columns present."""
        # TODO: from pipeline import run
        # out_path = tmp_path / "smoke_output.parquet"
        # run(sequence_ids=smoke_sequence_ids, frame_limit=smoke_frame_limit, output_path=out_path)
        # df = pl.read_parquet(out_path)
        # assert df.height > 0
        # EXPECTED_COLUMNS = [...]  # from §3.1 schema
        # assert set(EXPECTED_COLUMNS).issubset(df.columns)
        raise NotImplementedError
```

## Run target

```
pytest tests/test_smoke.py -v --timeout=300   # must complete < 5 min on CPU, toy subset
```
