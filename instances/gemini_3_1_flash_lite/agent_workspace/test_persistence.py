import numpy as np
from colony_lib.dynamics import GrayScott2D
from colony_lib.morphospace import betti0_persistence

def get_gs_pattern(f, k, grid_size=64):
    gs = GrayScott2D(size=(grid_size, grid_size), f=f, k=k)
    gs.u[:] = 1.0
    gs.v[:] = 0.0
    gs.v[32-5:32+5, 32-5:32+5] = 0.5
    gs.u[32-5:32+5, 32-5:32+5] = 0.5
    for _ in range(3000):
        gs.step()
    return gs.v

f_vals = [0.03, 0.04]
k_val = 0.06

for f in f_vals:
    pattern = get_gs_pattern(f, k_val)
    persistence = betti0_persistence(pattern)
    print(f"f={f}: Persistence={persistence}")
