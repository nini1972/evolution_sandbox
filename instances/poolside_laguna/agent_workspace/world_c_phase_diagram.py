"""Comprehensive phase diagram of R^alpha Kuramoto model"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def run_kuramoto_mean(N, K0, alpha, n_seeds=8):
    Ts, Tt, dt = 150, 100, 0.05
    Rs = []
    for s in range(n_seeds):
        rng = np.random.default_rng(s)
        omega = rng.uniform(-1, 1, N)
        theta = rng.uniform(0, 2*np.pi, N)
        t_total = int((Ts + Tt) / dt)
        for _ in range(t_total):
            z = np.mean(np.exp(1j * theta))
            R = np.abs(z)
            psi = np.angle(z)
            K_eff = K0 * R**alpha if R > 1e-15 else 0.0
            theta = (theta + dt * (omega + K_eff * np.sin(psi - theta))) % (2*np.pi)
        z_final = np.mean(np.exp(1j * theta))
        Rs.append(np.abs(z_final))
    return np.mean(Rs), np.std(Rs)

# Parameters
alphas = np.arange(0, 3.01, 0.1)
K0s = np.arange(0, 3.01, 0.05)

# Phase diagram
R_grid = np.zeros((len(alphas), len(K0s)))
for i, alpha in enumerate(alphas):
    for j, K0 in enumerate(K0s):
        R, _ = run_kuramoto_mean(300, K0, alpha, n_seeds=6)
        R_grid[i, j] = R
    print(f"alpha={alpha:.1f} done")

# Plot phase diagram
fig, ax = plt.subplots(figsize=(14, 8))
im = ax.pcolormesh(K0s, alphas, R_grid, shading='auto', cmap='viridis')
ax.set_xlabel('K0', fontsize=14)
ax.set_ylabel('alpha', fontsize=14)
ax.set_title('R-alpha Phase Diagram (R vs K0, alpha)', fontsize=16)
plt.colorbar(im, ax=ax, label='Order Parameter R')
plt.tight_layout()
plt.savefig('phase_diagram.png', dpi=200)
plt.close()
print("Saved phase_diagram.png")

# Extract critical coupling
Kc_alpha = []
for i, alpha in enumerate(alphas):
    R_alpha = R_grid[i, :]
    # Find transition point
    Kc = None
    for j in range(1, len(K0s)):
        if R_alpha[j] > 0.1 and R_alpha[j-1] < 0.1:
            Kc = K0s[j]
            break
    if Kc is None:
        Kc = K0s[-1]
    Kc_alpha.append(Kc)
    print(f"alpha={alpha:.1f}, Kc={Kc:.3f}")

Kc_alpha = np.array(Kc_alpha)
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(alphas, Kc_alpha, 'ro-', markersize=8)
ax.set_xlabel('alpha', fontsize=14)
ax.set_ylabel('Kc (critical coupling)', fontsize=14)
ax.set_title('Critical Coupling vs alpha', fontsize=16)
ax.grid(True)
plt.tight_layout()
plt.savefig('kc_vs_alpha.png', dpi=150)
plt.close()
print("Saved kc_vs_alpha.png")

# Save data
np.savez('phase_diagram_data.npz', alphas=alphas, K0s=K0s, R_grid=R_grid, Kc_alpha=Kc_alpha)
print("Saved phase_diagram_data.npz")
