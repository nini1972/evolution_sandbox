"""Preliminary exploration of reflexive Kuramoto near alpha*=1."""
import numpy as np
import json

def run_kuramoto(N, K0, alpha, T_trans=40.0, T_meas=80.0, dt=0.05, seed=0, init='random'):
    rng = np.random.default_rng(seed)
    omega = rng.uniform(-1, 1, N)
    if init == 'random':
        theta = rng.uniform(0, 2*np.pi, N)
    elif init == 'seeded':
        theta = rng.uniform(-0.3, 0.3, N)
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
    psi_final = np.angle(z_final)
    return R_final, psi_final

# Test near alpha=1 at K0=5 with random init
print("=== Preliminary test: alpha sweep at K0=5, N=200, random init ===")
results = {}
for alpha in [0.0, 0.5, 0.8, 0.9, 0.95, 0.98, 1.0, 1.03, 1.05, 1.1]:
    R_vals = [run_kuramoto(200, 5.0, alpha, seed=s)[0] for s in range(5)]
    R_mean = np.mean(R_vals)
    results[alpha] = R_mean
    print(f"alpha={alpha:.2f}, R_mean={R_mean:.4f}")

with open("prelim_results.json", "w") as f:
    json.dump({str(k): v for k, v in results.items()}, f)
print("Saved prelim_results.json")
