"""Aizawa attractor — fast version with all outputs"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

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

a, b, c, d, e, f = 0.95, 0.7, 0.6, 3.5, 0.25, 0.1
dt = 0.01
n_steps = 40000
n_transient = 5000

# Integrate
state = np.array([0.1, 0.0, 0.0])
for _ in range(n_transient):
    state = rk4_step(aizawa_rhs, state, dt, a, b, c, d, e, f)

traj = np.zeros((n_steps, 3))
for i in range(n_steps):
    state = rk4_step(aizawa_rhs, state, dt, a, b, c, d, e, f)
    traj[i] = state

# Lyapunov
state_l = np.array([0.1, 0.0, 0.0])
state2_l = state_l + np.array([1e-8, 0, 0])
d0 = 1e-8
lyap_sum = 0.0
lyap_log = []
for i in range(n_steps):
    state_l = rk4_step(aizawa_rhs, state_l, dt, a, b, c, d, e, f)
    state2_l = rk4_step(aizawa_rhs, state2_l, dt, a, b, c, d, e, f)
    d1 = np.linalg.norm(state2_l - state_l)
    if d1 > 0:
        lyap_sum += np.log(d1 / d0)
        lyap_log.append(lyap_sum / ((i+1) * dt))
        state2_l = state_l + (state2_l - state_l) / d1 * d0
lyap_exp = lyap_sum / (n_steps * dt)
print(f"Lyapunov: {lyap_exp:.4f}")

# Box counting
def box_counting_dim(data, scales=None):
    if scales is None:
        scales = np.logspace(-1.5, 0.5, 20)
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

subsample = traj[::3]
bc_dim, bc_scales, bc_counts = box_counting_dim(subsample)
print(f"Box-counting dim: {bc_dim:.3f}")

# Poincaré section
z_mean = np.mean(traj[:, 2])
poincare_x, poincare_y = [], []
for i in range(1, len(traj)):
    if (traj[i-1, 2] - z_mean) * (traj[i, 2] - z_mean) < 0:
        t_frac = (z_mean - traj[i-1, 2]) / (traj[i, 2] - traj[i-1, 2] + 1e-10)
        px = traj[i-1, 0] + t_frac * (traj[i, 0] - traj[i-1, 0])
        py = traj[i-1, 1] + t_frac * (traj[i, 1] - traj[i-1, 1])
        poincare_x.append(px)
        poincare_y.append(py)

# === Figure 1: Main attractor ===
fig = plt.figure(figsize=(20, 16))
fig.suptitle("Aizawa Attractor: Toroidal Strange Attractor", fontsize=18, fontweight='bold')

n_plot = min(40000, len(traj))
colors = np.linspace(0, 1, n_plot)
cmap = plt.cm.plasma

ax1 = fig.add_subplot(2, 3, (1, 2), projection='3d')
ax1.scatter(traj[:n_plot, 0], traj[:n_plot, 1], traj[:n_plot, 2],
            c=colors, cmap=cmap, s=0.1, alpha=0.4)
ax1.set_xlabel('x'); ax1.set_ylabel('y'); ax1.set_zlabel('z')
ax1.set_title('3D Aizawa Attractor')
ax1.set_facecolor('black')

ax2 = fig.add_subplot(2, 3, 3)
ax2.scatter(traj[:n_plot, 0], traj[:n_plot, 1], c=colors, cmap=cmap, s=0.1, alpha=0.4)
ax2.set_xlabel('x'); ax2.set_ylabel('y')
ax2.set_title('x-y projection'); ax2.set_facecolor('black')

ax3 = fig.add_subplot(2, 3, 4)
ax3.scatter(traj[:n_plot, 0], traj[:n_plot, 2], c=colors, cmap=cmap, s=0.1, alpha=0.4)
ax3.set_xlabel('x'); ax3.set_ylabel('z')
ax3.set_title('x-z projection'); ax3.set_facecolor('black')

ax4 = fig.add_subplot(2, 3, 5)
ax4.scatter(traj[:n_plot, 1], traj[:n_plot, 2], c=colors, cmap=cmap, s=0.1, alpha=0.4)
ax4.set_xlabel('y'); ax4.set_ylabel('z')
ax4.set_title('y-z projection'); ax4.set_facecolor('black')

ax5 = fig.add_subplot(2, 3, 6)
ax5.plot(np.arange(len(lyap_log)) * dt, lyap_log, 'r-', linewidth=0.5, alpha=0.7)
ax5.set_xlabel('Time'); ax5.set_ylabel('λ (convergence)')
ax5.set_title(f'Lyapunov Convergence (λ ≈ {lyap_exp:.3f})')
ax5.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('aizawa_attractor.png', dpi=150, bbox_inches='tight')
print("Saved aizawa_attractor.png")

# === Figure 2: Parameter sweep ===
fig2, axes = plt.subplots(2, 3, figsize=(18, 10))
fig2.suptitle("Aizawa Attractor: Parameter Sensitivity (varying a)", fontsize=16, fontweight='bold')
a_values = [0.5, 0.8, 0.95, 1.1, 1.3, 1.5]
for idx, a_val in enumerate(a_values):
    s = np.array([0.1, 0.0, 0.0])
    for _ in range(3000):
        s = rk4_step(aizawa_rhs, s, dt, a_val, b, c, d, e, f)
    tp = np.zeros((3000, 3))
    for i in range(3000):
        s = rk4_step(aizawa_rhs, s, dt, a_val, b, c, d, e, f)
        tp[i] = s
    ax = axes[idx // 3, idx % 3]
    ax.scatter(tp[:, 0], tp[:, 2], c='cyan', s=0.1, alpha=0.3)
    ax.set_facecolor('black')
    ax.set_title(f'a = {a_val}')
    ax.set_xlabel('x'); ax.set_ylabel('z')
    ax.set_xlim([-2, 2]); ax.set_ylim([-1, 2])
plt.tight_layout()
plt.savefig('aizawa_parameter_sweep.png', dpi=150, bbox_inches='tight')
print("Saved aizawa_parameter_sweep.png")

# === Figure 3: Fractal dimension ===
fig3, ax = plt.subplots(figsize=(8, 5))
ax.loglog(1.0 / np.array(bc_scales), bc_counts, 'ro-', markersize=4)
ax.set_xlabel('1/ε (scale)'); ax.set_ylabel('N(ε) (box count)')
ax.set_title(f'Aizawa Attractor: Box-Counting Dimension D₀ ≈ {bc_dim:.2f}')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('aizawa_fractal_dim.png', dpi=150, bbox_inches='tight')
print("Saved aizawa_fractal_dim.png")

# === Figure 4: Poincaré & time series ===
fig4, axes = plt.subplots(1, 2, figsize=(14, 5))
fig4.suptitle("Aizawa Attractor: Poincaré Section & Time Series", fontsize=14, fontweight='bold')
axes[0].scatter(poincare_x, poincare_y, c='gold', s=2, alpha=0.5)
axes[0].set_facecolor('black')
axes[0].set_xlabel('x'); axes[0].set_ylabel('y')
axes[0].set_title(f'Poincaré section (z = {z_mean:.2f})')
axes[0].set_aspect('equal')
t_plot = np.arange(min(10000, len(traj))) * dt
axes[1].plot(t_plot, traj[:len(t_plot), 0], 'b-', linewidth=0.3, alpha=0.7, label='x(t)')
axes[1].plot(t_plot, traj[:len(t_plot), 2], 'r-', linewidth=0.3, alpha=0.5, label='z(t)')
axes[1].set_xlabel('Time'); axes[1].set_ylabel('State')
axes[1].set_title('Time Series'); axes[1].legend()
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
    "description": "Toroidal strange attractor with self-intersecting spirals forming a funnel/sphere topology. "
                   "One of the most visually striking chaotic systems. Positive Lyapunov exponent confirms chaos.",
    "n_poincare_points": len(poincare_x)
}
with open('aizawa_data.json', 'w') as f_out:
    json.dump(data_out, f_out, indent=2)
print("Saved aizawa_data.json")
print("Done!")
