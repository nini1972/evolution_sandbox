#!/usr/bin/env python3
"""
Reproduce EMP-067 with uniform frequency distribution [-1, 1].
This is what gives R~0.99 at K0=4.0 (matching treaty's baseline).
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
from scipy.interpolate import interp1d

def kuramoto_static(N, K, gamma=1.0, dt=0.10, T_trans=40, T_meas=80, n_seeds=2, freq_dist='uniform'):
    R_final = []
    for seed in range(n_seeds):
        np.random.seed(seed)
        if freq_dist == 'uniform':
            omega = gamma * (2 * np.random.rand(N) - 1)
        else:
            omega = gamma * np.random.standard_cauchy(N)
        theta = 2 * np.pi * np.random.rand(N)
        for _ in range(int(T_trans/dt)):
            z = np.mean(np.exp(1j*theta))
            theta += dt * (omega + K * np.sin(np.angle(z) - theta))
            theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
        R_meas = []
        for _ in range(int(T_meas/dt)):
            z = np.mean(np.exp(1j*theta))
            theta += dt * (omega + K * np.sin(np.angle(z) - theta))
            theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
            R_meas.append(np.abs(z))
        R_final.append(np.mean(R_meas))
    return np.mean(R_final), np.std(R_final)

def kuramoto_reflexive(N, K0, alpha, gamma=1.0, dt=0.10, T_trans=40, T_meas=80, n_seeds=2, freq_dist='uniform'):
    R_final = []
    for seed in range(n_seeds):
        np.random.seed(seed)
        if freq_dist == 'uniform':
            omega = gamma * (2 * np.random.rand(N) - 1)
        else:
            omega = gamma * np.random.standard_cauchy(N)
        theta = 2 * np.pi * np.random.rand(N)
        for _ in range(int(T_trans/dt)):
            z = np.mean(np.exp(1j*theta))
            R = np.abs(z)
            K_eff = K0 * max(R, 1e-10)**alpha
            theta += dt * (omega + K_eff * np.sin(np.angle(z) - theta))
            theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
        R_meas = []
        for _ in range(int(T_meas/dt)):
            z = np.mean(np.exp(1j*theta))
            R = np.abs(z)
            K_eff = K0 * max(R, 1e-10)**alpha
            theta += dt * (omega + K_eff * np.sin(np.angle(z) - theta))
            theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
            R_meas.append(np.abs(z))
        R_final.append(np.mean(R_meas))
    return np.mean(R_final), np.std(R_final)

gamma = 1.0
N = 200
dt = 0.10
T_trans = 40.0
T_meas = 80.0

# Static reference R(K) - uniform distribution
Ks_static = np.linspace(0, 4, 16)
R_static = []
for K in Ks_static:
    r, s = kuramoto_static(N, K, gamma, dt=dt, T_trans=T_trans, T_meas=T_meas, freq_dist='uniform')
    R_static.append(r)
    print(f"Static K={K:.3f}: R={r:.4f}")
R_static = np.array(R_static)

# Fine static grid for interpolation
Ks_fine = np.linspace(0, 8, 81)
R_fine = []
for K in Ks_fine:
    r, s = kuramoto_static(N, K, gamma, dt=dt, T_trans=T_trans, T_meas=T_meas, freq_dist='uniform')
    R_fine.append(r)
R_fine = np.array(R_fine)

alphas = [-1, -0.5, 0, 0.5, 1]
K0s = [0.5, 1.2, 1.9, 2.6, 3.3, 4.0]
R_reflexive = np.zeros((len(K0s), len(alphas)))

print("\n=== Reflexive Kuramoto (uniform freq) ===")
for i, K0 in enumerate(K0s):
    for j, alpha in enumerate(alphas):
        r, s = kuramoto_reflexive(N, K0, alpha, gamma, dt, T_trans, T_meas, freq_dist='uniform')
        R_reflexive[i, j] = r
        print(f"K0={K0:4.1f}, alpha={alpha:+4.1f}: R={r:.4f} +/- {s:.4f}")

print("\n=== Treaty Value Checks ===")
TREATY_VALS = {(0.5, -1): 0.418, (0.5, 0): 0.226, (0.5, 1): 0.062,
               (4.0, -1): 0.993, (4.0, 0): 0.992, (4.0, 1): 0.872}
for (K0, alpha), treaty_val in TREATY_VALS.items():
    i = K0s.index(K0)
    j = alphas.index(alpha)
    sim_val = R_reflexive[i, j]
    match = "✓" if abs(sim_val - treaty_val) < 0.03 else "✗"
    print(f"  K0={K0}, alpha={alpha}: sim={sim_val:.4f}, treaty={treaty_val:.4f} {match}")

print("\n=== Collapse Analysis (uniform) ===")
residuals = []
categories = {'high': [], 'mid': [], 'low': []}
R_fine_interp = interp1d(Ks_fine, R_fine, kind='cubic', fill_value='extrapolate')
for i, K0 in enumerate(K0s):
    for j, alpha in enumerate(alphas):
        R_alpha = R_reflexive[i, j]
        if R_alpha > 1e-6:
            K_eff = K0 * (R_alpha ** alpha)
        else:
            K_eff = 0
        R_static_interp = float(R_fine_interp(K_eff)) if K_eff <= Ks_fine[-1] else R_fine[-1]
        resid = abs(R_alpha - R_static_interp)
        residuals.append(resid)
        cat = 'high' if R_alpha >= 0.5 else ('mid' if R_alpha >= 0.2 else 'low')
        categories[cat].append((resid, K0, alpha, R_alpha, K_eff, R_static_interp))
        print(f"  K0={K0:4.1f}, a={alpha:+4.1f}: R_a={R_alpha:.4f}, K_eff={K_eff:.4f}, R_static={R_static_interp:.4f}, resid={resid:.4f}")

print("\n=== Residual Stats (uniform, fine interp) ===")
for cat in ['high', 'mid', 'low']:
    if categories[cat]:
        resids = [x[0] for x in categories[cat]]
        print(f"  {cat.upper()} (n={len(resids)}): std={np.std(resids):.4f}, max={np.max(resids):.4f}")

# Plot
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
ax = axes[0]
for j, alpha in enumerate(alphas):
    ax.plot(K0s, R_reflexive[:, j], 'o-', label=f'alpha={alpha:+.1f}')
ax.plot(Ks_static, R_static, 'k--', label='Static R(K)')
ax.set_xlabel('K0'); ax.set_ylabel('R_ss')
ax.set_title('Reflexive Kuramoto (uniform freq)')
ax.legend(fontsize=8); ax.grid(alpha=0.3)

ax = axes[1]
colors = plt.cm.viridis(np.linspace(0, 1, len(alphas)))
for j, alpha in enumerate(alphas):
    K_effs = []
    for i, K0 in enumerate(K0s):
        R = R_reflexive[i, j]
        if R > 1e-6: K_effs.append(K0 * R**alpha)
        else: K_effs.append(0)
    ax.scatter(K_effs, R_reflexive[:, j], color=colors[j], s=60, label=f'alpha={alpha:+.1f}', zorder=3)
ax.plot(Ks_fine, R_fine, 'r--', linewidth=2, label='Static R(K)')
ax.set_xlabel(r'$K_{eff}$'); ax.set_ylabel(r'$R_{ss}$')
ax.set_title('Master-Curve Collapse')
ax.legend(fontsize=7); ax.grid(alpha=0.3)

ax = axes[2]
ax.hist(residuals, bins=15, edgecolor='black', alpha=0.7)
ax.axvline(0.024, color='g', linestyle='--', label='2.4% (high)')
ax.axvline(0.469, color='r', linestyle='--', label='46.9% (mid)')
ax.set_xlabel('|Residual|'); ax.set_ylabel('Count')
ax.set_title('Collapse Residual Distribution')
ax.legend(fontsize=8); ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('fig_emp067_uniform.png', dpi=150)
print(f"\nMax K_eff: {max([x[4] for cat in categories.values() for x in cat]):.4f}")
print("Saved: fig_emp067_uniform.png")

results = {
    'method': 'reproduce_emp067_uniform',
    'params': {'N': N, 'gamma': gamma, 'dt': dt, 'T_trans': T_trans, 'T_meas': T_meas, 'freq_dist': 'uniform'},
    'static_reference': {'Ks': Ks_static.tolist(), 'R': R_static.tolist()},
    'reflexive_scan': {'alphas': alphas, 'K0s': K0s, 'R': R_reflexive.tolist()},
    'collapse_residuals': {cat: {'n': len(categories[cat]),
                                'std': float(np.std([x[0] for x in categories[cat]])) if categories[cat] else 0,
                                'max': float(np.max([x[0] for x in categories[cat]])) if categories[cat] else 0}
                      for cat in categories}
}
with open('emp067_reproduction_uniform.json', 'w') as f:
    json.dump(results, f, indent=2)
print("DONE")
