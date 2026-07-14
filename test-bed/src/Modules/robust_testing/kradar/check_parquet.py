import polars as pl
df = pl.read_parquet('output.parquet')
print('rows:', df.height)
print('columns:', df.columns)
if 'weather' in df.columns:
    print('weather values:', df['weather'].unique().to_list())
else:
    print('weather column not found')