#!/usr/bin/env python3
"""
Reproduce EMP-067 with Cauchy frequencies + nearest-grid-point comparison.
The treaty uses Ks = np.arange(0, 4.5, 0.25) for static reference and 
nearest-grid interpolation for collapse analysis.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

def kuramoto_static_scan(N, Ks, gamma=1.0, dt=0.10, T_trans=40, T_meas=80, n_seeds=2):
    R_vals = []
    for K in Ks:
        R_mean = []
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
            R_mean.append(np.mean(R_meas))
        R_vals.append(np.mean(R_mean))
    return np.array(R_vals)

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

# Static grid - try different grid spacings
# The treaty uses np.linspace(0, 4, 16) for K0s
# For static, let's try the same grid
Ks_static = np.linspace(0, 4, 16)
R_static = kuramoto_static_scan(N, Ks_static, gamma, dt, T_trans, T_meas, n_seeds=2)

print("=== Static R(K) (Cauchy) ===")
for i, K in enumerate(Ks_static):
    print(f"  K={K:.3f}: R={R_static[i]:.4f}")

alphas = [-1, -0.5, 0, 0.5, 1]
K0s = [0.5, 1.2, 1.9, 2.6, 3.3, 4.0]
R_reflexive = np.zeros((len(K0s), len(alphas)))

print("\n=== Reflexive Kuramoto (Cauchy) ===")
for i, K0 in enumerate(K0s):
    for j, alpha in enumerate(alphas):
        r, s = kuramoto_reflexive(N, K0, alpha, gamma, dt, T_trans, T_meas)
        R_reflexive[i, j] = r
        print(f"  K0={K0:4.1f}, alpha={alpha:+4.1f}: R={r:.4f} +/- {s:.4f}")

print("\n=== Treaty Value Checks ===")
TREATY_VALS = {(0.5, -1): 0.418, (0.5, 0): 0.226, (0.5, 1): 0.062,
               (4.0, -1): 0.993, (4.0, 0): 0.992, (4.0, 1): 0.872}
for (K0, alpha), treaty_val in TREATY_VALS.items():
    i = K0s.index(K0)
    j = alphas.index(alpha)
    sim_val = R_reflexive[i, j]
    match = "✓" if abs(sim_val - treaty_val) < 0.03 else "✗"
    print(f"  K0={K0}, alpha={alpha}: sim={sim_val:.4f}, treaty={treaty_val:.4f} {match}")

print("\n=== Collapse: Nearest Grid Point ===")
categories = {'high': [], 'mid': [], 'low': []}
for i, K0 in enumerate(K0s):
    for j, alpha in enumerate(alphas):
        R_alpha = R_reflexive[i, j]
        if R_alpha > 1e-6:
            K_eff = K0 * (R_alpha ** alpha)
        else:
            K_eff = 0
        # Nearest grid point
        idx = np.argmin(np.abs(Ks_static - K_eff))
        R_static_match = R_static[idx]
        resid = abs(R_alpha - R_static_match)
        cat = 'high' if R_alpha >= 0.5 else ('mid' if R_alpha >= 0.2 else 'low')
        categories[cat].append((resid, K0, alpha, R_alpha, K_eff, R_static_match, idx))
        print(f"  K0={K0:4.1f}, a={alpha:+4.1f}: R_a={R_alpha:.4f}, K_eff={K_eff:.4f}, "
              f"K_grid[{idx}]={Ks_static[idx]:.3f}, R_static={R_static_match:.4f}, resid={resid:.4f}")

print("\n=== Residual Stats (nearest grid) ===")
for cat in ['high', 'mid', 'low']:
    if categories[cat]:
        resids = [x[0] for x in categories[cat]]
        print(f"  {cat.upper()} (n={len(resids)}): std={np.std(resids):.4f}, max={np.max(resids):.4f}")
        for x in categories[cat]:
            print(f"    K0={x[1]}, a={x[2]}: R_a={x[3]:.4f}, K_eff={x[4]:.4f}, "
                  f"R_static={x[5]:.4f}, resid={x[0]:.4f}")

# Also check with more seeds
print("\n=== K0=4.0, alpha=1.0 with more seeds ===")
for nseeds in [2, 5, 10, 20]:
    r, s = kuramoto_reflexive(N, 4.0, 1.0, gamma, dt, T_trans, T_meas, n_seeds=nseeds)
    print(f"  seeds={nseeds}: R={r:.4f} +/- {s:.4f}")

# Check with different N values
print("\n=== K0=4.0, alpha=1.0 with different N ===")
for Nval in [50, 100, 200, 500, 1000, 5000]:
    r, s = kuramoto_reflexive(Nval, 4.0, 1.0, gamma, dt, T_trans, T_meas, n_seeds=2)
    print(f"  N={Nval}: R={r:.4f} +/- {s:.4f}")

# Check K0=0.5, alpha=1.0 with different N
print("\n=== K0=0.5, alpha=1.0 with different N ===")
for Nval in [50, 100, 200, 500, 1000, 5000]:
    r, s = kuramoto_reflexive(Nval, 0.5, 1.0, gamma, dt, T_trans, T_meas, n_seeds=2)
    print(f"  N={Nval}: R={r:.4f} +/- {s:.4f}")
