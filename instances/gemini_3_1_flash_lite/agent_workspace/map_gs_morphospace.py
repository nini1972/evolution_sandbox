import numpy as np
from colony_lib.dynamics import GrayScott2D
from scipy.ndimage import label
import json

def get_gs_pattern(f, k, grid_size=64):
    gs = GrayScott2D(size=(grid_size, grid_size), f=f, k=k)
    gs.u[:] = 1.0
    gs.v[:] = 0.0
    gs.v[32-5:32+5, 32-5:32+5] = 0.5
    gs.u[32-5:32+5, 32-5:32+5] = 0.5
    for _ in range(5000):
        gs.step()
    return gs.v

def get_phenotype(pattern):
    # Use threshold 0.1 to discriminate spots vs stripes
    mask = (pattern > 0.1).astype(int)
    _, count = label(mask)
    return count

f_range = np.linspace(0.02, 0.05, 10)
k_range = np.linspace(0.04, 0.07, 10)

results = {}
for f in f_range:
    for k in k_range:
        pattern = get_gs_pattern(f, k)
        pheno = get_phenotype(pattern)
        results[f"f={f:.3f}_k={k:.3f}"] = pheno

with open('morphospace_map.json', 'w') as f:
    json.dump(results, f)
