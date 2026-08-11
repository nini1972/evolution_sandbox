"""
Discovery #013b: Lorenz System — Proper Symbolic Dynamics via Z-Maxima

The proper way to do symbolic dynamics on the Lorenz system:
- Find local maxima of z(t)
- Use the sequence of z-maxima as the symbolic sequence
- This creates a 1D return map z_{n+1} vs z_n
- The topological entropy comes from the growth rate of distinct n-words

This is the approach of the "Lorenz map" — the 1D map on z-maxima.
"""
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import json
from collections import Counter

# ---- Lorenz system ODE ----
def lorenz(state, sigma=10.0, rho=28.0, beta=8/3):
    x, y, z = state
    return np.array([
        sigma * (y - x),
        x * (rho - z) - y,
        x * y - beta * z
    ])

def rk4_step(f, state, dt):
    k1 = f(state)
    k2 = f(state + 0.5*dt*k1)
    k3 = f(state + 0.5*dt*k2)
    k4 = f(state + dt*k3)
    return state + dt * (k1 + 2*k2 + 2*k3 + k4) / 6

dt = 0.005  # finer dt for better maxima detection
N_steps = 200000
N_transient = 10000

state = np.array([1.0, 1.0, 1.0])
for _ in range(N_transient):
    state = rk4_step(lorenz, state, dt)

traj = np.zeros((N_steps, 3))
for i in range(N_steps):
    state = rk4_step(lorenz, state, dt)
    traj[i] = state

xs, ys, zs = traj[:, 0], traj[:, 1], traj[:, 2]
print(f"Lorenz trajectory: {N_steps} steps, dt={dt}")

# ---- Find local maxima of z ----
# A local max: z[i] > z[i-1] and z[i] > z[i+1]
z_maxima = []
z_max_indices = []
for i in range(1, N_steps - 1):
    if zs[i] > zs[i-1] and zs[i] > zs[i+1]:
        # Parabolic interpolation for better precision
        # z_max = z[i] + (z[i-1] - z[i+1]) / (2*(z[i-1] - 2*z[i] + z[i+1]))
        denom = zs[i-1] - 2*zs[i] + zs[i+1]
        if abs(denom) > 1e-10:
            offset = (zs[i-1] - zs[i+1]) / (2 * denom)
            z_max = zs[i] + offset
        else:
            z_max = zs[i]
        z_maxima.append(z_max)
        z_max_indices.append(i)

z_maxima = np.array(z_maxima)
print(f"Found {len(z_maxima)} local maxima of z")
print(f"  z_max range: [{z_maxima.min():.3f}, {z_maxima.max():.3f}]")

# ---- Symbolic dynamics: threshold partition ----
# Use the average of z_maxima as threshold (or a fixed value)
# The two wings of the attractor correspond to z_max > threshold and < threshold
# A good partition threshold is around z ≈ 28 (rho)
threshold = np.median(z_maxima)
print(f"  Partition threshold: {threshold:.4f}")

# Create symbol sequence: 0 if z_max < threshold, 1 if z_max >= threshold
symbols = [0 if z < threshold else 1 for z in z_maxima]

# ---- Block entropy and topological entropy ----
block_sizes = list(range(1, 20))
H_n = []  # Shannon block entropy
log_N_n = []  # log of number of distinct blocks

for n in block_sizes:
    blocks = []
    for i in range(len(symbols) - n + 1):
        blocks.append(tuple(symbols[i:i+n]))
    
    block_counts = Counter(blocks)
    total = len(blocks)
    probs = np.array(list(block_counts.values())) / total
    
    H = -np.sum(probs * np.log2(probs))
    H_n.append(H)
    log_N_n.append(np.log2(len(block_counts)))

H_n = np.array(H_n)
log_N_n = np.array(log_N_n)

# Topological entropy: slope of log(N_n) vs n
h_top = np.polyfit(block_sizes[-8:], log_N_n[-8:], 1)[0]
# Metric entropy: slope of H_n vs n
h_metric = np.polyfit(block_sizes[-8:], H_n[-8:], 1)[0]

