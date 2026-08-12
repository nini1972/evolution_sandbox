"""
Discovery #014: Rössler Attractor — Minimal Chaos and Its Lyapunov Spectrum

The Rössler system (1976) is a "simpler" chaotic system than Lorenz — 
only one nonlinear term (xz). It produces a banded strange attractor.

We compute:
1. Full Lyapunov spectrum via variational equations
2. Kaplan-Yorke dimension
3. Poincaré section
4. Comparison with Lorenz system
5. Return map analysis
"""
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import json

# ---- Rössler system ----
def roessler(state, a=0.2, b=0.2, c=5.7):
    x, y, z = state
    return np.array([
        -y - z,
        x + a * y,
        b + z * (x - c)
    ])

def roessler_jacobian(state, a=0.2, b=0.2, c=5.7):
    x, y, z = state
    return np.array([
        [0, -1, -1],
        [1, a, 0],
        [z, 0, x - c]
    ])

def rk4_step(f, state, dt):
    k1 = f(state)
    k2 = f(state + 0.5*dt*k1)
    k3 = f(state + 0.5*dt*k2)
    k4 = f(state + dt*k3)
    return state + dt * (k1 + 2*k2 + 2*k3 + k4) / 6

def rk4_variational(state, V, dt, f, jac):
    k1s = f(state)
    k2s = f(state + 0.5*dt*k1s)
    k3s = f(state + 0.5*dt*k2s)
    k4s = f(state + dt*k3s)
    new_state = state + dt * (k1s + 2*k2s + 2*k3s + k4s) / 6
    
    J1 = jac(state)
    J2 = jac(state + 0.5*dt*k1s)
    J3 = jac(state + 0.5*dt*k2s)
    J4 = jac(state + dt*k3s)
    
    k1v = J1 @ V
    k2v = J2 @ (V + 0.5*dt*k1v)
    k3v = J3 @ (V + 0.5*dt*k2v)
    k4v = J4 @ (V + dt*k3v)
    
    new_V = V + dt * (k1v + 2*k2v + 2*k3v + k4v) / 6
    return new_state, new_V

# ---- Generate trajectory ----
dt = 0.01
N_steps = 100000
N_transient = 5000

state = np.array([0.1, 0.0, 0.0])
for _ in range(N_transient):
    state = rk4_step(roessler, state, dt)

traj = np.zeros((N_steps, 3))
for i in range(N_steps):
    state = rk4_step(roessler, state, dt)
    traj[i] = state

xs, ys, zs = traj[:, 0], traj[:, 1], traj[:, 2]
print(f"Rössler trajectory: {N_steps} steps, dt={dt}")
print(f"  x range: [{xs.min():.3f}, {xs.max():.3f}]")
print(f"  y range: [{ys.min():.3f}, {ys.max():.3f}]")
print(f"  z range: [{zs.min():.3f}, {zs.max():.3f}]")

# ---- Lyapunov spectrum ----
state = np.array([0.1, 0.0, 0.0])
V = np.eye(3)
lyap_sum = np.zeros(3)
n_steps = 50000
dt_lyap = 0.01
n_renorm = 50

for step in range(n_steps):
    state, V = rk4_variational(state, V, dt_lyap, roessler, roessler_jacobian)
    if (step + 1) % n_renorm == 0:
        Q, R = np.linalg.qr(V)
        V = Q
        lyap_sum += np.log(np.abs(np.diag(R)))

T_total = n_steps * dt_lyap
lyapunov = lyap_sum / T_total
lyap_sorted = np.sort(lyapunov)[::-1]

print(f"\nLyapunov exponents (Rössler, a=0.2, b=0.2, c=5.7):")
print(f"  λ1 = {lyap_sorted[0]:.4f} (positive → chaos)")
print(f"  λ2 = {lyap_sorted[1]:.4f} (≈ 0 → flow direction)")
print(f"  λ3 = {lyap_sorted[2]:.4f} (negative → contraction)")
print(f"  Sum = {lyap_sorted.sum():.4f} (should be a+b-c... actually sum = a - c + ... let's see)")
print(f"  Literature: λ1≈0.0714, λ2≈0.0000, λ3≈-5.2400")

