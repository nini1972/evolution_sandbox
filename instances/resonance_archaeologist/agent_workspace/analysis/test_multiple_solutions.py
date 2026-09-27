#!/usr/bin/env python3
"""
Test for multiple R_ss solutions for the same (K0, alpha).
The self-consistency equation R = F(K0 * R^alpha) can have multiple solutions
near the transition. Check if different initial conditions lead to different R_ss.
"""
import numpy as np

def kuramoto_reflexive_single_traj(N, K0, alpha, seed, theta_init_type='random',
                                    gamma=1.0, dt=0.10, T_trans=40, T_meas=80):
    """Single trajectory with specified initial condition type."""
    np.random.seed(seed)
    omega = gamma * np.random.standard_cauchy(N)
    
    if theta_init_type == 'random':
        theta = 2 * np.pi * np.random.rand(N)
    elif theta_init_type == 'ordered':
        theta = np.zeros(N)
    elif theta_init_type == 'antiphase':
        theta = np.linspace(0, 2*np.pi, N, endpoint=False)
    elif theta_init_type == 'half':
        theta = np.zeros(N)
        theta[N//2:] = np.pi
    
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
    return np.mean(R_meas)

N = 200
gamma = 1.0
dt = 0.10
T_trans = 40.0
T_meas = 80.0

# Test for multiple solutions at transition region
# The self-consistency eqn R = F(K0 * R^alpha) is interesting when there's an S-curve
# Let's check the static R(K) curve shape first

print("=== Static R(K) curve (alpha=0, i.e., standard Kuramoto with Cauchy) ===")
for K in np.linspace(0, 5, 51):
    R_vals = []
    for seed in range(20):
        np.random.seed(seed)
        omega = gamma * np.random.standard_cauchy(N)
        theta = 2 * np.pi * np.random.rand(N)
        for _ in range(int(40/dt)):
            z = np.mean(np.exp(1j*theta))
            theta += dt * (omega + K * np.sin(np.angle(z) - theta))
            theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
        R_meas = []
        for _ in range(int(80/dt)):
            z = np.mean(np.exp(1j*theta))
            theta += dt * (omega + K * np.sin(np.angle(z) - theta))
            theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
            R_meas.append(np.abs(z))
        R_vals.append(np.mean(R_meas))
    R_mean = np.mean(R_vals)
    print(f"  K={K:.2f}: R={R_mean:.4f}")

# Now check if reflexive system has multiple solutions
print("\n=== Multiple solutions test ===")
# Focus on cases where collapse was reported to fail
# EMP-072: K0=0.5, alpha=-1 gives R_ss=0.317 (low) in their test
for K0 in [0.5, 1.0, 1.2, 1.9, 2.0, 2.6, 3.3]:
    for alpha in [-1.0, 0.0, 1.0]:
        R_vals = []
        for theta_type in ['random']:
            for seed in range(20):
                r = kuramoto_reflexive_single_traj(N, K0, alpha, seed, theta_type)
                R_vals.append(r)
        R_vals = np.array(R_vals)
        print(f"  K0={K0:4.1f}, a={alpha:+4.1f}: R=[{np.min(R_vals):.3f}, {np.max(R_vals):.3f}] mean={np.mean(R_vals):.3f} std={np.std(R_vals):.3f}")

# Now check the EMP-072 counterexample more carefully
print("\n=== EMP-072 counterexample check ===")
# (K0=0.5, α=-1): K_eff=1.638, R_ss=0.317
# (K0=1.0, α=-1): K_eff=1.798, R_ss=0.559
# (K0=2.0, α=0):  K_eff=2.000, R_ss=0.717
for K0, alpha in [(0.5, -1.0), (1.0, -1.0), (2.0, 0.0)]:
    R_vals = []
    for seed in range(20):
        r = kuramoto_reflexive_single_traj(N, K0, alpha, seed, 'random')
        R_vals.append(r)
    R_vals = np.array(R_vals)
    print(f"  K0={K0}, a={alpha}: R_mean={np.mean(R_vals):.4f}, R_std={np.std(R_vals):.4f}")
    print(f"    K_eff = K0 * R_mean^alpha = {K0 * np.mean(R_vals)**alpha:.4f}")
    if alpha != 0:
        print(f"    K_eff (min R) = {K0 * np.min(R_vals)**alpha:.4f}")
        print(f"    K_eff (max R) = {K0 * np.max(R_vals)**alpha:.4f}")
