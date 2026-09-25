#!/usr/bin/env python3
"""
Investigate seed-to-seed variability near K_c for reflexive Kuramoto.
The treaty reports collapse failure near K_c with resid=0.469.
This might be due to seeds giving bimodal distributions.
"""
import numpy as np

def kuramoto_reflexive_seed(N, K0, alpha, seed, gamma=1.0, dt=0.10, T_trans=40, T_meas=80):
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

N = 200
gamma = 1.0
dt = 0.10
T_trans = 40.0
T_meas = 80.0

# Focus on the transition region: K0=1.9, 2.6
# Also check K0=0.5, 1.2, 3.3, 4.0
print("=== Seed-by-seed R values ===")
for K0 in [0.5, 1.2, 1.9, 2.6, 3.3, 4.0]:
    for alpha in [-1, 0, 1]:
        R_vals = []
        for seed in range(20):
            r = kuramoto_reflexive_seed(N, K0, alpha, seed, gamma, dt, T_trans, T_meas)
            R_vals.append(r)
        R_vals = np.array(R_vals)
        mean2 = np.mean(R_vals[:2])  # treaty uses 2 seeds
        std2 = np.std(R_vals[:2])
        print(f"  K0={K0:4.1f}, a={alpha:+4.1f}: seeds=2: R={mean2:.4f}±{std2:.4f} | "
              f"seeds=20: R={np.mean(R_vals):.4f}±{np.std(R_vals):.4f} | "
              f"min={np.min(R_vals):.3f} max={np.max(R_vals):.3f}")

# Check if there's a transient issue - look at R trajectory for specific cases
print("\n=== R trajectory for K0=1.9, alpha=0 (near K_c=2) ===")
np.random.seed(0)
omega = gamma * np.random.standard_cauchy(N)
theta = 2 * np.pi * np.random.rand(N)
R_traj = []
for t in range(int(400/ dt)):
    z = np.mean(np.exp(1j*theta))
    R_traj.append(np.abs(z))
    theta += dt * (omega + 0 * np.sin(np.angle(z) - theta))  # K=0
    theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
R_traj = np.array(R_traj)
print(f"  First 10 steps: {R_traj[:10]}")
print(f"  Last 10 steps: {R_traj[-10:]}")

for K in [1.0, 1.5, 1.9, 2.0, 2.5, 3.0, 4.0]:
    np.random.seed(0)
    omega = gamma * np.random.standard_cauchy(N)
    theta = 2 * np.pi * np.random.rand(N)
    R_traj = []
    for t in range(int(200/dt)):
        z = np.mean(np.exp(1j*theta))
        R_traj.append(np.abs(z))
        theta += dt * (omega + K * np.sin(np.angle(z) - theta))
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
    R_traj = np.array(R_traj)
    print(f"  K={K:.1f}: R_traj[0]={R_traj[0]:.4f}, R_traj[100]={R_traj[100]:.4f}, R_traj[500]={R_traj[500]:.4f}, R_traj[1000]={R_traj[1000]:.4f}")

# Check the critical K_c for uniform [-1,1]
print("\n=== Standard Kuramoto with uniform [-1,1] ===")
for K in np.linspace(0.5, 2.0, 16):
    np.random.seed(0)
    omega = 1.0 * (2 * np.random.rand(N) - 1)
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
    print(f"  K={K:.3f}: R={np.mean(R_meas):.4f}")
