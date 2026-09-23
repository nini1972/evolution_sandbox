#!/usr/bin/env python3
"""Resonance Archaeologist: Adler Root Reproduction (optimized)."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

def kuramoto_correct(N, K, gamma=1.0, omega_dist='lorentzian', T=2000, dt=0.05, n_seeds=3):
    dt_arr = dt
    t_total = int(T / dt_arr)
    t_transient = int(t_total * 0.5)
    R_final = []
    for seed in range(n_seeds):
        np.random.seed(seed)
        if omega_dist == 'lorentzian':
            omega = gamma * np.random.standard_cauchy(N)
        elif omega_dist == 'gaussian':
            omega = gamma * np.random.randn(N)
        elif omega_dist == 'uniform':
            omega = gamma * (2 * np.random.rand(N) - 1)
        theta = 2 * np.pi * np.random.rand(N)
        for t in range(t_total):
            z = np.mean(np.exp(1j * theta))
            theta += dt_arr * (omega + 2*K * np.sin(np.angle(z) - theta))
            theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
        z = np.mean(np.exp(1j * theta))
        R_final.append(np.abs(z))
    return np.mean(R_final), np.std(R_final)

def adler_root_curve(delta):
    R = np.zeros_like(delta)
    mask = delta >= 1.0
    R[mask] = delta[mask] - np.sqrt(delta[mask]**2 - 1)
    return R

print("=== Adler Root Reproduction (PRF-009) ===")
gamma = 1.0
Kc_theory = {'lorentzian': 2*gamma/np.pi, 'gaussian': np.sqrt(8/np.pi)*gamma, 'uniform': gamma}
for d, kc in Kc_theory.items():
    print(f"  Kc({d}) = {kc:.6f}")

# Reproduce cross-locking curve
deltas_sim = np.linspace(1.0, 5.0, 12)
R_sim = []
for delta in deltas_sim:
    K = gamma / (2 * delta)
    R_m, R_s = kuramoto_correct(1500, K, gamma, 'lorentzian', n_seeds=3, T=1500)
    R_sim.append((R_m, R_s))
    print(f"  delta={delta:.2f}: R_sim={R_m:.4f}, R_exact={adler_root_curve(np.array([delta]))[0]:.4f}")
R_sim = np.array(R_sim)
R_exact_at_sim = adler_root_curve(deltas_sim)

# Distribution comparison
Ks_uni = np.linspace(0.3, 1.5, 20)
Ks_gau = np.linspace(0.6, 2.0, 20)
Ks_lor = np.linspace(0.3, 1.2, 20)
R_lor = np.array([kuramoto_correct(800, K, gamma, 'lorentzian', n_seeds=2, T=1500)[0] for K in Ks_lor])
R_gau = np.array([kuramoto_correct(800, K, gamma, 'gaussian', n_seeds=2, T=1500)[0] for K in Ks_gau])
R_uni = np.array([kuramoto_correct(800, K, gamma, 'uniform', n_seeds=2, T=1500)[0] for K in Ks_uni])

print(f"\nDistribution scaling check:")
for name, Ks, R, kc in [('L', Ks_lor, R_lor, Kc_theory['lorentzian']),
                          ('G', Ks_gau, R_gau, Kc_theory['gaussian']),
                          ('U', Ks_uni, R_uni, Kc_theory['uniform'])]:
    idx = np.argmin(np.abs(Ks/kc - 1.1))
    print(f"  {name}: R at K/Kc=1.1 = {R[idx]:.4f}")

# Finite-N
Ns = [200, 500, 1000, 2000]
Kc_finite = []
for N in Ns:
    Ks_fine = np.linspace(0.55, 0.72, 10)
    R_vals = np.array([kuramoto_correct(N, K, 1.0, 'lorentzian', n_seeds=3, T=1000)[0] for K in Ks_fine])
    idx = np.argmin(np.abs(R_vals - 0.5))
    Kc_finite.append(Ks_fine[idx])
    print(f"  N={N:5d}: K_c ~ {Kc_finite[-1]:.4f}")

# Critical exponent
Kc = Kc_theory['lorentzian']
Ks_crit = np.linspace(Kc, Kc*1.12, 12)
R_crit = np.array([kuramoto_correct(3000, K, 1.0, 'lorentzian', n_seeds=3, T=2000)[0] for K in Ks_crit])
eps = Ks_crit / Kc - 1
mask = eps > 0.01
slope, _ = np.polyfit(np.log(eps[mask]), np.log(R_crit[mask]), 1)
beta_measured = slope
print(f"\n  beta measured = {beta_measured:.4f} (theory = 0.5)")

results = {
    'adler_curve_deltas': deltas_sim.tolist(),
    'adler_curve_R_sim': R_sim[:,0].tolist(),
    'adler_curve_R_exact': R_exact_at_sim.tolist(),
    'Kc_theory': Kc_theory,
    'distribution_scan': {
        'lorentzian': {'Ks': Ks_lor.tolist(), 'R': R_lor.tolist()},
        'gaussian': {'Ks': Ks_gau.tolist(), 'R': R_gau.tolist()},
        'uniform': {'Ks': Ks_uni.tolist(), 'R': R_uni.tolist()}
    },
    'Kc_finite_N': {'Ns': Ns, 'Kc': Kc_finite},
    'critical_exponent': {'beta_measured': float(beta_measured), 'beta_theory': 0.5}
}
with open('adler_root_results.json', 'w') as f:
    json.dump(results, f, indent=2)

fig, axes = plt.subplots(1, 3, figsize=(16, 5))
ax = axes[0]
deltas_full = np.linspace(1.0, 5.0, 100)
ax.plot(deltas_full, adler_root_curve(deltas_full), 'r-', linewidth=2, label='Adler formula (PRF-009)')
ax.errorbar(deltas_sim, R_sim[:,0], yerr=R_sim[:,1], fmt='ko', markersize=6, capsize=3, label='Simulation')
ax.set_xlabel(r'$\delta$')
ax.set_ylabel(r'$R_{cross}$')
ax.set_title('Adler Root Curve')
ax.legend()
ax.grid(True, alpha=0.3)
ax = axes[1]
ax.plot(Ks_lor/Kc_theory['lorentzian'], R_lor, 'b^-', label='Lorentzian')
ax.plot(Ks_gau/Kc_theory['gaussian'], R_gau, 'gs-', label='Gaussian')
ax.plot(Ks_uni/Kc_theory['uniform'], R_uni, 'rv-', label='Uniform')
ax.axvline(1.0, color='k', linestyle='--', alpha=0.5)
ax.set_xlabel(r'$K/K_c$')
ax.set_ylabel(r'$R_{ss}$')
ax.set_title('Distribution Scaling')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)
ax = axes[2]
ax.plot(Ns, Kc_finite, 'ko-', markersize=8)
ax.axhline(Kc_theory['lorentzian'], color='r', linestyle='--', label=f'K_c(inf)={Kc_theory["lorentzian"]:.4f}')
ax.set_xlabel('N')
ax.set_ylabel(r'$K_c(N)$')
ax.set_xscale('log')
ax.set_title('Finite-Size Corrections')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('fig_adler_root_reproduction.png', dpi=150)
print(f"\nSaved: fig_adler_root_reproduction.png")
print("Done.")
