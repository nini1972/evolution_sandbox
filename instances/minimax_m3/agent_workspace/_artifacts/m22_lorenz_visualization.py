"""M22: Visualize why Lorenz attractor has concentrated invariant measure."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LogNorm

def lorenz_trajectory(sigma=10.0, rho=28.0, beta=8.0/3.0,
                     x0=1.0, y0=1.0, z0=1.0, dt=0.005, n_steps=100000):
    """Long Lorenz simulation for good statistics."""
    xs = np.zeros(n_steps)
    ys = np.zeros(n_steps)
    zs = np.zeros(n_steps)
    x, y, z = x0, y0, z0
    for i in range(n_steps):
        dx = sigma * (y - x)
        dy = x * (rho - z) - y
        dz = x * y - beta * z
        x += dx * dt
        y += dy * dt
        z += dz * dt
        xs[i] = x
        ys[i] = y
        zs[i] = z
    return xs, ys, zs

xs, ys, zs = lorenz_trajectory(n_steps=100000)
xs = xs[5000:]
ys = ys[5000:]
zs = zs[5000:]

fig, axes = plt.subplots(2, 2, figsize=(14, 12))

# 1. XY projection with density
ax = axes[0, 0]
H, xedges, yedges = np.histogram2d(xs, ys, bins=80)
ax.imshow(H.T, origin='lower', extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]],
          cmap='hot', aspect='auto', norm=LogNorm())
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_title('Lorenz (xy projection)\nlog-density of trajectory', fontsize=11)

# 2. YZ projection with density
ax = axes[0, 1]
H, yedges, zedges = np.histogram2d(ys, zs, bins=80)
ax.imshow(H.T, origin='lower', extent=[yedges[0], yedges[-1], zedges[0], zedges[-1]],
          cmap='hot', aspect='auto', norm=LogNorm())
ax.set_xlabel('y')
ax.set_ylabel('z')
ax.set_title('Lorenz (yz projection)\nlog-density of trajectory', fontsize=11)

# 3. Marginal distributions with bands
ax = axes[1, 0]
for i, (arr, name) in enumerate(zip([xs, ys, zs], ['x', 'y', 'z'])):
    lo = arr.min()
    hi = arr.max()
    mid_lo = lo + 0.3 * (hi - lo)
    mid_hi = lo + 0.7 * (hi - lo)
    n, bins, _ = ax.hist(arr, bins=100, alpha=0.5, label=f'{name} (bf={((arr>=mid_lo)&(arr<=mid_hi)).mean():.3f})',
                          density=True)
    ax.axvspan(mid_lo, mid_hi, alpha=0.15, color=f'C{i}')
ax.set_xlabel('value')
ax.set_ylabel('density')
ax.set_title('Lorenz marginal distributions\n(shading = "middle band" [0.3, 0.7] of range)', fontsize=11)
ax.legend(fontsize=10)

# 4. Band fraction by axis position
ax = axes[1, 1]
labels = ['x', 'y', 'z']
data = [xs, ys, zs]
fracs = []
total = []
mid_fracs = []
for arr in data:
    lo = arr.min()
    hi = arr.max()
    mid_lo = lo + 0.3 * (hi - lo)
    mid_hi = lo + 0.7 * (hi - lo)
    bf = ((arr >= mid_lo) & (arr <= mid_hi)).mean()
    fracs.append(bf)
    mid_fracs.append(0.4)  # uniform would give 0.4

x_pos = np.arange(len(labels))
width = 0.35
ax.bar(x_pos - width/2, fracs, width, label='Lorenz bf', color='C0')
ax.bar(x_pos + width/2, mid_fracs, width, label='uniform expectation', color='gray', alpha=0.5)
ax.axhline(0.414, color='red', linestyle='--', label='Adler ceiling')
ax.set_xticks(x_pos)
ax.set_xticklabels(labels)
ax.set_ylabel('band fraction')
ax.set_title('M22: Lorenz bf > ceiling for x,y,z\n(uniform would give 0.40)', fontsize=11)
ax.legend()
ax.grid(True, alpha=0.3)

plt.suptitle('M22: Why Lorenz Exceeds the Adler Ceiling — Invariant Measure Concentration',
             fontsize=14, y=1.00)
plt.tight_layout()
plt.savefig('_artifacts/m22_lorenz_visualization.png', dpi=110, bbox_inches='tight')
print('Saved m22_lorenz_visualization.png')

# Print statistics
print(f'\nLorenz statistics:')
print(f'  x: range [{xs.min():.2f}, {xs.max():.2f}], mean={xs.mean():.2f}')
print(f'  y: range [{ys.min():.2f}, {ys.max():.2f}], mean={ys.mean():.2f}')
print(f'  z: range [{zs.min():.2f}, {zs.max():.2f}], mean={zs.mean():.2f}')
print(f'\nBand fractions:')
for i, name in enumerate(['x', 'y', 'z']):
    arr = [xs, ys, zs][i]
    bf = fracs[i]
    lo = arr.min()
    hi = arr.max()
    print(f'  {name}: bf={bf:.4f}, R={bf/0.4142:.3f}× ceiling')