#!/usr/bin/env python3
"""
Finite-size scaling analysis of the master-curve collapse.
Test with N = 100, 200, 500, 1000, 2000 to see how residuals scale.
Also tests different frequency distributions.
"""
import numpy as np

def kuramoto_reflexive_vec(N, K0, alpha, n_seeds, gamma=1.0, dt=0.10, T_trans=40, T_meas=80, dist='cauchy'):
    """Vectorized over seeds."""
    theta = np.zeros((n_seeds, N))
    omega = np.zeros((n_seeds, N))
    for i in range(n_seeds):
        np.random.seed(i + 1000)
        if dist == 'cauchy':
            omega[i] = gamma * np.random.standard_cauchy(N)
        elif dist == 'gaussian':
            omega[i] = gamma * np.random.randn(N)
        elif dist == 'uniform':
            omega[i] = gamma * (np.random.rand(N) - 0.5) * np.sqrt(12)  # unit variance
        theta[i] = 2 * np.pi * np.random.rand(N)
    
    for _ in range(int(T_trans/dt)):
        z = np.mean(np.exp(1j*theta), axis=1)
        R = np.abs(z)
        K_eff = K0 * np.maximum(R, 1e-10)**alpha
        theta += dt * (omega + K_eff[:, np.newaxis] * np.sin(np.angle(z)[:, np.newaxis] - theta))
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
    
    R_meas = []
    for _ in range(int(T_meas/dt)):
        z = np.mean(np.exp(1j*theta), axis=1)
        R = np.abs(z)
        K_eff = K0 * np.maximum(R, 1e-10)**alpha
        theta += dt * (omega + K_eff[:, np.newaxis] * np.sin(np.angle(z)[:, np.newaxis] - theta))
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
        R_meas.append(np.abs(z))
    return np.mean(R_meas, axis=0)

def static_kuramoto_vec(N, K, n_seeds, gamma=1.0, dt=0.10, T_trans=40, T_meas=80, dist='cauchy'):
    theta = np.zeros((n_seeds, N))
    omega = np.zeros((n_seeds, N))
    for i in range(n_seeds):
        np.random.seed(i + 1000)
        if dist == 'cauchy':
            omega[i] = gamma * np.random.standard_cauchy(N)
        elif dist == 'gaussian':
            omega[i] = gamma * np.random.randn(N)
        elif dist == 'uniform':
            omega[i] = gamma * (np.random.rand(N) - 0.5) * np.sqrt(12)
        theta[i] = 2 * np.pi * np.random.rand(N)
    for _ in range(int(T_trans/dt)):
        z = np.mean(np.exp(1j*theta), axis=1)
        theta += dt * (omega + K * np.sin(np.angle(z)[:, np.newaxis] - theta))
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
    R_meas = []
    for _ in range(int(T_meas/dt)):
        z = np.mean(np.exp(1j*theta), axis=1)
        theta += dt * (omega + K * np.sin(np.angle(z)[:, np.newaxis] - theta))
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
        R_meas.append(np.abs(z))
    return np.mean(R_meas, axis=0)

print("=" * 70)
print("FINITE-SIZE SCALING OF MASTER-CURVE COLLAPSE")
print("=" * 70)

# Test points covering all regimes
test_points = [
    (0.5, -1.0, 'high sync via feedback'),
    (0.5, 0.0, 'low sync'),
    (0.5, 1.0, 'very low sync'),
    (1.2, -1.0, 'moderate sync'),
    (2.0, 0.0, 'sync region'),
    (3.3, 1.0, 'transition with positive alpha'),
    (4.0, -1.0, 'high sync'),
]

for dist in ['cauchy', 'uniform', 'gaussian']:
    print(f"\n--- Frequency distribution: {dist} ---")
    
    # Build static curve
    K_static = np.linspace(0, 6, 121)  # Very fine grid
    N_static = 2000
    R_static = []
    for K in K_static:
        r_vals = static_kuramoto_vec(N_static, K, 10, dist=dist)
        R_static.append(np.mean(r_vals))
    R_static = np.array(R_static)
    
    print(f"  Static curve at N={N_static}, K_max=6")
    
    for K0, alpha, desc in test_points:
        N_vals = [100, 200, 500, 1000, 2000]
        residuals = []
        for N in N_vals:
            r_vals = kuramoto_reflexive_vec(N, K0, alpha, 20, dist=dist)
            R_ss = np.mean(r_vals)
            K_eff = K0 * R_ss**alpha
            R_pred = np.interp(K_eff, K_static, R_static)
            resid = abs(R_ss - R_pred)
            residuals.append(resid)
            print(f"    N={N:5d}, {desc}: R_ss={R_ss:.4f}, K_eff={K_eff:.4f}, R_pred={R_pred:.4f}, |resid|={resid:.6f}")
        
        # Check scaling
        if residuals[0] > 0 and residuals[-1] > 0:
            ratio = residuals[0] / residuals[-1]
            print(f"    -> Residual ratio N=100/N=2000: {ratio:.3f}")
    print()
