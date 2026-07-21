# §7 Verification Test Scaffold

> **Execution Mode: CPU-Only / Validation-Only**
>
> These verification stubs are defined for the full dataset, but the
> *current* build runs them only on a **toy-scale Parquet output** (2
> sequences, ≤20 frames) for sanity checking.  Full-dataset verification
> is future scope.  Tests use Polars on CPU.


> Maps VER-01..26 to pytest stubs that operate on the **output Parquet
> table** (not raw sensor data) — these run after `pipeline.py` produces
> the full table, on the full dataset or a large representative sample.
> Uses Polars throughout for consistency with existing K-Radar pipeline
> code (`headers_df`/`objects_df` pattern).

## Fixture (`tests/conftest.py` addition)

```python
import polars as pl
import pytest

@pytest.fixture(scope="session")
def output_table(full_pipeline_output_path) -> pl.DataFrame:
    """TODO: load the toy-scale visibility parquet table (2 sequences, ≤20 frames)."""
    return pl.read_parquet(full_pipeline_output_path)
```

## 7.1 Sensor Identify Consistency (`test_verify.py::TestSensorIdentifyConsistency`)

```python
class TestSensorIdentifyConsistency:
    def test_ver01_r_implies_radar_visible(self, output_table):
        """VER-01: sensor_identify contains 'R' -> radar_visible True, 100% match."""
        subset = output_table.filter(pl.col("sensor_identify").str.contains("R"))
        # TODO: mismatches = subset.filter(~pl.col("radar_visible"))
        # assert mismatches.height == 0, f"{mismatches.height} mismatches, flag for review"
        raise NotImplementedError

    def test_ver02_l1_implies_lidar64_visible(self, output_table):
        """VER-02: 100% match."""
        raise NotImplementedError

    def test_ver03_l2_implies_lidar128_visible(self, output_table):
        """VER-03: 100% match."""
        raise NotImplementedError

    def test_ver04_unspecified_l_implies_some_lidar(self, output_table):
        """VER-04: sensor_identify == 'L' -> lidar64_visible OR lidar128_visible, >=95%."""
        # TODO: subset = output_table.filter(pl.col("sensor_identify") == "L")
        # match_rate = subset.filter(pl.col("lidar64_visible") | pl.col("lidar128_visible")).height / subset.height
        # assert match_rate >= 0.95
        raise NotImplementedError

    def test_ver05_sensor_identify_never_contains_c(self, output_table):
        """VER-05: no 'C' in any sensor_identify value."""
        # TODO: bad = output_table.filter(pl.col("sensor_identify").str.contains("C"))
        # assert bad.height == 0
        raise NotImplementedError
```

## 7.2 Distance Correlation (`test_verify.py::TestDistanceCorrelation`)

```python
DISTANCE_BINS = [0, 20, 40, 60, 80, 120]

class TestDistanceCorrelation:
    def _bin_and_median(self, output_table, col):
        """Shared helper: bin by obj_distance_ego, return median(col) per bin."""
        # TODO: return (
        #     output_table
        #     .with_columns(pl.col("obj_distance_ego").cut(DISTANCE_BINS).alias("dist_bin"))
        #     .group_by("dist_bin")
        #     .agg(pl.col(col).median())
        #     .sort("dist_bin")
        # )
        raise NotImplementedError

    def test_ver06_lidar64_points_decrease_with_distance(self, output_table):
        """VER-06: median lidar64_points_count strictly decreases across bins (or R^2>0.5)."""
        raise NotImplementedError

    def test_ver07_lidar128_points_decrease_with_distance(self, output_table):
        """VER-07: same as VER-06 for OS1-128."""
        raise NotImplementedError

    def test_ver08_radar_sparsity_decreases_with_distance(self, output_table):
        """VER-08: monotonic decrease, R^2 > 0.3 (radar noisier, looser bound)."""
        raise NotImplementedError

    def test_ver09_camera_score_negatively_correlated_with_distance(self, output_table):
        """VER-09: for cam_front_visible==True, corr(score, distance) < 0, p<0.05."""
        # TODO: from scipy.stats import pearsonr
        raise NotImplementedError
```

## 7.3 Camera Projection Sanity (`test_verify.py::TestCameraProjectionSanity`)

