#!/usr/bin/env python3
import numpy as np

def sim(N, K0, alpha, dist='cauchy', n_seeds=5):
    """Run reflexive Kuramoto and return R_ss."""
    theta = np.zeros((n_seeds, N))
    omega = np.zeros((n_seeds, N))
    for i in range(n_seeds):
        np.random.seed(i + 100)
        if dist == 'cauchy':
            omega[i] = np.random.standard_cauchy(N)
        elif dist == 'uniform':
            omega[i] = (np.random.rand(N) - 0.5) * 2
        theta[i] = 2 * np.pi * np.random.rand(N)
    dt = 0.10
    for _ in range(200):
        z = np.mean(np.exp(1j*theta), axis=1)
        R = np.abs(z)
        K_eff = K0 * np.maximum(R, 1e-10)**alpha
        theta += dt * (omega + K_eff[:, None] * np.sin(np.angle(z)[:, None] - theta))
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
    R_last = []
    for _ in range(400):
        z = np.mean(np.exp(1j*theta), axis=1)
        R = np.abs(z)
        K_eff = K0 * np.maximum(R, 1e-10)**alpha
        theta += dt * (omega + K_eff[:, None] * np.sin(np.angle(z)[:, None] - theta))
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
        R_last.append(np.abs(z))
    return np.mean(R_last, axis=0)

# Static curve (alpha=0) at a few key K values
print("=== Static R(K) curve ===")
for dist in ['cauchy', 'uniform']:
    print(f"\n{dist.upper()}:")
    K_static = np.array([0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0])
    R_static = {}
    for K in K_static:
        r = sim(1000, K, 0, dist=dist, n_seeds=10)
        R_static[K] = np.mean(r)
        print(f"  K={K:.1f}: R={R_static[K]:.4f}")

# Test collapse at different N
print("\n=== N-scaling of collapse residuals (Cauchy) ===")
for K0, alpha in [(0.5, -1.0), (0.5, 0.0), (1.2, 0.0), (2.0, 0.0), (4.0, -1.0)]:
    print(f"\n  K0={K0}, alpha={alpha}:")
    for N in [100, 200, 500, 1000]:
        r = sim(N, K0, alpha, 'cauchy', n_seeds=5)
        R_ss = np.mean(r)
        K_eff = K0 * R_ss**alpha
        # Find nearest K in static curve
        K_vals = np.array(list(R_static.keys()))
        R_vals = np.array(list(R_static.values()))
        R_pred = np.interp(K_eff, K_vals, R_vals)
        resid = abs(R_ss - R_pred)
        print(f"    N={N:5d}: R_ss={R_ss:.4f}, K_eff={K_eff:.4f}, F={R_pred:.4f}, |resid|={resid:.6f}")
