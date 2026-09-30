"""Test for hysteresis: seeded vs random init near transition at alpha=1."""
import numpy as np

def run_kuramoto(N, K0, alpha, T_trans, T_meas, dt, seed, init):
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
    return np.abs(z_final)

# Test hysteresis at alpha=1 near K0=1.5
print("=== Hysteresis test at alpha=1.0 ===")
print("K0    R_random  R_seeded")
for K0 in [1.0, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 2.0]:
    R_rand = np.mean([run_kuramoto(200, K0, 1.0, 80, 100, 0.05, s, 'random') for s in range(8)])
    R_seed = np.mean([run_kuramoto(200, K0, 1.0, 80, 100, 0.05, s, 'seeded') for s in range(8)])
    print(f"{K0:.1f}   {R_rand:.4f}    {R_seed:.4f}")

# Finer sweep near alpha=1 transition
print("\n=== Finer K0 sweep at alpha=1.0 ===")
K0_fine = np.arange(0.8, 2.5, 0.1)
for K0 in K0_fine:
    R = np.mean([run_kuramoto(200, K0, 1.0, 80, 100, 0.05, s, 'random') for s in range(6)])
    print(f"K0={K0:.1f}: R={R:.4f}")
