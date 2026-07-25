import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
def smooth(arr, w=10):
    out = np.zeros_like(arr, dtype=float)
    for i in range(len(arr)):
        lo = max(0, i - w)
        hi = min(len(arr), i + w + 1)
        out[i] = arr[lo:hi].mean()
    return out

def life_step(grid):
    nbrs = sum(np.roll(np.roll(grid, i, 0), j, 1)
               for i in (-1,0,1) for j in (-1,0,1) if (i,j) != (0,0))
    return ((nbrs == 3) | (grid & (nbrs == 2))).astype(int)

size = 80
np.random.seed(42)
grid = (np.random.rand(size, size) < 0.3).astype(int)

populations = []
for step in range(200):
    grid = life_step(grid)
    populations.append(grid.sum())

pops = np.array(populations, dtype=float)
print("Life populations range:", pops.min(), pops.max())

smoothed = smooth(pops, w=10)
s = (smoothed - smoothed.min()) / (smoothed.max() - smoothed.min() + 1e-9)
s = s * 2 - 1
thetas = s * np.pi
radii = 0.73 + 0.06 * np.cos(s * np.pi)
c_values = radii * np.exp(1j * thetas)

print("c values range:", c_values.real.min(), c_values.real.max())
