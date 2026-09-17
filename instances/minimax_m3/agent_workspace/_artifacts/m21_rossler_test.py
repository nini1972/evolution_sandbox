"""M21: Test Rössler attractor band fraction against Adler ceiling."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def rossler_trajectory(a=0.2, b=0.2, c=5.7,
                      x0=1.0, y0=1.0, z0=1.0, dt=0.01, n_steps=20000):
    """Simulate Rössler attractor."""
    xs = np.zeros(n_steps)
    ys = np.zeros(n_steps)
    zs = np.zeros(n_steps)
    x, y, z = x0, y0, z0
    for i in range(n_steps):
        dx = -y - z
        dy = x + a * y
        dz = b + z * (x - c)
        x += dx * dt
        y += dy * dt
        z += dz * dt
        xs[i] = x
        ys[i] = y
        zs[i] = z
    return xs, ys, zs

def band_frac(arr, lo_frac=0.3, hi_frac=0.7):
    lo = arr.min() + lo_frac * (arr.max() - arr.min())
    hi = arr.min() + hi_frac * (arr.max() - arr.min())
    return ((arr >= lo) & (arr <= hi)).mean()

# Rössler canonical: a=0.2, b=0.2, c=5.7
print('Rössler sweep (a=0.2, b=0.2, varying c):')
results = []
for c in [2.0, 3.0, 4.0, 5.0, 5.7, 6.0, 7.0, 8.0, 10.0]:
    xs, ys, zs = rossler_trajectory(c=c, n_steps=20000)
    xs = xs[5000:]
    ys = ys[5000:]
    zs = zs[5000:]
    bf_x = band_frac(xs)
    bf_y = band_frac(ys)
    bf_z = band_frac(zs)
    mean_bf = (bf_x + bf_y + bf_z) / 3
    results.append((c, bf_x, bf_y, bf_z, mean_bf))
    print(f'  c={c}: x={bf_x:.4f}, y={bf_y:.4f}, z={bf_z:.4f}, mean={mean_bf:.4f}')

# Plot
fig, ax = plt.subplots(figsize=(10, 6))
cs = [r[0] for r in results]
for i, label in enumerate(['x', 'y', 'z', 'mean']):
    vals = [r[i+1] for r in results]
    ax.plot(cs, vals, 'o-', linewidth=2, markersize=8, label=label)
ax.axhline(0.414, color='red', linestyle='--', linewidth=2, label='Adler ceiling')
ax.set_xlabel('c (Rössler control parameter)', fontsize=12)
ax.set_ylabel('Band fraction', fontsize=12)
ax.set_title('M21: Rössler Attractor Band Fraction vs c\nChaotic regime: c > 4.0', fontsize=13)
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('_artifacts/m21_rossler_bf.png', dpi=110, bbox_inches='tight')
print('\nSaved m21_rossler_bf.png')

import json
data = {
    'c_sweep': [
        {'c': r[0], 'bf_x': r[1], 'bf_y': r[2], 'bf_z': r[3], 'bf_mean': r[4]}
        for r in results
    ],
    'C_adler': 0.4141546526867628
}
with open('_artifacts/m21_rossler_bf.json', 'w') as f:
    json.dump(data, f, indent=2)
print('Saved m21_rossler_bf.json')