"""Thomas Attractor — labyrinthine chaos on a lattice"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

def thomas_rhs(state, b):
    x, y, z = state
    dx = np.sin(y) - b * x
    dy = np.sin(z) - b * y
    dz = np.sin(x) - b * z
    return np.array([dx, dy, dz])

def rk4_step(f, state, dt, *params):
    k1 = f(state, *params)
    k2 = f(state + 0.5 * dt * k1, *params)
    k3 = f(state + 0.5 * dt * k2, *params)
    k4 = f(state + dt * k3, *params)
    return state + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)

b = 0.18  # b > 0.208 is periodic, b < 0.208 is chaotic
dt = 0.01
n_steps = 60000
n_transient = 10000

# Integrate
state = np.array([1.0, 0.0, 0.0])
for _ in range(n_transient):
    state = rk4_step(thomas_rhs, state, dt, b)
traj = np.zeros((n_steps, 3))
for i in range(n_steps):
    state = rk4_step(thomas_rhs, state, dt, b)
    traj[i] = state

# Lyapunov
state_l = np.array([1.0, 0.0, 0.0])
state2_l = state_l + np.array([1e-8, 0, 0])
d0 = 1e-8
lyap_sum = 0.0
lyap_log = []
for _ in range(n_transient):
    state_l = rk4_step(thomas_rhs, state_l, dt, b)
    state2_l = rk4_step(thomas_rhs, state2_l, dt, b)
for i in range(n_steps):
    state_l = rk4_step(thomas_rhs, state_l, dt, b)
    state2_l = rk4_step(thomas_rhs, state2_l, dt, b)
    d1 = np.linalg.norm(state2_l - state_l)
    if d1 > 0:
        lyap_sum += np.log(d1 / d0)
        lyap_log.append(lyap_sum / ((i+1) * dt))
        state2_l = state_l + (state2_l - state_l) / d1 * d0
lyap_exp = lyap_sum / (n_steps * dt)
print(f"Thomas Attractor (b={b}) — Lyapunov: {lyap_exp:.4f}")

# === Figure 1: Main attractor ===
fig = plt.figure(figsize=(20, 16))
fig.suptitle(f"Thomas Attractor (b={b}): Labyrinthine Chaos", fontsize=18, fontweight='bold')
n_plot = min(60000, len(traj))
colors = np.linspace(0, 1, n_plot)
cmap = plt.cm.twilight

ax1 = fig.add_subplot(2, 3, (1, 2), projection='3d')
ax1.scatter(traj[:n_plot, 0], traj[:n_plot, 1], traj[:n_plot, 2],
            c=colors, cmap=cmap, s=0.1, alpha=0.3)
ax1.set_xlabel('x'); ax1.set_ylabel('y'); ax1.set_zlabel('z')
ax1.set_title('3D Thomas Attractor')
ax1.set_facecolor('black')

for idx, (i, j, lbl) in enumerate([(0,1,'x-y'), (0,2,'x-z'), (1,2,'y-z')]):
    ax = fig.add_subplot(2, 3, idx + 3)
    ax.scatter(traj[:n_plot, i], traj[:n_plot, j], c=colors, cmap=cmap, s=0.1, alpha=0.3)
    ax.set_xlabel(lbl.split('-')[0]); ax.set_ylabel(lbl.split('-')[1])
    ax.set_title(f'{lbl} projection'); ax.set_facecolor('black')

ax5 = fig.add_subplot(2, 3, 6)
ax5.plot(np.arange(len(lyap_log)) * dt, lyap_log, 'r-', linewidth=0.5, alpha=0.7)
ax5.set_xlabel('Time'); ax5.set_ylabel('λ (convergence)')
ax5.set_title(f'Lyapunov Convergence (λ ≈ {lyap_exp:.3f})')
ax5.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('thomas_attractor.png', dpi=150, bbox_inches='tight')
print("Saved thomas_attractor.png")

# === Figure 2: Parameter sweep ===
fig2, axes = plt.subplots(2, 3, figsize=(18, 10))
fig2.suptitle("Thomas Attractor: Parameter Sweep (varying b)", fontsize=16, fontweight='bold')
b_values = [0.10, 0.15, 0.18, 0.20, 0.22, 0.30]
for idx, b_val in enumerate(b_values):
    s = np.array([1.0, 0.0, 0.0])
    for _ in range(5000):
        s = rk4_step(thomas_rhs, s, dt, b_val)
    tp = np.zeros((5000, 3))
    for i in range(5000):
        s = rk4_step(thomas_rhs, s, dt, b_val)
        tp[i] = s
    ax = axes[idx // 3, idx % 3]
    ax.scatter(tp[:, 0], tp[:, 2], c='cyan', s=0.1, alpha=0.3)
    ax.set_facecolor('black')
    ax.set_title(f'b = {b_val}')
    ax.set_xlabel('x'); ax.set_ylabel('z')
    ax.set_xlim([-5, 5]); ax.set_ylim([-5, 5])
plt.tight_layout()
plt.savefig('thomas_parameter_sweep.png', dpi=150, bbox_inches='tight')
print("Saved thomas_parameter_sweep.png")

# === Figure 3: Time series & return map ===
fig3, axes = plt.subplots(1, 2, figsize=(14, 5))
fig3.suptitle("Thomas Attractor: Time Series & x(n+1) vs x(n) Return Map", fontsize=14, fontweight='bold')
t_plot = np.arange(min(10000, len(traj))) * dt
axes[0].plot(t_plot, traj[:len(t_plot), 0], 'b-', linewidth=0.3, alpha=0.7, label='x(t)')
axes[0].plot(t_plot, traj[:len(t_plot), 1], 'g-', linewidth=0.3, alpha=0.5, label='y(t)')
axes[0].set_xlabel('Time'); axes[0].set_ylabel('State')
axes[0].set_title('Time Series'); axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Return map (maxima of x)
x_series = traj[:, 0]
maxima = []
for i in range(1, len(x_series)-1):
    if x_series[i] > x_series[i-1] and x_series[i] > x_series[i+1]:
        maxima.append(x_series[i])
maxima = np.array(maxima)
if len(maxima) > 2:
    axes[1].scatter(maxima[:-1], maxima[1:], c='gold', s=3, alpha=0.5)
    axes[1].set_xlabel('x(n)'); axes[1].set_ylabel('x(n+1)')
    axes[1].set_title('Return Map (maxima of x)')
    axes[1].set_facecolor('black')
    axes[1].set_aspect('equal')
else:
    axes[1].text(0.5, 0.5, 'Not enough maxima', transform=axes[1].transAxes, ha='center')

plt.tight_layout()
plt.savefig('thomas_timeseries_returnmap.png', dpi=150, bbox_inches='tight')
print("Saved thomas_timeseries_returnmap.png")

# === Save data ===
data_out = {
    "system": "Thomas Attractor",
    "equations": "dx/dt=sin(y)-b*x, dy/dt=sin(z)-b*y, dz/dt=sin(x)-b*z",
    "parameters": {"b": b},
    "lyapunov_exponent": float(lyap_exp),
    "description": "Labyrinthine strange attractor with sinusoidal coupling creating a lattice-like structure. "
                   "Exhibits a transition from chaos to periodicity as b increases past ~0.208.",
    "bifurcation_point": 0.208
}
with open('thomas_data.json', 'w') as f_out:
    json.dump(data_out, f_out, indent=2)
print("Saved thomas_data.json")
print("Done!")
