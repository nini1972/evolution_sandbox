#!/usr/bin/env python3
"""
Investigate K0=4.0, alpha=+1 case. Why does treaty get R=0.872 but we get R=0.696?
Try different seeds, initial conditions, and check steady-state convergence.
"""
import numpy as np

def kuramoto_reflexive(N, K0, alpha, gamma=1.0, dt=0.10, T_trans=40, T_meas=80, seed=0, theta0=None):
    np.random.seed(seed)
    omega = gamma * np.random.standard_cauchy(N)
    if theta0 is None:
        theta = 2 * np.pi * np.random.rand(N)
    else:
        theta = theta0.copy()
    
    # transient
    for _ in range(int(T_trans/dt)):
        z = np.mean(np.exp(1j*theta))
        R = np.abs(z)
        K_eff = K0 * max(R, 1e-10)**alpha
        theta += dt * (omega + K_eff * np.sin(np.angle(z) - theta))
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
    
    # measurement with trajectory tracking
    R_traj = []
    for _ in range(int(T_meas/dt)):
        z = np.mean(np.exp(1j*theta))
        R = np.abs(z)
        K_eff = K0 * max(R, 1e-10)**alpha
        theta += dt * (omega + K_eff * np.sin(np.angle(z) - theta))
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
        R_traj.append(np.abs(z))
    
    return np.mean(R_traj), np.std(R_traj), R_traj

print("=== K0=4.0, alpha=1.0: Different seeds ===")
for seed in range(10):
    r, s, traj = kuramoto_reflexive(200, 4.0, 1.0, seed=seed)
    # Check if R is still changing
    first_half = np.mean(traj[:len(traj)//2])
    second_half = np.mean(traj[len(traj)//2:])
    print(f"  seed={seed}: R={r:.4f} +/- {s:.4f}, first_half={first_half:.4f}, second_half={second_half:.4f}")

print("\n=== K0=4.0, alpha=1.0: Longer run ===")
r, s, traj = kuramoto_reflexive(200, 4.0, 1.0, T_trans=400, T_meas=2000, seed=0)
print(f"  T_trans=400, T_meas=2000: R={r:.4f} +/- {s:.4f}")
first_half = np.mean(traj[:len(traj)//2])
second_half = np.mean(traj[len(traj)//2:])
print(f"  first_half={first_half:.4f}, second_half={second_half:.4f}")

# Also check alpha=-1 at K0=4.0
print("\n=== K0=4.0, alpha=-1.0: Different seeds ===")
for seed in range(10):
    r, s, traj = kuramoto_reflexive(200, 4.0, -1.0, seed=seed)
    first_half = np.mean(traj[:len(traj)//2])
    second_half = np.mean(traj[len(traj)//2:])
    print(f"  seed={seed}: R={r:.4f} +/- {s:.4f}, first_half={first_half:.4f}, second_half={second_half:.4f}")

# Check alpha=0 (static) at K0=4.0
print("\n=== K0=4.0, alpha=0.0: Different seeds ===")
for seed in range(10):
    r, s, traj = kuramoto_reflexive(200, 4.0, 0.0, seed=seed)
    print(f"  seed={seed}: R={r:.4f} +/- {s:.4f}")

# Check alpha=0.5 at K0=4.0
print("\n=== K0=4.0, alpha=0.5: Different seeds ===")
for seed in range(10):
    r, s, traj = kuramoto_reflexive(200, 4.0, 0.5, seed=seed)
    print(f"  seed={seed}: R={r:.4f} +/- {s:.4f}")
