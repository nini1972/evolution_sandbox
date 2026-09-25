#!/usr/bin/env python3
"""
Reproduce EMP-067 v2: Reflexive Kuramoto with interpolation + longer transients.
Key improvements: interpolate R_static, try different integration schemes.
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

# Static reference R(K) - finer grid for interpolation
Ks_static = np.linspace(0, 4, 16)
R_static = []
for K in Ks_static:
    r, s = kuramoto_static(N, K, gamma, dt=dt, T_trans=T_trans, T_meas=T_meas)
    R_static.append(r)
R_static = np.array(R_static)

# Also compute on a finer grid for interpolation
Ks_fine = np.linspace(0, 4, 161)  # finer grid
R_fine = []
for K in Ks_fine[::10]:  # sample every 10th for speed
    r, s = kuramoto_static(N, K, gamma, dt=dt, T_trans=T_trans, T_meas=T_meas, n_seeds=1)
    R_fine.append((K, r))
Ks_fine_sample = np.array([x[0] for x in R_fine])
R_fine_sample = np.array([x[1] for x in R_fine])

alphas = [-1, -0.5, 0, 0.5, 1]
K0s = [0.5, 1.2, 1.9, 2.6, 3.3, 4.0]
R_reflexive = np.zeros((len(K0s), len(alphas)))

print("=== Reflexive Kuramoto Scan ===")
for i, K0 in enumerate(K0s):
    for j, alpha in enumerate(alphas):
        r, s = kuramoto_reflexive(N, K0, alpha, gamma, dt, T_trans, T_meas)
        R_reflexive[i, j] = r
        print(f"K0={K0:4.1f}, alpha={alpha:+4.1f}: R={r:.4f}")

print("\n=== Master-Curve Collapse (with interpolation) ===")
# Interpolate static R at K_eff
from numpy import interp
residuals = []
categories = {'high': [], 'mid': [], 'low': []}
for i, K0 in enumerate(K0s):
    for j, alpha in enumerate(alphas):
        R_alpha = R_reflexive[i, j]
        if R_alpha > 1e-6:
            K_eff = K0 * (R_alpha ** alpha)
        else:
            K_eff = 0
        # Interpolate
        R_static_interp = np.interp(K_eff, Ks_static, R_static)
        resid = abs(R_alpha - R_static_interp)
        residuals.append(resid)
        cat = 'high' if R_alpha >= 0.5 else ('mid' if R_alpha >= 0.2 else 'low')
        categories[cat].append((resid, K0, alpha, R_alpha, K_eff, R_static_interp))
        print(f"K0={K0:4.1f}, a={alpha:+4.1f}: R_a={R_alpha:.4f}, K_eff={K_eff:.4f}, R_static={R_static_interp:.4f}, resid={resid:.4f}")

print("\n=== Residual Stats ===")
for cat in ['high', 'mid', 'low']:
    if categories[cat]:
        resids = [x[0] for x in categories[cat]]
        print(f"  {cat.upper()} (n={len(resids)}): std={np.std(resids):.4f}, max={np.max(resids):.4f}")

# Also test with longer transients
print("\n=== Longer Transient Test (T_trans=200, T_meas=200) ===")
R_long = np.zeros((len(K0s), len(alphas)))
for i, K0 in enumerate(K0s):
    for j, alpha in enumerate(alphas):
        r, s = kuramoto_reflexive(N, K0, alpha, gamma, dt=0.10, T_trans=200, T_meas=200)
        R_long[i, j] = r
        print(f"K0={K0:4.1f}, alpha={alpha:+4.1f}: R={r:.4f}")

# Check K0=4.0, alpha=+1 specifically with longer run
print("\n=== Extended K0=4.0, alpha=+1 run ===")
for T_tr, T_m in [(40, 80), (200, 200), (500, 500), (1000, 1000)]:
    r, s = kuramoto_reflexive(N, 4.0, 1.0, gamma, dt=0.10, T_trans=T_tr, T_meas=T_m, n_seeds=5)
    print(f"T_trans={T_tr}, T_meas={T_m}, seeds=5: R={r:.4f} +/- {s:.4f}")

results = {
    'method': 'reproduce_emp067_v2',
    'params': {'N': N, 'gamma': gamma, 'dt': dt, 'T_trans': T_trans, 'T_meas': T_meas},
    'static_reference': {'Ks': Ks_static.tolist(), 'R': R_static.tolist()},
    'reflexive_scan': {'alphas': alphas, 'K0s': K0s, 'R': R_reflexive.tolist()},
    'long_transient_scan': {'R': R_long.tolist()},
    'residuals': {cat: {'n': len(categories[cat]), 
                        'std': float(np.std([x[0] for x in categories[cat]])) if categories[cat] else 0,
                        'max': float(np.max([x[0] for x in categories[cat]])) if categories[cat] else 0}
                for cat in categories}
}
with open('emp067_reproduction_v2.json', 'w') as f:
    json.dump(results, f, indent=2)
print("\nDONE")
