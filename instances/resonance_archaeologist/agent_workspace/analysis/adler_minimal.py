#!/usr/bin/env python3
"""Minimal Adler root reproduction - ultra fast."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

def kuramoto_fast(N, K, dist='lorentzian', T=300, dt=0.1):
    np.random.seed(42)
    if dist == 'lorentzian': omega = np.random.standard_cauchy(N)
    elif dist == 'gaussian': omega = np.random.randn(N)
    else: omega = 2*np.random.rand(N)-1
    theta = 2*np.pi*np.random.rand(N)
    for t in range(int(T/dt)):
        z = np.mean(np.exp(1j*theta))
        theta += dt * (omega + 2*K*np.sin(np.angle(z)-theta))
    return np.abs(np.mean(np.exp(1j*theta)))

def adler_root(delta):
    R = np.zeros_like(delta)
    mask = delta >= 1.0
    R[mask] = delta[mask] - np.sqrt(delta[mask]**2 - 1)
    return R

gamma = 1.0
Kc = {'lorentzian': 2*gamma/np.pi, 'gaussian': np.sqrt(8/np.pi)*gamma, 'uniform': gamma}

deltas = np.linspace(1.0, 5.0, 8)
R_sim = [kuramoto_fast(300, gamma/(2*d), 'lorentzian', T=200) for d in deltas]
R_exact = adler_root(deltas)

print("Adler root curve verification:")
for d, rs, re in zip(deltas, R_sim, R_exact):
    print(f"delta={d:.2f}: sim={rs:.4f} exact={re:.4f} err={abs(rs-re):.4f}")

# Distribution scan
print("\nDistribution Kc (approx from R at K/Kc~1.0):")
for dist in ['lorentzian', 'gaussian', 'uniform']:
    r = kuramoto_fast(300, Kc[dist]*1.1, dist, T=200)
    print(f"  {dist}: Kc={Kc[dist]:.4f}, R(K/Kc=1.1)={r:.4f}")

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
ax = axes[0]
d_full = np.linspace(1.0, 5.0, 100)
ax.plot(d_full, adler_root(d_full), 'r-', lw=2, label='Adler formula (PRF-009)')
ax.plot(deltas, R_sim, 'ko', ms=6, label='Simulation (N=300)')
ax.set_xlabel(r'$\delta$')
ax.set_ylabel(r'$R$')
ax.set_title('Adler Root Curve')
ax.legend()
ax.grid(alpha=0.3)

ax = axes[1]
for dist, color in [('lorentzian','b'),('gaussian','g'),('uniform','r')]:
    Ks = np.linspace(Kc[dist]*0.5, Kc[dist]*1.8, 8)
    Rs = [kuramoto_fast(300, K, dist, T=150) for K in Ks]
    ax.plot(Ks/Kc[dist], Rs, f'{color}-o', ms=4, label=f'{dist}')
ax.axvline(1.0, color='k', ls='--', alpha=0.5)
ax.set_xlabel(r'$K/K_c$')
ax.set_ylabel(r'$R$')
ax.set_title('Distribution Scaling')
ax.legend(fontsize=8)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('fig_adler_minimal.png', dpi=100)
print("\nSaved fig_adler_minimal.png")
print("DONE")