print(f"\nBlock entropy analysis (z-maxima symbolic dynamics):")
print(f"  H_1 = {H_n[0]:.4f} bits")
print(f"  H_2 = {H_n[1]:.4f} bits")
print(f"  H_5 = {H_n[4]:.4f} bits")
print(f"  H_10 = {H_n[9]:.4f} bits")
print(f"  H_19 = {H_n[-1]:.4f} bits")
print(f"  Topological entropy h_top = {h_top:.4f} bits/symbol")
print(f"  Metric entropy h_KS = {h_metric:.4f} bits/symbol")

# ---- Lyapunov exponent via variational equations ----
def lorenz_jacobian(state, sigma=10.0, rho=28.0, beta=8/3):
    x, y, z = state
    return np.array([
        [-sigma, sigma, 0],
        [rho - z, -1, -x],
        [y, x, -beta]
    ])

def rk4_variational(state, V, dt):
    """Integrate state and variational matrix together."""
    # State
    k1s = lorenz(state)
    k2s = lorenz(state + 0.5*dt*k1s)
    k3s = lorenz(state + 0.5*dt*k2s)
    k4s = lorenz(state + dt*k3s)
    new_state = state + dt * (k1s + 2*k2s + 2*k3s + k4s) / 6
    
    # Variational
    J1 = lorenz_jacobian(state)
    J2 = lorenz_jacobian(state + 0.5*dt*k1s)
    J3 = lorenz_jacobian(state + 0.5*dt*k2s)
    J4 = lorenz_jacobian(state + dt*k3s)
    
    k1v = J1 @ V
    k2v = J2 @ (V + 0.5*dt*k1v)
    k3v = J3 @ (V + 0.5*dt*k2v)
    k4v = J4 @ (V + dt*k3v)
    
    new_V = V + dt * (k1v + 2*k2v + 2*k3v + k4v) / 6
    return new_state, new_V

# Compute all three Lyapunov exponents
state = np.array([1.0, 1.0, 1.0])
V = np.eye(3)

lyap_sum = np.zeros(3)
n_steps = 50000
dt_lyap = 0.01
n_renorm = 50

for step in range(n_steps):
    state, V = rk4_variational(state, V, dt_lyap)
    if (step + 1) % n_renorm == 0:
        # QR decomposition
        Q, R = np.linalg.qr(V)
        V = Q
        lyap_sum += np.log(np.abs(np.diag(R)))

T_total = n_steps * dt_lyap
lyapunov = lyap_sum / T_total
print(f"\nLyapunov exponents:")
print(f"  λ1 = {lyapunov[0]:.4f} (positive → chaos)")
print(f"  λ2 = {lyapunov[1]:.4f} (≈ 0 → flow direction)")
print(f"  λ3 = {lyapunov[2]:.4f} (negative → contraction)")
print(f"  Sum = {lyapunov.sum():.4f} (dissipation)")
print(f"  Literature: λ1≈0.9056, λ2≈0, λ3≈-14.5723")

# Kaplan-Yorke dimension
lyap_sorted = np.sort(lyapunov)[::-1]
cumsum = np.cumsum(lyap_sorted)
ky_dim = 0
for i in range(len(lyap_sorted) - 1):
    if cumsum[i] > 0:
        ky_dim = i + 1 + cumsum[i] / abs(lyap_sorted[i+1])
print(f"  Kaplan-Yorke dimension D_KY = {ky_dim:.4f}")
print(f"  Literature D_KY ≈ 2.062")

# ---- Plot ----
fig, axes = plt.subplots(2, 2, figsize=(16, 14))
fig.patch.set_facecolor('#0a0a1a')

# 1. Lorenz attractor
ax = axes[0, 0]
ax.set_facecolor('#0a0a1a')
ax.scatter(xs[::10], zs[::10], c=zs[::10], cmap='inferno', s=0.05, alpha=0.2)
ax.set_xlabel('x', fontsize=12, color='white')
ax.set_ylabel('z', fontsize=12, color='white')
ax.set_title('Lorenz Attractor (x-z plane)', fontsize=13, color='white', fontweight='bold')
ax.tick_params(colors='gray')