# Kaplan-Yorke dimension
cumsum = np.cumsum(lyap_sorted)
ky_dim = 0
for i in range(len(lyap_sorted) - 1):
    if cumsum[i] > 0:
        ky_dim = i + 1 + cumsum[i] / abs(lyap_sorted[i+1])
print(f"  Kaplan-Yorke dimension D_KY = {ky_dim:.4f}")
print(f"  Literature D_KY ≈ 2.0137")

# ---- Poincaré section at y=0 crossing (x increasing) ----
poincare_x = []
poincare_z = []
for i in range(1, len(traj)):
    if ys[i-1] < 0 and ys[i] >= 0 and xs[i] > 0:  # crossing y=0 in +x direction
        # Linear interpolation
        t_frac = -ys[i-1] / (ys[i] - ys[i-1])
        px = xs[i-1] + t_frac * (xs[i] - xs[i-1])
        pz = zs[i-1] + t_frac * (zs[i] - zs[i-1])
        poincare_x.append(px)
        poincare_z.append(pz)

poincare_x = np.array(poincare_x)
poincare_z = np.array(poincare_z)
print(f"\nPoincaré section (y=0, x-increasing): {len(poincare_x)} crossings")

# ---- Return map: x_{n+1} vs x_n from Poincaré ----
print(f"  x range in section: [{poincare_x.min():.3f}, {poincare_x.max():.3f}]")

# ---- Also compute Lorenz Lyapunov for comparison ----
def lorenz(state, sigma=10.0, rho=28.0, beta=8/3):
    x, y, z = state
    return np.array([sigma*(y-x), x*(rho-z)-y, x*y - beta*z])

def lorenz_jacobian(state, sigma=10.0, rho=28.0, beta=8/3):
    x, y, z = state
    return np.array([[-sigma, sigma, 0], [rho-z, -1, -x], [y, x, -beta]])

state_lorenz = np.array([1.0, 1.0, 1.0])
V_lorenz = np.eye(3)
lyap_sum_lorenz = np.zeros(3)

for step in range(50000):
    state_lorenz, V_lorenz = rk4_variational(state_lorenz, V_lorenz, 0.01, lorenz, lorenz_jacobian)
    if (step + 1) % 50 == 0:
        Q, R = np.linalg.qr(V_lorenz)
        V_lorenz = Q
        lyap_sum_lorenz += np.log(np.abs(np.diag(R)))

lyap_lorenz = np.sort(lyap_sum_lorenz / (50000 * 0.01))[::-1]
ky_lorenz = 2 + lyap_lorenz[0] / abs(lyap_lorenz[2])

print(f"\nLorenz Lyapunov (for comparison):")
print(f"  λ1={lyap_lorenz[0]:.4f}, λ2={lyap_lorenz[1]:.4f}, λ3={lyap_lorenz[2]:.4f}")
print(f"  D_KY = {ky_lorenz:.4f}")

# ---- Plot ----
fig, axes = plt.subplots(2, 3, figsize=(20, 13))
fig.patch.set_facecolor('#0a0a1a')

# 1. Rössler attractor (x-y)
ax = axes[0, 0]
ax.set_facecolor('#0a0a1a')
colors = np.arange(len(traj))
ax.scatter(xs[::5], ys[::5], c=colors[::5], cmap='plasma', s=0.1, alpha=0.3)
ax.set_xlabel('x', fontsize=12, color='white')
ax.set_ylabel('y', fontsize=12, color='white')
ax.set_title('Rössler Attractor (x-y)', fontsize=13, color='white', fontweight='bold')
ax.tick_params(colors='gray')

# 2. Rössler attractor (x-z)
ax = axes[0, 1]
ax.set_facecolor('#0a0a1a')
ax.scatter(xs[::5], zs[::5], c=zs[::5], cmap='inferno', s=0.1, alpha=0.3)
ax.set_xlabel('x', fontsize=12, color='white')
ax.set_ylabel('z', fontsize=12, color='white')
ax.set_title('Rössler Attractor (x-z)', fontsize=13, color='white', fontweight='bold')
ax.tick_params(colors='gray')

# 3. Poincaré section
ax = axes[0, 2]
ax.set_facecolor('#0a0a1a')
if len(poincare_x) > 0:
    ax.scatter(poincare_x, poincare_z, s=2, c='cyan', alpha=0.5)
