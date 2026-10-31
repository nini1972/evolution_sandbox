from colony_lib.datasets import load_dataset

ds = load_dataset('solar_sunspots')
df = ds.to_dataframe()
print(df.head())