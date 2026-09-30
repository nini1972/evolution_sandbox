"""Quick reduced test to find phase boundary structure."""
import numpy as np
import json

def run_kuramoto(N, K0, alpha, T_trans=30.0, T_meas=50.0, dt=0.1, seed=0, init='random'):
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
    return np.abs(z_final)

# Smaller, faster sweep
K0_range = [0.0, 0.2, 0.5, 0.8, 1.0, 1.2, 1.5, 1.8, 2.0, 2.5, 3.0]
alpha_range = [0.0, 0.5, 1.0, 1.5]

print("Quick test: N=100, 3 seeds")
phase_data = {}
for alpha in alpha_range:
    R_vals = []
    for K0 in K0_range:
        runs = [run_kuramoto(100, K0, alpha, seed=s, init='random') for s in range(3)]
        R_mean = np.mean(runs)
        R_vals.append(R_mean)
    phase_data[alpha] = {"K0_range": K0_range, "R_vals": [float(v) for v in R_vals]}
    # find transition
    trans = None
    for i in range(len(R_vals)):
        if R_vals[i] > 0.4:
            trans = K0_range[i]
            break
    print(f"alpha={alpha:.1f}: transition~K0={trans}, R_vals={[f'{v:.2f}' for v in R_vals]}")

with open("quick_phase.json", "w") as f:
    json.dump(phase_data, f)
print("Saved")
