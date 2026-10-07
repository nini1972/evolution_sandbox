#!/usr/bin/env python3
"""
Instrumented trajectory experiment: WATCH what actually happens.
Regimes to probe (reflexive Kuramoto, K = K0 R^alpha, per-osc Gaussian noise sigma):
  A) sigma=0 (no noise): theory says incoherence unstable -> deterministic escape, tau ~ R0^-alpha
  B) sigma>0, K0 << K_sn: below saddle-node -> no escape (or nucleation via finite-N)
  C) sigma>0, K0 >> K_sn: above saddle-node -> fast sync expected
  D) sigma>0, K0 near K_sn: critical
Also track effective K (coupling strength at small R) vs noise.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def fmax(alpha):
    Rm = np.sqrt(alpha/(alpha+2)) if alpha > 0 else 1.0/np.sqrt(3)
    return Rm**alpha*(1-Rm**2)

def ksn(sigma, alpha):
    return sigma**2/fmax(alpha)

def run_traj(N, K0, alpha, sigma, T, dt, R0, seed):
    rng = np.random.default_rng(seed)
    theta = rng.uniform(0, 2*np.pi, N)
    z = np.mean(np.exp(1j*theta))
    theta = theta - np.angle(z)
    # prepare with desired R0 by squeezing around the mean angle
    theta = theta * (1.0 - R0)
    R_hist = [R0]
    K_hist = [K0*R0**alpha if alpha>0 else K0]
    n = int(T/dt)
    for i in range(n):
        z = np.mean(np.exp(1j*theta))
        R = abs(z)
        psi = np.angle(z)
        K = K0 * (R**alpha) if alpha>0 else K0
        dtheta = K*R*np.sin(psi-theta)*dt + sigma*np.sqrt(dt)*rng.standard_normal(N)
        theta = theta + dtheta
        R_hist.append(R)
        K_hist.append(K)
    return np.array(R_hist), np.array(K_hist)

def heat(alpha):
    """f(R) = fmax * (R/Rm)^alpha * (1-R^2)/(1-Rm^2)... return normalized drift shape"""
    Rm = np.sqrt(alpha/(alpha+2))
    return Rm, alpha

# ---------- probe regimes ----------
fig, axes = plt.subplots(3, 2, figsize=(13, 11))
cases = [
    # (title, N, K0, alpha, sigma, T, dt, R0)
    ("A: sigma=0, K0=1 (no barrier)",       400, 1.0, 1.0, 0.0, 30, 0.01, 0.10),
    ("B: sigma=0.2, K0=0.05 << Ksn=0.104",  400, 0.05, 1.0, 0.2, 60, 0.01, 0.10),
    ("C: sigma=0.2, K0=0.2 >> Ksn=0.104",   400, 0.2, 1.0, 0.2, 60, 0.01, 0.10),
    ("D: sigma=0.2, K0=0.10 ~ Ksn=0.104",   400, 0.10, 1.0, 0.2, 60, 0.01, 0.10),
    ("E: sigma=0.5, alpha=2, K0=0.5 < Ksn=1",400, 0.5, 2.0, 0.5, 60, 0.01, 0.10),
    ("F: sigma=0.05, K0=3.7 alpha=0.5 (old job!)", 500, 3.7, 0.5, 0.05, 60, 0.01, 0.05),
]
for ax, (title, N, K0, alpha, sigma, T, dt, R0) in zip(axes.ravel(), cases):
    sk = ksn(sigma, alpha) if sigma>0 else float('inf')
    R, K = run_traj(N, K0, alpha, sigma, T, dt, R0, 42)
    t = np.arange(len(R))*dt
    ax.plot(t, R, lw=1.2, color='tab:blue', label=f'R(t) init {R0}')
    ax.axhline(0.9, color='gray', ls='--', lw=0.8)
    ax.set_title(f"{title}\nKsn={sk:.4f}", fontsize=9)
    ax.set_xlabel('t'); ax.set_ylabel('R')
    ax.set_ylim(-0.02, 1.02)
    ax.legend(fontsize=7, loc='lower right')
    # mark escape
    esc = np.where(R>=0.9)[0]
    if len(esc):
        ax.axvline(esc[0]*dt, color='red', lw=1.5, label=f'escape t={esc[0]*dt:.1f}')
        ax.legend(fontsize=7, loc='lower right')
    print(f"{title[:55]:<58} tau_esc={esc[0]*dt if len(esc) else 'inf':>8}  R_final={R[-1]:.3f}",
          f" Ksn={sk:.4f} K0/Ksn={K0/sk if sk<1e9 else float('inf'):.2f}")
plt.tight_layout()
plt.savefig('trajectory_probe.png', dpi=110)
print("saved trajectory_probe.png")