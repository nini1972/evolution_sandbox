#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = os.path.dirname(os.path.abspath(__file__))

def integrate_batch(th0, K0, alpha, sigma, dt=0.04, nsteps=250, rng=None, seed_phases=None):
    """Vectorized over seeds AND time. th0 shape (S, N)."""
    S, N = th0.shape
    th = np.array(th0, dtype=float)
    sd = math.sqrt(dt)
    if rng is None:
        rng = np.random.RandomState(42)
    # pre-generate noise: (S, N, nsteps) could be big; regenerate per step instead with fixed seed
    for _ in range(nsteps):
        z = np.mean(np.exp(1j * th), axis=1)          # (S,)
        R = np.abs(z)
        dth = np.imag(np.exp(-1j * th) * z[:, None])  # (S, N)
        K = K0 * (R ** alpha)
        th = th + dt * (K[:, None] * dth) + sd * sigma * rng.randn(S, N)
    return np.abs(np.mean(np.exp(1j * th), axis=1))   # (S,)

def cluster_phases(R0, N, rng):
    sigma_ph = np.sqrt(-2 * np.log(max(R0, 1e-4)))
    return rng.randn(N) * sigma_ph

def run_batch(alpha, K0, sigma=0.008, N=200, seeds=5):
    rng = np.random.RandomState(7)
    th_lo = rng.uniform(0, 2 * math.pi, (seeds, N))
    th_hi = np.array([cluster_phases(0.85, N, rng) for _ in range(seeds)])
    lo = integrate_batch(th_lo, K0, alpha, sigma, rng=rng)
    hi = integrate_batch(th_hi, K0, alpha, sigma, rng=rng)
    return float(lo.mean()), float(hi.mean())

ALPHAS = [0.6, 0.8, 1.0, 1.2, 1.5, 2.0]
KGRID = np.linspace(0.05, 2.5, 30)
res = {"alphas": ALPHAS, "kgrid": list(KGRID), "R_low": [], "R_high": []}
for a in ALPHAS:
    rl = []; rh = []
    for K0 in KGRID:
        lo, hi = run_batch(a, K0)
        rl.append(lo); rh.append(hi)
    res["R_low"].append(rl); res["R_high"].append(rh)
    dif = max(np.array(rh) - np.array(rl))
    print("alpha=%.1f  Rlow@K0=3: %.3f   Rhigh@K0=3: %.3f   | max gap: %.3f"
          % (a, rl[-1], rh[-1], dif))

with open(os.path.join(OUT, "alpha_hysteresis.json"), "w") as f:
    json.dump(res, f, indent=2)

fig, axes = plt.subplots(2, 3, figsize=(14, 8), sharey=True)
for idx, a in enumerate(ALPHAS):
    ax = axes[idx // 3][idx % 3]
    ax.plot(KGRID, res["R_low"][idx], 'o-', color='crimson', ms=4, label='from disorder (R0~0)')
    ax.plot(KGRID, res["R_high"][idx], 's-', color='navy', ms=4, label='from cluster (R0=0.85)')
    ax.set_title(r'$\alpha=%.1f$' % a, fontsize=12)
    ax.set_xlabel(r'$K_0$')
    if idx % 3 == 0: ax.set_ylabel(r'$R^*$')
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7)
fig.suptitle('Ignition-barrier probe: low-R vs high-R initial conditions (vectorized, N=200)', fontsize=14)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "alpha_hysteresis.png"), dpi=140)
print("saved alpha_hysteresis.png")