ax.set_xlabel('x (at y=0 crossing)', fontsize=12, color='white')
ax.set_ylabel('z (at y=0 crossing)', fontsize=12, color='white')
ax.set_title(f'Poincaré Section\n({len(poincare_x)} crossings)', fontsize=13, color='white', fontweight='bold')
ax.tick_params(colors='gray')

# 4. Return map from Poincaré
ax = axes[1, 0]
ax.set_facecolor('#0a0a1a')
if len(poincare_x) > 1:
    ax.scatter(poincare_x[:-1], poincare_x[1:], s=3, c='gold', alpha=0.5)
    # Plot y=x line for reference
    xmin, xmax = poincare_x.min(), poincare_x.max()
    ax.plot([xmin, xmax], [xmin, xmax], 'w--', alpha=0.2, linewidth=1)
ax.set_xlabel('x_n', fontsize=12, color='white')
ax.set_ylabel('x_{n+1}', fontsize=12, color='white')
ax.set_title('Return Map (x_{n+1} vs x_n)', fontsize=13, color='white', fontweight='bold')
ax.tick_params(colors='gray')

# 5. Lyapunov comparison
ax = axes[1, 1]
ax.set_facecolor('#0a0a1a')
x_labels = ['λ₁', 'λ₂', 'λ₃', 'D_KY']
rossler_vals = [lyap_sorted[0], lyap_sorted[1], lyap_sorted[2], ky_dim]
lorenz_vals = [lyap_lorenz[0], lyap_lorenz[1], lyap_lorenz[2], ky_lorenz]
x_pos = np.arange(4)
width = 0.35
bars1 = ax.bar(x_pos - width/2, rossler_vals, width, color='cyan', alpha=0.7, label='Rössler')
bars2 = ax.bar(x_pos + width/2, lorenz_vals, width, color='orange', alpha=0.7, label='Lorenz')
ax.axhline(y=0, color='white', linewidth=0.5)
ax.set_xticks(x_pos)
ax.set_xticklabels(x_labels, fontsize=12, color='white')
ax.set_ylabel('Value', fontsize=12, color='white')
ax.set_title('Lyapunov Spectrum Comparison', fontsize=13, color='white', fontweight='bold')
ax.legend(fontsize=10, facecolor='#1a1a3a', edgecolor='gray', labelcolor='white')
ax.tick_params(colors='gray')

# 6. 3D-ish view (x-y-z projection with color=z)
ax = axes[1, 2]
ax.set_facecolor('#0a0a1a')
# Pseudo-3D: project x, y with offset based on z
z_norm = (zs - zs.min()) / (zs.max() - zs.min())
x_proj = xs + 0.3 * z_norm  # tilt
y_proj = ys + 0.3 * z_norm
ax.scatter(x_proj[::5], y_proj[::5], c=zs[::5], cmap='viridis', s=0.1, alpha=0.3)
ax.set_xlabel('x (tilted)', fontsize=12, color='white')
ax.set_ylabel('y (tilted)', fontsize=12, color='white')
ax.set_title('Rössler Pseudo-3D View', fontsize=13, color='white', fontweight='bold')
ax.tick_params(colors='gray')

plt.suptitle('Rössler Attractor: Minimal Chaos & Lyapunov Analysis', 
             fontsize=16, color='white', fontweight='bold', y=1.01)
plt.tight_layout()
plt.savefig('roessler_attractor_analysis.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print("\nSaved roessler_attractor_analysis.png")

# Save data
results = {
    "description": "Rössler attractor: Lyapunov spectrum, Poincaré section, return map, comparison with Lorenz",
    "parameters": {"a": 0.2, "b": 0.2, "c": 5.7},
    "rossler_lyapunov": [float(x) for x in lyap_sorted],
    "rossler_lyapunov_literature": [0.0714, 0.0, -5.24],
    "rossler_kaplan_yorke": float(ky_dim),
    "rossler_ky_literature": 2.0137,
    "lorenz_lyapunov": [float(x) for x in lyap_lorenz],
    "lorenz_kaplan_yorke": float(ky_lorenz),
    "n_poincare_crossings": len(poincare_x),
}
with open('roessler_data.json', 'w') as f:
    json.dump(results, f, indent=2)
print("Saved roessler_data.json")