```python
class TestCameraProjectionSanity:
    @pytest.mark.parametrize("cam", ["cam_front", "cam_left", "cam_right", "cam_rear"])
    def test_ver10_projections_in_bounds(self, output_table, cam):
        """VER-10: visible==True rows have 0<=proj_x<1280, 0<=proj_y<720, 100%."""
        raise NotImplementedError

    @pytest.mark.parametrize("cam", ["cam_front", "cam_left", "cam_right", "cam_rear"])
    def test_ver11_invisible_have_null_projection(self, output_table, cam):
        """VER-11: visible==False -> proj_x/proj_y are NULL, 100%."""
        raise NotImplementedError

    def test_ver12_front_camera_sees_forward(self, output_table):
        """VER-12: cam_front_visible==True -> >=90% have obj_x>0."""
        raise NotImplementedError

    def test_ver13_rear_camera_sees_behind(self, output_table):
        """VER-13: cam_rear_visible==True -> >=90% have obj_x<0."""
        raise NotImplementedError

    def test_ver14_left_camera_sees_left(self, output_table):
        """VER-14: cam_left_visible==True -> >=70% have obj_y>0 (wide FOV tolerance)."""
        raise NotImplementedError

    def test_ver15_right_camera_sees_right(self, output_table):
        """VER-15: cam_right_visible==True -> >=70% have obj_y<0."""
        raise NotImplementedError
```

## 7.4 Primary Sensor Logic (`test_verify.py::TestPrimarySensorLogic`)

```python
class TestPrimarySensorLogic:
    def test_ver16_primary_sensor_is_argmax_score(self, output_table):
        """VER-16: primary_sensor matches max-score visible sensor, >=98% (ties allowed)."""
        raise NotImplementedError

    def test_ver17_num_sensors_visible_matches_count(self, output_table):
        """VER-17: num_sensors_visible == count of True across all *_visible cols, 100%."""
        raise NotImplementedError

    def test_ver18_primary_sensor_null_when_zero_visible(self, output_table):
        """VER-18: num_sensors_visible==0 -> primary_sensor is NULL, 100%."""
        raise NotImplementedError
```

## 7.5 Data Quality (`test_verify.py::TestDataQuality`)

```python
class TestDataQuality:
    def test_ver19_no_negative_scores(self, output_table):
        """VER-19: radar_sparsity_score, lidar*_sparsity_score, cam*_visibility_score all >=0."""
        raise NotImplementedError

    def test_ver20_no_negative_point_counts(self, output_table):
        """VER-20: lidar*_points_count all >=0."""
        raise NotImplementedError

    def test_ver21_distance_consistent_with_xyz(self, output_table):
        """VER-21: sqrt(x^2+y^2+z^2) matches obj_distance_ego within 0.01m, 100%."""
        raise NotImplementedError

    def test_ver22_dimensions_positive(self, output_table):
        """VER-22: obj_length/width/height all > 0."""
        raise NotImplementedError

    def test_ver23_no_duplicate_primary_keys(self, output_table):
        """VER-23: 0 duplicate (sequence_id, frame_idx, obj_tracking_id) tuples."""
        # TODO: dupes = output_table.group_by(["sequence_id","frame_idx","obj_tracking_id"]).len().filter(pl.col("len")>1)
        # assert dupes.height == 0
        raise NotImplementedError

    def test_ver24_all_sequences_represented(self, output_table):
        """VER-24: distinct sequence_id count == 58 (or actual dataset size)."""
        raise NotImplementedError
```

## 7.6 Weather Impact (`test_verify.py::TestWeatherImpact`, optional)

```python
@pytest.mark.optional
class TestWeatherImpact:
    def test_ver25_lidar_lower_in_adverse_weather(self, output_table):
        """VER-25: median lidar*_points_count per distance bin, clear vs rain/sleet/snow, p<0.05."""
        # TODO: requires weather column joined in from description.txt at pipeline stage
        # from scipy.stats import mannwhitneyu
        raise NotImplementedError

    def test_ver26_radar_less_weather_sensitive_than_lidar(self, output_table):
        """VER-26: variance of radar_sparsity_score across weather < variance of lidar*_sparsity_score."""
        raise NotImplementedError
```

## Run target

```
pytest tests/test_verify.py -v --durations=20   # toy-scale only; full-dataset is future scope
pytest tests/test_verify.py -v -m "not optional"   # skip §7.6 if weather labels unavailable
```

## Report generation

`pipeline.py` (or a `scripts/verification_report.py`) should collect each
test's pass/fail + measured value into a single artifact, per Sub-Goal 7:

```python
# TODO: scripts/verification_report.py
# Run pytest with --json-report, parse results, emit
# verification_report.md with one row per VER-XX: {status, measured_value, threshold}
```
