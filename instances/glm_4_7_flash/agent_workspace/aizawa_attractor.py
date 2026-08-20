"""
Aizawa Attractor — A Three-Dimensional Strange Attractor with Toroidal Topology
===============================================================================
Equations:
  dx/dt = (z - b) * x - d * y
  dy/dt = d * x + (z - b) * y
  dz/dt = c + a*z - z^3/3 - (x^2 + y^2)*(1 + e*z) + f*z*x^3

Classic parameters: a=0.95, b=3.6, c=0.6, d=1.0, e=0.25, f=0.1

The Aizawa attractor has a distinctive funnel/torus-like shape with
self-intersecting spirals, making it one of the most visually striking
strange attractors. It exhibits sensitive dependence on initial conditions
and has a complex basin structure.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import json, os

# --- Aizawa ODE ---
def aizawa_rhs(state, a, b, c, d, e, f):
    x, y, z = state
    dx = (z - b) * x - d * y
    dy = d * x + (z - b) * y
    dz = c + a * z - z**3 / 3.0 - (x**2 + y**2) * (1 + e * z) + f * z * x**3
    return np.array([dx, dy, dz])

def rk4_step(f, state, dt, *params):
    k1 = f(state, *params)
    k2 = f(state + 0.5 * dt * k1, *params)
    k3 = f(state + 0.5 * dt * k2, *params)
    k4 = f(state + dt * k3, *params)
    return state + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)

# --- Parameters ---
a, b, c, d, e, f = 0.95, 0.7, 0.6, 3.5, 0.25, 0.1
dt = 0.01
n_steps = 80000
n_transient = 10000

# --- Integrate ---
state = np.array([0.1, 0.0, 0.0])
traj_transient = []
for i in range(n_transient):
    state = rk4_step(aizawa_rhs, state, dt, a, b, c, d, e, f)

traj = np.zeros((n_steps, 3))
state2 = state + np.array([1e-8, 0, 0])  # nearby for Lyapunov
traj2 = np.zeros((n_steps, 3))
divergence = np.zeros(n_steps)

for i in range(n_steps):
    state = rk4_step(aizawa_rhs, state, dt, a, b, c, d, e, f)
    state2 = rk4_step(aizawa_rhs, state2, dt, a, b, c, d, e, f)
    traj[i] = state
    traj2[i] = state2
    divergence[i] = np.linalg.norm(state2 - state)
    # Renormalize to prevent overflow
    if divergence[i] > 1e-3:
        state2 = state + (state2 - state) / divergence[i] * 1e-8
        divergence[i] = 1e-8  # reset for continuous measurement

# --- Lyapunov exponent via continuous renormalization ---
# Instead, use the average log growth rate approach
lyap_sum = 0.0
lyap_count = 0
state = np.array([0.1, 0.0, 0.0])
state2 = state + np.array([1e-8, 0, 0])
d0 = 1e-8
lyap_log = []
for i in range(n_steps):
    state = rk4_step(aizawa_rhs, state, dt, a, b, c, d, e, f)
    state2 = rk4_step(aizawa_rhs, state2, dt, a, b, c, d, e, f)
    d1 = np.linalg.norm(state2 - state)
    if d1 > 0:
        lyap_sum += np.log(d1 / d0)
        lyap_count += 1
        lyap_log.append(lyap_sum / (lyap_count * dt))
        state2 = state + (state2 - state) / d1 * d0
lyap_exp = lyap_sum / (lyap_count * dt)

print(f"Aizawa Attractor — Largest Lyapunov exponent: {lyap_exp:.4f} / time unit")
print(f"State range: x=[{traj[:,0].min():.2f}, {traj[:,0].max():.2f}], "
      f"y=[{traj[:,1].min():.2f}, {traj[:,1].max():.2f}], "
      f"z=[{traj[:,2].min():.2f}, {traj[:,2].max():.2f}]")

# === Figure 1: Aizawa attractor visualizations ===
fig = plt.figure(figsize=(20, 16))
fig.suptitle("Aizawa Attractor: Toroidal Strange Attractor", fontsize=18, fontweight='bold')

n_plot = min(60000, len(traj))
# Color by time gradient
colors = np.linspace(0, 1, n_plot)
cmap = plt.cm.plasma

# 3D view
ax1 = fig.add_subplot(2, 3, (1, 2), projection='3d')
ax1.scatter(traj[:n_plot, 0], traj[:n_plot, 1], traj[:n_plot, 2],
            c=colors, cmap=cmap, s=0.1, alpha=0.4)
ax1.set_xlabel('x')
ax1.set_ylabel('y')
ax1.set_zlabel('z')
ax1.set_title('3D Aizawa Attractor')
ax1.set_facecolor('black')

# x-y projection
ax2 = fig.add_subplot(2, 3, 3)
ax2.scatter(traj[:n_plot, 0], traj[:n_plot, 1], c=colors, cmap=cmap, s=0.1, alpha=0.4)
ax2.set_xlabel('x')
ax2.set_ylabel('y')
ax2.set_title('x-y projection')
ax2.set_facecolor('black')

# x-z projection
ax3 = fig.add_subplot(2, 3, 4)
ax3.scatter(traj[:n_plot, 0], traj[:n_plot, 2], c=colors, cmap=cmap, s=0.1, alpha=0.4)
ax3.set_xlabel('x')
ax3.set_ylabel('z')
ax3.set_title('x-z projection')
ax3.set_facecolor('black')

# y-z projection
ax4 = fig.add_subplot(2, 3, 5)
ax4.scatter(traj[:n_plot, 1], traj[:n_plot, 2], c=colors, cmap=cmap, s=0.1, alpha=0.4)
ax4.set_xlabel('y')
ax4.set_ylabel('z')
ax4.set_title('y-z projection')
ax4.set_facecolor('black')

# Lyapunov convergence
ax5 = fig.add_subplot(2, 3, 6)
ax5.plot(np.arange(len(lyap_log)) * dt, lyap_log, 'r-', linewidth=0.5, alpha=0.7)
ax5.set_xlabel('Time')
ax5.set_ylabel('λ (convergence)')
ax5.set_title(f'Lyapunov Convergence (λ ≈ {lyap_exp:.3f})')
ax5.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('aizawa_attractor.png', dpi=150, bbox_inches='tight')
print("Saved aizawa_attractor.png")

# === Figure 2: Parameter sensitivity ===
fig2, axes = plt.subplots(2, 3, figsize=(18, 10))
fig2.suptitle("Aizawa Attractor: Parameter Sensitivity & Time Series", fontsize=16, fontweight='bold')

# Vary 'a' parameter
a_values = [0.5, 0.8, 0.95, 1.1, 1.3, 1.5]
for idx, a_val in enumerate(a_values):
    s = np.array([0.1, 0.0, 0.0])
    for _ in range(5000):
        s = rk4_step(aizawa_rhs, s, dt, a_val, b, c, d, e, f)
    traj_param = np.zeros((5000, 3))
    for i in range(5000):
        s = rk4_step(aizawa_rhs, s, dt, a_val, b, c, d, e, f)
        traj_param[i] = s
    ax = axes[idx // 3, idx % 3]
    ax.scatter(traj_param[:, 0], traj_param[:, 2], c='cyan', s=0.1, alpha=0.3)
    ax.set_facecolor('black')
    ax.set_title(f'a = {a_val}')
    ax.set_xlabel('x')
    ax.set_ylabel('z')
    ax.set_xlim([-3, 3])
    ax.set_ylim([-2, 3])

plt.tight_layout()
plt.savefig('aizawa_parameter_sweep.png', dpi=150, bbox_inches='tight')
print("Saved aizawa_parameter_sweep.png")

# === Box-counting dimension ===
def box_counting_dim(data, scales=None):
    if scales is None:
        scales = np.logspace(-1.5, 0.5, 25)
    d_min = data.min(axis=0)
    d_range = data.max(axis=0) - d_min + 1e-10
    counts = []
    for eps in scales:
        idx = ((data - d_min) / d_range / eps).astype(int)
        boxes = set(map(tuple, idx))
        counts.append(len(boxes))
    log_scales = np.log(1.0 / np.array(scales))
    log_counts = np.log(np.array(counts))
    valid = np.isfinite(log_scales) & np.isfinite(log_counts) & (np.array(counts) > 1)
    if np.sum(valid) > 2:
        coeffs = np.polyfit(log_scales[valid], log_counts[valid], 1)
        return coeffs[0], scales, counts
    return 0.0, scales, counts

subsample = traj[::5]
bc_dim, bc_scales, bc_counts = box_counting_dim(subsample)
print(f"Box-counting dimension: {bc_dim:.3f}")

fig3, ax = plt.subplots(figsize=(8, 5))
ax.loglog(1.0 / np.array(bc_scales), bc_counts, 'ro-', markersize=4)
ax.set_xlabel('1/ε (scale)')
ax.set_ylabel('N(ε) (box count)')
ax.set_title(f'Aizawa Attractor: Box-Counting Dimension D₀ ≈ {bc_dim:.2f}')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('aizawa_fractal_dim.png', dpi=150, bbox_inches='tight')
print("Saved aizawa_fractal_dim.png")

# === Poincaré section at z=0 ===
fig4, axes = plt.subplots(1, 2, figsize=(14, 5))
fig4.suptitle("Aizawa Attractor: Poincaré Section & Time Series", fontsize=14, fontweight='bold')

# Poincaré section: crossings of z = average(z)
z_mean = np.mean(traj[:, 2])
poincare_x = []
poincare_y = []
for i in range(1, len(traj)):
    if (traj[i-1, 2] - z_mean) * (traj[i, 2] - z_mean) < 0:
        # Linear interpolation
        t_frac = (z_mean - traj[i-1, 2]) / (traj[i, 2] - traj[i-1, 2] + 1e-10)
        px = traj[i-1, 0] + t_frac * (traj[i, 0] - traj[i-1, 0])
        py = traj[i-1, 1] + t_frac * (traj[i, 1] - traj[i-1, 1])
        poincare_x.append(px)
        poincare_y.append(py)

axes[0].scatter(poincare_x, poincare_y, c='gold', s=2, alpha=0.5)
axes[0].set_facecolor('black')
axes[0].set_xlabel('x')
axes[0].set_ylabel('y')
axes[0].set_title(f'Poincaré section (z = {z_mean:.2f})')
axes[0].set_aspect('equal')

# Time series
t_plot = np.arange(min(10000, len(traj))) * dt
axes[1].plot(t_plot, traj[:len(t_plot), 0], 'b-', linewidth=0.3, alpha=0.7, label='x(t)')
axes[1].plot(t_plot, traj[:len(t_plot), 2], 'r-', linewidth=0.3, alpha=0.5, label='z(t)')
axes[1].set_xlabel('Time')
axes[1].set_ylabel('State')
axes[1].set_title('Time Series')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('aizawa_poincare_timeseries.png', dpi=150, bbox_inches='tight')
print("Saved aizawa_poincare_timeseries.png")

# === Save data ===
data_out = {
    "system": "Aizawa Attractor",
    "equations": "dx/dt=(z-b)*x-d*y, dy/dt=d*x+(z-b)*y, dz/dt=c+a*z-z^3/3-(x^2+y^2)*(1+e*z)+f*z*x^3",
    "parameters": {"a": a, "b": b, "c": c, "d": d, "e": e, "f": f},
    "lyapunov_exponent": float(lyap_exp),
    "box_counting_dimension": float(bc_dim),
    "description": "Toroidal strange attractor with self-intersecting spirals. "
                   "Distinctive funnel-like topology, visually one of the most striking chaotic systems. "
                   "Exhibits complex basin structure and sensitive dependence on initial conditions.",
    "n_poincare_points": len(poincare_x)
}
with open('aizawa_data.json', 'w') as f_out:
    json.dump(data_out, f_out, indent=2)
print("Saved aizawa_data.json")
print("Done!")
