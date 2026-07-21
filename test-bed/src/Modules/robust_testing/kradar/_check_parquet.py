import polars as pl
df = pl.read_parquet("output.parquet")
print("Columns:", df.columns)
print("Shape:", df.shape)
print("Has ghost_flag:", "ghost_flag" in df.columns)
print("Has weather:", "weather" in df.columns)
if "ghost_flag" in df.columns:
    print("ghost_flag dtype:", df["ghost_flag"].dtype)
    print("ghost_flag value counts:", df["ghost_flag"].value_counts())
if "weather" in df.columns:
    print("weather value counts:", df["weather"].value_counts())
# Check score ranges
print()
print("radar_sparsity_score range:", df["radar_sparsity_score"].min(), "-", df["radar_sparsity_score"].max())
print("lidar64_sparsity_score range:", df["lidar64_sparsity_score"].min(), "-", df["lidar64_sparsity_score"].max())
print("lidar128_sparsity_score range:", df["lidar128_sparsity_score"].min(), "-", df["lidar128_sparsity_score"].max())
print("cam_front_visibility_score range:", df["cam_front_visibility_score"].min(), "-", df["cam_front_visibility_score"].max())