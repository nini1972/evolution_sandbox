#!/usr/bin/env python3
"""Fast Adler root reproduction."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

def kuramoto(N, K, gamma=1.0, dist='lorentzian', T=1000, dt=0.1, n_seeds=2):
    t_total = int(T/dt)
    R_final = []
    for seed in range(n_seeds):
        np.random.seed(seed)
        if dist == 'lorentzian': omega = gamma * np.random.standard_cauchy(N)
        elif dist == 'gaussian': omega = gamma * np.random.randn(N)
        else: omega = gamma * (2*np.random.rand(N)-1)
        theta = 2*np.pi*np.random.rand(N)
        for t in range(t_total):
            z = np.mean(np.exp(1j*theta))
            theta += dt * (omega + 2*K*np.sin(np.angle(z)-theta))
        z = np.mean(np.exp(1j*theta))
        R_final.append(np.abs(z))
    return np.mean(R_final), np.std(R_final)

def adler_root(delta):
    R = np.zeros_like(delta)
    mask = delta >= 1.0
    R[mask] = delta[mask] - np.sqrt(delta[mask]**2 - 1)
    return R

gamma = 1.0
Kc = {'lorentzian': 2*gamma/np.pi, 'gaussian': np.sqrt(8/np.pi)*gamma, 'uniform': gamma}

# Cross-locking curve
deltas = np.linspace(1.0, 5.0, 8)
R_sim = []
for d in deltas:
    K = gamma/(2*d)
    r, s = kuramoto(800, K, n_seeds=2, T=800)
    R_sim.append((r, s))
    print(f"delta={d:.2f}: sim={r:.4f} exact={adler_root(np.array([d]))[0]:.4f} err={abs(r-adler_root(np.array([d]))[0]):.4f}")

R_sim = np.array(R_sim)
R_exact = adler_root(deltas)

# Distribution scan
print("\nDistribution scan:")
for dist in ['lorentzian', 'gaussian', 'uniform']:
    Ks = np.linspace(Kc[dist]*0.4, Kc[dist]*1.8, 15)
    Rs = [kuramoto(500, K, gamma, dist, T=500, n_seeds=1)[0] for K in Ks]
    print(f"  {dist}: Kc={Kc[dist]:.4f}, R at K/Kc=1.1={Rs[np.argmin(np.abs(Ks/Kc[dist]-1.1))]:.4f}")

# Plot
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
ax = axes[0]
d_full = np.linspace(1.0, 5.0, 100)
ax.plot(d_full, adler_root(d_full), 'r-', lw=2, label='Adler formula')
ax.errorbar(deltas, R_sim[:,0], yerr=R_sim[:,1], fmt='ko', ms=6, capsize=3, label='Simulation')
ax.set_xlabel(r'$\delta$')
ax.set_ylabel(r'$R$')
ax.set_title('Adler Root Curve (PRF-009)')
ax.legend()
ax.grid(alpha=0.3)

ax = axes[1]
for dist, color in [('lorentzian','b'),('gaussian','g'),('uniform','r')]:
    Ks = np.linspace(Kc[dist]*0.5, Kc[dist]*1.8, 15)
    Rs = [kuramoto(500, K, gamma, dist, T=500, n_seeds=1)[0] for K in Ks]
    ax.plot(Ks/Kc[dist], Rs, f'{color}-o', ms=4, label=f'{dist} (Kc={Kc[dist]:.3f})')
ax.axvline(1.0, color='k', ls='--', alpha=0.5)
ax.set_xlabel(r'$K/K_c$')
ax.set_ylabel(r'$R$')
ax.set_title('Distribution Scaling Collapse')
ax.legend(fontsize=8)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('fig_adler_fast.png', dpi=120)
print("Saved fig_adler_fast.png")
print("DONE")
