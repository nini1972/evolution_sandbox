#!/usr/bin/env python3
"""
Reproduce EMP-067: Reflexive Kuramoto Master-Curve Collapse.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

def kuramoto_static(N, K, gamma=1.0, dt=0.10, T_trans=40, T_meas=80, n_seeds=2):
    R_final = []
    for seed in range(n_seeds):
        np.random.seed(seed)
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

def kuramoto_reflexive(N, K0, alpha, gamma=1.0, dt=0.10, T_trans=40, T_meas=80, n_seeds=2):
    R_final = []
    for seed in range(n_seeds):
        np.random.seed(seed)
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

Ks_static = np.linspace(0, 4, 16)
R_static = []
for K in Ks_static:
    r, s = kuramoto_static(N, K, gamma, dt=dt, T_trans=T_trans, T_meas=T_meas)
    R_static.append(r)
    print(f"Static K={K:.3f}: R={r:.4f}")
R_static = np.array(R_static)

alphas = [-1, -0.5, 0, 0.5, 1]
K0s = [0.5, 1.2, 1.9, 2.6, 3.3, 4.0]
R_reflexive = np.zeros((len(K0s), len(alphas)))
R_reflexive_std = np.zeros((len(K0s), len(alphas)))

print("\n=== Reflexive Kuramoto Scan ===")
for i, K0 in enumerate(K0s):
    for j, alpha in enumerate(alphas):
        r, s = kuramoto_reflexive(N, K0, alpha, gamma, dt, T_trans, T_meas)
        R_reflexive[i, j] = r
        R_reflexive_std[i, j] = s
        print(f"K0={K0:4.1f}, alpha={alpha:+4.1f}: R={r:.4f} +/- {s:.4f}")

print("\n=== Master-Curve Collapse Analysis ===")
residuals = []
categories = {'high': [], 'mid': [], 'low': []}
for i, K0 in enumerate(K0s):
    for j, alpha in enumerate(alphas):
        R_alpha = R_reflexive[i, j]
        if R_alpha > 1e-6:
            K_eff = K0 * (R_alpha ** alpha)
        else:
            K_eff = 0
        idx = np.argmin(np.abs(Ks_static - K_eff))
        R_static_interp = R_static[idx]
        resid = abs(R_alpha - R_static_interp)
        residuals.append(resid)
        if R_alpha >= 0.5:
            categories['high'].append((resid, K0, alpha, R_alpha, K_eff, R_static_interp))
        elif R_alpha >= 0.2:
            categories['mid'].append((resid, K0, alpha, R_alpha, K_eff, R_static_interp))
        else:
            categories['low'].append((resid, K0, alpha, R_alpha, K_eff, R_static_interp))

print("\n=== Residual Statistics ===")
for cat in ['high', 'mid', 'low']:
    if categories[cat]:
        resids = [x[0] for x in categories[cat]]
        print(f"  {cat.upper()} (n={len(resids)}): std={np.std(resids):.4f}, max|resid|={np.max(resids):.4f}")
    else:
        print(f"  {cat.upper()}: empty")

print("\n=== C1: Direction Check ===")
for i, K0 in enumerate(K0s):
    R_vals = R_reflexive[i, :]
    is_decreasing = all(R_vals[j] >= R_vals[j+1] for j in range(len(R_vals)-1))
    print(f"K0={K0:4.1f}: R by alpha = {R_vals}, decreasing={is_decreasing}")

print("\n=== Treaty Value Checks ===")
idx_k0_05 = K0s.index(0.5)
idx_a_neg1 = alphas.index(-1)
idx_a_pos1 = alphas.index(1)
idx_k0_40 = K0s.index(4.0)
print(f"K0=0.5, alpha=-1: R={R_reflexive[idx_k0_05, idx_a_neg1]:.4f} (treaty: 0.418)")
print(f"K0=0.5, alpha=+1: R={R_reflexive[idx_k0_05, idx_a_pos1]:.4f} (treaty: 0.062)")
print(f"K0=4.0, alpha=+1: R={R_reflexive[idx_k0_40, idx_a_pos1]:.4f} (treaty: 0.872)")

results = {
    'static_reference': {'Ks': Ks_static.tolist(), 'R': R_static.tolist()},
    'reflexive_scan': {
        'alphas': alphas, 'K0s': K0s,
        'R': R_reflexive.tolist(), 'R_std': R_reflexive_std.tolist()
    },
    'collapse_residuals': {
        'high': {'n': len(categories['high']), 'std': float(np.std(categories['high'])) if categories['high'] else None,
                 'max': float(np.max(categories['high'])) if categories['high'] else None},
        'mid': {'n': len(categories['mid']), 'std': float(np.std(categories['mid'])) if categories['mid'] else None,
                'max': float(np.max(categories['mid'])) if categories['mid'] else None},
        'low': {'n': len(categories['low']), 'std': float(np.std(categories['low'])) if categories['low'] else None,
                'max': float(np.max(categories['low'])) if categories['low'] else None}
    },
    'treaty_checks': {
        'K0_0.5_alpha_neg1': {'sim': float(R_reflexive[idx_k0_05, idx_a_neg1]), 'treaty': 0.418},
        'K0_0.5_alpha_pos1': {'sim': float(R_reflexive[idx_k0_05, idx_a_pos1]), 'treaty': 0.062},
        'K0_4.0_alpha_pos1': {'sim': float(R_reflexive[idx_k0_40, idx_a_pos1]), 'treaty': 0.872}
    }
}
with open('emp067_reproduction.json', 'w') as f:
    json.dump(results, f, indent=2)

fig, axes = plt.subplots(1, 3, figsize=(18, 5))
ax = axes[0]
for j, alpha in enumerate(alphas):
    ax.plot(K0s, R_reflexive[:, j], 'o-', label=f'alpha={alpha:+.1f}')
ax.set_xlabel('K0')
ax.set_ylabel('R_ss')
ax.set_title('Reflexive Kuramoto: R_ss vs K0')
ax.legend(fontsize=8)
ax.grid(alpha=0.3)

ax = axes[1]
colors = plt.cm.viridis(np.linspace(0, 1, len(alphas)))
for j, alpha in enumerate(alphas):
    K_effs = []
    for i, K0 in enumerate(K0s):
        R = R_reflexive[i, j]
        if R > 1e-6: K_effs.append(K0 * R**alpha)
        else: K_effs.append(0)
    ax.scatter(K_effs, R_reflexive[:, j], color=colors[j], s=60, label=f'alpha={alpha:+.1f}', zorder=3)
ax.plot(Ks_static, R_static, 'r--', linewidth=2, label='Static R(K)')
ax.set_xlabel(r'$K_{eff}$')
ax.set_ylabel(r'$R_{ss}$')
ax.set_title('Master-Curve Collapse: R_ss vs K_eff')
ax.legend(fontsize=7)
ax.grid(alpha=0.3)

ax = axes[2]
ax.hist(residuals, bins=15, edgecolor='black', alpha=0.7)
ax.axvline(0.024, color='g', linestyle='--', label='2.4% (high)')
ax.axvline(0.469, color='r', linestyle='--', label='46.9% (mid)')
ax.set_xlabel('|Residual|')
ax.set_ylabel('Count')
ax.set_title('Collapse Residual Distribution')
ax.legend(fontsize=8)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('fig_emp067_reproduction.png', dpi=150)
print("\nSaved: fig_emp067_reproduction.png")
print("DONE")
