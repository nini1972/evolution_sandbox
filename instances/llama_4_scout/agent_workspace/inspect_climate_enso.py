from colony_lib.datasets import load_dataset

ds = load_dataset("climate_enso")
print(ds.data.shape)
print(ds.data[:5])
print(ds.description)