#!/usr/bin/env python3
"""
Investigate different variants of reflexive Kuramoto to find which gives treaty values.
1. Standard (what we have): K_eff = K0 * R^alpha
2. R_eff model: R_eff = R_static(K0 * R^alpha)
3. Second-order (with inertia): alpha_ddot + d/dt(alpha) = omega + K*R*sin(...)
4. Different normalization: K_eff = K0 * R^alpha / N or K_eff = K0 * R^alpha * N
5. Using sin(K_eff * (psi - theta)) instead of K_eff * sin(psi - theta)
6. Using complex order parameter: K_eff * Z
"""
import numpy as np

# Variant 1: Standard (our current implementation)
def variant1(N, K0, alpha, seed=0, gamma=1.0, dt=0.10, T_trans=40, T_meas=80):
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
    return np.mean(R_meas)

# Variant 2: Using sin(K_eff * (psi - theta)) - the K_eff scales the phase difference
def variant2(N, K0, alpha, seed=0, gamma=1.0, dt=0.10, T_trans=40, T_meas=80):
    np.random.seed(seed)
    omega = gamma * np.random.standard_cauchy(N)
    theta = 2 * np.pi * np.random.rand(N)
    for _ in range(int(T_trans/dt)):
        z = np.mean(np.exp(1j*theta))
        R = np.abs(z)
        K_eff = K0 * max(R, 1e-10)**alpha
        theta += dt * (omega + np.sin(K_eff * (np.angle(z) - theta)))
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
    R_meas = []
    for _ in range(int(T_meas/dt)):
        z = np.mean(np.exp(1j*theta))
        R = np.abs(z)
        K_eff = K0 * max(R, 1e-10)**alpha
        theta += dt * (omega + np.sin(K_eff * (np.angle(z) - theta)))
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
        R_meas.append(np.abs(z))
    return np.mean(R_meas)

# Variant 3: K_eff = K0 + alpha * R (additive instead of multiplicative power)
def variant3(N, K0, alpha, seed=0, gamma=1.0, dt=0.10, T_trans=40, T_meas=80):
    np.random.seed(seed)
    omega = gamma * np.random.standard_cauchy(N)
    theta = 2 * np.pi * np.random.rand(N)
    for _ in range(int(T_trans/dt)):
        z = np.mean(np.exp(1j*theta))
        R = np.abs(z)
        K_eff = K0 * R**alpha
        theta += dt * (omega + K_eff * np.sin(np.angle(z) - theta))
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
    R_meas = []
    for _ in range(int(T_meas/dt)):
        z = np.mean(np.exp(1j*theta))
        R = np.abs(z)
        K_eff = K0 * R**alpha
        theta += dt * (omega + K_eff * np.sin(np.angle(z) - theta))
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
        R_meas.append(np.abs(z))
    return np.mean(R_meas)

# Variant 4: Using z directly (complex form): dtheta = omega + K_eff * Im(z / exp(i*theta))
# = omega + K_eff * Im(z * exp(-i*theta)) = omega + K_eff * Im(z_bar... wait
# K * sin(psi - theta_i) = K * Im(exp(i*(psi - theta_i))) = K * Im(exp(i*psi) * exp(-i*theta_i))
# z = R * exp(i*psi), so exp(i*psi) = z / R
# K * Im(z/R * exp(-i*theta_i)) = K/R * Im(z * exp(-i*theta_i))
# This is the same as K * sin(psi - theta_i) as long as we handle R=0

# Variant 5: K_eff = K0 * R**alpha but using K_eff without max(R, 1e-10) guard
# This could behave differently for alpha < 0 when R -> 0

# Let's try variant 2 (sin(K_eff * (psi - theta))) for K0=4.0, alpha=1.0
print("=== Variant 1 (standard) K0=4.0, alpha=1.0 ===")
for seed in range(3):
    r = variant1(200, 4.0, 1.0, seed=seed)
    print(f"  seed={seed}: R={r:.4f}")

print("=== Variant 2 (sin(K_eff*(psi-theta))) K0=4.0, alpha=1.0 ===")
for seed in range(3):
    r = variant2(200, 4.0, 1.0, seed=seed)
    print(f"  seed={seed}: R={r:.4f}")

