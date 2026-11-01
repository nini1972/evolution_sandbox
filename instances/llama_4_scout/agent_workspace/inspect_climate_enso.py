from colony_lib.datasets import load_dataset
import pandas as pd

ds = load_dataset("climate_enso")
print(ds.head())
print(ds.describe())