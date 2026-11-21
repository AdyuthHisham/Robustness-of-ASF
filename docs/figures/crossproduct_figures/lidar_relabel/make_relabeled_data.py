"""Build LiDAR-gaussian-relabeled copies of the two source parquets.

`lidar_gaussian_noise`'s current low/medium/high schedule (0.1/1.0/2.0m) has
no literature backing (see docs/lit_survey/noise_addition/parameter_audit.md).
This drops the medium/high tiers entirely and relabels the low tier (the one
tier closest to a defensible value) as "high", since it becomes the only
surviving lidar_gaussian_noise data point.

Writes two new parquet files alongside the originals, does not touch the
originals:
    full_denormalized_table_22cond_lidar_relabel.parquet
    crossproduct_v2/summary_full_density_lidar_relabel.parquet

Run: uv run --project test-bed python docs/crossproduct_figures/lidar_relabel/make_relabeled_data.py
"""

from pathlib import Path

import polars as pl

REPO_ROOT = Path("/home/adhish/Productivity/AMSCUP")
REPORTS = REPO_ROOT / "repos/K-Radar/outputs/robustness_reports"

COND_SRC = REPORTS / "full_denormalized_table_22cond.parquet"
COND_OUT = REPORTS / "full_denormalized_table_22cond_lidar_relabel.parquet"

SUMMARY_SRC = REPORTS / "crossproduct_v2" / "summary_full_density.parquet"
SUMMARY_OUT = REPORTS / "crossproduct_v2" / "summary_full_density_lidar_relabel.parquet"


def relabel_22cond() -> None:
    df = pl.read_parquet(COND_SRC)
    n_low = df.filter(pl.col("condition") == "lidar_gaussian_noise_low").height
    df = df.filter(~pl.col("condition").is_in(["lidar_gaussian_noise_medium", "lidar_gaussian_noise_high"]))
    df = df.with_columns(
        pl.when(pl.col("condition") == "lidar_gaussian_noise_low")
        .then(pl.lit("lidar_gaussian_noise_high"))
        .otherwise(pl.col("condition"))
        .alias("condition")
    )
    n_high = df.filter(pl.col("condition") == "lidar_gaussian_noise_high").height
    assert n_high == n_low, f"relabel row-count mismatch: {n_high} != {n_low}"
    assert df.filter(pl.col("condition").is_in(["lidar_gaussian_noise_medium"])).height == 0
    df.write_parquet(COND_OUT)
    print(f"wrote {COND_OUT} ({df.height} rows, lidar_gaussian_noise_high={n_high})")


def relabel_summary() -> None:
    df = pl.read_parquet(SUMMARY_SRC)
    is_lidar_gauss = (pl.col("modality") == "lidar") & (pl.col("effect") == "gaussian_noise")
    n_low = df.filter(is_lidar_gauss & (pl.col("severity") == "low")).height
    df = df.filter(~(is_lidar_gauss & pl.col("severity").is_in(["medium", "high"])))
    is_lidar_gauss_low = is_lidar_gauss & (pl.col("severity") == "low")
    df = df.with_columns(
        pl.when(is_lidar_gauss_low).then(pl.lit("high")).otherwise(pl.col("severity")).alias("severity"),
        pl.when(is_lidar_gauss_low).then(pl.lit("lidar_gaussian_noise_high")).otherwise(pl.col("condition")).alias("condition"),
    )
    n_high = df.filter(is_lidar_gauss & (pl.col("severity") == "high")).height
    assert n_high == n_low, f"relabel row-count mismatch: {n_high} != {n_low}"
    assert df.filter(is_lidar_gauss & (pl.col("severity") == "medium")).height == 0
    df.write_parquet(SUMMARY_OUT)
    print(f"wrote {SUMMARY_OUT} ({df.height} rows, lidar gaussian_noise high={n_high})")


if __name__ == "__main__":
    relabel_22cond()
    relabel_summary()
