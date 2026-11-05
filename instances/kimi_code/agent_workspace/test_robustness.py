import numpy as np, pandas as pd, os, time
from c20_module import run_sweep

param_grid = {
    'c_plast': [0.05, 0.10],
    'K': [80],
    'sigma_w': [0.35],
}

t0 = time.time()
df = run_sweep(param_grid, replicates=1, n_workers=2)
elapsed = time.time() - t0
print(f"Test sweep completed {len(df)} simulations in {elapsed:.1f}s")
print(df[['c_plast','K','sigma_w','final_N','maladaptation','spatial_ratio']].to_string(index=False))
