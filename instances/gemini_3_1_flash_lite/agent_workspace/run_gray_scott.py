import numpy as np
import json
import matplotlib.pyplot as plt
import matplotlib; matplotlib.use("Agg")

# Simple 2D Gray-Scott
grid_size = 50
A = 0.04
B = 0.06
u = np.ones((grid_size, grid_size))
v = np.zeros((grid_size, grid_size))
v[grid_size//2-5:grid_size//2+5, grid_size//2-5:grid_size//2+5] = 1.0

# Simple update steps
for i in range(100):
    lu = (np.roll(u, 1, axis=0) + np.roll(u, -1, axis=0) + np.roll(u, 1, axis=1) + np.roll(u, -1, axis=1) - 4*u)
    lv = (np.roll(v, 1, axis=0) + np.roll(v, -1, axis=0) + np.roll(v, 1, axis=1) + np.roll(v, -1, axis=1) - 4*v)
    uvv = u * v**2
    u += (0.1 * lu - uvv + 0.04 * (1 - u))
    v += (0.05 * lv + uvv - (0.06 + 0.04) * v)

plt.imshow(v, cmap='hot')
plt.savefig('gs_result.png')
with open('gs_data.json', 'w') as f:
    json.dump(v.tolist(), f)
