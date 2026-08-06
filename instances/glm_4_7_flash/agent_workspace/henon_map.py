"""
Discovery #006: The Hénon Map
A discrete-time dynamical system that produces a strange attractor.
One of the simplest 2D maps exhibiting chaos, with fractal structure.

x_{n+1} = 1 - a*x_n^2 + y_n
y_{n+1} = b*x_n

Classic parameters: a=1.4, b=0.3
"""
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt

def henon_map(x0, y0, a, b, n):
    xs = np.zeros(n)
    ys = np.zeros(n)
    x, y = x0, y0
    for i in range(n):
        xs[i] = x
        ys[i] = y
        x, y = 1 - a*x*x + y, b*x
    return xs, ys

fig = plt.figure(figsize=(18, 12))

# Panel 1: The Hénon attractor
ax1 = fig.add_subplot(221)
xs, ys = henon_map(0.1, 0.0, 1.4, 0.3, 100000)
ax1.scatter(xs[1000:], ys[1000:], s=0.05, alpha=0.3, c='navy')
ax1.set_title('Hénon Attractor (a=1.4, b=0.3)', fontsize=14, fontweight='bold')
ax1.set_xlabel('X'); ax1.set_ylabel('Y')

# Panel 2: Zoom into the attractor's fractal structure
ax2 = fig.add_subplot(222)
ax2.scatter(xs[1000:], ys[1000:], s=0.02, alpha=0.2, c='darkred')
ax2.set_xlim(-1.3, -1.1)
ax2.set_ylim(0.2, 0.4)
ax2.set_title('Hénon Attractor — Fractal Zoom', fontsize=12)
ax2.set_xlabel('X'); ax2.set_ylabel('Y')

# Panel 3: Effect of parameter a
ax3 = fig.add_subplot(223)
a_values = [1.0, 1.2, 1.4, 1.5, 1.6]
colors_a = ['blue', 'green', 'red', 'purple', 'orange']
for a, col in zip(a_values, colors_a):
    xs_a, ys_a = henon_map(0.1, 0.0, a, 0.3, 50000)
    ax3.scatter(xs_a[5000:], ys_a[5000:], s=0.05, alpha=0.3, c=col, label=f'a={a}')
ax3.set_title('Parameter a Sweep — Transitions', fontsize=12)
ax3.set_xlabel('X'); ax3.set_ylabel('Y')
ax3.legend(fontsize=8)

# Panel 4: Bifurcation diagram of x vs a
ax4 = fig.add_subplot(224)
a_range = np.linspace(1.0, 1.6, 300)
for a in a_range:
    xs_a, ys_a = henon_map(0.1, 0.0, a, 0.3, 2000)
    x = xs_a[1000:]
    # Show all x values as points
    ax4.scatter([a]*len(x), x, s=0.01, c='darkblue', alpha=0.3)
ax4.set_title('Bifurcation Diagram — Hénon Map (b=0.3)', fontsize=12, fontweight='bold')
ax4.set_xlabel('Parameter a')
ax4.set_ylabel('x_n')

plt.tight_layout()
plt.savefig('henon_map.png', dpi=150, bbox_inches='tight')
print("Hénon map saved to henon_map.png")

# Deep fractal zoom — successive zoom levels showing self-similarity
fig2, axes = plt.subplots(1, 4, figsize=(20, 5))
xs, ys = henon_map(0.1, 0.0, 1.4, 0.3, 500000)
xs, ys = xs[1000:], ys[1000:]

zooms = [
    (-1.5, 1.5, -0.5, 0.5),
    (-1.3, -1.1, 0.2, 0.4),
    (-1.25, -1.20, 0.24, 0.29),
    (-1.235, -1.225, 0.250, 0.265),
]
for ax, (xmin, xmax, ymin, ymax) in zip(axes, zooms):
    mask = (xs > xmin) & (xs < xmax) & (ys > ymin) & (ys < ymax)
    ax.scatter(xs[mask], ys[mask], s=0.1, alpha=0.3, c='darkred')
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_title(f'Zoom {xmin:.3f} to {xmax:.3f}', fontsize=10)
    ax.set_xlabel('X'); ax.set_ylabel('Y')

fig2.suptitle('Hénon Attractor — Successive Fractal Zooms (Self-Similarity)', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('henon_fractal_zoom.png', dpi=150, bbox_inches='tight')
print("Fractal zoom saved to henon_fractal_zoom.png")
