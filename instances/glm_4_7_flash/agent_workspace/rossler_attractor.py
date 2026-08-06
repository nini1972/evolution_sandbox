"""
Discovery #005: The Rössler Attractor
A simpler strange attractor than Lorenz, with a single nonlinear term.
Known for its "folded ribbon" topology and simpler chaos generation.
"""
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def rossler_rk4(x0, y0, z0, dt, steps, a=0.2, b=0.2, c=5.7):
    """Vectorized RK4 integration of the Rössler system."""
    xs = np.zeros(steps)
    ys = np.zeros(steps)
    zs = np.zeros(steps)
    x, y, z = x0, y0, z0
    for i in range(steps):
        xs[i] = x; ys[i] = y; zs[i] = z
        # k1
        k1x = -y - z
        k1y = x + a*y
        k1z = b + z*(x - c)
        # k2
        x2 = x + 0.5*dt*k1x; y2 = y + 0.5*dt*k1y; z2 = z + 0.5*dt*k1z
        k2x = -y2 - z2
        k2y = x2 + a*y2
        k2z = b + z2*(x2 - c)
        # k3
        x3 = x + 0.5*dt*k2x; y3 = y + 0.5*dt*k2y; z3 = z + 0.5*dt*k2z
        k3x = -y3 - z3
        k3y = x3 + a*y3
        k3z = b + z3*(x3 - c)
        # k4
        x4 = x + dt*k3x; y4 = y + dt*k3y; z4 = z + dt*k3z
        k4x = -y4 - z4
        k4y = x4 + a*y4
        k4z = b + z4*(x4 - c)
        x += dt/6*(k1x + 2*k2x + 2*k3x + k4x)
        y += dt/6*(k1y + 2*k2y + 2*k3y + k4y)
        z += dt/6*(k1z + 2*k2z + 2*k3z + k4z)
    return xs, ys, zs

dt = 0.01
steps = 20000

fig = plt.figure(figsize=(18, 12))

# Panel 1: 3D Rössler attractor
ax1 = fig.add_subplot(221, projection='3d')
for x0 in [0.1, 0.5, 1.0, -1.0]:
    xs, ys, zs = rossler_rk4(x0, 0.0, 0.0, dt, steps)
    s = 2000
    ax1.plot(xs[s:], ys[s:], zs[s:], linewidth=0.3, alpha=0.6, label=f'x₀={x0}')
ax1.set_title('Rössler Attractor — The Folded Ribbon', fontsize=14, fontweight='bold')
ax1.set_xlabel('X'); ax1.set_ylabel('Y'); ax1.set_zlabel('Z')
ax1.legend(fontsize=8)

# Panel 2: XY projection colored by Z
ax2 = fig.add_subplot(222)
xs, ys, zs = rossler_rk4(1.0, 0.0, 0.0, dt, steps)
s = 2000
ax2.scatter(xs[s:], ys[s:], s=0.2, alpha=0.4, c=zs[s:], cmap='plasma')
ax2.set_title('XY Projection (colored by Z)', fontsize=12)
ax2.set_xlabel('X'); ax2.set_ylabel('Y')

# Panel 3: Parameter c sweep
ax3 = fig.add_subplot(223)
for c in [2.0, 3.0, 4.0, 5.0, 5.7, 6.0, 7.0, 8.0, 9.0, 10.0]:
    xs, ys, zs = rossler_rk4(1.0, 0.0, 0.0, dt, steps, c=c)
    s = 10000
    ax3.plot(xs[s:], ys[s:], linewidth=0.2, alpha=0.5, label=f'c={c}')
ax3.set_title('Parameter c Sweep — Route to Chaos', fontsize=12)
ax3.set_xlabel('X'); ax3.set_ylabel('Y')
ax3.legend(fontsize=7, ncol=2)

# Panel 4: Bifurcation diagram (reduced c range for speed)
ax4 = fig.add_subplot(224)
c_values = np.linspace(2.0, 10.0, 100)
for c in c_values:
    xs, ys, zs = rossler_rk4(1.0, 0.0, 0.0, dt, 10000, c=c)
    x = xs[5000:]
    maxima = x[1:-1][(x[1:-1] > x[:-2]) & (x[1:-1] > x[2:])]
    ax4.scatter([c]*len(maxima), maxima, s=0.05, c='darkred', alpha=0.5)
ax4.set_title('Bifurcation Diagram — Rössler Route to Chaos', fontsize=12, fontweight='bold')
ax4.set_xlabel('Parameter c')
ax4.set_ylabel('Local maxima of x')

plt.tight_layout()
plt.savefig('rossler_attractor.png', dpi=150, bbox_inches='tight')
print("Rössler attractor saved to rossler_attractor.png")

# Deep view
fig2 = plt.figure(figsize=(10, 8))
ax = fig2.add_subplot(111, projection='3d')
xs, ys, zs = rossler_rk4(1.0, 0.0, 0.0, dt, 40000)
s = 5000
traj_x, traj_y, traj_z = xs[s:], ys[s:], zs[s:]
colors = np.arange(len(traj_x)) / len(traj_x)
ax.scatter(traj_x, traj_y, traj_z, c=colors, cmap='inferno', s=0.3, alpha=0.5)
ax.set_title('Rössler Attractor — Deep View (time-colored)', fontsize=14, fontweight='bold')
ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')
plt.savefig('rossler_deep_view.png', dpi=150, bbox_inches='tight')
print("Deep view saved to rossler_deep_view.png")
