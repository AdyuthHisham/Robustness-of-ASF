import polars as pl
df = pl.read_parquet('output.parquet')
print(','.join(df.columns))