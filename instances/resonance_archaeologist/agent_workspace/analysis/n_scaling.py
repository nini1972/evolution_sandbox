#!/usr/bin/env python3
"""
Quick N-scaling test for the master-curve collapse (Cauchy, key test points).
"""
import numpy as np

def kuramoto_reflexive(N, K0, alpha, n_seeds=10, dist='cauchy'):
    theta = np.zeros((n_seeds, N))
    omega = np.zeros((n_seeds, N))
    for i in range(n_seeds):
        np.random.seed(i + 1000)
        if dist == 'cauchy':
            omega[i] = np.random.standard_cauchy(N)
        elif dist == 'uniform':
            omega[i] = (np.random.rand(N) - 0.5) * 2  # uniform [-1,1]
        theta[i] = 2 * np.pi * np.random.rand(N)
    dt = 0.10
    for _ in range(400):
        z = np.mean(np.exp(1j*theta), axis=1)
        R = np.abs(z)
        K_eff = K0 * np.maximum(R, 1e-10)**alpha
        theta += dt * (omega + K_eff[:, None] * np.sin(np.angle(z)[:, None] - theta))
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
    R_meas = []
    for _ in range(800):
        z = np.mean(np.exp(1j*theta), axis=1)
        R = np.abs(z)
        K_eff = K0 * np.maximum(R, 1e-10)**alpha
        theta += dt * (omega + K_eff[:, None] * np.sin(np.angle(z)[:, None] - theta))
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
        R_meas.append(np.abs(z))
    return np.mean(R_meas, axis=0)

def static_kuramoto(N, K, n_seeds=10, dist='cauchy'):
    theta = np.zeros((n_seeds, N))
    omega = np.zeros((n_seeds, N))
    for i in range(n_seeds):
        np.random.seed(i + 1000)
        if dist == 'cauchy':
            omega[i] = np.random.standard_cauchy(N)
        elif dist == 'uniform':
            omega[i] = (np.random.rand(N) - 0.5) * 2
        theta[i] = 2 * np.pi * np.random.rand(N)
    dt = 0.10
    for _ in range(400):
        z = np.mean(np.exp(1j*theta), axis=1)
        theta += dt * (omega + K * np.sin(np.angle(z)[:, None] - theta))
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
    R_meas = []
    for _ in range(800):
        z = np.mean(np.exp(1j*theta), axis=1)
        theta += dt * (omega + K * np.sin(np.angle(z)[:, None] - theta))
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
        R_meas.append(np.abs(z))
    return np.mean(R_meas, axis=0)

# Build high-res static curves
K_static = np.linspace(0, 6, 121)

for dist in ['cauchy', 'uniform']:
    print(f"\n=== {dist.upper()} frequencies ===")
    R_static = []
    for K in K_static:
        r = static_kuramoto(2000, K, 10, dist=dist)
        R_static.append(np.mean(r))
    R_static = np.array(R_static)
    
    test_points = [(0.5, -1.0), (0.5, 0.0), (0.5, 1.0), (2.0, 0.0), (4.0, -1.0)]
    
    for K0, alpha in test_points:
        print(f"\n  K0={K0}, alpha={alpha}:")
        for N in [100, 200, 500, 1000, 2000]:
            r = kuramoto_reflexive(N, K0, alpha, 10, dist=dist)
            R_ss = np.mean(r)
            K_eff = K0 * R_ss**alpha
            R_pred = np.interp(K_eff, K_static, R_static)
            resid = abs(R_ss - R_pred)
            print(f"    N={N:5d}: R_ss={R_ss:.4f}, K_eff={K_eff:.4f}, F(K_eff)={R_pred:.4f}, |resid|={resid:.6f}")
