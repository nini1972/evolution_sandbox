"""
Chua's Circuit — The Simplest Electronic Chaos Generator
========================================================
Equations:
  dx/dt = alpha * (y - x - f(x))
  dy/dt = x - y + z
  dz/dt = -beta * y

where f(x) = m1*x + 0.5*(m0 - m1)*(|x+1| - |x-1|)

Classic parameters: alpha=15.6, beta=28.0, m0=-1.143, m1=-0.714
This produces the "double scroll" strange attractor.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json, os

# --- Chua's circuit ODE ---
def chua_rhs(state, alpha, beta, m0, m1):
    x, y, z = state
    f = m1 * x + 0.5 * (m0 - m1) * (abs(x + 1) - abs(x - 1))
    dx = alpha * (y - x - f)
    dy = x - y + z
    dz = -beta * y
    return np.array([dx, dy, dz])

def rk4_step(f, state, dt, *params):
    k1 = f(state, *params)
    k2 = f(state + 0.5*dt*k1, *params)
    k3 = f(state + 0.5*dt*k2, *params)
    k4 = f(state + dt*k3, *params)
    return state + (dt/6.0) * (k1 + 2*k2 + 2*k3 + k4)

# --- Parameters ---
alpha, beta = 15.6, 28.0
m0, m1 = -1.143, -0.714
dt = 0.005
n_steps = 120000
n_transient = 20000

# --- Integrate from two nearby initial conditions ---
state1 = np.array([0.1, 0.0, 0.0])
state2 = np.array([0.1 + 1e-8, 0.0, 0.0])

traj1 = np.zeros((n_steps, 3))
traj2 = np.zeros((n_steps, 3))
divergence = np.zeros(n_steps)

for i in range(n_steps):
    state1 = rk4_step(chua_rhs, state1, dt, alpha, beta, m0, m1)
    state2 = rk4_step(chua_rhs, state2, dt, alpha, beta, m0, m1)
    traj1[i] = state1
    traj2[i] = state2
    divergence[i] = np.linalg.norm(state2 - state1)

# --- Lyapunov exponent (largest) from divergence ---
mask = (divergence > 1e-20) & (divergence < 1e0)
t_arr = np.arange(n_steps) * dt
if np.any(mask):
    log_div = np.log(divergence[mask] + 1e-30)
    t_masked = t_arr[mask]
    # Fit line to log(div) vs t in the exponential growth regime
    from numpy.polynomial import polynomial as P
    coeffs = np.polyfit(t_masked[:5000], log_div[:5000], 1)
    lyap_exp = coeffs[0]
else:
    lyap_exp = 0.0

# --- Trajectory data ---
traj = traj1[n_transient:]
print(f"Largest Lyapunov exponent: {lyap_exp:.4f} / time unit")
print(f"State range: x=[{traj[:,0].min():.2f}, {traj[:,0].max():.2f}], "
      f"y=[{traj[:,1].min():.2f}, {traj[:,1].max():.2f}], "
      f"z=[{traj[:,2].min():.2f}, {traj[:,2].max():.2f}]")

# === Figure 1: Double-scroll attractor (3 projections + 3D) ===
fig = plt.figure(figsize=(18, 14))
fig.suptitle("Chua's Circuit: Double-Scroll Strange Attractor", fontsize=18, fontweight='bold')

# Color by time for visual flow
n_plot = min(80000, len(traj))
colors = np.linspace(0, 1, n_plot)

ax1 = fig.add_subplot(2, 3, 1)
ax1.scatter(traj[:n_plot, 0], traj[:n_plot, 1], c=colors, cmap='inferno', s=0.1, alpha=0.5)
ax1.set_xlabel('x (capacitor C1)')
ax1.set_ylabel('y (capacitor C2)')
ax1.set_title('x-y projection (Double Scroll)')
ax1.set_facecolor('black')

ax2 = fig.add_subplot(2, 3, 2)
ax2.scatter(traj[:n_plot, 0], traj[:n_plot, 2], c=colors, cmap='inferno', s=0.1, alpha=0.5)
ax2.set_xlabel('x')
ax2.set_ylabel('z (inductor current)')
ax2.set_title('x-z projection')
ax2.set_facecolor('black')

ax3 = fig.add_subplot(2, 3, 3)
ax3.scatter(traj[:n_plot, 1], traj[:n_plot, 2], c=colors, cmap='inferno', s=0.1, alpha=0.5)
ax3.set_xlabel('y')
ax3.set_ylabel('z')
ax3.set_title('y-z projection')
ax3.set_facecolor('black')

# 3D view
ax4 = fig.add_subplot(2, 3, (4,6), projection='3d')
ax4.scatter(traj[:n_plot, 0], traj[:n_plot, 1], traj[:n_plot, 2], 
            c=colors, cmap='inferno', s=0.05, alpha=0.3)
ax4.set_xlabel('x')
ax4.set_ylabel('y')
ax4.set_zlabel('z')
ax4.set_title('3D Double-Scroll Attractor')
ax4.set_facecolor('black')

# Lyapunov divergence plot
ax5 = fig.add_subplot(2, 3, 5)
mask_lyap = (divergence > 1e-20) & (divergence < 1e-2)
ax5.semilogy(t_arr[mask_lyap], divergence[mask_lyap], 'r-', linewidth=0.5, alpha=0.7)
ax5.set_xlabel('Time')
ax5.set_ylabel('|δ(t)| (log scale)')
ax5.set_title(f'Trajectory Divergence (λ = {lyap_exp:.3f})')
ax5.grid(True, alpha=0.3)
ax5.axhline(y=1e-8, color='g', linestyle='--', alpha=0.5, label='initial sep')
ax5.legend()

plt.tight_layout()
plt.savefig('chua_double_scroll.png', dpi=150, bbox_inches='tight')
print("Saved chua_double_scroll.png")

# === Figure 2: Nonlinearity and bifurcation ===
fig2, axes = plt.subplots(1, 3, figsize=(18, 5))
fig2.suptitle("Chua's Circuit: Nonlinearity & Parameter Dependence", fontsize=16, fontweight='bold')

# Piecewise linear resistor characteristic
x_curve = np.linspace(-3, 3, 1000)
f_curve = m1 * x_curve + 0.5 * (m0 - m1) * (np.abs(x_curve + 1) - np.abs(x_curve - 1))
axes[0].plot(x_curve, f_curve, 'r-', linewidth=2)
axes[0].set_xlabel('x')
axes[0].set_ylabel('f(x) = I_NL')
axes[0].set_title('Chua Diode: Piecewise-Linear Nonlinearity')
axes[0].grid(True, alpha=0.3)
axes[0].axhline(y=0, color='k', linewidth=0.5)
axes[0].axvline(x=0, color='k', linewidth=0.5)

# Bifurcation: vary alpha
alpha_range = np.linspace(8.0, 18.0, 100)
bif_data = []
for a in alpha_range:
    s = np.array([0.1, 0.0, 0.0])
    for _ in range(5000):
        s = rk4_step(chua_rhs, s, dt, a, beta, m0, m1)
    for _ in range(2000):
        s = rk4_step(chua_rhs, s, dt, a, beta, m0, m1)
        # Poincare section: y crossing zero
        s_prev = s.copy()
        s = rk4_step(chua_rhs, s, dt, a, beta, m0, m1)
        if s_prev[1] * s[1] < 0 and s[0] > 0:  # y crosses zero, x>0
            bif_data.append((a, s[0]))

if bif_data:
    bif_arr = np.array(bif_data)
    axes[1].scatter(bif_arr[:, 0], bif_arr[:, 1], s=0.5, c='blue', alpha=0.5)
axes[1].set_xlabel('α (parameter)')
axes[1].set_ylabel('x at Poincaré section')
axes[1].set_title('Bifurcation Diagram (vary α)')
axes[1].grid(True, alpha=0.3)

# Time series
t_plot = np.arange(min(10000, len(traj1))) * dt
axes[2].plot(t_plot, traj1[:len(t_plot), 0], 'b-', linewidth=0.3, alpha=0.7)
axes[2].set_xlabel('Time')
axes[2].set_ylabel('x(t)')
axes[2].set_title('Time Series: Chaotic Oscillation')
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('chua_bifurcation.png', dpi=150, bbox_inches='tight')
print("Saved chua_bifurcation.png")

# === Box-counting dimension of attractor ===
def box_counting_dim(data, scales=None):
    """Estimate box-counting dimension from 3D data."""
    if scales is None:
        scales = np.logspace(-2, 0, 20)
    d_min = data.min(axis=0)
    d_range = data.max(axis=0) - d_min + 1e-10
    
    counts = []
    for eps in scales:
        boxes = set()
        for pt in data[::10]:  # subsample for speed
            idx = tuple(((pt - d_min) / d_range / eps).astype(int))
            boxes.add(idx)
        counts.append(len(boxes))
    
    log_scales = np.log(1.0 / scales)
    log_counts = np.log(counts)
    valid = np.isfinite(log_scales) & np.isfinite(log_counts) & (np.array(counts) > 0)
    if np.sum(valid) > 2:
        coeffs = np.polyfit(log_scales[valid], log_counts[valid], 1)
        return coeffs[0], scales, counts
    return 0.0, scales, counts

# Subsample for speed
subsample = traj[::5]
bc_dim, bc_scales, bc_counts = box_counting_dim(subsample)
print(f"Box-counting dimension: {bc_dim:.3f}")

# === Save summary ===
fig3, ax = plt.subplots(figsize=(8, 5))
ax.loglog(1.0/np.array(bc_scales), bc_counts, 'ro-', markersize=4)
ax.set_xlabel('1/ε (scale)')
ax.set_ylabel('N(ε) (box count)')
ax.set_title(f'Box-Counting Dimension: D₀ ≈ {bc_dim:.2f}')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('chua_fractal_dim.png', dpi=150, bbox_inches='tight')
print("Saved chua_fractal_dim.png")

# === Save data ===
data_out = {
    "system": "Chua's Circuit",
    "equations": "dx/dt=alpha(y-x-f(x)), dy/dt=x-y+z, dz/dt=-beta*y",
    "nonlinearity": "piecewise linear: f(x)=m1*x+0.5*(m0-m1)*(|x+1|-|x-1|)",
    "parameters": {"alpha": alpha, "beta": beta, "m0": m0, "m1": m1},
    "lyapunov_exponent": float(lyap_exp),
    "box_counting_dimension": float(bc_dim),
    "description": "Double-scroll strange attractor. Simplest electronic circuit exhibiting chaos. "
                    "Two scroll structures around each equilibrium point, connected by chaotic switching.",
    "equilibria": [
        {"x": 0, "y": 0, "z": 0, "type": "unstable (saddle)"},
        {"x": -1.0/(m1), "y": (m1+1)/(m1)*(-1.0/m1) - 0, "z": 0, "approx": "scroll center 1"},
        {"x": 1.0/(m1), "y": 0, "z": 0, "approx": "scroll center 2"}
    ]
}
with open('chua_data.json', 'w') as f:
    json.dump(data_out, f, indent=2)
print("Saved chua_data.json")
print("Done!")
