"""Explore phase boundary: K0 sweep at different alpha values."""
import numpy as np
import json

def run_kuramoto(N, K0, alpha, T_trans=60.0, T_meas=80.0, dt=0.05, seed=0, init='random'):
    rng = np.random.default_rng(seed)
    omega = rng.uniform(-1, 1, N)
    if init == 'random':
        theta = rng.uniform(0, 2*np.pi, N)
    elif init == 'seeded':
        theta = rng.uniform(-0.2, 0.2, N)
    t_trans = int(T_trans / dt)
    t_meas = int(T_meas / dt)
    total = t_trans + t_meas
    for _ in range(total):
        z = np.mean(np.exp(1j * theta))
        R = np.abs(z)
        psi = np.angle(z)
        K_eff = K0 * R**alpha if R > 1e-15 else 0.0
        coupling = K_eff * np.sin(psi - theta)
        theta = (theta + dt * (omega + coupling)) % (2*np.pi)
    z_final = np.mean(np.exp(1j * theta))
    R_final = np.abs(z_final)
    return R_final

K0_range = np.arange(0.0, 3.01, 0.1)
alpha_range = [0.0, 0.5, 0.8, 0.95, 1.0, 1.05, 1.1, 1.2, 1.5]

print("K0 sweep across alpha values (random init, N=400)")
print(f"K0 range: {K0_range[0]:.1f} to {K0_range[-1]:.1f}")
print()

phase_data = {}
for alpha in alpha_range:
    R_vals = []
    for K0 in K0_range:
        # Average over 8 seeds
        runs = [run_kuramoto(400, K0, alpha, seed=s, init='random') for s in range(8)]
        R_mean = np.mean(runs)
        R_vals.append(R_mean)
    phase_data[alpha] = {"K0_range": K0_range.tolist(), "R_vals": R_vals}
    # Find approximate transition
    for i in range(len(R_vals)-1):
        if R_vals[i] > 0.3 and R_vals[i+1] > 0.3 and (i == 0 or R_vals[i-1] < 0.3):
            print(f"alpha={alpha:.2f}: transition near K0={K0_range[i]:.1f} (R={R_vals[i]:.3f})")
            break
    else:
        print(f"alpha={alpha:.2f}: no clear transition in range, R_max={max(R_vals):.3f}")

with open("phase_boundary_data.json", "w") as f:
    json.dump(phase_data, f)
print("\nSaved phase_boundary_data.json")