# 2. Lorenz map: z_{n+1} vs z_n
ax = axes[0, 1]
ax.set_facecolor('#0a0a1a')
ax.scatter(z_maxima[:-1], z_maxima[1:], s=1.5, c='cyan', alpha=0.3)
ax.axhline(y=threshold, color='gray', linestyle='--', alpha=0.3)
ax.axvline(x=threshold, color='gray', linestyle='--', alpha=0.3)
ax.set_xlabel('z_n (local max)', fontsize=12, color='white')
ax.set_ylabel('z_{n+1} (local max)', fontsize=12, color='white')
ax.set_title(f'Lorenz Map (z-maxima return map)\n{len(z_maxima)} points', fontsize=13, color='white', fontweight='bold')
ax.tick_params(colors='gray')

# 3. Block entropy growth
ax = axes[1, 0]
ax.set_facecolor('#0a0a1a')
ax.plot(block_sizes, H_n, 'o-', color='magenta', markersize=5, linewidth=2, label=f'H_n (Shannon)')
ax.plot(block_sizes, log_N_n, 's-', color='gold', markersize=5, linewidth=2, label=f'log₂ N_n (topological)')
ax.set_xlabel('Block size n', fontsize=12, color='white')
ax.set_ylabel('Bits', fontsize=12, color='white')
ax.set_title(f'Block Entropy Growth\nh_top={h_top:.4f}, h_KS={h_metric:.4f} bits/symbol',
             fontsize=13, color='white', fontweight='bold')
ax.legend(fontsize=10, facecolor='#1a1a3a', edgecolor='gray', labelcolor='white')
ax.tick_params(colors='gray')
ax.grid(True, alpha=0.1, color='gray')

# 4. Lyapunov spectrum
ax = axes[1, 1]
ax.set_facecolor('#0a0a1a')
colors_lyap = ['red', 'yellow', 'blue']
labels = [f'λ₁={lyapunov[0]:.4f}', f'λ₂={lyapunov[1]:.4f}', f'λ₃={lyapunov[2]:.4f}']
bars = ax.bar(range(3), np.sort(lyapunov)[::-1], color=colors_lyap, alpha=0.7)
ax.axhline(y=0, color='white', linewidth=0.5)
ax.set_xticks(range(3))
ax.set_xticklabels(['λ₁', 'λ₂', 'λ₃'], fontsize=12, color='white')
ax.set_ylabel('Value', fontsize=12, color='white')
ax.set_title(f'Lyapunov Spectrum\nD_KY = {ky_dim:.4f} (literature: ~2.062)',
             fontsize=13, color='white', fontweight='bold')
ax.tick_params(colors='gray')

plt.tight_layout()
plt.savefig('lorenz_symbolic_dynamics.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print("\nSaved lorenz_symbolic_dynamics.png")

# Save data
results = {
    "description": "Lorenz system: symbolic dynamics via z-maxima, Lyapunov spectrum, Kaplan-Yorke dimension",
    "parameters": {"sigma": 10.0, "rho": 28.0, "beta": 8/3},
    "n_z_maxima": len(z_maxima),
    "z_max_range": [float(z_maxima.min()), float(z_maxima.max())],
    "partition_threshold": float(threshold),
    "block_entropies": {str(n): float(h) for n, h in zip(block_sizes, H_n)},
    "topological_entropy": float(h_top),
    "metric_entropy": float(h_metric),
    "lyapunov_exponents": [float(x) for x in lyapunov],
    "lyapunov_literature": [0.9056, 0.0, -14.5723],
    "kaplan_yorke_dimension": float(ky_dim),
    "kaplan_yorke_literature": 2.062,
}
with open('lorenz_symbolic_data.json', 'w') as f:
    json.dump(results, f, indent=2)
print("Saved lorenz_symbolic_data.json")
