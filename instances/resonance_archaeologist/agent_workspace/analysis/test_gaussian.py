#!/usr/bin/env python3
"""Test with Gaussian frequencies - what gives R~0.872 at K0=4, alpha=1?"""
import numpy as np

def kuramoto_reflexive(N, K0, alpha, seed, omega_gen='cauchy', gamma=1.0, dt=0.10, T_trans=40, T_meas=80):
    np.random.seed(seed)
    if omega_gen == 'cauchy':
        omega = gamma * np.random.standard_cauchy(N)
    elif omega_gen == 'uniform':
        omega = gamma * (2 * np.random.rand(N) - 1)
    elif omega_gen == 'gaussian':
        omega = gamma * np.random.randn(N)
    elif omega_gen == 'uniform_sym':
        omega = gamma * np.random.uniform(-1, 1, N)
    
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
    return np.mean(R_meas)

for dist in ['cauchy', 'uniform', 'gaussian']:
    print(f"\n=== {dist.upper()} frequencies ===")
    for K0 in [0.5, 1.2, 1.9, 2.6, 3.3, 4.0]:
        for alpha in [-1, 0, 1]:
            R_vals = []
            for seed in range(10):
                r = kuramoto_reflexive(200, K0, alpha, seed, omega_gen=dist)
                R_vals.append(r)
            R_mean = np.mean(R_vals)
            R_mean2 = np.mean(R_vals[:2])
            print(f"  K0={K0:4.1f}, a={alpha:+4.1f}: R(10 seeds)={R_mean:.4f}, R(2 seeds)={R_mean2:.4f}")

# Also check: what if the treaty uses a different formula, like K_eff = K0 * R**alpha
# but without the max(R, 1e-10) guard, so when R->0, K_eff->0 for alpha>0 and K_eff->inf for alpha<0
# Let's also try: what if theta is initialized differently

print("\n=== Different theta initialization (all zeros) ===")
for K0 in [0.5, 1.9, 4.0]:
    for alpha in [-1, 0, 1]:
        np.random.seed(0)
        omega = 1.0 * np.random.standard_cauchy(200)
        theta = np.zeros(200)  # all zero
        dt = 0.10
        for _ in range(int(40/dt)):
            z = np.mean(np.exp(1j*theta))
            R = np.abs(z)
            K_eff = K0 * max(R, 1e-10)**alpha
            theta += dt * (omega + K_eff * np.sin(np.angle(z) - theta))
            theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
        R_meas = []
        for _ in range(int(80/dt)):
            z = np.mean(np.exp(1j*theta))
            R = np.abs(z)
            K_eff = K0 * max(R, 1e-10)**alpha
            theta += dt * (omega + K_eff * np.sin(np.angle(z) - theta))
            theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
            R_meas.append(np.abs(z))
        print(f"  K0={K0:4.1f}, a={alpha:+4.1f}, theta0=0: R={np.mean(R_meas):.4f}")

# What about random initial phases on a grid?
print("\n=== Random phases on a grid ===")
for K0 in [0.5, 4.0]:
    for alpha in [-1, 0, 1]:
        np.random.seed(0)
        omega = 1.0 * np.random.standard_cauchy(200)
        theta = np.random.rand(200) * 2 * np.pi  # different from 2*pi*rand
        dt = 0.10
        for _ in range(int(40/dt)):
            z = np.mean(np.exp(1j*theta))
            R = np.abs(z)
            K_eff = K0 * max(R, 1e-10)**alpha
            theta += dt * (omega + K_eff * np.sin(np.angle(z) - theta))
            theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
        R_meas = []
        for _ in range(int(80/dt)):
            z = np.mean(np.exp(1j*theta))
            R = np.abs(z)
            K_eff = K0 * max(R, 1e-10)**alpha
            theta += dt * (omega + K_eff * np.sin(np.angle(z) - theta))
            theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
            R_meas.append(np.abs(z))
        print(f"  K0={K0:4.1f}, a={alpha:+4.1f}, theta0=rand: R={np.mean(R_meas):.4f}")
