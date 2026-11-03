import numpy as np
import pandas as pd
from colony_lib.datasets import load_dataset

ds = load_dataset('belousov_zhabotinsky')
df = ds.to_dataframe()
print("Variables summary:")
print(df.describe())

# Check relations between u, v, z and redox
# In Oregonator:
# u: HBrO2 (bromous acid)
# v: Br- (bromide ion)
# z: Ce4+ / Fe(phen)3 3+ (oxidized catalyst)
# redox: Nernst potential ~ E0 + (RT/nF) * ln(z / (z_tot - z))
print("\nCorrelation matrix:")
print(df.corr())

