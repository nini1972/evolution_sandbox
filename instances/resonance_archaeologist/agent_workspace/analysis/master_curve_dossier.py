#!/usr/bin/env python3
"""
Master curve collapse analysis for reflexive Kuramoto.
Uses moderate N=500, fewer seeds, but comprehensive parameter sweep.
Tests both Cauchy and uniform frequency distributions.
"""
import numpy as np
import json

def sim_curly(N, K0, alpha, dist='cauchy', n_seeds=5, dt=0.10, T_trans=200, T_meas=400):
    """Reflexive Kuramoto. Returns R_ss per seed."""
    theta = np.zeros((n_seeds, N))
    omega = np.zeros((n_seeds, N))
    for i in range(n_seeds):
        np.random.seed(i + 100)
        if dist == 'cauchy':
            omega[i] = np.random.standard_cauchy(N)
        elif dist == 'uniform':
            omega[i] = (np.random.rand(N) - 0.5) * 2
        theta[i] = 2 * np.pi * np.random.rand(N)
    for _ in range(T_trans):
        z = np.mean(np.exp(1j*theta), axis=1)
        R = np.abs(z)
        K_eff = K0 * np.maximum(R, 1e-10)**alpha
        theta += dt * (omega + K_eff[:, None] * np.sin(np.angle(z)[:, None] - theta))
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
    R_meas = []
    for _ in range(T_meas):
        z = np.mean(np.exp(1j*theta), axis=1)
        R = np.abs(z)
        K_eff = K0 * np.maximum(R, 1e-10)**alpha
        theta += dt * (omega + K_eff[:, None] * np.sin(np.angle(z)[:, None] - theta))
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
        R_meas.append(np.abs(z))
    return np.mean(R_meas, axis=0)

def sim_static(N, K, dist='cauchy', n_seeds=20, dt=0.10, T_trans=200, T_meas=400):
    """Standard static Kuramoto. Returns mean R_ss."""
    theta = np.zeros((n_seeds, N))
    omega = np.zeros((n_seeds, N))
    for i in range(n_seeds):
        np.random.seed(i + 100)
        if dist == 'cauchy':
            omega[i] = np.random.standard_cauchy(N)
        elif dist == 'uniform':
            omega[i] = (np.random.rand(N) - 0.5) * 2
        theta[i] = 2 * np.pi * np.random.rand(N)
    for _ in range(T_trans):
        z = np.mean(np.exp(1j*theta), axis=1)
        theta += dt * (omega + K * np.sin(np.angle(z)[:, None] - theta))
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
    R_meas = []
    for _ in range(T_meas):
        z = np.mean(np.exp(1j*theta), axis=1)
        theta += dt * (omega + K * np.sin(np.angle(z)[:, None] - theta))
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
        R_meas.append(np.abs(z))
    return np.mean(R_meas, axis=0)

results = {}
for dist in ['cauchy', 'uniform']:
    print(f"\n=== {dist.upper()} frequencies, N=500 ===")
    N = 500
    
    # Build fine static curve
    K_static = np.linspace(0, 5, 51)
    R_static_vals = []
    for K in K_static:
        r = sim_static(N, K, dist=dist, n_seeds=20)
        R_static_vals.append(np.mean(r))
    R_static_vals = np.array(R_static_vals)
    
    # Test collapse across grid
    K0_grid = [0.5, 1.2, 1.9, 2.6, 3.3, 4.0]
    alpha_grid = [-1.0, -0.5, 0.0, 0.5, 1.0]
    
    dist_results = []
    for K0 in K0_grid:
        for alpha in alpha_grid:
            r = sim_curly(N, K0, alpha, dist=dist, n_seeds=10)
            R_ss = np.mean(r)
            R_err = np.std(r) / np.sqrt(len(r))
            K_eff = K0 * R_ss**alpha
            R_pred = np.interp(K_eff, K_static, R_static_vals)
            resid = R_ss - R_pred
            dist_results.append({
                'K0': K0, 'alpha': alpha, 'R_ss': R_ss, 'R_err': R_err,
                'K_eff': K_eff, 'R_pred': R_pred, 'resid': resid
            })
            print(f"  K0={K0:4.1f}, a={alpha:+4.1f}: R_ss={R_ss:.4f}±{R_err:.4f}, K_eff={K_eff:.4f}, F={R_pred:.4f}, resid={resid:+.4f}")
    
    residuals = np.array([abs(r['resid']) for r in dist_results])
    print(f"\n  Residuals: mean={np.mean(residuals):.6f}, max={np.max(residuals):.6f}")
    results[dist] = dist_results
    results[dist + '_static'] = {'K': list(K_static), 'R': list(R_static_vals)}

# Save
with open('master_curve_results.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)
print("\nResults saved to master_curve_results.json")
