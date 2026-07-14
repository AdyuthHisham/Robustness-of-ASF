import polars as pl
df = pl.read_parquet('output.parquet')
print('Total rows:', df.height)
print('Unique sensor_identify:', df['sensor_identify'].unique().to_list())
print('Count of L:', df.filter(pl.col('sensor_identify') == 'L').height)
print('Count of L1:', df.filter(pl.col('sensor_identify') == 'L1').height)
print('Count of L2:', df.filter(pl.col('sensor_identify') == 'L2').height)