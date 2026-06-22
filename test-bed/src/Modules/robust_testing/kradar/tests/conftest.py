import pytest
from pathlib import Path
import polars as pl

@pytest.fixture(scope="session")
def dataset_root():
    return Path("/home/adhish/Productivity/AMSCUP/repos/K-Radar")

@pytest.fixture(scope="session")
def smoke_sequence_ids():
    return ["1", "2"]

@pytest.fixture(scope="session")
def smoke_frame_limit():
    return 20

@pytest.fixture(scope="session")
def output_table():
    """Load the toy-scale visibility parquet table (2 sequences, ≤20 frames)."""
    parquet_path = Path("/home/adhish/Productivity/AMSCUP/test-bed/src/Modules/robust_testing/kradar/output.parquet")
    if not parquet_path.exists():
        pytest.skip("Parquet output not found — run pipeline first")
    return pl.read_parquet(parquet_path)
