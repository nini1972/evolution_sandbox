"""
Discovery #016: Hénon-Heiles System — Hamiltonian Chaos & KAM Theory
Fully vectorized across all ICs simultaneously using numpy.
"""
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import json

def compute_poincare(E, n_ic=20, t_max=500, dt=0.01):
    """Poincaré section at y=0, upward crossing. All ICs integrated simultaneously."""
    # Set up all ICs
    x = np.zeros(n_ic)
    px = np.zeros(n_ic)
    py = np.zeros(n_ic)
    y = np.linspace(0.01, 0.35, n_ic)
    
    py_sq = 2*E - y**2
    valid = py_sq > 0
    py = np.where(valid, np.sqrt(np.maximum(py_sq, 0)), 0)
    
    state = np.stack([x, y, px, py], axis=0)  # shape (4, n_ic)
    n_steps = int(t_max / dt)
    
    all_x = []
    all_px = []
    all_colors = []
    
    for step in range(n_steps):
        # Vectorized RK4
        def rhs(s):
            return np.stack([s[2], s[3], -s[0] - s[1]**2, -s[1] - 2*s[0]*s[1]])
        
        k1 = rhs(state)
        k2 = rhs(state + 0.5*dt*k1)
        k3 = rhs(state + 0.5*dt*k2)
        k4 = rhs(state + dt*k3)
        new_state = state + (dt/6) * (k1 + 2*k2 + 2*k3 + k4)
        
        # Check crossings: y goes from < 0 to >= 0
        crossing = (state[1] < 0) & (new_state[1] >= 0) & valid
        
        for ic in np.where(crossing)[0]:
            alpha = -state[1, ic] / (new_state[1, ic] - state[1, ic] + 1e-30)
            all_x.append(state[0, ic] + alpha * (new_state[0, ic] - state[0, ic]))
            all_px.append(state[2, ic] + alpha * (new_state[2, ic] - state[2, ic]))
            all_colors.append(ic)
        
        state = new_state
    
    return np.array(all_x), np.array(all_px), np.array(all_colors)

# ---- Poincaré sections at 3 energies ----
energies = [1/12, 1/8, 1/6]
E_labels = ["E = 1/12 (regular)", "E = 1/8 (mixed)", "E = 1/6 (critical)"]

fig, axes = plt.subplots(1, 3, figsize=(21, 7))
fig.patch.set_facecolor('#0a0a1a')
all_data = {"description": "Hénon-Heiles Poincaré sections at y=0 (upward crossing), vectorized RK4"}

for idx, (E, label) in enumerate(zip(energies, E_labels)):
    print(f"E = {E:.6f} ...")
    xs, pxs, colors = compute_poincare(E, n_ic=20, t_max=500, dt=0.01)
    print(f"  {len(xs)} points")
    all_data[f"E_{idx}"] = {"energy": float(E), "n_points": len(xs), "label": label}
    
    ax = axes[idx]
    ax.set_facecolor('#0a0a1a')
    if len(colors) > 0:
        n_colors = len(set(colors.tolist()))
        cmap = plt.colormaps['hsv'].resampled(max(n_colors, 1))
        for ci, c in enumerate(sorted(set(colors.tolist()))):
            mask = colors == c
            ax.scatter(xs[mask], pxs[mask], s=0.5, alpha=0.5, color=cmap(ci), edgecolors='none')
    
    ax.set_xlabel('x', fontsize=12, color='white')
    ax.set_ylabel('px', fontsize=12, color='white')
    ax.set_title(label, fontsize=13, color='white', fontweight='bold')
    ax.tick_params(colors='gray')
    ax.text(0.02, 0.98, f"N = {len(xs)} pts", transform=ax.transAxes,
            fontsize=10, color='white', verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='#1a1a3a', edgecolor='gray', alpha=0.7))

plt.suptitle('Hénon-Heiles System: KAM Transition in Poincaré Sections',
             fontsize=15, color='white', fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('henon_heiles_poincare.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print("Saved henon_heiles_poincare.png")

# ---- Trajectory at E=1/8 ----
print("Computing trajectory at E=1/8...")
E = 1/8
x0, y0, px0 = 0.0, 0.15, 0.03
py0 = np.sqrt(max(2*E - y0**2 - px0**2, 0))
state = np.array([x0, y0, px0, py0])
dt = 0.002
n_steps = 50000

def H(s):
    return 0.5*(s[0]**2 + s[1]**2 + s[2]**2 + s[3]**2) + s[0]*s[1]**2 - s[0]**3/3

traj = np.zeros((n_steps, 4))
E_vals = np.zeros(n_steps)
traj[0] = state
E_vals[0] = H(state)

def rhs(s):
    return np.array([s[2], s[3], -s[0] - s[1]**2, -s[1] - 2*s[0]*s[1]])

for step in range(1, n_steps):
    k1 = rhs(state)
    k2 = rhs(state + 0.5*dt*k1)
    k3 = rhs(state + 0.5*dt*k2)
    k4 = rhs(state + dt*k3)
    state = state + (dt/6) * (k1 + 2*k2 + 2*k3 + k4)
    traj[step] = state
    E_vals[step] = H(state)

drift = abs(E_vals[-1] - E_vals[0])
print(f"  Energy drift: {drift:.2e}")

fig2 = plt.figure(figsize=(16, 6))
fig2.patch.set_facecolor('#0a0a1a')

ax = fig2.add_subplot(131, projection='3d')
ax.plot(traj[:, 0], traj[:, 1], traj[:, 2], linewidth=0.15, color='cyan', alpha=0.4)
ax.set_xlabel('x', color='white', fontsize=9); ax.set_ylabel('y', color='white', fontsize=9); ax.set_zlabel('px', color='white', fontsize=9)
ax.set_title('Phase Space (x, y, px)', color='white', fontsize=11)
ax.tick_params(colors='gray', labelsize=7)

ax = fig2.add_subplot(132)
ax.set_facecolor('#0a0a1a')
ax.plot(np.arange(n_steps)*dt, E_vals, color='gold', linewidth=0.3)
ax.axhline(y=E, color='red', linewidth=1, alpha=0.5, linestyle='--')
ax.set_xlabel('t', color='white'); ax.set_ylabel('H', color='white')
ax.set_title(f'Energy Conservation (drift={drift:.2e})', color='white', fontsize=10)
ax.tick_params(colors='gray')

ax = fig2.add_subplot(133)
ax.set_facecolor('#0a0a1a')
ax.plot(np.arange(n_steps)*dt, traj[:, 0], color='cyan', linewidth=0.2)
ax.set_xlabel('t', color='white'); ax.set_ylabel('x(t)', color='white')
ax.set_title('x(t) Time Series', color='white', fontsize=11)
ax.tick_params(colors='gray')

plt.suptitle('Hénon-Heiles System at E=1/8 (Mixed Phase Space)', fontsize=13, color='white', fontweight='bold')
plt.tight_layout()
plt.savefig('henon_heiles_trajectory.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print("Saved henon_heiles_trajectory.png")

all_data["energy_conservation"] = {"E_initial": float(E_vals[0]), "E_final": float(E_vals[-1]), "drift": float(drift)}
with open('henon_heiles_data.json', 'w') as f:
    json.dump(all_data, f, indent=2)
print("Saved henon_heiles_data.json\nDone!")
