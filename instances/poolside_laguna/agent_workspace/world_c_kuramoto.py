"""Comprehensive phase diagram of R^alpha Kuramoto model with finite-size scaling
and critical coupling extraction across alpha parameter."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

def run_kuramoto_mean(N, K0, alpha, n_seeds=10):
    Ts, Tt, dt = 150.0, 120.0, 0.05
    Rs = []
    for s in range(n_seeds):
        rng = np.random.default_rng(s * 1000 + N)
        omega = rng.uniform(-1, 1, N)
        theta = rng.uniform(0, 2*np.pi, N)
        t_total = int((Ts + Tt) / dt)
        for _ in range(t_total):
            z = np.mean(np.exp(1j * theta))
            R = np.abs(z)
            psi = np.angle(z)
            K_eff = K0 * R**alpha if R > 1e-15 else 0.0
            theta = (theta + dt * (omega + K_eff * np.sin(psi - theta))) % (2*np.pi)
        z_final = np.mean(np.exp(1j * theta))
        Rs.append(np.abs(z_final))
    return np.mean(Rs), np.std(Rs)

# Parameters
alphas = np.arange(0, 3.01, 0.05)
K0s = np.arange(0.0, 3.01, 0.025)
N_val = 400
n_seeds = 8

# Phase diagram
print(f"Computing phase diagram: {len(alphas)} alphas x {len(K0s)} K0s")
R_grid = np.zeros((len(alphas), len(K0s)))
err_grid = np.zeros((len(alphas), len(K0s)))

for i, alpha in enumerate(alphas):
    for j, K0 in enumerate(K0s):
        R, e = run_kuramoto_mean(N_val, K0, alpha, n_seeds=n_seeds)
        R_grid[i, j] = R
        err_grid[i, j] = e
    if i % 10 == 0:
        print(f"  alpha={alpha:.2f} ({i+1}/{len(alphas)}) done")

# Save data
np.savez("/workspace/phase_diagram_data.npz",
         alphas=alphas, K0s=K0s, R_grid=R_grid, err_grid=err_grid)

# Extract Kc: where R crosses 0.5 threshold
Kc_vals = np.zeros(len(alphas))
print("\nExtracting Kc values...")
for i, alpha in enumerate(alphas):
    R_row = R_grid[i, :]
    above = R_row > 0.5
    if np.any(above) and np.any(~above):
        idx = np.where(np.diff(above.astype(int)) != 0)[0]
        if len(idx) > 0:
            j = idx[0]
            denom = (R_row[j+1] - R_row[j])
            if abs(denom) > 1e-15:
                Kc_vals[i] = K0s[j] + (0.5 - R_row[j]) * (K0s[j+1] - K0s[j]) / denom
            else:
                Kc_vals[i] = K0s[j]
        else:
            Kc_vals[i] = K0s[-1] if above[-1] else np.inf
    elif np.all(above):
        Kc_vals[i] = 0.0
    else:
        Kc_vals[i] = np.inf

# Finite-size scaling: compute for different N values at alpha=0 (standard Kuramoto)
print("\nFinite-size scaling analysis at alpha=0...")
N_values = [100, 200, 400, 800]
alpha0_Kc = {}
for N in N_values:
    K0_fine = np.arange(0.0, 2.0, 0.01)
    R_fine = []
    for K0 in K0_fine:
        R, _ = run_kuramoto_mean(N, K0, 0.0, n_seeds=15)
        R_fine.append(R)
    R_fine = np.array(R_fine)
    alpha0_Kc[N] = {'K0s': K0_fine.tolist(), 'R_vals': R_fine.tolist(), 'Kc': float(Kc_vals[0])}

# Plot phase diagram
fig, axes = plt.subplots(1, 2, figsize=(20, 7))

# Left: Phase diagram
ax1 = axes[0]
im = ax1.pcolormesh(K0s, alphas, R_grid, shading='auto', cmap='viridis',
                    vmin=0, vmax=1)
ax1.set_xlabel('K0 (coupling strength)', fontsize=14)
ax1.set_ylabel('alpha (nonlinearity exponent)', fontsize=14)
ax1.set_title('Kuramoto R^alpha Phase Diagram\nOrder Parameter R', fontsize=16)
plt.colorbar(im, ax=ax1, label='R')

# Overlay Kc curve
valid = np.isfinite(Kc_vals)
ax1.plot(Kc_vals[valid], alphas[valid], 'r-', linewidth=2, label='Kc(alpha) curve')
ax1.legend(fontsize=12)

# Right: Kc vs alpha
ax2 = axes[1]
ax2.plot(alphas[valid], Kc_vals[valid], 'ro-', markersize=5, linewidth=2)
ax2.set_xlabel('alpha', fontsize=14)
ax2.set_ylabel('Kc(alpha)', fontsize=14)
ax2.set_title('Critical Coupling vs Nonlinearity Exponent', fontsize=16)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/workspace/kuramoto_phase_diagram.png', dpi=150, bbox_inches='tight')
print("Saved phase diagram plot")

# Save results summary
results = {
    'alphas': alphas.tolist(),
    'Kc_vals': Kc_vals.tolist(),
    'finite_size_scaling': {str(N): {'data': alpha0_Kc[N]} for N in N_values},
    'description': 'Phase diagram of R^alpha Kuramoto model with critical coupling extraction'
}
with open('/workspace/kuramoto_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print("Saved results JSON")
