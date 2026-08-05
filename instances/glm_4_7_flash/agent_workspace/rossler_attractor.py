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

def rossler_system(state, t, a=0.2, b=0.2, c=5.7):
    x, y, z = state
    dx = -y - z
    dy = x + a * y
    dz = b + z * (x - c)
    return [dx, dy, dz]

def integrate_rk4(f, state, dt, steps, *args):
    trajectory = np.zeros((steps, 3))
    trajectory[0] = state
    for i in range(1, steps):
        k1 = f(state, i*dt, *args)
        k2 = f([s + 0.5*dt*k for s, k in zip(state, k1)], (i+0.5)*dt, *args)
        k3 = f([s + 0.5*dt*k for s, k in zip(state, k2)], (i+0.5)*dt, *args)
        k4 = f([s + dt*k for s, k in zip(state, k3)], (i+1)*dt, *args)
        state = [s + dt/6*(k1[j] + 2*k2[j] + 2*k3[j] + k4[j]) for j, s in enumerate(state)]
        trajectory[i] = state
    return trajectory

# Generate multiple trajectories with slightly different initial conditions
fig = plt.figure(figsize=(18, 12))

# Panel 1: 3D Rössler attractor
ax1 = fig.add_subplot(221, projection='3d')
dt = 0.01
steps = 50000

for x0 in [0.1, 0.5, 1.0, -1.0]:
    traj = integrate_rk4(rossler_system, [x0, 0.0, 0.0], dt, steps)
    # Skip transient
    traj = traj[5000:]
    ax1.plot(traj[:, 0], traj[:, 1], traj[:, 2], linewidth=0.3, alpha=0.6, label=f'x₀={x0}')

ax1.set_title('Rössler Attractor — The Folded Ribbon', fontsize=14, fontweight='bold')
ax1.set_xlabel('X')
ax1.set_ylabel('Y')
ax1.set_zlabel('Z')
ax1.legend(fontsize=8)

# Panel 2: XY projection
ax2 = fig.add_subplot(222)
for x0 in [0.1, 0.5, 1.0]:
    traj = integrate_rk4(rossler_system, [x0, 0.0, 0.0], dt, steps)
    traj = traj[5000:]
    ax2.scatter(traj[:, 0], traj[:, 1], s=0.1, alpha=0.3, c=traj[:, 2], cmap='plasma')
ax2.set_title('XY Projection (colored by Z)', fontsize=12)
ax2.set_xlabel('X')
ax2.set_ylabel('Y')

# Panel 3: Effect of parameter c on dynamics
ax3 = fig.add_subplot(223)
c_values = [2.0, 3.0, 4.0, 5.0, 5.7, 6.0, 7.0, 8.0, 9.0, 10.0]
for c in c_values:
    traj = integrate_rk4(rossler_system, [1.0, 0.0, 0.0], dt, steps, 0.2, 0.2, c)
    traj = traj[20000:]
    ax3.plot(traj[:, 0], traj[:, 1], linewidth=0.2, alpha=0.5, label=f'c={c}')

ax3.set_title('Parameter c Sweep — Route to Chaos', fontsize=12)
ax3.set_xlabel('X')
ax3.set_ylabel('Y')
ax3.legend(fontsize=7, ncol=2)

# Panel 4: Bifurcation diagram - local maxima of x vs c
ax4 = fig.add_subplot(224)
c_range = np.linspace(2.0, 10.0, 300)
for c in c_range:
    traj = integrate_rk4(rossler_system, [1.0, 0.0, 0.0], dt, 30000, 0.2, 0.2, c)
    traj = traj[15000:]  # skip transient
    x = traj[:, 0]
    # Find local maxima
    maxima = x[1:-1][(x[1:-1] > x[:-2]) & (x[1:-1] > x[2:])]
    ax4.scatter([c]*len(maxima), maxima, s=0.05, c='darkred', alpha=0.5)

ax4.set_title('Bifurcation Diagram — Rössler Route to Chaos', fontsize=12, fontweight='bold')
ax4.set_xlabel('Parameter c')
ax4.set_ylabel('Local maxima of x')

plt.tight_layout()
plt.savefig('rossler_attractor.png', dpi=150, bbox_inches='tight')
print("Rössler attractor saved to rossler_attractor.png")

# Also save a deep zoom into the chaotic regime
fig2 = plt.figure(figsize=(10, 8))
ax = fig2.add_subplot(111, projection='3d')
traj = integrate_rk4(rossler_system, [1.0, 0.0, 0.0], dt, 100000)
traj = traj[20000:]
# Color by time gradient
colors = np.arange(len(traj)) / len(traj)
ax.scatter(traj[:, 0], traj[:, 1], traj[:, 2], c=colors, cmap='inferno', s=0.3, alpha=0.5)
ax.set_title('Rössler Attractor — Deep View (100k steps, time-colored)', fontsize=14, fontweight='bold')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
plt.savefig('rossler_deep_view.png', dpi=150, bbox_inches='tight')
print("Deep view saved to rossler_deep_view.png")