# Variant 6: K_eff = K0 * R^alpha, but K_eff is used as K_eff * sin(...) with K_eff = K0 * R**alpha
# where R is updated every step (already doing this)

# Variant 7: What if the treaty uses R_eff = K0 * R^alpha and then R_ss = R_static(R_eff)?
# This would be a self-consistent equation. For alpha=1: R = R_static(K0*R)
# This is different from the dynamical system!

print("\n=== Self-consistent equation R = R_static(K0 * R^alpha) ===")
# Compute R_static for a range of K
def compute_R_static(N=200, gamma=1.0, dt=0.10, T_trans=40, T_meas=80):
    Ks = np.linspace(0, 5, 500)
    Rs = []
    for K in Ks:
        np.random.seed(0)
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
        Rs.append(np.mean(R_meas))
    return Ks, np.array(Rs)

Ks, Rs = compute_R_static()
from scipy.interpolate import interp1d
R_interp = interp1d(Ks, Rs, kind='cubic', fill_value=(Rs[0], Rs[-1]), bounds_error=False)

# Solve R = R_static(K0 * R^alpha) for K0=4.0, alpha=1.0
from scipy.optimize import brentq
K0, alpha = 4.0, 1.0
def self_consistent(R):
    K_eff = K0 * R**alpha
    return R - R_interp(K_eff)

# Search for fixed point
for R_try in np.linspace(0.5, 0.99, 100):
    K_eff = K0 * R_try
    R_pred = float(R_interp(K_eff))
    if abs(R_try - R_pred) < 0.001:
        print(f"  K0={K0}, alpha={alpha}: R={R_try:.4f}, K_eff={K_eff:.4f}, R_static(K_eff)={R_pred:.4f}")

# Also check K0=0.5, alpha=-1.0 (treaty says R=0.418)
K0, alpha = 0.5, -1.0
print(f"\n=== K0={K0}, alpha={alpha} ===")
for R_try in np.linspace(0.1, 0.8, 100):
    K_eff = K0 * R_try**alpha
    R_pred = float(R_interp(K_eff))
    if abs(R_try - R_pred) < 0.002:
        print(f"  Self-consistent: R={R_try:.4f}, K_eff={K_eff:.4f}, R_static(K_eff)={R_pred:.4f}")

# Check K0=4.0, alpha=0.0 (treaty says R~0.99)
K0, alpha = 4.0, 0.0
print(f"\n=== K0={K0}, alpha={alpha} ===")
K_eff = K0  # alpha=0
R_pred = float(R_interp(K_eff))
print(f"  K_eff={K_eff:.4f}, R_static(K_eff)={R_pred:.4f}")

# Check what alpha=-1 gives for various K0
print("\n=== Self-consistent solutions for alpha=-1 ===")
for K0 in [0.5, 1.2, 1.9, 2.6, 3.3, 4.0]:
    alpha = -1.0
    for R_try in np.linspace(0.5, 0.99, 100):
        K_eff = K0 * R_try**alpha
        R_pred = float(R_interp(K_eff))
        if abs(R_try - R_pred) < 0.002:
            print(f"  K0={K0}, alpha={alpha}: R={R_try:.4f}, K_eff={K_eff:.4f}")
            break
    else:
        print(f"  K0={K0}, alpha={alpha}: no solution found in [0.5, 0.99]")

print("\n=== Self-consistent solutions for alpha=1 ===")
for K0 in [0.5, 1.2, 1.9, 2.6, 3.3, 4.0]:
    alpha = 1.0
    for R_try in np.linspace(0.01, 0.5, 100):
        K_eff = K0 * R_try**alpha
        R_pred = float(R_interp(K_eff))
        if abs(R_try - R_pred) < 0.002:
            print(f"  K0={K0}, alpha={alpha}: R={R_try:.4f}, K_eff={K_eff:.4f}")
            break
    else:
        print(f"  K0={K0}, alpha={alpha}: no solution found in [0.01, 0.5]")
