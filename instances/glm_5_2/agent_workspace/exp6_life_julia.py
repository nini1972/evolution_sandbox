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

def julia_set(cx, cy, width=300, height=300, max_iter=80):
    x = np.linspace(-1.5, 1.5, width)
    y = np.linspace(-1.5, 1.5, height)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y
    c = cx + 1j * cy
    img = np.zeros((height, width))
    for i in range(max_iter):
        mask = np.abs(Z) < 2
        Z[mask] = Z[mask]**2 + c
        img[mask] = i
    return img

time_points = [10, 50, 100, 150, 199]
fig, axes = plt.subplots(1, 5, figsize=(25, 5))
for idx, tp in enumerate(time_points):
    c = c_values[tp]
    jimg = julia_set(c.real, c.imag, 200, 200, 60)
    axes[idx].imshow(jimg, cmap='magma', extent=[-1.5,1.5,-1.5,1.5])
    axes[idx].set_title('t=%d pop=%d\nc=%.3f%+.3fi' % (tp, populations[tp], c.real, c.imag), fontsize=9)
    axes[idx].axis('off')

fig.suptitle('R6: Game of Life Population -> Julia Set Parameter', fontsize=14, color='white')
plt.tight_layout()
plt.savefig('resonance_life_julia.png', dpi=120, bbox_inches='tight', facecolor='#0a0a12')
print("Saved resonance_life_julia.png")
